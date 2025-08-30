r'''
# `spotinst_stateful_node_azure`

Refer to the Terraform Registry for docs: [`spotinst_stateful_node_azure`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure).
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


class StatefulNodeAzure(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzure",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure spotinst_stateful_node_azure}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        os: builtins.str,
        region: builtins.str,
        resource_group_name: builtins.str,
        should_persist_data_disks: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        should_persist_network: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        should_persist_os_disk: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        strategy: typing.Union["StatefulNodeAzureStrategy", typing.Dict[builtins.str, typing.Any]],
        vm_sizes: typing.Union["StatefulNodeAzureVmSizes", typing.Dict[builtins.str, typing.Any]],
        attach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureAttachDataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureBootDiagnostics", typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_data: typing.Optional[builtins.str] = None,
        data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        data_disks_persistence_mode: typing.Optional[builtins.str] = None,
        delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDelete", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        detach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDetachDataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        extension: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureExtension", typing.Dict[builtins.str, typing.Any]]]]] = None,
        health: typing.Optional[typing.Union["StatefulNodeAzureHealth", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        image: typing.Optional[typing.Union["StatefulNodeAzureImage", typing.Dict[builtins.str, typing.Any]]] = None,
        import_vm: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImportVm", typing.Dict[builtins.str, typing.Any]]]]] = None,
        license_type: typing.Optional[builtins.str] = None,
        load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureLoadBalancer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        login: typing.Optional[typing.Union["StatefulNodeAzureLogin", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_service_identities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureManagedServiceIdentities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        network: typing.Optional[typing.Union["StatefulNodeAzureNetwork", typing.Dict[builtins.str, typing.Any]]] = None,
        os_disk: typing.Optional[typing.Union["StatefulNodeAzureOsDisk", typing.Dict[builtins.str, typing.Any]]] = None,
        os_disk_persistence_mode: typing.Optional[builtins.str] = None,
        preferred_zone: typing.Optional[builtins.str] = None,
        proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureProximityPlacementGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecret", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security: typing.Optional[typing.Union["StatefulNodeAzureSecurity", typing.Dict[builtins.str, typing.Any]]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSignal", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tag: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureTag", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_state: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureUpdateState", typing.Dict[builtins.str, typing.Any]]]]] = None,
        user_data: typing.Optional[builtins.str] = None,
        vm_name: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure spotinst_stateful_node_azure} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param os: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os StatefulNodeAzure#os}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#region StatefulNodeAzure#region}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        :param should_persist_data_disks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_data_disks StatefulNodeAzure#should_persist_data_disks}.
        :param should_persist_network: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_network StatefulNodeAzure#should_persist_network}.
        :param should_persist_os_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_os_disk StatefulNodeAzure#should_persist_os_disk}.
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#strategy StatefulNodeAzure#strategy}
        :param vm_sizes: vm_sizes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_sizes StatefulNodeAzure#vm_sizes}
        :param attach_data_disk: attach_data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#attach_data_disk StatefulNodeAzure#attach_data_disk}
        :param boot_diagnostics: boot_diagnostics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#boot_diagnostics StatefulNodeAzure#boot_diagnostics}
        :param custom_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_data StatefulNodeAzure#custom_data}.
        :param data_disk: data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk StatefulNodeAzure#data_disk}
        :param data_disks_persistence_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disks_persistence_mode StatefulNodeAzure#data_disks_persistence_mode}.
        :param delete: delete block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#delete StatefulNodeAzure#delete}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#description StatefulNodeAzure#description}.
        :param detach_data_disk: detach_data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#detach_data_disk StatefulNodeAzure#detach_data_disk}
        :param extension: extension block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#extension StatefulNodeAzure#extension}
        :param health: health block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#health StatefulNodeAzure#health}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#id StatefulNodeAzure#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image: image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#image StatefulNodeAzure#image}
        :param import_vm: import_vm block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#import_vm StatefulNodeAzure#import_vm}
        :param license_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#license_type StatefulNodeAzure#license_type}.
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#load_balancer StatefulNodeAzure#load_balancer}
        :param login: login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#login StatefulNodeAzure#login}
        :param managed_service_identities: managed_service_identities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#managed_service_identities StatefulNodeAzure#managed_service_identities}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network StatefulNodeAzure#network}
        :param os_disk: os_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os_disk StatefulNodeAzure#os_disk}
        :param os_disk_persistence_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os_disk_persistence_mode StatefulNodeAzure#os_disk_persistence_mode}.
        :param preferred_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_zone StatefulNodeAzure#preferred_zone}.
        :param proximity_placement_groups: proximity_placement_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#proximity_placement_groups StatefulNodeAzure#proximity_placement_groups}
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#scheduling_task StatefulNodeAzure#scheduling_task}
        :param secret: secret block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#secret StatefulNodeAzure#secret}
        :param security: security block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#security StatefulNodeAzure#security}
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#shutdown_script StatefulNodeAzure#shutdown_script}.
        :param signal: signal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#signal StatefulNodeAzure#signal}
        :param tag: tag block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag StatefulNodeAzure#tag}
        :param update_state: update_state block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#update_state StatefulNodeAzure#update_state}
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#user_data StatefulNodeAzure#user_data}.
        :param vm_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_name StatefulNodeAzure#vm_name}.
        :param vm_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_name_prefix StatefulNodeAzure#vm_name_prefix}.
        :param zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#zones StatefulNodeAzure#zones}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6411d4756ce105f886982172101ca71f8cfd1c221c0894ee68a36a4068b9a00)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = StatefulNodeAzureConfig(
            name=name,
            os=os,
            region=region,
            resource_group_name=resource_group_name,
            should_persist_data_disks=should_persist_data_disks,
            should_persist_network=should_persist_network,
            should_persist_os_disk=should_persist_os_disk,
            strategy=strategy,
            vm_sizes=vm_sizes,
            attach_data_disk=attach_data_disk,
            boot_diagnostics=boot_diagnostics,
            custom_data=custom_data,
            data_disk=data_disk,
            data_disks_persistence_mode=data_disks_persistence_mode,
            delete=delete,
            description=description,
            detach_data_disk=detach_data_disk,
            extension=extension,
            health=health,
            id=id,
            image=image,
            import_vm=import_vm,
            license_type=license_type,
            load_balancer=load_balancer,
            login=login,
            managed_service_identities=managed_service_identities,
            network=network,
            os_disk=os_disk,
            os_disk_persistence_mode=os_disk_persistence_mode,
            preferred_zone=preferred_zone,
            proximity_placement_groups=proximity_placement_groups,
            scheduling_task=scheduling_task,
            secret=secret,
            security=security,
            shutdown_script=shutdown_script,
            signal=signal,
            tag=tag,
            update_state=update_state,
            user_data=user_data,
            vm_name=vm_name,
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
        '''Generates CDKTF code for importing a StatefulNodeAzure resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StatefulNodeAzure to import.
        :param import_from_id: The id of the existing StatefulNodeAzure that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StatefulNodeAzure to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68e68406114d80b6f06b42a2e346d92131682b9b2f828e77a7ff5fafc1f5b6de)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAttachDataDisk")
    def put_attach_data_disk(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureAttachDataDisk", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b9b9a4a2bcde5f8294895858d40a9a36d5332e157c5987350baf1d7b315dee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAttachDataDisk", [value]))

    @jsii.member(jsii_name="putBootDiagnostics")
    def put_boot_diagnostics(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureBootDiagnostics", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b079bd829816c17192015c3ddbd43871208202c9ac690929b7a82011d632748)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBootDiagnostics", [value]))

    @jsii.member(jsii_name="putDataDisk")
    def put_data_disk(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDataDisk", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f319aa7e79daaa65437d5b3bfb0f3e6d2513184e58aa023425abdce771f4b82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDataDisk", [value]))

    @jsii.member(jsii_name="putDelete")
    def put_delete(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDelete", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c670de37fcc7e8dad922bfbe7c34e79db4512de52f9ad37d3cd3aa3708ec98c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDelete", [value]))

    @jsii.member(jsii_name="putDetachDataDisk")
    def put_detach_data_disk(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDetachDataDisk", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b49a282ff9f2c0162752d4dfc8a1d0cf8f08d4107c130442d84382821081a51f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDetachDataDisk", [value]))

    @jsii.member(jsii_name="putExtension")
    def put_extension(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureExtension", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a0df44362e03f6668355d53a0c0bf7ebc36e1b84bdd3468b527b56da2ef6b31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExtension", [value]))

    @jsii.member(jsii_name="putHealth")
    def put_health(
        self,
        *,
        auto_healing: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        health_check_types: typing.Sequence[builtins.str],
        grace_period: typing.Optional[jsii.Number] = None,
        unhealthy_duration: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param auto_healing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#auto_healing StatefulNodeAzure#auto_healing}.
        :param health_check_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#health_check_types StatefulNodeAzure#health_check_types}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#grace_period StatefulNodeAzure#grace_period}.
        :param unhealthy_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#unhealthy_duration StatefulNodeAzure#unhealthy_duration}.
        '''
        value = StatefulNodeAzureHealth(
            auto_healing=auto_healing,
            health_check_types=health_check_types,
            grace_period=grace_period,
            unhealthy_duration=unhealthy_duration,
        )

        return typing.cast(None, jsii.invoke(self, "putHealth", [value]))

    @jsii.member(jsii_name="putImage")
    def put_image(
        self,
        *,
        custom_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImageCustomImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gallery: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImageGallery", typing.Dict[builtins.str, typing.Any]]]]] = None,
        marketplace_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImageMarketplaceImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param custom_image: custom_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_image StatefulNodeAzure#custom_image}
        :param gallery: gallery block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery StatefulNodeAzure#gallery}
        :param marketplace_image: marketplace_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#marketplace_image StatefulNodeAzure#marketplace_image}
        '''
        value = StatefulNodeAzureImage(
            custom_image=custom_image,
            gallery=gallery,
            marketplace_image=marketplace_image,
        )

        return typing.cast(None, jsii.invoke(self, "putImage", [value]))

    @jsii.member(jsii_name="putImportVm")
    def put_import_vm(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImportVm", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b287b7326269cb308907f1fbdea179797f6551389da4ef3b997dc0c5aad9a4cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putImportVm", [value]))

    @jsii.member(jsii_name="putLoadBalancer")
    def put_load_balancer(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureLoadBalancer", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b4c1c0381481bc2364076b89a29d3dc0d7726efd504243a0813b66ef66b0e01)
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
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#user_name StatefulNodeAzure#user_name}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#password StatefulNodeAzure#password}.
        :param ssh_public_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#ssh_public_key StatefulNodeAzure#ssh_public_key}.
        '''
        value = StatefulNodeAzureLogin(
            user_name=user_name, password=password, ssh_public_key=ssh_public_key
        )

        return typing.cast(None, jsii.invoke(self, "putLogin", [value]))

    @jsii.member(jsii_name="putManagedServiceIdentities")
    def put_managed_service_identities(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureManagedServiceIdentities", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d03e79967c9b22aef6fd1c4dd396b536ea5547a61d96574427a9fdd163b3ce0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putManagedServiceIdentities", [value]))

    @jsii.member(jsii_name="putNetwork")
    def put_network(
        self,
        *,
        network_interface: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterface", typing.Dict[builtins.str, typing.Any]]]],
        network_resource_group_name: builtins.str,
        virtual_network_name: builtins.str,
    ) -> None:
        '''
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_interface StatefulNodeAzure#network_interface}
        :param network_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.
        :param virtual_network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#virtual_network_name StatefulNodeAzure#virtual_network_name}.
        '''
        value = StatefulNodeAzureNetwork(
            network_interface=network_interface,
            network_resource_group_name=network_resource_group_name,
            virtual_network_name=virtual_network_name,
        )

        return typing.cast(None, jsii.invoke(self, "putNetwork", [value]))

    @jsii.member(jsii_name="putOsDisk")
    def put_os_disk(
        self,
        *,
        type: builtins.str,
        caching: typing.Optional[builtins.str] = None,
        size_gb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        :param caching: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#caching StatefulNodeAzure#caching}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.
        '''
        value = StatefulNodeAzureOsDisk(type=type, caching=caching, size_gb=size_gb)

        return typing.cast(None, jsii.invoke(self, "putOsDisk", [value]))

    @jsii.member(jsii_name="putProximityPlacementGroups")
    def put_proximity_placement_groups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureProximityPlacementGroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__238973118137de900a9ac9338243fa431c978a3c2c0c716cc21b46061bfb9259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putProximityPlacementGroups", [value]))

    @jsii.member(jsii_name="putSchedulingTask")
    def put_scheduling_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSchedulingTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c5a840305bf927bb881444590f9fe8beac1625afc3dff55e05ea5bd2f78cd63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSchedulingTask", [value]))

    @jsii.member(jsii_name="putSecret")
    def put_secret(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecret", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b2339d4d512e0e51e1232d2c26b0021edf28e08af67737beb136e573d20ff33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSecret", [value]))

    @jsii.member(jsii_name="putSecurity")
    def put_security(
        self,
        *,
        confidential_os_disk_encryption: typing.Optional[builtins.str] = None,
        encryption_at_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        security_type: typing.Optional[builtins.str] = None,
        vtpm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param confidential_os_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#confidential_os_disk_encryption StatefulNodeAzure#confidential_os_disk_encryption}.
        :param encryption_at_host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#encryption_at_host StatefulNodeAzure#encryption_at_host}.
        :param secure_boot_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#secure_boot_enabled StatefulNodeAzure#secure_boot_enabled}.
        :param security_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#security_type StatefulNodeAzure#security_type}.
        :param vtpm_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vtpm_enabled StatefulNodeAzure#vtpm_enabled}.
        '''
        value = StatefulNodeAzureSecurity(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSignal", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea1bc6d3eb288e8d6cd408fed8a2a2b5db96e45b964a9a487770deeb7af8ef87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSignal", [value]))

    @jsii.member(jsii_name="putStrategy")
    def put_strategy(
        self,
        *,
        fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        availability_vs_cost: typing.Optional[jsii.Number] = None,
        capacity_reservation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureStrategyCapacityReservation", typing.Dict[builtins.str, typing.Any]]]]] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        od_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_life_cycle: typing.Optional[builtins.str] = None,
        revert_to_spot: typing.Optional[typing.Union["StatefulNodeAzureStrategyRevertToSpot", typing.Dict[builtins.str, typing.Any]]] = None,
        vm_admins: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param fallback_to_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#fallback_to_on_demand StatefulNodeAzure#fallback_to_on_demand}.
        :param availability_vs_cost: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#availability_vs_cost StatefulNodeAzure#availability_vs_cost}.
        :param capacity_reservation: capacity_reservation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#capacity_reservation StatefulNodeAzure#capacity_reservation}
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#draining_timeout StatefulNodeAzure#draining_timeout}.
        :param od_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#od_windows StatefulNodeAzure#od_windows}.
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#optimization_windows StatefulNodeAzure#optimization_windows}.
        :param preferred_life_cycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_life_cycle StatefulNodeAzure#preferred_life_cycle}.
        :param revert_to_spot: revert_to_spot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#revert_to_spot StatefulNodeAzure#revert_to_spot}
        :param vm_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_admins StatefulNodeAzure#vm_admins}.
        '''
        value = StatefulNodeAzureStrategy(
            fallback_to_on_demand=fallback_to_on_demand,
            availability_vs_cost=availability_vs_cost,
            capacity_reservation=capacity_reservation,
            draining_timeout=draining_timeout,
            od_windows=od_windows,
            optimization_windows=optimization_windows,
            preferred_life_cycle=preferred_life_cycle,
            revert_to_spot=revert_to_spot,
            vm_admins=vm_admins,
        )

        return typing.cast(None, jsii.invoke(self, "putStrategy", [value]))

    @jsii.member(jsii_name="putTag")
    def put_tag(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureTag", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b732fe6139805b68483601195e712f36f7c35385ebb86db47a82b4e85689b5f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTag", [value]))

    @jsii.member(jsii_name="putUpdateState")
    def put_update_state(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureUpdateState", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce320be27fa4e3cbf421c284beb997fe11ef438e69e827c93b408fb78e540308)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUpdateState", [value]))

    @jsii.member(jsii_name="putVmSizes")
    def put_vm_sizes(
        self,
        *,
        od_sizes: typing.Sequence[builtins.str],
        excluded_vm_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        spot_size_attributes: typing.Optional[typing.Union["StatefulNodeAzureVmSizesSpotSizeAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param od_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#od_sizes StatefulNodeAzure#od_sizes}.
        :param excluded_vm_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#excluded_vm_sizes StatefulNodeAzure#excluded_vm_sizes}.
        :param preferred_spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_spot_sizes StatefulNodeAzure#preferred_spot_sizes}.
        :param spot_size_attributes: spot_size_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_size_attributes StatefulNodeAzure#spot_size_attributes}
        :param spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_sizes StatefulNodeAzure#spot_sizes}.
        '''
        value = StatefulNodeAzureVmSizes(
            od_sizes=od_sizes,
            excluded_vm_sizes=excluded_vm_sizes,
            preferred_spot_sizes=preferred_spot_sizes,
            spot_size_attributes=spot_size_attributes,
            spot_sizes=spot_sizes,
        )

        return typing.cast(None, jsii.invoke(self, "putVmSizes", [value]))

    @jsii.member(jsii_name="resetAttachDataDisk")
    def reset_attach_data_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttachDataDisk", []))

    @jsii.member(jsii_name="resetBootDiagnostics")
    def reset_boot_diagnostics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootDiagnostics", []))

    @jsii.member(jsii_name="resetCustomData")
    def reset_custom_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomData", []))

    @jsii.member(jsii_name="resetDataDisk")
    def reset_data_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataDisk", []))

    @jsii.member(jsii_name="resetDataDisksPersistenceMode")
    def reset_data_disks_persistence_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataDisksPersistenceMode", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDetachDataDisk")
    def reset_detach_data_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDetachDataDisk", []))

    @jsii.member(jsii_name="resetExtension")
    def reset_extension(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtension", []))

    @jsii.member(jsii_name="resetHealth")
    def reset_health(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealth", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImage")
    def reset_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImage", []))

    @jsii.member(jsii_name="resetImportVm")
    def reset_import_vm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImportVm", []))

    @jsii.member(jsii_name="resetLicenseType")
    def reset_license_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseType", []))

    @jsii.member(jsii_name="resetLoadBalancer")
    def reset_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoadBalancer", []))

    @jsii.member(jsii_name="resetLogin")
    def reset_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogin", []))

    @jsii.member(jsii_name="resetManagedServiceIdentities")
    def reset_managed_service_identities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedServiceIdentities", []))

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetOsDisk")
    def reset_os_disk(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDisk", []))

    @jsii.member(jsii_name="resetOsDiskPersistenceMode")
    def reset_os_disk_persistence_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOsDiskPersistenceMode", []))

    @jsii.member(jsii_name="resetPreferredZone")
    def reset_preferred_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredZone", []))

    @jsii.member(jsii_name="resetProximityPlacementGroups")
    def reset_proximity_placement_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProximityPlacementGroups", []))

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

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetUpdateState")
    def reset_update_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateState", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @jsii.member(jsii_name="resetVmName")
    def reset_vm_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmName", []))

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
    @jsii.member(jsii_name="attachDataDisk")
    def attach_data_disk(self) -> "StatefulNodeAzureAttachDataDiskList":
        return typing.cast("StatefulNodeAzureAttachDataDiskList", jsii.get(self, "attachDataDisk"))

    @builtins.property
    @jsii.member(jsii_name="bootDiagnostics")
    def boot_diagnostics(self) -> "StatefulNodeAzureBootDiagnosticsList":
        return typing.cast("StatefulNodeAzureBootDiagnosticsList", jsii.get(self, "bootDiagnostics"))

    @builtins.property
    @jsii.member(jsii_name="dataDisk")
    def data_disk(self) -> "StatefulNodeAzureDataDiskList":
        return typing.cast("StatefulNodeAzureDataDiskList", jsii.get(self, "dataDisk"))

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> "StatefulNodeAzureDeleteList":
        return typing.cast("StatefulNodeAzureDeleteList", jsii.get(self, "delete"))

    @builtins.property
    @jsii.member(jsii_name="detachDataDisk")
    def detach_data_disk(self) -> "StatefulNodeAzureDetachDataDiskList":
        return typing.cast("StatefulNodeAzureDetachDataDiskList", jsii.get(self, "detachDataDisk"))

    @builtins.property
    @jsii.member(jsii_name="extension")
    def extension(self) -> "StatefulNodeAzureExtensionList":
        return typing.cast("StatefulNodeAzureExtensionList", jsii.get(self, "extension"))

    @builtins.property
    @jsii.member(jsii_name="health")
    def health(self) -> "StatefulNodeAzureHealthOutputReference":
        return typing.cast("StatefulNodeAzureHealthOutputReference", jsii.get(self, "health"))

    @builtins.property
    @jsii.member(jsii_name="image")
    def image(self) -> "StatefulNodeAzureImageOutputReference":
        return typing.cast("StatefulNodeAzureImageOutputReference", jsii.get(self, "image"))

    @builtins.property
    @jsii.member(jsii_name="importVm")
    def import_vm(self) -> "StatefulNodeAzureImportVmList":
        return typing.cast("StatefulNodeAzureImportVmList", jsii.get(self, "importVm"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(self) -> "StatefulNodeAzureLoadBalancerList":
        return typing.cast("StatefulNodeAzureLoadBalancerList", jsii.get(self, "loadBalancer"))

    @builtins.property
    @jsii.member(jsii_name="login")
    def login(self) -> "StatefulNodeAzureLoginOutputReference":
        return typing.cast("StatefulNodeAzureLoginOutputReference", jsii.get(self, "login"))

    @builtins.property
    @jsii.member(jsii_name="managedServiceIdentities")
    def managed_service_identities(
        self,
    ) -> "StatefulNodeAzureManagedServiceIdentitiesList":
        return typing.cast("StatefulNodeAzureManagedServiceIdentitiesList", jsii.get(self, "managedServiceIdentities"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> "StatefulNodeAzureNetworkOutputReference":
        return typing.cast("StatefulNodeAzureNetworkOutputReference", jsii.get(self, "network"))

    @builtins.property
    @jsii.member(jsii_name="osDisk")
    def os_disk(self) -> "StatefulNodeAzureOsDiskOutputReference":
        return typing.cast("StatefulNodeAzureOsDiskOutputReference", jsii.get(self, "osDisk"))

    @builtins.property
    @jsii.member(jsii_name="proximityPlacementGroups")
    def proximity_placement_groups(
        self,
    ) -> "StatefulNodeAzureProximityPlacementGroupsList":
        return typing.cast("StatefulNodeAzureProximityPlacementGroupsList", jsii.get(self, "proximityPlacementGroups"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTask")
    def scheduling_task(self) -> "StatefulNodeAzureSchedulingTaskList":
        return typing.cast("StatefulNodeAzureSchedulingTaskList", jsii.get(self, "schedulingTask"))

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> "StatefulNodeAzureSecretList":
        return typing.cast("StatefulNodeAzureSecretList", jsii.get(self, "secret"))

    @builtins.property
    @jsii.member(jsii_name="security")
    def security(self) -> "StatefulNodeAzureSecurityOutputReference":
        return typing.cast("StatefulNodeAzureSecurityOutputReference", jsii.get(self, "security"))

    @builtins.property
    @jsii.member(jsii_name="signal")
    def signal(self) -> "StatefulNodeAzureSignalList":
        return typing.cast("StatefulNodeAzureSignalList", jsii.get(self, "signal"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "StatefulNodeAzureStrategyOutputReference":
        return typing.cast("StatefulNodeAzureStrategyOutputReference", jsii.get(self, "strategy"))

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> "StatefulNodeAzureTagList":
        return typing.cast("StatefulNodeAzureTagList", jsii.get(self, "tag"))

    @builtins.property
    @jsii.member(jsii_name="updateState")
    def update_state(self) -> "StatefulNodeAzureUpdateStateList":
        return typing.cast("StatefulNodeAzureUpdateStateList", jsii.get(self, "updateState"))

    @builtins.property
    @jsii.member(jsii_name="vmSizes")
    def vm_sizes(self) -> "StatefulNodeAzureVmSizesOutputReference":
        return typing.cast("StatefulNodeAzureVmSizesOutputReference", jsii.get(self, "vmSizes"))

    @builtins.property
    @jsii.member(jsii_name="attachDataDiskInput")
    def attach_data_disk_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureAttachDataDisk"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureAttachDataDisk"]]], jsii.get(self, "attachDataDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="bootDiagnosticsInput")
    def boot_diagnostics_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureBootDiagnostics"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureBootDiagnostics"]]], jsii.get(self, "bootDiagnosticsInput"))

    @builtins.property
    @jsii.member(jsii_name="customDataInput")
    def custom_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDataInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDiskInput")
    def data_disk_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDataDisk"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDataDisk"]]], jsii.get(self, "dataDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDisksPersistenceModeInput")
    def data_disks_persistence_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataDisksPersistenceModeInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDelete"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDelete"]]], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="detachDataDiskInput")
    def detach_data_disk_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDetachDataDisk"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDetachDataDisk"]]], jsii.get(self, "detachDataDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="extensionInput")
    def extension_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureExtension"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureExtension"]]], jsii.get(self, "extensionInput"))

    @builtins.property
    @jsii.member(jsii_name="healthInput")
    def health_input(self) -> typing.Optional["StatefulNodeAzureHealth"]:
        return typing.cast(typing.Optional["StatefulNodeAzureHealth"], jsii.get(self, "healthInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional["StatefulNodeAzureImage"]:
        return typing.cast(typing.Optional["StatefulNodeAzureImage"], jsii.get(self, "imageInput"))

    @builtins.property
    @jsii.member(jsii_name="importVmInput")
    def import_vm_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImportVm"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImportVm"]]], jsii.get(self, "importVmInput"))

    @builtins.property
    @jsii.member(jsii_name="licenseTypeInput")
    def license_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "licenseTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="loadBalancerInput")
    def load_balancer_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureLoadBalancer"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureLoadBalancer"]]], jsii.get(self, "loadBalancerInput"))

    @builtins.property
    @jsii.member(jsii_name="loginInput")
    def login_input(self) -> typing.Optional["StatefulNodeAzureLogin"]:
        return typing.cast(typing.Optional["StatefulNodeAzureLogin"], jsii.get(self, "loginInput"))

    @builtins.property
    @jsii.member(jsii_name="managedServiceIdentitiesInput")
    def managed_service_identities_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureManagedServiceIdentities"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureManagedServiceIdentities"]]], jsii.get(self, "managedServiceIdentitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional["StatefulNodeAzureNetwork"]:
        return typing.cast(typing.Optional["StatefulNodeAzureNetwork"], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="osDiskInput")
    def os_disk_input(self) -> typing.Optional["StatefulNodeAzureOsDisk"]:
        return typing.cast(typing.Optional["StatefulNodeAzureOsDisk"], jsii.get(self, "osDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="osDiskPersistenceModeInput")
    def os_disk_persistence_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osDiskPersistenceModeInput"))

    @builtins.property
    @jsii.member(jsii_name="osInput")
    def os_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredZoneInput")
    def preferred_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="proximityPlacementGroupsInput")
    def proximity_placement_groups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureProximityPlacementGroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureProximityPlacementGroups"]]], jsii.get(self, "proximityPlacementGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTaskInput")
    def scheduling_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSchedulingTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSchedulingTask"]]], jsii.get(self, "schedulingTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecret"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecret"]]], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="securityInput")
    def security_input(self) -> typing.Optional["StatefulNodeAzureSecurity"]:
        return typing.cast(typing.Optional["StatefulNodeAzureSecurity"], jsii.get(self, "securityInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldPersistDataDisksInput")
    def should_persist_data_disks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldPersistDataDisksInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldPersistNetworkInput")
    def should_persist_network_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldPersistNetworkInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldPersistOsDiskInput")
    def should_persist_os_disk_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldPersistOsDiskInput"))

    @builtins.property
    @jsii.member(jsii_name="shutdownScriptInput")
    def shutdown_script_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shutdownScriptInput"))

    @builtins.property
    @jsii.member(jsii_name="signalInput")
    def signal_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSignal"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSignal"]]], jsii.get(self, "signalInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(self) -> typing.Optional["StatefulNodeAzureStrategy"]:
        return typing.cast(typing.Optional["StatefulNodeAzureStrategy"], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="tagInput")
    def tag_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureTag"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureTag"]]], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="updateStateInput")
    def update_state_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureUpdateState"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureUpdateState"]]], jsii.get(self, "updateStateInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property
    @jsii.member(jsii_name="vmNameInput")
    def vm_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vmNameInput"))

    @builtins.property
    @jsii.member(jsii_name="vmNamePrefixInput")
    def vm_name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vmNamePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="vmSizesInput")
    def vm_sizes_input(self) -> typing.Optional["StatefulNodeAzureVmSizes"]:
        return typing.cast(typing.Optional["StatefulNodeAzureVmSizes"], jsii.get(self, "vmSizesInput"))

    @builtins.property
    @jsii.member(jsii_name="zonesInput")
    def zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "zonesInput"))

    @builtins.property
    @jsii.member(jsii_name="customData")
    def custom_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customData"))

    @custom_data.setter
    def custom_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d316377dceea66757eb22fe2b05ef312e65140ff513f2882ead764caf0b34208)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataDisksPersistenceMode")
    def data_disks_persistence_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataDisksPersistenceMode"))

    @data_disks_persistence_mode.setter
    def data_disks_persistence_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__492c391cfd62d3468e9c176f97d615d8dc6c54311b4b601b90909afd8fc10ead)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataDisksPersistenceMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072109a4cfeb07e69ae8b1060bc7819114ea9e14c4ab0bae22e588de250d7504)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e806a5a9bac88f0ba083f3d93b47547e0f8821ed356662f73b5a41fc11f0199c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="licenseType")
    def license_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseType"))

    @license_type.setter
    def license_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deb2d415e559785cacc89908312a91f1c0cebc3a26eea08e75e7744dd6b6787f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "licenseType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d8acb333787133ddf6830fea172c66e453cd4cffb1086a2af0c38fa8465a07c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="os")
    def os(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "os"))

    @os.setter
    def os(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d3e75da2bba021eb4d7dfd31daf37a42abf883afce11ff1926a65e271c05592)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "os", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="osDiskPersistenceMode")
    def os_disk_persistence_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "osDiskPersistenceMode"))

    @os_disk_persistence_mode.setter
    def os_disk_persistence_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e76c18cf83d1461f816832807ee7a0dc5d240e913b5474374f85ad077b22bcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "osDiskPersistenceMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredZone")
    def preferred_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredZone"))

    @preferred_zone.setter
    def preferred_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0236d4736f4366915bb387445700c71eca205758321157f5cef6f8df81cbd4c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67a45fc161df8f45de3c6a783620a6381f9265845149dc96c8451435584ea186)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20150ed9e9f74acd4989fd81ddd257caf75368474a2cefc401f962adc07c8374)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldPersistDataDisks")
    def should_persist_data_disks(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldPersistDataDisks"))

    @should_persist_data_disks.setter
    def should_persist_data_disks(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e901d7764a827b172653b56a34a02dfb52aa58ba21727bfa49916cd5fe875f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldPersistDataDisks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldPersistNetwork")
    def should_persist_network(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldPersistNetwork"))

    @should_persist_network.setter
    def should_persist_network(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6eb12c12857324902ddbde2b92a9af097ce72ab79cf8f629d8ba21422052e9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldPersistNetwork", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldPersistOsDisk")
    def should_persist_os_disk(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldPersistOsDisk"))

    @should_persist_os_disk.setter
    def should_persist_os_disk(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2ea101ac225e24334776d652196f35d95589dacf52152e7b4e87c8c923a76c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldPersistOsDisk", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shutdownScript")
    def shutdown_script(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shutdownScript"))

    @shutdown_script.setter
    def shutdown_script(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e5cd3d349f5c29761e8f8a1160f7342c90990b90ce5f086d650b0d56acb6be5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shutdownScript", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b40adfc923a339ba99f3326e049afa4508f8f5b63163bb055c40782c59894f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmName")
    def vm_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmName"))

    @vm_name.setter
    def vm_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddd0bf712083572395202a1889b30cf15d7e2ada471453c8a8c1e79ab1f6d723)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmNamePrefix")
    def vm_name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vmNamePrefix"))

    @vm_name_prefix.setter
    def vm_name_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa3691e6abc2e5d624774fc5c5cfa7a2dca609d085e77fa195c3012d7627a547)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmNamePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zones")
    def zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "zones"))

    @zones.setter
    def zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f862b6ab84d043a7be23c8958db6e8e123d111ffd4a53eff51c5db59dfdbc600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zones", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureAttachDataDisk",
    jsii_struct_bases=[],
    name_mapping={
        "data_disk_name": "dataDiskName",
        "data_disk_resource_group_name": "dataDiskResourceGroupName",
        "size_gb": "sizeGb",
        "storage_account_type": "storageAccountType",
        "lun": "lun",
        "zone": "zone",
    },
)
class StatefulNodeAzureAttachDataDisk:
    def __init__(
        self,
        *,
        data_disk_name: builtins.str,
        data_disk_resource_group_name: builtins.str,
        size_gb: jsii.Number,
        storage_account_type: builtins.str,
        lun: typing.Optional[jsii.Number] = None,
        zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param data_disk_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_name StatefulNodeAzure#data_disk_name}.
        :param data_disk_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_resource_group_name StatefulNodeAzure#data_disk_resource_group_name}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.
        :param storage_account_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#storage_account_type StatefulNodeAzure#storage_account_type}.
        :param lun: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#lun StatefulNodeAzure#lun}.
        :param zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#zone StatefulNodeAzure#zone}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37fa66e7fc3311a23a506c4976a81db1f604e07261e5bb5bacc461b5cf465b4f)
            check_type(argname="argument data_disk_name", value=data_disk_name, expected_type=type_hints["data_disk_name"])
            check_type(argname="argument data_disk_resource_group_name", value=data_disk_resource_group_name, expected_type=type_hints["data_disk_resource_group_name"])
            check_type(argname="argument size_gb", value=size_gb, expected_type=type_hints["size_gb"])
            check_type(argname="argument storage_account_type", value=storage_account_type, expected_type=type_hints["storage_account_type"])
            check_type(argname="argument lun", value=lun, expected_type=type_hints["lun"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_disk_name": data_disk_name,
            "data_disk_resource_group_name": data_disk_resource_group_name,
            "size_gb": size_gb,
            "storage_account_type": storage_account_type,
        }
        if lun is not None:
            self._values["lun"] = lun
        if zone is not None:
            self._values["zone"] = zone

    @builtins.property
    def data_disk_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_name StatefulNodeAzure#data_disk_name}.'''
        result = self._values.get("data_disk_name")
        assert result is not None, "Required property 'data_disk_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_disk_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_resource_group_name StatefulNodeAzure#data_disk_resource_group_name}.'''
        result = self._values.get("data_disk_resource_group_name")
        assert result is not None, "Required property 'data_disk_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size_gb(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.'''
        result = self._values.get("size_gb")
        assert result is not None, "Required property 'size_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_account_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#storage_account_type StatefulNodeAzure#storage_account_type}.'''
        result = self._values.get("storage_account_type")
        assert result is not None, "Required property 'storage_account_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lun(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#lun StatefulNodeAzure#lun}.'''
        result = self._values.get("lun")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#zone StatefulNodeAzure#zone}.'''
        result = self._values.get("zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureAttachDataDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureAttachDataDiskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureAttachDataDiskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b74355ed3b997e611ff9bc0342e9cd9b1947e57c5e23ed4b6ec20cbe23221a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureAttachDataDiskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864c54851a55e5ce1529d0d215e19cd4906deb00fba96b0320d57fe41f2435c9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureAttachDataDiskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c3e5cf4267b072d3dc4ef38e2f5438167cca121b54152e5e2df38571ec102dd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc2f3fcedf29857275245b2198bc04b7c45b246ab7da9d2599545bb7060c55b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4abc19cb5494da8120ddbd9f1c835c5777e4c1d934dea25ff9a7aae91121e5a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureAttachDataDisk]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureAttachDataDisk]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureAttachDataDisk]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a8f16cb3e19b7d738138edbd3a12044344cb73015d1102ccd397225bc2ba68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureAttachDataDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureAttachDataDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50e677eb80086cf96e21a65757c8b71a700c751d9c861c4cc6c2374fa4bcf950)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetLun")
    def reset_lun(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLun", []))

    @jsii.member(jsii_name="resetZone")
    def reset_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZone", []))

    @builtins.property
    @jsii.member(jsii_name="dataDiskNameInput")
    def data_disk_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataDiskNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDiskResourceGroupNameInput")
    def data_disk_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataDiskResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="lunInput")
    def lun_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lunInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeGbInput")
    def size_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="storageAccountTypeInput")
    def storage_account_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageAccountTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDiskName")
    def data_disk_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataDiskName"))

    @data_disk_name.setter
    def data_disk_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6294fd7f368c05bdc17cc7f9e1612b273e3e8fe266369e4e7aedca8b768b5fda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataDiskName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataDiskResourceGroupName")
    def data_disk_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataDiskResourceGroupName"))

    @data_disk_resource_group_name.setter
    def data_disk_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f336286335b85671f18172ea9843b886d8a4feae5c0c8cb41237cd152070c455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataDiskResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lun")
    def lun(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lun"))

    @lun.setter
    def lun(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__336098f54b2088e874ec8ef2bf62d5396988283217569e2b2ec11541059d9bf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeGb")
    def size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeGb"))

    @size_gb.setter
    def size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ee47a520ab1ce5c9a362452254af2e7869a7837a9dd7e54b4110bef49c9654)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageAccountType")
    def storage_account_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageAccountType"))

    @storage_account_type.setter
    def storage_account_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b2c34dc90177d4c74e14c744877cd19d30422405114d8120f5e43608947700e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageAccountType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c5e9b2db1fdfa2902f8a0ceaf3bed728e515b4edb0e903142cc0efbb889f658)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureAttachDataDisk]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureAttachDataDisk]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureAttachDataDisk]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f02e58867a1acf42bb3ec625ab3145414f2cf706b7a329027542fc84ff3e2863)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureBootDiagnostics",
    jsii_struct_bases=[],
    name_mapping={
        "is_enabled": "isEnabled",
        "storage_url": "storageUrl",
        "type": "type",
    },
)
class StatefulNodeAzureBootDiagnostics:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        storage_url: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#is_enabled StatefulNodeAzure#is_enabled}.
        :param storage_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#storage_url StatefulNodeAzure#storage_url}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5dbb937b0b0d245207296df23d9f1ab1761c267580812ccfc2724545b949925)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument storage_url", value=storage_url, expected_type=type_hints["storage_url"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if storage_url is not None:
            self._values["storage_url"] = storage_url
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#is_enabled StatefulNodeAzure#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def storage_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#storage_url StatefulNodeAzure#storage_url}.'''
        result = self._values.get("storage_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureBootDiagnostics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureBootDiagnosticsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureBootDiagnosticsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6537f2ac563fa32fc3698118638d0c9bdfd81f83c294d32679e53bdc7918be8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureBootDiagnosticsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1eccd19f5d6175f3b04d8f3244a2f999889f693ef1605bffefcb3647189782)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureBootDiagnosticsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc043ff72b0d1128490ec7713ba8ebfe603e9fbd9c92aa24c8b739bdd061b328)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0235ecad67c297943ea6afd1a9b6ff0863b730f922ec91a231067a031ad31209)
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
            type_hints = typing.get_type_hints(_typecheckingstub__270182408917dd46efdc33b382cc2b8f48bd14e3321115daa59f6230c849296a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureBootDiagnostics]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureBootDiagnostics]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureBootDiagnostics]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86aa92cb60c962b1024868e31ef933797b9dbd59688045da1aa4580f633223b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureBootDiagnosticsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureBootDiagnosticsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c26fbe89267bcd6015185a04636f82d8710078c6beddfc73251caa5ba7303e06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetStorageUrl")
    def reset_storage_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageUrl", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__28bb1a0f6e4a4972a77ddac9fdf9536f1f5678a6c515268643fe2bef28afba0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageUrl")
    def storage_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageUrl"))

    @storage_url.setter
    def storage_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98a2086690acf26f5368b0673d163ade6a9b08e889c5018498772c75b0c63cf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31537207c7b06093e0bb26d7440b598818cc1e5948bbafe9289e5b7e4f6a8437)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureBootDiagnostics]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureBootDiagnostics]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureBootDiagnostics]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d577b50cda2a9e3e457c1d14228b24b578c7a188cf3a1c91a37ad86036ed5dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureConfig",
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
        "os": "os",
        "region": "region",
        "resource_group_name": "resourceGroupName",
        "should_persist_data_disks": "shouldPersistDataDisks",
        "should_persist_network": "shouldPersistNetwork",
        "should_persist_os_disk": "shouldPersistOsDisk",
        "strategy": "strategy",
        "vm_sizes": "vmSizes",
        "attach_data_disk": "attachDataDisk",
        "boot_diagnostics": "bootDiagnostics",
        "custom_data": "customData",
        "data_disk": "dataDisk",
        "data_disks_persistence_mode": "dataDisksPersistenceMode",
        "delete": "delete",
        "description": "description",
        "detach_data_disk": "detachDataDisk",
        "extension": "extension",
        "health": "health",
        "id": "id",
        "image": "image",
        "import_vm": "importVm",
        "license_type": "licenseType",
        "load_balancer": "loadBalancer",
        "login": "login",
        "managed_service_identities": "managedServiceIdentities",
        "network": "network",
        "os_disk": "osDisk",
        "os_disk_persistence_mode": "osDiskPersistenceMode",
        "preferred_zone": "preferredZone",
        "proximity_placement_groups": "proximityPlacementGroups",
        "scheduling_task": "schedulingTask",
        "secret": "secret",
        "security": "security",
        "shutdown_script": "shutdownScript",
        "signal": "signal",
        "tag": "tag",
        "update_state": "updateState",
        "user_data": "userData",
        "vm_name": "vmName",
        "vm_name_prefix": "vmNamePrefix",
        "zones": "zones",
    },
)
class StatefulNodeAzureConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        os: builtins.str,
        region: builtins.str,
        resource_group_name: builtins.str,
        should_persist_data_disks: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        should_persist_network: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        should_persist_os_disk: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        strategy: typing.Union["StatefulNodeAzureStrategy", typing.Dict[builtins.str, typing.Any]],
        vm_sizes: typing.Union["StatefulNodeAzureVmSizes", typing.Dict[builtins.str, typing.Any]],
        attach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureAttachDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
        boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureBootDiagnostics, typing.Dict[builtins.str, typing.Any]]]]] = None,
        custom_data: typing.Optional[builtins.str] = None,
        data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        data_disks_persistence_mode: typing.Optional[builtins.str] = None,
        delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDelete", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        detach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureDetachDataDisk", typing.Dict[builtins.str, typing.Any]]]]] = None,
        extension: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureExtension", typing.Dict[builtins.str, typing.Any]]]]] = None,
        health: typing.Optional[typing.Union["StatefulNodeAzureHealth", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        image: typing.Optional[typing.Union["StatefulNodeAzureImage", typing.Dict[builtins.str, typing.Any]]] = None,
        import_vm: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImportVm", typing.Dict[builtins.str, typing.Any]]]]] = None,
        license_type: typing.Optional[builtins.str] = None,
        load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureLoadBalancer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        login: typing.Optional[typing.Union["StatefulNodeAzureLogin", typing.Dict[builtins.str, typing.Any]]] = None,
        managed_service_identities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureManagedServiceIdentities", typing.Dict[builtins.str, typing.Any]]]]] = None,
        network: typing.Optional[typing.Union["StatefulNodeAzureNetwork", typing.Dict[builtins.str, typing.Any]]] = None,
        os_disk: typing.Optional[typing.Union["StatefulNodeAzureOsDisk", typing.Dict[builtins.str, typing.Any]]] = None,
        os_disk_persistence_mode: typing.Optional[builtins.str] = None,
        preferred_zone: typing.Optional[builtins.str] = None,
        proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureProximityPlacementGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecret", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security: typing.Optional[typing.Union["StatefulNodeAzureSecurity", typing.Dict[builtins.str, typing.Any]]] = None,
        shutdown_script: typing.Optional[builtins.str] = None,
        signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSignal", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tag: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureTag", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_state: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureUpdateState", typing.Dict[builtins.str, typing.Any]]]]] = None,
        user_data: typing.Optional[builtins.str] = None,
        vm_name: typing.Optional[builtins.str] = None,
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
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param os: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os StatefulNodeAzure#os}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#region StatefulNodeAzure#region}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        :param should_persist_data_disks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_data_disks StatefulNodeAzure#should_persist_data_disks}.
        :param should_persist_network: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_network StatefulNodeAzure#should_persist_network}.
        :param should_persist_os_disk: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_os_disk StatefulNodeAzure#should_persist_os_disk}.
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#strategy StatefulNodeAzure#strategy}
        :param vm_sizes: vm_sizes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_sizes StatefulNodeAzure#vm_sizes}
        :param attach_data_disk: attach_data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#attach_data_disk StatefulNodeAzure#attach_data_disk}
        :param boot_diagnostics: boot_diagnostics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#boot_diagnostics StatefulNodeAzure#boot_diagnostics}
        :param custom_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_data StatefulNodeAzure#custom_data}.
        :param data_disk: data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk StatefulNodeAzure#data_disk}
        :param data_disks_persistence_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disks_persistence_mode StatefulNodeAzure#data_disks_persistence_mode}.
        :param delete: delete block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#delete StatefulNodeAzure#delete}
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#description StatefulNodeAzure#description}.
        :param detach_data_disk: detach_data_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#detach_data_disk StatefulNodeAzure#detach_data_disk}
        :param extension: extension block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#extension StatefulNodeAzure#extension}
        :param health: health block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#health StatefulNodeAzure#health}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#id StatefulNodeAzure#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image: image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#image StatefulNodeAzure#image}
        :param import_vm: import_vm block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#import_vm StatefulNodeAzure#import_vm}
        :param license_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#license_type StatefulNodeAzure#license_type}.
        :param load_balancer: load_balancer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#load_balancer StatefulNodeAzure#load_balancer}
        :param login: login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#login StatefulNodeAzure#login}
        :param managed_service_identities: managed_service_identities block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#managed_service_identities StatefulNodeAzure#managed_service_identities}
        :param network: network block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network StatefulNodeAzure#network}
        :param os_disk: os_disk block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os_disk StatefulNodeAzure#os_disk}
        :param os_disk_persistence_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os_disk_persistence_mode StatefulNodeAzure#os_disk_persistence_mode}.
        :param preferred_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_zone StatefulNodeAzure#preferred_zone}.
        :param proximity_placement_groups: proximity_placement_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#proximity_placement_groups StatefulNodeAzure#proximity_placement_groups}
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#scheduling_task StatefulNodeAzure#scheduling_task}
        :param secret: secret block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#secret StatefulNodeAzure#secret}
        :param security: security block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#security StatefulNodeAzure#security}
        :param shutdown_script: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#shutdown_script StatefulNodeAzure#shutdown_script}.
        :param signal: signal block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#signal StatefulNodeAzure#signal}
        :param tag: tag block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag StatefulNodeAzure#tag}
        :param update_state: update_state block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#update_state StatefulNodeAzure#update_state}
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#user_data StatefulNodeAzure#user_data}.
        :param vm_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_name StatefulNodeAzure#vm_name}.
        :param vm_name_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_name_prefix StatefulNodeAzure#vm_name_prefix}.
        :param zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#zones StatefulNodeAzure#zones}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(strategy, dict):
            strategy = StatefulNodeAzureStrategy(**strategy)
        if isinstance(vm_sizes, dict):
            vm_sizes = StatefulNodeAzureVmSizes(**vm_sizes)
        if isinstance(health, dict):
            health = StatefulNodeAzureHealth(**health)
        if isinstance(image, dict):
            image = StatefulNodeAzureImage(**image)
        if isinstance(login, dict):
            login = StatefulNodeAzureLogin(**login)
        if isinstance(network, dict):
            network = StatefulNodeAzureNetwork(**network)
        if isinstance(os_disk, dict):
            os_disk = StatefulNodeAzureOsDisk(**os_disk)
        if isinstance(security, dict):
            security = StatefulNodeAzureSecurity(**security)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dc9d46615263cce03aa63961496271cbe7bb049936d81ca31550780bc76ee81)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument os", value=os, expected_type=type_hints["os"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument should_persist_data_disks", value=should_persist_data_disks, expected_type=type_hints["should_persist_data_disks"])
            check_type(argname="argument should_persist_network", value=should_persist_network, expected_type=type_hints["should_persist_network"])
            check_type(argname="argument should_persist_os_disk", value=should_persist_os_disk, expected_type=type_hints["should_persist_os_disk"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument vm_sizes", value=vm_sizes, expected_type=type_hints["vm_sizes"])
            check_type(argname="argument attach_data_disk", value=attach_data_disk, expected_type=type_hints["attach_data_disk"])
            check_type(argname="argument boot_diagnostics", value=boot_diagnostics, expected_type=type_hints["boot_diagnostics"])
            check_type(argname="argument custom_data", value=custom_data, expected_type=type_hints["custom_data"])
            check_type(argname="argument data_disk", value=data_disk, expected_type=type_hints["data_disk"])
            check_type(argname="argument data_disks_persistence_mode", value=data_disks_persistence_mode, expected_type=type_hints["data_disks_persistence_mode"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument detach_data_disk", value=detach_data_disk, expected_type=type_hints["detach_data_disk"])
            check_type(argname="argument extension", value=extension, expected_type=type_hints["extension"])
            check_type(argname="argument health", value=health, expected_type=type_hints["health"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument import_vm", value=import_vm, expected_type=type_hints["import_vm"])
            check_type(argname="argument license_type", value=license_type, expected_type=type_hints["license_type"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument login", value=login, expected_type=type_hints["login"])
            check_type(argname="argument managed_service_identities", value=managed_service_identities, expected_type=type_hints["managed_service_identities"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument os_disk", value=os_disk, expected_type=type_hints["os_disk"])
            check_type(argname="argument os_disk_persistence_mode", value=os_disk_persistence_mode, expected_type=type_hints["os_disk_persistence_mode"])
            check_type(argname="argument preferred_zone", value=preferred_zone, expected_type=type_hints["preferred_zone"])
            check_type(argname="argument proximity_placement_groups", value=proximity_placement_groups, expected_type=type_hints["proximity_placement_groups"])
            check_type(argname="argument scheduling_task", value=scheduling_task, expected_type=type_hints["scheduling_task"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument security", value=security, expected_type=type_hints["security"])
            check_type(argname="argument shutdown_script", value=shutdown_script, expected_type=type_hints["shutdown_script"])
            check_type(argname="argument signal", value=signal, expected_type=type_hints["signal"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument update_state", value=update_state, expected_type=type_hints["update_state"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument vm_name", value=vm_name, expected_type=type_hints["vm_name"])
            check_type(argname="argument vm_name_prefix", value=vm_name_prefix, expected_type=type_hints["vm_name_prefix"])
            check_type(argname="argument zones", value=zones, expected_type=type_hints["zones"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "os": os,
            "region": region,
            "resource_group_name": resource_group_name,
            "should_persist_data_disks": should_persist_data_disks,
            "should_persist_network": should_persist_network,
            "should_persist_os_disk": should_persist_os_disk,
            "strategy": strategy,
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
        if attach_data_disk is not None:
            self._values["attach_data_disk"] = attach_data_disk
        if boot_diagnostics is not None:
            self._values["boot_diagnostics"] = boot_diagnostics
        if custom_data is not None:
            self._values["custom_data"] = custom_data
        if data_disk is not None:
            self._values["data_disk"] = data_disk
        if data_disks_persistence_mode is not None:
            self._values["data_disks_persistence_mode"] = data_disks_persistence_mode
        if delete is not None:
            self._values["delete"] = delete
        if description is not None:
            self._values["description"] = description
        if detach_data_disk is not None:
            self._values["detach_data_disk"] = detach_data_disk
        if extension is not None:
            self._values["extension"] = extension
        if health is not None:
            self._values["health"] = health
        if id is not None:
            self._values["id"] = id
        if image is not None:
            self._values["image"] = image
        if import_vm is not None:
            self._values["import_vm"] = import_vm
        if license_type is not None:
            self._values["license_type"] = license_type
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if login is not None:
            self._values["login"] = login
        if managed_service_identities is not None:
            self._values["managed_service_identities"] = managed_service_identities
        if network is not None:
            self._values["network"] = network
        if os_disk is not None:
            self._values["os_disk"] = os_disk
        if os_disk_persistence_mode is not None:
            self._values["os_disk_persistence_mode"] = os_disk_persistence_mode
        if preferred_zone is not None:
            self._values["preferred_zone"] = preferred_zone
        if proximity_placement_groups is not None:
            self._values["proximity_placement_groups"] = proximity_placement_groups
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
        if tag is not None:
            self._values["tag"] = tag
        if update_state is not None:
            self._values["update_state"] = update_state
        if user_data is not None:
            self._values["user_data"] = user_data
        if vm_name is not None:
            self._values["vm_name"] = vm_name
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def os(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os StatefulNodeAzure#os}.'''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#region StatefulNodeAzure#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def should_persist_data_disks(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_data_disks StatefulNodeAzure#should_persist_data_disks}.'''
        result = self._values.get("should_persist_data_disks")
        assert result is not None, "Required property 'should_persist_data_disks' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def should_persist_network(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_network StatefulNodeAzure#should_persist_network}.'''
        result = self._values.get("should_persist_network")
        assert result is not None, "Required property 'should_persist_network' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def should_persist_os_disk(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_persist_os_disk StatefulNodeAzure#should_persist_os_disk}.'''
        result = self._values.get("should_persist_os_disk")
        assert result is not None, "Required property 'should_persist_os_disk' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def strategy(self) -> "StatefulNodeAzureStrategy":
        '''strategy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#strategy StatefulNodeAzure#strategy}
        '''
        result = self._values.get("strategy")
        assert result is not None, "Required property 'strategy' is missing"
        return typing.cast("StatefulNodeAzureStrategy", result)

    @builtins.property
    def vm_sizes(self) -> "StatefulNodeAzureVmSizes":
        '''vm_sizes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_sizes StatefulNodeAzure#vm_sizes}
        '''
        result = self._values.get("vm_sizes")
        assert result is not None, "Required property 'vm_sizes' is missing"
        return typing.cast("StatefulNodeAzureVmSizes", result)

    @builtins.property
    def attach_data_disk(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureAttachDataDisk]]]:
        '''attach_data_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#attach_data_disk StatefulNodeAzure#attach_data_disk}
        '''
        result = self._values.get("attach_data_disk")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureAttachDataDisk]]], result)

    @builtins.property
    def boot_diagnostics(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureBootDiagnostics]]]:
        '''boot_diagnostics block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#boot_diagnostics StatefulNodeAzure#boot_diagnostics}
        '''
        result = self._values.get("boot_diagnostics")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureBootDiagnostics]]], result)

    @builtins.property
    def custom_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_data StatefulNodeAzure#custom_data}.'''
        result = self._values.get("custom_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_disk(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDataDisk"]]]:
        '''data_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk StatefulNodeAzure#data_disk}
        '''
        result = self._values.get("data_disk")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDataDisk"]]], result)

    @builtins.property
    def data_disks_persistence_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disks_persistence_mode StatefulNodeAzure#data_disks_persistence_mode}.'''
        result = self._values.get("data_disks_persistence_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDelete"]]]:
        '''delete block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#delete StatefulNodeAzure#delete}
        '''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDelete"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#description StatefulNodeAzure#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detach_data_disk(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDetachDataDisk"]]]:
        '''detach_data_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#detach_data_disk StatefulNodeAzure#detach_data_disk}
        '''
        result = self._values.get("detach_data_disk")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureDetachDataDisk"]]], result)

    @builtins.property
    def extension(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureExtension"]]]:
        '''extension block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#extension StatefulNodeAzure#extension}
        '''
        result = self._values.get("extension")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureExtension"]]], result)

    @builtins.property
    def health(self) -> typing.Optional["StatefulNodeAzureHealth"]:
        '''health block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#health StatefulNodeAzure#health}
        '''
        result = self._values.get("health")
        return typing.cast(typing.Optional["StatefulNodeAzureHealth"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#id StatefulNodeAzure#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional["StatefulNodeAzureImage"]:
        '''image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#image StatefulNodeAzure#image}
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional["StatefulNodeAzureImage"], result)

    @builtins.property
    def import_vm(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImportVm"]]]:
        '''import_vm block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#import_vm StatefulNodeAzure#import_vm}
        '''
        result = self._values.get("import_vm")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImportVm"]]], result)

    @builtins.property
    def license_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#license_type StatefulNodeAzure#license_type}.'''
        result = self._values.get("license_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureLoadBalancer"]]]:
        '''load_balancer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#load_balancer StatefulNodeAzure#load_balancer}
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureLoadBalancer"]]], result)

    @builtins.property
    def login(self) -> typing.Optional["StatefulNodeAzureLogin"]:
        '''login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#login StatefulNodeAzure#login}
        '''
        result = self._values.get("login")
        return typing.cast(typing.Optional["StatefulNodeAzureLogin"], result)

    @builtins.property
    def managed_service_identities(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureManagedServiceIdentities"]]]:
        '''managed_service_identities block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#managed_service_identities StatefulNodeAzure#managed_service_identities}
        '''
        result = self._values.get("managed_service_identities")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureManagedServiceIdentities"]]], result)

    @builtins.property
    def network(self) -> typing.Optional["StatefulNodeAzureNetwork"]:
        '''network block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network StatefulNodeAzure#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional["StatefulNodeAzureNetwork"], result)

    @builtins.property
    def os_disk(self) -> typing.Optional["StatefulNodeAzureOsDisk"]:
        '''os_disk block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os_disk StatefulNodeAzure#os_disk}
        '''
        result = self._values.get("os_disk")
        return typing.cast(typing.Optional["StatefulNodeAzureOsDisk"], result)

    @builtins.property
    def os_disk_persistence_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#os_disk_persistence_mode StatefulNodeAzure#os_disk_persistence_mode}.'''
        result = self._values.get("os_disk_persistence_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_zone StatefulNodeAzure#preferred_zone}.'''
        result = self._values.get("preferred_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proximity_placement_groups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureProximityPlacementGroups"]]]:
        '''proximity_placement_groups block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#proximity_placement_groups StatefulNodeAzure#proximity_placement_groups}
        '''
        result = self._values.get("proximity_placement_groups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureProximityPlacementGroups"]]], result)

    @builtins.property
    def scheduling_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSchedulingTask"]]]:
        '''scheduling_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#scheduling_task StatefulNodeAzure#scheduling_task}
        '''
        result = self._values.get("scheduling_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSchedulingTask"]]], result)

    @builtins.property
    def secret(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecret"]]]:
        '''secret block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#secret StatefulNodeAzure#secret}
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecret"]]], result)

    @builtins.property
    def security(self) -> typing.Optional["StatefulNodeAzureSecurity"]:
        '''security block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#security StatefulNodeAzure#security}
        '''
        result = self._values.get("security")
        return typing.cast(typing.Optional["StatefulNodeAzureSecurity"], result)

    @builtins.property
    def shutdown_script(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#shutdown_script StatefulNodeAzure#shutdown_script}.'''
        result = self._values.get("shutdown_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signal(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSignal"]]]:
        '''signal block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#signal StatefulNodeAzure#signal}
        '''
        result = self._values.get("signal")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSignal"]]], result)

    @builtins.property
    def tag(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureTag"]]]:
        '''tag block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag StatefulNodeAzure#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureTag"]]], result)

    @builtins.property
    def update_state(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureUpdateState"]]]:
        '''update_state block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#update_state StatefulNodeAzure#update_state}
        '''
        result = self._values.get("update_state")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureUpdateState"]]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#user_data StatefulNodeAzure#user_data}.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vm_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_name StatefulNodeAzure#vm_name}.'''
        result = self._values.get("vm_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vm_name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_name_prefix StatefulNodeAzure#vm_name_prefix}.'''
        result = self._values.get("vm_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#zones StatefulNodeAzure#zones}.'''
        result = self._values.get("zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDataDisk",
    jsii_struct_bases=[],
    name_mapping={"lun": "lun", "size_gb": "sizeGb", "type": "type"},
)
class StatefulNodeAzureDataDisk:
    def __init__(
        self,
        *,
        lun: jsii.Number,
        size_gb: jsii.Number,
        type: builtins.str,
    ) -> None:
        '''
        :param lun: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#lun StatefulNodeAzure#lun}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46bd427affbbcb57948aa812c8f8785f105b7d4362e40f869894797263b37461)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#lun StatefulNodeAzure#lun}.'''
        result = self._values.get("lun")
        assert result is not None, "Required property 'lun' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size_gb(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.'''
        result = self._values.get("size_gb")
        assert result is not None, "Required property 'size_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureDataDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureDataDiskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDataDiskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__147c6bba9d288d43999b0fbf41dfa1c907d967bcac9e1c8f95fa17af7e8f1255)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureDataDiskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7532cec5ad7e3b3cb054009484f612e0673db5d452796400cf96af0896c30c8e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureDataDiskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3905a1f785b578e49ada588786349f9f67255c047b7bf37972825a65fcb39e94)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d0c9ef9c3efa4a2ebf6fe0530be0b1f27b759e014e0b6f1053fa9a7ce99ca72)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b275c79aaa95f5b984a1435f0af387c134aaaec06df36d94fe1286f52e0a7315)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDataDisk]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDataDisk]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDataDisk]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e25052b27f3c7124599fb125fedf07844f50324e9b1a2e9339dc8ac24a20bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureDataDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDataDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57473a8186b5e59920cb6830e859332cade8af2e3464f1e0a495edcc96648d39)
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
            type_hints = typing.get_type_hints(_typecheckingstub__017b59ae557f5cb9385c8943e7c4e1ef162579e187e481953ea8e6171ac35f83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeGb")
    def size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeGb"))

    @size_gb.setter
    def size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af4983095b2f52e926ed26d468a9c87882640c545d6e6a38914192beace66f10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a94d22ac77e53dd422a0a795d3907b912d57f6a106e1e058298b6a7f90f4d28b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDataDisk]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDataDisk]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDataDisk]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cdaff2a888496fa2367a9da93fea7bd1c824455c209b46144478a2b36a88aaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDelete",
    jsii_struct_bases=[],
    name_mapping={
        "should_terminate_vm": "shouldTerminateVm",
        "disk_should_deallocate": "diskShouldDeallocate",
        "disk_ttl_in_hours": "diskTtlInHours",
        "network_should_deallocate": "networkShouldDeallocate",
        "network_ttl_in_hours": "networkTtlInHours",
        "public_ip_should_deallocate": "publicIpShouldDeallocate",
        "public_ip_ttl_in_hours": "publicIpTtlInHours",
        "should_deregister_from_lb": "shouldDeregisterFromLb",
        "should_revert_to_od": "shouldRevertToOd",
        "snapshot_should_deallocate": "snapshotShouldDeallocate",
        "snapshot_ttl_in_hours": "snapshotTtlInHours",
    },
)
class StatefulNodeAzureDelete:
    def __init__(
        self,
        *,
        should_terminate_vm: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        disk_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disk_ttl_in_hours: typing.Optional[jsii.Number] = None,
        network_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_ttl_in_hours: typing.Optional[jsii.Number] = None,
        public_ip_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        public_ip_ttl_in_hours: typing.Optional[jsii.Number] = None,
        should_deregister_from_lb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        should_revert_to_od: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        snapshot_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        snapshot_ttl_in_hours: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param should_terminate_vm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_terminate_vm StatefulNodeAzure#should_terminate_vm}.
        :param disk_should_deallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#disk_should_deallocate StatefulNodeAzure#disk_should_deallocate}.
        :param disk_ttl_in_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#disk_ttl_in_hours StatefulNodeAzure#disk_ttl_in_hours}.
        :param network_should_deallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_should_deallocate StatefulNodeAzure#network_should_deallocate}.
        :param network_ttl_in_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_ttl_in_hours StatefulNodeAzure#network_ttl_in_hours}.
        :param public_ip_should_deallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ip_should_deallocate StatefulNodeAzure#public_ip_should_deallocate}.
        :param public_ip_ttl_in_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ip_ttl_in_hours StatefulNodeAzure#public_ip_ttl_in_hours}.
        :param should_deregister_from_lb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_deregister_from_lb StatefulNodeAzure#should_deregister_from_lb}.
        :param should_revert_to_od: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_revert_to_od StatefulNodeAzure#should_revert_to_od}.
        :param snapshot_should_deallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#snapshot_should_deallocate StatefulNodeAzure#snapshot_should_deallocate}.
        :param snapshot_ttl_in_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#snapshot_ttl_in_hours StatefulNodeAzure#snapshot_ttl_in_hours}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ab16258cd4612bd33c67b2ba337c03d38eb9b497f3013464cd073ffd117fbd8)
            check_type(argname="argument should_terminate_vm", value=should_terminate_vm, expected_type=type_hints["should_terminate_vm"])
            check_type(argname="argument disk_should_deallocate", value=disk_should_deallocate, expected_type=type_hints["disk_should_deallocate"])
            check_type(argname="argument disk_ttl_in_hours", value=disk_ttl_in_hours, expected_type=type_hints["disk_ttl_in_hours"])
            check_type(argname="argument network_should_deallocate", value=network_should_deallocate, expected_type=type_hints["network_should_deallocate"])
            check_type(argname="argument network_ttl_in_hours", value=network_ttl_in_hours, expected_type=type_hints["network_ttl_in_hours"])
            check_type(argname="argument public_ip_should_deallocate", value=public_ip_should_deallocate, expected_type=type_hints["public_ip_should_deallocate"])
            check_type(argname="argument public_ip_ttl_in_hours", value=public_ip_ttl_in_hours, expected_type=type_hints["public_ip_ttl_in_hours"])
            check_type(argname="argument should_deregister_from_lb", value=should_deregister_from_lb, expected_type=type_hints["should_deregister_from_lb"])
            check_type(argname="argument should_revert_to_od", value=should_revert_to_od, expected_type=type_hints["should_revert_to_od"])
            check_type(argname="argument snapshot_should_deallocate", value=snapshot_should_deallocate, expected_type=type_hints["snapshot_should_deallocate"])
            check_type(argname="argument snapshot_ttl_in_hours", value=snapshot_ttl_in_hours, expected_type=type_hints["snapshot_ttl_in_hours"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "should_terminate_vm": should_terminate_vm,
        }
        if disk_should_deallocate is not None:
            self._values["disk_should_deallocate"] = disk_should_deallocate
        if disk_ttl_in_hours is not None:
            self._values["disk_ttl_in_hours"] = disk_ttl_in_hours
        if network_should_deallocate is not None:
            self._values["network_should_deallocate"] = network_should_deallocate
        if network_ttl_in_hours is not None:
            self._values["network_ttl_in_hours"] = network_ttl_in_hours
        if public_ip_should_deallocate is not None:
            self._values["public_ip_should_deallocate"] = public_ip_should_deallocate
        if public_ip_ttl_in_hours is not None:
            self._values["public_ip_ttl_in_hours"] = public_ip_ttl_in_hours
        if should_deregister_from_lb is not None:
            self._values["should_deregister_from_lb"] = should_deregister_from_lb
        if should_revert_to_od is not None:
            self._values["should_revert_to_od"] = should_revert_to_od
        if snapshot_should_deallocate is not None:
            self._values["snapshot_should_deallocate"] = snapshot_should_deallocate
        if snapshot_ttl_in_hours is not None:
            self._values["snapshot_ttl_in_hours"] = snapshot_ttl_in_hours

    @builtins.property
    def should_terminate_vm(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_terminate_vm StatefulNodeAzure#should_terminate_vm}.'''
        result = self._values.get("should_terminate_vm")
        assert result is not None, "Required property 'should_terminate_vm' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def disk_should_deallocate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#disk_should_deallocate StatefulNodeAzure#disk_should_deallocate}.'''
        result = self._values.get("disk_should_deallocate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disk_ttl_in_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#disk_ttl_in_hours StatefulNodeAzure#disk_ttl_in_hours}.'''
        result = self._values.get("disk_ttl_in_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_should_deallocate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_should_deallocate StatefulNodeAzure#network_should_deallocate}.'''
        result = self._values.get("network_should_deallocate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def network_ttl_in_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_ttl_in_hours StatefulNodeAzure#network_ttl_in_hours}.'''
        result = self._values.get("network_ttl_in_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def public_ip_should_deallocate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ip_should_deallocate StatefulNodeAzure#public_ip_should_deallocate}.'''
        result = self._values.get("public_ip_should_deallocate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def public_ip_ttl_in_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ip_ttl_in_hours StatefulNodeAzure#public_ip_ttl_in_hours}.'''
        result = self._values.get("public_ip_ttl_in_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def should_deregister_from_lb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_deregister_from_lb StatefulNodeAzure#should_deregister_from_lb}.'''
        result = self._values.get("should_deregister_from_lb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def should_revert_to_od(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_revert_to_od StatefulNodeAzure#should_revert_to_od}.'''
        result = self._values.get("should_revert_to_od")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def snapshot_should_deallocate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#snapshot_should_deallocate StatefulNodeAzure#snapshot_should_deallocate}.'''
        result = self._values.get("snapshot_should_deallocate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def snapshot_ttl_in_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#snapshot_ttl_in_hours StatefulNodeAzure#snapshot_ttl_in_hours}.'''
        result = self._values.get("snapshot_ttl_in_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureDelete(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureDeleteList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDeleteList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b65a5c6e1b20481f582f2b915ebed62652624564d7ebbdf36052dd8ab22b722f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureDeleteOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8841cf3edf612c0f6a6407ebd416201506148b483a901b1aabd3b8480f2379d2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureDeleteOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61fa96a0f668597899159ad405c93fbed418437966f09a2e55f708a0bffdaa1c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea6cfef546af4433ea94f0165624cb3353d965fae471175fe109f2a638afaad0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ceebd77e50a2ae03ce64d7d372a44e3e906c0d01a2202190134c5a768c6b34f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDelete]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDelete]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDelete]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c19333ade9bee5af9313cc085a59e32244e6f3c91950171b3e9dab102462a612)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureDeleteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDeleteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d2240f639bf70da48909d7744335325dd9080893a225271c9b90273cfb79396)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDiskShouldDeallocate")
    def reset_disk_should_deallocate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskShouldDeallocate", []))

    @jsii.member(jsii_name="resetDiskTtlInHours")
    def reset_disk_ttl_in_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskTtlInHours", []))

    @jsii.member(jsii_name="resetNetworkShouldDeallocate")
    def reset_network_should_deallocate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkShouldDeallocate", []))

    @jsii.member(jsii_name="resetNetworkTtlInHours")
    def reset_network_ttl_in_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkTtlInHours", []))

    @jsii.member(jsii_name="resetPublicIpShouldDeallocate")
    def reset_public_ip_should_deallocate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicIpShouldDeallocate", []))

    @jsii.member(jsii_name="resetPublicIpTtlInHours")
    def reset_public_ip_ttl_in_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicIpTtlInHours", []))

    @jsii.member(jsii_name="resetShouldDeregisterFromLb")
    def reset_should_deregister_from_lb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldDeregisterFromLb", []))

    @jsii.member(jsii_name="resetShouldRevertToOd")
    def reset_should_revert_to_od(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldRevertToOd", []))

    @jsii.member(jsii_name="resetSnapshotShouldDeallocate")
    def reset_snapshot_should_deallocate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotShouldDeallocate", []))

    @jsii.member(jsii_name="resetSnapshotTtlInHours")
    def reset_snapshot_ttl_in_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotTtlInHours", []))

    @builtins.property
    @jsii.member(jsii_name="diskShouldDeallocateInput")
    def disk_should_deallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "diskShouldDeallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="diskTtlInHoursInput")
    def disk_ttl_in_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "diskTtlInHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="networkShouldDeallocateInput")
    def network_should_deallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "networkShouldDeallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="networkTtlInHoursInput")
    def network_ttl_in_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "networkTtlInHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="publicIpShouldDeallocateInput")
    def public_ip_should_deallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "publicIpShouldDeallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="publicIpTtlInHoursInput")
    def public_ip_ttl_in_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "publicIpTtlInHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldDeregisterFromLbInput")
    def should_deregister_from_lb_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldDeregisterFromLbInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldRevertToOdInput")
    def should_revert_to_od_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldRevertToOdInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldTerminateVmInput")
    def should_terminate_vm_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldTerminateVmInput"))

    @builtins.property
    @jsii.member(jsii_name="snapshotShouldDeallocateInput")
    def snapshot_should_deallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "snapshotShouldDeallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="snapshotTtlInHoursInput")
    def snapshot_ttl_in_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "snapshotTtlInHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="diskShouldDeallocate")
    def disk_should_deallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "diskShouldDeallocate"))

    @disk_should_deallocate.setter
    def disk_should_deallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47f120509966c51a311e9efd278caf3a4c1629086bc07b391430e813a67bf743)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskShouldDeallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskTtlInHours")
    def disk_ttl_in_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskTtlInHours"))

    @disk_ttl_in_hours.setter
    def disk_ttl_in_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ba3932257a965b634154c67c823b5fe9a50b904d32d2c5130520cf53eee3795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskTtlInHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkShouldDeallocate")
    def network_should_deallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "networkShouldDeallocate"))

    @network_should_deallocate.setter
    def network_should_deallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7df51c22dc9e1aa6d08f31a8e8898d35fc9450e5fdb0fd40f4fa2c0874ac002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkShouldDeallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkTtlInHours")
    def network_ttl_in_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "networkTtlInHours"))

    @network_ttl_in_hours.setter
    def network_ttl_in_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07eaf635a0ee130ae1ff9ea3f25a3afc1efb38e71b879dfb2d13db6420925242)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkTtlInHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicIpShouldDeallocate")
    def public_ip_should_deallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "publicIpShouldDeallocate"))

    @public_ip_should_deallocate.setter
    def public_ip_should_deallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfcaf6262908636179a6018c3ff127e2d1df0b52089b45e7ef2c48d09b8ca890)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicIpShouldDeallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicIpTtlInHours")
    def public_ip_ttl_in_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "publicIpTtlInHours"))

    @public_ip_ttl_in_hours.setter
    def public_ip_ttl_in_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b564e7184250320c2015540ce0e7fe0422769686e1487383d7de6524de5a037)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicIpTtlInHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldDeregisterFromLb")
    def should_deregister_from_lb(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldDeregisterFromLb"))

    @should_deregister_from_lb.setter
    def should_deregister_from_lb(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77cb40a610d936aac18b22ff51efe90b97ba2252f733296ff0482f626d02457c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldDeregisterFromLb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldRevertToOd")
    def should_revert_to_od(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldRevertToOd"))

    @should_revert_to_od.setter
    def should_revert_to_od(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33d62160e03d23bed8e0699432da50e6f55d066736539f1436cc0a82b05f074f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldRevertToOd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldTerminateVm")
    def should_terminate_vm(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldTerminateVm"))

    @should_terminate_vm.setter
    def should_terminate_vm(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72d8e0e5cf53c3b05416eb336b64d9c96b1ce41f66e4bc71780f3ebce6334feb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldTerminateVm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="snapshotShouldDeallocate")
    def snapshot_should_deallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "snapshotShouldDeallocate"))

    @snapshot_should_deallocate.setter
    def snapshot_should_deallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d6451916f3302d77c4b0edcb9fdf2054d06876559551a219bf0cdeebf256a9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snapshotShouldDeallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="snapshotTtlInHours")
    def snapshot_ttl_in_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotTtlInHours"))

    @snapshot_ttl_in_hours.setter
    def snapshot_ttl_in_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27bdc411ed3d70b186b40aa891e3c5eb70c5d7c645afe795132398646ae0148d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snapshotTtlInHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDelete]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDelete]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDelete]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beb65a74718c3bd895ff48e53c3496fe10cfccb4ea3dd7ca9e0d767b8acc9b16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDetachDataDisk",
    jsii_struct_bases=[],
    name_mapping={
        "data_disk_name": "dataDiskName",
        "data_disk_resource_group_name": "dataDiskResourceGroupName",
        "should_deallocate": "shouldDeallocate",
        "ttl_in_hours": "ttlInHours",
    },
)
class StatefulNodeAzureDetachDataDisk:
    def __init__(
        self,
        *,
        data_disk_name: builtins.str,
        data_disk_resource_group_name: builtins.str,
        should_deallocate: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        ttl_in_hours: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param data_disk_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_name StatefulNodeAzure#data_disk_name}.
        :param data_disk_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_resource_group_name StatefulNodeAzure#data_disk_resource_group_name}.
        :param should_deallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_deallocate StatefulNodeAzure#should_deallocate}.
        :param ttl_in_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#ttl_in_hours StatefulNodeAzure#ttl_in_hours}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e040369f3ebbca96835e78cefa0697195372ddb6757a199c5bd860971551c59e)
            check_type(argname="argument data_disk_name", value=data_disk_name, expected_type=type_hints["data_disk_name"])
            check_type(argname="argument data_disk_resource_group_name", value=data_disk_resource_group_name, expected_type=type_hints["data_disk_resource_group_name"])
            check_type(argname="argument should_deallocate", value=should_deallocate, expected_type=type_hints["should_deallocate"])
            check_type(argname="argument ttl_in_hours", value=ttl_in_hours, expected_type=type_hints["ttl_in_hours"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_disk_name": data_disk_name,
            "data_disk_resource_group_name": data_disk_resource_group_name,
            "should_deallocate": should_deallocate,
        }
        if ttl_in_hours is not None:
            self._values["ttl_in_hours"] = ttl_in_hours

    @builtins.property
    def data_disk_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_name StatefulNodeAzure#data_disk_name}.'''
        result = self._values.get("data_disk_name")
        assert result is not None, "Required property 'data_disk_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_disk_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#data_disk_resource_group_name StatefulNodeAzure#data_disk_resource_group_name}.'''
        result = self._values.get("data_disk_resource_group_name")
        assert result is not None, "Required property 'data_disk_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def should_deallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_deallocate StatefulNodeAzure#should_deallocate}.'''
        result = self._values.get("should_deallocate")
        assert result is not None, "Required property 'should_deallocate' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def ttl_in_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#ttl_in_hours StatefulNodeAzure#ttl_in_hours}.'''
        result = self._values.get("ttl_in_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureDetachDataDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureDetachDataDiskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDetachDataDiskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a949ab9c1f61194108b58638ea038c1073d3bd38f69cfbc001c205ce9d60b56)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureDetachDataDiskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b74b17559f326d68a34f966b6a1c099d68b171f5869f905c5558667e061c6808)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureDetachDataDiskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__046c751031ca6be1e7d725a5e9bf2ac64c31de51ef29266446bdfb88680bce24)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6fd2fb505ae0cfcb1f0cd1962002001d77368c317bc4b0f0585b2e9859cca6f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__12d03def7f163a19f7aec955759f0e5fd0b0548c484d256819901cc6681ac460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDetachDataDisk]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDetachDataDisk]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDetachDataDisk]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__980b7eb6eb2977246ff6ce4704b896ab3e37d85d68bfa5c75ca92f9a3226e200)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureDetachDataDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureDetachDataDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4282c0ae89fb12614c716cc13ccb90629bbbc86f452e02730b656b3273b8693d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetTtlInHours")
    def reset_ttl_in_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtlInHours", []))

    @builtins.property
    @jsii.member(jsii_name="dataDiskNameInput")
    def data_disk_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataDiskNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDiskResourceGroupNameInput")
    def data_disk_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataDiskResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldDeallocateInput")
    def should_deallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldDeallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInHoursInput")
    def ttl_in_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="dataDiskName")
    def data_disk_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataDiskName"))

    @data_disk_name.setter
    def data_disk_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__718b1bcf35a44198029514ee45c1f2d9f07722901ffe7317496cec29b2bbe1d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataDiskName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataDiskResourceGroupName")
    def data_disk_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataDiskResourceGroupName"))

    @data_disk_resource_group_name.setter
    def data_disk_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4495bf55e5a5d0a645346d30ec4a0f506ac09731b980bb8b76739aa15fcf3d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataDiskResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldDeallocate")
    def should_deallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldDeallocate"))

    @should_deallocate.setter
    def should_deallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66b08f4db8f3324e2f8af3d94c0f70d5429864bc8eeefbe1cc17c928b83e7af9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldDeallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttlInHours")
    def ttl_in_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttlInHours"))

    @ttl_in_hours.setter
    def ttl_in_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e100aa3ae8b9f0ba75afc353778df86afb97ca6e521e3896075f13562b4f41f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttlInHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDetachDataDisk]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDetachDataDisk]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDetachDataDisk]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d4494fc0f39f9f43b448b48e6ce0a5d9a51b1915790677d5dd686fcb4090e72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureExtension",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "minor_version_auto_upgrade": "minorVersionAutoUpgrade",
        "name": "name",
        "publisher": "publisher",
        "type": "type",
        "protected_settings": "protectedSettings",
        "public_settings": "publicSettings",
    },
)
class StatefulNodeAzureExtension:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        minor_version_auto_upgrade: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        name: builtins.str,
        publisher: builtins.str,
        type: builtins.str,
        protected_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        public_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param api_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#api_version StatefulNodeAzure#api_version}.
        :param minor_version_auto_upgrade: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#minor_version_auto_upgrade StatefulNodeAzure#minor_version_auto_upgrade}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param publisher: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#publisher StatefulNodeAzure#publisher}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        :param protected_settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#protected_settings StatefulNodeAzure#protected_settings}.
        :param public_settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_settings StatefulNodeAzure#public_settings}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eb654f27722bcb038b48941682fbcd1c89eccb3736e403d55bdfda25f6db19e)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument minor_version_auto_upgrade", value=minor_version_auto_upgrade, expected_type=type_hints["minor_version_auto_upgrade"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument publisher", value=publisher, expected_type=type_hints["publisher"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument protected_settings", value=protected_settings, expected_type=type_hints["protected_settings"])
            check_type(argname="argument public_settings", value=public_settings, expected_type=type_hints["public_settings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "minor_version_auto_upgrade": minor_version_auto_upgrade,
            "name": name,
            "publisher": publisher,
            "type": type,
        }
        if protected_settings is not None:
            self._values["protected_settings"] = protected_settings
        if public_settings is not None:
            self._values["public_settings"] = public_settings

    @builtins.property
    def api_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#api_version StatefulNodeAzure#api_version}.'''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def minor_version_auto_upgrade(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#minor_version_auto_upgrade StatefulNodeAzure#minor_version_auto_upgrade}.'''
        result = self._values.get("minor_version_auto_upgrade")
        assert result is not None, "Required property 'minor_version_auto_upgrade' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def publisher(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#publisher StatefulNodeAzure#publisher}.'''
        result = self._values.get("publisher")
        assert result is not None, "Required property 'publisher' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def protected_settings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#protected_settings StatefulNodeAzure#protected_settings}.'''
        result = self._values.get("protected_settings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def public_settings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_settings StatefulNodeAzure#public_settings}.'''
        result = self._values.get("public_settings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureExtension(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureExtensionList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureExtensionList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0956f0418dd194f83d89dbf3170003722816d759ec807601e49166096bf44a9f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureExtensionOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48567fd6118fa59cde500b8fccb2b785fdd178e64963148f72e4300f13bfeeaa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureExtensionOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c322ac63a7a22bde485bb62c3d1a7ab2c10f999d715f96c391f3ab4bf000264c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0875e4c46578185900487b752fbf4f9f2aed2b96967ededecf486236538243e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a39c37c0f89e871c429d446178677ecaeb6ffa0dbbed15dbaf0665eb53237db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureExtension]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureExtension]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureExtension]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__863d1fa54e9f8dc19118b60880c3a5b69cd3c40fc0ed17f58c99e18d932b05f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureExtensionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureExtensionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5a0c6f19fb6b963d9fd65f1080574cee3093d80b1d5b0bce1660f426e92b236f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetProtectedSettings")
    def reset_protected_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectedSettings", []))

    @jsii.member(jsii_name="resetPublicSettings")
    def reset_public_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicSettings", []))

    @builtins.property
    @jsii.member(jsii_name="apiVersionInput")
    def api_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiVersionInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__0760344e21c0083c804006e9b804600159ffe57b900d67fb789246f61fb4e6f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiVersion", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__ef45cd8c3d3346ae788baa53502cfa8866926f51556fc4fe0d0cd694bdf89767)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minorVersionAutoUpgrade", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ac1630a4698380a243f89e9545370d14d67567227414ac9bc80f08f53211f3a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7837c5a51a67e35e4ecd2047813d5e3fea8fb8b04ab7bbfa3d0ba87fcf3bfc97)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a78f843611a0c9e35d30677a9aae9d7c2400aaf5d3402d3f4b4b1d3b6438ec94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicSettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publisher")
    def publisher(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publisher"))

    @publisher.setter
    def publisher(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__849d257d6c61631aaa200c0de5e7b21ed52ee7fe1e9c7547364c2bfd2a2eb482)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publisher", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3239082acbdb30b36046f5117bb77aa66f505718536ee12158d6a735e6304d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureExtension]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureExtension]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureExtension]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09810de1a45f64f0c3a4887e417bad454ff3686a5c5399b71bc159cfac868f3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureHealth",
    jsii_struct_bases=[],
    name_mapping={
        "auto_healing": "autoHealing",
        "health_check_types": "healthCheckTypes",
        "grace_period": "gracePeriod",
        "unhealthy_duration": "unhealthyDuration",
    },
)
class StatefulNodeAzureHealth:
    def __init__(
        self,
        *,
        auto_healing: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        health_check_types: typing.Sequence[builtins.str],
        grace_period: typing.Optional[jsii.Number] = None,
        unhealthy_duration: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param auto_healing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#auto_healing StatefulNodeAzure#auto_healing}.
        :param health_check_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#health_check_types StatefulNodeAzure#health_check_types}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#grace_period StatefulNodeAzure#grace_period}.
        :param unhealthy_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#unhealthy_duration StatefulNodeAzure#unhealthy_duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73a02caf1b4c25a57b44eec6babc2145e0117e0e2c1115d11b4f05689d512c80)
            check_type(argname="argument auto_healing", value=auto_healing, expected_type=type_hints["auto_healing"])
            check_type(argname="argument health_check_types", value=health_check_types, expected_type=type_hints["health_check_types"])
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
            check_type(argname="argument unhealthy_duration", value=unhealthy_duration, expected_type=type_hints["unhealthy_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auto_healing": auto_healing,
            "health_check_types": health_check_types,
        }
        if grace_period is not None:
            self._values["grace_period"] = grace_period
        if unhealthy_duration is not None:
            self._values["unhealthy_duration"] = unhealthy_duration

    @builtins.property
    def auto_healing(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#auto_healing StatefulNodeAzure#auto_healing}.'''
        result = self._values.get("auto_healing")
        assert result is not None, "Required property 'auto_healing' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def health_check_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#health_check_types StatefulNodeAzure#health_check_types}.'''
        result = self._values.get("health_check_types")
        assert result is not None, "Required property 'health_check_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def grace_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#grace_period StatefulNodeAzure#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def unhealthy_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#unhealthy_duration StatefulNodeAzure#unhealthy_duration}.'''
        result = self._values.get("unhealthy_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureHealth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureHealthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureHealthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c4d859a2b6ea96c99775ed97984d50e1a5f035d44ca1bd6c512f960f8041549)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__304f94a2c2cf4b3e67d04cb6c3af01622dee6141ed16dcbfcda8e2e34bfa7a7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoHealing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54d0b6617690e92041262ea6244673f9749e6444f0a06e75b6b5239a0333f594)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gracePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthCheckTypes")
    def health_check_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "healthCheckTypes"))

    @health_check_types.setter
    def health_check_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0674113eff7a4243138212c36ff9879cf613ac47caa5165477903548a4a9cd67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthCheckTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unhealthyDuration")
    def unhealthy_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unhealthyDuration"))

    @unhealthy_duration.setter
    def unhealthy_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb4aea834efbfb4a92bea90121d1fbb5bfcc0a68c2325479e116026f3f069e3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unhealthyDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureHealth]:
        return typing.cast(typing.Optional[StatefulNodeAzureHealth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureHealth]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1dbf64158ab1b13e01a3692ac4cf297f5212a555c40ae0b42df40a8231a7fb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImage",
    jsii_struct_bases=[],
    name_mapping={
        "custom_image": "customImage",
        "gallery": "gallery",
        "marketplace_image": "marketplaceImage",
    },
)
class StatefulNodeAzureImage:
    def __init__(
        self,
        *,
        custom_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImageCustomImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gallery: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImageGallery", typing.Dict[builtins.str, typing.Any]]]]] = None,
        marketplace_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureImageMarketplaceImage", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param custom_image: custom_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_image StatefulNodeAzure#custom_image}
        :param gallery: gallery block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery StatefulNodeAzure#gallery}
        :param marketplace_image: marketplace_image block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#marketplace_image StatefulNodeAzure#marketplace_image}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb7a1029046889a479ad40042cb3c9f03c10a9bfab03d0e3abe67bc2a818eb5f)
            check_type(argname="argument custom_image", value=custom_image, expected_type=type_hints["custom_image"])
            check_type(argname="argument gallery", value=gallery, expected_type=type_hints["gallery"])
            check_type(argname="argument marketplace_image", value=marketplace_image, expected_type=type_hints["marketplace_image"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if custom_image is not None:
            self._values["custom_image"] = custom_image
        if gallery is not None:
            self._values["gallery"] = gallery
        if marketplace_image is not None:
            self._values["marketplace_image"] = marketplace_image

    @builtins.property
    def custom_image(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImageCustomImage"]]]:
        '''custom_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_image StatefulNodeAzure#custom_image}
        '''
        result = self._values.get("custom_image")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImageCustomImage"]]], result)

    @builtins.property
    def gallery(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImageGallery"]]]:
        '''gallery block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery StatefulNodeAzure#gallery}
        '''
        result = self._values.get("gallery")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImageGallery"]]], result)

    @builtins.property
    def marketplace_image(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImageMarketplaceImage"]]]:
        '''marketplace_image block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#marketplace_image StatefulNodeAzure#marketplace_image}
        '''
        result = self._values.get("marketplace_image")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureImageMarketplaceImage"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageCustomImage",
    jsii_struct_bases=[],
    name_mapping={
        "custom_image_resource_group_name": "customImageResourceGroupName",
        "name": "name",
    },
)
class StatefulNodeAzureImageCustomImage:
    def __init__(
        self,
        *,
        custom_image_resource_group_name: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param custom_image_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_image_resource_group_name StatefulNodeAzure#custom_image_resource_group_name}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f8f3fb8ebd08c5e2821a8f6112a304c3f422576e849be1be6d7b08b1f422f3a)
            check_type(argname="argument custom_image_resource_group_name", value=custom_image_resource_group_name, expected_type=type_hints["custom_image_resource_group_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "custom_image_resource_group_name": custom_image_resource_group_name,
            "name": name,
        }

    @builtins.property
    def custom_image_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#custom_image_resource_group_name StatefulNodeAzure#custom_image_resource_group_name}.'''
        result = self._values.get("custom_image_resource_group_name")
        assert result is not None, "Required property 'custom_image_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureImageCustomImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureImageCustomImageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageCustomImageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b2129e79f55ef4fa649daae1608bbb8845d006a755554e7b2c9642f632bc8fe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureImageCustomImageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f15c29b36fd45116a0373ba27869bd0cc674fe488b1f78374d5db6790b0468)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureImageCustomImageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f2b7aee3c700922040217a89394de2e2a99aee62afd0f98f7be49fe45f6d7d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f4a1e5f598c74fda5bc1fa371dd0cd8b63ae51ba097bacf47ce6f5007d9aa803)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58c26f425a3cb0611641d6bdca207df67e45725274d62fc7b0444244691552c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageCustomImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageCustomImage]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageCustomImage]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b6ec25baa161d4c2a3e6e0fd843dfeebdda07ecdb12c3e264acf3d05a45d13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureImageCustomImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageCustomImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dbb6dd311f8b2c0bc2c33b71e133ab9579a987501d05baa5e7f748dc4544a582)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="customImageResourceGroupNameInput")
    def custom_image_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customImageResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="customImageResourceGroupName")
    def custom_image_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customImageResourceGroupName"))

    @custom_image_resource_group_name.setter
    def custom_image_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__489ed4df2123046ed7bb1368088f8c3f8fc6a0f84b6f5019b08050d9200dca55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customImageResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a90d87ca5ff9fcc336954e2b6c231ac70fd15a2c94f0ae5ec99ccd3f52950af7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageCustomImage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageCustomImage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageCustomImage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__647e15b61ee53348f5d0f4e2610bbe1a8fa7ffca40836e9e7f5b48613057e6c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageGallery",
    jsii_struct_bases=[],
    name_mapping={
        "gallery_name": "galleryName",
        "gallery_resource_group_name": "galleryResourceGroupName",
        "image_name": "imageName",
        "version_name": "versionName",
        "spot_account_id": "spotAccountId",
    },
)
class StatefulNodeAzureImageGallery:
    def __init__(
        self,
        *,
        gallery_name: builtins.str,
        gallery_resource_group_name: builtins.str,
        image_name: builtins.str,
        version_name: builtins.str,
        spot_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param gallery_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery_name StatefulNodeAzure#gallery_name}.
        :param gallery_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery_resource_group_name StatefulNodeAzure#gallery_resource_group_name}.
        :param image_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#image_name StatefulNodeAzure#image_name}.
        :param version_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#version_name StatefulNodeAzure#version_name}.
        :param spot_account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_account_id StatefulNodeAzure#spot_account_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6297cf253ba8dfc737c1672fbe7ea747e12e248a5314e687fe414164629c62e)
            check_type(argname="argument gallery_name", value=gallery_name, expected_type=type_hints["gallery_name"])
            check_type(argname="argument gallery_resource_group_name", value=gallery_resource_group_name, expected_type=type_hints["gallery_resource_group_name"])
            check_type(argname="argument image_name", value=image_name, expected_type=type_hints["image_name"])
            check_type(argname="argument version_name", value=version_name, expected_type=type_hints["version_name"])
            check_type(argname="argument spot_account_id", value=spot_account_id, expected_type=type_hints["spot_account_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "gallery_name": gallery_name,
            "gallery_resource_group_name": gallery_resource_group_name,
            "image_name": image_name,
            "version_name": version_name,
        }
        if spot_account_id is not None:
            self._values["spot_account_id"] = spot_account_id

    @builtins.property
    def gallery_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery_name StatefulNodeAzure#gallery_name}.'''
        result = self._values.get("gallery_name")
        assert result is not None, "Required property 'gallery_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def gallery_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#gallery_resource_group_name StatefulNodeAzure#gallery_resource_group_name}.'''
        result = self._values.get("gallery_resource_group_name")
        assert result is not None, "Required property 'gallery_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#image_name StatefulNodeAzure#image_name}.'''
        result = self._values.get("image_name")
        assert result is not None, "Required property 'image_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#version_name StatefulNodeAzure#version_name}.'''
        result = self._values.get("version_name")
        assert result is not None, "Required property 'version_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def spot_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_account_id StatefulNodeAzure#spot_account_id}.'''
        result = self._values.get("spot_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureImageGallery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureImageGalleryList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageGalleryList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd25e75d79cd3df17f6e6fdea36f0b0e6e458ee9547c0d704195d59a84d3baa0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureImageGalleryOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5accf099d2948a92b3024172efb74a07359f6033fb3e422697e1b03f65782939)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureImageGalleryOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dddaf874e1b73a32c3ea70f96dabe1a0cd84fc5f8f67046fb80bf2692251d420)
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
            type_hints = typing.get_type_hints(_typecheckingstub__827394886d83af0a0fc45a65f679bc1488098014bf3d47658253e3562ef2c844)
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
            type_hints = typing.get_type_hints(_typecheckingstub__447826dab3d348bdf7d6778084201a02f368f1d5623da620eb2eed67fca11368)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageGallery]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageGallery]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageGallery]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c269bcdbfb4e9988dd327b477dc768a4f32e773978bf7049bc46ae8d1bb06eaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureImageGalleryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageGalleryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db0483dc826407d49492fee66fff9cc56e9bc87ac0877ab01659ae4d6a24d60f)
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
    @jsii.member(jsii_name="galleryResourceGroupNameInput")
    def gallery_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "galleryResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="imageNameInput")
    def image_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageNameInput"))

    @builtins.property
    @jsii.member(jsii_name="spotAccountIdInput")
    def spot_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotAccountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="versionNameInput")
    def version_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="galleryName")
    def gallery_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "galleryName"))

    @gallery_name.setter
    def gallery_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4f09bc07e044e0cf94987110b28098bd8d20065d6eb28091cb9e4abd7610a92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "galleryName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="galleryResourceGroupName")
    def gallery_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "galleryResourceGroupName"))

    @gallery_resource_group_name.setter
    def gallery_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e074837d44f1da14ee3c971520d9d07b7d4f5c27fe29768b109d35612259bb6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "galleryResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imageName")
    def image_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageName"))

    @image_name.setter
    def image_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc1ed6a92e75b49e449549bc13650a030fa69b00bf619db181ad364176e9dd5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotAccountId")
    def spot_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotAccountId"))

    @spot_account_id.setter
    def spot_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e2fef43e00c2e5cbbe8b009fa777eaa33e2e66e6cc5c5e43008c2f58940f08b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotAccountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="versionName")
    def version_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionName"))

    @version_name.setter
    def version_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52e6400d8edc18ecc17428994802df01c5e53fb242d15c8e5d6688eaac3bd732)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "versionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageGallery]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageGallery]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageGallery]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b9ddebace9b4705dffeaeeca3b2d3c11a08c1081035008824eebf41ec833363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageMarketplaceImage",
    jsii_struct_bases=[],
    name_mapping={
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "version": "version",
    },
)
class StatefulNodeAzureImageMarketplaceImage:
    def __init__(
        self,
        *,
        offer: builtins.str,
        publisher: builtins.str,
        sku: builtins.str,
        version: builtins.str,
    ) -> None:
        '''
        :param offer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#offer StatefulNodeAzure#offer}.
        :param publisher: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#publisher StatefulNodeAzure#publisher}.
        :param sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#sku StatefulNodeAzure#sku}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#version StatefulNodeAzure#version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__466080c36e49501ae45aebfc75be36089f7eea101ada7ed3111f15f7e98e0f1c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#offer StatefulNodeAzure#offer}.'''
        result = self._values.get("offer")
        assert result is not None, "Required property 'offer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def publisher(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#publisher StatefulNodeAzure#publisher}.'''
        result = self._values.get("publisher")
        assert result is not None, "Required property 'publisher' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sku(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#sku StatefulNodeAzure#sku}.'''
        result = self._values.get("sku")
        assert result is not None, "Required property 'sku' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#version StatefulNodeAzure#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureImageMarketplaceImage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureImageMarketplaceImageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageMarketplaceImageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__16e861042675ef4aae25ee22a7a8fd2c423603317a56540450ff170923eabb16)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureImageMarketplaceImageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9df315e11f7ff515d90805e24abbbfcf62869b541e23e5023c58fcfa267617cb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureImageMarketplaceImageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0e3fadb0446998f92ca4b33145a5296a05e170e5e5c79e570ce68e2b07c5ec4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d009baa8ee2ef977fb775adf5815e944efdd5e7909bbe959360b2df2c4d6916)
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
            type_hints = typing.get_type_hints(_typecheckingstub__72df1ecda6387628e071133c19c5d8e1615eab4b38282e58e599699cdafd2d91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageMarketplaceImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageMarketplaceImage]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageMarketplaceImage]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9300f9da24cd3f7470f779569e25a640bc4567cff7e803a66d222e489c73761)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureImageMarketplaceImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageMarketplaceImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__612d2c0c124902c1ed79000175b6bf837282c1b82578d2e3e587b18f9302b5c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2cd070c99183239c1878eadbc8febe3cc8e614761257c701765d1ec50cf8e1d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "offer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publisher")
    def publisher(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publisher"))

    @publisher.setter
    def publisher(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78aedb905ff195b69a70574329a5337501934f890d3f2aab2aab5961de10b6e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publisher", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sku")
    def sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sku"))

    @sku.setter
    def sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c1f474836c9b5a42561ddb71c2d4d66419f62bb17087742bd223e5f2fb40a40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60bdc10bd84ddb0ef7aa075ff58883528d61a5e1b0cd8e0bd99cab7a19d46a2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageMarketplaceImage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageMarketplaceImage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageMarketplaceImage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2bd9be6cca6edf679cabbd20a03e78bcafd04752303920c3a044598a4b1bb2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureImageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9de9fc7a709f3fe1f02fe80f189e0ca49b43403c74f73094f3f2a4298d02d73d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCustomImage")
    def put_custom_image(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageCustomImage, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71be782dfe2b72216cbd7a3439bf8420600f17501e93c08cca99ee7f056bd6cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomImage", [value]))

    @jsii.member(jsii_name="putGallery")
    def put_gallery(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageGallery, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d580a204dede454c4110ac0d543eb68e69cf157d5ff7e2dce9f5f55468e5677)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGallery", [value]))

    @jsii.member(jsii_name="putMarketplaceImage")
    def put_marketplace_image(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageMarketplaceImage, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4121bcd674b4e86dd591141e8d7aa2c103ac9f4afdd20213382523553a16a3eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMarketplaceImage", [value]))

    @jsii.member(jsii_name="resetCustomImage")
    def reset_custom_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomImage", []))

    @jsii.member(jsii_name="resetGallery")
    def reset_gallery(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGallery", []))

    @jsii.member(jsii_name="resetMarketplaceImage")
    def reset_marketplace_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMarketplaceImage", []))

    @builtins.property
    @jsii.member(jsii_name="customImage")
    def custom_image(self) -> StatefulNodeAzureImageCustomImageList:
        return typing.cast(StatefulNodeAzureImageCustomImageList, jsii.get(self, "customImage"))

    @builtins.property
    @jsii.member(jsii_name="gallery")
    def gallery(self) -> StatefulNodeAzureImageGalleryList:
        return typing.cast(StatefulNodeAzureImageGalleryList, jsii.get(self, "gallery"))

    @builtins.property
    @jsii.member(jsii_name="marketplaceImage")
    def marketplace_image(self) -> StatefulNodeAzureImageMarketplaceImageList:
        return typing.cast(StatefulNodeAzureImageMarketplaceImageList, jsii.get(self, "marketplaceImage"))

    @builtins.property
    @jsii.member(jsii_name="customImageInput")
    def custom_image_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageCustomImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageCustomImage]]], jsii.get(self, "customImageInput"))

    @builtins.property
    @jsii.member(jsii_name="galleryInput")
    def gallery_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageGallery]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageGallery]]], jsii.get(self, "galleryInput"))

    @builtins.property
    @jsii.member(jsii_name="marketplaceImageInput")
    def marketplace_image_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageMarketplaceImage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageMarketplaceImage]]], jsii.get(self, "marketplaceImageInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureImage]:
        return typing.cast(typing.Optional[StatefulNodeAzureImage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureImage]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7384c56911d1c6e57e44608d0f9107b52b74775323ed6dc6c180e77aa49766d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImportVm",
    jsii_struct_bases=[],
    name_mapping={
        "original_vm_name": "originalVmName",
        "resource_group_name": "resourceGroupName",
        "draining_timeout": "drainingTimeout",
        "resources_retention_time": "resourcesRetentionTime",
    },
)
class StatefulNodeAzureImportVm:
    def __init__(
        self,
        *,
        original_vm_name: builtins.str,
        resource_group_name: builtins.str,
        draining_timeout: typing.Optional[jsii.Number] = None,
        resources_retention_time: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param original_vm_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#original_vm_name StatefulNodeAzure#original_vm_name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#draining_timeout StatefulNodeAzure#draining_timeout}.
        :param resources_retention_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resources_retention_time StatefulNodeAzure#resources_retention_time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be7351e844c3343bd940d98572583cee8d15b113039afea6c958d9814a056f83)
            check_type(argname="argument original_vm_name", value=original_vm_name, expected_type=type_hints["original_vm_name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument resources_retention_time", value=resources_retention_time, expected_type=type_hints["resources_retention_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "original_vm_name": original_vm_name,
            "resource_group_name": resource_group_name,
        }
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if resources_retention_time is not None:
            self._values["resources_retention_time"] = resources_retention_time

    @builtins.property
    def original_vm_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#original_vm_name StatefulNodeAzure#original_vm_name}.'''
        result = self._values.get("original_vm_name")
        assert result is not None, "Required property 'original_vm_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#draining_timeout StatefulNodeAzure#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resources_retention_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resources_retention_time StatefulNodeAzure#resources_retention_time}.'''
        result = self._values.get("resources_retention_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureImportVm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureImportVmList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImportVmList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57c1ee486e359cae50f47a85495ab873bc1ca73515b5df065f37eeb6bd3b24d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureImportVmOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c177f42e6153fc5dfc1ba09aef347592b2deaf5af56aa90e28b08b9cc5cf9c8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureImportVmOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23aed64b74ed4834e00a4dadd15a6a898a5728a4530e8aa92a4a486303177b0a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a1653b76e0a503f4159ad116ba93e2dad4cc20cbc4ff3346a3dbdc5cbbe50bb0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__687d586fdc7093c9705537d58a67b4b5c6d0ab3f60648b756bfa55d5575a06da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImportVm]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImportVm]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImportVm]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc958aaa5fc0604f94a9bdb9a50bd3d4f89d4290a6410374d5d2d6c88831b7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureImportVmOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureImportVmOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad4a406a9161348fc252ddf9d927a00a338ed5134cbd0cdde8063ed13fce6952)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetResourcesRetentionTime")
    def reset_resources_retention_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourcesRetentionTime", []))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="originalVmNameInput")
    def original_vm_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originalVmNameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourcesRetentionTimeInput")
    def resources_retention_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "resourcesRetentionTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__783869455be086aebf98344d2d5c96203e9bd2aaf9b401ddeb5ef510c74a6dfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainingTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originalVmName")
    def original_vm_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originalVmName"))

    @original_vm_name.setter
    def original_vm_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e027a50c55b28511a75b0bd8d3e1633ef6e84ce5323d8beaadc886afaba0e664)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originalVmName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8fd474359260a18f21eb7194079313a573aef47afcc0d83841984b33406ff79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourcesRetentionTime")
    def resources_retention_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "resourcesRetentionTime"))

    @resources_retention_time.setter
    def resources_retention_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc061fb0feee7a813952d3ad730f0b6d2465a3a61961611e79e6bc2f6ceae58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourcesRetentionTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImportVm]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImportVm]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImportVm]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd17d64c7d3b081c7c329ad53e49ff8f35b6b7e8ea273b7ddeec62e3995ed9d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureLoadBalancer",
    jsii_struct_bases=[],
    name_mapping={
        "backend_pool_names": "backendPoolNames",
        "name": "name",
        "resource_group_name": "resourceGroupName",
        "type": "type",
        "sku": "sku",
    },
)
class StatefulNodeAzureLoadBalancer:
    def __init__(
        self,
        *,
        backend_pool_names: typing.Sequence[builtins.str],
        name: builtins.str,
        resource_group_name: builtins.str,
        type: builtins.str,
        sku: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param backend_pool_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#backend_pool_names StatefulNodeAzure#backend_pool_names}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        :param sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#sku StatefulNodeAzure#sku}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1c173d323a1de47373890573be7888c6a1739ebdc119ffefb92df0eba0dada1)
            check_type(argname="argument backend_pool_names", value=backend_pool_names, expected_type=type_hints["backend_pool_names"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument sku", value=sku, expected_type=type_hints["sku"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend_pool_names": backend_pool_names,
            "name": name,
            "resource_group_name": resource_group_name,
            "type": type,
        }
        if sku is not None:
            self._values["sku"] = sku

    @builtins.property
    def backend_pool_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#backend_pool_names StatefulNodeAzure#backend_pool_names}.'''
        result = self._values.get("backend_pool_names")
        assert result is not None, "Required property 'backend_pool_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sku(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#sku StatefulNodeAzure#sku}.'''
        result = self._values.get("sku")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureLoadBalancer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureLoadBalancerList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureLoadBalancerList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f28e61306f5c4747b31b6486993faac8f7e02569f014fac339d416715b0b579e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureLoadBalancerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b231227197cf1b91533aa6744153b1a7e0088b38b1b70bec695c1432729f8040)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureLoadBalancerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b47ab51ccd3e16c40e464527265c89a4ec2e7e0747f1884dc2ef28547f784808)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ea8f37e1ea939a0f7d789ca0c90b89cb635d1f9dc66265a9aa72bf1b443c401)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b627fddc948b732a527c3043288ccf9cc9030b5243ce334770f9de56921a061c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureLoadBalancer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureLoadBalancer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureLoadBalancer]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e7c6f220045bee05bb763c81b59d1f4a71c250064e8c810e1e1e99a8ec91908)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureLoadBalancerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureLoadBalancerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__50c41532f8c2882639f2bbb241d7d97f6b3034d5f627d3dd5ba95c94ad699ce3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__df7b5bcccc266eda05ccf51ae6b77614757e3750761d6a2b8c7f56df13989ae0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backendPoolNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2920594e4105a65aa761a56633d27d7be04cb63197228a2e58c95f5368ddd209)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66deab7f0ae7a1438be21a333ce800ae0bc6f1a9bfa99dbfff6518e437585350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sku")
    def sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sku"))

    @sku.setter
    def sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f43b43c5067119808c45e369a5fa414a7a93bb8494b28e9d2dcfedb1b83b0df6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff1f62057873a3a7b41253966d33bf6ab7495b55f3c296cd2415a088f1b6476e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureLoadBalancer]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureLoadBalancer]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureLoadBalancer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd4aa6d67e79fd8a334613c2dbff61fa2098e66b12d1720dd54c3dffeced9247)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureLogin",
    jsii_struct_bases=[],
    name_mapping={
        "user_name": "userName",
        "password": "password",
        "ssh_public_key": "sshPublicKey",
    },
)
class StatefulNodeAzureLogin:
    def __init__(
        self,
        *,
        user_name: builtins.str,
        password: typing.Optional[builtins.str] = None,
        ssh_public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param user_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#user_name StatefulNodeAzure#user_name}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#password StatefulNodeAzure#password}.
        :param ssh_public_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#ssh_public_key StatefulNodeAzure#ssh_public_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96601510d4b06f6c38006df8b858f45883c0bc63e10c02a3610a4b5c7ca71948)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#user_name StatefulNodeAzure#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#password StatefulNodeAzure#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_public_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#ssh_public_key StatefulNodeAzure#ssh_public_key}.'''
        result = self._values.get("ssh_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b1a1b3aa8a2f241ec57bc3c4b0453c1fef4273caeb122d6c5e263ab292d3c5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdb17e1fa4a69d64fa42f4ee9d671ceeb20270679b14a437e49cdaa63fb8486b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshPublicKey")
    def ssh_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshPublicKey"))

    @ssh_public_key.setter
    def ssh_public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d09e207d3e2658be7c391d7423941f1a5dc2b18f37c23ea1722d24e8ce4f3c94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshPublicKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c62f3fa2e24ec1162d08f7eb1fcbfa9915a3bdcd14a09a76c97fe6e4d00c7e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureLogin]:
        return typing.cast(typing.Optional[StatefulNodeAzureLogin], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureLogin]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9247cc0278d8872cd75c060043c705ccb5a4f8494263927cd08bd899c5596e46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureManagedServiceIdentities",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "resource_group_name": "resourceGroupName",
        "subscription_id": "subscriptionId",
    },
)
class StatefulNodeAzureManagedServiceIdentities:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
        subscription_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        :param subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#subscription_id StatefulNodeAzure#subscription_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a824252485a42b849e2b2082e28aaa3207e7c5d895fb4666bad6d08fddd936f7)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }
        if subscription_id is not None:
            self._values["subscription_id"] = subscription_id

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscription_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#subscription_id StatefulNodeAzure#subscription_id}.'''
        result = self._values.get("subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureManagedServiceIdentities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureManagedServiceIdentitiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureManagedServiceIdentitiesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__88bfd7a2dcbef4de768598b0aa967fe370ae9c80d4d05b8c9691c59c79dbe783)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureManagedServiceIdentitiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac7a88fa1b044ba06853c5b4ba3f457feb2335a680ab48819d58578b92c59553)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureManagedServiceIdentitiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b41514df8d3e926ce168c1b1bd6bb883b1bd12e4f63f970468047848787ed334)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3291878154c567356cef354f704b5ccbe12a566420fa01df2f04de4a423c8d51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__885dbb59c307bcc496a709c3b971095ac832cd7e786464860bf38973d07a8169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureManagedServiceIdentities]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureManagedServiceIdentities]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureManagedServiceIdentities]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a6e238f7574dc1d31a84cc1490ca800c7e8b9c81998f69c5bf73285481c847e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureManagedServiceIdentitiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureManagedServiceIdentitiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd4ae959284b4d38d6b53db0f6130940ca3ecb33fe5f6f8957a8cf154a08a620)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetSubscriptionId")
    def reset_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionId", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dc302897dc66416e62b6614356d6d0c5ab7e73545125760a2e629a6b36438da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba03cfd03217db04e3672ab17187c7ab1627453d4dd23b0021d6a7687e0a0e3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba599bfbf6ab5c9c6e806fd32b8fc47889ee38e7858169032f1ba6d45244d17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureManagedServiceIdentities]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureManagedServiceIdentities]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureManagedServiceIdentities]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__493911c74bd9d8bae5507313c5778dd940e0ca4d67b73d47a0e954bae8743e7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetwork",
    jsii_struct_bases=[],
    name_mapping={
        "network_interface": "networkInterface",
        "network_resource_group_name": "networkResourceGroupName",
        "virtual_network_name": "virtualNetworkName",
    },
)
class StatefulNodeAzureNetwork:
    def __init__(
        self,
        *,
        network_interface: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterface", typing.Dict[builtins.str, typing.Any]]]],
        network_resource_group_name: builtins.str,
        virtual_network_name: builtins.str,
    ) -> None:
        '''
        :param network_interface: network_interface block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_interface StatefulNodeAzure#network_interface}
        :param network_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.
        :param virtual_network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#virtual_network_name StatefulNodeAzure#virtual_network_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9c917e00ecbfc11bf51b8c5b09f5bc5d55d32303b20b2658cc61dd98ce1d10f)
            check_type(argname="argument network_interface", value=network_interface, expected_type=type_hints["network_interface"])
            check_type(argname="argument network_resource_group_name", value=network_resource_group_name, expected_type=type_hints["network_resource_group_name"])
            check_type(argname="argument virtual_network_name", value=virtual_network_name, expected_type=type_hints["virtual_network_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network_interface": network_interface,
            "network_resource_group_name": network_resource_group_name,
            "virtual_network_name": virtual_network_name,
        }

    @builtins.property
    def network_interface(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterface"]]:
        '''network_interface block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_interface StatefulNodeAzure#network_interface}
        '''
        result = self._values.get("network_interface")
        assert result is not None, "Required property 'network_interface' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterface"]], result)

    @builtins.property
    def network_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.'''
        result = self._values.get("network_resource_group_name")
        assert result is not None, "Required property 'network_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_network_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#virtual_network_name StatefulNodeAzure#virtual_network_name}.'''
        result = self._values.get("virtual_network_name")
        assert result is not None, "Required property 'virtual_network_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureNetwork(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterface",
    jsii_struct_bases=[],
    name_mapping={
        "is_primary": "isPrimary",
        "subnet_name": "subnetName",
        "additional_ip_configurations": "additionalIpConfigurations",
        "application_security_groups": "applicationSecurityGroups",
        "assign_public_ip": "assignPublicIp",
        "enable_ip_forwarding": "enableIpForwarding",
        "network_security_group": "networkSecurityGroup",
        "private_ip_addresses": "privateIpAddresses",
        "public_ips": "publicIps",
        "public_ip_sku": "publicIpSku",
    },
)
class StatefulNodeAzureNetworkNetworkInterface:
    def __init__(
        self,
        *,
        is_primary: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        subnet_name: builtins.str,
        additional_ip_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations", typing.Dict[builtins.str, typing.Any]]]]] = None,
        application_security_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        assign_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        network_security_group: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup", typing.Dict[builtins.str, typing.Any]]]]] = None,
        private_ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        public_ips: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterfacePublicIps", typing.Dict[builtins.str, typing.Any]]]]] = None,
        public_ip_sku: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param is_primary: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#is_primary StatefulNodeAzure#is_primary}.
        :param subnet_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#subnet_name StatefulNodeAzure#subnet_name}.
        :param additional_ip_configurations: additional_ip_configurations block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#additional_ip_configurations StatefulNodeAzure#additional_ip_configurations}
        :param application_security_groups: application_security_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#application_security_groups StatefulNodeAzure#application_security_groups}
        :param assign_public_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#assign_public_ip StatefulNodeAzure#assign_public_ip}.
        :param enable_ip_forwarding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#enable_ip_forwarding StatefulNodeAzure#enable_ip_forwarding}.
        :param network_security_group: network_security_group block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_security_group StatefulNodeAzure#network_security_group}
        :param private_ip_addresses: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#private_ip_addresses StatefulNodeAzure#private_ip_addresses}.
        :param public_ips: public_ips block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ips StatefulNodeAzure#public_ips}
        :param public_ip_sku: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ip_sku StatefulNodeAzure#public_ip_sku}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55f0a16a5fe3e99e816d3cbe29fc093d4b8e1f174cde9053f89ecb804abe0a05)
            check_type(argname="argument is_primary", value=is_primary, expected_type=type_hints["is_primary"])
            check_type(argname="argument subnet_name", value=subnet_name, expected_type=type_hints["subnet_name"])
            check_type(argname="argument additional_ip_configurations", value=additional_ip_configurations, expected_type=type_hints["additional_ip_configurations"])
            check_type(argname="argument application_security_groups", value=application_security_groups, expected_type=type_hints["application_security_groups"])
            check_type(argname="argument assign_public_ip", value=assign_public_ip, expected_type=type_hints["assign_public_ip"])
            check_type(argname="argument enable_ip_forwarding", value=enable_ip_forwarding, expected_type=type_hints["enable_ip_forwarding"])
            check_type(argname="argument network_security_group", value=network_security_group, expected_type=type_hints["network_security_group"])
            check_type(argname="argument private_ip_addresses", value=private_ip_addresses, expected_type=type_hints["private_ip_addresses"])
            check_type(argname="argument public_ips", value=public_ips, expected_type=type_hints["public_ips"])
            check_type(argname="argument public_ip_sku", value=public_ip_sku, expected_type=type_hints["public_ip_sku"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "is_primary": is_primary,
            "subnet_name": subnet_name,
        }
        if additional_ip_configurations is not None:
            self._values["additional_ip_configurations"] = additional_ip_configurations
        if application_security_groups is not None:
            self._values["application_security_groups"] = application_security_groups
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if enable_ip_forwarding is not None:
            self._values["enable_ip_forwarding"] = enable_ip_forwarding
        if network_security_group is not None:
            self._values["network_security_group"] = network_security_group
        if private_ip_addresses is not None:
            self._values["private_ip_addresses"] = private_ip_addresses
        if public_ips is not None:
            self._values["public_ips"] = public_ips
        if public_ip_sku is not None:
            self._values["public_ip_sku"] = public_ip_sku

    @builtins.property
    def is_primary(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#is_primary StatefulNodeAzure#is_primary}.'''
        result = self._values.get("is_primary")
        assert result is not None, "Required property 'is_primary' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def subnet_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#subnet_name StatefulNodeAzure#subnet_name}.'''
        result = self._values.get("subnet_name")
        assert result is not None, "Required property 'subnet_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_ip_configurations(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations"]]]:
        '''additional_ip_configurations block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#additional_ip_configurations StatefulNodeAzure#additional_ip_configurations}
        '''
        result = self._values.get("additional_ip_configurations")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations"]]], result)

    @builtins.property
    def application_security_groups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups"]]]:
        '''application_security_groups block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#application_security_groups StatefulNodeAzure#application_security_groups}
        '''
        result = self._values.get("application_security_groups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups"]]], result)

    @builtins.property
    def assign_public_ip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#assign_public_ip StatefulNodeAzure#assign_public_ip}.'''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_ip_forwarding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#enable_ip_forwarding StatefulNodeAzure#enable_ip_forwarding}.'''
        result = self._values.get("enable_ip_forwarding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def network_security_group(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup"]]]:
        '''network_security_group block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_security_group StatefulNodeAzure#network_security_group}
        '''
        result = self._values.get("network_security_group")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup"]]], result)

    @builtins.property
    def private_ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#private_ip_addresses StatefulNodeAzure#private_ip_addresses}.'''
        result = self._values.get("private_ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def public_ips(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfacePublicIps"]]]:
        '''public_ips block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ips StatefulNodeAzure#public_ips}
        '''
        result = self._values.get("public_ips")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfacePublicIps"]]], result)

    @builtins.property
    def public_ip_sku(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#public_ip_sku StatefulNodeAzure#public_ip_sku}.'''
        result = self._values.get("public_ip_sku")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureNetworkNetworkInterface(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "private_ip_address_version": "privateIpAddressVersion",
    },
)
class StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations:
    def __init__(
        self,
        *,
        name: builtins.str,
        private_ip_address_version: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param private_ip_address_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#private_ip_address_version StatefulNodeAzure#private_ip_address_version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8e130ddd0b1e107fd066196c8671e9380f2814a0ed526a2581b86dc645a7af1)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument private_ip_address_version", value=private_ip_address_version, expected_type=type_hints["private_ip_address_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "private_ip_address_version": private_ip_address_version,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_ip_address_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#private_ip_address_version StatefulNodeAzure#private_ip_address_version}.'''
        result = self._values.get("private_ip_address_version")
        assert result is not None, "Required property 'private_ip_address_version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3ccfddc53025ddabd4e1a096fe5ff1cab7ee230b4c0f112d3a4f6b5fe85f28e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da27e0b58b4403df2e681e3e5742e0d465ceea7b4e475a2619f9ad99b1eb25fe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b41a520b24700013c43928378bf8cfbf6117c5876706aa8af7fbe45f97ba4a2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__33f0cb3857842aa4ab9e2e28eeb7c80827c0815f5b4e14f4c395596937c003fd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e369d7f8da8fd7686c115d788020768dc6d3bb0d17655c58874206031ec5bd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3f4c983bea3f8e68ea3df9333f776170d6d96451a2c49de5da390e20d39dc21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a013be5a5bda84fc3694f1c51a33957adab51dab1b0ee0900addd4649b609fce)
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
    @jsii.member(jsii_name="privateIpAddressVersionInput")
    def private_ip_address_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateIpAddressVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__686434b791e18809c1777d6a21783c909eda1492c3b57f9394021d8f62b2be3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIpAddressVersion")
    def private_ip_address_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIpAddressVersion"))

    @private_ip_address_version.setter
    def private_ip_address_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcf2044b634f8b08b511281cabe1960dcabd39ededd1bd658e13f0dafb473a72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIpAddressVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__473939eac060d5606bba48983aee8ed3106f5f14b19015272752e3eda5c5dd38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "network_resource_group_name": "networkResourceGroupName",
    },
)
class StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups:
    def __init__(
        self,
        *,
        name: builtins.str,
        network_resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param network_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__384b98238e7750acf201453a2c93502b621893147fe4e51cd1972d6cf76e09c8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_resource_group_name", value=network_resource_group_name, expected_type=type_hints["network_resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "network_resource_group_name": network_resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.'''
        result = self._values.get("network_resource_group_name")
        assert result is not None, "Required property 'network_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe5e1f34c14c19202d344d641539475773b8a01d183cae35e7a7cdd60304c9ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b04ed1814106248a4925880741f9ba4846bae02acd457acf0222fc7b5ac6a0f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af82d4486d268265bd727a84afeb0f2f49fa7fd0851ce721dbdaa74134e9e946)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b2429a32304a99cd906a482f8dc370041a7cbe98d7acce0d178874f03961011)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31d56acb6f380c460ff698177d50d3d9c71d462617d13d2b8ab6fc3333cb07c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa79fa8c610c1d94a7f0c79a78d83bce067bdbe842c59a36af06640ff211eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7eb1e81f004e8dd8373d260fa922d0e1f6478a769b76460b04dcb24aee97dc7b)
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
    @jsii.member(jsii_name="networkResourceGroupNameInput")
    def network_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__226a3e42499adc6f8fa48c3d5cbd6e45530b667014f076f7ace81366c3868b1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourceGroupName")
    def network_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkResourceGroupName"))

    @network_resource_group_name.setter
    def network_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__432f4fb49542439c327559fbf4e23d6c21d2e48088b5cb565bedeb8bf68aae1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8d5a10afab02ee9118706f975259a22cc07c5855a5f7b9c39f4b25757c2a0db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkNetworkInterfaceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b9a454e326880a3d72eb92514a34c93936bad5ca519f9727ff5c6b25b79063c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureNetworkNetworkInterfaceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5116dce8887868909273c3801da530bcff12f0a3bf194ae8cd6ef41e2202dc31)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureNetworkNetworkInterfaceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5388dc141ca1c16f0f76299fe0667bde84e59b66eb6072dc50b847d53b9d9e26)
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
            type_hints = typing.get_type_hints(_typecheckingstub__62c7ee00caf5547cf330ad9115b5f1e7987cf6c553dd09afbb49eeabac363b4a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d6a628fe7f87d3e59d21ecd96ab9b94eeae641e86b0de91c0904b41167336d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterface]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterface]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cb0d428f82e0f60542c6faf44df426c523c648b1690bcba2b7ee9e462e72a27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "network_resource_group_name": "networkResourceGroupName",
    },
)
class StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        network_resource_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param network_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b339f0f55e43be4cd95641b6e696ffcd2bb2b0f69ad6177f7f2b2b0c731d63c)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_resource_group_name", value=network_resource_group_name, expected_type=type_hints["network_resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if network_resource_group_name is not None:
            self._values["network_resource_group_name"] = network_resource_group_name

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_resource_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.'''
        result = self._values.get("network_resource_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9659f4b1e9647760077b7bdf891d1a913152c9a7e2bb70b1db88c44632870b7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92918997cea4f00d7d7a6b4491e4db37b10dfe3a2873ffbd4d3fcc714eb9bd1c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f28cb38a184fdbdb78487804c15f6c6b2986b09b06f920afbbb3cd9f48ad19f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1923bed51ca5479cc48f4bee12886948c3a5f285dc28a3f64bb8a8d98ad1eb75)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac68d3e67c28d1ebb6f1a2bd536ef0b12bbe2b97e402138567fa019f565bede0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__506302e25bf91e39cfc26e29be8f0193d711021897aed4714dea0236505b7838)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1055636342b823fc6e6cd4c1b12d8c8d0999c432f01527766e13259aeb1cfbea)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNetworkResourceGroupName")
    def reset_network_resource_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkResourceGroupName", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourceGroupNameInput")
    def network_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__498acd8c9486890345e6301152b447f8ed687d189a35c979891cb984627b4cdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourceGroupName")
    def network_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkResourceGroupName"))

    @network_resource_group_name.setter
    def network_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__719692c1640485f9c9f4ac9a857afe97bca6adaa7da675943146a391bb365405)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09e2951ca8bccc487711450f95f8fbcda90888c9470dbc34d57b2ddc5be3c10d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkNetworkInterfaceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfaceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00f4beb3daf377c49438ff77484cfd02f4fda960c81994dc9aa311029ccb43e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAdditionalIpConfigurations")
    def put_additional_ip_configurations(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45fbb37f30be4756956337662a9a127db53eed53ae5b8a6155d891b0a4e5e6b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAdditionalIpConfigurations", [value]))

    @jsii.member(jsii_name="putApplicationSecurityGroups")
    def put_application_security_groups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3acb3619deca3e9d13d74a9c1fd150f45cde4267ea91d337ee44fcd0a6fb62cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApplicationSecurityGroups", [value]))

    @jsii.member(jsii_name="putNetworkSecurityGroup")
    def put_network_security_group(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1da10c91f0fa66fa3f8544e0281e453ba6f44db3f6c9618e56ed2a06a008a04e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkSecurityGroup", [value]))

    @jsii.member(jsii_name="putPublicIps")
    def put_public_ips(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureNetworkNetworkInterfacePublicIps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a11c71ee5d491e3cfb530a3bbcea18f502144ce1fc8489beabb281fa8b64a64a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPublicIps", [value]))

    @jsii.member(jsii_name="resetAdditionalIpConfigurations")
    def reset_additional_ip_configurations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalIpConfigurations", []))

    @jsii.member(jsii_name="resetApplicationSecurityGroups")
    def reset_application_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationSecurityGroups", []))

    @jsii.member(jsii_name="resetAssignPublicIp")
    def reset_assign_public_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssignPublicIp", []))

    @jsii.member(jsii_name="resetEnableIpForwarding")
    def reset_enable_ip_forwarding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableIpForwarding", []))

    @jsii.member(jsii_name="resetNetworkSecurityGroup")
    def reset_network_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkSecurityGroup", []))

    @jsii.member(jsii_name="resetPrivateIpAddresses")
    def reset_private_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIpAddresses", []))

    @jsii.member(jsii_name="resetPublicIps")
    def reset_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicIps", []))

    @jsii.member(jsii_name="resetPublicIpSku")
    def reset_public_ip_sku(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicIpSku", []))

    @builtins.property
    @jsii.member(jsii_name="additionalIpConfigurations")
    def additional_ip_configurations(
        self,
    ) -> StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsList:
        return typing.cast(StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsList, jsii.get(self, "additionalIpConfigurations"))

    @builtins.property
    @jsii.member(jsii_name="applicationSecurityGroups")
    def application_security_groups(
        self,
    ) -> StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsList:
        return typing.cast(StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsList, jsii.get(self, "applicationSecurityGroups"))

    @builtins.property
    @jsii.member(jsii_name="networkSecurityGroup")
    def network_security_group(
        self,
    ) -> StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupList:
        return typing.cast(StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupList, jsii.get(self, "networkSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="publicIps")
    def public_ips(self) -> "StatefulNodeAzureNetworkNetworkInterfacePublicIpsList":
        return typing.cast("StatefulNodeAzureNetworkNetworkInterfacePublicIpsList", jsii.get(self, "publicIps"))

    @builtins.property
    @jsii.member(jsii_name="additionalIpConfigurationsInput")
    def additional_ip_configurations_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]], jsii.get(self, "additionalIpConfigurationsInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationSecurityGroupsInput")
    def application_security_groups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]], jsii.get(self, "applicationSecurityGroupsInput"))

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
    @jsii.member(jsii_name="networkSecurityGroupInput")
    def network_security_group_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]], jsii.get(self, "networkSecurityGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="privateIpAddressesInput")
    def private_ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "privateIpAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="publicIpsInput")
    def public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfacePublicIps"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureNetworkNetworkInterfacePublicIps"]]], jsii.get(self, "publicIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="publicIpSkuInput")
    def public_ip_sku_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicIpSkuInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c042009b04e2ae9159e75ed966a6e0bcaa31fbd5e8915e4040291afe64207cc5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__469ba1c92a3d6294b67c0fd2a3772515a06a00c13e405591edfcb560431d4ff5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6256636471f4d4afb01d9875639d224615f1fcdf7fdf208769a80fa00e320cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPrimary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateIpAddresses")
    def private_ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "privateIpAddresses"))

    @private_ip_addresses.setter
    def private_ip_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b1a34f4c1268b6852d3ba56c8b3b9df970e6614d4394a696f3512eb03eff304)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateIpAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicIpSku")
    def public_ip_sku(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicIpSku"))

    @public_ip_sku.setter
    def public_ip_sku(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2223e329c0d1ab3c5831ea2dbb86c9ade614f242e2e0adabb9dea48429b85fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicIpSku", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetName")
    def subnet_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetName"))

    @subnet_name.setter
    def subnet_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f88b79efba923cfd5d563bfdcffa4f474efe094aa462111084410b4dc7f3e3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterface]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterface]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterface]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e8e97239d7daa4d26502c98fd7cf038880fb995184ea5aaf8c8c407f7bfc7b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfacePublicIps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "network_resource_group_name": "networkResourceGroupName",
    },
)
class StatefulNodeAzureNetworkNetworkInterfacePublicIps:
    def __init__(
        self,
        *,
        name: builtins.str,
        network_resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param network_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7713fae4508f705158fdd3057769e0e578b4b22203b46bf6b54cf156c34f55d5)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_resource_group_name", value=network_resource_group_name, expected_type=type_hints["network_resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "network_resource_group_name": network_resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def network_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#network_resource_group_name StatefulNodeAzure#network_resource_group_name}.'''
        result = self._values.get("network_resource_group_name")
        assert result is not None, "Required property 'network_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureNetworkNetworkInterfacePublicIps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureNetworkNetworkInterfacePublicIpsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfacePublicIpsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8420ac4bed3678d970ca0dcd0beff2c3341db35fd50f9857b3eb181620ee6e5f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureNetworkNetworkInterfacePublicIpsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__643e592ca5f68c01aee77dcb9a28881ab6da41e1713596d9edae78cee88fca87)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureNetworkNetworkInterfacePublicIpsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc2b243f085d721adabff92699e2bed88fa389e9891b186ac0bf0cad22ad252d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e881fb17d5f520f84bafbefed2b54f0465cb61c38a535354ab851259306b69d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__627ac419e873d42dc6ea1353d6a8a278a50c6d82344a2bc09581764afbc0ff59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfacePublicIps]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfacePublicIps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfacePublicIps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e23829c8b8cabb3d9f432af7ee1acca698a4e75449e42d25d0eae63b0e40e919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkNetworkInterfacePublicIpsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkNetworkInterfacePublicIpsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5d376a55ce3ddb960885ef9e1495d13817c7757aec045a9066857df7a1907b7)
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
    @jsii.member(jsii_name="networkResourceGroupNameInput")
    def network_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aa98d2567c6af444f687a0b347f920b941950059f0915debc0a0e10532dc8af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkResourceGroupName")
    def network_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkResourceGroupName"))

    @network_resource_group_name.setter
    def network_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__540a2e4d528989f23877c32da4cd96fc66eecb82c0da4013ef113e3daa8d408a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfacePublicIps]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfacePublicIps]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfacePublicIps]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2acc8237755c86a9ac1f280210e6a39f3c387cab72f160b9c490702865ae82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureNetworkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureNetworkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7cad555978c74da5586ea70e9ca010749bc6558bb3926488c0ca9915af8485f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNetworkInterface")
    def put_network_interface(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d6816f18da1184576132dddba813064879eb97ee8e37fb8bdfecfb7788c59d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterface", [value]))

    @builtins.property
    @jsii.member(jsii_name="networkInterface")
    def network_interface(self) -> StatefulNodeAzureNetworkNetworkInterfaceList:
        return typing.cast(StatefulNodeAzureNetworkNetworkInterfaceList, jsii.get(self, "networkInterface"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaceInput")
    def network_interface_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterface]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterface]]], jsii.get(self, "networkInterfaceInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourceGroupNameInput")
    def network_resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkResourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkNameInput")
    def virtual_network_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNetworkNameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkResourceGroupName")
    def network_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkResourceGroupName"))

    @network_resource_group_name.setter
    def network_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbb8467c98e6902306ea2c7a6291c7861dbb154532ddea609bd7b74b9b8ca912)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkResourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualNetworkName")
    def virtual_network_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualNetworkName"))

    @virtual_network_name.setter
    def virtual_network_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805d95d8f6f57d4e25f4587a43a09e6c9fb3b78913ea47f808efa2b58a213976)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualNetworkName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureNetwork]:
        return typing.cast(typing.Optional[StatefulNodeAzureNetwork], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureNetwork]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bdb672d847cf42d0dac8e33cc6fd4ac19ab7961bb162a426058f012d1108581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureOsDisk",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "caching": "caching", "size_gb": "sizeGb"},
)
class StatefulNodeAzureOsDisk:
    def __init__(
        self,
        *,
        type: builtins.str,
        caching: typing.Optional[builtins.str] = None,
        size_gb: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        :param caching: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#caching StatefulNodeAzure#caching}.
        :param size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fee640ec7c5787c7d8b9c626909d9f75e1fad5548922d1ac183d4e423a69f7a)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument caching", value=caching, expected_type=type_hints["caching"])
            check_type(argname="argument size_gb", value=size_gb, expected_type=type_hints["size_gb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if caching is not None:
            self._values["caching"] = caching
        if size_gb is not None:
            self._values["size_gb"] = size_gb

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def caching(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#caching StatefulNodeAzure#caching}.'''
        result = self._values.get("caching")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def size_gb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#size_gb StatefulNodeAzure#size_gb}.'''
        result = self._values.get("size_gb")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureOsDisk(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureOsDiskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureOsDiskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da91438b28ad4ab72186e93544b0c3a4ca49f506259a3fffa67b15b748dcb715)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCaching")
    def reset_caching(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaching", []))

    @jsii.member(jsii_name="resetSizeGb")
    def reset_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSizeGb", []))

    @builtins.property
    @jsii.member(jsii_name="cachingInput")
    def caching_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cachingInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeGbInput")
    def size_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="caching")
    def caching(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caching"))

    @caching.setter
    def caching(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b0607bcb9c26868ca8e46a409aab25ae6047d30c6eee13a79219364e8ffdf73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caching", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeGb")
    def size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeGb"))

    @size_gb.setter
    def size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a012b7d27780f63a235ee5a69013a640abd51eb93732f21ed3cfbbcca9745973)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__515693ac7ef3009ed0d89f58e1990cb19af1b1f06d4dc9bf264e62a54ecd664f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureOsDisk]:
        return typing.cast(typing.Optional[StatefulNodeAzureOsDisk], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureOsDisk]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a563c79af2490347c1cadc9af4f0abba874afa713457fa273905f13d92569ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureProximityPlacementGroups",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class StatefulNodeAzureProximityPlacementGroups:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83b70dac0c17919d04bcdf77512c4aac25ce043eba5c237fa9a02f3d5663f6e7)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureProximityPlacementGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureProximityPlacementGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureProximityPlacementGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f709e1b85bbf12a1ad402445cc7ed6147c576eee02c07465161a8bad1f1a620a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureProximityPlacementGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f17347fc00c3af747b5a059086934fc9d19618047821dfe1ec39bea978b698a4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureProximityPlacementGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fad754712abdb37723fd79abd35f74fef2b9922d3407556beb13b91e8f7ad9f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a654868893de010718427948cbff9804d92facdec8a49194f1cfb8dda17bfefa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__265c95d6c781bb0c3547bc2b0fd7d30e464ec279512cbec3da043d636f5f0492)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureProximityPlacementGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureProximityPlacementGroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureProximityPlacementGroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5b21f22a6252df7077c9bcc9aa7be75b698275197f0df7f2c4c6eb581a54e48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureProximityPlacementGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureProximityPlacementGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95f55f1f3b0b0337b3f44fefba10ae497a3d5612f72875d9f4e51ac1afe6f0f6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db68c0391bb10df20c6a611f5e56081927fe7e2a9eae260e718cb594d6395084)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78629e3d4fdb0e55ca28565d76c252709ad90391ca0cdfe19f7de19405a12d1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureProximityPlacementGroups]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureProximityPlacementGroups]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureProximityPlacementGroups]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2365d7816dcca37205b2dc54f1254fc3749dae093567a543819468e872246393)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSchedulingTask",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "is_enabled": "isEnabled",
        "type": "type",
    },
)
class StatefulNodeAzureSchedulingTask:
    def __init__(
        self,
        *,
        cron_expression: builtins.str,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        type: builtins.str,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#cron_expression StatefulNodeAzure#cron_expression}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#is_enabled StatefulNodeAzure#is_enabled}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36842cff501a1ee9a0bd55035e3adc7ad9cda1c5a49464b6debfc5b081d24e02)
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron_expression": cron_expression,
            "is_enabled": is_enabled,
            "type": type,
        }

    @builtins.property
    def cron_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#cron_expression StatefulNodeAzure#cron_expression}.'''
        result = self._values.get("cron_expression")
        assert result is not None, "Required property 'cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#is_enabled StatefulNodeAzure#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureSchedulingTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureSchedulingTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSchedulingTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b5f482394266d66a21549c4a8fae18d53381da42a68c85ada1de7896d2b177c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureSchedulingTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40cf2b93fc5a11b57fb34b4f57c1bdae0fb1d35e42216104ec46b35f7d5fd7fb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureSchedulingTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c84bc37a45cdd694dcd39a2e9fc92390e599600d18b91447a469b69719a7462e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e6bbfc68c3b953d80c1ba1bc975f29358836d59121ea5f6db1f0893c9239e2f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d56921a8132e29389de21bcc38ab3bb1d58e6fe23f47ecac4d952e8d40f92ff4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSchedulingTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSchedulingTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSchedulingTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad3f2dc37adba6c425820aa615a32b74762da0e2c85def970f4feb56957b28f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureSchedulingTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSchedulingTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89cbad03ffa1a07b4661d2eafc80fc087b878c712f07e2996b2ba070413c2524)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="cronExpression")
    def cron_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cronExpression"))

    @cron_expression.setter
    def cron_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d010d463cb5ee5a6868081d68e91b0f09aa4bbeeb64e900a7fe2b615668f58)
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
            type_hints = typing.get_type_hints(_typecheckingstub__83aeba17b46db6b5e7d23d04b585ae89806081f07edb6d7d9c67e17951a9f654)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6db48c9095818dab0a6d85ce7beeb8411a3e443801c8dbccdf762e6cb457c7f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSchedulingTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSchedulingTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSchedulingTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61c63831bf7e1ff57182d86add8f21ec2f078c068a69b2fc84a7d664b107f288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecret",
    jsii_struct_bases=[],
    name_mapping={
        "source_vault": "sourceVault",
        "vault_certificates": "vaultCertificates",
    },
)
class StatefulNodeAzureSecret:
    def __init__(
        self,
        *,
        source_vault: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecretSourceVault", typing.Dict[builtins.str, typing.Any]]]],
        vault_certificates: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecretVaultCertificates", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param source_vault: source_vault block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#source_vault StatefulNodeAzure#source_vault}
        :param vault_certificates: vault_certificates block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vault_certificates StatefulNodeAzure#vault_certificates}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3b510a9ac511eeb3d97a80f0a8cb1efbf20bdd950f81064869b493cea3630fc)
            check_type(argname="argument source_vault", value=source_vault, expected_type=type_hints["source_vault"])
            check_type(argname="argument vault_certificates", value=vault_certificates, expected_type=type_hints["vault_certificates"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_vault": source_vault,
            "vault_certificates": vault_certificates,
        }

    @builtins.property
    def source_vault(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretSourceVault"]]:
        '''source_vault block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#source_vault StatefulNodeAzure#source_vault}
        '''
        result = self._values.get("source_vault")
        assert result is not None, "Required property 'source_vault' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretSourceVault"]], result)

    @builtins.property
    def vault_certificates(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretVaultCertificates"]]:
        '''vault_certificates block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vault_certificates StatefulNodeAzure#vault_certificates}
        '''
        result = self._values.get("vault_certificates")
        assert result is not None, "Required property 'vault_certificates' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretVaultCertificates"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureSecret(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureSecretList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83705ef0b02c11e3513491d5032caab6ff59c59bd744bdc17d5aaeb50c4751c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureSecretOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__138cd4fa4d45cbedaff3abf4f8f6e3016e519d8e13df6653d1d1f2c5b2bef614)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureSecretOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4846b0272d8195d006b87656001c2338016cd0cd2d4aec00e4cb7453ee1f3ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__987174ec7da679135ca345f257bf860047a741263989c856e15d987cb52bbd55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f46ed554c9ba81e7fe5ad3c482966544f5d23ca01efb7e3580307711a0ca007)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecret]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecret]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecret]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a51173756fa50672cfd833891e5128c3c65ed803d41b003c830a946b0ec514f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureSecretOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b64df1d4a844e7b68ab9fa5ecd9f6395caf102e2b084ca9e1fa4dca94c0d479c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putSourceVault")
    def put_source_vault(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecretSourceVault", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53272d52eaf1cbf20ac11e0e77d10fc6b38df0c5419d5a506362a620e597a2ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSourceVault", [value]))

    @jsii.member(jsii_name="putVaultCertificates")
    def put_vault_certificates(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureSecretVaultCertificates", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ddba7647c7f8d0307925670a51538ab9adbc5676310c4fefefe7eb628edf2db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVaultCertificates", [value]))

    @builtins.property
    @jsii.member(jsii_name="sourceVault")
    def source_vault(self) -> "StatefulNodeAzureSecretSourceVaultList":
        return typing.cast("StatefulNodeAzureSecretSourceVaultList", jsii.get(self, "sourceVault"))

    @builtins.property
    @jsii.member(jsii_name="vaultCertificates")
    def vault_certificates(self) -> "StatefulNodeAzureSecretVaultCertificatesList":
        return typing.cast("StatefulNodeAzureSecretVaultCertificatesList", jsii.get(self, "vaultCertificates"))

    @builtins.property
    @jsii.member(jsii_name="sourceVaultInput")
    def source_vault_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretSourceVault"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretSourceVault"]]], jsii.get(self, "sourceVaultInput"))

    @builtins.property
    @jsii.member(jsii_name="vaultCertificatesInput")
    def vault_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretVaultCertificates"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureSecretVaultCertificates"]]], jsii.get(self, "vaultCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecret]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecret]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecret]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1191af5eae82c03bf7c9e091d22b3cc6d9e13bf085560cc32cd69f9e242abfe9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretSourceVault",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "resource_group_name": "resourceGroupName"},
)
class StatefulNodeAzureSecretSourceVault:
    def __init__(
        self,
        *,
        name: builtins.str,
        resource_group_name: builtins.str,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1de629eda68a141a1a579736deeb15e2390e97e71c60052a505a62f2a1f63fd2)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "resource_group_name": resource_group_name,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#name StatefulNodeAzure#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#resource_group_name StatefulNodeAzure#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureSecretSourceVault(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureSecretSourceVaultList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretSourceVaultList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2848ef01abad44b36d4e735c912934032358a126b2af43f70482cc32ef805d2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureSecretSourceVaultOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edad9fe817a499a21845012ff284657ad6c9c5974af756cd4cf072221bb85e44)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureSecretSourceVaultOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2900e7434eafef887d258a3cbcb60a781138803c97cb8a3d8bf1ecd51e995cbb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fca37be26023c31d591171111ae6597f6b50809c5edccb119e305b2a7e6b8099)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e20fe41843d9de3caa22767e899d06d66d009dd2486f936b1c020775c62f8e9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretSourceVault]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretSourceVault]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretSourceVault]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b3ba86c108f00baef587bd7ae840dadcbbe8eac6afa413989b5f4841c73d2e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureSecretSourceVaultOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretSourceVaultOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b423b412eab25bcf04be3ed5d23c2e2462416eac3d7b88cefc38af7a681acc09)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a563db6f31d73f50fd1991141d3ee2c66892e53b2cededf252408039046426a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7b5dabb7b0f34feafb5a976f1a2efb186e8efd17a4e53bcca968a4110a6f96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretSourceVault]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretSourceVault]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretSourceVault]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f23f81da125ffeaf0ab735666d2ba894ea6fcbc77e6745381cb8b2f2dafcf63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretVaultCertificates",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_store": "certificateStore",
        "certificate_url": "certificateUrl",
    },
)
class StatefulNodeAzureSecretVaultCertificates:
    def __init__(
        self,
        *,
        certificate_store: typing.Optional[builtins.str] = None,
        certificate_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param certificate_store: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#certificate_store StatefulNodeAzure#certificate_store}.
        :param certificate_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#certificate_url StatefulNodeAzure#certificate_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9de52ebd04de282ab20e0fffdc079400aa9c58b6af0d66438c3234369ec13e9b)
            check_type(argname="argument certificate_store", value=certificate_store, expected_type=type_hints["certificate_store"])
            check_type(argname="argument certificate_url", value=certificate_url, expected_type=type_hints["certificate_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if certificate_store is not None:
            self._values["certificate_store"] = certificate_store
        if certificate_url is not None:
            self._values["certificate_url"] = certificate_url

    @builtins.property
    def certificate_store(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#certificate_store StatefulNodeAzure#certificate_store}.'''
        result = self._values.get("certificate_store")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#certificate_url StatefulNodeAzure#certificate_url}.'''
        result = self._values.get("certificate_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureSecretVaultCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureSecretVaultCertificatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretVaultCertificatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__92d35a4fb5d1e7f0e9848d958516a8b3a6dcbbed3338c317ab568134780e1eab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureSecretVaultCertificatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdab746ae35b0481ad5a99d212baa41d040852f76833270c69b45ffe998511bd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureSecretVaultCertificatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1d1a285c6df5f16903c5dfacf838a979e06b525727d3ccf155e1183cf68f149)
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
            type_hints = typing.get_type_hints(_typecheckingstub__958596d59eaa4107eedbe847337abc7edcefa201f04dc882533d68e9052bc0f5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__44a8e3cdb3e8980bcca8e6422f5818c1c2cad332c5b438010deb6ba2d2910013)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretVaultCertificates]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretVaultCertificates]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretVaultCertificates]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7648622208b700e87b4f8aae7af78dc2bb0ad490073e77e53596ce839814b0fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureSecretVaultCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecretVaultCertificatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f07b0e8fab3b8207fe165222b575cc3e0c355917da96fb2e5a176bba5710f1ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCertificateStore")
    def reset_certificate_store(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateStore", []))

    @jsii.member(jsii_name="resetCertificateUrl")
    def reset_certificate_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateUrl", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__09fd818b2489700526c965e9c1ea785b85cd73419d055aed8f8c86def7776429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateUrl")
    def certificate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateUrl"))

    @certificate_url.setter
    def certificate_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbab3c9a254030676696d1091c8dd2092e8216f9e6c5b62856990ee2eb67c317)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretVaultCertificates]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretVaultCertificates]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretVaultCertificates]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__309a79b20e3c28aef10856436265763ea856c6c42155eed74b3e84d4a45c88ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecurity",
    jsii_struct_bases=[],
    name_mapping={
        "confidential_os_disk_encryption": "confidentialOsDiskEncryption",
        "encryption_at_host": "encryptionAtHost",
        "secure_boot_enabled": "secureBootEnabled",
        "security_type": "securityType",
        "vtpm_enabled": "vtpmEnabled",
    },
)
class StatefulNodeAzureSecurity:
    def __init__(
        self,
        *,
        confidential_os_disk_encryption: typing.Optional[builtins.str] = None,
        encryption_at_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        security_type: typing.Optional[builtins.str] = None,
        vtpm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param confidential_os_disk_encryption: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#confidential_os_disk_encryption StatefulNodeAzure#confidential_os_disk_encryption}.
        :param encryption_at_host: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#encryption_at_host StatefulNodeAzure#encryption_at_host}.
        :param secure_boot_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#secure_boot_enabled StatefulNodeAzure#secure_boot_enabled}.
        :param security_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#security_type StatefulNodeAzure#security_type}.
        :param vtpm_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vtpm_enabled StatefulNodeAzure#vtpm_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4a53e9b559bc0c680e80daee9a70ac98b8edafc65f8d1d272b4bd2e88904b6b)
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
    def confidential_os_disk_encryption(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#confidential_os_disk_encryption StatefulNodeAzure#confidential_os_disk_encryption}.'''
        result = self._values.get("confidential_os_disk_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_at_host(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#encryption_at_host StatefulNodeAzure#encryption_at_host}.'''
        result = self._values.get("encryption_at_host")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_boot_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#secure_boot_enabled StatefulNodeAzure#secure_boot_enabled}.'''
        result = self._values.get("secure_boot_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def security_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#security_type StatefulNodeAzure#security_type}.'''
        result = self._values.get("security_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vtpm_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vtpm_enabled StatefulNodeAzure#vtpm_enabled}.'''
        result = self._values.get("vtpm_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureSecurity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureSecurityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSecurityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__017c780d0d99be8dedd0056e07de1ff6e673605c77d0c42f9348c0039ccc5f1b)
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
    def confidential_os_disk_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confidentialOsDiskEncryptionInput"))

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
    def confidential_os_disk_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confidentialOsDiskEncryption"))

    @confidential_os_disk_encryption.setter
    def confidential_os_disk_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76d8ad5a0037a28bf2bc5487f1751a48c24be1e4a0844dc2ae6196981acbb84e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5b1a262a89d94d68771a41e1587f67029a77b48d7473ee8383d44e1ff051298)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee24a01e121007e635d812a242e65180f373530228814018c9476d109c04d562)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureBootEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityType")
    def security_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityType"))

    @security_type.setter
    def security_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdabaada8735d4b54fdf67247a681d84ad420eeb325763eb51047188c1c811d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a467ca184d70c640746b0580544bd0ad1b682355a7a7eb9bd1c75482beba1c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vtpmEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureSecurity]:
        return typing.cast(typing.Optional[StatefulNodeAzureSecurity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureSecurity]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8c2a26ee09de64ba8641d806d8c9182060d1e08a7c9a4243d21bc17977a279e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSignal",
    jsii_struct_bases=[],
    name_mapping={"timeout": "timeout", "type": "type"},
)
class StatefulNodeAzureSignal:
    def __init__(self, *, timeout: jsii.Number, type: builtins.str) -> None:
        '''
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#timeout StatefulNodeAzure#timeout}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b27723ee6eead5cee2ba134b41c7a06337bebeeaddbd6b1f994e25093323c9c3)
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "timeout": timeout,
            "type": type,
        }

    @builtins.property
    def timeout(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#timeout StatefulNodeAzure#timeout}.'''
        result = self._values.get("timeout")
        assert result is not None, "Required property 'timeout' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#type StatefulNodeAzure#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureSignal(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureSignalList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSignalList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3a6c8dcb47ea35fe3dbcd04440b5bf4bc56eecc80e867134e75656b95f2d2c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureSignalOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30a8e5c576feae0ee5de6564cff14dad4d2c4e01ea52e32babb3ba5aacd75bcf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureSignalOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29ed13a63dad526faa48bf35b00c7c634c30fc05944f037b1415dc2224860364)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1255d2a81d0800121d9af7bb71b12712649a55330dfaae79dac9d6bdf29b6068)
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
            type_hints = typing.get_type_hints(_typecheckingstub__719a8ad0358452b15fdacdf65c53cd3c96b0a9e1ac1df55243c3959a2606e95e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSignal]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSignal]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSignal]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2436a5dfdd0e20ca170d1dd4b4d192b2395a7c6a44d14b46ebadb6ea44b6d5a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureSignalOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureSignalOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__455626b780085d087dd1a3ac3a436aad8747c8393c3de290b4068d757922d554)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c89dd66fb8109f87296c6b5bc7d1307a9f04e377482f234f7dc17f695799a64f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef31d8d872a20214cb8924da7ef757e4e34e2dd076c9bda6a1bd9b1f38a86e43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSignal]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSignal]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSignal]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cb946596c1882a51bed1801008b67384e5eb5b365f3e43d26aac0a3834c5da6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategy",
    jsii_struct_bases=[],
    name_mapping={
        "fallback_to_on_demand": "fallbackToOnDemand",
        "availability_vs_cost": "availabilityVsCost",
        "capacity_reservation": "capacityReservation",
        "draining_timeout": "drainingTimeout",
        "od_windows": "odWindows",
        "optimization_windows": "optimizationWindows",
        "preferred_life_cycle": "preferredLifeCycle",
        "revert_to_spot": "revertToSpot",
        "vm_admins": "vmAdmins",
    },
)
class StatefulNodeAzureStrategy:
    def __init__(
        self,
        *,
        fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        availability_vs_cost: typing.Optional[jsii.Number] = None,
        capacity_reservation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureStrategyCapacityReservation", typing.Dict[builtins.str, typing.Any]]]]] = None,
        draining_timeout: typing.Optional[jsii.Number] = None,
        od_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_life_cycle: typing.Optional[builtins.str] = None,
        revert_to_spot: typing.Optional[typing.Union["StatefulNodeAzureStrategyRevertToSpot", typing.Dict[builtins.str, typing.Any]]] = None,
        vm_admins: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param fallback_to_on_demand: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#fallback_to_on_demand StatefulNodeAzure#fallback_to_on_demand}.
        :param availability_vs_cost: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#availability_vs_cost StatefulNodeAzure#availability_vs_cost}.
        :param capacity_reservation: capacity_reservation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#capacity_reservation StatefulNodeAzure#capacity_reservation}
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#draining_timeout StatefulNodeAzure#draining_timeout}.
        :param od_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#od_windows StatefulNodeAzure#od_windows}.
        :param optimization_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#optimization_windows StatefulNodeAzure#optimization_windows}.
        :param preferred_life_cycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_life_cycle StatefulNodeAzure#preferred_life_cycle}.
        :param revert_to_spot: revert_to_spot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#revert_to_spot StatefulNodeAzure#revert_to_spot}
        :param vm_admins: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_admins StatefulNodeAzure#vm_admins}.
        '''
        if isinstance(revert_to_spot, dict):
            revert_to_spot = StatefulNodeAzureStrategyRevertToSpot(**revert_to_spot)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d3f7ba12bd229ba7ec573dc76c8970adc9d9bf93241f5dd8b4a45afd750c568)
            check_type(argname="argument fallback_to_on_demand", value=fallback_to_on_demand, expected_type=type_hints["fallback_to_on_demand"])
            check_type(argname="argument availability_vs_cost", value=availability_vs_cost, expected_type=type_hints["availability_vs_cost"])
            check_type(argname="argument capacity_reservation", value=capacity_reservation, expected_type=type_hints["capacity_reservation"])
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument od_windows", value=od_windows, expected_type=type_hints["od_windows"])
            check_type(argname="argument optimization_windows", value=optimization_windows, expected_type=type_hints["optimization_windows"])
            check_type(argname="argument preferred_life_cycle", value=preferred_life_cycle, expected_type=type_hints["preferred_life_cycle"])
            check_type(argname="argument revert_to_spot", value=revert_to_spot, expected_type=type_hints["revert_to_spot"])
            check_type(argname="argument vm_admins", value=vm_admins, expected_type=type_hints["vm_admins"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fallback_to_on_demand": fallback_to_on_demand,
        }
        if availability_vs_cost is not None:
            self._values["availability_vs_cost"] = availability_vs_cost
        if capacity_reservation is not None:
            self._values["capacity_reservation"] = capacity_reservation
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if od_windows is not None:
            self._values["od_windows"] = od_windows
        if optimization_windows is not None:
            self._values["optimization_windows"] = optimization_windows
        if preferred_life_cycle is not None:
            self._values["preferred_life_cycle"] = preferred_life_cycle
        if revert_to_spot is not None:
            self._values["revert_to_spot"] = revert_to_spot
        if vm_admins is not None:
            self._values["vm_admins"] = vm_admins

    @builtins.property
    def fallback_to_on_demand(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#fallback_to_on_demand StatefulNodeAzure#fallback_to_on_demand}.'''
        result = self._values.get("fallback_to_on_demand")
        assert result is not None, "Required property 'fallback_to_on_demand' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def availability_vs_cost(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#availability_vs_cost StatefulNodeAzure#availability_vs_cost}.'''
        result = self._values.get("availability_vs_cost")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def capacity_reservation(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureStrategyCapacityReservation"]]]:
        '''capacity_reservation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#capacity_reservation StatefulNodeAzure#capacity_reservation}
        '''
        result = self._values.get("capacity_reservation")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureStrategyCapacityReservation"]]], result)

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#draining_timeout StatefulNodeAzure#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def od_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#od_windows StatefulNodeAzure#od_windows}.'''
        result = self._values.get("od_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def optimization_windows(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#optimization_windows StatefulNodeAzure#optimization_windows}.'''
        result = self._values.get("optimization_windows")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preferred_life_cycle(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_life_cycle StatefulNodeAzure#preferred_life_cycle}.'''
        result = self._values.get("preferred_life_cycle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revert_to_spot(
        self,
    ) -> typing.Optional["StatefulNodeAzureStrategyRevertToSpot"]:
        '''revert_to_spot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#revert_to_spot StatefulNodeAzure#revert_to_spot}
        '''
        result = self._values.get("revert_to_spot")
        return typing.cast(typing.Optional["StatefulNodeAzureStrategyRevertToSpot"], result)

    @builtins.property
    def vm_admins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#vm_admins StatefulNodeAzure#vm_admins}.'''
        result = self._values.get("vm_admins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyCapacityReservation",
    jsii_struct_bases=[],
    name_mapping={
        "should_utilize": "shouldUtilize",
        "utilization_strategy": "utilizationStrategy",
        "capacity_reservation_groups": "capacityReservationGroups",
    },
)
class StatefulNodeAzureStrategyCapacityReservation:
    def __init__(
        self,
        *,
        should_utilize: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        utilization_strategy: builtins.str,
        capacity_reservation_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param should_utilize: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_utilize StatefulNodeAzure#should_utilize}.
        :param utilization_strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#utilization_strategy StatefulNodeAzure#utilization_strategy}.
        :param capacity_reservation_groups: capacity_reservation_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#capacity_reservation_groups StatefulNodeAzure#capacity_reservation_groups}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d19be6d2e53694872177674c1aa4a03496973ed1e859a3c86d25319afef2c001)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#should_utilize StatefulNodeAzure#should_utilize}.'''
        result = self._values.get("should_utilize")
        assert result is not None, "Required property 'should_utilize' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def utilization_strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#utilization_strategy StatefulNodeAzure#utilization_strategy}.'''
        result = self._values.get("utilization_strategy")
        assert result is not None, "Required property 'utilization_strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity_reservation_groups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups"]]]:
        '''capacity_reservation_groups block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#capacity_reservation_groups StatefulNodeAzure#capacity_reservation_groups}
        '''
        result = self._values.get("capacity_reservation_groups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureStrategyCapacityReservation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups",
    jsii_struct_bases=[],
    name_mapping={
        "crg_name": "crgName",
        "crg_resource_group_name": "crgResourceGroupName",
        "crg_should_prioritize": "crgShouldPrioritize",
    },
)
class StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups:
    def __init__(
        self,
        *,
        crg_name: builtins.str,
        crg_resource_group_name: builtins.str,
        crg_should_prioritize: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param crg_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#crg_name StatefulNodeAzure#crg_name}.
        :param crg_resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#crg_resource_group_name StatefulNodeAzure#crg_resource_group_name}.
        :param crg_should_prioritize: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#crg_should_prioritize StatefulNodeAzure#crg_should_prioritize}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca1f9df1789a66b7e8dbf6eea51337671a942cbede80bd20b7296614f032249c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#crg_name StatefulNodeAzure#crg_name}.'''
        result = self._values.get("crg_name")
        assert result is not None, "Required property 'crg_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def crg_resource_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#crg_resource_group_name StatefulNodeAzure#crg_resource_group_name}.'''
        result = self._values.get("crg_resource_group_name")
        assert result is not None, "Required property 'crg_resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def crg_should_prioritize(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#crg_should_prioritize StatefulNodeAzure#crg_should_prioritize}.'''
        result = self._values.get("crg_should_prioritize")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e97b69854525dfc3146fb32193161826081b4dfe642110ecccda082c1944392a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da5ab4b977e72681cd35045b8d40573d4ec48ea32156df3b9fb47d3d59d83f1a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f10c931ea95bf462b50eaa74f2da3365ac0acb6b696dda49b5b65614aff32b30)
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
            type_hints = typing.get_type_hints(_typecheckingstub__10319d688e4641cb23c11bfe195f4e8f82aa82cd095cb554d8dc6d434f6f16f5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ba9eb7027ab1f4d42e8039aa2b2bb8ea8b5c4e2aad91bfbb576d7491bc3c188)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0649b5078cb2bc714820795f25172f56f8710e77289dc9b983d083e0421c0723)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f452aa7ec591bd8f21cb7e2a87aecdeb7de39d1328ee88c9d59252674ae71f5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__fc202b9b97f29189bc02a23fff1c9dd5f6cad96ce308819055eb8a6b98245dba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crgName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crgResourceGroupName")
    def crg_resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crgResourceGroupName"))

    @crg_resource_group_name.setter
    def crg_resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a19b1cc8721e49e49ebba882afc2a6ace7e560a5398d1aac9d4d1d1aea6311)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b36cc5d93ccefc50c64f3c767661a9bbbee11ab5d68577a88edde7a3dcf6801)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crgShouldPrioritize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce04508cc93a00c1035aeaa9e025d8a1544d227b7979bfd8d85ef9e7a0bfbd31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureStrategyCapacityReservationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyCapacityReservationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__005dd55b01eef5b117ecbdcea48394ad92cd31cac01426e29da948ede26c8d28)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "StatefulNodeAzureStrategyCapacityReservationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f56d2d76f8e3a3abfd7c343d758c8af68fcf8e2a35b51c6cce670162c709fcfa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureStrategyCapacityReservationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7120905773bccf30f6b301960ab73086750dfe44d275fa091944a83692d6ee35)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c294712de67c732ef7acfff781e432302806b547c478a67e95b3031321de65a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cadac1a76349478f2c0775f6e18f2299de056bd92c586ee295cc55358f7bf71a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservation]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservation]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservation]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__188c08ed3fecdb00f9733eb2e5bbd5efcb097533232c8cb7cd78f848865b63cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureStrategyCapacityReservationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyCapacityReservationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4750e662d4c370b918eae739cf8848ee1a6436387d593ce54494214e1b1aaf30)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCapacityReservationGroups")
    def put_capacity_reservation_groups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b37673685a3a904c57a562d676214870b68eb199e75b80c330a995bfd43b470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCapacityReservationGroups", [value]))

    @jsii.member(jsii_name="resetCapacityReservationGroups")
    def reset_capacity_reservation_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityReservationGroups", []))

    @builtins.property
    @jsii.member(jsii_name="capacityReservationGroups")
    def capacity_reservation_groups(
        self,
    ) -> StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsList:
        return typing.cast(StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsList, jsii.get(self, "capacityReservationGroups"))

    @builtins.property
    @jsii.member(jsii_name="capacityReservationGroupsInput")
    def capacity_reservation_groups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]], jsii.get(self, "capacityReservationGroupsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__1e1b8d31c7f0d406e9d7d911d3ede30c074b4f5dfe24f2ee52c87bc346c8b26d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldUtilize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="utilizationStrategy")
    def utilization_strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "utilizationStrategy"))

    @utilization_strategy.setter
    def utilization_strategy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c54e233f8204c2d592b4642bdd4a18dd221631fa34ead2aed639135d439c5182)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utilizationStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__145ea77f3be7793951e7f9d97b2ab682311f69719518449d55810f039345fdaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07afad8d9aa3894264edf1c77d663fc997c2ad93c24252088d84a4ecce4b0569)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCapacityReservation")
    def put_capacity_reservation(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureStrategyCapacityReservation, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__617f728dda109bc78f4e11cb163c864465f36475fdc6dce1c5380743bced4531)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCapacityReservation", [value]))

    @jsii.member(jsii_name="putRevertToSpot")
    def put_revert_to_spot(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#perform_at StatefulNodeAzure#perform_at}.
        '''
        value = StatefulNodeAzureStrategyRevertToSpot(perform_at=perform_at)

        return typing.cast(None, jsii.invoke(self, "putRevertToSpot", [value]))

    @jsii.member(jsii_name="resetAvailabilityVsCost")
    def reset_availability_vs_cost(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityVsCost", []))

    @jsii.member(jsii_name="resetCapacityReservation")
    def reset_capacity_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityReservation", []))

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetOdWindows")
    def reset_od_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOdWindows", []))

    @jsii.member(jsii_name="resetOptimizationWindows")
    def reset_optimization_windows(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptimizationWindows", []))

    @jsii.member(jsii_name="resetPreferredLifeCycle")
    def reset_preferred_life_cycle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredLifeCycle", []))

    @jsii.member(jsii_name="resetRevertToSpot")
    def reset_revert_to_spot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevertToSpot", []))

    @jsii.member(jsii_name="resetVmAdmins")
    def reset_vm_admins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVmAdmins", []))

    @builtins.property
    @jsii.member(jsii_name="capacityReservation")
    def capacity_reservation(self) -> StatefulNodeAzureStrategyCapacityReservationList:
        return typing.cast(StatefulNodeAzureStrategyCapacityReservationList, jsii.get(self, "capacityReservation"))

    @builtins.property
    @jsii.member(jsii_name="revertToSpot")
    def revert_to_spot(self) -> "StatefulNodeAzureStrategyRevertToSpotOutputReference":
        return typing.cast("StatefulNodeAzureStrategyRevertToSpotOutputReference", jsii.get(self, "revertToSpot"))

    @builtins.property
    @jsii.member(jsii_name="availabilityVsCostInput")
    def availability_vs_cost_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "availabilityVsCostInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityReservationInput")
    def capacity_reservation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservation]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservation]]], jsii.get(self, "capacityReservationInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="fallbackToOnDemandInput")
    def fallback_to_on_demand_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "fallbackToOnDemandInput"))

    @builtins.property
    @jsii.member(jsii_name="odWindowsInput")
    def od_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "odWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="optimizationWindowsInput")
    def optimization_windows_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optimizationWindowsInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredLifeCycleInput")
    def preferred_life_cycle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredLifeCycleInput"))

    @builtins.property
    @jsii.member(jsii_name="revertToSpotInput")
    def revert_to_spot_input(
        self,
    ) -> typing.Optional["StatefulNodeAzureStrategyRevertToSpot"]:
        return typing.cast(typing.Optional["StatefulNodeAzureStrategyRevertToSpot"], jsii.get(self, "revertToSpotInput"))

    @builtins.property
    @jsii.member(jsii_name="vmAdminsInput")
    def vm_admins_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vmAdminsInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityVsCost")
    def availability_vs_cost(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "availabilityVsCost"))

    @availability_vs_cost.setter
    def availability_vs_cost(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a6268d997a23c5bcb6b9a4652db58a88d28170b8ed8ed76bf2ac8a4847d03bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityVsCost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86b165fe28d428a5adf54195aec210d4877d661a354771caf12740e3dfde69c4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ede7eeb6ef8f42ce0c9158597efba7ee283e37fba742211381d3089b4781590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fallbackToOnDemand", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="odWindows")
    def od_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "odWindows"))

    @od_windows.setter
    def od_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b6efbc132ec15539908e4a50f29461b89e4b5de58238abea9d9df8faf5ef5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "odWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="optimizationWindows")
    def optimization_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "optimizationWindows"))

    @optimization_windows.setter
    def optimization_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32b2ab8e58dfef90b8286fb64f9bc7c9e7884926f94f8c4a6680a270450905f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "optimizationWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredLifeCycle")
    def preferred_life_cycle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredLifeCycle"))

    @preferred_life_cycle.setter
    def preferred_life_cycle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea8f004030526433b24c67e95537a9c2e796d8d425be8ea7538da118f653d039)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredLifeCycle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vmAdmins")
    def vm_admins(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vmAdmins"))

    @vm_admins.setter
    def vm_admins(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3d0dbe5ed79c38a4fc1f070471da168e384df3e06eec9b41ef5dec21f054031)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vmAdmins", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureStrategy]:
        return typing.cast(typing.Optional[StatefulNodeAzureStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureStrategy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bcbd15be3471ea80f52d91cbbc53879ac241187d8d70e219a624aa831fc9682)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyRevertToSpot",
    jsii_struct_bases=[],
    name_mapping={"perform_at": "performAt"},
)
class StatefulNodeAzureStrategyRevertToSpot:
    def __init__(self, *, perform_at: builtins.str) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#perform_at StatefulNodeAzure#perform_at}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52384c21f472920f1ed9cdcfa16702f0976a40c612a12b48c87a2046e12ad555)
            check_type(argname="argument perform_at", value=perform_at, expected_type=type_hints["perform_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "perform_at": perform_at,
        }

    @builtins.property
    def perform_at(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#perform_at StatefulNodeAzure#perform_at}.'''
        result = self._values.get("perform_at")
        assert result is not None, "Required property 'perform_at' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureStrategyRevertToSpot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureStrategyRevertToSpotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureStrategyRevertToSpotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__75ba36274800625800e0fe0a784d4f880a6cd6ea56af516794b5b169a20780b4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dae7eb91b0e4a90b302ef0160d7d31951b90c6e9b47a65bf87ad9a4fea506dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureStrategyRevertToSpot]:
        return typing.cast(typing.Optional[StatefulNodeAzureStrategyRevertToSpot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StatefulNodeAzureStrategyRevertToSpot],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85c0cdabf95d42018f83ea656250134a0ee000bf6392af69858daacaf7fb604c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureTag",
    jsii_struct_bases=[],
    name_mapping={"tag_key": "tagKey", "tag_value": "tagValue"},
)
class StatefulNodeAzureTag:
    def __init__(
        self,
        *,
        tag_key: builtins.str,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param tag_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag_key StatefulNodeAzure#tag_key}.
        :param tag_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag_value StatefulNodeAzure#tag_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817bf04892879f4e1dc8f47fd778b39c7ea5978d26f4aee283f9d36ba3db842b)
            check_type(argname="argument tag_key", value=tag_key, expected_type=type_hints["tag_key"])
            check_type(argname="argument tag_value", value=tag_value, expected_type=type_hints["tag_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "tag_key": tag_key,
        }
        if tag_value is not None:
            self._values["tag_value"] = tag_value

    @builtins.property
    def tag_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag_key StatefulNodeAzure#tag_key}.'''
        result = self._values.get("tag_key")
        assert result is not None, "Required property 'tag_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tag_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#tag_value StatefulNodeAzure#tag_value}.'''
        result = self._values.get("tag_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureTagList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureTagList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b2bc465117817aa1b5559d41a754f48de86dd74cd0184e1f722a46a0405e186)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureTagOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b1ac48fe6bb838cebfba7288052d15ffdb99c67e5781725d1db36d7f0fab223)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureTagOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04f15866edbbad68c4fead28d0334cf0a7793667e3a253f7d3b8d71a7e484803)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef70d61b85f469cde5e0d5f3bcc046832207b408dcfb49bee66bbe09c5a7c206)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18a7f927e9fca1d1f09fcff1cd9442a8028007a793ddf7e8072f66425b409c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureTag]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureTag]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureTag]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__337dcb5b33ef61d999c4afb8792f2c159539460e676e994bc44ed98d11161b99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureTagOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureTagOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f6b09ebeb29db90eb0006f06828b0170580e982f3208720e80ae4c22d2188a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetTagValue")
    def reset_tag_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagValue", []))

    @builtins.property
    @jsii.member(jsii_name="tagKeyInput")
    def tag_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="tagValueInput")
    def tag_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagValueInput"))

    @builtins.property
    @jsii.member(jsii_name="tagKey")
    def tag_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagKey"))

    @tag_key.setter
    def tag_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b63a3e3f31161c942e3d6299d3455a43a292e660af4e0f377060878360595b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagValue")
    def tag_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagValue"))

    @tag_value.setter
    def tag_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e764e1313e17a8a9d1847d3a31773704f5f9f43130e152b7d1f7e0604d581a90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureTag]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureTag]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureTag]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cac4fc1cc39d2be3f31915817dfc282bb4877197c25eea5989dd831bebf43548)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureUpdateState",
    jsii_struct_bases=[],
    name_mapping={"state": "state"},
)
class StatefulNodeAzureUpdateState:
    def __init__(self, *, state: builtins.str) -> None:
        '''
        :param state: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#state StatefulNodeAzure#state}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dee53129e1bdbbef6847574354428adc384140d3cc676a9549d4a98f2bbec4b)
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "state": state,
        }

    @builtins.property
    def state(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#state StatefulNodeAzure#state}.'''
        result = self._values.get("state")
        assert result is not None, "Required property 'state' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureUpdateState(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureUpdateStateList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureUpdateStateList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae502f9a82a8aa9a23021de7cb78cd9a38aa6534bec17bd89f7227542f565474)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "StatefulNodeAzureUpdateStateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d43ee6af8abd4aee5edab1cb007b3587a0d1774cb8add3349cd14809e008777)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("StatefulNodeAzureUpdateStateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8eca29f3e95dbea1fc8c1e09140f3ae291f95a5ac60698a1183ea39fdab2cad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db6c15891befdf40048ca1b743928877cdfe046947470571c9d7b3f32006d570)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2bf9df6635e71d6daf182ba297d3ad438caa6330b80b7eb388c575332e788844)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureUpdateState]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureUpdateState]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureUpdateState]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__612ee87262b7406f783f7bdd0695b90306b7149adca3deca45a6fc161c7e164b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StatefulNodeAzureUpdateStateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureUpdateStateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e2b8c149d2d85795d6f26ed1df44415201f6b756648eb76e453e30628a5b017)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2fc6a02f52cd1890b27ce6c64456f84d11a56d567be06eb19fe11ab97ad97b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureUpdateState]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureUpdateState]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureUpdateState]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04bb465116f264135bc1aa1d784b63a852df589e0a2f78ffd14e0eec0c559b26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureVmSizes",
    jsii_struct_bases=[],
    name_mapping={
        "od_sizes": "odSizes",
        "excluded_vm_sizes": "excludedVmSizes",
        "preferred_spot_sizes": "preferredSpotSizes",
        "spot_size_attributes": "spotSizeAttributes",
        "spot_sizes": "spotSizes",
    },
)
class StatefulNodeAzureVmSizes:
    def __init__(
        self,
        *,
        od_sizes: typing.Sequence[builtins.str],
        excluded_vm_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
        spot_size_attributes: typing.Optional[typing.Union["StatefulNodeAzureVmSizesSpotSizeAttributes", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param od_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#od_sizes StatefulNodeAzure#od_sizes}.
        :param excluded_vm_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#excluded_vm_sizes StatefulNodeAzure#excluded_vm_sizes}.
        :param preferred_spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_spot_sizes StatefulNodeAzure#preferred_spot_sizes}.
        :param spot_size_attributes: spot_size_attributes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_size_attributes StatefulNodeAzure#spot_size_attributes}
        :param spot_sizes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_sizes StatefulNodeAzure#spot_sizes}.
        '''
        if isinstance(spot_size_attributes, dict):
            spot_size_attributes = StatefulNodeAzureVmSizesSpotSizeAttributes(**spot_size_attributes)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03f6c2a72325cf8b5573a29ba3a7cc64b4d388464306d2c370d196f110ab2f36)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#od_sizes StatefulNodeAzure#od_sizes}.'''
        result = self._values.get("od_sizes")
        assert result is not None, "Required property 'od_sizes' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def excluded_vm_sizes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#excluded_vm_sizes StatefulNodeAzure#excluded_vm_sizes}.'''
        result = self._values.get("excluded_vm_sizes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preferred_spot_sizes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#preferred_spot_sizes StatefulNodeAzure#preferred_spot_sizes}.'''
        result = self._values.get("preferred_spot_sizes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def spot_size_attributes(
        self,
    ) -> typing.Optional["StatefulNodeAzureVmSizesSpotSizeAttributes"]:
        '''spot_size_attributes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_size_attributes StatefulNodeAzure#spot_size_attributes}
        '''
        result = self._values.get("spot_size_attributes")
        return typing.cast(typing.Optional["StatefulNodeAzureVmSizesSpotSizeAttributes"], result)

    @builtins.property
    def spot_sizes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#spot_sizes StatefulNodeAzure#spot_sizes}.'''
        result = self._values.get("spot_sizes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureVmSizes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureVmSizesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureVmSizesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d13071e0dc512665c36cbf94097a770b91f414caf7741a8079e551a8bf2cb734)
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
        :param max_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_cpu StatefulNodeAzure#max_cpu}.
        :param max_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_memory StatefulNodeAzure#max_memory}.
        :param max_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_storage StatefulNodeAzure#max_storage}.
        :param min_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_cpu StatefulNodeAzure#min_cpu}.
        :param min_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_memory StatefulNodeAzure#min_memory}.
        :param min_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_storage StatefulNodeAzure#min_storage}.
        '''
        value = StatefulNodeAzureVmSizesSpotSizeAttributes(
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
    ) -> "StatefulNodeAzureVmSizesSpotSizeAttributesOutputReference":
        return typing.cast("StatefulNodeAzureVmSizesSpotSizeAttributesOutputReference", jsii.get(self, "spotSizeAttributes"))

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
    ) -> typing.Optional["StatefulNodeAzureVmSizesSpotSizeAttributes"]:
        return typing.cast(typing.Optional["StatefulNodeAzureVmSizesSpotSizeAttributes"], jsii.get(self, "spotSizeAttributesInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__954cc863f7bcb7b78e04df425e3e1f4f60a67e332e1b5b82dab7b37338cd4d22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedVmSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="odSizes")
    def od_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "odSizes"))

    @od_sizes.setter
    def od_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc52fee69fa22ea4f2ac492df672de0153787d512ec953b72184552cb8a551aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "odSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredSpotSizes")
    def preferred_spot_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredSpotSizes"))

    @preferred_spot_sizes.setter
    def preferred_spot_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de391dfb0b52ce3964763ddab8f80490dda5a46cf438f2ecd1b4b1bff3f1e6ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredSpotSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotSizes")
    def spot_sizes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "spotSizes"))

    @spot_sizes.setter
    def spot_sizes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d6fc4a521ada480367cafd929a098e8419fe48b338a45869873bb3b11c0482)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotSizes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StatefulNodeAzureVmSizes]:
        return typing.cast(typing.Optional[StatefulNodeAzureVmSizes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[StatefulNodeAzureVmSizes]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e63700a450f38863691e1502f627dcff1a4e2df7b4fb1354234a8fcb032d63ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureVmSizesSpotSizeAttributes",
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
class StatefulNodeAzureVmSizesSpotSizeAttributes:
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
        :param max_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_cpu StatefulNodeAzure#max_cpu}.
        :param max_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_memory StatefulNodeAzure#max_memory}.
        :param max_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_storage StatefulNodeAzure#max_storage}.
        :param min_cpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_cpu StatefulNodeAzure#min_cpu}.
        :param min_memory: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_memory StatefulNodeAzure#min_memory}.
        :param min_storage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_storage StatefulNodeAzure#min_storage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c269de65ac4f2598c8e951deb0eddbfdef793e0c300caffe60654ba4b6a44909)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_cpu StatefulNodeAzure#max_cpu}.'''
        result = self._values.get("max_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_memory(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_memory StatefulNodeAzure#max_memory}.'''
        result = self._values.get("max_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#max_storage StatefulNodeAzure#max_storage}.'''
        result = self._values.get("max_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_cpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_cpu StatefulNodeAzure#min_cpu}.'''
        result = self._values.get("min_cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_memory StatefulNodeAzure#min_memory}.'''
        result = self._values.get("min_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/stateful_node_azure#min_storage StatefulNodeAzure#min_storage}.'''
        result = self._values.get("min_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulNodeAzureVmSizesSpotSizeAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StatefulNodeAzureVmSizesSpotSizeAttributesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.statefulNodeAzure.StatefulNodeAzureVmSizesSpotSizeAttributesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b489c0d9c802ea3e4c3d02a98c45c1ae6d6abd6edc6877de7561771e36f68d09)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7f9ccdf416922f2804df55f18e2dcae14ef0920d12a4f1024586db8ffdeee53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemory")
    def max_memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemory"))

    @max_memory.setter
    def max_memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f76bea7f5996abefd271884f783e3f8f6b176523aec8955dd956a3a5afb6d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStorage")
    def max_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStorage"))

    @max_storage.setter
    def max_storage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d0b01bdb1b4ab357c3f0bf5c1ea4444dd51d2f1edec46b139a41149f7762a38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStorage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCpu")
    def min_cpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minCpu"))

    @min_cpu.setter
    def min_cpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79d581a4a3c8c93ad7718497e21a9a6a6508335550e9fb6a3a057b420c3e2dae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemory")
    def min_memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemory"))

    @min_memory.setter
    def min_memory(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__129ed7f720e64086c4894bb5444fe56106685a53d4a92b91d532cef6893e668b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minStorage")
    def min_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minStorage"))

    @min_storage.setter
    def min_storage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa7d5b9eb471f2189ddaedd499155624484d04327a291787a17623b103d3ab3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minStorage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[StatefulNodeAzureVmSizesSpotSizeAttributes]:
        return typing.cast(typing.Optional[StatefulNodeAzureVmSizesSpotSizeAttributes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StatefulNodeAzureVmSizesSpotSizeAttributes],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c410247269967988c46ef0e3614bbd888dbdf3d7835e37f69b05b09a806aee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "StatefulNodeAzure",
    "StatefulNodeAzureAttachDataDisk",
    "StatefulNodeAzureAttachDataDiskList",
    "StatefulNodeAzureAttachDataDiskOutputReference",
    "StatefulNodeAzureBootDiagnostics",
    "StatefulNodeAzureBootDiagnosticsList",
    "StatefulNodeAzureBootDiagnosticsOutputReference",
    "StatefulNodeAzureConfig",
    "StatefulNodeAzureDataDisk",
    "StatefulNodeAzureDataDiskList",
    "StatefulNodeAzureDataDiskOutputReference",
    "StatefulNodeAzureDelete",
    "StatefulNodeAzureDeleteList",
    "StatefulNodeAzureDeleteOutputReference",
    "StatefulNodeAzureDetachDataDisk",
    "StatefulNodeAzureDetachDataDiskList",
    "StatefulNodeAzureDetachDataDiskOutputReference",
    "StatefulNodeAzureExtension",
    "StatefulNodeAzureExtensionList",
    "StatefulNodeAzureExtensionOutputReference",
    "StatefulNodeAzureHealth",
    "StatefulNodeAzureHealthOutputReference",
    "StatefulNodeAzureImage",
    "StatefulNodeAzureImageCustomImage",
    "StatefulNodeAzureImageCustomImageList",
    "StatefulNodeAzureImageCustomImageOutputReference",
    "StatefulNodeAzureImageGallery",
    "StatefulNodeAzureImageGalleryList",
    "StatefulNodeAzureImageGalleryOutputReference",
    "StatefulNodeAzureImageMarketplaceImage",
    "StatefulNodeAzureImageMarketplaceImageList",
    "StatefulNodeAzureImageMarketplaceImageOutputReference",
    "StatefulNodeAzureImageOutputReference",
    "StatefulNodeAzureImportVm",
    "StatefulNodeAzureImportVmList",
    "StatefulNodeAzureImportVmOutputReference",
    "StatefulNodeAzureLoadBalancer",
    "StatefulNodeAzureLoadBalancerList",
    "StatefulNodeAzureLoadBalancerOutputReference",
    "StatefulNodeAzureLogin",
    "StatefulNodeAzureLoginOutputReference",
    "StatefulNodeAzureManagedServiceIdentities",
    "StatefulNodeAzureManagedServiceIdentitiesList",
    "StatefulNodeAzureManagedServiceIdentitiesOutputReference",
    "StatefulNodeAzureNetwork",
    "StatefulNodeAzureNetworkNetworkInterface",
    "StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations",
    "StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsList",
    "StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurationsOutputReference",
    "StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups",
    "StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsList",
    "StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroupsOutputReference",
    "StatefulNodeAzureNetworkNetworkInterfaceList",
    "StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup",
    "StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupList",
    "StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroupOutputReference",
    "StatefulNodeAzureNetworkNetworkInterfaceOutputReference",
    "StatefulNodeAzureNetworkNetworkInterfacePublicIps",
    "StatefulNodeAzureNetworkNetworkInterfacePublicIpsList",
    "StatefulNodeAzureNetworkNetworkInterfacePublicIpsOutputReference",
    "StatefulNodeAzureNetworkOutputReference",
    "StatefulNodeAzureOsDisk",
    "StatefulNodeAzureOsDiskOutputReference",
    "StatefulNodeAzureProximityPlacementGroups",
    "StatefulNodeAzureProximityPlacementGroupsList",
    "StatefulNodeAzureProximityPlacementGroupsOutputReference",
    "StatefulNodeAzureSchedulingTask",
    "StatefulNodeAzureSchedulingTaskList",
    "StatefulNodeAzureSchedulingTaskOutputReference",
    "StatefulNodeAzureSecret",
    "StatefulNodeAzureSecretList",
    "StatefulNodeAzureSecretOutputReference",
    "StatefulNodeAzureSecretSourceVault",
    "StatefulNodeAzureSecretSourceVaultList",
    "StatefulNodeAzureSecretSourceVaultOutputReference",
    "StatefulNodeAzureSecretVaultCertificates",
    "StatefulNodeAzureSecretVaultCertificatesList",
    "StatefulNodeAzureSecretVaultCertificatesOutputReference",
    "StatefulNodeAzureSecurity",
    "StatefulNodeAzureSecurityOutputReference",
    "StatefulNodeAzureSignal",
    "StatefulNodeAzureSignalList",
    "StatefulNodeAzureSignalOutputReference",
    "StatefulNodeAzureStrategy",
    "StatefulNodeAzureStrategyCapacityReservation",
    "StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups",
    "StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsList",
    "StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroupsOutputReference",
    "StatefulNodeAzureStrategyCapacityReservationList",
    "StatefulNodeAzureStrategyCapacityReservationOutputReference",
    "StatefulNodeAzureStrategyOutputReference",
    "StatefulNodeAzureStrategyRevertToSpot",
    "StatefulNodeAzureStrategyRevertToSpotOutputReference",
    "StatefulNodeAzureTag",
    "StatefulNodeAzureTagList",
    "StatefulNodeAzureTagOutputReference",
    "StatefulNodeAzureUpdateState",
    "StatefulNodeAzureUpdateStateList",
    "StatefulNodeAzureUpdateStateOutputReference",
    "StatefulNodeAzureVmSizes",
    "StatefulNodeAzureVmSizesOutputReference",
    "StatefulNodeAzureVmSizesSpotSizeAttributes",
    "StatefulNodeAzureVmSizesSpotSizeAttributesOutputReference",
]

publication.publish()

def _typecheckingstub__d6411d4756ce105f886982172101ca71f8cfd1c221c0894ee68a36a4068b9a00(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    os: builtins.str,
    region: builtins.str,
    resource_group_name: builtins.str,
    should_persist_data_disks: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    should_persist_network: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    should_persist_os_disk: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    strategy: typing.Union[StatefulNodeAzureStrategy, typing.Dict[builtins.str, typing.Any]],
    vm_sizes: typing.Union[StatefulNodeAzureVmSizes, typing.Dict[builtins.str, typing.Any]],
    attach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureAttachDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureBootDiagnostics, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_data: typing.Optional[builtins.str] = None,
    data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data_disks_persistence_mode: typing.Optional[builtins.str] = None,
    delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDelete, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    detach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDetachDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    extension: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureExtension, typing.Dict[builtins.str, typing.Any]]]]] = None,
    health: typing.Optional[typing.Union[StatefulNodeAzureHealth, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    image: typing.Optional[typing.Union[StatefulNodeAzureImage, typing.Dict[builtins.str, typing.Any]]] = None,
    import_vm: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImportVm, typing.Dict[builtins.str, typing.Any]]]]] = None,
    license_type: typing.Optional[builtins.str] = None,
    load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureLoadBalancer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    login: typing.Optional[typing.Union[StatefulNodeAzureLogin, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_service_identities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureManagedServiceIdentities, typing.Dict[builtins.str, typing.Any]]]]] = None,
    network: typing.Optional[typing.Union[StatefulNodeAzureNetwork, typing.Dict[builtins.str, typing.Any]]] = None,
    os_disk: typing.Optional[typing.Union[StatefulNodeAzureOsDisk, typing.Dict[builtins.str, typing.Any]]] = None,
    os_disk_persistence_mode: typing.Optional[builtins.str] = None,
    preferred_zone: typing.Optional[builtins.str] = None,
    proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureProximityPlacementGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecret, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security: typing.Optional[typing.Union[StatefulNodeAzureSecurity, typing.Dict[builtins.str, typing.Any]]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSignal, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tag: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureTag, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_state: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureUpdateState, typing.Dict[builtins.str, typing.Any]]]]] = None,
    user_data: typing.Optional[builtins.str] = None,
    vm_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__68e68406114d80b6f06b42a2e346d92131682b9b2f828e77a7ff5fafc1f5b6de(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9b9a4a2bcde5f8294895858d40a9a36d5332e157c5987350baf1d7b315dee9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureAttachDataDisk, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b079bd829816c17192015c3ddbd43871208202c9ac690929b7a82011d632748(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureBootDiagnostics, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f319aa7e79daaa65437d5b3bfb0f3e6d2513184e58aa023425abdce771f4b82(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDataDisk, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c670de37fcc7e8dad922bfbe7c34e79db4512de52f9ad37d3cd3aa3708ec98c9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDelete, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b49a282ff9f2c0162752d4dfc8a1d0cf8f08d4107c130442d84382821081a51f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDetachDataDisk, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a0df44362e03f6668355d53a0c0bf7ebc36e1b84bdd3468b527b56da2ef6b31(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureExtension, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b287b7326269cb308907f1fbdea179797f6551389da4ef3b997dc0c5aad9a4cc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImportVm, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b4c1c0381481bc2364076b89a29d3dc0d7726efd504243a0813b66ef66b0e01(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureLoadBalancer, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d03e79967c9b22aef6fd1c4dd396b536ea5547a61d96574427a9fdd163b3ce0d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureManagedServiceIdentities, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__238973118137de900a9ac9338243fa431c978a3c2c0c716cc21b46061bfb9259(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureProximityPlacementGroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c5a840305bf927bb881444590f9fe8beac1625afc3dff55e05ea5bd2f78cd63(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSchedulingTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b2339d4d512e0e51e1232d2c26b0021edf28e08af67737beb136e573d20ff33(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecret, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1bc6d3eb288e8d6cd408fed8a2a2b5db96e45b964a9a487770deeb7af8ef87(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSignal, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b732fe6139805b68483601195e712f36f7c35385ebb86db47a82b4e85689b5f6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureTag, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce320be27fa4e3cbf421c284beb997fe11ef438e69e827c93b408fb78e540308(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureUpdateState, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d316377dceea66757eb22fe2b05ef312e65140ff513f2882ead764caf0b34208(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__492c391cfd62d3468e9c176f97d615d8dc6c54311b4b601b90909afd8fc10ead(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072109a4cfeb07e69ae8b1060bc7819114ea9e14c4ab0bae22e588de250d7504(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e806a5a9bac88f0ba083f3d93b47547e0f8821ed356662f73b5a41fc11f0199c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deb2d415e559785cacc89908312a91f1c0cebc3a26eea08e75e7744dd6b6787f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d8acb333787133ddf6830fea172c66e453cd4cffb1086a2af0c38fa8465a07c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d3e75da2bba021eb4d7dfd31daf37a42abf883afce11ff1926a65e271c05592(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e76c18cf83d1461f816832807ee7a0dc5d240e913b5474374f85ad077b22bcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0236d4736f4366915bb387445700c71eca205758321157f5cef6f8df81cbd4c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67a45fc161df8f45de3c6a783620a6381f9265845149dc96c8451435584ea186(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20150ed9e9f74acd4989fd81ddd257caf75368474a2cefc401f962adc07c8374(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e901d7764a827b172653b56a34a02dfb52aa58ba21727bfa49916cd5fe875f9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6eb12c12857324902ddbde2b92a9af097ce72ab79cf8f629d8ba21422052e9b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2ea101ac225e24334776d652196f35d95589dacf52152e7b4e87c8c923a76c7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e5cd3d349f5c29761e8f8a1160f7342c90990b90ce5f086d650b0d56acb6be5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b40adfc923a339ba99f3326e049afa4508f8f5b63163bb055c40782c59894f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddd0bf712083572395202a1889b30cf15d7e2ada471453c8a8c1e79ab1f6d723(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa3691e6abc2e5d624774fc5c5cfa7a2dca609d085e77fa195c3012d7627a547(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f862b6ab84d043a7be23c8958db6e8e123d111ffd4a53eff51c5db59dfdbc600(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37fa66e7fc3311a23a506c4976a81db1f604e07261e5bb5bacc461b5cf465b4f(
    *,
    data_disk_name: builtins.str,
    data_disk_resource_group_name: builtins.str,
    size_gb: jsii.Number,
    storage_account_type: builtins.str,
    lun: typing.Optional[jsii.Number] = None,
    zone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b74355ed3b997e611ff9bc0342e9cd9b1947e57c5e23ed4b6ec20cbe23221a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864c54851a55e5ce1529d0d215e19cd4906deb00fba96b0320d57fe41f2435c9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c3e5cf4267b072d3dc4ef38e2f5438167cca121b54152e5e2df38571ec102dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc2f3fcedf29857275245b2198bc04b7c45b246ab7da9d2599545bb7060c55b6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4abc19cb5494da8120ddbd9f1c835c5777e4c1d934dea25ff9a7aae91121e5a2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a8f16cb3e19b7d738138edbd3a12044344cb73015d1102ccd397225bc2ba68(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureAttachDataDisk]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50e677eb80086cf96e21a65757c8b71a700c751d9c861c4cc6c2374fa4bcf950(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6294fd7f368c05bdc17cc7f9e1612b273e3e8fe266369e4e7aedca8b768b5fda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f336286335b85671f18172ea9843b886d8a4feae5c0c8cb41237cd152070c455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__336098f54b2088e874ec8ef2bf62d5396988283217569e2b2ec11541059d9bf2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ee47a520ab1ce5c9a362452254af2e7869a7837a9dd7e54b4110bef49c9654(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b2c34dc90177d4c74e14c744877cd19d30422405114d8120f5e43608947700e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c5e9b2db1fdfa2902f8a0ceaf3bed728e515b4edb0e903142cc0efbb889f658(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f02e58867a1acf42bb3ec625ab3145414f2cf706b7a329027542fc84ff3e2863(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureAttachDataDisk]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5dbb937b0b0d245207296df23d9f1ab1761c267580812ccfc2724545b949925(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    storage_url: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6537f2ac563fa32fc3698118638d0c9bdfd81f83c294d32679e53bdc7918be8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee1eccd19f5d6175f3b04d8f3244a2f999889f693ef1605bffefcb3647189782(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc043ff72b0d1128490ec7713ba8ebfe603e9fbd9c92aa24c8b739bdd061b328(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0235ecad67c297943ea6afd1a9b6ff0863b730f922ec91a231067a031ad31209(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__270182408917dd46efdc33b382cc2b8f48bd14e3321115daa59f6230c849296a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86aa92cb60c962b1024868e31ef933797b9dbd59688045da1aa4580f633223b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureBootDiagnostics]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c26fbe89267bcd6015185a04636f82d8710078c6beddfc73251caa5ba7303e06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28bb1a0f6e4a4972a77ddac9fdf9536f1f5678a6c515268643fe2bef28afba0d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98a2086690acf26f5368b0673d163ade6a9b08e889c5018498772c75b0c63cf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31537207c7b06093e0bb26d7440b598818cc1e5948bbafe9289e5b7e4f6a8437(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d577b50cda2a9e3e457c1d14228b24b578c7a188cf3a1c91a37ad86036ed5dd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureBootDiagnostics]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dc9d46615263cce03aa63961496271cbe7bb049936d81ca31550780bc76ee81(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    os: builtins.str,
    region: builtins.str,
    resource_group_name: builtins.str,
    should_persist_data_disks: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    should_persist_network: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    should_persist_os_disk: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    strategy: typing.Union[StatefulNodeAzureStrategy, typing.Dict[builtins.str, typing.Any]],
    vm_sizes: typing.Union[StatefulNodeAzureVmSizes, typing.Dict[builtins.str, typing.Any]],
    attach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureAttachDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    boot_diagnostics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureBootDiagnostics, typing.Dict[builtins.str, typing.Any]]]]] = None,
    custom_data: typing.Optional[builtins.str] = None,
    data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    data_disks_persistence_mode: typing.Optional[builtins.str] = None,
    delete: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDelete, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    detach_data_disk: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureDetachDataDisk, typing.Dict[builtins.str, typing.Any]]]]] = None,
    extension: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureExtension, typing.Dict[builtins.str, typing.Any]]]]] = None,
    health: typing.Optional[typing.Union[StatefulNodeAzureHealth, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    image: typing.Optional[typing.Union[StatefulNodeAzureImage, typing.Dict[builtins.str, typing.Any]]] = None,
    import_vm: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImportVm, typing.Dict[builtins.str, typing.Any]]]]] = None,
    license_type: typing.Optional[builtins.str] = None,
    load_balancer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureLoadBalancer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    login: typing.Optional[typing.Union[StatefulNodeAzureLogin, typing.Dict[builtins.str, typing.Any]]] = None,
    managed_service_identities: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureManagedServiceIdentities, typing.Dict[builtins.str, typing.Any]]]]] = None,
    network: typing.Optional[typing.Union[StatefulNodeAzureNetwork, typing.Dict[builtins.str, typing.Any]]] = None,
    os_disk: typing.Optional[typing.Union[StatefulNodeAzureOsDisk, typing.Dict[builtins.str, typing.Any]]] = None,
    os_disk_persistence_mode: typing.Optional[builtins.str] = None,
    preferred_zone: typing.Optional[builtins.str] = None,
    proximity_placement_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureProximityPlacementGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    secret: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecret, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security: typing.Optional[typing.Union[StatefulNodeAzureSecurity, typing.Dict[builtins.str, typing.Any]]] = None,
    shutdown_script: typing.Optional[builtins.str] = None,
    signal: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSignal, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tag: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureTag, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_state: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureUpdateState, typing.Dict[builtins.str, typing.Any]]]]] = None,
    user_data: typing.Optional[builtins.str] = None,
    vm_name: typing.Optional[builtins.str] = None,
    vm_name_prefix: typing.Optional[builtins.str] = None,
    zones: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46bd427affbbcb57948aa812c8f8785f105b7d4362e40f869894797263b37461(
    *,
    lun: jsii.Number,
    size_gb: jsii.Number,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__147c6bba9d288d43999b0fbf41dfa1c907d967bcac9e1c8f95fa17af7e8f1255(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7532cec5ad7e3b3cb054009484f612e0673db5d452796400cf96af0896c30c8e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3905a1f785b578e49ada588786349f9f67255c047b7bf37972825a65fcb39e94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d0c9ef9c3efa4a2ebf6fe0530be0b1f27b759e014e0b6f1053fa9a7ce99ca72(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b275c79aaa95f5b984a1435f0af387c134aaaec06df36d94fe1286f52e0a7315(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e25052b27f3c7124599fb125fedf07844f50324e9b1a2e9339dc8ac24a20bb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDataDisk]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57473a8186b5e59920cb6830e859332cade8af2e3464f1e0a495edcc96648d39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__017b59ae557f5cb9385c8943e7c4e1ef162579e187e481953ea8e6171ac35f83(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af4983095b2f52e926ed26d468a9c87882640c545d6e6a38914192beace66f10(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a94d22ac77e53dd422a0a795d3907b912d57f6a106e1e058298b6a7f90f4d28b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cdaff2a888496fa2367a9da93fea7bd1c824455c209b46144478a2b36a88aaf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDataDisk]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ab16258cd4612bd33c67b2ba337c03d38eb9b497f3013464cd073ffd117fbd8(
    *,
    should_terminate_vm: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    disk_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disk_ttl_in_hours: typing.Optional[jsii.Number] = None,
    network_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_ttl_in_hours: typing.Optional[jsii.Number] = None,
    public_ip_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    public_ip_ttl_in_hours: typing.Optional[jsii.Number] = None,
    should_deregister_from_lb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    should_revert_to_od: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    snapshot_should_deallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    snapshot_ttl_in_hours: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b65a5c6e1b20481f582f2b915ebed62652624564d7ebbdf36052dd8ab22b722f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8841cf3edf612c0f6a6407ebd416201506148b483a901b1aabd3b8480f2379d2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61fa96a0f668597899159ad405c93fbed418437966f09a2e55f708a0bffdaa1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea6cfef546af4433ea94f0165624cb3353d965fae471175fe109f2a638afaad0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceebd77e50a2ae03ce64d7d372a44e3e906c0d01a2202190134c5a768c6b34f4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c19333ade9bee5af9313cc085a59e32244e6f3c91950171b3e9dab102462a612(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDelete]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d2240f639bf70da48909d7744335325dd9080893a225271c9b90273cfb79396(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f120509966c51a311e9efd278caf3a4c1629086bc07b391430e813a67bf743(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ba3932257a965b634154c67c823b5fe9a50b904d32d2c5130520cf53eee3795(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7df51c22dc9e1aa6d08f31a8e8898d35fc9450e5fdb0fd40f4fa2c0874ac002(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07eaf635a0ee130ae1ff9ea3f25a3afc1efb38e71b879dfb2d13db6420925242(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfcaf6262908636179a6018c3ff127e2d1df0b52089b45e7ef2c48d09b8ca890(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b564e7184250320c2015540ce0e7fe0422769686e1487383d7de6524de5a037(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77cb40a610d936aac18b22ff51efe90b97ba2252f733296ff0482f626d02457c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33d62160e03d23bed8e0699432da50e6f55d066736539f1436cc0a82b05f074f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72d8e0e5cf53c3b05416eb336b64d9c96b1ce41f66e4bc71780f3ebce6334feb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d6451916f3302d77c4b0edcb9fdf2054d06876559551a219bf0cdeebf256a9b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27bdc411ed3d70b186b40aa891e3c5eb70c5d7c645afe795132398646ae0148d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb65a74718c3bd895ff48e53c3496fe10cfccb4ea3dd7ca9e0d767b8acc9b16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDelete]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e040369f3ebbca96835e78cefa0697195372ddb6757a199c5bd860971551c59e(
    *,
    data_disk_name: builtins.str,
    data_disk_resource_group_name: builtins.str,
    should_deallocate: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ttl_in_hours: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a949ab9c1f61194108b58638ea038c1073d3bd38f69cfbc001c205ce9d60b56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b74b17559f326d68a34f966b6a1c099d68b171f5869f905c5558667e061c6808(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__046c751031ca6be1e7d725a5e9bf2ac64c31de51ef29266446bdfb88680bce24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6fd2fb505ae0cfcb1f0cd1962002001d77368c317bc4b0f0585b2e9859cca6f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d03def7f163a19f7aec955759f0e5fd0b0548c484d256819901cc6681ac460(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__980b7eb6eb2977246ff6ce4704b896ab3e37d85d68bfa5c75ca92f9a3226e200(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureDetachDataDisk]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4282c0ae89fb12614c716cc13ccb90629bbbc86f452e02730b656b3273b8693d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__718b1bcf35a44198029514ee45c1f2d9f07722901ffe7317496cec29b2bbe1d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4495bf55e5a5d0a645346d30ec4a0f506ac09731b980bb8b76739aa15fcf3d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66b08f4db8f3324e2f8af3d94c0f70d5429864bc8eeefbe1cc17c928b83e7af9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e100aa3ae8b9f0ba75afc353778df86afb97ca6e521e3896075f13562b4f41f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d4494fc0f39f9f43b448b48e6ce0a5d9a51b1915790677d5dd686fcb4090e72(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureDetachDataDisk]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb654f27722bcb038b48941682fbcd1c89eccb3736e403d55bdfda25f6db19e(
    *,
    api_version: builtins.str,
    minor_version_auto_upgrade: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    name: builtins.str,
    publisher: builtins.str,
    type: builtins.str,
    protected_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    public_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0956f0418dd194f83d89dbf3170003722816d759ec807601e49166096bf44a9f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48567fd6118fa59cde500b8fccb2b785fdd178e64963148f72e4300f13bfeeaa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c322ac63a7a22bde485bb62c3d1a7ab2c10f999d715f96c391f3ab4bf000264c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0875e4c46578185900487b752fbf4f9f2aed2b96967ededecf486236538243e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a39c37c0f89e871c429d446178677ecaeb6ffa0dbbed15dbaf0665eb53237db(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__863d1fa54e9f8dc19118b60880c3a5b69cd3c40fc0ed17f58c99e18d932b05f4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureExtension]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a0c6f19fb6b963d9fd65f1080574cee3093d80b1d5b0bce1660f426e92b236f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0760344e21c0083c804006e9b804600159ffe57b900d67fb789246f61fb4e6f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef45cd8c3d3346ae788baa53502cfa8866926f51556fc4fe0d0cd694bdf89767(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac1630a4698380a243f89e9545370d14d67567227414ac9bc80f08f53211f3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7837c5a51a67e35e4ecd2047813d5e3fea8fb8b04ab7bbfa3d0ba87fcf3bfc97(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a78f843611a0c9e35d30677a9aae9d7c2400aaf5d3402d3f4b4b1d3b6438ec94(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__849d257d6c61631aaa200c0de5e7b21ed52ee7fe1e9c7547364c2bfd2a2eb482(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3239082acbdb30b36046f5117bb77aa66f505718536ee12158d6a735e6304d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09810de1a45f64f0c3a4887e417bad454ff3686a5c5399b71bc159cfac868f3f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureExtension]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73a02caf1b4c25a57b44eec6babc2145e0117e0e2c1115d11b4f05689d512c80(
    *,
    auto_healing: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    health_check_types: typing.Sequence[builtins.str],
    grace_period: typing.Optional[jsii.Number] = None,
    unhealthy_duration: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c4d859a2b6ea96c99775ed97984d50e1a5f035d44ca1bd6c512f960f8041549(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__304f94a2c2cf4b3e67d04cb6c3af01622dee6141ed16dcbfcda8e2e34bfa7a7b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54d0b6617690e92041262ea6244673f9749e6444f0a06e75b6b5239a0333f594(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0674113eff7a4243138212c36ff9879cf613ac47caa5165477903548a4a9cd67(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb4aea834efbfb4a92bea90121d1fbb5bfcc0a68c2325479e116026f3f069e3a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1dbf64158ab1b13e01a3692ac4cf297f5212a555c40ae0b42df40a8231a7fb1(
    value: typing.Optional[StatefulNodeAzureHealth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb7a1029046889a479ad40042cb3c9f03c10a9bfab03d0e3abe67bc2a818eb5f(
    *,
    custom_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageCustomImage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gallery: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageGallery, typing.Dict[builtins.str, typing.Any]]]]] = None,
    marketplace_image: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageMarketplaceImage, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f8f3fb8ebd08c5e2821a8f6112a304c3f422576e849be1be6d7b08b1f422f3a(
    *,
    custom_image_resource_group_name: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b2129e79f55ef4fa649daae1608bbb8845d006a755554e7b2c9642f632bc8fe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f15c29b36fd45116a0373ba27869bd0cc674fe488b1f78374d5db6790b0468(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8f2b7aee3c700922040217a89394de2e2a99aee62afd0f98f7be49fe45f6d7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4a1e5f598c74fda5bc1fa371dd0cd8b63ae51ba097bacf47ce6f5007d9aa803(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c26f425a3cb0611641d6bdca207df67e45725274d62fc7b0444244691552c9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b6ec25baa161d4c2a3e6e0fd843dfeebdda07ecdb12c3e264acf3d05a45d13(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageCustomImage]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbb6dd311f8b2c0bc2c33b71e133ab9579a987501d05baa5e7f748dc4544a582(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__489ed4df2123046ed7bb1368088f8c3f8fc6a0f84b6f5019b08050d9200dca55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a90d87ca5ff9fcc336954e2b6c231ac70fd15a2c94f0ae5ec99ccd3f52950af7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__647e15b61ee53348f5d0f4e2610bbe1a8fa7ffca40836e9e7f5b48613057e6c5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageCustomImage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6297cf253ba8dfc737c1672fbe7ea747e12e248a5314e687fe414164629c62e(
    *,
    gallery_name: builtins.str,
    gallery_resource_group_name: builtins.str,
    image_name: builtins.str,
    version_name: builtins.str,
    spot_account_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd25e75d79cd3df17f6e6fdea36f0b0e6e458ee9547c0d704195d59a84d3baa0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5accf099d2948a92b3024172efb74a07359f6033fb3e422697e1b03f65782939(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dddaf874e1b73a32c3ea70f96dabe1a0cd84fc5f8f67046fb80bf2692251d420(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827394886d83af0a0fc45a65f679bc1488098014bf3d47658253e3562ef2c844(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__447826dab3d348bdf7d6778084201a02f368f1d5623da620eb2eed67fca11368(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c269bcdbfb4e9988dd327b477dc768a4f32e773978bf7049bc46ae8d1bb06eaa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageGallery]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db0483dc826407d49492fee66fff9cc56e9bc87ac0877ab01659ae4d6a24d60f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f09bc07e044e0cf94987110b28098bd8d20065d6eb28091cb9e4abd7610a92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e074837d44f1da14ee3c971520d9d07b7d4f5c27fe29768b109d35612259bb6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc1ed6a92e75b49e449549bc13650a030fa69b00bf619db181ad364176e9dd5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e2fef43e00c2e5cbbe8b009fa777eaa33e2e66e6cc5c5e43008c2f58940f08b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52e6400d8edc18ecc17428994802df01c5e53fb242d15c8e5d6688eaac3bd732(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9ddebace9b4705dffeaeeca3b2d3c11a08c1081035008824eebf41ec833363(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageGallery]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__466080c36e49501ae45aebfc75be36089f7eea101ada7ed3111f15f7e98e0f1c(
    *,
    offer: builtins.str,
    publisher: builtins.str,
    sku: builtins.str,
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16e861042675ef4aae25ee22a7a8fd2c423603317a56540450ff170923eabb16(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9df315e11f7ff515d90805e24abbbfcf62869b541e23e5023c58fcfa267617cb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0e3fadb0446998f92ca4b33145a5296a05e170e5e5c79e570ce68e2b07c5ec4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d009baa8ee2ef977fb775adf5815e944efdd5e7909bbe959360b2df2c4d6916(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72df1ecda6387628e071133c19c5d8e1615eab4b38282e58e599699cdafd2d91(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9300f9da24cd3f7470f779569e25a640bc4567cff7e803a66d222e489c73761(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImageMarketplaceImage]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__612d2c0c124902c1ed79000175b6bf837282c1b82578d2e3e587b18f9302b5c8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cd070c99183239c1878eadbc8febe3cc8e614761257c701765d1ec50cf8e1d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78aedb905ff195b69a70574329a5337501934f890d3f2aab2aab5961de10b6e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c1f474836c9b5a42561ddb71c2d4d66419f62bb17087742bd223e5f2fb40a40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60bdc10bd84ddb0ef7aa075ff58883528d61a5e1b0cd8e0bd99cab7a19d46a2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2bd9be6cca6edf679cabbd20a03e78bcafd04752303920c3a044598a4b1bb2d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImageMarketplaceImage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de9fc7a709f3fe1f02fe80f189e0ca49b43403c74f73094f3f2a4298d02d73d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71be782dfe2b72216cbd7a3439bf8420600f17501e93c08cca99ee7f056bd6cd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageCustomImage, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d580a204dede454c4110ac0d543eb68e69cf157d5ff7e2dce9f5f55468e5677(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageGallery, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4121bcd674b4e86dd591141e8d7aa2c103ac9f4afdd20213382523553a16a3eb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureImageMarketplaceImage, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7384c56911d1c6e57e44608d0f9107b52b74775323ed6dc6c180e77aa49766d1(
    value: typing.Optional[StatefulNodeAzureImage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be7351e844c3343bd940d98572583cee8d15b113039afea6c958d9814a056f83(
    *,
    original_vm_name: builtins.str,
    resource_group_name: builtins.str,
    draining_timeout: typing.Optional[jsii.Number] = None,
    resources_retention_time: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c1ee486e359cae50f47a85495ab873bc1ca73515b5df065f37eeb6bd3b24d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c177f42e6153fc5dfc1ba09aef347592b2deaf5af56aa90e28b08b9cc5cf9c8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23aed64b74ed4834e00a4dadd15a6a898a5728a4530e8aa92a4a486303177b0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1653b76e0a503f4159ad116ba93e2dad4cc20cbc4ff3346a3dbdc5cbbe50bb0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__687d586fdc7093c9705537d58a67b4b5c6d0ab3f60648b756bfa55d5575a06da(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc958aaa5fc0604f94a9bdb9a50bd3d4f89d4290a6410374d5d2d6c88831b7eb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureImportVm]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4a406a9161348fc252ddf9d927a00a338ed5134cbd0cdde8063ed13fce6952(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__783869455be086aebf98344d2d5c96203e9bd2aaf9b401ddeb5ef510c74a6dfc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e027a50c55b28511a75b0bd8d3e1633ef6e84ce5323d8beaadc886afaba0e664(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8fd474359260a18f21eb7194079313a573aef47afcc0d83841984b33406ff79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc061fb0feee7a813952d3ad730f0b6d2465a3a61961611e79e6bc2f6ceae58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd17d64c7d3b081c7c329ad53e49ff8f35b6b7e8ea273b7ddeec62e3995ed9d4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureImportVm]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1c173d323a1de47373890573be7888c6a1739ebdc119ffefb92df0eba0dada1(
    *,
    backend_pool_names: typing.Sequence[builtins.str],
    name: builtins.str,
    resource_group_name: builtins.str,
    type: builtins.str,
    sku: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f28e61306f5c4747b31b6486993faac8f7e02569f014fac339d416715b0b579e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b231227197cf1b91533aa6744153b1a7e0088b38b1b70bec695c1432729f8040(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b47ab51ccd3e16c40e464527265c89a4ec2e7e0747f1884dc2ef28547f784808(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ea8f37e1ea939a0f7d789ca0c90b89cb635d1f9dc66265a9aa72bf1b443c401(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b627fddc948b732a527c3043288ccf9cc9030b5243ce334770f9de56921a061c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e7c6f220045bee05bb763c81b59d1f4a71c250064e8c810e1e1e99a8ec91908(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureLoadBalancer]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c41532f8c2882639f2bbb241d7d97f6b3034d5f627d3dd5ba95c94ad699ce3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df7b5bcccc266eda05ccf51ae6b77614757e3750761d6a2b8c7f56df13989ae0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2920594e4105a65aa761a56633d27d7be04cb63197228a2e58c95f5368ddd209(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66deab7f0ae7a1438be21a333ce800ae0bc6f1a9bfa99dbfff6518e437585350(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f43b43c5067119808c45e369a5fa414a7a93bb8494b28e9d2dcfedb1b83b0df6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff1f62057873a3a7b41253966d33bf6ab7495b55f3c296cd2415a088f1b6476e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd4aa6d67e79fd8a334613c2dbff61fa2098e66b12d1720dd54c3dffeced9247(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureLoadBalancer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96601510d4b06f6c38006df8b858f45883c0bc63e10c02a3610a4b5c7ca71948(
    *,
    user_name: builtins.str,
    password: typing.Optional[builtins.str] = None,
    ssh_public_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b1a1b3aa8a2f241ec57bc3c4b0453c1fef4273caeb122d6c5e263ab292d3c5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdb17e1fa4a69d64fa42f4ee9d671ceeb20270679b14a437e49cdaa63fb8486b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d09e207d3e2658be7c391d7423941f1a5dc2b18f37c23ea1722d24e8ce4f3c94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c62f3fa2e24ec1162d08f7eb1fcbfa9915a3bdcd14a09a76c97fe6e4d00c7e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9247cc0278d8872cd75c060043c705ccb5a4f8494263927cd08bd899c5596e46(
    value: typing.Optional[StatefulNodeAzureLogin],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a824252485a42b849e2b2082e28aaa3207e7c5d895fb4666bad6d08fddd936f7(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
    subscription_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88bfd7a2dcbef4de768598b0aa967fe370ae9c80d4d05b8c9691c59c79dbe783(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac7a88fa1b044ba06853c5b4ba3f457feb2335a680ab48819d58578b92c59553(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b41514df8d3e926ce168c1b1bd6bb883b1bd12e4f63f970468047848787ed334(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3291878154c567356cef354f704b5ccbe12a566420fa01df2f04de4a423c8d51(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__885dbb59c307bcc496a709c3b971095ac832cd7e786464860bf38973d07a8169(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a6e238f7574dc1d31a84cc1490ca800c7e8b9c81998f69c5bf73285481c847e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureManagedServiceIdentities]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd4ae959284b4d38d6b53db0f6130940ca3ecb33fe5f6f8957a8cf154a08a620(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dc302897dc66416e62b6614356d6d0c5ab7e73545125760a2e629a6b36438da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba03cfd03217db04e3672ab17187c7ab1627453d4dd23b0021d6a7687e0a0e3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba599bfbf6ab5c9c6e806fd32b8fc47889ee38e7858169032f1ba6d45244d17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__493911c74bd9d8bae5507313c5778dd940e0ca4d67b73d47a0e954bae8743e7f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureManagedServiceIdentities]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9c917e00ecbfc11bf51b8c5b09f5bc5d55d32303b20b2658cc61dd98ce1d10f(
    *,
    network_interface: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
    network_resource_group_name: builtins.str,
    virtual_network_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55f0a16a5fe3e99e816d3cbe29fc093d4b8e1f174cde9053f89ecb804abe0a05(
    *,
    is_primary: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    subnet_name: builtins.str,
    additional_ip_configurations: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations, typing.Dict[builtins.str, typing.Any]]]]] = None,
    application_security_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    assign_public_ip: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_ip_forwarding: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    network_security_group: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup, typing.Dict[builtins.str, typing.Any]]]]] = None,
    private_ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    public_ips: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfacePublicIps, typing.Dict[builtins.str, typing.Any]]]]] = None,
    public_ip_sku: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8e130ddd0b1e107fd066196c8671e9380f2814a0ed526a2581b86dc645a7af1(
    *,
    name: builtins.str,
    private_ip_address_version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3ccfddc53025ddabd4e1a096fe5ff1cab7ee230b4c0f112d3a4f6b5fe85f28e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da27e0b58b4403df2e681e3e5742e0d465ceea7b4e475a2619f9ad99b1eb25fe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b41a520b24700013c43928378bf8cfbf6117c5876706aa8af7fbe45f97ba4a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33f0cb3857842aa4ab9e2e28eeb7c80827c0815f5b4e14f4c395596937c003fd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e369d7f8da8fd7686c115d788020768dc6d3bb0d17655c58874206031ec5bd6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3f4c983bea3f8e68ea3df9333f776170d6d96451a2c49de5da390e20d39dc21(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a013be5a5bda84fc3694f1c51a33957adab51dab1b0ee0900addd4649b609fce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__686434b791e18809c1777d6a21783c909eda1492c3b57f9394021d8f62b2be3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcf2044b634f8b08b511281cabe1960dcabd39ededd1bd658e13f0dafb473a72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__473939eac060d5606bba48983aee8ed3106f5f14b19015272752e3eda5c5dd38(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__384b98238e7750acf201453a2c93502b621893147fe4e51cd1972d6cf76e09c8(
    *,
    name: builtins.str,
    network_resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe5e1f34c14c19202d344d641539475773b8a01d183cae35e7a7cdd60304c9ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b04ed1814106248a4925880741f9ba4846bae02acd457acf0222fc7b5ac6a0f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af82d4486d268265bd727a84afeb0f2f49fa7fd0851ce721dbdaa74134e9e946(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b2429a32304a99cd906a482f8dc370041a7cbe98d7acce0d178874f03961011(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31d56acb6f380c460ff698177d50d3d9c71d462617d13d2b8ab6fc3333cb07c9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfa79fa8c610c1d94a7f0c79a78d83bce067bdbe842c59a36af06640ff211eba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eb1e81f004e8dd8373d260fa922d0e1f6478a769b76460b04dcb24aee97dc7b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__226a3e42499adc6f8fa48c3d5cbd6e45530b667014f076f7ace81366c3868b1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__432f4fb49542439c327559fbf4e23d6c21d2e48088b5cb565bedeb8bf68aae1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8d5a10afab02ee9118706f975259a22cc07c5855a5f7b9c39f4b25757c2a0db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9a454e326880a3d72eb92514a34c93936bad5ca519f9727ff5c6b25b79063c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5116dce8887868909273c3801da530bcff12f0a3bf194ae8cd6ef41e2202dc31(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5388dc141ca1c16f0f76299fe0667bde84e59b66eb6072dc50b847d53b9d9e26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62c7ee00caf5547cf330ad9115b5f1e7987cf6c553dd09afbb49eeabac363b4a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d6a628fe7f87d3e59d21ecd96ab9b94eeae641e86b0de91c0904b41167336d6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cb0d428f82e0f60542c6faf44df426c523c648b1690bcba2b7ee9e462e72a27(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterface]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b339f0f55e43be4cd95641b6e696ffcd2bb2b0f69ad6177f7f2b2b0c731d63c(
    *,
    name: typing.Optional[builtins.str] = None,
    network_resource_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9659f4b1e9647760077b7bdf891d1a913152c9a7e2bb70b1db88c44632870b7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92918997cea4f00d7d7a6b4491e4db37b10dfe3a2873ffbd4d3fcc714eb9bd1c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f28cb38a184fdbdb78487804c15f6c6b2986b09b06f920afbbb3cd9f48ad19f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1923bed51ca5479cc48f4bee12886948c3a5f285dc28a3f64bb8a8d98ad1eb75(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac68d3e67c28d1ebb6f1a2bd536ef0b12bbe2b97e402138567fa019f565bede0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__506302e25bf91e39cfc26e29be8f0193d711021897aed4714dea0236505b7838(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1055636342b823fc6e6cd4c1b12d8c8d0999c432f01527766e13259aeb1cfbea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__498acd8c9486890345e6301152b447f8ed687d189a35c979891cb984627b4cdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__719692c1640485f9c9f4ac9a857afe97bca6adaa7da675943146a391bb365405(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09e2951ca8bccc487711450f95f8fbcda90888c9470dbc34d57b2ddc5be3c10d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00f4beb3daf377c49438ff77484cfd02f4fda960c81994dc9aa311029ccb43e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45fbb37f30be4756956337662a9a127db53eed53ae5b8a6155d891b0a4e5e6b7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceAdditionalIpConfigurations, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3acb3619deca3e9d13d74a9c1fd150f45cde4267ea91d337ee44fcd0a6fb62cc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceApplicationSecurityGroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1da10c91f0fa66fa3f8544e0281e453ba6f44db3f6c9618e56ed2a06a008a04e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfaceNetworkSecurityGroup, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a11c71ee5d491e3cfb530a3bbcea18f502144ce1fc8489beabb281fa8b64a64a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterfacePublicIps, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c042009b04e2ae9159e75ed966a6e0bcaa31fbd5e8915e4040291afe64207cc5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469ba1c92a3d6294b67c0fd2a3772515a06a00c13e405591edfcb560431d4ff5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6256636471f4d4afb01d9875639d224615f1fcdf7fdf208769a80fa00e320cc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b1a34f4c1268b6852d3ba56c8b3b9df970e6614d4394a696f3512eb03eff304(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2223e329c0d1ab3c5831ea2dbb86c9ade614f242e2e0adabb9dea48429b85fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f88b79efba923cfd5d563bfdcffa4f474efe094aa462111084410b4dc7f3e3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e8e97239d7daa4d26502c98fd7cf038880fb995184ea5aaf8c8c407f7bfc7b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterface]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7713fae4508f705158fdd3057769e0e578b4b22203b46bf6b54cf156c34f55d5(
    *,
    name: builtins.str,
    network_resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8420ac4bed3678d970ca0dcd0beff2c3341db35fd50f9857b3eb181620ee6e5f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__643e592ca5f68c01aee77dcb9a28881ab6da41e1713596d9edae78cee88fca87(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc2b243f085d721adabff92699e2bed88fa389e9891b186ac0bf0cad22ad252d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e881fb17d5f520f84bafbefed2b54f0465cb61c38a535354ab851259306b69d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__627ac419e873d42dc6ea1353d6a8a278a50c6d82344a2bc09581764afbc0ff59(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e23829c8b8cabb3d9f432af7ee1acca698a4e75449e42d25d0eae63b0e40e919(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureNetworkNetworkInterfacePublicIps]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5d376a55ce3ddb960885ef9e1495d13817c7757aec045a9066857df7a1907b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aa98d2567c6af444f687a0b347f920b941950059f0915debc0a0e10532dc8af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__540a2e4d528989f23877c32da4cd96fc66eecb82c0da4013ef113e3daa8d408a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2acc8237755c86a9ac1f280210e6a39f3c387cab72f160b9c490702865ae82(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureNetworkNetworkInterfacePublicIps]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7cad555978c74da5586ea70e9ca010749bc6558bb3926488c0ca9915af8485f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d6816f18da1184576132dddba813064879eb97ee8e37fb8bdfecfb7788c59d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureNetworkNetworkInterface, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbb8467c98e6902306ea2c7a6291c7861dbb154532ddea609bd7b74b9b8ca912(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805d95d8f6f57d4e25f4587a43a09e6c9fb3b78913ea47f808efa2b58a213976(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bdb672d847cf42d0dac8e33cc6fd4ac19ab7961bb162a426058f012d1108581(
    value: typing.Optional[StatefulNodeAzureNetwork],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fee640ec7c5787c7d8b9c626909d9f75e1fad5548922d1ac183d4e423a69f7a(
    *,
    type: builtins.str,
    caching: typing.Optional[builtins.str] = None,
    size_gb: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da91438b28ad4ab72186e93544b0c3a4ca49f506259a3fffa67b15b748dcb715(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b0607bcb9c26868ca8e46a409aab25ae6047d30c6eee13a79219364e8ffdf73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a012b7d27780f63a235ee5a69013a640abd51eb93732f21ed3cfbbcca9745973(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__515693ac7ef3009ed0d89f58e1990cb19af1b1f06d4dc9bf264e62a54ecd664f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a563c79af2490347c1cadc9af4f0abba874afa713457fa273905f13d92569ff(
    value: typing.Optional[StatefulNodeAzureOsDisk],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83b70dac0c17919d04bcdf77512c4aac25ce043eba5c237fa9a02f3d5663f6e7(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f709e1b85bbf12a1ad402445cc7ed6147c576eee02c07465161a8bad1f1a620a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17347fc00c3af747b5a059086934fc9d19618047821dfe1ec39bea978b698a4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fad754712abdb37723fd79abd35f74fef2b9922d3407556beb13b91e8f7ad9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a654868893de010718427948cbff9804d92facdec8a49194f1cfb8dda17bfefa(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265c95d6c781bb0c3547bc2b0fd7d30e464ec279512cbec3da043d636f5f0492(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5b21f22a6252df7077c9bcc9aa7be75b698275197f0df7f2c4c6eb581a54e48(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureProximityPlacementGroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95f55f1f3b0b0337b3f44fefba10ae497a3d5612f72875d9f4e51ac1afe6f0f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db68c0391bb10df20c6a611f5e56081927fe7e2a9eae260e718cb594d6395084(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78629e3d4fdb0e55ca28565d76c252709ad90391ca0cdfe19f7de19405a12d1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2365d7816dcca37205b2dc54f1254fc3749dae093567a543819468e872246393(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureProximityPlacementGroups]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36842cff501a1ee9a0bd55035e3adc7ad9cda1c5a49464b6debfc5b081d24e02(
    *,
    cron_expression: builtins.str,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b5f482394266d66a21549c4a8fae18d53381da42a68c85ada1de7896d2b177c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40cf2b93fc5a11b57fb34b4f57c1bdae0fb1d35e42216104ec46b35f7d5fd7fb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c84bc37a45cdd694dcd39a2e9fc92390e599600d18b91447a469b69719a7462e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e6bbfc68c3b953d80c1ba1bc975f29358836d59121ea5f6db1f0893c9239e2f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d56921a8132e29389de21bcc38ab3bb1d58e6fe23f47ecac4d952e8d40f92ff4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad3f2dc37adba6c425820aa615a32b74762da0e2c85def970f4feb56957b28f2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSchedulingTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89cbad03ffa1a07b4661d2eafc80fc087b878c712f07e2996b2ba070413c2524(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d010d463cb5ee5a6868081d68e91b0f09aa4bbeeb64e900a7fe2b615668f58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83aeba17b46db6b5e7d23d04b585ae89806081f07edb6d7d9c67e17951a9f654(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6db48c9095818dab0a6d85ce7beeb8411a3e443801c8dbccdf762e6cb457c7f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61c63831bf7e1ff57182d86add8f21ec2f078c068a69b2fc84a7d664b107f288(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSchedulingTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b510a9ac511eeb3d97a80f0a8cb1efbf20bdd950f81064869b493cea3630fc(
    *,
    source_vault: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecretSourceVault, typing.Dict[builtins.str, typing.Any]]]],
    vault_certificates: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecretVaultCertificates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83705ef0b02c11e3513491d5032caab6ff59c59bd744bdc17d5aaeb50c4751c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__138cd4fa4d45cbedaff3abf4f8f6e3016e519d8e13df6653d1d1f2c5b2bef614(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4846b0272d8195d006b87656001c2338016cd0cd2d4aec00e4cb7453ee1f3ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__987174ec7da679135ca345f257bf860047a741263989c856e15d987cb52bbd55(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f46ed554c9ba81e7fe5ad3c482966544f5d23ca01efb7e3580307711a0ca007(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a51173756fa50672cfd833891e5128c3c65ed803d41b003c830a946b0ec514f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecret]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b64df1d4a844e7b68ab9fa5ecd9f6395caf102e2b084ca9e1fa4dca94c0d479c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53272d52eaf1cbf20ac11e0e77d10fc6b38df0c5419d5a506362a620e597a2ab(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecretSourceVault, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ddba7647c7f8d0307925670a51538ab9adbc5676310c4fefefe7eb628edf2db(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureSecretVaultCertificates, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1191af5eae82c03bf7c9e091d22b3cc6d9e13bf085560cc32cd69f9e242abfe9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecret]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1de629eda68a141a1a579736deeb15e2390e97e71c60052a505a62f2a1f63fd2(
    *,
    name: builtins.str,
    resource_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2848ef01abad44b36d4e735c912934032358a126b2af43f70482cc32ef805d2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edad9fe817a499a21845012ff284657ad6c9c5974af756cd4cf072221bb85e44(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2900e7434eafef887d258a3cbcb60a781138803c97cb8a3d8bf1ecd51e995cbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca37be26023c31d591171111ae6597f6b50809c5edccb119e305b2a7e6b8099(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e20fe41843d9de3caa22767e899d06d66d009dd2486f936b1c020775c62f8e9f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b3ba86c108f00baef587bd7ae840dadcbbe8eac6afa413989b5f4841c73d2e9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretSourceVault]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b423b412eab25bcf04be3ed5d23c2e2462416eac3d7b88cefc38af7a681acc09(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a563db6f31d73f50fd1991141d3ee2c66892e53b2cededf252408039046426a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7b5dabb7b0f34feafb5a976f1a2efb186e8efd17a4e53bcca968a4110a6f96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f23f81da125ffeaf0ab735666d2ba894ea6fcbc77e6745381cb8b2f2dafcf63(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretSourceVault]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de52ebd04de282ab20e0fffdc079400aa9c58b6af0d66438c3234369ec13e9b(
    *,
    certificate_store: typing.Optional[builtins.str] = None,
    certificate_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92d35a4fb5d1e7f0e9848d958516a8b3a6dcbbed3338c317ab568134780e1eab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdab746ae35b0481ad5a99d212baa41d040852f76833270c69b45ffe998511bd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1d1a285c6df5f16903c5dfacf838a979e06b525727d3ccf155e1183cf68f149(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958596d59eaa4107eedbe847337abc7edcefa201f04dc882533d68e9052bc0f5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44a8e3cdb3e8980bcca8e6422f5818c1c2cad332c5b438010deb6ba2d2910013(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7648622208b700e87b4f8aae7af78dc2bb0ad490073e77e53596ce839814b0fe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSecretVaultCertificates]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f07b0e8fab3b8207fe165222b575cc3e0c355917da96fb2e5a176bba5710f1ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09fd818b2489700526c965e9c1ea785b85cd73419d055aed8f8c86def7776429(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbab3c9a254030676696d1091c8dd2092e8216f9e6c5b62856990ee2eb67c317(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__309a79b20e3c28aef10856436265763ea856c6c42155eed74b3e84d4a45c88ca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSecretVaultCertificates]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4a53e9b559bc0c680e80daee9a70ac98b8edafc65f8d1d272b4bd2e88904b6b(
    *,
    confidential_os_disk_encryption: typing.Optional[builtins.str] = None,
    encryption_at_host: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_boot_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    security_type: typing.Optional[builtins.str] = None,
    vtpm_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__017c780d0d99be8dedd0056e07de1ff6e673605c77d0c42f9348c0039ccc5f1b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d8ad5a0037a28bf2bc5487f1751a48c24be1e4a0844dc2ae6196981acbb84e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5b1a262a89d94d68771a41e1587f67029a77b48d7473ee8383d44e1ff051298(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee24a01e121007e635d812a242e65180f373530228814018c9476d109c04d562(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdabaada8735d4b54fdf67247a681d84ad420eeb325763eb51047188c1c811d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a467ca184d70c640746b0580544bd0ad1b682355a7a7eb9bd1c75482beba1c72(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c2a26ee09de64ba8641d806d8c9182060d1e08a7c9a4243d21bc17977a279e(
    value: typing.Optional[StatefulNodeAzureSecurity],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27723ee6eead5cee2ba134b41c7a06337bebeeaddbd6b1f994e25093323c9c3(
    *,
    timeout: jsii.Number,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a6c8dcb47ea35fe3dbcd04440b5bf4bc56eecc80e867134e75656b95f2d2c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30a8e5c576feae0ee5de6564cff14dad4d2c4e01ea52e32babb3ba5aacd75bcf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29ed13a63dad526faa48bf35b00c7c634c30fc05944f037b1415dc2224860364(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1255d2a81d0800121d9af7bb71b12712649a55330dfaae79dac9d6bdf29b6068(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__719a8ad0358452b15fdacdf65c53cd3c96b0a9e1ac1df55243c3959a2606e95e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2436a5dfdd0e20ca170d1dd4b4d192b2395a7c6a44d14b46ebadb6ea44b6d5a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureSignal]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__455626b780085d087dd1a3ac3a436aad8747c8393c3de290b4068d757922d554(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c89dd66fb8109f87296c6b5bc7d1307a9f04e377482f234f7dc17f695799a64f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef31d8d872a20214cb8924da7ef757e4e34e2dd076c9bda6a1bd9b1f38a86e43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cb946596c1882a51bed1801008b67384e5eb5b365f3e43d26aac0a3834c5da6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureSignal]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d3f7ba12bd229ba7ec573dc76c8970adc9d9bf93241f5dd8b4a45afd750c568(
    *,
    fallback_to_on_demand: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    availability_vs_cost: typing.Optional[jsii.Number] = None,
    capacity_reservation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureStrategyCapacityReservation, typing.Dict[builtins.str, typing.Any]]]]] = None,
    draining_timeout: typing.Optional[jsii.Number] = None,
    od_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    optimization_windows: typing.Optional[typing.Sequence[builtins.str]] = None,
    preferred_life_cycle: typing.Optional[builtins.str] = None,
    revert_to_spot: typing.Optional[typing.Union[StatefulNodeAzureStrategyRevertToSpot, typing.Dict[builtins.str, typing.Any]]] = None,
    vm_admins: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d19be6d2e53694872177674c1aa4a03496973ed1e859a3c86d25319afef2c001(
    *,
    should_utilize: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    utilization_strategy: builtins.str,
    capacity_reservation_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca1f9df1789a66b7e8dbf6eea51337671a942cbede80bd20b7296614f032249c(
    *,
    crg_name: builtins.str,
    crg_resource_group_name: builtins.str,
    crg_should_prioritize: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e97b69854525dfc3146fb32193161826081b4dfe642110ecccda082c1944392a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da5ab4b977e72681cd35045b8d40573d4ec48ea32156df3b9fb47d3d59d83f1a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f10c931ea95bf462b50eaa74f2da3365ac0acb6b696dda49b5b65614aff32b30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10319d688e4641cb23c11bfe195f4e8f82aa82cd095cb554d8dc6d434f6f16f5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba9eb7027ab1f4d42e8039aa2b2bb8ea8b5c4e2aad91bfbb576d7491bc3c188(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0649b5078cb2bc714820795f25172f56f8710e77289dc9b983d083e0421c0723(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f452aa7ec591bd8f21cb7e2a87aecdeb7de39d1328ee88c9d59252674ae71f5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc202b9b97f29189bc02a23fff1c9dd5f6cad96ce308819055eb8a6b98245dba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a19b1cc8721e49e49ebba882afc2a6ace7e560a5398d1aac9d4d1d1aea6311(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b36cc5d93ccefc50c64f3c767661a9bbbee11ab5d68577a88edde7a3dcf6801(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce04508cc93a00c1035aeaa9e025d8a1544d227b7979bfd8d85ef9e7a0bfbd31(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__005dd55b01eef5b117ecbdcea48394ad92cd31cac01426e29da948ede26c8d28(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f56d2d76f8e3a3abfd7c343d758c8af68fcf8e2a35b51c6cce670162c709fcfa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7120905773bccf30f6b301960ab73086750dfe44d275fa091944a83692d6ee35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c294712de67c732ef7acfff781e432302806b547c478a67e95b3031321de65a7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cadac1a76349478f2c0775f6e18f2299de056bd92c586ee295cc55358f7bf71a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__188c08ed3fecdb00f9733eb2e5bbd5efcb097533232c8cb7cd78f848865b63cc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureStrategyCapacityReservation]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4750e662d4c370b918eae739cf8848ee1a6436387d593ce54494214e1b1aaf30(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b37673685a3a904c57a562d676214870b68eb199e75b80c330a995bfd43b470(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureStrategyCapacityReservationCapacityReservationGroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e1b8d31c7f0d406e9d7d911d3ede30c074b4f5dfe24f2ee52c87bc346c8b26d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c54e233f8204c2d592b4642bdd4a18dd221631fa34ead2aed639135d439c5182(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__145ea77f3be7793951e7f9d97b2ab682311f69719518449d55810f039345fdaa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureStrategyCapacityReservation]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07afad8d9aa3894264edf1c77d663fc997c2ad93c24252088d84a4ecce4b0569(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__617f728dda109bc78f4e11cb163c864465f36475fdc6dce1c5380743bced4531(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[StatefulNodeAzureStrategyCapacityReservation, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a6268d997a23c5bcb6b9a4652db58a88d28170b8ed8ed76bf2ac8a4847d03bc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86b165fe28d428a5adf54195aec210d4877d661a354771caf12740e3dfde69c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ede7eeb6ef8f42ce0c9158597efba7ee283e37fba742211381d3089b4781590(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b6efbc132ec15539908e4a50f29461b89e4b5de58238abea9d9df8faf5ef5f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b2ab8e58dfef90b8286fb64f9bc7c9e7884926f94f8c4a6680a270450905f8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea8f004030526433b24c67e95537a9c2e796d8d425be8ea7538da118f653d039(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3d0dbe5ed79c38a4fc1f070471da168e384df3e06eec9b41ef5dec21f054031(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bcbd15be3471ea80f52d91cbbc53879ac241187d8d70e219a624aa831fc9682(
    value: typing.Optional[StatefulNodeAzureStrategy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52384c21f472920f1ed9cdcfa16702f0976a40c612a12b48c87a2046e12ad555(
    *,
    perform_at: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75ba36274800625800e0fe0a784d4f880a6cd6ea56af516794b5b169a20780b4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dae7eb91b0e4a90b302ef0160d7d31951b90c6e9b47a65bf87ad9a4fea506dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85c0cdabf95d42018f83ea656250134a0ee000bf6392af69858daacaf7fb604c(
    value: typing.Optional[StatefulNodeAzureStrategyRevertToSpot],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817bf04892879f4e1dc8f47fd778b39c7ea5978d26f4aee283f9d36ba3db842b(
    *,
    tag_key: builtins.str,
    tag_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b2bc465117817aa1b5559d41a754f48de86dd74cd0184e1f722a46a0405e186(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b1ac48fe6bb838cebfba7288052d15ffdb99c67e5781725d1db36d7f0fab223(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04f15866edbbad68c4fead28d0334cf0a7793667e3a253f7d3b8d71a7e484803(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef70d61b85f469cde5e0d5f3bcc046832207b408dcfb49bee66bbe09c5a7c206(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18a7f927e9fca1d1f09fcff1cd9442a8028007a793ddf7e8072f66425b409c7c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__337dcb5b33ef61d999c4afb8792f2c159539460e676e994bc44ed98d11161b99(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureTag]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6b09ebeb29db90eb0006f06828b0170580e982f3208720e80ae4c22d2188a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b63a3e3f31161c942e3d6299d3455a43a292e660af4e0f377060878360595b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e764e1313e17a8a9d1847d3a31773704f5f9f43130e152b7d1f7e0604d581a90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cac4fc1cc39d2be3f31915817dfc282bb4877197c25eea5989dd831bebf43548(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureTag]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dee53129e1bdbbef6847574354428adc384140d3cc676a9549d4a98f2bbec4b(
    *,
    state: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae502f9a82a8aa9a23021de7cb78cd9a38aa6534bec17bd89f7227542f565474(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d43ee6af8abd4aee5edab1cb007b3587a0d1774cb8add3349cd14809e008777(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8eca29f3e95dbea1fc8c1e09140f3ae291f95a5ac60698a1183ea39fdab2cad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db6c15891befdf40048ca1b743928877cdfe046947470571c9d7b3f32006d570(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bf9df6635e71d6daf182ba297d3ad438caa6330b80b7eb388c575332e788844(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__612ee87262b7406f783f7bdd0695b90306b7149adca3deca45a6fc161c7e164b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[StatefulNodeAzureUpdateState]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e2b8c149d2d85795d6f26ed1df44415201f6b756648eb76e453e30628a5b017(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2fc6a02f52cd1890b27ce6c64456f84d11a56d567be06eb19fe11ab97ad97b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04bb465116f264135bc1aa1d784b63a852df589e0a2f78ffd14e0eec0c559b26(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StatefulNodeAzureUpdateState]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03f6c2a72325cf8b5573a29ba3a7cc64b4d388464306d2c370d196f110ab2f36(
    *,
    od_sizes: typing.Sequence[builtins.str],
    excluded_vm_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    preferred_spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
    spot_size_attributes: typing.Optional[typing.Union[StatefulNodeAzureVmSizesSpotSizeAttributes, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_sizes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d13071e0dc512665c36cbf94097a770b91f414caf7741a8079e551a8bf2cb734(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__954cc863f7bcb7b78e04df425e3e1f4f60a67e332e1b5b82dab7b37338cd4d22(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc52fee69fa22ea4f2ac492df672de0153787d512ec953b72184552cb8a551aa(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de391dfb0b52ce3964763ddab8f80490dda5a46cf438f2ecd1b4b1bff3f1e6ff(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d6fc4a521ada480367cafd929a098e8419fe48b338a45869873bb3b11c0482(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e63700a450f38863691e1502f627dcff1a4e2df7b4fb1354234a8fcb032d63ed(
    value: typing.Optional[StatefulNodeAzureVmSizes],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c269de65ac4f2598c8e951deb0eddbfdef793e0c300caffe60654ba4b6a44909(
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

def _typecheckingstub__b489c0d9c802ea3e4c3d02a98c45c1ae6d6abd6edc6877de7561771e36f68d09(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7f9ccdf416922f2804df55f18e2dcae14ef0920d12a4f1024586db8ffdeee53(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f76bea7f5996abefd271884f783e3f8f6b176523aec8955dd956a3a5afb6d1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d0b01bdb1b4ab357c3f0bf5c1ea4444dd51d2f1edec46b139a41149f7762a38(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79d581a4a3c8c93ad7718497e21a9a6a6508335550e9fb6a3a057b420c3e2dae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__129ed7f720e64086c4894bb5444fe56106685a53d4a92b91d532cef6893e668b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa7d5b9eb471f2189ddaedd499155624484d04327a291787a17623b103d3ab3c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c410247269967988c46ef0e3614bbd888dbdf3d7835e37f69b05b09a806aee9(
    value: typing.Optional[StatefulNodeAzureVmSizesSpotSizeAttributes],
) -> None:
    """Type checking stubs"""
    pass
