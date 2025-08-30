r'''
# `spotinst_elastigroup_azure_v3`

Refer to the Terraform Registry for docs: [`spotinst_elastigroup_azure_v3`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3).
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


class ElastigroupAzureV3(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3 spotinst_elastigroup_azure_v3}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        name: builtins.str,
        network: typing.Union["ElastigroupAzureV3Network", typing.Dict[builtins.str, typing.Any]],
        os: builtins.str,
        region: builtins.str,
        resource_group_name: builtins.str,
        vm_sizes: typing.Union["ElastigroupAzureV3VmSizes", typing.Dict[builtins.str, typing.Any]],
        availability_vs_cost: typing.Optional[jsii.Number] = None,
        boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3BootDiagnostics", typing.Dict[builtins.str, typing.Any]]]]] = None,
        capacity_reservation: typing.Optional[typing.Union["ElastigroupAzureV3CapacityReservation", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_data: typing.Optional[builtins.str] = None,
        data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3DataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Extensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        health: typing.Optional[typing.Union["ElastigroupAzureV3Health", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Image", typing.Dict[builtins.str, typing.Any]]]]] = None,
        load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3LoadBalancer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        login: typing.Optional[typing.Union["ElastigroupAzureV3Login", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_service_identity: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ManagedServiceIdentity", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        on_demand_count: typing.Optional[jsii.Number] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        os_disk: typing.Optional[typing.Union["ElastigroupAzureV3OsDisk", typing.Dict[builtins.str, typing.Any]]] = None,
        preferred_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ProximityPlacementGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        revert_to_spot: typing.Optional[typing.Union["ElastigroupAzureV3RevertToSpot", typing.Dict[builtins.str, typing.Any]]] = None,
        scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Secret", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security: typing.Optional[typing.Union["ElastigroupAzureV3Security", typing.Dict[builtins.str, typing.Any]]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Signal", typing.Dict[builtins.str, typing.Any]]]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Tags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        user_data: typing.Optional[builtins.str] = None,
        vm_name_prefix: typing.Optional[builtins.str] = None,
        zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3 spotinst_elastigroup_azure_v3} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param fallback_to_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#fallback_to_on_demand ElastigroupAzureV3#fallback_to_on_demand}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#network ElastigroupAzureV3#network}
        :param os: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#os ElastigroupAzureV3#os}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#region ElastigroupAzureV3#region}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        :param vm_sizes: vm_sizes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vm_sizes ElastigroupAzureV3#vm_sizes}
        :param availability_vs_cost: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#availability_vs_cost ElastigroupAzureV3#availability_vs_cost}.
        :param boot_diagnostics: boot_diagnostics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#boot_diagnostics ElastigroupAzureV3#boot_diagnostics}
        :param capacity_reservation: capacity_reservation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#capacity_reservation ElastigroupAzureV3#capacity_reservation}
        :param custom_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#custom_data ElastigroupAzureV3#custom_data}.
        :param data_disk: data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#data_disk ElastigroupAzureV3#data_disk}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#description ElastigroupAzureV3#description}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#desired_capacity ElastigroupAzureV3#desired_capacity}.
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#draining_timeout ElastigroupAzureV3#draining_timeout}.
        :param extensions: extensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#extensions ElastigroupAzureV3#extensions}
        :param health: health block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#health ElastigroupAzureV3#health}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#id ElastigroupAzureV3#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image: image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image ElastigroupAzureV3#image}
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#load_balancer ElastigroupAzureV3#load_balancer}
        :param login: login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#login ElastigroupAzureV3#login}
        :param managed_service_identity: managed_service_identity block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#managed_service_identity ElastigroupAzureV3#managed_service_identity}
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_size ElastigroupAzureV3#max_size}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_size ElastigroupAzureV3#min_size}.
        :param on_demand_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#on_demand_count ElastigroupAzureV3#on_demand_count}.
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#optimization_windows ElastigroupAzureV3#optimization_windows}.
        :param os_disk: os_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#os_disk ElastigroupAzureV3#os_disk}
        :param preferred_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#preferred_zones ElastigroupAzureV3#preferred_zones}.
        :param proximity_placement_groups: proximity_placement_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#proximity_placement_groups ElastigroupAzureV3#proximity_placement_groups}
        :param revert_to_spot: revert_to_spot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#revert_to_spot ElastigroupAzureV3#revert_to_spot}
        :param scaling_down_policy: scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scaling_down_policy ElastigroupAzureV3#scaling_down_policy}
        :param scaling_up_policy: scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scaling_up_policy ElastigroupAzureV3#scaling_up_policy}
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scheduling_task ElastigroupAzureV3#scheduling_task}
        :param secret: secret block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secret ElastigroupAzureV3#secret}
        :param security: security block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security ElastigroupAzureV3#security}
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#shutdown_script ElastigroupAzureV3#shutdown_script}.
        :param signal: signal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#signal ElastigroupAzureV3#signal}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_percentage ElastigroupAzureV3#spot_percentage}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#tags ElastigroupAzureV3#tags}
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#user_data ElastigroupAzureV3#user_data}.
        :param vm_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vm_name_prefix ElastigroupAzureV3#vm_name_prefix}.
        :param zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#zones ElastigroupAzureV3#zones}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53f7c061b4714ed0e34fd061e2e2b00e6d764bdcc37298b4b59f4797cf347893)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElastigroupAzureV3Config(
            fallback_to_on_demand=fallback_to_on_demand,
            name=name,
            network=network,
            os=os,
            region=region,
            resource_group_name=resource_group_name,
            vm_sizes=vm_sizes,
            availability_vs_cost=availability_vs_cost,
            boot_diagnostics=boot_diagnostics,
            capacity_reservation=capacity_reservation,
            custom_data=custom_data,
            data_disk=data_disk,
            description=description,
            desired_capacity=desired_capacity,
            draining_timeout=draining_timeout,
            extensions=extensions,
            health=health,
            id=id,
            image=image,
            load_balancer=load_balancer,
            login=login,
            managed_service_identity=managed_service_identity,
            max_size=max_size,
            min_size=min_size,
            on_demand_count=on_demand_count,
            optimization_windows=optimization_windows,
            os_disk=os_disk,
            preferred_zones=preferred_zones,
            proximity_placement_groups=proximity_placement_groups,
            revert_to_spot=revert_to_spot,
            scaling_down_policy=scaling_down_policy,
            scaling_up_policy=scaling_up_policy,
            scheduling_task=scheduling_task,
            secret=secret,
            security=security,
            shutdown_script=shutdown_script,
            signal=signal,
            spot_percentage=spot_percentage,
            tags=tags,
            user_data=user_data,
            vm_name_prefix=vm_name_prefix,
            zones=zones,
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
        '''Generates CDKTF code for importing a ElastigroupAzureV3 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ElastigroupAzureV3 to import.
        :param import_from_id: The id of the existing ElastigroupAzureV3 that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ElastigroupAzureV3 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c534953e092d487ada42112f101456eea77aa7b85820daf3a03ae5592c1aeff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putBootDiagnostics")
    def put_boot_diagnostics(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3BootDiagnostics", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ca1ebd463f681bfc6281635566a7a672526abadb6f3602fb720dbdfb45eb8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBootDiagnostics", [value]))

    @jsii.member(jsii_name="putCapacityReservation")
    def put_capacity_reservation(
        self,
        *,
        should_utilize: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        utilization_strategy: builtins.str,
        capacity_reservation_groups: typing.Optional[typing.Union["ElastigroupAzureV3CapacityReservationCapacityReservationGroups", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_utilize: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#should_utilize ElastigroupAzureV3#should_utilize}.
        :param utilization_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#utilization_strategy ElastigroupAzureV3#utilization_strategy}.
        :param capacity_reservation_groups: capacity_reservation_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#capacity_reservation_groups ElastigroupAzureV3#capacity_reservation_groups}
        '''
        value = ElastigroupAzureV3CapacityReservation(
            should_utilize=should_utilize,
            utilization_strategy=utilization_strategy,
            capacity_reservation_groups=capacity_reservation_groups,
        )

        return typing.cast(None, jsii.invoke(self, "putCapacityReservation", [value]))

    @jsii.member(jsii_name="putDataDisk")
    def put_data_disk(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3DataDisk", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59902e1da0d04e351df0bd04ef0d6e4380f5776b312d13e93cae18653ae9d9c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDataDisk", [value]))

    @jsii.member(jsii_name="putExtensions")
    def put_extensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Extensions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5845c82aa4ecf191f180b7d4aded9996aa6d67571e10462559d23ba0ef9ab0b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExtensions", [value]))

    @jsii.member(jsii_name="putHealth")
    def put_health(
        self,
        *,
        auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        grace_period: typing.Optional[jsii.Number] = None,
        health_check_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        unhealthy_duration: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param auto_healing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#auto_healing ElastigroupAzureV3#auto_healing}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#grace_period ElastigroupAzureV3#grace_period}.
        :param health_check_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#health_check_types ElastigroupAzureV3#health_check_types}.
        :param unhealthy_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unhealthy_duration ElastigroupAzureV3#unhealthy_duration}.
        '''
        value = ElastigroupAzureV3Health(
            auto_healing=auto_healing,
            grace_period=grace_period,
            health_check_types=health_check_types,
            unhealthy_duration=unhealthy_duration,
        )

        return typing.cast(None, jsii.invoke(self, "putHealth", [value]))

    @jsii.member(jsii_name="putImage")
    def put_image(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Image", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21d59cb1cb9dde435082d87fae76afe4c1f26e397ebd82861b71f68d27214b57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putImage", [value]))

    @jsii.member(jsii_name="putLoadBalancer")
    def put_load_balancer(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3LoadBalancer", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__780236eaf3c7244a0704795b6dbdee6523671420862eac4af12172fdf4c8948a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLoadBalancer", [value]))

    @jsii.member(jsii_name="putLogin")
    def put_login(
        self,
        *,
        user_name: builtins.str,
        password: typing.Optional[builtins.str] = None,
        ssh_public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#user_name ElastigroupAzureV3#user_name}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#password ElastigroupAzureV3#password}.
        :param ssh_public_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#ssh_public_key ElastigroupAzureV3#ssh_public_key}.
        '''
        value = ElastigroupAzureV3Login(
            user_name=user_name, password=password, ssh_public_key=ssh_public_key
        )

        return typing.cast(None, jsii.invoke(self, "putLogin", [value]))

    @jsii.member(jsii_name="putManagedServiceIdentity")
    def put_managed_service_identity(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ManagedServiceIdentity", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd7cd62849b1c2011977b8065f1f565cf340f1c12155e8213bb02a0b79f06dbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putManagedServiceIdentity", [value]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        *,
        network_interfaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3NetworkNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]],
        resource_group_name: builtins.str,
        virtual_network_name: builtins.str,
    ) -> None:
        '''
        :param network_interfaces: network_interfaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#network_interfaces ElastigroupAzureV3#network_interfaces}
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        :param virtual_network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#virtual_network_name ElastigroupAzureV3#virtual_network_name}.
        '''
        value = ElastigroupAzureV3Network(
            network_interfaces=network_interfaces,
            resource_group_name=resource_group_name,
            virtual_network_name=virtual_network_name,
        )

        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putOsDisk")
    def put_os_disk(
        self,
        *,
        type: builtins.str,
        size_gb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#size_gb ElastigroupAzureV3#size_gb}.
        '''
        value = ElastigroupAzureV3OsDisk(type=type, size_gb=size_gb)

        return typing.cast(None, jsii.invoke(self, "putOsDisk", [value]))

    @jsii.member(jsii_name="putProximityPlacementGroups")
    def put_proximity_placement_groups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ProximityPlacementGroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbdf019b3e060828b24c3f9ce3c3ae8bec91796a033429ea27853879e9969a9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putProximityPlacementGroups", [value]))

    @jsii.member(jsii_name="putRevertToSpot")
    def put_revert_to_spot(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#perform_at ElastigroupAzureV3#perform_at}.
        '''
        value = ElastigroupAzureV3RevertToSpot(perform_at=perform_at)

        return typing.cast(None, jsii.invoke(self, "putRevertToSpot", [value]))

    @jsii.member(jsii_name="putScalingDownPolicy")
    def put_scaling_down_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f069f544160fabc9e52c2aacb944cd8ae65553f43d7c84bd2e9b719d3b94fcce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScalingDownPolicy", [value]))

    @jsii.member(jsii_name="putScalingUpPolicy")
    def put_scaling_up_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__506528337c3ed268b9d70ae5002466346a15e31b635158bf567ef9d906e3da4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScalingUpPolicy", [value]))

    @jsii.member(jsii_name="putSchedulingTask")
    def put_scheduling_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SchedulingTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4699c1abfd00ee7b69f44505e539824938388bb85f4f98255aaf2220a268bdaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSchedulingTask", [value]))

    @jsii.member(jsii_name="putSecret")
    def put_secret(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Secret", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e13f6f8a4bd851f260f64c357d14a6d5f13faa18b9e1ea45d77c17d2ac3e90a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSecret", [value]))

    @jsii.member(jsii_name="putSecurity")
    def put_security(
        self,
        *,
        confidential_os_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_at_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        security_type: typing.Optional[builtins.str] = None,
        vtpm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param confidential_os_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#confidential_os_disk_encryption ElastigroupAzureV3#confidential_os_disk_encryption}.
        :param encryption_at_host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#encryption_at_host ElastigroupAzureV3#encryption_at_host}.
        :param secure_boot_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secure_boot_enabled ElastigroupAzureV3#secure_boot_enabled}.
        :param security_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security_type ElastigroupAzureV3#security_type}.
        :param vtpm_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vtpm_enabled ElastigroupAzureV3#vtpm_enabled}.
        '''
        value = ElastigroupAzureV3Security(
            confidential_os_disk_encryption=confidential_os_disk_encryption,
            encryption_at_host=encryption_at_host,
            secure_boot_enabled=secure_boot_enabled,
            security_type=security_type,
            vtpm_enabled=vtpm_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putSecurity", [value]))

    @jsii.member(jsii_name="putSignal")
    def put_signal(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Signal", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e537ea3444b244bfc9c1593da970e0050d46abc0cea73b34c7adc7d4bb41afb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSignal", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Tags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d068333819880e4eb44d6218604088f95ee0bd9f6edb512e96e2d407b6e2b140)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putVmSizes")
    def put_vm_sizes(
        self,
        *,
        od_sizes: typing.Sequence[builtins.str],
        excluded_vm_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        spot_size_attributes: typing.Optional[typing.Union["ElastigroupAzureV3VmSizesSpotSizeAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param od_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#od_sizes ElastigroupAzureV3#od_sizes}.
        :param excluded_vm_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#excluded_vm_sizes ElastigroupAzureV3#excluded_vm_sizes}.
        :param preferred_spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#preferred_spot_sizes ElastigroupAzureV3#preferred_spot_sizes}.
        :param spot_size_attributes: spot_size_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_size_attributes ElastigroupAzureV3#spot_size_attributes}
        :param spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_sizes ElastigroupAzureV3#spot_sizes}.
        '''
        value = ElastigroupAzureV3VmSizes(
            od_sizes=od_sizes,
            excluded_vm_sizes=excluded_vm_sizes,
            preferred_spot_sizes=preferred_spot_sizes,
            spot_size_attributes=spot_size_attributes,
            spot_sizes=spot_sizes,
        )

        return typing.cast(None, jsii.invoke(self, "putVmSizes", [value]))

    @jsii.member(jsii_name="resetAvailabilityVsCost")
    def reset_availability_vs_cost(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityVsCost", []))

    @jsii.member(jsii_name="resetBootDiagnostics")
    def reset_boot_diagnostics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootDiagnostics", []))

    @jsii.member(jsii_name="resetCapacityReservation")
    def reset_capacity_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityReservation", []))

    @jsii.member(jsii_name="resetCustomData")
    def reset_custom_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomData", []))

    @jsii.member(jsii_name="resetDataDisk")
    def reset_data_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataDisk", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDesiredCapacity")
    def reset_desired_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDesiredCapacity", []))

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetExtensions")
    def reset_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtensions", []))

    @jsii.member(jsii_name="resetHealth")
    def reset_health(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealth", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImage")
    def reset_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImage", []))

    @jsii.member(jsii_name="resetLoadBalancer")
    def reset_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancer", []))

    @jsii.member(jsii_name="resetLogin")
    def reset_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogin", []))

    @jsii.member(jsii_name="resetManagedServiceIdentity")
    def reset_managed_service_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedServiceIdentity", []))

    @jsii.member(jsii_name="resetMaxSize")
    def reset_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxSize", []))

    @jsii.member(jsii_name="resetMinSize")
    def reset_min_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinSize", []))

    @jsii.member(jsii_name="resetOnDemandCount")
    def reset_on_demand_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemandCount", []))

    @jsii.member(jsii_name="resetOptimizationWindows")
    def reset_optimization_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimizationWindows", []))

    @jsii.member(jsii_name="resetOsDisk")
    def reset_os_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDisk", []))

    @jsii.member(jsii_name="resetPreferredZones")
    def reset_preferred_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredZones", []))

    @jsii.member(jsii_name="resetProximityPlacementGroups")
    def reset_proximity_placement_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProximityPlacementGroups", []))

    @jsii.member(jsii_name="resetRevertToSpot")
    def reset_revert_to_spot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevertToSpot", []))

    @jsii.member(jsii_name="resetScalingDownPolicy")
    def reset_scaling_down_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingDownPolicy", []))

    @jsii.member(jsii_name="resetScalingUpPolicy")
    def reset_scaling_up_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingUpPolicy", []))

    @jsii.member(jsii_name="resetSchedulingTask")
    def reset_scheduling_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingTask", []))

    @jsii.member(jsii_name="resetSecret")
    def reset_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecret", []))

    @jsii.member(jsii_name="resetSecurity")
    def reset_security(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurity", []))

    @jsii.member(jsii_name="resetShutdownScript")
    def reset_shutdown_script(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownScript", []))

    @jsii.member(jsii_name="resetSignal")
    def reset_signal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignal", []))

    @jsii.member(jsii_name="resetSpotPercentage")
    def reset_spot_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotPercentage", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @jsii.member(jsii_name="resetVmNamePrefix")
    def reset_vm_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmNamePrefix", []))

    @jsii.member(jsii_name="resetZones")
    def reset_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZones", []))

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
    @jsii.member(jsii_name="bootDiagnostics")
    def boot_diagnostics(self) -> "ElastigroupAzureV3BootDiagnosticsList":
        return typing.cast("ElastigroupAzureV3BootDiagnosticsList", jsii.get(self, "bootDiagnostics"))

    @builtins.property
    @jsii.member(jsii_name="capacityReservation")
    def capacity_reservation(
        self,
    ) -> "ElastigroupAzureV3CapacityReservationOutputReference":
        return typing.cast("ElastigroupAzureV3CapacityReservationOutputReference", jsii.get(self, "capacityReservation"))

    @builtins.property
    @jsii.member(jsii_name="dataDisk")
    def data_disk(self) -> "ElastigroupAzureV3DataDiskList":
        return typing.cast("ElastigroupAzureV3DataDiskList", jsii.get(self, "dataDisk"))

    @builtins.property
    @jsii.member(jsii_name="extensions")
    def extensions(self) -> "ElastigroupAzureV3ExtensionsList":
        return typing.cast("ElastigroupAzureV3ExtensionsList", jsii.get(self, "extensions"))

    @builtins.property
    @jsii.member(jsii_name="health")
    def health(self) -> "ElastigroupAzureV3HealthOutputReference":
        return typing.cast("ElastigroupAzureV3HealthOutputReference", jsii.get(self, "health"))

    @builtins.property
    @jsii.member(jsii_name="image")
    def image(self) -> "ElastigroupAzureV3ImageList":
        return typing.cast("ElastigroupAzureV3ImageList", jsii.get(self, "image"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(self) -> "ElastigroupAzureV3LoadBalancerList":
        return typing.cast("ElastigroupAzureV3LoadBalancerList", jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="login")
    def login(self) -> "ElastigroupAzureV3LoginOutputReference":
        return typing.cast("ElastigroupAzureV3LoginOutputReference", jsii.get(self, "login"))

    @builtins.property
    @jsii.member(jsii_name="managedServiceIdentity")
    def managed_service_identity(
        self,
    ) -> "ElastigroupAzureV3ManagedServiceIdentityList":
        return typing.cast("ElastigroupAzureV3ManagedServiceIdentityList", jsii.get(self, "managedServiceIdentity"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "ElastigroupAzureV3NetworkOutputReference":
        return typing.cast("ElastigroupAzureV3NetworkOutputReference", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="osDisk")
    def os_disk(self) -> "ElastigroupAzureV3OsDiskOutputReference":
        return typing.cast("ElastigroupAzureV3OsDiskOutputReference", jsii.get(self, "osDisk"))

    @builtins.property
    @jsii.member(jsii_name="proximityPlacementGroups")
    def proximity_placement_groups(
        self,
    ) -> "ElastigroupAzureV3ProximityPlacementGroupsList":
        return typing.cast("ElastigroupAzureV3ProximityPlacementGroupsList", jsii.get(self, "proximityPlacementGroups"))

    @builtins.property
    @jsii.member(jsii_name="revertToSpot")
    def revert_to_spot(self) -> "ElastigroupAzureV3RevertToSpotOutputReference":
        return typing.cast("ElastigroupAzureV3RevertToSpotOutputReference", jsii.get(self, "revertToSpot"))

    @builtins.property
    @jsii.member(jsii_name="scalingDownPolicy")
    def scaling_down_policy(self) -> "ElastigroupAzureV3ScalingDownPolicyList":
        return typing.cast("ElastigroupAzureV3ScalingDownPolicyList", jsii.get(self, "scalingDownPolicy"))

    @builtins.property
    @jsii.member(jsii_name="scalingUpPolicy")
    def scaling_up_policy(self) -> "ElastigroupAzureV3ScalingUpPolicyList":
        return typing.cast("ElastigroupAzureV3ScalingUpPolicyList", jsii.get(self, "scalingUpPolicy"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTask")
    def scheduling_task(self) -> "ElastigroupAzureV3SchedulingTaskList":
        return typing.cast("ElastigroupAzureV3SchedulingTaskList", jsii.get(self, "schedulingTask"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> "ElastigroupAzureV3SecretList":
        return typing.cast("ElastigroupAzureV3SecretList", jsii.get(self, "secret"))

    @builtins.property
    @jsii.member(jsii_name="security")
    def security(self) -> "ElastigroupAzureV3SecurityOutputReference":
        return typing.cast("ElastigroupAzureV3SecurityOutputReference", jsii.get(self, "security"))

    @builtins.property
    @jsii.member(jsii_name="signal")
    def signal(self) -> "ElastigroupAzureV3SignalList":
        return typing.cast("ElastigroupAzureV3SignalList", jsii.get(self, "signal"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "ElastigroupAzureV3TagsList":
        return typing.cast("ElastigroupAzureV3TagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="vmSizes")
    def vm_sizes(self) -> "ElastigroupAzureV3VmSizesOutputReference":
        return typing.cast("ElastigroupAzureV3VmSizesOutputReference", jsii.get(self, "vmSizes"))

    @builtins.property
    @jsii.member(jsii_name="availabilityVsCostInput")
    def availability_vs_cost_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "availabilityVsCostInput"))

    @builtins.property
    @jsii.member(jsii_name="bootDiagnosticsInput")
    def boot_diagnostics_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3BootDiagnostics"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3BootDiagnostics"]]], jsii.get(self, "bootDiagnosticsInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityReservationInput")
    def capacity_reservation_input(
        self,
    ) -> typing.Optional["ElastigroupAzureV3CapacityReservation"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3CapacityReservation"], jsii.get(self, "capacityReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="customDataInput")
    def custom_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDataInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDiskInput")
    def data_disk_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3DataDisk"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3DataDisk"]]], jsii.get(self, "dataDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="desiredCapacityInput")
    def desired_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "desiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="extensionsInput")
    def extensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Extensions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Extensions"]]], jsii.get(self, "extensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackToOnDemandInput")
    def fallback_to_on_demand_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackToOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="healthInput")
    def health_input(self) -> typing.Optional["ElastigroupAzureV3Health"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3Health"], jsii.get(self, "healthInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="imageInput")
    def image_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Image"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Image"]]], jsii.get(self, "imageInput"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancerInput")
    def load_balancer_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3LoadBalancer"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3LoadBalancer"]]], jsii.get(self, "loadBalancerInput"))

    @builtins.property
    @jsii.member(jsii_name="loginInput")
    def login_input(self) -> typing.Optional["ElastigroupAzureV3Login"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3Login"], jsii.get(self, "loginInput"))

    @builtins.property
    @jsii.member(jsii_name="managedServiceIdentityInput")
    def managed_service_identity_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ManagedServiceIdentity"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ManagedServiceIdentity"]]], jsii.get(self, "managedServiceIdentityInput"))

    @builtins.property
    @jsii.member(jsii_name="maxSizeInput")
    def max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="minSizeInput")
    def min_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional["ElastigroupAzureV3Network"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3Network"], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="onDemandCountInput")
    def on_demand_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "onDemandCountInput"))

    @builtins.property
    @jsii.member(jsii_name="optimizationWindowsInput")
    def optimization_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optimizationWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="osDiskInput")
    def os_disk_input(self) -> typing.Optional["ElastigroupAzureV3OsDisk"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3OsDisk"], jsii.get(self, "osDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="osInput")
    def os_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredZonesInput")
    def preferred_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredZonesInput"))

    @builtins.property
    @jsii.member(jsii_name="proximityPlacementGroupsInput")
    def proximity_placement_groups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ProximityPlacementGroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ProximityPlacementGroups"]]], jsii.get(self, "proximityPlacementGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="revertToSpotInput")
    def revert_to_spot_input(self) -> typing.Optional["ElastigroupAzureV3RevertToSpot"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3RevertToSpot"], jsii.get(self, "revertToSpotInput"))

    @builtins.property
    @jsii.member(jsii_name="scalingDownPolicyInput")
    def scaling_down_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingDownPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingDownPolicy"]]], jsii.get(self, "scalingDownPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="scalingUpPolicyInput")
    def scaling_up_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingUpPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingUpPolicy"]]], jsii.get(self, "scalingUpPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTaskInput")
    def scheduling_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SchedulingTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SchedulingTask"]]], jsii.get(self, "schedulingTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Secret"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Secret"]]], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="securityInput")
    def security_input(self) -> typing.Optional["ElastigroupAzureV3Security"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3Security"], jsii.get(self, "securityInput"))

    @builtins.property
    @jsii.member(jsii_name="shutdownScriptInput")
    def shutdown_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shutdownScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="signalInput")
    def signal_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Signal"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Signal"]]], jsii.get(self, "signalInput"))

    @builtins.property
    @jsii.member(jsii_name="spotPercentageInput")
    def spot_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Tags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Tags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property
    @jsii.member(jsii_name="vmNamePrefixInput")
    def vm_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vmNamePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="vmSizesInput")
    def vm_sizes_input(self) -> typing.Optional["ElastigroupAzureV3VmSizes"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3VmSizes"], jsii.get(self, "vmSizesInput"))

    @builtins.property
    @jsii.member(jsii_name="zonesInput")
    def zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "zonesInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityVsCost")
    def availability_vs_cost(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "availabilityVsCost"))

    @availability_vs_cost.setter
    def availability_vs_cost(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbd7f746ea383525116b16f5de031c6443401ad05daf392e19ee30c96e7dddf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityVsCost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customData")
    def custom_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customData"))

    @custom_data.setter
    def custom_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f876fbc4c7e79444086b5095158074843d1ff30b801c390e6a7240fb37d355d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94ed00d078664c6a773cdbf9ebca1810982eb6e1523dd2dd4e204513a0011c0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="desiredCapacity")
    def desired_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "desiredCapacity"))

    @desired_capacity.setter
    def desired_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe58ccb567210b120ce792fbbaa40aaa6dc07467cd0cc77229a285f4f2e574dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07b6a667380233684aec1d9dc1307b42978a915c3ef2ff4ca2e73ade80289372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainingTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fallbackToOnDemand")
    def fallback_to_on_demand(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "fallbackToOnDemand"))

    @fallback_to_on_demand.setter
    def fallback_to_on_demand(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6695cef71ddb2b7f7ac678846b45f3dd31df28aaa71b452c21e09859c1dae7e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackToOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f6d034d8a92d25a595356eda4160ff0849c893aa239daa1d6c9c22fb5162645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxSize")
    def max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSize"))

    @max_size.setter
    def max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcd725f02a67b5ef7be31ba86897bf88c4e9077077ace70cf5da84203ca86879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minSize")
    def min_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSize"))

    @min_size.setter
    def min_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86b94b66b7a2f2a5077c493e3902acf43a99720cc101fcefc9ccc39fbbb8e84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__662bb7b3318d34466a4f81f5394d52df5875516081bdcb71ba2155735ae3a99b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="onDemandCount")
    def on_demand_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "onDemandCount"))

    @on_demand_count.setter
    def on_demand_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3031bfe395d694d4a5af030d21b0b58563520c519de714aaca7d6925f9685550)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "onDemandCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optimizationWindows")
    def optimization_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "optimizationWindows"))

    @optimization_windows.setter
    def optimization_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d8a11d55249d3e427fcc60176175b07aaaee9470b9828b0b47ea79eccddc74a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimizationWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="os")
    def os(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "os"))

    @os.setter
    def os(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__397fa1b95dee853896ce46be6ba62e69a3b6e2532fe28d9b4927a9af4f7e4d96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "os", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredZones")
    def preferred_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredZones"))

    @preferred_zones.setter
    def preferred_zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0694f8456bfaa0f2f807f8a3ea97de28892e95792eec55e03af3777d5a74127b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredZones", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07807e45fbffe00c3e7a6a9bdbecf1c268dfe46ca1a61df7a3a50468e72e25c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c628008e7b0a6e19c06d95614a1d68262e64998203a6d686308f4a7e15b13f67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shutdownScript")
    def shutdown_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shutdownScript"))

    @shutdown_script.setter
    def shutdown_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efff9e1133251a9fd6d457ef2b83d15697c119643cf0d2ea36fad9deb23df5f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shutdownScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotPercentage")
    def spot_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotPercentage"))

    @spot_percentage.setter
    def spot_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3163b95d7705de7c3f138afd6e20179e6aac8a038681bce0abe6fc427cf6362b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__211d5158d50e5dc6104a7047fd6999f54d55b3ad5e32425235be5773bcea436d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmNamePrefix")
    def vm_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmNamePrefix"))

    @vm_name_prefix.setter
    def vm_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__941d3ce2be3b425d1ce45bfb648229dc55aa6d31c92ad4b4f1a467f161733808)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zones")
    def zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "zones"))

    @zones.setter
    def zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ba1e8727122a82b61c9c501c52a2672ce780724dfd89b0c6922b528eaff4f9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zones", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3BootDiagnostics",
    jsii_struct_bases=[],
    name_mapping={
        "is_enabled": "isEnabled",
        "type": "type",
        "storage_url": "storageUrl",
    },
)
class ElastigroupAzureV3BootDiagnostics:
    def __init__(
        self,
        *,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        type: builtins.str,
        storage_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        :param storage_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#storage_url ElastigroupAzureV3#storage_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eef5e3545af66379d3983dc38a14ae456b317527581fe9017f71ae0f6eb27f7)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument storage_url", value=storage_url, expected_type=type_hints["storage_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "is_enabled": is_enabled,
            "type": type,
        }
        if storage_url is not None:
            self._values["storage_url"] = storage_url

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def storage_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#storage_url ElastigroupAzureV3#storage_url}.'''
        result = self._values.get("storage_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3BootDiagnostics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3BootDiagnosticsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3BootDiagnosticsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7fe6ca23069d5fb6bd6ca349d8d332b23f14d7a8412de0786a87b653c6ba18d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3BootDiagnosticsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31f82674e73634a0ffb9e957d568240d373426bc7c5c2d4fd507cfbe6dec6a6d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3BootDiagnosticsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7d55ca278df0951079a9e707ee9d86c737c8a2181be3ed92cfa666fba5ba1b8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebc50c4b194ccc11ce247b2a706a376e3a2f1b81766729aa636f1883b8ea62f2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3329c721f31a45523c72859b79895276281160f2f8ee022064611c4d6428c86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3BootDiagnostics]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3BootDiagnostics]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3BootDiagnostics]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78d6cec60ffe47ccdc3f734012b9c3df7645aa36761b99ebaa5801fefe0348b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3BootDiagnosticsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3BootDiagnosticsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9dfaee2f86aa3e885ca69e57a17eb23aeec24db8f0e46937012bdaf3d04c3eac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetStorageUrl")
    def reset_storage_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageUrl", []))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="storageUrlInput")
    def storage_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ebd3560836475940028d483df552cf7a0e6f85a7e6ec2717856e5486d6e92f1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageUrl")
    def storage_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageUrl"))

    @storage_url.setter
    def storage_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a38150c5741deed8e50ac654681c02fa759ef132723ff29081582c3120ac65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a115b638996ea60825c36d79e907019900297b9e2eb27690d93f9116ad9a8f75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3BootDiagnostics]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3BootDiagnostics]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3BootDiagnostics]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__115b5b6bfb5b6b91504ac749a90feb473f303fcfa5f990776a0619c0cf58e948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3CapacityReservation",
    jsii_struct_bases=[],
    name_mapping={
        "should_utilize": "shouldUtilize",
        "utilization_strategy": "utilizationStrategy",
        "capacity_reservation_groups": "capacityReservationGroups",
    },
)
class ElastigroupAzureV3CapacityReservation:
    def __init__(
        self,
        *,
        should_utilize: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        utilization_strategy: builtins.str,
        capacity_reservation_groups: typing.Optional[typing.Union["ElastigroupAzureV3CapacityReservationCapacityReservationGroups", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_utilize: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#should_utilize ElastigroupAzureV3#should_utilize}.
        :param utilization_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#utilization_strategy ElastigroupAzureV3#utilization_strategy}.
        :param capacity_reservation_groups: capacity_reservation_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#capacity_reservation_groups ElastigroupAzureV3#capacity_reservation_groups}
        '''
        if isinstance(capacity_reservation_groups, dict):
            capacity_reservation_groups = ElastigroupAzureV3CapacityReservationCapacityReservationGroups(**capacity_reservation_groups)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd6fbce92548bb2c5736104ae5cece13fc7dac1db28b1ef3926ccffa9bc3c4ec)
            check_type(argname="argument should_utilize", value=should_utilize, expected_type=type_hints["should_utilize"])
            check_type(argname="argument utilization_strategy", value=utilization_strategy, expected_type=type_hints["utilization_strategy"])
            check_type(argname="argument capacity_reservation_groups", value=capacity_reservation_groups, expected_type=type_hints["capacity_reservation_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "should_utilize": should_utilize,
            "utilization_strategy": utilization_strategy,
        }
        if capacity_reservation_groups is not None:
            self._values["capacity_reservation_groups"] = capacity_reservation_groups

    @builtins.property
    def should_utilize(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#should_utilize ElastigroupAzureV3#should_utilize}.'''
        result = self._values.get("should_utilize")
        assert result is not None, "Required property 'should_utilize' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def utilization_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#utilization_strategy ElastigroupAzureV3#utilization_strategy}.'''
        result = self._values.get("utilization_strategy")
        assert result is not None, "Required property 'utilization_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity_reservation_groups(
        self,
    ) -> typing.Optional["ElastigroupAzureV3CapacityReservationCapacityReservationGroups"]:
        '''capacity_reservation_groups block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#capacity_reservation_groups ElastigroupAzureV3#capacity_reservation_groups}
        '''
        result = self._values.get("capacity_reservation_groups")
        return typing.cast(typing.Optional["ElastigroupAzureV3CapacityReservationCapacityReservationGroups"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3CapacityReservation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3CapacityReservationCapacityReservationGroups",
    jsii_struct_bases=[],
    name_mapping={
        "crg_name": "crgName",
        "crg_resource_group_name": "crgResourceGroupName",
        "crg_should_prioritize": "crgShouldPrioritize",
    },
)
class ElastigroupAzureV3CapacityReservationCapacityReservationGroups:
    def __init__(
        self,
        *,
        crg_name: builtins.str,
        crg_resource_group_name: builtins.str,
        crg_should_prioritize: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param crg_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_name ElastigroupAzureV3#crg_name}.
        :param crg_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_resource_group_name ElastigroupAzureV3#crg_resource_group_name}.
        :param crg_should_prioritize: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_should_prioritize ElastigroupAzureV3#crg_should_prioritize}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac9ce427b5240fa4e58b6a8b76a380a3b1dc06c7d40c5e003a060f8eedd076b1)
            check_type(argname="argument crg_name", value=crg_name, expected_type=type_hints["crg_name"])
            check_type(argname="argument crg_resource_group_name", value=crg_resource_group_name, expected_type=type_hints["crg_resource_group_name"])
            check_type(argname="argument crg_should_prioritize", value=crg_should_prioritize, expected_type=type_hints["crg_should_prioritize"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "crg_name": crg_name,
            "crg_resource_group_name": crg_resource_group_name,
        }
        if crg_should_prioritize is not None:
            self._values["crg_should_prioritize"] = crg_should_prioritize

    @builtins.property
    def crg_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_name ElastigroupAzureV3#crg_name}.'''
        result = self._values.get("crg_name")
        assert result is not None, "Required property 'crg_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def crg_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_resource_group_name ElastigroupAzureV3#crg_resource_group_name}.'''
        result = self._values.get("crg_resource_group_name")
        assert result is not None, "Required property 'crg_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def crg_should_prioritize(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_should_prioritize ElastigroupAzureV3#crg_should_prioritize}.'''
        result = self._values.get("crg_should_prioritize")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3CapacityReservationCapacityReservationGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3CapacityReservationCapacityReservationGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3CapacityReservationCapacityReservationGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ab032a90ccfe39842606c8ef487d5e057c47eae252efee3a69c883b492164a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCrgShouldPrioritize")
    def reset_crg_should_prioritize(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrgShouldPrioritize", []))

    @builtins.property
    @jsii.member(jsii_name="crgNameInput")
    def crg_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crgNameInput"))

    @builtins.property
    @jsii.member(jsii_name="crgResourceGroupNameInput")
    def crg_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crgResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="crgShouldPrioritizeInput")
    def crg_should_prioritize_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "crgShouldPrioritizeInput"))

    @builtins.property
    @jsii.member(jsii_name="crgName")
    def crg_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crgName"))

    @crg_name.setter
    def crg_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6516a292486414dd2cb31fef4c961cc3d78cfee5df77f250aba3b30d3eb6446)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crgName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crgResourceGroupName")
    def crg_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crgResourceGroupName"))

    @crg_resource_group_name.setter
    def crg_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cc14c6ee052d0582dd018f0779c39381a2c8a43885e31c9fd9c5b3b2b76d2b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crgResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crgShouldPrioritize")
    def crg_should_prioritize(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "crgShouldPrioritize"))

    @crg_should_prioritize.setter
    def crg_should_prioritize(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8396decf2e5c9b57456ceb6585456fe2b8f2d026800830ebb7b06db65f311b85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crgShouldPrioritize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAzureV3CapacityReservationCapacityReservationGroups]:
        return typing.cast(typing.Optional[ElastigroupAzureV3CapacityReservationCapacityReservationGroups], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3CapacityReservationCapacityReservationGroups],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f4edad139e119552229742ab8b781116e6d98dec87232f221926bfe42adc5c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3CapacityReservationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3CapacityReservationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b224cbd8fec348b5c867a4b4e01df1548569bb31d9be468df73f20c7a0e5ac69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCapacityReservationGroups")
    def put_capacity_reservation_groups(
        self,
        *,
        crg_name: builtins.str,
        crg_resource_group_name: builtins.str,
        crg_should_prioritize: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param crg_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_name ElastigroupAzureV3#crg_name}.
        :param crg_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_resource_group_name ElastigroupAzureV3#crg_resource_group_name}.
        :param crg_should_prioritize: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#crg_should_prioritize ElastigroupAzureV3#crg_should_prioritize}.
        '''
        value = ElastigroupAzureV3CapacityReservationCapacityReservationGroups(
            crg_name=crg_name,
            crg_resource_group_name=crg_resource_group_name,
            crg_should_prioritize=crg_should_prioritize,
        )

        return typing.cast(None, jsii.invoke(self, "putCapacityReservationGroups", [value]))

    @jsii.member(jsii_name="resetCapacityReservationGroups")
    def reset_capacity_reservation_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityReservationGroups", []))

    @builtins.property
    @jsii.member(jsii_name="capacityReservationGroups")
    def capacity_reservation_groups(
        self,
    ) -> ElastigroupAzureV3CapacityReservationCapacityReservationGroupsOutputReference:
        return typing.cast(ElastigroupAzureV3CapacityReservationCapacityReservationGroupsOutputReference, jsii.get(self, "capacityReservationGroups"))

    @builtins.property
    @jsii.member(jsii_name="capacityReservationGroupsInput")
    def capacity_reservation_groups_input(
        self,
    ) -> typing.Optional[ElastigroupAzureV3CapacityReservationCapacityReservationGroups]:
        return typing.cast(typing.Optional[ElastigroupAzureV3CapacityReservationCapacityReservationGroups], jsii.get(self, "capacityReservationGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldUtilizeInput")
    def should_utilize_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldUtilizeInput"))

    @builtins.property
    @jsii.member(jsii_name="utilizationStrategyInput")
    def utilization_strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "utilizationStrategyInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldUtilize")
    def should_utilize(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldUtilize"))

    @should_utilize.setter
    def should_utilize(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b40124d5e3c783677f21c232da3562cbe3b0c287ae41036e92ae9b725f83ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldUtilize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="utilizationStrategy")
    def utilization_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "utilizationStrategy"))

    @utilization_strategy.setter
    def utilization_strategy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f91ec31dc485d3aeb9b090b51cdcceb46980a1372d22865dab5231d730ef12f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utilizationStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3CapacityReservation]:
        return typing.cast(typing.Optional[ElastigroupAzureV3CapacityReservation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3CapacityReservation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2acd91c16765f10d4846eeeef3c361654d0898faf5bc9f3571473190c3e2221)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "fallback_to_on_demand": "fallbackToOnDemand",
        "name": "name",
        "network": "network",
        "os": "os",
        "region": "region",
        "resource_group_name": "resourceGroupName",
        "vm_sizes": "vmSizes",
        "availability_vs_cost": "availabilityVsCost",
        "boot_diagnostics": "bootDiagnostics",
        "capacity_reservation": "capacityReservation",
        "custom_data": "customData",
        "data_disk": "dataDisk",
        "description": "description",
        "desired_capacity": "desiredCapacity",
        "draining_timeout": "drainingTimeout",
        "extensions": "extensions",
        "health": "health",
        "id": "id",
        "image": "image",
        "load_balancer": "loadBalancer",
        "login": "login",
        "managed_service_identity": "managedServiceIdentity",
        "max_size": "maxSize",
        "min_size": "minSize",
        "on_demand_count": "onDemandCount",
        "optimization_windows": "optimizationWindows",
        "os_disk": "osDisk",
        "preferred_zones": "preferredZones",
        "proximity_placement_groups": "proximityPlacementGroups",
        "revert_to_spot": "revertToSpot",
        "scaling_down_policy": "scalingDownPolicy",
        "scaling_up_policy": "scalingUpPolicy",
        "scheduling_task": "schedulingTask",
        "secret": "secret",
        "security": "security",
        "shutdown_script": "shutdownScript",
        "signal": "signal",
        "spot_percentage": "spotPercentage",
        "tags": "tags",
        "user_data": "userData",
        "vm_name_prefix": "vmNamePrefix",
        "zones": "zones",
    },
)
class ElastigroupAzureV3Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        name: builtins.str,
        network: typing.Union["ElastigroupAzureV3Network", typing.Dict[builtins.str, typing.Any]],
        os: builtins.str,
        region: builtins.str,
        resource_group_name: builtins.str,
        vm_sizes: typing.Union["ElastigroupAzureV3VmSizes", typing.Dict[builtins.str, typing.Any]],
        availability_vs_cost: typing.Optional[jsii.Number] = None,
        boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3BootDiagnostics, typing.Dict[builtins.str, typing.Any]]]]] = None,
        capacity_reservation: typing.Optional[typing.Union[ElastigroupAzureV3CapacityReservation, typing.Dict[builtins.str, typing.Any]]] = None,
        custom_data: typing.Optional[builtins.str] = None,
        data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3DataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Extensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        health: typing.Optional[typing.Union["ElastigroupAzureV3Health", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Image", typing.Dict[builtins.str, typing.Any]]]]] = None,
        load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3LoadBalancer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        login: typing.Optional[typing.Union["ElastigroupAzureV3Login", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_service_identity: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ManagedServiceIdentity", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        on_demand_count: typing.Optional[jsii.Number] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        os_disk: typing.Optional[typing.Union["ElastigroupAzureV3OsDisk", typing.Dict[builtins.str, typing.Any]]] = None,
        preferred_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ProximityPlacementGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        revert_to_spot: typing.Optional[typing.Union["ElastigroupAzureV3RevertToSpot", typing.Dict[builtins.str, typing.Any]]] = None,
        scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Secret", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security: typing.Optional[typing.Union["ElastigroupAzureV3Security", typing.Dict[builtins.str, typing.Any]]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Signal", typing.Dict[builtins.str, typing.Any]]]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3Tags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        user_data: typing.Optional[builtins.str] = None,
        vm_name_prefix: typing.Optional[builtins.str] = None,
        zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param fallback_to_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#fallback_to_on_demand ElastigroupAzureV3#fallback_to_on_demand}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#network ElastigroupAzureV3#network}
        :param os: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#os ElastigroupAzureV3#os}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#region ElastigroupAzureV3#region}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        :param vm_sizes: vm_sizes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vm_sizes ElastigroupAzureV3#vm_sizes}
        :param availability_vs_cost: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#availability_vs_cost ElastigroupAzureV3#availability_vs_cost}.
        :param boot_diagnostics: boot_diagnostics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#boot_diagnostics ElastigroupAzureV3#boot_diagnostics}
        :param capacity_reservation: capacity_reservation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#capacity_reservation ElastigroupAzureV3#capacity_reservation}
        :param custom_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#custom_data ElastigroupAzureV3#custom_data}.
        :param data_disk: data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#data_disk ElastigroupAzureV3#data_disk}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#description ElastigroupAzureV3#description}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#desired_capacity ElastigroupAzureV3#desired_capacity}.
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#draining_timeout ElastigroupAzureV3#draining_timeout}.
        :param extensions: extensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#extensions ElastigroupAzureV3#extensions}
        :param health: health block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#health ElastigroupAzureV3#health}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#id ElastigroupAzureV3#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image: image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image ElastigroupAzureV3#image}
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#load_balancer ElastigroupAzureV3#load_balancer}
        :param login: login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#login ElastigroupAzureV3#login}
        :param managed_service_identity: managed_service_identity block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#managed_service_identity ElastigroupAzureV3#managed_service_identity}
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_size ElastigroupAzureV3#max_size}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_size ElastigroupAzureV3#min_size}.
        :param on_demand_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#on_demand_count ElastigroupAzureV3#on_demand_count}.
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#optimization_windows ElastigroupAzureV3#optimization_windows}.
        :param os_disk: os_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#os_disk ElastigroupAzureV3#os_disk}
        :param preferred_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#preferred_zones ElastigroupAzureV3#preferred_zones}.
        :param proximity_placement_groups: proximity_placement_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#proximity_placement_groups ElastigroupAzureV3#proximity_placement_groups}
        :param revert_to_spot: revert_to_spot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#revert_to_spot ElastigroupAzureV3#revert_to_spot}
        :param scaling_down_policy: scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scaling_down_policy ElastigroupAzureV3#scaling_down_policy}
        :param scaling_up_policy: scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scaling_up_policy ElastigroupAzureV3#scaling_up_policy}
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scheduling_task ElastigroupAzureV3#scheduling_task}
        :param secret: secret block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secret ElastigroupAzureV3#secret}
        :param security: security block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security ElastigroupAzureV3#security}
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#shutdown_script ElastigroupAzureV3#shutdown_script}.
        :param signal: signal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#signal ElastigroupAzureV3#signal}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_percentage ElastigroupAzureV3#spot_percentage}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#tags ElastigroupAzureV3#tags}
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#user_data ElastigroupAzureV3#user_data}.
        :param vm_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vm_name_prefix ElastigroupAzureV3#vm_name_prefix}.
        :param zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#zones ElastigroupAzureV3#zones}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(network, dict):
            network = ElastigroupAzureV3Network(**network)
        if isinstance(vm_sizes, dict):
            vm_sizes = ElastigroupAzureV3VmSizes(**vm_sizes)
        if isinstance(capacity_reservation, dict):
            capacity_reservation = ElastigroupAzureV3CapacityReservation(**capacity_reservation)
        if isinstance(health, dict):
            health = ElastigroupAzureV3Health(**health)
        if isinstance(login, dict):
            login = ElastigroupAzureV3Login(**login)
        if isinstance(os_disk, dict):
            os_disk = ElastigroupAzureV3OsDisk(**os_disk)
        if isinstance(revert_to_spot, dict):
            revert_to_spot = ElastigroupAzureV3RevertToSpot(**revert_to_spot)
        if isinstance(security, dict):
            security = ElastigroupAzureV3Security(**security)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a37fe9b0cf973e4644ab1bc2acecfc0f26ff2d3f60a2da163bfb6cf20b5f8d38)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument fallback_to_on_demand", value=fallback_to_on_demand, expected_type=type_hints["fallback_to_on_demand"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument os", value=os, expected_type=type_hints["os"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument vm_sizes", value=vm_sizes, expected_type=type_hints["vm_sizes"])
            check_type(argname="argument availability_vs_cost", value=availability_vs_cost, expected_type=type_hints["availability_vs_cost"])
            check_type(argname="argument boot_diagnostics", value=boot_diagnostics, expected_type=type_hints["boot_diagnostics"])
            check_type(argname="argument capacity_reservation", value=capacity_reservation, expected_type=type_hints["capacity_reservation"])
            check_type(argname="argument custom_data", value=custom_data, expected_type=type_hints["custom_data"])
            check_type(argname="argument data_disk", value=data_disk, expected_type=type_hints["data_disk"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument extensions", value=extensions, expected_type=type_hints["extensions"])
            check_type(argname="argument health", value=health, expected_type=type_hints["health"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument login", value=login, expected_type=type_hints["login"])
            check_type(argname="argument managed_service_identity", value=managed_service_identity, expected_type=type_hints["managed_service_identity"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument on_demand_count", value=on_demand_count, expected_type=type_hints["on_demand_count"])
            check_type(argname="argument optimization_windows", value=optimization_windows, expected_type=type_hints["optimization_windows"])
            check_type(argname="argument os_disk", value=os_disk, expected_type=type_hints["os_disk"])
            check_type(argname="argument preferred_zones", value=preferred_zones, expected_type=type_hints["preferred_zones"])
            check_type(argname="argument proximity_placement_groups", value=proximity_placement_groups, expected_type=type_hints["proximity_placement_groups"])
            check_type(argname="argument revert_to_spot", value=revert_to_spot, expected_type=type_hints["revert_to_spot"])
            check_type(argname="argument scaling_down_policy", value=scaling_down_policy, expected_type=type_hints["scaling_down_policy"])
            check_type(argname="argument scaling_up_policy", value=scaling_up_policy, expected_type=type_hints["scaling_up_policy"])
            check_type(argname="argument scheduling_task", value=scheduling_task, expected_type=type_hints["scheduling_task"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument security", value=security, expected_type=type_hints["security"])
            check_type(argname="argument shutdown_script", value=shutdown_script, expected_type=type_hints["shutdown_script"])
            check_type(argname="argument signal", value=signal, expected_type=type_hints["signal"])
            check_type(argname="argument spot_percentage", value=spot_percentage, expected_type=type_hints["spot_percentage"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument vm_name_prefix", value=vm_name_prefix, expected_type=type_hints["vm_name_prefix"])
            check_type(argname="argument zones", value=zones, expected_type=type_hints["zones"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fallback_to_on_demand": fallback_to_on_demand,
            "name": name,
            "network": network,
            "os": os,
            "region": region,
            "resource_group_name": resource_group_name,
            "vm_sizes": vm_sizes,
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
        if availability_vs_cost is not None:
            self._values["availability_vs_cost"] = availability_vs_cost
        if boot_diagnostics is not None:
            self._values["boot_diagnostics"] = boot_diagnostics
        if capacity_reservation is not None:
            self._values["capacity_reservation"] = capacity_reservation
        if custom_data is not None:
            self._values["custom_data"] = custom_data
        if data_disk is not None:
            self._values["data_disk"] = data_disk
        if description is not None:
            self._values["description"] = description
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if extensions is not None:
            self._values["extensions"] = extensions
        if health is not None:
            self._values["health"] = health
        if id is not None:
            self._values["id"] = id
        if image is not None:
            self._values["image"] = image
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if login is not None:
            self._values["login"] = login
        if managed_service_identity is not None:
            self._values["managed_service_identity"] = managed_service_identity
        if max_size is not None:
            self._values["max_size"] = max_size
        if min_size is not None:
            self._values["min_size"] = min_size
        if on_demand_count is not None:
            self._values["on_demand_count"] = on_demand_count
        if optimization_windows is not None:
            self._values["optimization_windows"] = optimization_windows
        if os_disk is not None:
            self._values["os_disk"] = os_disk
        if preferred_zones is not None:
            self._values["preferred_zones"] = preferred_zones
        if proximity_placement_groups is not None:
            self._values["proximity_placement_groups"] = proximity_placement_groups
        if revert_to_spot is not None:
            self._values["revert_to_spot"] = revert_to_spot
        if scaling_down_policy is not None:
            self._values["scaling_down_policy"] = scaling_down_policy
        if scaling_up_policy is not None:
            self._values["scaling_up_policy"] = scaling_up_policy
        if scheduling_task is not None:
            self._values["scheduling_task"] = scheduling_task
        if secret is not None:
            self._values["secret"] = secret
        if security is not None:
            self._values["security"] = security
        if shutdown_script is not None:
            self._values["shutdown_script"] = shutdown_script
        if signal is not None:
            self._values["signal"] = signal
        if spot_percentage is not None:
            self._values["spot_percentage"] = spot_percentage
        if tags is not None:
            self._values["tags"] = tags
        if user_data is not None:
            self._values["user_data"] = user_data
        if vm_name_prefix is not None:
            self._values["vm_name_prefix"] = vm_name_prefix
        if zones is not None:
            self._values["zones"] = zones

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
    def fallback_to_on_demand(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#fallback_to_on_demand ElastigroupAzureV3#fallback_to_on_demand}.'''
        result = self._values.get("fallback_to_on_demand")
        assert result is not None, "Required property 'fallback_to_on_demand' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network(self) -> "ElastigroupAzureV3Network":
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#network ElastigroupAzureV3#network}
        '''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast("ElastigroupAzureV3Network", result)

    @builtins.property
    def os(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#os ElastigroupAzureV3#os}.'''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#region ElastigroupAzureV3#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vm_sizes(self) -> "ElastigroupAzureV3VmSizes":
        '''vm_sizes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vm_sizes ElastigroupAzureV3#vm_sizes}
        '''
        result = self._values.get("vm_sizes")
        assert result is not None, "Required property 'vm_sizes' is missing"
        return typing.cast("ElastigroupAzureV3VmSizes", result)

    @builtins.property
    def availability_vs_cost(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#availability_vs_cost ElastigroupAzureV3#availability_vs_cost}.'''
        result = self._values.get("availability_vs_cost")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def boot_diagnostics(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3BootDiagnostics]]]:
        '''boot_diagnostics block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#boot_diagnostics ElastigroupAzureV3#boot_diagnostics}
        '''
        result = self._values.get("boot_diagnostics")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3BootDiagnostics]]], result)

    @builtins.property
    def capacity_reservation(
        self,
    ) -> typing.Optional[ElastigroupAzureV3CapacityReservation]:
        '''capacity_reservation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#capacity_reservation ElastigroupAzureV3#capacity_reservation}
        '''
        result = self._values.get("capacity_reservation")
        return typing.cast(typing.Optional[ElastigroupAzureV3CapacityReservation], result)

    @builtins.property
    def custom_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#custom_data ElastigroupAzureV3#custom_data}.'''
        result = self._values.get("custom_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_disk(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3DataDisk"]]]:
        '''data_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#data_disk ElastigroupAzureV3#data_disk}
        '''
        result = self._values.get("data_disk")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3DataDisk"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#description ElastigroupAzureV3#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#desired_capacity ElastigroupAzureV3#desired_capacity}.'''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#draining_timeout ElastigroupAzureV3#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def extensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Extensions"]]]:
        '''extensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#extensions ElastigroupAzureV3#extensions}
        '''
        result = self._values.get("extensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Extensions"]]], result)

    @builtins.property
    def health(self) -> typing.Optional["ElastigroupAzureV3Health"]:
        '''health block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#health ElastigroupAzureV3#health}
        '''
        result = self._values.get("health")
        return typing.cast(typing.Optional["ElastigroupAzureV3Health"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#id ElastigroupAzureV3#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Image"]]]:
        '''image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image ElastigroupAzureV3#image}
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Image"]]], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3LoadBalancer"]]]:
        '''load_balancer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#load_balancer ElastigroupAzureV3#load_balancer}
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3LoadBalancer"]]], result)

    @builtins.property
    def login(self) -> typing.Optional["ElastigroupAzureV3Login"]:
        '''login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#login ElastigroupAzureV3#login}
        '''
        result = self._values.get("login")
        return typing.cast(typing.Optional["ElastigroupAzureV3Login"], result)

    @builtins.property
    def managed_service_identity(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ManagedServiceIdentity"]]]:
        '''managed_service_identity block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#managed_service_identity ElastigroupAzureV3#managed_service_identity}
        '''
        result = self._values.get("managed_service_identity")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ManagedServiceIdentity"]]], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_size ElastigroupAzureV3#max_size}.'''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_size ElastigroupAzureV3#min_size}.'''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def on_demand_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#on_demand_count ElastigroupAzureV3#on_demand_count}.'''
        result = self._values.get("on_demand_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def optimization_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#optimization_windows ElastigroupAzureV3#optimization_windows}.'''
        result = self._values.get("optimization_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def os_disk(self) -> typing.Optional["ElastigroupAzureV3OsDisk"]:
        '''os_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#os_disk ElastigroupAzureV3#os_disk}
        '''
        result = self._values.get("os_disk")
        return typing.cast(typing.Optional["ElastigroupAzureV3OsDisk"], result)

    @builtins.property
    def preferred_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#preferred_zones ElastigroupAzureV3#preferred_zones}.'''
        result = self._values.get("preferred_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def proximity_placement_groups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ProximityPlacementGroups"]]]:
        '''proximity_placement_groups block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#proximity_placement_groups ElastigroupAzureV3#proximity_placement_groups}
        '''
        result = self._values.get("proximity_placement_groups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ProximityPlacementGroups"]]], result)

    @builtins.property
    def revert_to_spot(self) -> typing.Optional["ElastigroupAzureV3RevertToSpot"]:
        '''revert_to_spot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#revert_to_spot ElastigroupAzureV3#revert_to_spot}
        '''
        result = self._values.get("revert_to_spot")
        return typing.cast(typing.Optional["ElastigroupAzureV3RevertToSpot"], result)

    @builtins.property
    def scaling_down_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingDownPolicy"]]]:
        '''scaling_down_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scaling_down_policy ElastigroupAzureV3#scaling_down_policy}
        '''
        result = self._values.get("scaling_down_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingDownPolicy"]]], result)

    @builtins.property
    def scaling_up_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingUpPolicy"]]]:
        '''scaling_up_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scaling_up_policy ElastigroupAzureV3#scaling_up_policy}
        '''
        result = self._values.get("scaling_up_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingUpPolicy"]]], result)

    @builtins.property
    def scheduling_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SchedulingTask"]]]:
        '''scheduling_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scheduling_task ElastigroupAzureV3#scheduling_task}
        '''
        result = self._values.get("scheduling_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SchedulingTask"]]], result)

    @builtins.property
    def secret(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Secret"]]]:
        '''secret block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secret ElastigroupAzureV3#secret}
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Secret"]]], result)

    @builtins.property
    def security(self) -> typing.Optional["ElastigroupAzureV3Security"]:
        '''security block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security ElastigroupAzureV3#security}
        '''
        result = self._values.get("security")
        return typing.cast(typing.Optional["ElastigroupAzureV3Security"], result)

    @builtins.property
    def shutdown_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#shutdown_script ElastigroupAzureV3#shutdown_script}.'''
        result = self._values.get("shutdown_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signal(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Signal"]]]:
        '''signal block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#signal ElastigroupAzureV3#signal}
        '''
        result = self._values.get("signal")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Signal"]]], result)

    @builtins.property
    def spot_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_percentage ElastigroupAzureV3#spot_percentage}.'''
        result = self._values.get("spot_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Tags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#tags ElastigroupAzureV3#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3Tags"]]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#user_data ElastigroupAzureV3#user_data}.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vm_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vm_name_prefix ElastigroupAzureV3#vm_name_prefix}.'''
        result = self._values.get("vm_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#zones ElastigroupAzureV3#zones}.'''
        result = self._values.get("zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3DataDisk",
    jsii_struct_bases=[],
    name_mapping={"lun": "lun", "size_gb": "sizeGb", "type": "type"},
)
class ElastigroupAzureV3DataDisk:
    def __init__(
        self,
        *,
        lun: jsii.Number,
        size_gb: jsii.Number,
        type: builtins.str,
    ) -> None:
        '''
        :param lun: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#lun ElastigroupAzureV3#lun}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#size_gb ElastigroupAzureV3#size_gb}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc5161096580d5153bfa1860887cd86f225390880373a056fb0f793ad013ea99)
            check_type(argname="argument lun", value=lun, expected_type=type_hints["lun"])
            check_type(argname="argument size_gb", value=size_gb, expected_type=type_hints["size_gb"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lun": lun,
            "size_gb": size_gb,
            "type": type,
        }

    @builtins.property
    def lun(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#lun ElastigroupAzureV3#lun}.'''
        result = self._values.get("lun")
        assert result is not None, "Required property 'lun' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size_gb(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#size_gb ElastigroupAzureV3#size_gb}.'''
        result = self._values.get("size_gb")
        assert result is not None, "Required property 'size_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3DataDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3DataDiskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3DataDiskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__569bdd3f03f7036b18a92718f31d2dd928a7a5692ad852cadbecbe1571784877)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3DataDiskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__259c03a256acd7a749d5130c273b053f72aabc7b84bd31247cd5c5f160c41e66)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3DataDiskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b46efc73f909045a9056eb38eeed8dddf11a6005f261756c8931693429e318a1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7a06a0161c46a340ef30b73b6b433bc4dbe2c99a4c58d2185b42156cbd0993a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e6cd38bd7cc32199e69591044a94d73563fc39582d2bf37be48fafd54626b2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3DataDisk]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3DataDisk]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3DataDisk]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e7a1a3807e838855c981cd4ed5eec47484dc0af37f9f40064f413374ed41e9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3DataDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3DataDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2428790c2d07819633a0cb91e9db3f19ae4f7755856d1a13d0b1f296171cb698)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="lunInput")
    def lun_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lunInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeGbInput")
    def size_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="lun")
    def lun(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lun"))

    @lun.setter
    def lun(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d48f909a5c42b9f486b45f14d7269366945afab61ebe749a985b83844b46767)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeGb")
    def size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeGb"))

    @size_gb.setter
    def size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a835d6eab9ffe8901265886ab61a8c781591f25eeb52cb30e417c08d32dde74f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8dac3d972b30529ca8de993bccb29a0d704a07c30f9df2801560119c9c6c451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3DataDisk]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3DataDisk]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3DataDisk]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a228a7b4db98073def9347347a3f99ba5bd58a008703a16ba85ce9fd484fccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Extensions",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "minor_version_auto_upgrade": "minorVersionAutoUpgrade",
        "name": "name",
        "publisher": "publisher",
        "type": "type",
        "enable_automatic_upgrade": "enableAutomaticUpgrade",
        "protected_settings": "protectedSettings",
        "protected_settings_from_key_vault": "protectedSettingsFromKeyVault",
        "public_settings": "publicSettings",
    },
)
class ElastigroupAzureV3Extensions:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        minor_version_auto_upgrade: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        name: builtins.str,
        publisher: builtins.str,
        type: builtins.str,
        enable_automatic_upgrade: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        protected_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        protected_settings_from_key_vault: typing.Optional[typing.Union["ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault", typing.Dict[builtins.str, typing.Any]]] = None,
        public_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#api_version ElastigroupAzureV3#api_version}.
        :param minor_version_auto_upgrade: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minor_version_auto_upgrade ElastigroupAzureV3#minor_version_auto_upgrade}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param publisher: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#publisher ElastigroupAzureV3#publisher}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        :param enable_automatic_upgrade: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#enable_automatic_upgrade ElastigroupAzureV3#enable_automatic_upgrade}.
        :param protected_settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#protected_settings ElastigroupAzureV3#protected_settings}.
        :param protected_settings_from_key_vault: protected_settings_from_key_vault block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#protected_settings_from_key_vault ElastigroupAzureV3#protected_settings_from_key_vault}
        :param public_settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#public_settings ElastigroupAzureV3#public_settings}.
        '''
        if isinstance(protected_settings_from_key_vault, dict):
            protected_settings_from_key_vault = ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault(**protected_settings_from_key_vault)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3517ca943a243395911aacbcdd6a7ec6814e1dda63b8396dce780fdf506b8192)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument minor_version_auto_upgrade", value=minor_version_auto_upgrade, expected_type=type_hints["minor_version_auto_upgrade"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument publisher", value=publisher, expected_type=type_hints["publisher"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument enable_automatic_upgrade", value=enable_automatic_upgrade, expected_type=type_hints["enable_automatic_upgrade"])
            check_type(argname="argument protected_settings", value=protected_settings, expected_type=type_hints["protected_settings"])
            check_type(argname="argument protected_settings_from_key_vault", value=protected_settings_from_key_vault, expected_type=type_hints["protected_settings_from_key_vault"])
            check_type(argname="argument public_settings", value=public_settings, expected_type=type_hints["public_settings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "minor_version_auto_upgrade": minor_version_auto_upgrade,
            "name": name,
            "publisher": publisher,
            "type": type,
        }
        if enable_automatic_upgrade is not None:
            self._values["enable_automatic_upgrade"] = enable_automatic_upgrade
        if protected_settings is not None:
            self._values["protected_settings"] = protected_settings
        if protected_settings_from_key_vault is not None:
            self._values["protected_settings_from_key_vault"] = protected_settings_from_key_vault
        if public_settings is not None:
            self._values["public_settings"] = public_settings

    @builtins.property
    def api_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#api_version ElastigroupAzureV3#api_version}.'''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def minor_version_auto_upgrade(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minor_version_auto_upgrade ElastigroupAzureV3#minor_version_auto_upgrade}.'''
        result = self._values.get("minor_version_auto_upgrade")
        assert result is not None, "Required property 'minor_version_auto_upgrade' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def publisher(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#publisher ElastigroupAzureV3#publisher}.'''
        result = self._values.get("publisher")
        assert result is not None, "Required property 'publisher' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enable_automatic_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#enable_automatic_upgrade ElastigroupAzureV3#enable_automatic_upgrade}.'''
        result = self._values.get("enable_automatic_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def protected_settings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#protected_settings ElastigroupAzureV3#protected_settings}.'''
        result = self._values.get("protected_settings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def protected_settings_from_key_vault(
        self,
    ) -> typing.Optional["ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault"]:
        '''protected_settings_from_key_vault block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#protected_settings_from_key_vault ElastigroupAzureV3#protected_settings_from_key_vault}
        '''
        result = self._values.get("protected_settings_from_key_vault")
        return typing.cast(typing.Optional["ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault"], result)

    @builtins.property
    def public_settings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#public_settings ElastigroupAzureV3#public_settings}.'''
        result = self._values.get("public_settings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Extensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ExtensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ExtensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a794e4897b72fa48a9797dc8e679081c9a86406c1e7b848c2b9a346d63e43a07)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3ExtensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57b6d5db0ddda376d2e281f91af90c30af3c9a6bac3ada740d10a3ca429b75c2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ExtensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e423d98296f349dee0f0d40f5833eba54f88da769c3f9d4d3d5bd7b1c7fb4dec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7ccaf1080500488c4fb9cf9fec97d7ef54daf3e9f1475c4d22fcc49f64ebd33)
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
            type_hints = typing.get_type_hints(_typecheckingstub__95b27c04141596c089522c7ecf83fde9bbf7497783d88837173e8d49b455e779)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Extensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Extensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Extensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9f5f6eda462eb113345df4764c082a48992321d31e6d3504a8b589b90deef8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ExtensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ExtensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a9b65bac0b1a5b40315d073ddd2d09cc51090f06840f0a7315ea4ae344b71a7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putProtectedSettingsFromKeyVault")
    def put_protected_settings_from_key_vault(
        self,
        *,
        secret_url: builtins.str,
        source_vault: builtins.str,
    ) -> None:
        '''
        :param secret_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secret_url ElastigroupAzureV3#secret_url}.
        :param source_vault: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source_vault ElastigroupAzureV3#source_vault}.
        '''
        value = ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault(
            secret_url=secret_url, source_vault=source_vault
        )

        return typing.cast(None, jsii.invoke(self, "putProtectedSettingsFromKeyVault", [value]))

    @jsii.member(jsii_name="resetEnableAutomaticUpgrade")
    def reset_enable_automatic_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAutomaticUpgrade", []))

    @jsii.member(jsii_name="resetProtectedSettings")
    def reset_protected_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectedSettings", []))

    @jsii.member(jsii_name="resetProtectedSettingsFromKeyVault")
    def reset_protected_settings_from_key_vault(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectedSettingsFromKeyVault", []))

    @jsii.member(jsii_name="resetPublicSettings")
    def reset_public_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicSettings", []))

    @builtins.property
    @jsii.member(jsii_name="protectedSettingsFromKeyVault")
    def protected_settings_from_key_vault(
        self,
    ) -> "ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVaultOutputReference":
        return typing.cast("ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVaultOutputReference", jsii.get(self, "protectedSettingsFromKeyVault"))

    @builtins.property
    @jsii.member(jsii_name="apiVersionInput")
    def api_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="enableAutomaticUpgradeInput")
    def enable_automatic_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableAutomaticUpgradeInput"))

    @builtins.property
    @jsii.member(jsii_name="minorVersionAutoUpgradeInput")
    def minor_version_auto_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "minorVersionAutoUpgradeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="protectedSettingsFromKeyVaultInput")
    def protected_settings_from_key_vault_input(
        self,
    ) -> typing.Optional["ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault"], jsii.get(self, "protectedSettingsFromKeyVaultInput"))

    @builtins.property
    @jsii.member(jsii_name="protectedSettingsInput")
    def protected_settings_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "protectedSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="publicSettingsInput")
    def public_settings_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "publicSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="publisherInput")
    def publisher_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publisherInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="apiVersion")
    def api_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiVersion"))

    @api_version.setter
    def api_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a88bbbd3ac9be42e52b30e2aee1985ef78a4d5f463e0a93e554b08b9d536c0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableAutomaticUpgrade")
    def enable_automatic_upgrade(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableAutomaticUpgrade"))

    @enable_automatic_upgrade.setter
    def enable_automatic_upgrade(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c55750ac08728d6390bd487f4c5f37c2aa2018e8974336d436991d32283c721)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableAutomaticUpgrade", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minorVersionAutoUpgrade")
    def minor_version_auto_upgrade(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "minorVersionAutoUpgrade"))

    @minor_version_auto_upgrade.setter
    def minor_version_auto_upgrade(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18e06e92c493fe99365d1d763e8fc015ae5bd053e20b98b366bcff15e5faf607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minorVersionAutoUpgrade", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73aa7cfcf8d2ac28e53f9dfd96434a6a468852566365a1296bd76bc7066a8743)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protectedSettings")
    def protected_settings(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "protectedSettings"))

    @protected_settings.setter
    def protected_settings(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18a46b3a416e778b6d7167df559f235905a0da99abd9afc4dbc48d407a31b041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protectedSettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicSettings")
    def public_settings(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "publicSettings"))

    @public_settings.setter
    def public_settings(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ec3600d68e0bed660ef99cb7e8b7204867a3f9ba6ee34bf7bd7067b7a6fb88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicSettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publisher")
    def publisher(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publisher"))

    @publisher.setter
    def publisher(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee4ba06bb79c306b17f2251c7233796c5ada3b22f1e19145a9c88ec776accbc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publisher", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9758d24eb1e003418cab425cc84f1c365bce6ad5be2bc5ab59fd406a108867dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Extensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Extensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Extensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7b28b9cc9e6e2aa685de786e93637341016ca4c96dfd2ddd62938c29ed6b23c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault",
    jsii_struct_bases=[],
    name_mapping={"secret_url": "secretUrl", "source_vault": "sourceVault"},
)
class ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault:
    def __init__(self, *, secret_url: builtins.str, source_vault: builtins.str) -> None:
        '''
        :param secret_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secret_url ElastigroupAzureV3#secret_url}.
        :param source_vault: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source_vault ElastigroupAzureV3#source_vault}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa7fc138808d94158de8ad6f983c431d14983b4dc5010033ec5356f4e3477f19)
            check_type(argname="argument secret_url", value=secret_url, expected_type=type_hints["secret_url"])
            check_type(argname="argument source_vault", value=source_vault, expected_type=type_hints["source_vault"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "secret_url": secret_url,
            "source_vault": source_vault,
        }

    @builtins.property
    def secret_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secret_url ElastigroupAzureV3#secret_url}.'''
        result = self._values.get("secret_url")
        assert result is not None, "Required property 'secret_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_vault(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source_vault ElastigroupAzureV3#source_vault}.'''
        result = self._values.get("source_vault")
        assert result is not None, "Required property 'source_vault' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVaultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVaultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3632ecd5d43457d2df55730bdeb6ab67e0f31d5f2d81c7398a5e1ab24a7167a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="secretUrlInput")
    def secret_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceVaultInput")
    def source_vault_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceVaultInput"))

    @builtins.property
    @jsii.member(jsii_name="secretUrl")
    def secret_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretUrl"))

    @secret_url.setter
    def secret_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bf30aab4c1a6c5fe04bbdead6c2ec7dfd0d774eb757645b1b4fe3246ae79e6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceVault")
    def source_vault(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceVault"))

    @source_vault.setter
    def source_vault(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddd64ac25153508a6f392b7817f4c59e649888b856edbc44be0827720f36a5f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceVault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault]:
        return typing.cast(typing.Optional[ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9fe197f07c9363da4ef25caec542492abcec9964de0f6348472d50190835bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Health",
    jsii_struct_bases=[],
    name_mapping={
        "auto_healing": "autoHealing",
        "grace_period": "gracePeriod",
        "health_check_types": "healthCheckTypes",
        "unhealthy_duration": "unhealthyDuration",
    },
)
class ElastigroupAzureV3Health:
    def __init__(
        self,
        *,
        auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        grace_period: typing.Optional[jsii.Number] = None,
        health_check_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        unhealthy_duration: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param auto_healing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#auto_healing ElastigroupAzureV3#auto_healing}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#grace_period ElastigroupAzureV3#grace_period}.
        :param health_check_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#health_check_types ElastigroupAzureV3#health_check_types}.
        :param unhealthy_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unhealthy_duration ElastigroupAzureV3#unhealthy_duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a6e990bda44270ad67c3404228449287642d607e9d1dddbc6a0fba2faa73d3a)
            check_type(argname="argument auto_healing", value=auto_healing, expected_type=type_hints["auto_healing"])
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
            check_type(argname="argument health_check_types", value=health_check_types, expected_type=type_hints["health_check_types"])
            check_type(argname="argument unhealthy_duration", value=unhealthy_duration, expected_type=type_hints["unhealthy_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if grace_period is not None:
            self._values["grace_period"] = grace_period
        if health_check_types is not None:
            self._values["health_check_types"] = health_check_types
        if unhealthy_duration is not None:
            self._values["unhealthy_duration"] = unhealthy_duration

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#auto_healing ElastigroupAzureV3#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def grace_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#grace_period ElastigroupAzureV3#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#health_check_types ElastigroupAzureV3#health_check_types}.'''
        result = self._values.get("health_check_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def unhealthy_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unhealthy_duration ElastigroupAzureV3#unhealthy_duration}.'''
        result = self._values.get("unhealthy_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Health(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3HealthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3HealthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72e0d81fb88eebaf54c459f5b0b58a7f65f59f816ceb260edfac6626f83956f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

    @jsii.member(jsii_name="resetHealthCheckTypes")
    def reset_health_check_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckTypes", []))

    @jsii.member(jsii_name="resetUnhealthyDuration")
    def reset_unhealthy_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnhealthyDuration", []))

    @builtins.property
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property
    @jsii.member(jsii_name="gracePeriodInput")
    def grace_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gracePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckTypesInput")
    def health_check_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "healthCheckTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="unhealthyDurationInput")
    def unhealthy_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unhealthyDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee70486b90693c69a7df062e81ba95384cc799563fc54763cef4a7eb3a5cd0f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoHealing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee7c4f125a18978202cf5cb02aac96ec616d5af48874f8446e926d40afcd1072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gracePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckTypes")
    def health_check_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "healthCheckTypes"))

    @health_check_types.setter
    def health_check_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c64a3e59695e8ed4cc83bddb418009827b807c2039b08412a75b9b69c6fb1df5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unhealthyDuration")
    def unhealthy_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unhealthyDuration"))

    @unhealthy_duration.setter
    def unhealthy_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b9a2d7a8e6437a600969ecdd4d570e9f9ff526c242fbb67c2bbb806d5a26ce7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unhealthyDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3Health]:
        return typing.cast(typing.Optional[ElastigroupAzureV3Health], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ElastigroupAzureV3Health]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f9a2cf294701f15168746e46f3d8eb726e365156f29369babccfb8442e89b5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Image",
    jsii_struct_bases=[],
    name_mapping={
        "custom": "custom",
        "gallery_image": "galleryImage",
        "marketplace": "marketplace",
    },
)
class ElastigroupAzureV3Image:
    def __init__(
        self,
        *,
        custom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ImageCustom", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gallery_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ImageGalleryImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        marketplace: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ImageMarketplace", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param custom: custom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#custom ElastigroupAzureV3#custom}
        :param gallery_image: gallery_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#gallery_image ElastigroupAzureV3#gallery_image}
        :param marketplace: marketplace block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#marketplace ElastigroupAzureV3#marketplace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e10ba92c93d701fe0b4671d34e6c5ca1181d7604075bed1ddcc49858691fdf)
            check_type(argname="argument custom", value=custom, expected_type=type_hints["custom"])
            check_type(argname="argument gallery_image", value=gallery_image, expected_type=type_hints["gallery_image"])
            check_type(argname="argument marketplace", value=marketplace, expected_type=type_hints["marketplace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if custom is not None:
            self._values["custom"] = custom
        if gallery_image is not None:
            self._values["gallery_image"] = gallery_image
        if marketplace is not None:
            self._values["marketplace"] = marketplace

    @builtins.property
    def custom(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ImageCustom"]]]:
        '''custom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#custom ElastigroupAzureV3#custom}
        '''
        result = self._values.get("custom")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ImageCustom"]]], result)

    @builtins.property
    def gallery_image(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ImageGalleryImage"]]]:
        '''gallery_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#gallery_image ElastigroupAzureV3#gallery_image}
        '''
        result = self._values.get("gallery_image")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ImageGalleryImage"]]], result)

    @builtins.property
    def marketplace(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ImageMarketplace"]]]:
        '''marketplace block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#marketplace ElastigroupAzureV3#marketplace}
        '''
        result = self._values.get("marketplace")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ImageMarketplace"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Image(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageCustom",
    jsii_struct_bases=[],
    name_mapping={
        "image_name": "imageName",
        "resource_group_name": "resourceGroupName",
    },
)
class ElastigroupAzureV3ImageCustom:
    def __init__(
        self,
        *,
        image_name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param image_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image_name ElastigroupAzureV3#image_name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b706e3fe3641269bc9c82998132305b573f433a63a553abc727dbbb296d5130)
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "image_name": image_name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def image_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image_name ElastigroupAzureV3#image_name}.'''
        result = self._values.get("image_name")
        assert result is not None, "Required property 'image_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ImageCustom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ImageCustomList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageCustomList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba5532510f93dc827388ebded4851439b11c80358ace880f3768d97ed0affa28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3ImageCustomOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc91d2bf6bcfa551e272ba0e42dfce2ec79f6500561e7caceb1e9cd5efc2b9c4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ImageCustomOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abc9d9211714e8fb04527e7c4fbc0b73d978fd7d593a00acfed5f9ddc565af68)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a8fe0c671d3f2d4f01a0290f5a65b6c56ca224063523220e7882237d7918d3a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__51d8e154ba707b556409151e5176c095a784236e0d80edbacc89236090e0ce69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageCustom]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageCustom]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageCustom]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d94eb8aeb647c69af925e5434d8de1d2ea4b9d40c417cd11a4797a0f9aee260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ImageCustomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageCustomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aba67e046e4dba931158e7ecd756b672e41b27963fae66860e364c4d2cc3cb73)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="imageNameInput")
    def image_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageNameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa2a32b33b4082f7b1785585cf0418815f2a7b49482a81070a43e54e5d4e981)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae96aec00ed532d217647415d8eb425097fb4fee62a7ee45ffaccf30d7a64243)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageCustom]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageCustom]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageCustom]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d119cdf05fb3731072049dc8d33c44a47f81b61cdff33f1c4d0b0ea4e1ea98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageGalleryImage",
    jsii_struct_bases=[],
    name_mapping={
        "gallery_name": "galleryName",
        "image_name": "imageName",
        "resource_group_name": "resourceGroupName",
        "version": "version",
        "spot_account_id": "spotAccountId",
    },
)
class ElastigroupAzureV3ImageGalleryImage:
    def __init__(
        self,
        *,
        gallery_name: builtins.str,
        image_name: builtins.str,
        resource_group_name: builtins.str,
        version: builtins.str,
        spot_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param gallery_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#gallery_name ElastigroupAzureV3#gallery_name}.
        :param image_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image_name ElastigroupAzureV3#image_name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#version ElastigroupAzureV3#version}.
        :param spot_account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_account_id ElastigroupAzureV3#spot_account_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12991ce6ced6b5dde96c277c8d5436a21abddd6151b2711fc6c07686f3e5f61b)
            check_type(argname="argument gallery_name", value=gallery_name, expected_type=type_hints["gallery_name"])
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument spot_account_id", value=spot_account_id, expected_type=type_hints["spot_account_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gallery_name": gallery_name,
            "image_name": image_name,
            "resource_group_name": resource_group_name,
            "version": version,
        }
        if spot_account_id is not None:
            self._values["spot_account_id"] = spot_account_id

    @builtins.property
    def gallery_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#gallery_name ElastigroupAzureV3#gallery_name}.'''
        result = self._values.get("gallery_name")
        assert result is not None, "Required property 'gallery_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#image_name ElastigroupAzureV3#image_name}.'''
        result = self._values.get("image_name")
        assert result is not None, "Required property 'image_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#version ElastigroupAzureV3#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def spot_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_account_id ElastigroupAzureV3#spot_account_id}.'''
        result = self._values.get("spot_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ImageGalleryImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ImageGalleryImageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageGalleryImageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e44af829d73beeaac91f2bc88af338c7269f5c178fd5d1343a4d7a9fd7883c5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ImageGalleryImageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78dd4765863be762c5dbdc64ffb5d14b9e56c09876c59f5d3dc6137a05e401b8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ImageGalleryImageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__999eae35698ee82ff0a559fa9dedd65ac75be5b062ed6acf18470d9ef9c50a0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__928e5503d1719d9c2e241e50346f943edae59191fdb2ae32441ad2ce58e1639b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f4d57dc3eb6b58e627cb550b5adc24ec8a21413064528f2c868c61dc0223837c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageGalleryImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageGalleryImage]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageGalleryImage]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53f3b28e8a1e999d37001d4cc3e5716e462b9d9085f3b7dd7d4722bffe0673ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ImageGalleryImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageGalleryImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9de458c51c487d17280ee813eaaabe1e8bfb0a1be0adaac4d26d0f8d4e459949)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetSpotAccountId")
    def reset_spot_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotAccountId", []))

    @builtins.property
    @jsii.member(jsii_name="galleryNameInput")
    def gallery_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "galleryNameInput"))

    @builtins.property
    @jsii.member(jsii_name="imageNameInput")
    def image_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageNameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="spotAccountIdInput")
    def spot_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotAccountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="galleryName")
    def gallery_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "galleryName"))

    @gallery_name.setter
    def gallery_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__633ee5c7fa67aa99b602a2f4ce63316744d9d94b963086977ec34d4b4110c2ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "galleryName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cca0dd01eea748b2e706f1bb12f2c93f1d8f4c316160da15975a3a280368c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d96cd9499e8579d1b50fb91a9cdc18bf50235f4943b358546807e131fb36460e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotAccountId")
    def spot_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotAccountId"))

    @spot_account_id.setter
    def spot_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__136a8ebe5e83bf8d257da8e4f9aa2e24d3683bd00b10a1a57128e57a91fc1f10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotAccountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710658ab578db7260408d13e894d2ae2123da3977be49cb8dd0606228f68d0f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageGalleryImage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageGalleryImage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageGalleryImage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5f3bbc3ab61be85bbb7ff5e5e3962a4d918b91b0e709f48f82e5c64934d4b7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ImageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__416ce0ca42bbb32cc14d2505433ac3693e67e3c152e939336fdcd85afce1b8b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3ImageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__468380111501a6465c8ae3a0703665d86eb7ee9ac975a1e18433c8178756a9c7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ImageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f7b55af6b5d6b1d5cb90b0fdbcb78f8b7a2f75b3f9543770f516c43c42169a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bbe2151d99337411bc3723d4698735d8c88d5e8fae0516abf3a2d291f8b63d5e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb6722460a5428272015e082bdd10541638dad20fb4eac4ad1eb122b8156043f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Image]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Image]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Image]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a9acbe14471a5e031a401f42cacbe658dc0c347593a496fef1ecc0c2d587a25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageMarketplace",
    jsii_struct_bases=[],
    name_mapping={
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "version": "version",
    },
)
class ElastigroupAzureV3ImageMarketplace:
    def __init__(
        self,
        *,
        offer: builtins.str,
        publisher: builtins.str,
        sku: builtins.str,
        version: builtins.str,
    ) -> None:
        '''
        :param offer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#offer ElastigroupAzureV3#offer}.
        :param publisher: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#publisher ElastigroupAzureV3#publisher}.
        :param sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#sku ElastigroupAzureV3#sku}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#version ElastigroupAzureV3#version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8388e3e4a39e3a9906e4a3c60449851ac382528556695e6608e02457da5d8604)
            check_type(argname="argument offer", value=offer, expected_type=type_hints["offer"])
            check_type(argname="argument publisher", value=publisher, expected_type=type_hints["publisher"])
            check_type(argname="argument sku", value=sku, expected_type=type_hints["sku"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "offer": offer,
            "publisher": publisher,
            "sku": sku,
            "version": version,
        }

    @builtins.property
    def offer(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#offer ElastigroupAzureV3#offer}.'''
        result = self._values.get("offer")
        assert result is not None, "Required property 'offer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def publisher(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#publisher ElastigroupAzureV3#publisher}.'''
        result = self._values.get("publisher")
        assert result is not None, "Required property 'publisher' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sku(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#sku ElastigroupAzureV3#sku}.'''
        result = self._values.get("sku")
        assert result is not None, "Required property 'sku' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#version ElastigroupAzureV3#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ImageMarketplace(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ImageMarketplaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageMarketplaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a539ce4d98452bb0a77ce65d692f808993b324f7076015c71b0f8b152c0913c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ImageMarketplaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__974bb7a284d976dbdcc8437293205705a062c232577a5d79965133ab75d3310c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ImageMarketplaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7df089e1553109bb55a3650ca5ccb451901179a080616d4f3c3a6a0c63889b3a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d126e300dd7135dc38269521d604bdf9c3e9c328ec830cf8a805661f60aa20a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__46f3ca5715d90382ad9893877f6e1760c4f61079a51f93e700b739cf121fc4b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageMarketplace]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageMarketplace]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageMarketplace]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c04388dd152c1f70b530992cffdfaf37a833c6ac818523419ac0eb4f747b243)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ImageMarketplaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageMarketplaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3d1e7ac780e3d6e6f9765278895c0fcdb34be3b7981074826b93fa998064b72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="offerInput")
    def offer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "offerInput"))

    @builtins.property
    @jsii.member(jsii_name="publisherInput")
    def publisher_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publisherInput"))

    @builtins.property
    @jsii.member(jsii_name="skuInput")
    def sku_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "skuInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="offer")
    def offer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "offer"))

    @offer.setter
    def offer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dfac443fed60e9ae17966508bfda3d870aca29c6c7b3597f3d37b4802277ae6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publisher")
    def publisher(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publisher"))

    @publisher.setter
    def publisher(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__050b06d421cc3dd599bfb73b8763918320df14ffd5d41dde23c05d55de7d5957)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publisher", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sku")
    def sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sku"))

    @sku.setter
    def sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2e219391bd4962f59722ead5c749e304c5949aff0dcc1fc6c4c4bc4abadeab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__439bab063883d4ca5150b5437e1241bb4b81050df54babd28e8e2f84e2a95cf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageMarketplace]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageMarketplace]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageMarketplace]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd87a4925a335ac29914978f5cd347e18d44e73a1629f95a593794214dbba7b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0626ca52cb736b9797c33941ed114ca7e7d50a76d1ef1e17d783932b7dc96fd7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCustom")
    def put_custom(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageCustom, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0bf1d928c0b830ab973bbcd4f06b0f7c78f97790df36f352f26f8e37cc08ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustom", [value]))

    @jsii.member(jsii_name="putGalleryImage")
    def put_gallery_image(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageGalleryImage, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52b8338095fb250210b51b21f4aef3a4ab4e2f566f50c3fcb80c81975d47e380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGalleryImage", [value]))

    @jsii.member(jsii_name="putMarketplace")
    def put_marketplace(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageMarketplace, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a81b3a7351bc4c0dfa160e2cbcc26732c8beb5b1ee6f8ae64b2a7d0b0c4bee25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMarketplace", [value]))

    @jsii.member(jsii_name="resetCustom")
    def reset_custom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustom", []))

    @jsii.member(jsii_name="resetGalleryImage")
    def reset_gallery_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGalleryImage", []))

    @jsii.member(jsii_name="resetMarketplace")
    def reset_marketplace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMarketplace", []))

    @builtins.property
    @jsii.member(jsii_name="custom")
    def custom(self) -> ElastigroupAzureV3ImageCustomList:
        return typing.cast(ElastigroupAzureV3ImageCustomList, jsii.get(self, "custom"))

    @builtins.property
    @jsii.member(jsii_name="galleryImage")
    def gallery_image(self) -> ElastigroupAzureV3ImageGalleryImageList:
        return typing.cast(ElastigroupAzureV3ImageGalleryImageList, jsii.get(self, "galleryImage"))

    @builtins.property
    @jsii.member(jsii_name="marketplace")
    def marketplace(self) -> ElastigroupAzureV3ImageMarketplaceList:
        return typing.cast(ElastigroupAzureV3ImageMarketplaceList, jsii.get(self, "marketplace"))

    @builtins.property
    @jsii.member(jsii_name="customInput")
    def custom_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageCustom]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageCustom]]], jsii.get(self, "customInput"))

    @builtins.property
    @jsii.member(jsii_name="galleryImageInput")
    def gallery_image_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageGalleryImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageGalleryImage]]], jsii.get(self, "galleryImageInput"))

    @builtins.property
    @jsii.member(jsii_name="marketplaceInput")
    def marketplace_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageMarketplace]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageMarketplace]]], jsii.get(self, "marketplaceInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Image]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Image]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Image]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d64abb228c01ee3b5723124e63bd8b9efcb6f2a9b27cc6a7672d6f3250469b9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3LoadBalancer",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "resource_group_name": "resourceGroupName",
        "type": "type",
        "backend_pool_names": "backendPoolNames",
        "sku": "sku",
    },
)
class ElastigroupAzureV3LoadBalancer:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
        type: builtins.str,
        backend_pool_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        sku: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        :param backend_pool_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#backend_pool_names ElastigroupAzureV3#backend_pool_names}.
        :param sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#sku ElastigroupAzureV3#sku}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee42412492c3ec91066685c31a0f8a2b2393320cc51b4ce053fc5a32706e4a1c)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument backend_pool_names", value=backend_pool_names, expected_type=type_hints["backend_pool_names"])
            check_type(argname="argument sku", value=sku, expected_type=type_hints["sku"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
            "type": type,
        }
        if backend_pool_names is not None:
            self._values["backend_pool_names"] = backend_pool_names
        if sku is not None:
            self._values["sku"] = sku

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend_pool_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#backend_pool_names ElastigroupAzureV3#backend_pool_names}.'''
        result = self._values.get("backend_pool_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sku(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#sku ElastigroupAzureV3#sku}.'''
        result = self._values.get("sku")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3LoadBalancer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3LoadBalancerList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3LoadBalancerList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65f48965fb1573b68d4155a0aad154ca4c89aae4fc39f43bf054513a7830156f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3LoadBalancerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b3b512060f65e870cf0e29ce5810dc7150f5130fcf30180b9ed39e252a6a324)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3LoadBalancerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad21f4a7cddd69c741708106640471c1e66c04a01e1945dff2fc94413f0463f5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2058f74afb1aab40753d5c0c84ea7f73b41ae46ce89c46257f357c096173ede)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f1891304c2e7f119689a39c1ad8c2a3ee8af07c54661315b331b55bb469b398f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3LoadBalancer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3LoadBalancer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3LoadBalancer]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4559fec3b5a934569e53ce0b2b9515fa968987490f2e663d9bd1d30d850cf940)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3LoadBalancerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3LoadBalancerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__732d035b4bbe5e23ed71ca7a5134a67050b73d21ecf0364e17717e6b3b8316e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBackendPoolNames")
    def reset_backend_pool_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackendPoolNames", []))

    @jsii.member(jsii_name="resetSku")
    def reset_sku(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSku", []))

    @builtins.property
    @jsii.member(jsii_name="backendPoolNamesInput")
    def backend_pool_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "backendPoolNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="skuInput")
    def sku_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "skuInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="backendPoolNames")
    def backend_pool_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "backendPoolNames"))

    @backend_pool_names.setter
    def backend_pool_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27f06b5020e76ac02caf30c223e1c9b4b3f91d31484463b24c84257a82ca947c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backendPoolNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8fee8689c562037c556f7469ac35f9b6d8d1627ecc7fccf6ab953b284ea9abc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f62b6313486574729ecf330bb96244f780c1612427c010a58a86c53d08ff89a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sku")
    def sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sku"))

    @sku.setter
    def sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbf6a2dc5ecc6c4df28419c627d2b7f804a8b5c84c297574edbc8694ba05b437)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa27dfe6dd47ef6cfc792a1fdc6b66f99e7186966bca5bae9e227727b887334b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3LoadBalancer]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3LoadBalancer]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3LoadBalancer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1238676c6cfe6f72ec9a442a65a5d516c281f8ffa80b4878aa369878a514365)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Login",
    jsii_struct_bases=[],
    name_mapping={
        "user_name": "userName",
        "password": "password",
        "ssh_public_key": "sshPublicKey",
    },
)
class ElastigroupAzureV3Login:
    def __init__(
        self,
        *,
        user_name: builtins.str,
        password: typing.Optional[builtins.str] = None,
        ssh_public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#user_name ElastigroupAzureV3#user_name}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#password ElastigroupAzureV3#password}.
        :param ssh_public_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#ssh_public_key ElastigroupAzureV3#ssh_public_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b1d1d9b43783755cdf7e18cc7daf7a64c654bfe52af2a762bfabd1ce1080664)
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument ssh_public_key", value=ssh_public_key, expected_type=type_hints["ssh_public_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_name": user_name,
        }
        if password is not None:
            self._values["password"] = password
        if ssh_public_key is not None:
            self._values["ssh_public_key"] = ssh_public_key

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#user_name ElastigroupAzureV3#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#password ElastigroupAzureV3#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_public_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#ssh_public_key ElastigroupAzureV3#ssh_public_key}.'''
        result = self._values.get("ssh_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Login(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3LoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3LoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4486581ac2e21e7b2898e2badf02e67b266ced01fcd51cea8e9715f008b976f1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetSshPublicKey")
    def reset_ssh_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshPublicKey", []))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="sshPublicKeyInput")
    def ssh_public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshPublicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e8ddca03805e1ea13540a628ec9dcd10c5a8edda3c25108834f3ad5cc58331c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshPublicKey")
    def ssh_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshPublicKey"))

    @ssh_public_key.setter
    def ssh_public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba02e2542838a2460bd9c20bb142b21a0c36ffdd431c276e7ea56b83cd9345ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshPublicKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44c9edfe177aab34c4b5698177c504aaf83350ec08e99e0639af3a583fe10c1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3Login]:
        return typing.cast(typing.Optional[ElastigroupAzureV3Login], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ElastigroupAzureV3Login]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4442eb8284d124c692f5fddd175c31a3d64fee50ae8418d6a8879ec77efee795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ManagedServiceIdentity",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class ElastigroupAzureV3ManagedServiceIdentity:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cd77a5a5e1bbf3e1e171cec737b8810efcc36fbdd5e05992d206af79d5147de)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ManagedServiceIdentity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ManagedServiceIdentityList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ManagedServiceIdentityList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39830ecba4af83ef97289b94582719b096e548af55b16d38ba716a690a913abc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ManagedServiceIdentityOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb651768f6f25e72f16c428089b518ea7188c81a50e6a20129ee479e25fa54fd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ManagedServiceIdentityOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa5ab7a1fca0bcf0fa1c60a262520f6b1055683e4a0e1b4d790c369936423f22)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0537a932103cd191f1c3cd89ee4599e99654640061399614cdaa4565517107f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7875ad0aee5a3cb311b4b395adf75e139458191c74c90c1adc12a15d153b2e3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ManagedServiceIdentity]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ManagedServiceIdentity]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ManagedServiceIdentity]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398f7d010935d7a55b9272dbb97855bc03faf6efdc0d33005ca2478965be3216)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ManagedServiceIdentityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ManagedServiceIdentityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd915668226e77ea7d731a67a7b350e36a88e9a4164ef401911daa4bff13e35a)
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
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df369b05a3a8e9383939ca0b04a1a2f5c3669756f9707a155ef5ab956223272a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09b62879c72cafe40ff2f7699bed99e242919b7cebc4eab0b25c3eed2317cfaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ManagedServiceIdentity]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ManagedServiceIdentity]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ManagedServiceIdentity]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0247675ff18d3b3a3a278c7925d5437e4982a9ca157d9a0772aeb3384a6d4710)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Network",
    jsii_struct_bases=[],
    name_mapping={
        "network_interfaces": "networkInterfaces",
        "resource_group_name": "resourceGroupName",
        "virtual_network_name": "virtualNetworkName",
    },
)
class ElastigroupAzureV3Network:
    def __init__(
        self,
        *,
        network_interfaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3NetworkNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]],
        resource_group_name: builtins.str,
        virtual_network_name: builtins.str,
    ) -> None:
        '''
        :param network_interfaces: network_interfaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#network_interfaces ElastigroupAzureV3#network_interfaces}
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        :param virtual_network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#virtual_network_name ElastigroupAzureV3#virtual_network_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fad1f2de604be5662221076d1e442d12906d979412eda559f5a64217832abe28)
            check_type(argname="argument network_interfaces", value=network_interfaces, expected_type=type_hints["network_interfaces"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument virtual_network_name", value=virtual_network_name, expected_type=type_hints["virtual_network_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network_interfaces": network_interfaces,
            "resource_group_name": resource_group_name,
            "virtual_network_name": virtual_network_name,
        }

    @builtins.property
    def network_interfaces(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfaces"]]:
        '''network_interfaces block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#network_interfaces ElastigroupAzureV3#network_interfaces}
        '''
        result = self._values.get("network_interfaces")
        assert result is not None, "Required property 'network_interfaces' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfaces"]], result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_network_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#virtual_network_name ElastigroupAzureV3#virtual_network_name}.'''
        result = self._values.get("virtual_network_name")
        assert result is not None, "Required property 'virtual_network_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Network(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfaces",
    jsii_struct_bases=[],
    name_mapping={
        "assign_public_ip": "assignPublicIp",
        "is_primary": "isPrimary",
        "subnet_name": "subnetName",
        "additional_ip_configs": "additionalIpConfigs",
        "application_security_group": "applicationSecurityGroup",
        "enable_ip_forwarding": "enableIpForwarding",
        "private_ip_addresses": "privateIpAddresses",
        "public_ip_sku": "publicIpSku",
        "security_group": "securityGroup",
    },
)
class ElastigroupAzureV3NetworkNetworkInterfaces:
    def __init__(
        self,
        *,
        assign_public_ip: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        is_primary: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        subnet_name: builtins.str,
        additional_ip_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        application_security_group: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup", typing.Dict[builtins.str, typing.Any]]]]] = None,
        enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        private_ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        public_ip_sku: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param assign_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#assign_public_ip ElastigroupAzureV3#assign_public_ip}.
        :param is_primary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_primary ElastigroupAzureV3#is_primary}.
        :param subnet_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#subnet_name ElastigroupAzureV3#subnet_name}.
        :param additional_ip_configs: additional_ip_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#additional_ip_configs ElastigroupAzureV3#additional_ip_configs}
        :param application_security_group: application_security_group block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#application_security_group ElastigroupAzureV3#application_security_group}
        :param enable_ip_forwarding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#enable_ip_forwarding ElastigroupAzureV3#enable_ip_forwarding}.
        :param private_ip_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#private_ip_addresses ElastigroupAzureV3#private_ip_addresses}.
        :param public_ip_sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#public_ip_sku ElastigroupAzureV3#public_ip_sku}.
        :param security_group: security_group block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security_group ElastigroupAzureV3#security_group}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1164f1e62c0db97ffaa3e7ad90b071722095b4018292ac3c717412f1bd568078)
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument is_primary", value=is_primary, expected_type=type_hints["is_primary"])
            check_type(argname="argument subnet_name", value=subnet_name, expected_type=type_hints["subnet_name"])
            check_type(argname="argument additional_ip_configs", value=additional_ip_configs, expected_type=type_hints["additional_ip_configs"])
            check_type(argname="argument application_security_group", value=application_security_group, expected_type=type_hints["application_security_group"])
            check_type(argname="argument enable_ip_forwarding", value=enable_ip_forwarding, expected_type=type_hints["enable_ip_forwarding"])
            check_type(argname="argument private_ip_addresses", value=private_ip_addresses, expected_type=type_hints["private_ip_addresses"])
            check_type(argname="argument public_ip_sku", value=public_ip_sku, expected_type=type_hints["public_ip_sku"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assign_public_ip": assign_public_ip,
            "is_primary": is_primary,
            "subnet_name": subnet_name,
        }
        if additional_ip_configs is not None:
            self._values["additional_ip_configs"] = additional_ip_configs
        if application_security_group is not None:
            self._values["application_security_group"] = application_security_group
        if enable_ip_forwarding is not None:
            self._values["enable_ip_forwarding"] = enable_ip_forwarding
        if private_ip_addresses is not None:
            self._values["private_ip_addresses"] = private_ip_addresses
        if public_ip_sku is not None:
            self._values["public_ip_sku"] = public_ip_sku
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def assign_public_ip(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#assign_public_ip ElastigroupAzureV3#assign_public_ip}.'''
        result = self._values.get("assign_public_ip")
        assert result is not None, "Required property 'assign_public_ip' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def is_primary(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_primary ElastigroupAzureV3#is_primary}.'''
        result = self._values.get("is_primary")
        assert result is not None, "Required property 'is_primary' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def subnet_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#subnet_name ElastigroupAzureV3#subnet_name}.'''
        result = self._values.get("subnet_name")
        assert result is not None, "Required property 'subnet_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_ip_configs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs"]]]:
        '''additional_ip_configs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#additional_ip_configs ElastigroupAzureV3#additional_ip_configs}
        '''
        result = self._values.get("additional_ip_configs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs"]]], result)

    @builtins.property
    def application_security_group(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup"]]]:
        '''application_security_group block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#application_security_group ElastigroupAzureV3#application_security_group}
        '''
        result = self._values.get("application_security_group")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup"]]], result)

    @builtins.property
    def enable_ip_forwarding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#enable_ip_forwarding ElastigroupAzureV3#enable_ip_forwarding}.'''
        result = self._values.get("enable_ip_forwarding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def private_ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#private_ip_addresses ElastigroupAzureV3#private_ip_addresses}.'''
        result = self._values.get("private_ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def public_ip_sku(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#public_ip_sku ElastigroupAzureV3#public_ip_sku}.'''
        result = self._values.get("public_ip_sku")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup"]]]:
        '''security_group block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security_group ElastigroupAzureV3#security_group}
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3NetworkNetworkInterfaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "private_ip_version": "privateIpVersion"},
)
class ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs:
    def __init__(
        self,
        *,
        name: builtins.str,
        private_ip_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param private_ip_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#private_ip_version ElastigroupAzureV3#private_ip_version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d4d3434341c207b3ec51f6d668e14ca7107101d1fee721d55e5aefef05d83c3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument private_ip_version", value=private_ip_version, expected_type=type_hints["private_ip_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if private_ip_version is not None:
            self._values["private_ip_version"] = private_ip_version

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_ip_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#private_ip_version ElastigroupAzureV3#private_ip_version}.'''
        result = self._values.get("private_ip_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3803d49b5fa57a5101f0b447936f2991f0f7ec901102032e77c82187507ccdf4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27ab624df4e11dd4560d6f957e10b270305a74303569831751a6a1c66f913656)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e2a5d19ddc93f43529326a40e34b9429722f065c278c55989347abdfed57b7d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c68c8d5b0ffd385db80361863d8253944a34f7f342085dc7c2dd745537c9939)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c97be3744c82a6be2aeaa64d13610d269e6ba75dba86e78d8358394be7ecad1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09e7c284f5ddee1882d17a8c31757fca8d5b88cea25bde78a2b37fabeba923cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8f243a4832d5755c3a56eaf3a31629c38535c58221cd3ee1e371421cde6cc5c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPrivateIpVersion")
    def reset_private_ip_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIpVersion", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="privateIpVersionInput")
    def private_ip_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateIpVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d512576860dd3679731f08f5860bbcda631106257078f7453426bf8e4829110f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIpVersion")
    def private_ip_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIpVersion"))

    @private_ip_version.setter
    def private_ip_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0931ac945b76e2846114d31710d793ff821005e7ca9913ed5f7dacee394c7fd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIpVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e5f8997cd092fab7efcb7236e4cc06e27cee5321804d6f063f0a9e521b474a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__069e5262d21768eda7fbe63efe689bfa156a7a881f515c81f9bb7759cadde0fa)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee9b39024740c6a07a0a7bce6a7796d2fa23bf89d389165cc346942c24008359)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b344f1763181d8852ed702ee38a4f8b6eea8176aa059c614d0f15c79bfb93ab)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a334b16050c5514e674652464dc0b092cb2b6e6bcbdeb9d453e60e8b0aaaedc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__beb68546299f4373f8390d647e6b783d93b4258d87f9288136f57a7a45c245a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9493b82111ad39e8436b96d724678b43209cd62a641113cfb74280595fa5290)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7ca3592a4e239bad279dfc031b3b1903100e0bcf68e63e947b1694589501867)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6db43efef1e1b0285545a4e043aebe5d559f5dcbe0881cd9e1059d017f05b92)
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
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb1c62f0ff02975a21ef54ea813d64474c71aa0b41f86698bd7e0d7b262f903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de8bc6c2577554052714902e60e27cbb5fdc0a30359fcd5edde1a6a67df2f83a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a53a28f44f14a4ee3ccf23abba226e5fbd0ae7eff777c6ca9da8c15393bbbad3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3NetworkNetworkInterfacesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b300f518196c9a299f7e624fdc72d6bff3cd931a7e89b9bb86c1ec8fbb24f50)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3NetworkNetworkInterfacesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71379ed071e6f73460cdfe2f005b131b2ea9066af94ad87a1047b90f411aba54)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3NetworkNetworkInterfacesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0de009dbea5e8c23906a5e0d20fc49d2900e2fd8d3d35bccb4f7da798bd77988)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47ef9cf98151345850f79d78832c522ab934b08cea5470810bae0e3f7e830aa5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__25f8db7188f11e25187fb72d0dfaafd02622e19799dcc73f51ceffbcd2a2f250)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf921ecec5596b0c838f5871eae2f7e00f96f5f1d2e7955a0cb381ac8208134)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3NetworkNetworkInterfacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c360ea491c0ed2616b14c409fd03abfae141a882d2f379347701ae8f4f876c5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAdditionalIpConfigs")
    def put_additional_ip_configs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f0311baec94a2c5bed16aa63d074801c231e846d3ce73c100b110091f0acc82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAdditionalIpConfigs", [value]))

    @jsii.member(jsii_name="putApplicationSecurityGroup")
    def put_application_security_group(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3674d5efc0563324862aed029173f7e58654de011b9a3741ebbc04b2eb14a1e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApplicationSecurityGroup", [value]))

    @jsii.member(jsii_name="putSecurityGroup")
    def put_security_group(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b1e788e652fa6d81fe2d1b0d48cc44f64e708e527a6fd28ee474efad4b6467)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSecurityGroup", [value]))

    @jsii.member(jsii_name="resetAdditionalIpConfigs")
    def reset_additional_ip_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalIpConfigs", []))

    @jsii.member(jsii_name="resetApplicationSecurityGroup")
    def reset_application_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationSecurityGroup", []))

    @jsii.member(jsii_name="resetEnableIpForwarding")
    def reset_enable_ip_forwarding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableIpForwarding", []))

    @jsii.member(jsii_name="resetPrivateIpAddresses")
    def reset_private_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIpAddresses", []))

    @jsii.member(jsii_name="resetPublicIpSku")
    def reset_public_ip_sku(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicIpSku", []))

    @jsii.member(jsii_name="resetSecurityGroup")
    def reset_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroup", []))

    @builtins.property
    @jsii.member(jsii_name="additionalIpConfigs")
    def additional_ip_configs(
        self,
    ) -> ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsList:
        return typing.cast(ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsList, jsii.get(self, "additionalIpConfigs"))

    @builtins.property
    @jsii.member(jsii_name="applicationSecurityGroup")
    def application_security_group(
        self,
    ) -> ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupList:
        return typing.cast(ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupList, jsii.get(self, "applicationSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="securityGroup")
    def security_group(
        self,
    ) -> "ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupList":
        return typing.cast("ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupList", jsii.get(self, "securityGroup"))

    @builtins.property
    @jsii.member(jsii_name="additionalIpConfigsInput")
    def additional_ip_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]], jsii.get(self, "additionalIpConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationSecurityGroupInput")
    def application_security_group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]], jsii.get(self, "applicationSecurityGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="assignPublicIpInput")
    def assign_public_ip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "assignPublicIpInput"))

    @builtins.property
    @jsii.member(jsii_name="enableIpForwardingInput")
    def enable_ip_forwarding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableIpForwardingInput"))

    @builtins.property
    @jsii.member(jsii_name="isPrimaryInput")
    def is_primary_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isPrimaryInput"))

    @builtins.property
    @jsii.member(jsii_name="privateIpAddressesInput")
    def private_ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "privateIpAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="publicIpSkuInput")
    def public_ip_sku_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicIpSkuInput"))

    @builtins.property
    @jsii.member(jsii_name="securityGroupInput")
    def security_group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup"]]], jsii.get(self, "securityGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetNameInput")
    def subnet_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="assignPublicIp")
    def assign_public_ip(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "assignPublicIp"))

    @assign_public_ip.setter
    def assign_public_ip(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d68b53344d678a6906a12d5b6c66166415b62f0934b97aa91ecf9e42d33eb7c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assignPublicIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableIpForwarding")
    def enable_ip_forwarding(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableIpForwarding"))

    @enable_ip_forwarding.setter
    def enable_ip_forwarding(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b083e5af44bd677008409efda7a39c37ce1f31dfecf4ba891dc1774f27424a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableIpForwarding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isPrimary")
    def is_primary(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isPrimary"))

    @is_primary.setter
    def is_primary(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16161fec59a4e9e1a1df69078e0d87731f49e5e45acc85eb17f47708fdd39b45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPrimary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIpAddresses")
    def private_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "privateIpAddresses"))

    @private_ip_addresses.setter
    def private_ip_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9238551383fb2f2b01ed983487873c2e894f10bcbf2c9edf806155a660b35764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIpAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicIpSku")
    def public_ip_sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicIpSku"))

    @public_ip_sku.setter
    def public_ip_sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd93b4555dd8146cb2566efe7854f6fa75fef7b5673d2f97fb88fb16315c4b3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicIpSku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetName")
    def subnet_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetName"))

    @subnet_name.setter
    def subnet_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cf9bf0b8e3f28eae29ef52bfdb4acac52f6f064c982e118c238cbb4b44c0d98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe32d5d42799ac42ac0cdca668ac02d5af53af8d610a54578df1c5b92b02575)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        resource_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24f07dc641da4a3b4ae53e549b86588a8ebcc454fc7222ae76a5ee868437a6e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if resource_group_name is not None:
            self._values["resource_group_name"] = resource_group_name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1f9c3286736464f5d54f2557243b782e0f3c59c7d161bed09f95e600da98bee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c59dc663acc11ef79f98a418aa4ff40010e3171e341acdbfd101fc1c6d6731a9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b2ebc4e131c20d38185d09b1a188a6557fcdac9fb38923a6b9590ddea89816a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__de6a5735ae7f4ad10a46735466923f811ab37bf7fb8074283371253277211941)
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
            type_hints = typing.get_type_hints(_typecheckingstub__44f4968980148be3632fe1822821f5498152016f9e3f5c8f3a543a23256268ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8f9252485d78a9cde90e3221b284138decade54d2fd0a935740df8e0141fb8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__21b5e290ea4871d933919cea18415c3ab1ab355b4fc5098862071985c42e6e27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetResourceGroupName")
    def reset_resource_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceGroupName", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0169e9cd0ad18087bc8e4e02248ff45f94795d172d9fc4a449aa2b19200ad04f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e62494cd66aa2810e1e944de5766ffcea844d6441f4aae0b973c1d07cfaca6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56403dc48b4542a2152c1a94e1bc574eadd58da7fed5dbf731c0cb45cadfb44b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3NetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3NetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__60fa0ce4ad59907ad9343caba70f4323864a6ca66f53223eae29265e5a23abb8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworkInterfaces")
    def put_network_interfaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da5cc9a5e0de23908a7d5607142470f724e26c3670f1b1706ac13a036ff14fe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterfaces", [value]))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaces")
    def network_interfaces(self) -> ElastigroupAzureV3NetworkNetworkInterfacesList:
        return typing.cast(ElastigroupAzureV3NetworkNetworkInterfacesList, jsii.get(self, "networkInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfacesInput")
    def network_interfaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfaces]]], jsii.get(self, "networkInterfacesInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkNameInput")
    def virtual_network_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNetworkNameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58b2c49aa895598ee323243c62b314534c44ab5e7b795f97e8342553bc4ed455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkName")
    def virtual_network_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkName"))

    @virtual_network_name.setter
    def virtual_network_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c74a488ca47ae06f34ff31d020eaca8150a35ce413626b9d0c864198e313f35f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualNetworkName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3Network]:
        return typing.cast(typing.Optional[ElastigroupAzureV3Network], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ElastigroupAzureV3Network]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f704e47e954be4cf434ea9a09bf2f4de140868054034bf52cf79d3836c52f04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3OsDisk",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "size_gb": "sizeGb"},
)
class ElastigroupAzureV3OsDisk:
    def __init__(
        self,
        *,
        type: builtins.str,
        size_gb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#size_gb ElastigroupAzureV3#size_gb}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad5f7ac1cf9665281d0b32c76d8013fa43d03a0950ce3fa58ce799d41c33824e)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument size_gb", value=size_gb, expected_type=type_hints["size_gb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if size_gb is not None:
            self._values["size_gb"] = size_gb

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size_gb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#size_gb ElastigroupAzureV3#size_gb}.'''
        result = self._values.get("size_gb")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3OsDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3OsDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3OsDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a10fe5ed1cfb84eb88a2ffa3ad29bb72299ea45ff9933513f1eb62919c31a0a9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSizeGb")
    def reset_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSizeGb", []))

    @builtins.property
    @jsii.member(jsii_name="sizeGbInput")
    def size_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeGb")
    def size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeGb"))

    @size_gb.setter
    def size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__234a0f5f99fa7d250495ac7d2435b3b2ea43773788030bc04dd2f85792738b01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7c37aaa278962a84e417d9fb3f8ffbdba7163236ad837711aec2041422e3357)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3OsDisk]:
        return typing.cast(typing.Optional[ElastigroupAzureV3OsDisk], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ElastigroupAzureV3OsDisk]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfda973be6a1239dab96baa33dbc41776a3d5707cc62f5b41bff3c6d0f1539a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ProximityPlacementGroups",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class ElastigroupAzureV3ProximityPlacementGroups:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__030555b30fd3ef3a87d68a2ab276e75021ee8409f7f25dd49484f843fc8e82a9)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ProximityPlacementGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ProximityPlacementGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ProximityPlacementGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a80a44a24c0bdef102741071a3abd81eef23c3a421bae16cc8eab7ccd3a3b56c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ProximityPlacementGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0938a236e340d3ec79413135a6f7e58a1f223817d46bd54122afb7f0aa67b81d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ProximityPlacementGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__458755221a23680e1c622168e287719950d7031d346294de6c81fbe9a756d07c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c25e31fdbe52d80ef86bb54f977b7e4c343cc7f42165a53a0726cd118541c5a1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e589928330e57998a5e72f2dd6916aace7876772ddca834c808306fb7728f100)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ProximityPlacementGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ProximityPlacementGroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ProximityPlacementGroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e02d2d263d317068d302b2190291812ef4fe2a673b249a60177689e8f252c615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ProximityPlacementGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ProximityPlacementGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__011d85f1199e275c7e8ad770e162ed0c9a933b13dbcf9e0879517d9527daffab)
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
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3f064bdfcb32c7222cf82fcf7c300504776fdf7b42906166fdeed6ea9352f24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c15ad5fa16f32dffe670d5c6afc8ad31343519be964b8b990e65a33d959c858d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ProximityPlacementGroups]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ProximityPlacementGroups]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ProximityPlacementGroups]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ea800338d7749820b3ad113d42e14fbe7941e3854103b261c71a1fc1aa980f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3RevertToSpot",
    jsii_struct_bases=[],
    name_mapping={"perform_at": "performAt"},
)
class ElastigroupAzureV3RevertToSpot:
    def __init__(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#perform_at ElastigroupAzureV3#perform_at}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a9c6974c245e5a4c81e573c5b729cadacf090afcb9d7bc49c4ac244071c0f02)
            check_type(argname="argument perform_at", value=perform_at, expected_type=type_hints["perform_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "perform_at": perform_at,
        }

    @builtins.property
    def perform_at(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#perform_at ElastigroupAzureV3#perform_at}.'''
        result = self._values.get("perform_at")
        assert result is not None, "Required property 'perform_at' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3RevertToSpot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3RevertToSpotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3RevertToSpotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2dff3464ededce3a07c3ae1db04c4ff70c28ed82387335dae78e2e5871c6556d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__0eeefece98a5afa6ee0a031a036d56b6881351701b245c54c31b11e34aea74f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3RevertToSpot]:
        return typing.cast(typing.Optional[ElastigroupAzureV3RevertToSpot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3RevertToSpot],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0185b7191c0e0df65d022a8c01d2ba9a34b17cd60497ce1dabc522473de87454)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "cooldown": "cooldown",
        "evaluation_periods": "evaluationPeriods",
        "metric_name": "metricName",
        "namespace": "namespace",
        "operator": "operator",
        "period": "period",
        "policy_name": "policyName",
        "statistic": "statistic",
        "threshold": "threshold",
        "dimensions": "dimensions",
        "is_enabled": "isEnabled",
        "source": "source",
        "unit": "unit",
    },
)
class ElastigroupAzureV3ScalingDownPolicy:
    def __init__(
        self,
        *,
        action: typing.Union["ElastigroupAzureV3ScalingDownPolicyAction", typing.Dict[builtins.str, typing.Any]],
        cooldown: jsii.Number,
        evaluation_periods: jsii.Number,
        metric_name: builtins.str,
        namespace: builtins.str,
        operator: builtins.str,
        period: jsii.Number,
        policy_name: builtins.str,
        statistic: builtins.str,
        threshold: jsii.Number,
        dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingDownPolicyDimensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        source: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#action ElastigroupAzureV3#action}
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#cooldown ElastigroupAzureV3#cooldown}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#evaluation_periods ElastigroupAzureV3#evaluation_periods}.
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#metric_name ElastigroupAzureV3#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#namespace ElastigroupAzureV3#namespace}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#operator ElastigroupAzureV3#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#period ElastigroupAzureV3#period}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#policy_name ElastigroupAzureV3#policy_name}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#statistic ElastigroupAzureV3#statistic}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#threshold ElastigroupAzureV3#threshold}.
        :param dimensions: dimensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#dimensions ElastigroupAzureV3#dimensions}
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source ElastigroupAzureV3#source}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unit ElastigroupAzureV3#unit}.
        '''
        if isinstance(action, dict):
            action = ElastigroupAzureV3ScalingDownPolicyAction(**action)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e69262846c8900b0e78e7d10a5d201c72463a5533ec91f4ceaa297f464e550ce)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument cooldown", value=cooldown, expected_type=type_hints["cooldown"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "cooldown": cooldown,
            "evaluation_periods": evaluation_periods,
            "metric_name": metric_name,
            "namespace": namespace,
            "operator": operator,
            "period": period,
            "policy_name": policy_name,
            "statistic": statistic,
            "threshold": threshold,
        }
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if source is not None:
            self._values["source"] = source
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def action(self) -> "ElastigroupAzureV3ScalingDownPolicyAction":
        '''action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#action ElastigroupAzureV3#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast("ElastigroupAzureV3ScalingDownPolicyAction", result)

    @builtins.property
    def cooldown(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#cooldown ElastigroupAzureV3#cooldown}.'''
        result = self._values.get("cooldown")
        assert result is not None, "Required property 'cooldown' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#evaluation_periods ElastigroupAzureV3#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#metric_name ElastigroupAzureV3#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#namespace ElastigroupAzureV3#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#operator ElastigroupAzureV3#operator}.'''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#period ElastigroupAzureV3#period}.'''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#policy_name ElastigroupAzureV3#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def statistic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#statistic ElastigroupAzureV3#statistic}.'''
        result = self._values.get("statistic")
        assert result is not None, "Required property 'statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#threshold ElastigroupAzureV3#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingDownPolicyDimensions"]]]:
        '''dimensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#dimensions ElastigroupAzureV3#dimensions}
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingDownPolicyDimensions"]]], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source ElastigroupAzureV3#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unit ElastigroupAzureV3#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ScalingDownPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyAction",
    jsii_struct_bases=[],
    name_mapping={
        "adjustment": "adjustment",
        "maximum": "maximum",
        "minimum": "minimum",
        "target": "target",
        "type": "type",
    },
)
class ElastigroupAzureV3ScalingDownPolicyAction:
    def __init__(
        self,
        *,
        adjustment: typing.Optional[builtins.str] = None,
        maximum: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#maximum ElastigroupAzureV3#maximum}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minimum ElastigroupAzureV3#minimum}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#target ElastigroupAzureV3#target}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6425079153b9652e0adbae5236c2e86fe7bb148687c467fc3dd31ea86ad70581)
            check_type(argname="argument adjustment", value=adjustment, expected_type=type_hints["adjustment"])
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if adjustment is not None:
            self._values["adjustment"] = adjustment
        if maximum is not None:
            self._values["maximum"] = maximum
        if minimum is not None:
            self._values["minimum"] = minimum
        if target is not None:
            self._values["target"] = target
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#maximum ElastigroupAzureV3#maximum}.'''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minimum ElastigroupAzureV3#minimum}.'''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#target ElastigroupAzureV3#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ScalingDownPolicyAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ScalingDownPolicyActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyActionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__65cfba84f13ed58c3afa8d26b5c12e069d8c457daee1a7c6243568bfbf300e10)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAdjustment")
    def reset_adjustment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdjustment", []))

    @jsii.member(jsii_name="resetMaximum")
    def reset_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximum", []))

    @jsii.member(jsii_name="resetMinimum")
    def reset_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimum", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumInput")
    def maximum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInput")
    def minimum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ef51755b5e1e599d83d8f6901a13a4880d551189b89e9f79a4ef6be10b47c40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximum"))

    @maximum.setter
    def maximum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62448d41e5e6896af65c3708febea7ef3671d030ad50f2287c1a3a8d43e40142)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimum"))

    @minimum.setter
    def minimum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__057c37e7f60a60c1df89b954c7610709ffeeaec61a5d1bea737a5488c53409cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__563d512be8790144689c85b0bbd9ca911119cee4f5aa6779cb20fae1e7f28489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c8f9dfaf3bceaa3645de398ccfcbd5b057408d2d42c34085bd44948310b996b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAzureV3ScalingDownPolicyAction]:
        return typing.cast(typing.Optional[ElastigroupAzureV3ScalingDownPolicyAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3ScalingDownPolicyAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0403a6f066088189b751af9f7a4a3ce2585bcbd45e244d3b638c39732990b6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyDimensions",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ElastigroupAzureV3ScalingDownPolicyDimensions:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#value ElastigroupAzureV3#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccd39616d6ba5dc9e6105b25503f924b55445ff8cfe16fa4dc784e7f78c911cd)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#value ElastigroupAzureV3#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ScalingDownPolicyDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ScalingDownPolicyDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0b5d06767c364d776e863176377aabde132ced0812f61598add66c7ee8f9297)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ScalingDownPolicyDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8a114eda79502582ee83d9014b7eea76e1bf355d6b50cbde70cf47a4ec52b42)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ScalingDownPolicyDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d492228d64f8dd815f9be0a9f52699417db21357f033ec632ad8587fb64440d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ab4cc5b7afd451e5b84631c51ffbd2c1bd03715a22f659bfb973c2ff92e261b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dda02ff1afd0a9533a2f1b306c557766c46fad2a04720eb76afc1db5cdf10ffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicyDimensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicyDimensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5a73724929de5a6fe0e0c29cfd1d4c21815fb3cd38240e13b68283dca93d0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ScalingDownPolicyDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07af2385074c3bade43deb52be19a24746325d865d0bc615d79abf617a041a9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__67fe176422f40efd04b928663f5f937281711b500d7e3281e120e5802bbe91e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f18d5667b91b25d289298fcc8ee76c0b681b1c1b82d77f871dcfdefc217a157)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicyDimensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicyDimensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicyDimensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2766656ec03d0249036ba78b072b6b8c66adca0db4ab541b7abe871a3b4e7c58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ScalingDownPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1762e370416006e1ebdd0da7247b47682a4442458f1ec2c0e1d9efe14b5b9b0a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ScalingDownPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8d516e06f2f40e4b05cfd74e20bb7c457570a03f37167e8e03e97b645050ea2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ScalingDownPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e84e91ec770f6953ad93dcf2f7a9f3b56944f35dcbd8deb40b1b548079847ba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__149c41584883431be19fa8a4005136cb7b78195b63088151de9e27d855dd9d00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__65632557cdef8c91aed5df833e596fc957b9273f0cf587fd58e2ae41d2c32e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca90497df512d598dcd01ba24cf43049e6c74dccee1beae6ce844da7456dfd9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ScalingDownPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingDownPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3d6539849fd009b5d5851cd5466afd99679b30c038726b5b0aefa51fc0c9613)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAction")
    def put_action(
        self,
        *,
        adjustment: typing.Optional[builtins.str] = None,
        maximum: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#maximum ElastigroupAzureV3#maximum}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minimum ElastigroupAzureV3#minimum}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#target ElastigroupAzureV3#target}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        '''
        value = ElastigroupAzureV3ScalingDownPolicyAction(
            adjustment=adjustment,
            maximum=maximum,
            minimum=minimum,
            target=target,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putAction", [value]))

    @jsii.member(jsii_name="putDimensions")
    def put_dimensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingDownPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2712e081aae84dc6eaeb1e39da7a609c8f0f074ff7e385ade14416c00c1d591)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimensions", [value]))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> ElastigroupAzureV3ScalingDownPolicyActionOutputReference:
        return typing.cast(ElastigroupAzureV3ScalingDownPolicyActionOutputReference, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> ElastigroupAzureV3ScalingDownPolicyDimensionsList:
        return typing.cast(ElastigroupAzureV3ScalingDownPolicyDimensionsList, jsii.get(self, "dimensions"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(
        self,
    ) -> typing.Optional[ElastigroupAzureV3ScalingDownPolicyAction]:
        return typing.cast(typing.Optional[ElastigroupAzureV3ScalingDownPolicyAction], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicyDimensions]]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

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
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__830ab36610af43302de51e281dc5004f3562483af5e6bb067473bc9204eb15d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3411c2e45c948863a993ff36b803954e4cb3cefc8c8c3268662aae124bbba8d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__bb2af6b263dc7da440b4d113769378c5ad03853bf7c142b29114b9acd33c306c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d048a4be7bda16ddb0236468711846fa9c366145ca09b533f2af3233324e3198)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bf7c5e3eaa3aeff7bc358ce89f85d0ed01f9c2126fc5d00a7b47fedb4bc81d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec3921ba2b0ff8c1bfc8da23413be3e4a28080d820643bb90457d07899f9c14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dc637d523712d1c6a699fa8817f1469097d30e771f92cd579ef698031aa9d6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8297fc435ddba15cbfafe89c8739974ea010f5903910355cbe745d5b3b93f92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__060d603099a3e36c179912f1673ea71a1b573372ab1ab1f0ce91d16b56a2a218)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79ff0a05fb092cb12d93dfc0f3c6fcd886a263670672db8b2bb966a42841d45d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e7882ce1afd685874bd5f1a69c1120d92ac36ecc2962d6ca73fa804fc0976b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc7415c7a8b8587c8aad94e90adacaaa2e647be60c09bfd5b3de8434df36c307)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42c63c0a4aaaaa9c695f80df3ef2bf1db605776a9f0901fead708bf22d70b2ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "cooldown": "cooldown",
        "evaluation_periods": "evaluationPeriods",
        "metric_name": "metricName",
        "namespace": "namespace",
        "operator": "operator",
        "period": "period",
        "policy_name": "policyName",
        "statistic": "statistic",
        "threshold": "threshold",
        "dimensions": "dimensions",
        "is_enabled": "isEnabled",
        "source": "source",
        "unit": "unit",
    },
)
class ElastigroupAzureV3ScalingUpPolicy:
    def __init__(
        self,
        *,
        action: typing.Union["ElastigroupAzureV3ScalingUpPolicyAction", typing.Dict[builtins.str, typing.Any]],
        cooldown: jsii.Number,
        evaluation_periods: jsii.Number,
        metric_name: builtins.str,
        namespace: builtins.str,
        operator: builtins.str,
        period: jsii.Number,
        policy_name: builtins.str,
        statistic: builtins.str,
        threshold: jsii.Number,
        dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3ScalingUpPolicyDimensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        source: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action: action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#action ElastigroupAzureV3#action}
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#cooldown ElastigroupAzureV3#cooldown}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#evaluation_periods ElastigroupAzureV3#evaluation_periods}.
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#metric_name ElastigroupAzureV3#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#namespace ElastigroupAzureV3#namespace}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#operator ElastigroupAzureV3#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#period ElastigroupAzureV3#period}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#policy_name ElastigroupAzureV3#policy_name}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#statistic ElastigroupAzureV3#statistic}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#threshold ElastigroupAzureV3#threshold}.
        :param dimensions: dimensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#dimensions ElastigroupAzureV3#dimensions}
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.
        :param source: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source ElastigroupAzureV3#source}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unit ElastigroupAzureV3#unit}.
        '''
        if isinstance(action, dict):
            action = ElastigroupAzureV3ScalingUpPolicyAction(**action)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d050af936aa421f97b90a5dbb64c3dbd91b812ce211e93d1b56328ac17712d2)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument cooldown", value=cooldown, expected_type=type_hints["cooldown"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "cooldown": cooldown,
            "evaluation_periods": evaluation_periods,
            "metric_name": metric_name,
            "namespace": namespace,
            "operator": operator,
            "period": period,
            "policy_name": policy_name,
            "statistic": statistic,
            "threshold": threshold,
        }
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if source is not None:
            self._values["source"] = source
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def action(self) -> "ElastigroupAzureV3ScalingUpPolicyAction":
        '''action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#action ElastigroupAzureV3#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast("ElastigroupAzureV3ScalingUpPolicyAction", result)

    @builtins.property
    def cooldown(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#cooldown ElastigroupAzureV3#cooldown}.'''
        result = self._values.get("cooldown")
        assert result is not None, "Required property 'cooldown' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#evaluation_periods ElastigroupAzureV3#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        assert result is not None, "Required property 'evaluation_periods' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#metric_name ElastigroupAzureV3#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#namespace ElastigroupAzureV3#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#operator ElastigroupAzureV3#operator}.'''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#period ElastigroupAzureV3#period}.'''
        result = self._values.get("period")
        assert result is not None, "Required property 'period' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#policy_name ElastigroupAzureV3#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def statistic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#statistic ElastigroupAzureV3#statistic}.'''
        result = self._values.get("statistic")
        assert result is not None, "Required property 'statistic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#threshold ElastigroupAzureV3#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingUpPolicyDimensions"]]]:
        '''dimensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#dimensions ElastigroupAzureV3#dimensions}
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3ScalingUpPolicyDimensions"]]], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source ElastigroupAzureV3#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#unit ElastigroupAzureV3#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ScalingUpPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyAction",
    jsii_struct_bases=[],
    name_mapping={
        "adjustment": "adjustment",
        "maximum": "maximum",
        "minimum": "minimum",
        "target": "target",
        "type": "type",
    },
)
class ElastigroupAzureV3ScalingUpPolicyAction:
    def __init__(
        self,
        *,
        adjustment: typing.Optional[builtins.str] = None,
        maximum: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#maximum ElastigroupAzureV3#maximum}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minimum ElastigroupAzureV3#minimum}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#target ElastigroupAzureV3#target}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__995437a810064f444b1825291d5046df33afbb51852abbd1eb9f582c581fa9e7)
            check_type(argname="argument adjustment", value=adjustment, expected_type=type_hints["adjustment"])
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if adjustment is not None:
            self._values["adjustment"] = adjustment
        if maximum is not None:
            self._values["maximum"] = maximum
        if minimum is not None:
            self._values["minimum"] = minimum
        if target is not None:
            self._values["target"] = target
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maximum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#maximum ElastigroupAzureV3#maximum}.'''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minimum ElastigroupAzureV3#minimum}.'''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#target ElastigroupAzureV3#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ScalingUpPolicyAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ScalingUpPolicyActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyActionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__99fc3955a6718a91423e2835a33beb048707d9d0cac6556df8d3e163be099612)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAdjustment")
    def reset_adjustment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdjustment", []))

    @jsii.member(jsii_name="resetMaximum")
    def reset_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximum", []))

    @jsii.member(jsii_name="resetMinimum")
    def reset_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimum", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumInput")
    def maximum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInput")
    def minimum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66322ad684a7c8260a2b868f649f55b9a2fa5db5c7f615918cf1912d7458aa88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximum"))

    @maximum.setter
    def maximum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6148a56eea89445afcca7e8b3c2c51d5aff4603e33f7efe910eca82b8a4d74c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimum"))

    @minimum.setter
    def minimum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36abbc5abe6cf7446bf5351ce26727b02d92d788d97aa6410c3c5a64ad923f9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d873fa8c74913dfa6454f27f1dee2d53f9f77290dbccfc3878db8997d49c97de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8114706d35b690dc93e0f0496c2a84ae218c7fab65f189ff72243c115dd047c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAzureV3ScalingUpPolicyAction]:
        return typing.cast(typing.Optional[ElastigroupAzureV3ScalingUpPolicyAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3ScalingUpPolicyAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d76f53f4d75f5038ca5fae5c4eff5b48460f9141d239276734fd13b5e69d7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyDimensions",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ElastigroupAzureV3ScalingUpPolicyDimensions:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#value ElastigroupAzureV3#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d45f5c73054aab6de24e94f2ac9701754ebc177a1bbaf775015e4c63bde16238)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#value ElastigroupAzureV3#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3ScalingUpPolicyDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3ScalingUpPolicyDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2750ff567983a3f056c2b669b581fd5f9a524cf3e7d63fece66f983fb3e3c9b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ScalingUpPolicyDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d253c59fb782ccb34f0ba9872603c61bcea546ee3cf122f6940d7b455e0bb3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ScalingUpPolicyDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee63acf2d43a4e10cbaeded5a0e44a85b7c4d2ed3be858b0c1eaf0b762889778)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47c5978f46ea81e1f7e69f720a7c36fd31697c73afcf93435c689edc361f84be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d0791721954e3dc40a9310bcf7403826cac78bad8a708797627080ea7c8658e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicyDimensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicyDimensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fba9106fec1cb98133c8a0368ca2b568ae2f5f7a0282297bb175bafe22924ab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ScalingUpPolicyDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cc98ca20aa60bdf9986e969f7dc8782eae07c6374daa2eab40a203e54df07df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3fff249f347f744ed4c331a50b959f8550c3eafbaf3d8611153cef901dc7ec3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc2d55340530da21f1c6de92f94df738fb2c8502780858e156f1458ae3d3ea26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicyDimensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicyDimensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicyDimensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c4b320fff2d5e44dffa88694ba32fd46dd80de6cb53c4ca4aa5981170aa1c2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ScalingUpPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea5e6749d7960eceffb7b7c2e3e83689da3eefb35c9e31d137bad4eeffe8998d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3ScalingUpPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74e04b3b9acdbf0706f9d25d3a858523f84475426cee27f4746e169bc97578f9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3ScalingUpPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e677f3726d13892949398cd3dbc4127302574cb0ce721ab12e9ae1124acc2d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__65f2a9440a9a983990a57fc87dfbfe33ec4cee7fc27bda9d7cfc5de5a237b22b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6895cc5f1d5a9b3a5858aaa9fb818211539cc93fff8537c3850f1880134f5a56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce2858e9a92734e8762b1def0ba6217ff5a4ecf2a7c65c659941e1c1c80b150d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3ScalingUpPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3ScalingUpPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d24de9f0347fb237d351bea67e01374104a2e06099a08462e9c03e5b2992d25b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAction")
    def put_action(
        self,
        *,
        adjustment: typing.Optional[builtins.str] = None,
        maximum: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#maximum ElastigroupAzureV3#maximum}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#minimum ElastigroupAzureV3#minimum}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#target ElastigroupAzureV3#target}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        '''
        value = ElastigroupAzureV3ScalingUpPolicyAction(
            adjustment=adjustment,
            maximum=maximum,
            minimum=minimum,
            target=target,
            type=type,
        )

        return typing.cast(None, jsii.invoke(self, "putAction", [value]))

    @jsii.member(jsii_name="putDimensions")
    def put_dimensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingUpPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8055124bc83e426df3d8515211494a3f5f51908cbe8f27e852f811cc850595e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimensions", [value]))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> ElastigroupAzureV3ScalingUpPolicyActionOutputReference:
        return typing.cast(ElastigroupAzureV3ScalingUpPolicyActionOutputReference, jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> ElastigroupAzureV3ScalingUpPolicyDimensionsList:
        return typing.cast(ElastigroupAzureV3ScalingUpPolicyDimensionsList, jsii.get(self, "dimensions"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[ElastigroupAzureV3ScalingUpPolicyAction]:
        return typing.cast(typing.Optional[ElastigroupAzureV3ScalingUpPolicyAction], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicyDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicyDimensions]]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

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
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0a5089e7663f663e3bbd40fb593d91672891b3992735bab172fbff430344625)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__549dc72a20332677f26c9856f6e0a7aeb3ed65a4fc030388f1384cf27148d40c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__fd34b77845edbeae017e2d0496194004816d4f82ab6d0f2c2f69cec1068bd4c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b70ee887a29a864487189616a060682d2ee31f793c02e98a42cbbbca8affb2db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__687e38a0a023fdd9b15305223778abab3cc74e67c72bc6a4aaa58afc6e150a86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faa6fd3d4f951e2b3456a0ae6eda74b790f36b6490b1b7398fbfc3c7422d5cab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8de062841d1990d7d2a1fc798e45f9c53504496a14a16f08a4214e7cf33923a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__654868db82f958b006cd60050b957d8cfec023ccdeeed56d3b492ea14e5aa4df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f68bbb060452602b6cf70d6d47fc4b4eae425d968949d0e81c5e8348e2f87f85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__790cf129be703db99850f8ee898154af986d3663206aec895196c76a381dde94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__290e91ff8cdd2dfcc06180e7a457f2a38fd7070e2e5e0fc8701d186da8264ae9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7528cc63c79d9c43ed631ba0c27ba16a9831d1ed83988b5619a4d29bac2223e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c74903dac0cbd565495be32dcc0b43c58eb8f119db8ab2bcdbf39bd787fb6db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SchedulingTask",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "is_enabled": "isEnabled",
        "type": "type",
        "adjustment": "adjustment",
        "adjustment_percentage": "adjustmentPercentage",
        "batch_size_percentage": "batchSizePercentage",
        "grace_period": "gracePeriod",
        "scale_max_capacity": "scaleMaxCapacity",
        "scale_min_capacity": "scaleMinCapacity",
        "scale_target_capacity": "scaleTargetCapacity",
    },
)
class ElastigroupAzureV3SchedulingTask:
    def __init__(
        self,
        *,
        cron_expression: builtins.str,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        type: builtins.str,
        adjustment: typing.Optional[builtins.str] = None,
        adjustment_percentage: typing.Optional[builtins.str] = None,
        batch_size_percentage: typing.Optional[builtins.str] = None,
        grace_period: typing.Optional[builtins.str] = None,
        scale_max_capacity: typing.Optional[builtins.str] = None,
        scale_min_capacity: typing.Optional[builtins.str] = None,
        scale_target_capacity: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#cron_expression ElastigroupAzureV3#cron_expression}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.
        :param adjustment_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment_percentage ElastigroupAzureV3#adjustment_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#batch_size_percentage ElastigroupAzureV3#batch_size_percentage}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#grace_period ElastigroupAzureV3#grace_period}.
        :param scale_max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scale_max_capacity ElastigroupAzureV3#scale_max_capacity}.
        :param scale_min_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scale_min_capacity ElastigroupAzureV3#scale_min_capacity}.
        :param scale_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scale_target_capacity ElastigroupAzureV3#scale_target_capacity}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1baf926e06cf1e29aff62d3f7bac31ec34fa915213c73e2b77850c2fe2f8d1a8)
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument adjustment", value=adjustment, expected_type=type_hints["adjustment"])
            check_type(argname="argument adjustment_percentage", value=adjustment_percentage, expected_type=type_hints["adjustment_percentage"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
            check_type(argname="argument scale_max_capacity", value=scale_max_capacity, expected_type=type_hints["scale_max_capacity"])
            check_type(argname="argument scale_min_capacity", value=scale_min_capacity, expected_type=type_hints["scale_min_capacity"])
            check_type(argname="argument scale_target_capacity", value=scale_target_capacity, expected_type=type_hints["scale_target_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron_expression": cron_expression,
            "is_enabled": is_enabled,
            "type": type,
        }
        if adjustment is not None:
            self._values["adjustment"] = adjustment
        if adjustment_percentage is not None:
            self._values["adjustment_percentage"] = adjustment_percentage
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if grace_period is not None:
            self._values["grace_period"] = grace_period
        if scale_max_capacity is not None:
            self._values["scale_max_capacity"] = scale_max_capacity
        if scale_min_capacity is not None:
            self._values["scale_min_capacity"] = scale_min_capacity
        if scale_target_capacity is not None:
            self._values["scale_target_capacity"] = scale_target_capacity

    @builtins.property
    def cron_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#cron_expression ElastigroupAzureV3#cron_expression}.'''
        result = self._values.get("cron_expression")
        assert result is not None, "Required property 'cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#is_enabled ElastigroupAzureV3#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment ElastigroupAzureV3#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment_percentage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#adjustment_percentage ElastigroupAzureV3#adjustment_percentage}.'''
        result = self._values.get("adjustment_percentage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#batch_size_percentage ElastigroupAzureV3#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def grace_period(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#grace_period ElastigroupAzureV3#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_max_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scale_max_capacity ElastigroupAzureV3#scale_max_capacity}.'''
        result = self._values.get("scale_max_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_min_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scale_min_capacity ElastigroupAzureV3#scale_min_capacity}.'''
        result = self._values.get("scale_min_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#scale_target_capacity ElastigroupAzureV3#scale_target_capacity}.'''
        result = self._values.get("scale_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3SchedulingTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3SchedulingTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SchedulingTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__004091e08ea851298ad63dc447ad6251c59f7bab913a5a29aca4347499492403)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3SchedulingTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__632bf01fdc31545bb47cc4d245a759678637fc3b4d3c8b4eec52724e9a83f15e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3SchedulingTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4539b242d0b0609ed58f9e43910ecfda6264b8c3a2d6a49bc5273b7bcc30094)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f2a087e25aa3ee044af6352f43e66246df690322c843cdd2825238f78891050)
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
            type_hints = typing.get_type_hints(_typecheckingstub__04b44e70e01cc0505d77825a268572691aceada9bcbf14394ae6f8cee4164110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SchedulingTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SchedulingTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SchedulingTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1734771bc027df32e317d26a983ec39a8dd567bda285bbf28ab8b14998cc1f52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3SchedulingTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SchedulingTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67f439eae8b15f5d4d06e91ae3a8ee2672ff10176319c3ece582320f119a251a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAdjustment")
    def reset_adjustment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdjustment", []))

    @jsii.member(jsii_name="resetAdjustmentPercentage")
    def reset_adjustment_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdjustmentPercentage", []))

    @jsii.member(jsii_name="resetBatchSizePercentage")
    def reset_batch_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSizePercentage", []))

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

    @jsii.member(jsii_name="resetScaleMaxCapacity")
    def reset_scale_max_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleMaxCapacity", []))

    @jsii.member(jsii_name="resetScaleMinCapacity")
    def reset_scale_min_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleMinCapacity", []))

    @jsii.member(jsii_name="resetScaleTargetCapacity")
    def reset_scale_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleTargetCapacity", []))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentPercentageInput")
    def adjustment_percentage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="cronExpressionInput")
    def cron_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronExpressionInput"))

    @builtins.property
    @jsii.member(jsii_name="gracePeriodInput")
    def grace_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gracePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleMaxCapacityInput")
    def scale_max_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scaleMaxCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleMinCapacityInput")
    def scale_min_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scaleMinCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleTargetCapacityInput")
    def scale_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scaleTargetCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e222ae5cfcfe87ddcb7b3ed2316e2e909b111bc4d8e9136292e157704c19e350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustmentPercentage")
    def adjustment_percentage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustmentPercentage"))

    @adjustment_percentage.setter
    def adjustment_percentage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ddc631f46b68d52c145be1397618ee76c0b826121ba9361b1a5669d4dc37cbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustmentPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ef2df51b9caba671f36a18eca354d1dc5fbc95d6471d31c4a354f6bc29b9f29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cronExpression")
    def cron_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cronExpression"))

    @cron_expression.setter
    def cron_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06afdd0811f1d8c9e14a87c797bc66cfe8c7adb61794f7a517b2aaff4ae3c5ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cronExpression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1033b8a73f685070e9cf22fa9d77d240046e7ee74cd2fdfe381fc100e55cce9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gracePeriod", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__1bd42ea738ba1b5ff7ab7ca6b265b0f4bda109e70a3b1c74369a151c6b94eba3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleMaxCapacity")
    def scale_max_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleMaxCapacity"))

    @scale_max_capacity.setter
    def scale_max_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7dc297ea688cadd3d4b0313bb60c9ea3822a1598b6bd332a22931c021d4283f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleMaxCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleMinCapacity")
    def scale_min_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleMinCapacity"))

    @scale_min_capacity.setter
    def scale_min_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6d9c3eb0840d562f4385841bc1088b5edcbaf0dcbaf244be49ffc5eec574d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleMinCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleTargetCapacity")
    def scale_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleTargetCapacity"))

    @scale_target_capacity.setter
    def scale_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3c1f2e60b0698f3dcb3679f30cb2c27778cad0304904a1910d2b32533c8ca2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7207af54f310b76b4453afc966bdc56c3df2e2621be4e8fe3d6ea93e104e9e60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SchedulingTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SchedulingTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SchedulingTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e71352e3e095a07d56463eaca40f19e9916854050135e73bf6ef7bb77a8997e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Secret",
    jsii_struct_bases=[],
    name_mapping={
        "source_vault": "sourceVault",
        "vault_certificates": "vaultCertificates",
    },
)
class ElastigroupAzureV3Secret:
    def __init__(
        self,
        *,
        source_vault: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SecretSourceVault", typing.Dict[builtins.str, typing.Any]]]],
        vault_certificates: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SecretVaultCertificates", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param source_vault: source_vault block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source_vault ElastigroupAzureV3#source_vault}
        :param vault_certificates: vault_certificates block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vault_certificates ElastigroupAzureV3#vault_certificates}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9458ce462827bd6279d29be1281399f6051752a5d5153129bb70435f8fda3f8)
            check_type(argname="argument source_vault", value=source_vault, expected_type=type_hints["source_vault"])
            check_type(argname="argument vault_certificates", value=vault_certificates, expected_type=type_hints["vault_certificates"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_vault": source_vault,
            "vault_certificates": vault_certificates,
        }

    @builtins.property
    def source_vault(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretSourceVault"]]:
        '''source_vault block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#source_vault ElastigroupAzureV3#source_vault}
        '''
        result = self._values.get("source_vault")
        assert result is not None, "Required property 'source_vault' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretSourceVault"]], result)

    @builtins.property
    def vault_certificates(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretVaultCertificates"]]:
        '''vault_certificates block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vault_certificates ElastigroupAzureV3#vault_certificates}
        '''
        result = self._values.get("vault_certificates")
        assert result is not None, "Required property 'vault_certificates' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretVaultCertificates"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Secret(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3SecretList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__183b826d9e40fd33c8e4456fb2b70c33a621fe8f7dce66976079225c26266d06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3SecretOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cb3715f1331558e82d3e5fe92bd53bcfc96123d55a036af087a49121c65973a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3SecretOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f521b326318f3aa12ff2d04dfe78856f946bf137d86a7d481dd05878646a1a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2486a722e8a012bf838bc2130686961c2c10662e9e0c4759a61d8d6b1a150235)
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
            type_hints = typing.get_type_hints(_typecheckingstub__026a05b1020dcd5b96bd8d3b7ebd3983f3c056a9e9ae6180414433f765fef637)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Secret]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Secret]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Secret]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ac5f2cdf4381c63d034840607e47b88b94639a3befe2fdb398b66f2aec1ca82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3SecretOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dcaa459890d254a23d6422c15fc88af6ff6a5ff9bc0745f9d841d1ded6ab9ed9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putSourceVault")
    def put_source_vault(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SecretSourceVault", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3901a47746ca5cee64c86c5cb2134eb10f7b067f22b212b30333714cc13ec5b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSourceVault", [value]))

    @jsii.member(jsii_name="putVaultCertificates")
    def put_vault_certificates(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAzureV3SecretVaultCertificates", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fdbe594779f9c2f4578037fe2425bbe60eb8f3c9fbc8b9e48af3abd74cc006a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVaultCertificates", [value]))

    @builtins.property
    @jsii.member(jsii_name="sourceVault")
    def source_vault(self) -> "ElastigroupAzureV3SecretSourceVaultList":
        return typing.cast("ElastigroupAzureV3SecretSourceVaultList", jsii.get(self, "sourceVault"))

    @builtins.property
    @jsii.member(jsii_name="vaultCertificates")
    def vault_certificates(self) -> "ElastigroupAzureV3SecretVaultCertificatesList":
        return typing.cast("ElastigroupAzureV3SecretVaultCertificatesList", jsii.get(self, "vaultCertificates"))

    @builtins.property
    @jsii.member(jsii_name="sourceVaultInput")
    def source_vault_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretSourceVault"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretSourceVault"]]], jsii.get(self, "sourceVaultInput"))

    @builtins.property
    @jsii.member(jsii_name="vaultCertificatesInput")
    def vault_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretVaultCertificates"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAzureV3SecretVaultCertificates"]]], jsii.get(self, "vaultCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Secret]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Secret]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Secret]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac09ee6d862e0569f79d27f27546e32ffc458d52d3766de48a1608b5f24db1f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretSourceVault",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class ElastigroupAzureV3SecretSourceVault:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1009eb89ba798e6eff0a47ed67fac0251a9486387a57eb971433d51e06c26386)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#name ElastigroupAzureV3#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#resource_group_name ElastigroupAzureV3#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3SecretSourceVault(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3SecretSourceVaultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretSourceVaultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8eec1485b1eb695f3f855d69637b6df7aac45ca208b4f55ddd4594f2f2f1e21c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3SecretSourceVaultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1da4d910cfeeb22e7b659ee1a5a8e909e4a147c0ab28f708401a78406009573)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3SecretSourceVaultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c536892dd50cf15c865fd85fd8df78ecf3fbba679f1ab2c34f09ab9f4042483)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a45ecadc1d767493f66b83560733033081c2ca95e099ae56ccfd9b99565af697)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6f66d849dd2a493e9777f30a90a026d315ef52d9feb33ced708562bc9168e59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretSourceVault]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretSourceVault]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretSourceVault]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82584cc51934b3a69fb2a3be4be59b0db57dd9de1f69daf3bca89c1989648c5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3SecretSourceVaultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretSourceVaultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__68437cc5d5c294593f25b8e0e1f062bb841d9c815680f07d2ec347d29f99dd81)
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
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acee576ef0c806d0f25a3ea46320071a192cfe8aa69084d97b18e679da98b3b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f51fa58136438af3c254f642e417b21dd5beba68f291636ebe2d6eda8352de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretSourceVault]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretSourceVault]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretSourceVault]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed9845c8299baf81589284be2751863c111690a0f2d1b31bf6789984ca7cc255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretVaultCertificates",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_store": "certificateStore",
        "certificate_url": "certificateUrl",
    },
)
class ElastigroupAzureV3SecretVaultCertificates:
    def __init__(
        self,
        *,
        certificate_store: builtins.str,
        certificate_url: builtins.str,
    ) -> None:
        '''
        :param certificate_store: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#certificate_store ElastigroupAzureV3#certificate_store}.
        :param certificate_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#certificate_url ElastigroupAzureV3#certificate_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7dd83e52c0cfa31ec90c0f30565ebc501886046edf7a0f6b273e2845278c4e1)
            check_type(argname="argument certificate_store", value=certificate_store, expected_type=type_hints["certificate_store"])
            check_type(argname="argument certificate_url", value=certificate_url, expected_type=type_hints["certificate_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate_store": certificate_store,
            "certificate_url": certificate_url,
        }

    @builtins.property
    def certificate_store(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#certificate_store ElastigroupAzureV3#certificate_store}.'''
        result = self._values.get("certificate_store")
        assert result is not None, "Required property 'certificate_store' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#certificate_url ElastigroupAzureV3#certificate_url}.'''
        result = self._values.get("certificate_url")
        assert result is not None, "Required property 'certificate_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3SecretVaultCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3SecretVaultCertificatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretVaultCertificatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__87b3a0266bf22a5c72a29bb78ebfa34ec4de36e54f933b520ecdbbe3db43ea26)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAzureV3SecretVaultCertificatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99c7e3a1c61cf9d4eb92073805bfb8c968451abc5ffef05ac7c3da1ca662a48b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3SecretVaultCertificatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b3c6664baabd25f4f62151f4590fd5c3f09dfd0e82d254e8e5fe672d66ac30)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c27550fda160ed8d92d8513435862f04d97895bdde8d2d5ba575e23dfd069e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__216d7726878c1623cea765ac7e9ea1e88c57133aeac4a0f7b8298bfc89b588b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretVaultCertificates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretVaultCertificates]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretVaultCertificates]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c47484e6612a91edd469af0f6e3db30577344c26600c0a306b56dd096d72c86c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3SecretVaultCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecretVaultCertificatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8e4ef0a870cccda8b0456d2cad30cc00107880b99f406dfda379b87899fbad4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="certificateStoreInput")
    def certificate_store_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateStoreInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateUrlInput")
    def certificate_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateStore")
    def certificate_store(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateStore"))

    @certificate_store.setter
    def certificate_store(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b26e95b2a39b07845f108908a65e7aff0a11a901bfdd56f50106d1a2e4db54a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateUrl")
    def certificate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateUrl"))

    @certificate_url.setter
    def certificate_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79fc18e32d0ea64d5f18efb81b8a596847d508d8bf2ea6fe6b9a6799b471c3a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretVaultCertificates]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretVaultCertificates]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretVaultCertificates]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36ea151b11d9395711ce462d48aa253f0ecbca578baff819afbaf0b4034798b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Security",
    jsii_struct_bases=[],
    name_mapping={
        "confidential_os_disk_encryption": "confidentialOsDiskEncryption",
        "encryption_at_host": "encryptionAtHost",
        "secure_boot_enabled": "secureBootEnabled",
        "security_type": "securityType",
        "vtpm_enabled": "vtpmEnabled",
    },
)
class ElastigroupAzureV3Security:
    def __init__(
        self,
        *,
        confidential_os_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_at_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        security_type: typing.Optional[builtins.str] = None,
        vtpm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param confidential_os_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#confidential_os_disk_encryption ElastigroupAzureV3#confidential_os_disk_encryption}.
        :param encryption_at_host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#encryption_at_host ElastigroupAzureV3#encryption_at_host}.
        :param secure_boot_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secure_boot_enabled ElastigroupAzureV3#secure_boot_enabled}.
        :param security_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security_type ElastigroupAzureV3#security_type}.
        :param vtpm_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vtpm_enabled ElastigroupAzureV3#vtpm_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f6188903801f2cf9f64fc02aa1a2bbd3484a7e7ab7e6763ae3196e8cb9dd712)
            check_type(argname="argument confidential_os_disk_encryption", value=confidential_os_disk_encryption, expected_type=type_hints["confidential_os_disk_encryption"])
            check_type(argname="argument encryption_at_host", value=encryption_at_host, expected_type=type_hints["encryption_at_host"])
            check_type(argname="argument secure_boot_enabled", value=secure_boot_enabled, expected_type=type_hints["secure_boot_enabled"])
            check_type(argname="argument security_type", value=security_type, expected_type=type_hints["security_type"])
            check_type(argname="argument vtpm_enabled", value=vtpm_enabled, expected_type=type_hints["vtpm_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if confidential_os_disk_encryption is not None:
            self._values["confidential_os_disk_encryption"] = confidential_os_disk_encryption
        if encryption_at_host is not None:
            self._values["encryption_at_host"] = encryption_at_host
        if secure_boot_enabled is not None:
            self._values["secure_boot_enabled"] = secure_boot_enabled
        if security_type is not None:
            self._values["security_type"] = security_type
        if vtpm_enabled is not None:
            self._values["vtpm_enabled"] = vtpm_enabled

    @builtins.property
    def confidential_os_disk_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#confidential_os_disk_encryption ElastigroupAzureV3#confidential_os_disk_encryption}.'''
        result = self._values.get("confidential_os_disk_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_at_host(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#encryption_at_host ElastigroupAzureV3#encryption_at_host}.'''
        result = self._values.get("encryption_at_host")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_boot_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#secure_boot_enabled ElastigroupAzureV3#secure_boot_enabled}.'''
        result = self._values.get("secure_boot_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def security_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#security_type ElastigroupAzureV3#security_type}.'''
        result = self._values.get("security_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vtpm_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#vtpm_enabled ElastigroupAzureV3#vtpm_enabled}.'''
        result = self._values.get("vtpm_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Security(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3SecurityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SecurityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__582d224d6fbcb10f3848b4dc6fea71e4d4f8f48245389f39147bbf093c20277e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConfidentialOsDiskEncryption")
    def reset_confidential_os_disk_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfidentialOsDiskEncryption", []))

    @jsii.member(jsii_name="resetEncryptionAtHost")
    def reset_encryption_at_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAtHost", []))

    @jsii.member(jsii_name="resetSecureBootEnabled")
    def reset_secure_boot_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureBootEnabled", []))

    @jsii.member(jsii_name="resetSecurityType")
    def reset_security_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityType", []))

    @jsii.member(jsii_name="resetVtpmEnabled")
    def reset_vtpm_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVtpmEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="confidentialOsDiskEncryptionInput")
    def confidential_os_disk_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "confidentialOsDiskEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAtHostInput")
    def encryption_at_host_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "encryptionAtHostInput"))

    @builtins.property
    @jsii.member(jsii_name="secureBootEnabledInput")
    def secure_boot_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureBootEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="securityTypeInput")
    def security_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="vtpmEnabledInput")
    def vtpm_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "vtpmEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="confidentialOsDiskEncryption")
    def confidential_os_disk_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "confidentialOsDiskEncryption"))

    @confidential_os_disk_encryption.setter
    def confidential_os_disk_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7e611e64ab6a9f292c11ed0733a1c122440fc7319918abcd93e22f45b9169da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confidentialOsDiskEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionAtHost")
    def encryption_at_host(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "encryptionAtHost"))

    @encryption_at_host.setter
    def encryption_at_host(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d88a102919fce2ad7e81b124ad372c5df0a90ff87e8a00e4b1b7652a07b27f1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionAtHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secureBootEnabled")
    def secure_boot_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureBootEnabled"))

    @secure_boot_enabled.setter
    def secure_boot_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73aa2c0417f8ca5870e735b2a0039099ae75ea311ec92500387bde3b7d4062b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureBootEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityType")
    def security_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityType"))

    @security_type.setter
    def security_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb655bbd06cf15e3249388e41774ef3e2e4cc69b5d3cb672e5c85c3cdd731ed4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vtpmEnabled")
    def vtpm_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "vtpmEnabled"))

    @vtpm_enabled.setter
    def vtpm_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__445d8ab39f63ad4bfd55ec84030b1b42274c4663f91f6295dc3e8e4ba7b16b23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vtpmEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3Security]:
        return typing.cast(typing.Optional[ElastigroupAzureV3Security], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3Security],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfe38d24ab6d4ca999e6b655762e659e48bf464f5026de7a34a01d19a94e5305)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Signal",
    jsii_struct_bases=[],
    name_mapping={"timeout": "timeout", "type": "type"},
)
class ElastigroupAzureV3Signal:
    def __init__(self, *, timeout: jsii.Number, type: builtins.str) -> None:
        '''
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#timeout ElastigroupAzureV3#timeout}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe47eff6dfa1b8c49a8d1d1388721368472dda7c9056706fad67977237083c01)
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "timeout": timeout,
            "type": type,
        }

    @builtins.property
    def timeout(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#timeout ElastigroupAzureV3#timeout}.'''
        result = self._values.get("timeout")
        assert result is not None, "Required property 'timeout' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#type ElastigroupAzureV3#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Signal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3SignalList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SignalList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad44d7c7753e5c5acc58f42861282cb83dd161e87b8fde161616f3abe1363901)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3SignalOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0873c13d1d2211629ec922c399f6695050773b5c5bf0b79e3b7df2158d27fdba)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3SignalOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57564c7bdc65c48c8775347b4a204fe3ef31a6ae90f641033fa90ed0ef800199)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0baf48df6a45633a5036efde101ccc6202b5abdb441bd5a5bd8e5db1e8f8873)
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
            type_hints = typing.get_type_hints(_typecheckingstub__69d016a16cd42613948a91f8be32f75623b581265a5e5d76a7878754112012fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Signal]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Signal]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Signal]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e5631be7ac5f5fe3f33912496689e6926e5895569d2709af476a3ac4d37fd6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3SignalOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3SignalOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9585a17e7c7f04911a06c7ca7ccb4bacbb8bb95d7225bd8d7e386267f50be009)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5223f25b5dc398a4326f9e86be4c322e961d07482664eee32626e4e9fd95d5fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05059668a0d1ec3a0fbce218ebef1c3b4cc638840142ede3f1fbac89c971870a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Signal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Signal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Signal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__719f3ea9c9ed9f5685fe1e0dd20e3b40506ef2e13394360711daeff11928a1e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3Tags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ElastigroupAzureV3Tags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#key ElastigroupAzureV3#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#value ElastigroupAzureV3#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d46f7942c9eb6b01f8f052d77af573d86b6abd37958131be25567ed6e01af2d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#key ElastigroupAzureV3#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#value ElastigroupAzureV3#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3Tags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3TagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3TagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e5ae827b185397274ff7514d1817dcf2ebd8ea5229230a041322e523f84b08f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ElastigroupAzureV3TagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6353b9b2f0d2aec0dd8c782d6502a05e5a40d510ba35a385505df6cff729712a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAzureV3TagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35a0b7b9726ba36b5a8f46ac0021b564b6f39d3432c9cfd755217be5db55d505)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f39a62df7daf8d492dd7a2c1771113a4a1713c62f14314d5c7ceb2e2cf331ae2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1a815d48f11dd53b27b652ed11b0c969f1c065668d02c3c716b2500f7df9bcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Tags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Tags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Tags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ee0adc52a581046c7695e859afa89a0bc8075581d00cc6c5eb4d68ec3c379d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAzureV3TagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3TagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a849bc387f55273f4446e6b4ca98287e307a27d5374b4b6aba0a939993cad0a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa2c1f1862c62f90765d0b45908e66fdee547eaffda2fcb25dc75b93a7847e56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d5080d7a1de6ae2a4d4e66c43d94343036106d9b735dbe1e2d5da4b6e019d26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Tags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Tags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Tags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deaa3cd76407b5970a7452cb42312e150d0b29407f320dabf10e7eef68f0458a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3VmSizes",
    jsii_struct_bases=[],
    name_mapping={
        "od_sizes": "odSizes",
        "excluded_vm_sizes": "excludedVmSizes",
        "preferred_spot_sizes": "preferredSpotSizes",
        "spot_size_attributes": "spotSizeAttributes",
        "spot_sizes": "spotSizes",
    },
)
class ElastigroupAzureV3VmSizes:
    def __init__(
        self,
        *,
        od_sizes: typing.Sequence[builtins.str],
        excluded_vm_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        spot_size_attributes: typing.Optional[typing.Union["ElastigroupAzureV3VmSizesSpotSizeAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param od_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#od_sizes ElastigroupAzureV3#od_sizes}.
        :param excluded_vm_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#excluded_vm_sizes ElastigroupAzureV3#excluded_vm_sizes}.
        :param preferred_spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#preferred_spot_sizes ElastigroupAzureV3#preferred_spot_sizes}.
        :param spot_size_attributes: spot_size_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_size_attributes ElastigroupAzureV3#spot_size_attributes}
        :param spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_sizes ElastigroupAzureV3#spot_sizes}.
        '''
        if isinstance(spot_size_attributes, dict):
            spot_size_attributes = ElastigroupAzureV3VmSizesSpotSizeAttributes(**spot_size_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8341ee4d1b9c90959504f548adb97623c9c345545607326d02c11bca6a55ac8)
            check_type(argname="argument od_sizes", value=od_sizes, expected_type=type_hints["od_sizes"])
            check_type(argname="argument excluded_vm_sizes", value=excluded_vm_sizes, expected_type=type_hints["excluded_vm_sizes"])
            check_type(argname="argument preferred_spot_sizes", value=preferred_spot_sizes, expected_type=type_hints["preferred_spot_sizes"])
            check_type(argname="argument spot_size_attributes", value=spot_size_attributes, expected_type=type_hints["spot_size_attributes"])
            check_type(argname="argument spot_sizes", value=spot_sizes, expected_type=type_hints["spot_sizes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "od_sizes": od_sizes,
        }
        if excluded_vm_sizes is not None:
            self._values["excluded_vm_sizes"] = excluded_vm_sizes
        if preferred_spot_sizes is not None:
            self._values["preferred_spot_sizes"] = preferred_spot_sizes
        if spot_size_attributes is not None:
            self._values["spot_size_attributes"] = spot_size_attributes
        if spot_sizes is not None:
            self._values["spot_sizes"] = spot_sizes

    @builtins.property
    def od_sizes(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#od_sizes ElastigroupAzureV3#od_sizes}.'''
        result = self._values.get("od_sizes")
        assert result is not None, "Required property 'od_sizes' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def excluded_vm_sizes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#excluded_vm_sizes ElastigroupAzureV3#excluded_vm_sizes}.'''
        result = self._values.get("excluded_vm_sizes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preferred_spot_sizes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#preferred_spot_sizes ElastigroupAzureV3#preferred_spot_sizes}.'''
        result = self._values.get("preferred_spot_sizes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def spot_size_attributes(
        self,
    ) -> typing.Optional["ElastigroupAzureV3VmSizesSpotSizeAttributes"]:
        '''spot_size_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_size_attributes ElastigroupAzureV3#spot_size_attributes}
        '''
        result = self._values.get("spot_size_attributes")
        return typing.cast(typing.Optional["ElastigroupAzureV3VmSizesSpotSizeAttributes"], result)

    @builtins.property
    def spot_sizes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#spot_sizes ElastigroupAzureV3#spot_sizes}.'''
        result = self._values.get("spot_sizes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3VmSizes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3VmSizesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3VmSizesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__655f5829fadfaa71ebe7b0cea9be7c08f42c39e6ad4f6706ea2b3d0abe6b7599)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSpotSizeAttributes")
    def put_spot_size_attributes(
        self,
        *,
        max_cpu: typing.Optional[jsii.Number] = None,
        max_memory: typing.Optional[jsii.Number] = None,
        max_storage: typing.Optional[jsii.Number] = None,
        min_cpu: typing.Optional[jsii.Number] = None,
        min_memory: typing.Optional[jsii.Number] = None,
        min_storage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_cpu ElastigroupAzureV3#max_cpu}.
        :param max_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_memory ElastigroupAzureV3#max_memory}.
        :param max_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_storage ElastigroupAzureV3#max_storage}.
        :param min_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_cpu ElastigroupAzureV3#min_cpu}.
        :param min_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_memory ElastigroupAzureV3#min_memory}.
        :param min_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_storage ElastigroupAzureV3#min_storage}.
        '''
        value = ElastigroupAzureV3VmSizesSpotSizeAttributes(
            max_cpu=max_cpu,
            max_memory=max_memory,
            max_storage=max_storage,
            min_cpu=min_cpu,
            min_memory=min_memory,
            min_storage=min_storage,
        )

        return typing.cast(None, jsii.invoke(self, "putSpotSizeAttributes", [value]))

    @jsii.member(jsii_name="resetExcludedVmSizes")
    def reset_excluded_vm_sizes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedVmSizes", []))

    @jsii.member(jsii_name="resetPreferredSpotSizes")
    def reset_preferred_spot_sizes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredSpotSizes", []))

    @jsii.member(jsii_name="resetSpotSizeAttributes")
    def reset_spot_size_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotSizeAttributes", []))

    @jsii.member(jsii_name="resetSpotSizes")
    def reset_spot_sizes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotSizes", []))

    @builtins.property
    @jsii.member(jsii_name="spotSizeAttributes")
    def spot_size_attributes(
        self,
    ) -> "ElastigroupAzureV3VmSizesSpotSizeAttributesOutputReference":
        return typing.cast("ElastigroupAzureV3VmSizesSpotSizeAttributesOutputReference", jsii.get(self, "spotSizeAttributes"))

    @builtins.property
    @jsii.member(jsii_name="excludedVmSizesInput")
    def excluded_vm_sizes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedVmSizesInput"))

    @builtins.property
    @jsii.member(jsii_name="odSizesInput")
    def od_sizes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "odSizesInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredSpotSizesInput")
    def preferred_spot_sizes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredSpotSizesInput"))

    @builtins.property
    @jsii.member(jsii_name="spotSizeAttributesInput")
    def spot_size_attributes_input(
        self,
    ) -> typing.Optional["ElastigroupAzureV3VmSizesSpotSizeAttributes"]:
        return typing.cast(typing.Optional["ElastigroupAzureV3VmSizesSpotSizeAttributes"], jsii.get(self, "spotSizeAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="spotSizesInput")
    def spot_sizes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "spotSizesInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedVmSizes")
    def excluded_vm_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedVmSizes"))

    @excluded_vm_sizes.setter
    def excluded_vm_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b9fda9c4cfb364d8790e5f102f4ebd3e30b8e4669084ec539b58d21a1adf5df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedVmSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="odSizes")
    def od_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "odSizes"))

    @od_sizes.setter
    def od_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e45a4f5fbf63ba5b0aee26302bc7f7520a601ef73966879ee9002cd94e52f96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "odSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredSpotSizes")
    def preferred_spot_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredSpotSizes"))

    @preferred_spot_sizes.setter
    def preferred_spot_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b3c0316bc70becef2c42af3c80caf777e418d119770354c644ecb08315a794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredSpotSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotSizes")
    def spot_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "spotSizes"))

    @spot_sizes.setter
    def spot_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__343a670034d6050b250614f6a66f9b6a65f73100e76eaf37551db606a1841cb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAzureV3VmSizes]:
        return typing.cast(typing.Optional[ElastigroupAzureV3VmSizes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ElastigroupAzureV3VmSizes]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14246746d54fd9bcf96670088c85ee7539531864b72d09bf1089202012425fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3VmSizesSpotSizeAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "max_cpu": "maxCpu",
        "max_memory": "maxMemory",
        "max_storage": "maxStorage",
        "min_cpu": "minCpu",
        "min_memory": "minMemory",
        "min_storage": "minStorage",
    },
)
class ElastigroupAzureV3VmSizesSpotSizeAttributes:
    def __init__(
        self,
        *,
        max_cpu: typing.Optional[jsii.Number] = None,
        max_memory: typing.Optional[jsii.Number] = None,
        max_storage: typing.Optional[jsii.Number] = None,
        min_cpu: typing.Optional[jsii.Number] = None,
        min_memory: typing.Optional[jsii.Number] = None,
        min_storage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_cpu ElastigroupAzureV3#max_cpu}.
        :param max_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_memory ElastigroupAzureV3#max_memory}.
        :param max_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_storage ElastigroupAzureV3#max_storage}.
        :param min_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_cpu ElastigroupAzureV3#min_cpu}.
        :param min_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_memory ElastigroupAzureV3#min_memory}.
        :param min_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_storage ElastigroupAzureV3#min_storage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86fa557cde704a58fa70eb5d0e86fa1ffa043c6ed4144acc5fd0c4c8698dcd23)
            check_type(argname="argument max_cpu", value=max_cpu, expected_type=type_hints["max_cpu"])
            check_type(argname="argument max_memory", value=max_memory, expected_type=type_hints["max_memory"])
            check_type(argname="argument max_storage", value=max_storage, expected_type=type_hints["max_storage"])
            check_type(argname="argument min_cpu", value=min_cpu, expected_type=type_hints["min_cpu"])
            check_type(argname="argument min_memory", value=min_memory, expected_type=type_hints["min_memory"])
            check_type(argname="argument min_storage", value=min_storage, expected_type=type_hints["min_storage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_cpu is not None:
            self._values["max_cpu"] = max_cpu
        if max_memory is not None:
            self._values["max_memory"] = max_memory
        if max_storage is not None:
            self._values["max_storage"] = max_storage
        if min_cpu is not None:
            self._values["min_cpu"] = min_cpu
        if min_memory is not None:
            self._values["min_memory"] = min_memory
        if min_storage is not None:
            self._values["min_storage"] = min_storage

    @builtins.property
    def max_cpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_cpu ElastigroupAzureV3#max_cpu}.'''
        result = self._values.get("max_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_memory(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_memory ElastigroupAzureV3#max_memory}.'''
        result = self._values.get("max_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#max_storage ElastigroupAzureV3#max_storage}.'''
        result = self._values.get("max_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_cpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_cpu ElastigroupAzureV3#min_cpu}.'''
        result = self._values.get("min_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_memory ElastigroupAzureV3#min_memory}.'''
        result = self._values.get("min_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_azure_v3#min_storage ElastigroupAzureV3#min_storage}.'''
        result = self._values.get("min_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAzureV3VmSizesSpotSizeAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAzureV3VmSizesSpotSizeAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAzureV3.ElastigroupAzureV3VmSizesSpotSizeAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b3370808a4baa4fb0394c29c608d95c2c31894931a55b696c17897d5bf9b49f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxCpu")
    def reset_max_cpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCpu", []))

    @jsii.member(jsii_name="resetMaxMemory")
    def reset_max_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMemory", []))

    @jsii.member(jsii_name="resetMaxStorage")
    def reset_max_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStorage", []))

    @jsii.member(jsii_name="resetMinCpu")
    def reset_min_cpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCpu", []))

    @jsii.member(jsii_name="resetMinMemory")
    def reset_min_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinMemory", []))

    @jsii.member(jsii_name="resetMinStorage")
    def reset_min_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinStorage", []))

    @builtins.property
    @jsii.member(jsii_name="maxCpuInput")
    def max_cpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCpuInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMemoryInput")
    def max_memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMemoryInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStorageInput")
    def max_storage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStorageInput"))

    @builtins.property
    @jsii.member(jsii_name="minCpuInput")
    def min_cpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minCpuInput"))

    @builtins.property
    @jsii.member(jsii_name="minMemoryInput")
    def min_memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minMemoryInput"))

    @builtins.property
    @jsii.member(jsii_name="minStorageInput")
    def min_storage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minStorageInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCpu")
    def max_cpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCpu"))

    @max_cpu.setter
    def max_cpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93732599606baa78ad184706b1d90cd7de51cc07e44b344bfbe06cc42742d538)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemory")
    def max_memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemory"))

    @max_memory.setter
    def max_memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc2016d48f48ab972323b4a3fc81e1aab058755d7e973d72e962221883f3c5fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStorage")
    def max_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStorage"))

    @max_storage.setter
    def max_storage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b8f2581cb7b2a816e476cd35e856189fa6a780d89c3fdb384bc3c3b07c40b72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStorage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCpu")
    def min_cpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minCpu"))

    @min_cpu.setter
    def min_cpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49c1ce3932af3cf239fb3922fa4bca3a48edfc385f2f074bcfcd4f1c2bfcd849)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemory")
    def min_memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemory"))

    @min_memory.setter
    def min_memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de539920b0c8762b135c53a32ab80b6a550c8853e14c6524ca4755195e1d2881)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minStorage")
    def min_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minStorage"))

    @min_storage.setter
    def min_storage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78546068310fe8a6890d7509dfbbcd5d596c16da54a127469894524afac50909)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minStorage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAzureV3VmSizesSpotSizeAttributes]:
        return typing.cast(typing.Optional[ElastigroupAzureV3VmSizesSpotSizeAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAzureV3VmSizesSpotSizeAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab10a292972f81f1564aac0fe3a034d67139a7e1764b7d3703ff26e93685b174)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ElastigroupAzureV3",
    "ElastigroupAzureV3BootDiagnostics",
    "ElastigroupAzureV3BootDiagnosticsList",
    "ElastigroupAzureV3BootDiagnosticsOutputReference",
    "ElastigroupAzureV3CapacityReservation",
    "ElastigroupAzureV3CapacityReservationCapacityReservationGroups",
    "ElastigroupAzureV3CapacityReservationCapacityReservationGroupsOutputReference",
    "ElastigroupAzureV3CapacityReservationOutputReference",
    "ElastigroupAzureV3Config",
    "ElastigroupAzureV3DataDisk",
    "ElastigroupAzureV3DataDiskList",
    "ElastigroupAzureV3DataDiskOutputReference",
    "ElastigroupAzureV3Extensions",
    "ElastigroupAzureV3ExtensionsList",
    "ElastigroupAzureV3ExtensionsOutputReference",
    "ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault",
    "ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVaultOutputReference",
    "ElastigroupAzureV3Health",
    "ElastigroupAzureV3HealthOutputReference",
    "ElastigroupAzureV3Image",
    "ElastigroupAzureV3ImageCustom",
    "ElastigroupAzureV3ImageCustomList",
    "ElastigroupAzureV3ImageCustomOutputReference",
    "ElastigroupAzureV3ImageGalleryImage",
    "ElastigroupAzureV3ImageGalleryImageList",
    "ElastigroupAzureV3ImageGalleryImageOutputReference",
    "ElastigroupAzureV3ImageList",
    "ElastigroupAzureV3ImageMarketplace",
    "ElastigroupAzureV3ImageMarketplaceList",
    "ElastigroupAzureV3ImageMarketplaceOutputReference",
    "ElastigroupAzureV3ImageOutputReference",
    "ElastigroupAzureV3LoadBalancer",
    "ElastigroupAzureV3LoadBalancerList",
    "ElastigroupAzureV3LoadBalancerOutputReference",
    "ElastigroupAzureV3Login",
    "ElastigroupAzureV3LoginOutputReference",
    "ElastigroupAzureV3ManagedServiceIdentity",
    "ElastigroupAzureV3ManagedServiceIdentityList",
    "ElastigroupAzureV3ManagedServiceIdentityOutputReference",
    "ElastigroupAzureV3Network",
    "ElastigroupAzureV3NetworkNetworkInterfaces",
    "ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs",
    "ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsList",
    "ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigsOutputReference",
    "ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup",
    "ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupList",
    "ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroupOutputReference",
    "ElastigroupAzureV3NetworkNetworkInterfacesList",
    "ElastigroupAzureV3NetworkNetworkInterfacesOutputReference",
    "ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup",
    "ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupList",
    "ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroupOutputReference",
    "ElastigroupAzureV3NetworkOutputReference",
    "ElastigroupAzureV3OsDisk",
    "ElastigroupAzureV3OsDiskOutputReference",
    "ElastigroupAzureV3ProximityPlacementGroups",
    "ElastigroupAzureV3ProximityPlacementGroupsList",
    "ElastigroupAzureV3ProximityPlacementGroupsOutputReference",
    "ElastigroupAzureV3RevertToSpot",
    "ElastigroupAzureV3RevertToSpotOutputReference",
    "ElastigroupAzureV3ScalingDownPolicy",
    "ElastigroupAzureV3ScalingDownPolicyAction",
    "ElastigroupAzureV3ScalingDownPolicyActionOutputReference",
    "ElastigroupAzureV3ScalingDownPolicyDimensions",
    "ElastigroupAzureV3ScalingDownPolicyDimensionsList",
    "ElastigroupAzureV3ScalingDownPolicyDimensionsOutputReference",
    "ElastigroupAzureV3ScalingDownPolicyList",
    "ElastigroupAzureV3ScalingDownPolicyOutputReference",
    "ElastigroupAzureV3ScalingUpPolicy",
    "ElastigroupAzureV3ScalingUpPolicyAction",
    "ElastigroupAzureV3ScalingUpPolicyActionOutputReference",
    "ElastigroupAzureV3ScalingUpPolicyDimensions",
    "ElastigroupAzureV3ScalingUpPolicyDimensionsList",
    "ElastigroupAzureV3ScalingUpPolicyDimensionsOutputReference",
    "ElastigroupAzureV3ScalingUpPolicyList",
    "ElastigroupAzureV3ScalingUpPolicyOutputReference",
    "ElastigroupAzureV3SchedulingTask",
    "ElastigroupAzureV3SchedulingTaskList",
    "ElastigroupAzureV3SchedulingTaskOutputReference",
    "ElastigroupAzureV3Secret",
    "ElastigroupAzureV3SecretList",
    "ElastigroupAzureV3SecretOutputReference",
    "ElastigroupAzureV3SecretSourceVault",
    "ElastigroupAzureV3SecretSourceVaultList",
    "ElastigroupAzureV3SecretSourceVaultOutputReference",
    "ElastigroupAzureV3SecretVaultCertificates",
    "ElastigroupAzureV3SecretVaultCertificatesList",
    "ElastigroupAzureV3SecretVaultCertificatesOutputReference",
    "ElastigroupAzureV3Security",
    "ElastigroupAzureV3SecurityOutputReference",
    "ElastigroupAzureV3Signal",
    "ElastigroupAzureV3SignalList",
    "ElastigroupAzureV3SignalOutputReference",
    "ElastigroupAzureV3Tags",
    "ElastigroupAzureV3TagsList",
    "ElastigroupAzureV3TagsOutputReference",
    "ElastigroupAzureV3VmSizes",
    "ElastigroupAzureV3VmSizesOutputReference",
    "ElastigroupAzureV3VmSizesSpotSizeAttributes",
    "ElastigroupAzureV3VmSizesSpotSizeAttributesOutputReference",
]

publication.publish()

def _typecheckingstub__53f7c061b4714ed0e34fd061e2e2b00e6d764bdcc37298b4b59f4797cf347893(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    name: builtins.str,
    network: typing.Union[ElastigroupAzureV3Network, typing.Dict[builtins.str, typing.Any]],
    os: builtins.str,
    region: builtins.str,
    resource_group_name: builtins.str,
    vm_sizes: typing.Union[ElastigroupAzureV3VmSizes, typing.Dict[builtins.str, typing.Any]],
    availability_vs_cost: typing.Optional[jsii.Number] = None,
    boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3BootDiagnostics, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capacity_reservation: typing.Optional[typing.Union[ElastigroupAzureV3CapacityReservation, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_data: typing.Optional[builtins.str] = None,
    data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3DataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Extensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    health: typing.Optional[typing.Union[ElastigroupAzureV3Health, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Image, typing.Dict[builtins.str, typing.Any]]]]] = None,
    load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3LoadBalancer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    login: typing.Optional[typing.Union[ElastigroupAzureV3Login, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_service_identity: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ManagedServiceIdentity, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    on_demand_count: typing.Optional[jsii.Number] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    os_disk: typing.Optional[typing.Union[ElastigroupAzureV3OsDisk, typing.Dict[builtins.str, typing.Any]]] = None,
    preferred_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ProximityPlacementGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    revert_to_spot: typing.Optional[typing.Union[ElastigroupAzureV3RevertToSpot, typing.Dict[builtins.str, typing.Any]]] = None,
    scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Secret, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security: typing.Optional[typing.Union[ElastigroupAzureV3Security, typing.Dict[builtins.str, typing.Any]]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Signal, typing.Dict[builtins.str, typing.Any]]]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Tags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    user_data: typing.Optional[builtins.str] = None,
    vm_name_prefix: typing.Optional[builtins.str] = None,
    zones: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__8c534953e092d487ada42112f101456eea77aa7b85820daf3a03ae5592c1aeff(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ca1ebd463f681bfc6281635566a7a672526abadb6f3602fb720dbdfb45eb8e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3BootDiagnostics, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59902e1da0d04e351df0bd04ef0d6e4380f5776b312d13e93cae18653ae9d9c3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3DataDisk, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5845c82aa4ecf191f180b7d4aded9996aa6d67571e10462559d23ba0ef9ab0b8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Extensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21d59cb1cb9dde435082d87fae76afe4c1f26e397ebd82861b71f68d27214b57(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Image, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__780236eaf3c7244a0704795b6dbdee6523671420862eac4af12172fdf4c8948a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3LoadBalancer, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7cd62849b1c2011977b8065f1f565cf340f1c12155e8213bb02a0b79f06dbe(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ManagedServiceIdentity, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbdf019b3e060828b24c3f9ce3c3ae8bec91796a033429ea27853879e9969a9e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ProximityPlacementGroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f069f544160fabc9e52c2aacb944cd8ae65553f43d7c84bd2e9b719d3b94fcce(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506528337c3ed268b9d70ae5002466346a15e31b635158bf567ef9d906e3da4c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4699c1abfd00ee7b69f44505e539824938388bb85f4f98255aaf2220a268bdaf(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SchedulingTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e13f6f8a4bd851f260f64c357d14a6d5f13faa18b9e1ea45d77c17d2ac3e90a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Secret, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e537ea3444b244bfc9c1593da970e0050d46abc0cea73b34c7adc7d4bb41afb7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Signal, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d068333819880e4eb44d6218604088f95ee0bd9f6edb512e96e2d407b6e2b140(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Tags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbd7f746ea383525116b16f5de031c6443401ad05daf392e19ee30c96e7dddf0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f876fbc4c7e79444086b5095158074843d1ff30b801c390e6a7240fb37d355d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94ed00d078664c6a773cdbf9ebca1810982eb6e1523dd2dd4e204513a0011c0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe58ccb567210b120ce792fbbaa40aaa6dc07467cd0cc77229a285f4f2e574dd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07b6a667380233684aec1d9dc1307b42978a915c3ef2ff4ca2e73ade80289372(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6695cef71ddb2b7f7ac678846b45f3dd31df28aaa71b452c21e09859c1dae7e1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f6d034d8a92d25a595356eda4160ff0849c893aa239daa1d6c9c22fb5162645(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd725f02a67b5ef7be31ba86897bf88c4e9077077ace70cf5da84203ca86879(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86b94b66b7a2f2a5077c493e3902acf43a99720cc101fcefc9ccc39fbbb8e84(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__662bb7b3318d34466a4f81f5394d52df5875516081bdcb71ba2155735ae3a99b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3031bfe395d694d4a5af030d21b0b58563520c519de714aaca7d6925f9685550(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d8a11d55249d3e427fcc60176175b07aaaee9470b9828b0b47ea79eccddc74a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__397fa1b95dee853896ce46be6ba62e69a3b6e2532fe28d9b4927a9af4f7e4d96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0694f8456bfaa0f2f807f8a3ea97de28892e95792eec55e03af3777d5a74127b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07807e45fbffe00c3e7a6a9bdbecf1c268dfe46ca1a61df7a3a50468e72e25c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c628008e7b0a6e19c06d95614a1d68262e64998203a6d686308f4a7e15b13f67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efff9e1133251a9fd6d457ef2b83d15697c119643cf0d2ea36fad9deb23df5f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3163b95d7705de7c3f138afd6e20179e6aac8a038681bce0abe6fc427cf6362b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__211d5158d50e5dc6104a7047fd6999f54d55b3ad5e32425235be5773bcea436d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__941d3ce2be3b425d1ce45bfb648229dc55aa6d31c92ad4b4f1a467f161733808(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba1e8727122a82b61c9c501c52a2672ce780724dfd89b0c6922b528eaff4f9a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eef5e3545af66379d3983dc38a14ae456b317527581fe9017f71ae0f6eb27f7(
    *,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    type: builtins.str,
    storage_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fe6ca23069d5fb6bd6ca349d8d332b23f14d7a8412de0786a87b653c6ba18d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31f82674e73634a0ffb9e957d568240d373426bc7c5c2d4fd507cfbe6dec6a6d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7d55ca278df0951079a9e707ee9d86c737c8a2181be3ed92cfa666fba5ba1b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc50c4b194ccc11ce247b2a706a376e3a2f1b81766729aa636f1883b8ea62f2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3329c721f31a45523c72859b79895276281160f2f8ee022064611c4d6428c86(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78d6cec60ffe47ccdc3f734012b9c3df7645aa36761b99ebaa5801fefe0348b2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3BootDiagnostics]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dfaee2f86aa3e885ca69e57a17eb23aeec24db8f0e46937012bdaf3d04c3eac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebd3560836475940028d483df552cf7a0e6f85a7e6ec2717856e5486d6e92f1a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a38150c5741deed8e50ac654681c02fa759ef132723ff29081582c3120ac65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a115b638996ea60825c36d79e907019900297b9e2eb27690d93f9116ad9a8f75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__115b5b6bfb5b6b91504ac749a90feb473f303fcfa5f990776a0619c0cf58e948(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3BootDiagnostics]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd6fbce92548bb2c5736104ae5cece13fc7dac1db28b1ef3926ccffa9bc3c4ec(
    *,
    should_utilize: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    utilization_strategy: builtins.str,
    capacity_reservation_groups: typing.Optional[typing.Union[ElastigroupAzureV3CapacityReservationCapacityReservationGroups, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac9ce427b5240fa4e58b6a8b76a380a3b1dc06c7d40c5e003a060f8eedd076b1(
    *,
    crg_name: builtins.str,
    crg_resource_group_name: builtins.str,
    crg_should_prioritize: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab032a90ccfe39842606c8ef487d5e057c47eae252efee3a69c883b492164a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6516a292486414dd2cb31fef4c961cc3d78cfee5df77f250aba3b30d3eb6446(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cc14c6ee052d0582dd018f0779c39381a2c8a43885e31c9fd9c5b3b2b76d2b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8396decf2e5c9b57456ceb6585456fe2b8f2d026800830ebb7b06db65f311b85(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f4edad139e119552229742ab8b781116e6d98dec87232f221926bfe42adc5c5(
    value: typing.Optional[ElastigroupAzureV3CapacityReservationCapacityReservationGroups],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b224cbd8fec348b5c867a4b4e01df1548569bb31d9be468df73f20c7a0e5ac69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b40124d5e3c783677f21c232da3562cbe3b0c287ae41036e92ae9b725f83ca(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f91ec31dc485d3aeb9b090b51cdcceb46980a1372d22865dab5231d730ef12f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2acd91c16765f10d4846eeeef3c361654d0898faf5bc9f3571473190c3e2221(
    value: typing.Optional[ElastigroupAzureV3CapacityReservation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a37fe9b0cf973e4644ab1bc2acecfc0f26ff2d3f60a2da163bfb6cf20b5f8d38(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    name: builtins.str,
    network: typing.Union[ElastigroupAzureV3Network, typing.Dict[builtins.str, typing.Any]],
    os: builtins.str,
    region: builtins.str,
    resource_group_name: builtins.str,
    vm_sizes: typing.Union[ElastigroupAzureV3VmSizes, typing.Dict[builtins.str, typing.Any]],
    availability_vs_cost: typing.Optional[jsii.Number] = None,
    boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3BootDiagnostics, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capacity_reservation: typing.Optional[typing.Union[ElastigroupAzureV3CapacityReservation, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_data: typing.Optional[builtins.str] = None,
    data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3DataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    extensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Extensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    health: typing.Optional[typing.Union[ElastigroupAzureV3Health, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Image, typing.Dict[builtins.str, typing.Any]]]]] = None,
    load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3LoadBalancer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    login: typing.Optional[typing.Union[ElastigroupAzureV3Login, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_service_identity: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ManagedServiceIdentity, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    on_demand_count: typing.Optional[jsii.Number] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    os_disk: typing.Optional[typing.Union[ElastigroupAzureV3OsDisk, typing.Dict[builtins.str, typing.Any]]] = None,
    preferred_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ProximityPlacementGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    revert_to_spot: typing.Optional[typing.Union[ElastigroupAzureV3RevertToSpot, typing.Dict[builtins.str, typing.Any]]] = None,
    scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Secret, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security: typing.Optional[typing.Union[ElastigroupAzureV3Security, typing.Dict[builtins.str, typing.Any]]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Signal, typing.Dict[builtins.str, typing.Any]]]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3Tags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    user_data: typing.Optional[builtins.str] = None,
    vm_name_prefix: typing.Optional[builtins.str] = None,
    zones: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc5161096580d5153bfa1860887cd86f225390880373a056fb0f793ad013ea99(
    *,
    lun: jsii.Number,
    size_gb: jsii.Number,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__569bdd3f03f7036b18a92718f31d2dd928a7a5692ad852cadbecbe1571784877(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__259c03a256acd7a749d5130c273b053f72aabc7b84bd31247cd5c5f160c41e66(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46efc73f909045a9056eb38eeed8dddf11a6005f261756c8931693429e318a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a06a0161c46a340ef30b73b6b433bc4dbe2c99a4c58d2185b42156cbd0993a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e6cd38bd7cc32199e69591044a94d73563fc39582d2bf37be48fafd54626b2a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e7a1a3807e838855c981cd4ed5eec47484dc0af37f9f40064f413374ed41e9a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3DataDisk]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2428790c2d07819633a0cb91e9db3f19ae4f7755856d1a13d0b1f296171cb698(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d48f909a5c42b9f486b45f14d7269366945afab61ebe749a985b83844b46767(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a835d6eab9ffe8901265886ab61a8c781591f25eeb52cb30e417c08d32dde74f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8dac3d972b30529ca8de993bccb29a0d704a07c30f9df2801560119c9c6c451(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a228a7b4db98073def9347347a3f99ba5bd58a008703a16ba85ce9fd484fccc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3DataDisk]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3517ca943a243395911aacbcdd6a7ec6814e1dda63b8396dce780fdf506b8192(
    *,
    api_version: builtins.str,
    minor_version_auto_upgrade: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    name: builtins.str,
    publisher: builtins.str,
    type: builtins.str,
    enable_automatic_upgrade: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    protected_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    protected_settings_from_key_vault: typing.Optional[typing.Union[ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault, typing.Dict[builtins.str, typing.Any]]] = None,
    public_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a794e4897b72fa48a9797dc8e679081c9a86406c1e7b848c2b9a346d63e43a07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57b6d5db0ddda376d2e281f91af90c30af3c9a6bac3ada740d10a3ca429b75c2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e423d98296f349dee0f0d40f5833eba54f88da769c3f9d4d3d5bd7b1c7fb4dec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ccaf1080500488c4fb9cf9fec97d7ef54daf3e9f1475c4d22fcc49f64ebd33(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95b27c04141596c089522c7ecf83fde9bbf7497783d88837173e8d49b455e779(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9f5f6eda462eb113345df4764c082a48992321d31e6d3504a8b589b90deef8f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Extensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9b65bac0b1a5b40315d073ddd2d09cc51090f06840f0a7315ea4ae344b71a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a88bbbd3ac9be42e52b30e2aee1985ef78a4d5f463e0a93e554b08b9d536c0c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c55750ac08728d6390bd487f4c5f37c2aa2018e8974336d436991d32283c721(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18e06e92c493fe99365d1d763e8fc015ae5bd053e20b98b366bcff15e5faf607(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73aa7cfcf8d2ac28e53f9dfd96434a6a468852566365a1296bd76bc7066a8743(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18a46b3a416e778b6d7167df559f235905a0da99abd9afc4dbc48d407a31b041(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ec3600d68e0bed660ef99cb7e8b7204867a3f9ba6ee34bf7bd7067b7a6fb88(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee4ba06bb79c306b17f2251c7233796c5ada3b22f1e19145a9c88ec776accbc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9758d24eb1e003418cab425cc84f1c365bce6ad5be2bc5ab59fd406a108867dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7b28b9cc9e6e2aa685de786e93637341016ca4c96dfd2ddd62938c29ed6b23c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Extensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa7fc138808d94158de8ad6f983c431d14983b4dc5010033ec5356f4e3477f19(
    *,
    secret_url: builtins.str,
    source_vault: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3632ecd5d43457d2df55730bdeb6ab67e0f31d5f2d81c7398a5e1ab24a7167a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bf30aab4c1a6c5fe04bbdead6c2ec7dfd0d774eb757645b1b4fe3246ae79e6b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddd64ac25153508a6f392b7817f4c59e649888b856edbc44be0827720f36a5f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9fe197f07c9363da4ef25caec542492abcec9964de0f6348472d50190835bd8(
    value: typing.Optional[ElastigroupAzureV3ExtensionsProtectedSettingsFromKeyVault],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6e990bda44270ad67c3404228449287642d607e9d1dddbc6a0fba2faa73d3a(
    *,
    auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    grace_period: typing.Optional[jsii.Number] = None,
    health_check_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    unhealthy_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e0d81fb88eebaf54c459f5b0b58a7f65f59f816ceb260edfac6626f83956f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee70486b90693c69a7df062e81ba95384cc799563fc54763cef4a7eb3a5cd0f0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee7c4f125a18978202cf5cb02aac96ec616d5af48874f8446e926d40afcd1072(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c64a3e59695e8ed4cc83bddb418009827b807c2039b08412a75b9b69c6fb1df5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9a2d7a8e6437a600969ecdd4d570e9f9ff526c242fbb67c2bbb806d5a26ce7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f9a2cf294701f15168746e46f3d8eb726e365156f29369babccfb8442e89b5e(
    value: typing.Optional[ElastigroupAzureV3Health],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e10ba92c93d701fe0b4671d34e6c5ca1181d7604075bed1ddcc49858691fdf(
    *,
    custom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageCustom, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gallery_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageGalleryImage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    marketplace: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageMarketplace, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b706e3fe3641269bc9c82998132305b573f433a63a553abc727dbbb296d5130(
    *,
    image_name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba5532510f93dc827388ebded4851439b11c80358ace880f3768d97ed0affa28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc91d2bf6bcfa551e272ba0e42dfce2ec79f6500561e7caceb1e9cd5efc2b9c4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abc9d9211714e8fb04527e7c4fbc0b73d978fd7d593a00acfed5f9ddc565af68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8fe0c671d3f2d4f01a0290f5a65b6c56ca224063523220e7882237d7918d3a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d8e154ba707b556409151e5176c095a784236e0d80edbacc89236090e0ce69(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d94eb8aeb647c69af925e5434d8de1d2ea4b9d40c417cd11a4797a0f9aee260(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageCustom]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aba67e046e4dba931158e7ecd756b672e41b27963fae66860e364c4d2cc3cb73(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa2a32b33b4082f7b1785585cf0418815f2a7b49482a81070a43e54e5d4e981(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae96aec00ed532d217647415d8eb425097fb4fee62a7ee45ffaccf30d7a64243(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d119cdf05fb3731072049dc8d33c44a47f81b61cdff33f1c4d0b0ea4e1ea98(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageCustom]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12991ce6ced6b5dde96c277c8d5436a21abddd6151b2711fc6c07686f3e5f61b(
    *,
    gallery_name: builtins.str,
    image_name: builtins.str,
    resource_group_name: builtins.str,
    version: builtins.str,
    spot_account_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e44af829d73beeaac91f2bc88af338c7269f5c178fd5d1343a4d7a9fd7883c5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78dd4765863be762c5dbdc64ffb5d14b9e56c09876c59f5d3dc6137a05e401b8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__999eae35698ee82ff0a559fa9dedd65ac75be5b062ed6acf18470d9ef9c50a0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__928e5503d1719d9c2e241e50346f943edae59191fdb2ae32441ad2ce58e1639b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4d57dc3eb6b58e627cb550b5adc24ec8a21413064528f2c868c61dc0223837c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53f3b28e8a1e999d37001d4cc3e5716e462b9d9085f3b7dd7d4722bffe0673ae(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageGalleryImage]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de458c51c487d17280ee813eaaabe1e8bfb0a1be0adaac4d26d0f8d4e459949(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__633ee5c7fa67aa99b602a2f4ce63316744d9d94b963086977ec34d4b4110c2ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cca0dd01eea748b2e706f1bb12f2c93f1d8f4c316160da15975a3a280368c0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d96cd9499e8579d1b50fb91a9cdc18bf50235f4943b358546807e131fb36460e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__136a8ebe5e83bf8d257da8e4f9aa2e24d3683bd00b10a1a57128e57a91fc1f10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710658ab578db7260408d13e894d2ae2123da3977be49cb8dd0606228f68d0f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5f3bbc3ab61be85bbb7ff5e5e3962a4d918b91b0e709f48f82e5c64934d4b7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageGalleryImage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__416ce0ca42bbb32cc14d2505433ac3693e67e3c152e939336fdcd85afce1b8b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__468380111501a6465c8ae3a0703665d86eb7ee9ac975a1e18433c8178756a9c7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f7b55af6b5d6b1d5cb90b0fdbcb78f8b7a2f75b3f9543770f516c43c42169a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbe2151d99337411bc3723d4698735d8c88d5e8fae0516abf3a2d291f8b63d5e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb6722460a5428272015e082bdd10541638dad20fb4eac4ad1eb122b8156043f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a9acbe14471a5e031a401f42cacbe658dc0c347593a496fef1ecc0c2d587a25(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Image]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8388e3e4a39e3a9906e4a3c60449851ac382528556695e6608e02457da5d8604(
    *,
    offer: builtins.str,
    publisher: builtins.str,
    sku: builtins.str,
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a539ce4d98452bb0a77ce65d692f808993b324f7076015c71b0f8b152c0913c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__974bb7a284d976dbdcc8437293205705a062c232577a5d79965133ab75d3310c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7df089e1553109bb55a3650ca5ccb451901179a080616d4f3c3a6a0c63889b3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d126e300dd7135dc38269521d604bdf9c3e9c328ec830cf8a805661f60aa20a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46f3ca5715d90382ad9893877f6e1760c4f61079a51f93e700b739cf121fc4b4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c04388dd152c1f70b530992cffdfaf37a833c6ac818523419ac0eb4f747b243(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ImageMarketplace]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3d1e7ac780e3d6e6f9765278895c0fcdb34be3b7981074826b93fa998064b72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dfac443fed60e9ae17966508bfda3d870aca29c6c7b3597f3d37b4802277ae6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__050b06d421cc3dd599bfb73b8763918320df14ffd5d41dde23c05d55de7d5957(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2e219391bd4962f59722ead5c749e304c5949aff0dcc1fc6c4c4bc4abadeab2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__439bab063883d4ca5150b5437e1241bb4b81050df54babd28e8e2f84e2a95cf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd87a4925a335ac29914978f5cd347e18d44e73a1629f95a593794214dbba7b1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ImageMarketplace]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0626ca52cb736b9797c33941ed114ca7e7d50a76d1ef1e17d783932b7dc96fd7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0bf1d928c0b830ab973bbcd4f06b0f7c78f97790df36f352f26f8e37cc08ed(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageCustom, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b8338095fb250210b51b21f4aef3a4ab4e2f566f50c3fcb80c81975d47e380(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageGalleryImage, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a81b3a7351bc4c0dfa160e2cbcc26732c8beb5b1ee6f8ae64b2a7d0b0c4bee25(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ImageMarketplace, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d64abb228c01ee3b5723124e63bd8b9efcb6f2a9b27cc6a7672d6f3250469b9a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Image]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee42412492c3ec91066685c31a0f8a2b2393320cc51b4ce053fc5a32706e4a1c(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
    type: builtins.str,
    backend_pool_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    sku: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65f48965fb1573b68d4155a0aad154ca4c89aae4fc39f43bf054513a7830156f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b3b512060f65e870cf0e29ce5810dc7150f5130fcf30180b9ed39e252a6a324(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad21f4a7cddd69c741708106640471c1e66c04a01e1945dff2fc94413f0463f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2058f74afb1aab40753d5c0c84ea7f73b41ae46ce89c46257f357c096173ede(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1891304c2e7f119689a39c1ad8c2a3ee8af07c54661315b331b55bb469b398f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4559fec3b5a934569e53ce0b2b9515fa968987490f2e663d9bd1d30d850cf940(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3LoadBalancer]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__732d035b4bbe5e23ed71ca7a5134a67050b73d21ecf0364e17717e6b3b8316e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27f06b5020e76ac02caf30c223e1c9b4b3f91d31484463b24c84257a82ca947c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8fee8689c562037c556f7469ac35f9b6d8d1627ecc7fccf6ab953b284ea9abc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f62b6313486574729ecf330bb96244f780c1612427c010a58a86c53d08ff89a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf6a2dc5ecc6c4df28419c627d2b7f804a8b5c84c297574edbc8694ba05b437(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa27dfe6dd47ef6cfc792a1fdc6b66f99e7186966bca5bae9e227727b887334b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1238676c6cfe6f72ec9a442a65a5d516c281f8ffa80b4878aa369878a514365(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3LoadBalancer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b1d1d9b43783755cdf7e18cc7daf7a64c654bfe52af2a762bfabd1ce1080664(
    *,
    user_name: builtins.str,
    password: typing.Optional[builtins.str] = None,
    ssh_public_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4486581ac2e21e7b2898e2badf02e67b266ced01fcd51cea8e9715f008b976f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e8ddca03805e1ea13540a628ec9dcd10c5a8edda3c25108834f3ad5cc58331c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba02e2542838a2460bd9c20bb142b21a0c36ffdd431c276e7ea56b83cd9345ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44c9edfe177aab34c4b5698177c504aaf83350ec08e99e0639af3a583fe10c1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4442eb8284d124c692f5fddd175c31a3d64fee50ae8418d6a8879ec77efee795(
    value: typing.Optional[ElastigroupAzureV3Login],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cd77a5a5e1bbf3e1e171cec737b8810efcc36fbdd5e05992d206af79d5147de(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39830ecba4af83ef97289b94582719b096e548af55b16d38ba716a690a913abc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb651768f6f25e72f16c428089b518ea7188c81a50e6a20129ee479e25fa54fd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa5ab7a1fca0bcf0fa1c60a262520f6b1055683e4a0e1b4d790c369936423f22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0537a932103cd191f1c3cd89ee4599e99654640061399614cdaa4565517107f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7875ad0aee5a3cb311b4b395adf75e139458191c74c90c1adc12a15d153b2e3c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398f7d010935d7a55b9272dbb97855bc03faf6efdc0d33005ca2478965be3216(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ManagedServiceIdentity]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd915668226e77ea7d731a67a7b350e36a88e9a4164ef401911daa4bff13e35a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df369b05a3a8e9383939ca0b04a1a2f5c3669756f9707a155ef5ab956223272a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09b62879c72cafe40ff2f7699bed99e242919b7cebc4eab0b25c3eed2317cfaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0247675ff18d3b3a3a278c7925d5437e4982a9ca157d9a0772aeb3384a6d4710(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ManagedServiceIdentity]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad1f2de604be5662221076d1e442d12906d979412eda559f5a64217832abe28(
    *,
    network_interfaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]],
    resource_group_name: builtins.str,
    virtual_network_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1164f1e62c0db97ffaa3e7ad90b071722095b4018292ac3c717412f1bd568078(
    *,
    assign_public_ip: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    is_primary: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    subnet_name: builtins.str,
    additional_ip_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    application_security_group: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup, typing.Dict[builtins.str, typing.Any]]]]] = None,
    enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    private_ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    public_ip_sku: typing.Optional[builtins.str] = None,
    security_group: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d4d3434341c207b3ec51f6d668e14ca7107101d1fee721d55e5aefef05d83c3(
    *,
    name: builtins.str,
    private_ip_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3803d49b5fa57a5101f0b447936f2991f0f7ec901102032e77c82187507ccdf4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27ab624df4e11dd4560d6f957e10b270305a74303569831751a6a1c66f913656(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e2a5d19ddc93f43529326a40e34b9429722f065c278c55989347abdfed57b7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c68c8d5b0ffd385db80361863d8253944a34f7f342085dc7c2dd745537c9939(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97be3744c82a6be2aeaa64d13610d269e6ba75dba86e78d8358394be7ecad1b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09e7c284f5ddee1882d17a8c31757fca8d5b88cea25bde78a2b37fabeba923cc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8f243a4832d5755c3a56eaf3a31629c38535c58221cd3ee1e371421cde6cc5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d512576860dd3679731f08f5860bbcda631106257078f7453426bf8e4829110f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0931ac945b76e2846114d31710d793ff821005e7ca9913ed5f7dacee394c7fd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e5f8997cd092fab7efcb7236e4cc06e27cee5321804d6f063f0a9e521b474a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069e5262d21768eda7fbe63efe689bfa156a7a881f515c81f9bb7759cadde0fa(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9b39024740c6a07a0a7bce6a7796d2fa23bf89d389165cc346942c24008359(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b344f1763181d8852ed702ee38a4f8b6eea8176aa059c614d0f15c79bfb93ab(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a334b16050c5514e674652464dc0b092cb2b6e6bcbdeb9d453e60e8b0aaaedc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb68546299f4373f8390d647e6b783d93b4258d87f9288136f57a7a45c245a0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9493b82111ad39e8436b96d724678b43209cd62a641113cfb74280595fa5290(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ca3592a4e239bad279dfc031b3b1903100e0bcf68e63e947b1694589501867(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6db43efef1e1b0285545a4e043aebe5d559f5dcbe0881cd9e1059d017f05b92(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb1c62f0ff02975a21ef54ea813d64474c71aa0b41f86698bd7e0d7b262f903(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de8bc6c2577554052714902e60e27cbb5fdc0a30359fcd5edde1a6a67df2f83a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a53a28f44f14a4ee3ccf23abba226e5fbd0ae7eff777c6ca9da8c15393bbbad3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b300f518196c9a299f7e624fdc72d6bff3cd931a7e89b9bb86c1ec8fbb24f50(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71379ed071e6f73460cdfe2f005b131b2ea9066af94ad87a1047b90f411aba54(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0de009dbea5e8c23906a5e0d20fc49d2900e2fd8d3d35bccb4f7da798bd77988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47ef9cf98151345850f79d78832c522ab934b08cea5470810bae0e3f7e830aa5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25f8db7188f11e25187fb72d0dfaafd02622e19799dcc73f51ceffbcd2a2f250(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf921ecec5596b0c838f5871eae2f7e00f96f5f1d2e7955a0cb381ac8208134(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c360ea491c0ed2616b14c409fd03abfae141a882d2f379347701ae8f4f876c5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f0311baec94a2c5bed16aa63d074801c231e846d3ce73c100b110091f0acc82(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesAdditionalIpConfigs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3674d5efc0563324862aed029173f7e58654de011b9a3741ebbc04b2eb14a1e6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesApplicationSecurityGroup, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89b1e788e652fa6d81fe2d1b0d48cc44f64e708e527a6fd28ee474efad4b6467(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68b53344d678a6906a12d5b6c66166415b62f0934b97aa91ecf9e42d33eb7c7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b083e5af44bd677008409efda7a39c37ce1f31dfecf4ba891dc1774f27424a6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16161fec59a4e9e1a1df69078e0d87731f49e5e45acc85eb17f47708fdd39b45(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9238551383fb2f2b01ed983487873c2e894f10bcbf2c9edf806155a660b35764(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd93b4555dd8146cb2566efe7854f6fa75fef7b5673d2f97fb88fb16315c4b3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cf9bf0b8e3f28eae29ef52bfdb4acac52f6f064c982e118c238cbb4b44c0d98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe32d5d42799ac42ac0cdca668ac02d5af53af8d610a54578df1c5b92b02575(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24f07dc641da4a3b4ae53e549b86588a8ebcc454fc7222ae76a5ee868437a6e(
    *,
    name: typing.Optional[builtins.str] = None,
    resource_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1f9c3286736464f5d54f2557243b782e0f3c59c7d161bed09f95e600da98bee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c59dc663acc11ef79f98a418aa4ff40010e3171e341acdbfd101fc1c6d6731a9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b2ebc4e131c20d38185d09b1a188a6557fcdac9fb38923a6b9590ddea89816a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de6a5735ae7f4ad10a46735466923f811ab37bf7fb8074283371253277211941(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f4968980148be3632fe1822821f5498152016f9e3f5c8f3a543a23256268ff(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8f9252485d78a9cde90e3221b284138decade54d2fd0a935740df8e0141fb8b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21b5e290ea4871d933919cea18415c3ab1ab355b4fc5098862071985c42e6e27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0169e9cd0ad18087bc8e4e02248ff45f94795d172d9fc4a449aa2b19200ad04f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e62494cd66aa2810e1e944de5766ffcea844d6441f4aae0b973c1d07cfaca6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56403dc48b4542a2152c1a94e1bc574eadd58da7fed5dbf731c0cb45cadfb44b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3NetworkNetworkInterfacesSecurityGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60fa0ce4ad59907ad9343caba70f4323864a6ca66f53223eae29265e5a23abb8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da5cc9a5e0de23908a7d5607142470f724e26c3670f1b1706ac13a036ff14fe1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3NetworkNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58b2c49aa895598ee323243c62b314534c44ab5e7b795f97e8342553bc4ed455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c74a488ca47ae06f34ff31d020eaca8150a35ce413626b9d0c864198e313f35f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f704e47e954be4cf434ea9a09bf2f4de140868054034bf52cf79d3836c52f04(
    value: typing.Optional[ElastigroupAzureV3Network],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad5f7ac1cf9665281d0b32c76d8013fa43d03a0950ce3fa58ce799d41c33824e(
    *,
    type: builtins.str,
    size_gb: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a10fe5ed1cfb84eb88a2ffa3ad29bb72299ea45ff9933513f1eb62919c31a0a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234a0f5f99fa7d250495ac7d2435b3b2ea43773788030bc04dd2f85792738b01(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7c37aaa278962a84e417d9fb3f8ffbdba7163236ad837711aec2041422e3357(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfda973be6a1239dab96baa33dbc41776a3d5707cc62f5b41bff3c6d0f1539a6(
    value: typing.Optional[ElastigroupAzureV3OsDisk],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__030555b30fd3ef3a87d68a2ab276e75021ee8409f7f25dd49484f843fc8e82a9(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a80a44a24c0bdef102741071a3abd81eef23c3a421bae16cc8eab7ccd3a3b56c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0938a236e340d3ec79413135a6f7e58a1f223817d46bd54122afb7f0aa67b81d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__458755221a23680e1c622168e287719950d7031d346294de6c81fbe9a756d07c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c25e31fdbe52d80ef86bb54f977b7e4c343cc7f42165a53a0726cd118541c5a1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e589928330e57998a5e72f2dd6916aace7876772ddca834c808306fb7728f100(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e02d2d263d317068d302b2190291812ef4fe2a673b249a60177689e8f252c615(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ProximityPlacementGroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__011d85f1199e275c7e8ad770e162ed0c9a933b13dbcf9e0879517d9527daffab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3f064bdfcb32c7222cf82fcf7c300504776fdf7b42906166fdeed6ea9352f24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c15ad5fa16f32dffe670d5c6afc8ad31343519be964b8b990e65a33d959c858d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea800338d7749820b3ad113d42e14fbe7941e3854103b261c71a1fc1aa980f5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ProximityPlacementGroups]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a9c6974c245e5a4c81e573c5b729cadacf090afcb9d7bc49c4ac244071c0f02(
    *,
    perform_at: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dff3464ededce3a07c3ae1db04c4ff70c28ed82387335dae78e2e5871c6556d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0eeefece98a5afa6ee0a031a036d56b6881351701b245c54c31b11e34aea74f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0185b7191c0e0df65d022a8c01d2ba9a34b17cd60497ce1dabc522473de87454(
    value: typing.Optional[ElastigroupAzureV3RevertToSpot],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e69262846c8900b0e78e7d10a5d201c72463a5533ec91f4ceaa297f464e550ce(
    *,
    action: typing.Union[ElastigroupAzureV3ScalingDownPolicyAction, typing.Dict[builtins.str, typing.Any]],
    cooldown: jsii.Number,
    evaluation_periods: jsii.Number,
    metric_name: builtins.str,
    namespace: builtins.str,
    operator: builtins.str,
    period: jsii.Number,
    policy_name: builtins.str,
    statistic: builtins.str,
    threshold: jsii.Number,
    dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingDownPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    source: typing.Optional[builtins.str] = None,
    unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6425079153b9652e0adbae5236c2e86fe7bb148687c467fc3dd31ea86ad70581(
    *,
    adjustment: typing.Optional[builtins.str] = None,
    maximum: typing.Optional[builtins.str] = None,
    minimum: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65cfba84f13ed58c3afa8d26b5c12e069d8c457daee1a7c6243568bfbf300e10(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ef51755b5e1e599d83d8f6901a13a4880d551189b89e9f79a4ef6be10b47c40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62448d41e5e6896af65c3708febea7ef3671d030ad50f2287c1a3a8d43e40142(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057c37e7f60a60c1df89b954c7610709ffeeaec61a5d1bea737a5488c53409cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__563d512be8790144689c85b0bbd9ca911119cee4f5aa6779cb20fae1e7f28489(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c8f9dfaf3bceaa3645de398ccfcbd5b057408d2d42c34085bd44948310b996b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0403a6f066088189b751af9f7a4a3ce2585bcbd45e244d3b638c39732990b6a(
    value: typing.Optional[ElastigroupAzureV3ScalingDownPolicyAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccd39616d6ba5dc9e6105b25503f924b55445ff8cfe16fa4dc784e7f78c911cd(
    *,
    name: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0b5d06767c364d776e863176377aabde132ced0812f61598add66c7ee8f9297(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8a114eda79502582ee83d9014b7eea76e1bf355d6b50cbde70cf47a4ec52b42(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d492228d64f8dd815f9be0a9f52699417db21357f033ec632ad8587fb64440d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ab4cc5b7afd451e5b84631c51ffbd2c1bd03715a22f659bfb973c2ff92e261b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda02ff1afd0a9533a2f1b306c557766c46fad2a04720eb76afc1db5cdf10ffd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5a73724929de5a6fe0e0c29cfd1d4c21815fb3cd38240e13b68283dca93d0f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicyDimensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07af2385074c3bade43deb52be19a24746325d865d0bc615d79abf617a041a9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67fe176422f40efd04b928663f5f937281711b500d7e3281e120e5802bbe91e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f18d5667b91b25d289298fcc8ee76c0b681b1c1b82d77f871dcfdefc217a157(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2766656ec03d0249036ba78b072b6b8c66adca0db4ab541b7abe871a3b4e7c58(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicyDimensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1762e370416006e1ebdd0da7247b47682a4442458f1ec2c0e1d9efe14b5b9b0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8d516e06f2f40e4b05cfd74e20bb7c457570a03f37167e8e03e97b645050ea2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e84e91ec770f6953ad93dcf2f7a9f3b56944f35dcbd8deb40b1b548079847ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__149c41584883431be19fa8a4005136cb7b78195b63088151de9e27d855dd9d00(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65632557cdef8c91aed5df833e596fc957b9273f0cf587fd58e2ae41d2c32e09(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca90497df512d598dcd01ba24cf43049e6c74dccee1beae6ce844da7456dfd9c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingDownPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3d6539849fd009b5d5851cd5466afd99679b30c038726b5b0aefa51fc0c9613(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2712e081aae84dc6eaeb1e39da7a609c8f0f074ff7e385ade14416c00c1d591(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingDownPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__830ab36610af43302de51e281dc5004f3562483af5e6bb067473bc9204eb15d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3411c2e45c948863a993ff36b803954e4cb3cefc8c8c3268662aae124bbba8d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb2af6b263dc7da440b4d113769378c5ad03853bf7c142b29114b9acd33c306c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d048a4be7bda16ddb0236468711846fa9c366145ca09b533f2af3233324e3198(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bf7c5e3eaa3aeff7bc358ce89f85d0ed01f9c2126fc5d00a7b47fedb4bc81d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec3921ba2b0ff8c1bfc8da23413be3e4a28080d820643bb90457d07899f9c14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dc637d523712d1c6a699fa8817f1469097d30e771f92cd579ef698031aa9d6d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8297fc435ddba15cbfafe89c8739974ea010f5903910355cbe745d5b3b93f92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__060d603099a3e36c179912f1673ea71a1b573372ab1ab1f0ce91d16b56a2a218(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ff0a05fb092cb12d93dfc0f3c6fcd886a263670672db8b2bb966a42841d45d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e7882ce1afd685874bd5f1a69c1120d92ac36ecc2962d6ca73fa804fc0976b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc7415c7a8b8587c8aad94e90adacaaa2e647be60c09bfd5b3de8434df36c307(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42c63c0a4aaaaa9c695f80df3ef2bf1db605776a9f0901fead708bf22d70b2ad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingDownPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d050af936aa421f97b90a5dbb64c3dbd91b812ce211e93d1b56328ac17712d2(
    *,
    action: typing.Union[ElastigroupAzureV3ScalingUpPolicyAction, typing.Dict[builtins.str, typing.Any]],
    cooldown: jsii.Number,
    evaluation_periods: jsii.Number,
    metric_name: builtins.str,
    namespace: builtins.str,
    operator: builtins.str,
    period: jsii.Number,
    policy_name: builtins.str,
    statistic: builtins.str,
    threshold: jsii.Number,
    dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingUpPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    source: typing.Optional[builtins.str] = None,
    unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__995437a810064f444b1825291d5046df33afbb51852abbd1eb9f582c581fa9e7(
    *,
    adjustment: typing.Optional[builtins.str] = None,
    maximum: typing.Optional[builtins.str] = None,
    minimum: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99fc3955a6718a91423e2835a33beb048707d9d0cac6556df8d3e163be099612(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66322ad684a7c8260a2b868f649f55b9a2fa5db5c7f615918cf1912d7458aa88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6148a56eea89445afcca7e8b3c2c51d5aff4603e33f7efe910eca82b8a4d74c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36abbc5abe6cf7446bf5351ce26727b02d92d788d97aa6410c3c5a64ad923f9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d873fa8c74913dfa6454f27f1dee2d53f9f77290dbccfc3878db8997d49c97de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8114706d35b690dc93e0f0496c2a84ae218c7fab65f189ff72243c115dd047c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d76f53f4d75f5038ca5fae5c4eff5b48460f9141d239276734fd13b5e69d7a(
    value: typing.Optional[ElastigroupAzureV3ScalingUpPolicyAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d45f5c73054aab6de24e94f2ac9701754ebc177a1bbaf775015e4c63bde16238(
    *,
    name: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2750ff567983a3f056c2b669b581fd5f9a524cf3e7d63fece66f983fb3e3c9b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d253c59fb782ccb34f0ba9872603c61bcea546ee3cf122f6940d7b455e0bb3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee63acf2d43a4e10cbaeded5a0e44a85b7c4d2ed3be858b0c1eaf0b762889778(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47c5978f46ea81e1f7e69f720a7c36fd31697c73afcf93435c689edc361f84be(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d0791721954e3dc40a9310bcf7403826cac78bad8a708797627080ea7c8658e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fba9106fec1cb98133c8a0368ca2b568ae2f5f7a0282297bb175bafe22924ab0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicyDimensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cc98ca20aa60bdf9986e969f7dc8782eae07c6374daa2eab40a203e54df07df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fff249f347f744ed4c331a50b959f8550c3eafbaf3d8611153cef901dc7ec3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc2d55340530da21f1c6de92f94df738fb2c8502780858e156f1458ae3d3ea26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c4b320fff2d5e44dffa88694ba32fd46dd80de6cb53c4ca4aa5981170aa1c2c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicyDimensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea5e6749d7960eceffb7b7c2e3e83689da3eefb35c9e31d137bad4eeffe8998d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74e04b3b9acdbf0706f9d25d3a858523f84475426cee27f4746e169bc97578f9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83e677f3726d13892949398cd3dbc4127302574cb0ce721ab12e9ae1124acc2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65f2a9440a9a983990a57fc87dfbfe33ec4cee7fc27bda9d7cfc5de5a237b22b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6895cc5f1d5a9b3a5858aaa9fb818211539cc93fff8537c3850f1880134f5a56(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce2858e9a92734e8762b1def0ba6217ff5a4ecf2a7c65c659941e1c1c80b150d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3ScalingUpPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d24de9f0347fb237d351bea67e01374104a2e06099a08462e9c03e5b2992d25b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8055124bc83e426df3d8515211494a3f5f51908cbe8f27e852f811cc850595e5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3ScalingUpPolicyDimensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0a5089e7663f663e3bbd40fb593d91672891b3992735bab172fbff430344625(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549dc72a20332677f26c9856f6e0a7aeb3ed65a4fc030388f1384cf27148d40c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd34b77845edbeae017e2d0496194004816d4f82ab6d0f2c2f69cec1068bd4c6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b70ee887a29a864487189616a060682d2ee31f793c02e98a42cbbbca8affb2db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__687e38a0a023fdd9b15305223778abab3cc74e67c72bc6a4aaa58afc6e150a86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faa6fd3d4f951e2b3456a0ae6eda74b790f36b6490b1b7398fbfc3c7422d5cab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8de062841d1990d7d2a1fc798e45f9c53504496a14a16f08a4214e7cf33923a8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__654868db82f958b006cd60050b957d8cfec023ccdeeed56d3b492ea14e5aa4df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f68bbb060452602b6cf70d6d47fc4b4eae425d968949d0e81c5e8348e2f87f85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__790cf129be703db99850f8ee898154af986d3663206aec895196c76a381dde94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__290e91ff8cdd2dfcc06180e7a457f2a38fd7070e2e5e0fc8701d186da8264ae9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7528cc63c79d9c43ed631ba0c27ba16a9831d1ed83988b5619a4d29bac2223e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c74903dac0cbd565495be32dcc0b43c58eb8f119db8ab2bcdbf39bd787fb6db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3ScalingUpPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1baf926e06cf1e29aff62d3f7bac31ec34fa915213c73e2b77850c2fe2f8d1a8(
    *,
    cron_expression: builtins.str,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    type: builtins.str,
    adjustment: typing.Optional[builtins.str] = None,
    adjustment_percentage: typing.Optional[builtins.str] = None,
    batch_size_percentage: typing.Optional[builtins.str] = None,
    grace_period: typing.Optional[builtins.str] = None,
    scale_max_capacity: typing.Optional[builtins.str] = None,
    scale_min_capacity: typing.Optional[builtins.str] = None,
    scale_target_capacity: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__004091e08ea851298ad63dc447ad6251c59f7bab913a5a29aca4347499492403(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__632bf01fdc31545bb47cc4d245a759678637fc3b4d3c8b4eec52724e9a83f15e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4539b242d0b0609ed58f9e43910ecfda6264b8c3a2d6a49bc5273b7bcc30094(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f2a087e25aa3ee044af6352f43e66246df690322c843cdd2825238f78891050(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04b44e70e01cc0505d77825a268572691aceada9bcbf14394ae6f8cee4164110(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1734771bc027df32e317d26a983ec39a8dd567bda285bbf28ab8b14998cc1f52(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SchedulingTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67f439eae8b15f5d4d06e91ae3a8ee2672ff10176319c3ece582320f119a251a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e222ae5cfcfe87ddcb7b3ed2316e2e909b111bc4d8e9136292e157704c19e350(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ddc631f46b68d52c145be1397618ee76c0b826121ba9361b1a5669d4dc37cbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ef2df51b9caba671f36a18eca354d1dc5fbc95d6471d31c4a354f6bc29b9f29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06afdd0811f1d8c9e14a87c797bc66cfe8c7adb61794f7a517b2aaff4ae3c5ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1033b8a73f685070e9cf22fa9d77d240046e7ee74cd2fdfe381fc100e55cce9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bd42ea738ba1b5ff7ab7ca6b265b0f4bda109e70a3b1c74369a151c6b94eba3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7dc297ea688cadd3d4b0313bb60c9ea3822a1598b6bd332a22931c021d4283f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6d9c3eb0840d562f4385841bc1088b5edcbaf0dcbaf244be49ffc5eec574d58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3c1f2e60b0698f3dcb3679f30cb2c27778cad0304904a1910d2b32533c8ca2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7207af54f310b76b4453afc966bdc56c3df2e2621be4e8fe3d6ea93e104e9e60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e71352e3e095a07d56463eaca40f19e9916854050135e73bf6ef7bb77a8997e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SchedulingTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9458ce462827bd6279d29be1281399f6051752a5d5153129bb70435f8fda3f8(
    *,
    source_vault: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SecretSourceVault, typing.Dict[builtins.str, typing.Any]]]],
    vault_certificates: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SecretVaultCertificates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__183b826d9e40fd33c8e4456fb2b70c33a621fe8f7dce66976079225c26266d06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cb3715f1331558e82d3e5fe92bd53bcfc96123d55a036af087a49121c65973a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f521b326318f3aa12ff2d04dfe78856f946bf137d86a7d481dd05878646a1a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2486a722e8a012bf838bc2130686961c2c10662e9e0c4759a61d8d6b1a150235(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026a05b1020dcd5b96bd8d3b7ebd3983f3c056a9e9ae6180414433f765fef637(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac5f2cdf4381c63d034840607e47b88b94639a3befe2fdb398b66f2aec1ca82(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Secret]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcaa459890d254a23d6422c15fc88af6ff6a5ff9bc0745f9d841d1ded6ab9ed9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3901a47746ca5cee64c86c5cb2134eb10f7b067f22b212b30333714cc13ec5b9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SecretSourceVault, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fdbe594779f9c2f4578037fe2425bbe60eb8f3c9fbc8b9e48af3abd74cc006a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAzureV3SecretVaultCertificates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac09ee6d862e0569f79d27f27546e32ffc458d52d3766de48a1608b5f24db1f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Secret]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1009eb89ba798e6eff0a47ed67fac0251a9486387a57eb971433d51e06c26386(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eec1485b1eb695f3f855d69637b6df7aac45ca208b4f55ddd4594f2f2f1e21c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1da4d910cfeeb22e7b659ee1a5a8e909e4a147c0ab28f708401a78406009573(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c536892dd50cf15c865fd85fd8df78ecf3fbba679f1ab2c34f09ab9f4042483(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a45ecadc1d767493f66b83560733033081c2ca95e099ae56ccfd9b99565af697(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f66d849dd2a493e9777f30a90a026d315ef52d9feb33ced708562bc9168e59(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82584cc51934b3a69fb2a3be4be59b0db57dd9de1f69daf3bca89c1989648c5b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretSourceVault]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68437cc5d5c294593f25b8e0e1f062bb841d9c815680f07d2ec347d29f99dd81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acee576ef0c806d0f25a3ea46320071a192cfe8aa69084d97b18e679da98b3b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f51fa58136438af3c254f642e417b21dd5beba68f291636ebe2d6eda8352de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9845c8299baf81589284be2751863c111690a0f2d1b31bf6789984ca7cc255(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretSourceVault]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7dd83e52c0cfa31ec90c0f30565ebc501886046edf7a0f6b273e2845278c4e1(
    *,
    certificate_store: builtins.str,
    certificate_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87b3a0266bf22a5c72a29bb78ebfa34ec4de36e54f933b520ecdbbe3db43ea26(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c7e3a1c61cf9d4eb92073805bfb8c968451abc5ffef05ac7c3da1ca662a48b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b3c6664baabd25f4f62151f4590fd5c3f09dfd0e82d254e8e5fe672d66ac30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c27550fda160ed8d92d8513435862f04d97895bdde8d2d5ba575e23dfd069e0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__216d7726878c1623cea765ac7e9ea1e88c57133aeac4a0f7b8298bfc89b588b2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c47484e6612a91edd469af0f6e3db30577344c26600c0a306b56dd096d72c86c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3SecretVaultCertificates]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e4ef0a870cccda8b0456d2cad30cc00107880b99f406dfda379b87899fbad4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b26e95b2a39b07845f108908a65e7aff0a11a901bfdd56f50106d1a2e4db54a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79fc18e32d0ea64d5f18efb81b8a596847d508d8bf2ea6fe6b9a6799b471c3a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36ea151b11d9395711ce462d48aa253f0ecbca578baff819afbaf0b4034798b2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3SecretVaultCertificates]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f6188903801f2cf9f64fc02aa1a2bbd3484a7e7ab7e6763ae3196e8cb9dd712(
    *,
    confidential_os_disk_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_at_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    security_type: typing.Optional[builtins.str] = None,
    vtpm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__582d224d6fbcb10f3848b4dc6fea71e4d4f8f48245389f39147bbf093c20277e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7e611e64ab6a9f292c11ed0733a1c122440fc7319918abcd93e22f45b9169da(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d88a102919fce2ad7e81b124ad372c5df0a90ff87e8a00e4b1b7652a07b27f1c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73aa2c0417f8ca5870e735b2a0039099ae75ea311ec92500387bde3b7d4062b5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb655bbd06cf15e3249388e41774ef3e2e4cc69b5d3cb672e5c85c3cdd731ed4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__445d8ab39f63ad4bfd55ec84030b1b42274c4663f91f6295dc3e8e4ba7b16b23(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfe38d24ab6d4ca999e6b655762e659e48bf464f5026de7a34a01d19a94e5305(
    value: typing.Optional[ElastigroupAzureV3Security],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe47eff6dfa1b8c49a8d1d1388721368472dda7c9056706fad67977237083c01(
    *,
    timeout: jsii.Number,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad44d7c7753e5c5acc58f42861282cb83dd161e87b8fde161616f3abe1363901(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0873c13d1d2211629ec922c399f6695050773b5c5bf0b79e3b7df2158d27fdba(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57564c7bdc65c48c8775347b4a204fe3ef31a6ae90f641033fa90ed0ef800199(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0baf48df6a45633a5036efde101ccc6202b5abdb441bd5a5bd8e5db1e8f8873(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69d016a16cd42613948a91f8be32f75623b581265a5e5d76a7878754112012fe(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e5631be7ac5f5fe3f33912496689e6926e5895569d2709af476a3ac4d37fd6b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Signal]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9585a17e7c7f04911a06c7ca7ccb4bacbb8bb95d7225bd8d7e386267f50be009(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5223f25b5dc398a4326f9e86be4c322e961d07482664eee32626e4e9fd95d5fd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05059668a0d1ec3a0fbce218ebef1c3b4cc638840142ede3f1fbac89c971870a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__719f3ea9c9ed9f5685fe1e0dd20e3b40506ef2e13394360711daeff11928a1e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Signal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d46f7942c9eb6b01f8f052d77af573d86b6abd37958131be25567ed6e01af2d(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e5ae827b185397274ff7514d1817dcf2ebd8ea5229230a041322e523f84b08f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6353b9b2f0d2aec0dd8c782d6502a05e5a40d510ba35a385505df6cff729712a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35a0b7b9726ba36b5a8f46ac0021b564b6f39d3432c9cfd755217be5db55d505(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f39a62df7daf8d492dd7a2c1771113a4a1713c62f14314d5c7ceb2e2cf331ae2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1a815d48f11dd53b27b652ed11b0c969f1c065668d02c3c716b2500f7df9bcb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ee0adc52a581046c7695e859afa89a0bc8075581d00cc6c5eb4d68ec3c379d3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAzureV3Tags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a849bc387f55273f4446e6b4ca98287e307a27d5374b4b6aba0a939993cad0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa2c1f1862c62f90765d0b45908e66fdee547eaffda2fcb25dc75b93a7847e56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d5080d7a1de6ae2a4d4e66c43d94343036106d9b735dbe1e2d5da4b6e019d26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deaa3cd76407b5970a7452cb42312e150d0b29407f320dabf10e7eef68f0458a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAzureV3Tags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8341ee4d1b9c90959504f548adb97623c9c345545607326d02c11bca6a55ac8(
    *,
    od_sizes: typing.Sequence[builtins.str],
    excluded_vm_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    preferred_spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    spot_size_attributes: typing.Optional[typing.Union[ElastigroupAzureV3VmSizesSpotSizeAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__655f5829fadfaa71ebe7b0cea9be7c08f42c39e6ad4f6706ea2b3d0abe6b7599(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b9fda9c4cfb364d8790e5f102f4ebd3e30b8e4669084ec539b58d21a1adf5df(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e45a4f5fbf63ba5b0aee26302bc7f7520a601ef73966879ee9002cd94e52f96(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b3c0316bc70becef2c42af3c80caf777e418d119770354c644ecb08315a794(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__343a670034d6050b250614f6a66f9b6a65f73100e76eaf37551db606a1841cb4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14246746d54fd9bcf96670088c85ee7539531864b72d09bf1089202012425fad(
    value: typing.Optional[ElastigroupAzureV3VmSizes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86fa557cde704a58fa70eb5d0e86fa1ffa043c6ed4144acc5fd0c4c8698dcd23(
    *,
    max_cpu: typing.Optional[jsii.Number] = None,
    max_memory: typing.Optional[jsii.Number] = None,
    max_storage: typing.Optional[jsii.Number] = None,
    min_cpu: typing.Optional[jsii.Number] = None,
    min_memory: typing.Optional[jsii.Number] = None,
    min_storage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b3370808a4baa4fb0394c29c608d95c2c31894931a55b696c17897d5bf9b49f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93732599606baa78ad184706b1d90cd7de51cc07e44b344bfbe06cc42742d538(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc2016d48f48ab972323b4a3fc81e1aab058755d7e973d72e962221883f3c5fb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b8f2581cb7b2a816e476cd35e856189fa6a780d89c3fdb384bc3c3b07c40b72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49c1ce3932af3cf239fb3922fa4bca3a48edfc385f2f074bcfcd4f1c2bfcd849(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de539920b0c8762b135c53a32ab80b6a550c8853e14c6524ca4755195e1d2881(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78546068310fe8a6890d7509dfbbcd5d596c16da54a127469894524afac50909(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab10a292972f81f1564aac0fe3a034d67139a7e1764b7d3703ff26e93685b174(
    value: typing.Optional[ElastigroupAzureV3VmSizesSpotSizeAttributes],
) -> None:
    """Type checking stubs"""
    pass
