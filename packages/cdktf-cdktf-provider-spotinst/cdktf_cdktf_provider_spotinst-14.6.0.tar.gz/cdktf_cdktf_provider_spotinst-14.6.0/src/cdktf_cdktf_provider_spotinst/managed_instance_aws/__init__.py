r'''
# `spotinst_managed_instance_aws`

Refer to the Terraform Registry for docs: [`spotinst_managed_instance_aws`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws).
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


class ManagedInstanceAws(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAws",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws spotinst_managed_instance_aws}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        image_id: builtins.str,
        name: builtins.str,
        persist_block_devices: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        product: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
        auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsBlockDeviceMappings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        block_devices_mode: typing.Optional[builtins.str] = None,
        cpu_credits: typing.Optional[builtins.str] = None,
        delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsDelete", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        enable_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        grace_period: typing.Optional[jsii.Number] = None,
        health_check_type: typing.Optional[builtins.str] = None,
        iam_instance_profile: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        integration_route53: typing.Optional[typing.Union["ManagedInstanceAwsIntegrationRoute53", typing.Dict[builtins.str, typing.Any]]] = None,
        key_pair: typing.Optional[builtins.str] = None,
        life_cycle: typing.Optional[builtins.str] = None,
        load_balancers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsLoadBalancers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        managed_instance_action: typing.Optional[typing.Union["ManagedInstanceAwsManagedInstanceAction", typing.Dict[builtins.str, typing.Any]]] = None,
        metadata_options: typing.Optional[typing.Union["ManagedInstanceAwsMetadataOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        minimum_instance_lifetime: typing.Optional[jsii.Number] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        orientation: typing.Optional[builtins.str] = None,
        persist_private_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        persist_root_device: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        placement_tenancy: typing.Optional[builtins.str] = None,
        preferred_type: typing.Optional[builtins.str] = None,
        preferred_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        private_ip: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        resource_requirements: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsResourceRequirements", typing.Dict[builtins.str, typing.Any]]]]] = None,
        resource_tag_specification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsResourceTagSpecification", typing.Dict[builtins.str, typing.Any]]]]] = None,
        revert_to_spot: typing.Optional[typing.Union["ManagedInstanceAwsRevertToSpot", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        unhealthy_duration: typing.Optional[jsii.Number] = None,
        user_data: typing.Optional[builtins.str] = None,
        utilize_reserved_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws spotinst_managed_instance_aws} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param image_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#image_id ManagedInstanceAws#image_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.
        :param persist_block_devices: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_block_devices ManagedInstanceAws#persist_block_devices}.
        :param product: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#product ManagedInstanceAws#product}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#subnet_ids ManagedInstanceAws#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#vpc_id ManagedInstanceAws#vpc_id}.
        :param auto_healing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#auto_healing ManagedInstanceAws#auto_healing}.
        :param block_device_mappings: block_device_mappings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#block_device_mappings ManagedInstanceAws#block_device_mappings}
        :param block_devices_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#block_devices_mode ManagedInstanceAws#block_devices_mode}.
        :param cpu_credits: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#cpu_credits ManagedInstanceAws#cpu_credits}.
        :param delete: delete block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#delete ManagedInstanceAws#delete}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#description ManagedInstanceAws#description}.
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#draining_timeout ManagedInstanceAws#draining_timeout}.
        :param ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ebs_optimized ManagedInstanceAws#ebs_optimized}.
        :param elastic_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#elastic_ip ManagedInstanceAws#elastic_ip}.
        :param enable_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#enable_monitoring ManagedInstanceAws#enable_monitoring}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#fallback_to_ondemand ManagedInstanceAws#fallback_to_ondemand}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#grace_period ManagedInstanceAws#grace_period}.
        :param health_check_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#health_check_type ManagedInstanceAws#health_check_type}.
        :param iam_instance_profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#iam_instance_profile ManagedInstanceAws#iam_instance_profile}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#id ManagedInstanceAws#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#instance_types ManagedInstanceAws#instance_types}.
        :param integration_route53: integration_route53 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#integration_route53 ManagedInstanceAws#integration_route53}
        :param key_pair: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#key_pair ManagedInstanceAws#key_pair}.
        :param life_cycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#life_cycle ManagedInstanceAws#life_cycle}.
        :param load_balancers: load_balancers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#load_balancers ManagedInstanceAws#load_balancers}
        :param managed_instance_action: managed_instance_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#managed_instance_action ManagedInstanceAws#managed_instance_action}
        :param metadata_options: metadata_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#metadata_options ManagedInstanceAws#metadata_options}
        :param minimum_instance_lifetime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#minimum_instance_lifetime ManagedInstanceAws#minimum_instance_lifetime}.
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#network_interface ManagedInstanceAws#network_interface}
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#optimization_windows ManagedInstanceAws#optimization_windows}.
        :param orientation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#orientation ManagedInstanceAws#orientation}.
        :param persist_private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_private_ip ManagedInstanceAws#persist_private_ip}.
        :param persist_root_device: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_root_device ManagedInstanceAws#persist_root_device}.
        :param placement_tenancy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#placement_tenancy ManagedInstanceAws#placement_tenancy}.
        :param preferred_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#preferred_type ManagedInstanceAws#preferred_type}.
        :param preferred_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#preferred_types ManagedInstanceAws#preferred_types}.
        :param private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#private_ip ManagedInstanceAws#private_ip}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#region ManagedInstanceAws#region}.
        :param resource_requirements: resource_requirements block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#resource_requirements ManagedInstanceAws#resource_requirements}
        :param resource_tag_specification: resource_tag_specification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#resource_tag_specification ManagedInstanceAws#resource_tag_specification}
        :param revert_to_spot: revert_to_spot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#revert_to_spot ManagedInstanceAws#revert_to_spot}
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#scheduled_task ManagedInstanceAws#scheduled_task}
        :param security_group_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#security_group_ids ManagedInstanceAws#security_group_ids}.
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#shutdown_script ManagedInstanceAws#shutdown_script}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#tags ManagedInstanceAws#tags}
        :param unhealthy_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#unhealthy_duration ManagedInstanceAws#unhealthy_duration}.
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#user_data ManagedInstanceAws#user_data}.
        :param utilize_reserved_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#utilize_reserved_instances ManagedInstanceAws#utilize_reserved_instances}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dd494a633a7ceac821a993cc45f1e29b839cb1d25c83da8b4e13a965b643844)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ManagedInstanceAwsConfig(
            image_id=image_id,
            name=name,
            persist_block_devices=persist_block_devices,
            product=product,
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
            auto_healing=auto_healing,
            block_device_mappings=block_device_mappings,
            block_devices_mode=block_devices_mode,
            cpu_credits=cpu_credits,
            delete=delete,
            description=description,
            draining_timeout=draining_timeout,
            ebs_optimized=ebs_optimized,
            elastic_ip=elastic_ip,
            enable_monitoring=enable_monitoring,
            fallback_to_ondemand=fallback_to_ondemand,
            grace_period=grace_period,
            health_check_type=health_check_type,
            iam_instance_profile=iam_instance_profile,
            id=id,
            instance_types=instance_types,
            integration_route53=integration_route53,
            key_pair=key_pair,
            life_cycle=life_cycle,
            load_balancers=load_balancers,
            managed_instance_action=managed_instance_action,
            metadata_options=metadata_options,
            minimum_instance_lifetime=minimum_instance_lifetime,
            network_interface=network_interface,
            optimization_windows=optimization_windows,
            orientation=orientation,
            persist_private_ip=persist_private_ip,
            persist_root_device=persist_root_device,
            placement_tenancy=placement_tenancy,
            preferred_type=preferred_type,
            preferred_types=preferred_types,
            private_ip=private_ip,
            region=region,
            resource_requirements=resource_requirements,
            resource_tag_specification=resource_tag_specification,
            revert_to_spot=revert_to_spot,
            scheduled_task=scheduled_task,
            security_group_ids=security_group_ids,
            shutdown_script=shutdown_script,
            tags=tags,
            unhealthy_duration=unhealthy_duration,
            user_data=user_data,
            utilize_reserved_instances=utilize_reserved_instances,
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
        '''Generates CDKTF code for importing a ManagedInstanceAws resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ManagedInstanceAws to import.
        :param import_from_id: The id of the existing ManagedInstanceAws that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ManagedInstanceAws to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c22ce2ebd6e770a5827d0eeb47aa2ae3614794c73eea0d55dae8c004c605f2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putBlockDeviceMappings")
    def put_block_device_mappings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsBlockDeviceMappings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e72b566bed9b7a5d9a240db42bf26739612f083fce4585539c199ccbedbaf2de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBlockDeviceMappings", [value]))

    @jsii.member(jsii_name="putDelete")
    def put_delete(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsDelete", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b13c93ee49ba7171ffee2e5856ae8fb18a47b40acf4d4300003156b5b4f1abfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDelete", [value]))

    @jsii.member(jsii_name="putIntegrationRoute53")
    def put_integration_route53(
        self,
        *,
        domains: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsIntegrationRoute53Domains", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param domains: domains block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#domains ManagedInstanceAws#domains}
        '''
        value = ManagedInstanceAwsIntegrationRoute53(domains=domains)

        return typing.cast(None, jsii.invoke(self, "putIntegrationRoute53", [value]))

    @jsii.member(jsii_name="putLoadBalancers")
    def put_load_balancers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsLoadBalancers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bcf9bddb5e8cb82f18176f252d5a1cdad9e1166a3b8d47cb611ebf7b0669f4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLoadBalancers", [value]))

    @jsii.member(jsii_name="putManagedInstanceAction")
    def put_managed_instance_action(self, *, type: builtins.str) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#type ManagedInstanceAws#type}.
        '''
        value = ManagedInstanceAwsManagedInstanceAction(type=type)

        return typing.cast(None, jsii.invoke(self, "putManagedInstanceAction", [value]))

    @jsii.member(jsii_name="putMetadataOptions")
    def put_metadata_options(
        self,
        *,
        http_tokens: builtins.str,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        instance_metadata_tags: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param http_tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#http_tokens ManagedInstanceAws#http_tokens}.
        :param http_put_response_hop_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#http_put_response_hop_limit ManagedInstanceAws#http_put_response_hop_limit}.
        :param instance_metadata_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#instance_metadata_tags ManagedInstanceAws#instance_metadata_tags}.
        '''
        value = ManagedInstanceAwsMetadataOptions(
            http_tokens=http_tokens,
            http_put_response_hop_limit=http_put_response_hop_limit,
            instance_metadata_tags=instance_metadata_tags,
        )

        return typing.cast(None, jsii.invoke(self, "putMetadataOptions", [value]))

    @jsii.member(jsii_name="putNetworkInterface")
    def put_network_interface(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsNetworkInterface", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75505da419c8b7de79986b6f7b186f4f35f78b829dc9d722ed98b3ab73ecef84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterface", [value]))

    @jsii.member(jsii_name="putResourceRequirements")
    def put_resource_requirements(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsResourceRequirements", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ccc93729045078eb5279cb66dff489645f3f75c4217b6fefd71468138bec08c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResourceRequirements", [value]))

    @jsii.member(jsii_name="putResourceTagSpecification")
    def put_resource_tag_specification(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsResourceTagSpecification", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9683a13b9e3c0af4296f92caa767b80bc6782a81cde8a9c45e3c6b730686230)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResourceTagSpecification", [value]))

    @jsii.member(jsii_name="putRevertToSpot")
    def put_revert_to_spot(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#perform_at ManagedInstanceAws#perform_at}.
        '''
        value = ManagedInstanceAwsRevertToSpot(perform_at=perform_at)

        return typing.cast(None, jsii.invoke(self, "putRevertToSpot", [value]))

    @jsii.member(jsii_name="putScheduledTask")
    def put_scheduled_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsScheduledTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff3d519f90a37db11ea82adeb0cdf0881744a918bdea189d4401b28632c3db8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScheduledTask", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0963aa412aba89a40c32b158ddd032b5bbb4075e1062c9faeb2955b5c37df47f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetBlockDeviceMappings")
    def reset_block_device_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockDeviceMappings", []))

    @jsii.member(jsii_name="resetBlockDevicesMode")
    def reset_block_devices_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockDevicesMode", []))

    @jsii.member(jsii_name="resetCpuCredits")
    def reset_cpu_credits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuCredits", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetEbsOptimized")
    def reset_ebs_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsOptimized", []))

    @jsii.member(jsii_name="resetElasticIp")
    def reset_elastic_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticIp", []))

    @jsii.member(jsii_name="resetEnableMonitoring")
    def reset_enable_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableMonitoring", []))

    @jsii.member(jsii_name="resetFallbackToOndemand")
    def reset_fallback_to_ondemand(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFallbackToOndemand", []))

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

    @jsii.member(jsii_name="resetHealthCheckType")
    def reset_health_check_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthCheckType", []))

    @jsii.member(jsii_name="resetIamInstanceProfile")
    def reset_iam_instance_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamInstanceProfile", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceTypes")
    def reset_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypes", []))

    @jsii.member(jsii_name="resetIntegrationRoute53")
    def reset_integration_route53(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationRoute53", []))

    @jsii.member(jsii_name="resetKeyPair")
    def reset_key_pair(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyPair", []))

    @jsii.member(jsii_name="resetLifeCycle")
    def reset_life_cycle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLifeCycle", []))

    @jsii.member(jsii_name="resetLoadBalancers")
    def reset_load_balancers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancers", []))

    @jsii.member(jsii_name="resetManagedInstanceAction")
    def reset_managed_instance_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedInstanceAction", []))

    @jsii.member(jsii_name="resetMetadataOptions")
    def reset_metadata_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadataOptions", []))

    @jsii.member(jsii_name="resetMinimumInstanceLifetime")
    def reset_minimum_instance_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumInstanceLifetime", []))

    @jsii.member(jsii_name="resetNetworkInterface")
    def reset_network_interface(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkInterface", []))

    @jsii.member(jsii_name="resetOptimizationWindows")
    def reset_optimization_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimizationWindows", []))

    @jsii.member(jsii_name="resetOrientation")
    def reset_orientation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrientation", []))

    @jsii.member(jsii_name="resetPersistPrivateIp")
    def reset_persist_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPersistPrivateIp", []))

    @jsii.member(jsii_name="resetPersistRootDevice")
    def reset_persist_root_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPersistRootDevice", []))

    @jsii.member(jsii_name="resetPlacementTenancy")
    def reset_placement_tenancy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlacementTenancy", []))

    @jsii.member(jsii_name="resetPreferredType")
    def reset_preferred_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredType", []))

    @jsii.member(jsii_name="resetPreferredTypes")
    def reset_preferred_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredTypes", []))

    @jsii.member(jsii_name="resetPrivateIp")
    def reset_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIp", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetResourceRequirements")
    def reset_resource_requirements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceRequirements", []))

    @jsii.member(jsii_name="resetResourceTagSpecification")
    def reset_resource_tag_specification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceTagSpecification", []))

    @jsii.member(jsii_name="resetRevertToSpot")
    def reset_revert_to_spot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevertToSpot", []))

    @jsii.member(jsii_name="resetScheduledTask")
    def reset_scheduled_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledTask", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetShutdownScript")
    def reset_shutdown_script(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownScript", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUnhealthyDuration")
    def reset_unhealthy_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnhealthyDuration", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @jsii.member(jsii_name="resetUtilizeReservedInstances")
    def reset_utilize_reserved_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUtilizeReservedInstances", []))

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
    @jsii.member(jsii_name="blockDeviceMappings")
    def block_device_mappings(self) -> "ManagedInstanceAwsBlockDeviceMappingsList":
        return typing.cast("ManagedInstanceAwsBlockDeviceMappingsList", jsii.get(self, "blockDeviceMappings"))

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> "ManagedInstanceAwsDeleteList":
        return typing.cast("ManagedInstanceAwsDeleteList", jsii.get(self, "delete"))

    @builtins.property
    @jsii.member(jsii_name="integrationRoute53")
    def integration_route53(
        self,
    ) -> "ManagedInstanceAwsIntegrationRoute53OutputReference":
        return typing.cast("ManagedInstanceAwsIntegrationRoute53OutputReference", jsii.get(self, "integrationRoute53"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancers")
    def load_balancers(self) -> "ManagedInstanceAwsLoadBalancersList":
        return typing.cast("ManagedInstanceAwsLoadBalancersList", jsii.get(self, "loadBalancers"))

    @builtins.property
    @jsii.member(jsii_name="managedInstanceAction")
    def managed_instance_action(
        self,
    ) -> "ManagedInstanceAwsManagedInstanceActionOutputReference":
        return typing.cast("ManagedInstanceAwsManagedInstanceActionOutputReference", jsii.get(self, "managedInstanceAction"))

    @builtins.property
    @jsii.member(jsii_name="metadataOptions")
    def metadata_options(self) -> "ManagedInstanceAwsMetadataOptionsOutputReference":
        return typing.cast("ManagedInstanceAwsMetadataOptionsOutputReference", jsii.get(self, "metadataOptions"))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> "ManagedInstanceAwsNetworkInterfaceList":
        return typing.cast("ManagedInstanceAwsNetworkInterfaceList", jsii.get(self, "networkInterface"))

    @builtins.property
    @jsii.member(jsii_name="resourceRequirements")
    def resource_requirements(self) -> "ManagedInstanceAwsResourceRequirementsList":
        return typing.cast("ManagedInstanceAwsResourceRequirementsList", jsii.get(self, "resourceRequirements"))

    @builtins.property
    @jsii.member(jsii_name="resourceTagSpecification")
    def resource_tag_specification(
        self,
    ) -> "ManagedInstanceAwsResourceTagSpecificationList":
        return typing.cast("ManagedInstanceAwsResourceTagSpecificationList", jsii.get(self, "resourceTagSpecification"))

    @builtins.property
    @jsii.member(jsii_name="revertToSpot")
    def revert_to_spot(self) -> "ManagedInstanceAwsRevertToSpotOutputReference":
        return typing.cast("ManagedInstanceAwsRevertToSpotOutputReference", jsii.get(self, "revertToSpot"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTask")
    def scheduled_task(self) -> "ManagedInstanceAwsScheduledTaskList":
        return typing.cast("ManagedInstanceAwsScheduledTaskList", jsii.get(self, "scheduledTask"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "ManagedInstanceAwsTagsList":
        return typing.cast("ManagedInstanceAwsTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property
    @jsii.member(jsii_name="blockDeviceMappingsInput")
    def block_device_mappings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsBlockDeviceMappings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsBlockDeviceMappings"]]], jsii.get(self, "blockDeviceMappingsInput"))

    @builtins.property
    @jsii.member(jsii_name="blockDevicesModeInput")
    def block_devices_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blockDevicesModeInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuCreditsInput")
    def cpu_credits_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuCreditsInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsDelete"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsDelete"]]], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsOptimizedInput")
    def ebs_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ebsOptimizedInput"))

    @builtins.property
    @jsii.member(jsii_name="elasticIpInput")
    def elastic_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticIpInput"))

    @builtins.property
    @jsii.member(jsii_name="enableMonitoringInput")
    def enable_monitoring_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableMonitoringInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackToOndemandInput")
    def fallback_to_ondemand_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackToOndemandInput"))

    @builtins.property
    @jsii.member(jsii_name="gracePeriodInput")
    def grace_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gracePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="healthCheckTypeInput")
    def health_check_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "healthCheckTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="iamInstanceProfileInput")
    def iam_instance_profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamInstanceProfileInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="imageIdInput")
    def image_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesInput")
    def instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationRoute53Input")
    def integration_route53_input(
        self,
    ) -> typing.Optional["ManagedInstanceAwsIntegrationRoute53"]:
        return typing.cast(typing.Optional["ManagedInstanceAwsIntegrationRoute53"], jsii.get(self, "integrationRoute53Input"))

    @builtins.property
    @jsii.member(jsii_name="keyPairInput")
    def key_pair_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPairInput"))

    @builtins.property
    @jsii.member(jsii_name="lifeCycleInput")
    def life_cycle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lifeCycleInput"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancersInput")
    def load_balancers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsLoadBalancers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsLoadBalancers"]]], jsii.get(self, "loadBalancersInput"))

    @builtins.property
    @jsii.member(jsii_name="managedInstanceActionInput")
    def managed_instance_action_input(
        self,
    ) -> typing.Optional["ManagedInstanceAwsManagedInstanceAction"]:
        return typing.cast(typing.Optional["ManagedInstanceAwsManagedInstanceAction"], jsii.get(self, "managedInstanceActionInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataOptionsInput")
    def metadata_options_input(
        self,
    ) -> typing.Optional["ManagedInstanceAwsMetadataOptions"]:
        return typing.cast(typing.Optional["ManagedInstanceAwsMetadataOptions"], jsii.get(self, "metadataOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInstanceLifetimeInput")
    def minimum_instance_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimumInstanceLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsNetworkInterface"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsNetworkInterface"]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="optimizationWindowsInput")
    def optimization_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optimizationWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="orientationInput")
    def orientation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orientationInput"))

    @builtins.property
    @jsii.member(jsii_name="persistBlockDevicesInput")
    def persist_block_devices_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "persistBlockDevicesInput"))

    @builtins.property
    @jsii.member(jsii_name="persistPrivateIpInput")
    def persist_private_ip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "persistPrivateIpInput"))

    @builtins.property
    @jsii.member(jsii_name="persistRootDeviceInput")
    def persist_root_device_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "persistRootDeviceInput"))

    @builtins.property
    @jsii.member(jsii_name="placementTenancyInput")
    def placement_tenancy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "placementTenancyInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredTypeInput")
    def preferred_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredTypesInput")
    def preferred_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="privateIpInput")
    def private_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateIpInput"))

    @builtins.property
    @jsii.member(jsii_name="productInput")
    def product_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceRequirementsInput")
    def resource_requirements_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceRequirements"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceRequirements"]]], jsii.get(self, "resourceRequirementsInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceTagSpecificationInput")
    def resource_tag_specification_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceTagSpecification"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceTagSpecification"]]], jsii.get(self, "resourceTagSpecificationInput"))

    @builtins.property
    @jsii.member(jsii_name="revertToSpotInput")
    def revert_to_spot_input(self) -> typing.Optional["ManagedInstanceAwsRevertToSpot"]:
        return typing.cast(typing.Optional["ManagedInstanceAwsRevertToSpot"], jsii.get(self, "revertToSpotInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTaskInput")
    def scheduled_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsScheduledTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsScheduledTask"]]], jsii.get(self, "scheduledTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="shutdownScriptInput")
    def shutdown_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shutdownScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="unhealthyDurationInput")
    def unhealthy_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unhealthyDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property
    @jsii.member(jsii_name="utilizeReservedInstancesInput")
    def utilize_reserved_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "utilizeReservedInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__04a781057e3a32b5d00150c1129e15ba2384dfba806932826f1d2d7ab2e9590f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoHealing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockDevicesMode")
    def block_devices_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blockDevicesMode"))

    @block_devices_mode.setter
    def block_devices_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d2964032101f083cf00a1eaa3cb492485d674c34db4ce12584220aeee95092)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockDevicesMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuCredits")
    def cpu_credits(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuCredits"))

    @cpu_credits.setter
    def cpu_credits(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f606e5635f0d083026cdcfa5054b134cdc177ab31fc81217a8399d2c79575ab9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuCredits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f02700b16b84afb5fff343e0607b7b149e4cd4f1152e86c8ff62b974b57bf17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da6cb6d4232e13b69ae09d52bd80cf5546d67395334038112c81559f4f137e32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainingTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsOptimized")
    def ebs_optimized(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ebsOptimized"))

    @ebs_optimized.setter
    def ebs_optimized(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7397075afb1c0ce27a2c5e443ccccf130b53be9a692ddcaf289e3da10f8fa810)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsOptimized", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticIp"))

    @elastic_ip.setter
    def elastic_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ae0fbe41da4b27e1416d05ea8a05aa92300f9b05a497922021c2865c00725ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elasticIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableMonitoring")
    def enable_monitoring(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableMonitoring"))

    @enable_monitoring.setter
    def enable_monitoring(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d34113b3b6c156c7737d1e949fa1c97e99fb0655d4122baf2ef2e1e16391d8ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableMonitoring", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__0b9c3189a84768499eedb3f282438b6d3feef21cd6eb836449c7f536a0d5e95e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackToOndemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed7636167a355fe7d926e089a6c3bf6f97e0eeb098ae667069d9bd32c9fe6ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gracePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckType")
    def health_check_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthCheckType"))

    @health_check_type.setter
    def health_check_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c29b52d7c7011f1b87adf4e01db046e737a04c5c15314e64f3628fd3c7aaa4f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamInstanceProfile")
    def iam_instance_profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamInstanceProfile"))

    @iam_instance_profile.setter
    def iam_instance_profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac744f7df00676696bc59055d083f9c1064b3045b1ce5c45a2aa4cf2aeb23b41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamInstanceProfile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c6ab7ed22aa50ebf56be66c01c32ff6117b77f3ae350e67e2318a73b18520f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d6bcde336e49b6dffd7ec5e01fb1dc94ef70735362c644f1eb78f06f9031ff0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypes"))

    @instance_types.setter
    def instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dffd8405f08256d8858d25f4f66bf2874e9b203535e79799b547b443adb66a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyPair")
    def key_pair(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyPair"))

    @key_pair.setter
    def key_pair(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19ca56727e7a953c6172e34a37b3bae34001a72dc283fa4eb9bfa785eca6165f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyPair", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lifeCycle")
    def life_cycle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lifeCycle"))

    @life_cycle.setter
    def life_cycle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64d11132e8f38ba6018f81568901673bd7f9812f3126eda8151a26b0a5a35463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lifeCycle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimumInstanceLifetime")
    def minimum_instance_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minimumInstanceLifetime"))

    @minimum_instance_lifetime.setter
    def minimum_instance_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c7f1cabb0bd0f02f40495d129f3f238eaddac108b6fb090927dd0383a53cc48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumInstanceLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__591f3cba0d0490b682600ea4f7aab2896f3c739e17051bc5de3499f7b0794ff1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optimizationWindows")
    def optimization_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "optimizationWindows"))

    @optimization_windows.setter
    def optimization_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef1a8d1fca6ae46ffb5f4b68c4bf1beba73b92baa983bf67bd6dddb2c1a9344c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimizationWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="orientation")
    def orientation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orientation"))

    @orientation.setter
    def orientation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d491f830c4aa0aebdb255add9cd7fd86fd3d0a7d3486c419742ee88a29c4e10f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "orientation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistBlockDevices")
    def persist_block_devices(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "persistBlockDevices"))

    @persist_block_devices.setter
    def persist_block_devices(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa6a7df29e14d1bbde8dbd1c65d762dc33f39a379a729d529cfa8091d55359fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistBlockDevices", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistPrivateIp")
    def persist_private_ip(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "persistPrivateIp"))

    @persist_private_ip.setter
    def persist_private_ip(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc4fce33a709d2b3e15ce13398455db06d0300c14aa74de7c3921dcd06be8b02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistPrivateIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistRootDevice")
    def persist_root_device(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "persistRootDevice"))

    @persist_root_device.setter
    def persist_root_device(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b39bc58974218ae27464c17fb723454f6fb3f5ab22f2bb8de363acbe62a66b2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistRootDevice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="placementTenancy")
    def placement_tenancy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "placementTenancy"))

    @placement_tenancy.setter
    def placement_tenancy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38d07f93be959f2387546c9f84582bfc88d923a8b73d31cf42f7acc7952e6df4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "placementTenancy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredType")
    def preferred_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredType"))

    @preferred_type.setter
    def preferred_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bf5e68b667557996caafbc68e823644a79f8f02c118ee62aaddd90065ebd55a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredTypes")
    def preferred_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredTypes"))

    @preferred_types.setter
    def preferred_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73994828814a53bc5a6e9fe038525230f28b0e1538bfdbdb506708270977de8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIp")
    def private_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIp"))

    @private_ip.setter
    def private_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__493eec15205c84170ff373fb79dc0a1324a45300165e52c373632e3d8da9dc8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="product")
    def product(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "product"))

    @product.setter
    def product(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94b943c6617c61ace521bb99f367edf0a2fb419a0d7447cd6cc768a2b47fdd3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "product", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48cac7a15c882a00cab83d60c1e9d63add9edf7ff1199837bb276c9dc6e8c4e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5635ddde46b53305af436ad446b89d2328e09b250b609e327fee4583274b4bbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroupIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shutdownScript")
    def shutdown_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shutdownScript"))

    @shutdown_script.setter
    def shutdown_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84caf0170ee1fba82c4fab7153f6e5e6fa63e6cdfd1db2693c68c910dc5f1b04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shutdownScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48b5295d173ca7e102bb64b922bc70dcefb7b758a6ac790bfa0148942f1ce747)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unhealthyDuration")
    def unhealthy_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unhealthyDuration"))

    @unhealthy_duration.setter
    def unhealthy_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c1d00e5637fb87ff90152e1f86b3a7005d978fff3fdab3494fd0a73be97c152)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unhealthyDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0390ab643fc27fe1b3913a8b6c38534f57c59f1902aefd04500d92d05c978e0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="utilizeReservedInstances")
    def utilize_reserved_instances(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "utilizeReservedInstances"))

    @utilize_reserved_instances.setter
    def utilize_reserved_instances(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4423ba197d14ab977ab02afb996798016394318870738de1be6d92c14224474)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utilizeReservedInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0114dea09597e84259d0fe0f705cd1cd03dadcfca8f9d779a752c7689a881b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsBlockDeviceMappings",
    jsii_struct_bases=[],
    name_mapping={"device_name": "deviceName", "ebs": "ebs"},
)
class ManagedInstanceAwsBlockDeviceMappings:
    def __init__(
        self,
        *,
        device_name: builtins.str,
        ebs: typing.Optional[typing.Union["ManagedInstanceAwsBlockDeviceMappingsEbs", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param device_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#device_name ManagedInstanceAws#device_name}.
        :param ebs: ebs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ebs ManagedInstanceAws#ebs}
        '''
        if isinstance(ebs, dict):
            ebs = ManagedInstanceAwsBlockDeviceMappingsEbs(**ebs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91e600339887f464ecb1f136bc5b6a47ada2dbbf2a322d473b1869a17bc406db)
            check_type(argname="argument device_name", value=device_name, expected_type=type_hints["device_name"])
            check_type(argname="argument ebs", value=ebs, expected_type=type_hints["ebs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "device_name": device_name,
        }
        if ebs is not None:
            self._values["ebs"] = ebs

    @builtins.property
    def device_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#device_name ManagedInstanceAws#device_name}.'''
        result = self._values.get("device_name")
        assert result is not None, "Required property 'device_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ebs(self) -> typing.Optional["ManagedInstanceAwsBlockDeviceMappingsEbs"]:
        '''ebs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ebs ManagedInstanceAws#ebs}
        '''
        result = self._values.get("ebs")
        return typing.cast(typing.Optional["ManagedInstanceAwsBlockDeviceMappingsEbs"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsBlockDeviceMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsBlockDeviceMappingsEbs",
    jsii_struct_bases=[],
    name_mapping={
        "delete_on_termination": "deleteOnTermination",
        "encrypted": "encrypted",
        "iops": "iops",
        "kms_key_id": "kmsKeyId",
        "snapshot_id": "snapshotId",
        "throughput": "throughput",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class ManagedInstanceAwsBlockDeviceMappingsEbs:
    def __init__(
        self,
        *,
        delete_on_termination: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        throughput: typing.Optional[jsii.Number] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#delete_on_termination ManagedInstanceAws#delete_on_termination}.
        :param encrypted: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#encrypted ManagedInstanceAws#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#iops ManagedInstanceAws#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#kms_key_id ManagedInstanceAws#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#snapshot_id ManagedInstanceAws#snapshot_id}.
        :param throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#throughput ManagedInstanceAws#throughput}.
        :param volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#volume_size ManagedInstanceAws#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#volume_type ManagedInstanceAws#volume_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c22e309111a431f89f1e6603ca53df6d5ad8f2c89579ec61b4bdb16c48993e9)
            check_type(argname="argument delete_on_termination", value=delete_on_termination, expected_type=type_hints["delete_on_termination"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument iops", value=iops, expected_type=type_hints["iops"])
            check_type(argname="argument kms_key_id", value=kms_key_id, expected_type=type_hints["kms_key_id"])
            check_type(argname="argument snapshot_id", value=snapshot_id, expected_type=type_hints["snapshot_id"])
            check_type(argname="argument throughput", value=throughput, expected_type=type_hints["throughput"])
            check_type(argname="argument volume_size", value=volume_size, expected_type=type_hints["volume_size"])
            check_type(argname="argument volume_type", value=volume_type, expected_type=type_hints["volume_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if delete_on_termination is not None:
            self._values["delete_on_termination"] = delete_on_termination
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
        if throughput is not None:
            self._values["throughput"] = throughput
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if volume_type is not None:
            self._values["volume_type"] = volume_type

    @builtins.property
    def delete_on_termination(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#delete_on_termination ManagedInstanceAws#delete_on_termination}.'''
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#encrypted ManagedInstanceAws#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#iops ManagedInstanceAws#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#kms_key_id ManagedInstanceAws#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#snapshot_id ManagedInstanceAws#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#throughput ManagedInstanceAws#throughput}.'''
        result = self._values.get("throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#volume_size ManagedInstanceAws#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#volume_type ManagedInstanceAws#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsBlockDeviceMappingsEbs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsBlockDeviceMappingsEbsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsBlockDeviceMappingsEbsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2904041a84091084359772bd40c785895cd6a4f7adef0fe0a6e4a43eeff58f00)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeleteOnTermination")
    def reset_delete_on_termination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteOnTermination", []))

    @jsii.member(jsii_name="resetEncrypted")
    def reset_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncrypted", []))

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

    @jsii.member(jsii_name="resetThroughput")
    def reset_throughput(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThroughput", []))

    @jsii.member(jsii_name="resetVolumeSize")
    def reset_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeSize", []))

    @jsii.member(jsii_name="resetVolumeType")
    def reset_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumeType", []))

    @builtins.property
    @jsii.member(jsii_name="deleteOnTerminationInput")
    def delete_on_termination_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteOnTerminationInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptedInput")
    def encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "encryptedInput"))

    @builtins.property
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

    @builtins.property
    @jsii.member(jsii_name="throughputInput")
    def throughput_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throughputInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeSizeInput")
    def volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteOnTermination")
    def delete_on_termination(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deleteOnTermination"))

    @delete_on_termination.setter
    def delete_on_termination(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90c1b7ed7bea68dc5864bc68558fbc2a73cabcdabcc160e0f9964b22869f3486)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteOnTermination", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "encrypted"))

    @encrypted.setter
    def encrypted(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba7e3c0564cabd0875745d544b643e169591f2910e8d89cf6adad416d703e8d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encrypted", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57dfd852d96dfae1182a1cfed145706bc2cba2287feb4f91f33a4a7046ef3aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8b17c792fff8fe4b73bb94d67eaddf3e96a3f4905a4c9776c1984d0b055d360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f12436c74bb76c4b86f57ac486691cde95738701d83bf5e5b0d862a165deb602)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snapshotId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="throughput")
    def throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throughput"))

    @throughput.setter
    def throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58fb4514ac8173d3776507dc57492f5b04267b4d57c8ed3edba833b6b1270b04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "throughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @volume_size.setter
    def volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b78c950d8c518add70189e7606f83d93bcc56722944d5595f14ec2903c7c29a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3bfa15ca7635a958f795c9603a4a27e6f05227cf08241444abd96d360a49369)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedInstanceAwsBlockDeviceMappingsEbs]:
        return typing.cast(typing.Optional[ManagedInstanceAwsBlockDeviceMappingsEbs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedInstanceAwsBlockDeviceMappingsEbs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4da7834b79f5befd97cc7e10582acef074ea76e2296276a61bd833047a8196df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsBlockDeviceMappingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsBlockDeviceMappingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__861422ac3892b6839fc6ba9af502b21bec982ff0e12c7a5030ec623f2783d673)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsBlockDeviceMappingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5885b2888d14ed49f69dfcf6ad943b999c7dd4fc33c2f668a9530887c28e91df)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsBlockDeviceMappingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__558a061178ea2bc3be1d8a9a5b7e15ab45891751bd4dc49d61f172f763edf008)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dfb9f1edc0554842145899aebeeb26b57ffc858f9b1a13884beae4081bae86d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__372fe474fa857e81a9f29b2eb0e25071c9fe33b9547a947c084697e47b6108c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsBlockDeviceMappings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsBlockDeviceMappings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsBlockDeviceMappings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57448ae7d5553aee7097e0410c0b8938370ef86360e904fddd1c3f2128c91d0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsBlockDeviceMappingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsBlockDeviceMappingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b74e606536529c4487b7c2d4d4a8402c64441d5d9c6a534ed2d4807b42a87185)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putEbs")
    def put_ebs(
        self,
        *,
        delete_on_termination: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        throughput: typing.Optional[jsii.Number] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#delete_on_termination ManagedInstanceAws#delete_on_termination}.
        :param encrypted: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#encrypted ManagedInstanceAws#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#iops ManagedInstanceAws#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#kms_key_id ManagedInstanceAws#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#snapshot_id ManagedInstanceAws#snapshot_id}.
        :param throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#throughput ManagedInstanceAws#throughput}.
        :param volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#volume_size ManagedInstanceAws#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#volume_type ManagedInstanceAws#volume_type}.
        '''
        value = ManagedInstanceAwsBlockDeviceMappingsEbs(
            delete_on_termination=delete_on_termination,
            encrypted=encrypted,
            iops=iops,
            kms_key_id=kms_key_id,
            snapshot_id=snapshot_id,
            throughput=throughput,
            volume_size=volume_size,
            volume_type=volume_type,
        )

        return typing.cast(None, jsii.invoke(self, "putEbs", [value]))

    @jsii.member(jsii_name="resetEbs")
    def reset_ebs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbs", []))

    @builtins.property
    @jsii.member(jsii_name="ebs")
    def ebs(self) -> ManagedInstanceAwsBlockDeviceMappingsEbsOutputReference:
        return typing.cast(ManagedInstanceAwsBlockDeviceMappingsEbsOutputReference, jsii.get(self, "ebs"))

    @builtins.property
    @jsii.member(jsii_name="deviceNameInput")
    def device_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsInput")
    def ebs_input(self) -> typing.Optional[ManagedInstanceAwsBlockDeviceMappingsEbs]:
        return typing.cast(typing.Optional[ManagedInstanceAwsBlockDeviceMappingsEbs], jsii.get(self, "ebsInput"))

    @builtins.property
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @device_name.setter
    def device_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d039306a1614b3cb5c12fbd967f8c9a5954040d251d5577d109385732481a994)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsBlockDeviceMappings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsBlockDeviceMappings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsBlockDeviceMappings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cda87cf46dce89bf8feede03743f157e49634d44b5b306040673cc4a44c3b3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "image_id": "imageId",
        "name": "name",
        "persist_block_devices": "persistBlockDevices",
        "product": "product",
        "subnet_ids": "subnetIds",
        "vpc_id": "vpcId",
        "auto_healing": "autoHealing",
        "block_device_mappings": "blockDeviceMappings",
        "block_devices_mode": "blockDevicesMode",
        "cpu_credits": "cpuCredits",
        "delete": "delete",
        "description": "description",
        "draining_timeout": "drainingTimeout",
        "ebs_optimized": "ebsOptimized",
        "elastic_ip": "elasticIp",
        "enable_monitoring": "enableMonitoring",
        "fallback_to_ondemand": "fallbackToOndemand",
        "grace_period": "gracePeriod",
        "health_check_type": "healthCheckType",
        "iam_instance_profile": "iamInstanceProfile",
        "id": "id",
        "instance_types": "instanceTypes",
        "integration_route53": "integrationRoute53",
        "key_pair": "keyPair",
        "life_cycle": "lifeCycle",
        "load_balancers": "loadBalancers",
        "managed_instance_action": "managedInstanceAction",
        "metadata_options": "metadataOptions",
        "minimum_instance_lifetime": "minimumInstanceLifetime",
        "network_interface": "networkInterface",
        "optimization_windows": "optimizationWindows",
        "orientation": "orientation",
        "persist_private_ip": "persistPrivateIp",
        "persist_root_device": "persistRootDevice",
        "placement_tenancy": "placementTenancy",
        "preferred_type": "preferredType",
        "preferred_types": "preferredTypes",
        "private_ip": "privateIp",
        "region": "region",
        "resource_requirements": "resourceRequirements",
        "resource_tag_specification": "resourceTagSpecification",
        "revert_to_spot": "revertToSpot",
        "scheduled_task": "scheduledTask",
        "security_group_ids": "securityGroupIds",
        "shutdown_script": "shutdownScript",
        "tags": "tags",
        "unhealthy_duration": "unhealthyDuration",
        "user_data": "userData",
        "utilize_reserved_instances": "utilizeReservedInstances",
    },
)
class ManagedInstanceAwsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        image_id: builtins.str,
        name: builtins.str,
        persist_block_devices: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        product: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        vpc_id: builtins.str,
        auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]]] = None,
        block_devices_mode: typing.Optional[builtins.str] = None,
        cpu_credits: typing.Optional[builtins.str] = None,
        delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsDelete", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        enable_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        grace_period: typing.Optional[jsii.Number] = None,
        health_check_type: typing.Optional[builtins.str] = None,
        iam_instance_profile: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        integration_route53: typing.Optional[typing.Union["ManagedInstanceAwsIntegrationRoute53", typing.Dict[builtins.str, typing.Any]]] = None,
        key_pair: typing.Optional[builtins.str] = None,
        life_cycle: typing.Optional[builtins.str] = None,
        load_balancers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsLoadBalancers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        managed_instance_action: typing.Optional[typing.Union["ManagedInstanceAwsManagedInstanceAction", typing.Dict[builtins.str, typing.Any]]] = None,
        metadata_options: typing.Optional[typing.Union["ManagedInstanceAwsMetadataOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        minimum_instance_lifetime: typing.Optional[jsii.Number] = None,
        network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsNetworkInterface", typing.Dict[builtins.str, typing.Any]]]]] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        orientation: typing.Optional[builtins.str] = None,
        persist_private_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        persist_root_device: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        placement_tenancy: typing.Optional[builtins.str] = None,
        preferred_type: typing.Optional[builtins.str] = None,
        preferred_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        private_ip: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        resource_requirements: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsResourceRequirements", typing.Dict[builtins.str, typing.Any]]]]] = None,
        resource_tag_specification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsResourceTagSpecification", typing.Dict[builtins.str, typing.Any]]]]] = None,
        revert_to_spot: typing.Optional[typing.Union["ManagedInstanceAwsRevertToSpot", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        unhealthy_duration: typing.Optional[jsii.Number] = None,
        user_data: typing.Optional[builtins.str] = None,
        utilize_reserved_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param image_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#image_id ManagedInstanceAws#image_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.
        :param persist_block_devices: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_block_devices ManagedInstanceAws#persist_block_devices}.
        :param product: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#product ManagedInstanceAws#product}.
        :param subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#subnet_ids ManagedInstanceAws#subnet_ids}.
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#vpc_id ManagedInstanceAws#vpc_id}.
        :param auto_healing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#auto_healing ManagedInstanceAws#auto_healing}.
        :param block_device_mappings: block_device_mappings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#block_device_mappings ManagedInstanceAws#block_device_mappings}
        :param block_devices_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#block_devices_mode ManagedInstanceAws#block_devices_mode}.
        :param cpu_credits: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#cpu_credits ManagedInstanceAws#cpu_credits}.
        :param delete: delete block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#delete ManagedInstanceAws#delete}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#description ManagedInstanceAws#description}.
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#draining_timeout ManagedInstanceAws#draining_timeout}.
        :param ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ebs_optimized ManagedInstanceAws#ebs_optimized}.
        :param elastic_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#elastic_ip ManagedInstanceAws#elastic_ip}.
        :param enable_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#enable_monitoring ManagedInstanceAws#enable_monitoring}.
        :param fallback_to_ondemand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#fallback_to_ondemand ManagedInstanceAws#fallback_to_ondemand}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#grace_period ManagedInstanceAws#grace_period}.
        :param health_check_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#health_check_type ManagedInstanceAws#health_check_type}.
        :param iam_instance_profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#iam_instance_profile ManagedInstanceAws#iam_instance_profile}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#id ManagedInstanceAws#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#instance_types ManagedInstanceAws#instance_types}.
        :param integration_route53: integration_route53 block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#integration_route53 ManagedInstanceAws#integration_route53}
        :param key_pair: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#key_pair ManagedInstanceAws#key_pair}.
        :param life_cycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#life_cycle ManagedInstanceAws#life_cycle}.
        :param load_balancers: load_balancers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#load_balancers ManagedInstanceAws#load_balancers}
        :param managed_instance_action: managed_instance_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#managed_instance_action ManagedInstanceAws#managed_instance_action}
        :param metadata_options: metadata_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#metadata_options ManagedInstanceAws#metadata_options}
        :param minimum_instance_lifetime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#minimum_instance_lifetime ManagedInstanceAws#minimum_instance_lifetime}.
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#network_interface ManagedInstanceAws#network_interface}
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#optimization_windows ManagedInstanceAws#optimization_windows}.
        :param orientation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#orientation ManagedInstanceAws#orientation}.
        :param persist_private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_private_ip ManagedInstanceAws#persist_private_ip}.
        :param persist_root_device: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_root_device ManagedInstanceAws#persist_root_device}.
        :param placement_tenancy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#placement_tenancy ManagedInstanceAws#placement_tenancy}.
        :param preferred_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#preferred_type ManagedInstanceAws#preferred_type}.
        :param preferred_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#preferred_types ManagedInstanceAws#preferred_types}.
        :param private_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#private_ip ManagedInstanceAws#private_ip}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#region ManagedInstanceAws#region}.
        :param resource_requirements: resource_requirements block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#resource_requirements ManagedInstanceAws#resource_requirements}
        :param resource_tag_specification: resource_tag_specification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#resource_tag_specification ManagedInstanceAws#resource_tag_specification}
        :param revert_to_spot: revert_to_spot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#revert_to_spot ManagedInstanceAws#revert_to_spot}
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#scheduled_task ManagedInstanceAws#scheduled_task}
        :param security_group_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#security_group_ids ManagedInstanceAws#security_group_ids}.
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#shutdown_script ManagedInstanceAws#shutdown_script}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#tags ManagedInstanceAws#tags}
        :param unhealthy_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#unhealthy_duration ManagedInstanceAws#unhealthy_duration}.
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#user_data ManagedInstanceAws#user_data}.
        :param utilize_reserved_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#utilize_reserved_instances ManagedInstanceAws#utilize_reserved_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(integration_route53, dict):
            integration_route53 = ManagedInstanceAwsIntegrationRoute53(**integration_route53)
        if isinstance(managed_instance_action, dict):
            managed_instance_action = ManagedInstanceAwsManagedInstanceAction(**managed_instance_action)
        if isinstance(metadata_options, dict):
            metadata_options = ManagedInstanceAwsMetadataOptions(**metadata_options)
        if isinstance(revert_to_spot, dict):
            revert_to_spot = ManagedInstanceAwsRevertToSpot(**revert_to_spot)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63caced62e9bceb84b90844c047b52505419e102f6dafea560f9879a213d651a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument image_id", value=image_id, expected_type=type_hints["image_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument persist_block_devices", value=persist_block_devices, expected_type=type_hints["persist_block_devices"])
            check_type(argname="argument product", value=product, expected_type=type_hints["product"])
            check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            check_type(argname="argument auto_healing", value=auto_healing, expected_type=type_hints["auto_healing"])
            check_type(argname="argument block_device_mappings", value=block_device_mappings, expected_type=type_hints["block_device_mappings"])
            check_type(argname="argument block_devices_mode", value=block_devices_mode, expected_type=type_hints["block_devices_mode"])
            check_type(argname="argument cpu_credits", value=cpu_credits, expected_type=type_hints["cpu_credits"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument elastic_ip", value=elastic_ip, expected_type=type_hints["elastic_ip"])
            check_type(argname="argument enable_monitoring", value=enable_monitoring, expected_type=type_hints["enable_monitoring"])
            check_type(argname="argument fallback_to_ondemand", value=fallback_to_ondemand, expected_type=type_hints["fallback_to_ondemand"])
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
            check_type(argname="argument health_check_type", value=health_check_type, expected_type=type_hints["health_check_type"])
            check_type(argname="argument iam_instance_profile", value=iam_instance_profile, expected_type=type_hints["iam_instance_profile"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument integration_route53", value=integration_route53, expected_type=type_hints["integration_route53"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument life_cycle", value=life_cycle, expected_type=type_hints["life_cycle"])
            check_type(argname="argument load_balancers", value=load_balancers, expected_type=type_hints["load_balancers"])
            check_type(argname="argument managed_instance_action", value=managed_instance_action, expected_type=type_hints["managed_instance_action"])
            check_type(argname="argument metadata_options", value=metadata_options, expected_type=type_hints["metadata_options"])
            check_type(argname="argument minimum_instance_lifetime", value=minimum_instance_lifetime, expected_type=type_hints["minimum_instance_lifetime"])
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
            check_type(argname="argument optimization_windows", value=optimization_windows, expected_type=type_hints["optimization_windows"])
            check_type(argname="argument orientation", value=orientation, expected_type=type_hints["orientation"])
            check_type(argname="argument persist_private_ip", value=persist_private_ip, expected_type=type_hints["persist_private_ip"])
            check_type(argname="argument persist_root_device", value=persist_root_device, expected_type=type_hints["persist_root_device"])
            check_type(argname="argument placement_tenancy", value=placement_tenancy, expected_type=type_hints["placement_tenancy"])
            check_type(argname="argument preferred_type", value=preferred_type, expected_type=type_hints["preferred_type"])
            check_type(argname="argument preferred_types", value=preferred_types, expected_type=type_hints["preferred_types"])
            check_type(argname="argument private_ip", value=private_ip, expected_type=type_hints["private_ip"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument resource_requirements", value=resource_requirements, expected_type=type_hints["resource_requirements"])
            check_type(argname="argument resource_tag_specification", value=resource_tag_specification, expected_type=type_hints["resource_tag_specification"])
            check_type(argname="argument revert_to_spot", value=revert_to_spot, expected_type=type_hints["revert_to_spot"])
            check_type(argname="argument scheduled_task", value=scheduled_task, expected_type=type_hints["scheduled_task"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument shutdown_script", value=shutdown_script, expected_type=type_hints["shutdown_script"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument unhealthy_duration", value=unhealthy_duration, expected_type=type_hints["unhealthy_duration"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument utilize_reserved_instances", value=utilize_reserved_instances, expected_type=type_hints["utilize_reserved_instances"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "image_id": image_id,
            "name": name,
            "persist_block_devices": persist_block_devices,
            "product": product,
            "subnet_ids": subnet_ids,
            "vpc_id": vpc_id,
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
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if block_devices_mode is not None:
            self._values["block_devices_mode"] = block_devices_mode
        if cpu_credits is not None:
            self._values["cpu_credits"] = cpu_credits
        if delete is not None:
            self._values["delete"] = delete
        if description is not None:
            self._values["description"] = description
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if elastic_ip is not None:
            self._values["elastic_ip"] = elastic_ip
        if enable_monitoring is not None:
            self._values["enable_monitoring"] = enable_monitoring
        if fallback_to_ondemand is not None:
            self._values["fallback_to_ondemand"] = fallback_to_ondemand
        if grace_period is not None:
            self._values["grace_period"] = grace_period
        if health_check_type is not None:
            self._values["health_check_type"] = health_check_type
        if iam_instance_profile is not None:
            self._values["iam_instance_profile"] = iam_instance_profile
        if id is not None:
            self._values["id"] = id
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if integration_route53 is not None:
            self._values["integration_route53"] = integration_route53
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if life_cycle is not None:
            self._values["life_cycle"] = life_cycle
        if load_balancers is not None:
            self._values["load_balancers"] = load_balancers
        if managed_instance_action is not None:
            self._values["managed_instance_action"] = managed_instance_action
        if metadata_options is not None:
            self._values["metadata_options"] = metadata_options
        if minimum_instance_lifetime is not None:
            self._values["minimum_instance_lifetime"] = minimum_instance_lifetime
        if network_interface is not None:
            self._values["network_interface"] = network_interface
        if optimization_windows is not None:
            self._values["optimization_windows"] = optimization_windows
        if orientation is not None:
            self._values["orientation"] = orientation
        if persist_private_ip is not None:
            self._values["persist_private_ip"] = persist_private_ip
        if persist_root_device is not None:
            self._values["persist_root_device"] = persist_root_device
        if placement_tenancy is not None:
            self._values["placement_tenancy"] = placement_tenancy
        if preferred_type is not None:
            self._values["preferred_type"] = preferred_type
        if preferred_types is not None:
            self._values["preferred_types"] = preferred_types
        if private_ip is not None:
            self._values["private_ip"] = private_ip
        if region is not None:
            self._values["region"] = region
        if resource_requirements is not None:
            self._values["resource_requirements"] = resource_requirements
        if resource_tag_specification is not None:
            self._values["resource_tag_specification"] = resource_tag_specification
        if revert_to_spot is not None:
            self._values["revert_to_spot"] = revert_to_spot
        if scheduled_task is not None:
            self._values["scheduled_task"] = scheduled_task
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if shutdown_script is not None:
            self._values["shutdown_script"] = shutdown_script
        if tags is not None:
            self._values["tags"] = tags
        if unhealthy_duration is not None:
            self._values["unhealthy_duration"] = unhealthy_duration
        if user_data is not None:
            self._values["user_data"] = user_data
        if utilize_reserved_instances is not None:
            self._values["utilize_reserved_instances"] = utilize_reserved_instances

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
    def image_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#image_id ManagedInstanceAws#image_id}.'''
        result = self._values.get("image_id")
        assert result is not None, "Required property 'image_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def persist_block_devices(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_block_devices ManagedInstanceAws#persist_block_devices}.'''
        result = self._values.get("persist_block_devices")
        assert result is not None, "Required property 'persist_block_devices' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def product(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#product ManagedInstanceAws#product}.'''
        result = self._values.get("product")
        assert result is not None, "Required property 'product' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#subnet_ids ManagedInstanceAws#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#vpc_id ManagedInstanceAws#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#auto_healing ManagedInstanceAws#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsBlockDeviceMappings]]]:
        '''block_device_mappings block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#block_device_mappings ManagedInstanceAws#block_device_mappings}
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsBlockDeviceMappings]]], result)

    @builtins.property
    def block_devices_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#block_devices_mode ManagedInstanceAws#block_devices_mode}.'''
        result = self._values.get("block_devices_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_credits(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#cpu_credits ManagedInstanceAws#cpu_credits}.'''
        result = self._values.get("cpu_credits")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsDelete"]]]:
        '''delete block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#delete ManagedInstanceAws#delete}
        '''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsDelete"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#description ManagedInstanceAws#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#draining_timeout ManagedInstanceAws#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ebs_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ebs_optimized ManagedInstanceAws#ebs_optimized}.'''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def elastic_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#elastic_ip ManagedInstanceAws#elastic_ip}.'''
        result = self._values.get("elastic_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_monitoring(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#enable_monitoring ManagedInstanceAws#enable_monitoring}.'''
        result = self._values.get("enable_monitoring")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def fallback_to_ondemand(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#fallback_to_ondemand ManagedInstanceAws#fallback_to_ondemand}.'''
        result = self._values.get("fallback_to_ondemand")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def grace_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#grace_period ManagedInstanceAws#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#health_check_type ManagedInstanceAws#health_check_type}.'''
        result = self._values.get("health_check_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_instance_profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#iam_instance_profile ManagedInstanceAws#iam_instance_profile}.'''
        result = self._values.get("iam_instance_profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#id ManagedInstanceAws#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#instance_types ManagedInstanceAws#instance_types}.'''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def integration_route53(
        self,
    ) -> typing.Optional["ManagedInstanceAwsIntegrationRoute53"]:
        '''integration_route53 block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#integration_route53 ManagedInstanceAws#integration_route53}
        '''
        result = self._values.get("integration_route53")
        return typing.cast(typing.Optional["ManagedInstanceAwsIntegrationRoute53"], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#key_pair ManagedInstanceAws#key_pair}.'''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def life_cycle(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#life_cycle ManagedInstanceAws#life_cycle}.'''
        result = self._values.get("life_cycle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsLoadBalancers"]]]:
        '''load_balancers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#load_balancers ManagedInstanceAws#load_balancers}
        '''
        result = self._values.get("load_balancers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsLoadBalancers"]]], result)

    @builtins.property
    def managed_instance_action(
        self,
    ) -> typing.Optional["ManagedInstanceAwsManagedInstanceAction"]:
        '''managed_instance_action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#managed_instance_action ManagedInstanceAws#managed_instance_action}
        '''
        result = self._values.get("managed_instance_action")
        return typing.cast(typing.Optional["ManagedInstanceAwsManagedInstanceAction"], result)

    @builtins.property
    def metadata_options(self) -> typing.Optional["ManagedInstanceAwsMetadataOptions"]:
        '''metadata_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#metadata_options ManagedInstanceAws#metadata_options}
        '''
        result = self._values.get("metadata_options")
        return typing.cast(typing.Optional["ManagedInstanceAwsMetadataOptions"], result)

    @builtins.property
    def minimum_instance_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#minimum_instance_lifetime ManagedInstanceAws#minimum_instance_lifetime}.'''
        result = self._values.get("minimum_instance_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsNetworkInterface"]]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#network_interface ManagedInstanceAws#network_interface}
        '''
        result = self._values.get("network_interface")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsNetworkInterface"]]], result)

    @builtins.property
    def optimization_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#optimization_windows ManagedInstanceAws#optimization_windows}.'''
        result = self._values.get("optimization_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def orientation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#orientation ManagedInstanceAws#orientation}.'''
        result = self._values.get("orientation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def persist_private_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_private_ip ManagedInstanceAws#persist_private_ip}.'''
        result = self._values.get("persist_private_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def persist_root_device(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#persist_root_device ManagedInstanceAws#persist_root_device}.'''
        result = self._values.get("persist_root_device")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def placement_tenancy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#placement_tenancy ManagedInstanceAws#placement_tenancy}.'''
        result = self._values.get("placement_tenancy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#preferred_type ManagedInstanceAws#preferred_type}.'''
        result = self._values.get("preferred_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#preferred_types ManagedInstanceAws#preferred_types}.'''
        result = self._values.get("preferred_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def private_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#private_ip ManagedInstanceAws#private_ip}.'''
        result = self._values.get("private_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#region ManagedInstanceAws#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_requirements(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceRequirements"]]]:
        '''resource_requirements block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#resource_requirements ManagedInstanceAws#resource_requirements}
        '''
        result = self._values.get("resource_requirements")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceRequirements"]]], result)

    @builtins.property
    def resource_tag_specification(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceTagSpecification"]]]:
        '''resource_tag_specification block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#resource_tag_specification ManagedInstanceAws#resource_tag_specification}
        '''
        result = self._values.get("resource_tag_specification")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsResourceTagSpecification"]]], result)

    @builtins.property
    def revert_to_spot(self) -> typing.Optional["ManagedInstanceAwsRevertToSpot"]:
        '''revert_to_spot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#revert_to_spot ManagedInstanceAws#revert_to_spot}
        '''
        result = self._values.get("revert_to_spot")
        return typing.cast(typing.Optional["ManagedInstanceAwsRevertToSpot"], result)

    @builtins.property
    def scheduled_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsScheduledTask"]]]:
        '''scheduled_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#scheduled_task ManagedInstanceAws#scheduled_task}
        '''
        result = self._values.get("scheduled_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsScheduledTask"]]], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#security_group_ids ManagedInstanceAws#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def shutdown_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#shutdown_script ManagedInstanceAws#shutdown_script}.'''
        result = self._values.get("shutdown_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#tags ManagedInstanceAws#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsTags"]]], result)

    @builtins.property
    def unhealthy_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#unhealthy_duration ManagedInstanceAws#unhealthy_duration}.'''
        result = self._values.get("unhealthy_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#user_data ManagedInstanceAws#user_data}.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def utilize_reserved_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#utilize_reserved_instances ManagedInstanceAws#utilize_reserved_instances}.'''
        result = self._values.get("utilize_reserved_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsDelete",
    jsii_struct_bases=[],
    name_mapping={
        "ami_backup_should_delete_images": "amiBackupShouldDeleteImages",
        "deallocation_config_should_delete_images": "deallocationConfigShouldDeleteImages",
        "should_delete_network_interfaces": "shouldDeleteNetworkInterfaces",
        "should_delete_snapshots": "shouldDeleteSnapshots",
        "should_delete_volumes": "shouldDeleteVolumes",
        "should_terminate_instance": "shouldTerminateInstance",
    },
)
class ManagedInstanceAwsDelete:
    def __init__(
        self,
        *,
        ami_backup_should_delete_images: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deallocation_config_should_delete_images: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_delete_network_interfaces: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_delete_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_delete_volumes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_terminate_instance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param ami_backup_should_delete_images: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ami_backup_should_delete_images ManagedInstanceAws#ami_backup_should_delete_images}.
        :param deallocation_config_should_delete_images: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#deallocation_config_should_delete_images ManagedInstanceAws#deallocation_config_should_delete_images}.
        :param should_delete_network_interfaces: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_delete_network_interfaces ManagedInstanceAws#should_delete_network_interfaces}.
        :param should_delete_snapshots: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_delete_snapshots ManagedInstanceAws#should_delete_snapshots}.
        :param should_delete_volumes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_delete_volumes ManagedInstanceAws#should_delete_volumes}.
        :param should_terminate_instance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_terminate_instance ManagedInstanceAws#should_terminate_instance}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__022ac0d66f87c340124a259215cd2f7a5e24e66566a5a0c98beba6efde9ef0c5)
            check_type(argname="argument ami_backup_should_delete_images", value=ami_backup_should_delete_images, expected_type=type_hints["ami_backup_should_delete_images"])
            check_type(argname="argument deallocation_config_should_delete_images", value=deallocation_config_should_delete_images, expected_type=type_hints["deallocation_config_should_delete_images"])
            check_type(argname="argument should_delete_network_interfaces", value=should_delete_network_interfaces, expected_type=type_hints["should_delete_network_interfaces"])
            check_type(argname="argument should_delete_snapshots", value=should_delete_snapshots, expected_type=type_hints["should_delete_snapshots"])
            check_type(argname="argument should_delete_volumes", value=should_delete_volumes, expected_type=type_hints["should_delete_volumes"])
            check_type(argname="argument should_terminate_instance", value=should_terminate_instance, expected_type=type_hints["should_terminate_instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ami_backup_should_delete_images is not None:
            self._values["ami_backup_should_delete_images"] = ami_backup_should_delete_images
        if deallocation_config_should_delete_images is not None:
            self._values["deallocation_config_should_delete_images"] = deallocation_config_should_delete_images
        if should_delete_network_interfaces is not None:
            self._values["should_delete_network_interfaces"] = should_delete_network_interfaces
        if should_delete_snapshots is not None:
            self._values["should_delete_snapshots"] = should_delete_snapshots
        if should_delete_volumes is not None:
            self._values["should_delete_volumes"] = should_delete_volumes
        if should_terminate_instance is not None:
            self._values["should_terminate_instance"] = should_terminate_instance

    @builtins.property
    def ami_backup_should_delete_images(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#ami_backup_should_delete_images ManagedInstanceAws#ami_backup_should_delete_images}.'''
        result = self._values.get("ami_backup_should_delete_images")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deallocation_config_should_delete_images(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#deallocation_config_should_delete_images ManagedInstanceAws#deallocation_config_should_delete_images}.'''
        result = self._values.get("deallocation_config_should_delete_images")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_delete_network_interfaces(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_delete_network_interfaces ManagedInstanceAws#should_delete_network_interfaces}.'''
        result = self._values.get("should_delete_network_interfaces")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_delete_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_delete_snapshots ManagedInstanceAws#should_delete_snapshots}.'''
        result = self._values.get("should_delete_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_delete_volumes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_delete_volumes ManagedInstanceAws#should_delete_volumes}.'''
        result = self._values.get("should_delete_volumes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_terminate_instance(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_terminate_instance ManagedInstanceAws#should_terminate_instance}.'''
        result = self._values.get("should_terminate_instance")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsDelete(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsDeleteList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsDeleteList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdb97bc6381095ba940fe057afe520d6aa06ddda0c3e662841a08850c1985b40)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ManagedInstanceAwsDeleteOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb3c9587524c3ac2c5b8a4cff78f2ffcfbecfb329e6ec27b3228774e32999053)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsDeleteOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__442d07121268197492d8ae3ea259b31364165d3f198edf910a49c2a4ac0eb7c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f0ea742daeed84326cf459b25a4e1e1654c1cdc2e0a43341334d9c68ff2cc6e9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__556939914a8d8646ba355506c63038c54be1179199b9a7e2e94c2b9dcff457bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsDelete]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsDelete]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsDelete]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__262dbebe75da1d6264906b59d3b6dcffe8bf7ca0cfb7f31dd39c17390beaa920)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsDeleteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsDeleteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__deb5d4a14e5140f6188d1c8788f39e079974ee2d31298aa61f43e38a197c893e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAmiBackupShouldDeleteImages")
    def reset_ami_backup_should_delete_images(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmiBackupShouldDeleteImages", []))

    @jsii.member(jsii_name="resetDeallocationConfigShouldDeleteImages")
    def reset_deallocation_config_should_delete_images(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeallocationConfigShouldDeleteImages", []))

    @jsii.member(jsii_name="resetShouldDeleteNetworkInterfaces")
    def reset_should_delete_network_interfaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldDeleteNetworkInterfaces", []))

    @jsii.member(jsii_name="resetShouldDeleteSnapshots")
    def reset_should_delete_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldDeleteSnapshots", []))

    @jsii.member(jsii_name="resetShouldDeleteVolumes")
    def reset_should_delete_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldDeleteVolumes", []))

    @jsii.member(jsii_name="resetShouldTerminateInstance")
    def reset_should_terminate_instance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldTerminateInstance", []))

    @builtins.property
    @jsii.member(jsii_name="amiBackupShouldDeleteImagesInput")
    def ami_backup_should_delete_images_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "amiBackupShouldDeleteImagesInput"))

    @builtins.property
    @jsii.member(jsii_name="deallocationConfigShouldDeleteImagesInput")
    def deallocation_config_should_delete_images_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deallocationConfigShouldDeleteImagesInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldDeleteNetworkInterfacesInput")
    def should_delete_network_interfaces_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldDeleteNetworkInterfacesInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldDeleteSnapshotsInput")
    def should_delete_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldDeleteSnapshotsInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldDeleteVolumesInput")
    def should_delete_volumes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldDeleteVolumesInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldTerminateInstanceInput")
    def should_terminate_instance_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldTerminateInstanceInput"))

    @builtins.property
    @jsii.member(jsii_name="amiBackupShouldDeleteImages")
    def ami_backup_should_delete_images(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "amiBackupShouldDeleteImages"))

    @ami_backup_should_delete_images.setter
    def ami_backup_should_delete_images(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__504e2fb25eb7e58d526da93350211644e180db5d9f7b888a79d8f87f7d466fe5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amiBackupShouldDeleteImages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deallocationConfigShouldDeleteImages")
    def deallocation_config_should_delete_images(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deallocationConfigShouldDeleteImages"))

    @deallocation_config_should_delete_images.setter
    def deallocation_config_should_delete_images(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d916788d3adf21ae2f8416b72a0205571af51bc9a4366fc7536e8a456720e04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deallocationConfigShouldDeleteImages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldDeleteNetworkInterfaces")
    def should_delete_network_interfaces(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldDeleteNetworkInterfaces"))

    @should_delete_network_interfaces.setter
    def should_delete_network_interfaces(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa6eb9acd7a917b24fa1f7891074e32d075aa75470311d74db42ff6866132b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldDeleteNetworkInterfaces", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldDeleteSnapshots")
    def should_delete_snapshots(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldDeleteSnapshots"))

    @should_delete_snapshots.setter
    def should_delete_snapshots(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__395a1901ddb9cd8e78f0a501d1620027aa2ddf1da2506dd5b7982faa6f1ec1b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldDeleteSnapshots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldDeleteVolumes")
    def should_delete_volumes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldDeleteVolumes"))

    @should_delete_volumes.setter
    def should_delete_volumes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38d76753ab7c770445a2c42f1b882faec3bd3a647aa7a89e7dff3660e6b1ba63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldDeleteVolumes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldTerminateInstance")
    def should_terminate_instance(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldTerminateInstance"))

    @should_terminate_instance.setter
    def should_terminate_instance(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a8dfc41eded8e442db45211b1b689cca7a7408ba425c2e1153826079f6cc5e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldTerminateInstance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsDelete]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsDelete]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsDelete]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1208dd8082a574e665edea1166d1e31dd4d0c0224a02a4a57690eca61837a48f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53",
    jsii_struct_bases=[],
    name_mapping={"domains": "domains"},
)
class ManagedInstanceAwsIntegrationRoute53:
    def __init__(
        self,
        *,
        domains: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsIntegrationRoute53Domains", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param domains: domains block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#domains ManagedInstanceAws#domains}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c25e0e273c4f29573830d8a0d398673c2d7ce90264bea372786486f0f4e17c2d)
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domains": domains,
        }

    @builtins.property
    def domains(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsIntegrationRoute53Domains"]]:
        '''domains block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#domains ManagedInstanceAws#domains}
        '''
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsIntegrationRoute53Domains"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsIntegrationRoute53(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53Domains",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone_id": "hostedZoneId",
        "record_sets": "recordSets",
        "record_set_type": "recordSetType",
        "spotinst_acct_id": "spotinstAcctId",
    },
)
class ManagedInstanceAwsIntegrationRoute53Domains:
    def __init__(
        self,
        *,
        hosted_zone_id: builtins.str,
        record_sets: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsIntegrationRoute53DomainsRecordSets", typing.Dict[builtins.str, typing.Any]]]],
        record_set_type: typing.Optional[builtins.str] = None,
        spotinst_acct_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#hosted_zone_id ManagedInstanceAws#hosted_zone_id}.
        :param record_sets: record_sets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#record_sets ManagedInstanceAws#record_sets}
        :param record_set_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#record_set_type ManagedInstanceAws#record_set_type}.
        :param spotinst_acct_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#spotinst_acct_id ManagedInstanceAws#spotinst_acct_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57e25eb73b780d9dd61fe1679f93281c1e00c5d3214c22d3f6a6bcdc3e544280)
            check_type(argname="argument hosted_zone_id", value=hosted_zone_id, expected_type=type_hints["hosted_zone_id"])
            check_type(argname="argument record_sets", value=record_sets, expected_type=type_hints["record_sets"])
            check_type(argname="argument record_set_type", value=record_set_type, expected_type=type_hints["record_set_type"])
            check_type(argname="argument spotinst_acct_id", value=spotinst_acct_id, expected_type=type_hints["spotinst_acct_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone_id": hosted_zone_id,
            "record_sets": record_sets,
        }
        if record_set_type is not None:
            self._values["record_set_type"] = record_set_type
        if spotinst_acct_id is not None:
            self._values["spotinst_acct_id"] = spotinst_acct_id

    @builtins.property
    def hosted_zone_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#hosted_zone_id ManagedInstanceAws#hosted_zone_id}.'''
        result = self._values.get("hosted_zone_id")
        assert result is not None, "Required property 'hosted_zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def record_sets(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsIntegrationRoute53DomainsRecordSets"]]:
        '''record_sets block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#record_sets ManagedInstanceAws#record_sets}
        '''
        result = self._values.get("record_sets")
        assert result is not None, "Required property 'record_sets' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsIntegrationRoute53DomainsRecordSets"]], result)

    @builtins.property
    def record_set_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#record_set_type ManagedInstanceAws#record_set_type}.'''
        result = self._values.get("record_set_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spotinst_acct_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#spotinst_acct_id ManagedInstanceAws#spotinst_acct_id}.'''
        result = self._values.get("spotinst_acct_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsIntegrationRoute53Domains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsIntegrationRoute53DomainsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53DomainsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf8f3e31662feebf4f6c7b8782dad0ee800ce9ff95089815542e690b5a573c9b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsIntegrationRoute53DomainsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78d040de36ea0c93f66df14775e45fdae26c1f33cf5667bef707e93affafe9a1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsIntegrationRoute53DomainsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__867574bbfdd1b12bd1c1c78cea3b914116737ba42008140524676b5092b15c15)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da4885368c73406eed7c22cbc1613a4a8a454216fafa3b33f2e301f3ccc3d5be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5175c3d80efa9622a1e6ad953c8cc9d8233583d34641faf87b9a14356b50882)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53Domains]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53Domains]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53Domains]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a53d8e438c3c4b0fa40d24a0497df2bc33513013cc6eab43088668126213fc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsIntegrationRoute53DomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53DomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7decdf639cbc2be9d57d302b718113cebe5596e111b2246f3d74b9896da3c796)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRecordSets")
    def put_record_sets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ManagedInstanceAwsIntegrationRoute53DomainsRecordSets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f889c89e68a893e11e7e701f0e5382d6a1a6b4936dbbe170c5343cf343d5e980)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecordSets", [value]))

    @jsii.member(jsii_name="resetRecordSetType")
    def reset_record_set_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecordSetType", []))

    @jsii.member(jsii_name="resetSpotinstAcctId")
    def reset_spotinst_acct_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotinstAcctId", []))

    @builtins.property
    @jsii.member(jsii_name="recordSets")
    def record_sets(
        self,
    ) -> "ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsList":
        return typing.cast("ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsList", jsii.get(self, "recordSets"))

    @builtins.property
    @jsii.member(jsii_name="hostedZoneIdInput")
    def hosted_zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostedZoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="recordSetsInput")
    def record_sets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsIntegrationRoute53DomainsRecordSets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ManagedInstanceAwsIntegrationRoute53DomainsRecordSets"]]], jsii.get(self, "recordSetsInput"))

    @builtins.property
    @jsii.member(jsii_name="recordSetTypeInput")
    def record_set_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordSetTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="spotinstAcctIdInput")
    def spotinst_acct_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotinstAcctIdInput"))

    @builtins.property
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @hosted_zone_id.setter
    def hosted_zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c21bc74c8677434cb19ff8d6078c09ba54d87fc25437cbe9dfdb371b751ec3fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostedZoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recordSetType")
    def record_set_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recordSetType"))

    @record_set_type.setter
    def record_set_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f0dac342189559834682f8be30dbcd4c1cce7a4ebf3b1b6b28a1bfdd65262d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recordSetType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotinstAcctId")
    def spotinst_acct_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotinstAcctId"))

    @spotinst_acct_id.setter
    def spotinst_acct_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73bbfe36e8ce312cca92a53ce143bbeba56fd395c7e420e0ecbc70a30fcfe4ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotinstAcctId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53Domains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53Domains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53Domains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a0daa75846de2044788f82b29b6e4f1f255203c56727db7490921bd8189886c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53DomainsRecordSets",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "use_public_dns": "usePublicDns",
        "use_public_ip": "usePublicIp",
    },
)
class ManagedInstanceAwsIntegrationRoute53DomainsRecordSets:
    def __init__(
        self,
        *,
        name: builtins.str,
        use_public_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.
        :param use_public_dns: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#use_public_dns ManagedInstanceAws#use_public_dns}.
        :param use_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#use_public_ip ManagedInstanceAws#use_public_ip}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__922e4f578391ecd0ffb09af07f46f88306f948f6dc1865f5367f9ff5c1765e99)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument use_public_dns", value=use_public_dns, expected_type=type_hints["use_public_dns"])
            check_type(argname="argument use_public_ip", value=use_public_ip, expected_type=type_hints["use_public_ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if use_public_dns is not None:
            self._values["use_public_dns"] = use_public_dns
        if use_public_ip is not None:
            self._values["use_public_ip"] = use_public_ip

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def use_public_dns(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#use_public_dns ManagedInstanceAws#use_public_dns}.'''
        result = self._values.get("use_public_dns")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_public_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#use_public_ip ManagedInstanceAws#use_public_ip}.'''
        result = self._values.get("use_public_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsIntegrationRoute53DomainsRecordSets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26cc45b591fd16151c13ac2d0dccb2d78fdff830d7d953cde7d6a7e5b33cdcbd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c0763f0ca2be0cc1691511b621c836ab5f9c82773d2680e8bc069562067bfb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f896e1f2057633d841fd2c36f58ad8ff863b979c1f20b2a0993cdc739dc2b577)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b15a4a853c50254cc7e2dc855344ff88d5a17163ecfb8a42c5c1f818349e5720)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5c210a2a38d0dca8c90dcd3ee07deac743fc92e3e62980accdb35e352036153)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11816d5225609931995aa6b657006e016d4f1497459fe3e7b825a2ac4c269429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__080f347e24ee3c2351a2bc9f412ac5c9557ed50ec13f5687bace095d569ea17f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetUsePublicDns")
    def reset_use_public_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsePublicDns", []))

    @jsii.member(jsii_name="resetUsePublicIp")
    def reset_use_public_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsePublicIp", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="usePublicDnsInput")
    def use_public_dns_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePublicDnsInput"))

    @builtins.property
    @jsii.member(jsii_name="usePublicIpInput")
    def use_public_ip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePublicIpInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd6f1e71908f2d70bd6a27234f54b282921256953e23916fa720ec150e9bdbdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usePublicDns")
    def use_public_dns(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usePublicDns"))

    @use_public_dns.setter
    def use_public_dns(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d4aaac6d0f6b73ea4905fbfd55d32bcefb0cd46237eec4071490393bc8cd36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePublicDns", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usePublicIp")
    def use_public_ip(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usePublicIp"))

    @use_public_ip.setter
    def use_public_ip(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f3656ee701da9e226eea684161faff48856cd6646531b12db10b8fd7d8fb5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePublicIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a80a7ab434a9045c640819e18dc8b42c718b0a0b501551c934e8bac538174613)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsIntegrationRoute53OutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsIntegrationRoute53OutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d0fd0ff9a1ee6db32506e301c839e0fdefd874bb725047b2d8520ef47dd2c0a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDomains")
    def put_domains(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsIntegrationRoute53Domains, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ff3e59cd59585804f1664c3b12b7cafe980a4ad7578e1b8b6c234a55bb87d28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDomains", [value]))

    @builtins.property
    @jsii.member(jsii_name="domains")
    def domains(self) -> ManagedInstanceAwsIntegrationRoute53DomainsList:
        return typing.cast(ManagedInstanceAwsIntegrationRoute53DomainsList, jsii.get(self, "domains"))

    @builtins.property
    @jsii.member(jsii_name="domainsInput")
    def domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53Domains]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53Domains]]], jsii.get(self, "domainsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedInstanceAwsIntegrationRoute53]:
        return typing.cast(typing.Optional[ManagedInstanceAwsIntegrationRoute53], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedInstanceAwsIntegrationRoute53],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eb9d58506668488d76ec77d3399a93503c9f13620ad3194c530372a8ddc1521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsLoadBalancers",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "arn": "arn", "name": "name"},
)
class ManagedInstanceAwsLoadBalancers:
    def __init__(
        self,
        *,
        type: builtins.str,
        arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#type ManagedInstanceAws#type}.
        :param arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#arn ManagedInstanceAws#arn}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07fcdbbc077261ce172d6dd3570cf414aa0014312e4b1ab9e56757212baeb52a)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if arn is not None:
            self._values["arn"] = arn
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#type ManagedInstanceAws#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#arn ManagedInstanceAws#arn}.'''
        result = self._values.get("arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#name ManagedInstanceAws#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsLoadBalancers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsLoadBalancersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsLoadBalancersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b0432368002e6f35cee94404c89ccb904d5d5978a93075ac433943a6943837f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsLoadBalancersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9adc7d31a54a851e954f3dea3e619009f9bff58f1ac5300fc08db626fb80054c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsLoadBalancersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efae4d6f8d17f1f1d7ddf644b8154f5a69fa2e4eab6ff96d526bddd00d3c112c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e0ccbc04742137a7a0a4b3ae3c4c7549865f5f9d142fd1fee37212d2ad9ed87)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f24acb5bdde6dd85aaec98e86a2251b53c41a6a59ca048794510ecbb41a9721)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsLoadBalancers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsLoadBalancers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsLoadBalancers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8431e08fa7ecd960cd62824b7d39d47c2f1683ddeb10521649f25d846d66fc78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsLoadBalancersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsLoadBalancersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__12a019489d725fb61f1ab76bbd7b0aaaa37111d82250e1f7dbc46271ac1a203c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetArn")
    def reset_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArn", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7c107ac3ed937b38abb47b015f0ebea1a3f9488f99cae26c7e24f6bc626ecf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "arn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91aeb2cb7540c68d0aab12ebb813636124ec207d1173a0ce27798b36f36fe01c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efadfad04ee30e2037be3f272c1f24d4d3a131e0ce05b60d79b015756354f440)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsLoadBalancers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsLoadBalancers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsLoadBalancers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15d08733bad001ee62091d5129bff77b29785a9e11539312ac61de105d4050ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsManagedInstanceAction",
    jsii_struct_bases=[],
    name_mapping={"type": "type"},
)
class ManagedInstanceAwsManagedInstanceAction:
    def __init__(self, *, type: builtins.str) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#type ManagedInstanceAws#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90d5b22970c2aade4005dee48bf87929dc83e955ee3fa500207e99c6a6280d04)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#type ManagedInstanceAws#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsManagedInstanceAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsManagedInstanceActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsManagedInstanceActionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f4026826348548f0874191f4b28aaed0ef1e8db38ae02e1709e96dbbbfef5e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b28c006022d7da5a4d64170b05f6e15a7dfa24548b1e8bfcbc80ee48363a616f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ManagedInstanceAwsManagedInstanceAction]:
        return typing.cast(typing.Optional[ManagedInstanceAwsManagedInstanceAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedInstanceAwsManagedInstanceAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a23df4573a2ba9eaad21144535d4c25363c2ed175fff4fde8af5e8ceef59179)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsMetadataOptions",
    jsii_struct_bases=[],
    name_mapping={
        "http_tokens": "httpTokens",
        "http_put_response_hop_limit": "httpPutResponseHopLimit",
        "instance_metadata_tags": "instanceMetadataTags",
    },
)
class ManagedInstanceAwsMetadataOptions:
    def __init__(
        self,
        *,
        http_tokens: builtins.str,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        instance_metadata_tags: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param http_tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#http_tokens ManagedInstanceAws#http_tokens}.
        :param http_put_response_hop_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#http_put_response_hop_limit ManagedInstanceAws#http_put_response_hop_limit}.
        :param instance_metadata_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#instance_metadata_tags ManagedInstanceAws#instance_metadata_tags}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df459da1e581e1ed0946d26cdd848a7496b8ce3709633b6c6f0aae55ae59aa39)
            check_type(argname="argument http_tokens", value=http_tokens, expected_type=type_hints["http_tokens"])
            check_type(argname="argument http_put_response_hop_limit", value=http_put_response_hop_limit, expected_type=type_hints["http_put_response_hop_limit"])
            check_type(argname="argument instance_metadata_tags", value=instance_metadata_tags, expected_type=type_hints["instance_metadata_tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_tokens": http_tokens,
        }
        if http_put_response_hop_limit is not None:
            self._values["http_put_response_hop_limit"] = http_put_response_hop_limit
        if instance_metadata_tags is not None:
            self._values["instance_metadata_tags"] = instance_metadata_tags

    @builtins.property
    def http_tokens(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#http_tokens ManagedInstanceAws#http_tokens}.'''
        result = self._values.get("http_tokens")
        assert result is not None, "Required property 'http_tokens' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def http_put_response_hop_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#http_put_response_hop_limit ManagedInstanceAws#http_put_response_hop_limit}.'''
        result = self._values.get("http_put_response_hop_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_metadata_tags(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#instance_metadata_tags ManagedInstanceAws#instance_metadata_tags}.'''
        result = self._values.get("instance_metadata_tags")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsMetadataOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsMetadataOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsMetadataOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3eb3ed3306066eaae7a1de2dacb38a2b0078b15d20fae8cdfb4d2921aa46f912)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHttpPutResponseHopLimit")
    def reset_http_put_response_hop_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpPutResponseHopLimit", []))

    @jsii.member(jsii_name="resetInstanceMetadataTags")
    def reset_instance_metadata_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceMetadataTags", []))

    @builtins.property
    @jsii.member(jsii_name="httpPutResponseHopLimitInput")
    def http_put_response_hop_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpPutResponseHopLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="httpTokensInput")
    def http_tokens_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpTokensInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceMetadataTagsInput")
    def instance_metadata_tags_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceMetadataTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="httpPutResponseHopLimit")
    def http_put_response_hop_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpPutResponseHopLimit"))

    @http_put_response_hop_limit.setter
    def http_put_response_hop_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55c0a7b0916f5263ad5d7690976f961bc55a907b23181ba96381b8d18f673a78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpPutResponseHopLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpTokens")
    def http_tokens(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpTokens"))

    @http_tokens.setter
    def http_tokens(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc5e0c1ca17df8ed7c1fc42e744431f9a4ef75c6970c3990f6b5388e706ae71a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceMetadataTags")
    def instance_metadata_tags(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceMetadataTags"))

    @instance_metadata_tags.setter
    def instance_metadata_tags(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79373dfb9ed72e997450ac601b6238aef14820e23416a2c9300df5fc65f2dd7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceMetadataTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedInstanceAwsMetadataOptions]:
        return typing.cast(typing.Optional[ManagedInstanceAwsMetadataOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedInstanceAwsMetadataOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d628f222efc3d398522755a763adc61bcef510bb7d5c800e28db633edfa8b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsNetworkInterface",
    jsii_struct_bases=[],
    name_mapping={
        "device_index": "deviceIndex",
        "associate_ipv6_address": "associateIpv6Address",
        "associate_public_ip_address": "associatePublicIpAddress",
    },
)
class ManagedInstanceAwsNetworkInterface:
    def __init__(
        self,
        *,
        device_index: builtins.str,
        associate_ipv6_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        associate_public_ip_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param device_index: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#device_index ManagedInstanceAws#device_index}.
        :param associate_ipv6_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#associate_ipv6_address ManagedInstanceAws#associate_ipv6_address}.
        :param associate_public_ip_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#associate_public_ip_address ManagedInstanceAws#associate_public_ip_address}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cde21136cfa0572ea793e9f4c1cf18a987d4866cd97696a7953178c5796c8994)
            check_type(argname="argument device_index", value=device_index, expected_type=type_hints["device_index"])
            check_type(argname="argument associate_ipv6_address", value=associate_ipv6_address, expected_type=type_hints["associate_ipv6_address"])
            check_type(argname="argument associate_public_ip_address", value=associate_public_ip_address, expected_type=type_hints["associate_public_ip_address"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "device_index": device_index,
        }
        if associate_ipv6_address is not None:
            self._values["associate_ipv6_address"] = associate_ipv6_address
        if associate_public_ip_address is not None:
            self._values["associate_public_ip_address"] = associate_public_ip_address

    @builtins.property
    def device_index(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#device_index ManagedInstanceAws#device_index}.'''
        result = self._values.get("device_index")
        assert result is not None, "Required property 'device_index' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_ipv6_address(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#associate_ipv6_address ManagedInstanceAws#associate_ipv6_address}.'''
        result = self._values.get("associate_ipv6_address")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def associate_public_ip_address(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#associate_public_ip_address ManagedInstanceAws#associate_public_ip_address}.'''
        result = self._values.get("associate_public_ip_address")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsNetworkInterfaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsNetworkInterfaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__419b96b3a590c15febc753fff1984d4611c0a7e5e3a37b0ca4f1d93273de7728)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsNetworkInterfaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16355d14cf6bf3fa9963fc67c7272c61856413e73e7a1c6af0cb8215cd09c18d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsNetworkInterfaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4a1ca7ac547a950e1e12a0619141a41a2559c02a4ab5604a98892183cae6c99)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd863cc4e934a5ee98be564a173cfb9a1c10c4d72c72a19a7cee51767fc94b4e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9df74bca2e006dd24e9347c72fc102281f424caeaaa04546bf3e5a83f3270ec7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsNetworkInterface]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsNetworkInterface]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8e98a8d6a8601f046a2bf795eaff59a44d4f2e43afb864511420a8c4949813)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsNetworkInterfaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsNetworkInterfaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93a95baf27525513a2b5fc31df8f664d6a24a7e524c9903afe1217428609b472)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAssociateIpv6Address")
    def reset_associate_ipv6_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssociateIpv6Address", []))

    @jsii.member(jsii_name="resetAssociatePublicIpAddress")
    def reset_associate_public_ip_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssociatePublicIpAddress", []))

    @builtins.property
    @jsii.member(jsii_name="associateIpv6AddressInput")
    def associate_ipv6_address_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "associateIpv6AddressInput"))

    @builtins.property
    @jsii.member(jsii_name="associatePublicIpAddressInput")
    def associate_public_ip_address_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "associatePublicIpAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="deviceIndexInput")
    def device_index_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceIndexInput"))

    @builtins.property
    @jsii.member(jsii_name="associateIpv6Address")
    def associate_ipv6_address(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "associateIpv6Address"))

    @associate_ipv6_address.setter
    def associate_ipv6_address(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5308928c0a2a87303231ccaa4888b3efac80d3b7ddf7dab8ac407347f40721c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "associateIpv6Address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="associatePublicIpAddress")
    def associate_public_ip_address(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "associatePublicIpAddress"))

    @associate_public_ip_address.setter
    def associate_public_ip_address(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1b380a11ca73807a71cc75838a04dfb8234ff3925bf615e9bd86e912295a973)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "associatePublicIpAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deviceIndex")
    def device_index(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceIndex"))

    @device_index.setter
    def device_index(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c9e8ae912e2e9119570cff3ccbb9c050ae85be9d1b845151ef40986c6be6a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceIndex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsNetworkInterface]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsNetworkInterface]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsNetworkInterface]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ac154d1798635bc845a2a6fa42414dc23ac2e28caeb5b7872511e7beafccd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsResourceRequirements",
    jsii_struct_bases=[],
    name_mapping={
        "required_memory_maximum": "requiredMemoryMaximum",
        "required_memory_minimum": "requiredMemoryMinimum",
        "required_vcpu_maximum": "requiredVcpuMaximum",
        "required_vcpu_minimum": "requiredVcpuMinimum",
        "excluded_instance_families": "excludedInstanceFamilies",
        "excluded_instance_generations": "excludedInstanceGenerations",
        "excluded_instance_types": "excludedInstanceTypes",
        "required_gpu_maximum": "requiredGpuMaximum",
        "required_gpu_minimum": "requiredGpuMinimum",
    },
)
class ManagedInstanceAwsResourceRequirements:
    def __init__(
        self,
        *,
        required_memory_maximum: jsii.Number,
        required_memory_minimum: jsii.Number,
        required_vcpu_maximum: jsii.Number,
        required_vcpu_minimum: jsii.Number,
        excluded_instance_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_instance_generations: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_gpu_maximum: typing.Optional[jsii.Number] = None,
        required_gpu_minimum: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param required_memory_maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_memory_maximum ManagedInstanceAws#required_memory_maximum}.
        :param required_memory_minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_memory_minimum ManagedInstanceAws#required_memory_minimum}.
        :param required_vcpu_maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_vcpu_maximum ManagedInstanceAws#required_vcpu_maximum}.
        :param required_vcpu_minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_vcpu_minimum ManagedInstanceAws#required_vcpu_minimum}.
        :param excluded_instance_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#excluded_instance_families ManagedInstanceAws#excluded_instance_families}.
        :param excluded_instance_generations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#excluded_instance_generations ManagedInstanceAws#excluded_instance_generations}.
        :param excluded_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#excluded_instance_types ManagedInstanceAws#excluded_instance_types}.
        :param required_gpu_maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_gpu_maximum ManagedInstanceAws#required_gpu_maximum}.
        :param required_gpu_minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_gpu_minimum ManagedInstanceAws#required_gpu_minimum}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e14128cc8926eab2df519d163f2fe6fb0aa980cb9584a01555f2b238d69d8f2b)
            check_type(argname="argument required_memory_maximum", value=required_memory_maximum, expected_type=type_hints["required_memory_maximum"])
            check_type(argname="argument required_memory_minimum", value=required_memory_minimum, expected_type=type_hints["required_memory_minimum"])
            check_type(argname="argument required_vcpu_maximum", value=required_vcpu_maximum, expected_type=type_hints["required_vcpu_maximum"])
            check_type(argname="argument required_vcpu_minimum", value=required_vcpu_minimum, expected_type=type_hints["required_vcpu_minimum"])
            check_type(argname="argument excluded_instance_families", value=excluded_instance_families, expected_type=type_hints["excluded_instance_families"])
            check_type(argname="argument excluded_instance_generations", value=excluded_instance_generations, expected_type=type_hints["excluded_instance_generations"])
            check_type(argname="argument excluded_instance_types", value=excluded_instance_types, expected_type=type_hints["excluded_instance_types"])
            check_type(argname="argument required_gpu_maximum", value=required_gpu_maximum, expected_type=type_hints["required_gpu_maximum"])
            check_type(argname="argument required_gpu_minimum", value=required_gpu_minimum, expected_type=type_hints["required_gpu_minimum"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "required_memory_maximum": required_memory_maximum,
            "required_memory_minimum": required_memory_minimum,
            "required_vcpu_maximum": required_vcpu_maximum,
            "required_vcpu_minimum": required_vcpu_minimum,
        }
        if excluded_instance_families is not None:
            self._values["excluded_instance_families"] = excluded_instance_families
        if excluded_instance_generations is not None:
            self._values["excluded_instance_generations"] = excluded_instance_generations
        if excluded_instance_types is not None:
            self._values["excluded_instance_types"] = excluded_instance_types
        if required_gpu_maximum is not None:
            self._values["required_gpu_maximum"] = required_gpu_maximum
        if required_gpu_minimum is not None:
            self._values["required_gpu_minimum"] = required_gpu_minimum

    @builtins.property
    def required_memory_maximum(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_memory_maximum ManagedInstanceAws#required_memory_maximum}.'''
        result = self._values.get("required_memory_maximum")
        assert result is not None, "Required property 'required_memory_maximum' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def required_memory_minimum(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_memory_minimum ManagedInstanceAws#required_memory_minimum}.'''
        result = self._values.get("required_memory_minimum")
        assert result is not None, "Required property 'required_memory_minimum' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def required_vcpu_maximum(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_vcpu_maximum ManagedInstanceAws#required_vcpu_maximum}.'''
        result = self._values.get("required_vcpu_maximum")
        assert result is not None, "Required property 'required_vcpu_maximum' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def required_vcpu_minimum(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_vcpu_minimum ManagedInstanceAws#required_vcpu_minimum}.'''
        result = self._values.get("required_vcpu_minimum")
        assert result is not None, "Required property 'required_vcpu_minimum' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def excluded_instance_families(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#excluded_instance_families ManagedInstanceAws#excluded_instance_families}.'''
        result = self._values.get("excluded_instance_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_instance_generations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#excluded_instance_generations ManagedInstanceAws#excluded_instance_generations}.'''
        result = self._values.get("excluded_instance_generations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#excluded_instance_types ManagedInstanceAws#excluded_instance_types}.'''
        result = self._values.get("excluded_instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def required_gpu_maximum(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_gpu_maximum ManagedInstanceAws#required_gpu_maximum}.'''
        result = self._values.get("required_gpu_maximum")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def required_gpu_minimum(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#required_gpu_minimum ManagedInstanceAws#required_gpu_minimum}.'''
        result = self._values.get("required_gpu_minimum")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsResourceRequirements(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsResourceRequirementsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsResourceRequirementsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7d9c9d0213c23e844bc15611fbdc5afdb5d2bfc87660427c0cdcced8f622529)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsResourceRequirementsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9afb0885648f5e85c72c6d02045e66efd9303381c428c9bf15701dedec55c13)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsResourceRequirementsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a111816b9f15e86fbeadcae8eb859f414484ec5a1ce431d428699d938c63adbb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0913aea64fe1af6ba6689bba7c4c60a6974ac623e5db878b68f592a77348a8d8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aab21a8b4f7f537fcf9d1430438d225f8f974f3e6ed8974227749f1c3f6da6d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceRequirements]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceRequirements]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceRequirements]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ca42801693ace5c76de4107fe360a01876130a12d2968e949e63e25d5cfb34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsResourceRequirementsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsResourceRequirementsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__140069ae5389c5c972aeb132f79618a4f1ab9d6cbd649da34f60979977569339)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetExcludedInstanceFamilies")
    def reset_excluded_instance_families(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedInstanceFamilies", []))

    @jsii.member(jsii_name="resetExcludedInstanceGenerations")
    def reset_excluded_instance_generations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedInstanceGenerations", []))

    @jsii.member(jsii_name="resetExcludedInstanceTypes")
    def reset_excluded_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedInstanceTypes", []))

    @jsii.member(jsii_name="resetRequiredGpuMaximum")
    def reset_required_gpu_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredGpuMaximum", []))

    @jsii.member(jsii_name="resetRequiredGpuMinimum")
    def reset_required_gpu_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredGpuMinimum", []))

    @builtins.property
    @jsii.member(jsii_name="excludedInstanceFamiliesInput")
    def excluded_instance_families_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedInstanceFamiliesInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedInstanceGenerationsInput")
    def excluded_instance_generations_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedInstanceGenerationsInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedInstanceTypesInput")
    def excluded_instance_types_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedInstanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredGpuMaximumInput")
    def required_gpu_maximum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requiredGpuMaximumInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredGpuMinimumInput")
    def required_gpu_minimum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requiredGpuMinimumInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredMemoryMaximumInput")
    def required_memory_maximum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requiredMemoryMaximumInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredMemoryMinimumInput")
    def required_memory_minimum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requiredMemoryMinimumInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredVcpuMaximumInput")
    def required_vcpu_maximum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requiredVcpuMaximumInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredVcpuMinimumInput")
    def required_vcpu_minimum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requiredVcpuMinimumInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedInstanceFamilies")
    def excluded_instance_families(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedInstanceFamilies"))

    @excluded_instance_families.setter
    def excluded_instance_families(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5857e1d151877c27c06b275ccaf27e3ac0d71fce64ac31717b8ce7f645df9820)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedInstanceFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedInstanceGenerations")
    def excluded_instance_generations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedInstanceGenerations"))

    @excluded_instance_generations.setter
    def excluded_instance_generations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7cecc6f9663efa9f61a8c4adc44691ccfc29c7903d1e6fa942812e9e49c9306)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedInstanceGenerations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedInstanceTypes")
    def excluded_instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedInstanceTypes"))

    @excluded_instance_types.setter
    def excluded_instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67bc9679432f513948cb7f1905ca64e0c33ae6f48aa0f54c5d61c9e9a1c79103)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedInstanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredGpuMaximum")
    def required_gpu_maximum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requiredGpuMaximum"))

    @required_gpu_maximum.setter
    def required_gpu_maximum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__439fd2741114987c9248857f6f23a0502cb52424ed59330ecb1c9e5274dac138)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredGpuMaximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredGpuMinimum")
    def required_gpu_minimum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requiredGpuMinimum"))

    @required_gpu_minimum.setter
    def required_gpu_minimum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81bc465d5d0fc714b0ab9587aaf7740e8d45c27074d931c94fccb5157b491d30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredGpuMinimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredMemoryMaximum")
    def required_memory_maximum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requiredMemoryMaximum"))

    @required_memory_maximum.setter
    def required_memory_maximum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b297ad92be27e01537cd37e1f21aaba6069b53aad4f4bb430d142d4a48c8146)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredMemoryMaximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredMemoryMinimum")
    def required_memory_minimum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requiredMemoryMinimum"))

    @required_memory_minimum.setter
    def required_memory_minimum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d414163d2332e2fe129c1f00e0e0cf76ed54392f1253d6331cfbcf42a394b8e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredMemoryMinimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredVcpuMaximum")
    def required_vcpu_maximum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requiredVcpuMaximum"))

    @required_vcpu_maximum.setter
    def required_vcpu_maximum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__423f75e4c463c510076288171e9b554057cfa20af4548657a62f4b44f921239c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredVcpuMaximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredVcpuMinimum")
    def required_vcpu_minimum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requiredVcpuMinimum"))

    @required_vcpu_minimum.setter
    def required_vcpu_minimum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5430e457b5f548db908c099a4979cd0f2d6ebad5c6b7ce07060e5d7db64521d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredVcpuMinimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceRequirements]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceRequirements]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceRequirements]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__746d6cd3e36f1310e9292fb420f1d3c765a99a5c9660e81d4ccfca4eb1d74a36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsResourceTagSpecification",
    jsii_struct_bases=[],
    name_mapping={
        "should_tag_amis": "shouldTagAmis",
        "should_tag_enis": "shouldTagEnis",
        "should_tag_snapshots": "shouldTagSnapshots",
        "should_tag_volumes": "shouldTagVolumes",
    },
)
class ManagedInstanceAwsResourceTagSpecification:
    def __init__(
        self,
        *,
        should_tag_amis: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_tag_enis: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_tag_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_tag_volumes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param should_tag_amis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_amis ManagedInstanceAws#should_tag_amis}.
        :param should_tag_enis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_enis ManagedInstanceAws#should_tag_enis}.
        :param should_tag_snapshots: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_snapshots ManagedInstanceAws#should_tag_snapshots}.
        :param should_tag_volumes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_volumes ManagedInstanceAws#should_tag_volumes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a79979b3adb0bb1947ab2e8a7e45bfa4e891b34d54edaabd059e55aed615f897)
            check_type(argname="argument should_tag_amis", value=should_tag_amis, expected_type=type_hints["should_tag_amis"])
            check_type(argname="argument should_tag_enis", value=should_tag_enis, expected_type=type_hints["should_tag_enis"])
            check_type(argname="argument should_tag_snapshots", value=should_tag_snapshots, expected_type=type_hints["should_tag_snapshots"])
            check_type(argname="argument should_tag_volumes", value=should_tag_volumes, expected_type=type_hints["should_tag_volumes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if should_tag_amis is not None:
            self._values["should_tag_amis"] = should_tag_amis
        if should_tag_enis is not None:
            self._values["should_tag_enis"] = should_tag_enis
        if should_tag_snapshots is not None:
            self._values["should_tag_snapshots"] = should_tag_snapshots
        if should_tag_volumes is not None:
            self._values["should_tag_volumes"] = should_tag_volumes

    @builtins.property
    def should_tag_amis(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_amis ManagedInstanceAws#should_tag_amis}.'''
        result = self._values.get("should_tag_amis")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_tag_enis(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_enis ManagedInstanceAws#should_tag_enis}.'''
        result = self._values.get("should_tag_enis")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_tag_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_snapshots ManagedInstanceAws#should_tag_snapshots}.'''
        result = self._values.get("should_tag_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_tag_volumes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#should_tag_volumes ManagedInstanceAws#should_tag_volumes}.'''
        result = self._values.get("should_tag_volumes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsResourceTagSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsResourceTagSpecificationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsResourceTagSpecificationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd14136bb8f407c55ff3e179a460d2641492a7727b4283f065be0029304e0698)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsResourceTagSpecificationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20f7b719852be16360ede8c713e76dbf63e689df0f5e513c99a9e3ddc9639e0e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsResourceTagSpecificationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1788e037dd4711c1f7fe603de9c6af1393a173a47d1b4c9797abc4085f13c6d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e7fa9204d89411d527faac7d71bf6b8ac39680bd7032553b7a248407c8a6ce7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__840cff6c615eb39217ced5bab2b3f8b13f3aa3ec2e94ac593561c45ebe6109fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceTagSpecification]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceTagSpecification]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceTagSpecification]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62d7a5cb7b31ce14697b8a59d2cbee0dfd134b050d03054c757e81bc4f1faf9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsResourceTagSpecificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsResourceTagSpecificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a69870c96486a44227605efb64725a27b2b2331dc841f37837ffa37ac7caaf8b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetShouldTagAmis")
    def reset_should_tag_amis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldTagAmis", []))

    @jsii.member(jsii_name="resetShouldTagEnis")
    def reset_should_tag_enis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldTagEnis", []))

    @jsii.member(jsii_name="resetShouldTagSnapshots")
    def reset_should_tag_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldTagSnapshots", []))

    @jsii.member(jsii_name="resetShouldTagVolumes")
    def reset_should_tag_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldTagVolumes", []))

    @builtins.property
    @jsii.member(jsii_name="shouldTagAmisInput")
    def should_tag_amis_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldTagAmisInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldTagEnisInput")
    def should_tag_enis_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldTagEnisInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldTagSnapshotsInput")
    def should_tag_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldTagSnapshotsInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldTagVolumesInput")
    def should_tag_volumes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldTagVolumesInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldTagAmis")
    def should_tag_amis(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldTagAmis"))

    @should_tag_amis.setter
    def should_tag_amis(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76ddffd389f64e0235cced29d14340ea7b086974a7c59935f2d8806d16bf1b13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldTagAmis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldTagEnis")
    def should_tag_enis(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldTagEnis"))

    @should_tag_enis.setter
    def should_tag_enis(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d5a1b273d0bcbece1cace62c925fa337a7ef7672c70ffd591693364c2023cf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldTagEnis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldTagSnapshots")
    def should_tag_snapshots(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldTagSnapshots"))

    @should_tag_snapshots.setter
    def should_tag_snapshots(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e01031bf81264e1a74e70f10dbb2fcaf866d75804545f7efc2287c7e85cab77b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldTagSnapshots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldTagVolumes")
    def should_tag_volumes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldTagVolumes"))

    @should_tag_volumes.setter
    def should_tag_volumes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43ad4cac60f64218d75734daf3fdbc6192133e62526356e3e9fb0440ff87e250)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldTagVolumes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceTagSpecification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceTagSpecification]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceTagSpecification]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90d41ce51850e1ae6d64a8a2178b3a38523123657af7028d430f39c96ed8fce5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsRevertToSpot",
    jsii_struct_bases=[],
    name_mapping={"perform_at": "performAt"},
)
class ManagedInstanceAwsRevertToSpot:
    def __init__(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#perform_at ManagedInstanceAws#perform_at}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f3777d0973a56f2d2cf3fb8f29b353241dc348847aa98f3aed26c6d0318f247)
            check_type(argname="argument perform_at", value=perform_at, expected_type=type_hints["perform_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "perform_at": perform_at,
        }

    @builtins.property
    def perform_at(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#perform_at ManagedInstanceAws#perform_at}.'''
        result = self._values.get("perform_at")
        assert result is not None, "Required property 'perform_at' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsRevertToSpot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsRevertToSpotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsRevertToSpotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1eead1d1e5430c324b3acfaf3ed0c217beb1a1a6b4a44c0946f5518cc78ab62d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4395db6acc56dd620d18406a3c13b700c1c5cf04492fd2986e343dfdd69ae52a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ManagedInstanceAwsRevertToSpot]:
        return typing.cast(typing.Optional[ManagedInstanceAwsRevertToSpot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ManagedInstanceAwsRevertToSpot],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e88f49582500216398ed3284f9c1fbdca5dfc412373e32fafbbeb4471e367f6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsScheduledTask",
    jsii_struct_bases=[],
    name_mapping={
        "task_type": "taskType",
        "cron_expression": "cronExpression",
        "frequency": "frequency",
        "is_enabled": "isEnabled",
        "start_time": "startTime",
    },
)
class ManagedInstanceAwsScheduledTask:
    def __init__(
        self,
        *,
        task_type: builtins.str,
        cron_expression: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        start_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#task_type ManagedInstanceAws#task_type}.
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#cron_expression ManagedInstanceAws#cron_expression}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#frequency ManagedInstanceAws#frequency}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#is_enabled ManagedInstanceAws#is_enabled}.
        :param start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#start_time ManagedInstanceAws#start_time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bed4c15a9144580093505d7280d8fd48e6cee93f771e8e1943f78d0218bbce6)
            check_type(argname="argument task_type", value=task_type, expected_type=type_hints["task_type"])
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument frequency", value=frequency, expected_type=type_hints["frequency"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "task_type": task_type,
        }
        if cron_expression is not None:
            self._values["cron_expression"] = cron_expression
        if frequency is not None:
            self._values["frequency"] = frequency
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if start_time is not None:
            self._values["start_time"] = start_time

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#task_type ManagedInstanceAws#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cron_expression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#cron_expression ManagedInstanceAws#cron_expression}.'''
        result = self._values.get("cron_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#frequency ManagedInstanceAws#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#is_enabled ManagedInstanceAws#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#start_time ManagedInstanceAws#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsScheduledTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsScheduledTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsScheduledTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__923d0b611823251dbccabef4346181187f94391f0fc3f4e04e92f25a466cf947)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ManagedInstanceAwsScheduledTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__823e38c8ec02eb165b3b4a62fe3d30e5207581741815420f5b21e3d78a6b9a60)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsScheduledTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__004d9c87eca1043a00c3c0d0b10602b477d962c2e789206b05ea857783a36584)
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
            type_hints = typing.get_type_hints(_typecheckingstub__39ff1cc784adb6b6684b32a211ec2c3892791997c2cabb969b7271e59537060b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18bb9599b31272748bf3361f4ec49b430e9e18959705158a0f8cac994f77338d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsScheduledTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsScheduledTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsScheduledTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a24e4af8c387dd58b80cbdc97cfac5664129efefd326b8ef6bf2099dc64f5e94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsScheduledTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsScheduledTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__413bb0d8f08c64aa2156acea1eaa861dd5b63197c6dc8acda15bdd167acf8cf0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCronExpression")
    def reset_cron_expression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCronExpression", []))

    @jsii.member(jsii_name="resetFrequency")
    def reset_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequency", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetStartTime")
    def reset_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTime", []))

    @builtins.property
    @jsii.member(jsii_name="cronExpressionInput")
    def cron_expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronExpressionInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startTimeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__d83ed7be73fa3fe1422c9487a08c6411097217afd4eafd80ebdad658c02eead7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cronExpression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c443f1778e6e0b5a86766eec9db7b9434132692f955c3a1e529f79a4fbddad45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__17e69301c8a31658f933b52a60fb610fd7daab9273aeebdb59a0adee4efc8ad1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffd79f2ded6f5fd3551277afb01462eaa1ae61a525777c5fb26565a1e5a54915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__289b7856ac1694e2c6b82c482cbb6391706f7965508f8ecd949c315c1c0aa520)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsScheduledTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsScheduledTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsScheduledTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f03e686bbd915fd46efdb54ca69f1009a4220b6f5b0fcd6d3c2d63f64524bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ManagedInstanceAwsTags:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#key ManagedInstanceAws#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#value ManagedInstanceAws#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__836286d24c53126d41954cdd2a2f80edda21e8739339c0bdfdf0890868439a3f)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#key ManagedInstanceAws#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/managed_instance_aws#value ManagedInstanceAws#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedInstanceAwsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManagedInstanceAwsTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7ca332d5aebd24ef3e1ff990661fed87f60fdaf60e42db70345b8f34292baa9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ManagedInstanceAwsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab3b8daa64e91a185ee83f0133a5046ecf33c0efaf2e2f3b58bd2e6d28602689)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ManagedInstanceAwsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a78d2cce4afc6e06a5536995a68b0c8f2c0b1216669bb484d828487ce1c6ec7a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__52a4f56c3f9fcbbe88347669ad6e90ab622e900a387e077a03623b3553579136)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fed3e1fe6f846e6819e4e99902cd8c8c7126456c0ef21654068a3af4064fdf58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58544591d3043d44dc77f27ee59874e98331c9af898cfb98db3c0bc9a2de9182)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ManagedInstanceAwsTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.managedInstanceAws.ManagedInstanceAwsTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db86f1d0f29a618e3447c2d80839381284802e37cdebd71b436fbf284ecb0a6f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__9703dea10d0dc383a8a3c4a2399c84590e73df7ef319c4bea27a8f4a9cea76a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b01fe303f0ed82a4cbd6bf684fddb507d2954cb9558ffdddc35d27ce5f3a352)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__496214941afaa7079d415f8e1df259700bf8f6b8a575fafd2d82c1869680a05d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ManagedInstanceAws",
    "ManagedInstanceAwsBlockDeviceMappings",
    "ManagedInstanceAwsBlockDeviceMappingsEbs",
    "ManagedInstanceAwsBlockDeviceMappingsEbsOutputReference",
    "ManagedInstanceAwsBlockDeviceMappingsList",
    "ManagedInstanceAwsBlockDeviceMappingsOutputReference",
    "ManagedInstanceAwsConfig",
    "ManagedInstanceAwsDelete",
    "ManagedInstanceAwsDeleteList",
    "ManagedInstanceAwsDeleteOutputReference",
    "ManagedInstanceAwsIntegrationRoute53",
    "ManagedInstanceAwsIntegrationRoute53Domains",
    "ManagedInstanceAwsIntegrationRoute53DomainsList",
    "ManagedInstanceAwsIntegrationRoute53DomainsOutputReference",
    "ManagedInstanceAwsIntegrationRoute53DomainsRecordSets",
    "ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsList",
    "ManagedInstanceAwsIntegrationRoute53DomainsRecordSetsOutputReference",
    "ManagedInstanceAwsIntegrationRoute53OutputReference",
    "ManagedInstanceAwsLoadBalancers",
    "ManagedInstanceAwsLoadBalancersList",
    "ManagedInstanceAwsLoadBalancersOutputReference",
    "ManagedInstanceAwsManagedInstanceAction",
    "ManagedInstanceAwsManagedInstanceActionOutputReference",
    "ManagedInstanceAwsMetadataOptions",
    "ManagedInstanceAwsMetadataOptionsOutputReference",
    "ManagedInstanceAwsNetworkInterface",
    "ManagedInstanceAwsNetworkInterfaceList",
    "ManagedInstanceAwsNetworkInterfaceOutputReference",
    "ManagedInstanceAwsResourceRequirements",
    "ManagedInstanceAwsResourceRequirementsList",
    "ManagedInstanceAwsResourceRequirementsOutputReference",
    "ManagedInstanceAwsResourceTagSpecification",
    "ManagedInstanceAwsResourceTagSpecificationList",
    "ManagedInstanceAwsResourceTagSpecificationOutputReference",
    "ManagedInstanceAwsRevertToSpot",
    "ManagedInstanceAwsRevertToSpotOutputReference",
    "ManagedInstanceAwsScheduledTask",
    "ManagedInstanceAwsScheduledTaskList",
    "ManagedInstanceAwsScheduledTaskOutputReference",
    "ManagedInstanceAwsTags",
    "ManagedInstanceAwsTagsList",
    "ManagedInstanceAwsTagsOutputReference",
]

publication.publish()

def _typecheckingstub__7dd494a633a7ceac821a993cc45f1e29b839cb1d25c83da8b4e13a965b643844(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    image_id: builtins.str,
    name: builtins.str,
    persist_block_devices: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    product: builtins.str,
    subnet_ids: typing.Sequence[builtins.str],
    vpc_id: builtins.str,
    auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    block_devices_mode: typing.Optional[builtins.str] = None,
    cpu_credits: typing.Optional[builtins.str] = None,
    delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsDelete, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    elastic_ip: typing.Optional[builtins.str] = None,
    enable_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    grace_period: typing.Optional[jsii.Number] = None,
    health_check_type: typing.Optional[builtins.str] = None,
    iam_instance_profile: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    integration_route53: typing.Optional[typing.Union[ManagedInstanceAwsIntegrationRoute53, typing.Dict[builtins.str, typing.Any]]] = None,
    key_pair: typing.Optional[builtins.str] = None,
    life_cycle: typing.Optional[builtins.str] = None,
    load_balancers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsLoadBalancers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    managed_instance_action: typing.Optional[typing.Union[ManagedInstanceAwsManagedInstanceAction, typing.Dict[builtins.str, typing.Any]]] = None,
    metadata_options: typing.Optional[typing.Union[ManagedInstanceAwsMetadataOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    minimum_instance_lifetime: typing.Optional[jsii.Number] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    orientation: typing.Optional[builtins.str] = None,
    persist_private_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    persist_root_device: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    placement_tenancy: typing.Optional[builtins.str] = None,
    preferred_type: typing.Optional[builtins.str] = None,
    preferred_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    private_ip: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    resource_requirements: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsResourceRequirements, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resource_tag_specification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsResourceTagSpecification, typing.Dict[builtins.str, typing.Any]]]]] = None,
    revert_to_spot: typing.Optional[typing.Union[ManagedInstanceAwsRevertToSpot, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    unhealthy_duration: typing.Optional[jsii.Number] = None,
    user_data: typing.Optional[builtins.str] = None,
    utilize_reserved_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__a3c22ce2ebd6e770a5827d0eeb47aa2ae3614794c73eea0d55dae8c004c605f2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e72b566bed9b7a5d9a240db42bf26739612f083fce4585539c199ccbedbaf2de(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b13c93ee49ba7171ffee2e5856ae8fb18a47b40acf4d4300003156b5b4f1abfb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsDelete, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bcf9bddb5e8cb82f18176f252d5a1cdad9e1166a3b8d47cb611ebf7b0669f4b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsLoadBalancers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75505da419c8b7de79986b6f7b186f4f35f78b829dc9d722ed98b3ab73ecef84(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ccc93729045078eb5279cb66dff489645f3f75c4217b6fefd71468138bec08c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsResourceRequirements, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9683a13b9e3c0af4296f92caa767b80bc6782a81cde8a9c45e3c6b730686230(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsResourceTagSpecification, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff3d519f90a37db11ea82adeb0cdf0881744a918bdea189d4401b28632c3db8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsScheduledTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0963aa412aba89a40c32b158ddd032b5bbb4075e1062c9faeb2955b5c37df47f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04a781057e3a32b5d00150c1129e15ba2384dfba806932826f1d2d7ab2e9590f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d2964032101f083cf00a1eaa3cb492485d674c34db4ce12584220aeee95092(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f606e5635f0d083026cdcfa5054b134cdc177ab31fc81217a8399d2c79575ab9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f02700b16b84afb5fff343e0607b7b149e4cd4f1152e86c8ff62b974b57bf17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6cb6d4232e13b69ae09d52bd80cf5546d67395334038112c81559f4f137e32(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7397075afb1c0ce27a2c5e443ccccf130b53be9a692ddcaf289e3da10f8fa810(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae0fbe41da4b27e1416d05ea8a05aa92300f9b05a497922021c2865c00725ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d34113b3b6c156c7737d1e949fa1c97e99fb0655d4122baf2ef2e1e16391d8ed(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b9c3189a84768499eedb3f282438b6d3feef21cd6eb836449c7f536a0d5e95e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed7636167a355fe7d926e089a6c3bf6f97e0eeb098ae667069d9bd32c9fe6ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c29b52d7c7011f1b87adf4e01db046e737a04c5c15314e64f3628fd3c7aaa4f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac744f7df00676696bc59055d083f9c1064b3045b1ce5c45a2aa4cf2aeb23b41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c6ab7ed22aa50ebf56be66c01c32ff6117b77f3ae350e67e2318a73b18520f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d6bcde336e49b6dffd7ec5e01fb1dc94ef70735362c644f1eb78f06f9031ff0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dffd8405f08256d8858d25f4f66bf2874e9b203535e79799b547b443adb66a4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19ca56727e7a953c6172e34a37b3bae34001a72dc283fa4eb9bfa785eca6165f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64d11132e8f38ba6018f81568901673bd7f9812f3126eda8151a26b0a5a35463(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c7f1cabb0bd0f02f40495d129f3f238eaddac108b6fb090927dd0383a53cc48(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__591f3cba0d0490b682600ea4f7aab2896f3c739e17051bc5de3499f7b0794ff1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef1a8d1fca6ae46ffb5f4b68c4bf1beba73b92baa983bf67bd6dddb2c1a9344c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d491f830c4aa0aebdb255add9cd7fd86fd3d0a7d3486c419742ee88a29c4e10f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa6a7df29e14d1bbde8dbd1c65d762dc33f39a379a729d529cfa8091d55359fb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc4fce33a709d2b3e15ce13398455db06d0300c14aa74de7c3921dcd06be8b02(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b39bc58974218ae27464c17fb723454f6fb3f5ab22f2bb8de363acbe62a66b2e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38d07f93be959f2387546c9f84582bfc88d923a8b73d31cf42f7acc7952e6df4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bf5e68b667557996caafbc68e823644a79f8f02c118ee62aaddd90065ebd55a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73994828814a53bc5a6e9fe038525230f28b0e1538bfdbdb506708270977de8c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__493eec15205c84170ff373fb79dc0a1324a45300165e52c373632e3d8da9dc8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94b943c6617c61ace521bb99f367edf0a2fb419a0d7447cd6cc768a2b47fdd3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48cac7a15c882a00cab83d60c1e9d63add9edf7ff1199837bb276c9dc6e8c4e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5635ddde46b53305af436ad446b89d2328e09b250b609e327fee4583274b4bbe(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84caf0170ee1fba82c4fab7153f6e5e6fa63e6cdfd1db2693c68c910dc5f1b04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48b5295d173ca7e102bb64b922bc70dcefb7b758a6ac790bfa0148942f1ce747(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c1d00e5637fb87ff90152e1f86b3a7005d978fff3fdab3494fd0a73be97c152(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0390ab643fc27fe1b3913a8b6c38534f57c59f1902aefd04500d92d05c978e0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4423ba197d14ab977ab02afb996798016394318870738de1be6d92c14224474(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0114dea09597e84259d0fe0f705cd1cd03dadcfca8f9d779a752c7689a881b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e600339887f464ecb1f136bc5b6a47ada2dbbf2a322d473b1869a17bc406db(
    *,
    device_name: builtins.str,
    ebs: typing.Optional[typing.Union[ManagedInstanceAwsBlockDeviceMappingsEbs, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c22e309111a431f89f1e6603ca53df6d5ad8f2c89579ec61b4bdb16c48993e9(
    *,
    delete_on_termination: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encrypted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    iops: typing.Optional[jsii.Number] = None,
    kms_key_id: typing.Optional[builtins.str] = None,
    snapshot_id: typing.Optional[builtins.str] = None,
    throughput: typing.Optional[jsii.Number] = None,
    volume_size: typing.Optional[jsii.Number] = None,
    volume_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2904041a84091084359772bd40c785895cd6a4f7adef0fe0a6e4a43eeff58f00(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90c1b7ed7bea68dc5864bc68558fbc2a73cabcdabcc160e0f9964b22869f3486(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7e3c0564cabd0875745d544b643e169591f2910e8d89cf6adad416d703e8d0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57dfd852d96dfae1182a1cfed145706bc2cba2287feb4f91f33a4a7046ef3aee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8b17c792fff8fe4b73bb94d67eaddf3e96a3f4905a4c9776c1984d0b055d360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f12436c74bb76c4b86f57ac486691cde95738701d83bf5e5b0d862a165deb602(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58fb4514ac8173d3776507dc57492f5b04267b4d57c8ed3edba833b6b1270b04(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b78c950d8c518add70189e7606f83d93bcc56722944d5595f14ec2903c7c29a6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3bfa15ca7635a958f795c9603a4a27e6f05227cf08241444abd96d360a49369(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4da7834b79f5befd97cc7e10582acef074ea76e2296276a61bd833047a8196df(
    value: typing.Optional[ManagedInstanceAwsBlockDeviceMappingsEbs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__861422ac3892b6839fc6ba9af502b21bec982ff0e12c7a5030ec623f2783d673(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5885b2888d14ed49f69dfcf6ad943b999c7dd4fc33c2f668a9530887c28e91df(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__558a061178ea2bc3be1d8a9a5b7e15ab45891751bd4dc49d61f172f763edf008(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dfb9f1edc0554842145899aebeeb26b57ffc858f9b1a13884beae4081bae86d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__372fe474fa857e81a9f29b2eb0e25071c9fe33b9547a947c084697e47b6108c8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57448ae7d5553aee7097e0410c0b8938370ef86360e904fddd1c3f2128c91d0b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsBlockDeviceMappings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b74e606536529c4487b7c2d4d4a8402c64441d5d9c6a534ed2d4807b42a87185(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d039306a1614b3cb5c12fbd967f8c9a5954040d251d5577d109385732481a994(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cda87cf46dce89bf8feede03743f157e49634d44b5b306040673cc4a44c3b3b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsBlockDeviceMappings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63caced62e9bceb84b90844c047b52505419e102f6dafea560f9879a213d651a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    image_id: builtins.str,
    name: builtins.str,
    persist_block_devices: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    product: builtins.str,
    subnet_ids: typing.Sequence[builtins.str],
    vpc_id: builtins.str,
    auto_healing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    block_devices_mode: typing.Optional[builtins.str] = None,
    cpu_credits: typing.Optional[builtins.str] = None,
    delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsDelete, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    elastic_ip: typing.Optional[builtins.str] = None,
    enable_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    fallback_to_ondemand: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    grace_period: typing.Optional[jsii.Number] = None,
    health_check_type: typing.Optional[builtins.str] = None,
    iam_instance_profile: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    integration_route53: typing.Optional[typing.Union[ManagedInstanceAwsIntegrationRoute53, typing.Dict[builtins.str, typing.Any]]] = None,
    key_pair: typing.Optional[builtins.str] = None,
    life_cycle: typing.Optional[builtins.str] = None,
    load_balancers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsLoadBalancers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    managed_instance_action: typing.Optional[typing.Union[ManagedInstanceAwsManagedInstanceAction, typing.Dict[builtins.str, typing.Any]]] = None,
    metadata_options: typing.Optional[typing.Union[ManagedInstanceAwsMetadataOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    minimum_instance_lifetime: typing.Optional[jsii.Number] = None,
    network_interface: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsNetworkInterface, typing.Dict[builtins.str, typing.Any]]]]] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    orientation: typing.Optional[builtins.str] = None,
    persist_private_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    persist_root_device: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    placement_tenancy: typing.Optional[builtins.str] = None,
    preferred_type: typing.Optional[builtins.str] = None,
    preferred_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    private_ip: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    resource_requirements: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsResourceRequirements, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resource_tag_specification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsResourceTagSpecification, typing.Dict[builtins.str, typing.Any]]]]] = None,
    revert_to_spot: typing.Optional[typing.Union[ManagedInstanceAwsRevertToSpot, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    unhealthy_duration: typing.Optional[jsii.Number] = None,
    user_data: typing.Optional[builtins.str] = None,
    utilize_reserved_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__022ac0d66f87c340124a259215cd2f7a5e24e66566a5a0c98beba6efde9ef0c5(
    *,
    ami_backup_should_delete_images: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deallocation_config_should_delete_images: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_delete_network_interfaces: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_delete_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_delete_volumes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_terminate_instance: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdb97bc6381095ba940fe057afe520d6aa06ddda0c3e662841a08850c1985b40(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb3c9587524c3ac2c5b8a4cff78f2ffcfbecfb329e6ec27b3228774e32999053(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__442d07121268197492d8ae3ea259b31364165d3f198edf910a49c2a4ac0eb7c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0ea742daeed84326cf459b25a4e1e1654c1cdc2e0a43341334d9c68ff2cc6e9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__556939914a8d8646ba355506c63038c54be1179199b9a7e2e94c2b9dcff457bf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__262dbebe75da1d6264906b59d3b6dcffe8bf7ca0cfb7f31dd39c17390beaa920(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsDelete]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deb5d4a14e5140f6188d1c8788f39e079974ee2d31298aa61f43e38a197c893e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__504e2fb25eb7e58d526da93350211644e180db5d9f7b888a79d8f87f7d466fe5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d916788d3adf21ae2f8416b72a0205571af51bc9a4366fc7536e8a456720e04(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa6eb9acd7a917b24fa1f7891074e32d075aa75470311d74db42ff6866132b6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__395a1901ddb9cd8e78f0a501d1620027aa2ddf1da2506dd5b7982faa6f1ec1b2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38d76753ab7c770445a2c42f1b882faec3bd3a647aa7a89e7dff3660e6b1ba63(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a8dfc41eded8e442db45211b1b689cca7a7408ba425c2e1153826079f6cc5e0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1208dd8082a574e665edea1166d1e31dd4d0c0224a02a4a57690eca61837a48f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsDelete]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c25e0e273c4f29573830d8a0d398673c2d7ce90264bea372786486f0f4e17c2d(
    *,
    domains: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsIntegrationRoute53Domains, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57e25eb73b780d9dd61fe1679f93281c1e00c5d3214c22d3f6a6bcdc3e544280(
    *,
    hosted_zone_id: builtins.str,
    record_sets: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsIntegrationRoute53DomainsRecordSets, typing.Dict[builtins.str, typing.Any]]]],
    record_set_type: typing.Optional[builtins.str] = None,
    spotinst_acct_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf8f3e31662feebf4f6c7b8782dad0ee800ce9ff95089815542e690b5a573c9b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78d040de36ea0c93f66df14775e45fdae26c1f33cf5667bef707e93affafe9a1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__867574bbfdd1b12bd1c1c78cea3b914116737ba42008140524676b5092b15c15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da4885368c73406eed7c22cbc1613a4a8a454216fafa3b33f2e301f3ccc3d5be(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5175c3d80efa9622a1e6ad953c8cc9d8233583d34641faf87b9a14356b50882(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a53d8e438c3c4b0fa40d24a0497df2bc33513013cc6eab43088668126213fc3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53Domains]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7decdf639cbc2be9d57d302b718113cebe5596e111b2246f3d74b9896da3c796(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f889c89e68a893e11e7e701f0e5382d6a1a6b4936dbbe170c5343cf343d5e980(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsIntegrationRoute53DomainsRecordSets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c21bc74c8677434cb19ff8d6078c09ba54d87fc25437cbe9dfdb371b751ec3fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f0dac342189559834682f8be30dbcd4c1cce7a4ebf3b1b6b28a1bfdd65262d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73bbfe36e8ce312cca92a53ce143bbeba56fd395c7e420e0ecbc70a30fcfe4ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a0daa75846de2044788f82b29b6e4f1f255203c56727db7490921bd8189886c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53Domains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__922e4f578391ecd0ffb09af07f46f88306f948f6dc1865f5367f9ff5c1765e99(
    *,
    name: builtins.str,
    use_public_dns: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26cc45b591fd16151c13ac2d0dccb2d78fdff830d7d953cde7d6a7e5b33cdcbd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c0763f0ca2be0cc1691511b621c836ab5f9c82773d2680e8bc069562067bfb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f896e1f2057633d841fd2c36f58ad8ff863b979c1f20b2a0993cdc739dc2b577(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b15a4a853c50254cc7e2dc855344ff88d5a17163ecfb8a42c5c1f818349e5720(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c210a2a38d0dca8c90dcd3ee07deac743fc92e3e62980accdb35e352036153(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11816d5225609931995aa6b657006e016d4f1497459fe3e7b825a2ac4c269429(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080f347e24ee3c2351a2bc9f412ac5c9557ed50ec13f5687bace095d569ea17f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd6f1e71908f2d70bd6a27234f54b282921256953e23916fa720ec150e9bdbdf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d4aaac6d0f6b73ea4905fbfd55d32bcefb0cd46237eec4071490393bc8cd36(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f3656ee701da9e226eea684161faff48856cd6646531b12db10b8fd7d8fb5d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a80a7ab434a9045c640819e18dc8b42c718b0a0b501551c934e8bac538174613(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsIntegrationRoute53DomainsRecordSets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d0fd0ff9a1ee6db32506e301c839e0fdefd874bb725047b2d8520ef47dd2c0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ff3e59cd59585804f1664c3b12b7cafe980a4ad7578e1b8b6c234a55bb87d28(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ManagedInstanceAwsIntegrationRoute53Domains, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eb9d58506668488d76ec77d3399a93503c9f13620ad3194c530372a8ddc1521(
    value: typing.Optional[ManagedInstanceAwsIntegrationRoute53],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07fcdbbc077261ce172d6dd3570cf414aa0014312e4b1ab9e56757212baeb52a(
    *,
    type: builtins.str,
    arn: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b0432368002e6f35cee94404c89ccb904d5d5978a93075ac433943a6943837f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9adc7d31a54a851e954f3dea3e619009f9bff58f1ac5300fc08db626fb80054c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efae4d6f8d17f1f1d7ddf644b8154f5a69fa2e4eab6ff96d526bddd00d3c112c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e0ccbc04742137a7a0a4b3ae3c4c7549865f5f9d142fd1fee37212d2ad9ed87(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f24acb5bdde6dd85aaec98e86a2251b53c41a6a59ca048794510ecbb41a9721(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8431e08fa7ecd960cd62824b7d39d47c2f1683ddeb10521649f25d846d66fc78(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsLoadBalancers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12a019489d725fb61f1ab76bbd7b0aaaa37111d82250e1f7dbc46271ac1a203c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7c107ac3ed937b38abb47b015f0ebea1a3f9488f99cae26c7e24f6bc626ecf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91aeb2cb7540c68d0aab12ebb813636124ec207d1173a0ce27798b36f36fe01c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efadfad04ee30e2037be3f272c1f24d4d3a131e0ce05b60d79b015756354f440(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15d08733bad001ee62091d5129bff77b29785a9e11539312ac61de105d4050ef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsLoadBalancers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90d5b22970c2aade4005dee48bf87929dc83e955ee3fa500207e99c6a6280d04(
    *,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4026826348548f0874191f4b28aaed0ef1e8db38ae02e1709e96dbbbfef5e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b28c006022d7da5a4d64170b05f6e15a7dfa24548b1e8bfcbc80ee48363a616f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a23df4573a2ba9eaad21144535d4c25363c2ed175fff4fde8af5e8ceef59179(
    value: typing.Optional[ManagedInstanceAwsManagedInstanceAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df459da1e581e1ed0946d26cdd848a7496b8ce3709633b6c6f0aae55ae59aa39(
    *,
    http_tokens: builtins.str,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    instance_metadata_tags: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eb3ed3306066eaae7a1de2dacb38a2b0078b15d20fae8cdfb4d2921aa46f912(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55c0a7b0916f5263ad5d7690976f961bc55a907b23181ba96381b8d18f673a78(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc5e0c1ca17df8ed7c1fc42e744431f9a4ef75c6970c3990f6b5388e706ae71a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79373dfb9ed72e997450ac601b6238aef14820e23416a2c9300df5fc65f2dd7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d628f222efc3d398522755a763adc61bcef510bb7d5c800e28db633edfa8b2(
    value: typing.Optional[ManagedInstanceAwsMetadataOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cde21136cfa0572ea793e9f4c1cf18a987d4866cd97696a7953178c5796c8994(
    *,
    device_index: builtins.str,
    associate_ipv6_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    associate_public_ip_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__419b96b3a590c15febc753fff1984d4611c0a7e5e3a37b0ca4f1d93273de7728(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16355d14cf6bf3fa9963fc67c7272c61856413e73e7a1c6af0cb8215cd09c18d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4a1ca7ac547a950e1e12a0619141a41a2559c02a4ab5604a98892183cae6c99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd863cc4e934a5ee98be564a173cfb9a1c10c4d72c72a19a7cee51767fc94b4e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9df74bca2e006dd24e9347c72fc102281f424caeaaa04546bf3e5a83f3270ec7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8e98a8d6a8601f046a2bf795eaff59a44d4f2e43afb864511420a8c4949813(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsNetworkInterface]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93a95baf27525513a2b5fc31df8f664d6a24a7e524c9903afe1217428609b472(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5308928c0a2a87303231ccaa4888b3efac80d3b7ddf7dab8ac407347f40721c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1b380a11ca73807a71cc75838a04dfb8234ff3925bf615e9bd86e912295a973(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c9e8ae912e2e9119570cff3ccbb9c050ae85be9d1b845151ef40986c6be6a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ac154d1798635bc845a2a6fa42414dc23ac2e28caeb5b7872511e7beafccd8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsNetworkInterface]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e14128cc8926eab2df519d163f2fe6fb0aa980cb9584a01555f2b238d69d8f2b(
    *,
    required_memory_maximum: jsii.Number,
    required_memory_minimum: jsii.Number,
    required_vcpu_maximum: jsii.Number,
    required_vcpu_minimum: jsii.Number,
    excluded_instance_families: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_instance_generations: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    required_gpu_maximum: typing.Optional[jsii.Number] = None,
    required_gpu_minimum: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d9c9d0213c23e844bc15611fbdc5afdb5d2bfc87660427c0cdcced8f622529(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9afb0885648f5e85c72c6d02045e66efd9303381c428c9bf15701dedec55c13(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a111816b9f15e86fbeadcae8eb859f414484ec5a1ce431d428699d938c63adbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0913aea64fe1af6ba6689bba7c4c60a6974ac623e5db878b68f592a77348a8d8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aab21a8b4f7f537fcf9d1430438d225f8f974f3e6ed8974227749f1c3f6da6d3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ca42801693ace5c76de4107fe360a01876130a12d2968e949e63e25d5cfb34(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceRequirements]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__140069ae5389c5c972aeb132f79618a4f1ab9d6cbd649da34f60979977569339(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5857e1d151877c27c06b275ccaf27e3ac0d71fce64ac31717b8ce7f645df9820(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7cecc6f9663efa9f61a8c4adc44691ccfc29c7903d1e6fa942812e9e49c9306(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67bc9679432f513948cb7f1905ca64e0c33ae6f48aa0f54c5d61c9e9a1c79103(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__439fd2741114987c9248857f6f23a0502cb52424ed59330ecb1c9e5274dac138(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81bc465d5d0fc714b0ab9587aaf7740e8d45c27074d931c94fccb5157b491d30(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b297ad92be27e01537cd37e1f21aaba6069b53aad4f4bb430d142d4a48c8146(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d414163d2332e2fe129c1f00e0e0cf76ed54392f1253d6331cfbcf42a394b8e7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__423f75e4c463c510076288171e9b554057cfa20af4548657a62f4b44f921239c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5430e457b5f548db908c099a4979cd0f2d6ebad5c6b7ce07060e5d7db64521d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__746d6cd3e36f1310e9292fb420f1d3c765a99a5c9660e81d4ccfca4eb1d74a36(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceRequirements]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a79979b3adb0bb1947ab2e8a7e45bfa4e891b34d54edaabd059e55aed615f897(
    *,
    should_tag_amis: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_tag_enis: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_tag_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_tag_volumes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd14136bb8f407c55ff3e179a460d2641492a7727b4283f065be0029304e0698(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20f7b719852be16360ede8c713e76dbf63e689df0f5e513c99a9e3ddc9639e0e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1788e037dd4711c1f7fe603de9c6af1393a173a47d1b4c9797abc4085f13c6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e7fa9204d89411d527faac7d71bf6b8ac39680bd7032553b7a248407c8a6ce7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__840cff6c615eb39217ced5bab2b3f8b13f3aa3ec2e94ac593561c45ebe6109fc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d7a5cb7b31ce14697b8a59d2cbee0dfd134b050d03054c757e81bc4f1faf9b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsResourceTagSpecification]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69870c96486a44227605efb64725a27b2b2331dc841f37837ffa37ac7caaf8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76ddffd389f64e0235cced29d14340ea7b086974a7c59935f2d8806d16bf1b13(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d5a1b273d0bcbece1cace62c925fa337a7ef7672c70ffd591693364c2023cf9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e01031bf81264e1a74e70f10dbb2fcaf866d75804545f7efc2287c7e85cab77b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43ad4cac60f64218d75734daf3fdbc6192133e62526356e3e9fb0440ff87e250(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90d41ce51850e1ae6d64a8a2178b3a38523123657af7028d430f39c96ed8fce5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsResourceTagSpecification]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f3777d0973a56f2d2cf3fb8f29b353241dc348847aa98f3aed26c6d0318f247(
    *,
    perform_at: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eead1d1e5430c324b3acfaf3ed0c217beb1a1a6b4a44c0946f5518cc78ab62d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4395db6acc56dd620d18406a3c13b700c1c5cf04492fd2986e343dfdd69ae52a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e88f49582500216398ed3284f9c1fbdca5dfc412373e32fafbbeb4471e367f6b(
    value: typing.Optional[ManagedInstanceAwsRevertToSpot],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bed4c15a9144580093505d7280d8fd48e6cee93f771e8e1943f78d0218bbce6(
    *,
    task_type: builtins.str,
    cron_expression: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    start_time: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__923d0b611823251dbccabef4346181187f94391f0fc3f4e04e92f25a466cf947(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__823e38c8ec02eb165b3b4a62fe3d30e5207581741815420f5b21e3d78a6b9a60(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__004d9c87eca1043a00c3c0d0b10602b477d962c2e789206b05ea857783a36584(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39ff1cc784adb6b6684b32a211ec2c3892791997c2cabb969b7271e59537060b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18bb9599b31272748bf3361f4ec49b430e9e18959705158a0f8cac994f77338d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a24e4af8c387dd58b80cbdc97cfac5664129efefd326b8ef6bf2099dc64f5e94(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsScheduledTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__413bb0d8f08c64aa2156acea1eaa861dd5b63197c6dc8acda15bdd167acf8cf0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d83ed7be73fa3fe1422c9487a08c6411097217afd4eafd80ebdad658c02eead7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c443f1778e6e0b5a86766eec9db7b9434132692f955c3a1e529f79a4fbddad45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17e69301c8a31658f933b52a60fb610fd7daab9273aeebdb59a0adee4efc8ad1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd79f2ded6f5fd3551277afb01462eaa1ae61a525777c5fb26565a1e5a54915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289b7856ac1694e2c6b82c482cbb6391706f7965508f8ecd949c315c1c0aa520(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f03e686bbd915fd46efdb54ca69f1009a4220b6f5b0fcd6d3c2d63f64524bb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsScheduledTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__836286d24c53126d41954cdd2a2f80edda21e8739339c0bdfdf0890868439a3f(
    *,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7ca332d5aebd24ef3e1ff990661fed87f60fdaf60e42db70345b8f34292baa9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab3b8daa64e91a185ee83f0133a5046ecf33c0efaf2e2f3b58bd2e6d28602689(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a78d2cce4afc6e06a5536995a68b0c8f2c0b1216669bb484d828487ce1c6ec7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a4f56c3f9fcbbe88347669ad6e90ab622e900a387e077a03623b3553579136(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed3e1fe6f846e6819e4e99902cd8c8c7126456c0ef21654068a3af4064fdf58(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58544591d3043d44dc77f27ee59874e98331c9af898cfb98db3c0bc9a2de9182(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ManagedInstanceAwsTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db86f1d0f29a618e3447c2d80839381284802e37cdebd71b436fbf284ecb0a6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9703dea10d0dc383a8a3c4a2399c84590e73df7ef319c4bea27a8f4a9cea76a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b01fe303f0ed82a4cbd6bf684fddb507d2954cb9558ffdddc35d27ce5f3a352(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__496214941afaa7079d415f8e1df259700bf8f6b8a575fafd2d82c1869680a05d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ManagedInstanceAwsTags]],
) -> None:
    """Type checking stubs"""
    pass
