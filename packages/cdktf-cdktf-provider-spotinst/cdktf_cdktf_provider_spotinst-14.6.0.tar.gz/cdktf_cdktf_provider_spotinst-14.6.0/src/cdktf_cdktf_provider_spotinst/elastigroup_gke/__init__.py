r'''
# `spotinst_elastigroup_gke`

Refer to the Terraform Registry for docs: [`spotinst_elastigroup_gke`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke).
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


class ElastigroupGke(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGke",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke spotinst_elastigroup_gke}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_zone_name: builtins.str,
        desired_capacity: jsii.Number,
        name: builtins.str,
        backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeBackendServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gpu: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeGpu", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_name_prefix: typing.Optional[builtins.str] = None,
        instance_types_custom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeInstanceTypesCustom", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_types_ondemand: typing.Optional[builtins.str] = None,
        instance_types_preemptible: typing.Optional[typing.Sequence[builtins.str]] = None,
        integration_docker_swarm: typing.Optional[typing.Union["ElastigroupGkeIntegrationDockerSwarm", typing.Dict[builtins.str, typing.Any]]] = None,
        integration_gke: typing.Optional[typing.Union["ElastigroupGkeIntegrationGke", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeMetadata", typing.Dict[builtins.str, typing.Any]]]]] = None,
        min_cpu_platform: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        node_image: typing.Optional[builtins.str] = None,
        ondemand_count: typing.Optional[jsii.Number] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        preemptible_percentage: typing.Optional[jsii.Number] = None,
        provisioning_model: typing.Optional[builtins.str] = None,
        revert_to_preemptible: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeRevertToPreemptible", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_account: typing.Optional[builtins.str] = None,
        shielded_instance_config: typing.Optional[typing.Union["ElastigroupGkeShieldedInstanceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        should_utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        startup_script: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke spotinst_elastigroup_gke} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_zone_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_zone_name ElastigroupGke#cluster_zone_name}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#desired_capacity ElastigroupGke#desired_capacity}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.
        :param backend_services: backend_services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_services ElastigroupGke#backend_services}
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_id ElastigroupGke#cluster_id}.
        :param disk: disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk ElastigroupGke#disk}
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#draining_timeout ElastigroupGke#draining_timeout}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#fallback_to_ondemand ElastigroupGke#fallback_to_ondemand}.
        :param gpu: gpu block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#gpu ElastigroupGke#gpu}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#id ElastigroupGke#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_name_prefix ElastigroupGke#instance_name_prefix}.
        :param instance_types_custom: instance_types_custom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_custom ElastigroupGke#instance_types_custom}
        :param instance_types_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_ondemand ElastigroupGke#instance_types_ondemand}.
        :param instance_types_preemptible: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_preemptible ElastigroupGke#instance_types_preemptible}.
        :param integration_docker_swarm: integration_docker_swarm block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#integration_docker_swarm ElastigroupGke#integration_docker_swarm}
        :param integration_gke: integration_gke block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#integration_gke ElastigroupGke#integration_gke}
        :param ip_forwarding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ip_forwarding ElastigroupGke#ip_forwarding}.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#labels ElastigroupGke#labels}
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#max_size ElastigroupGke#max_size}.
        :param metadata: metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metadata ElastigroupGke#metadata}
        :param min_cpu_platform: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#min_cpu_platform ElastigroupGke#min_cpu_platform}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#min_size ElastigroupGke#min_size}.
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#network_interface ElastigroupGke#network_interface}
        :param node_image: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#node_image ElastigroupGke#node_image}.
        :param ondemand_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ondemand_count ElastigroupGke#ondemand_count}.
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#optimization_windows ElastigroupGke#optimization_windows}.
        :param preemptible_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#preemptible_percentage ElastigroupGke#preemptible_percentage}.
        :param provisioning_model: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#provisioning_model ElastigroupGke#provisioning_model}.
        :param revert_to_preemptible: revert_to_preemptible block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#revert_to_preemptible ElastigroupGke#revert_to_preemptible}
        :param scaling_down_policy: scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scaling_down_policy ElastigroupGke#scaling_down_policy}
        :param scaling_up_policy: scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scaling_up_policy ElastigroupGke#scaling_up_policy}
        :param service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#service_account ElastigroupGke#service_account}.
        :param shielded_instance_config: shielded_instance_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#shielded_instance_config ElastigroupGke#shielded_instance_config}
        :param should_utilize_commitments: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#should_utilize_commitments ElastigroupGke#should_utilize_commitments}.
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#shutdown_script ElastigroupGke#shutdown_script}.
        :param startup_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#startup_script ElastigroupGke#startup_script}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#tags ElastigroupGke#tags}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ab72032d7eb2efff6d0fe7d3c446e32344fb0b12cea79683d6ded1f2d5a8ba)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElastigroupGkeConfig(
            cluster_zone_name=cluster_zone_name,
            desired_capacity=desired_capacity,
            name=name,
            backend_services=backend_services,
            cluster_id=cluster_id,
            disk=disk,
            draining_timeout=draining_timeout,
            fallback_to_ondemand=fallback_to_ondemand,
            gpu=gpu,
            id=id,
            instance_name_prefix=instance_name_prefix,
            instance_types_custom=instance_types_custom,
            instance_types_ondemand=instance_types_ondemand,
            instance_types_preemptible=instance_types_preemptible,
            integration_docker_swarm=integration_docker_swarm,
            integration_gke=integration_gke,
            ip_forwarding=ip_forwarding,
            labels=labels,
            max_size=max_size,
            metadata=metadata,
            min_cpu_platform=min_cpu_platform,
            min_size=min_size,
            network_interface=network_interface,
            node_image=node_image,
            ondemand_count=ondemand_count,
            optimization_windows=optimization_windows,
            preemptible_percentage=preemptible_percentage,
            provisioning_model=provisioning_model,
            revert_to_preemptible=revert_to_preemptible,
            scaling_down_policy=scaling_down_policy,
            scaling_up_policy=scaling_up_policy,
            service_account=service_account,
            shielded_instance_config=shielded_instance_config,
            should_utilize_commitments=should_utilize_commitments,
            shutdown_script=shutdown_script,
            startup_script=startup_script,
            tags=tags,
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
        '''Generates CDKTF code for importing a ElastigroupGke resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ElastigroupGke to import.
        :param import_from_id: The id of the existing ElastigroupGke that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ElastigroupGke to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83877478f2df8be7519a1bab89f86e6f6e1e02642852324aa8dc1d6ba8271c22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putBackendServices")
    def put_backend_services(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeBackendServices", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a735eb945ab54c178a07c47a53e734c607308143ea2773d33cb6e6782746ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBackendServices", [value]))

    @jsii.member(jsii_name="putDisk")
    def put_disk(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeDisk", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0566651a74216b0e2b4854d92d6a5ebd2a9e5cbbbb4629ad6ab31fe0e9949be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDisk", [value]))

    @jsii.member(jsii_name="putGpu")
    def put_gpu(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeGpu", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e0dcd985d8b39fedcd97baa1d9258f3f1f062fdebec6735a46c0d8f22c5bf76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGpu", [value]))

    @jsii.member(jsii_name="putInstanceTypesCustom")
    def put_instance_types_custom(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeInstanceTypesCustom", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__881dcb7c86b2de5055cf5564f776d3af2ec9a57ca797eb743c6cefdd75e22dd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInstanceTypesCustom", [value]))

    @jsii.member(jsii_name="putIntegrationDockerSwarm")
    def put_integration_docker_swarm(
        self,
        *,
        master_host: builtins.str,
        master_port: jsii.Number,
    ) -> None:
        '''
        :param master_host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#master_host ElastigroupGke#master_host}.
        :param master_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#master_port ElastigroupGke#master_port}.
        '''
        value = ElastigroupGkeIntegrationDockerSwarm(
            master_host=master_host, master_port=master_port
        )

        return typing.cast(None, jsii.invoke(self, "putIntegrationDockerSwarm", [value]))

    @jsii.member(jsii_name="putIntegrationGke")
    def put_integration_gke(
        self,
        *,
        autoscale_cooldown: typing.Optional[jsii.Number] = None,
        autoscale_down: typing.Optional[typing.Union["ElastigroupGkeIntegrationGkeAutoscaleDown", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_headroom: typing.Optional[typing.Union["ElastigroupGkeIntegrationGkeAutoscaleHeadroom", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_is_auto_config: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale_is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale_labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeIntegrationGkeAutoscaleLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auto_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param autoscale_cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_cooldown ElastigroupGke#autoscale_cooldown}.
        :param autoscale_down: autoscale_down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_down ElastigroupGke#autoscale_down}
        :param autoscale_headroom: autoscale_headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_headroom ElastigroupGke#autoscale_headroom}
        :param autoscale_is_auto_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_is_auto_config ElastigroupGke#autoscale_is_auto_config}.
        :param autoscale_is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_is_enabled ElastigroupGke#autoscale_is_enabled}.
        :param autoscale_labels: autoscale_labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_labels ElastigroupGke#autoscale_labels}
        :param auto_update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#auto_update ElastigroupGke#auto_update}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_id ElastigroupGke#cluster_id}.
        :param location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#location ElastigroupGke#location}.
        '''
        value = ElastigroupGkeIntegrationGke(
            autoscale_cooldown=autoscale_cooldown,
            autoscale_down=autoscale_down,
            autoscale_headroom=autoscale_headroom,
            autoscale_is_auto_config=autoscale_is_auto_config,
            autoscale_is_enabled=autoscale_is_enabled,
            autoscale_labels=autoscale_labels,
            auto_update=auto_update,
            cluster_id=cluster_id,
            location=location,
        )

        return typing.cast(None, jsii.invoke(self, "putIntegrationGke", [value]))

    @jsii.member(jsii_name="putLabels")
    def put_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeLabels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cca2b2e03a5b1ddd2de25438630e79da8fc522a68a344f2b818dae5b7d2364fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLabels", [value]))

    @jsii.member(jsii_name="putMetadata")
    def put_metadata(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeMetadata", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3a161565c7015f1e31caaa789162b310c36e58b4e7001c0779c74ad72f05a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMetadata", [value]))

    @jsii.member(jsii_name="putNetworkInterface")
    def put_network_interface(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeNetworkInterface", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8767c039d8f7af36e234e8a12f6330f641ca07386b1b27020e5d4c7a3beb9b62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterface", [value]))

    @jsii.member(jsii_name="putRevertToPreemptible")
    def put_revert_to_preemptible(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeRevertToPreemptible", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e40e9ee22daad5158993dc5a7607436f297912eeadc4385fd795ad3db1ddb06e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRevertToPreemptible", [value]))

    @jsii.member(jsii_name="putScalingDownPolicy")
    def put_scaling_down_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13f49123044c5abc566fb835add9231ed8f77f37bdeff9b7c8cce93e9d16d322)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScalingDownPolicy", [value]))

    @jsii.member(jsii_name="putScalingUpPolicy")
    def put_scaling_up_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__250c472f6750b0fdfa9d6233d71dfc0e0d71002d51a1dd9d3a812838e471de53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScalingUpPolicy", [value]))

    @jsii.member(jsii_name="putShieldedInstanceConfig")
    def put_shielded_instance_config(
        self,
        *,
        enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enable_integrity_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#enable_integrity_monitoring ElastigroupGke#enable_integrity_monitoring}.
        :param enable_secure_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#enable_secure_boot ElastigroupGke#enable_secure_boot}.
        '''
        value = ElastigroupGkeShieldedInstanceConfig(
            enable_integrity_monitoring=enable_integrity_monitoring,
            enable_secure_boot=enable_secure_boot,
        )

        return typing.cast(None, jsii.invoke(self, "putShieldedInstanceConfig", [value]))

    @jsii.member(jsii_name="resetBackendServices")
    def reset_backend_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackendServices", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetDisk")
    def reset_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisk", []))

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetFallbackToOndemand")
    def reset_fallback_to_ondemand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallbackToOndemand", []))

    @jsii.member(jsii_name="resetGpu")
    def reset_gpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGpu", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceNamePrefix")
    def reset_instance_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceNamePrefix", []))

    @jsii.member(jsii_name="resetInstanceTypesCustom")
    def reset_instance_types_custom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypesCustom", []))

    @jsii.member(jsii_name="resetInstanceTypesOndemand")
    def reset_instance_types_ondemand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypesOndemand", []))

    @jsii.member(jsii_name="resetInstanceTypesPreemptible")
    def reset_instance_types_preemptible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypesPreemptible", []))

    @jsii.member(jsii_name="resetIntegrationDockerSwarm")
    def reset_integration_docker_swarm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationDockerSwarm", []))

    @jsii.member(jsii_name="resetIntegrationGke")
    def reset_integration_gke(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationGke", []))

    @jsii.member(jsii_name="resetIpForwarding")
    def reset_ip_forwarding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpForwarding", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMaxSize")
    def reset_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxSize", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetMinCpuPlatform")
    def reset_min_cpu_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCpuPlatform", []))

    @jsii.member(jsii_name="resetMinSize")
    def reset_min_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinSize", []))

    @jsii.member(jsii_name="resetNetworkInterface")
    def reset_network_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkInterface", []))

    @jsii.member(jsii_name="resetNodeImage")
    def reset_node_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeImage", []))

    @jsii.member(jsii_name="resetOndemandCount")
    def reset_ondemand_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOndemandCount", []))

    @jsii.member(jsii_name="resetOptimizationWindows")
    def reset_optimization_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimizationWindows", []))

    @jsii.member(jsii_name="resetPreemptiblePercentage")
    def reset_preemptible_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreemptiblePercentage", []))

    @jsii.member(jsii_name="resetProvisioningModel")
    def reset_provisioning_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisioningModel", []))

    @jsii.member(jsii_name="resetRevertToPreemptible")
    def reset_revert_to_preemptible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevertToPreemptible", []))

    @jsii.member(jsii_name="resetScalingDownPolicy")
    def reset_scaling_down_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingDownPolicy", []))

    @jsii.member(jsii_name="resetScalingUpPolicy")
    def reset_scaling_up_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingUpPolicy", []))

    @jsii.member(jsii_name="resetServiceAccount")
    def reset_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccount", []))

    @jsii.member(jsii_name="resetShieldedInstanceConfig")
    def reset_shielded_instance_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShieldedInstanceConfig", []))

    @jsii.member(jsii_name="resetShouldUtilizeCommitments")
    def reset_should_utilize_commitments(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldUtilizeCommitments", []))

    @jsii.member(jsii_name="resetShutdownScript")
    def reset_shutdown_script(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownScript", []))

    @jsii.member(jsii_name="resetStartupScript")
    def reset_startup_script(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartupScript", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="backendServices")
    def backend_services(self) -> "ElastigroupGkeBackendServicesList":
        return typing.cast("ElastigroupGkeBackendServicesList", jsii.get(self, "backendServices"))

    @builtins.property
    @jsii.member(jsii_name="disk")
    def disk(self) -> "ElastigroupGkeDiskList":
        return typing.cast("ElastigroupGkeDiskList", jsii.get(self, "disk"))

    @builtins.property
    @jsii.member(jsii_name="gpu")
    def gpu(self) -> "ElastigroupGkeGpuList":
        return typing.cast("ElastigroupGkeGpuList", jsii.get(self, "gpu"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesCustom")
    def instance_types_custom(self) -> "ElastigroupGkeInstanceTypesCustomList":
        return typing.cast("ElastigroupGkeInstanceTypesCustomList", jsii.get(self, "instanceTypesCustom"))

    @builtins.property
    @jsii.member(jsii_name="integrationDockerSwarm")
    def integration_docker_swarm(
        self,
    ) -> "ElastigroupGkeIntegrationDockerSwarmOutputReference":
        return typing.cast("ElastigroupGkeIntegrationDockerSwarmOutputReference", jsii.get(self, "integrationDockerSwarm"))

    @builtins.property
    @jsii.member(jsii_name="integrationGke")
    def integration_gke(self) -> "ElastigroupGkeIntegrationGkeOutputReference":
        return typing.cast("ElastigroupGkeIntegrationGkeOutputReference", jsii.get(self, "integrationGke"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> "ElastigroupGkeLabelsList":
        return typing.cast("ElastigroupGkeLabelsList", jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> "ElastigroupGkeMetadataList":
        return typing.cast("ElastigroupGkeMetadataList", jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> "ElastigroupGkeNetworkInterfaceList":
        return typing.cast("ElastigroupGkeNetworkInterfaceList", jsii.get(self, "networkInterface"))

    @builtins.property
    @jsii.member(jsii_name="revertToPreemptible")
    def revert_to_preemptible(self) -> "ElastigroupGkeRevertToPreemptibleList":
        return typing.cast("ElastigroupGkeRevertToPreemptibleList", jsii.get(self, "revertToPreemptible"))

    @builtins.property
    @jsii.member(jsii_name="scalingDownPolicy")
    def scaling_down_policy(self) -> "ElastigroupGkeScalingDownPolicyList":
        return typing.cast("ElastigroupGkeScalingDownPolicyList", jsii.get(self, "scalingDownPolicy"))

    @builtins.property
    @jsii.member(jsii_name="scalingUpPolicy")
    def scaling_up_policy(self) -> "ElastigroupGkeScalingUpPolicyList":
        return typing.cast("ElastigroupGkeScalingUpPolicyList", jsii.get(self, "scalingUpPolicy"))

    @builtins.property
    @jsii.member(jsii_name="shieldedInstanceConfig")
    def shielded_instance_config(
        self,
    ) -> "ElastigroupGkeShieldedInstanceConfigOutputReference":
        return typing.cast("ElastigroupGkeShieldedInstanceConfigOutputReference", jsii.get(self, "shieldedInstanceConfig"))

    @builtins.property
    @jsii.member(jsii_name="backendServicesInput")
    def backend_services_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeBackendServices"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeBackendServices"]]], jsii.get(self, "backendServicesInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterZoneNameInput")
    def cluster_zone_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterZoneNameInput"))

    @builtins.property
    @jsii.member(jsii_name="desiredCapacityInput")
    def desired_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "desiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="diskInput")
    def disk_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeDisk"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeDisk"]]], jsii.get(self, "diskInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackToOndemandInput")
    def fallback_to_ondemand_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackToOndemandInput"))

    @builtins.property
    @jsii.member(jsii_name="gpuInput")
    def gpu_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeGpu"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeGpu"]]], jsii.get(self, "gpuInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceNamePrefixInput")
    def instance_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceNamePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesCustomInput")
    def instance_types_custom_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeInstanceTypesCustom"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeInstanceTypesCustom"]]], jsii.get(self, "instanceTypesCustomInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesOndemandInput")
    def instance_types_ondemand_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypesOndemandInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesPreemptibleInput")
    def instance_types_preemptible_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypesPreemptibleInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationDockerSwarmInput")
    def integration_docker_swarm_input(
        self,
    ) -> typing.Optional["ElastigroupGkeIntegrationDockerSwarm"]:
        return typing.cast(typing.Optional["ElastigroupGkeIntegrationDockerSwarm"], jsii.get(self, "integrationDockerSwarmInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationGkeInput")
    def integration_gke_input(self) -> typing.Optional["ElastigroupGkeIntegrationGke"]:
        return typing.cast(typing.Optional["ElastigroupGkeIntegrationGke"], jsii.get(self, "integrationGkeInput"))

    @builtins.property
    @jsii.member(jsii_name="ipForwardingInput")
    def ip_forwarding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipForwardingInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeLabels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeLabels"]]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxSizeInput")
    def max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeMetadata"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeMetadata"]]], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="minCpuPlatformInput")
    def min_cpu_platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minCpuPlatformInput"))

    @builtins.property
    @jsii.member(jsii_name="minSizeInput")
    def min_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterface"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterface"]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeImageInput")
    def node_image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeImageInput"))

    @builtins.property
    @jsii.member(jsii_name="ondemandCountInput")
    def ondemand_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ondemandCountInput"))

    @builtins.property
    @jsii.member(jsii_name="optimizationWindowsInput")
    def optimization_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optimizationWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="preemptiblePercentageInput")
    def preemptible_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "preemptiblePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="provisioningModelInput")
    def provisioning_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provisioningModelInput"))

    @builtins.property
    @jsii.member(jsii_name="revertToPreemptibleInput")
    def revert_to_preemptible_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeRevertToPreemptible"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeRevertToPreemptible"]]], jsii.get(self, "revertToPreemptibleInput"))

    @builtins.property
    @jsii.member(jsii_name="scalingDownPolicyInput")
    def scaling_down_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingDownPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingDownPolicy"]]], jsii.get(self, "scalingDownPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="scalingUpPolicyInput")
    def scaling_up_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingUpPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingUpPolicy"]]], jsii.get(self, "scalingUpPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountInput")
    def service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="shieldedInstanceConfigInput")
    def shielded_instance_config_input(
        self,
    ) -> typing.Optional["ElastigroupGkeShieldedInstanceConfig"]:
        return typing.cast(typing.Optional["ElastigroupGkeShieldedInstanceConfig"], jsii.get(self, "shieldedInstanceConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldUtilizeCommitmentsInput")
    def should_utilize_commitments_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldUtilizeCommitmentsInput"))

    @builtins.property
    @jsii.member(jsii_name="shutdownScriptInput")
    def shutdown_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shutdownScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="startupScriptInput")
    def startup_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startupScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e23124c9930b9b9cb5e15a9053b734cf1e6ab7625eaa5b5c6bea0f5755a204e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterZoneName")
    def cluster_zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterZoneName"))

    @cluster_zone_name.setter
    def cluster_zone_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd28c88b9990fcf62d7672ccfd54cd64af0cab83fc0c3b454e07662f9247e402)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterZoneName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="desiredCapacity")
    def desired_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "desiredCapacity"))

    @desired_capacity.setter
    def desired_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__373d857b071d02af2ecfb33f2430857e2892b8e7cf87928cc72ce068e7320380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb1a38ab76d91769af3c006b2b61bdc527003003085eaa6b5e82682a32a8694d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainingTimeout", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__72c17147a465aa9f7b89e235776b7ff1e83bfa197cd045a895bdbd91bfa4e92c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackToOndemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1c979f67d0a34c4dbe767798e23ba71f62b95917705686a635d203649463870)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceNamePrefix")
    def instance_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceNamePrefix"))

    @instance_name_prefix.setter
    def instance_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d4f7f6389053b6787eb9f6b7b95c593d0e3f62b3e277f8c21a7b144e8c725a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceTypesOndemand")
    def instance_types_ondemand(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceTypesOndemand"))

    @instance_types_ondemand.setter
    def instance_types_ondemand(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__100eef8a5810d7314e8037906ec5b4195ef872590339f7bf38c6b3f2bb4e35ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypesOndemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceTypesPreemptible")
    def instance_types_preemptible(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypesPreemptible"))

    @instance_types_preemptible.setter
    def instance_types_preemptible(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98386d6c63f91e21ec0ae2cf00f9fedfc4cfa9bdd8a849bc6d501ae9c562e47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypesPreemptible", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipForwarding")
    def ip_forwarding(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipForwarding"))

    @ip_forwarding.setter
    def ip_forwarding(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32f61fb510fca2f4ca48ddde520d47b5181a2b10bd80712e5c0efd26e9efa7a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipForwarding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxSize")
    def max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSize"))

    @max_size.setter
    def max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab5571a192eca21c2201e874aaac426085b2b605b5b00ec3ea14fc7042470e68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCpuPlatform")
    def min_cpu_platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minCpuPlatform"))

    @min_cpu_platform.setter
    def min_cpu_platform(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a9d5aaa867b3f78394bbe1ffe0160491cbcb332c53bc4772aa566413eb6331d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCpuPlatform", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minSize")
    def min_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSize"))

    @min_size.setter
    def min_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__559d15bced24aeef490be2d90e750a8bb8edeb9c0737b70080330636102e0259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d9c7021402af527195d4da21feeda98a520a3082d653dbd8d9477a18b685e28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeImage")
    def node_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeImage"))

    @node_image.setter
    def node_image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a38f798856894c823cca1a8a36c0e51e944de61813b105dd73486a9ec5bded2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeImage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ondemandCount")
    def ondemand_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ondemandCount"))

    @ondemand_count.setter
    def ondemand_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f82d4b353339b325731a42c3184220ed4a0ffa5c45329730c18e01276da1bd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ondemandCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optimizationWindows")
    def optimization_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "optimizationWindows"))

    @optimization_windows.setter
    def optimization_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__617e0c41c0286daeb42f6f886b18e50d3249ce38105f8cc85a2f5f134c68c4ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimizationWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preemptiblePercentage")
    def preemptible_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preemptiblePercentage"))

    @preemptible_percentage.setter
    def preemptible_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce1f98451b50572f9da937af37e4c7cd3d5eba7c53bd317bc8f967f18572381f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preemptiblePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provisioningModel")
    def provisioning_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningModel"))

    @provisioning_model.setter
    def provisioning_model(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__765750ac2dadcf17746ce6bedbe317f6988db8c4936335277c1dfeb58d5ae6f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provisioningModel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccount"))

    @service_account.setter
    def service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb90639fa6b754183b2fc5a7600156cc967008fb821e6fa1e1f357504a7a5005)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldUtilizeCommitments")
    def should_utilize_commitments(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldUtilizeCommitments"))

    @should_utilize_commitments.setter
    def should_utilize_commitments(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baa7bb12b86f73468a9e80505d7bc3896c93a392bc81493b7e1cde14701a779a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldUtilizeCommitments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shutdownScript")
    def shutdown_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shutdownScript"))

    @shutdown_script.setter
    def shutdown_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0eafca9f79e518319de43e2efd86cebc92dd54ebfeed37ddce6ff50943e270a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shutdownScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startupScript")
    def startup_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startupScript"))

    @startup_script.setter
    def startup_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d85592f381c5e34ac389b6e559db9fe9755afe05099835c58f17a959bb7545)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startupScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d766467ec63a7c5f8d0fe801c56eaa3bbfe1673a66857b7457d15b533874b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServices",
    jsii_struct_bases=[],
    name_mapping={
        "service_name": "serviceName",
        "backend_balancing": "backendBalancing",
        "location_type": "locationType",
        "named_ports": "namedPorts",
        "scheme": "scheme",
    },
)
class ElastigroupGkeBackendServices:
    def __init__(
        self,
        *,
        service_name: builtins.str,
        backend_balancing: typing.Optional[typing.Union["ElastigroupGkeBackendServicesBackendBalancing", typing.Dict[builtins.str, typing.Any]]] = None,
        location_type: typing.Optional[builtins.str] = None,
        named_ports: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeBackendServicesNamedPorts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scheme: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#service_name ElastigroupGke#service_name}.
        :param backend_balancing: backend_balancing block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_balancing ElastigroupGke#backend_balancing}
        :param location_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#location_type ElastigroupGke#location_type}.
        :param named_ports: named_ports block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#named_ports ElastigroupGke#named_ports}
        :param scheme: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scheme ElastigroupGke#scheme}.
        '''
        if isinstance(backend_balancing, dict):
            backend_balancing = ElastigroupGkeBackendServicesBackendBalancing(**backend_balancing)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55f5eb709ab8e9fa433ec35dddb0a8d8036a4cbcf6187ea6db4ebf35bf798646)
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument backend_balancing", value=backend_balancing, expected_type=type_hints["backend_balancing"])
            check_type(argname="argument location_type", value=location_type, expected_type=type_hints["location_type"])
            check_type(argname="argument named_ports", value=named_ports, expected_type=type_hints["named_ports"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_name": service_name,
        }
        if backend_balancing is not None:
            self._values["backend_balancing"] = backend_balancing
        if location_type is not None:
            self._values["location_type"] = location_type
        if named_ports is not None:
            self._values["named_ports"] = named_ports
        if scheme is not None:
            self._values["scheme"] = scheme

    @builtins.property
    def service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#service_name ElastigroupGke#service_name}.'''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend_balancing(
        self,
    ) -> typing.Optional["ElastigroupGkeBackendServicesBackendBalancing"]:
        '''backend_balancing block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_balancing ElastigroupGke#backend_balancing}
        '''
        result = self._values.get("backend_balancing")
        return typing.cast(typing.Optional["ElastigroupGkeBackendServicesBackendBalancing"], result)

    @builtins.property
    def location_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#location_type ElastigroupGke#location_type}.'''
        result = self._values.get("location_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def named_ports(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeBackendServicesNamedPorts"]]]:
        '''named_ports block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#named_ports ElastigroupGke#named_ports}
        '''
        result = self._values.get("named_ports")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeBackendServicesNamedPorts"]]], result)

    @builtins.property
    def scheme(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scheme ElastigroupGke#scheme}.'''
        result = self._values.get("scheme")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeBackendServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesBackendBalancing",
    jsii_struct_bases=[],
    name_mapping={
        "backend_balancing_mode": "backendBalancingMode",
        "max_rate_per_instance": "maxRatePerInstance",
    },
)
class ElastigroupGkeBackendServicesBackendBalancing:
    def __init__(
        self,
        *,
        backend_balancing_mode: typing.Optional[builtins.str] = None,
        max_rate_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param backend_balancing_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_balancing_mode ElastigroupGke#backend_balancing_mode}.
        :param max_rate_per_instance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#max_rate_per_instance ElastigroupGke#max_rate_per_instance}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12090e1c337f5f8a30effa1714c1de32ae246856ceb2db48cabad5b0c4d5041e)
            check_type(argname="argument backend_balancing_mode", value=backend_balancing_mode, expected_type=type_hints["backend_balancing_mode"])
            check_type(argname="argument max_rate_per_instance", value=max_rate_per_instance, expected_type=type_hints["max_rate_per_instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if backend_balancing_mode is not None:
            self._values["backend_balancing_mode"] = backend_balancing_mode
        if max_rate_per_instance is not None:
            self._values["max_rate_per_instance"] = max_rate_per_instance

    @builtins.property
    def backend_balancing_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_balancing_mode ElastigroupGke#backend_balancing_mode}.'''
        result = self._values.get("backend_balancing_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_rate_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#max_rate_per_instance ElastigroupGke#max_rate_per_instance}.'''
        result = self._values.get("max_rate_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeBackendServicesBackendBalancing(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeBackendServicesBackendBalancingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesBackendBalancingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__deb3ff3056a14217ba00dac160ed93b008b792b2607a597ecd153f1acd0cc17c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBackendBalancingMode")
    def reset_backend_balancing_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackendBalancingMode", []))

    @jsii.member(jsii_name="resetMaxRatePerInstance")
    def reset_max_rate_per_instance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRatePerInstance", []))

    @builtins.property
    @jsii.member(jsii_name="backendBalancingModeInput")
    def backend_balancing_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendBalancingModeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRatePerInstanceInput")
    def max_rate_per_instance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRatePerInstanceInput"))

    @builtins.property
    @jsii.member(jsii_name="backendBalancingMode")
    def backend_balancing_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backendBalancingMode"))

    @backend_balancing_mode.setter
    def backend_balancing_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b47767b3156f558e414211b78d58af0e03f3af63b47fc6dec3e71daaebd1e82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backendBalancingMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRatePerInstance")
    def max_rate_per_instance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRatePerInstance"))

    @max_rate_per_instance.setter
    def max_rate_per_instance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e1882dae39b1d8c2adb3a1ae21033f7e877dcfb3582090eaea8f205e2b29dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRatePerInstance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupGkeBackendServicesBackendBalancing]:
        return typing.cast(typing.Optional[ElastigroupGkeBackendServicesBackendBalancing], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupGkeBackendServicesBackendBalancing],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d9b8383de17ec21e32fb62cbe56fb33f7e860792b6e3a726f5186de645f6c84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeBackendServicesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2dfa1918eb3d05517acc6685a76610e01860c88a2676100504eba53bc83718ec)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupGkeBackendServicesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37d0c4da8b872913938f83053ad8755cdb4a1243f567b78d89238d50658d6acd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeBackendServicesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a48ec2ff5b3e00f6d692fedfcf9c1c2c21f8de275d93d88de7682ad257196cb8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f05af79eceada0ea85731c34391e243f58319c8a44f74d382fd765a439292e63)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60319bd8fcb3be8c907fa4332c87b8da56c104dcfdc73c7f4bf364a196e94a6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServices]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServices]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServices]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3554e48888991d59897b97712262e9cb66f6016c2661e6db760ca0ebfbfcdcd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesNamedPorts",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "ports": "ports"},
)
class ElastigroupGkeBackendServicesNamedPorts:
    def __init__(
        self,
        *,
        name: builtins.str,
        ports: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.
        :param ports: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ports ElastigroupGke#ports}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf31f2dc005cd04e9200011d1ccd74c5473a88b9fbef1d8db6d2d26e3ea75f2)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ports", value=ports, expected_type=type_hints["ports"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "ports": ports,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ports(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ports ElastigroupGke#ports}.'''
        result = self._values.get("ports")
        assert result is not None, "Required property 'ports' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeBackendServicesNamedPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeBackendServicesNamedPortsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesNamedPortsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c16966dceff4e6e45a4e93ce6b401a8bbd55706542033daaf0b969c0be54ecd4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeBackendServicesNamedPortsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d90dc372ded5ea9d68ad6b5e4ebae056f2f1f1005a5c9c0ce47f099470df6e4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeBackendServicesNamedPortsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0280efe60f66f6076a2b1e0d5d3bb4e66221efc528ccea04dd6a10e008284f3d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__194df109ee492fe67b727b6b0945d36b6dc1f20fe4121b2fdbc0253b1e6d8b45)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28c6ff2cd545e9f1a84e2613637ef539097685f2f6957d20654d5ed1b03b9fdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServicesNamedPorts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServicesNamedPorts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServicesNamedPorts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ee18b811c8f462c442db86529752c8fd491e445f1c3711e7dd608ca213a1baa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeBackendServicesNamedPortsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesNamedPortsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f6dfd9891e296a140beec17b6951bab83bb375242c1f31af52721fbd8f1e6ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="portsInput")
    def ports_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "portsInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__265ef78efac034aa1801acaa4010ebb4042eb39132a07acd093ebdd41a60e445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd8bcd9ffb4d051a1f97bf1bbb25be93da07bc78207ca8afe82fc87d19b2401)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ports", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServicesNamedPorts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServicesNamedPorts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServicesNamedPorts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbbdb302bcd1cf852258ea78ffa1120c6fff0bb7159ea4e66226a7d16c326bc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeBackendServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeBackendServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50b710239b1abb44ec3d0b4c9bbd515da31c46276059fd162478179aecff8ffc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putBackendBalancing")
    def put_backend_balancing(
        self,
        *,
        backend_balancing_mode: typing.Optional[builtins.str] = None,
        max_rate_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param backend_balancing_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_balancing_mode ElastigroupGke#backend_balancing_mode}.
        :param max_rate_per_instance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#max_rate_per_instance ElastigroupGke#max_rate_per_instance}.
        '''
        value = ElastigroupGkeBackendServicesBackendBalancing(
            backend_balancing_mode=backend_balancing_mode,
            max_rate_per_instance=max_rate_per_instance,
        )

        return typing.cast(None, jsii.invoke(self, "putBackendBalancing", [value]))

    @jsii.member(jsii_name="putNamedPorts")
    def put_named_ports(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServicesNamedPorts, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__849f61f4bb983080ac38cd8fbcf667e3e3dcbd35f0f729a6a9f90f231f359978)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNamedPorts", [value]))

    @jsii.member(jsii_name="resetBackendBalancing")
    def reset_backend_balancing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackendBalancing", []))

    @jsii.member(jsii_name="resetLocationType")
    def reset_location_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocationType", []))

    @jsii.member(jsii_name="resetNamedPorts")
    def reset_named_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamedPorts", []))

    @jsii.member(jsii_name="resetScheme")
    def reset_scheme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheme", []))

    @builtins.property
    @jsii.member(jsii_name="backendBalancing")
    def backend_balancing(
        self,
    ) -> ElastigroupGkeBackendServicesBackendBalancingOutputReference:
        return typing.cast(ElastigroupGkeBackendServicesBackendBalancingOutputReference, jsii.get(self, "backendBalancing"))

    @builtins.property
    @jsii.member(jsii_name="namedPorts")
    def named_ports(self) -> ElastigroupGkeBackendServicesNamedPortsList:
        return typing.cast(ElastigroupGkeBackendServicesNamedPortsList, jsii.get(self, "namedPorts"))

    @builtins.property
    @jsii.member(jsii_name="backendBalancingInput")
    def backend_balancing_input(
        self,
    ) -> typing.Optional[ElastigroupGkeBackendServicesBackendBalancing]:
        return typing.cast(typing.Optional[ElastigroupGkeBackendServicesBackendBalancing], jsii.get(self, "backendBalancingInput"))

    @builtins.property
    @jsii.member(jsii_name="locationTypeInput")
    def location_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="namedPortsInput")
    def named_ports_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServicesNamedPorts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServicesNamedPorts]]], jsii.get(self, "namedPortsInput"))

    @builtins.property
    @jsii.member(jsii_name="schemeInput")
    def scheme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemeInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceNameInput")
    def service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="locationType")
    def location_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locationType"))

    @location_type.setter
    def location_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28985df1b0f9dfa3ab6137cb06453f9561209149471f7be32279e00d80d301ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f7fa6c990b25990d85f86279c2bd851ea095df3af4ba06bf0f0e058355e8e19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__404564523fdddbef0c9bce0598630837c4b7a943a30422624848534868420994)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServices]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServices]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServices]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3da6376d7e4a4ae3660ad1803da84745a41f34e899534597c5a4365902d7f20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_zone_name": "clusterZoneName",
        "desired_capacity": "desiredCapacity",
        "name": "name",
        "backend_services": "backendServices",
        "cluster_id": "clusterId",
        "disk": "disk",
        "draining_timeout": "drainingTimeout",
        "fallback_to_ondemand": "fallbackToOndemand",
        "gpu": "gpu",
        "id": "id",
        "instance_name_prefix": "instanceNamePrefix",
        "instance_types_custom": "instanceTypesCustom",
        "instance_types_ondemand": "instanceTypesOndemand",
        "instance_types_preemptible": "instanceTypesPreemptible",
        "integration_docker_swarm": "integrationDockerSwarm",
        "integration_gke": "integrationGke",
        "ip_forwarding": "ipForwarding",
        "labels": "labels",
        "max_size": "maxSize",
        "metadata": "metadata",
        "min_cpu_platform": "minCpuPlatform",
        "min_size": "minSize",
        "network_interface": "networkInterface",
        "node_image": "nodeImage",
        "ondemand_count": "ondemandCount",
        "optimization_windows": "optimizationWindows",
        "preemptible_percentage": "preemptiblePercentage",
        "provisioning_model": "provisioningModel",
        "revert_to_preemptible": "revertToPreemptible",
        "scaling_down_policy": "scalingDownPolicy",
        "scaling_up_policy": "scalingUpPolicy",
        "service_account": "serviceAccount",
        "shielded_instance_config": "shieldedInstanceConfig",
        "should_utilize_commitments": "shouldUtilizeCommitments",
        "shutdown_script": "shutdownScript",
        "startup_script": "startupScript",
        "tags": "tags",
    },
)
class ElastigroupGkeConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_zone_name: builtins.str,
        desired_capacity: jsii.Number,
        name: builtins.str,
        backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gpu: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeGpu", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_name_prefix: typing.Optional[builtins.str] = None,
        instance_types_custom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeInstanceTypesCustom", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_types_ondemand: typing.Optional[builtins.str] = None,
        instance_types_preemptible: typing.Optional[typing.Sequence[builtins.str]] = None,
        integration_docker_swarm: typing.Optional[typing.Union["ElastigroupGkeIntegrationDockerSwarm", typing.Dict[builtins.str, typing.Any]]] = None,
        integration_gke: typing.Optional[typing.Union["ElastigroupGkeIntegrationGke", typing.Dict[builtins.str, typing.Any]]] = None,
        ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeMetadata", typing.Dict[builtins.str, typing.Any]]]]] = None,
        min_cpu_platform: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        node_image: typing.Optional[builtins.str] = None,
        ondemand_count: typing.Optional[jsii.Number] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        preemptible_percentage: typing.Optional[jsii.Number] = None,
        provisioning_model: typing.Optional[builtins.str] = None,
        revert_to_preemptible: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeRevertToPreemptible", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_account: typing.Optional[builtins.str] = None,
        shielded_instance_config: typing.Optional[typing.Union["ElastigroupGkeShieldedInstanceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        should_utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        startup_script: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_zone_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_zone_name ElastigroupGke#cluster_zone_name}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#desired_capacity ElastigroupGke#desired_capacity}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.
        :param backend_services: backend_services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_services ElastigroupGke#backend_services}
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_id ElastigroupGke#cluster_id}.
        :param disk: disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk ElastigroupGke#disk}
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#draining_timeout ElastigroupGke#draining_timeout}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#fallback_to_ondemand ElastigroupGke#fallback_to_ondemand}.
        :param gpu: gpu block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#gpu ElastigroupGke#gpu}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#id ElastigroupGke#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_name_prefix ElastigroupGke#instance_name_prefix}.
        :param instance_types_custom: instance_types_custom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_custom ElastigroupGke#instance_types_custom}
        :param instance_types_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_ondemand ElastigroupGke#instance_types_ondemand}.
        :param instance_types_preemptible: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_preemptible ElastigroupGke#instance_types_preemptible}.
        :param integration_docker_swarm: integration_docker_swarm block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#integration_docker_swarm ElastigroupGke#integration_docker_swarm}
        :param integration_gke: integration_gke block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#integration_gke ElastigroupGke#integration_gke}
        :param ip_forwarding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ip_forwarding ElastigroupGke#ip_forwarding}.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#labels ElastigroupGke#labels}
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#max_size ElastigroupGke#max_size}.
        :param metadata: metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metadata ElastigroupGke#metadata}
        :param min_cpu_platform: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#min_cpu_platform ElastigroupGke#min_cpu_platform}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#min_size ElastigroupGke#min_size}.
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#network_interface ElastigroupGke#network_interface}
        :param node_image: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#node_image ElastigroupGke#node_image}.
        :param ondemand_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ondemand_count ElastigroupGke#ondemand_count}.
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#optimization_windows ElastigroupGke#optimization_windows}.
        :param preemptible_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#preemptible_percentage ElastigroupGke#preemptible_percentage}.
        :param provisioning_model: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#provisioning_model ElastigroupGke#provisioning_model}.
        :param revert_to_preemptible: revert_to_preemptible block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#revert_to_preemptible ElastigroupGke#revert_to_preemptible}
        :param scaling_down_policy: scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scaling_down_policy ElastigroupGke#scaling_down_policy}
        :param scaling_up_policy: scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scaling_up_policy ElastigroupGke#scaling_up_policy}
        :param service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#service_account ElastigroupGke#service_account}.
        :param shielded_instance_config: shielded_instance_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#shielded_instance_config ElastigroupGke#shielded_instance_config}
        :param should_utilize_commitments: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#should_utilize_commitments ElastigroupGke#should_utilize_commitments}.
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#shutdown_script ElastigroupGke#shutdown_script}.
        :param startup_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#startup_script ElastigroupGke#startup_script}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#tags ElastigroupGke#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(integration_docker_swarm, dict):
            integration_docker_swarm = ElastigroupGkeIntegrationDockerSwarm(**integration_docker_swarm)
        if isinstance(integration_gke, dict):
            integration_gke = ElastigroupGkeIntegrationGke(**integration_gke)
        if isinstance(shielded_instance_config, dict):
            shielded_instance_config = ElastigroupGkeShieldedInstanceConfig(**shielded_instance_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31cc1488e67b1ba3dcd55861e50eb60f032807325c88fa2cd57b8a3d0406d1b4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_zone_name", value=cluster_zone_name, expected_type=type_hints["cluster_zone_name"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument backend_services", value=backend_services, expected_type=type_hints["backend_services"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument disk", value=disk, expected_type=type_hints["disk"])
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument fallback_to_ondemand", value=fallback_to_ondemand, expected_type=type_hints["fallback_to_ondemand"])
            check_type(argname="argument gpu", value=gpu, expected_type=type_hints["gpu"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_name_prefix", value=instance_name_prefix, expected_type=type_hints["instance_name_prefix"])
            check_type(argname="argument instance_types_custom", value=instance_types_custom, expected_type=type_hints["instance_types_custom"])
            check_type(argname="argument instance_types_ondemand", value=instance_types_ondemand, expected_type=type_hints["instance_types_ondemand"])
            check_type(argname="argument instance_types_preemptible", value=instance_types_preemptible, expected_type=type_hints["instance_types_preemptible"])
            check_type(argname="argument integration_docker_swarm", value=integration_docker_swarm, expected_type=type_hints["integration_docker_swarm"])
            check_type(argname="argument integration_gke", value=integration_gke, expected_type=type_hints["integration_gke"])
            check_type(argname="argument ip_forwarding", value=ip_forwarding, expected_type=type_hints["ip_forwarding"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument min_cpu_platform", value=min_cpu_platform, expected_type=type_hints["min_cpu_platform"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
            check_type(argname="argument node_image", value=node_image, expected_type=type_hints["node_image"])
            check_type(argname="argument ondemand_count", value=ondemand_count, expected_type=type_hints["ondemand_count"])
            check_type(argname="argument optimization_windows", value=optimization_windows, expected_type=type_hints["optimization_windows"])
            check_type(argname="argument preemptible_percentage", value=preemptible_percentage, expected_type=type_hints["preemptible_percentage"])
            check_type(argname="argument provisioning_model", value=provisioning_model, expected_type=type_hints["provisioning_model"])
            check_type(argname="argument revert_to_preemptible", value=revert_to_preemptible, expected_type=type_hints["revert_to_preemptible"])
            check_type(argname="argument scaling_down_policy", value=scaling_down_policy, expected_type=type_hints["scaling_down_policy"])
            check_type(argname="argument scaling_up_policy", value=scaling_up_policy, expected_type=type_hints["scaling_up_policy"])
            check_type(argname="argument service_account", value=service_account, expected_type=type_hints["service_account"])
            check_type(argname="argument shielded_instance_config", value=shielded_instance_config, expected_type=type_hints["shielded_instance_config"])
            check_type(argname="argument should_utilize_commitments", value=should_utilize_commitments, expected_type=type_hints["should_utilize_commitments"])
            check_type(argname="argument shutdown_script", value=shutdown_script, expected_type=type_hints["shutdown_script"])
            check_type(argname="argument startup_script", value=startup_script, expected_type=type_hints["startup_script"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_zone_name": cluster_zone_name,
            "desired_capacity": desired_capacity,
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
        if backend_services is not None:
            self._values["backend_services"] = backend_services
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if disk is not None:
            self._values["disk"] = disk
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if fallback_to_ondemand is not None:
            self._values["fallback_to_ondemand"] = fallback_to_ondemand
        if gpu is not None:
            self._values["gpu"] = gpu
        if id is not None:
            self._values["id"] = id
        if instance_name_prefix is not None:
            self._values["instance_name_prefix"] = instance_name_prefix
        if instance_types_custom is not None:
            self._values["instance_types_custom"] = instance_types_custom
        if instance_types_ondemand is not None:
            self._values["instance_types_ondemand"] = instance_types_ondemand
        if instance_types_preemptible is not None:
            self._values["instance_types_preemptible"] = instance_types_preemptible
        if integration_docker_swarm is not None:
            self._values["integration_docker_swarm"] = integration_docker_swarm
        if integration_gke is not None:
            self._values["integration_gke"] = integration_gke
        if ip_forwarding is not None:
            self._values["ip_forwarding"] = ip_forwarding
        if labels is not None:
            self._values["labels"] = labels
        if max_size is not None:
            self._values["max_size"] = max_size
        if metadata is not None:
            self._values["metadata"] = metadata
        if min_cpu_platform is not None:
            self._values["min_cpu_platform"] = min_cpu_platform
        if min_size is not None:
            self._values["min_size"] = min_size
        if network_interface is not None:
            self._values["network_interface"] = network_interface
        if node_image is not None:
            self._values["node_image"] = node_image
        if ondemand_count is not None:
            self._values["ondemand_count"] = ondemand_count
        if optimization_windows is not None:
            self._values["optimization_windows"] = optimization_windows
        if preemptible_percentage is not None:
            self._values["preemptible_percentage"] = preemptible_percentage
        if provisioning_model is not None:
            self._values["provisioning_model"] = provisioning_model
        if revert_to_preemptible is not None:
            self._values["revert_to_preemptible"] = revert_to_preemptible
        if scaling_down_policy is not None:
            self._values["scaling_down_policy"] = scaling_down_policy
        if scaling_up_policy is not None:
            self._values["scaling_up_policy"] = scaling_up_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if shielded_instance_config is not None:
            self._values["shielded_instance_config"] = shielded_instance_config
        if should_utilize_commitments is not None:
            self._values["should_utilize_commitments"] = should_utilize_commitments
        if shutdown_script is not None:
            self._values["shutdown_script"] = shutdown_script
        if startup_script is not None:
            self._values["startup_script"] = startup_script
        if tags is not None:
            self._values["tags"] = tags

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
    def cluster_zone_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_zone_name ElastigroupGke#cluster_zone_name}.'''
        result = self._values.get("cluster_zone_name")
        assert result is not None, "Required property 'cluster_zone_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def desired_capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#desired_capacity ElastigroupGke#desired_capacity}.'''
        result = self._values.get("desired_capacity")
        assert result is not None, "Required property 'desired_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend_services(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServices]]]:
        '''backend_services block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#backend_services ElastigroupGke#backend_services}
        '''
        result = self._values.get("backend_services")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServices]]], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_id ElastigroupGke#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeDisk"]]]:
        '''disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk ElastigroupGke#disk}
        '''
        result = self._values.get("disk")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeDisk"]]], result)

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#draining_timeout ElastigroupGke#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fallback_to_ondemand(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#fallback_to_ondemand ElastigroupGke#fallback_to_ondemand}.'''
        result = self._values.get("fallback_to_ondemand")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gpu(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeGpu"]]]:
        '''gpu block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#gpu ElastigroupGke#gpu}
        '''
        result = self._values.get("gpu")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeGpu"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#id ElastigroupGke#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_name_prefix ElastigroupGke#instance_name_prefix}.'''
        result = self._values.get("instance_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types_custom(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeInstanceTypesCustom"]]]:
        '''instance_types_custom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_custom ElastigroupGke#instance_types_custom}
        '''
        result = self._values.get("instance_types_custom")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeInstanceTypesCustom"]]], result)

    @builtins.property
    def instance_types_ondemand(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_ondemand ElastigroupGke#instance_types_ondemand}.'''
        result = self._values.get("instance_types_ondemand")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types_preemptible(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#instance_types_preemptible ElastigroupGke#instance_types_preemptible}.'''
        result = self._values.get("instance_types_preemptible")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def integration_docker_swarm(
        self,
    ) -> typing.Optional["ElastigroupGkeIntegrationDockerSwarm"]:
        '''integration_docker_swarm block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#integration_docker_swarm ElastigroupGke#integration_docker_swarm}
        '''
        result = self._values.get("integration_docker_swarm")
        return typing.cast(typing.Optional["ElastigroupGkeIntegrationDockerSwarm"], result)

    @builtins.property
    def integration_gke(self) -> typing.Optional["ElastigroupGkeIntegrationGke"]:
        '''integration_gke block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#integration_gke ElastigroupGke#integration_gke}
        '''
        result = self._values.get("integration_gke")
        return typing.cast(typing.Optional["ElastigroupGkeIntegrationGke"], result)

    @builtins.property
    def ip_forwarding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ip_forwarding ElastigroupGke#ip_forwarding}.'''
        result = self._values.get("ip_forwarding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeLabels"]]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#labels ElastigroupGke#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeLabels"]]], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#max_size ElastigroupGke#max_size}.'''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def metadata(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeMetadata"]]]:
        '''metadata block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metadata ElastigroupGke#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeMetadata"]]], result)

    @builtins.property
    def min_cpu_platform(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#min_cpu_platform ElastigroupGke#min_cpu_platform}.'''
        result = self._values.get("min_cpu_platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#min_size ElastigroupGke#min_size}.'''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterface"]]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#network_interface ElastigroupGke#network_interface}
        '''
        result = self._values.get("network_interface")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterface"]]], result)

    @builtins.property
    def node_image(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#node_image ElastigroupGke#node_image}.'''
        result = self._values.get("node_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ondemand_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ondemand_count ElastigroupGke#ondemand_count}.'''
        result = self._values.get("ondemand_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def optimization_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#optimization_windows ElastigroupGke#optimization_windows}.'''
        result = self._values.get("optimization_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preemptible_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#preemptible_percentage ElastigroupGke#preemptible_percentage}.'''
        result = self._values.get("preemptible_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def provisioning_model(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#provisioning_model ElastigroupGke#provisioning_model}.'''
        result = self._values.get("provisioning_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revert_to_preemptible(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeRevertToPreemptible"]]]:
        '''revert_to_preemptible block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#revert_to_preemptible ElastigroupGke#revert_to_preemptible}
        '''
        result = self._values.get("revert_to_preemptible")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeRevertToPreemptible"]]], result)

    @builtins.property
    def scaling_down_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingDownPolicy"]]]:
        '''scaling_down_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scaling_down_policy ElastigroupGke#scaling_down_policy}
        '''
        result = self._values.get("scaling_down_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingDownPolicy"]]], result)

    @builtins.property
    def scaling_up_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingUpPolicy"]]]:
        '''scaling_up_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#scaling_up_policy ElastigroupGke#scaling_up_policy}
        '''
        result = self._values.get("scaling_up_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingUpPolicy"]]], result)

    @builtins.property
    def service_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#service_account ElastigroupGke#service_account}.'''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shielded_instance_config(
        self,
    ) -> typing.Optional["ElastigroupGkeShieldedInstanceConfig"]:
        '''shielded_instance_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#shielded_instance_config ElastigroupGke#shielded_instance_config}
        '''
        result = self._values.get("shielded_instance_config")
        return typing.cast(typing.Optional["ElastigroupGkeShieldedInstanceConfig"], result)

    @builtins.property
    def should_utilize_commitments(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#should_utilize_commitments ElastigroupGke#should_utilize_commitments}.'''
        result = self._values.get("should_utilize_commitments")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def shutdown_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#shutdown_script ElastigroupGke#shutdown_script}.'''
        result = self._values.get("shutdown_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def startup_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#startup_script ElastigroupGke#startup_script}.'''
        result = self._values.get("startup_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#tags ElastigroupGke#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeDisk",
    jsii_struct_bases=[],
    name_mapping={
        "auto_delete": "autoDelete",
        "boot": "boot",
        "device_name": "deviceName",
        "initialize_params": "initializeParams",
        "interface": "interface",
        "mode": "mode",
        "source": "source",
        "type": "type",
    },
)
class ElastigroupGkeDisk:
    def __init__(
        self,
        *,
        auto_delete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        device_name: typing.Optional[builtins.str] = None,
        initialize_params: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeDiskInitializeParams", typing.Dict[builtins.str, typing.Any]]]]] = None,
        interface: typing.Optional[builtins.str] = None,
        mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auto_delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#auto_delete ElastigroupGke#auto_delete}.
        :param boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#boot ElastigroupGke#boot}.
        :param device_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#device_name ElastigroupGke#device_name}.
        :param initialize_params: initialize_params block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#initialize_params ElastigroupGke#initialize_params}
        :param interface: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#interface ElastigroupGke#interface}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#mode ElastigroupGke#mode}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source ElastigroupGke#source}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#type ElastigroupGke#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78e2ea026bd428344f402d30979917cf250e43c5d83bee0dc3cc1ea5e5cc2536)
            check_type(argname="argument auto_delete", value=auto_delete, expected_type=type_hints["auto_delete"])
            check_type(argname="argument boot", value=boot, expected_type=type_hints["boot"])
            check_type(argname="argument device_name", value=device_name, expected_type=type_hints["device_name"])
            check_type(argname="argument initialize_params", value=initialize_params, expected_type=type_hints["initialize_params"])
            check_type(argname="argument interface", value=interface, expected_type=type_hints["interface"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_delete is not None:
            self._values["auto_delete"] = auto_delete
        if boot is not None:
            self._values["boot"] = boot
        if device_name is not None:
            self._values["device_name"] = device_name
        if initialize_params is not None:
            self._values["initialize_params"] = initialize_params
        if interface is not None:
            self._values["interface"] = interface
        if mode is not None:
            self._values["mode"] = mode
        if source is not None:
            self._values["source"] = source
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def auto_delete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#auto_delete ElastigroupGke#auto_delete}.'''
        result = self._values.get("auto_delete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#boot ElastigroupGke#boot}.'''
        result = self._values.get("boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def device_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#device_name ElastigroupGke#device_name}.'''
        result = self._values.get("device_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initialize_params(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeDiskInitializeParams"]]]:
        '''initialize_params block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#initialize_params ElastigroupGke#initialize_params}
        '''
        result = self._values.get("initialize_params")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeDiskInitializeParams"]]], result)

    @builtins.property
    def interface(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#interface ElastigroupGke#interface}.'''
        result = self._values.get("interface")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#mode ElastigroupGke#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source ElastigroupGke#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#type ElastigroupGke#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeDiskInitializeParams",
    jsii_struct_bases=[],
    name_mapping={
        "source_image": "sourceImage",
        "disk_size_gb": "diskSizeGb",
        "disk_type": "diskType",
    },
)
class ElastigroupGkeDiskInitializeParams:
    def __init__(
        self,
        *,
        source_image: builtins.str,
        disk_size_gb: typing.Optional[builtins.str] = None,
        disk_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param source_image: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source_image ElastigroupGke#source_image}.
        :param disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk_size_gb ElastigroupGke#disk_size_gb}.
        :param disk_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk_type ElastigroupGke#disk_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__161a87053383976c3992807ced1e8256d9c2683dc133ee9e0dfe1a9f44e0e1d2)
            check_type(argname="argument source_image", value=source_image, expected_type=type_hints["source_image"])
            check_type(argname="argument disk_size_gb", value=disk_size_gb, expected_type=type_hints["disk_size_gb"])
            check_type(argname="argument disk_type", value=disk_type, expected_type=type_hints["disk_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_image": source_image,
        }
        if disk_size_gb is not None:
            self._values["disk_size_gb"] = disk_size_gb
        if disk_type is not None:
            self._values["disk_type"] = disk_type

    @builtins.property
    def source_image(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source_image ElastigroupGke#source_image}.'''
        result = self._values.get("source_image")
        assert result is not None, "Required property 'source_image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def disk_size_gb(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk_size_gb ElastigroupGke#disk_size_gb}.'''
        result = self._values.get("disk_size_gb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#disk_type ElastigroupGke#disk_type}.'''
        result = self._values.get("disk_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeDiskInitializeParams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeDiskInitializeParamsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeDiskInitializeParamsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__939b661d58c3648439e2dca6a8262088d7f7708ac23e3395b8be9eb732a5d993)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeDiskInitializeParamsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cec97e84200949098314fed944c7eb293959706df4a47b64f269544a9e347931)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeDiskInitializeParamsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4f5276f9a81fd1682793705eaee50cba8f2a706bb0cdddc072d973d2b42b314)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee783fae29484ceae4689790498c3646ca093a685d9036ec11bcbf7782fb230b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__130399b5fdc68d63e294a6e1d2b1f76d38f120846534515b7b72dddb8b6698b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDiskInitializeParams]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDiskInitializeParams]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDiskInitializeParams]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ac3c7f07773dafc9572be82722b82efd8f68877f8bd683346e152a32ea9a886)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeDiskInitializeParamsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeDiskInitializeParamsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd9d8a18c64aa8745cb66cc152df7003a4a9b24c376fe4fbf9e722e522de90a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDiskSizeGb")
    def reset_disk_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSizeGb", []))

    @jsii.member(jsii_name="resetDiskType")
    def reset_disk_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskType", []))

    @builtins.property
    @jsii.member(jsii_name="diskSizeGbInput")
    def disk_size_gb_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskSizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="diskTypeInput")
    def disk_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceImageInput")
    def source_image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceImageInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSizeGb")
    def disk_size_gb(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskSizeGb"))

    @disk_size_gb.setter
    def disk_size_gb(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1187dea0c8505a41fb48b5be50c16f033c65df211dec32c28ec74756bc6be07f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskType")
    def disk_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diskType"))

    @disk_type.setter
    def disk_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd2676ec636146482f5482512a11951ac92c779d7ca26734dc4ab2e1b25cd111)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceImage")
    def source_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceImage"))

    @source_image.setter
    def source_image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cba7a19f0a73c498db832c3c7e95575f09130f210e8dee5740347399bbe573b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceImage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDiskInitializeParams]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDiskInitializeParams]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDiskInitializeParams]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d871aa931e7baddd24086f8c2c6f069ff3e727a43e6464c3346c511309e68646)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeDiskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeDiskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__73d9626ff1f509aded059999dfdc981ffaf5b465abc3842e016296caa4f4db46)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupGkeDiskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32ca2b634bf9d5e1f5081be9e5bfb56b1cee5e6fc4bfc69ba051e373b7253c3a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeDiskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b346afc29501995a5c619f67d98e7307fe1b99dee12cf0e96928159a962f4006)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d70c4e49a46c5ff5fa1d98ce6acfb4fbcf07e5b0401113e5a5f4c4c3f61bf122)
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
            type_hints = typing.get_type_hints(_typecheckingstub__289f5d306f05507e6eeebd6a69e63acd6b797a66a69f83a7b5bdba50a91f8187)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDisk]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDisk]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDisk]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb2c7eff6f1e009d46a0d7a5be65bab2b8ffd1f55e47f35043851a91b443de17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85847c95a707e1512ff30981435e5d64af72e67df8d76ae9246fd1c7625f1fae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putInitializeParams")
    def put_initialize_params(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeDiskInitializeParams, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ecdd5588f6474a7c50c2f0b2cb6fb0ff0b6c60b690c7cb7ffca525fd0e2c69a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInitializeParams", [value]))

    @jsii.member(jsii_name="resetAutoDelete")
    def reset_auto_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoDelete", []))

    @jsii.member(jsii_name="resetBoot")
    def reset_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoot", []))

    @jsii.member(jsii_name="resetDeviceName")
    def reset_device_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceName", []))

    @jsii.member(jsii_name="resetInitializeParams")
    def reset_initialize_params(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitializeParams", []))

    @jsii.member(jsii_name="resetInterface")
    def reset_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterface", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="initializeParams")
    def initialize_params(self) -> ElastigroupGkeDiskInitializeParamsList:
        return typing.cast(ElastigroupGkeDiskInitializeParamsList, jsii.get(self, "initializeParams"))

    @builtins.property
    @jsii.member(jsii_name="autoDeleteInput")
    def auto_delete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoDeleteInput"))

    @builtins.property
    @jsii.member(jsii_name="bootInput")
    def boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "bootInput"))

    @builtins.property
    @jsii.member(jsii_name="deviceNameInput")
    def device_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="initializeParamsInput")
    def initialize_params_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDiskInitializeParams]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDiskInitializeParams]]], jsii.get(self, "initializeParamsInput"))

    @builtins.property
    @jsii.member(jsii_name="interfaceInput")
    def interface_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "interfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="autoDelete")
    def auto_delete(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoDelete"))

    @auto_delete.setter
    def auto_delete(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3383f1efee119bd17ead41f7309c8d8fa241c580e0061253edc82a7196e87d64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoDelete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boot")
    def boot(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "boot"))

    @boot.setter
    def boot(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d0ffec9c70d034d4e7e6a8099154681323758d3d22b8802b2644c83ce24cea6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @device_name.setter
    def device_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8c31dd244a500c83717ceba7733230ebc0baac9ca44092a7a269aabadaf511a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interface")
    def interface(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interface"))

    @interface.setter
    def interface(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18dc01b910cc82f685e16f614b0e5b4d99bbd1c8dfe85b00224a8e6d4dbbaa3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interface", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b641372986b6cf1a5d653833e534c431cf68a5932b1a10cc0a670024176035d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b6fb6ca5e421cf07d6499be71e0052ab9532e58915f3916c2aeafa4080a7ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__490ebe2bdf80042f464ffc8a003c04ded070c9e282e368a47aa9779fff8181e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDisk]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDisk]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDisk]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef592af178bf33e901c01c63c1057f8d4f7f7591b4ece1736e805c434e69be2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeGpu",
    jsii_struct_bases=[],
    name_mapping={"count": "count", "type": "type"},
)
class ElastigroupGkeGpu:
    def __init__(self, *, count: jsii.Number, type: builtins.str) -> None:
        '''
        :param count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#count ElastigroupGke#count}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#type ElastigroupGke#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e64a09cf159e5a87b3ed60e039cabb8c815762c082866ad896f3cef3d52f75)
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "count": count,
            "type": type,
        }

    @builtins.property
    def count(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#count ElastigroupGke#count}.'''
        result = self._values.get("count")
        assert result is not None, "Required property 'count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#type ElastigroupGke#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeGpu(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeGpuList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeGpuList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a6329da3555b3e516aeb6be1d8318506a2acd9af4e52ccf3d45b8d5b2dc021a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupGkeGpuOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__291380353403012a45180d44a74c9cbac5239b90c97138c7b4e3abcb5b36f5d9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeGpuOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35220bbcecb63d1eaf13189fa941160cb4369fd559ddc132f73c863a56a5be0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d1744109be749b259fadf7a530d39e960d4d8493a59f6f187f754c458bc5e55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__19e550c7e619239472e9af94ec815acde33e9476ddf68b085bf1ca5d4807c944)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeGpu]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeGpu]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeGpu]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15fb7ff22f26d8ebad49e2431785318b5227892b9de65a6414cf67440daf0e29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeGpuOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeGpuOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da6ddc72df6b6c279c01235849fe9167fde85cf11273f163817d0263d8ec1a54)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d19fb2ee93e8f79c08426dbba97ac207253e5120a32c328232a4a3f5d2d5015)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "count", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92902385a0127ecb62b7bdcc4121a97e68c22ca57c609626213bb27bba1e8388)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeGpu]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeGpu]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeGpu]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ca3f9ad91df66121753c3a44470f9e96b6c739387d308fbbc656b97b445a74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeInstanceTypesCustom",
    jsii_struct_bases=[],
    name_mapping={"memory_gib": "memoryGib", "vcpu": "vcpu"},
)
class ElastigroupGkeInstanceTypesCustom:
    def __init__(self, *, memory_gib: jsii.Number, vcpu: jsii.Number) -> None:
        '''
        :param memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#memory_gib ElastigroupGke#memory_gib}.
        :param vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#vcpu ElastigroupGke#vcpu}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19ed856d4647aa37a6a96e3a52b5342a5f2863c05ec445cd3e0adeb7bdcc4bc4)
            check_type(argname="argument memory_gib", value=memory_gib, expected_type=type_hints["memory_gib"])
            check_type(argname="argument vcpu", value=vcpu, expected_type=type_hints["vcpu"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "memory_gib": memory_gib,
            "vcpu": vcpu,
        }

    @builtins.property
    def memory_gib(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#memory_gib ElastigroupGke#memory_gib}.'''
        result = self._values.get("memory_gib")
        assert result is not None, "Required property 'memory_gib' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vcpu(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#vcpu ElastigroupGke#vcpu}.'''
        result = self._values.get("vcpu")
        assert result is not None, "Required property 'vcpu' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeInstanceTypesCustom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeInstanceTypesCustomList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeInstanceTypesCustomList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__069b561987c625afbf2da7cabb9ed5e0e09aa024fa79265dab39ad9370b6c66e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeInstanceTypesCustomOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef5422a6bc3ac4e01c5ef7dd2dfd572de0d4cd58afb33b8197d75d8add1a28e5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeInstanceTypesCustomOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd035e578de7abd60529975de42526f52791a064769ca2c98691f386dd6e2150)
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
            type_hints = typing.get_type_hints(_typecheckingstub__91a9a11b1b85bd2f3995fcbd47b7b323490d9b72a9a4faee7f0302d92bf1e165)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d432fe2a105e04981c6065ed93228b667b434633505551d4d68f8427d42a558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeInstanceTypesCustom]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeInstanceTypesCustom]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeInstanceTypesCustom]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a26afe8652b6bdc91de50726efb30405531301787272050dd453084ca053753)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeInstanceTypesCustomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeInstanceTypesCustomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e1a052cdcd2474b515713eea2067c87dabb9b94f9678abc3753a6d22c185179)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="memoryGibInput")
    def memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="vcpuInput")
    def vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "vcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryGib")
    def memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryGib"))

    @memory_gib.setter
    def memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c4f8a66e95af940d172cbd8ec952d68b4413a003561beae72a631db4bf055eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vcpu")
    def vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "vcpu"))

    @vcpu.setter
    def vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09cc5eee25d3367ec4c8af8948045944e8f979ede79f6f6318560b45720137bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeInstanceTypesCustom]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeInstanceTypesCustom]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeInstanceTypesCustom]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47e824d5f0293ea6a25258eb44a0a2108ea50df5ad7f603c9873d1193cb462d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationDockerSwarm",
    jsii_struct_bases=[],
    name_mapping={"master_host": "masterHost", "master_port": "masterPort"},
)
class ElastigroupGkeIntegrationDockerSwarm:
    def __init__(self, *, master_host: builtins.str, master_port: jsii.Number) -> None:
        '''
        :param master_host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#master_host ElastigroupGke#master_host}.
        :param master_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#master_port ElastigroupGke#master_port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6350d3337e3a6fb62d76c2802dccc5082d2502a80ac7ffa3305648c80ea9fea2)
            check_type(argname="argument master_host", value=master_host, expected_type=type_hints["master_host"])
            check_type(argname="argument master_port", value=master_port, expected_type=type_hints["master_port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "master_host": master_host,
            "master_port": master_port,
        }

    @builtins.property
    def master_host(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#master_host ElastigroupGke#master_host}.'''
        result = self._values.get("master_host")
        assert result is not None, "Required property 'master_host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def master_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#master_port ElastigroupGke#master_port}.'''
        result = self._values.get("master_port")
        assert result is not None, "Required property 'master_port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeIntegrationDockerSwarm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeIntegrationDockerSwarmOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationDockerSwarmOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b1849ff7658649af93c3a014a7811c8ec2aa92aa504f13ff3c7eb057328c7ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="masterHostInput")
    def master_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterHostInput"))

    @builtins.property
    @jsii.member(jsii_name="masterPortInput")
    def master_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "masterPortInput"))

    @builtins.property
    @jsii.member(jsii_name="masterHost")
    def master_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterHost"))

    @master_host.setter
    def master_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f480da93b1bd2e6dc7e15ff82c9d054003b7bed6e11f51f48d4a7d3205c3b3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="masterPort")
    def master_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "masterPort"))

    @master_port.setter
    def master_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__058b4451bc38a656bcee70531e57679dd26fd009e2a229edd1d89e4f4adbc17e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupGkeIntegrationDockerSwarm]:
        return typing.cast(typing.Optional[ElastigroupGkeIntegrationDockerSwarm], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupGkeIntegrationDockerSwarm],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39a7451f1bf0470281ecf2a0345a2ef1db519fd17914670dfea403f562c03107)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGke",
    jsii_struct_bases=[],
    name_mapping={
        "autoscale_cooldown": "autoscaleCooldown",
        "autoscale_down": "autoscaleDown",
        "autoscale_headroom": "autoscaleHeadroom",
        "autoscale_is_auto_config": "autoscaleIsAutoConfig",
        "autoscale_is_enabled": "autoscaleIsEnabled",
        "autoscale_labels": "autoscaleLabels",
        "auto_update": "autoUpdate",
        "cluster_id": "clusterId",
        "location": "location",
    },
)
class ElastigroupGkeIntegrationGke:
    def __init__(
        self,
        *,
        autoscale_cooldown: typing.Optional[jsii.Number] = None,
        autoscale_down: typing.Optional[typing.Union["ElastigroupGkeIntegrationGkeAutoscaleDown", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_headroom: typing.Optional[typing.Union["ElastigroupGkeIntegrationGkeAutoscaleHeadroom", typing.Dict[builtins.str, typing.Any]]] = None,
        autoscale_is_auto_config: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale_is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale_labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeIntegrationGkeAutoscaleLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auto_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param autoscale_cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_cooldown ElastigroupGke#autoscale_cooldown}.
        :param autoscale_down: autoscale_down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_down ElastigroupGke#autoscale_down}
        :param autoscale_headroom: autoscale_headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_headroom ElastigroupGke#autoscale_headroom}
        :param autoscale_is_auto_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_is_auto_config ElastigroupGke#autoscale_is_auto_config}.
        :param autoscale_is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_is_enabled ElastigroupGke#autoscale_is_enabled}.
        :param autoscale_labels: autoscale_labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_labels ElastigroupGke#autoscale_labels}
        :param auto_update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#auto_update ElastigroupGke#auto_update}.
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_id ElastigroupGke#cluster_id}.
        :param location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#location ElastigroupGke#location}.
        '''
        if isinstance(autoscale_down, dict):
            autoscale_down = ElastigroupGkeIntegrationGkeAutoscaleDown(**autoscale_down)
        if isinstance(autoscale_headroom, dict):
            autoscale_headroom = ElastigroupGkeIntegrationGkeAutoscaleHeadroom(**autoscale_headroom)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcee4dc325f1f0ebc7a6631475939e7eccf4a19f147822d68bba12dead359b6a)
            check_type(argname="argument autoscale_cooldown", value=autoscale_cooldown, expected_type=type_hints["autoscale_cooldown"])
            check_type(argname="argument autoscale_down", value=autoscale_down, expected_type=type_hints["autoscale_down"])
            check_type(argname="argument autoscale_headroom", value=autoscale_headroom, expected_type=type_hints["autoscale_headroom"])
            check_type(argname="argument autoscale_is_auto_config", value=autoscale_is_auto_config, expected_type=type_hints["autoscale_is_auto_config"])
            check_type(argname="argument autoscale_is_enabled", value=autoscale_is_enabled, expected_type=type_hints["autoscale_is_enabled"])
            check_type(argname="argument autoscale_labels", value=autoscale_labels, expected_type=type_hints["autoscale_labels"])
            check_type(argname="argument auto_update", value=auto_update, expected_type=type_hints["auto_update"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if autoscale_cooldown is not None:
            self._values["autoscale_cooldown"] = autoscale_cooldown
        if autoscale_down is not None:
            self._values["autoscale_down"] = autoscale_down
        if autoscale_headroom is not None:
            self._values["autoscale_headroom"] = autoscale_headroom
        if autoscale_is_auto_config is not None:
            self._values["autoscale_is_auto_config"] = autoscale_is_auto_config
        if autoscale_is_enabled is not None:
            self._values["autoscale_is_enabled"] = autoscale_is_enabled
        if autoscale_labels is not None:
            self._values["autoscale_labels"] = autoscale_labels
        if auto_update is not None:
            self._values["auto_update"] = auto_update
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if location is not None:
            self._values["location"] = location

    @builtins.property
    def autoscale_cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_cooldown ElastigroupGke#autoscale_cooldown}.'''
        result = self._values.get("autoscale_cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autoscale_down(
        self,
    ) -> typing.Optional["ElastigroupGkeIntegrationGkeAutoscaleDown"]:
        '''autoscale_down block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_down ElastigroupGke#autoscale_down}
        '''
        result = self._values.get("autoscale_down")
        return typing.cast(typing.Optional["ElastigroupGkeIntegrationGkeAutoscaleDown"], result)

    @builtins.property
    def autoscale_headroom(
        self,
    ) -> typing.Optional["ElastigroupGkeIntegrationGkeAutoscaleHeadroom"]:
        '''autoscale_headroom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_headroom ElastigroupGke#autoscale_headroom}
        '''
        result = self._values.get("autoscale_headroom")
        return typing.cast(typing.Optional["ElastigroupGkeIntegrationGkeAutoscaleHeadroom"], result)

    @builtins.property
    def autoscale_is_auto_config(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_is_auto_config ElastigroupGke#autoscale_is_auto_config}.'''
        result = self._values.get("autoscale_is_auto_config")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def autoscale_is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_is_enabled ElastigroupGke#autoscale_is_enabled}.'''
        result = self._values.get("autoscale_is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def autoscale_labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeIntegrationGkeAutoscaleLabels"]]]:
        '''autoscale_labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#autoscale_labels ElastigroupGke#autoscale_labels}
        '''
        result = self._values.get("autoscale_labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeIntegrationGkeAutoscaleLabels"]]], result)

    @builtins.property
    def auto_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#auto_update ElastigroupGke#auto_update}.'''
        result = self._values.get("auto_update")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cluster_id ElastigroupGke#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#location ElastigroupGke#location}.'''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeIntegrationGke(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleDown",
    jsii_struct_bases=[],
    name_mapping={"evaluation_periods": "evaluationPeriods"},
)
class ElastigroupGkeIntegrationGkeAutoscaleDown:
    def __init__(
        self,
        *,
        evaluation_periods: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97bfcaa9427025c0dc948c8be20b8d9854304541bc0c2c4d96317d7dc270ee81)
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeIntegrationGkeAutoscaleDown(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeIntegrationGkeAutoscaleDownOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleDownOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__df43ac7e45e84ecb4e39d294cf2b236b8736c8cbc9b042a6f4d7cb3bcdb4ff70)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEvaluationPeriods")
    def reset_evaluation_periods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluationPeriods", []))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec47339bb957eb9793f3599936dfb26b938b1f1c975a5321e424f6f1277a87ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleDown]:
        return typing.cast(typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleDown], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleDown],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__009877fa223113175e6be2355d89aae897338982b61b7b5d59bc88bab976357e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleHeadroom",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_per_unit": "cpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
        "num_of_units": "numOfUnits",
    },
)
class ElastigroupGkeIntegrationGkeAutoscaleHeadroom:
    def __init__(
        self,
        *,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
        num_of_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cpu_per_unit ElastigroupGke#cpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#memory_per_unit ElastigroupGke#memory_per_unit}.
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#num_of_units ElastigroupGke#num_of_units}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a6a800dfb4f382d5a99d36460a08e95b80136448355129992c0ab94300159fe)
            check_type(argname="argument cpu_per_unit", value=cpu_per_unit, expected_type=type_hints["cpu_per_unit"])
            check_type(argname="argument memory_per_unit", value=memory_per_unit, expected_type=type_hints["memory_per_unit"])
            check_type(argname="argument num_of_units", value=num_of_units, expected_type=type_hints["num_of_units"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_per_unit is not None:
            self._values["cpu_per_unit"] = cpu_per_unit
        if memory_per_unit is not None:
            self._values["memory_per_unit"] = memory_per_unit
        if num_of_units is not None:
            self._values["num_of_units"] = num_of_units

    @builtins.property
    def cpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cpu_per_unit ElastigroupGke#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#memory_per_unit ElastigroupGke#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_of_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#num_of_units ElastigroupGke#num_of_units}.'''
        result = self._values.get("num_of_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeIntegrationGkeAutoscaleHeadroom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeIntegrationGkeAutoscaleHeadroomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleHeadroomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__94952072df72e3034614f280b408aaeb293bfc386a450c1d8853f675e166abd2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCpuPerUnit")
    def reset_cpu_per_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuPerUnit", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__80f2204d5d798007f16fcb1096c5ba44a8db1a717a59d8addff79cf7d6b24294)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0389f532f5b5b694164c97dcd8c4f010bfa828e09775bd5ab8e4371e135d4363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f644a9dcf7af952fa7678aaef453120edda88a7f190389158e984c29cfa667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleHeadroom]:
        return typing.cast(typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleHeadroom], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleHeadroom],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__948f10dcc120048730a4868117aee00a844ffef8f84fa2a9c2f33360e1846562)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ElastigroupGkeIntegrationGkeAutoscaleLabels:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#key ElastigroupGke#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1d048a6c42208c0565fecd9739fcf8183df025190f4ab7a26ae94e13609c5e8)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#key ElastigroupGke#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeIntegrationGkeAutoscaleLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeIntegrationGkeAutoscaleLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35a04e57750602fb5c20167982a63945dc66e08a341f06ab6c479b32bdebed79)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeIntegrationGkeAutoscaleLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54211e52fdd3a20652332f06b55cecaf8eed67fa0519ec25415555177f71abe7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeIntegrationGkeAutoscaleLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__831b05d788314b7c0ce6eeefb42eda07924eb88e9eb6622b05c235edfad031b8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__173c8a3ef8ed5e54af98dfbc52a4e6d3516fb3e5ac4bd2bac09a8fcc896c3dc8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b950e3dfeb34df4c55884738be69bfa6af74f13e11b35c04d5e55930b90cc53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeIntegrationGkeAutoscaleLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeIntegrationGkeAutoscaleLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeIntegrationGkeAutoscaleLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8b2a8a641e3b8edfc7f768459ea40d3bc3e83dbc273fcaa549c9b363fd38ca5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeIntegrationGkeAutoscaleLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeAutoscaleLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__beb30003be487f99eaa89d661a72f4488a5b39187eceaae048e61cd61304ed6f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea755c27bda2fa15787ed1a70fab6f5aa5a03414b26c51ce56976b6f9de17aa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3165288f8fea94a43f68caa6a5c4105bf475e49ca6ee2e3e2650d02933a4e25a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeIntegrationGkeAutoscaleLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeIntegrationGkeAutoscaleLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeIntegrationGkeAutoscaleLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e415a63848cd5bb01303f62bc9e2595ef4ae82c081327c4bc95cd3f703d83f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeIntegrationGkeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeIntegrationGkeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__643da5dbbc38854540d81cbda928f100896383ed3b62a79702a82a875ecdc00f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAutoscaleDown")
    def put_autoscale_down(
        self,
        *,
        evaluation_periods: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.
        '''
        value = ElastigroupGkeIntegrationGkeAutoscaleDown(
            evaluation_periods=evaluation_periods
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscaleDown", [value]))

    @jsii.member(jsii_name="putAutoscaleHeadroom")
    def put_autoscale_headroom(
        self,
        *,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
        num_of_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cpu_per_unit ElastigroupGke#cpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#memory_per_unit ElastigroupGke#memory_per_unit}.
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#num_of_units ElastigroupGke#num_of_units}.
        '''
        value = ElastigroupGkeIntegrationGkeAutoscaleHeadroom(
            cpu_per_unit=cpu_per_unit,
            memory_per_unit=memory_per_unit,
            num_of_units=num_of_units,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscaleHeadroom", [value]))

    @jsii.member(jsii_name="putAutoscaleLabels")
    def put_autoscale_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeIntegrationGkeAutoscaleLabels, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98f0b9f4632ce6cc7951c7322c12b6ffe86dd22e2dbabb6b14c815bfdeeebe51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoscaleLabels", [value]))

    @jsii.member(jsii_name="resetAutoscaleCooldown")
    def reset_autoscale_cooldown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleCooldown", []))

    @jsii.member(jsii_name="resetAutoscaleDown")
    def reset_autoscale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleDown", []))

    @jsii.member(jsii_name="resetAutoscaleHeadroom")
    def reset_autoscale_headroom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleHeadroom", []))

    @jsii.member(jsii_name="resetAutoscaleIsAutoConfig")
    def reset_autoscale_is_auto_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleIsAutoConfig", []))

    @jsii.member(jsii_name="resetAutoscaleIsEnabled")
    def reset_autoscale_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleIsEnabled", []))

    @jsii.member(jsii_name="resetAutoscaleLabels")
    def reset_autoscale_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleLabels", []))

    @jsii.member(jsii_name="resetAutoUpdate")
    def reset_auto_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoUpdate", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

    @builtins.property
    @jsii.member(jsii_name="autoscaleDown")
    def autoscale_down(
        self,
    ) -> ElastigroupGkeIntegrationGkeAutoscaleDownOutputReference:
        return typing.cast(ElastigroupGkeIntegrationGkeAutoscaleDownOutputReference, jsii.get(self, "autoscaleDown"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroom")
    def autoscale_headroom(
        self,
    ) -> ElastigroupGkeIntegrationGkeAutoscaleHeadroomOutputReference:
        return typing.cast(ElastigroupGkeIntegrationGkeAutoscaleHeadroomOutputReference, jsii.get(self, "autoscaleHeadroom"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleLabels")
    def autoscale_labels(self) -> ElastigroupGkeIntegrationGkeAutoscaleLabelsList:
        return typing.cast(ElastigroupGkeIntegrationGkeAutoscaleLabelsList, jsii.get(self, "autoscaleLabels"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleCooldownInput")
    def autoscale_cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoscaleCooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleDownInput")
    def autoscale_down_input(
        self,
    ) -> typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleDown]:
        return typing.cast(typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleDown], jsii.get(self, "autoscaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomInput")
    def autoscale_headroom_input(
        self,
    ) -> typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleHeadroom]:
        return typing.cast(typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleHeadroom], jsii.get(self, "autoscaleHeadroomInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleIsAutoConfigInput")
    def autoscale_is_auto_config_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoscaleIsAutoConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleIsEnabledInput")
    def autoscale_is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoscaleIsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleLabelsInput")
    def autoscale_labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeIntegrationGkeAutoscaleLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeIntegrationGkeAutoscaleLabels]]], jsii.get(self, "autoscaleLabelsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoUpdateInput")
    def auto_update_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoUpdateInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleCooldown")
    def autoscale_cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoscaleCooldown"))

    @autoscale_cooldown.setter
    def autoscale_cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1e7a4a0bc3b15844620e46a0bd4e3867dae7ac945c08d1c6a2d017fae7df336)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoscaleCooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoscaleIsAutoConfig")
    def autoscale_is_auto_config(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoscaleIsAutoConfig"))

    @autoscale_is_auto_config.setter
    def autoscale_is_auto_config(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3329f0b192135e729b84e75c3ec20c8918335afe4d5a59733195a24d32a31b64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoscaleIsAutoConfig", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__3601a71644331a40ced16189181f05b889c25522827a057ab69f61e030acff96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoscaleIsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoUpdate")
    def auto_update(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoUpdate"))

    @auto_update.setter
    def auto_update(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97793dfd8e31f2c7d6a019b0de7e070ccadd39f4714d15daf7eddaa23b5a22c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoUpdate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dab42e3ad6a1be1e953fbf294fdbb9ddce35e6687403693e62338a147a8ac9fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dae15c233109bf3fc8c8e0f00fe1551082195ab43a1eb5ac0a035e4929f7c89d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupGkeIntegrationGke]:
        return typing.cast(typing.Optional[ElastigroupGkeIntegrationGke], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupGkeIntegrationGke],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bc34444b702c9793f3f012bb6fe19675fd728b64088e99109d655a56ae7db2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ElastigroupGkeLabels:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#key ElastigroupGke#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20db70f4f08b227afb93b01d6c04f2bc14e1a76a517a75281032720d417c273e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#key ElastigroupGke#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3384432382a8cfcc48ac212a87c2dce1a6e5a763e9d30bfc66db2b36afd84a13)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupGkeLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4e150cbfbacc5a03c7005750ca73f9d8827ddd18235b4dd29f0b8ca167f2c95)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35a76858462a919c695924b5320cd4f0b9ee06a674f669458609d9a41b15d6da)
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
            type_hints = typing.get_type_hints(_typecheckingstub__34169c719de4210cc58b2607aa35a1abd5b4870d4f6eea634b44dbc255d5ee16)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cbc70baec436df88177907244fcbec817db09da70f4945572f96b90254fe049d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b083c069d26289dabc32a7f7418cc23f129618dceb9742d9db3a05914c8d96c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__029874497df904074bcd64a467d7720fa177e8e8acbf5761052a057006581cb4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c57e422fa45a83dd75a9ed7ebbe8cd4055b25349d31f61b7e3b201781be6b97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0cc904948236ee379d53956563f2aa0224673918f33c4774757f8e5ba682a4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d9542805919101a8ce166b33274aea221a6102b3be7182dc0338ca24766d1f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeMetadata",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ElastigroupGkeMetadata:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#key ElastigroupGke#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18b456aab87ac60dbe0cbb2aa6803c1cef9dc5141e120a8bd7969d1bb85d2ff0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#key ElastigroupGke#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeMetadataList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeMetadataList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7504515ad0b2e532f13d1fd7536a2d47760737969e16f4e892942793dd864b08)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupGkeMetadataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45270db54e7c5d0cf8bc62351ea73e3de7d2b4607714537e5d87a173a2245bc1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeMetadataOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00da913446148ece73c2b44f3584842c315fa004efebaeaecb37a06f448f397a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c08ec7e6a829e0ed2540c269c43751e79790a0849636907ef887780825e0e87)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9634dead5d9a93dffda33aeff07ebee4e51e654b0350b4153f8bd1bc6479f4d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeMetadata]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeMetadata]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeMetadata]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bf3964db118cb3f10ff4f328d4895462ae2232e04b5bd67a7b8edb624e5ee14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef81421fb57c93c6e4c7e402cd6c599aaa7801088cae04124eea687c6daea70f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09d103727b1ce77b65bd96d15c2495dba7eb0c2290e3b4c582fba35bc452597a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98c58c9e363bc6a983905b54d50ad3735c4ba2b2423153cb42e4a6ba303f4445)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeMetadata]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeMetadata]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeMetadata]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cdabc0b596320586afc67e3226db640fc36e0e0f6434b323f41fd3d2a9835c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterface",
    jsii_struct_bases=[],
    name_mapping={
        "network": "network",
        "access_configs": "accessConfigs",
        "alias_ip_ranges": "aliasIpRanges",
    },
)
class ElastigroupGkeNetworkInterface:
    def __init__(
        self,
        *,
        network: builtins.str,
        access_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeNetworkInterfaceAccessConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        alias_ip_ranges: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeNetworkInterfaceAliasIpRanges", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param network: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#network ElastigroupGke#network}.
        :param access_configs: access_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#access_configs ElastigroupGke#access_configs}
        :param alias_ip_ranges: alias_ip_ranges block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#alias_ip_ranges ElastigroupGke#alias_ip_ranges}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c72ae2642b587a97083417bcecd6c63f6baa26e8e6aade1db691f101973baa8)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument access_configs", value=access_configs, expected_type=type_hints["access_configs"])
            check_type(argname="argument alias_ip_ranges", value=alias_ip_ranges, expected_type=type_hints["alias_ip_ranges"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network": network,
        }
        if access_configs is not None:
            self._values["access_configs"] = access_configs
        if alias_ip_ranges is not None:
            self._values["alias_ip_ranges"] = alias_ip_ranges

    @builtins.property
    def network(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#network ElastigroupGke#network}.'''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_configs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterfaceAccessConfigs"]]]:
        '''access_configs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#access_configs ElastigroupGke#access_configs}
        '''
        result = self._values.get("access_configs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterfaceAccessConfigs"]]], result)

    @builtins.property
    def alias_ip_ranges(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterfaceAliasIpRanges"]]]:
        '''alias_ip_ranges block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#alias_ip_ranges ElastigroupGke#alias_ip_ranges}
        '''
        result = self._values.get("alias_ip_ranges")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeNetworkInterfaceAliasIpRanges"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceAccessConfigs",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class ElastigroupGkeNetworkInterfaceAccessConfigs:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#type ElastigroupGke#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31d28cc0696f7f12b5c7ea190d537f110db5a3a2afd375dd57da5ce9fa14792e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#type ElastigroupGke#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeNetworkInterfaceAccessConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeNetworkInterfaceAccessConfigsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceAccessConfigsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5773f422effd8fc481b0ccf87aef61f04e592bfc01202239e8d6d4bc5877e2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeNetworkInterfaceAccessConfigsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f69e404de019bd2991711ec348662f221eeb570cbaf2bc08511bace3a880ebae)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeNetworkInterfaceAccessConfigsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ebd56a76be03b6ce7e66eb68afbf556fc5a65f36534dfc09aa209a63e3f3d32)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f9050021046015468d0a68bab4c27d0af696fee4f1f8c53f1e912652e9e13408)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d42d67d13d362c552b7f90f0a94413a9e48c61e76922ae9f33e6a71785f334d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAccessConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAccessConfigs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAccessConfigs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c0bdb4ebac1979340e22d165d821f427a5ef40297f26f4fc3ab69cbdeabb7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeNetworkInterfaceAccessConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceAccessConfigsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__523de1df57e219198c7009590c8df531478d9cae364613d0ca5ecd6cc20ad56b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7767e75fef1c2bd0e61ffe9e5b4db850b210f1e4e404ba2d9ce46d1dfc5c162e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b071650259374db66dd1c15c939b418b0faf30005b2476f08d2a37da7cbee0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAccessConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAccessConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAccessConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b96b56bbd289d2308fef55653d5dc9391a1954aa4f67dc3aa74eff9e9a552b75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceAliasIpRanges",
    jsii_struct_bases=[],
    name_mapping={
        "ip_cidr_range": "ipCidrRange",
        "subnetwork_range_name": "subnetworkRangeName",
    },
)
class ElastigroupGkeNetworkInterfaceAliasIpRanges:
    def __init__(
        self,
        *,
        ip_cidr_range: builtins.str,
        subnetwork_range_name: builtins.str,
    ) -> None:
        '''
        :param ip_cidr_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ip_cidr_range ElastigroupGke#ip_cidr_range}.
        :param subnetwork_range_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#subnetwork_range_name ElastigroupGke#subnetwork_range_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb658ae91cb001c505d5c4498dd99ca24b8a61e01e50aa6cfcef87aaa44c9d4f)
            check_type(argname="argument ip_cidr_range", value=ip_cidr_range, expected_type=type_hints["ip_cidr_range"])
            check_type(argname="argument subnetwork_range_name", value=subnetwork_range_name, expected_type=type_hints["subnetwork_range_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip_cidr_range": ip_cidr_range,
            "subnetwork_range_name": subnetwork_range_name,
        }

    @builtins.property
    def ip_cidr_range(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#ip_cidr_range ElastigroupGke#ip_cidr_range}.'''
        result = self._values.get("ip_cidr_range")
        assert result is not None, "Required property 'ip_cidr_range' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnetwork_range_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#subnetwork_range_name ElastigroupGke#subnetwork_range_name}.'''
        result = self._values.get("subnetwork_range_name")
        assert result is not None, "Required property 'subnetwork_range_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeNetworkInterfaceAliasIpRanges(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeNetworkInterfaceAliasIpRangesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceAliasIpRangesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d958144e7766712525d94ca0f8ef3afc3620b37b57eee912268019ab73de3ee7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeNetworkInterfaceAliasIpRangesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b80d81fdc13d27dba85a7c643f68246f9b1818ac480a2f22c22e5f2e2ed5934e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeNetworkInterfaceAliasIpRangesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f07e3ccc1d47a388d4eee3274de28ef46439f0fb666f1c09f8d5cf90eea5fe6b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6229aebfb12be1bda0bf528731a823c2fda9dd4239a4ae8f29d1d904a775b00b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a614bf35b07374625745377dc8a44ece36aa30afa22127485e1c12ac19a134f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAliasIpRanges]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAliasIpRanges]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAliasIpRanges]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9183865c3cdd1d6e74abff877e2027f4965df2acf507dd64413a952e39a9eccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeNetworkInterfaceAliasIpRangesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceAliasIpRangesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8169af25e4e0786cb52c67a0c5c9ac6c276822187286fd37883012c552554fdb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="ipCidrRangeInput")
    def ip_cidr_range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipCidrRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetworkRangeNameInput")
    def subnetwork_range_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetworkRangeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ipCidrRange")
    def ip_cidr_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipCidrRange"))

    @ip_cidr_range.setter
    def ip_cidr_range(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd8556a0945772e826713d3ecf5d177cb2a6d14d1368509169c112f3744da37d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipCidrRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetworkRangeName")
    def subnetwork_range_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetworkRangeName"))

    @subnetwork_range_name.setter
    def subnetwork_range_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a544a065e1e08fa8b3b61ff7b67a9289345c4d8fc48af6cb1ffc1a2c9b9f1102)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetworkRangeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAliasIpRanges]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAliasIpRanges]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAliasIpRanges]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1ec4794b129a1f5de633cab063cbc286c9d9184b7dd982ea71db3e5eeec098d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeNetworkInterfaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c4cd359daeace419d5d772783f314ac0ce5df9ef3477bd2b8ae3caa8df11467)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeNetworkInterfaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__590a38c3157af93d07bc665771421ce86586679c8e29149e92a887f1cf6ca9f8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeNetworkInterfaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31f1d412f36ffa16de110c55e160b8c5deae2e8c434352d180e538731ccc6aba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7000f402c1ecc8fb3fb881d34c53ae29a2ceaab52e2437e06e7a3c0d4fe0534f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ddd634aba30a61d775558dfae47e1a72e29300cd51447ba9c11f1d50bb0c590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterface]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterface]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e72141018726c8b6cb19aedeae3ba162a2130e2f261e4fdea82a8cc6a57e488b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeNetworkInterfaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeNetworkInterfaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb00f47ca5cfa042f6cb109eee35b4ecc3710ae04d43059fdd2bba01bcc88d89)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAccessConfigs")
    def put_access_configs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterfaceAccessConfigs, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__631feea653e27a99c7c0463e49e5c11526208bd5d03cace05a780f6fcf9d39e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAccessConfigs", [value]))

    @jsii.member(jsii_name="putAliasIpRanges")
    def put_alias_ip_ranges(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterfaceAliasIpRanges, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543ab2f6328f5fb91294ef1dc20b8c6f94b80d31559136e1cf6be8d9946b5be7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAliasIpRanges", [value]))

    @jsii.member(jsii_name="resetAccessConfigs")
    def reset_access_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessConfigs", []))

    @jsii.member(jsii_name="resetAliasIpRanges")
    def reset_alias_ip_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasIpRanges", []))

    @builtins.property
    @jsii.member(jsii_name="accessConfigs")
    def access_configs(self) -> ElastigroupGkeNetworkInterfaceAccessConfigsList:
        return typing.cast(ElastigroupGkeNetworkInterfaceAccessConfigsList, jsii.get(self, "accessConfigs"))

    @builtins.property
    @jsii.member(jsii_name="aliasIpRanges")
    def alias_ip_ranges(self) -> ElastigroupGkeNetworkInterfaceAliasIpRangesList:
        return typing.cast(ElastigroupGkeNetworkInterfaceAliasIpRangesList, jsii.get(self, "aliasIpRanges"))

    @builtins.property
    @jsii.member(jsii_name="accessConfigsInput")
    def access_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAccessConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAccessConfigs]]], jsii.get(self, "accessConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasIpRangesInput")
    def alias_ip_ranges_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAliasIpRanges]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAliasIpRanges]]], jsii.get(self, "aliasIpRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d5cd8964d49377c7718e502c38d1c9f265e79ef02f3fcbb83a6a7e9a7e5608)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterface]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterface]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterface]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc39e559f6882de450545f30b164848b436988566b461e8dbd8a9a039c4fc0e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeRevertToPreemptible",
    jsii_struct_bases=[],
    name_mapping={"perform_at": "performAt"},
)
class ElastigroupGkeRevertToPreemptible:
    def __init__(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#perform_at ElastigroupGke#perform_at}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__043062ed5f2065e449ab8026959fda340620f0bcee74ef9ced3dd91305031ef6)
            check_type(argname="argument perform_at", value=perform_at, expected_type=type_hints["perform_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "perform_at": perform_at,
        }

    @builtins.property
    def perform_at(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#perform_at ElastigroupGke#perform_at}.'''
        result = self._values.get("perform_at")
        assert result is not None, "Required property 'perform_at' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeRevertToPreemptible(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeRevertToPreemptibleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeRevertToPreemptibleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__16d28bf35c5d8e7fce7d3b2fddd3523e24ee924dc7a4c9fdd70114dead55105d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeRevertToPreemptibleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08e9c8d909c0fbf552bfccf24a253706425d2f6c96288bf77934e6f901617c99)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeRevertToPreemptibleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9845716c1052b7e640ea5b2c5cc37a563c21fcb7c3d57ceb754b3b2a33c638c1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31fa9ff20abf94abe0fdbedc90b4c29f1966b76415baa75161cd5f0b6c5b6aa3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__daa72a013fb434f269ba4c29ac8baf0f52adf6f431b903e9e04fe5ed12e97fcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeRevertToPreemptible]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeRevertToPreemptible]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeRevertToPreemptible]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c05500b164d0950a1dc49da33f1d3b3e9d1fbc911732d9e9b80c0e9bceaf673)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeRevertToPreemptibleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeRevertToPreemptibleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__13a700d36e5863913a5f839cd05a970b8b5e4875eca71f06832be3ef39d7b05a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="performAtInput")
    def perform_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "performAtInput"))

    @builtins.property
    @jsii.member(jsii_name="performAt")
    def perform_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "performAt"))

    @perform_at.setter
    def perform_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cfc56c0ca161801f1172ea23ceb6934b09e9ba33db019bdcadda9fb15deb71f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeRevertToPreemptible]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeRevertToPreemptible]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeRevertToPreemptible]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__122a020bd5e5fdc14870bae5f08f3247a444dd95694d067959b454f8799e1d54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingDownPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "namespace": "namespace",
        "policy_name": "policyName",
        "threshold": "threshold",
        "unit": "unit",
        "action_type": "actionType",
        "adjustment": "adjustment",
        "cooldown": "cooldown",
        "dimensions": "dimensions",
        "evaluation_periods": "evaluationPeriods",
        "operator": "operator",
        "period": "period",
        "source": "source",
        "statistic": "statistic",
    },
)
class ElastigroupGkeScalingDownPolicy:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        policy_name: builtins.str,
        threshold: jsii.Number,
        unit: builtins.str,
        action_type: typing.Optional[builtins.str] = None,
        adjustment: typing.Optional[jsii.Number] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingDownPolicyDimensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        source: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metric_name ElastigroupGke#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#namespace ElastigroupGke#namespace}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#policy_name ElastigroupGke#policy_name}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#threshold ElastigroupGke#threshold}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#unit ElastigroupGke#unit}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#action_type ElastigroupGke#action_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#adjustment ElastigroupGke#adjustment}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cooldown ElastigroupGke#cooldown}.
        :param dimensions: dimensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#dimensions ElastigroupGke#dimensions}
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#operator ElastigroupGke#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#period ElastigroupGke#period}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source ElastigroupGke#source}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#statistic ElastigroupGke#statistic}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c345a9125cb765319f4962fec4de80f219e2d40162c011a22796626456eba77c)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument action_type", value=action_type, expected_type=type_hints["action_type"])
            check_type(argname="argument adjustment", value=adjustment, expected_type=type_hints["adjustment"])
            check_type(argname="argument cooldown", value=cooldown, expected_type=type_hints["cooldown"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_name": metric_name,
            "namespace": namespace,
            "policy_name": policy_name,
            "threshold": threshold,
            "unit": unit,
        }
        if action_type is not None:
            self._values["action_type"] = action_type
        if adjustment is not None:
            self._values["adjustment"] = adjustment
        if cooldown is not None:
            self._values["cooldown"] = cooldown
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if source is not None:
            self._values["source"] = source
        if statistic is not None:
            self._values["statistic"] = statistic

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metric_name ElastigroupGke#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#namespace ElastigroupGke#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#policy_name ElastigroupGke#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#threshold ElastigroupGke#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#unit ElastigroupGke#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#action_type ElastigroupGke#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#adjustment ElastigroupGke#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cooldown ElastigroupGke#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingDownPolicyDimensions"]]]:
        '''dimensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#dimensions ElastigroupGke#dimensions}
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingDownPolicyDimensions"]]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#operator ElastigroupGke#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#period ElastigroupGke#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source ElastigroupGke#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#statistic ElastigroupGke#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeScalingDownPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingDownPolicyDimensions",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ElastigroupGkeScalingDownPolicyDimensions:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dda8f70f98764ec64688f07704b7e6dc002285d42ac4c6d6c86d7c5487b6f439)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeScalingDownPolicyDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeScalingDownPolicyDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingDownPolicyDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee6273db138c1d03a3a7234d585e889fbb85e123c80f1e583d72ff7bc19bf289)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeScalingDownPolicyDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82a9eecfd1981671b2959c564268d90cc022cddc4d3db327c623ed8beba5f9f4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeScalingDownPolicyDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f70aa170537676341d588623c706ea0dc32086b412a3ca70c9adb5f99bc84673)
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
            type_hints = typing.get_type_hints(_typecheckingstub__40388bf23b492f9dd5a609e0e85bda804a7b2285ce9d0b516f3112a3d700762a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__234b91066480159c6ac424bd17594c78d604ee0d7114e363afe20c8e5cb0901d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicyDimensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicyDimensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0d6234af8f86b2e409dcf2c16ba7da6a2256845679701851b1935b11384d0e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeScalingDownPolicyDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingDownPolicyDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__801c0e6db1a83abf7207d1a453268502edfa74425a4bad6d870101b780b4f576)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb8ec0472327c12c12e36990c8adb1a672ab6a5e81aca2d42d77fa93185407f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72ac91f986aae8164bec2809b755772c1e95bbda7bab3723d46fc4017fc1dfb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicyDimensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicyDimensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicyDimensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dd899550ea8be69699fd1a15110b292498f953217da4921d4e7e0e1bf97429b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeScalingDownPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingDownPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6483731ba19c622415c0b2a917bad011b8b92c282cd27227b67402b51e2f35b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeScalingDownPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6892998a66cc6499edb98394f20c57f82e5062bb93b11add3d20eec0a5f97ead)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeScalingDownPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1aff10aa0049f8decc5809ba253097e961f33228deae057feb8b977bca8fef8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d3debe840093b67e8e916189160bd0e9f3c2fa11a96f86ebe47d2572aeafe1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8a912ec93d7b178a3c02e415e323a762c6f94af331d4fe0b0c4953009a8a0d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1904c4156459b2b2def523e765d08f77eeaff93f3cb7c1b1c2b8c15a950f59c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeScalingDownPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingDownPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a0496f8912951084574d300677af8cbc772482cb8b7f12648432a18db9e7363)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDimensions")
    def put_dimensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingDownPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41cc73b8c8f27d5207cf924baa6f652e57b2d9816e1804d61df799bade1d559f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimensions", [value]))

    @jsii.member(jsii_name="resetActionType")
    def reset_action_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionType", []))

    @jsii.member(jsii_name="resetAdjustment")
    def reset_adjustment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdjustment", []))

    @jsii.member(jsii_name="resetCooldown")
    def reset_cooldown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldown", []))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetEvaluationPeriods")
    def reset_evaluation_periods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluationPeriods", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> ElastigroupGkeScalingDownPolicyDimensionsList:
        return typing.cast(ElastigroupGkeScalingDownPolicyDimensionsList, jsii.get(self, "dimensions"))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicyDimensions]]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "periodInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property
    @jsii.member(jsii_name="actionType")
    def action_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionType"))

    @action_type.setter
    def action_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6e7eff3ce63c714332488d01c441a39819c82495a8245c9844d49b2d8c38587)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a00091bcb833cb4e65bbd5cba74d77e4ef3df67aee4ae8c0a562815069374f91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4a64914df22eb959b8a9d94513869801cd5e81293b83dd28fa8ba25327ed42a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27bc449a0ff854a8dc09657e62d01bfd543c80d0b27286a0977d9adb7e18a619)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b9c117980c6e4feccff71c49541e18f310a4565bc6aa277c0f49317857970cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c8e40bb3f12fdee4435d9f2a270be64197549119d9aac6687234be969d9520d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f6f2a76a320c649fef7dfcb8d99ffa944b23d5ecb0b60410d6a1880670fd823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21cbf87c07a404424e596ce2d1cbbcec1ecb06d92c8be9e101db5b9f2794031b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b092ad91f38c3b51b2b07e9f1b0c0e5eb9fa54db624d2403a141937c8d7eca64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17d385ce1d6387002b0775b56e5b3bd6fac61271c2d67bbff60325e240193389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02bfd83da31ea2de59f08f81feadb4f68f235342ec5d94faeb4c3979d70e19fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c201c8af0affa97ff044b42bb312c4bedcd7e2d599e3ae1e5cc6809a0598508d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffcc90e3848da3424fa3c3b114e0c11a0fae86649ee42bfdf80ec2e7d32e6802)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c059024e0e361d95c0da604af9541da83e6df201197a49779b8d3bb99ac16ec1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingUpPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "namespace": "namespace",
        "policy_name": "policyName",
        "threshold": "threshold",
        "unit": "unit",
        "action_type": "actionType",
        "adjustment": "adjustment",
        "cooldown": "cooldown",
        "dimensions": "dimensions",
        "evaluation_periods": "evaluationPeriods",
        "operator": "operator",
        "period": "period",
        "source": "source",
        "statistic": "statistic",
    },
)
class ElastigroupGkeScalingUpPolicy:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        policy_name: builtins.str,
        threshold: jsii.Number,
        unit: builtins.str,
        action_type: typing.Optional[builtins.str] = None,
        adjustment: typing.Optional[jsii.Number] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupGkeScalingUpPolicyDimensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        source: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metric_name ElastigroupGke#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#namespace ElastigroupGke#namespace}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#policy_name ElastigroupGke#policy_name}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#threshold ElastigroupGke#threshold}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#unit ElastigroupGke#unit}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#action_type ElastigroupGke#action_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#adjustment ElastigroupGke#adjustment}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cooldown ElastigroupGke#cooldown}.
        :param dimensions: dimensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#dimensions ElastigroupGke#dimensions}
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#operator ElastigroupGke#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#period ElastigroupGke#period}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source ElastigroupGke#source}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#statistic ElastigroupGke#statistic}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__452803770fdd4ae4167c27496e294a6b5eb2f70848e545ed431ebe45bbc6e351)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument action_type", value=action_type, expected_type=type_hints["action_type"])
            check_type(argname="argument adjustment", value=adjustment, expected_type=type_hints["adjustment"])
            check_type(argname="argument cooldown", value=cooldown, expected_type=type_hints["cooldown"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_name": metric_name,
            "namespace": namespace,
            "policy_name": policy_name,
            "threshold": threshold,
            "unit": unit,
        }
        if action_type is not None:
            self._values["action_type"] = action_type
        if adjustment is not None:
            self._values["adjustment"] = adjustment
        if cooldown is not None:
            self._values["cooldown"] = cooldown
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if source is not None:
            self._values["source"] = source
        if statistic is not None:
            self._values["statistic"] = statistic

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#metric_name ElastigroupGke#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#namespace ElastigroupGke#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#policy_name ElastigroupGke#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#threshold ElastigroupGke#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#unit ElastigroupGke#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#action_type ElastigroupGke#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#adjustment ElastigroupGke#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#cooldown ElastigroupGke#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingUpPolicyDimensions"]]]:
        '''dimensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#dimensions ElastigroupGke#dimensions}
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupGkeScalingUpPolicyDimensions"]]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#evaluation_periods ElastigroupGke#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#operator ElastigroupGke#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#period ElastigroupGke#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#source ElastigroupGke#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#statistic ElastigroupGke#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeScalingUpPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingUpPolicyDimensions",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ElastigroupGkeScalingUpPolicyDimensions:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b5519b569e3d44b15a9b06846fb9476f30e95c8ff6e2fa6f3c7067001b2f135)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#name ElastigroupGke#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#value ElastigroupGke#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeScalingUpPolicyDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeScalingUpPolicyDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingUpPolicyDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40ff71cc657d64aa2a1fd852c73a15d90d536f359e5f3421e55012138795e1ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupGkeScalingUpPolicyDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca677c7fcfe28fd7b251f1515c2c9a38872a22f4f60538884e60c0e063d8a0f4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeScalingUpPolicyDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac897fcce30af75c6eb23dcd51ac6f0f8b26548ca2f647c70256178b09cc9ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c384f71016e37da1d9eebab805f9c60d2639733572067b8c685aa7bdefd0421)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16c912faabd06547b3ecdc61fa9807f264d19701467510f8fc768df7494f738d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicyDimensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicyDimensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e77e95b3bbf013bb5004609a3e6522a85e6f21db611516edccd186b9e1a97fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeScalingUpPolicyDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingUpPolicyDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ddbbf675a2b5e895be5bda42eb4726ca148f65b2b5543363bb2696c4e05d7bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f6b3ba315d753971663749cf27a95326c8013a9046690f0409a284003457050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90810e250ae83f41f10686c5e3d988f781b08ae4e911cb2e6fb3a52494cb6a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicyDimensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicyDimensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicyDimensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d758690ab32a571f1e70ee4453cb65b8a452c07c08bad3b8756caf34d3be2cef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeScalingUpPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingUpPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67343862ec4d263cba13a4cb49770f9814740c96e39c9b9038005548450ded79)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupGkeScalingUpPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99af64b8bf243469121a786b86c17010f4065ff1cdc3ce2f9c2889adb6a9456e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupGkeScalingUpPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c8f74cb918ece298db7fd335b58841b6e382e8233223aa7c2705e2994091c38)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d88c7fb634f40d71c8ba86352cf9c68d12cb10a08dd67173b26ec4c1d267295)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3516dc241fb5cacce0e4092bfc6becf7b1e1f43b785281dd2355201da24624a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99efe48ef2491320ec1653029130d447e64249af557f813cda39c4216c73ef3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupGkeScalingUpPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeScalingUpPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7c8041f840554a4dd4663946753c9f005ebf1585b37ea5629f2d71caf7558e5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDimensions")
    def put_dimensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingUpPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__491558ff1eff61b83b2aac0800e4d6e9d1c4b9c45ad9fdc4888a8dc947a20f85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimensions", [value]))

    @jsii.member(jsii_name="resetActionType")
    def reset_action_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionType", []))

    @jsii.member(jsii_name="resetAdjustment")
    def reset_adjustment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdjustment", []))

    @jsii.member(jsii_name="resetCooldown")
    def reset_cooldown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldown", []))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetEvaluationPeriods")
    def reset_evaluation_periods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluationPeriods", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> ElastigroupGkeScalingUpPolicyDimensionsList:
        return typing.cast(ElastigroupGkeScalingUpPolicyDimensionsList, jsii.get(self, "dimensions"))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicyDimensions]]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "periodInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property
    @jsii.member(jsii_name="actionType")
    def action_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionType"))

    @action_type.setter
    def action_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c532f5d75503a425f09e555f9c86f0252b8924ff023ef38f5da6899a388bf0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bfbe4a79175005a4370db9821375c6493643e133d4821c7dd664ec0a6b4c52f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ca69d71f31c208ecad2be8e71050b881d00937c4ef1e7ea6a01832a2de55d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3219fd74caff21c6501772284a5f3e1b4ca1baf17491680e91928915e008d452)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__695e9534f2c41a2691425a069bb36942ce753b0db189f7c7b3a4b95c8720c6dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81e9a284a77ec35e9fd3e43614ae7e59d5f5532258234acb5eee20037306f34a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1813288d3c3ce5a321bf863d27cb52d2ab37e5915038f8007b68e3af4e0b7ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a23482357e8c5a8ef6d24f70c92c4d58a2014dd2c0afe60aafdb6586d211ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fb8c41fad594c51c7b9024b28aad8fcefabdf1829ce83dd6519be595b3c0917)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21a9635003eaf98b7409906c714d4946bf3bddff45d2ca2d090df1c406e72982)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3708e0603f2cc8a7807e10ee276d89a52099b4cf91cb9aa5448b6dfb74b480eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef0259d5a34725a974a28fb1b29391fad79592040185a2fbdf3ebe4b6f3f4f38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60112b469ef222d123c20215314f95565d18869e890625d27fb9056183f4aabc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02f3aea956b32dd1b5e2bc57fae710b9bb0ef3d6a63e169ed71a08dc734152d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeShieldedInstanceConfig",
    jsii_struct_bases=[],
    name_mapping={
        "enable_integrity_monitoring": "enableIntegrityMonitoring",
        "enable_secure_boot": "enableSecureBoot",
    },
)
class ElastigroupGkeShieldedInstanceConfig:
    def __init__(
        self,
        *,
        enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enable_integrity_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#enable_integrity_monitoring ElastigroupGke#enable_integrity_monitoring}.
        :param enable_secure_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#enable_secure_boot ElastigroupGke#enable_secure_boot}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__806c18609fce6b99f485ca7c06fe45873221d1998048ebb63c6d71c89ed11537)
            check_type(argname="argument enable_integrity_monitoring", value=enable_integrity_monitoring, expected_type=type_hints["enable_integrity_monitoring"])
            check_type(argname="argument enable_secure_boot", value=enable_secure_boot, expected_type=type_hints["enable_secure_boot"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enable_integrity_monitoring is not None:
            self._values["enable_integrity_monitoring"] = enable_integrity_monitoring
        if enable_secure_boot is not None:
            self._values["enable_secure_boot"] = enable_secure_boot

    @builtins.property
    def enable_integrity_monitoring(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#enable_integrity_monitoring ElastigroupGke#enable_integrity_monitoring}.'''
        result = self._values.get("enable_integrity_monitoring")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_secure_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_gke#enable_secure_boot ElastigroupGke#enable_secure_boot}.'''
        result = self._values.get("enable_secure_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupGkeShieldedInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupGkeShieldedInstanceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupGke.ElastigroupGkeShieldedInstanceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86b251911a3e4bda166cf1764f30db5ddcab62f5183973bdb1352815d7113c14)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnableIntegrityMonitoring")
    def reset_enable_integrity_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableIntegrityMonitoring", []))

    @jsii.member(jsii_name="resetEnableSecureBoot")
    def reset_enable_secure_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSecureBoot", []))

    @builtins.property
    @jsii.member(jsii_name="enableIntegrityMonitoringInput")
    def enable_integrity_monitoring_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableIntegrityMonitoringInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSecureBootInput")
    def enable_secure_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSecureBootInput"))

    @builtins.property
    @jsii.member(jsii_name="enableIntegrityMonitoring")
    def enable_integrity_monitoring(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableIntegrityMonitoring"))

    @enable_integrity_monitoring.setter
    def enable_integrity_monitoring(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5f0ba568ada46c5f0b7ab22844c7290724a47948f8736f2b4792b891beeed91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableIntegrityMonitoring", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSecureBoot")
    def enable_secure_boot(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSecureBoot"))

    @enable_secure_boot.setter
    def enable_secure_boot(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55af1008dc8dd8f74d2826e9eb15e27b279588222483afa3d1844c4a2d56b965)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSecureBoot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupGkeShieldedInstanceConfig]:
        return typing.cast(typing.Optional[ElastigroupGkeShieldedInstanceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupGkeShieldedInstanceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf83952a06f4c4ee2036ef63968460ce5dbfe2b38bd7bc7bdcb48f8e78cd78b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ElastigroupGke",
    "ElastigroupGkeBackendServices",
    "ElastigroupGkeBackendServicesBackendBalancing",
    "ElastigroupGkeBackendServicesBackendBalancingOutputReference",
    "ElastigroupGkeBackendServicesList",
    "ElastigroupGkeBackendServicesNamedPorts",
    "ElastigroupGkeBackendServicesNamedPortsList",
    "ElastigroupGkeBackendServicesNamedPortsOutputReference",
    "ElastigroupGkeBackendServicesOutputReference",
    "ElastigroupGkeConfig",
    "ElastigroupGkeDisk",
    "ElastigroupGkeDiskInitializeParams",
    "ElastigroupGkeDiskInitializeParamsList",
    "ElastigroupGkeDiskInitializeParamsOutputReference",
    "ElastigroupGkeDiskList",
    "ElastigroupGkeDiskOutputReference",
    "ElastigroupGkeGpu",
    "ElastigroupGkeGpuList",
    "ElastigroupGkeGpuOutputReference",
    "ElastigroupGkeInstanceTypesCustom",
    "ElastigroupGkeInstanceTypesCustomList",
    "ElastigroupGkeInstanceTypesCustomOutputReference",
    "ElastigroupGkeIntegrationDockerSwarm",
    "ElastigroupGkeIntegrationDockerSwarmOutputReference",
    "ElastigroupGkeIntegrationGke",
    "ElastigroupGkeIntegrationGkeAutoscaleDown",
    "ElastigroupGkeIntegrationGkeAutoscaleDownOutputReference",
    "ElastigroupGkeIntegrationGkeAutoscaleHeadroom",
    "ElastigroupGkeIntegrationGkeAutoscaleHeadroomOutputReference",
    "ElastigroupGkeIntegrationGkeAutoscaleLabels",
    "ElastigroupGkeIntegrationGkeAutoscaleLabelsList",
    "ElastigroupGkeIntegrationGkeAutoscaleLabelsOutputReference",
    "ElastigroupGkeIntegrationGkeOutputReference",
    "ElastigroupGkeLabels",
    "ElastigroupGkeLabelsList",
    "ElastigroupGkeLabelsOutputReference",
    "ElastigroupGkeMetadata",
    "ElastigroupGkeMetadataList",
    "ElastigroupGkeMetadataOutputReference",
    "ElastigroupGkeNetworkInterface",
    "ElastigroupGkeNetworkInterfaceAccessConfigs",
    "ElastigroupGkeNetworkInterfaceAccessConfigsList",
    "ElastigroupGkeNetworkInterfaceAccessConfigsOutputReference",
    "ElastigroupGkeNetworkInterfaceAliasIpRanges",
    "ElastigroupGkeNetworkInterfaceAliasIpRangesList",
    "ElastigroupGkeNetworkInterfaceAliasIpRangesOutputReference",
    "ElastigroupGkeNetworkInterfaceList",
    "ElastigroupGkeNetworkInterfaceOutputReference",
    "ElastigroupGkeRevertToPreemptible",
    "ElastigroupGkeRevertToPreemptibleList",
    "ElastigroupGkeRevertToPreemptibleOutputReference",
    "ElastigroupGkeScalingDownPolicy",
    "ElastigroupGkeScalingDownPolicyDimensions",
    "ElastigroupGkeScalingDownPolicyDimensionsList",
    "ElastigroupGkeScalingDownPolicyDimensionsOutputReference",
    "ElastigroupGkeScalingDownPolicyList",
    "ElastigroupGkeScalingDownPolicyOutputReference",
    "ElastigroupGkeScalingUpPolicy",
    "ElastigroupGkeScalingUpPolicyDimensions",
    "ElastigroupGkeScalingUpPolicyDimensionsList",
    "ElastigroupGkeScalingUpPolicyDimensionsOutputReference",
    "ElastigroupGkeScalingUpPolicyList",
    "ElastigroupGkeScalingUpPolicyOutputReference",
    "ElastigroupGkeShieldedInstanceConfig",
    "ElastigroupGkeShieldedInstanceConfigOutputReference",
]

publication.publish()

def _typecheckingstub__13ab72032d7eb2efff6d0fe7d3c446e32344fb0b12cea79683d6ded1f2d5a8ba(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_zone_name: builtins.str,
    desired_capacity: jsii.Number,
    name: builtins.str,
    backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gpu: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeGpu, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_name_prefix: typing.Optional[builtins.str] = None,
    instance_types_custom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeInstanceTypesCustom, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_types_ondemand: typing.Optional[builtins.str] = None,
    instance_types_preemptible: typing.Optional[typing.Sequence[builtins.str]] = None,
    integration_docker_swarm: typing.Optional[typing.Union[ElastigroupGkeIntegrationDockerSwarm, typing.Dict[builtins.str, typing.Any]]] = None,
    integration_gke: typing.Optional[typing.Union[ElastigroupGkeIntegrationGke, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeMetadata, typing.Dict[builtins.str, typing.Any]]]]] = None,
    min_cpu_platform: typing.Optional[builtins.str] = None,
    min_size: typing.Optional[jsii.Number] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    node_image: typing.Optional[builtins.str] = None,
    ondemand_count: typing.Optional[jsii.Number] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    preemptible_percentage: typing.Optional[jsii.Number] = None,
    provisioning_model: typing.Optional[builtins.str] = None,
    revert_to_preemptible: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeRevertToPreemptible, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_account: typing.Optional[builtins.str] = None,
    shielded_instance_config: typing.Optional[typing.Union[ElastigroupGkeShieldedInstanceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    should_utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    startup_script: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__83877478f2df8be7519a1bab89f86e6f6e1e02642852324aa8dc1d6ba8271c22(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a735eb945ab54c178a07c47a53e734c607308143ea2773d33cb6e6782746ff(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServices, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0566651a74216b0e2b4854d92d6a5ebd2a9e5cbbbb4629ad6ab31fe0e9949be(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeDisk, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e0dcd985d8b39fedcd97baa1d9258f3f1f062fdebec6735a46c0d8f22c5bf76(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeGpu, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__881dcb7c86b2de5055cf5564f776d3af2ec9a57ca797eb743c6cefdd75e22dd7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeInstanceTypesCustom, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cca2b2e03a5b1ddd2de25438630e79da8fc522a68a344f2b818dae5b7d2364fe(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3a161565c7015f1e31caaa789162b310c36e58b4e7001c0779c74ad72f05a4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeMetadata, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8767c039d8f7af36e234e8a12f6330f641ca07386b1b27020e5d4c7a3beb9b62(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e40e9ee22daad5158993dc5a7607436f297912eeadc4385fd795ad3db1ddb06e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeRevertToPreemptible, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13f49123044c5abc566fb835add9231ed8f77f37bdeff9b7c8cce93e9d16d322(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__250c472f6750b0fdfa9d6233d71dfc0e0d71002d51a1dd9d3a812838e471de53(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e23124c9930b9b9cb5e15a9053b734cf1e6ab7625eaa5b5c6bea0f5755a204e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd28c88b9990fcf62d7672ccfd54cd64af0cab83fc0c3b454e07662f9247e402(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__373d857b071d02af2ecfb33f2430857e2892b8e7cf87928cc72ce068e7320380(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb1a38ab76d91769af3c006b2b61bdc527003003085eaa6b5e82682a32a8694d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72c17147a465aa9f7b89e235776b7ff1e83bfa197cd045a895bdbd91bfa4e92c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1c979f67d0a34c4dbe767798e23ba71f62b95917705686a635d203649463870(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d4f7f6389053b6787eb9f6b7b95c593d0e3f62b3e277f8c21a7b144e8c725a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100eef8a5810d7314e8037906ec5b4195ef872590339f7bf38c6b3f2bb4e35ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98386d6c63f91e21ec0ae2cf00f9fedfc4cfa9bdd8a849bc6d501ae9c562e47(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32f61fb510fca2f4ca48ddde520d47b5181a2b10bd80712e5c0efd26e9efa7a7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5571a192eca21c2201e874aaac426085b2b605b5b00ec3ea14fc7042470e68(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a9d5aaa867b3f78394bbe1ffe0160491cbcb332c53bc4772aa566413eb6331d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__559d15bced24aeef490be2d90e750a8bb8edeb9c0737b70080330636102e0259(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d9c7021402af527195d4da21feeda98a520a3082d653dbd8d9477a18b685e28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38f798856894c823cca1a8a36c0e51e944de61813b105dd73486a9ec5bded2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f82d4b353339b325731a42c3184220ed4a0ffa5c45329730c18e01276da1bd4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__617e0c41c0286daeb42f6f886b18e50d3249ce38105f8cc85a2f5f134c68c4ad(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce1f98451b50572f9da937af37e4c7cd3d5eba7c53bd317bc8f967f18572381f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__765750ac2dadcf17746ce6bedbe317f6988db8c4936335277c1dfeb58d5ae6f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb90639fa6b754183b2fc5a7600156cc967008fb821e6fa1e1f357504a7a5005(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baa7bb12b86f73468a9e80505d7bc3896c93a392bc81493b7e1cde14701a779a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0eafca9f79e518319de43e2efd86cebc92dd54ebfeed37ddce6ff50943e270a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d85592f381c5e34ac389b6e559db9fe9755afe05099835c58f17a959bb7545(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d766467ec63a7c5f8d0fe801c56eaa3bbfe1673a66857b7457d15b533874b8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55f5eb709ab8e9fa433ec35dddb0a8d8036a4cbcf6187ea6db4ebf35bf798646(
    *,
    service_name: builtins.str,
    backend_balancing: typing.Optional[typing.Union[ElastigroupGkeBackendServicesBackendBalancing, typing.Dict[builtins.str, typing.Any]]] = None,
    location_type: typing.Optional[builtins.str] = None,
    named_ports: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServicesNamedPorts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scheme: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12090e1c337f5f8a30effa1714c1de32ae246856ceb2db48cabad5b0c4d5041e(
    *,
    backend_balancing_mode: typing.Optional[builtins.str] = None,
    max_rate_per_instance: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deb3ff3056a14217ba00dac160ed93b008b792b2607a597ecd153f1acd0cc17c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b47767b3156f558e414211b78d58af0e03f3af63b47fc6dec3e71daaebd1e82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e1882dae39b1d8c2adb3a1ae21033f7e877dcfb3582090eaea8f205e2b29dd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d9b8383de17ec21e32fb62cbe56fb33f7e860792b6e3a726f5186de645f6c84(
    value: typing.Optional[ElastigroupGkeBackendServicesBackendBalancing],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dfa1918eb3d05517acc6685a76610e01860c88a2676100504eba53bc83718ec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37d0c4da8b872913938f83053ad8755cdb4a1243f567b78d89238d50658d6acd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a48ec2ff5b3e00f6d692fedfcf9c1c2c21f8de275d93d88de7682ad257196cb8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05af79eceada0ea85731c34391e243f58319c8a44f74d382fd765a439292e63(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60319bd8fcb3be8c907fa4332c87b8da56c104dcfdc73c7f4bf364a196e94a6d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3554e48888991d59897b97712262e9cb66f6016c2661e6db760ca0ebfbfcdcd4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServices]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf31f2dc005cd04e9200011d1ccd74c5473a88b9fbef1d8db6d2d26e3ea75f2(
    *,
    name: builtins.str,
    ports: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c16966dceff4e6e45a4e93ce6b401a8bbd55706542033daaf0b969c0be54ecd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d90dc372ded5ea9d68ad6b5e4ebae056f2f1f1005a5c9c0ce47f099470df6e4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0280efe60f66f6076a2b1e0d5d3bb4e66221efc528ccea04dd6a10e008284f3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__194df109ee492fe67b727b6b0945d36b6dc1f20fe4121b2fdbc0253b1e6d8b45(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c6ff2cd545e9f1a84e2613637ef539097685f2f6957d20654d5ed1b03b9fdb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ee18b811c8f462c442db86529752c8fd491e445f1c3711e7dd608ca213a1baa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeBackendServicesNamedPorts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f6dfd9891e296a140beec17b6951bab83bb375242c1f31af52721fbd8f1e6ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265ef78efac034aa1801acaa4010ebb4042eb39132a07acd093ebdd41a60e445(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd8bcd9ffb4d051a1f97bf1bbb25be93da07bc78207ca8afe82fc87d19b2401(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbbdb302bcd1cf852258ea78ffa1120c6fff0bb7159ea4e66226a7d16c326bc8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServicesNamedPorts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50b710239b1abb44ec3d0b4c9bbd515da31c46276059fd162478179aecff8ffc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__849f61f4bb983080ac38cd8fbcf667e3e3dcbd35f0f729a6a9f90f231f359978(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServicesNamedPorts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28985df1b0f9dfa3ab6137cb06453f9561209149471f7be32279e00d80d301ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f7fa6c990b25990d85f86279c2bd851ea095df3af4ba06bf0f0e058355e8e19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__404564523fdddbef0c9bce0598630837c4b7a943a30422624848534868420994(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3da6376d7e4a4ae3660ad1803da84745a41f34e899534597c5a4365902d7f20(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeBackendServices]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31cc1488e67b1ba3dcd55861e50eb60f032807325c88fa2cd57b8a3d0406d1b4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_zone_name: builtins.str,
    desired_capacity: jsii.Number,
    name: builtins.str,
    backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeBackendServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gpu: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeGpu, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_name_prefix: typing.Optional[builtins.str] = None,
    instance_types_custom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeInstanceTypesCustom, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_types_ondemand: typing.Optional[builtins.str] = None,
    instance_types_preemptible: typing.Optional[typing.Sequence[builtins.str]] = None,
    integration_docker_swarm: typing.Optional[typing.Union[ElastigroupGkeIntegrationDockerSwarm, typing.Dict[builtins.str, typing.Any]]] = None,
    integration_gke: typing.Optional[typing.Union[ElastigroupGkeIntegrationGke, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeMetadata, typing.Dict[builtins.str, typing.Any]]]]] = None,
    min_cpu_platform: typing.Optional[builtins.str] = None,
    min_size: typing.Optional[jsii.Number] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    node_image: typing.Optional[builtins.str] = None,
    ondemand_count: typing.Optional[jsii.Number] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    preemptible_percentage: typing.Optional[jsii.Number] = None,
    provisioning_model: typing.Optional[builtins.str] = None,
    revert_to_preemptible: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeRevertToPreemptible, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_account: typing.Optional[builtins.str] = None,
    shielded_instance_config: typing.Optional[typing.Union[ElastigroupGkeShieldedInstanceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    should_utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    startup_script: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78e2ea026bd428344f402d30979917cf250e43c5d83bee0dc3cc1ea5e5cc2536(
    *,
    auto_delete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    device_name: typing.Optional[builtins.str] = None,
    initialize_params: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeDiskInitializeParams, typing.Dict[builtins.str, typing.Any]]]]] = None,
    interface: typing.Optional[builtins.str] = None,
    mode: typing.Optional[builtins.str] = None,
    source: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__161a87053383976c3992807ced1e8256d9c2683dc133ee9e0dfe1a9f44e0e1d2(
    *,
    source_image: builtins.str,
    disk_size_gb: typing.Optional[builtins.str] = None,
    disk_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__939b661d58c3648439e2dca6a8262088d7f7708ac23e3395b8be9eb732a5d993(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cec97e84200949098314fed944c7eb293959706df4a47b64f269544a9e347931(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f5276f9a81fd1682793705eaee50cba8f2a706bb0cdddc072d973d2b42b314(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee783fae29484ceae4689790498c3646ca093a685d9036ec11bcbf7782fb230b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__130399b5fdc68d63e294a6e1d2b1f76d38f120846534515b7b72dddb8b6698b0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ac3c7f07773dafc9572be82722b82efd8f68877f8bd683346e152a32ea9a886(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDiskInitializeParams]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9d8a18c64aa8745cb66cc152df7003a4a9b24c376fe4fbf9e722e522de90a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1187dea0c8505a41fb48b5be50c16f033c65df211dec32c28ec74756bc6be07f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd2676ec636146482f5482512a11951ac92c779d7ca26734dc4ab2e1b25cd111(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cba7a19f0a73c498db832c3c7e95575f09130f210e8dee5740347399bbe573b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d871aa931e7baddd24086f8c2c6f069ff3e727a43e6464c3346c511309e68646(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDiskInitializeParams]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73d9626ff1f509aded059999dfdc981ffaf5b465abc3842e016296caa4f4db46(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32ca2b634bf9d5e1f5081be9e5bfb56b1cee5e6fc4bfc69ba051e373b7253c3a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b346afc29501995a5c619f67d98e7307fe1b99dee12cf0e96928159a962f4006(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d70c4e49a46c5ff5fa1d98ce6acfb4fbcf07e5b0401113e5a5f4c4c3f61bf122(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289f5d306f05507e6eeebd6a69e63acd6b797a66a69f83a7b5bdba50a91f8187(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb2c7eff6f1e009d46a0d7a5be65bab2b8ffd1f55e47f35043851a91b443de17(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeDisk]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85847c95a707e1512ff30981435e5d64af72e67df8d76ae9246fd1c7625f1fae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ecdd5588f6474a7c50c2f0b2cb6fb0ff0b6c60b690c7cb7ffca525fd0e2c69a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeDiskInitializeParams, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3383f1efee119bd17ead41f7309c8d8fa241c580e0061253edc82a7196e87d64(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0ffec9c70d034d4e7e6a8099154681323758d3d22b8802b2644c83ce24cea6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c31dd244a500c83717ceba7733230ebc0baac9ca44092a7a269aabadaf511a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18dc01b910cc82f685e16f614b0e5b4d99bbd1c8dfe85b00224a8e6d4dbbaa3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b641372986b6cf1a5d653833e534c431cf68a5932b1a10cc0a670024176035d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b6fb6ca5e421cf07d6499be71e0052ab9532e58915f3916c2aeafa4080a7ca4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__490ebe2bdf80042f464ffc8a003c04ded070c9e282e368a47aa9779fff8181e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef592af178bf33e901c01c63c1057f8d4f7f7591b4ece1736e805c434e69be2a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeDisk]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e64a09cf159e5a87b3ed60e039cabb8c815762c082866ad896f3cef3d52f75(
    *,
    count: jsii.Number,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6329da3555b3e516aeb6be1d8318506a2acd9af4e52ccf3d45b8d5b2dc021a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__291380353403012a45180d44a74c9cbac5239b90c97138c7b4e3abcb5b36f5d9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35220bbcecb63d1eaf13189fa941160cb4369fd559ddc132f73c863a56a5be0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d1744109be749b259fadf7a530d39e960d4d8493a59f6f187f754c458bc5e55(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19e550c7e619239472e9af94ec815acde33e9476ddf68b085bf1ca5d4807c944(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15fb7ff22f26d8ebad49e2431785318b5227892b9de65a6414cf67440daf0e29(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeGpu]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6ddc72df6b6c279c01235849fe9167fde85cf11273f163817d0263d8ec1a54(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d19fb2ee93e8f79c08426dbba97ac207253e5120a32c328232a4a3f5d2d5015(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92902385a0127ecb62b7bdcc4121a97e68c22ca57c609626213bb27bba1e8388(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ca3f9ad91df66121753c3a44470f9e96b6c739387d308fbbc656b97b445a74(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeGpu]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19ed856d4647aa37a6a96e3a52b5342a5f2863c05ec445cd3e0adeb7bdcc4bc4(
    *,
    memory_gib: jsii.Number,
    vcpu: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069b561987c625afbf2da7cabb9ed5e0e09aa024fa79265dab39ad9370b6c66e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef5422a6bc3ac4e01c5ef7dd2dfd572de0d4cd58afb33b8197d75d8add1a28e5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd035e578de7abd60529975de42526f52791a064769ca2c98691f386dd6e2150(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a9a11b1b85bd2f3995fcbd47b7b323490d9b72a9a4faee7f0302d92bf1e165(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d432fe2a105e04981c6065ed93228b667b434633505551d4d68f8427d42a558(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a26afe8652b6bdc91de50726efb30405531301787272050dd453084ca053753(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeInstanceTypesCustom]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1a052cdcd2474b515713eea2067c87dabb9b94f9678abc3753a6d22c185179(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c4f8a66e95af940d172cbd8ec952d68b4413a003561beae72a631db4bf055eb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09cc5eee25d3367ec4c8af8948045944e8f979ede79f6f6318560b45720137bb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47e824d5f0293ea6a25258eb44a0a2108ea50df5ad7f603c9873d1193cb462d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeInstanceTypesCustom]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6350d3337e3a6fb62d76c2802dccc5082d2502a80ac7ffa3305648c80ea9fea2(
    *,
    master_host: builtins.str,
    master_port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b1849ff7658649af93c3a014a7811c8ec2aa92aa504f13ff3c7eb057328c7ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f480da93b1bd2e6dc7e15ff82c9d054003b7bed6e11f51f48d4a7d3205c3b3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__058b4451bc38a656bcee70531e57679dd26fd009e2a229edd1d89e4f4adbc17e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39a7451f1bf0470281ecf2a0345a2ef1db519fd17914670dfea403f562c03107(
    value: typing.Optional[ElastigroupGkeIntegrationDockerSwarm],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcee4dc325f1f0ebc7a6631475939e7eccf4a19f147822d68bba12dead359b6a(
    *,
    autoscale_cooldown: typing.Optional[jsii.Number] = None,
    autoscale_down: typing.Optional[typing.Union[ElastigroupGkeIntegrationGkeAutoscaleDown, typing.Dict[builtins.str, typing.Any]]] = None,
    autoscale_headroom: typing.Optional[typing.Union[ElastigroupGkeIntegrationGkeAutoscaleHeadroom, typing.Dict[builtins.str, typing.Any]]] = None,
    autoscale_is_auto_config: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autoscale_is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autoscale_labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeIntegrationGkeAutoscaleLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auto_update: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    location: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97bfcaa9427025c0dc948c8be20b8d9854304541bc0c2c4d96317d7dc270ee81(
    *,
    evaluation_periods: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df43ac7e45e84ecb4e39d294cf2b236b8736c8cbc9b042a6f4d7cb3bcdb4ff70(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec47339bb957eb9793f3599936dfb26b938b1f1c975a5321e424f6f1277a87ae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__009877fa223113175e6be2355d89aae897338982b61b7b5d59bc88bab976357e(
    value: typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleDown],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6a800dfb4f382d5a99d36460a08e95b80136448355129992c0ab94300159fe(
    *,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
    num_of_units: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94952072df72e3034614f280b408aaeb293bfc386a450c1d8853f675e166abd2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f2204d5d798007f16fcb1096c5ba44a8db1a717a59d8addff79cf7d6b24294(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0389f532f5b5b694164c97dcd8c4f010bfa828e09775bd5ab8e4371e135d4363(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f644a9dcf7af952fa7678aaef453120edda88a7f190389158e984c29cfa667(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__948f10dcc120048730a4868117aee00a844ffef8f84fa2a9c2f33360e1846562(
    value: typing.Optional[ElastigroupGkeIntegrationGkeAutoscaleHeadroom],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1d048a6c42208c0565fecd9739fcf8183df025190f4ab7a26ae94e13609c5e8(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35a04e57750602fb5c20167982a63945dc66e08a341f06ab6c479b32bdebed79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54211e52fdd3a20652332f06b55cecaf8eed67fa0519ec25415555177f71abe7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__831b05d788314b7c0ce6eeefb42eda07924eb88e9eb6622b05c235edfad031b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__173c8a3ef8ed5e54af98dfbc52a4e6d3516fb3e5ac4bd2bac09a8fcc896c3dc8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b950e3dfeb34df4c55884738be69bfa6af74f13e11b35c04d5e55930b90cc53(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8b2a8a641e3b8edfc7f768459ea40d3bc3e83dbc273fcaa549c9b363fd38ca5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeIntegrationGkeAutoscaleLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb30003be487f99eaa89d661a72f4488a5b39187eceaae048e61cd61304ed6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea755c27bda2fa15787ed1a70fab6f5aa5a03414b26c51ce56976b6f9de17aa1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3165288f8fea94a43f68caa6a5c4105bf475e49ca6ee2e3e2650d02933a4e25a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e415a63848cd5bb01303f62bc9e2595ef4ae82c081327c4bc95cd3f703d83f0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeIntegrationGkeAutoscaleLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__643da5dbbc38854540d81cbda928f100896383ed3b62a79702a82a875ecdc00f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98f0b9f4632ce6cc7951c7322c12b6ffe86dd22e2dbabb6b14c815bfdeeebe51(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeIntegrationGkeAutoscaleLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e7a4a0bc3b15844620e46a0bd4e3867dae7ac945c08d1c6a2d017fae7df336(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3329f0b192135e729b84e75c3ec20c8918335afe4d5a59733195a24d32a31b64(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3601a71644331a40ced16189181f05b889c25522827a057ab69f61e030acff96(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97793dfd8e31f2c7d6a019b0de7e070ccadd39f4714d15daf7eddaa23b5a22c6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab42e3ad6a1be1e953fbf294fdbb9ddce35e6687403693e62338a147a8ac9fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dae15c233109bf3fc8c8e0f00fe1551082195ab43a1eb5ac0a035e4929f7c89d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bc34444b702c9793f3f012bb6fe19675fd728b64088e99109d655a56ae7db2f(
    value: typing.Optional[ElastigroupGkeIntegrationGke],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20db70f4f08b227afb93b01d6c04f2bc14e1a76a517a75281032720d417c273e(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3384432382a8cfcc48ac212a87c2dce1a6e5a763e9d30bfc66db2b36afd84a13(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4e150cbfbacc5a03c7005750ca73f9d8827ddd18235b4dd29f0b8ca167f2c95(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35a76858462a919c695924b5320cd4f0b9ee06a674f669458609d9a41b15d6da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34169c719de4210cc58b2607aa35a1abd5b4870d4f6eea634b44dbc255d5ee16(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbc70baec436df88177907244fcbec817db09da70f4945572f96b90254fe049d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b083c069d26289dabc32a7f7418cc23f129618dceb9742d9db3a05914c8d96c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__029874497df904074bcd64a467d7720fa177e8e8acbf5761052a057006581cb4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c57e422fa45a83dd75a9ed7ebbe8cd4055b25349d31f61b7e3b201781be6b97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0cc904948236ee379d53956563f2aa0224673918f33c4774757f8e5ba682a4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d9542805919101a8ce166b33274aea221a6102b3be7182dc0338ca24766d1f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b456aab87ac60dbe0cbb2aa6803c1cef9dc5141e120a8bd7969d1bb85d2ff0(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7504515ad0b2e532f13d1fd7536a2d47760737969e16f4e892942793dd864b08(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45270db54e7c5d0cf8bc62351ea73e3de7d2b4607714537e5d87a173a2245bc1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00da913446148ece73c2b44f3584842c315fa004efebaeaecb37a06f448f397a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c08ec7e6a829e0ed2540c269c43751e79790a0849636907ef887780825e0e87(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9634dead5d9a93dffda33aeff07ebee4e51e654b0350b4153f8bd1bc6479f4d0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bf3964db118cb3f10ff4f328d4895462ae2232e04b5bd67a7b8edb624e5ee14(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeMetadata]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef81421fb57c93c6e4c7e402cd6c599aaa7801088cae04124eea687c6daea70f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09d103727b1ce77b65bd96d15c2495dba7eb0c2290e3b4c582fba35bc452597a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98c58c9e363bc6a983905b54d50ad3735c4ba2b2423153cb42e4a6ba303f4445(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cdabc0b596320586afc67e3226db640fc36e0e0f6434b323f41fd3d2a9835c6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeMetadata]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c72ae2642b587a97083417bcecd6c63f6baa26e8e6aade1db691f101973baa8(
    *,
    network: builtins.str,
    access_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterfaceAccessConfigs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    alias_ip_ranges: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterfaceAliasIpRanges, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31d28cc0696f7f12b5c7ea190d537f110db5a3a2afd375dd57da5ce9fa14792e(
    *,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5773f422effd8fc481b0ccf87aef61f04e592bfc01202239e8d6d4bc5877e2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f69e404de019bd2991711ec348662f221eeb570cbaf2bc08511bace3a880ebae(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ebd56a76be03b6ce7e66eb68afbf556fc5a65f36534dfc09aa209a63e3f3d32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9050021046015468d0a68bab4c27d0af696fee4f1f8c53f1e912652e9e13408(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d42d67d13d362c552b7f90f0a94413a9e48c61e76922ae9f33e6a71785f334d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c0bdb4ebac1979340e22d165d821f427a5ef40297f26f4fc3ab69cbdeabb7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAccessConfigs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__523de1df57e219198c7009590c8df531478d9cae364613d0ca5ecd6cc20ad56b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7767e75fef1c2bd0e61ffe9e5b4db850b210f1e4e404ba2d9ce46d1dfc5c162e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b071650259374db66dd1c15c939b418b0faf30005b2476f08d2a37da7cbee0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b96b56bbd289d2308fef55653d5dc9391a1954aa4f67dc3aa74eff9e9a552b75(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAccessConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb658ae91cb001c505d5c4498dd99ca24b8a61e01e50aa6cfcef87aaa44c9d4f(
    *,
    ip_cidr_range: builtins.str,
    subnetwork_range_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d958144e7766712525d94ca0f8ef3afc3620b37b57eee912268019ab73de3ee7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b80d81fdc13d27dba85a7c643f68246f9b1818ac480a2f22c22e5f2e2ed5934e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f07e3ccc1d47a388d4eee3274de28ef46439f0fb666f1c09f8d5cf90eea5fe6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6229aebfb12be1bda0bf528731a823c2fda9dd4239a4ae8f29d1d904a775b00b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a614bf35b07374625745377dc8a44ece36aa30afa22127485e1c12ac19a134f4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9183865c3cdd1d6e74abff877e2027f4965df2acf507dd64413a952e39a9eccc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterfaceAliasIpRanges]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8169af25e4e0786cb52c67a0c5c9ac6c276822187286fd37883012c552554fdb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd8556a0945772e826713d3ecf5d177cb2a6d14d1368509169c112f3744da37d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a544a065e1e08fa8b3b61ff7b67a9289345c4d8fc48af6cb1ffc1a2c9b9f1102(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ec4794b129a1f5de633cab063cbc286c9d9184b7dd982ea71db3e5eeec098d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterfaceAliasIpRanges]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c4cd359daeace419d5d772783f314ac0ce5df9ef3477bd2b8ae3caa8df11467(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__590a38c3157af93d07bc665771421ce86586679c8e29149e92a887f1cf6ca9f8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31f1d412f36ffa16de110c55e160b8c5deae2e8c434352d180e538731ccc6aba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7000f402c1ecc8fb3fb881d34c53ae29a2ceaab52e2437e06e7a3c0d4fe0534f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ddd634aba30a61d775558dfae47e1a72e29300cd51447ba9c11f1d50bb0c590(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e72141018726c8b6cb19aedeae3ba162a2130e2f261e4fdea82a8cc6a57e488b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeNetworkInterface]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb00f47ca5cfa042f6cb109eee35b4ecc3710ae04d43059fdd2bba01bcc88d89(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631feea653e27a99c7c0463e49e5c11526208bd5d03cace05a780f6fcf9d39e9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterfaceAccessConfigs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__543ab2f6328f5fb91294ef1dc20b8c6f94b80d31559136e1cf6be8d9946b5be7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeNetworkInterfaceAliasIpRanges, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d5cd8964d49377c7718e502c38d1c9f265e79ef02f3fcbb83a6a7e9a7e5608(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc39e559f6882de450545f30b164848b436988566b461e8dbd8a9a039c4fc0e0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeNetworkInterface]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__043062ed5f2065e449ab8026959fda340620f0bcee74ef9ced3dd91305031ef6(
    *,
    perform_at: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16d28bf35c5d8e7fce7d3b2fddd3523e24ee924dc7a4c9fdd70114dead55105d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08e9c8d909c0fbf552bfccf24a253706425d2f6c96288bf77934e6f901617c99(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9845716c1052b7e640ea5b2c5cc37a563c21fcb7c3d57ceb754b3b2a33c638c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31fa9ff20abf94abe0fdbedc90b4c29f1966b76415baa75161cd5f0b6c5b6aa3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daa72a013fb434f269ba4c29ac8baf0f52adf6f431b903e9e04fe5ed12e97fcf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c05500b164d0950a1dc49da33f1d3b3e9d1fbc911732d9e9b80c0e9bceaf673(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeRevertToPreemptible]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a700d36e5863913a5f839cd05a970b8b5e4875eca71f06832be3ef39d7b05a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cfc56c0ca161801f1172ea23ceb6934b09e9ba33db019bdcadda9fb15deb71f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__122a020bd5e5fdc14870bae5f08f3247a444dd95694d067959b454f8799e1d54(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeRevertToPreemptible]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c345a9125cb765319f4962fec4de80f219e2d40162c011a22796626456eba77c(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    policy_name: builtins.str,
    threshold: jsii.Number,
    unit: builtins.str,
    action_type: typing.Optional[builtins.str] = None,
    adjustment: typing.Optional[jsii.Number] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingDownPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    source: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda8f70f98764ec64688f07704b7e6dc002285d42ac4c6d6c86d7c5487b6f439(
    *,
    name: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee6273db138c1d03a3a7234d585e889fbb85e123c80f1e583d72ff7bc19bf289(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82a9eecfd1981671b2959c564268d90cc022cddc4d3db327c623ed8beba5f9f4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f70aa170537676341d588623c706ea0dc32086b412a3ca70c9adb5f99bc84673(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40388bf23b492f9dd5a609e0e85bda804a7b2285ce9d0b516f3112a3d700762a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234b91066480159c6ac424bd17594c78d604ee0d7114e363afe20c8e5cb0901d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0d6234af8f86b2e409dcf2c16ba7da6a2256845679701851b1935b11384d0e5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicyDimensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__801c0e6db1a83abf7207d1a453268502edfa74425a4bad6d870101b780b4f576(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb8ec0472327c12c12e36990c8adb1a672ab6a5e81aca2d42d77fa93185407f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72ac91f986aae8164bec2809b755772c1e95bbda7bab3723d46fc4017fc1dfb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dd899550ea8be69699fd1a15110b292498f953217da4921d4e7e0e1bf97429b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicyDimensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6483731ba19c622415c0b2a917bad011b8b92c282cd27227b67402b51e2f35b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6892998a66cc6499edb98394f20c57f82e5062bb93b11add3d20eec0a5f97ead(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1aff10aa0049f8decc5809ba253097e961f33228deae057feb8b977bca8fef8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d3debe840093b67e8e916189160bd0e9f3c2fa11a96f86ebe47d2572aeafe1e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8a912ec93d7b178a3c02e415e323a762c6f94af331d4fe0b0c4953009a8a0d8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1904c4156459b2b2def523e765d08f77eeaff93f3cb7c1b1c2b8c15a950f59c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingDownPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a0496f8912951084574d300677af8cbc772482cb8b7f12648432a18db9e7363(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41cc73b8c8f27d5207cf924baa6f652e57b2d9816e1804d61df799bade1d559f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingDownPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6e7eff3ce63c714332488d01c441a39819c82495a8245c9844d49b2d8c38587(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a00091bcb833cb4e65bbd5cba74d77e4ef3df67aee4ae8c0a562815069374f91(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a64914df22eb959b8a9d94513869801cd5e81293b83dd28fa8ba25327ed42a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27bc449a0ff854a8dc09657e62d01bfd543c80d0b27286a0977d9adb7e18a619(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b9c117980c6e4feccff71c49541e18f310a4565bc6aa277c0f49317857970cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8e40bb3f12fdee4435d9f2a270be64197549119d9aac6687234be969d9520d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f6f2a76a320c649fef7dfcb8d99ffa944b23d5ecb0b60410d6a1880670fd823(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21cbf87c07a404424e596ce2d1cbbcec1ecb06d92c8be9e101db5b9f2794031b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b092ad91f38c3b51b2b07e9f1b0c0e5eb9fa54db624d2403a141937c8d7eca64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17d385ce1d6387002b0775b56e5b3bd6fac61271c2d67bbff60325e240193389(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02bfd83da31ea2de59f08f81feadb4f68f235342ec5d94faeb4c3979d70e19fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c201c8af0affa97ff044b42bb312c4bedcd7e2d599e3ae1e5cc6809a0598508d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffcc90e3848da3424fa3c3b114e0c11a0fae86649ee42bfdf80ec2e7d32e6802(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c059024e0e361d95c0da604af9541da83e6df201197a49779b8d3bb99ac16ec1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingDownPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__452803770fdd4ae4167c27496e294a6b5eb2f70848e545ed431ebe45bbc6e351(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    policy_name: builtins.str,
    threshold: jsii.Number,
    unit: builtins.str,
    action_type: typing.Optional[builtins.str] = None,
    adjustment: typing.Optional[jsii.Number] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingUpPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    source: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b5519b569e3d44b15a9b06846fb9476f30e95c8ff6e2fa6f3c7067001b2f135(
    *,
    name: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40ff71cc657d64aa2a1fd852c73a15d90d536f359e5f3421e55012138795e1ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca677c7fcfe28fd7b251f1515c2c9a38872a22f4f60538884e60c0e063d8a0f4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac897fcce30af75c6eb23dcd51ac6f0f8b26548ca2f647c70256178b09cc9ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c384f71016e37da1d9eebab805f9c60d2639733572067b8c685aa7bdefd0421(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16c912faabd06547b3ecdc61fa9807f264d19701467510f8fc768df7494f738d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e77e95b3bbf013bb5004609a3e6522a85e6f21db611516edccd186b9e1a97fb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicyDimensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ddbbf675a2b5e895be5bda42eb4726ca148f65b2b5543363bb2696c4e05d7bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f6b3ba315d753971663749cf27a95326c8013a9046690f0409a284003457050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90810e250ae83f41f10686c5e3d988f781b08ae4e911cb2e6fb3a52494cb6a85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d758690ab32a571f1e70ee4453cb65b8a452c07c08bad3b8756caf34d3be2cef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicyDimensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67343862ec4d263cba13a4cb49770f9814740c96e39c9b9038005548450ded79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99af64b8bf243469121a786b86c17010f4065ff1cdc3ce2f9c2889adb6a9456e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8f74cb918ece298db7fd335b58841b6e382e8233223aa7c2705e2994091c38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d88c7fb634f40d71c8ba86352cf9c68d12cb10a08dd67173b26ec4c1d267295(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3516dc241fb5cacce0e4092bfc6becf7b1e1f43b785281dd2355201da24624a6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99efe48ef2491320ec1653029130d447e64249af557f813cda39c4216c73ef3e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupGkeScalingUpPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7c8041f840554a4dd4663946753c9f005ebf1585b37ea5629f2d71caf7558e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__491558ff1eff61b83b2aac0800e4d6e9d1c4b9c45ad9fdc4888a8dc947a20f85(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupGkeScalingUpPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c532f5d75503a425f09e555f9c86f0252b8924ff023ef38f5da6899a388bf0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bfbe4a79175005a4370db9821375c6493643e133d4821c7dd664ec0a6b4c52f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ca69d71f31c208ecad2be8e71050b881d00937c4ef1e7ea6a01832a2de55d8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3219fd74caff21c6501772284a5f3e1b4ca1baf17491680e91928915e008d452(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__695e9534f2c41a2691425a069bb36942ce753b0db189f7c7b3a4b95c8720c6dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81e9a284a77ec35e9fd3e43614ae7e59d5f5532258234acb5eee20037306f34a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1813288d3c3ce5a321bf863d27cb52d2ab37e5915038f8007b68e3af4e0b7ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a23482357e8c5a8ef6d24f70c92c4d58a2014dd2c0afe60aafdb6586d211ff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb8c41fad594c51c7b9024b28aad8fcefabdf1829ce83dd6519be595b3c0917(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a9635003eaf98b7409906c714d4946bf3bddff45d2ca2d090df1c406e72982(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3708e0603f2cc8a7807e10ee276d89a52099b4cf91cb9aa5448b6dfb74b480eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef0259d5a34725a974a28fb1b29391fad79592040185a2fbdf3ebe4b6f3f4f38(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60112b469ef222d123c20215314f95565d18869e890625d27fb9056183f4aabc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02f3aea956b32dd1b5e2bc57fae710b9bb0ef3d6a63e169ed71a08dc734152d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupGkeScalingUpPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__806c18609fce6b99f485ca7c06fe45873221d1998048ebb63c6d71c89ed11537(
    *,
    enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86b251911a3e4bda166cf1764f30db5ddcab62f5183973bdb1352815d7113c14(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5f0ba568ada46c5f0b7ab22844c7290724a47948f8736f2b4792b891beeed91(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55af1008dc8dd8f74d2826e9eb15e27b279588222483afa3d1844c4a2d56b965(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf83952a06f4c4ee2036ef63968460ce5dbfe2b38bd7bc7bdcb48f8e78cd78b6(
    value: typing.Optional[ElastigroupGkeShieldedInstanceConfig],
) -> None:
    """Type checking stubs"""
    pass
