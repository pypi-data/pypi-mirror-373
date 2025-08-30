r'''
# `spotinst_ocean_aks_np`

Refer to the Terraform Registry for docs: [`spotinst_ocean_aks_np`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np).
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


class OceanAksNp(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNp",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np spotinst_ocean_aks_np}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        aks_cluster_name: builtins.str,
        aks_infrastructure_resource_group_name: builtins.str,
        aks_region: builtins.str,
        aks_resource_group_name: builtins.str,
        availability_zones: typing.Sequence[builtins.str],
        controller_cluster_id: builtins.str,
        name: builtins.str,
        autoscaler: typing.Optional[typing.Union["OceanAksNpAutoscaler", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filters: typing.Optional[typing.Union["OceanAksNpFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpHeadrooms", typing.Dict[builtins.str, typing.Any]]]]] = None,
        health: typing.Optional[typing.Union["OceanAksNpHealth", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        kubernetes_version: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpLinuxOsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        logging: typing.Optional[typing.Union["OceanAksNpLogging", typing.Dict[builtins.str, typing.Any]]] = None,
        max_count: typing.Optional[jsii.Number] = None,
        max_pods_per_node: typing.Optional[jsii.Number] = None,
        min_count: typing.Optional[jsii.Number] = None,
        os_disk_size_gb: typing.Optional[jsii.Number] = None,
        os_disk_type: typing.Optional[builtins.str] = None,
        os_sku: typing.Optional[builtins.str] = None,
        os_type: typing.Optional[builtins.str] = None,
        pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling: typing.Optional[typing.Union["OceanAksNpScheduling", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanAksNpUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vng_template_scheduling: typing.Optional[typing.Union["OceanAksNpVngTemplateScheduling", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np spotinst_ocean_aks_np} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aks_cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_cluster_name OceanAksNp#aks_cluster_name}.
        :param aks_infrastructure_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_infrastructure_resource_group_name OceanAksNp#aks_infrastructure_resource_group_name}.
        :param aks_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_region OceanAksNp#aks_region}.
        :param aks_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_resource_group_name OceanAksNp#aks_resource_group_name}.
        :param availability_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#availability_zones OceanAksNp#availability_zones}.
        :param controller_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#controller_cluster_id OceanAksNp#controller_cluster_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#name OceanAksNp#name}.
        :param autoscaler: autoscaler block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscaler OceanAksNp#autoscaler}
        :param enable_node_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#enable_node_public_ip OceanAksNp#enable_node_public_ip}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#fallback_to_ondemand OceanAksNp#fallback_to_ondemand}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#filters OceanAksNp#filters}
        :param headrooms: headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#headrooms OceanAksNp#headrooms}
        :param health: health block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#health OceanAksNp#health}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#id OceanAksNp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kubernetes_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#kubernetes_version OceanAksNp#kubernetes_version}.
        :param labels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#labels OceanAksNp#labels}.
        :param linux_os_config: linux_os_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#linux_os_config OceanAksNp#linux_os_config}
        :param logging: logging block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#logging OceanAksNp#logging}
        :param max_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_count OceanAksNp#max_count}.
        :param max_pods_per_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_pods_per_node OceanAksNp#max_pods_per_node}.
        :param min_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_count OceanAksNp#min_count}.
        :param os_disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_disk_size_gb OceanAksNp#os_disk_size_gb}.
        :param os_disk_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_disk_type OceanAksNp#os_disk_type}.
        :param os_sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_sku OceanAksNp#os_sku}.
        :param os_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_type OceanAksNp#os_type}.
        :param pod_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#pod_subnet_ids OceanAksNp#pod_subnet_ids}.
        :param scheduling: scheduling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#scheduling OceanAksNp#scheduling}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#spot_percentage OceanAksNp#spot_percentage}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#tags OceanAksNp#tags}.
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#taints OceanAksNp#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#update_policy OceanAksNp#update_policy}
        :param vnet_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vnet_subnet_ids OceanAksNp#vnet_subnet_ids}.
        :param vng_template_scheduling: vng_template_scheduling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_template_scheduling OceanAksNp#vng_template_scheduling}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__898ccbb93cd7b1a458d7f489d68c3366490a1abc47b94a9d60566b0529018fed)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanAksNpConfig(
            aks_cluster_name=aks_cluster_name,
            aks_infrastructure_resource_group_name=aks_infrastructure_resource_group_name,
            aks_region=aks_region,
            aks_resource_group_name=aks_resource_group_name,
            availability_zones=availability_zones,
            controller_cluster_id=controller_cluster_id,
            name=name,
            autoscaler=autoscaler,
            enable_node_public_ip=enable_node_public_ip,
            fallback_to_ondemand=fallback_to_ondemand,
            filters=filters,
            headrooms=headrooms,
            health=health,
            id=id,
            kubernetes_version=kubernetes_version,
            labels=labels,
            linux_os_config=linux_os_config,
            logging=logging,
            max_count=max_count,
            max_pods_per_node=max_pods_per_node,
            min_count=min_count,
            os_disk_size_gb=os_disk_size_gb,
            os_disk_type=os_disk_type,
            os_sku=os_sku,
            os_type=os_type,
            pod_subnet_ids=pod_subnet_ids,
            scheduling=scheduling,
            spot_percentage=spot_percentage,
            tags=tags,
            taints=taints,
            update_policy=update_policy,
            vnet_subnet_ids=vnet_subnet_ids,
            vng_template_scheduling=vng_template_scheduling,
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
        '''Generates CDKTF code for importing a OceanAksNp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanAksNp to import.
        :param import_from_id: The id of the existing OceanAksNp that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanAksNp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__093d761e9ff01af6c29b326f08730e5c36753a8fb0dd64b7126b262010496297)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAutoscaler")
    def put_autoscaler(
        self,
        *,
        autoscale_down: typing.Optional[typing.Union["OceanAksNpAutoscalerAutoscaleDown", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_headroom: typing.Optional[typing.Union["OceanAksNpAutoscalerAutoscaleHeadroom", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        resource_limits: typing.Optional[typing.Union["OceanAksNpAutoscalerResourceLimits", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param autoscale_down: autoscale_down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_down OceanAksNp#autoscale_down}
        :param autoscale_headroom: autoscale_headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_headroom OceanAksNp#autoscale_headroom}
        :param autoscale_is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_is_enabled OceanAksNp#autoscale_is_enabled}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#resource_limits OceanAksNp#resource_limits}
        '''
        value = OceanAksNpAutoscaler(
            autoscale_down=autoscale_down,
            autoscale_headroom=autoscale_headroom,
            autoscale_is_enabled=autoscale_is_enabled,
            resource_limits=resource_limits,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscaler", [value]))

    @jsii.member(jsii_name="putFilters")
    def put_filters(
        self,
        *,
        accelerated_networking: typing.Optional[builtins.str] = None,
        architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
        disk_performance: typing.Optional[builtins.str] = None,
        exclude_series: typing.Optional[typing.Sequence[builtins.str]] = None,
        gpu_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_gpu: typing.Optional[jsii.Number] = None,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
        min_disk: typing.Optional[jsii.Number] = None,
        min_gpu: typing.Optional[jsii.Number] = None,
        min_memory_gib: typing.Optional[jsii.Number] = None,
        min_nics: typing.Optional[jsii.Number] = None,
        min_vcpu: typing.Optional[jsii.Number] = None,
        series: typing.Optional[typing.Sequence[builtins.str]] = None,
        vm_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param accelerated_networking: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#accelerated_networking OceanAksNp#accelerated_networking}.
        :param architectures: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#architectures OceanAksNp#architectures}.
        :param disk_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#disk_performance OceanAksNp#disk_performance}.
        :param exclude_series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#exclude_series OceanAksNp#exclude_series}.
        :param gpu_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#gpu_types OceanAksNp#gpu_types}.
        :param max_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_gpu OceanAksNp#max_gpu}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_memory_gib OceanAksNp#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_vcpu OceanAksNp#max_vcpu}.
        :param min_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_disk OceanAksNp#min_disk}.
        :param min_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_gpu OceanAksNp#min_gpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_memory_gib OceanAksNp#min_memory_gib}.
        :param min_nics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_nics OceanAksNp#min_nics}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_vcpu OceanAksNp#min_vcpu}.
        :param series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#series OceanAksNp#series}.
        :param vm_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vm_types OceanAksNp#vm_types}.
        '''
        value = OceanAksNpFilters(
            accelerated_networking=accelerated_networking,
            architectures=architectures,
            disk_performance=disk_performance,
            exclude_series=exclude_series,
            gpu_types=gpu_types,
            max_gpu=max_gpu,
            max_memory_gib=max_memory_gib,
            max_vcpu=max_vcpu,
            min_disk=min_disk,
            min_gpu=min_gpu,
            min_memory_gib=min_memory_gib,
            min_nics=min_nics,
            min_vcpu=min_vcpu,
            series=series,
            vm_types=vm_types,
        )

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

    @jsii.member(jsii_name="putHeadrooms")
    def put_headrooms(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpHeadrooms", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__284c374fcc23f7877c2e31bfa73cdbeb548c9a186476cd657442a94547da0842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHeadrooms", [value]))

    @jsii.member(jsii_name="putHealth")
    def put_health(self, *, grace_period: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#grace_period OceanAksNp#grace_period}.
        '''
        value = OceanAksNpHealth(grace_period=grace_period)

        return typing.cast(None, jsii.invoke(self, "putHealth", [value]))

    @jsii.member(jsii_name="putLinuxOsConfig")
    def put_linux_os_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpLinuxOsConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4846e4e0da5bd72cf696ff4fa4e0d78663ebc9ab07e6088be3f038108cf10b68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLinuxOsConfig", [value]))

    @jsii.member(jsii_name="putLogging")
    def put_logging(
        self,
        *,
        export: typing.Optional[typing.Union["OceanAksNpLoggingExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param export: export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#export OceanAksNp#export}
        '''
        value = OceanAksNpLogging(export=export)

        return typing.cast(None, jsii.invoke(self, "putLogging", [value]))

    @jsii.member(jsii_name="putScheduling")
    def put_scheduling(
        self,
        *,
        shutdown_hours: typing.Optional[typing.Union["OceanAksNpSchedulingShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
        suspension_hours: typing.Optional[typing.Union["OceanAksNpSchedulingSuspensionHours", typing.Dict[builtins.str, typing.Any]]] = None,
        tasks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpSchedulingTasks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param shutdown_hours: shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#shutdown_hours OceanAksNp#shutdown_hours}
        :param suspension_hours: suspension_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#suspension_hours OceanAksNp#suspension_hours}
        :param tasks: tasks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#tasks OceanAksNp#tasks}
        '''
        value = OceanAksNpScheduling(
            shutdown_hours=shutdown_hours,
            suspension_hours=suspension_hours,
            tasks=tasks,
        )

        return typing.cast(None, jsii.invoke(self, "putScheduling", [value]))

    @jsii.member(jsii_name="putTaints")
    def put_taints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpTaints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52fcc7c22e4bac75dfaf5872709d568cac573e3dd5764f65ad904b1247fd2db3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaints", [value]))

    @jsii.member(jsii_name="putUpdatePolicy")
    def put_update_policy(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_config: typing.Optional[typing.Union["OceanAksNpUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#should_roll OceanAksNp#should_roll}.
        :param conditioned_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#conditioned_roll OceanAksNp#conditioned_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#roll_config OceanAksNp#roll_config}
        '''
        value = OceanAksNpUpdatePolicy(
            should_roll=should_roll,
            conditioned_roll=conditioned_roll,
            roll_config=roll_config,
        )

        return typing.cast(None, jsii.invoke(self, "putUpdatePolicy", [value]))

    @jsii.member(jsii_name="putVngTemplateScheduling")
    def put_vng_template_scheduling(
        self,
        *,
        vng_template_shutdown_hours: typing.Optional[typing.Union["OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param vng_template_shutdown_hours: vng_template_shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_template_shutdown_hours OceanAksNp#vng_template_shutdown_hours}
        '''
        value = OceanAksNpVngTemplateScheduling(
            vng_template_shutdown_hours=vng_template_shutdown_hours
        )

        return typing.cast(None, jsii.invoke(self, "putVngTemplateScheduling", [value]))

    @jsii.member(jsii_name="resetAutoscaler")
    def reset_autoscaler(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaler", []))

    @jsii.member(jsii_name="resetEnableNodePublicIp")
    def reset_enable_node_public_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableNodePublicIp", []))

    @jsii.member(jsii_name="resetFallbackToOndemand")
    def reset_fallback_to_ondemand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallbackToOndemand", []))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

    @jsii.member(jsii_name="resetHeadrooms")
    def reset_headrooms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeadrooms", []))

    @jsii.member(jsii_name="resetHealth")
    def reset_health(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealth", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKubernetesVersion")
    def reset_kubernetes_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKubernetesVersion", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetLinuxOsConfig")
    def reset_linux_os_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinuxOsConfig", []))

    @jsii.member(jsii_name="resetLogging")
    def reset_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogging", []))

    @jsii.member(jsii_name="resetMaxCount")
    def reset_max_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCount", []))

    @jsii.member(jsii_name="resetMaxPodsPerNode")
    def reset_max_pods_per_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPodsPerNode", []))

    @jsii.member(jsii_name="resetMinCount")
    def reset_min_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCount", []))

    @jsii.member(jsii_name="resetOsDiskSizeGb")
    def reset_os_disk_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDiskSizeGb", []))

    @jsii.member(jsii_name="resetOsDiskType")
    def reset_os_disk_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDiskType", []))

    @jsii.member(jsii_name="resetOsSku")
    def reset_os_sku(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsSku", []))

    @jsii.member(jsii_name="resetOsType")
    def reset_os_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsType", []))

    @jsii.member(jsii_name="resetPodSubnetIds")
    def reset_pod_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPodSubnetIds", []))

    @jsii.member(jsii_name="resetScheduling")
    def reset_scheduling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduling", []))

    @jsii.member(jsii_name="resetSpotPercentage")
    def reset_spot_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotPercentage", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTaints")
    def reset_taints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaints", []))

    @jsii.member(jsii_name="resetUpdatePolicy")
    def reset_update_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatePolicy", []))

    @jsii.member(jsii_name="resetVnetSubnetIds")
    def reset_vnet_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVnetSubnetIds", []))

    @jsii.member(jsii_name="resetVngTemplateScheduling")
    def reset_vng_template_scheduling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVngTemplateScheduling", []))

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
    @jsii.member(jsii_name="autoscaler")
    def autoscaler(self) -> "OceanAksNpAutoscalerOutputReference":
        return typing.cast("OceanAksNpAutoscalerOutputReference", jsii.get(self, "autoscaler"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> "OceanAksNpFiltersOutputReference":
        return typing.cast("OceanAksNpFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="headrooms")
    def headrooms(self) -> "OceanAksNpHeadroomsList":
        return typing.cast("OceanAksNpHeadroomsList", jsii.get(self, "headrooms"))

    @builtins.property
    @jsii.member(jsii_name="health")
    def health(self) -> "OceanAksNpHealthOutputReference":
        return typing.cast("OceanAksNpHealthOutputReference", jsii.get(self, "health"))

    @builtins.property
    @jsii.member(jsii_name="linuxOsConfig")
    def linux_os_config(self) -> "OceanAksNpLinuxOsConfigList":
        return typing.cast("OceanAksNpLinuxOsConfigList", jsii.get(self, "linuxOsConfig"))

    @builtins.property
    @jsii.member(jsii_name="logging")
    def logging(self) -> "OceanAksNpLoggingOutputReference":
        return typing.cast("OceanAksNpLoggingOutputReference", jsii.get(self, "logging"))

    @builtins.property
    @jsii.member(jsii_name="scheduling")
    def scheduling(self) -> "OceanAksNpSchedulingOutputReference":
        return typing.cast("OceanAksNpSchedulingOutputReference", jsii.get(self, "scheduling"))

    @builtins.property
    @jsii.member(jsii_name="taints")
    def taints(self) -> "OceanAksNpTaintsList":
        return typing.cast("OceanAksNpTaintsList", jsii.get(self, "taints"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> "OceanAksNpUpdatePolicyOutputReference":
        return typing.cast("OceanAksNpUpdatePolicyOutputReference", jsii.get(self, "updatePolicy"))

    @builtins.property
    @jsii.member(jsii_name="vngTemplateScheduling")
    def vng_template_scheduling(
        self,
    ) -> "OceanAksNpVngTemplateSchedulingOutputReference":
        return typing.cast("OceanAksNpVngTemplateSchedulingOutputReference", jsii.get(self, "vngTemplateScheduling"))

    @builtins.property
    @jsii.member(jsii_name="aksClusterNameInput")
    def aks_cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aksClusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="aksInfrastructureResourceGroupNameInput")
    def aks_infrastructure_resource_group_name_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aksInfrastructureResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="aksRegionInput")
    def aks_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aksRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="aksResourceGroupNameInput")
    def aks_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aksResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscalerInput")
    def autoscaler_input(self) -> typing.Optional["OceanAksNpAutoscaler"]:
        return typing.cast(typing.Optional["OceanAksNpAutoscaler"], jsii.get(self, "autoscalerInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZonesInput")
    def availability_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZonesInput"))

    @builtins.property
    @jsii.member(jsii_name="controllerClusterIdInput")
    def controller_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "controllerClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enableNodePublicIpInput")
    def enable_node_public_ip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableNodePublicIpInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackToOndemandInput")
    def fallback_to_ondemand_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackToOndemandInput"))

    @builtins.property
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional["OceanAksNpFilters"]:
        return typing.cast(typing.Optional["OceanAksNpFilters"], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="headroomsInput")
    def headrooms_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpHeadrooms"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpHeadrooms"]]], jsii.get(self, "headroomsInput"))

    @builtins.property
    @jsii.member(jsii_name="healthInput")
    def health_input(self) -> typing.Optional["OceanAksNpHealth"]:
        return typing.cast(typing.Optional["OceanAksNpHealth"], jsii.get(self, "healthInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="kubernetesVersionInput")
    def kubernetes_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kubernetesVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="linuxOsConfigInput")
    def linux_os_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfig"]]], jsii.get(self, "linuxOsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="loggingInput")
    def logging_input(self) -> typing.Optional["OceanAksNpLogging"]:
        return typing.cast(typing.Optional["OceanAksNpLogging"], jsii.get(self, "loggingInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCountInput")
    def max_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCountInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPodsPerNodeInput")
    def max_pods_per_node_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPodsPerNodeInput"))

    @builtins.property
    @jsii.member(jsii_name="minCountInput")
    def min_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="osDiskSizeGbInput")
    def os_disk_size_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "osDiskSizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="osDiskTypeInput")
    def os_disk_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osDiskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="osSkuInput")
    def os_sku_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osSkuInput"))

    @builtins.property
    @jsii.member(jsii_name="osTypeInput")
    def os_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="podSubnetIdsInput")
    def pod_subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "podSubnetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="schedulingInput")
    def scheduling_input(self) -> typing.Optional["OceanAksNpScheduling"]:
        return typing.cast(typing.Optional["OceanAksNpScheduling"], jsii.get(self, "schedulingInput"))

    @builtins.property
    @jsii.member(jsii_name="spotPercentageInput")
    def spot_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="taintsInput")
    def taints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpTaints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpTaints"]]], jsii.get(self, "taintsInput"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicyInput")
    def update_policy_input(self) -> typing.Optional["OceanAksNpUpdatePolicy"]:
        return typing.cast(typing.Optional["OceanAksNpUpdatePolicy"], jsii.get(self, "updatePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="vnetSubnetIdsInput")
    def vnet_subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vnetSubnetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="vngTemplateSchedulingInput")
    def vng_template_scheduling_input(
        self,
    ) -> typing.Optional["OceanAksNpVngTemplateScheduling"]:
        return typing.cast(typing.Optional["OceanAksNpVngTemplateScheduling"], jsii.get(self, "vngTemplateSchedulingInput"))

    @builtins.property
    @jsii.member(jsii_name="aksClusterName")
    def aks_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aksClusterName"))

    @aks_cluster_name.setter
    def aks_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62a5844e745d3dc3bc50168b6d11d932a24790b381febdd79aa3acdba95594ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aksClusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aksInfrastructureResourceGroupName")
    def aks_infrastructure_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aksInfrastructureResourceGroupName"))

    @aks_infrastructure_resource_group_name.setter
    def aks_infrastructure_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea69ad8644dd89aa463fc85d07e524019a06a1cc120da1e5987046a167466f62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aksInfrastructureResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aksRegion")
    def aks_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aksRegion"))

    @aks_region.setter
    def aks_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75ec4fefd2f1d7c22a01397d06dae7fd932b7d24c5aed9becabb675f4a845d80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aksRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aksResourceGroupName")
    def aks_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aksResourceGroupName"))

    @aks_resource_group_name.setter
    def aks_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6179ec6fb80c523d3bbccb2b6580f1f29112d47edae838bd46f35883dbc7999)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aksResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__277c847b46190413d77cdd0ec9934c355c98b40f731ac2beba195207710617de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZones", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="controllerClusterId")
    def controller_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "controllerClusterId"))

    @controller_cluster_id.setter
    def controller_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f37accc031cfce63d2dede6fb5e99addd1ffafe921af10c1d3bded64a9f38de0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "controllerClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableNodePublicIp")
    def enable_node_public_ip(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableNodePublicIp"))

    @enable_node_public_ip.setter
    def enable_node_public_ip(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44df0c8a8822bc1dcd738c59f5a3909445fb3aec5820edabc5722192d5a098ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableNodePublicIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallbackToOndemand")
    def fallback_to_ondemand(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "fallbackToOndemand"))

    @fallback_to_ondemand.setter
    def fallback_to_ondemand(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d7b35b0a5c743235e1ae0ff043dc3e570e58168eb4e23805c4af0d49d26b1e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackToOndemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d260296295b25370fc455d1d4c9a607901c5cf42dacfb779bcb1e0557886d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kubernetesVersion")
    def kubernetes_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kubernetesVersion"))

    @kubernetes_version.setter
    def kubernetes_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f205fc97059e2e675db7cd66935260bb789b418a7ef2c5000f834971da7bade1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kubernetesVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf3021f2aa21020ec377f6d47e7e39dca0e27337a2fb5afa335f86be5f073cb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCount")
    def max_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCount"))

    @max_count.setter
    def max_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47778ca946ad4ccfe14cfe5ae2a85cfc6c161788aed5f8697d1e4718505439ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPodsPerNode")
    def max_pods_per_node(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPodsPerNode"))

    @max_pods_per_node.setter
    def max_pods_per_node(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88419e6c825defaa4ac92fe1c20480259588dc45277611521e2a183eae035a71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPodsPerNode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCount")
    def min_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minCount"))

    @min_count.setter
    def min_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a87ed622c0b11d0f2b346ba0ec6761aba7c644142354bfcc76466be4f28f1469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b336cc34e01b20430edee7becd47c00b9fd1e4f8dce0b2d9d4f5944aee8b153)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDiskSizeGb")
    def os_disk_size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "osDiskSizeGb"))

    @os_disk_size_gb.setter
    def os_disk_size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5297b4865bb4041d494b256e9a6a1ca46517024b5172258ef6a2adce38ce5bc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDiskSizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDiskType")
    def os_disk_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osDiskType"))

    @os_disk_type.setter
    def os_disk_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e34a9a6875fb6e0b20bd147f857ece0bffef93a279e097c559567a1dddef51d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDiskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osSku")
    def os_sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osSku"))

    @os_sku.setter
    def os_sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__338e5f41b3606d67e98979a8864305bbbe7e85e06153bc623a1c7529c0c3fea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osSku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osType")
    def os_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osType"))

    @os_type.setter
    def os_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a405be31d799aaa7a83bbb92dabe9622e3cfbc1cbfe473d34a12036422aa9abb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="podSubnetIds")
    def pod_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "podSubnetIds"))

    @pod_subnet_ids.setter
    def pod_subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2700fe40b6d36c8434590c3f6ef6baa3aec9ef2047c6436cf82c24ee381dc66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "podSubnetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotPercentage")
    def spot_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotPercentage"))

    @spot_percentage.setter
    def spot_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a17ecd73e9618bd166376ebe256e68840e49d45a403e6fcbabf779f0417e2a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f840978c379636cb42b7cfb9b618103389df7c9747536fdc06b6cede3362a1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vnetSubnetIds")
    def vnet_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vnetSubnetIds"))

    @vnet_subnet_ids.setter
    def vnet_subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614fd26df3d39f418b33abda3525bfa2b90a8d383a6a710b43bc7048e7e91ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vnetSubnetIds", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscaler",
    jsii_struct_bases=[],
    name_mapping={
        "autoscale_down": "autoscaleDown",
        "autoscale_headroom": "autoscaleHeadroom",
        "autoscale_is_enabled": "autoscaleIsEnabled",
        "resource_limits": "resourceLimits",
    },
)
class OceanAksNpAutoscaler:
    def __init__(
        self,
        *,
        autoscale_down: typing.Optional[typing.Union["OceanAksNpAutoscalerAutoscaleDown", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_headroom: typing.Optional[typing.Union["OceanAksNpAutoscalerAutoscaleHeadroom", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        resource_limits: typing.Optional[typing.Union["OceanAksNpAutoscalerResourceLimits", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param autoscale_down: autoscale_down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_down OceanAksNp#autoscale_down}
        :param autoscale_headroom: autoscale_headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_headroom OceanAksNp#autoscale_headroom}
        :param autoscale_is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_is_enabled OceanAksNp#autoscale_is_enabled}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#resource_limits OceanAksNp#resource_limits}
        '''
        if isinstance(autoscale_down, dict):
            autoscale_down = OceanAksNpAutoscalerAutoscaleDown(**autoscale_down)
        if isinstance(autoscale_headroom, dict):
            autoscale_headroom = OceanAksNpAutoscalerAutoscaleHeadroom(**autoscale_headroom)
        if isinstance(resource_limits, dict):
            resource_limits = OceanAksNpAutoscalerResourceLimits(**resource_limits)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acd5b84fed7b90a6e8df57726b3376ad4897744a5f1d3df74f1742a1eba4d2eb)
            check_type(argname="argument autoscale_down", value=autoscale_down, expected_type=type_hints["autoscale_down"])
            check_type(argname="argument autoscale_headroom", value=autoscale_headroom, expected_type=type_hints["autoscale_headroom"])
            check_type(argname="argument autoscale_is_enabled", value=autoscale_is_enabled, expected_type=type_hints["autoscale_is_enabled"])
            check_type(argname="argument resource_limits", value=resource_limits, expected_type=type_hints["resource_limits"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if autoscale_down is not None:
            self._values["autoscale_down"] = autoscale_down
        if autoscale_headroom is not None:
            self._values["autoscale_headroom"] = autoscale_headroom
        if autoscale_is_enabled is not None:
            self._values["autoscale_is_enabled"] = autoscale_is_enabled
        if resource_limits is not None:
            self._values["resource_limits"] = resource_limits

    @builtins.property
    def autoscale_down(self) -> typing.Optional["OceanAksNpAutoscalerAutoscaleDown"]:
        '''autoscale_down block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_down OceanAksNp#autoscale_down}
        '''
        result = self._values.get("autoscale_down")
        return typing.cast(typing.Optional["OceanAksNpAutoscalerAutoscaleDown"], result)

    @builtins.property
    def autoscale_headroom(
        self,
    ) -> typing.Optional["OceanAksNpAutoscalerAutoscaleHeadroom"]:
        '''autoscale_headroom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_headroom OceanAksNp#autoscale_headroom}
        '''
        result = self._values.get("autoscale_headroom")
        return typing.cast(typing.Optional["OceanAksNpAutoscalerAutoscaleHeadroom"], result)

    @builtins.property
    def autoscale_is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscale_is_enabled OceanAksNp#autoscale_is_enabled}.'''
        result = self._values.get("autoscale_is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def resource_limits(self) -> typing.Optional["OceanAksNpAutoscalerResourceLimits"]:
        '''resource_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#resource_limits OceanAksNp#resource_limits}
        '''
        result = self._values.get("resource_limits")
        return typing.cast(typing.Optional["OceanAksNpAutoscalerResourceLimits"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpAutoscaler(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerAutoscaleDown",
    jsii_struct_bases=[],
    name_mapping={"max_scale_down_percentage": "maxScaleDownPercentage"},
)
class OceanAksNpAutoscalerAutoscaleDown:
    def __init__(
        self,
        *,
        max_scale_down_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_scale_down_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_scale_down_percentage OceanAksNp#max_scale_down_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90025a750dab1d36f316beb5c4d4bc277fb2fece46d0c095beee1b058f490a97)
            check_type(argname="argument max_scale_down_percentage", value=max_scale_down_percentage, expected_type=type_hints["max_scale_down_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_scale_down_percentage is not None:
            self._values["max_scale_down_percentage"] = max_scale_down_percentage

    @builtins.property
    def max_scale_down_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_scale_down_percentage OceanAksNp#max_scale_down_percentage}.'''
        result = self._values.get("max_scale_down_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpAutoscalerAutoscaleDown(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpAutoscalerAutoscaleDownOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerAutoscaleDownOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e323dc3d55845c8138edb6fa0ed07b64348d49458e8d173ad68cf23277bd56f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxScaleDownPercentage")
    def reset_max_scale_down_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxScaleDownPercentage", []))

    @builtins.property
    @jsii.member(jsii_name="maxScaleDownPercentageInput")
    def max_scale_down_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxScaleDownPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="maxScaleDownPercentage")
    def max_scale_down_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxScaleDownPercentage"))

    @max_scale_down_percentage.setter
    def max_scale_down_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e211cc7941a4f9d530dab9597943bd8cc3102383b1020c7ea5938be4144edea9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScaleDownPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpAutoscalerAutoscaleDown]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerAutoscaleDown], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpAutoscalerAutoscaleDown],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__694925ba377ee2297c478fa7de17a6028ae390c9b028bdb0ef21a8bbaf61cb13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerAutoscaleHeadroom",
    jsii_struct_bases=[],
    name_mapping={"automatic": "automatic"},
)
class OceanAksNpAutoscalerAutoscaleHeadroom:
    def __init__(
        self,
        *,
        automatic: typing.Optional[typing.Union["OceanAksNpAutoscalerAutoscaleHeadroomAutomatic", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param automatic: automatic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#automatic OceanAksNp#automatic}
        '''
        if isinstance(automatic, dict):
            automatic = OceanAksNpAutoscalerAutoscaleHeadroomAutomatic(**automatic)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f3500b9c60d85bcf43c8bfb06f8a67e246dfe5c2c75f4a0cf43faa35e91db9d)
            check_type(argname="argument automatic", value=automatic, expected_type=type_hints["automatic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automatic is not None:
            self._values["automatic"] = automatic

    @builtins.property
    def automatic(
        self,
    ) -> typing.Optional["OceanAksNpAutoscalerAutoscaleHeadroomAutomatic"]:
        '''automatic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#automatic OceanAksNp#automatic}
        '''
        result = self._values.get("automatic")
        return typing.cast(typing.Optional["OceanAksNpAutoscalerAutoscaleHeadroomAutomatic"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpAutoscalerAutoscaleHeadroom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerAutoscaleHeadroomAutomatic",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled", "percentage": "percentage"},
)
class OceanAksNpAutoscalerAutoscaleHeadroomAutomatic:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#percentage OceanAksNp#percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14a6682d5e28cfd7d5d2788a7f90a30240c46435e6bd6e853722b0c11de95fa6)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument percentage", value=percentage, expected_type=type_hints["percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if percentage is not None:
            self._values["percentage"] = percentage

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#percentage OceanAksNp#percentage}.'''
        result = self._values.get("percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpAutoscalerAutoscaleHeadroomAutomatic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpAutoscalerAutoscaleHeadroomAutomaticOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerAutoscaleHeadroomAutomaticOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__27b7cb40a358c82222c6e38ba5aa9b9f55f00ba74337ecd6896e5d1a62874cc0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetPercentage")
    def reset_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPercentage", []))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="percentageInput")
    def percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "percentageInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c1ab0ea7bfa62e8afc65122fab28247b4fee0be1089fce8c5c2f1ae5905554f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="percentage")
    def percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "percentage"))

    @percentage.setter
    def percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9164955a5ae0aada1ca6cee1a1ee85d69ad7c4686e4005350b5be4899038b9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "percentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59fbba227f6bd247ed11b119bc5e54ce48f5b9c7aec7d0646366479d2f94fc2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpAutoscalerAutoscaleHeadroomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerAutoscaleHeadroomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0919e878c242a679f4ee67c299f7c4bb7af254bbad557c02a1273830852f338)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutomatic")
    def put_automatic(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#percentage OceanAksNp#percentage}.
        '''
        value = OceanAksNpAutoscalerAutoscaleHeadroomAutomatic(
            is_enabled=is_enabled, percentage=percentage
        )

        return typing.cast(None, jsii.invoke(self, "putAutomatic", [value]))

    @jsii.member(jsii_name="resetAutomatic")
    def reset_automatic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomatic", []))

    @builtins.property
    @jsii.member(jsii_name="automatic")
    def automatic(
        self,
    ) -> OceanAksNpAutoscalerAutoscaleHeadroomAutomaticOutputReference:
        return typing.cast(OceanAksNpAutoscalerAutoscaleHeadroomAutomaticOutputReference, jsii.get(self, "automatic"))

    @builtins.property
    @jsii.member(jsii_name="automaticInput")
    def automatic_input(
        self,
    ) -> typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic], jsii.get(self, "automaticInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroom]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroom], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroom],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59c244f9824c5e7cb48ea4637399431e5bc70474602ca5922ee474962451c71e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpAutoscalerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c7b3548c7c7a2d7cf9ed3738e3162adc17b8b3086567472ad6ad6854c948256)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoscaleDown")
    def put_autoscale_down(
        self,
        *,
        max_scale_down_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_scale_down_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_scale_down_percentage OceanAksNp#max_scale_down_percentage}.
        '''
        value = OceanAksNpAutoscalerAutoscaleDown(
            max_scale_down_percentage=max_scale_down_percentage
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscaleDown", [value]))

    @jsii.member(jsii_name="putAutoscaleHeadroom")
    def put_autoscale_headroom(
        self,
        *,
        automatic: typing.Optional[typing.Union[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param automatic: automatic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#automatic OceanAksNp#automatic}
        '''
        value = OceanAksNpAutoscalerAutoscaleHeadroom(automatic=automatic)

        return typing.cast(None, jsii.invoke(self, "putAutoscaleHeadroom", [value]))

    @jsii.member(jsii_name="putResourceLimits")
    def put_resource_limits(
        self,
        *,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_memory_gib OceanAksNp#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_vcpu OceanAksNp#max_vcpu}.
        '''
        value = OceanAksNpAutoscalerResourceLimits(
            max_memory_gib=max_memory_gib, max_vcpu=max_vcpu
        )

        return typing.cast(None, jsii.invoke(self, "putResourceLimits", [value]))

    @jsii.member(jsii_name="resetAutoscaleDown")
    def reset_autoscale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleDown", []))

    @jsii.member(jsii_name="resetAutoscaleHeadroom")
    def reset_autoscale_headroom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleHeadroom", []))

    @jsii.member(jsii_name="resetAutoscaleIsEnabled")
    def reset_autoscale_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleIsEnabled", []))

    @jsii.member(jsii_name="resetResourceLimits")
    def reset_resource_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceLimits", []))

    @builtins.property
    @jsii.member(jsii_name="autoscaleDown")
    def autoscale_down(self) -> OceanAksNpAutoscalerAutoscaleDownOutputReference:
        return typing.cast(OceanAksNpAutoscalerAutoscaleDownOutputReference, jsii.get(self, "autoscaleDown"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroom")
    def autoscale_headroom(
        self,
    ) -> OceanAksNpAutoscalerAutoscaleHeadroomOutputReference:
        return typing.cast(OceanAksNpAutoscalerAutoscaleHeadroomOutputReference, jsii.get(self, "autoscaleHeadroom"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimits")
    def resource_limits(self) -> "OceanAksNpAutoscalerResourceLimitsOutputReference":
        return typing.cast("OceanAksNpAutoscalerResourceLimitsOutputReference", jsii.get(self, "resourceLimits"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleDownInput")
    def autoscale_down_input(
        self,
    ) -> typing.Optional[OceanAksNpAutoscalerAutoscaleDown]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerAutoscaleDown], jsii.get(self, "autoscaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomInput")
    def autoscale_headroom_input(
        self,
    ) -> typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroom]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroom], jsii.get(self, "autoscaleHeadroomInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleIsEnabledInput")
    def autoscale_is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoscaleIsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimitsInput")
    def resource_limits_input(
        self,
    ) -> typing.Optional["OceanAksNpAutoscalerResourceLimits"]:
        return typing.cast(typing.Optional["OceanAksNpAutoscalerResourceLimits"], jsii.get(self, "resourceLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleIsEnabled")
    def autoscale_is_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoscaleIsEnabled"))

    @autoscale_is_enabled.setter
    def autoscale_is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da55f0718b621653af224776827ca6681da47a8b7520c55d829dfaf411c63382)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoscaleIsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpAutoscaler]:
        return typing.cast(typing.Optional[OceanAksNpAutoscaler], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpAutoscaler]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1648c48e96a0709637e03dddcca11e4292b34ea0ae7e40867a72cc2e85b66e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerResourceLimits",
    jsii_struct_bases=[],
    name_mapping={"max_memory_gib": "maxMemoryGib", "max_vcpu": "maxVcpu"},
)
class OceanAksNpAutoscalerResourceLimits:
    def __init__(
        self,
        *,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_memory_gib OceanAksNp#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_vcpu OceanAksNp#max_vcpu}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a5a0c123b4007faf87d6c403994a74c1db5f68aedd37c6754116ad94e1164fd)
            check_type(argname="argument max_memory_gib", value=max_memory_gib, expected_type=type_hints["max_memory_gib"])
            check_type(argname="argument max_vcpu", value=max_vcpu, expected_type=type_hints["max_vcpu"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_memory_gib is not None:
            self._values["max_memory_gib"] = max_memory_gib
        if max_vcpu is not None:
            self._values["max_vcpu"] = max_vcpu

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_memory_gib OceanAksNp#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_vcpu OceanAksNp#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpAutoscalerResourceLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpAutoscalerResourceLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpAutoscalerResourceLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71cbffbd897e11688fd174fd8ed556b1888ea72e313351b955cab1461248eec7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxMemoryGib")
    def reset_max_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMemoryGib", []))

    @jsii.member(jsii_name="resetMaxVcpu")
    def reset_max_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxVcpu", []))

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGibInput")
    def max_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="maxVcpuInput")
    def max_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGib")
    def max_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemoryGib"))

    @max_memory_gib.setter
    def max_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e14ca6f83844bc92b5506d7a61488a3b988fb9b002111e37c86faf65b58dec24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b89ad8c1aa30471337199f6611e44ca026982358d6a0c5d6a9cb325ce4469b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpAutoscalerResourceLimits]:
        return typing.cast(typing.Optional[OceanAksNpAutoscalerResourceLimits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpAutoscalerResourceLimits],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bda71648bd77cd9febd4bf4fe53060c188279f266968f16f74a65d6b6e348bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "aks_cluster_name": "aksClusterName",
        "aks_infrastructure_resource_group_name": "aksInfrastructureResourceGroupName",
        "aks_region": "aksRegion",
        "aks_resource_group_name": "aksResourceGroupName",
        "availability_zones": "availabilityZones",
        "controller_cluster_id": "controllerClusterId",
        "name": "name",
        "autoscaler": "autoscaler",
        "enable_node_public_ip": "enableNodePublicIp",
        "fallback_to_ondemand": "fallbackToOndemand",
        "filters": "filters",
        "headrooms": "headrooms",
        "health": "health",
        "id": "id",
        "kubernetes_version": "kubernetesVersion",
        "labels": "labels",
        "linux_os_config": "linuxOsConfig",
        "logging": "logging",
        "max_count": "maxCount",
        "max_pods_per_node": "maxPodsPerNode",
        "min_count": "minCount",
        "os_disk_size_gb": "osDiskSizeGb",
        "os_disk_type": "osDiskType",
        "os_sku": "osSku",
        "os_type": "osType",
        "pod_subnet_ids": "podSubnetIds",
        "scheduling": "scheduling",
        "spot_percentage": "spotPercentage",
        "tags": "tags",
        "taints": "taints",
        "update_policy": "updatePolicy",
        "vnet_subnet_ids": "vnetSubnetIds",
        "vng_template_scheduling": "vngTemplateScheduling",
    },
)
class OceanAksNpConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        aks_cluster_name: builtins.str,
        aks_infrastructure_resource_group_name: builtins.str,
        aks_region: builtins.str,
        aks_resource_group_name: builtins.str,
        availability_zones: typing.Sequence[builtins.str],
        controller_cluster_id: builtins.str,
        name: builtins.str,
        autoscaler: typing.Optional[typing.Union[OceanAksNpAutoscaler, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filters: typing.Optional[typing.Union["OceanAksNpFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpHeadrooms", typing.Dict[builtins.str, typing.Any]]]]] = None,
        health: typing.Optional[typing.Union["OceanAksNpHealth", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        kubernetes_version: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpLinuxOsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        logging: typing.Optional[typing.Union["OceanAksNpLogging", typing.Dict[builtins.str, typing.Any]]] = None,
        max_count: typing.Optional[jsii.Number] = None,
        max_pods_per_node: typing.Optional[jsii.Number] = None,
        min_count: typing.Optional[jsii.Number] = None,
        os_disk_size_gb: typing.Optional[jsii.Number] = None,
        os_disk_type: typing.Optional[builtins.str] = None,
        os_sku: typing.Optional[builtins.str] = None,
        os_type: typing.Optional[builtins.str] = None,
        pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling: typing.Optional[typing.Union["OceanAksNpScheduling", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanAksNpUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vng_template_scheduling: typing.Optional[typing.Union["OceanAksNpVngTemplateScheduling", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param aks_cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_cluster_name OceanAksNp#aks_cluster_name}.
        :param aks_infrastructure_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_infrastructure_resource_group_name OceanAksNp#aks_infrastructure_resource_group_name}.
        :param aks_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_region OceanAksNp#aks_region}.
        :param aks_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_resource_group_name OceanAksNp#aks_resource_group_name}.
        :param availability_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#availability_zones OceanAksNp#availability_zones}.
        :param controller_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#controller_cluster_id OceanAksNp#controller_cluster_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#name OceanAksNp#name}.
        :param autoscaler: autoscaler block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscaler OceanAksNp#autoscaler}
        :param enable_node_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#enable_node_public_ip OceanAksNp#enable_node_public_ip}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#fallback_to_ondemand OceanAksNp#fallback_to_ondemand}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#filters OceanAksNp#filters}
        :param headrooms: headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#headrooms OceanAksNp#headrooms}
        :param health: health block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#health OceanAksNp#health}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#id OceanAksNp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kubernetes_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#kubernetes_version OceanAksNp#kubernetes_version}.
        :param labels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#labels OceanAksNp#labels}.
        :param linux_os_config: linux_os_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#linux_os_config OceanAksNp#linux_os_config}
        :param logging: logging block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#logging OceanAksNp#logging}
        :param max_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_count OceanAksNp#max_count}.
        :param max_pods_per_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_pods_per_node OceanAksNp#max_pods_per_node}.
        :param min_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_count OceanAksNp#min_count}.
        :param os_disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_disk_size_gb OceanAksNp#os_disk_size_gb}.
        :param os_disk_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_disk_type OceanAksNp#os_disk_type}.
        :param os_sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_sku OceanAksNp#os_sku}.
        :param os_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_type OceanAksNp#os_type}.
        :param pod_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#pod_subnet_ids OceanAksNp#pod_subnet_ids}.
        :param scheduling: scheduling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#scheduling OceanAksNp#scheduling}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#spot_percentage OceanAksNp#spot_percentage}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#tags OceanAksNp#tags}.
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#taints OceanAksNp#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#update_policy OceanAksNp#update_policy}
        :param vnet_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vnet_subnet_ids OceanAksNp#vnet_subnet_ids}.
        :param vng_template_scheduling: vng_template_scheduling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_template_scheduling OceanAksNp#vng_template_scheduling}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(autoscaler, dict):
            autoscaler = OceanAksNpAutoscaler(**autoscaler)
        if isinstance(filters, dict):
            filters = OceanAksNpFilters(**filters)
        if isinstance(health, dict):
            health = OceanAksNpHealth(**health)
        if isinstance(logging, dict):
            logging = OceanAksNpLogging(**logging)
        if isinstance(scheduling, dict):
            scheduling = OceanAksNpScheduling(**scheduling)
        if isinstance(update_policy, dict):
            update_policy = OceanAksNpUpdatePolicy(**update_policy)
        if isinstance(vng_template_scheduling, dict):
            vng_template_scheduling = OceanAksNpVngTemplateScheduling(**vng_template_scheduling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9bab4f3e98d3b0cba441a02e1e4220b0e83e9de8e80d93eb0348c9802bbac4b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument aks_cluster_name", value=aks_cluster_name, expected_type=type_hints["aks_cluster_name"])
            check_type(argname="argument aks_infrastructure_resource_group_name", value=aks_infrastructure_resource_group_name, expected_type=type_hints["aks_infrastructure_resource_group_name"])
            check_type(argname="argument aks_region", value=aks_region, expected_type=type_hints["aks_region"])
            check_type(argname="argument aks_resource_group_name", value=aks_resource_group_name, expected_type=type_hints["aks_resource_group_name"])
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument controller_cluster_id", value=controller_cluster_id, expected_type=type_hints["controller_cluster_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument autoscaler", value=autoscaler, expected_type=type_hints["autoscaler"])
            check_type(argname="argument enable_node_public_ip", value=enable_node_public_ip, expected_type=type_hints["enable_node_public_ip"])
            check_type(argname="argument fallback_to_ondemand", value=fallback_to_ondemand, expected_type=type_hints["fallback_to_ondemand"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument headrooms", value=headrooms, expected_type=type_hints["headrooms"])
            check_type(argname="argument health", value=health, expected_type=type_hints["health"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument kubernetes_version", value=kubernetes_version, expected_type=type_hints["kubernetes_version"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument linux_os_config", value=linux_os_config, expected_type=type_hints["linux_os_config"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument max_count", value=max_count, expected_type=type_hints["max_count"])
            check_type(argname="argument max_pods_per_node", value=max_pods_per_node, expected_type=type_hints["max_pods_per_node"])
            check_type(argname="argument min_count", value=min_count, expected_type=type_hints["min_count"])
            check_type(argname="argument os_disk_size_gb", value=os_disk_size_gb, expected_type=type_hints["os_disk_size_gb"])
            check_type(argname="argument os_disk_type", value=os_disk_type, expected_type=type_hints["os_disk_type"])
            check_type(argname="argument os_sku", value=os_sku, expected_type=type_hints["os_sku"])
            check_type(argname="argument os_type", value=os_type, expected_type=type_hints["os_type"])
            check_type(argname="argument pod_subnet_ids", value=pod_subnet_ids, expected_type=type_hints["pod_subnet_ids"])
            check_type(argname="argument scheduling", value=scheduling, expected_type=type_hints["scheduling"])
            check_type(argname="argument spot_percentage", value=spot_percentage, expected_type=type_hints["spot_percentage"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument taints", value=taints, expected_type=type_hints["taints"])
            check_type(argname="argument update_policy", value=update_policy, expected_type=type_hints["update_policy"])
            check_type(argname="argument vnet_subnet_ids", value=vnet_subnet_ids, expected_type=type_hints["vnet_subnet_ids"])
            check_type(argname="argument vng_template_scheduling", value=vng_template_scheduling, expected_type=type_hints["vng_template_scheduling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "aks_cluster_name": aks_cluster_name,
            "aks_infrastructure_resource_group_name": aks_infrastructure_resource_group_name,
            "aks_region": aks_region,
            "aks_resource_group_name": aks_resource_group_name,
            "availability_zones": availability_zones,
            "controller_cluster_id": controller_cluster_id,
            "name": name,
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
        if autoscaler is not None:
            self._values["autoscaler"] = autoscaler
        if enable_node_public_ip is not None:
            self._values["enable_node_public_ip"] = enable_node_public_ip
        if fallback_to_ondemand is not None:
            self._values["fallback_to_ondemand"] = fallback_to_ondemand
        if filters is not None:
            self._values["filters"] = filters
        if headrooms is not None:
            self._values["headrooms"] = headrooms
        if health is not None:
            self._values["health"] = health
        if id is not None:
            self._values["id"] = id
        if kubernetes_version is not None:
            self._values["kubernetes_version"] = kubernetes_version
        if labels is not None:
            self._values["labels"] = labels
        if linux_os_config is not None:
            self._values["linux_os_config"] = linux_os_config
        if logging is not None:
            self._values["logging"] = logging
        if max_count is not None:
            self._values["max_count"] = max_count
        if max_pods_per_node is not None:
            self._values["max_pods_per_node"] = max_pods_per_node
        if min_count is not None:
            self._values["min_count"] = min_count
        if os_disk_size_gb is not None:
            self._values["os_disk_size_gb"] = os_disk_size_gb
        if os_disk_type is not None:
            self._values["os_disk_type"] = os_disk_type
        if os_sku is not None:
            self._values["os_sku"] = os_sku
        if os_type is not None:
            self._values["os_type"] = os_type
        if pod_subnet_ids is not None:
            self._values["pod_subnet_ids"] = pod_subnet_ids
        if scheduling is not None:
            self._values["scheduling"] = scheduling
        if spot_percentage is not None:
            self._values["spot_percentage"] = spot_percentage
        if tags is not None:
            self._values["tags"] = tags
        if taints is not None:
            self._values["taints"] = taints
        if update_policy is not None:
            self._values["update_policy"] = update_policy
        if vnet_subnet_ids is not None:
            self._values["vnet_subnet_ids"] = vnet_subnet_ids
        if vng_template_scheduling is not None:
            self._values["vng_template_scheduling"] = vng_template_scheduling

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
    def aks_cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_cluster_name OceanAksNp#aks_cluster_name}.'''
        result = self._values.get("aks_cluster_name")
        assert result is not None, "Required property 'aks_cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aks_infrastructure_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_infrastructure_resource_group_name OceanAksNp#aks_infrastructure_resource_group_name}.'''
        result = self._values.get("aks_infrastructure_resource_group_name")
        assert result is not None, "Required property 'aks_infrastructure_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aks_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_region OceanAksNp#aks_region}.'''
        result = self._values.get("aks_region")
        assert result is not None, "Required property 'aks_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aks_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#aks_resource_group_name OceanAksNp#aks_resource_group_name}.'''
        result = self._values.get("aks_resource_group_name")
        assert result is not None, "Required property 'aks_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def availability_zones(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#availability_zones OceanAksNp#availability_zones}.'''
        result = self._values.get("availability_zones")
        assert result is not None, "Required property 'availability_zones' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def controller_cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#controller_cluster_id OceanAksNp#controller_cluster_id}.'''
        result = self._values.get("controller_cluster_id")
        assert result is not None, "Required property 'controller_cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#name OceanAksNp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autoscaler(self) -> typing.Optional[OceanAksNpAutoscaler]:
        '''autoscaler block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#autoscaler OceanAksNp#autoscaler}
        '''
        result = self._values.get("autoscaler")
        return typing.cast(typing.Optional[OceanAksNpAutoscaler], result)

    @builtins.property
    def enable_node_public_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#enable_node_public_ip OceanAksNp#enable_node_public_ip}.'''
        result = self._values.get("enable_node_public_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fallback_to_ondemand(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#fallback_to_ondemand OceanAksNp#fallback_to_ondemand}.'''
        result = self._values.get("fallback_to_ondemand")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def filters(self) -> typing.Optional["OceanAksNpFilters"]:
        '''filters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#filters OceanAksNp#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["OceanAksNpFilters"], result)

    @builtins.property
    def headrooms(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpHeadrooms"]]]:
        '''headrooms block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#headrooms OceanAksNp#headrooms}
        '''
        result = self._values.get("headrooms")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpHeadrooms"]]], result)

    @builtins.property
    def health(self) -> typing.Optional["OceanAksNpHealth"]:
        '''health block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#health OceanAksNp#health}
        '''
        result = self._values.get("health")
        return typing.cast(typing.Optional["OceanAksNpHealth"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#id OceanAksNp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kubernetes_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#kubernetes_version OceanAksNp#kubernetes_version}.'''
        result = self._values.get("kubernetes_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#labels OceanAksNp#labels}.'''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def linux_os_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfig"]]]:
        '''linux_os_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#linux_os_config OceanAksNp#linux_os_config}
        '''
        result = self._values.get("linux_os_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfig"]]], result)

    @builtins.property
    def logging(self) -> typing.Optional["OceanAksNpLogging"]:
        '''logging block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#logging OceanAksNp#logging}
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional["OceanAksNpLogging"], result)

    @builtins.property
    def max_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_count OceanAksNp#max_count}.'''
        result = self._values.get("max_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pods_per_node(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_pods_per_node OceanAksNp#max_pods_per_node}.'''
        result = self._values.get("max_pods_per_node")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_count OceanAksNp#min_count}.'''
        result = self._values.get("min_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def os_disk_size_gb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_disk_size_gb OceanAksNp#os_disk_size_gb}.'''
        result = self._values.get("os_disk_size_gb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def os_disk_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_disk_type OceanAksNp#os_disk_type}.'''
        result = self._values.get("os_disk_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_sku(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_sku OceanAksNp#os_sku}.'''
        result = self._values.get("os_sku")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#os_type OceanAksNp#os_type}.'''
        result = self._values.get("os_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pod_subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#pod_subnet_ids OceanAksNp#pod_subnet_ids}.'''
        result = self._values.get("pod_subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def scheduling(self) -> typing.Optional["OceanAksNpScheduling"]:
        '''scheduling block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#scheduling OceanAksNp#scheduling}
        '''
        result = self._values.get("scheduling")
        return typing.cast(typing.Optional["OceanAksNpScheduling"], result)

    @builtins.property
    def spot_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#spot_percentage OceanAksNp#spot_percentage}.'''
        result = self._values.get("spot_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#tags OceanAksNp#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def taints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpTaints"]]]:
        '''taints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#taints OceanAksNp#taints}
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpTaints"]]], result)

    @builtins.property
    def update_policy(self) -> typing.Optional["OceanAksNpUpdatePolicy"]:
        '''update_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#update_policy OceanAksNp#update_policy}
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional["OceanAksNpUpdatePolicy"], result)

    @builtins.property
    def vnet_subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vnet_subnet_ids OceanAksNp#vnet_subnet_ids}.'''
        result = self._values.get("vnet_subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vng_template_scheduling(
        self,
    ) -> typing.Optional["OceanAksNpVngTemplateScheduling"]:
        '''vng_template_scheduling block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_template_scheduling OceanAksNp#vng_template_scheduling}
        '''
        result = self._values.get("vng_template_scheduling")
        return typing.cast(typing.Optional["OceanAksNpVngTemplateScheduling"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpFilters",
    jsii_struct_bases=[],
    name_mapping={
        "accelerated_networking": "acceleratedNetworking",
        "architectures": "architectures",
        "disk_performance": "diskPerformance",
        "exclude_series": "excludeSeries",
        "gpu_types": "gpuTypes",
        "max_gpu": "maxGpu",
        "max_memory_gib": "maxMemoryGib",
        "max_vcpu": "maxVcpu",
        "min_disk": "minDisk",
        "min_gpu": "minGpu",
        "min_memory_gib": "minMemoryGib",
        "min_nics": "minNics",
        "min_vcpu": "minVcpu",
        "series": "series",
        "vm_types": "vmTypes",
    },
)
class OceanAksNpFilters:
    def __init__(
        self,
        *,
        accelerated_networking: typing.Optional[builtins.str] = None,
        architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
        disk_performance: typing.Optional[builtins.str] = None,
        exclude_series: typing.Optional[typing.Sequence[builtins.str]] = None,
        gpu_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_gpu: typing.Optional[jsii.Number] = None,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
        min_disk: typing.Optional[jsii.Number] = None,
        min_gpu: typing.Optional[jsii.Number] = None,
        min_memory_gib: typing.Optional[jsii.Number] = None,
        min_nics: typing.Optional[jsii.Number] = None,
        min_vcpu: typing.Optional[jsii.Number] = None,
        series: typing.Optional[typing.Sequence[builtins.str]] = None,
        vm_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param accelerated_networking: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#accelerated_networking OceanAksNp#accelerated_networking}.
        :param architectures: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#architectures OceanAksNp#architectures}.
        :param disk_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#disk_performance OceanAksNp#disk_performance}.
        :param exclude_series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#exclude_series OceanAksNp#exclude_series}.
        :param gpu_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#gpu_types OceanAksNp#gpu_types}.
        :param max_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_gpu OceanAksNp#max_gpu}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_memory_gib OceanAksNp#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_vcpu OceanAksNp#max_vcpu}.
        :param min_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_disk OceanAksNp#min_disk}.
        :param min_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_gpu OceanAksNp#min_gpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_memory_gib OceanAksNp#min_memory_gib}.
        :param min_nics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_nics OceanAksNp#min_nics}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_vcpu OceanAksNp#min_vcpu}.
        :param series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#series OceanAksNp#series}.
        :param vm_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vm_types OceanAksNp#vm_types}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34a9f7ac92271595654997c1c567d2192601f5aa35699adec679624356c181ab)
            check_type(argname="argument accelerated_networking", value=accelerated_networking, expected_type=type_hints["accelerated_networking"])
            check_type(argname="argument architectures", value=architectures, expected_type=type_hints["architectures"])
            check_type(argname="argument disk_performance", value=disk_performance, expected_type=type_hints["disk_performance"])
            check_type(argname="argument exclude_series", value=exclude_series, expected_type=type_hints["exclude_series"])
            check_type(argname="argument gpu_types", value=gpu_types, expected_type=type_hints["gpu_types"])
            check_type(argname="argument max_gpu", value=max_gpu, expected_type=type_hints["max_gpu"])
            check_type(argname="argument max_memory_gib", value=max_memory_gib, expected_type=type_hints["max_memory_gib"])
            check_type(argname="argument max_vcpu", value=max_vcpu, expected_type=type_hints["max_vcpu"])
            check_type(argname="argument min_disk", value=min_disk, expected_type=type_hints["min_disk"])
            check_type(argname="argument min_gpu", value=min_gpu, expected_type=type_hints["min_gpu"])
            check_type(argname="argument min_memory_gib", value=min_memory_gib, expected_type=type_hints["min_memory_gib"])
            check_type(argname="argument min_nics", value=min_nics, expected_type=type_hints["min_nics"])
            check_type(argname="argument min_vcpu", value=min_vcpu, expected_type=type_hints["min_vcpu"])
            check_type(argname="argument series", value=series, expected_type=type_hints["series"])
            check_type(argname="argument vm_types", value=vm_types, expected_type=type_hints["vm_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if accelerated_networking is not None:
            self._values["accelerated_networking"] = accelerated_networking
        if architectures is not None:
            self._values["architectures"] = architectures
        if disk_performance is not None:
            self._values["disk_performance"] = disk_performance
        if exclude_series is not None:
            self._values["exclude_series"] = exclude_series
        if gpu_types is not None:
            self._values["gpu_types"] = gpu_types
        if max_gpu is not None:
            self._values["max_gpu"] = max_gpu
        if max_memory_gib is not None:
            self._values["max_memory_gib"] = max_memory_gib
        if max_vcpu is not None:
            self._values["max_vcpu"] = max_vcpu
        if min_disk is not None:
            self._values["min_disk"] = min_disk
        if min_gpu is not None:
            self._values["min_gpu"] = min_gpu
        if min_memory_gib is not None:
            self._values["min_memory_gib"] = min_memory_gib
        if min_nics is not None:
            self._values["min_nics"] = min_nics
        if min_vcpu is not None:
            self._values["min_vcpu"] = min_vcpu
        if series is not None:
            self._values["series"] = series
        if vm_types is not None:
            self._values["vm_types"] = vm_types

    @builtins.property
    def accelerated_networking(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#accelerated_networking OceanAksNp#accelerated_networking}.'''
        result = self._values.get("accelerated_networking")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def architectures(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#architectures OceanAksNp#architectures}.'''
        result = self._values.get("architectures")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disk_performance(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#disk_performance OceanAksNp#disk_performance}.'''
        result = self._values.get("disk_performance")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_series(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#exclude_series OceanAksNp#exclude_series}.'''
        result = self._values.get("exclude_series")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gpu_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#gpu_types OceanAksNp#gpu_types}.'''
        result = self._values.get("gpu_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_gpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_gpu OceanAksNp#max_gpu}.'''
        result = self._values.get("max_gpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_memory_gib OceanAksNp#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#max_vcpu OceanAksNp#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_disk(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_disk OceanAksNp#min_disk}.'''
        result = self._values.get("min_disk")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_gpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_gpu OceanAksNp#min_gpu}.'''
        result = self._values.get("min_gpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_memory_gib OceanAksNp#min_memory_gib}.'''
        result = self._values.get("min_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_nics(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_nics OceanAksNp#min_nics}.'''
        result = self._values.get("min_nics")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#min_vcpu OceanAksNp#min_vcpu}.'''
        result = self._values.get("min_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def series(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#series OceanAksNp#series}.'''
        result = self._values.get("series")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vm_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vm_types OceanAksNp#vm_types}.'''
        result = self._values.get("vm_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb3d5c6b23f914408dcab4cd492a9e2c57a0dfc473c15cc81e6fed9569e4a885)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAcceleratedNetworking")
    def reset_accelerated_networking(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcceleratedNetworking", []))

    @jsii.member(jsii_name="resetArchitectures")
    def reset_architectures(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArchitectures", []))

    @jsii.member(jsii_name="resetDiskPerformance")
    def reset_disk_performance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskPerformance", []))

    @jsii.member(jsii_name="resetExcludeSeries")
    def reset_exclude_series(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeSeries", []))

    @jsii.member(jsii_name="resetGpuTypes")
    def reset_gpu_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGpuTypes", []))

    @jsii.member(jsii_name="resetMaxGpu")
    def reset_max_gpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxGpu", []))

    @jsii.member(jsii_name="resetMaxMemoryGib")
    def reset_max_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMemoryGib", []))

    @jsii.member(jsii_name="resetMaxVcpu")
    def reset_max_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxVcpu", []))

    @jsii.member(jsii_name="resetMinDisk")
    def reset_min_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinDisk", []))

    @jsii.member(jsii_name="resetMinGpu")
    def reset_min_gpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinGpu", []))

    @jsii.member(jsii_name="resetMinMemoryGib")
    def reset_min_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinMemoryGib", []))

    @jsii.member(jsii_name="resetMinNics")
    def reset_min_nics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinNics", []))

    @jsii.member(jsii_name="resetMinVcpu")
    def reset_min_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinVcpu", []))

    @jsii.member(jsii_name="resetSeries")
    def reset_series(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeries", []))

    @jsii.member(jsii_name="resetVmTypes")
    def reset_vm_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmTypes", []))

    @builtins.property
    @jsii.member(jsii_name="acceleratedNetworkingInput")
    def accelerated_networking_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acceleratedNetworkingInput"))

    @builtins.property
    @jsii.member(jsii_name="architecturesInput")
    def architectures_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "architecturesInput"))

    @builtins.property
    @jsii.member(jsii_name="diskPerformanceInput")
    def disk_performance_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskPerformanceInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeSeriesInput")
    def exclude_series_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeSeriesInput"))

    @builtins.property
    @jsii.member(jsii_name="gpuTypesInput")
    def gpu_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "gpuTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxGpuInput")
    def max_gpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxGpuInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGibInput")
    def max_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="maxVcpuInput")
    def max_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="minDiskInput")
    def min_disk_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="minGpuInput")
    def min_gpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minGpuInput"))

    @builtins.property
    @jsii.member(jsii_name="minMemoryGibInput")
    def min_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="minNicsInput")
    def min_nics_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minNicsInput"))

    @builtins.property
    @jsii.member(jsii_name="minVcpuInput")
    def min_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="seriesInput")
    def series_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "seriesInput"))

    @builtins.property
    @jsii.member(jsii_name="vmTypesInput")
    def vm_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vmTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="acceleratedNetworking")
    def accelerated_networking(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acceleratedNetworking"))

    @accelerated_networking.setter
    def accelerated_networking(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee388709d1565b586d153fbcb4c4db73d07f73b6f592dc66c1ca93b98b4a945b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acceleratedNetworking", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="architectures")
    def architectures(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "architectures"))

    @architectures.setter
    def architectures(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c742c1c4d9379baf6663ee29e90347b76841893ec7c21d5f0c078681e63b322)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "architectures", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskPerformance")
    def disk_performance(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskPerformance"))

    @disk_performance.setter
    def disk_performance(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afbe8d66bc8afc1a997487114b51da9db7e17086de47d2422d9cc82fdb5e0db5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskPerformance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeSeries")
    def exclude_series(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeSeries"))

    @exclude_series.setter
    def exclude_series(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71c859c25dae8d7f829f8a4c7a10d8f95ea10064ef8ec38c26a9b7ec99c89146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeSeries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuTypes")
    def gpu_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gpuTypes"))

    @gpu_types.setter
    def gpu_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__655de80b749e3f6169b1935080116c7aa6526ab5a70babb82390e62e656e0269)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxGpu")
    def max_gpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxGpu"))

    @max_gpu.setter
    def max_gpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c8dfb8486e6f9ff1443621b5969fe2227906e0cb20dade66f1c1c629c157e26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxGpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGib")
    def max_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemoryGib"))

    @max_memory_gib.setter
    def max_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb7e75e2b21793f5c4a71c261dcd0e2f3c8c247bb5e8055027755fd8929fec3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c124113da710685d1046267a1bef2d22b3f6c4960033e838db3f969d0c94544)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minDisk")
    def min_disk(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minDisk"))

    @min_disk.setter
    def min_disk(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a30a41b857f7dbb1a71c27ab48e06fbcfc2e41ae15b21dd49b1c43f0d465c23f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minGpu")
    def min_gpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minGpu"))

    @min_gpu.setter
    def min_gpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaef3d9405dfa602d7bcee79852b76c52146b52dcd15267515a8dd4036956b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minGpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemoryGib")
    def min_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemoryGib"))

    @min_memory_gib.setter
    def min_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7006276093120f973474fc0cd23738284fa202900d8a7f7cdff0cf99fc52cbb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minNics")
    def min_nics(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNics"))

    @min_nics.setter
    def min_nics(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e318816c124c46f93960ffc0e6dbbdd0cf6ec9c95a1b86b02801018303241d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minNics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVcpu")
    def min_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpu"))

    @min_vcpu.setter
    def min_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8f9842d5ec88efa702799bf7305f81cdd9657e6343aeefea4a229a40d027493)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="series")
    def series(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "series"))

    @series.setter
    def series(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2fa2a5a1c3686a833a5af9341349061e311b0645695207344c40eb87ab3e64e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "series", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmTypes")
    def vm_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vmTypes"))

    @vm_types.setter
    def vm_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5ea2b88093c0500834a83ea6aec4ae4257fdd8e591befc4898ab51c498a394e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpFilters]:
        return typing.cast(typing.Optional[OceanAksNpFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpFilters]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f31bd0fc5a502010cec257c33953fdf09d6f9013fd19fca25907e25d7b91be82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpHeadrooms",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
        "num_of_units": "numOfUnits",
    },
)
class OceanAksNpHeadrooms:
    def __init__(
        self,
        *,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
        num_of_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#cpu_per_unit OceanAksNp#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#gpu_per_unit OceanAksNp#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#memory_per_unit OceanAksNp#memory_per_unit}.
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#num_of_units OceanAksNp#num_of_units}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71f8750b24926f1ba765bf3f4bae5f9a952c815a93d08ba5ab409373a843371b)
            check_type(argname="argument cpu_per_unit", value=cpu_per_unit, expected_type=type_hints["cpu_per_unit"])
            check_type(argname="argument gpu_per_unit", value=gpu_per_unit, expected_type=type_hints["gpu_per_unit"])
            check_type(argname="argument memory_per_unit", value=memory_per_unit, expected_type=type_hints["memory_per_unit"])
            check_type(argname="argument num_of_units", value=num_of_units, expected_type=type_hints["num_of_units"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_per_unit is not None:
            self._values["cpu_per_unit"] = cpu_per_unit
        if gpu_per_unit is not None:
            self._values["gpu_per_unit"] = gpu_per_unit
        if memory_per_unit is not None:
            self._values["memory_per_unit"] = memory_per_unit
        if num_of_units is not None:
            self._values["num_of_units"] = num_of_units

    @builtins.property
    def cpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#cpu_per_unit OceanAksNp#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#gpu_per_unit OceanAksNp#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#memory_per_unit OceanAksNp#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_of_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#num_of_units OceanAksNp#num_of_units}.'''
        result = self._values.get("num_of_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpHeadrooms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpHeadroomsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpHeadroomsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5c950d5f3f70655493d9d9c052fe216c9f66fcc7e611665d994f76175adb2fe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAksNpHeadroomsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddd81aaf8bb9776ce0913f2849cc0a6d8850205e7945e73eb68e7cd06190a2e3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpHeadroomsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__974e4e6b976d69c90b5f86b11bfe4d68b5d80dc9e4861f115816562c61596d8f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8066f1a1deb87058e4059c1959e90872007b95885d9438a3f8ce29bd6f4915f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__deaf9d4b8b9ae52192fc3601c0951f8914b64eb56931429524cd80ff38e28ef0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpHeadrooms]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpHeadrooms]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpHeadrooms]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__930213753fd0fffc740533f09448e92002d97f00bf6f641ec3f39a8a3806a535)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpHeadroomsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpHeadroomsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0ff8aa121081ccb41ad6c5fc8d3ea6631df992c898121214ebf3e687e08f17d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCpuPerUnit")
    def reset_cpu_per_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuPerUnit", []))

    @jsii.member(jsii_name="resetGpuPerUnit")
    def reset_gpu_per_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGpuPerUnit", []))

    @jsii.member(jsii_name="resetMemoryPerUnit")
    def reset_memory_per_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryPerUnit", []))

    @jsii.member(jsii_name="resetNumOfUnits")
    def reset_num_of_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumOfUnits", []))

    @builtins.property
    @jsii.member(jsii_name="cpuPerUnitInput")
    def cpu_per_unit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuPerUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnitInput")
    def gpu_per_unit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gpuPerUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnitInput")
    def memory_per_unit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryPerUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="numOfUnitsInput")
    def num_of_units_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numOfUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuPerUnit")
    def cpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuPerUnit"))

    @cpu_per_unit.setter
    def cpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32475492fd397e67799604b757dd5b65aaac594140765ddbe0d8fb11ed5bcbe8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14959e319a974453ba22c4bc44072e335bd6d76e7eeb1dd1119a6378f4e4c1be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e4aa00243509d7b4f1b0dd8329bd3517aae69bcdb204a1c47df019bff2c3b6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__856e5ad14de0acec5e7d139d2a8b96fc92c5ae52d209d7c616ede8873891bf0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpHeadrooms]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpHeadrooms]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpHeadrooms]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0561065072d4a65c55dd2068d56986da11a509b67366f7fa28ac74525134cfd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpHealth",
    jsii_struct_bases=[],
    name_mapping={"grace_period": "gracePeriod"},
)
class OceanAksNpHealth:
    def __init__(self, *, grace_period: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#grace_period OceanAksNp#grace_period}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0446171353b1dda6da14d9676f214aa866da2a98185290415005f5b979db2eb7)
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if grace_period is not None:
            self._values["grace_period"] = grace_period

    @builtins.property
    def grace_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#grace_period OceanAksNp#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpHealth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpHealthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpHealthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e7aedccee9ce43e6ed6a3722e435b998ea72bcfb5ec8f247f3156ec79e8f40a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

    @builtins.property
    @jsii.member(jsii_name="gracePeriodInput")
    def grace_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gracePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__913de7f1851a455383aaeebdae3597173c9cceb7381a5d37852b0b1bad8f04a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gracePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpHealth]:
        return typing.cast(typing.Optional[OceanAksNpHealth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpHealth]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf340db4cbe5a708e17e8e299156919e448f4418f16a733c27fa1313b55df2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLinuxOsConfig",
    jsii_struct_bases=[],
    name_mapping={"sysctls": "sysctls"},
)
class OceanAksNpLinuxOsConfig:
    def __init__(
        self,
        *,
        sysctls: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpLinuxOsConfigSysctls", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param sysctls: sysctls block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#sysctls OceanAksNp#sysctls}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a358dd81765eec4a41ebb3e471be2ed6cd62e3de8993d5238d73dad36aad760)
            check_type(argname="argument sysctls", value=sysctls, expected_type=type_hints["sysctls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if sysctls is not None:
            self._values["sysctls"] = sysctls

    @builtins.property
    def sysctls(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfigSysctls"]]]:
        '''sysctls block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#sysctls OceanAksNp#sysctls}
        '''
        result = self._values.get("sysctls")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfigSysctls"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpLinuxOsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpLinuxOsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLinuxOsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e71cdf4cf1092a391f97e0280cd25e1d13b7869d6f8a8c8224a056f210e09f4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAksNpLinuxOsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1413c6ad64a4c21e6092d7e9ba5127d531b16a573baaaf45e6d84f8d49844638)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpLinuxOsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d04c31d9dfb885200f59b89fe844c8f8b106b7e4311afbb8c8854fc4a365072)
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
            type_hints = typing.get_type_hints(_typecheckingstub__470414e5b6863c315be4bc819613c07c40ce60837ff7142bd11e4e383238bb90)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d402c07831a50a444d10e2b94506b6292c7db201c4e4b9f7257fe7093d3fff1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3245b8d6a9ce03af0a9d8e9292e4f70d8a2aae88baf98cc4e899072efe455ada)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpLinuxOsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLinuxOsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebecd7f5cc58d81c09e0d7e774ff1b57bbb27d50d25afeabf0a0ba26d020436e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putSysctls")
    def put_sysctls(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpLinuxOsConfigSysctls", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b35b3678e294a3633279af6008402955600486c4dc84d92e285ddcbfafd7de17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSysctls", [value]))

    @jsii.member(jsii_name="resetSysctls")
    def reset_sysctls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSysctls", []))

    @builtins.property
    @jsii.member(jsii_name="sysctls")
    def sysctls(self) -> "OceanAksNpLinuxOsConfigSysctlsList":
        return typing.cast("OceanAksNpLinuxOsConfigSysctlsList", jsii.get(self, "sysctls"))

    @builtins.property
    @jsii.member(jsii_name="sysctlsInput")
    def sysctls_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfigSysctls"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLinuxOsConfigSysctls"]]], jsii.get(self, "sysctlsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__338e8b77d13194c4c96fa0148b8fcf84195461a9e9a004a234615736628ef1a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLinuxOsConfigSysctls",
    jsii_struct_bases=[],
    name_mapping={"vm_max_map_count": "vmMaxMapCount"},
)
class OceanAksNpLinuxOsConfigSysctls:
    def __init__(
        self,
        *,
        vm_max_map_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param vm_max_map_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vm_max_map_count OceanAksNp#vm_max_map_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67fa521eadd72eb55f8528b9e5f499dd0ff1cc262737bc3631effdda982a4887)
            check_type(argname="argument vm_max_map_count", value=vm_max_map_count, expected_type=type_hints["vm_max_map_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if vm_max_map_count is not None:
            self._values["vm_max_map_count"] = vm_max_map_count

    @builtins.property
    def vm_max_map_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vm_max_map_count OceanAksNp#vm_max_map_count}.'''
        result = self._values.get("vm_max_map_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpLinuxOsConfigSysctls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpLinuxOsConfigSysctlsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLinuxOsConfigSysctlsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3485d32f831bdb745686adf7c107474295c3afc6ae6a8c76b4952ff5cf31e509)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAksNpLinuxOsConfigSysctlsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a72c749154bcbf1587d258279b9c3a79969c0aef3c88730c611ab64d649bfd6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpLinuxOsConfigSysctlsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4d7475880a286a5e7a7edd624bb6e87d1d6035b57b2ee4c351cbb9997ea912b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9a4cbb24466dd580c6de7ec0b1f8874cb1b597ce8bd4749102c77b2d5fc0f76)
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
            type_hints = typing.get_type_hints(_typecheckingstub__070b46f9704be672372066dd2cb6ed78cfc8a0e7d56271ccb7e43c094863b3b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfigSysctls]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfigSysctls]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfigSysctls]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b8872a75ee98d8c9493423cae0bca61a071a9fce85d1bbd8fe90408d7a76acc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpLinuxOsConfigSysctlsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLinuxOsConfigSysctlsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9c756365b267967b6cd62e5edff2b40fcf158197790941975c02f0781f0196b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetVmMaxMapCount")
    def reset_vm_max_map_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmMaxMapCount", []))

    @builtins.property
    @jsii.member(jsii_name="vmMaxMapCountInput")
    def vm_max_map_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vmMaxMapCountInput"))

    @builtins.property
    @jsii.member(jsii_name="vmMaxMapCount")
    def vm_max_map_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vmMaxMapCount"))

    @vm_max_map_count.setter
    def vm_max_map_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9236a5f31465d1e6b441d7d62d573ed93c353a33cfa81102e100871d2ac3ebd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmMaxMapCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfigSysctls]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfigSysctls]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfigSysctls]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71a8a4d6699d0db75c6f3bb90e453c3105160e74f578204679f7a15d972aa7a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLogging",
    jsii_struct_bases=[],
    name_mapping={"export": "export"},
)
class OceanAksNpLogging:
    def __init__(
        self,
        *,
        export: typing.Optional[typing.Union["OceanAksNpLoggingExport", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param export: export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#export OceanAksNp#export}
        '''
        if isinstance(export, dict):
            export = OceanAksNpLoggingExport(**export)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d156fe377db05f6a4069fe398c022baecb6a092091d38cc9d7fbad7fecffed7b)
            check_type(argname="argument export", value=export, expected_type=type_hints["export"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if export is not None:
            self._values["export"] = export

    @builtins.property
    def export(self) -> typing.Optional["OceanAksNpLoggingExport"]:
        '''export block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#export OceanAksNp#export}
        '''
        result = self._values.get("export")
        return typing.cast(typing.Optional["OceanAksNpLoggingExport"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLoggingExport",
    jsii_struct_bases=[],
    name_mapping={"azure_blob": "azureBlob"},
)
class OceanAksNpLoggingExport:
    def __init__(
        self,
        *,
        azure_blob: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpLoggingExportAzureBlob", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param azure_blob: azure_blob block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#azure_blob OceanAksNp#azure_blob}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe50d55636eef9a8157f73aa55fe0025419cd866f3c933bf3b98548b30dc485d)
            check_type(argname="argument azure_blob", value=azure_blob, expected_type=type_hints["azure_blob"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if azure_blob is not None:
            self._values["azure_blob"] = azure_blob

    @builtins.property
    def azure_blob(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLoggingExportAzureBlob"]]]:
        '''azure_blob block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#azure_blob OceanAksNp#azure_blob}
        '''
        result = self._values.get("azure_blob")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpLoggingExportAzureBlob"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpLoggingExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLoggingExportAzureBlob",
    jsii_struct_bases=[],
    name_mapping={"id": "id"},
)
class OceanAksNpLoggingExportAzureBlob:
    def __init__(self, *, id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#id OceanAksNp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ffe0f8d7d3df82c71566005ed9b28640311713ba639f24e05eef0389f1f7ab)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#id OceanAksNp#id}.

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
        return "OceanAksNpLoggingExportAzureBlob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpLoggingExportAzureBlobList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLoggingExportAzureBlobList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1584c6d366cc6e2d9237b1f5c95e0f136802b0a52886625fe59422e3c445173c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAksNpLoggingExportAzureBlobOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceeef09bd5db38e7e699ae577815c05064d4d673dbbe465008819178146336c4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpLoggingExportAzureBlobOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69e41e087c383e06651520239ff1a7315457f38e7e1619324d8c9bc56e147164)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a5d2b8511c3a1d00b9d22b2bcafc6e0d66d785b8084ec18b444786b9a1ea4c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa42aff99317bd3a52d4c6b465a7563d1835a83f4b3b018353a2dec4681e3aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLoggingExportAzureBlob]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLoggingExportAzureBlob]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLoggingExportAzureBlob]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764e26dbc7195ecccb52780b06bf6c09f99f91c2aaf96ab011eb0ee1a5781344)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpLoggingExportAzureBlobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLoggingExportAzureBlobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8a6f71acbb39539bdf061b08777732f3bad58108138c3e44b93be35db164991)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d37fb3c4a754fc9fc7d18a349e0797573a1e8a0b7802684d9076fbe128e87de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLoggingExportAzureBlob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLoggingExportAzureBlob]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLoggingExportAzureBlob]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f056638d2f806f340e0868033c8c881e8ce9541a21dc3c3d66463a523f4039f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpLoggingExportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLoggingExportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd44bace80407d64396bdbf341065588a00c812265fded0b9587add1153fbc33)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAzureBlob")
    def put_azure_blob(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLoggingExportAzureBlob, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cef225aa19730c762d086c6a44377a8585836fb9ddfc1bbb8af16784e14ad9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzureBlob", [value]))

    @jsii.member(jsii_name="resetAzureBlob")
    def reset_azure_blob(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureBlob", []))

    @builtins.property
    @jsii.member(jsii_name="azureBlob")
    def azure_blob(self) -> OceanAksNpLoggingExportAzureBlobList:
        return typing.cast(OceanAksNpLoggingExportAzureBlobList, jsii.get(self, "azureBlob"))

    @builtins.property
    @jsii.member(jsii_name="azureBlobInput")
    def azure_blob_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLoggingExportAzureBlob]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLoggingExportAzureBlob]]], jsii.get(self, "azureBlobInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpLoggingExport]:
        return typing.cast(typing.Optional[OceanAksNpLoggingExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpLoggingExport]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d914e5e8055cc691585c41dd6fe4fb640d55ab9c3f0d3f8a208e705d0ce7c357)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpLoggingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpLoggingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f558b1e496238e72703628034a805aaeaba3e0d38903a2f1c22dafcb4c72e818)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putExport")
    def put_export(
        self,
        *,
        azure_blob: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLoggingExportAzureBlob, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param azure_blob: azure_blob block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#azure_blob OceanAksNp#azure_blob}
        '''
        value = OceanAksNpLoggingExport(azure_blob=azure_blob)

        return typing.cast(None, jsii.invoke(self, "putExport", [value]))

    @jsii.member(jsii_name="resetExport")
    def reset_export(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExport", []))

    @builtins.property
    @jsii.member(jsii_name="export")
    def export(self) -> OceanAksNpLoggingExportOutputReference:
        return typing.cast(OceanAksNpLoggingExportOutputReference, jsii.get(self, "export"))

    @builtins.property
    @jsii.member(jsii_name="exportInput")
    def export_input(self) -> typing.Optional[OceanAksNpLoggingExport]:
        return typing.cast(typing.Optional[OceanAksNpLoggingExport], jsii.get(self, "exportInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpLogging]:
        return typing.cast(typing.Optional[OceanAksNpLogging], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpLogging]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e33b0379c397171ee9f059dd1dab9e92f3fdcadf93194209d82af7117c953feb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpScheduling",
    jsii_struct_bases=[],
    name_mapping={
        "shutdown_hours": "shutdownHours",
        "suspension_hours": "suspensionHours",
        "tasks": "tasks",
    },
)
class OceanAksNpScheduling:
    def __init__(
        self,
        *,
        shutdown_hours: typing.Optional[typing.Union["OceanAksNpSchedulingShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
        suspension_hours: typing.Optional[typing.Union["OceanAksNpSchedulingSuspensionHours", typing.Dict[builtins.str, typing.Any]]] = None,
        tasks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpSchedulingTasks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param shutdown_hours: shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#shutdown_hours OceanAksNp#shutdown_hours}
        :param suspension_hours: suspension_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#suspension_hours OceanAksNp#suspension_hours}
        :param tasks: tasks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#tasks OceanAksNp#tasks}
        '''
        if isinstance(shutdown_hours, dict):
            shutdown_hours = OceanAksNpSchedulingShutdownHours(**shutdown_hours)
        if isinstance(suspension_hours, dict):
            suspension_hours = OceanAksNpSchedulingSuspensionHours(**suspension_hours)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d20ebe1bf5190dc49c807ca036b51189ee29c47672aba96614a263fd410910)
            check_type(argname="argument shutdown_hours", value=shutdown_hours, expected_type=type_hints["shutdown_hours"])
            check_type(argname="argument suspension_hours", value=suspension_hours, expected_type=type_hints["suspension_hours"])
            check_type(argname="argument tasks", value=tasks, expected_type=type_hints["tasks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if shutdown_hours is not None:
            self._values["shutdown_hours"] = shutdown_hours
        if suspension_hours is not None:
            self._values["suspension_hours"] = suspension_hours
        if tasks is not None:
            self._values["tasks"] = tasks

    @builtins.property
    def shutdown_hours(self) -> typing.Optional["OceanAksNpSchedulingShutdownHours"]:
        '''shutdown_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#shutdown_hours OceanAksNp#shutdown_hours}
        '''
        result = self._values.get("shutdown_hours")
        return typing.cast(typing.Optional["OceanAksNpSchedulingShutdownHours"], result)

    @builtins.property
    def suspension_hours(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingSuspensionHours"]:
        '''suspension_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#suspension_hours OceanAksNp#suspension_hours}
        '''
        result = self._values.get("suspension_hours")
        return typing.cast(typing.Optional["OceanAksNpSchedulingSuspensionHours"], result)

    @builtins.property
    def tasks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpSchedulingTasks"]]]:
        '''tasks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#tasks OceanAksNp#tasks}
        '''
        result = self._values.get("tasks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpSchedulingTasks"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpScheduling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9b23839593ae1052707b8b8b15a603e7cd9124c4d6717d97ec9d541fdaccdff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putShutdownHours")
    def put_shutdown_hours(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.
        '''
        value = OceanAksNpSchedulingShutdownHours(
            is_enabled=is_enabled, time_windows=time_windows
        )

        return typing.cast(None, jsii.invoke(self, "putShutdownHours", [value]))

    @jsii.member(jsii_name="putSuspensionHours")
    def put_suspension_hours(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.
        '''
        value = OceanAksNpSchedulingSuspensionHours(
            is_enabled=is_enabled, time_windows=time_windows
        )

        return typing.cast(None, jsii.invoke(self, "putSuspensionHours", [value]))

    @jsii.member(jsii_name="putTasks")
    def put_tasks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpSchedulingTasks", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15b39c661ed05a9f01448888c1020c8dcff0527b75ace17602eaa7539e39020b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTasks", [value]))

    @jsii.member(jsii_name="resetShutdownHours")
    def reset_shutdown_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownHours", []))

    @jsii.member(jsii_name="resetSuspensionHours")
    def reset_suspension_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuspensionHours", []))

    @jsii.member(jsii_name="resetTasks")
    def reset_tasks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTasks", []))

    @builtins.property
    @jsii.member(jsii_name="shutdownHours")
    def shutdown_hours(self) -> "OceanAksNpSchedulingShutdownHoursOutputReference":
        return typing.cast("OceanAksNpSchedulingShutdownHoursOutputReference", jsii.get(self, "shutdownHours"))

    @builtins.property
    @jsii.member(jsii_name="suspensionHours")
    def suspension_hours(self) -> "OceanAksNpSchedulingSuspensionHoursOutputReference":
        return typing.cast("OceanAksNpSchedulingSuspensionHoursOutputReference", jsii.get(self, "suspensionHours"))

    @builtins.property
    @jsii.member(jsii_name="tasks")
    def tasks(self) -> "OceanAksNpSchedulingTasksList":
        return typing.cast("OceanAksNpSchedulingTasksList", jsii.get(self, "tasks"))

    @builtins.property
    @jsii.member(jsii_name="shutdownHoursInput")
    def shutdown_hours_input(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingShutdownHours"]:
        return typing.cast(typing.Optional["OceanAksNpSchedulingShutdownHours"], jsii.get(self, "shutdownHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="suspensionHoursInput")
    def suspension_hours_input(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingSuspensionHours"]:
        return typing.cast(typing.Optional["OceanAksNpSchedulingSuspensionHours"], jsii.get(self, "suspensionHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="tasksInput")
    def tasks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpSchedulingTasks"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpSchedulingTasks"]]], jsii.get(self, "tasksInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpScheduling]:
        return typing.cast(typing.Optional[OceanAksNpScheduling], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpScheduling]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42efce885b277ff0467b937bbf380f852367148461159c02ec153066704117d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingShutdownHours",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled", "time_windows": "timeWindows"},
)
class OceanAksNpSchedulingShutdownHours:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45995a95327fe7c1d819054ab0a424f8ca422d0b9989cab007cac55904f55d20)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument time_windows", value=time_windows, expected_type=type_hints["time_windows"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if time_windows is not None:
            self._values["time_windows"] = time_windows

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def time_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.'''
        result = self._values.get("time_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingShutdownHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingShutdownHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingShutdownHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2da2f3033c6c0996a552559a0b6b2dc185633de63eb50d3ab1530eca4263504b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetTimeWindows")
    def reset_time_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindows", []))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowsInput")
    def time_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "timeWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fbe117480707862ebd505639ed8d82ae9744065320b96e68870882b86dd58c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindows")
    def time_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeWindows"))

    @time_windows.setter
    def time_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1989117ce19416a2c34b64619e9eed1082a3c3788410b48d8909672540868a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpSchedulingShutdownHours]:
        return typing.cast(typing.Optional[OceanAksNpSchedulingShutdownHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpSchedulingShutdownHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14e4b92d6508fea86858f2a4cfdc5363c175f45496e7ee7f02dd5a3e7789fae5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingSuspensionHours",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled", "time_windows": "timeWindows"},
)
class OceanAksNpSchedulingSuspensionHours:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8380ceb37f5c1f295eb1e4c1df09484626fcf2e1b197ce5400f72fe9540b2287)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument time_windows", value=time_windows, expected_type=type_hints["time_windows"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if time_windows is not None:
            self._values["time_windows"] = time_windows

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def time_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.'''
        result = self._values.get("time_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingSuspensionHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingSuspensionHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingSuspensionHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2857f3c29220c3287de98027f3cd551187100955392a12731571da56d20bfebb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetTimeWindows")
    def reset_time_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindows", []))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowsInput")
    def time_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "timeWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3155feca379d5ced73699ccbdeed9647d03fc10b207cd42b8d2e24d3dca976e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindows")
    def time_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeWindows"))

    @time_windows.setter
    def time_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__983c0c87fd65b980a7a8a6b279f9cf4159af9e837c7629d87cd07c95c951fb10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpSchedulingSuspensionHours]:
        return typing.cast(typing.Optional[OceanAksNpSchedulingSuspensionHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpSchedulingSuspensionHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__808cd7581c48cac60dcd32df5be9dcfaeeab457d7d3913f897d3c0c0c013b3ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasks",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "is_enabled": "isEnabled",
        "task_type": "taskType",
        "parameters": "parameters",
    },
)
class OceanAksNpSchedulingTasks:
    def __init__(
        self,
        *,
        cron_expression: builtins.str,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        task_type: builtins.str,
        parameters: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParameters", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#cron_expression OceanAksNp#cron_expression}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#task_type OceanAksNp#task_type}.
        :param parameters: parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters OceanAksNp#parameters}
        '''
        if isinstance(parameters, dict):
            parameters = OceanAksNpSchedulingTasksParameters(**parameters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__886c35d1eacd76f0878e09490fdf346f9addc6b5ee55e7f8ce6d3b65d42229dd)
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument task_type", value=task_type, expected_type=type_hints["task_type"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron_expression": cron_expression,
            "is_enabled": is_enabled,
            "task_type": task_type,
        }
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def cron_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#cron_expression OceanAksNp#cron_expression}.'''
        result = self._values.get("cron_expression")
        assert result is not None, "Required property 'cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#task_type OceanAksNp#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Optional["OceanAksNpSchedulingTasksParameters"]:
        '''parameters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters OceanAksNp#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParameters"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingTasks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingTasksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__266da5cd48d9037ea288f30bbaf7a33c8b14f8fd39e6c5548f29d3613e33b3ce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAksNpSchedulingTasksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__884022db33c843a24208e3591d9215ddf258d3654beeb5c43ce37752f0b43723)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpSchedulingTasksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8f18095ea3caa6aa94775753a2d9dc778861366c2db37da34ffe9a5722ed32d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3bebc32bccd0cf313e99bd56e99cf8a1f1a02a8906f33d2d6a78a36175536ff7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__549510f5ea6e09d9389bf738c164e3909d0644cad443ad377ffac34e23873b42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpSchedulingTasks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpSchedulingTasks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpSchedulingTasks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44d2612e30d4687d37fc965bbb38c7074bdf572db91cba903c3d6cfbe40a3e4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpSchedulingTasksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__086c327ba908f251bbab8037fcc964bdc8a6dc82809e7dc9eab09db679c819ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putParameters")
    def put_parameters(
        self,
        *,
        parameters_cluster_roll: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParametersParametersClusterRoll", typing.Dict[builtins.str, typing.Any]]] = None,
        parameters_upgrade_config: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParametersParametersUpgradeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param parameters_cluster_roll: parameters_cluster_roll block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters_cluster_roll OceanAksNp#parameters_cluster_roll}
        :param parameters_upgrade_config: parameters_upgrade_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters_upgrade_config OceanAksNp#parameters_upgrade_config}
        '''
        value = OceanAksNpSchedulingTasksParameters(
            parameters_cluster_roll=parameters_cluster_roll,
            parameters_upgrade_config=parameters_upgrade_config,
        )

        return typing.cast(None, jsii.invoke(self, "putParameters", [value]))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> "OceanAksNpSchedulingTasksParametersOutputReference":
        return typing.cast("OceanAksNpSchedulingTasksParametersOutputReference", jsii.get(self, "parameters"))

    @builtins.property
    @jsii.member(jsii_name="cronExpressionInput")
    def cron_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronExpressionInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParameters"]:
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParameters"], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="taskTypeInput")
    def task_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cronExpression")
    def cron_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cronExpression"))

    @cron_expression.setter
    def cron_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe59e77c4dc9fd872b0ef2b27195f32369af93fc1ce73d603646730342691567)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cronExpression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5af831d8ef619ccd6cd7d9aa6837574d36b954f95bee93bf36998a92804bf61c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43a35911121bb9ea593acd403200b6a198f8b77041060f97b986c1ece550f8e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpSchedulingTasks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpSchedulingTasks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpSchedulingTasks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58b0425b4e8d71b35c23af2e495805f4a7d79dae727cd2b78f5d13d6782eb217)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParameters",
    jsii_struct_bases=[],
    name_mapping={
        "parameters_cluster_roll": "parametersClusterRoll",
        "parameters_upgrade_config": "parametersUpgradeConfig",
    },
)
class OceanAksNpSchedulingTasksParameters:
    def __init__(
        self,
        *,
        parameters_cluster_roll: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParametersParametersClusterRoll", typing.Dict[builtins.str, typing.Any]]] = None,
        parameters_upgrade_config: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParametersParametersUpgradeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param parameters_cluster_roll: parameters_cluster_roll block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters_cluster_roll OceanAksNp#parameters_cluster_roll}
        :param parameters_upgrade_config: parameters_upgrade_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters_upgrade_config OceanAksNp#parameters_upgrade_config}
        '''
        if isinstance(parameters_cluster_roll, dict):
            parameters_cluster_roll = OceanAksNpSchedulingTasksParametersParametersClusterRoll(**parameters_cluster_roll)
        if isinstance(parameters_upgrade_config, dict):
            parameters_upgrade_config = OceanAksNpSchedulingTasksParametersParametersUpgradeConfig(**parameters_upgrade_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b9907b2a24cf36967ce0a3cd8b764343deea6fa183c4af33ed85e100f179d77)
            check_type(argname="argument parameters_cluster_roll", value=parameters_cluster_roll, expected_type=type_hints["parameters_cluster_roll"])
            check_type(argname="argument parameters_upgrade_config", value=parameters_upgrade_config, expected_type=type_hints["parameters_upgrade_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if parameters_cluster_roll is not None:
            self._values["parameters_cluster_roll"] = parameters_cluster_roll
        if parameters_upgrade_config is not None:
            self._values["parameters_upgrade_config"] = parameters_upgrade_config

    @builtins.property
    def parameters_cluster_roll(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParametersParametersClusterRoll"]:
        '''parameters_cluster_roll block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters_cluster_roll OceanAksNp#parameters_cluster_roll}
        '''
        result = self._values.get("parameters_cluster_roll")
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParametersParametersClusterRoll"], result)

    @builtins.property
    def parameters_upgrade_config(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfig"]:
        '''parameters_upgrade_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#parameters_upgrade_config OceanAksNp#parameters_upgrade_config}
        '''
        result = self._values.get("parameters_upgrade_config")
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingTasksParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingTasksParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf3bd50cf7dedc23b0358db62af28d28f0c6e2a704cf6e83db5def19647b1f47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putParametersClusterRoll")
    def put_parameters_cluster_roll(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vng_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.
        :param vng_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_ids OceanAksNp#vng_ids}.
        '''
        value = OceanAksNpSchedulingTasksParametersParametersClusterRoll(
            batch_min_healthy_percentage=batch_min_healthy_percentage,
            batch_size_percentage=batch_size_percentage,
            comment=comment,
            respect_pdb=respect_pdb,
            respect_restrict_scale_down=respect_restrict_scale_down,
            vng_ids=vng_ids,
        )

        return typing.cast(None, jsii.invoke(self, "putParametersClusterRoll", [value]))

    @jsii.member(jsii_name="putParametersUpgradeConfig")
    def put_parameters_upgrade_config(
        self,
        *,
        apply_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_parameters: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        scope_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param apply_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#apply_roll OceanAksNp#apply_roll}.
        :param roll_parameters: roll_parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#roll_parameters OceanAksNp#roll_parameters}
        :param scope_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#scope_version OceanAksNp#scope_version}.
        '''
        value = OceanAksNpSchedulingTasksParametersParametersUpgradeConfig(
            apply_roll=apply_roll,
            roll_parameters=roll_parameters,
            scope_version=scope_version,
        )

        return typing.cast(None, jsii.invoke(self, "putParametersUpgradeConfig", [value]))

    @jsii.member(jsii_name="resetParametersClusterRoll")
    def reset_parameters_cluster_roll(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParametersClusterRoll", []))

    @jsii.member(jsii_name="resetParametersUpgradeConfig")
    def reset_parameters_upgrade_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParametersUpgradeConfig", []))

    @builtins.property
    @jsii.member(jsii_name="parametersClusterRoll")
    def parameters_cluster_roll(
        self,
    ) -> "OceanAksNpSchedulingTasksParametersParametersClusterRollOutputReference":
        return typing.cast("OceanAksNpSchedulingTasksParametersParametersClusterRollOutputReference", jsii.get(self, "parametersClusterRoll"))

    @builtins.property
    @jsii.member(jsii_name="parametersUpgradeConfig")
    def parameters_upgrade_config(
        self,
    ) -> "OceanAksNpSchedulingTasksParametersParametersUpgradeConfigOutputReference":
        return typing.cast("OceanAksNpSchedulingTasksParametersParametersUpgradeConfigOutputReference", jsii.get(self, "parametersUpgradeConfig"))

    @builtins.property
    @jsii.member(jsii_name="parametersClusterRollInput")
    def parameters_cluster_roll_input(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParametersParametersClusterRoll"]:
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParametersParametersClusterRoll"], jsii.get(self, "parametersClusterRollInput"))

    @builtins.property
    @jsii.member(jsii_name="parametersUpgradeConfigInput")
    def parameters_upgrade_config_input(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfig"]:
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfig"], jsii.get(self, "parametersUpgradeConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpSchedulingTasksParameters]:
        return typing.cast(typing.Optional[OceanAksNpSchedulingTasksParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpSchedulingTasksParameters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf2f5b4dfb05448d73dc215a7a0088210e8592c564e06547c8d80f67f945e016)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersParametersClusterRoll",
    jsii_struct_bases=[],
    name_mapping={
        "batch_min_healthy_percentage": "batchMinHealthyPercentage",
        "batch_size_percentage": "batchSizePercentage",
        "comment": "comment",
        "respect_pdb": "respectPdb",
        "respect_restrict_scale_down": "respectRestrictScaleDown",
        "vng_ids": "vngIds",
    },
)
class OceanAksNpSchedulingTasksParametersParametersClusterRoll:
    def __init__(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vng_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.
        :param vng_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_ids OceanAksNp#vng_ids}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b1cc3dc3ea7233c35f256f478486df048766679deef708b05cc8994702fa372)
            check_type(argname="argument batch_min_healthy_percentage", value=batch_min_healthy_percentage, expected_type=type_hints["batch_min_healthy_percentage"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument respect_pdb", value=respect_pdb, expected_type=type_hints["respect_pdb"])
            check_type(argname="argument respect_restrict_scale_down", value=respect_restrict_scale_down, expected_type=type_hints["respect_restrict_scale_down"])
            check_type(argname="argument vng_ids", value=vng_ids, expected_type=type_hints["vng_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_min_healthy_percentage is not None:
            self._values["batch_min_healthy_percentage"] = batch_min_healthy_percentage
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if comment is not None:
            self._values["comment"] = comment
        if respect_pdb is not None:
            self._values["respect_pdb"] = respect_pdb
        if respect_restrict_scale_down is not None:
            self._values["respect_restrict_scale_down"] = respect_restrict_scale_down
        if vng_ids is not None:
            self._values["vng_ids"] = vng_ids

    @builtins.property
    def batch_min_healthy_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.'''
        result = self._values.get("batch_min_healthy_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def respect_restrict_scale_down(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.'''
        result = self._values.get("respect_restrict_scale_down")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vng_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_ids OceanAksNp#vng_ids}.'''
        result = self._values.get("vng_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingTasksParametersParametersClusterRoll(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingTasksParametersParametersClusterRollOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersParametersClusterRollOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5822b57563e068270584d55720a376522aa52dd4d9f371d2dd8c90c7929e203)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBatchMinHealthyPercentage")
    def reset_batch_min_healthy_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchMinHealthyPercentage", []))

    @jsii.member(jsii_name="resetBatchSizePercentage")
    def reset_batch_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSizePercentage", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetRespectPdb")
    def reset_respect_pdb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectPdb", []))

    @jsii.member(jsii_name="resetRespectRestrictScaleDown")
    def reset_respect_restrict_scale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectRestrictScaleDown", []))

    @jsii.member(jsii_name="resetVngIds")
    def reset_vng_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVngIds", []))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentageInput")
    def batch_min_healthy_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchMinHealthyPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="respectPdbInput")
    def respect_pdb_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectPdbInput"))

    @builtins.property
    @jsii.member(jsii_name="respectRestrictScaleDownInput")
    def respect_restrict_scale_down_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectRestrictScaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="vngIdsInput")
    def vng_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vngIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentage")
    def batch_min_healthy_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchMinHealthyPercentage"))

    @batch_min_healthy_percentage.setter
    def batch_min_healthy_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__194e514c8a9feeb243dcbe3bd1f0f161a1388b6ea8a4e965ccd427413dad5402)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchMinHealthyPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8aa290cff09d72812cb3adcabc0e359bdb5de5d46a618f0c8f0af3a6d32192d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feb707807d52a3a8966fca6352434777ba4b658612ea4a92907dfe7d88a9cc61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectPdb")
    def respect_pdb(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "respectPdb"))

    @respect_pdb.setter
    def respect_pdb(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f8739c7a45a606b90b7db6fba5033019009106ad5085db0b061a8a60dd4a490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectPdb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectRestrictScaleDown")
    def respect_restrict_scale_down(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "respectRestrictScaleDown"))

    @respect_restrict_scale_down.setter
    def respect_restrict_scale_down(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e68fddb5ef37ea0dbc5989af6ed916daa456f824db5f7ac20cee55c69f80ebeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectRestrictScaleDown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vngIds")
    def vng_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vngIds"))

    @vng_ids.setter
    def vng_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d85f8e8a3c505180b0c054fcb1fa30a6e6404b3556af61a6f12019cba6817e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vngIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpSchedulingTasksParametersParametersClusterRoll]:
        return typing.cast(typing.Optional[OceanAksNpSchedulingTasksParametersParametersClusterRoll], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpSchedulingTasksParametersParametersClusterRoll],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44f42b1e2a080f30c382c7b250d1d38492b4d59e0307d01ce52401d56e829a9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersParametersUpgradeConfig",
    jsii_struct_bases=[],
    name_mapping={
        "apply_roll": "applyRoll",
        "roll_parameters": "rollParameters",
        "scope_version": "scopeVersion",
    },
)
class OceanAksNpSchedulingTasksParametersParametersUpgradeConfig:
    def __init__(
        self,
        *,
        apply_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_parameters: typing.Optional[typing.Union["OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        scope_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param apply_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#apply_roll OceanAksNp#apply_roll}.
        :param roll_parameters: roll_parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#roll_parameters OceanAksNp#roll_parameters}
        :param scope_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#scope_version OceanAksNp#scope_version}.
        '''
        if isinstance(roll_parameters, dict):
            roll_parameters = OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters(**roll_parameters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__338acb605f6c57c0e4413ba5d541be9f8452fb2f2f71ef1c50f9fb64b21f3187)
            check_type(argname="argument apply_roll", value=apply_roll, expected_type=type_hints["apply_roll"])
            check_type(argname="argument roll_parameters", value=roll_parameters, expected_type=type_hints["roll_parameters"])
            check_type(argname="argument scope_version", value=scope_version, expected_type=type_hints["scope_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if apply_roll is not None:
            self._values["apply_roll"] = apply_roll
        if roll_parameters is not None:
            self._values["roll_parameters"] = roll_parameters
        if scope_version is not None:
            self._values["scope_version"] = scope_version

    @builtins.property
    def apply_roll(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#apply_roll OceanAksNp#apply_roll}.'''
        result = self._values.get("apply_roll")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def roll_parameters(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters"]:
        '''roll_parameters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#roll_parameters OceanAksNp#roll_parameters}
        '''
        result = self._values.get("roll_parameters")
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters"], result)

    @builtins.property
    def scope_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#scope_version OceanAksNp#scope_version}.'''
        result = self._values.get("scope_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingTasksParametersParametersUpgradeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingTasksParametersParametersUpgradeConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersParametersUpgradeConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9623928249b4f92b89972f63125bda546bb137dcb86879691869efc9def21ebf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRollParameters")
    def put_roll_parameters(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.
        '''
        value = OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters(
            batch_min_healthy_percentage=batch_min_healthy_percentage,
            batch_size_percentage=batch_size_percentage,
            comment=comment,
            respect_pdb=respect_pdb,
            respect_restrict_scale_down=respect_restrict_scale_down,
        )

        return typing.cast(None, jsii.invoke(self, "putRollParameters", [value]))

    @jsii.member(jsii_name="resetApplyRoll")
    def reset_apply_roll(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyRoll", []))

    @jsii.member(jsii_name="resetRollParameters")
    def reset_roll_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollParameters", []))

    @jsii.member(jsii_name="resetScopeVersion")
    def reset_scope_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScopeVersion", []))

    @builtins.property
    @jsii.member(jsii_name="rollParameters")
    def roll_parameters(
        self,
    ) -> "OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParametersOutputReference":
        return typing.cast("OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParametersOutputReference", jsii.get(self, "rollParameters"))

    @builtins.property
    @jsii.member(jsii_name="applyRollInput")
    def apply_roll_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "applyRollInput"))

    @builtins.property
    @jsii.member(jsii_name="rollParametersInput")
    def roll_parameters_input(
        self,
    ) -> typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters"]:
        return typing.cast(typing.Optional["OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters"], jsii.get(self, "rollParametersInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeVersionInput")
    def scope_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="applyRoll")
    def apply_roll(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "applyRoll"))

    @apply_roll.setter
    def apply_roll(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1004ac03e35e15792cf8b03b3f55beeaf29bf24e4294083a177cc881aa98291d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applyRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scopeVersion")
    def scope_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scopeVersion"))

    @scope_version.setter
    def scope_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c595d2089140bcd69eaea6f1905f15bfc98d40deb9f593e4ce3ef8b80918d0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scopeVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfig]:
        return typing.cast(typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25f01abe696ab85006a08a8d8865ed632eaa038f8a782400feab5f05a5122990)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters",
    jsii_struct_bases=[],
    name_mapping={
        "batch_min_healthy_percentage": "batchMinHealthyPercentage",
        "batch_size_percentage": "batchSizePercentage",
        "comment": "comment",
        "respect_pdb": "respectPdb",
        "respect_restrict_scale_down": "respectRestrictScaleDown",
    },
)
class OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters:
    def __init__(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5747794851778866f65c44aa52e33f1178a84d544f67285cdf010c348b36580)
            check_type(argname="argument batch_min_healthy_percentage", value=batch_min_healthy_percentage, expected_type=type_hints["batch_min_healthy_percentage"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument respect_pdb", value=respect_pdb, expected_type=type_hints["respect_pdb"])
            check_type(argname="argument respect_restrict_scale_down", value=respect_restrict_scale_down, expected_type=type_hints["respect_restrict_scale_down"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_min_healthy_percentage is not None:
            self._values["batch_min_healthy_percentage"] = batch_min_healthy_percentage
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if comment is not None:
            self._values["comment"] = comment
        if respect_pdb is not None:
            self._values["respect_pdb"] = respect_pdb
        if respect_restrict_scale_down is not None:
            self._values["respect_restrict_scale_down"] = respect_restrict_scale_down

    @builtins.property
    def batch_min_healthy_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.'''
        result = self._values.get("batch_min_healthy_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def respect_restrict_scale_down(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.'''
        result = self._values.get("respect_restrict_scale_down")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__acce90216efdd55f3d60003ef62ee8ba2611adaeba73e251f393b14e6c7b18ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBatchMinHealthyPercentage")
    def reset_batch_min_healthy_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchMinHealthyPercentage", []))

    @jsii.member(jsii_name="resetBatchSizePercentage")
    def reset_batch_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSizePercentage", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetRespectPdb")
    def reset_respect_pdb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectPdb", []))

    @jsii.member(jsii_name="resetRespectRestrictScaleDown")
    def reset_respect_restrict_scale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectRestrictScaleDown", []))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentageInput")
    def batch_min_healthy_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchMinHealthyPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="respectPdbInput")
    def respect_pdb_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectPdbInput"))

    @builtins.property
    @jsii.member(jsii_name="respectRestrictScaleDownInput")
    def respect_restrict_scale_down_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectRestrictScaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentage")
    def batch_min_healthy_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchMinHealthyPercentage"))

    @batch_min_healthy_percentage.setter
    def batch_min_healthy_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__607dfee7ca94567e65d560ccc0c9daa6f8d4ebb8198a78b302923c2dea962f59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchMinHealthyPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eacbede4667fe02f5630c7ab512e29814cf7033d8ac07d0ab0852b945d75435e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d2411d6ca28c567a41703c9a60bfe69e91b1913b53d04e34d009c0f9649d1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectPdb")
    def respect_pdb(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "respectPdb"))

    @respect_pdb.setter
    def respect_pdb(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8d746ffe55bd35e005d44ecdce0de27e03167230c2ebe7f0aeaeb21546d21b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectPdb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectRestrictScaleDown")
    def respect_restrict_scale_down(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "respectRestrictScaleDown"))

    @respect_restrict_scale_down.setter
    def respect_restrict_scale_down(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__982be9ce1cf810dc0238926433d8ea1b64aa15a92826baacbad7383020395a40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectRestrictScaleDown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters]:
        return typing.cast(typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8505c638c7aa6aadaf863c102dbf1e456b9e1d6bd6b74cbfca2bf655d9e6ef28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpTaints",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class OceanAksNpTaints:
    def __init__(
        self,
        *,
        effect: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param effect: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#effect OceanAksNp#effect}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#key OceanAksNp#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#value OceanAksNp#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6405863ddb06d92e42ec8b68ae430bf71f9a78bd1de8330ebbcddc3ca14513e0)
            check_type(argname="argument effect", value=effect, expected_type=type_hints["effect"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "effect": effect,
            "key": key,
            "value": value,
        }

    @builtins.property
    def effect(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#effect OceanAksNp#effect}.'''
        result = self._values.get("effect")
        assert result is not None, "Required property 'effect' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#key OceanAksNp#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#value OceanAksNp#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpTaints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpTaintsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpTaintsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bccda8cff8cd35b59025ec8505ae5fef9bfa67836a9cd38cf0f2f53a737987d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAksNpTaintsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b95f7d63d51367ba18f9f7d56ba2e32e41750219476e19d2ed683779fc4256a1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpTaintsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c75766fdebefc353d55778a076ee6e4f138f125e5f72271728bf2434a85cad83)
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
            type_hints = typing.get_type_hints(_typecheckingstub__632b24880a1a359914183f1c3a99b8b8707d6466d37f1084522e41e32743e5e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd76d67d3386fe6c4659ed18f908692fc1a8437689f5a219ff90eb46ecc201d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpTaints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpTaints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpTaints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c763e184885cbbe077123246e2b44527a3a7ea4fe0301a3cdfa6785f665af98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpTaintsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpTaintsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__34ba3872921f82627c72bff53a3eece25ceeb53d9cb5bf35255f53df547da01b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="effectInput")
    def effect_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "effectInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="effect")
    def effect(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "effect"))

    @effect.setter
    def effect(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cdae04ccbf75d107ac77c7b8c396f84d8867842e85ac8217f6093f7bdcbdbbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aadbec3dcbf826a8c26fa439ed539ef2f4cfe6b707a11d13a6c34bd18530b53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__269fb8f3eac05193692e73d537ce2f5cab783d3e2acf3abfbe8214f97e39f5ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpTaints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpTaints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpTaints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3c1159b06026c1f8e7afbe40fa9df934025ce9377970e157eaa9cf002e9c6fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpUpdatePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "should_roll": "shouldRoll",
        "conditioned_roll": "conditionedRoll",
        "roll_config": "rollConfig",
    },
)
class OceanAksNpUpdatePolicy:
    def __init__(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_config: typing.Optional[typing.Union["OceanAksNpUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#should_roll OceanAksNp#should_roll}.
        :param conditioned_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#conditioned_roll OceanAksNp#conditioned_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#roll_config OceanAksNp#roll_config}
        '''
        if isinstance(roll_config, dict):
            roll_config = OceanAksNpUpdatePolicyRollConfig(**roll_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce9c2f16a9795bd9fd5dcb470fee2b36b5a6d0b0035268caec8193aafab17b6d)
            check_type(argname="argument should_roll", value=should_roll, expected_type=type_hints["should_roll"])
            check_type(argname="argument conditioned_roll", value=conditioned_roll, expected_type=type_hints["conditioned_roll"])
            check_type(argname="argument roll_config", value=roll_config, expected_type=type_hints["roll_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "should_roll": should_roll,
        }
        if conditioned_roll is not None:
            self._values["conditioned_roll"] = conditioned_roll
        if roll_config is not None:
            self._values["roll_config"] = roll_config

    @builtins.property
    def should_roll(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#should_roll OceanAksNp#should_roll}.'''
        result = self._values.get("should_roll")
        assert result is not None, "Required property 'should_roll' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def conditioned_roll(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#conditioned_roll OceanAksNp#conditioned_roll}.'''
        result = self._values.get("conditioned_roll")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def roll_config(self) -> typing.Optional["OceanAksNpUpdatePolicyRollConfig"]:
        '''roll_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#roll_config OceanAksNp#roll_config}
        '''
        result = self._values.get("roll_config")
        return typing.cast(typing.Optional["OceanAksNpUpdatePolicyRollConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpUpdatePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpUpdatePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpUpdatePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac5346277bffb8fd551d046e372650d461b56703fec4419aa2d69b940d17e81d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRollConfig")
    def put_roll_config(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        node_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_pool_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vng_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.
        :param node_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#node_names OceanAksNp#node_names}.
        :param node_pool_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#node_pool_names OceanAksNp#node_pool_names}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.
        :param vng_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_ids OceanAksNp#vng_ids}.
        '''
        value = OceanAksNpUpdatePolicyRollConfig(
            batch_min_healthy_percentage=batch_min_healthy_percentage,
            batch_size_percentage=batch_size_percentage,
            comment=comment,
            node_names=node_names,
            node_pool_names=node_pool_names,
            respect_pdb=respect_pdb,
            respect_restrict_scale_down=respect_restrict_scale_down,
            vng_ids=vng_ids,
        )

        return typing.cast(None, jsii.invoke(self, "putRollConfig", [value]))

    @jsii.member(jsii_name="resetConditionedRoll")
    def reset_conditioned_roll(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConditionedRoll", []))

    @jsii.member(jsii_name="resetRollConfig")
    def reset_roll_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollConfig", []))

    @builtins.property
    @jsii.member(jsii_name="rollConfig")
    def roll_config(self) -> "OceanAksNpUpdatePolicyRollConfigOutputReference":
        return typing.cast("OceanAksNpUpdatePolicyRollConfigOutputReference", jsii.get(self, "rollConfig"))

    @builtins.property
    @jsii.member(jsii_name="conditionedRollInput")
    def conditioned_roll_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "conditionedRollInput"))

    @builtins.property
    @jsii.member(jsii_name="rollConfigInput")
    def roll_config_input(self) -> typing.Optional["OceanAksNpUpdatePolicyRollConfig"]:
        return typing.cast(typing.Optional["OceanAksNpUpdatePolicyRollConfig"], jsii.get(self, "rollConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldRollInput")
    def should_roll_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldRollInput"))

    @builtins.property
    @jsii.member(jsii_name="conditionedRoll")
    def conditioned_roll(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "conditionedRoll"))

    @conditioned_roll.setter
    def conditioned_roll(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__565e11b54a9c42ab141ca566a3d6533e91743b49796ab9e8a0130896cbea6a7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "conditionedRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldRoll")
    def should_roll(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldRoll"))

    @should_roll.setter
    def should_roll(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b933b43c4fc81b7263c3640fe4eb0855f7140768991752d595ec5758658a318)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpUpdatePolicy]:
        return typing.cast(typing.Optional[OceanAksNpUpdatePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanAksNpUpdatePolicy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d506ffc0d400681884bf816d782980b1e8851db04b4c493f776a7ab4ddbe4570)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpUpdatePolicyRollConfig",
    jsii_struct_bases=[],
    name_mapping={
        "batch_min_healthy_percentage": "batchMinHealthyPercentage",
        "batch_size_percentage": "batchSizePercentage",
        "comment": "comment",
        "node_names": "nodeNames",
        "node_pool_names": "nodePoolNames",
        "respect_pdb": "respectPdb",
        "respect_restrict_scale_down": "respectRestrictScaleDown",
        "vng_ids": "vngIds",
    },
)
class OceanAksNpUpdatePolicyRollConfig:
    def __init__(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        node_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_pool_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vng_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.
        :param node_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#node_names OceanAksNp#node_names}.
        :param node_pool_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#node_pool_names OceanAksNp#node_pool_names}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.
        :param vng_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_ids OceanAksNp#vng_ids}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b182af76c226516b07c3d827174a66e96d48b5cf3001ff6512aca0cf705376ad)
            check_type(argname="argument batch_min_healthy_percentage", value=batch_min_healthy_percentage, expected_type=type_hints["batch_min_healthy_percentage"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument node_names", value=node_names, expected_type=type_hints["node_names"])
            check_type(argname="argument node_pool_names", value=node_pool_names, expected_type=type_hints["node_pool_names"])
            check_type(argname="argument respect_pdb", value=respect_pdb, expected_type=type_hints["respect_pdb"])
            check_type(argname="argument respect_restrict_scale_down", value=respect_restrict_scale_down, expected_type=type_hints["respect_restrict_scale_down"])
            check_type(argname="argument vng_ids", value=vng_ids, expected_type=type_hints["vng_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_min_healthy_percentage is not None:
            self._values["batch_min_healthy_percentage"] = batch_min_healthy_percentage
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if comment is not None:
            self._values["comment"] = comment
        if node_names is not None:
            self._values["node_names"] = node_names
        if node_pool_names is not None:
            self._values["node_pool_names"] = node_pool_names
        if respect_pdb is not None:
            self._values["respect_pdb"] = respect_pdb
        if respect_restrict_scale_down is not None:
            self._values["respect_restrict_scale_down"] = respect_restrict_scale_down
        if vng_ids is not None:
            self._values["vng_ids"] = vng_ids

    @builtins.property
    def batch_min_healthy_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_min_healthy_percentage OceanAksNp#batch_min_healthy_percentage}.'''
        result = self._values.get("batch_min_healthy_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#batch_size_percentage OceanAksNp#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#comment OceanAksNp#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#node_names OceanAksNp#node_names}.'''
        result = self._values.get("node_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node_pool_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#node_pool_names OceanAksNp#node_pool_names}.'''
        result = self._values.get("node_pool_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_pdb OceanAksNp#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def respect_restrict_scale_down(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#respect_restrict_scale_down OceanAksNp#respect_restrict_scale_down}.'''
        result = self._values.get("respect_restrict_scale_down")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vng_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_ids OceanAksNp#vng_ids}.'''
        result = self._values.get("vng_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpUpdatePolicyRollConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpUpdatePolicyRollConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpUpdatePolicyRollConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5234d2d6be4a415bd953ddcec6775059b8b271f5c5aff3d161036ffd830591bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBatchMinHealthyPercentage")
    def reset_batch_min_healthy_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchMinHealthyPercentage", []))

    @jsii.member(jsii_name="resetBatchSizePercentage")
    def reset_batch_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSizePercentage", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetNodeNames")
    def reset_node_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeNames", []))

    @jsii.member(jsii_name="resetNodePoolNames")
    def reset_node_pool_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodePoolNames", []))

    @jsii.member(jsii_name="resetRespectPdb")
    def reset_respect_pdb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectPdb", []))

    @jsii.member(jsii_name="resetRespectRestrictScaleDown")
    def reset_respect_restrict_scale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectRestrictScaleDown", []))

    @jsii.member(jsii_name="resetVngIds")
    def reset_vng_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVngIds", []))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentageInput")
    def batch_min_healthy_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchMinHealthyPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeNamesInput")
    def node_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "nodeNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="nodePoolNamesInput")
    def node_pool_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "nodePoolNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="respectPdbInput")
    def respect_pdb_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectPdbInput"))

    @builtins.property
    @jsii.member(jsii_name="respectRestrictScaleDownInput")
    def respect_restrict_scale_down_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectRestrictScaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="vngIdsInput")
    def vng_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vngIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentage")
    def batch_min_healthy_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchMinHealthyPercentage"))

    @batch_min_healthy_percentage.setter
    def batch_min_healthy_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95c2891a25a56543111c5a7b6acfe44b34d649d3eab9442bc686dfd5452c1cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchMinHealthyPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab39726d56d78433e30267b04aa11e1d96f6434975bb252565323aadb12caef0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb6c329913c7ed6226ace411aad44adcf1c7186c87cd1bb38822d8cf8e314012)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeNames")
    def node_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nodeNames"))

    @node_names.setter
    def node_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7c06be99cd0fc42e9b8774671a3397987284dc1b3c41fdd4dc36b97b7583a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodePoolNames")
    def node_pool_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nodePoolNames"))

    @node_pool_names.setter
    def node_pool_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3af7f51e6d9fee999b871585a48241a26aab37a85c1991a7934cd4b0960d5c40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodePoolNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectPdb")
    def respect_pdb(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "respectPdb"))

    @respect_pdb.setter
    def respect_pdb(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75b4ddaf9dbc5ee043ac111a8ffbccb641c346a299e76d5567e894cfdd081dcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectPdb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="respectRestrictScaleDown")
    def respect_restrict_scale_down(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "respectRestrictScaleDown"))

    @respect_restrict_scale_down.setter
    def respect_restrict_scale_down(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6066be617e9b4ddfecea5670744b4a4be431096a6e1fc0570f45f2947daf9c4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectRestrictScaleDown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vngIds")
    def vng_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vngIds"))

    @vng_ids.setter
    def vng_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ada835d08af167db3c696cd40121ebdf97e4cf0d087a155787dd42e84dc7da6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vngIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpUpdatePolicyRollConfig]:
        return typing.cast(typing.Optional[OceanAksNpUpdatePolicyRollConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpUpdatePolicyRollConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f14360bcf6cc0bb9b7d4d0f4bcf43ee982ae93bf07011f577ca25a902197ece9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpVngTemplateScheduling",
    jsii_struct_bases=[],
    name_mapping={"vng_template_shutdown_hours": "vngTemplateShutdownHours"},
)
class OceanAksNpVngTemplateScheduling:
    def __init__(
        self,
        *,
        vng_template_shutdown_hours: typing.Optional[typing.Union["OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param vng_template_shutdown_hours: vng_template_shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_template_shutdown_hours OceanAksNp#vng_template_shutdown_hours}
        '''
        if isinstance(vng_template_shutdown_hours, dict):
            vng_template_shutdown_hours = OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours(**vng_template_shutdown_hours)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c43878e3b329bf24eda94ac3cd08e688a3e48b1a7b739c8e6ab2c6b536e0d2d)
            check_type(argname="argument vng_template_shutdown_hours", value=vng_template_shutdown_hours, expected_type=type_hints["vng_template_shutdown_hours"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if vng_template_shutdown_hours is not None:
            self._values["vng_template_shutdown_hours"] = vng_template_shutdown_hours

    @builtins.property
    def vng_template_shutdown_hours(
        self,
    ) -> typing.Optional["OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours"]:
        '''vng_template_shutdown_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#vng_template_shutdown_hours OceanAksNp#vng_template_shutdown_hours}
        '''
        result = self._values.get("vng_template_shutdown_hours")
        return typing.cast(typing.Optional["OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVngTemplateScheduling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVngTemplateSchedulingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpVngTemplateSchedulingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f615ec33beaf45ab70f2179c693011fc31895ed18574beef492a776d0d270d1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putVngTemplateShutdownHours")
    def put_vng_template_shutdown_hours(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.
        '''
        value = OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours(
            is_enabled=is_enabled, time_windows=time_windows
        )

        return typing.cast(None, jsii.invoke(self, "putVngTemplateShutdownHours", [value]))

    @jsii.member(jsii_name="resetVngTemplateShutdownHours")
    def reset_vng_template_shutdown_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVngTemplateShutdownHours", []))

    @builtins.property
    @jsii.member(jsii_name="vngTemplateShutdownHours")
    def vng_template_shutdown_hours(
        self,
    ) -> "OceanAksNpVngTemplateSchedulingVngTemplateShutdownHoursOutputReference":
        return typing.cast("OceanAksNpVngTemplateSchedulingVngTemplateShutdownHoursOutputReference", jsii.get(self, "vngTemplateShutdownHours"))

    @builtins.property
    @jsii.member(jsii_name="vngTemplateShutdownHoursInput")
    def vng_template_shutdown_hours_input(
        self,
    ) -> typing.Optional["OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours"]:
        return typing.cast(typing.Optional["OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours"], jsii.get(self, "vngTemplateShutdownHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpVngTemplateScheduling]:
        return typing.cast(typing.Optional[OceanAksNpVngTemplateScheduling], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVngTemplateScheduling],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06bc9853e084f47f96c5c7e3f735b21cb8f60e9164a29793f68191a1151a69a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled", "time_windows": "timeWindows"},
)
class OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a1af472e7648d6e50b46ea53b67e88ff375a7dcaccab4453f369430d219d590)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument time_windows", value=time_windows, expected_type=type_hints["time_windows"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if time_windows is not None:
            self._values["time_windows"] = time_windows

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#is_enabled OceanAksNp#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def time_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np#time_windows OceanAksNp#time_windows}.'''
        result = self._values.get("time_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVngTemplateSchedulingVngTemplateShutdownHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNp.OceanAksNpVngTemplateSchedulingVngTemplateShutdownHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f429090177823c14c1770e8fd7cd861782af42785961232549852abdbe8724d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetTimeWindows")
    def reset_time_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindows", []))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowsInput")
    def time_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "timeWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0d24c0c94de18b6a222be575cd83d2f520bb2ef5eb771f4689d853a98dd0b44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindows")
    def time_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeWindows"))

    @time_windows.setter
    def time_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77140cb241f6109405c24346503f1a6d31b24803b5e9185d255b9c715d8297f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours]:
        return typing.cast(typing.Optional[OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c559a6eba1df4d4af0a4f5f872f45f4de3f40f6cfa3161410a8fdfda87ecd12d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanAksNp",
    "OceanAksNpAutoscaler",
    "OceanAksNpAutoscalerAutoscaleDown",
    "OceanAksNpAutoscalerAutoscaleDownOutputReference",
    "OceanAksNpAutoscalerAutoscaleHeadroom",
    "OceanAksNpAutoscalerAutoscaleHeadroomAutomatic",
    "OceanAksNpAutoscalerAutoscaleHeadroomAutomaticOutputReference",
    "OceanAksNpAutoscalerAutoscaleHeadroomOutputReference",
    "OceanAksNpAutoscalerOutputReference",
    "OceanAksNpAutoscalerResourceLimits",
    "OceanAksNpAutoscalerResourceLimitsOutputReference",
    "OceanAksNpConfig",
    "OceanAksNpFilters",
    "OceanAksNpFiltersOutputReference",
    "OceanAksNpHeadrooms",
    "OceanAksNpHeadroomsList",
    "OceanAksNpHeadroomsOutputReference",
    "OceanAksNpHealth",
    "OceanAksNpHealthOutputReference",
    "OceanAksNpLinuxOsConfig",
    "OceanAksNpLinuxOsConfigList",
    "OceanAksNpLinuxOsConfigOutputReference",
    "OceanAksNpLinuxOsConfigSysctls",
    "OceanAksNpLinuxOsConfigSysctlsList",
    "OceanAksNpLinuxOsConfigSysctlsOutputReference",
    "OceanAksNpLogging",
    "OceanAksNpLoggingExport",
    "OceanAksNpLoggingExportAzureBlob",
    "OceanAksNpLoggingExportAzureBlobList",
    "OceanAksNpLoggingExportAzureBlobOutputReference",
    "OceanAksNpLoggingExportOutputReference",
    "OceanAksNpLoggingOutputReference",
    "OceanAksNpScheduling",
    "OceanAksNpSchedulingOutputReference",
    "OceanAksNpSchedulingShutdownHours",
    "OceanAksNpSchedulingShutdownHoursOutputReference",
    "OceanAksNpSchedulingSuspensionHours",
    "OceanAksNpSchedulingSuspensionHoursOutputReference",
    "OceanAksNpSchedulingTasks",
    "OceanAksNpSchedulingTasksList",
    "OceanAksNpSchedulingTasksOutputReference",
    "OceanAksNpSchedulingTasksParameters",
    "OceanAksNpSchedulingTasksParametersOutputReference",
    "OceanAksNpSchedulingTasksParametersParametersClusterRoll",
    "OceanAksNpSchedulingTasksParametersParametersClusterRollOutputReference",
    "OceanAksNpSchedulingTasksParametersParametersUpgradeConfig",
    "OceanAksNpSchedulingTasksParametersParametersUpgradeConfigOutputReference",
    "OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters",
    "OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParametersOutputReference",
    "OceanAksNpTaints",
    "OceanAksNpTaintsList",
    "OceanAksNpTaintsOutputReference",
    "OceanAksNpUpdatePolicy",
    "OceanAksNpUpdatePolicyOutputReference",
    "OceanAksNpUpdatePolicyRollConfig",
    "OceanAksNpUpdatePolicyRollConfigOutputReference",
    "OceanAksNpVngTemplateScheduling",
    "OceanAksNpVngTemplateSchedulingOutputReference",
    "OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours",
    "OceanAksNpVngTemplateSchedulingVngTemplateShutdownHoursOutputReference",
]

publication.publish()

def _typecheckingstub__898ccbb93cd7b1a458d7f489d68c3366490a1abc47b94a9d60566b0529018fed(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    aks_cluster_name: builtins.str,
    aks_infrastructure_resource_group_name: builtins.str,
    aks_region: builtins.str,
    aks_resource_group_name: builtins.str,
    availability_zones: typing.Sequence[builtins.str],
    controller_cluster_id: builtins.str,
    name: builtins.str,
    autoscaler: typing.Optional[typing.Union[OceanAksNpAutoscaler, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filters: typing.Optional[typing.Union[OceanAksNpFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    health: typing.Optional[typing.Union[OceanAksNpHealth, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    kubernetes_version: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLinuxOsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    logging: typing.Optional[typing.Union[OceanAksNpLogging, typing.Dict[builtins.str, typing.Any]]] = None,
    max_count: typing.Optional[jsii.Number] = None,
    max_pods_per_node: typing.Optional[jsii.Number] = None,
    min_count: typing.Optional[jsii.Number] = None,
    os_disk_size_gb: typing.Optional[jsii.Number] = None,
    os_disk_type: typing.Optional[builtins.str] = None,
    os_sku: typing.Optional[builtins.str] = None,
    os_type: typing.Optional[builtins.str] = None,
    pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling: typing.Optional[typing.Union[OceanAksNpScheduling, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanAksNpUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    vng_template_scheduling: typing.Optional[typing.Union[OceanAksNpVngTemplateScheduling, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__093d761e9ff01af6c29b326f08730e5c36753a8fb0dd64b7126b262010496297(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__284c374fcc23f7877c2e31bfa73cdbeb548c9a186476cd657442a94547da0842(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpHeadrooms, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4846e4e0da5bd72cf696ff4fa4e0d78663ebc9ab07e6088be3f038108cf10b68(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLinuxOsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52fcc7c22e4bac75dfaf5872709d568cac573e3dd5764f65ad904b1247fd2db3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpTaints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62a5844e745d3dc3bc50168b6d11d932a24790b381febdd79aa3acdba95594ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea69ad8644dd89aa463fc85d07e524019a06a1cc120da1e5987046a167466f62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75ec4fefd2f1d7c22a01397d06dae7fd932b7d24c5aed9becabb675f4a845d80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6179ec6fb80c523d3bbccb2b6580f1f29112d47edae838bd46f35883dbc7999(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__277c847b46190413d77cdd0ec9934c355c98b40f731ac2beba195207710617de(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f37accc031cfce63d2dede6fb5e99addd1ffafe921af10c1d3bded64a9f38de0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44df0c8a8822bc1dcd738c59f5a3909445fb3aec5820edabc5722192d5a098ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d7b35b0a5c743235e1ae0ff043dc3e570e58168eb4e23805c4af0d49d26b1e0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d260296295b25370fc455d1d4c9a607901c5cf42dacfb779bcb1e0557886d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f205fc97059e2e675db7cd66935260bb789b418a7ef2c5000f834971da7bade1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3021f2aa21020ec377f6d47e7e39dca0e27337a2fb5afa335f86be5f073cb6(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47778ca946ad4ccfe14cfe5ae2a85cfc6c161788aed5f8697d1e4718505439ca(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88419e6c825defaa4ac92fe1c20480259588dc45277611521e2a183eae035a71(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a87ed622c0b11d0f2b346ba0ec6761aba7c644142354bfcc76466be4f28f1469(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b336cc34e01b20430edee7becd47c00b9fd1e4f8dce0b2d9d4f5944aee8b153(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5297b4865bb4041d494b256e9a6a1ca46517024b5172258ef6a2adce38ce5bc6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e34a9a6875fb6e0b20bd147f857ece0bffef93a279e097c559567a1dddef51d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__338e5f41b3606d67e98979a8864305bbbe7e85e06153bc623a1c7529c0c3fea9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a405be31d799aaa7a83bbb92dabe9622e3cfbc1cbfe473d34a12036422aa9abb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2700fe40b6d36c8434590c3f6ef6baa3aec9ef2047c6436cf82c24ee381dc66(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a17ecd73e9618bd166376ebe256e68840e49d45a403e6fcbabf779f0417e2a1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f840978c379636cb42b7cfb9b618103389df7c9747536fdc06b6cede3362a1c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614fd26df3d39f418b33abda3525bfa2b90a8d383a6a710b43bc7048e7e91ca4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acd5b84fed7b90a6e8df57726b3376ad4897744a5f1d3df74f1742a1eba4d2eb(
    *,
    autoscale_down: typing.Optional[typing.Union[OceanAksNpAutoscalerAutoscaleDown, typing.Dict[builtins.str, typing.Any]]] = None,
    autoscale_headroom: typing.Optional[typing.Union[OceanAksNpAutoscalerAutoscaleHeadroom, typing.Dict[builtins.str, typing.Any]]] = None,
    autoscale_is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    resource_limits: typing.Optional[typing.Union[OceanAksNpAutoscalerResourceLimits, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90025a750dab1d36f316beb5c4d4bc277fb2fece46d0c095beee1b058f490a97(
    *,
    max_scale_down_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e323dc3d55845c8138edb6fa0ed07b64348d49458e8d173ad68cf23277bd56f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e211cc7941a4f9d530dab9597943bd8cc3102383b1020c7ea5938be4144edea9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__694925ba377ee2297c478fa7de17a6028ae390c9b028bdb0ef21a8bbaf61cb13(
    value: typing.Optional[OceanAksNpAutoscalerAutoscaleDown],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f3500b9c60d85bcf43c8bfb06f8a67e246dfe5c2c75f4a0cf43faa35e91db9d(
    *,
    automatic: typing.Optional[typing.Union[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14a6682d5e28cfd7d5d2788a7f90a30240c46435e6bd6e853722b0c11de95fa6(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b7cb40a358c82222c6e38ba5aa9b9f55f00ba74337ecd6896e5d1a62874cc0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c1ab0ea7bfa62e8afc65122fab28247b4fee0be1089fce8c5c2f1ae5905554f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9164955a5ae0aada1ca6cee1a1ee85d69ad7c4686e4005350b5be4899038b9d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59fbba227f6bd247ed11b119bc5e54ce48f5b9c7aec7d0646366479d2f94fc2e(
    value: typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroomAutomatic],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0919e878c242a679f4ee67c299f7c4bb7af254bbad557c02a1273830852f338(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59c244f9824c5e7cb48ea4637399431e5bc70474602ca5922ee474962451c71e(
    value: typing.Optional[OceanAksNpAutoscalerAutoscaleHeadroom],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c7b3548c7c7a2d7cf9ed3738e3162adc17b8b3086567472ad6ad6854c948256(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da55f0718b621653af224776827ca6681da47a8b7520c55d829dfaf411c63382(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1648c48e96a0709637e03dddcca11e4292b34ea0ae7e40867a72cc2e85b66e8(
    value: typing.Optional[OceanAksNpAutoscaler],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a5a0c123b4007faf87d6c403994a74c1db5f68aedd37c6754116ad94e1164fd(
    *,
    max_memory_gib: typing.Optional[jsii.Number] = None,
    max_vcpu: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71cbffbd897e11688fd174fd8ed556b1888ea72e313351b955cab1461248eec7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e14ca6f83844bc92b5506d7a61488a3b988fb9b002111e37c86faf65b58dec24(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89b89ad8c1aa30471337199f6611e44ca026982358d6a0c5d6a9cb325ce4469b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bda71648bd77cd9febd4bf4fe53060c188279f266968f16f74a65d6b6e348bb(
    value: typing.Optional[OceanAksNpAutoscalerResourceLimits],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9bab4f3e98d3b0cba441a02e1e4220b0e83e9de8e80d93eb0348c9802bbac4b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aks_cluster_name: builtins.str,
    aks_infrastructure_resource_group_name: builtins.str,
    aks_region: builtins.str,
    aks_resource_group_name: builtins.str,
    availability_zones: typing.Sequence[builtins.str],
    controller_cluster_id: builtins.str,
    name: builtins.str,
    autoscaler: typing.Optional[typing.Union[OceanAksNpAutoscaler, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filters: typing.Optional[typing.Union[OceanAksNpFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    health: typing.Optional[typing.Union[OceanAksNpHealth, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    kubernetes_version: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLinuxOsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    logging: typing.Optional[typing.Union[OceanAksNpLogging, typing.Dict[builtins.str, typing.Any]]] = None,
    max_count: typing.Optional[jsii.Number] = None,
    max_pods_per_node: typing.Optional[jsii.Number] = None,
    min_count: typing.Optional[jsii.Number] = None,
    os_disk_size_gb: typing.Optional[jsii.Number] = None,
    os_disk_type: typing.Optional[builtins.str] = None,
    os_sku: typing.Optional[builtins.str] = None,
    os_type: typing.Optional[builtins.str] = None,
    pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling: typing.Optional[typing.Union[OceanAksNpScheduling, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanAksNpUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    vng_template_scheduling: typing.Optional[typing.Union[OceanAksNpVngTemplateScheduling, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a9f7ac92271595654997c1c567d2192601f5aa35699adec679624356c181ab(
    *,
    accelerated_networking: typing.Optional[builtins.str] = None,
    architectures: typing.Optional[typing.Sequence[builtins.str]] = None,
    disk_performance: typing.Optional[builtins.str] = None,
    exclude_series: typing.Optional[typing.Sequence[builtins.str]] = None,
    gpu_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_gpu: typing.Optional[jsii.Number] = None,
    max_memory_gib: typing.Optional[jsii.Number] = None,
    max_vcpu: typing.Optional[jsii.Number] = None,
    min_disk: typing.Optional[jsii.Number] = None,
    min_gpu: typing.Optional[jsii.Number] = None,
    min_memory_gib: typing.Optional[jsii.Number] = None,
    min_nics: typing.Optional[jsii.Number] = None,
    min_vcpu: typing.Optional[jsii.Number] = None,
    series: typing.Optional[typing.Sequence[builtins.str]] = None,
    vm_types: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3d5c6b23f914408dcab4cd492a9e2c57a0dfc473c15cc81e6fed9569e4a885(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee388709d1565b586d153fbcb4c4db73d07f73b6f592dc66c1ca93b98b4a945b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c742c1c4d9379baf6663ee29e90347b76841893ec7c21d5f0c078681e63b322(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afbe8d66bc8afc1a997487114b51da9db7e17086de47d2422d9cc82fdb5e0db5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71c859c25dae8d7f829f8a4c7a10d8f95ea10064ef8ec38c26a9b7ec99c89146(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__655de80b749e3f6169b1935080116c7aa6526ab5a70babb82390e62e656e0269(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c8dfb8486e6f9ff1443621b5969fe2227906e0cb20dade66f1c1c629c157e26(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb7e75e2b21793f5c4a71c261dcd0e2f3c8c247bb5e8055027755fd8929fec3c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c124113da710685d1046267a1bef2d22b3f6c4960033e838db3f969d0c94544(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a30a41b857f7dbb1a71c27ab48e06fbcfc2e41ae15b21dd49b1c43f0d465c23f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaef3d9405dfa602d7bcee79852b76c52146b52dcd15267515a8dd4036956b91(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7006276093120f973474fc0cd23738284fa202900d8a7f7cdff0cf99fc52cbb6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e318816c124c46f93960ffc0e6dbbdd0cf6ec9c95a1b86b02801018303241d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8f9842d5ec88efa702799bf7305f81cdd9657e6343aeefea4a229a40d027493(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2fa2a5a1c3686a833a5af9341349061e311b0645695207344c40eb87ab3e64e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5ea2b88093c0500834a83ea6aec4ae4257fdd8e591befc4898ab51c498a394e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f31bd0fc5a502010cec257c33953fdf09d6f9013fd19fca25907e25d7b91be82(
    value: typing.Optional[OceanAksNpFilters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71f8750b24926f1ba765bf3f4bae5f9a952c815a93d08ba5ab409373a843371b(
    *,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
    num_of_units: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5c950d5f3f70655493d9d9c052fe216c9f66fcc7e611665d994f76175adb2fe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddd81aaf8bb9776ce0913f2849cc0a6d8850205e7945e73eb68e7cd06190a2e3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__974e4e6b976d69c90b5f86b11bfe4d68b5d80dc9e4861f115816562c61596d8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8066f1a1deb87058e4059c1959e90872007b95885d9438a3f8ce29bd6f4915f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deaf9d4b8b9ae52192fc3601c0951f8914b64eb56931429524cd80ff38e28ef0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__930213753fd0fffc740533f09448e92002d97f00bf6f641ec3f39a8a3806a535(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpHeadrooms]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0ff8aa121081ccb41ad6c5fc8d3ea6631df992c898121214ebf3e687e08f17d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32475492fd397e67799604b757dd5b65aaac594140765ddbe0d8fb11ed5bcbe8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14959e319a974453ba22c4bc44072e335bd6d76e7eeb1dd1119a6378f4e4c1be(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e4aa00243509d7b4f1b0dd8329bd3517aae69bcdb204a1c47df019bff2c3b6f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__856e5ad14de0acec5e7d139d2a8b96fc92c5ae52d209d7c616ede8873891bf0c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0561065072d4a65c55dd2068d56986da11a509b67366f7fa28ac74525134cfd8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpHeadrooms]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0446171353b1dda6da14d9676f214aa866da2a98185290415005f5b979db2eb7(
    *,
    grace_period: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e7aedccee9ce43e6ed6a3722e435b998ea72bcfb5ec8f247f3156ec79e8f40a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__913de7f1851a455383aaeebdae3597173c9cceb7381a5d37852b0b1bad8f04a2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf340db4cbe5a708e17e8e299156919e448f4418f16a733c27fa1313b55df2b(
    value: typing.Optional[OceanAksNpHealth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a358dd81765eec4a41ebb3e471be2ed6cd62e3de8993d5238d73dad36aad760(
    *,
    sysctls: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLinuxOsConfigSysctls, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71cdf4cf1092a391f97e0280cd25e1d13b7869d6f8a8c8224a056f210e09f4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1413c6ad64a4c21e6092d7e9ba5127d531b16a573baaaf45e6d84f8d49844638(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d04c31d9dfb885200f59b89fe844c8f8b106b7e4311afbb8c8854fc4a365072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__470414e5b6863c315be4bc819613c07c40ce60837ff7142bd11e4e383238bb90(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d402c07831a50a444d10e2b94506b6292c7db201c4e4b9f7257fe7093d3fff1f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3245b8d6a9ce03af0a9d8e9292e4f70d8a2aae88baf98cc4e899072efe455ada(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebecd7f5cc58d81c09e0d7e774ff1b57bbb27d50d25afeabf0a0ba26d020436e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35b3678e294a3633279af6008402955600486c4dc84d92e285ddcbfafd7de17(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLinuxOsConfigSysctls, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__338e8b77d13194c4c96fa0148b8fcf84195461a9e9a004a234615736628ef1a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67fa521eadd72eb55f8528b9e5f499dd0ff1cc262737bc3631effdda982a4887(
    *,
    vm_max_map_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3485d32f831bdb745686adf7c107474295c3afc6ae6a8c76b4952ff5cf31e509(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a72c749154bcbf1587d258279b9c3a79969c0aef3c88730c611ab64d649bfd6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4d7475880a286a5e7a7edd624bb6e87d1d6035b57b2ee4c351cbb9997ea912b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9a4cbb24466dd580c6de7ec0b1f8874cb1b597ce8bd4749102c77b2d5fc0f76(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__070b46f9704be672372066dd2cb6ed78cfc8a0e7d56271ccb7e43c094863b3b2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b8872a75ee98d8c9493423cae0bca61a071a9fce85d1bbd8fe90408d7a76acc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLinuxOsConfigSysctls]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c756365b267967b6cd62e5edff2b40fcf158197790941975c02f0781f0196b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9236a5f31465d1e6b441d7d62d573ed93c353a33cfa81102e100871d2ac3ebd3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71a8a4d6699d0db75c6f3bb90e453c3105160e74f578204679f7a15d972aa7a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLinuxOsConfigSysctls]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d156fe377db05f6a4069fe398c022baecb6a092091d38cc9d7fbad7fecffed7b(
    *,
    export: typing.Optional[typing.Union[OceanAksNpLoggingExport, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe50d55636eef9a8157f73aa55fe0025419cd866f3c933bf3b98548b30dc485d(
    *,
    azure_blob: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLoggingExportAzureBlob, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ffe0f8d7d3df82c71566005ed9b28640311713ba639f24e05eef0389f1f7ab(
    *,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1584c6d366cc6e2d9237b1f5c95e0f136802b0a52886625fe59422e3c445173c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceeef09bd5db38e7e699ae577815c05064d4d673dbbe465008819178146336c4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69e41e087c383e06651520239ff1a7315457f38e7e1619324d8c9bc56e147164(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a5d2b8511c3a1d00b9d22b2bcafc6e0d66d785b8084ec18b444786b9a1ea4c8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa42aff99317bd3a52d4c6b465a7563d1835a83f4b3b018353a2dec4681e3aee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764e26dbc7195ecccb52780b06bf6c09f99f91c2aaf96ab011eb0ee1a5781344(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpLoggingExportAzureBlob]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a6f71acbb39539bdf061b08777732f3bad58108138c3e44b93be35db164991(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d37fb3c4a754fc9fc7d18a349e0797573a1e8a0b7802684d9076fbe128e87de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f056638d2f806f340e0868033c8c881e8ce9541a21dc3c3d66463a523f4039f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpLoggingExportAzureBlob]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd44bace80407d64396bdbf341065588a00c812265fded0b9587add1153fbc33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cef225aa19730c762d086c6a44377a8585836fb9ddfc1bbb8af16784e14ad9f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpLoggingExportAzureBlob, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d914e5e8055cc691585c41dd6fe4fb640d55ab9c3f0d3f8a208e705d0ce7c357(
    value: typing.Optional[OceanAksNpLoggingExport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f558b1e496238e72703628034a805aaeaba3e0d38903a2f1c22dafcb4c72e818(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e33b0379c397171ee9f059dd1dab9e92f3fdcadf93194209d82af7117c953feb(
    value: typing.Optional[OceanAksNpLogging],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d20ebe1bf5190dc49c807ca036b51189ee29c47672aba96614a263fd410910(
    *,
    shutdown_hours: typing.Optional[typing.Union[OceanAksNpSchedulingShutdownHours, typing.Dict[builtins.str, typing.Any]]] = None,
    suspension_hours: typing.Optional[typing.Union[OceanAksNpSchedulingSuspensionHours, typing.Dict[builtins.str, typing.Any]]] = None,
    tasks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpSchedulingTasks, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b23839593ae1052707b8b8b15a603e7cd9124c4d6717d97ec9d541fdaccdff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15b39c661ed05a9f01448888c1020c8dcff0527b75ace17602eaa7539e39020b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpSchedulingTasks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42efce885b277ff0467b937bbf380f852367148461159c02ec153066704117d8(
    value: typing.Optional[OceanAksNpScheduling],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45995a95327fe7c1d819054ab0a424f8ca422d0b9989cab007cac55904f55d20(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2da2f3033c6c0996a552559a0b6b2dc185633de63eb50d3ab1530eca4263504b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fbe117480707862ebd505639ed8d82ae9744065320b96e68870882b86dd58c9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1989117ce19416a2c34b64619e9eed1082a3c3788410b48d8909672540868a7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14e4b92d6508fea86858f2a4cfdc5363c175f45496e7ee7f02dd5a3e7789fae5(
    value: typing.Optional[OceanAksNpSchedulingShutdownHours],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8380ceb37f5c1f295eb1e4c1df09484626fcf2e1b197ce5400f72fe9540b2287(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2857f3c29220c3287de98027f3cd551187100955392a12731571da56d20bfebb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3155feca379d5ced73699ccbdeed9647d03fc10b207cd42b8d2e24d3dca976e0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__983c0c87fd65b980a7a8a6b279f9cf4159af9e837c7629d87cd07c95c951fb10(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__808cd7581c48cac60dcd32df5be9dcfaeeab457d7d3913f897d3c0c0c013b3ea(
    value: typing.Optional[OceanAksNpSchedulingSuspensionHours],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__886c35d1eacd76f0878e09490fdf346f9addc6b5ee55e7f8ce6d3b65d42229dd(
    *,
    cron_expression: builtins.str,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    task_type: builtins.str,
    parameters: typing.Optional[typing.Union[OceanAksNpSchedulingTasksParameters, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__266da5cd48d9037ea288f30bbaf7a33c8b14f8fd39e6c5548f29d3613e33b3ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__884022db33c843a24208e3591d9215ddf258d3654beeb5c43ce37752f0b43723(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8f18095ea3caa6aa94775753a2d9dc778861366c2db37da34ffe9a5722ed32d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bebc32bccd0cf313e99bd56e99cf8a1f1a02a8906f33d2d6a78a36175536ff7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549510f5ea6e09d9389bf738c164e3909d0644cad443ad377ffac34e23873b42(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44d2612e30d4687d37fc965bbb38c7074bdf572db91cba903c3d6cfbe40a3e4f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpSchedulingTasks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__086c327ba908f251bbab8037fcc964bdc8a6dc82809e7dc9eab09db679c819ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe59e77c4dc9fd872b0ef2b27195f32369af93fc1ce73d603646730342691567(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5af831d8ef619ccd6cd7d9aa6837574d36b954f95bee93bf36998a92804bf61c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43a35911121bb9ea593acd403200b6a198f8b77041060f97b986c1ece550f8e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58b0425b4e8d71b35c23af2e495805f4a7d79dae727cd2b78f5d13d6782eb217(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpSchedulingTasks]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b9907b2a24cf36967ce0a3cd8b764343deea6fa183c4af33ed85e100f179d77(
    *,
    parameters_cluster_roll: typing.Optional[typing.Union[OceanAksNpSchedulingTasksParametersParametersClusterRoll, typing.Dict[builtins.str, typing.Any]]] = None,
    parameters_upgrade_config: typing.Optional[typing.Union[OceanAksNpSchedulingTasksParametersParametersUpgradeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3bd50cf7dedc23b0358db62af28d28f0c6e2a704cf6e83db5def19647b1f47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2f5b4dfb05448d73dc215a7a0088210e8592c564e06547c8d80f67f945e016(
    value: typing.Optional[OceanAksNpSchedulingTasksParameters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b1cc3dc3ea7233c35f256f478486df048766679deef708b05cc8994702fa372(
    *,
    batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
    batch_size_percentage: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vng_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5822b57563e068270584d55720a376522aa52dd4d9f371d2dd8c90c7929e203(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__194e514c8a9feeb243dcbe3bd1f0f161a1388b6ea8a4e965ccd427413dad5402(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8aa290cff09d72812cb3adcabc0e359bdb5de5d46a618f0c8f0af3a6d32192d1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feb707807d52a3a8966fca6352434777ba4b658612ea4a92907dfe7d88a9cc61(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f8739c7a45a606b90b7db6fba5033019009106ad5085db0b061a8a60dd4a490(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e68fddb5ef37ea0dbc5989af6ed916daa456f824db5f7ac20cee55c69f80ebeb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d85f8e8a3c505180b0c054fcb1fa30a6e6404b3556af61a6f12019cba6817e9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f42b1e2a080f30c382c7b250d1d38492b4d59e0307d01ce52401d56e829a9e(
    value: typing.Optional[OceanAksNpSchedulingTasksParametersParametersClusterRoll],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__338acb605f6c57c0e4413ba5d541be9f8452fb2f2f71ef1c50f9fb64b21f3187(
    *,
    apply_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    roll_parameters: typing.Optional[typing.Union[OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters, typing.Dict[builtins.str, typing.Any]]] = None,
    scope_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9623928249b4f92b89972f63125bda546bb137dcb86879691869efc9def21ebf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1004ac03e35e15792cf8b03b3f55beeaf29bf24e4294083a177cc881aa98291d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c595d2089140bcd69eaea6f1905f15bfc98d40deb9f593e4ce3ef8b80918d0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25f01abe696ab85006a08a8d8865ed632eaa038f8a782400feab5f05a5122990(
    value: typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5747794851778866f65c44aa52e33f1178a84d544f67285cdf010c348b36580(
    *,
    batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
    batch_size_percentage: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acce90216efdd55f3d60003ef62ee8ba2611adaeba73e251f393b14e6c7b18ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__607dfee7ca94567e65d560ccc0c9daa6f8d4ebb8198a78b302923c2dea962f59(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eacbede4667fe02f5630c7ab512e29814cf7033d8ac07d0ab0852b945d75435e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d2411d6ca28c567a41703c9a60bfe69e91b1913b53d04e34d009c0f9649d1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d746ffe55bd35e005d44ecdce0de27e03167230c2ebe7f0aeaeb21546d21b1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__982be9ce1cf810dc0238926433d8ea1b64aa15a92826baacbad7383020395a40(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8505c638c7aa6aadaf863c102dbf1e456b9e1d6bd6b74cbfca2bf655d9e6ef28(
    value: typing.Optional[OceanAksNpSchedulingTasksParametersParametersUpgradeConfigRollParameters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6405863ddb06d92e42ec8b68ae430bf71f9a78bd1de8330ebbcddc3ca14513e0(
    *,
    effect: builtins.str,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bccda8cff8cd35b59025ec8505ae5fef9bfa67836a9cd38cf0f2f53a737987d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b95f7d63d51367ba18f9f7d56ba2e32e41750219476e19d2ed683779fc4256a1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c75766fdebefc353d55778a076ee6e4f138f125e5f72271728bf2434a85cad83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__632b24880a1a359914183f1c3a99b8b8707d6466d37f1084522e41e32743e5e0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd76d67d3386fe6c4659ed18f908692fc1a8437689f5a219ff90eb46ecc201d7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c763e184885cbbe077123246e2b44527a3a7ea4fe0301a3cdfa6785f665af98(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpTaints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34ba3872921f82627c72bff53a3eece25ceeb53d9cb5bf35255f53df547da01b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cdae04ccbf75d107ac77c7b8c396f84d8867842e85ac8217f6093f7bdcbdbbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aadbec3dcbf826a8c26fa439ed539ef2f4cfe6b707a11d13a6c34bd18530b53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__269fb8f3eac05193692e73d537ce2f5cab783d3e2acf3abfbe8214f97e39f5ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3c1159b06026c1f8e7afbe40fa9df934025ce9377970e157eaa9cf002e9c6fc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpTaints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce9c2f16a9795bd9fd5dcb470fee2b36b5a6d0b0035268caec8193aafab17b6d(
    *,
    should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    roll_config: typing.Optional[typing.Union[OceanAksNpUpdatePolicyRollConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac5346277bffb8fd551d046e372650d461b56703fec4419aa2d69b940d17e81d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__565e11b54a9c42ab141ca566a3d6533e91743b49796ab9e8a0130896cbea6a7c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b933b43c4fc81b7263c3640fe4eb0855f7140768991752d595ec5758658a318(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d506ffc0d400681884bf816d782980b1e8851db04b4c493f776a7ab4ddbe4570(
    value: typing.Optional[OceanAksNpUpdatePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b182af76c226516b07c3d827174a66e96d48b5cf3001ff6512aca0cf705376ad(
    *,
    batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
    batch_size_percentage: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    node_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    node_pool_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    respect_restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vng_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5234d2d6be4a415bd953ddcec6775059b8b271f5c5aff3d161036ffd830591bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95c2891a25a56543111c5a7b6acfe44b34d649d3eab9442bc686dfd5452c1cbc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab39726d56d78433e30267b04aa11e1d96f6434975bb252565323aadb12caef0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb6c329913c7ed6226ace411aad44adcf1c7186c87cd1bb38822d8cf8e314012(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7c06be99cd0fc42e9b8774671a3397987284dc1b3c41fdd4dc36b97b7583a2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3af7f51e6d9fee999b871585a48241a26aab37a85c1991a7934cd4b0960d5c40(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b4ddaf9dbc5ee043ac111a8ffbccb641c346a299e76d5567e894cfdd081dcb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6066be617e9b4ddfecea5670744b4a4be431096a6e1fc0570f45f2947daf9c4b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ada835d08af167db3c696cd40121ebdf97e4cf0d087a155787dd42e84dc7da6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f14360bcf6cc0bb9b7d4d0f4bcf43ee982ae93bf07011f577ca25a902197ece9(
    value: typing.Optional[OceanAksNpUpdatePolicyRollConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c43878e3b329bf24eda94ac3cd08e688a3e48b1a7b739c8e6ab2c6b536e0d2d(
    *,
    vng_template_shutdown_hours: typing.Optional[typing.Union[OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f615ec33beaf45ab70f2179c693011fc31895ed18574beef492a776d0d270d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06bc9853e084f47f96c5c7e3f735b21cb8f60e9164a29793f68191a1151a69a3(
    value: typing.Optional[OceanAksNpVngTemplateScheduling],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a1af472e7648d6e50b46ea53b67e88ff375a7dcaccab4453f369430d219d590(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f429090177823c14c1770e8fd7cd861782af42785961232549852abdbe8724d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0d24c0c94de18b6a222be575cd83d2f520bb2ef5eb771f4689d853a98dd0b44(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77140cb241f6109405c24346503f1a6d31b24803b5e9185d255b9c715d8297f7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c559a6eba1df4d4af0a4f5f872f45f4de3f40f6cfa3161410a8fdfda87ecd12d(
    value: typing.Optional[OceanAksNpVngTemplateSchedulingVngTemplateShutdownHours],
) -> None:
    """Type checking stubs"""
    pass
