r'''
# `spotinst_ocean_spark`

Refer to the Terraform Registry for docs: [`spotinst_ocean_spark`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark).
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


class OceanSpark(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSpark",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark spotinst_ocean_spark}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        ocean_cluster_id: builtins.str,
        compute: typing.Optional[typing.Union["OceanSparkCompute", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        ingress: typing.Optional[typing.Union["OceanSparkIngress", typing.Dict[builtins.str, typing.Any]]] = None,
        log_collection: typing.Optional[typing.Union["OceanSparkLogCollection", typing.Dict[builtins.str, typing.Any]]] = None,
        spark: typing.Optional[typing.Union["OceanSparkSpark", typing.Dict[builtins.str, typing.Any]]] = None,
        webhook: typing.Optional[typing.Union["OceanSparkWebhook", typing.Dict[builtins.str, typing.Any]]] = None,
        workspaces: typing.Optional[typing.Union["OceanSparkWorkspaces", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark spotinst_ocean_spark} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ocean_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#ocean_cluster_id OceanSpark#ocean_cluster_id}.
        :param compute: compute block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#compute OceanSpark#compute}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#id OceanSpark#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ingress: ingress block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#ingress OceanSpark#ingress}
        :param log_collection: log_collection block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#log_collection OceanSpark#log_collection}
        :param spark: spark block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#spark OceanSpark#spark}
        :param webhook: webhook block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#webhook OceanSpark#webhook}
        :param workspaces: workspaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#workspaces OceanSpark#workspaces}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1b1c4bc9ac16a6f54df9d8f9743a0efcb7223d78fdd53130efcce6d47647516)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanSparkConfig(
            ocean_cluster_id=ocean_cluster_id,
            compute=compute,
            id=id,
            ingress=ingress,
            log_collection=log_collection,
            spark=spark,
            webhook=webhook,
            workspaces=workspaces,
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
        '''Generates CDKTF code for importing a OceanSpark resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanSpark to import.
        :param import_from_id: The id of the existing OceanSpark that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanSpark to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad0407ed141bf93f77d1afb7db4937fd72d9602f61e000d8fd0809da9c23adf3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCompute")
    def put_compute(
        self,
        *,
        create_vngs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_taints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param create_vngs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#create_vngs OceanSpark#create_vngs}.
        :param use_taints: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#use_taints OceanSpark#use_taints}.
        '''
        value = OceanSparkCompute(create_vngs=create_vngs, use_taints=use_taints)

        return typing.cast(None, jsii.invoke(self, "putCompute", [value]))

    @jsii.member(jsii_name="putIngress")
    def put_ingress(
        self,
        *,
        controller: typing.Optional[typing.Union["OceanSparkIngressController", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_endpoint: typing.Optional[typing.Union["OceanSparkIngressCustomEndpoint", typing.Dict[builtins.str, typing.Any]]] = None,
        load_balancer: typing.Optional[typing.Union["OceanSparkIngressLoadBalancer", typing.Dict[builtins.str, typing.Any]]] = None,
        private_link: typing.Optional[typing.Union["OceanSparkIngressPrivateLink", typing.Dict[builtins.str, typing.Any]]] = None,
        service_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param controller: controller block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#controller OceanSpark#controller}
        :param custom_endpoint: custom_endpoint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#custom_endpoint OceanSpark#custom_endpoint}
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#load_balancer OceanSpark#load_balancer}
        :param private_link: private_link block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#private_link OceanSpark#private_link}
        :param service_annotations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#service_annotations OceanSpark#service_annotations}.
        '''
        value = OceanSparkIngress(
            controller=controller,
            custom_endpoint=custom_endpoint,
            load_balancer=load_balancer,
            private_link=private_link,
            service_annotations=service_annotations,
        )

        return typing.cast(None, jsii.invoke(self, "putIngress", [value]))

    @jsii.member(jsii_name="putLogCollection")
    def put_log_collection(
        self,
        *,
        collect_app_logs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param collect_app_logs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#collect_app_logs OceanSpark#collect_app_logs}.
        '''
        value = OceanSparkLogCollection(collect_app_logs=collect_app_logs)

        return typing.cast(None, jsii.invoke(self, "putLogCollection", [value]))

    @jsii.member(jsii_name="putSpark")
    def put_spark(
        self,
        *,
        additional_app_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param additional_app_namespaces: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#additional_app_namespaces OceanSpark#additional_app_namespaces}.
        '''
        value = OceanSparkSpark(additional_app_namespaces=additional_app_namespaces)

        return typing.cast(None, jsii.invoke(self, "putSpark", [value]))

    @jsii.member(jsii_name="putWebhook")
    def put_webhook(
        self,
        *,
        host_network_ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        use_host_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param host_network_ports: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#host_network_ports OceanSpark#host_network_ports}.
        :param use_host_network: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#use_host_network OceanSpark#use_host_network}.
        '''
        value = OceanSparkWebhook(
            host_network_ports=host_network_ports, use_host_network=use_host_network
        )

        return typing.cast(None, jsii.invoke(self, "putWebhook", [value]))

    @jsii.member(jsii_name="putWorkspaces")
    def put_workspaces(
        self,
        *,
        storage: typing.Optional[typing.Union["OceanSparkWorkspacesStorage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param storage: storage block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#storage OceanSpark#storage}
        '''
        value = OceanSparkWorkspaces(storage=storage)

        return typing.cast(None, jsii.invoke(self, "putWorkspaces", [value]))

    @jsii.member(jsii_name="resetCompute")
    def reset_compute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompute", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIngress")
    def reset_ingress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngress", []))

    @jsii.member(jsii_name="resetLogCollection")
    def reset_log_collection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogCollection", []))

    @jsii.member(jsii_name="resetSpark")
    def reset_spark(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpark", []))

    @jsii.member(jsii_name="resetWebhook")
    def reset_webhook(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhook", []))

    @jsii.member(jsii_name="resetWorkspaces")
    def reset_workspaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkspaces", []))

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
    @jsii.member(jsii_name="compute")
    def compute(self) -> "OceanSparkComputeOutputReference":
        return typing.cast("OceanSparkComputeOutputReference", jsii.get(self, "compute"))

    @builtins.property
    @jsii.member(jsii_name="ingress")
    def ingress(self) -> "OceanSparkIngressOutputReference":
        return typing.cast("OceanSparkIngressOutputReference", jsii.get(self, "ingress"))

    @builtins.property
    @jsii.member(jsii_name="logCollection")
    def log_collection(self) -> "OceanSparkLogCollectionOutputReference":
        return typing.cast("OceanSparkLogCollectionOutputReference", jsii.get(self, "logCollection"))

    @builtins.property
    @jsii.member(jsii_name="spark")
    def spark(self) -> "OceanSparkSparkOutputReference":
        return typing.cast("OceanSparkSparkOutputReference", jsii.get(self, "spark"))

    @builtins.property
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> "OceanSparkWebhookOutputReference":
        return typing.cast("OceanSparkWebhookOutputReference", jsii.get(self, "webhook"))

    @builtins.property
    @jsii.member(jsii_name="workspaces")
    def workspaces(self) -> "OceanSparkWorkspacesOutputReference":
        return typing.cast("OceanSparkWorkspacesOutputReference", jsii.get(self, "workspaces"))

    @builtins.property
    @jsii.member(jsii_name="computeInput")
    def compute_input(self) -> typing.Optional["OceanSparkCompute"]:
        return typing.cast(typing.Optional["OceanSparkCompute"], jsii.get(self, "computeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ingressInput")
    def ingress_input(self) -> typing.Optional["OceanSparkIngress"]:
        return typing.cast(typing.Optional["OceanSparkIngress"], jsii.get(self, "ingressInput"))

    @builtins.property
    @jsii.member(jsii_name="logCollectionInput")
    def log_collection_input(self) -> typing.Optional["OceanSparkLogCollection"]:
        return typing.cast(typing.Optional["OceanSparkLogCollection"], jsii.get(self, "logCollectionInput"))

    @builtins.property
    @jsii.member(jsii_name="oceanClusterIdInput")
    def ocean_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oceanClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="sparkInput")
    def spark_input(self) -> typing.Optional["OceanSparkSpark"]:
        return typing.cast(typing.Optional["OceanSparkSpark"], jsii.get(self, "sparkInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookInput")
    def webhook_input(self) -> typing.Optional["OceanSparkWebhook"]:
        return typing.cast(typing.Optional["OceanSparkWebhook"], jsii.get(self, "webhookInput"))

    @builtins.property
    @jsii.member(jsii_name="workspacesInput")
    def workspaces_input(self) -> typing.Optional["OceanSparkWorkspaces"]:
        return typing.cast(typing.Optional["OceanSparkWorkspaces"], jsii.get(self, "workspacesInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b32cd9ea2665f1a0867bedb774891dadb71a815890ed20dfd2031817470ec487)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oceanClusterId")
    def ocean_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oceanClusterId"))

    @ocean_cluster_id.setter
    def ocean_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b299987c1a8811030b1d82669490ad6d7fd08c05926a07f7b4f656e45a3d3c5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oceanClusterId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkCompute",
    jsii_struct_bases=[],
    name_mapping={"create_vngs": "createVngs", "use_taints": "useTaints"},
)
class OceanSparkCompute:
    def __init__(
        self,
        *,
        create_vngs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_taints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param create_vngs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#create_vngs OceanSpark#create_vngs}.
        :param use_taints: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#use_taints OceanSpark#use_taints}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4610e707f0aec1c278f0e97e6035d36c402df29450a80faca8bfb3143ad81bc0)
            check_type(argname="argument create_vngs", value=create_vngs, expected_type=type_hints["create_vngs"])
            check_type(argname="argument use_taints", value=use_taints, expected_type=type_hints["use_taints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create_vngs is not None:
            self._values["create_vngs"] = create_vngs
        if use_taints is not None:
            self._values["use_taints"] = use_taints

    @builtins.property
    def create_vngs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#create_vngs OceanSpark#create_vngs}.'''
        result = self._values.get("create_vngs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_taints(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#use_taints OceanSpark#use_taints}.'''
        result = self._values.get("use_taints")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkCompute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkComputeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkComputeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d5e7afd8c4e0e72437877e8576b6261784cab053dd5d3b592d387d621ae0fdf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreateVngs")
    def reset_create_vngs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateVngs", []))

    @jsii.member(jsii_name="resetUseTaints")
    def reset_use_taints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseTaints", []))

    @builtins.property
    @jsii.member(jsii_name="createVngsInput")
    def create_vngs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "createVngsInput"))

    @builtins.property
    @jsii.member(jsii_name="useTaintsInput")
    def use_taints_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useTaintsInput"))

    @builtins.property
    @jsii.member(jsii_name="createVngs")
    def create_vngs(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "createVngs"))

    @create_vngs.setter
    def create_vngs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08a8ae314062aa8240f6cb20a43e7ff33d16c4118192f34e5ebda661b97b0ae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createVngs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useTaints")
    def use_taints(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useTaints"))

    @use_taints.setter
    def use_taints(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5420a67ca502f78424546a0db5af1f2d88b4b19ca46d80c6f5a5e891d9472fd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useTaints", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkCompute]:
        return typing.cast(typing.Optional[OceanSparkCompute], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanSparkCompute]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38263ed7004c6a7e41dc42b95b20d94e3f657fb9bab67ce31efc5277889e35d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "ocean_cluster_id": "oceanClusterId",
        "compute": "compute",
        "id": "id",
        "ingress": "ingress",
        "log_collection": "logCollection",
        "spark": "spark",
        "webhook": "webhook",
        "workspaces": "workspaces",
    },
)
class OceanSparkConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        ocean_cluster_id: builtins.str,
        compute: typing.Optional[typing.Union[OceanSparkCompute, typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        ingress: typing.Optional[typing.Union["OceanSparkIngress", typing.Dict[builtins.str, typing.Any]]] = None,
        log_collection: typing.Optional[typing.Union["OceanSparkLogCollection", typing.Dict[builtins.str, typing.Any]]] = None,
        spark: typing.Optional[typing.Union["OceanSparkSpark", typing.Dict[builtins.str, typing.Any]]] = None,
        webhook: typing.Optional[typing.Union["OceanSparkWebhook", typing.Dict[builtins.str, typing.Any]]] = None,
        workspaces: typing.Optional[typing.Union["OceanSparkWorkspaces", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param ocean_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#ocean_cluster_id OceanSpark#ocean_cluster_id}.
        :param compute: compute block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#compute OceanSpark#compute}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#id OceanSpark#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ingress: ingress block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#ingress OceanSpark#ingress}
        :param log_collection: log_collection block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#log_collection OceanSpark#log_collection}
        :param spark: spark block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#spark OceanSpark#spark}
        :param webhook: webhook block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#webhook OceanSpark#webhook}
        :param workspaces: workspaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#workspaces OceanSpark#workspaces}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(compute, dict):
            compute = OceanSparkCompute(**compute)
        if isinstance(ingress, dict):
            ingress = OceanSparkIngress(**ingress)
        if isinstance(log_collection, dict):
            log_collection = OceanSparkLogCollection(**log_collection)
        if isinstance(spark, dict):
            spark = OceanSparkSpark(**spark)
        if isinstance(webhook, dict):
            webhook = OceanSparkWebhook(**webhook)
        if isinstance(workspaces, dict):
            workspaces = OceanSparkWorkspaces(**workspaces)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__286ba412bd73327f01a051d064e2c7c310afd50b3674fc79fe0a7cedf108e461)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument ocean_cluster_id", value=ocean_cluster_id, expected_type=type_hints["ocean_cluster_id"])
            check_type(argname="argument compute", value=compute, expected_type=type_hints["compute"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ingress", value=ingress, expected_type=type_hints["ingress"])
            check_type(argname="argument log_collection", value=log_collection, expected_type=type_hints["log_collection"])
            check_type(argname="argument spark", value=spark, expected_type=type_hints["spark"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument workspaces", value=workspaces, expected_type=type_hints["workspaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ocean_cluster_id": ocean_cluster_id,
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
        if compute is not None:
            self._values["compute"] = compute
        if id is not None:
            self._values["id"] = id
        if ingress is not None:
            self._values["ingress"] = ingress
        if log_collection is not None:
            self._values["log_collection"] = log_collection
        if spark is not None:
            self._values["spark"] = spark
        if webhook is not None:
            self._values["webhook"] = webhook
        if workspaces is not None:
            self._values["workspaces"] = workspaces

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
    def ocean_cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#ocean_cluster_id OceanSpark#ocean_cluster_id}.'''
        result = self._values.get("ocean_cluster_id")
        assert result is not None, "Required property 'ocean_cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def compute(self) -> typing.Optional[OceanSparkCompute]:
        '''compute block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#compute OceanSpark#compute}
        '''
        result = self._values.get("compute")
        return typing.cast(typing.Optional[OceanSparkCompute], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#id OceanSpark#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingress(self) -> typing.Optional["OceanSparkIngress"]:
        '''ingress block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#ingress OceanSpark#ingress}
        '''
        result = self._values.get("ingress")
        return typing.cast(typing.Optional["OceanSparkIngress"], result)

    @builtins.property
    def log_collection(self) -> typing.Optional["OceanSparkLogCollection"]:
        '''log_collection block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#log_collection OceanSpark#log_collection}
        '''
        result = self._values.get("log_collection")
        return typing.cast(typing.Optional["OceanSparkLogCollection"], result)

    @builtins.property
    def spark(self) -> typing.Optional["OceanSparkSpark"]:
        '''spark block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#spark OceanSpark#spark}
        '''
        result = self._values.get("spark")
        return typing.cast(typing.Optional["OceanSparkSpark"], result)

    @builtins.property
    def webhook(self) -> typing.Optional["OceanSparkWebhook"]:
        '''webhook block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#webhook OceanSpark#webhook}
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional["OceanSparkWebhook"], result)

    @builtins.property
    def workspaces(self) -> typing.Optional["OceanSparkWorkspaces"]:
        '''workspaces block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#workspaces OceanSpark#workspaces}
        '''
        result = self._values.get("workspaces")
        return typing.cast(typing.Optional["OceanSparkWorkspaces"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngress",
    jsii_struct_bases=[],
    name_mapping={
        "controller": "controller",
        "custom_endpoint": "customEndpoint",
        "load_balancer": "loadBalancer",
        "private_link": "privateLink",
        "service_annotations": "serviceAnnotations",
    },
)
class OceanSparkIngress:
    def __init__(
        self,
        *,
        controller: typing.Optional[typing.Union["OceanSparkIngressController", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_endpoint: typing.Optional[typing.Union["OceanSparkIngressCustomEndpoint", typing.Dict[builtins.str, typing.Any]]] = None,
        load_balancer: typing.Optional[typing.Union["OceanSparkIngressLoadBalancer", typing.Dict[builtins.str, typing.Any]]] = None,
        private_link: typing.Optional[typing.Union["OceanSparkIngressPrivateLink", typing.Dict[builtins.str, typing.Any]]] = None,
        service_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param controller: controller block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#controller OceanSpark#controller}
        :param custom_endpoint: custom_endpoint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#custom_endpoint OceanSpark#custom_endpoint}
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#load_balancer OceanSpark#load_balancer}
        :param private_link: private_link block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#private_link OceanSpark#private_link}
        :param service_annotations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#service_annotations OceanSpark#service_annotations}.
        '''
        if isinstance(controller, dict):
            controller = OceanSparkIngressController(**controller)
        if isinstance(custom_endpoint, dict):
            custom_endpoint = OceanSparkIngressCustomEndpoint(**custom_endpoint)
        if isinstance(load_balancer, dict):
            load_balancer = OceanSparkIngressLoadBalancer(**load_balancer)
        if isinstance(private_link, dict):
            private_link = OceanSparkIngressPrivateLink(**private_link)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd91c4f0dc4e99a521b8c57bef0287eccf40665d7b8ddff0bd024aa3d5bb839)
            check_type(argname="argument controller", value=controller, expected_type=type_hints["controller"])
            check_type(argname="argument custom_endpoint", value=custom_endpoint, expected_type=type_hints["custom_endpoint"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument private_link", value=private_link, expected_type=type_hints["private_link"])
            check_type(argname="argument service_annotations", value=service_annotations, expected_type=type_hints["service_annotations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if controller is not None:
            self._values["controller"] = controller
        if custom_endpoint is not None:
            self._values["custom_endpoint"] = custom_endpoint
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if private_link is not None:
            self._values["private_link"] = private_link
        if service_annotations is not None:
            self._values["service_annotations"] = service_annotations

    @builtins.property
    def controller(self) -> typing.Optional["OceanSparkIngressController"]:
        '''controller block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#controller OceanSpark#controller}
        '''
        result = self._values.get("controller")
        return typing.cast(typing.Optional["OceanSparkIngressController"], result)

    @builtins.property
    def custom_endpoint(self) -> typing.Optional["OceanSparkIngressCustomEndpoint"]:
        '''custom_endpoint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#custom_endpoint OceanSpark#custom_endpoint}
        '''
        result = self._values.get("custom_endpoint")
        return typing.cast(typing.Optional["OceanSparkIngressCustomEndpoint"], result)

    @builtins.property
    def load_balancer(self) -> typing.Optional["OceanSparkIngressLoadBalancer"]:
        '''load_balancer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#load_balancer OceanSpark#load_balancer}
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional["OceanSparkIngressLoadBalancer"], result)

    @builtins.property
    def private_link(self) -> typing.Optional["OceanSparkIngressPrivateLink"]:
        '''private_link block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#private_link OceanSpark#private_link}
        '''
        result = self._values.get("private_link")
        return typing.cast(typing.Optional["OceanSparkIngressPrivateLink"], result)

    @builtins.property
    def service_annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#service_annotations OceanSpark#service_annotations}.'''
        result = self._values.get("service_annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkIngress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressController",
    jsii_struct_bases=[],
    name_mapping={"managed": "managed"},
)
class OceanSparkIngressController:
    def __init__(
        self,
        *,
        managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param managed: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#managed OceanSpark#managed}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dca300324ce13da691bbeb9939026393581a6ad92015ece5b09f994253dc87d)
            check_type(argname="argument managed", value=managed, expected_type=type_hints["managed"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed is not None:
            self._values["managed"] = managed

    @builtins.property
    def managed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#managed OceanSpark#managed}.'''
        result = self._values.get("managed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkIngressController(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkIngressControllerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressControllerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__293c89d5f8265f0a37925038caece2c31fe0a6d81d25272bc83a549f1edcb8d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManaged")
    def reset_managed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManaged", []))

    @builtins.property
    @jsii.member(jsii_name="managedInput")
    def managed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "managedInput"))

    @builtins.property
    @jsii.member(jsii_name="managed")
    def managed(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "managed"))

    @managed.setter
    def managed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65f3459a15fd2a6de964532cca0e494e2f420de4d6dcd70e9e84ddc099998ee5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkIngressController]:
        return typing.cast(typing.Optional[OceanSparkIngressController], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanSparkIngressController],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f991ddbe6d7a00d046b1a643d517931d8fa30911a363d2c1a754153c7dfa041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressCustomEndpoint",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "enabled": "enabled"},
)
class OceanSparkIngressCustomEndpoint:
    def __init__(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#address OceanSpark#address}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#enabled OceanSpark#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4274454c2a1090fb2b92c80e6303460866fe17dc9703906b9153af36e79f0575)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if address is not None:
            self._values["address"] = address
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#address OceanSpark#address}.'''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#enabled OceanSpark#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkIngressCustomEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkIngressCustomEndpointOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressCustomEndpointOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1075dbf235403b5a8dc1753d0b2dbd835a0790caa658d7a173d171e7fab34419)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27a24c4341e81756286a0ccac764cb2f56e68ea8e564361ac0d6d42f4408cbae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__116bc2f7c4a5a8a036f27b658d5d98d6d598f29d1f7de1a3c58f8a6a8bd5fb01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkIngressCustomEndpoint]:
        return typing.cast(typing.Optional[OceanSparkIngressCustomEndpoint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanSparkIngressCustomEndpoint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6057c7fcbb7ebc0b977b940287533aedc90232655b67b97b837e87a06c98676)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressLoadBalancer",
    jsii_struct_bases=[],
    name_mapping={
        "managed": "managed",
        "service_annotations": "serviceAnnotations",
        "target_group_arn": "targetGroupArn",
    },
)
class OceanSparkIngressLoadBalancer:
    def __init__(
        self,
        *,
        managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        target_group_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#managed OceanSpark#managed}.
        :param service_annotations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#service_annotations OceanSpark#service_annotations}.
        :param target_group_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#target_group_arn OceanSpark#target_group_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35d186486fad538bf434179575983f09e6e4cc3a8c7bcb5dc7102b2996282515)
            check_type(argname="argument managed", value=managed, expected_type=type_hints["managed"])
            check_type(argname="argument service_annotations", value=service_annotations, expected_type=type_hints["service_annotations"])
            check_type(argname="argument target_group_arn", value=target_group_arn, expected_type=type_hints["target_group_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if managed is not None:
            self._values["managed"] = managed
        if service_annotations is not None:
            self._values["service_annotations"] = service_annotations
        if target_group_arn is not None:
            self._values["target_group_arn"] = target_group_arn

    @builtins.property
    def managed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#managed OceanSpark#managed}.'''
        result = self._values.get("managed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#service_annotations OceanSpark#service_annotations}.'''
        result = self._values.get("service_annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def target_group_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#target_group_arn OceanSpark#target_group_arn}.'''
        result = self._values.get("target_group_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkIngressLoadBalancer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkIngressLoadBalancerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressLoadBalancerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b646e99451f2437448d310a0fedd858d2779bacc075258e15b7040748e7603c8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetManaged")
    def reset_managed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManaged", []))

    @jsii.member(jsii_name="resetServiceAnnotations")
    def reset_service_annotations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAnnotations", []))

    @jsii.member(jsii_name="resetTargetGroupArn")
    def reset_target_group_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetGroupArn", []))

    @builtins.property
    @jsii.member(jsii_name="managedInput")
    def managed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "managedInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAnnotationsInput")
    def service_annotations_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "serviceAnnotationsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetGroupArnInput")
    def target_group_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetGroupArnInput"))

    @builtins.property
    @jsii.member(jsii_name="managed")
    def managed(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "managed"))

    @managed.setter
    def managed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74fdd32484858c39b906c87af8ea190104c2450a206260430d891e280503b5a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAnnotations")
    def service_annotations(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "serviceAnnotations"))

    @service_annotations.setter
    def service_annotations(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f8f77a34720538127313d52b23d1f29b061624a3ac923e24064b8625c798f6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAnnotations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetGroupArn")
    def target_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetGroupArn"))

    @target_group_arn.setter
    def target_group_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f159c85faacd74fb04dc621c7e6703ca5aabe65bdcec5aa07462e92f418f5e5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetGroupArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkIngressLoadBalancer]:
        return typing.cast(typing.Optional[OceanSparkIngressLoadBalancer], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanSparkIngressLoadBalancer],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f5b030ab7c3c03120be8d6eed5bb033da3e9474319c3e6749870b55427e3481)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanSparkIngressOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__569deec9e54f5548e968442c4706220c8564b78b3eea4eb48d2dedc5390ad022)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putController")
    def put_controller(
        self,
        *,
        managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param managed: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#managed OceanSpark#managed}.
        '''
        value = OceanSparkIngressController(managed=managed)

        return typing.cast(None, jsii.invoke(self, "putController", [value]))

    @jsii.member(jsii_name="putCustomEndpoint")
    def put_custom_endpoint(
        self,
        *,
        address: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#address OceanSpark#address}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#enabled OceanSpark#enabled}.
        '''
        value = OceanSparkIngressCustomEndpoint(address=address, enabled=enabled)

        return typing.cast(None, jsii.invoke(self, "putCustomEndpoint", [value]))

    @jsii.member(jsii_name="putLoadBalancer")
    def put_load_balancer(
        self,
        *,
        managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        target_group_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param managed: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#managed OceanSpark#managed}.
        :param service_annotations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#service_annotations OceanSpark#service_annotations}.
        :param target_group_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#target_group_arn OceanSpark#target_group_arn}.
        '''
        value = OceanSparkIngressLoadBalancer(
            managed=managed,
            service_annotations=service_annotations,
            target_group_arn=target_group_arn,
        )

        return typing.cast(None, jsii.invoke(self, "putLoadBalancer", [value]))

    @jsii.member(jsii_name="putPrivateLink")
    def put_private_link(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vpc_endpoint_service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#enabled OceanSpark#enabled}.
        :param vpc_endpoint_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#vpc_endpoint_service OceanSpark#vpc_endpoint_service}.
        '''
        value = OceanSparkIngressPrivateLink(
            enabled=enabled, vpc_endpoint_service=vpc_endpoint_service
        )

        return typing.cast(None, jsii.invoke(self, "putPrivateLink", [value]))

    @jsii.member(jsii_name="resetController")
    def reset_controller(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetController", []))

    @jsii.member(jsii_name="resetCustomEndpoint")
    def reset_custom_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomEndpoint", []))

    @jsii.member(jsii_name="resetLoadBalancer")
    def reset_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancer", []))

    @jsii.member(jsii_name="resetPrivateLink")
    def reset_private_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateLink", []))

    @jsii.member(jsii_name="resetServiceAnnotations")
    def reset_service_annotations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAnnotations", []))

    @builtins.property
    @jsii.member(jsii_name="controller")
    def controller(self) -> OceanSparkIngressControllerOutputReference:
        return typing.cast(OceanSparkIngressControllerOutputReference, jsii.get(self, "controller"))

    @builtins.property
    @jsii.member(jsii_name="customEndpoint")
    def custom_endpoint(self) -> OceanSparkIngressCustomEndpointOutputReference:
        return typing.cast(OceanSparkIngressCustomEndpointOutputReference, jsii.get(self, "customEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(self) -> OceanSparkIngressLoadBalancerOutputReference:
        return typing.cast(OceanSparkIngressLoadBalancerOutputReference, jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="privateLink")
    def private_link(self) -> "OceanSparkIngressPrivateLinkOutputReference":
        return typing.cast("OceanSparkIngressPrivateLinkOutputReference", jsii.get(self, "privateLink"))

    @builtins.property
    @jsii.member(jsii_name="controllerInput")
    def controller_input(self) -> typing.Optional[OceanSparkIngressController]:
        return typing.cast(typing.Optional[OceanSparkIngressController], jsii.get(self, "controllerInput"))

    @builtins.property
    @jsii.member(jsii_name="customEndpointInput")
    def custom_endpoint_input(self) -> typing.Optional[OceanSparkIngressCustomEndpoint]:
        return typing.cast(typing.Optional[OceanSparkIngressCustomEndpoint], jsii.get(self, "customEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancerInput")
    def load_balancer_input(self) -> typing.Optional[OceanSparkIngressLoadBalancer]:
        return typing.cast(typing.Optional[OceanSparkIngressLoadBalancer], jsii.get(self, "loadBalancerInput"))

    @builtins.property
    @jsii.member(jsii_name="privateLinkInput")
    def private_link_input(self) -> typing.Optional["OceanSparkIngressPrivateLink"]:
        return typing.cast(typing.Optional["OceanSparkIngressPrivateLink"], jsii.get(self, "privateLinkInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAnnotationsInput")
    def service_annotations_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "serviceAnnotationsInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAnnotations")
    def service_annotations(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "serviceAnnotations"))

    @service_annotations.setter
    def service_annotations(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79e7da0ff5541de73c8457c7f97f2dce548a7836f2f3821b4a7ddbc803da01c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAnnotations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkIngress]:
        return typing.cast(typing.Optional[OceanSparkIngress], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanSparkIngress]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__140556ab92fb5089d72e65115b4133e1945cc87570eef0b58ff11d3b25d2d848)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressPrivateLink",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "vpc_endpoint_service": "vpcEndpointService"},
)
class OceanSparkIngressPrivateLink:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vpc_endpoint_service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#enabled OceanSpark#enabled}.
        :param vpc_endpoint_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#vpc_endpoint_service OceanSpark#vpc_endpoint_service}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31721d1717914f6d9f6c6fa563a5f6db92dd2b450d03a4129ca360c30f9671b8)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument vpc_endpoint_service", value=vpc_endpoint_service, expected_type=type_hints["vpc_endpoint_service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if vpc_endpoint_service is not None:
            self._values["vpc_endpoint_service"] = vpc_endpoint_service

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#enabled OceanSpark#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vpc_endpoint_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#vpc_endpoint_service OceanSpark#vpc_endpoint_service}.'''
        result = self._values.get("vpc_endpoint_service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkIngressPrivateLink(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkIngressPrivateLinkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkIngressPrivateLinkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3650873b607e35a0a709518668b3d4b69630b461f0cf239ef97cfe2ca7cf86d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetVpcEndpointService")
    def reset_vpc_endpoint_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcEndpointService", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointServiceInput")
    def vpc_endpoint_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcEndpointServiceInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e588be73bc7ce6fec1cafaa2bbe0ac3f275fb08c48d06a1819144a23854ebcd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcEndpointService")
    def vpc_endpoint_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcEndpointService"))

    @vpc_endpoint_service.setter
    def vpc_endpoint_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e2dd4b25cee4321d0bb747e7f48cbddf727abed9b863dff173d1dda629ef6a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcEndpointService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkIngressPrivateLink]:
        return typing.cast(typing.Optional[OceanSparkIngressPrivateLink], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanSparkIngressPrivateLink],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da31f828f9d620d13ac91ce36a2ab79692d4d2c1fc45a6094fd3b1f4c58f3bde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkLogCollection",
    jsii_struct_bases=[],
    name_mapping={"collect_app_logs": "collectAppLogs"},
)
class OceanSparkLogCollection:
    def __init__(
        self,
        *,
        collect_app_logs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param collect_app_logs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#collect_app_logs OceanSpark#collect_app_logs}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e1ba6bc27cfd1ecfca0358d447573c0113e87f983c3f336a8a0be772dedb2ed)
            check_type(argname="argument collect_app_logs", value=collect_app_logs, expected_type=type_hints["collect_app_logs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if collect_app_logs is not None:
            self._values["collect_app_logs"] = collect_app_logs

    @builtins.property
    def collect_app_logs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#collect_app_logs OceanSpark#collect_app_logs}.'''
        result = self._values.get("collect_app_logs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkLogCollection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkLogCollectionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkLogCollectionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e710e6fa71a2a7a66cb7790b6a0dea16db687be22436bf5bf39e0385004fbc8e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCollectAppLogs")
    def reset_collect_app_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollectAppLogs", []))

    @builtins.property
    @jsii.member(jsii_name="collectAppLogsInput")
    def collect_app_logs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "collectAppLogsInput"))

    @builtins.property
    @jsii.member(jsii_name="collectAppLogs")
    def collect_app_logs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "collectAppLogs"))

    @collect_app_logs.setter
    def collect_app_logs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23ce2953b6fd3c452f5fc3b0b2033e8d597f5f22238599fe2e02d729b600ec40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectAppLogs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkLogCollection]:
        return typing.cast(typing.Optional[OceanSparkLogCollection], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanSparkLogCollection]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea419c886dfcc4e29c02e6958edb55f40a9a3b4d65ffb7faa4315508de762d57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkSpark",
    jsii_struct_bases=[],
    name_mapping={"additional_app_namespaces": "additionalAppNamespaces"},
)
class OceanSparkSpark:
    def __init__(
        self,
        *,
        additional_app_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param additional_app_namespaces: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#additional_app_namespaces OceanSpark#additional_app_namespaces}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49dd84e45632094a51989ef27d50d1e3000a28253cf98398f4bb775073934a6e)
            check_type(argname="argument additional_app_namespaces", value=additional_app_namespaces, expected_type=type_hints["additional_app_namespaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_app_namespaces is not None:
            self._values["additional_app_namespaces"] = additional_app_namespaces

    @builtins.property
    def additional_app_namespaces(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#additional_app_namespaces OceanSpark#additional_app_namespaces}.'''
        result = self._values.get("additional_app_namespaces")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkSpark(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkSparkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkSparkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b0c6c0e656cdc0e6e74ba02cc9f447fc11f59395b33daa7c5fc1c8862197c39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAdditionalAppNamespaces")
    def reset_additional_app_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalAppNamespaces", []))

    @builtins.property
    @jsii.member(jsii_name="additionalAppNamespacesInput")
    def additional_app_namespaces_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "additionalAppNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="additionalAppNamespaces")
    def additional_app_namespaces(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalAppNamespaces"))

    @additional_app_namespaces.setter
    def additional_app_namespaces(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e707824e5405ff3cd1596c4ee61db254f85eafe00a376e4312de073a2690c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalAppNamespaces", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkSpark]:
        return typing.cast(typing.Optional[OceanSparkSpark], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanSparkSpark]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f921376bdbad90f8cb0f8394698b7fb328ed043cb4c3deb339bb2dd5db1d9b7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWebhook",
    jsii_struct_bases=[],
    name_mapping={
        "host_network_ports": "hostNetworkPorts",
        "use_host_network": "useHostNetwork",
    },
)
class OceanSparkWebhook:
    def __init__(
        self,
        *,
        host_network_ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        use_host_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param host_network_ports: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#host_network_ports OceanSpark#host_network_ports}.
        :param use_host_network: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#use_host_network OceanSpark#use_host_network}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2b53f4137a911f81713ecd8268cd2c17403b2a0b71d0d3f7497a6d4b3cad3d3)
            check_type(argname="argument host_network_ports", value=host_network_ports, expected_type=type_hints["host_network_ports"])
            check_type(argname="argument use_host_network", value=use_host_network, expected_type=type_hints["use_host_network"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host_network_ports is not None:
            self._values["host_network_ports"] = host_network_ports
        if use_host_network is not None:
            self._values["use_host_network"] = use_host_network

    @builtins.property
    def host_network_ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#host_network_ports OceanSpark#host_network_ports}.'''
        result = self._values.get("host_network_ports")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def use_host_network(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#use_host_network OceanSpark#use_host_network}.'''
        result = self._values.get("use_host_network")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkWebhook(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkWebhookOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWebhookOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__673b5210c45ad569a30540f938831dfa5319cd89c32932a1a897ea731cf02477)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHostNetworkPorts")
    def reset_host_network_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostNetworkPorts", []))

    @jsii.member(jsii_name="resetUseHostNetwork")
    def reset_use_host_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseHostNetwork", []))

    @builtins.property
    @jsii.member(jsii_name="hostNetworkPortsInput")
    def host_network_ports_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "hostNetworkPortsInput"))

    @builtins.property
    @jsii.member(jsii_name="useHostNetworkInput")
    def use_host_network_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useHostNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="hostNetworkPorts")
    def host_network_ports(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "hostNetworkPorts"))

    @host_network_ports.setter
    def host_network_ports(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c85068950eed6650371d2c335401c7484bc6e699ed784bc77ec93dbdddde00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostNetworkPorts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useHostNetwork")
    def use_host_network(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useHostNetwork"))

    @use_host_network.setter
    def use_host_network(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30f5f97374774e9db52e91761d42bb0d9b260e7da8704ed6ac781d60bf026267)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useHostNetwork", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkWebhook]:
        return typing.cast(typing.Optional[OceanSparkWebhook], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanSparkWebhook]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5490bde79ee9ad254ebd6f217b52adf5ad6f6df56c74966cf9989928cc1f523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWorkspaces",
    jsii_struct_bases=[],
    name_mapping={"storage": "storage"},
)
class OceanSparkWorkspaces:
    def __init__(
        self,
        *,
        storage: typing.Optional[typing.Union["OceanSparkWorkspacesStorage", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param storage: storage block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#storage OceanSpark#storage}
        '''
        if isinstance(storage, dict):
            storage = OceanSparkWorkspacesStorage(**storage)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0da322c9638d43369eb2236ed942e2ab88084683079634a4a5f2d5b931acdf26)
            check_type(argname="argument storage", value=storage, expected_type=type_hints["storage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage is not None:
            self._values["storage"] = storage

    @builtins.property
    def storage(self) -> typing.Optional["OceanSparkWorkspacesStorage"]:
        '''storage block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#storage OceanSpark#storage}
        '''
        result = self._values.get("storage")
        return typing.cast(typing.Optional["OceanSparkWorkspacesStorage"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkWorkspaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkWorkspacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWorkspacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14a446ce1fd241edd95c0df59eb2160964230a2cd53b42c175f2aa67c80ff4c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putStorage")
    def put_storage(
        self,
        *,
        defaults: typing.Optional[typing.Union["OceanSparkWorkspacesStorageDefaults", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param defaults: defaults block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#defaults OceanSpark#defaults}
        '''
        value = OceanSparkWorkspacesStorage(defaults=defaults)

        return typing.cast(None, jsii.invoke(self, "putStorage", [value]))

    @jsii.member(jsii_name="resetStorage")
    def reset_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorage", []))

    @builtins.property
    @jsii.member(jsii_name="storage")
    def storage(self) -> "OceanSparkWorkspacesStorageOutputReference":
        return typing.cast("OceanSparkWorkspacesStorageOutputReference", jsii.get(self, "storage"))

    @builtins.property
    @jsii.member(jsii_name="storageInput")
    def storage_input(self) -> typing.Optional["OceanSparkWorkspacesStorage"]:
        return typing.cast(typing.Optional["OceanSparkWorkspacesStorage"], jsii.get(self, "storageInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkWorkspaces]:
        return typing.cast(typing.Optional[OceanSparkWorkspaces], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanSparkWorkspaces]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__698808147a11fe3f0c9a70fd728f2afd46abb4298d80d6a7e1784b729906b734)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWorkspacesStorage",
    jsii_struct_bases=[],
    name_mapping={"defaults": "defaults"},
)
class OceanSparkWorkspacesStorage:
    def __init__(
        self,
        *,
        defaults: typing.Optional[typing.Union["OceanSparkWorkspacesStorageDefaults", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param defaults: defaults block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#defaults OceanSpark#defaults}
        '''
        if isinstance(defaults, dict):
            defaults = OceanSparkWorkspacesStorageDefaults(**defaults)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543e3bcfee7ec6c440a6d63f3d9cad49018f4527cf4e3a551c58765976ba7ae6)
            check_type(argname="argument defaults", value=defaults, expected_type=type_hints["defaults"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if defaults is not None:
            self._values["defaults"] = defaults

    @builtins.property
    def defaults(self) -> typing.Optional["OceanSparkWorkspacesStorageDefaults"]:
        '''defaults block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#defaults OceanSpark#defaults}
        '''
        result = self._values.get("defaults")
        return typing.cast(typing.Optional["OceanSparkWorkspacesStorageDefaults"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkWorkspacesStorage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWorkspacesStorageDefaults",
    jsii_struct_bases=[],
    name_mapping={"storage_class_name": "storageClassName"},
)
class OceanSparkWorkspacesStorageDefaults:
    def __init__(
        self,
        *,
        storage_class_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_class_name: The name of the persistent volume storage class to use by default for new workspaces. Leave it empty to use the cluster defaults. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#storage_class_name OceanSpark#storage_class_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4ee3adceec5e2c2ec64c8d43b28076a0923d7ee4574985bd58a6c28258ac8ac)
            check_type(argname="argument storage_class_name", value=storage_class_name, expected_type=type_hints["storage_class_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if storage_class_name is not None:
            self._values["storage_class_name"] = storage_class_name

    @builtins.property
    def storage_class_name(self) -> typing.Optional[builtins.str]:
        '''The name of the persistent volume storage class to use by default for new workspaces.

        Leave it empty to use the cluster defaults.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#storage_class_name OceanSpark#storage_class_name}
        '''
        result = self._values.get("storage_class_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanSparkWorkspacesStorageDefaults(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanSparkWorkspacesStorageDefaultsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWorkspacesStorageDefaultsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f1b5c76c5967032075e69f3910301fea147416a1eed67146577a4170ed0903d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetStorageClassName")
    def reset_storage_class_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClassName", []))

    @builtins.property
    @jsii.member(jsii_name="storageClassNameInput")
    def storage_class_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassNameInput"))

    @builtins.property
    @jsii.member(jsii_name="storageClassName")
    def storage_class_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClassName"))

    @storage_class_name.setter
    def storage_class_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4b4ab0e69729cf50cffaf854851089a52cff5713e252dfb8df0e2fc8762b71e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageClassName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkWorkspacesStorageDefaults]:
        return typing.cast(typing.Optional[OceanSparkWorkspacesStorageDefaults], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanSparkWorkspacesStorageDefaults],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__101ef61729ffe8f51af0c668ba58da5043ba79158f8ac0dd552ffbad65fb43de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanSparkWorkspacesStorageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanSpark.OceanSparkWorkspacesStorageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26d6e30523e3a4b0ce5fb754fe4928187568998709f3f3bf839ef61d34e4e921)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDefaults")
    def put_defaults(
        self,
        *,
        storage_class_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param storage_class_name: The name of the persistent volume storage class to use by default for new workspaces. Leave it empty to use the cluster defaults. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_spark#storage_class_name OceanSpark#storage_class_name}
        '''
        value = OceanSparkWorkspacesStorageDefaults(
            storage_class_name=storage_class_name
        )

        return typing.cast(None, jsii.invoke(self, "putDefaults", [value]))

    @jsii.member(jsii_name="resetDefaults")
    def reset_defaults(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaults", []))

    @builtins.property
    @jsii.member(jsii_name="defaults")
    def defaults(self) -> OceanSparkWorkspacesStorageDefaultsOutputReference:
        return typing.cast(OceanSparkWorkspacesStorageDefaultsOutputReference, jsii.get(self, "defaults"))

    @builtins.property
    @jsii.member(jsii_name="defaultsInput")
    def defaults_input(self) -> typing.Optional[OceanSparkWorkspacesStorageDefaults]:
        return typing.cast(typing.Optional[OceanSparkWorkspacesStorageDefaults], jsii.get(self, "defaultsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanSparkWorkspacesStorage]:
        return typing.cast(typing.Optional[OceanSparkWorkspacesStorage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanSparkWorkspacesStorage],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac452fd62dccea655318ef4c1cf2b26bdb815e83f12249400b7625d3de68821)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanSpark",
    "OceanSparkCompute",
    "OceanSparkComputeOutputReference",
    "OceanSparkConfig",
    "OceanSparkIngress",
    "OceanSparkIngressController",
    "OceanSparkIngressControllerOutputReference",
    "OceanSparkIngressCustomEndpoint",
    "OceanSparkIngressCustomEndpointOutputReference",
    "OceanSparkIngressLoadBalancer",
    "OceanSparkIngressLoadBalancerOutputReference",
    "OceanSparkIngressOutputReference",
    "OceanSparkIngressPrivateLink",
    "OceanSparkIngressPrivateLinkOutputReference",
    "OceanSparkLogCollection",
    "OceanSparkLogCollectionOutputReference",
    "OceanSparkSpark",
    "OceanSparkSparkOutputReference",
    "OceanSparkWebhook",
    "OceanSparkWebhookOutputReference",
    "OceanSparkWorkspaces",
    "OceanSparkWorkspacesOutputReference",
    "OceanSparkWorkspacesStorage",
    "OceanSparkWorkspacesStorageDefaults",
    "OceanSparkWorkspacesStorageDefaultsOutputReference",
    "OceanSparkWorkspacesStorageOutputReference",
]

publication.publish()

def _typecheckingstub__e1b1c4bc9ac16a6f54df9d8f9743a0efcb7223d78fdd53130efcce6d47647516(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    ocean_cluster_id: builtins.str,
    compute: typing.Optional[typing.Union[OceanSparkCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    ingress: typing.Optional[typing.Union[OceanSparkIngress, typing.Dict[builtins.str, typing.Any]]] = None,
    log_collection: typing.Optional[typing.Union[OceanSparkLogCollection, typing.Dict[builtins.str, typing.Any]]] = None,
    spark: typing.Optional[typing.Union[OceanSparkSpark, typing.Dict[builtins.str, typing.Any]]] = None,
    webhook: typing.Optional[typing.Union[OceanSparkWebhook, typing.Dict[builtins.str, typing.Any]]] = None,
    workspaces: typing.Optional[typing.Union[OceanSparkWorkspaces, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__ad0407ed141bf93f77d1afb7db4937fd72d9602f61e000d8fd0809da9c23adf3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b32cd9ea2665f1a0867bedb774891dadb71a815890ed20dfd2031817470ec487(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b299987c1a8811030b1d82669490ad6d7fd08c05926a07f7b4f656e45a3d3c5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4610e707f0aec1c278f0e97e6035d36c402df29450a80faca8bfb3143ad81bc0(
    *,
    create_vngs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_taints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d5e7afd8c4e0e72437877e8576b6261784cab053dd5d3b592d387d621ae0fdf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08a8ae314062aa8240f6cb20a43e7ff33d16c4118192f34e5ebda661b97b0ae8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5420a67ca502f78424546a0db5af1f2d88b4b19ca46d80c6f5a5e891d9472fd0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38263ed7004c6a7e41dc42b95b20d94e3f657fb9bab67ce31efc5277889e35d8(
    value: typing.Optional[OceanSparkCompute],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286ba412bd73327f01a051d064e2c7c310afd50b3674fc79fe0a7cedf108e461(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ocean_cluster_id: builtins.str,
    compute: typing.Optional[typing.Union[OceanSparkCompute, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    ingress: typing.Optional[typing.Union[OceanSparkIngress, typing.Dict[builtins.str, typing.Any]]] = None,
    log_collection: typing.Optional[typing.Union[OceanSparkLogCollection, typing.Dict[builtins.str, typing.Any]]] = None,
    spark: typing.Optional[typing.Union[OceanSparkSpark, typing.Dict[builtins.str, typing.Any]]] = None,
    webhook: typing.Optional[typing.Union[OceanSparkWebhook, typing.Dict[builtins.str, typing.Any]]] = None,
    workspaces: typing.Optional[typing.Union[OceanSparkWorkspaces, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd91c4f0dc4e99a521b8c57bef0287eccf40665d7b8ddff0bd024aa3d5bb839(
    *,
    controller: typing.Optional[typing.Union[OceanSparkIngressController, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_endpoint: typing.Optional[typing.Union[OceanSparkIngressCustomEndpoint, typing.Dict[builtins.str, typing.Any]]] = None,
    load_balancer: typing.Optional[typing.Union[OceanSparkIngressLoadBalancer, typing.Dict[builtins.str, typing.Any]]] = None,
    private_link: typing.Optional[typing.Union[OceanSparkIngressPrivateLink, typing.Dict[builtins.str, typing.Any]]] = None,
    service_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dca300324ce13da691bbeb9939026393581a6ad92015ece5b09f994253dc87d(
    *,
    managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__293c89d5f8265f0a37925038caece2c31fe0a6d81d25272bc83a549f1edcb8d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65f3459a15fd2a6de964532cca0e494e2f420de4d6dcd70e9e84ddc099998ee5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f991ddbe6d7a00d046b1a643d517931d8fa30911a363d2c1a754153c7dfa041(
    value: typing.Optional[OceanSparkIngressController],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4274454c2a1090fb2b92c80e6303460866fe17dc9703906b9153af36e79f0575(
    *,
    address: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1075dbf235403b5a8dc1753d0b2dbd835a0790caa658d7a173d171e7fab34419(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27a24c4341e81756286a0ccac764cb2f56e68ea8e564361ac0d6d42f4408cbae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__116bc2f7c4a5a8a036f27b658d5d98d6d598f29d1f7de1a3c58f8a6a8bd5fb01(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6057c7fcbb7ebc0b977b940287533aedc90232655b67b97b837e87a06c98676(
    value: typing.Optional[OceanSparkIngressCustomEndpoint],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d186486fad538bf434179575983f09e6e4cc3a8c7bcb5dc7102b2996282515(
    *,
    managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    target_group_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b646e99451f2437448d310a0fedd858d2779bacc075258e15b7040748e7603c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74fdd32484858c39b906c87af8ea190104c2450a206260430d891e280503b5a9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f8f77a34720538127313d52b23d1f29b061624a3ac923e24064b8625c798f6c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f159c85faacd74fb04dc621c7e6703ca5aabe65bdcec5aa07462e92f418f5e5c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f5b030ab7c3c03120be8d6eed5bb033da3e9474319c3e6749870b55427e3481(
    value: typing.Optional[OceanSparkIngressLoadBalancer],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__569deec9e54f5548e968442c4706220c8564b78b3eea4eb48d2dedc5390ad022(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79e7da0ff5541de73c8457c7f97f2dce548a7836f2f3821b4a7ddbc803da01c4(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__140556ab92fb5089d72e65115b4133e1945cc87570eef0b58ff11d3b25d2d848(
    value: typing.Optional[OceanSparkIngress],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31721d1717914f6d9f6c6fa563a5f6db92dd2b450d03a4129ca360c30f9671b8(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vpc_endpoint_service: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3650873b607e35a0a709518668b3d4b69630b461f0cf239ef97cfe2ca7cf86d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e588be73bc7ce6fec1cafaa2bbe0ac3f275fb08c48d06a1819144a23854ebcd8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e2dd4b25cee4321d0bb747e7f48cbddf727abed9b863dff173d1dda629ef6a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da31f828f9d620d13ac91ce36a2ab79692d4d2c1fc45a6094fd3b1f4c58f3bde(
    value: typing.Optional[OceanSparkIngressPrivateLink],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1ba6bc27cfd1ecfca0358d447573c0113e87f983c3f336a8a0be772dedb2ed(
    *,
    collect_app_logs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e710e6fa71a2a7a66cb7790b6a0dea16db687be22436bf5bf39e0385004fbc8e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23ce2953b6fd3c452f5fc3b0b2033e8d597f5f22238599fe2e02d729b600ec40(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea419c886dfcc4e29c02e6958edb55f40a9a3b4d65ffb7faa4315508de762d57(
    value: typing.Optional[OceanSparkLogCollection],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49dd84e45632094a51989ef27d50d1e3000a28253cf98398f4bb775073934a6e(
    *,
    additional_app_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b0c6c0e656cdc0e6e74ba02cc9f447fc11f59395b33daa7c5fc1c8862197c39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e707824e5405ff3cd1596c4ee61db254f85eafe00a376e4312de073a2690c7c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f921376bdbad90f8cb0f8394698b7fb328ed043cb4c3deb339bb2dd5db1d9b7f(
    value: typing.Optional[OceanSparkSpark],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2b53f4137a911f81713ecd8268cd2c17403b2a0b71d0d3f7497a6d4b3cad3d3(
    *,
    host_network_ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
    use_host_network: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__673b5210c45ad569a30540f938831dfa5319cd89c32932a1a897ea731cf02477(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89c85068950eed6650371d2c335401c7484bc6e699ed784bc77ec93dbdddde00(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30f5f97374774e9db52e91761d42bb0d9b260e7da8704ed6ac781d60bf026267(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5490bde79ee9ad254ebd6f217b52adf5ad6f6df56c74966cf9989928cc1f523(
    value: typing.Optional[OceanSparkWebhook],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0da322c9638d43369eb2236ed942e2ab88084683079634a4a5f2d5b931acdf26(
    *,
    storage: typing.Optional[typing.Union[OceanSparkWorkspacesStorage, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14a446ce1fd241edd95c0df59eb2160964230a2cd53b42c175f2aa67c80ff4c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__698808147a11fe3f0c9a70fd728f2afd46abb4298d80d6a7e1784b729906b734(
    value: typing.Optional[OceanSparkWorkspaces],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__543e3bcfee7ec6c440a6d63f3d9cad49018f4527cf4e3a551c58765976ba7ae6(
    *,
    defaults: typing.Optional[typing.Union[OceanSparkWorkspacesStorageDefaults, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4ee3adceec5e2c2ec64c8d43b28076a0923d7ee4574985bd58a6c28258ac8ac(
    *,
    storage_class_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f1b5c76c5967032075e69f3910301fea147416a1eed67146577a4170ed0903d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4b4ab0e69729cf50cffaf854851089a52cff5713e252dfb8df0e2fc8762b71e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101ef61729ffe8f51af0c668ba58da5043ba79158f8ac0dd552ffbad65fb43de(
    value: typing.Optional[OceanSparkWorkspacesStorageDefaults],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26d6e30523e3a4b0ce5fb754fe4928187568998709f3f3bf839ef61d34e4e921(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac452fd62dccea655318ef4c1cf2b26bdb815e83f12249400b7625d3de68821(
    value: typing.Optional[OceanSparkWorkspacesStorage],
) -> None:
    """Type checking stubs"""
    pass
