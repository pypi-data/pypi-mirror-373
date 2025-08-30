r'''
# `spotinst_ocean_aks_np_virtual_node_group`

Refer to the Terraform Registry for docs: [`spotinst_ocean_aks_np_virtual_node_group`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group).
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


class OceanAksNpVirtualNodeGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group spotinst_ocean_aks_np_virtual_node_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        ocean_id: builtins.str,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filters: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupHeadrooms", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        kubernetes_version: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupLinuxOsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_count: typing.Optional[jsii.Number] = None,
        max_pods_per_node: typing.Optional[jsii.Number] = None,
        min_count: typing.Optional[jsii.Number] = None,
        os_disk_size_gb: typing.Optional[jsii.Number] = None,
        os_disk_type: typing.Optional[builtins.str] = None,
        os_sku: typing.Optional[builtins.str] = None,
        os_type: typing.Optional[builtins.str] = None,
        pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupScheduling", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group spotinst_ocean_aks_np_virtual_node_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#name OceanAksNpVirtualNodeGroup#name}.
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#ocean_id OceanAksNpVirtualNodeGroup#ocean_id}.
        :param availability_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#availability_zones OceanAksNpVirtualNodeGroup#availability_zones}.
        :param enable_node_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#enable_node_public_ip OceanAksNpVirtualNodeGroup#enable_node_public_ip}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#fallback_to_ondemand OceanAksNpVirtualNodeGroup#fallback_to_ondemand}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#filters OceanAksNpVirtualNodeGroup#filters}
        :param headrooms: headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#headrooms OceanAksNpVirtualNodeGroup#headrooms}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#id OceanAksNpVirtualNodeGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kubernetes_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#kubernetes_version OceanAksNpVirtualNodeGroup#kubernetes_version}.
        :param labels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#labels OceanAksNpVirtualNodeGroup#labels}.
        :param linux_os_config: linux_os_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#linux_os_config OceanAksNpVirtualNodeGroup#linux_os_config}
        :param max_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_count OceanAksNpVirtualNodeGroup#max_count}.
        :param max_pods_per_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_pods_per_node OceanAksNpVirtualNodeGroup#max_pods_per_node}.
        :param min_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_count OceanAksNpVirtualNodeGroup#min_count}.
        :param os_disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_disk_size_gb OceanAksNpVirtualNodeGroup#os_disk_size_gb}.
        :param os_disk_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_disk_type OceanAksNpVirtualNodeGroup#os_disk_type}.
        :param os_sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_sku OceanAksNpVirtualNodeGroup#os_sku}.
        :param os_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_type OceanAksNpVirtualNodeGroup#os_type}.
        :param pod_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#pod_subnet_ids OceanAksNpVirtualNodeGroup#pod_subnet_ids}.
        :param scheduling: scheduling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#scheduling OceanAksNpVirtualNodeGroup#scheduling}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#spot_percentage OceanAksNpVirtualNodeGroup#spot_percentage}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#tags OceanAksNpVirtualNodeGroup#tags}.
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#taints OceanAksNpVirtualNodeGroup#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#update_policy OceanAksNpVirtualNodeGroup#update_policy}
        :param vnet_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vnet_subnet_ids OceanAksNpVirtualNodeGroup#vnet_subnet_ids}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb94c83fd03c70412f5e6aaaaf00ee680b7dab6c645ad6fb5e95a986abb0cf51)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanAksNpVirtualNodeGroupConfig(
            name=name,
            ocean_id=ocean_id,
            availability_zones=availability_zones,
            enable_node_public_ip=enable_node_public_ip,
            fallback_to_ondemand=fallback_to_ondemand,
            filters=filters,
            headrooms=headrooms,
            id=id,
            kubernetes_version=kubernetes_version,
            labels=labels,
            linux_os_config=linux_os_config,
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
        '''Generates CDKTF code for importing a OceanAksNpVirtualNodeGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanAksNpVirtualNodeGroup to import.
        :param import_from_id: The id of the existing OceanAksNpVirtualNodeGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanAksNpVirtualNodeGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d2c1249fb3a9f27cc7fbe4ef0f46b529b30ca5a2aadc068a53e76fc2875e6c5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

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
        :param accelerated_networking: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#accelerated_networking OceanAksNpVirtualNodeGroup#accelerated_networking}.
        :param architectures: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#architectures OceanAksNpVirtualNodeGroup#architectures}.
        :param disk_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#disk_performance OceanAksNpVirtualNodeGroup#disk_performance}.
        :param exclude_series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#exclude_series OceanAksNpVirtualNodeGroup#exclude_series}.
        :param gpu_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#gpu_types OceanAksNpVirtualNodeGroup#gpu_types}.
        :param max_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_gpu OceanAksNpVirtualNodeGroup#max_gpu}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_memory_gib OceanAksNpVirtualNodeGroup#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_vcpu OceanAksNpVirtualNodeGroup#max_vcpu}.
        :param min_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_disk OceanAksNpVirtualNodeGroup#min_disk}.
        :param min_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_gpu OceanAksNpVirtualNodeGroup#min_gpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_memory_gib OceanAksNpVirtualNodeGroup#min_memory_gib}.
        :param min_nics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_nics OceanAksNpVirtualNodeGroup#min_nics}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_vcpu OceanAksNpVirtualNodeGroup#min_vcpu}.
        :param series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#series OceanAksNpVirtualNodeGroup#series}.
        :param vm_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vm_types OceanAksNpVirtualNodeGroup#vm_types}.
        '''
        value = OceanAksNpVirtualNodeGroupFilters(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupHeadrooms", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57064b045997e5dd79e1a8e41b8e46cb9806fdbe4892c684e557171f85fef316)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putHeadrooms", [value]))

    @jsii.member(jsii_name="putLinuxOsConfig")
    def put_linux_os_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupLinuxOsConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5ca0d8b1182e3808eb12013852cc85f02c5a5a81b8d8dee171b0ad42a92df28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLinuxOsConfig", [value]))

    @jsii.member(jsii_name="putScheduling")
    def put_scheduling(
        self,
        *,
        shutdown_hours: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupSchedulingShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param shutdown_hours: shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#shutdown_hours OceanAksNpVirtualNodeGroup#shutdown_hours}
        '''
        value = OceanAksNpVirtualNodeGroupScheduling(shutdown_hours=shutdown_hours)

        return typing.cast(None, jsii.invoke(self, "putScheduling", [value]))

    @jsii.member(jsii_name="putTaints")
    def put_taints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupTaints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90474312d786e0cd0310b61ab5a441a4211a73046096a109fc3cb0ee70f6c4e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaints", [value]))

    @jsii.member(jsii_name="putUpdatePolicy")
    def put_update_policy(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_config: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#should_roll OceanAksNpVirtualNodeGroup#should_roll}.
        :param conditioned_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#conditioned_roll OceanAksNpVirtualNodeGroup#conditioned_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#roll_config OceanAksNpVirtualNodeGroup#roll_config}
        '''
        value = OceanAksNpVirtualNodeGroupUpdatePolicy(
            should_roll=should_roll,
            conditioned_roll=conditioned_roll,
            roll_config=roll_config,
        )

        return typing.cast(None, jsii.invoke(self, "putUpdatePolicy", [value]))

    @jsii.member(jsii_name="resetAvailabilityZones")
    def reset_availability_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZones", []))

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
    @jsii.member(jsii_name="filters")
    def filters(self) -> "OceanAksNpVirtualNodeGroupFiltersOutputReference":
        return typing.cast("OceanAksNpVirtualNodeGroupFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="headrooms")
    def headrooms(self) -> "OceanAksNpVirtualNodeGroupHeadroomsList":
        return typing.cast("OceanAksNpVirtualNodeGroupHeadroomsList", jsii.get(self, "headrooms"))

    @builtins.property
    @jsii.member(jsii_name="linuxOsConfig")
    def linux_os_config(self) -> "OceanAksNpVirtualNodeGroupLinuxOsConfigList":
        return typing.cast("OceanAksNpVirtualNodeGroupLinuxOsConfigList", jsii.get(self, "linuxOsConfig"))

    @builtins.property
    @jsii.member(jsii_name="scheduling")
    def scheduling(self) -> "OceanAksNpVirtualNodeGroupSchedulingOutputReference":
        return typing.cast("OceanAksNpVirtualNodeGroupSchedulingOutputReference", jsii.get(self, "scheduling"))

    @builtins.property
    @jsii.member(jsii_name="taints")
    def taints(self) -> "OceanAksNpVirtualNodeGroupTaintsList":
        return typing.cast("OceanAksNpVirtualNodeGroupTaintsList", jsii.get(self, "taints"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> "OceanAksNpVirtualNodeGroupUpdatePolicyOutputReference":
        return typing.cast("OceanAksNpVirtualNodeGroupUpdatePolicyOutputReference", jsii.get(self, "updatePolicy"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZonesInput")
    def availability_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZonesInput"))

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
    def filters_input(self) -> typing.Optional["OceanAksNpVirtualNodeGroupFilters"]:
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupFilters"], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="headroomsInput")
    def headrooms_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupHeadrooms"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupHeadrooms"]]], jsii.get(self, "headroomsInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfig"]]], jsii.get(self, "linuxOsConfigInput"))

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
    @jsii.member(jsii_name="oceanIdInput")
    def ocean_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oceanIdInput"))

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
    def scheduling_input(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupScheduling"]:
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupScheduling"], jsii.get(self, "schedulingInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupTaints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupTaints"]]], jsii.get(self, "taintsInput"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicyInput")
    def update_policy_input(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicy"]:
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicy"], jsii.get(self, "updatePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="vnetSubnetIdsInput")
    def vnet_subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vnetSubnetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f136c0dc27a72e97b5786bd06ce621a428515c58a110c0c603153e9379e139d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZones", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__d77f8a8fa45226a27a38bf793b62e21e76f36db3fabe8273fdc0354c2702328f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__74109d527dee39fcd0d11ebfce8996348d02bf207ea2b4e261a2ee8cf184d8a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackToOndemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a39b9046b9b72e917acaef1ac2a96e42bf6ea39d787e444e27dfa136ba6d74a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kubernetesVersion")
    def kubernetes_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kubernetesVersion"))

    @kubernetes_version.setter
    def kubernetes_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4ec301d5282a0e91f5c1ed1256717db251e5ff85af223789fab6d55995860cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kubernetesVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a76be99151d0ef9031a88b4730b1e52b3e2fbf5174860e7105d8cf8de1107c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCount")
    def max_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCount"))

    @max_count.setter
    def max_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35d52a9fbdff3807be7f1a3637c1be2756d32a01920c8e98b3ab022da0e9e75c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPodsPerNode")
    def max_pods_per_node(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPodsPerNode"))

    @max_pods_per_node.setter
    def max_pods_per_node(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14f126f3cda35b71a4c545ffc79a48d49708ae4044d8c39fc3ad990287f0340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPodsPerNode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCount")
    def min_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minCount"))

    @min_count.setter
    def min_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb232bed1517a3393724bc2469e81f94b9de793020eaf5f896be2dc48a3a24e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1091ea4eb21760e24b9fa5c968cd0a9e79c375faae6dc50731d4bced48065ab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oceanId")
    def ocean_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oceanId"))

    @ocean_id.setter
    def ocean_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e38684343dcd939535a299d6fcee9def285fb80d10ec2b78c92ae1793ca72044)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oceanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDiskSizeGb")
    def os_disk_size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "osDiskSizeGb"))

    @os_disk_size_gb.setter
    def os_disk_size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3683469b615aaf08edb69c6b62290d2022f62dd58e727bc5e43a73d130787053)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDiskSizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDiskType")
    def os_disk_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osDiskType"))

    @os_disk_type.setter
    def os_disk_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d88664ff47d6517ecbfd1d5c18e24e20f34e6a79a64b73bb8a5b84e62859c23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDiskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osSku")
    def os_sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osSku"))

    @os_sku.setter
    def os_sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__455c8a543cde2e6a5c98f3d354c72131e4215a1d22ac5d8d116a50a136a65867)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osSku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osType")
    def os_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osType"))

    @os_type.setter
    def os_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81eacb2a91cb58148e757d487bf79c7edb38ec6c1b5ddb845ebf67757ac3539d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="podSubnetIds")
    def pod_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "podSubnetIds"))

    @pod_subnet_ids.setter
    def pod_subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac2dcb43daefa492f4c8abe3b2e3b2fc2a028dfd3b3a7c0a25c631d27f90c60f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "podSubnetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotPercentage")
    def spot_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotPercentage"))

    @spot_percentage.setter
    def spot_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61be4df3ed48cb5106eb6791dd3d6c679178d9250e091c96e9f303bc6c979eb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c5da87b1a3fb604677b8e953d3d352e2d34dca26a77ef428cafceffec3ca880)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vnetSubnetIds")
    def vnet_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vnetSubnetIds"))

    @vnet_subnet_ids.setter
    def vnet_subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072f6446c57d78d0938f45feb3366528218d83bdf3d1bbc4521f39911f8c45a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vnetSubnetIds", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "ocean_id": "oceanId",
        "availability_zones": "availabilityZones",
        "enable_node_public_ip": "enableNodePublicIp",
        "fallback_to_ondemand": "fallbackToOndemand",
        "filters": "filters",
        "headrooms": "headrooms",
        "id": "id",
        "kubernetes_version": "kubernetesVersion",
        "labels": "labels",
        "linux_os_config": "linuxOsConfig",
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
    },
)
class OceanAksNpVirtualNodeGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        ocean_id: builtins.str,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        filters: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupHeadrooms", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        kubernetes_version: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupLinuxOsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_count: typing.Optional[jsii.Number] = None,
        max_pods_per_node: typing.Optional[jsii.Number] = None,
        min_count: typing.Optional[jsii.Number] = None,
        os_disk_size_gb: typing.Optional[jsii.Number] = None,
        os_disk_type: typing.Optional[builtins.str] = None,
        os_sku: typing.Optional[builtins.str] = None,
        os_type: typing.Optional[builtins.str] = None,
        pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        scheduling: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupScheduling", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#name OceanAksNpVirtualNodeGroup#name}.
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#ocean_id OceanAksNpVirtualNodeGroup#ocean_id}.
        :param availability_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#availability_zones OceanAksNpVirtualNodeGroup#availability_zones}.
        :param enable_node_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#enable_node_public_ip OceanAksNpVirtualNodeGroup#enable_node_public_ip}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#fallback_to_ondemand OceanAksNpVirtualNodeGroup#fallback_to_ondemand}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#filters OceanAksNpVirtualNodeGroup#filters}
        :param headrooms: headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#headrooms OceanAksNpVirtualNodeGroup#headrooms}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#id OceanAksNpVirtualNodeGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kubernetes_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#kubernetes_version OceanAksNpVirtualNodeGroup#kubernetes_version}.
        :param labels: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#labels OceanAksNpVirtualNodeGroup#labels}.
        :param linux_os_config: linux_os_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#linux_os_config OceanAksNpVirtualNodeGroup#linux_os_config}
        :param max_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_count OceanAksNpVirtualNodeGroup#max_count}.
        :param max_pods_per_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_pods_per_node OceanAksNpVirtualNodeGroup#max_pods_per_node}.
        :param min_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_count OceanAksNpVirtualNodeGroup#min_count}.
        :param os_disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_disk_size_gb OceanAksNpVirtualNodeGroup#os_disk_size_gb}.
        :param os_disk_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_disk_type OceanAksNpVirtualNodeGroup#os_disk_type}.
        :param os_sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_sku OceanAksNpVirtualNodeGroup#os_sku}.
        :param os_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_type OceanAksNpVirtualNodeGroup#os_type}.
        :param pod_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#pod_subnet_ids OceanAksNpVirtualNodeGroup#pod_subnet_ids}.
        :param scheduling: scheduling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#scheduling OceanAksNpVirtualNodeGroup#scheduling}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#spot_percentage OceanAksNpVirtualNodeGroup#spot_percentage}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#tags OceanAksNpVirtualNodeGroup#tags}.
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#taints OceanAksNpVirtualNodeGroup#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#update_policy OceanAksNpVirtualNodeGroup#update_policy}
        :param vnet_subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vnet_subnet_ids OceanAksNpVirtualNodeGroup#vnet_subnet_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filters, dict):
            filters = OceanAksNpVirtualNodeGroupFilters(**filters)
        if isinstance(scheduling, dict):
            scheduling = OceanAksNpVirtualNodeGroupScheduling(**scheduling)
        if isinstance(update_policy, dict):
            update_policy = OceanAksNpVirtualNodeGroupUpdatePolicy(**update_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36b827f1f790c792f27aa490328a52655e9b7bc5bf63c279f78a15fb71548ed5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ocean_id", value=ocean_id, expected_type=type_hints["ocean_id"])
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument enable_node_public_ip", value=enable_node_public_ip, expected_type=type_hints["enable_node_public_ip"])
            check_type(argname="argument fallback_to_ondemand", value=fallback_to_ondemand, expected_type=type_hints["fallback_to_ondemand"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument headrooms", value=headrooms, expected_type=type_hints["headrooms"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument kubernetes_version", value=kubernetes_version, expected_type=type_hints["kubernetes_version"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument linux_os_config", value=linux_os_config, expected_type=type_hints["linux_os_config"])
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
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "ocean_id": ocean_id,
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
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if enable_node_public_ip is not None:
            self._values["enable_node_public_ip"] = enable_node_public_ip
        if fallback_to_ondemand is not None:
            self._values["fallback_to_ondemand"] = fallback_to_ondemand
        if filters is not None:
            self._values["filters"] = filters
        if headrooms is not None:
            self._values["headrooms"] = headrooms
        if id is not None:
            self._values["id"] = id
        if kubernetes_version is not None:
            self._values["kubernetes_version"] = kubernetes_version
        if labels is not None:
            self._values["labels"] = labels
        if linux_os_config is not None:
            self._values["linux_os_config"] = linux_os_config
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#name OceanAksNpVirtualNodeGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ocean_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#ocean_id OceanAksNpVirtualNodeGroup#ocean_id}.'''
        result = self._values.get("ocean_id")
        assert result is not None, "Required property 'ocean_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#availability_zones OceanAksNpVirtualNodeGroup#availability_zones}.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enable_node_public_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#enable_node_public_ip OceanAksNpVirtualNodeGroup#enable_node_public_ip}.'''
        result = self._values.get("enable_node_public_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fallback_to_ondemand(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#fallback_to_ondemand OceanAksNpVirtualNodeGroup#fallback_to_ondemand}.'''
        result = self._values.get("fallback_to_ondemand")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def filters(self) -> typing.Optional["OceanAksNpVirtualNodeGroupFilters"]:
        '''filters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#filters OceanAksNpVirtualNodeGroup#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupFilters"], result)

    @builtins.property
    def headrooms(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupHeadrooms"]]]:
        '''headrooms block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#headrooms OceanAksNpVirtualNodeGroup#headrooms}
        '''
        result = self._values.get("headrooms")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupHeadrooms"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#id OceanAksNpVirtualNodeGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kubernetes_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#kubernetes_version OceanAksNpVirtualNodeGroup#kubernetes_version}.'''
        result = self._values.get("kubernetes_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#labels OceanAksNpVirtualNodeGroup#labels}.'''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def linux_os_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfig"]]]:
        '''linux_os_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#linux_os_config OceanAksNpVirtualNodeGroup#linux_os_config}
        '''
        result = self._values.get("linux_os_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfig"]]], result)

    @builtins.property
    def max_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_count OceanAksNpVirtualNodeGroup#max_count}.'''
        result = self._values.get("max_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pods_per_node(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_pods_per_node OceanAksNpVirtualNodeGroup#max_pods_per_node}.'''
        result = self._values.get("max_pods_per_node")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_count OceanAksNpVirtualNodeGroup#min_count}.'''
        result = self._values.get("min_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def os_disk_size_gb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_disk_size_gb OceanAksNpVirtualNodeGroup#os_disk_size_gb}.'''
        result = self._values.get("os_disk_size_gb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def os_disk_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_disk_type OceanAksNpVirtualNodeGroup#os_disk_type}.'''
        result = self._values.get("os_disk_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_sku(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_sku OceanAksNpVirtualNodeGroup#os_sku}.'''
        result = self._values.get("os_sku")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#os_type OceanAksNpVirtualNodeGroup#os_type}.'''
        result = self._values.get("os_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pod_subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#pod_subnet_ids OceanAksNpVirtualNodeGroup#pod_subnet_ids}.'''
        result = self._values.get("pod_subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def scheduling(self) -> typing.Optional["OceanAksNpVirtualNodeGroupScheduling"]:
        '''scheduling block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#scheduling OceanAksNpVirtualNodeGroup#scheduling}
        '''
        result = self._values.get("scheduling")
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupScheduling"], result)

    @builtins.property
    def spot_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#spot_percentage OceanAksNpVirtualNodeGroup#spot_percentage}.'''
        result = self._values.get("spot_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#tags OceanAksNpVirtualNodeGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def taints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupTaints"]]]:
        '''taints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#taints OceanAksNpVirtualNodeGroup#taints}
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupTaints"]]], result)

    @builtins.property
    def update_policy(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicy"]:
        '''update_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#update_policy OceanAksNpVirtualNodeGroup#update_policy}
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicy"], result)

    @builtins.property
    def vnet_subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vnet_subnet_ids OceanAksNpVirtualNodeGroup#vnet_subnet_ids}.'''
        result = self._values.get("vnet_subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupFilters",
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
class OceanAksNpVirtualNodeGroupFilters:
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
        :param accelerated_networking: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#accelerated_networking OceanAksNpVirtualNodeGroup#accelerated_networking}.
        :param architectures: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#architectures OceanAksNpVirtualNodeGroup#architectures}.
        :param disk_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#disk_performance OceanAksNpVirtualNodeGroup#disk_performance}.
        :param exclude_series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#exclude_series OceanAksNpVirtualNodeGroup#exclude_series}.
        :param gpu_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#gpu_types OceanAksNpVirtualNodeGroup#gpu_types}.
        :param max_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_gpu OceanAksNpVirtualNodeGroup#max_gpu}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_memory_gib OceanAksNpVirtualNodeGroup#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_vcpu OceanAksNpVirtualNodeGroup#max_vcpu}.
        :param min_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_disk OceanAksNpVirtualNodeGroup#min_disk}.
        :param min_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_gpu OceanAksNpVirtualNodeGroup#min_gpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_memory_gib OceanAksNpVirtualNodeGroup#min_memory_gib}.
        :param min_nics: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_nics OceanAksNpVirtualNodeGroup#min_nics}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_vcpu OceanAksNpVirtualNodeGroup#min_vcpu}.
        :param series: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#series OceanAksNpVirtualNodeGroup#series}.
        :param vm_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vm_types OceanAksNpVirtualNodeGroup#vm_types}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f63cb28b7caa6fc1f499540bb48e4b4d0a8c8f076fda66820783f79135b679f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#accelerated_networking OceanAksNpVirtualNodeGroup#accelerated_networking}.'''
        result = self._values.get("accelerated_networking")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def architectures(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#architectures OceanAksNpVirtualNodeGroup#architectures}.'''
        result = self._values.get("architectures")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disk_performance(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#disk_performance OceanAksNpVirtualNodeGroup#disk_performance}.'''
        result = self._values.get("disk_performance")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_series(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#exclude_series OceanAksNpVirtualNodeGroup#exclude_series}.'''
        result = self._values.get("exclude_series")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gpu_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#gpu_types OceanAksNpVirtualNodeGroup#gpu_types}.'''
        result = self._values.get("gpu_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_gpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_gpu OceanAksNpVirtualNodeGroup#max_gpu}.'''
        result = self._values.get("max_gpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_memory_gib OceanAksNpVirtualNodeGroup#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#max_vcpu OceanAksNpVirtualNodeGroup#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_disk(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_disk OceanAksNpVirtualNodeGroup#min_disk}.'''
        result = self._values.get("min_disk")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_gpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_gpu OceanAksNpVirtualNodeGroup#min_gpu}.'''
        result = self._values.get("min_gpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_memory_gib OceanAksNpVirtualNodeGroup#min_memory_gib}.'''
        result = self._values.get("min_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_nics(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_nics OceanAksNpVirtualNodeGroup#min_nics}.'''
        result = self._values.get("min_nics")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#min_vcpu OceanAksNpVirtualNodeGroup#min_vcpu}.'''
        result = self._values.get("min_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def series(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#series OceanAksNpVirtualNodeGroup#series}.'''
        result = self._values.get("series")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vm_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vm_types OceanAksNpVirtualNodeGroup#vm_types}.'''
        result = self._values.get("vm_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__82d1c7ca3ed253bcaaca86ed66a7734acfa7a23f4e36ed3c9b20f109c9e18aa5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a4791bc21b1dbad6d56305146c8030a96ee6c16969e0ada3083ade5190a1543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acceleratedNetworking", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="architectures")
    def architectures(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "architectures"))

    @architectures.setter
    def architectures(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af6a5290e8b4cf11a5f6117cddf8047c1c6ac6687fd54e96877ca54f8e98124f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "architectures", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskPerformance")
    def disk_performance(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskPerformance"))

    @disk_performance.setter
    def disk_performance(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__504e7eadeb6ab7d093be6964810e50bbb54bc3ad1283c61d6bbe21683c93f87c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskPerformance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeSeries")
    def exclude_series(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeSeries"))

    @exclude_series.setter
    def exclude_series(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6b465ee5ac1a1303507dad9131703445d0e8c9cbe31e49ab75259427e7276d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeSeries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuTypes")
    def gpu_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gpuTypes"))

    @gpu_types.setter
    def gpu_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b02d6c3f0eadef70e597f017164aa2d262af3810591d95d7c21c4eefb075cc3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxGpu")
    def max_gpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxGpu"))

    @max_gpu.setter
    def max_gpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5190f8b0d383ac5226ce273508e4ac39d73ee9ace402b7690a6eb0a99c86a338)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxGpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGib")
    def max_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemoryGib"))

    @max_memory_gib.setter
    def max_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17fcf7f30dec694aa3f83451a37cf39d2c8a7103f6f3dee9d8489920054810fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b599c6e065fc2ca0416b5d6aba4292a3bd0b9aa568292edb2808c721bf66ed0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minDisk")
    def min_disk(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minDisk"))

    @min_disk.setter
    def min_disk(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a943188d69826c9b7a551f7bc88305a9d38ed4b8573f3ca817469a328888952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minGpu")
    def min_gpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minGpu"))

    @min_gpu.setter
    def min_gpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e746f20be811de710a3d5e8429b14030bb52e8fef8cd9dd4adcc0bf906aa51b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minGpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemoryGib")
    def min_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemoryGib"))

    @min_memory_gib.setter
    def min_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eb08b60a4bcc94c891eec04fe10290257a443b7b862ceac14114b0ef76ba871)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minNics")
    def min_nics(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNics"))

    @min_nics.setter
    def min_nics(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01963254a678d679a324ca8cc37b420831e35ef3e7f3d5e8b848f5569b550587)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minNics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVcpu")
    def min_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpu"))

    @min_vcpu.setter
    def min_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26fcb9bc7ae6cc117ce4f68284ab33e6ef204c3a0bacd83e7a93f06e0c55406c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="series")
    def series(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "series"))

    @series.setter
    def series(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__582ffd85cecc9232445c5fcbd95cd7dc437203d0a8e66c80c464362f9414fe3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "series", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmTypes")
    def vm_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vmTypes"))

    @vm_types.setter
    def vm_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__372a81ba3244b4022b3b7135b91ce7f86ad0ee7a2bbe5daddc336fbb41adb1f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpVirtualNodeGroupFilters]:
        return typing.cast(typing.Optional[OceanAksNpVirtualNodeGroupFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVirtualNodeGroupFilters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2422a17a7bb5a7251372c36990eaf93478659caf05b064a869f50266f62e25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupHeadrooms",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
        "num_of_units": "numOfUnits",
    },
)
class OceanAksNpVirtualNodeGroupHeadrooms:
    def __init__(
        self,
        *,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
        num_of_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#cpu_per_unit OceanAksNpVirtualNodeGroup#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#gpu_per_unit OceanAksNpVirtualNodeGroup#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#memory_per_unit OceanAksNpVirtualNodeGroup#memory_per_unit}.
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#num_of_units OceanAksNpVirtualNodeGroup#num_of_units}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568e17c9e36be61c3d869c1c4db12b35782695418dd87c8f2dcf3959f9166982)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#cpu_per_unit OceanAksNpVirtualNodeGroup#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#gpu_per_unit OceanAksNpVirtualNodeGroup#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#memory_per_unit OceanAksNpVirtualNodeGroup#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_of_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#num_of_units OceanAksNpVirtualNodeGroup#num_of_units}.'''
        result = self._values.get("num_of_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupHeadrooms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupHeadroomsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupHeadroomsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fbc2b99b87a13a47fafcf8cbcee92962c126cb8b0b206eac41df5f7fc312b10a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAksNpVirtualNodeGroupHeadroomsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__803708bb30c29e1ced1c9bfaa36053a5c032f0d4011a371609b5594167856285)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpVirtualNodeGroupHeadroomsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38c412f8961ebcf8e48806d21e16c46ce5109d7f29772ce2767c680f5a4aa050)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9e8c0dd828f811a2d8ebc866225875bac5cc124e4f75ba5b4ba4f479c9efa9a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__974d43c7fc45257ac74d187ad8f75a70405d9ce2fe66ec2b4a3b4768e9c2c79f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupHeadrooms]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupHeadrooms]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupHeadrooms]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb5110fbb42e9070c8b4cf937abca1b9f6f34bfc506522b6f26a171bca17feb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpVirtualNodeGroupHeadroomsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupHeadroomsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ef602ecc7433a63db191d09d6b08bd1bf032a29c3b869556b5d20c99c49bedd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad4ec17e4d177ab6b577ec37ecd28df38cce45544ed58b7d866fd6ed5107f2ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d173de7af7cfe2c56716df288ac213c1279e9ef7ce683a8183b851b3cf3a0558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__039e6ec96c708c630464e5170c17cef132e3bb90696139ca7ce36a7d0540ecb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00aa8db649aa5f96ee20954b8d0688bca1acffda9287b81117b35e765aa3d6db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupHeadrooms]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupHeadrooms]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupHeadrooms]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f78ed37056e186f6a63012cbbfc48622138f87a59edabd17883c1d69421f9258)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupLinuxOsConfig",
    jsii_struct_bases=[],
    name_mapping={"sysctls": "sysctls"},
)
class OceanAksNpVirtualNodeGroupLinuxOsConfig:
    def __init__(
        self,
        *,
        sysctls: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param sysctls: sysctls block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#sysctls OceanAksNpVirtualNodeGroup#sysctls}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cce293951226d705e1f0dbc020059cd72c87e8f8512fdab01d865821c54c356)
            check_type(argname="argument sysctls", value=sysctls, expected_type=type_hints["sysctls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if sysctls is not None:
            self._values["sysctls"] = sysctls

    @builtins.property
    def sysctls(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls"]]]:
        '''sysctls block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#sysctls OceanAksNpVirtualNodeGroup#sysctls}
        '''
        result = self._values.get("sysctls")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupLinuxOsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupLinuxOsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupLinuxOsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc6f62879beefb2700fd701083e33cbc30bd7d39ee8a6eaa82804194b5844e6c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAksNpVirtualNodeGroupLinuxOsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c1036782a1629402fd5741ca48cca418db303bf8d731835d337d566983ac597)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpVirtualNodeGroupLinuxOsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cae9d0c45f53a9d5e372d2c6d0360c5f470ba9b274189ccc53337a5f9ea8289)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f234f01df188726615842eecb6e5caaa8136dc62da12a59c8d9a91180981eea8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5413b49e265c1cdc1bc09cdb1904af945709f1f3bb98c9433d9e0713427191e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__121bac06d84d07540216d87cf3343a7a7bba99668f9354dc5e79c30c0fa100b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpVirtualNodeGroupLinuxOsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupLinuxOsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cd4991cf8e62d30d7cef7ba6792888aa7a1a7723ce02c7dd624842ad40b558b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putSysctls")
    def put_sysctls(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60af336cd1f4614ed030cb689a0ec04e2ec34555ce23362d13fce7898e698070)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSysctls", [value]))

    @jsii.member(jsii_name="resetSysctls")
    def reset_sysctls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSysctls", []))

    @builtins.property
    @jsii.member(jsii_name="sysctls")
    def sysctls(self) -> "OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsList":
        return typing.cast("OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsList", jsii.get(self, "sysctls"))

    @builtins.property
    @jsii.member(jsii_name="sysctlsInput")
    def sysctls_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls"]]], jsii.get(self, "sysctlsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e3813b3b17aec3564bbe5c825b3dae8a135fa37030a7688112643189f13912a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls",
    jsii_struct_bases=[],
    name_mapping={"vm_max_map_count": "vmMaxMapCount"},
)
class OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls:
    def __init__(
        self,
        *,
        vm_max_map_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param vm_max_map_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vm_max_map_count OceanAksNpVirtualNodeGroup#vm_max_map_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__560c2ab0972198df47012fe368d80b10b6eae9865f4826c26349dc7173eb5243)
            check_type(argname="argument vm_max_map_count", value=vm_max_map_count, expected_type=type_hints["vm_max_map_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if vm_max_map_count is not None:
            self._values["vm_max_map_count"] = vm_max_map_count

    @builtins.property
    def vm_max_map_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vm_max_map_count OceanAksNpVirtualNodeGroup#vm_max_map_count}.'''
        result = self._values.get("vm_max_map_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35771e03e937dc5d801a4b9940d514d6f32381903a2f5a73802f45a05fd24ae2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a8ae85d270628099c1d4a6f4ead9cbfba41b8c219ea1dc09c1f2b0ca1b212be)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34d8e632c3d9b23af8c68b9f705b88e4ad4a3eaa525184d3c47df28af4d95635)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6d1f4db73e9b0411b9678933f960492b2df9bad3c41d0156cdebbef5e3718ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c19f06dc342118f4e183bf962935e5b1c8772da34c2568bee9fa61b966af23e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d2dd816548a144094f2af40923bc4c78c84461996d3779a1c34aac424847011)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7e38ba3d3c1a72ab8f5414882a366cf342f8f9f15425f44ce384aec2b63a642)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d4970069819beaf5eb40d6dc025e0d712b8f48bed57a07706644863bd49f535)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmMaxMapCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39d6c53e66ce4e0d83e0be167196d704041fbc711a36578c317a3d41f27471ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupScheduling",
    jsii_struct_bases=[],
    name_mapping={"shutdown_hours": "shutdownHours"},
)
class OceanAksNpVirtualNodeGroupScheduling:
    def __init__(
        self,
        *,
        shutdown_hours: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupSchedulingShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param shutdown_hours: shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#shutdown_hours OceanAksNpVirtualNodeGroup#shutdown_hours}
        '''
        if isinstance(shutdown_hours, dict):
            shutdown_hours = OceanAksNpVirtualNodeGroupSchedulingShutdownHours(**shutdown_hours)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4547e6781b5f7532237f0da37ededd519cde93ebbb11c213146f6da83d9d4a75)
            check_type(argname="argument shutdown_hours", value=shutdown_hours, expected_type=type_hints["shutdown_hours"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if shutdown_hours is not None:
            self._values["shutdown_hours"] = shutdown_hours

    @builtins.property
    def shutdown_hours(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupSchedulingShutdownHours"]:
        '''shutdown_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#shutdown_hours OceanAksNpVirtualNodeGroup#shutdown_hours}
        '''
        result = self._values.get("shutdown_hours")
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupSchedulingShutdownHours"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupScheduling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupSchedulingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupSchedulingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__13868be4e3d82d9930248c7bb62b333472434c9a503dab91076ce7c985f004bb)
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
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#is_enabled OceanAksNpVirtualNodeGroup#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#time_windows OceanAksNpVirtualNodeGroup#time_windows}.
        '''
        value = OceanAksNpVirtualNodeGroupSchedulingShutdownHours(
            is_enabled=is_enabled, time_windows=time_windows
        )

        return typing.cast(None, jsii.invoke(self, "putShutdownHours", [value]))

    @jsii.member(jsii_name="resetShutdownHours")
    def reset_shutdown_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownHours", []))

    @builtins.property
    @jsii.member(jsii_name="shutdownHours")
    def shutdown_hours(
        self,
    ) -> "OceanAksNpVirtualNodeGroupSchedulingShutdownHoursOutputReference":
        return typing.cast("OceanAksNpVirtualNodeGroupSchedulingShutdownHoursOutputReference", jsii.get(self, "shutdownHours"))

    @builtins.property
    @jsii.member(jsii_name="shutdownHoursInput")
    def shutdown_hours_input(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupSchedulingShutdownHours"]:
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupSchedulingShutdownHours"], jsii.get(self, "shutdownHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpVirtualNodeGroupScheduling]:
        return typing.cast(typing.Optional[OceanAksNpVirtualNodeGroupScheduling], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVirtualNodeGroupScheduling],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f46b3ce5fb615494d65f730faa1f8b550443d22b2acfe2e4c0c6fd8ad69cb300)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupSchedulingShutdownHours",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled", "time_windows": "timeWindows"},
)
class OceanAksNpVirtualNodeGroupSchedulingShutdownHours:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#is_enabled OceanAksNpVirtualNodeGroup#is_enabled}.
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#time_windows OceanAksNpVirtualNodeGroup#time_windows}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bfce19630654e8ddd482225edae63e94d05005e632a66b0eae8b7d0763a5eaf)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#is_enabled OceanAksNpVirtualNodeGroup#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def time_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#time_windows OceanAksNpVirtualNodeGroup#time_windows}.'''
        result = self._values.get("time_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupSchedulingShutdownHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupSchedulingShutdownHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupSchedulingShutdownHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0d49826c817b8e1de448d638688a8cb91f1be53fef5cfe6ae0bd72e775cf5a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d0bc0a0bee5a4fb2f7b5ff68eaf92b4096b976d965e8737178fdf66b6c3f997)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindows")
    def time_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeWindows"))

    @time_windows.setter
    def time_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16168e8e9b9bc2b0a23fa8d4ca9461bd63c2f58aba4ae588ae277c5bc7696f78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpVirtualNodeGroupSchedulingShutdownHours]:
        return typing.cast(typing.Optional[OceanAksNpVirtualNodeGroupSchedulingShutdownHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVirtualNodeGroupSchedulingShutdownHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76f30b688f3e8beacd8f2e7ac37d34d3337e8aeb29ff391286706d42193967bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupTaints",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class OceanAksNpVirtualNodeGroupTaints:
    def __init__(
        self,
        *,
        effect: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param effect: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#effect OceanAksNpVirtualNodeGroup#effect}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#key OceanAksNpVirtualNodeGroup#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#value OceanAksNpVirtualNodeGroup#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c36029db99e9eeb7d9df65e8c23c82708b392187028177b45b2b0453dcd26b8)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#effect OceanAksNpVirtualNodeGroup#effect}.'''
        result = self._values.get("effect")
        assert result is not None, "Required property 'effect' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#key OceanAksNpVirtualNodeGroup#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#value OceanAksNpVirtualNodeGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupTaints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupTaintsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupTaintsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3e1111feacf402bf993830f8d356e63595b82c5573b1e80eb735fe93bc86010)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAksNpVirtualNodeGroupTaintsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c3af34a4ff6f8dc794fb7f985284eb028f960553bd39c11fa1166c67a470053)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAksNpVirtualNodeGroupTaintsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0227fbb32d363a73d1f1e10e8f90dcf88e5914fd0451abded3e1a3c0a36f701)
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
            type_hints = typing.get_type_hints(_typecheckingstub__72e347739e8c7e01ad75fa3812af16a3d465672668f5917855526cf8b1d68d53)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b013ed1adbbc44fc9e3854785967fdb4ada61f0832f45b249c4c42978e8e673)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupTaints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupTaints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupTaints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fee9c6958336b8bc49ac430614bf7b111e0af0b541987fb33406a573689aa9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAksNpVirtualNodeGroupTaintsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupTaintsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0394db69208dac15d750e907b0a7fc85cba20150d4176e170003d85f858818a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__451532ee485e07ce155bea4f346db453216583cc65f68dd714c1569e533c13bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7d9aae87ae5133291effabe84ae8eb4b86899a8396d5d569418773b7c40fb1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__217f28ff77015606607f2a23b366df4eb186beaf605af63ebfcc13347666802b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupTaints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupTaints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupTaints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4892dca50e5af8648753b4f32b41013252377373ffd226c748cfa16e125f2930)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupUpdatePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "should_roll": "shouldRoll",
        "conditioned_roll": "conditionedRoll",
        "roll_config": "rollConfig",
    },
)
class OceanAksNpVirtualNodeGroupUpdatePolicy:
    def __init__(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_config: typing.Optional[typing.Union["OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#should_roll OceanAksNpVirtualNodeGroup#should_roll}.
        :param conditioned_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#conditioned_roll OceanAksNpVirtualNodeGroup#conditioned_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#roll_config OceanAksNpVirtualNodeGroup#roll_config}
        '''
        if isinstance(roll_config, dict):
            roll_config = OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig(**roll_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__964e53e6bda5342d6b5c0b27001807b47be7b032f741e87d09f8b235c28cb6ae)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#should_roll OceanAksNpVirtualNodeGroup#should_roll}.'''
        result = self._values.get("should_roll")
        assert result is not None, "Required property 'should_roll' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def conditioned_roll(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#conditioned_roll OceanAksNpVirtualNodeGroup#conditioned_roll}.'''
        result = self._values.get("conditioned_roll")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def roll_config(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig"]:
        '''roll_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#roll_config OceanAksNpVirtualNodeGroup#roll_config}
        '''
        result = self._values.get("roll_config")
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupUpdatePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupUpdatePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupUpdatePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b27c7a033feef7a852c629eac641dfb852ce9988990c30e5eb689a533ddc0dbf)
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
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#batch_min_healthy_percentage OceanAksNpVirtualNodeGroup#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#batch_size_percentage OceanAksNpVirtualNodeGroup#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#comment OceanAksNpVirtualNodeGroup#comment}.
        :param node_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#node_names OceanAksNpVirtualNodeGroup#node_names}.
        :param node_pool_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#node_pool_names OceanAksNpVirtualNodeGroup#node_pool_names}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#respect_pdb OceanAksNpVirtualNodeGroup#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#respect_restrict_scale_down OceanAksNpVirtualNodeGroup#respect_restrict_scale_down}.
        :param vng_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vng_ids OceanAksNpVirtualNodeGroup#vng_ids}.
        '''
        value = OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig(
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
    def roll_config(
        self,
    ) -> "OceanAksNpVirtualNodeGroupUpdatePolicyRollConfigOutputReference":
        return typing.cast("OceanAksNpVirtualNodeGroupUpdatePolicyRollConfigOutputReference", jsii.get(self, "rollConfig"))

    @builtins.property
    @jsii.member(jsii_name="conditionedRollInput")
    def conditioned_roll_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "conditionedRollInput"))

    @builtins.property
    @jsii.member(jsii_name="rollConfigInput")
    def roll_config_input(
        self,
    ) -> typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig"]:
        return typing.cast(typing.Optional["OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig"], jsii.get(self, "rollConfigInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__814b65a7e8b468c9732ce45bdc9da8e9d8cbc98eb566fb0b06f98cad43cbb7b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d4287d5b6f2affca2370ad31229ccbce392c809401e08a1d439b246562116ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicy]:
        return typing.cast(typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f21b23d0a665d3715cd9f60156c10a5a114d093cabfe81c6a5e990ccddb9443)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig",
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
class OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig:
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
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#batch_min_healthy_percentage OceanAksNpVirtualNodeGroup#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#batch_size_percentage OceanAksNpVirtualNodeGroup#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#comment OceanAksNpVirtualNodeGroup#comment}.
        :param node_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#node_names OceanAksNpVirtualNodeGroup#node_names}.
        :param node_pool_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#node_pool_names OceanAksNpVirtualNodeGroup#node_pool_names}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#respect_pdb OceanAksNpVirtualNodeGroup#respect_pdb}.
        :param respect_restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#respect_restrict_scale_down OceanAksNpVirtualNodeGroup#respect_restrict_scale_down}.
        :param vng_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vng_ids OceanAksNpVirtualNodeGroup#vng_ids}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaba2c0cabf87898490d590f9d204a7ffe1c69e2efd7f4c34b7aefcd4eb0d400)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#batch_min_healthy_percentage OceanAksNpVirtualNodeGroup#batch_min_healthy_percentage}.'''
        result = self._values.get("batch_min_healthy_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#batch_size_percentage OceanAksNpVirtualNodeGroup#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#comment OceanAksNpVirtualNodeGroup#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#node_names OceanAksNpVirtualNodeGroup#node_names}.'''
        result = self._values.get("node_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node_pool_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#node_pool_names OceanAksNpVirtualNodeGroup#node_pool_names}.'''
        result = self._values.get("node_pool_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#respect_pdb OceanAksNpVirtualNodeGroup#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def respect_restrict_scale_down(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#respect_restrict_scale_down OceanAksNpVirtualNodeGroup#respect_restrict_scale_down}.'''
        result = self._values.get("respect_restrict_scale_down")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vng_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aks_np_virtual_node_group#vng_ids OceanAksNpVirtualNodeGroup#vng_ids}.'''
        result = self._values.get("vng_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAksNpVirtualNodeGroupUpdatePolicyRollConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAksNpVirtualNodeGroup.OceanAksNpVirtualNodeGroupUpdatePolicyRollConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a50e780c3ae628f39195a82d0d1c0135e2b7ad65f6c54ccbf284854cbc09f066)
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
            type_hints = typing.get_type_hints(_typecheckingstub__004919baab4d5fccfdcfe52cc9abcd40d3f7f4c375c883b605518bb39d3d570e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchMinHealthyPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8186aaab4aef44b4b2fa98fcc7fdf08cec0e9e7a4c8886f0c784583412d23b65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7097eb5aff6e909ca007c033e434966ab6a7f289e62ecf902509483e0c3fcb2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeNames")
    def node_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nodeNames"))

    @node_names.setter
    def node_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__322aee7324591449ddce1441397a7d35d6c037a22d7220026c46425f3b9e285a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodePoolNames")
    def node_pool_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nodePoolNames"))

    @node_pool_names.setter
    def node_pool_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d62c85040656956fdeeb2407b86f078ff694a2d86c70f04b90de42abdd84060)
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
            type_hints = typing.get_type_hints(_typecheckingstub__52565d1c6e236015e00c4e3751910bdff88ba8f574d5b1bfbfb3160dbed4addf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__340d9e397ed673115fefc63beb75fde376f29ce8c81298eba2bc919c2c686f99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectRestrictScaleDown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vngIds")
    def vng_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vngIds"))

    @vng_ids.setter
    def vng_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f52ba4339ede28f6857e16457b45bd436f67a3e52cf6b968d05dcea8dd1de5c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vngIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig]:
        return typing.cast(typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4b881222f4b5525fe87fe5f69ea0c7bcb03d6fe0beed1c1491103e0b689fe9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanAksNpVirtualNodeGroup",
    "OceanAksNpVirtualNodeGroupConfig",
    "OceanAksNpVirtualNodeGroupFilters",
    "OceanAksNpVirtualNodeGroupFiltersOutputReference",
    "OceanAksNpVirtualNodeGroupHeadrooms",
    "OceanAksNpVirtualNodeGroupHeadroomsList",
    "OceanAksNpVirtualNodeGroupHeadroomsOutputReference",
    "OceanAksNpVirtualNodeGroupLinuxOsConfig",
    "OceanAksNpVirtualNodeGroupLinuxOsConfigList",
    "OceanAksNpVirtualNodeGroupLinuxOsConfigOutputReference",
    "OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls",
    "OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsList",
    "OceanAksNpVirtualNodeGroupLinuxOsConfigSysctlsOutputReference",
    "OceanAksNpVirtualNodeGroupScheduling",
    "OceanAksNpVirtualNodeGroupSchedulingOutputReference",
    "OceanAksNpVirtualNodeGroupSchedulingShutdownHours",
    "OceanAksNpVirtualNodeGroupSchedulingShutdownHoursOutputReference",
    "OceanAksNpVirtualNodeGroupTaints",
    "OceanAksNpVirtualNodeGroupTaintsList",
    "OceanAksNpVirtualNodeGroupTaintsOutputReference",
    "OceanAksNpVirtualNodeGroupUpdatePolicy",
    "OceanAksNpVirtualNodeGroupUpdatePolicyOutputReference",
    "OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig",
    "OceanAksNpVirtualNodeGroupUpdatePolicyRollConfigOutputReference",
]

publication.publish()

def _typecheckingstub__bb94c83fd03c70412f5e6aaaaf00ee680b7dab6c645ad6fb5e95a986abb0cf51(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    ocean_id: builtins.str,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filters: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    kubernetes_version: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupLinuxOsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_count: typing.Optional[jsii.Number] = None,
    max_pods_per_node: typing.Optional[jsii.Number] = None,
    min_count: typing.Optional[jsii.Number] = None,
    os_disk_size_gb: typing.Optional[jsii.Number] = None,
    os_disk_type: typing.Optional[builtins.str] = None,
    os_sku: typing.Optional[builtins.str] = None,
    os_type: typing.Optional[builtins.str] = None,
    pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupScheduling, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__8d2c1249fb3a9f27cc7fbe4ef0f46b529b30ca5a2aadc068a53e76fc2875e6c5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57064b045997e5dd79e1a8e41b8e46cb9806fdbe4892c684e557171f85fef316(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupHeadrooms, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5ca0d8b1182e3808eb12013852cc85f02c5a5a81b8d8dee171b0ad42a92df28(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupLinuxOsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90474312d786e0cd0310b61ab5a441a4211a73046096a109fc3cb0ee70f6c4e6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupTaints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f136c0dc27a72e97b5786bd06ce621a428515c58a110c0c603153e9379e139d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d77f8a8fa45226a27a38bf793b62e21e76f36db3fabe8273fdc0354c2702328f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74109d527dee39fcd0d11ebfce8996348d02bf207ea2b4e261a2ee8cf184d8a1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a39b9046b9b72e917acaef1ac2a96e42bf6ea39d787e444e27dfa136ba6d74a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4ec301d5282a0e91f5c1ed1256717db251e5ff85af223789fab6d55995860cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a76be99151d0ef9031a88b4730b1e52b3e2fbf5174860e7105d8cf8de1107c1(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d52a9fbdff3807be7f1a3637c1be2756d32a01920c8e98b3ab022da0e9e75c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14f126f3cda35b71a4c545ffc79a48d49708ae4044d8c39fc3ad990287f0340(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb232bed1517a3393724bc2469e81f94b9de793020eaf5f896be2dc48a3a24e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1091ea4eb21760e24b9fa5c968cd0a9e79c375faae6dc50731d4bced48065ab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e38684343dcd939535a299d6fcee9def285fb80d10ec2b78c92ae1793ca72044(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3683469b615aaf08edb69c6b62290d2022f62dd58e727bc5e43a73d130787053(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d88664ff47d6517ecbfd1d5c18e24e20f34e6a79a64b73bb8a5b84e62859c23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__455c8a543cde2e6a5c98f3d354c72131e4215a1d22ac5d8d116a50a136a65867(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81eacb2a91cb58148e757d487bf79c7edb38ec6c1b5ddb845ebf67757ac3539d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac2dcb43daefa492f4c8abe3b2e3b2fc2a028dfd3b3a7c0a25c631d27f90c60f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61be4df3ed48cb5106eb6791dd3d6c679178d9250e091c96e9f303bc6c979eb9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c5da87b1a3fb604677b8e953d3d352e2d34dca26a77ef428cafceffec3ca880(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072f6446c57d78d0938f45feb3366528218d83bdf3d1bbc4521f39911f8c45a4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36b827f1f790c792f27aa490328a52655e9b7bc5bf63c279f78a15fb71548ed5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    ocean_id: builtins.str,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    enable_node_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    filters: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    kubernetes_version: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    linux_os_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupLinuxOsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_count: typing.Optional[jsii.Number] = None,
    max_pods_per_node: typing.Optional[jsii.Number] = None,
    min_count: typing.Optional[jsii.Number] = None,
    os_disk_size_gb: typing.Optional[jsii.Number] = None,
    os_disk_type: typing.Optional[builtins.str] = None,
    os_sku: typing.Optional[builtins.str] = None,
    os_type: typing.Optional[builtins.str] = None,
    pod_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    scheduling: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupScheduling, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    vnet_subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f63cb28b7caa6fc1f499540bb48e4b4d0a8c8f076fda66820783f79135b679f(
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

def _typecheckingstub__82d1c7ca3ed253bcaaca86ed66a7734acfa7a23f4e36ed3c9b20f109c9e18aa5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4791bc21b1dbad6d56305146c8030a96ee6c16969e0ada3083ade5190a1543(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af6a5290e8b4cf11a5f6117cddf8047c1c6ac6687fd54e96877ca54f8e98124f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__504e7eadeb6ab7d093be6964810e50bbb54bc3ad1283c61d6bbe21683c93f87c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6b465ee5ac1a1303507dad9131703445d0e8c9cbe31e49ab75259427e7276d4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b02d6c3f0eadef70e597f017164aa2d262af3810591d95d7c21c4eefb075cc3f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5190f8b0d383ac5226ce273508e4ac39d73ee9ace402b7690a6eb0a99c86a338(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17fcf7f30dec694aa3f83451a37cf39d2c8a7103f6f3dee9d8489920054810fe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b599c6e065fc2ca0416b5d6aba4292a3bd0b9aa568292edb2808c721bf66ed0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a943188d69826c9b7a551f7bc88305a9d38ed4b8573f3ca817469a328888952(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e746f20be811de710a3d5e8429b14030bb52e8fef8cd9dd4adcc0bf906aa51b4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eb08b60a4bcc94c891eec04fe10290257a443b7b862ceac14114b0ef76ba871(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01963254a678d679a324ca8cc37b420831e35ef3e7f3d5e8b848f5569b550587(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26fcb9bc7ae6cc117ce4f68284ab33e6ef204c3a0bacd83e7a93f06e0c55406c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__582ffd85cecc9232445c5fcbd95cd7dc437203d0a8e66c80c464362f9414fe3f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__372a81ba3244b4022b3b7135b91ce7f86ad0ee7a2bbe5daddc336fbb41adb1f2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2422a17a7bb5a7251372c36990eaf93478659caf05b064a869f50266f62e25(
    value: typing.Optional[OceanAksNpVirtualNodeGroupFilters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568e17c9e36be61c3d869c1c4db12b35782695418dd87c8f2dcf3959f9166982(
    *,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
    num_of_units: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc2b99b87a13a47fafcf8cbcee92962c126cb8b0b206eac41df5f7fc312b10a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__803708bb30c29e1ced1c9bfaa36053a5c032f0d4011a371609b5594167856285(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c412f8961ebcf8e48806d21e16c46ce5109d7f29772ce2767c680f5a4aa050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9e8c0dd828f811a2d8ebc866225875bac5cc124e4f75ba5b4ba4f479c9efa9a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__974d43c7fc45257ac74d187ad8f75a70405d9ce2fe66ec2b4a3b4768e9c2c79f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb5110fbb42e9070c8b4cf937abca1b9f6f34bfc506522b6f26a171bca17feb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupHeadrooms]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ef602ecc7433a63db191d09d6b08bd1bf032a29c3b869556b5d20c99c49bedd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4ec17e4d177ab6b577ec37ecd28df38cce45544ed58b7d866fd6ed5107f2ee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d173de7af7cfe2c56716df288ac213c1279e9ef7ce683a8183b851b3cf3a0558(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039e6ec96c708c630464e5170c17cef132e3bb90696139ca7ce36a7d0540ecb5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00aa8db649aa5f96ee20954b8d0688bca1acffda9287b81117b35e765aa3d6db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f78ed37056e186f6a63012cbbfc48622138f87a59edabd17883c1d69421f9258(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupHeadrooms]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cce293951226d705e1f0dbc020059cd72c87e8f8512fdab01d865821c54c356(
    *,
    sysctls: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc6f62879beefb2700fd701083e33cbc30bd7d39ee8a6eaa82804194b5844e6c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c1036782a1629402fd5741ca48cca418db303bf8d731835d337d566983ac597(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cae9d0c45f53a9d5e372d2c6d0360c5f470ba9b274189ccc53337a5f9ea8289(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f234f01df188726615842eecb6e5caaa8136dc62da12a59c8d9a91180981eea8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5413b49e265c1cdc1bc09cdb1904af945709f1f3bb98c9433d9e0713427191e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__121bac06d84d07540216d87cf3343a7a7bba99668f9354dc5e79c30c0fa100b9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cd4991cf8e62d30d7cef7ba6792888aa7a1a7723ce02c7dd624842ad40b558b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60af336cd1f4614ed030cb689a0ec04e2ec34555ce23362d13fce7898e698070(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e3813b3b17aec3564bbe5c825b3dae8a135fa37030a7688112643189f13912a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__560c2ab0972198df47012fe368d80b10b6eae9865f4826c26349dc7173eb5243(
    *,
    vm_max_map_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35771e03e937dc5d801a4b9940d514d6f32381903a2f5a73802f45a05fd24ae2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8ae85d270628099c1d4a6f4ead9cbfba41b8c219ea1dc09c1f2b0ca1b212be(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34d8e632c3d9b23af8c68b9f705b88e4ad4a3eaa525184d3c47df28af4d95635(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d1f4db73e9b0411b9678933f960492b2df9bad3c41d0156cdebbef5e3718ac(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c19f06dc342118f4e183bf962935e5b1c8772da34c2568bee9fa61b966af23e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d2dd816548a144094f2af40923bc4c78c84461996d3779a1c34aac424847011(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7e38ba3d3c1a72ab8f5414882a366cf342f8f9f15425f44ce384aec2b63a642(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d4970069819beaf5eb40d6dc025e0d712b8f48bed57a07706644863bd49f535(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39d6c53e66ce4e0d83e0be167196d704041fbc711a36578c317a3d41f27471ce(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupLinuxOsConfigSysctls]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4547e6781b5f7532237f0da37ededd519cde93ebbb11c213146f6da83d9d4a75(
    *,
    shutdown_hours: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupSchedulingShutdownHours, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13868be4e3d82d9930248c7bb62b333472434c9a503dab91076ce7c985f004bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f46b3ce5fb615494d65f730faa1f8b550443d22b2acfe2e4c0c6fd8ad69cb300(
    value: typing.Optional[OceanAksNpVirtualNodeGroupScheduling],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bfce19630654e8ddd482225edae63e94d05005e632a66b0eae8b7d0763a5eaf(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    time_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0d49826c817b8e1de448d638688a8cb91f1be53fef5cfe6ae0bd72e775cf5a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0bc0a0bee5a4fb2f7b5ff68eaf92b4096b976d965e8737178fdf66b6c3f997(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16168e8e9b9bc2b0a23fa8d4ca9461bd63c2f58aba4ae588ae277c5bc7696f78(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76f30b688f3e8beacd8f2e7ac37d34d3337e8aeb29ff391286706d42193967bf(
    value: typing.Optional[OceanAksNpVirtualNodeGroupSchedulingShutdownHours],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c36029db99e9eeb7d9df65e8c23c82708b392187028177b45b2b0453dcd26b8(
    *,
    effect: builtins.str,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3e1111feacf402bf993830f8d356e63595b82c5573b1e80eb735fe93bc86010(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c3af34a4ff6f8dc794fb7f985284eb028f960553bd39c11fa1166c67a470053(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0227fbb32d363a73d1f1e10e8f90dcf88e5914fd0451abded3e1a3c0a36f701(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e347739e8c7e01ad75fa3812af16a3d465672668f5917855526cf8b1d68d53(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b013ed1adbbc44fc9e3854785967fdb4ada61f0832f45b249c4c42978e8e673(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fee9c6958336b8bc49ac430614bf7b111e0af0b541987fb33406a573689aa9b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAksNpVirtualNodeGroupTaints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0394db69208dac15d750e907b0a7fc85cba20150d4176e170003d85f858818a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__451532ee485e07ce155bea4f346db453216583cc65f68dd714c1569e533c13bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d9aae87ae5133291effabe84ae8eb4b86899a8396d5d569418773b7c40fb1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__217f28ff77015606607f2a23b366df4eb186beaf605af63ebfcc13347666802b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4892dca50e5af8648753b4f32b41013252377373ffd226c748cfa16e125f2930(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAksNpVirtualNodeGroupTaints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__964e53e6bda5342d6b5c0b27001807b47be7b032f741e87d09f8b235c28cb6ae(
    *,
    should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    roll_config: typing.Optional[typing.Union[OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27c7a033feef7a852c629eac641dfb852ce9988990c30e5eb689a533ddc0dbf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__814b65a7e8b468c9732ce45bdc9da8e9d8cbc98eb566fb0b06f98cad43cbb7b6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d4287d5b6f2affca2370ad31229ccbce392c809401e08a1d439b246562116ee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f21b23d0a665d3715cd9f60156c10a5a114d093cabfe81c6a5e990ccddb9443(
    value: typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaba2c0cabf87898490d590f9d204a7ffe1c69e2efd7f4c34b7aefcd4eb0d400(
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

def _typecheckingstub__a50e780c3ae628f39195a82d0d1c0135e2b7ad65f6c54ccbf284854cbc09f066(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__004919baab4d5fccfdcfe52cc9abcd40d3f7f4c375c883b605518bb39d3d570e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8186aaab4aef44b4b2fa98fcc7fdf08cec0e9e7a4c8886f0c784583412d23b65(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7097eb5aff6e909ca007c033e434966ab6a7f289e62ecf902509483e0c3fcb2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322aee7324591449ddce1441397a7d35d6c037a22d7220026c46425f3b9e285a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d62c85040656956fdeeb2407b86f078ff694a2d86c70f04b90de42abdd84060(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52565d1c6e236015e00c4e3751910bdff88ba8f574d5b1bfbfb3160dbed4addf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340d9e397ed673115fefc63beb75fde376f29ce8c81298eba2bc919c2c686f99(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f52ba4339ede28f6857e16457b45bd436f67a3e52cf6b968d05dcea8dd1de5c0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4b881222f4b5525fe87fe5f69ea0c7bcb03d6fe0beed1c1491103e0b689fe9f(
    value: typing.Optional[OceanAksNpVirtualNodeGroupUpdatePolicyRollConfig],
) -> None:
    """Type checking stubs"""
    pass
