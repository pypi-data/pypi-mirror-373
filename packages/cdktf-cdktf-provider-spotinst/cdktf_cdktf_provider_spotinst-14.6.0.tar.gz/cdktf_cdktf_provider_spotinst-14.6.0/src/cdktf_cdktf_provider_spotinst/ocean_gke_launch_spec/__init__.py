r'''
# `spotinst_ocean_gke_launch_spec`

Refer to the Terraform Registry for docs: [`spotinst_ocean_gke_launch_spec`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec).
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


class OceanGkeLaunchSpec(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpec",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec spotinst_ocean_gke_launch_spec}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        ocean_id: builtins.str,
        autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecAutoscaleHeadrooms", typing.Dict[builtins.str, typing.Any]]]]] = None,
        autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        create_options: typing.Optional[typing.Union["OceanGkeLaunchSpecCreateOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        filters: typing.Optional[typing.Union["OceanGkeLaunchSpecFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecMetadata", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        node_pool_name: typing.Optional[builtins.str] = None,
        resource_limits: typing.Optional[typing.Union["OceanGkeLaunchSpecResourceLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
        root_volume_type: typing.Optional[builtins.str] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecSchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_account: typing.Optional[builtins.str] = None,
        shielded_instance_config: typing.Optional[typing.Union["OceanGkeLaunchSpecShieldedInstanceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        source_image: typing.Optional[builtins.str] = None,
        storage: typing.Optional[typing.Union["OceanGkeLaunchSpecStorage", typing.Dict[builtins.str, typing.Any]]] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanGkeLaunchSpecUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec spotinst_ocean_gke_launch_spec} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#ocean_id OceanGkeLaunchSpec#ocean_id}.
        :param autoscale_headrooms: autoscale_headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#autoscale_headrooms OceanGkeLaunchSpec#autoscale_headrooms}
        :param autoscale_headrooms_automatic: autoscale_headrooms_automatic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#autoscale_headrooms_automatic OceanGkeLaunchSpec#autoscale_headrooms_automatic}
        :param create_options: create_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#create_options OceanGkeLaunchSpec#create_options}
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#filters OceanGkeLaunchSpec#filters}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#id OceanGkeLaunchSpec#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#instance_types OceanGkeLaunchSpec#instance_types}.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#labels OceanGkeLaunchSpec#labels}
        :param metadata: metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#metadata OceanGkeLaunchSpec#metadata}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#name OceanGkeLaunchSpec#name}.
        :param network_interfaces: network_interfaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#network_interfaces OceanGkeLaunchSpec#network_interfaces}
        :param node_pool_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#node_pool_name OceanGkeLaunchSpec#node_pool_name}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#resource_limits OceanGkeLaunchSpec#resource_limits}
        :param restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#restrict_scale_down OceanGkeLaunchSpec#restrict_scale_down}.
        :param root_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#root_volume_size OceanGkeLaunchSpec#root_volume_size}.
        :param root_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#root_volume_type OceanGkeLaunchSpec#root_volume_type}.
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#scheduling_task OceanGkeLaunchSpec#scheduling_task}
        :param service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#service_account OceanGkeLaunchSpec#service_account}.
        :param shielded_instance_config: shielded_instance_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#shielded_instance_config OceanGkeLaunchSpec#shielded_instance_config}
        :param source_image: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#source_image OceanGkeLaunchSpec#source_image}.
        :param storage: storage block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#storage OceanGkeLaunchSpec#storage}
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#strategy OceanGkeLaunchSpec#strategy}
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#tags OceanGkeLaunchSpec#tags}.
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#taints OceanGkeLaunchSpec#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#update_policy OceanGkeLaunchSpec#update_policy}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30825e6ae15ea90744aff808b6f8f2c185d17312bfa56d6ceaff3e56a3f4273f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanGkeLaunchSpecConfig(
            ocean_id=ocean_id,
            autoscale_headrooms=autoscale_headrooms,
            autoscale_headrooms_automatic=autoscale_headrooms_automatic,
            create_options=create_options,
            filters=filters,
            id=id,
            instance_types=instance_types,
            labels=labels,
            metadata=metadata,
            name=name,
            network_interfaces=network_interfaces,
            node_pool_name=node_pool_name,
            resource_limits=resource_limits,
            restrict_scale_down=restrict_scale_down,
            root_volume_size=root_volume_size,
            root_volume_type=root_volume_type,
            scheduling_task=scheduling_task,
            service_account=service_account,
            shielded_instance_config=shielded_instance_config,
            source_image=source_image,
            storage=storage,
            strategy=strategy,
            tags=tags,
            taints=taints,
            update_policy=update_policy,
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
        '''Generates CDKTF code for importing a OceanGkeLaunchSpec resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanGkeLaunchSpec to import.
        :param import_from_id: The id of the existing OceanGkeLaunchSpec that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanGkeLaunchSpec to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__699edabb0c3eb9b71bd159757fbb864f741d7ce214d5cc2ef65a0b3d88e522bb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAutoscaleHeadrooms")
    def put_autoscale_headrooms(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecAutoscaleHeadrooms", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56529d2b825b669181c178082460cc3b5d96621960f98de93eccef1fb00b865c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoscaleHeadrooms", [value]))

    @jsii.member(jsii_name="putAutoscaleHeadroomsAutomatic")
    def put_autoscale_headrooms_automatic(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1165c3a7952bf227892ce55608f41e9c12eb0dec4af5621bd2eee4c79348e69c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoscaleHeadroomsAutomatic", [value]))

    @jsii.member(jsii_name="putCreateOptions")
    def put_create_options(
        self,
        *,
        initial_nodes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param initial_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#initial_nodes OceanGkeLaunchSpec#initial_nodes}.
        '''
        value = OceanGkeLaunchSpecCreateOptions(initial_nodes=initial_nodes)

        return typing.cast(None, jsii.invoke(self, "putCreateOptions", [value]))

    @jsii.member(jsii_name="putFilters")
    def put_filters(
        self,
        *,
        exclude_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
        min_memory_gib: typing.Optional[jsii.Number] = None,
        min_vcpu: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param exclude_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#exclude_families OceanGkeLaunchSpec#exclude_families}.
        :param include_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#include_families OceanGkeLaunchSpec#include_families}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_memory_gib OceanGkeLaunchSpec#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_vcpu OceanGkeLaunchSpec#max_vcpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_memory_gib OceanGkeLaunchSpec#min_memory_gib}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_vcpu OceanGkeLaunchSpec#min_vcpu}.
        '''
        value = OceanGkeLaunchSpecFilters(
            exclude_families=exclude_families,
            include_families=include_families,
            max_memory_gib=max_memory_gib,
            max_vcpu=max_vcpu,
            min_memory_gib=min_memory_gib,
            min_vcpu=min_vcpu,
        )

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

    @jsii.member(jsii_name="putLabels")
    def put_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecLabels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1953d948b6fd3713e062aba51e124de97f0ad293fbeeb42b3f6933cf99256e34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLabels", [value]))

    @jsii.member(jsii_name="putMetadata")
    def put_metadata(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecMetadata", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb5ea3bd1e86706aab061169fcb3b6d4d84bc952f8b147588775b4a65cf2f3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMetadata", [value]))

    @jsii.member(jsii_name="putNetworkInterfaces")
    def put_network_interfaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1c62a014f9439fa2a14a60c3462359194d27fe73d6037e83527f028b538e9fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkInterfaces", [value]))

    @jsii.member(jsii_name="putResourceLimits")
    def put_resource_limits(
        self,
        *,
        max_instance_count: typing.Optional[jsii.Number] = None,
        min_instance_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_instance_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_instance_count OceanGkeLaunchSpec#max_instance_count}.
        :param min_instance_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_instance_count OceanGkeLaunchSpec#min_instance_count}.
        '''
        value = OceanGkeLaunchSpecResourceLimits(
            max_instance_count=max_instance_count,
            min_instance_count=min_instance_count,
        )

        return typing.cast(None, jsii.invoke(self, "putResourceLimits", [value]))

    @jsii.member(jsii_name="putSchedulingTask")
    def put_scheduling_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecSchedulingTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c69097c42688aff6d3c4d32f4695b1142c250495b4f52ec871b66d79475497b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSchedulingTask", [value]))

    @jsii.member(jsii_name="putShieldedInstanceConfig")
    def put_shielded_instance_config(
        self,
        *,
        enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enable_integrity_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#enable_integrity_monitoring OceanGkeLaunchSpec#enable_integrity_monitoring}.
        :param enable_secure_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#enable_secure_boot OceanGkeLaunchSpec#enable_secure_boot}.
        '''
        value = OceanGkeLaunchSpecShieldedInstanceConfig(
            enable_integrity_monitoring=enable_integrity_monitoring,
            enable_secure_boot=enable_secure_boot,
        )

        return typing.cast(None, jsii.invoke(self, "putShieldedInstanceConfig", [value]))

    @jsii.member(jsii_name="putStorage")
    def put_storage(
        self,
        *,
        local_ssd_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#local_ssd_count OceanGkeLaunchSpec#local_ssd_count}.
        '''
        value = OceanGkeLaunchSpecStorage(local_ssd_count=local_ssd_count)

        return typing.cast(None, jsii.invoke(self, "putStorage", [value]))

    @jsii.member(jsii_name="putStrategy")
    def put_strategy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecStrategy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__889b458459f8ee5974e4671efc2c5185a4e85b79f5a7abb6a7e130eee89508ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStrategy", [value]))

    @jsii.member(jsii_name="putTaints")
    def put_taints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecTaints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06b88379b593f0b08393302eb8b983ae2a3ed24c760e423eda3138cdbb1e483)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaints", [value]))

    @jsii.member(jsii_name="putUpdatePolicy")
    def put_update_policy(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        roll_config: typing.Optional[typing.Union["OceanGkeLaunchSpecUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#should_roll OceanGkeLaunchSpec#should_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#roll_config OceanGkeLaunchSpec#roll_config}
        '''
        value = OceanGkeLaunchSpecUpdatePolicy(
            should_roll=should_roll, roll_config=roll_config
        )

        return typing.cast(None, jsii.invoke(self, "putUpdatePolicy", [value]))

    @jsii.member(jsii_name="resetAutoscaleHeadrooms")
    def reset_autoscale_headrooms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleHeadrooms", []))

    @jsii.member(jsii_name="resetAutoscaleHeadroomsAutomatic")
    def reset_autoscale_headrooms_automatic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleHeadroomsAutomatic", []))

    @jsii.member(jsii_name="resetCreateOptions")
    def reset_create_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateOptions", []))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceTypes")
    def reset_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypes", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNetworkInterfaces")
    def reset_network_interfaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkInterfaces", []))

    @jsii.member(jsii_name="resetNodePoolName")
    def reset_node_pool_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodePoolName", []))

    @jsii.member(jsii_name="resetResourceLimits")
    def reset_resource_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceLimits", []))

    @jsii.member(jsii_name="resetRestrictScaleDown")
    def reset_restrict_scale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictScaleDown", []))

    @jsii.member(jsii_name="resetRootVolumeSize")
    def reset_root_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeSize", []))

    @jsii.member(jsii_name="resetRootVolumeType")
    def reset_root_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeType", []))

    @jsii.member(jsii_name="resetSchedulingTask")
    def reset_scheduling_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingTask", []))

    @jsii.member(jsii_name="resetServiceAccount")
    def reset_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccount", []))

    @jsii.member(jsii_name="resetShieldedInstanceConfig")
    def reset_shielded_instance_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShieldedInstanceConfig", []))

    @jsii.member(jsii_name="resetSourceImage")
    def reset_source_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceImage", []))

    @jsii.member(jsii_name="resetStorage")
    def reset_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorage", []))

    @jsii.member(jsii_name="resetStrategy")
    def reset_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrategy", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTaints")
    def reset_taints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaints", []))

    @jsii.member(jsii_name="resetUpdatePolicy")
    def reset_update_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatePolicy", []))

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
    @jsii.member(jsii_name="autoscaleHeadrooms")
    def autoscale_headrooms(self) -> "OceanGkeLaunchSpecAutoscaleHeadroomsList":
        return typing.cast("OceanGkeLaunchSpecAutoscaleHeadroomsList", jsii.get(self, "autoscaleHeadrooms"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomsAutomatic")
    def autoscale_headrooms_automatic(
        self,
    ) -> "OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticList":
        return typing.cast("OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticList", jsii.get(self, "autoscaleHeadroomsAutomatic"))

    @builtins.property
    @jsii.member(jsii_name="createOptions")
    def create_options(self) -> "OceanGkeLaunchSpecCreateOptionsOutputReference":
        return typing.cast("OceanGkeLaunchSpecCreateOptionsOutputReference", jsii.get(self, "createOptions"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> "OceanGkeLaunchSpecFiltersOutputReference":
        return typing.cast("OceanGkeLaunchSpecFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> "OceanGkeLaunchSpecLabelsList":
        return typing.cast("OceanGkeLaunchSpecLabelsList", jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> "OceanGkeLaunchSpecMetadataList":
        return typing.cast("OceanGkeLaunchSpecMetadataList", jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfaces")
    def network_interfaces(self) -> "OceanGkeLaunchSpecNetworkInterfacesList":
        return typing.cast("OceanGkeLaunchSpecNetworkInterfacesList", jsii.get(self, "networkInterfaces"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimits")
    def resource_limits(self) -> "OceanGkeLaunchSpecResourceLimitsOutputReference":
        return typing.cast("OceanGkeLaunchSpecResourceLimitsOutputReference", jsii.get(self, "resourceLimits"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTask")
    def scheduling_task(self) -> "OceanGkeLaunchSpecSchedulingTaskList":
        return typing.cast("OceanGkeLaunchSpecSchedulingTaskList", jsii.get(self, "schedulingTask"))

    @builtins.property
    @jsii.member(jsii_name="shieldedInstanceConfig")
    def shielded_instance_config(
        self,
    ) -> "OceanGkeLaunchSpecShieldedInstanceConfigOutputReference":
        return typing.cast("OceanGkeLaunchSpecShieldedInstanceConfigOutputReference", jsii.get(self, "shieldedInstanceConfig"))

    @builtins.property
    @jsii.member(jsii_name="storage")
    def storage(self) -> "OceanGkeLaunchSpecStorageOutputReference":
        return typing.cast("OceanGkeLaunchSpecStorageOutputReference", jsii.get(self, "storage"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "OceanGkeLaunchSpecStrategyList":
        return typing.cast("OceanGkeLaunchSpecStrategyList", jsii.get(self, "strategy"))

    @builtins.property
    @jsii.member(jsii_name="taints")
    def taints(self) -> "OceanGkeLaunchSpecTaintsList":
        return typing.cast("OceanGkeLaunchSpecTaintsList", jsii.get(self, "taints"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> "OceanGkeLaunchSpecUpdatePolicyOutputReference":
        return typing.cast("OceanGkeLaunchSpecUpdatePolicyOutputReference", jsii.get(self, "updatePolicy"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomsAutomaticInput")
    def autoscale_headrooms_automatic_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic"]]], jsii.get(self, "autoscaleHeadroomsAutomaticInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomsInput")
    def autoscale_headrooms_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecAutoscaleHeadrooms"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecAutoscaleHeadrooms"]]], jsii.get(self, "autoscaleHeadroomsInput"))

    @builtins.property
    @jsii.member(jsii_name="createOptionsInput")
    def create_options_input(
        self,
    ) -> typing.Optional["OceanGkeLaunchSpecCreateOptions"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecCreateOptions"], jsii.get(self, "createOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional["OceanGkeLaunchSpecFilters"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecFilters"], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesInput")
    def instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecLabels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecLabels"]]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecMetadata"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecMetadata"]]], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInterfacesInput")
    def network_interfaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfaces"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfaces"]]], jsii.get(self, "networkInterfacesInput"))

    @builtins.property
    @jsii.member(jsii_name="nodePoolNameInput")
    def node_pool_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodePoolNameInput"))

    @builtins.property
    @jsii.member(jsii_name="oceanIdInput")
    def ocean_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oceanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimitsInput")
    def resource_limits_input(
        self,
    ) -> typing.Optional["OceanGkeLaunchSpecResourceLimits"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecResourceLimits"], jsii.get(self, "resourceLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictScaleDownInput")
    def restrict_scale_down_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "restrictScaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="rootVolumeSizeInput")
    def root_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rootVolumeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="rootVolumeTypeInput")
    def root_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTaskInput")
    def scheduling_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTask"]]], jsii.get(self, "schedulingTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountInput")
    def service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="shieldedInstanceConfigInput")
    def shielded_instance_config_input(
        self,
    ) -> typing.Optional["OceanGkeLaunchSpecShieldedInstanceConfig"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecShieldedInstanceConfig"], jsii.get(self, "shieldedInstanceConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceImageInput")
    def source_image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceImageInput"))

    @builtins.property
    @jsii.member(jsii_name="storageInput")
    def storage_input(self) -> typing.Optional["OceanGkeLaunchSpecStorage"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecStorage"], jsii.get(self, "storageInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecStrategy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecStrategy"]]], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="taintsInput")
    def taints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecTaints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecTaints"]]], jsii.get(self, "taintsInput"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicyInput")
    def update_policy_input(self) -> typing.Optional["OceanGkeLaunchSpecUpdatePolicy"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecUpdatePolicy"], jsii.get(self, "updatePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6229d94215748686badbaa3b86ce485ae2775a39a7e32ba415cbfa1cee3987e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypes"))

    @instance_types.setter
    def instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__715fe8ed143c461ea82a44526cd97c29417f6e3099b66697b02320c549f2c7c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65fb6d467c1d99d68b8857040a485fb65c31bbf787eb174bf4e30e3dcf13e880)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodePoolName")
    def node_pool_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodePoolName"))

    @node_pool_name.setter
    def node_pool_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49282cded53597eacc6bcc0f12cbda2012a0b40df6c966a2385d5a442a6f8c03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodePoolName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oceanId")
    def ocean_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oceanId"))

    @ocean_id.setter
    def ocean_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75ff5b84cf94869ef64b9e31394b8b641a32430d4c95d74ddbbb97ed16a55aa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oceanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restrictScaleDown")
    def restrict_scale_down(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "restrictScaleDown"))

    @restrict_scale_down.setter
    def restrict_scale_down(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e85a052e23a372c505fb0694347b027f34a86d9e1274eb7b41715b9fd3531d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictScaleDown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootVolumeSize")
    def root_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rootVolumeSize"))

    @root_volume_size.setter
    def root_volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24c545a0008283aa41a3cd3a93b0b16770d4d266baec61bef7159f2e48e524c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootVolumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootVolumeType")
    def root_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootVolumeType"))

    @root_volume_type.setter
    def root_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c1954df0b316ee86945dfe1d7510e0eb1d2cb9bde8fb365700f9e4feafafebe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccount"))

    @service_account.setter
    def service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad1018837371e6b3c79af0be343a4a1d8ee400b245f9e8bf1e3fb0266864c1be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceImage")
    def source_image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceImage"))

    @source_image.setter
    def source_image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e063bf9312cba0bdcb627d68e23141cb8658f07d9a288062d34007d32468396b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceImage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84445d23df6655c1bd1e5533454818bae533571095ade8b3cf1948aba713166b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecAutoscaleHeadrooms",
    jsii_struct_bases=[],
    name_mapping={
        "num_of_units": "numOfUnits",
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
    },
)
class OceanGkeLaunchSpecAutoscaleHeadrooms:
    def __init__(
        self,
        *,
        num_of_units: jsii.Number,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#num_of_units OceanGkeLaunchSpec#num_of_units}.
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#cpu_per_unit OceanGkeLaunchSpec#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#gpu_per_unit OceanGkeLaunchSpec#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#memory_per_unit OceanGkeLaunchSpec#memory_per_unit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a907b1a20743fb8437bdfc9eee2b3a8b63374e331a2859d36d4ac2a3c7af770f)
            check_type(argname="argument num_of_units", value=num_of_units, expected_type=type_hints["num_of_units"])
            check_type(argname="argument cpu_per_unit", value=cpu_per_unit, expected_type=type_hints["cpu_per_unit"])
            check_type(argname="argument gpu_per_unit", value=gpu_per_unit, expected_type=type_hints["gpu_per_unit"])
            check_type(argname="argument memory_per_unit", value=memory_per_unit, expected_type=type_hints["memory_per_unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "num_of_units": num_of_units,
        }
        if cpu_per_unit is not None:
            self._values["cpu_per_unit"] = cpu_per_unit
        if gpu_per_unit is not None:
            self._values["gpu_per_unit"] = gpu_per_unit
        if memory_per_unit is not None:
            self._values["memory_per_unit"] = memory_per_unit

    @builtins.property
    def num_of_units(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#num_of_units OceanGkeLaunchSpec#num_of_units}.'''
        result = self._values.get("num_of_units")
        assert result is not None, "Required property 'num_of_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#cpu_per_unit OceanGkeLaunchSpec#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#gpu_per_unit OceanGkeLaunchSpec#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#memory_per_unit OceanGkeLaunchSpec#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecAutoscaleHeadrooms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic",
    jsii_struct_bases=[],
    name_mapping={"auto_headroom_percentage": "autoHeadroomPercentage"},
)
class OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic:
    def __init__(
        self,
        *,
        auto_headroom_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param auto_headroom_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#auto_headroom_percentage OceanGkeLaunchSpec#auto_headroom_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9124225df8189071f80771fd2e67094e29541dca1b9fa2e7fba06b8b478aad8d)
            check_type(argname="argument auto_headroom_percentage", value=auto_headroom_percentage, expected_type=type_hints["auto_headroom_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_headroom_percentage is not None:
            self._values["auto_headroom_percentage"] = auto_headroom_percentage

    @builtins.property
    def auto_headroom_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#auto_headroom_percentage OceanGkeLaunchSpec#auto_headroom_percentage}.'''
        result = self._values.get("auto_headroom_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c0c4a31a01a4310fc72582e29ef8876faa652b3aa0b69ee6c61d7a164dacd75)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79954aedf091de9efb94768c1353201c1f1c850e48b89f65c79863aeefed6835)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c33b11777cb7c3cab9577c72ed7fbb6c3e1f9cc2c108b2676a11a6e0724ebad6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2137f486e3ad46e1b50657b5ef65b8122c5cff013aa0c3c0495f5e39abb1d0f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf17f60a493b49f8528343d32b325661af0ff7a622c0325f5dd57569b200bcde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e433a1434e4c4f999073492b53f7aff7a92c223bde6a69f732fd5bfeda2cfaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb2e5e5e5a993fd9de8ab5888672fb0a95789d13c98e45874f8578d6250a36ad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAutoHeadroomPercentage")
    def reset_auto_headroom_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHeadroomPercentage", []))

    @builtins.property
    @jsii.member(jsii_name="autoHeadroomPercentageInput")
    def auto_headroom_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoHeadroomPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="autoHeadroomPercentage")
    def auto_headroom_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoHeadroomPercentage"))

    @auto_headroom_percentage.setter
    def auto_headroom_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1624d75211a28f69b572be141d20b8b371adda274f04bddf0b554e8c4cfe470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoHeadroomPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8211734abb5f1088cc72fdcead8411c94d263c5321b0c32e654eb3934d080a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecAutoscaleHeadroomsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecAutoscaleHeadroomsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4a8127ae9a58ae32e41b641cae857548e9832fcec32032f52096780286afd55)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecAutoscaleHeadroomsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__462a6a049b85ad55ab32c1208c08e0533f213755c09382b4c9f89164264e3c38)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecAutoscaleHeadroomsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1922bcec59f5059223f5d56cf18946f19925bf43b19a0d42144eee4c2a269748)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4b78521d3d8694ec1587e5ce01be33079befa53172a80751b3d12bb21d633098)
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
            type_hints = typing.get_type_hints(_typecheckingstub__67544552d9f187a398ed5fb37595cf3cb407324f6765d516662fd0d41efbea25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadrooms]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadrooms]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadrooms]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d63745a6dc3d3511dc76436469f5bf60e2a1016c89b79ca84eeb3658499d78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecAutoscaleHeadroomsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecAutoscaleHeadroomsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffd6734b0f0bda6ca3d9452d0ad3c339b29174ce5a620c365436f7934b6090b1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d468da34e75707aa206493c0b947ac8ab75573a2dcbbb7463543c23309931be4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad1289d3316360745838d7fa357624bb74d9c460d830ea096f23b4d04a56e49d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__106d28369e7fa6137e51c5486d0dcb36055272fbc8e36240b1503b906bcd9c87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34437d2c752b8e8ace544d340f42224a3d5aaf76919eba588627d836cbfb8deb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadrooms]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadrooms]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadrooms]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2235d5f03e801e9fd618d21f5c2b445c80ab42723a53c30c72277b93c859948c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "ocean_id": "oceanId",
        "autoscale_headrooms": "autoscaleHeadrooms",
        "autoscale_headrooms_automatic": "autoscaleHeadroomsAutomatic",
        "create_options": "createOptions",
        "filters": "filters",
        "id": "id",
        "instance_types": "instanceTypes",
        "labels": "labels",
        "metadata": "metadata",
        "name": "name",
        "network_interfaces": "networkInterfaces",
        "node_pool_name": "nodePoolName",
        "resource_limits": "resourceLimits",
        "restrict_scale_down": "restrictScaleDown",
        "root_volume_size": "rootVolumeSize",
        "root_volume_type": "rootVolumeType",
        "scheduling_task": "schedulingTask",
        "service_account": "serviceAccount",
        "shielded_instance_config": "shieldedInstanceConfig",
        "source_image": "sourceImage",
        "storage": "storage",
        "strategy": "strategy",
        "tags": "tags",
        "taints": "taints",
        "update_policy": "updatePolicy",
    },
)
class OceanGkeLaunchSpecConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        ocean_id: builtins.str,
        autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
        autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]]] = None,
        create_options: typing.Optional[typing.Union["OceanGkeLaunchSpecCreateOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        filters: typing.Optional[typing.Union["OceanGkeLaunchSpecFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecMetadata", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecNetworkInterfaces", typing.Dict[builtins.str, typing.Any]]]]] = None,
        node_pool_name: typing.Optional[builtins.str] = None,
        resource_limits: typing.Optional[typing.Union["OceanGkeLaunchSpecResourceLimits", typing.Dict[builtins.str, typing.Any]]] = None,
        restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
        root_volume_type: typing.Optional[builtins.str] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecSchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        service_account: typing.Optional[builtins.str] = None,
        shielded_instance_config: typing.Optional[typing.Union["OceanGkeLaunchSpecShieldedInstanceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        source_image: typing.Optional[builtins.str] = None,
        storage: typing.Optional[typing.Union["OceanGkeLaunchSpecStorage", typing.Dict[builtins.str, typing.Any]]] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanGkeLaunchSpecUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#ocean_id OceanGkeLaunchSpec#ocean_id}.
        :param autoscale_headrooms: autoscale_headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#autoscale_headrooms OceanGkeLaunchSpec#autoscale_headrooms}
        :param autoscale_headrooms_automatic: autoscale_headrooms_automatic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#autoscale_headrooms_automatic OceanGkeLaunchSpec#autoscale_headrooms_automatic}
        :param create_options: create_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#create_options OceanGkeLaunchSpec#create_options}
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#filters OceanGkeLaunchSpec#filters}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#id OceanGkeLaunchSpec#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#instance_types OceanGkeLaunchSpec#instance_types}.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#labels OceanGkeLaunchSpec#labels}
        :param metadata: metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#metadata OceanGkeLaunchSpec#metadata}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#name OceanGkeLaunchSpec#name}.
        :param network_interfaces: network_interfaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#network_interfaces OceanGkeLaunchSpec#network_interfaces}
        :param node_pool_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#node_pool_name OceanGkeLaunchSpec#node_pool_name}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#resource_limits OceanGkeLaunchSpec#resource_limits}
        :param restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#restrict_scale_down OceanGkeLaunchSpec#restrict_scale_down}.
        :param root_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#root_volume_size OceanGkeLaunchSpec#root_volume_size}.
        :param root_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#root_volume_type OceanGkeLaunchSpec#root_volume_type}.
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#scheduling_task OceanGkeLaunchSpec#scheduling_task}
        :param service_account: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#service_account OceanGkeLaunchSpec#service_account}.
        :param shielded_instance_config: shielded_instance_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#shielded_instance_config OceanGkeLaunchSpec#shielded_instance_config}
        :param source_image: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#source_image OceanGkeLaunchSpec#source_image}.
        :param storage: storage block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#storage OceanGkeLaunchSpec#storage}
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#strategy OceanGkeLaunchSpec#strategy}
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#tags OceanGkeLaunchSpec#tags}.
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#taints OceanGkeLaunchSpec#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#update_policy OceanGkeLaunchSpec#update_policy}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(create_options, dict):
            create_options = OceanGkeLaunchSpecCreateOptions(**create_options)
        if isinstance(filters, dict):
            filters = OceanGkeLaunchSpecFilters(**filters)
        if isinstance(resource_limits, dict):
            resource_limits = OceanGkeLaunchSpecResourceLimits(**resource_limits)
        if isinstance(shielded_instance_config, dict):
            shielded_instance_config = OceanGkeLaunchSpecShieldedInstanceConfig(**shielded_instance_config)
        if isinstance(storage, dict):
            storage = OceanGkeLaunchSpecStorage(**storage)
        if isinstance(update_policy, dict):
            update_policy = OceanGkeLaunchSpecUpdatePolicy(**update_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3890801980f67ec0388e8fc9e258a3da5d1a8f9313f3b4d0f6c0e256e7b1b40)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument ocean_id", value=ocean_id, expected_type=type_hints["ocean_id"])
            check_type(argname="argument autoscale_headrooms", value=autoscale_headrooms, expected_type=type_hints["autoscale_headrooms"])
            check_type(argname="argument autoscale_headrooms_automatic", value=autoscale_headrooms_automatic, expected_type=type_hints["autoscale_headrooms_automatic"])
            check_type(argname="argument create_options", value=create_options, expected_type=type_hints["create_options"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument network_interfaces", value=network_interfaces, expected_type=type_hints["network_interfaces"])
            check_type(argname="argument node_pool_name", value=node_pool_name, expected_type=type_hints["node_pool_name"])
            check_type(argname="argument resource_limits", value=resource_limits, expected_type=type_hints["resource_limits"])
            check_type(argname="argument restrict_scale_down", value=restrict_scale_down, expected_type=type_hints["restrict_scale_down"])
            check_type(argname="argument root_volume_size", value=root_volume_size, expected_type=type_hints["root_volume_size"])
            check_type(argname="argument root_volume_type", value=root_volume_type, expected_type=type_hints["root_volume_type"])
            check_type(argname="argument scheduling_task", value=scheduling_task, expected_type=type_hints["scheduling_task"])
            check_type(argname="argument service_account", value=service_account, expected_type=type_hints["service_account"])
            check_type(argname="argument shielded_instance_config", value=shielded_instance_config, expected_type=type_hints["shielded_instance_config"])
            check_type(argname="argument source_image", value=source_image, expected_type=type_hints["source_image"])
            check_type(argname="argument storage", value=storage, expected_type=type_hints["storage"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument taints", value=taints, expected_type=type_hints["taints"])
            check_type(argname="argument update_policy", value=update_policy, expected_type=type_hints["update_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if autoscale_headrooms is not None:
            self._values["autoscale_headrooms"] = autoscale_headrooms
        if autoscale_headrooms_automatic is not None:
            self._values["autoscale_headrooms_automatic"] = autoscale_headrooms_automatic
        if create_options is not None:
            self._values["create_options"] = create_options
        if filters is not None:
            self._values["filters"] = filters
        if id is not None:
            self._values["id"] = id
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if labels is not None:
            self._values["labels"] = labels
        if metadata is not None:
            self._values["metadata"] = metadata
        if name is not None:
            self._values["name"] = name
        if network_interfaces is not None:
            self._values["network_interfaces"] = network_interfaces
        if node_pool_name is not None:
            self._values["node_pool_name"] = node_pool_name
        if resource_limits is not None:
            self._values["resource_limits"] = resource_limits
        if restrict_scale_down is not None:
            self._values["restrict_scale_down"] = restrict_scale_down
        if root_volume_size is not None:
            self._values["root_volume_size"] = root_volume_size
        if root_volume_type is not None:
            self._values["root_volume_type"] = root_volume_type
        if scheduling_task is not None:
            self._values["scheduling_task"] = scheduling_task
        if service_account is not None:
            self._values["service_account"] = service_account
        if shielded_instance_config is not None:
            self._values["shielded_instance_config"] = shielded_instance_config
        if source_image is not None:
            self._values["source_image"] = source_image
        if storage is not None:
            self._values["storage"] = storage
        if strategy is not None:
            self._values["strategy"] = strategy
        if tags is not None:
            self._values["tags"] = tags
        if taints is not None:
            self._values["taints"] = taints
        if update_policy is not None:
            self._values["update_policy"] = update_policy

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
    def ocean_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#ocean_id OceanGkeLaunchSpec#ocean_id}.'''
        result = self._values.get("ocean_id")
        assert result is not None, "Required property 'ocean_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autoscale_headrooms(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadrooms]]]:
        '''autoscale_headrooms block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#autoscale_headrooms OceanGkeLaunchSpec#autoscale_headrooms}
        '''
        result = self._values.get("autoscale_headrooms")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadrooms]]], result)

    @builtins.property
    def autoscale_headrooms_automatic(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]]:
        '''autoscale_headrooms_automatic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#autoscale_headrooms_automatic OceanGkeLaunchSpec#autoscale_headrooms_automatic}
        '''
        result = self._values.get("autoscale_headrooms_automatic")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]], result)

    @builtins.property
    def create_options(self) -> typing.Optional["OceanGkeLaunchSpecCreateOptions"]:
        '''create_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#create_options OceanGkeLaunchSpec#create_options}
        '''
        result = self._values.get("create_options")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecCreateOptions"], result)

    @builtins.property
    def filters(self) -> typing.Optional["OceanGkeLaunchSpecFilters"]:
        '''filters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#filters OceanGkeLaunchSpec#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecFilters"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#id OceanGkeLaunchSpec#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#instance_types OceanGkeLaunchSpec#instance_types}.'''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecLabels"]]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#labels OceanGkeLaunchSpec#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecLabels"]]], result)

    @builtins.property
    def metadata(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecMetadata"]]]:
        '''metadata block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#metadata OceanGkeLaunchSpec#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecMetadata"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#name OceanGkeLaunchSpec#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_interfaces(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfaces"]]]:
        '''network_interfaces block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#network_interfaces OceanGkeLaunchSpec#network_interfaces}
        '''
        result = self._values.get("network_interfaces")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfaces"]]], result)

    @builtins.property
    def node_pool_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#node_pool_name OceanGkeLaunchSpec#node_pool_name}.'''
        result = self._values.get("node_pool_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_limits(self) -> typing.Optional["OceanGkeLaunchSpecResourceLimits"]:
        '''resource_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#resource_limits OceanGkeLaunchSpec#resource_limits}
        '''
        result = self._values.get("resource_limits")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecResourceLimits"], result)

    @builtins.property
    def restrict_scale_down(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#restrict_scale_down OceanGkeLaunchSpec#restrict_scale_down}.'''
        result = self._values.get("restrict_scale_down")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def root_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#root_volume_size OceanGkeLaunchSpec#root_volume_size}.'''
        result = self._values.get("root_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def root_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#root_volume_type OceanGkeLaunchSpec#root_volume_type}.'''
        result = self._values.get("root_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheduling_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTask"]]]:
        '''scheduling_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#scheduling_task OceanGkeLaunchSpec#scheduling_task}
        '''
        result = self._values.get("scheduling_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTask"]]], result)

    @builtins.property
    def service_account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#service_account OceanGkeLaunchSpec#service_account}.'''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shielded_instance_config(
        self,
    ) -> typing.Optional["OceanGkeLaunchSpecShieldedInstanceConfig"]:
        '''shielded_instance_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#shielded_instance_config OceanGkeLaunchSpec#shielded_instance_config}
        '''
        result = self._values.get("shielded_instance_config")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecShieldedInstanceConfig"], result)

    @builtins.property
    def source_image(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#source_image OceanGkeLaunchSpec#source_image}.'''
        result = self._values.get("source_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage(self) -> typing.Optional["OceanGkeLaunchSpecStorage"]:
        '''storage block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#storage OceanGkeLaunchSpec#storage}
        '''
        result = self._values.get("storage")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecStorage"], result)

    @builtins.property
    def strategy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecStrategy"]]]:
        '''strategy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#strategy OceanGkeLaunchSpec#strategy}
        '''
        result = self._values.get("strategy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecStrategy"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#tags OceanGkeLaunchSpec#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def taints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecTaints"]]]:
        '''taints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#taints OceanGkeLaunchSpec#taints}
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecTaints"]]], result)

    @builtins.property
    def update_policy(self) -> typing.Optional["OceanGkeLaunchSpecUpdatePolicy"]:
        '''update_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#update_policy OceanGkeLaunchSpec#update_policy}
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecUpdatePolicy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecCreateOptions",
    jsii_struct_bases=[],
    name_mapping={"initial_nodes": "initialNodes"},
)
class OceanGkeLaunchSpecCreateOptions:
    def __init__(self, *, initial_nodes: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param initial_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#initial_nodes OceanGkeLaunchSpec#initial_nodes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa35cae6eb0f9443489f2be2ac9a94c4a823527e75dc9039e0de7123ffe4f422)
            check_type(argname="argument initial_nodes", value=initial_nodes, expected_type=type_hints["initial_nodes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if initial_nodes is not None:
            self._values["initial_nodes"] = initial_nodes

    @builtins.property
    def initial_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#initial_nodes OceanGkeLaunchSpec#initial_nodes}.'''
        result = self._values.get("initial_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecCreateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecCreateOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecCreateOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3da7ca64b4921ebc7402a554aabb3b5067a3777007cf0c41310b25da51b060e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetInitialNodes")
    def reset_initial_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitialNodes", []))

    @builtins.property
    @jsii.member(jsii_name="initialNodesInput")
    def initial_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "initialNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="initialNodes")
    def initial_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "initialNodes"))

    @initial_nodes.setter
    def initial_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__886e37e4f269bc7c408d3a506226605239234d46eeb33a4b7e3e0b5e05cb20c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initialNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeLaunchSpecCreateOptions]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecCreateOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeLaunchSpecCreateOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__152a72e5d91ce25537adb8bf84056617f7d51286307048f21b796f89c4f59cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecFilters",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_families": "excludeFamilies",
        "include_families": "includeFamilies",
        "max_memory_gib": "maxMemoryGib",
        "max_vcpu": "maxVcpu",
        "min_memory_gib": "minMemoryGib",
        "min_vcpu": "minVcpu",
    },
)
class OceanGkeLaunchSpecFilters:
    def __init__(
        self,
        *,
        exclude_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
        min_memory_gib: typing.Optional[jsii.Number] = None,
        min_vcpu: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param exclude_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#exclude_families OceanGkeLaunchSpec#exclude_families}.
        :param include_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#include_families OceanGkeLaunchSpec#include_families}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_memory_gib OceanGkeLaunchSpec#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_vcpu OceanGkeLaunchSpec#max_vcpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_memory_gib OceanGkeLaunchSpec#min_memory_gib}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_vcpu OceanGkeLaunchSpec#min_vcpu}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cb10295afc1d705432a0b350c95dd35b676624e0f57fc7b457197383749b690)
            check_type(argname="argument exclude_families", value=exclude_families, expected_type=type_hints["exclude_families"])
            check_type(argname="argument include_families", value=include_families, expected_type=type_hints["include_families"])
            check_type(argname="argument max_memory_gib", value=max_memory_gib, expected_type=type_hints["max_memory_gib"])
            check_type(argname="argument max_vcpu", value=max_vcpu, expected_type=type_hints["max_vcpu"])
            check_type(argname="argument min_memory_gib", value=min_memory_gib, expected_type=type_hints["min_memory_gib"])
            check_type(argname="argument min_vcpu", value=min_vcpu, expected_type=type_hints["min_vcpu"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exclude_families is not None:
            self._values["exclude_families"] = exclude_families
        if include_families is not None:
            self._values["include_families"] = include_families
        if max_memory_gib is not None:
            self._values["max_memory_gib"] = max_memory_gib
        if max_vcpu is not None:
            self._values["max_vcpu"] = max_vcpu
        if min_memory_gib is not None:
            self._values["min_memory_gib"] = min_memory_gib
        if min_vcpu is not None:
            self._values["min_vcpu"] = min_vcpu

    @builtins.property
    def exclude_families(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#exclude_families OceanGkeLaunchSpec#exclude_families}.'''
        result = self._values.get("exclude_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_families(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#include_families OceanGkeLaunchSpec#include_families}.'''
        result = self._values.get("include_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_memory_gib OceanGkeLaunchSpec#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_vcpu OceanGkeLaunchSpec#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_memory_gib OceanGkeLaunchSpec#min_memory_gib}.'''
        result = self._values.get("min_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_vcpu OceanGkeLaunchSpec#min_vcpu}.'''
        result = self._values.get("min_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9d1a0224278b1582d5fb93b6c75dfdef49ca5f7b8e466c5c953be1bf6a1894c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExcludeFamilies")
    def reset_exclude_families(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeFamilies", []))

    @jsii.member(jsii_name="resetIncludeFamilies")
    def reset_include_families(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeFamilies", []))

    @jsii.member(jsii_name="resetMaxMemoryGib")
    def reset_max_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMemoryGib", []))

    @jsii.member(jsii_name="resetMaxVcpu")
    def reset_max_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxVcpu", []))

    @jsii.member(jsii_name="resetMinMemoryGib")
    def reset_min_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinMemoryGib", []))

    @jsii.member(jsii_name="resetMinVcpu")
    def reset_min_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinVcpu", []))

    @builtins.property
    @jsii.member(jsii_name="excludeFamiliesInput")
    def exclude_families_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeFamiliesInput"))

    @builtins.property
    @jsii.member(jsii_name="includeFamiliesInput")
    def include_families_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeFamiliesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGibInput")
    def max_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="maxVcpuInput")
    def max_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="minMemoryGibInput")
    def min_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="minVcpuInput")
    def min_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeFamilies")
    def exclude_families(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeFamilies"))

    @exclude_families.setter
    def exclude_families(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1392fd2bd07b7f13c04b6b45a1fbd3787bd3b8c4dba49fb27580c243258e3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeFamilies")
    def include_families(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeFamilies"))

    @include_families.setter
    def include_families(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c1ce83424fb8cb822d25ea7ca575e6778a8ffa853aca1706ca92f4cef4f67ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGib")
    def max_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemoryGib"))

    @max_memory_gib.setter
    def max_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c67b06caeeeac2b3be7165cc7143e51f10bc5ad7560f853e85e23e24b75a8451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1699640e5316dd3f973b844b47ca8573106d76a37c611ae4b8124548e2fdeaff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemoryGib")
    def min_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemoryGib"))

    @min_memory_gib.setter
    def min_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b9b10ae722dfb073d8afd19d843fd23acba97bdd53a1549209b577a95f5c3d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVcpu")
    def min_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpu"))

    @min_vcpu.setter
    def min_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d388fedfd7401e13d13c4e76af9710ab9bc3db352f921a8729680abcf24e8668)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeLaunchSpecFilters]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanGkeLaunchSpecFilters]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cae9ab46df4b7e3899539dab0177bf5128bb5197b30ffadadd7cc222a6258d42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class OceanGkeLaunchSpecLabels:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#key OceanGkeLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#value OceanGkeLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12fd8c471e89448621e3cf62d814497972e64fad4c825a0ae2758a2198088c9f)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#key OceanGkeLaunchSpec#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#value OceanGkeLaunchSpec#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bc7dc8aceb968c83729d6e83fc6218d0eb128cb5bb298810da710878fbcaed5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeLaunchSpecLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__655a0e15335711dddace0828e7c29ebb89b27409dd1322155538346e49db38f0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2107371c113d6108d04b03eff729c15a975963addce479c34cff0c1af9c47fbe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9158fdd70281c02de533a6fadd7649bac6f431f4ba202c1749c052865b049c6f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05db45d89fe76038cc83774488a32572a76cee667d66cbb229480e463453caab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5750c242a93d1c4600acacbf7e79845524c233fec0b2b7a712569e5a7fa5025a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af9dfdd1c3c3a262067ef8fc28a141cfaa8cf84220d69077dab2cbb9fab41b18)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3311228b9c12b478777271a671964a4251d89eb24519beb18963b1ba559b40a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b39ea33826e14980ebd14f0b27287f34678a1b750d85cea922249930924c3455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__586b25df52a2afa917eeb1055116b04d66e4119e81945464d4ffcdcd9f584f77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecMetadata",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class OceanGkeLaunchSpecMetadata:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#key OceanGkeLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#value OceanGkeLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f145632d1df7cd3793062e111beac1a65d4ac448cb23beb5c6413a6cecfca5a6)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#key OceanGkeLaunchSpec#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#value OceanGkeLaunchSpec#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecMetadataList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecMetadataList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__21628cca7c2ecc965787fe7d9f5d28333e598b8c204a100c83b158d1712f5489)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeLaunchSpecMetadataOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e2629776fd4f4ee8e7367fa2deed40c4fb8c3599da2fe071b205dda641b996f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecMetadataOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2506dd85c78a3c7eb9394e1488b39d37950878d2906b451bc2d124e86d8e528)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a65726d9748b1c653525c7a11c62433ff0a3eb38c112bc91f3c1558be481d140)
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
            type_hints = typing.get_type_hints(_typecheckingstub__178e0071c838f9429bbfcaa5bf3f4135aab5099dc99547846e55512f797cb16b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecMetadata]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecMetadata]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecMetadata]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a2eab22b5b050e5989c4143d6f8ebd83e058dda702f6b352716c322a3ac7ceb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecMetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__250c3f22849543784912db024d1f426ec1f3d1e34ea60ef96dfc63836115b4af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e918d08eddc8503eb11848433988d36ee544a76d11a96e9d159d13168fe866dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__935836e89ac6073cbc805947df3860bc079acfadaaeb1414eab97ba4fd31e69f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecMetadata]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecMetadata]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecMetadata]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9a8f1dc5924ccb343ef99419d52dabcdc03a6de0eac8e100345c23fc13f73ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfaces",
    jsii_struct_bases=[],
    name_mapping={
        "network": "network",
        "access_configs": "accessConfigs",
        "alias_ip_ranges": "aliasIpRanges",
        "project_id": "projectId",
    },
)
class OceanGkeLaunchSpecNetworkInterfaces:
    def __init__(
        self,
        *,
        network: builtins.str,
        access_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecNetworkInterfacesAccessConfigs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        alias_ip_ranges: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges", typing.Dict[builtins.str, typing.Any]]]]] = None,
        project_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param network: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#network OceanGkeLaunchSpec#network}.
        :param access_configs: access_configs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#access_configs OceanGkeLaunchSpec#access_configs}
        :param alias_ip_ranges: alias_ip_ranges block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#alias_ip_ranges OceanGkeLaunchSpec#alias_ip_ranges}
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#project_id OceanGkeLaunchSpec#project_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692b6a2d0af155ff91a1dbe715821f43f2fa451c942f44273600afc89fb989b4)
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument access_configs", value=access_configs, expected_type=type_hints["access_configs"])
            check_type(argname="argument alias_ip_ranges", value=alias_ip_ranges, expected_type=type_hints["alias_ip_ranges"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "network": network,
        }
        if access_configs is not None:
            self._values["access_configs"] = access_configs
        if alias_ip_ranges is not None:
            self._values["alias_ip_ranges"] = alias_ip_ranges
        if project_id is not None:
            self._values["project_id"] = project_id

    @builtins.property
    def network(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#network OceanGkeLaunchSpec#network}.'''
        result = self._values.get("network")
        assert result is not None, "Required property 'network' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_configs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfacesAccessConfigs"]]]:
        '''access_configs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#access_configs OceanGkeLaunchSpec#access_configs}
        '''
        result = self._values.get("access_configs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfacesAccessConfigs"]]], result)

    @builtins.property
    def alias_ip_ranges(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges"]]]:
        '''alias_ip_ranges block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#alias_ip_ranges OceanGkeLaunchSpec#alias_ip_ranges}
        '''
        result = self._values.get("alias_ip_ranges")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges"]]], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#project_id OceanGkeLaunchSpec#project_id}.'''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecNetworkInterfaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesAccessConfigs",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "type": "type"},
)
class OceanGkeLaunchSpecNetworkInterfacesAccessConfigs:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#name OceanGkeLaunchSpec#name}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#type OceanGkeLaunchSpec#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ada99c7006b6949133eca2c35e40a9bb4ba8a683c167832058187431b38be94)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#name OceanGkeLaunchSpec#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#type OceanGkeLaunchSpec#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecNetworkInterfacesAccessConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecNetworkInterfacesAccessConfigsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesAccessConfigsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ebdcc0226a2c592b38837c4bd1781cd3ab4bb5b243aa766b8b17f270042c9bc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecNetworkInterfacesAccessConfigsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15d086f7c518606ccb8cf3e6b85545995da39857d4c22369242a7da3264b1649)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecNetworkInterfacesAccessConfigsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d22162d535b4ebdfd48085012c51e99e640af4800b551501efee1b778b447de)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e783c3ea80016ed5ae5d9bf4ea9d71ed93edcd65c166fba119184e2406b77514)
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
            type_hints = typing.get_type_hints(_typecheckingstub__077aa0139928f666d473184a681c24802ca4c6b876570f73fc4bf3948f4d4d85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6209e7af2feb35340e42f6eb8f477804e6022cd9e7c39d494f3074dd5d958408)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecNetworkInterfacesAccessConfigsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesAccessConfigsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2cfc0abe91104ab50c90c98a5e6134d4e486cd1c7824c0b75157ae24a525f946)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2f9aad7d473f755cf4904281e345c3af8e5089e2004ce2ecdd33cc29d2e6d3f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__228ef77046ef9358a636c81660adf720ac1d4abeae6c50d953e983f3b6f44471)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be651e19fd54668a3edc6ca36f53a2f5534fece615fa44829e9efa6a81e38ff7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges",
    jsii_struct_bases=[],
    name_mapping={
        "ip_cidr_range": "ipCidrRange",
        "subnetwork_range_name": "subnetworkRangeName",
    },
)
class OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges:
    def __init__(
        self,
        *,
        ip_cidr_range: builtins.str,
        subnetwork_range_name: builtins.str,
    ) -> None:
        '''
        :param ip_cidr_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#ip_cidr_range OceanGkeLaunchSpec#ip_cidr_range}.
        :param subnetwork_range_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#subnetwork_range_name OceanGkeLaunchSpec#subnetwork_range_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3001f2d257c2ea1111852cb31dd22b5f91aec8885664075e8b297adde27c20)
            check_type(argname="argument ip_cidr_range", value=ip_cidr_range, expected_type=type_hints["ip_cidr_range"])
            check_type(argname="argument subnetwork_range_name", value=subnetwork_range_name, expected_type=type_hints["subnetwork_range_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ip_cidr_range": ip_cidr_range,
            "subnetwork_range_name": subnetwork_range_name,
        }

    @builtins.property
    def ip_cidr_range(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#ip_cidr_range OceanGkeLaunchSpec#ip_cidr_range}.'''
        result = self._values.get("ip_cidr_range")
        assert result is not None, "Required property 'ip_cidr_range' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnetwork_range_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#subnetwork_range_name OceanGkeLaunchSpec#subnetwork_range_name}.'''
        result = self._values.get("subnetwork_range_name")
        assert result is not None, "Required property 'subnetwork_range_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83f689fb5f74a35f613f0b59a290f38452e8f2e4fcdbd6c7ced1a3a6a451ac23)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a7ac566bb23416c4a9c26aa25077f5c12eedb0601cac82fad4dbe7ecf84a100)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfb2d56bc07e64352cc3dcbc51a89c62f91b574cb0128ada815701a55cd0a6a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0254f4c6d4be8af209477db0a1cd03ee8c82a374264b9f3c4bd8443905c6de8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__259d923f97a36f0c09b6ef7ac9b856940804c23037dcfa19223a8723e1543947)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a4c5a1319f32f086fea4d64c10a4a4dca254c623b25138d367fd7ffcdbc1bc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d53df6faee87a6e54ba9b9c599188350158cbd62ab740c989c1cf93f15234976)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed217b9f606ebb410c4d83b91a15f66afebc4864ccf45cd181708a96d386948f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipCidrRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetworkRangeName")
    def subnetwork_range_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetworkRangeName"))

    @subnetwork_range_name.setter
    def subnetwork_range_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66917cc7045701b9a9f5d3dd8f0d873e6d8d6997132df24b7ac29d6def263231)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetworkRangeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1574e4ab82a5c9ccc5ad6654eb173ff2d43bd5718c4b464aa126360e484ab741)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecNetworkInterfacesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ddf2ee2e8f3723b5837295a25fa8b5eed720af0eb0afaecfd36511b3b628754b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecNetworkInterfacesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43a007ffff3a6e9205eca0d6c352f5fbd2c9812056e88c339690a9c9cf31a824)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecNetworkInterfacesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__641d4d62c113bebab5f6b08f1ea8b34e534aa3e168d68adcf9ce1e805e1f2a38)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db3c9ddb2594c2a025142417643f99c5eb210387e543ef0912b82e9414f3eebc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__77099273c5230d462e9ec7019b105b65cc68bdd154884f898b7fab7b7c187d53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c0c7cce68821802a67285540bed4ca0732d4c87e7ddbed4ff03b73e62fecaf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecNetworkInterfacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecNetworkInterfacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b8c564910a5a6d8be47a102a582937ca40a2d7b8ea97a6d4d2ee2a85d11e42c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAccessConfigs")
    def put_access_configs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b0339fe507afcfe8d85bcb2bc148e831784e5c304a505d78ce47d29384764d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAccessConfigs", [value]))

    @jsii.member(jsii_name="putAliasIpRanges")
    def put_alias_ip_ranges(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63e37f5d5ccd0c8ea883497abb877355b3cc703ec30ebb88759ef6671f7e470f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAliasIpRanges", [value]))

    @jsii.member(jsii_name="resetAccessConfigs")
    def reset_access_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessConfigs", []))

    @jsii.member(jsii_name="resetAliasIpRanges")
    def reset_alias_ip_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasIpRanges", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @builtins.property
    @jsii.member(jsii_name="accessConfigs")
    def access_configs(self) -> OceanGkeLaunchSpecNetworkInterfacesAccessConfigsList:
        return typing.cast(OceanGkeLaunchSpecNetworkInterfacesAccessConfigsList, jsii.get(self, "accessConfigs"))

    @builtins.property
    @jsii.member(jsii_name="aliasIpRanges")
    def alias_ip_ranges(self) -> OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesList:
        return typing.cast(OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesList, jsii.get(self, "aliasIpRanges"))

    @builtins.property
    @jsii.member(jsii_name="accessConfigsInput")
    def access_configs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]], jsii.get(self, "accessConfigsInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasIpRangesInput")
    def alias_ip_ranges_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]], jsii.get(self, "aliasIpRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aa1c67192aef06b35c5eb662d60f914011dc02affa02c05e8369038dfa8b851)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eb0cf67d2d6c0ff9ff59de19c62956fab516b796cfc53becf79e943d132cd87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a2e17807c15bdb00908126db30905b5acb2f93a075048d5baeea2b7149a328c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecResourceLimits",
    jsii_struct_bases=[],
    name_mapping={
        "max_instance_count": "maxInstanceCount",
        "min_instance_count": "minInstanceCount",
    },
)
class OceanGkeLaunchSpecResourceLimits:
    def __init__(
        self,
        *,
        max_instance_count: typing.Optional[jsii.Number] = None,
        min_instance_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_instance_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_instance_count OceanGkeLaunchSpec#max_instance_count}.
        :param min_instance_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_instance_count OceanGkeLaunchSpec#min_instance_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2b82eaa7309252990a75fa0cd272f425195506f0640d298680482daacbe6350)
            check_type(argname="argument max_instance_count", value=max_instance_count, expected_type=type_hints["max_instance_count"])
            check_type(argname="argument min_instance_count", value=min_instance_count, expected_type=type_hints["min_instance_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_instance_count is not None:
            self._values["max_instance_count"] = max_instance_count
        if min_instance_count is not None:
            self._values["min_instance_count"] = min_instance_count

    @builtins.property
    def max_instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#max_instance_count OceanGkeLaunchSpec#max_instance_count}.'''
        result = self._values.get("max_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#min_instance_count OceanGkeLaunchSpec#min_instance_count}.'''
        result = self._values.get("min_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecResourceLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecResourceLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecResourceLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a704cf28afa42543c533e5bcdd490dbbc49781ccfa2253d3b5b537c22a40b41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxInstanceCount")
    def reset_max_instance_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxInstanceCount", []))

    @jsii.member(jsii_name="resetMinInstanceCount")
    def reset_min_instance_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinInstanceCount", []))

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCountInput")
    def max_instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxInstanceCountInput"))

    @builtins.property
    @jsii.member(jsii_name="minInstanceCountInput")
    def min_instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minInstanceCountInput"))

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCount")
    def max_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstanceCount"))

    @max_instance_count.setter
    def max_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf1b95fb131f53b32a0223453b6fd19b08d3787586dcf401683b0f184f11a6f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35107fa27cbc6180051e9b202a0d163868c5cc64eb654fad42f88cb7533bff4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeLaunchSpecResourceLimits]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecResourceLimits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeLaunchSpecResourceLimits],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5815fe11d97a5f1817c2c3b1e143ba3be3e999ff0b12a7fdf7768dbc80be96d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecSchedulingTask",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "is_enabled": "isEnabled",
        "task_type": "taskType",
        "task_headroom": "taskHeadroom",
    },
)
class OceanGkeLaunchSpecSchedulingTask:
    def __init__(
        self,
        *,
        cron_expression: builtins.str,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        task_type: builtins.str,
        task_headroom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecSchedulingTaskTaskHeadroom", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#cron_expression OceanGkeLaunchSpec#cron_expression}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#is_enabled OceanGkeLaunchSpec#is_enabled}.
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#task_type OceanGkeLaunchSpec#task_type}.
        :param task_headroom: task_headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#task_headroom OceanGkeLaunchSpec#task_headroom}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25be9816d99eb2233da840f13cf89097b40c60d470b6bdd4c90d394c29e053cc)
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument task_type", value=task_type, expected_type=type_hints["task_type"])
            check_type(argname="argument task_headroom", value=task_headroom, expected_type=type_hints["task_headroom"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron_expression": cron_expression,
            "is_enabled": is_enabled,
            "task_type": task_type,
        }
        if task_headroom is not None:
            self._values["task_headroom"] = task_headroom

    @builtins.property
    def cron_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#cron_expression OceanGkeLaunchSpec#cron_expression}.'''
        result = self._values.get("cron_expression")
        assert result is not None, "Required property 'cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#is_enabled OceanGkeLaunchSpec#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#task_type OceanGkeLaunchSpec#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_headroom(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTaskTaskHeadroom"]]]:
        '''task_headroom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#task_headroom OceanGkeLaunchSpec#task_headroom}
        '''
        result = self._values.get("task_headroom")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTaskTaskHeadroom"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecSchedulingTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecSchedulingTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecSchedulingTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f706e56b88bf25de1c96340933e7a7db13d29cf135acf9ac9a5f547e2ab41478)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecSchedulingTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dce400ee72d2aeaa5a838e8b2bef9316621d6ecd9ddad40181e23f946862617a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecSchedulingTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b04b79e60fd7d23ad7bb04581c0f2e5600713e84b170782053fe530fb797567b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5cf7cd6061fa9f5a9cc9d576561d278a7fa98e4bcfc215fea3cf76279356d1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f31ad9cf0c6c742698702e6e144a782bd8f86a657646916b0ff69d3a73bc2cc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ad05c218f7d26c8814f1351e4c3603886d06664af7de505f2272de5b3c5ed90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecSchedulingTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecSchedulingTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__620287d1f756d7318d4a81b5bd0dbe1b47068e117325158b6e920329ec6a4632)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTaskHeadroom")
    def put_task_headroom(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeLaunchSpecSchedulingTaskTaskHeadroom", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24eea7209cc5062f67f19b67bd2941ab9bedfe503f31ed7e515e518f6a99b65f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaskHeadroom", [value]))

    @jsii.member(jsii_name="resetTaskHeadroom")
    def reset_task_headroom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskHeadroom", []))

    @builtins.property
    @jsii.member(jsii_name="taskHeadroom")
    def task_headroom(self) -> "OceanGkeLaunchSpecSchedulingTaskTaskHeadroomList":
        return typing.cast("OceanGkeLaunchSpecSchedulingTaskTaskHeadroomList", jsii.get(self, "taskHeadroom"))

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
    @jsii.member(jsii_name="taskHeadroomInput")
    def task_headroom_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTaskTaskHeadroom"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeLaunchSpecSchedulingTaskTaskHeadroom"]]], jsii.get(self, "taskHeadroomInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c2c2ea3690f20035b2781e736d1320bcc77ba2329a922bbd9cd9574c462ac9c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__932cfbcaa567969d4415218afcd73a8eb5c3497c9cc1590d0182ee7726dafb0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1cbea37ac31c370687bef1248d1aa0ab194f5eb53a577a8edd4bd61d5a6dcc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c9df0e074e3bad6cd0f4c2509eebc686028858b04e0a326d0904e2f90bb122c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecSchedulingTaskTaskHeadroom",
    jsii_struct_bases=[],
    name_mapping={
        "num_of_units": "numOfUnits",
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
    },
)
class OceanGkeLaunchSpecSchedulingTaskTaskHeadroom:
    def __init__(
        self,
        *,
        num_of_units: jsii.Number,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#num_of_units OceanGkeLaunchSpec#num_of_units}.
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#cpu_per_unit OceanGkeLaunchSpec#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#gpu_per_unit OceanGkeLaunchSpec#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#memory_per_unit OceanGkeLaunchSpec#memory_per_unit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7de3f5b24c2360c2bfa42889e97e49a97d07af633288f4196210ab856125800a)
            check_type(argname="argument num_of_units", value=num_of_units, expected_type=type_hints["num_of_units"])
            check_type(argname="argument cpu_per_unit", value=cpu_per_unit, expected_type=type_hints["cpu_per_unit"])
            check_type(argname="argument gpu_per_unit", value=gpu_per_unit, expected_type=type_hints["gpu_per_unit"])
            check_type(argname="argument memory_per_unit", value=memory_per_unit, expected_type=type_hints["memory_per_unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "num_of_units": num_of_units,
        }
        if cpu_per_unit is not None:
            self._values["cpu_per_unit"] = cpu_per_unit
        if gpu_per_unit is not None:
            self._values["gpu_per_unit"] = gpu_per_unit
        if memory_per_unit is not None:
            self._values["memory_per_unit"] = memory_per_unit

    @builtins.property
    def num_of_units(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#num_of_units OceanGkeLaunchSpec#num_of_units}.'''
        result = self._values.get("num_of_units")
        assert result is not None, "Required property 'num_of_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#cpu_per_unit OceanGkeLaunchSpec#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#gpu_per_unit OceanGkeLaunchSpec#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#memory_per_unit OceanGkeLaunchSpec#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecSchedulingTaskTaskHeadroom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecSchedulingTaskTaskHeadroomList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecSchedulingTaskTaskHeadroomList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b26d32eaa8ecc5e726efacf209f227f0e266f679a8477c718b24dea94ab7964)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeLaunchSpecSchedulingTaskTaskHeadroomOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1ae36e60b09fb47a4be77b993622574bcb1075f1c18f1ea2d77cf0dd7c7af5f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecSchedulingTaskTaskHeadroomOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82ef2de329f3edec8f55386393e37a45d6937ab447442d503599f26da995e610)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d30fd8106b7d8f25b9fcf99bbc17d8d8db5b14857a5acb47fba4cdfe160e0003)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e52d00f074409e9931827a5c6d193addb972f3f939af727fe2bc42fcc5c9ef65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da223fa6deebe6c8a526a94688065611862214dbec88b5b293fd5802774695a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecSchedulingTaskTaskHeadroomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecSchedulingTaskTaskHeadroomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0290f8b0b10d3f44ad024ebe4dcfb3c03cd898e67dfab5c8ccbed79fb37b16a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d76b29a3aadce90876b5d536ebcd1240b79fee0c036e7300768874f51f6161b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74f17709b6057bd29e20959f859d894ee888376b72cc3e290dc9f13ec99f67c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d55eb9155a7f390ab5975add7529c7da82fa2a37be799051d33c200ecad1ab17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c22e03726880741edb667d8c5c0a57f32a44777d882462d7458fcea7c420f71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5618f4c762fcc88569892cc8313adbdf732c640c74cfe620bb737d74139a919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecShieldedInstanceConfig",
    jsii_struct_bases=[],
    name_mapping={
        "enable_integrity_monitoring": "enableIntegrityMonitoring",
        "enable_secure_boot": "enableSecureBoot",
    },
)
class OceanGkeLaunchSpecShieldedInstanceConfig:
    def __init__(
        self,
        *,
        enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enable_integrity_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#enable_integrity_monitoring OceanGkeLaunchSpec#enable_integrity_monitoring}.
        :param enable_secure_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#enable_secure_boot OceanGkeLaunchSpec#enable_secure_boot}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b3612c48f598fded67a22dd6e6539c4e4d9f434aa163e3fb0bf729d6c3fe556)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#enable_integrity_monitoring OceanGkeLaunchSpec#enable_integrity_monitoring}.'''
        result = self._values.get("enable_integrity_monitoring")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_secure_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#enable_secure_boot OceanGkeLaunchSpec#enable_secure_boot}.'''
        result = self._values.get("enable_secure_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecShieldedInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecShieldedInstanceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecShieldedInstanceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f00eb26e429a177475d533eaf15253de1be1cf98b7757454e319c8e3f7d75317)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4af13ec391ba9a1d846de7263108eca0bb54d66fec68a734bc9d7604d60b7961)
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
            type_hints = typing.get_type_hints(_typecheckingstub__daf4e78370f3c8363baa45921084c9300b67bcfd0a887371c6ab121639abb156)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSecureBoot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanGkeLaunchSpecShieldedInstanceConfig]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecShieldedInstanceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeLaunchSpecShieldedInstanceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4ea12c88e842cf8426e41051e4ffc05d586e6d8f5fb4d74a366c5e8c291d41a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecStorage",
    jsii_struct_bases=[],
    name_mapping={"local_ssd_count": "localSsdCount"},
)
class OceanGkeLaunchSpecStorage:
    def __init__(self, *, local_ssd_count: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param local_ssd_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#local_ssd_count OceanGkeLaunchSpec#local_ssd_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5026a1a7a668fc65666e7f1dac33463cd5e5457bc8d1c98f52c2cb34f89fde8a)
            check_type(argname="argument local_ssd_count", value=local_ssd_count, expected_type=type_hints["local_ssd_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if local_ssd_count is not None:
            self._values["local_ssd_count"] = local_ssd_count

    @builtins.property
    def local_ssd_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#local_ssd_count OceanGkeLaunchSpec#local_ssd_count}.'''
        result = self._values.get("local_ssd_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecStorage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecStorageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecStorageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5769756a332782174471eb1d12a8c5890d509006fd2be9dc969ec4474b389007)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetLocalSsdCount")
    def reset_local_ssd_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalSsdCount", []))

    @builtins.property
    @jsii.member(jsii_name="localSsdCountInput")
    def local_ssd_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "localSsdCountInput"))

    @builtins.property
    @jsii.member(jsii_name="localSsdCount")
    def local_ssd_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "localSsdCount"))

    @local_ssd_count.setter
    def local_ssd_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01b9b6c7929283ddcd2fad8d249120b6478b05d1cde3369145199005d6da3050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localSsdCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeLaunchSpecStorage]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecStorage], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanGkeLaunchSpecStorage]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5de1d0750fda685e10ec5f1c7ed71235989f7cdbaed5db33d844e03beff4b1ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecStrategy",
    jsii_struct_bases=[],
    name_mapping={
        "preemptible_percentage": "preemptiblePercentage",
        "scaling_orientation": "scalingOrientation",
    },
)
class OceanGkeLaunchSpecStrategy:
    def __init__(
        self,
        *,
        preemptible_percentage: typing.Optional[jsii.Number] = None,
        scaling_orientation: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param preemptible_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#preemptible_percentage OceanGkeLaunchSpec#preemptible_percentage}.
        :param scaling_orientation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#scaling_orientation OceanGkeLaunchSpec#scaling_orientation}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a47ef06cab52a1f4a09d4e95c5d10d38919f13cf91a8c8f516126d2c2ca51fe)
            check_type(argname="argument preemptible_percentage", value=preemptible_percentage, expected_type=type_hints["preemptible_percentage"])
            check_type(argname="argument scaling_orientation", value=scaling_orientation, expected_type=type_hints["scaling_orientation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if preemptible_percentage is not None:
            self._values["preemptible_percentage"] = preemptible_percentage
        if scaling_orientation is not None:
            self._values["scaling_orientation"] = scaling_orientation

    @builtins.property
    def preemptible_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#preemptible_percentage OceanGkeLaunchSpec#preemptible_percentage}.'''
        result = self._values.get("preemptible_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scaling_orientation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#scaling_orientation OceanGkeLaunchSpec#scaling_orientation}.'''
        result = self._values.get("scaling_orientation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecStrategyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecStrategyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9fb5f783f2e3c3f4d4d71b747e566f509fbdfb0b5f2433cab8ed5a9fcbef27ea)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeLaunchSpecStrategyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a28ee17fccbd055b156648fce1ade892477c2160b4cea3c5ac5b2d771d370c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecStrategyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79e499dc020da70a174f8fa5ee0dea98175730a36098ada18837010d1efd65d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7aa1cf6d418391c9436dd6eb35e37c1d690990fde360ead24dc159709fe8cc46)
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
            type_hints = typing.get_type_hints(_typecheckingstub__39222984dd78244628b9d6ed1c8a10fff402cc161b7751c3d5195ac948076a5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecStrategy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecStrategy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecStrategy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45fafa3be1b50574efb76dd8072443d427ad3b612f9492427e582022ed205ee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__44661c073de23a34289b1e7e6a98ca29fa69550dbb7c5fdff1502278d7155e0f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPreemptiblePercentage")
    def reset_preemptible_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreemptiblePercentage", []))

    @jsii.member(jsii_name="resetScalingOrientation")
    def reset_scaling_orientation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingOrientation", []))

    @builtins.property
    @jsii.member(jsii_name="preemptiblePercentageInput")
    def preemptible_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "preemptiblePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="scalingOrientationInput")
    def scaling_orientation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scalingOrientationInput"))

    @builtins.property
    @jsii.member(jsii_name="preemptiblePercentage")
    def preemptible_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preemptiblePercentage"))

    @preemptible_percentage.setter
    def preemptible_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbe218e00e6aa32e09913d21e50ad392f4a7b7a32bbb7e0143186d452f0eb195)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preemptiblePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scalingOrientation")
    def scaling_orientation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scalingOrientation"))

    @scaling_orientation.setter
    def scaling_orientation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25faa7f2baca5e52ccecf5b68debadf5948d46100a82c03c790da9a3289ec3c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scalingOrientation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecStrategy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecStrategy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__284f67af0bf56f9b4a26dd9503948e54bbb40855db003e8a004e0d06a341118e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecTaints",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class OceanGkeLaunchSpecTaints:
    def __init__(
        self,
        *,
        effect: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param effect: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#effect OceanGkeLaunchSpec#effect}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#key OceanGkeLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#value OceanGkeLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44c927f4a1b0f017a5603fa82a4262deb8e07b952057d43896466f750299cde0)
            check_type(argname="argument effect", value=effect, expected_type=type_hints["effect"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if effect is not None:
            self._values["effect"] = effect
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def effect(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#effect OceanGkeLaunchSpec#effect}.'''
        result = self._values.get("effect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#key OceanGkeLaunchSpec#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#value OceanGkeLaunchSpec#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecTaints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecTaintsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecTaintsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da99841d69f5f35d5b01ac3a25572cdba0ce6ef3967e26da537186c964af2518)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeLaunchSpecTaintsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63fed597b125b64d9734f936ae68903daa7f9f901668eb96d9691b6d63ad9f23)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeLaunchSpecTaintsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__215c91600395183fbae1deeca39cda3dc1b95bc94121f1d9fa3d3294e6fc3ce7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dcd18e14aa5414201522e8697e534b909d24fcc2732b04806ddb440c708237d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f717635d36a76157862c701dd341de7f1f3beec7563e8c894a16950c8f3d333)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecTaints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecTaints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecTaints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__358cc25d9b15a4945f6c4aaa6bb2397171d5cb03b42245953ee054cbde458793)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeLaunchSpecTaintsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecTaintsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91414167d8b846a57a8820181af16477c4410943a4843e9975ff2b2728060acd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEffect")
    def reset_effect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffect", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3a70ce8050bbd3b3909aef0ee8c0ff5d0781ac59136d5f90b309acce5c8d3b30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a642d0f91b0281ee60eb481ecbd81dd32c1668698f66ac9f28af9445d20b3ecf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__788d8f7b5d9136d7026fed54fc3e9f79bea7d92b7ac42dff29ba230ae9238f26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecTaints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecTaints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecTaints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5a2213e42ad34ec4012061397708adfb747e231e30d1c469652fa77abf1e67b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecUpdatePolicy",
    jsii_struct_bases=[],
    name_mapping={"should_roll": "shouldRoll", "roll_config": "rollConfig"},
)
class OceanGkeLaunchSpecUpdatePolicy:
    def __init__(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        roll_config: typing.Optional[typing.Union["OceanGkeLaunchSpecUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#should_roll OceanGkeLaunchSpec#should_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#roll_config OceanGkeLaunchSpec#roll_config}
        '''
        if isinstance(roll_config, dict):
            roll_config = OceanGkeLaunchSpecUpdatePolicyRollConfig(**roll_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf029720113a1aa463df37575cbf2f459ede888a8d11cd329e8604073943f134)
            check_type(argname="argument should_roll", value=should_roll, expected_type=type_hints["should_roll"])
            check_type(argname="argument roll_config", value=roll_config, expected_type=type_hints["roll_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "should_roll": should_roll,
        }
        if roll_config is not None:
            self._values["roll_config"] = roll_config

    @builtins.property
    def should_roll(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#should_roll OceanGkeLaunchSpec#should_roll}.'''
        result = self._values.get("should_roll")
        assert result is not None, "Required property 'should_roll' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def roll_config(
        self,
    ) -> typing.Optional["OceanGkeLaunchSpecUpdatePolicyRollConfig"]:
        '''roll_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#roll_config OceanGkeLaunchSpec#roll_config}
        '''
        result = self._values.get("roll_config")
        return typing.cast(typing.Optional["OceanGkeLaunchSpecUpdatePolicyRollConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecUpdatePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecUpdatePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecUpdatePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__63e77baa588d870871883a4a9e3b97996cd5b34e51910b006fec547cea7929a1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRollConfig")
    def put_roll_config(self, *, batch_size_percentage: jsii.Number) -> None:
        '''
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#batch_size_percentage OceanGkeLaunchSpec#batch_size_percentage}.
        '''
        value = OceanGkeLaunchSpecUpdatePolicyRollConfig(
            batch_size_percentage=batch_size_percentage
        )

        return typing.cast(None, jsii.invoke(self, "putRollConfig", [value]))

    @jsii.member(jsii_name="resetRollConfig")
    def reset_roll_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollConfig", []))

    @builtins.property
    @jsii.member(jsii_name="rollConfig")
    def roll_config(self) -> "OceanGkeLaunchSpecUpdatePolicyRollConfigOutputReference":
        return typing.cast("OceanGkeLaunchSpecUpdatePolicyRollConfigOutputReference", jsii.get(self, "rollConfig"))

    @builtins.property
    @jsii.member(jsii_name="rollConfigInput")
    def roll_config_input(
        self,
    ) -> typing.Optional["OceanGkeLaunchSpecUpdatePolicyRollConfig"]:
        return typing.cast(typing.Optional["OceanGkeLaunchSpecUpdatePolicyRollConfig"], jsii.get(self, "rollConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldRollInput")
    def should_roll_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldRollInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3e6d579f8668a8e095ee4bc92f895083522dbedaad41abfbd56bfafae7adc412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeLaunchSpecUpdatePolicy]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecUpdatePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeLaunchSpecUpdatePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad522300cbcfa2b3d28dccaaacea5aef7a1f693b48795a43d2ce711caaaf05ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecUpdatePolicyRollConfig",
    jsii_struct_bases=[],
    name_mapping={"batch_size_percentage": "batchSizePercentage"},
)
class OceanGkeLaunchSpecUpdatePolicyRollConfig:
    def __init__(self, *, batch_size_percentage: jsii.Number) -> None:
        '''
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#batch_size_percentage OceanGkeLaunchSpec#batch_size_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daa42dd4ef0cd5ed82ded5af0bf9fb4424a44a71e6f24e137f0d1cd03bf139d0)
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "batch_size_percentage": batch_size_percentage,
        }

    @builtins.property
    def batch_size_percentage(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_launch_spec#batch_size_percentage OceanGkeLaunchSpec#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        assert result is not None, "Required property 'batch_size_percentage' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeLaunchSpecUpdatePolicyRollConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeLaunchSpecUpdatePolicyRollConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeLaunchSpec.OceanGkeLaunchSpecUpdatePolicyRollConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a90484f89087d37b62623be2f6e0e003ea84a96fa22c4e54717fde39b3f08ae1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a56095c8bec5c232d6cd6c0f82241dd357c7824f4d4aaaee8e48ecd4cd18c7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanGkeLaunchSpecUpdatePolicyRollConfig]:
        return typing.cast(typing.Optional[OceanGkeLaunchSpecUpdatePolicyRollConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeLaunchSpecUpdatePolicyRollConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be2a4115f9743596d1bf944038a117733e06b09d7c63898b1ab0fcf138914bfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanGkeLaunchSpec",
    "OceanGkeLaunchSpecAutoscaleHeadrooms",
    "OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic",
    "OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticList",
    "OceanGkeLaunchSpecAutoscaleHeadroomsAutomaticOutputReference",
    "OceanGkeLaunchSpecAutoscaleHeadroomsList",
    "OceanGkeLaunchSpecAutoscaleHeadroomsOutputReference",
    "OceanGkeLaunchSpecConfig",
    "OceanGkeLaunchSpecCreateOptions",
    "OceanGkeLaunchSpecCreateOptionsOutputReference",
    "OceanGkeLaunchSpecFilters",
    "OceanGkeLaunchSpecFiltersOutputReference",
    "OceanGkeLaunchSpecLabels",
    "OceanGkeLaunchSpecLabelsList",
    "OceanGkeLaunchSpecLabelsOutputReference",
    "OceanGkeLaunchSpecMetadata",
    "OceanGkeLaunchSpecMetadataList",
    "OceanGkeLaunchSpecMetadataOutputReference",
    "OceanGkeLaunchSpecNetworkInterfaces",
    "OceanGkeLaunchSpecNetworkInterfacesAccessConfigs",
    "OceanGkeLaunchSpecNetworkInterfacesAccessConfigsList",
    "OceanGkeLaunchSpecNetworkInterfacesAccessConfigsOutputReference",
    "OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges",
    "OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesList",
    "OceanGkeLaunchSpecNetworkInterfacesAliasIpRangesOutputReference",
    "OceanGkeLaunchSpecNetworkInterfacesList",
    "OceanGkeLaunchSpecNetworkInterfacesOutputReference",
    "OceanGkeLaunchSpecResourceLimits",
    "OceanGkeLaunchSpecResourceLimitsOutputReference",
    "OceanGkeLaunchSpecSchedulingTask",
    "OceanGkeLaunchSpecSchedulingTaskList",
    "OceanGkeLaunchSpecSchedulingTaskOutputReference",
    "OceanGkeLaunchSpecSchedulingTaskTaskHeadroom",
    "OceanGkeLaunchSpecSchedulingTaskTaskHeadroomList",
    "OceanGkeLaunchSpecSchedulingTaskTaskHeadroomOutputReference",
    "OceanGkeLaunchSpecShieldedInstanceConfig",
    "OceanGkeLaunchSpecShieldedInstanceConfigOutputReference",
    "OceanGkeLaunchSpecStorage",
    "OceanGkeLaunchSpecStorageOutputReference",
    "OceanGkeLaunchSpecStrategy",
    "OceanGkeLaunchSpecStrategyList",
    "OceanGkeLaunchSpecStrategyOutputReference",
    "OceanGkeLaunchSpecTaints",
    "OceanGkeLaunchSpecTaintsList",
    "OceanGkeLaunchSpecTaintsOutputReference",
    "OceanGkeLaunchSpecUpdatePolicy",
    "OceanGkeLaunchSpecUpdatePolicyOutputReference",
    "OceanGkeLaunchSpecUpdatePolicyRollConfig",
    "OceanGkeLaunchSpecUpdatePolicyRollConfigOutputReference",
]

publication.publish()

def _typecheckingstub__30825e6ae15ea90744aff808b6f8f2c185d17312bfa56d6ceaff3e56a3f4273f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    ocean_id: builtins.str,
    autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]]] = None,
    create_options: typing.Optional[typing.Union[OceanGkeLaunchSpecCreateOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    filters: typing.Optional[typing.Union[OceanGkeLaunchSpecFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecMetadata, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    node_pool_name: typing.Optional[builtins.str] = None,
    resource_limits: typing.Optional[typing.Union[OceanGkeLaunchSpecResourceLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
    root_volume_type: typing.Optional[builtins.str] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecSchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_account: typing.Optional[builtins.str] = None,
    shielded_instance_config: typing.Optional[typing.Union[OceanGkeLaunchSpecShieldedInstanceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    source_image: typing.Optional[builtins.str] = None,
    storage: typing.Optional[typing.Union[OceanGkeLaunchSpecStorage, typing.Dict[builtins.str, typing.Any]]] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanGkeLaunchSpecUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__699edabb0c3eb9b71bd159757fbb864f741d7ce214d5cc2ef65a0b3d88e522bb(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56529d2b825b669181c178082460cc3b5d96621960f98de93eccef1fb00b865c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1165c3a7952bf227892ce55608f41e9c12eb0dec4af5621bd2eee4c79348e69c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1953d948b6fd3713e062aba51e124de97f0ad293fbeeb42b3f6933cf99256e34(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb5ea3bd1e86706aab061169fcb3b6d4d84bc952f8b147588775b4a65cf2f3e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecMetadata, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1c62a014f9439fa2a14a60c3462359194d27fe73d6037e83527f028b538e9fc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c69097c42688aff6d3c4d32f4695b1142c250495b4f52ec871b66d79475497b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecSchedulingTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__889b458459f8ee5974e4671efc2c5185a4e85b79f5a7abb6a7e130eee89508ae(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecStrategy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06b88379b593f0b08393302eb8b983ae2a3ed24c760e423eda3138cdbb1e483(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecTaints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6229d94215748686badbaa3b86ce485ae2775a39a7e32ba415cbfa1cee3987e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715fe8ed143c461ea82a44526cd97c29417f6e3099b66697b02320c549f2c7c3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65fb6d467c1d99d68b8857040a485fb65c31bbf787eb174bf4e30e3dcf13e880(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49282cded53597eacc6bcc0f12cbda2012a0b40df6c966a2385d5a442a6f8c03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75ff5b84cf94869ef64b9e31394b8b641a32430d4c95d74ddbbb97ed16a55aa9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e85a052e23a372c505fb0694347b027f34a86d9e1274eb7b41715b9fd3531d8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24c545a0008283aa41a3cd3a93b0b16770d4d266baec61bef7159f2e48e524c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c1954df0b316ee86945dfe1d7510e0eb1d2cb9bde8fb365700f9e4feafafebe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1018837371e6b3c79af0be343a4a1d8ee400b245f9e8bf1e3fb0266864c1be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e063bf9312cba0bdcb627d68e23141cb8658f07d9a288062d34007d32468396b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84445d23df6655c1bd1e5533454818bae533571095ade8b3cf1948aba713166b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a907b1a20743fb8437bdfc9eee2b3a8b63374e331a2859d36d4ac2a3c7af770f(
    *,
    num_of_units: jsii.Number,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9124225df8189071f80771fd2e67094e29541dca1b9fa2e7fba06b8b478aad8d(
    *,
    auto_headroom_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c0c4a31a01a4310fc72582e29ef8876faa652b3aa0b69ee6c61d7a164dacd75(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79954aedf091de9efb94768c1353201c1f1c850e48b89f65c79863aeefed6835(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c33b11777cb7c3cab9577c72ed7fbb6c3e1f9cc2c108b2676a11a6e0724ebad6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2137f486e3ad46e1b50657b5ef65b8122c5cff013aa0c3c0495f5e39abb1d0f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf17f60a493b49f8528343d32b325661af0ff7a622c0325f5dd57569b200bcde(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e433a1434e4c4f999073492b53f7aff7a92c223bde6a69f732fd5bfeda2cfaf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb2e5e5e5a993fd9de8ab5888672fb0a95789d13c98e45874f8578d6250a36ad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1624d75211a28f69b572be141d20b8b371adda274f04bddf0b554e8c4cfe470(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8211734abb5f1088cc72fdcead8411c94d263c5321b0c32e654eb3934d080a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4a8127ae9a58ae32e41b641cae857548e9832fcec32032f52096780286afd55(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__462a6a049b85ad55ab32c1208c08e0533f213755c09382b4c9f89164264e3c38(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1922bcec59f5059223f5d56cf18946f19925bf43b19a0d42144eee4c2a269748(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b78521d3d8694ec1587e5ce01be33079befa53172a80751b3d12bb21d633098(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67544552d9f187a398ed5fb37595cf3cb407324f6765d516662fd0d41efbea25(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d63745a6dc3d3511dc76436469f5bf60e2a1016c89b79ca84eeb3658499d78(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecAutoscaleHeadrooms]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd6734b0f0bda6ca3d9452d0ad3c339b29174ce5a620c365436f7934b6090b1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d468da34e75707aa206493c0b947ac8ab75573a2dcbbb7463543c23309931be4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1289d3316360745838d7fa357624bb74d9c460d830ea096f23b4d04a56e49d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__106d28369e7fa6137e51c5486d0dcb36055272fbc8e36240b1503b906bcd9c87(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34437d2c752b8e8ace544d340f42224a3d5aaf76919eba588627d836cbfb8deb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2235d5f03e801e9fd618d21f5c2b445c80ab42723a53c30c72277b93c859948c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecAutoscaleHeadrooms]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3890801980f67ec0388e8fc9e258a3da5d1a8f9313f3b4d0f6c0e256e7b1b40(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ocean_id: builtins.str,
    autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]]] = None,
    create_options: typing.Optional[typing.Union[OceanGkeLaunchSpecCreateOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    filters: typing.Optional[typing.Union[OceanGkeLaunchSpecFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    metadata: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecMetadata, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    network_interfaces: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfaces, typing.Dict[builtins.str, typing.Any]]]]] = None,
    node_pool_name: typing.Optional[builtins.str] = None,
    resource_limits: typing.Optional[typing.Union[OceanGkeLaunchSpecResourceLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
    root_volume_type: typing.Optional[builtins.str] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecSchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    service_account: typing.Optional[builtins.str] = None,
    shielded_instance_config: typing.Optional[typing.Union[OceanGkeLaunchSpecShieldedInstanceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    source_image: typing.Optional[builtins.str] = None,
    storage: typing.Optional[typing.Union[OceanGkeLaunchSpecStorage, typing.Dict[builtins.str, typing.Any]]] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanGkeLaunchSpecUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa35cae6eb0f9443489f2be2ac9a94c4a823527e75dc9039e0de7123ffe4f422(
    *,
    initial_nodes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3da7ca64b4921ebc7402a554aabb3b5067a3777007cf0c41310b25da51b060e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__886e37e4f269bc7c408d3a506226605239234d46eeb33a4b7e3e0b5e05cb20c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__152a72e5d91ce25537adb8bf84056617f7d51286307048f21b796f89c4f59cbc(
    value: typing.Optional[OceanGkeLaunchSpecCreateOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cb10295afc1d705432a0b350c95dd35b676624e0f57fc7b457197383749b690(
    *,
    exclude_families: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_families: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_memory_gib: typing.Optional[jsii.Number] = None,
    max_vcpu: typing.Optional[jsii.Number] = None,
    min_memory_gib: typing.Optional[jsii.Number] = None,
    min_vcpu: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d1a0224278b1582d5fb93b6c75dfdef49ca5f7b8e466c5c953be1bf6a1894c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1392fd2bd07b7f13c04b6b45a1fbd3787bd3b8c4dba49fb27580c243258e3f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c1ce83424fb8cb822d25ea7ca575e6778a8ffa853aca1706ca92f4cef4f67ed(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c67b06caeeeac2b3be7165cc7143e51f10bc5ad7560f853e85e23e24b75a8451(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1699640e5316dd3f973b844b47ca8573106d76a37c611ae4b8124548e2fdeaff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b9b10ae722dfb073d8afd19d843fd23acba97bdd53a1549209b577a95f5c3d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d388fedfd7401e13d13c4e76af9710ab9bc3db352f921a8729680abcf24e8668(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cae9ab46df4b7e3899539dab0177bf5128bb5197b30ffadadd7cc222a6258d42(
    value: typing.Optional[OceanGkeLaunchSpecFilters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12fd8c471e89448621e3cf62d814497972e64fad4c825a0ae2758a2198088c9f(
    *,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bc7dc8aceb968c83729d6e83fc6218d0eb128cb5bb298810da710878fbcaed5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__655a0e15335711dddace0828e7c29ebb89b27409dd1322155538346e49db38f0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2107371c113d6108d04b03eff729c15a975963addce479c34cff0c1af9c47fbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9158fdd70281c02de533a6fadd7649bac6f431f4ba202c1749c052865b049c6f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05db45d89fe76038cc83774488a32572a76cee667d66cbb229480e463453caab(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5750c242a93d1c4600acacbf7e79845524c233fec0b2b7a712569e5a7fa5025a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9dfdd1c3c3a262067ef8fc28a141cfaa8cf84220d69077dab2cbb9fab41b18(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3311228b9c12b478777271a671964a4251d89eb24519beb18963b1ba559b40a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b39ea33826e14980ebd14f0b27287f34678a1b750d85cea922249930924c3455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__586b25df52a2afa917eeb1055116b04d66e4119e81945464d4ffcdcd9f584f77(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f145632d1df7cd3793062e111beac1a65d4ac448cb23beb5c6413a6cecfca5a6(
    *,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21628cca7c2ecc965787fe7d9f5d28333e598b8c204a100c83b158d1712f5489(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e2629776fd4f4ee8e7367fa2deed40c4fb8c3599da2fe071b205dda641b996f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2506dd85c78a3c7eb9394e1488b39d37950878d2906b451bc2d124e86d8e528(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a65726d9748b1c653525c7a11c62433ff0a3eb38c112bc91f3c1558be481d140(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__178e0071c838f9429bbfcaa5bf3f4135aab5099dc99547846e55512f797cb16b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a2eab22b5b050e5989c4143d6f8ebd83e058dda702f6b352716c322a3ac7ceb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecMetadata]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__250c3f22849543784912db024d1f426ec1f3d1e34ea60ef96dfc63836115b4af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e918d08eddc8503eb11848433988d36ee544a76d11a96e9d159d13168fe866dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__935836e89ac6073cbc805947df3860bc079acfadaaeb1414eab97ba4fd31e69f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9a8f1dc5924ccb343ef99419d52dabcdc03a6de0eac8e100345c23fc13f73ad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecMetadata]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692b6a2d0af155ff91a1dbe715821f43f2fa451c942f44273600afc89fb989b4(
    *,
    network: builtins.str,
    access_configs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    alias_ip_ranges: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ada99c7006b6949133eca2c35e40a9bb4ba8a683c167832058187431b38be94(
    *,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ebdcc0226a2c592b38837c4bd1781cd3ab4bb5b243aa766b8b17f270042c9bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15d086f7c518606ccb8cf3e6b85545995da39857d4c22369242a7da3264b1649(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d22162d535b4ebdfd48085012c51e99e640af4800b551501efee1b778b447de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e783c3ea80016ed5ae5d9bf4ea9d71ed93edcd65c166fba119184e2406b77514(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__077aa0139928f666d473184a681c24802ca4c6b876570f73fc4bf3948f4d4d85(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6209e7af2feb35340e42f6eb8f477804e6022cd9e7c39d494f3074dd5d958408(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cfc0abe91104ab50c90c98a5e6134d4e486cd1c7824c0b75157ae24a525f946(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f9aad7d473f755cf4904281e345c3af8e5089e2004ce2ecdd33cc29d2e6d3f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__228ef77046ef9358a636c81660adf720ac1d4abeae6c50d953e983f3b6f44471(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be651e19fd54668a3edc6ca36f53a2f5534fece615fa44829e9efa6a81e38ff7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAccessConfigs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3001f2d257c2ea1111852cb31dd22b5f91aec8885664075e8b297adde27c20(
    *,
    ip_cidr_range: builtins.str,
    subnetwork_range_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83f689fb5f74a35f613f0b59a290f38452e8f2e4fcdbd6c7ced1a3a6a451ac23(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a7ac566bb23416c4a9c26aa25077f5c12eedb0601cac82fad4dbe7ecf84a100(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfb2d56bc07e64352cc3dcbc51a89c62f91b574cb0128ada815701a55cd0a6a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0254f4c6d4be8af209477db0a1cd03ee8c82a374264b9f3c4bd8443905c6de8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__259d923f97a36f0c09b6ef7ac9b856940804c23037dcfa19223a8723e1543947(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a4c5a1319f32f086fea4d64c10a4a4dca254c623b25138d367fd7ffcdbc1bc5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d53df6faee87a6e54ba9b9c599188350158cbd62ab740c989c1cf93f15234976(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed217b9f606ebb410c4d83b91a15f66afebc4864ccf45cd181708a96d386948f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66917cc7045701b9a9f5d3dd8f0d873e6d8d6997132df24b7ac29d6def263231(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1574e4ab82a5c9ccc5ad6654eb173ff2d43bd5718c4b464aa126360e484ab741(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddf2ee2e8f3723b5837295a25fa8b5eed720af0eb0afaecfd36511b3b628754b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43a007ffff3a6e9205eca0d6c352f5fbd2c9812056e88c339690a9c9cf31a824(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__641d4d62c113bebab5f6b08f1ea8b34e534aa3e168d68adcf9ce1e805e1f2a38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3c9ddb2594c2a025142417643f99c5eb210387e543ef0912b82e9414f3eebc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77099273c5230d462e9ec7019b105b65cc68bdd154884f898b7fab7b7c187d53(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c0c7cce68821802a67285540bed4ca0732d4c87e7ddbed4ff03b73e62fecaf6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecNetworkInterfaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b8c564910a5a6d8be47a102a582937ca40a2d7b8ea97a6d4d2ee2a85d11e42c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b0339fe507afcfe8d85bcb2bc148e831784e5c304a505d78ce47d29384764d1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfacesAccessConfigs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e37f5d5ccd0c8ea883497abb877355b3cc703ec30ebb88759ef6671f7e470f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecNetworkInterfacesAliasIpRanges, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aa1c67192aef06b35c5eb662d60f914011dc02affa02c05e8369038dfa8b851(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eb0cf67d2d6c0ff9ff59de19c62956fab516b796cfc53becf79e943d132cd87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a2e17807c15bdb00908126db30905b5acb2f93a075048d5baeea2b7149a328c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecNetworkInterfaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2b82eaa7309252990a75fa0cd272f425195506f0640d298680482daacbe6350(
    *,
    max_instance_count: typing.Optional[jsii.Number] = None,
    min_instance_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a704cf28afa42543c533e5bcdd490dbbc49781ccfa2253d3b5b537c22a40b41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf1b95fb131f53b32a0223453b6fd19b08d3787586dcf401683b0f184f11a6f3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35107fa27cbc6180051e9b202a0d163868c5cc64eb654fad42f88cb7533bff4f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5815fe11d97a5f1817c2c3b1e143ba3be3e999ff0b12a7fdf7768dbc80be96d(
    value: typing.Optional[OceanGkeLaunchSpecResourceLimits],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25be9816d99eb2233da840f13cf89097b40c60d470b6bdd4c90d394c29e053cc(
    *,
    cron_expression: builtins.str,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    task_type: builtins.str,
    task_headroom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecSchedulingTaskTaskHeadroom, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f706e56b88bf25de1c96340933e7a7db13d29cf135acf9ac9a5f547e2ab41478(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dce400ee72d2aeaa5a838e8b2bef9316621d6ecd9ddad40181e23f946862617a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b04b79e60fd7d23ad7bb04581c0f2e5600713e84b170782053fe530fb797567b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5cf7cd6061fa9f5a9cc9d576561d278a7fa98e4bcfc215fea3cf76279356d1e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f31ad9cf0c6c742698702e6e144a782bd8f86a657646916b0ff69d3a73bc2cc8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ad05c218f7d26c8814f1351e4c3603886d06664af7de505f2272de5b3c5ed90(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__620287d1f756d7318d4a81b5bd0dbe1b47068e117325158b6e920329ec6a4632(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24eea7209cc5062f67f19b67bd2941ab9bedfe503f31ed7e515e518f6a99b65f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeLaunchSpecSchedulingTaskTaskHeadroom, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2c2ea3690f20035b2781e736d1320bcc77ba2329a922bbd9cd9574c462ac9c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__932cfbcaa567969d4415218afcd73a8eb5c3497c9cc1590d0182ee7726dafb0c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1cbea37ac31c370687bef1248d1aa0ab194f5eb53a577a8edd4bd61d5a6dcc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c9df0e074e3bad6cd0f4c2509eebc686028858b04e0a326d0904e2f90bb122c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7de3f5b24c2360c2bfa42889e97e49a97d07af633288f4196210ab856125800a(
    *,
    num_of_units: jsii.Number,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b26d32eaa8ecc5e726efacf209f227f0e266f679a8477c718b24dea94ab7964(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ae36e60b09fb47a4be77b993622574bcb1075f1c18f1ea2d77cf0dd7c7af5f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ef2de329f3edec8f55386393e37a45d6937ab447442d503599f26da995e610(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d30fd8106b7d8f25b9fcf99bbc17d8d8db5b14857a5acb47fba4cdfe160e0003(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e52d00f074409e9931827a5c6d193addb972f3f939af727fe2bc42fcc5c9ef65(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da223fa6deebe6c8a526a94688065611862214dbec88b5b293fd5802774695a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0290f8b0b10d3f44ad024ebe4dcfb3c03cd898e67dfab5c8ccbed79fb37b16a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d76b29a3aadce90876b5d536ebcd1240b79fee0c036e7300768874f51f6161b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74f17709b6057bd29e20959f859d894ee888376b72cc3e290dc9f13ec99f67c9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d55eb9155a7f390ab5975add7529c7da82fa2a37be799051d33c200ecad1ab17(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c22e03726880741edb667d8c5c0a57f32a44777d882462d7458fcea7c420f71(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5618f4c762fcc88569892cc8313adbdf732c640c74cfe620bb737d74139a919(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecSchedulingTaskTaskHeadroom]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b3612c48f598fded67a22dd6e6539c4e4d9f434aa163e3fb0bf729d6c3fe556(
    *,
    enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00eb26e429a177475d533eaf15253de1be1cf98b7757454e319c8e3f7d75317(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af13ec391ba9a1d846de7263108eca0bb54d66fec68a734bc9d7604d60b7961(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daf4e78370f3c8363baa45921084c9300b67bcfd0a887371c6ab121639abb156(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4ea12c88e842cf8426e41051e4ffc05d586e6d8f5fb4d74a366c5e8c291d41a(
    value: typing.Optional[OceanGkeLaunchSpecShieldedInstanceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5026a1a7a668fc65666e7f1dac33463cd5e5457bc8d1c98f52c2cb34f89fde8a(
    *,
    local_ssd_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5769756a332782174471eb1d12a8c5890d509006fd2be9dc969ec4474b389007(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01b9b6c7929283ddcd2fad8d249120b6478b05d1cde3369145199005d6da3050(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5de1d0750fda685e10ec5f1c7ed71235989f7cdbaed5db33d844e03beff4b1ed(
    value: typing.Optional[OceanGkeLaunchSpecStorage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a47ef06cab52a1f4a09d4e95c5d10d38919f13cf91a8c8f516126d2c2ca51fe(
    *,
    preemptible_percentage: typing.Optional[jsii.Number] = None,
    scaling_orientation: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fb5f783f2e3c3f4d4d71b747e566f509fbdfb0b5f2433cab8ed5a9fcbef27ea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a28ee17fccbd055b156648fce1ade892477c2160b4cea3c5ac5b2d771d370c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79e499dc020da70a174f8fa5ee0dea98175730a36098ada18837010d1efd65d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aa1cf6d418391c9436dd6eb35e37c1d690990fde360ead24dc159709fe8cc46(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39222984dd78244628b9d6ed1c8a10fff402cc161b7751c3d5195ac948076a5f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45fafa3be1b50574efb76dd8072443d427ad3b612f9492427e582022ed205ee7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecStrategy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44661c073de23a34289b1e7e6a98ca29fa69550dbb7c5fdff1502278d7155e0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbe218e00e6aa32e09913d21e50ad392f4a7b7a32bbb7e0143186d452f0eb195(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25faa7f2baca5e52ccecf5b68debadf5948d46100a82c03c790da9a3289ec3c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__284f67af0bf56f9b4a26dd9503948e54bbb40855db003e8a004e0d06a341118e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecStrategy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44c927f4a1b0f017a5603fa82a4262deb8e07b952057d43896466f750299cde0(
    *,
    effect: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da99841d69f5f35d5b01ac3a25572cdba0ce6ef3967e26da537186c964af2518(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63fed597b125b64d9734f936ae68903daa7f9f901668eb96d9691b6d63ad9f23(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__215c91600395183fbae1deeca39cda3dc1b95bc94121f1d9fa3d3294e6fc3ce7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd18e14aa5414201522e8697e534b909d24fcc2732b04806ddb440c708237d1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f717635d36a76157862c701dd341de7f1f3beec7563e8c894a16950c8f3d333(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__358cc25d9b15a4945f6c4aaa6bb2397171d5cb03b42245953ee054cbde458793(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeLaunchSpecTaints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91414167d8b846a57a8820181af16477c4410943a4843e9975ff2b2728060acd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a70ce8050bbd3b3909aef0ee8c0ff5d0781ac59136d5f90b309acce5c8d3b30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a642d0f91b0281ee60eb481ecbd81dd32c1668698f66ac9f28af9445d20b3ecf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__788d8f7b5d9136d7026fed54fc3e9f79bea7d92b7ac42dff29ba230ae9238f26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5a2213e42ad34ec4012061397708adfb747e231e30d1c469652fa77abf1e67b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeLaunchSpecTaints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf029720113a1aa463df37575cbf2f459ede888a8d11cd329e8604073943f134(
    *,
    should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    roll_config: typing.Optional[typing.Union[OceanGkeLaunchSpecUpdatePolicyRollConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e77baa588d870871883a4a9e3b97996cd5b34e51910b006fec547cea7929a1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e6d579f8668a8e095ee4bc92f895083522dbedaad41abfbd56bfafae7adc412(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad522300cbcfa2b3d28dccaaacea5aef7a1f693b48795a43d2ce711caaaf05ed(
    value: typing.Optional[OceanGkeLaunchSpecUpdatePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daa42dd4ef0cd5ed82ded5af0bf9fb4424a44a71e6f24e137f0d1cd03bf139d0(
    *,
    batch_size_percentage: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a90484f89087d37b62623be2f6e0e003ea84a96fa22c4e54717fde39b3f08ae1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a56095c8bec5c232d6cd6c0f82241dd357c7824f4d4aaaee8e48ecd4cd18c7e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be2a4115f9743596d1bf944038a117733e06b09d7c63898b1ab0fcf138914bfe(
    value: typing.Optional[OceanGkeLaunchSpecUpdatePolicyRollConfig],
) -> None:
    """Type checking stubs"""
    pass
