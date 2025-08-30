r'''
# `spotinst_ocean_aws_launch_spec`

Refer to the Terraform Registry for docs: [`spotinst_ocean_aws_launch_spec`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec).
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


class OceanAwsLaunchSpec(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpec",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec spotinst_ocean_aws_launch_spec}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        ocean_id: builtins.str,
        associate_public_ip_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale_down: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecAutoscaleDown", typing.Dict[builtins.str, typing.Any]]]]] = None,
        autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecAutoscaleHeadrooms", typing.Dict[builtins.str, typing.Any]]]]] = None,
        autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecBlockDeviceMappings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        create_options: typing.Optional[typing.Union["OceanAwsLaunchSpecCreateOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        delete_options: typing.Optional[typing.Union["OceanAwsLaunchSpecDeleteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        elastic_ip_pool: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecElasticIpPool", typing.Dict[builtins.str, typing.Any]]]]] = None,
        ephemeral_storage: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecEphemeralStorage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        iam_instance_profile: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        images: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecImages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_metadata_options: typing.Optional[typing.Union["OceanAwsLaunchSpecInstanceMetadataOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_store_policy: typing.Optional[typing.Union["OceanAwsLaunchSpecInstanceStorePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        instance_types_filters: typing.Optional[typing.Union["OceanAwsLaunchSpecInstanceTypesFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        preferred_od_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_spot_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        reserved_enis: typing.Optional[jsii.Number] = None,
        resource_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecResourceLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
        scheduling_shutdown_hours: typing.Optional[typing.Union["OceanAwsLaunchSpecSchedulingShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecSchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        startup_taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecStartupTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanAwsLaunchSpecUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        user_data: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec spotinst_ocean_aws_launch_spec} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ocean_id OceanAwsLaunchSpec#ocean_id}.
        :param associate_public_ip_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#associate_public_ip_address OceanAwsLaunchSpec#associate_public_ip_address}.
        :param autoscale_down: autoscale_down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_down OceanAwsLaunchSpec#autoscale_down}
        :param autoscale_headrooms: autoscale_headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_headrooms OceanAwsLaunchSpec#autoscale_headrooms}
        :param autoscale_headrooms_automatic: autoscale_headrooms_automatic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_headrooms_automatic OceanAwsLaunchSpec#autoscale_headrooms_automatic}
        :param block_device_mappings: block_device_mappings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#block_device_mappings OceanAwsLaunchSpec#block_device_mappings}
        :param create_options: create_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#create_options OceanAwsLaunchSpec#create_options}
        :param delete_options: delete_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_options OceanAwsLaunchSpec#delete_options}
        :param elastic_ip_pool: elastic_ip_pool block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#elastic_ip_pool OceanAwsLaunchSpec#elastic_ip_pool}
        :param ephemeral_storage: ephemeral_storage block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ephemeral_storage OceanAwsLaunchSpec#ephemeral_storage}
        :param iam_instance_profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#iam_instance_profile OceanAwsLaunchSpec#iam_instance_profile}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#id OceanAwsLaunchSpec#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#image_id OceanAwsLaunchSpec#image_id}.
        :param images: images block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#images OceanAwsLaunchSpec#images}
        :param instance_metadata_options: instance_metadata_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_metadata_options OceanAwsLaunchSpec#instance_metadata_options}
        :param instance_store_policy: instance_store_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_store_policy OceanAwsLaunchSpec#instance_store_policy}
        :param instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_types OceanAwsLaunchSpec#instance_types}.
        :param instance_types_filters: instance_types_filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_types_filters OceanAwsLaunchSpec#instance_types_filters}
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#labels OceanAwsLaunchSpec#labels}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#name OceanAwsLaunchSpec#name}.
        :param preferred_od_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#preferred_od_types OceanAwsLaunchSpec#preferred_od_types}.
        :param preferred_spot_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#preferred_spot_types OceanAwsLaunchSpec#preferred_spot_types}.
        :param reserved_enis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#reserved_enis OceanAwsLaunchSpec#reserved_enis}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#resource_limits OceanAwsLaunchSpec#resource_limits}
        :param restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#restrict_scale_down OceanAwsLaunchSpec#restrict_scale_down}.
        :param root_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#root_volume_size OceanAwsLaunchSpec#root_volume_size}.
        :param scheduling_shutdown_hours: scheduling_shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#scheduling_shutdown_hours OceanAwsLaunchSpec#scheduling_shutdown_hours}
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#scheduling_task OceanAwsLaunchSpec#scheduling_task}
        :param security_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#security_groups OceanAwsLaunchSpec#security_groups}.
        :param startup_taints: startup_taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#startup_taints OceanAwsLaunchSpec#startup_taints}
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#strategy OceanAwsLaunchSpec#strategy}
        :param subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#subnet_ids OceanAwsLaunchSpec#subnet_ids}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tags OceanAwsLaunchSpec#tags}
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#taints OceanAwsLaunchSpec#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#update_policy OceanAwsLaunchSpec#update_policy}
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#user_data OceanAwsLaunchSpec#user_data}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f32d702f716a2f5dff9548e1a3816b17b946225f283f7101fd3a2a28bce1f23)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanAwsLaunchSpecConfig(
            ocean_id=ocean_id,
            associate_public_ip_address=associate_public_ip_address,
            autoscale_down=autoscale_down,
            autoscale_headrooms=autoscale_headrooms,
            autoscale_headrooms_automatic=autoscale_headrooms_automatic,
            block_device_mappings=block_device_mappings,
            create_options=create_options,
            delete_options=delete_options,
            elastic_ip_pool=elastic_ip_pool,
            ephemeral_storage=ephemeral_storage,
            iam_instance_profile=iam_instance_profile,
            id=id,
            image_id=image_id,
            images=images,
            instance_metadata_options=instance_metadata_options,
            instance_store_policy=instance_store_policy,
            instance_types=instance_types,
            instance_types_filters=instance_types_filters,
            labels=labels,
            name=name,
            preferred_od_types=preferred_od_types,
            preferred_spot_types=preferred_spot_types,
            reserved_enis=reserved_enis,
            resource_limits=resource_limits,
            restrict_scale_down=restrict_scale_down,
            root_volume_size=root_volume_size,
            scheduling_shutdown_hours=scheduling_shutdown_hours,
            scheduling_task=scheduling_task,
            security_groups=security_groups,
            startup_taints=startup_taints,
            strategy=strategy,
            subnet_ids=subnet_ids,
            tags=tags,
            taints=taints,
            update_policy=update_policy,
            user_data=user_data,
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
        '''Generates CDKTF code for importing a OceanAwsLaunchSpec resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanAwsLaunchSpec to import.
        :param import_from_id: The id of the existing OceanAwsLaunchSpec that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanAwsLaunchSpec to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ffb1d01bbf92ea2acb22ba4e50de8ae92fa97ed8a2131322e03e07fb720acc9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAutoscaleDown")
    def put_autoscale_down(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecAutoscaleDown", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c4a9adad79cf8bf8a3aed756fb98fc876d0b439de8d565ce4b2ae91029d09a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoscaleDown", [value]))

    @jsii.member(jsii_name="putAutoscaleHeadrooms")
    def put_autoscale_headrooms(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecAutoscaleHeadrooms", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2eb35f9d318918ef62982e46870a180e6b86952c56fbedc22bd15696e54262f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoscaleHeadrooms", [value]))

    @jsii.member(jsii_name="putAutoscaleHeadroomsAutomatic")
    def put_autoscale_headrooms_automatic(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a321f91d35e6eabe432037291c1923d3ad1bbe56fc7fbc8c7ec6d46d17654707)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoscaleHeadroomsAutomatic", [value]))

    @jsii.member(jsii_name="putBlockDeviceMappings")
    def put_block_device_mappings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecBlockDeviceMappings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56ec253792a01e9bcc397d21ed23fdd3e28c56e321872edb062245802a43d460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBlockDeviceMappings", [value]))

    @jsii.member(jsii_name="putCreateOptions")
    def put_create_options(
        self,
        *,
        initial_nodes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param initial_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#initial_nodes OceanAwsLaunchSpec#initial_nodes}.
        '''
        value = OceanAwsLaunchSpecCreateOptions(initial_nodes=initial_nodes)

        return typing.cast(None, jsii.invoke(self, "putCreateOptions", [value]))

    @jsii.member(jsii_name="putDeleteOptions")
    def put_delete_options(
        self,
        *,
        force_delete: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        delete_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param force_delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#force_delete OceanAwsLaunchSpec#force_delete}.
        :param delete_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_nodes OceanAwsLaunchSpec#delete_nodes}.
        '''
        value = OceanAwsLaunchSpecDeleteOptions(
            force_delete=force_delete, delete_nodes=delete_nodes
        )

        return typing.cast(None, jsii.invoke(self, "putDeleteOptions", [value]))

    @jsii.member(jsii_name="putElasticIpPool")
    def put_elastic_ip_pool(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecElasticIpPool", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__005b836f7f8079d42fd4c8afe58efa9bdcf6b59a6353f436e012d4dc8c358e45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putElasticIpPool", [value]))

    @jsii.member(jsii_name="putEphemeralStorage")
    def put_ephemeral_storage(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecEphemeralStorage", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1268598b29d39f92c52479f978fe32c79c222f8064221d34c1cfbad568bbd921)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEphemeralStorage", [value]))

    @jsii.member(jsii_name="putImages")
    def put_images(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecImages", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ef59d89a96856d7619f9573fe6903cb6c656dce5c68eb9bb445fa8cea6b00ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putImages", [value]))

    @jsii.member(jsii_name="putInstanceMetadataOptions")
    def put_instance_metadata_options(
        self,
        *,
        http_tokens: builtins.str,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param http_tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#http_tokens OceanAwsLaunchSpec#http_tokens}.
        :param http_put_response_hop_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#http_put_response_hop_limit OceanAwsLaunchSpec#http_put_response_hop_limit}.
        '''
        value = OceanAwsLaunchSpecInstanceMetadataOptions(
            http_tokens=http_tokens,
            http_put_response_hop_limit=http_put_response_hop_limit,
        )

        return typing.cast(None, jsii.invoke(self, "putInstanceMetadataOptions", [value]))

    @jsii.member(jsii_name="putInstanceStorePolicy")
    def put_instance_store_policy(
        self,
        *,
        instance_store_policy_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_store_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_store_policy_type OceanAwsLaunchSpec#instance_store_policy_type}.
        '''
        value = OceanAwsLaunchSpecInstanceStorePolicy(
            instance_store_policy_type=instance_store_policy_type
        )

        return typing.cast(None, jsii.invoke(self, "putInstanceStorePolicy", [value]))

    @jsii.member(jsii_name="putInstanceTypesFilters")
    def put_instance_types_filters(
        self,
        *,
        categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        disk_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude_metal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hypervisor: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_ena_supported: typing.Optional[builtins.str] = None,
        max_gpu: typing.Optional[jsii.Number] = None,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_network_performance: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
        min_enis: typing.Optional[jsii.Number] = None,
        min_gpu: typing.Optional[jsii.Number] = None,
        min_memory_gib: typing.Optional[jsii.Number] = None,
        min_network_performance: typing.Optional[jsii.Number] = None,
        min_vcpu: typing.Optional[jsii.Number] = None,
        root_device_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtualization_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param categories: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#categories OceanAwsLaunchSpec#categories}.
        :param disk_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#disk_types OceanAwsLaunchSpec#disk_types}.
        :param exclude_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#exclude_families OceanAwsLaunchSpec#exclude_families}.
        :param exclude_metal: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#exclude_metal OceanAwsLaunchSpec#exclude_metal}.
        :param hypervisor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#hypervisor OceanAwsLaunchSpec#hypervisor}.
        :param include_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#include_families OceanAwsLaunchSpec#include_families}.
        :param is_ena_supported: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_ena_supported OceanAwsLaunchSpec#is_ena_supported}.
        :param max_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_gpu OceanAwsLaunchSpec#max_gpu}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_memory_gib OceanAwsLaunchSpec#max_memory_gib}.
        :param max_network_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_network_performance OceanAwsLaunchSpec#max_network_performance}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_vcpu OceanAwsLaunchSpec#max_vcpu}.
        :param min_enis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_enis OceanAwsLaunchSpec#min_enis}.
        :param min_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_gpu OceanAwsLaunchSpec#min_gpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_memory_gib OceanAwsLaunchSpec#min_memory_gib}.
        :param min_network_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_network_performance OceanAwsLaunchSpec#min_network_performance}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_vcpu OceanAwsLaunchSpec#min_vcpu}.
        :param root_device_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#root_device_types OceanAwsLaunchSpec#root_device_types}.
        :param virtualization_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#virtualization_types OceanAwsLaunchSpec#virtualization_types}.
        '''
        value = OceanAwsLaunchSpecInstanceTypesFilters(
            categories=categories,
            disk_types=disk_types,
            exclude_families=exclude_families,
            exclude_metal=exclude_metal,
            hypervisor=hypervisor,
            include_families=include_families,
            is_ena_supported=is_ena_supported,
            max_gpu=max_gpu,
            max_memory_gib=max_memory_gib,
            max_network_performance=max_network_performance,
            max_vcpu=max_vcpu,
            min_enis=min_enis,
            min_gpu=min_gpu,
            min_memory_gib=min_memory_gib,
            min_network_performance=min_network_performance,
            min_vcpu=min_vcpu,
            root_device_types=root_device_types,
            virtualization_types=virtualization_types,
        )

        return typing.cast(None, jsii.invoke(self, "putInstanceTypesFilters", [value]))

    @jsii.member(jsii_name="putLabels")
    def put_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecLabels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd52c19488371732a8e287f040bf6e7e78c648ccc201d4317ddf639a8a4a3e58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLabels", [value]))

    @jsii.member(jsii_name="putResourceLimits")
    def put_resource_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecResourceLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6fe67483f81ff5c53da9d701848e429ce132407300223ce7c70be7ee4e69bc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResourceLimits", [value]))

    @jsii.member(jsii_name="putSchedulingShutdownHours")
    def put_scheduling_shutdown_hours(
        self,
        *,
        time_windows: typing.Sequence[builtins.str],
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#time_windows OceanAwsLaunchSpec#time_windows}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_enabled OceanAwsLaunchSpec#is_enabled}.
        '''
        value = OceanAwsLaunchSpecSchedulingShutdownHours(
            time_windows=time_windows, is_enabled=is_enabled
        )

        return typing.cast(None, jsii.invoke(self, "putSchedulingShutdownHours", [value]))

    @jsii.member(jsii_name="putSchedulingTask")
    def put_scheduling_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecSchedulingTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a5255d8a7c562990f2a0511eccc8ee4faff8b297c567040edc59fbeb3f8d567)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSchedulingTask", [value]))

    @jsii.member(jsii_name="putStartupTaints")
    def put_startup_taints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecStartupTaints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b549d52142f5386077ea053fe312cb800d9a1c16fb1975b7cb74541ba8faee4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStartupTaints", [value]))

    @jsii.member(jsii_name="putStrategy")
    def put_strategy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecStrategy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba55e44db0b61ebdff3a75a3f0dcd897e564e0ccd8c9813d5910bcb8f822429e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStrategy", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b1034add65eac94422ad211039f4b5772713896227bcab79deea86dd1d0ab7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putTaints")
    def put_taints(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecTaints", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d980b3db4ad0b5a979ba99070063d524eaa6f0be444136c99963ff1e6adc4d72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaints", [value]))

    @jsii.member(jsii_name="putUpdatePolicy")
    def put_update_policy(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        roll_config: typing.Optional[typing.Union["OceanAwsLaunchSpecUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#should_roll OceanAwsLaunchSpec#should_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#roll_config OceanAwsLaunchSpec#roll_config}
        '''
        value = OceanAwsLaunchSpecUpdatePolicy(
            should_roll=should_roll, roll_config=roll_config
        )

        return typing.cast(None, jsii.invoke(self, "putUpdatePolicy", [value]))

    @jsii.member(jsii_name="resetAssociatePublicIpAddress")
    def reset_associate_public_ip_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssociatePublicIpAddress", []))

    @jsii.member(jsii_name="resetAutoscaleDown")
    def reset_autoscale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleDown", []))

    @jsii.member(jsii_name="resetAutoscaleHeadrooms")
    def reset_autoscale_headrooms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleHeadrooms", []))

    @jsii.member(jsii_name="resetAutoscaleHeadroomsAutomatic")
    def reset_autoscale_headrooms_automatic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaleHeadroomsAutomatic", []))

    @jsii.member(jsii_name="resetBlockDeviceMappings")
    def reset_block_device_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockDeviceMappings", []))

    @jsii.member(jsii_name="resetCreateOptions")
    def reset_create_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreateOptions", []))

    @jsii.member(jsii_name="resetDeleteOptions")
    def reset_delete_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteOptions", []))

    @jsii.member(jsii_name="resetElasticIpPool")
    def reset_elastic_ip_pool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticIpPool", []))

    @jsii.member(jsii_name="resetEphemeralStorage")
    def reset_ephemeral_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEphemeralStorage", []))

    @jsii.member(jsii_name="resetIamInstanceProfile")
    def reset_iam_instance_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamInstanceProfile", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImageId")
    def reset_image_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageId", []))

    @jsii.member(jsii_name="resetImages")
    def reset_images(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImages", []))

    @jsii.member(jsii_name="resetInstanceMetadataOptions")
    def reset_instance_metadata_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceMetadataOptions", []))

    @jsii.member(jsii_name="resetInstanceStorePolicy")
    def reset_instance_store_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceStorePolicy", []))

    @jsii.member(jsii_name="resetInstanceTypes")
    def reset_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypes", []))

    @jsii.member(jsii_name="resetInstanceTypesFilters")
    def reset_instance_types_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceTypesFilters", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPreferredOdTypes")
    def reset_preferred_od_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredOdTypes", []))

    @jsii.member(jsii_name="resetPreferredSpotTypes")
    def reset_preferred_spot_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredSpotTypes", []))

    @jsii.member(jsii_name="resetReservedEnis")
    def reset_reserved_enis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReservedEnis", []))

    @jsii.member(jsii_name="resetResourceLimits")
    def reset_resource_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceLimits", []))

    @jsii.member(jsii_name="resetRestrictScaleDown")
    def reset_restrict_scale_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictScaleDown", []))

    @jsii.member(jsii_name="resetRootVolumeSize")
    def reset_root_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeSize", []))

    @jsii.member(jsii_name="resetSchedulingShutdownHours")
    def reset_scheduling_shutdown_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingShutdownHours", []))

    @jsii.member(jsii_name="resetSchedulingTask")
    def reset_scheduling_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedulingTask", []))

    @jsii.member(jsii_name="resetSecurityGroups")
    def reset_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroups", []))

    @jsii.member(jsii_name="resetStartupTaints")
    def reset_startup_taints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartupTaints", []))

    @jsii.member(jsii_name="resetStrategy")
    def reset_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrategy", []))

    @jsii.member(jsii_name="resetSubnetIds")
    def reset_subnet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetIds", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTaints")
    def reset_taints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaints", []))

    @jsii.member(jsii_name="resetUpdatePolicy")
    def reset_update_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatePolicy", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

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
    @jsii.member(jsii_name="autoscaleDown")
    def autoscale_down(self) -> "OceanAwsLaunchSpecAutoscaleDownList":
        return typing.cast("OceanAwsLaunchSpecAutoscaleDownList", jsii.get(self, "autoscaleDown"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadrooms")
    def autoscale_headrooms(self) -> "OceanAwsLaunchSpecAutoscaleHeadroomsList":
        return typing.cast("OceanAwsLaunchSpecAutoscaleHeadroomsList", jsii.get(self, "autoscaleHeadrooms"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomsAutomatic")
    def autoscale_headrooms_automatic(
        self,
    ) -> "OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticList":
        return typing.cast("OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticList", jsii.get(self, "autoscaleHeadroomsAutomatic"))

    @builtins.property
    @jsii.member(jsii_name="blockDeviceMappings")
    def block_device_mappings(self) -> "OceanAwsLaunchSpecBlockDeviceMappingsList":
        return typing.cast("OceanAwsLaunchSpecBlockDeviceMappingsList", jsii.get(self, "blockDeviceMappings"))

    @builtins.property
    @jsii.member(jsii_name="createOptions")
    def create_options(self) -> "OceanAwsLaunchSpecCreateOptionsOutputReference":
        return typing.cast("OceanAwsLaunchSpecCreateOptionsOutputReference", jsii.get(self, "createOptions"))

    @builtins.property
    @jsii.member(jsii_name="deleteOptions")
    def delete_options(self) -> "OceanAwsLaunchSpecDeleteOptionsOutputReference":
        return typing.cast("OceanAwsLaunchSpecDeleteOptionsOutputReference", jsii.get(self, "deleteOptions"))

    @builtins.property
    @jsii.member(jsii_name="elasticIpPool")
    def elastic_ip_pool(self) -> "OceanAwsLaunchSpecElasticIpPoolList":
        return typing.cast("OceanAwsLaunchSpecElasticIpPoolList", jsii.get(self, "elasticIpPool"))

    @builtins.property
    @jsii.member(jsii_name="ephemeralStorage")
    def ephemeral_storage(self) -> "OceanAwsLaunchSpecEphemeralStorageList":
        return typing.cast("OceanAwsLaunchSpecEphemeralStorageList", jsii.get(self, "ephemeralStorage"))

    @builtins.property
    @jsii.member(jsii_name="images")
    def images(self) -> "OceanAwsLaunchSpecImagesList":
        return typing.cast("OceanAwsLaunchSpecImagesList", jsii.get(self, "images"))

    @builtins.property
    @jsii.member(jsii_name="instanceMetadataOptions")
    def instance_metadata_options(
        self,
    ) -> "OceanAwsLaunchSpecInstanceMetadataOptionsOutputReference":
        return typing.cast("OceanAwsLaunchSpecInstanceMetadataOptionsOutputReference", jsii.get(self, "instanceMetadataOptions"))

    @builtins.property
    @jsii.member(jsii_name="instanceStorePolicy")
    def instance_store_policy(
        self,
    ) -> "OceanAwsLaunchSpecInstanceStorePolicyOutputReference":
        return typing.cast("OceanAwsLaunchSpecInstanceStorePolicyOutputReference", jsii.get(self, "instanceStorePolicy"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesFilters")
    def instance_types_filters(
        self,
    ) -> "OceanAwsLaunchSpecInstanceTypesFiltersOutputReference":
        return typing.cast("OceanAwsLaunchSpecInstanceTypesFiltersOutputReference", jsii.get(self, "instanceTypesFilters"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> "OceanAwsLaunchSpecLabelsList":
        return typing.cast("OceanAwsLaunchSpecLabelsList", jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimits")
    def resource_limits(self) -> "OceanAwsLaunchSpecResourceLimitsList":
        return typing.cast("OceanAwsLaunchSpecResourceLimitsList", jsii.get(self, "resourceLimits"))

    @builtins.property
    @jsii.member(jsii_name="schedulingShutdownHours")
    def scheduling_shutdown_hours(
        self,
    ) -> "OceanAwsLaunchSpecSchedulingShutdownHoursOutputReference":
        return typing.cast("OceanAwsLaunchSpecSchedulingShutdownHoursOutputReference", jsii.get(self, "schedulingShutdownHours"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTask")
    def scheduling_task(self) -> "OceanAwsLaunchSpecSchedulingTaskList":
        return typing.cast("OceanAwsLaunchSpecSchedulingTaskList", jsii.get(self, "schedulingTask"))

    @builtins.property
    @jsii.member(jsii_name="startupTaints")
    def startup_taints(self) -> "OceanAwsLaunchSpecStartupTaintsList":
        return typing.cast("OceanAwsLaunchSpecStartupTaintsList", jsii.get(self, "startupTaints"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "OceanAwsLaunchSpecStrategyList":
        return typing.cast("OceanAwsLaunchSpecStrategyList", jsii.get(self, "strategy"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "OceanAwsLaunchSpecTagsList":
        return typing.cast("OceanAwsLaunchSpecTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="taints")
    def taints(self) -> "OceanAwsLaunchSpecTaintsList":
        return typing.cast("OceanAwsLaunchSpecTaintsList", jsii.get(self, "taints"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> "OceanAwsLaunchSpecUpdatePolicyOutputReference":
        return typing.cast("OceanAwsLaunchSpecUpdatePolicyOutputReference", jsii.get(self, "updatePolicy"))

    @builtins.property
    @jsii.member(jsii_name="associatePublicIpAddressInput")
    def associate_public_ip_address_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "associatePublicIpAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleDownInput")
    def autoscale_down_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecAutoscaleDown"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecAutoscaleDown"]]], jsii.get(self, "autoscaleDownInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomsAutomaticInput")
    def autoscale_headrooms_automatic_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic"]]], jsii.get(self, "autoscaleHeadroomsAutomaticInput"))

    @builtins.property
    @jsii.member(jsii_name="autoscaleHeadroomsInput")
    def autoscale_headrooms_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecAutoscaleHeadrooms"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecAutoscaleHeadrooms"]]], jsii.get(self, "autoscaleHeadroomsInput"))

    @builtins.property
    @jsii.member(jsii_name="blockDeviceMappingsInput")
    def block_device_mappings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecBlockDeviceMappings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecBlockDeviceMappings"]]], jsii.get(self, "blockDeviceMappingsInput"))

    @builtins.property
    @jsii.member(jsii_name="createOptionsInput")
    def create_options_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecCreateOptions"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecCreateOptions"], jsii.get(self, "createOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteOptionsInput")
    def delete_options_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecDeleteOptions"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecDeleteOptions"], jsii.get(self, "deleteOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="elasticIpPoolInput")
    def elastic_ip_pool_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecElasticIpPool"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecElasticIpPool"]]], jsii.get(self, "elasticIpPoolInput"))

    @builtins.property
    @jsii.member(jsii_name="ephemeralStorageInput")
    def ephemeral_storage_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecEphemeralStorage"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecEphemeralStorage"]]], jsii.get(self, "ephemeralStorageInput"))

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
    @jsii.member(jsii_name="imagesInput")
    def images_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecImages"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecImages"]]], jsii.get(self, "imagesInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceMetadataOptionsInput")
    def instance_metadata_options_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecInstanceMetadataOptions"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecInstanceMetadataOptions"], jsii.get(self, "instanceMetadataOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceStorePolicyInput")
    def instance_store_policy_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecInstanceStorePolicy"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecInstanceStorePolicy"], jsii.get(self, "instanceStorePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesFiltersInput")
    def instance_types_filters_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecInstanceTypesFilters"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecInstanceTypesFilters"], jsii.get(self, "instanceTypesFiltersInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesInput")
    def instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecLabels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecLabels"]]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="oceanIdInput")
    def ocean_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oceanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredOdTypesInput")
    def preferred_od_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredOdTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredSpotTypesInput")
    def preferred_spot_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredSpotTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="reservedEnisInput")
    def reserved_enis_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "reservedEnisInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimitsInput")
    def resource_limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecResourceLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecResourceLimits"]]], jsii.get(self, "resourceLimitsInput"))

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
    @jsii.member(jsii_name="schedulingShutdownHoursInput")
    def scheduling_shutdown_hours_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecSchedulingShutdownHours"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecSchedulingShutdownHours"], jsii.get(self, "schedulingShutdownHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="schedulingTaskInput")
    def scheduling_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTask"]]], jsii.get(self, "schedulingTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="securityGroupsInput")
    def security_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="startupTaintsInput")
    def startup_taints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStartupTaints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStartupTaints"]]], jsii.get(self, "startupTaintsInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStrategy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStrategy"]]], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="taintsInput")
    def taints_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTaints"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTaints"]]], jsii.get(self, "taintsInput"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicyInput")
    def update_policy_input(self) -> typing.Optional["OceanAwsLaunchSpecUpdatePolicy"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecUpdatePolicy"], jsii.get(self, "updatePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e2c5cc4576388a49f924ba6d183ab02ab6ae44f8d4cbc6fa54d0dbea3dae652c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "associatePublicIpAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamInstanceProfile")
    def iam_instance_profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamInstanceProfile"))

    @iam_instance_profile.setter
    def iam_instance_profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb3db31e636a77d017cf37ec506c7c32e82df9b6201f46c917d1e0f7700f0489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamInstanceProfile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a69051fd18930c5d831db01e8424712c15faa1bd94f1a0e220304299bfa3be1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a73276661b0b20f0b014a4599232fc533b0b7130f59ff13e4bbcfb44b69641d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceTypes")
    def instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypes"))

    @instance_types.setter
    def instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5235fba41453ec8f4ced5096e23ec94e16e72dbd449c36b7f190d1478600bee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcabc90032713eb4d62e55d366f609a7a3b0f01be091287cfcd50133ae8d0252)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oceanId")
    def ocean_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oceanId"))

    @ocean_id.setter
    def ocean_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48c7cb551a46240fe335a48d425fbac4a3693f9acada5612229fd7de1cf4cd9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oceanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredOdTypes")
    def preferred_od_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredOdTypes"))

    @preferred_od_types.setter
    def preferred_od_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8e19215e5038c8c4dd9900840282e6c2e062eae46db69f47bc7961d7e6b6e04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredOdTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preferredSpotTypes")
    def preferred_spot_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredSpotTypes"))

    @preferred_spot_types.setter
    def preferred_spot_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b59a674534fe5aa7e4f8d1cf1e5cbb1ef58eb7840a105f909627e9862d84c6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredSpotTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reservedEnis")
    def reserved_enis(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "reservedEnis"))

    @reserved_enis.setter
    def reserved_enis(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04f1e6f07b7d88c56bfd948475987367df4d440e9d1bd6d85dfa4eda900db455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reservedEnis", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__d33b1779883d296245af84965c4bd5c62360f54c8849330f8a8cbd41fc0143b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictScaleDown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootVolumeSize")
    def root_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rootVolumeSize"))

    @root_volume_size.setter
    def root_volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d43888e6487dfebd56a5258dc18adcc383d26e37356aa6de5833c78e73bd360f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootVolumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityGroups")
    def security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroups"))

    @security_groups.setter
    def security_groups(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8827a694d0fac88474c53936c91f3bab007163d9f90e625d58c8da86b6991ddc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityGroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__197277b6d27ac6ed1d3cd2c86b4097a7bd7c8acd83dde5e43b8e03d3ad7d3b3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subnetIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dee50480cfe57e4807ce24cc39da55b7cfb5bf2c9192d7b958e8309914ef625f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleDown",
    jsii_struct_bases=[],
    name_mapping={"max_scale_down_percentage": "maxScaleDownPercentage"},
)
class OceanAwsLaunchSpecAutoscaleDown:
    def __init__(
        self,
        *,
        max_scale_down_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_scale_down_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_scale_down_percentage OceanAwsLaunchSpec#max_scale_down_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ecf59a370015d46d98dc518167891f4d473473b7cc3539e0db8158bd51c5110)
            check_type(argname="argument max_scale_down_percentage", value=max_scale_down_percentage, expected_type=type_hints["max_scale_down_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_scale_down_percentage is not None:
            self._values["max_scale_down_percentage"] = max_scale_down_percentage

    @builtins.property
    def max_scale_down_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_scale_down_percentage OceanAwsLaunchSpec#max_scale_down_percentage}.'''
        result = self._values.get("max_scale_down_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecAutoscaleDown(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecAutoscaleDownList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleDownList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b440c85a8293255b6101a39d42c18eeff4bb7bda2123da1ebd739e726d228fcb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecAutoscaleDownOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efe9b2a4685a77908622b70a0b2fbe72060b90b101615168d796a606e6c7f73)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecAutoscaleDownOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84f968c8bd3ca231a349ac69d260582adffa072630eff3605fa607c7b7cbf2a5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc2663b84b032090a3d7ec819710745eed2a3ab83009d93abcf47dc2355f06cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2bd9bbaf901b9b6f7cd76951c68419633a1332be46e56dad5137c6a6718a301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleDown]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleDown]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleDown]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16f3bd1e2c597a9ace21945c11f092a4728611cc3a2ce9ee2d1b8959b8119bc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecAutoscaleDownOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleDownOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcc82eb769945cf27ae7d0a91dca72dfc0972d06ba1651c912ae8cadd65c9aca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__794e30357086cc1ea487e4131fd090b20e893dbbb4198cfc9e4e2472e1b8afed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScaleDownPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleDown]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleDown]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleDown]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ddfa505fa3c0dac18f25e6c5ec3d2971e741bcc1278b9e3495b24f178955102)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleHeadrooms",
    jsii_struct_bases=[],
    name_mapping={
        "num_of_units": "numOfUnits",
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
    },
)
class OceanAwsLaunchSpecAutoscaleHeadrooms:
    def __init__(
        self,
        *,
        num_of_units: jsii.Number,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#num_of_units OceanAwsLaunchSpec#num_of_units}.
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#cpu_per_unit OceanAwsLaunchSpec#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#gpu_per_unit OceanAwsLaunchSpec#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#memory_per_unit OceanAwsLaunchSpec#memory_per_unit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05a33c9ca5e8a3868d21439a4216439f821d9445d77fc63e40fb98aa40eec877)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#num_of_units OceanAwsLaunchSpec#num_of_units}.'''
        result = self._values.get("num_of_units")
        assert result is not None, "Required property 'num_of_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#cpu_per_unit OceanAwsLaunchSpec#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#gpu_per_unit OceanAwsLaunchSpec#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#memory_per_unit OceanAwsLaunchSpec#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecAutoscaleHeadrooms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic",
    jsii_struct_bases=[],
    name_mapping={"auto_headroom_percentage": "autoHeadroomPercentage"},
)
class OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic:
    def __init__(
        self,
        *,
        auto_headroom_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param auto_headroom_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#auto_headroom_percentage OceanAwsLaunchSpec#auto_headroom_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a58d0ff61a1d4abff3d7099d0d9700a409150a3c56b226f88dba0c4bd8f2263)
            check_type(argname="argument auto_headroom_percentage", value=auto_headroom_percentage, expected_type=type_hints["auto_headroom_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_headroom_percentage is not None:
            self._values["auto_headroom_percentage"] = auto_headroom_percentage

    @builtins.property
    def auto_headroom_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#auto_headroom_percentage OceanAwsLaunchSpec#auto_headroom_percentage}.'''
        result = self._values.get("auto_headroom_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f54d4ea5d13742bd558b11a78c2d4b33ce14ecee7431383fa6d19594afeb7ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8ae2e45ad0f3fa4bf5e07388b6c78f9800c372db506ca2c3ea03e8a51215ab5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d317c72c0c643fac416febd837bf6a844646cea9590e65d6b1e364f90959ab9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cfb1ce78e77ad56611585d88f01bc7d6f91bc48a258675b514ddd3eb32b61f97)
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
            type_hints = typing.get_type_hints(_typecheckingstub__66d242abbb4cd2559d6dc5bd4840abb91fefbef61ba75568e7bd4285751f8059)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d226c08dc1809d7b5cd90d32db3ae056c28293e4d4db4452e3b52c49053b0f90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac58cc06667e66440228ce3a823809b3dc96c35a785c3b3c30a110fada57d274)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ae034a3a125fa20f3e2155e4c7fee4c8abafdc33f85d677f3cc4fccc7a039bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoHeadroomPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b645594ef9caf97e60469bfa06eae49694d18b2b4beecaf85a2772a188e8061a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecAutoscaleHeadroomsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleHeadroomsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ada662d29da9e8084232e7d7969b5b414213e19aaedc0e78416cc37b4ac9921)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecAutoscaleHeadroomsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22ec821188607539d89264131bc10bb79fcbd04f567da9663f81541f43c3057e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecAutoscaleHeadroomsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84988915683e154b058ec29001f2e58529c998bd760108d052121997485b3399)
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
            type_hints = typing.get_type_hints(_typecheckingstub__578b37254801eeeb0fd9d6d3b3a2198481c7540c2917359ca98b4ddd360c1bee)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ceaa570fd9d8d1326a85f3331c3d7dfb88912a7ebd8c984f731b29e0b72687e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadrooms]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadrooms]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadrooms]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bea01102db3d8d2f69329fb42ffb7d91b5af4dc139806d82fa1c8187e9b928d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecAutoscaleHeadroomsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecAutoscaleHeadroomsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28478e53384f7764e0b62551934683c010c8dbbd7192ba0fbad995d7c049eeeb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5bbccdb3e5f6f940d0922e66a0414ded5544e25ec3ec2fa07c879b972712ea79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76a2fa6fdffe57cb960ff52b054bc488f864565154e13915edf1e5e7c436ec54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7728df7d455e198394467c1efc22c19e3bca07f07dac8add1d7b67915aab7261)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a42fa2b6068d10cbbd4a8bee021a4cd27ee8f658ece50a05927c8fff9909e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadrooms]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadrooms]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadrooms]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58f760681abb204b04823e8b4ed815661e2545beac9b437defc3e8a75a4bf346)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappings",
    jsii_struct_bases=[],
    name_mapping={
        "device_name": "deviceName",
        "ebs": "ebs",
        "no_device": "noDevice",
        "virtual_name": "virtualName",
    },
)
class OceanAwsLaunchSpecBlockDeviceMappings:
    def __init__(
        self,
        *,
        device_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional[typing.Union["OceanAwsLaunchSpecBlockDeviceMappingsEbs", typing.Dict[builtins.str, typing.Any]]] = None,
        no_device: typing.Optional[builtins.str] = None,
        virtual_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#device_name OceanAwsLaunchSpec#device_name}.
        :param ebs: ebs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ebs OceanAwsLaunchSpec#ebs}
        :param no_device: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#no_device OceanAwsLaunchSpec#no_device}.
        :param virtual_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#virtual_name OceanAwsLaunchSpec#virtual_name}.
        '''
        if isinstance(ebs, dict):
            ebs = OceanAwsLaunchSpecBlockDeviceMappingsEbs(**ebs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d968a7e52ea3dc07c70e971c88b9e6de0e04403d869cd1f6d577a0eabd752cc7)
            check_type(argname="argument device_name", value=device_name, expected_type=type_hints["device_name"])
            check_type(argname="argument ebs", value=ebs, expected_type=type_hints["ebs"])
            check_type(argname="argument no_device", value=no_device, expected_type=type_hints["no_device"])
            check_type(argname="argument virtual_name", value=virtual_name, expected_type=type_hints["virtual_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if device_name is not None:
            self._values["device_name"] = device_name
        if ebs is not None:
            self._values["ebs"] = ebs
        if no_device is not None:
            self._values["no_device"] = no_device
        if virtual_name is not None:
            self._values["virtual_name"] = virtual_name

    @builtins.property
    def device_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#device_name OceanAwsLaunchSpec#device_name}.'''
        result = self._values.get("device_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs(self) -> typing.Optional["OceanAwsLaunchSpecBlockDeviceMappingsEbs"]:
        '''ebs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ebs OceanAwsLaunchSpec#ebs}
        '''
        result = self._values.get("ebs")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecBlockDeviceMappingsEbs"], result)

    @builtins.property
    def no_device(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#no_device OceanAwsLaunchSpec#no_device}.'''
        result = self._values.get("no_device")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def virtual_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#virtual_name OceanAwsLaunchSpec#virtual_name}.'''
        result = self._values.get("virtual_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecBlockDeviceMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappingsEbs",
    jsii_struct_bases=[],
    name_mapping={
        "delete_on_termination": "deleteOnTermination",
        "dynamic_volume_size": "dynamicVolumeSize",
        "encrypted": "encrypted",
        "iops": "iops",
        "kms_key_id": "kmsKeyId",
        "snapshot_id": "snapshotId",
        "throughput": "throughput",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class OceanAwsLaunchSpecBlockDeviceMappingsEbs:
    def __init__(
        self,
        *,
        delete_on_termination: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dynamic_volume_size: typing.Optional[typing.Union["OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize", typing.Dict[builtins.str, typing.Any]]] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        throughput: typing.Optional[jsii.Number] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_on_termination OceanAwsLaunchSpec#delete_on_termination}.
        :param dynamic_volume_size: dynamic_volume_size block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#dynamic_volume_size OceanAwsLaunchSpec#dynamic_volume_size}
        :param encrypted: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#encrypted OceanAwsLaunchSpec#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#iops OceanAwsLaunchSpec#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#kms_key_id OceanAwsLaunchSpec#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#snapshot_id OceanAwsLaunchSpec#snapshot_id}.
        :param throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#throughput OceanAwsLaunchSpec#throughput}.
        :param volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#volume_size OceanAwsLaunchSpec#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#volume_type OceanAwsLaunchSpec#volume_type}.
        '''
        if isinstance(dynamic_volume_size, dict):
            dynamic_volume_size = OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize(**dynamic_volume_size)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c99cba1ddfbbbf2bd63e11c43861e7323380e4d54a7402351a1169ec2313265e)
            check_type(argname="argument delete_on_termination", value=delete_on_termination, expected_type=type_hints["delete_on_termination"])
            check_type(argname="argument dynamic_volume_size", value=dynamic_volume_size, expected_type=type_hints["dynamic_volume_size"])
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
        if dynamic_volume_size is not None:
            self._values["dynamic_volume_size"] = dynamic_volume_size
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_on_termination OceanAwsLaunchSpec#delete_on_termination}.'''
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dynamic_volume_size(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize"]:
        '''dynamic_volume_size block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#dynamic_volume_size OceanAwsLaunchSpec#dynamic_volume_size}
        '''
        result = self._values.get("dynamic_volume_size")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize"], result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#encrypted OceanAwsLaunchSpec#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#iops OceanAwsLaunchSpec#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#kms_key_id OceanAwsLaunchSpec#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#snapshot_id OceanAwsLaunchSpec#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def throughput(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#throughput OceanAwsLaunchSpec#throughput}.'''
        result = self._values.get("throughput")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#volume_size OceanAwsLaunchSpec#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#volume_type OceanAwsLaunchSpec#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecBlockDeviceMappingsEbs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize",
    jsii_struct_bases=[],
    name_mapping={
        "base_size": "baseSize",
        "resource": "resource",
        "size_per_resource_unit": "sizePerResourceUnit",
    },
)
class OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize:
    def __init__(
        self,
        *,
        base_size: jsii.Number,
        resource: builtins.str,
        size_per_resource_unit: jsii.Number,
    ) -> None:
        '''
        :param base_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#base_size OceanAwsLaunchSpec#base_size}.
        :param resource: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#resource OceanAwsLaunchSpec#resource}.
        :param size_per_resource_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#size_per_resource_unit OceanAwsLaunchSpec#size_per_resource_unit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2674bc182e3263cad712c50bbe4c5a7dba451a1eb58f5fd55dea394a1e998ba9)
            check_type(argname="argument base_size", value=base_size, expected_type=type_hints["base_size"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
            check_type(argname="argument size_per_resource_unit", value=size_per_resource_unit, expected_type=type_hints["size_per_resource_unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "base_size": base_size,
            "resource": resource,
            "size_per_resource_unit": size_per_resource_unit,
        }

    @builtins.property
    def base_size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#base_size OceanAwsLaunchSpec#base_size}.'''
        result = self._values.get("base_size")
        assert result is not None, "Required property 'base_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def resource(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#resource OceanAwsLaunchSpec#resource}.'''
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size_per_resource_unit(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#size_per_resource_unit OceanAwsLaunchSpec#size_per_resource_unit}.'''
        result = self._values.get("size_per_resource_unit")
        assert result is not None, "Required property 'size_per_resource_unit' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSizeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSizeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8125d70995719f5d880ddfe4e560998382576dfa24e62a3edee712453258cbb7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="baseSizeInput")
    def base_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "baseSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceInput")
    def resource_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceInput"))

    @builtins.property
    @jsii.member(jsii_name="sizePerResourceUnitInput")
    def size_per_resource_unit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizePerResourceUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="baseSize")
    def base_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "baseSize"))

    @base_size.setter
    def base_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080f0c29e4b822e9b986ef66d227b9aa0b351536192b1347528808faf3da96db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resource")
    def resource(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resource"))

    @resource.setter
    def resource(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb92f49ce976151713ccfba02b5fdf37608c5b4e163da54be8b4175e9267631b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizePerResourceUnit")
    def size_per_resource_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizePerResourceUnit"))

    @size_per_resource_unit.setter
    def size_per_resource_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32f9351cd6e921760afacdae9d43e701203be01ba0724ceb750bbb0d3ae62bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizePerResourceUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33a34c7099c89674e7cc216c33ea54c835e83d2dd9105d2a204ac2700bfeb785)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecBlockDeviceMappingsEbsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappingsEbsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e620a899dc51852248ccf388a5e82cf521c26e9959b291c885b003879fa936e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDynamicVolumeSize")
    def put_dynamic_volume_size(
        self,
        *,
        base_size: jsii.Number,
        resource: builtins.str,
        size_per_resource_unit: jsii.Number,
    ) -> None:
        '''
        :param base_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#base_size OceanAwsLaunchSpec#base_size}.
        :param resource: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#resource OceanAwsLaunchSpec#resource}.
        :param size_per_resource_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#size_per_resource_unit OceanAwsLaunchSpec#size_per_resource_unit}.
        '''
        value = OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize(
            base_size=base_size,
            resource=resource,
            size_per_resource_unit=size_per_resource_unit,
        )

        return typing.cast(None, jsii.invoke(self, "putDynamicVolumeSize", [value]))

    @jsii.member(jsii_name="resetDeleteOnTermination")
    def reset_delete_on_termination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteOnTermination", []))

    @jsii.member(jsii_name="resetDynamicVolumeSize")
    def reset_dynamic_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamicVolumeSize", []))

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
    @jsii.member(jsii_name="dynamicVolumeSize")
    def dynamic_volume_size(
        self,
    ) -> OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSizeOutputReference:
        return typing.cast(OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSizeOutputReference, jsii.get(self, "dynamicVolumeSize"))

    @builtins.property
    @jsii.member(jsii_name="deleteOnTerminationInput")
    def delete_on_termination_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteOnTerminationInput"))

    @builtins.property
    @jsii.member(jsii_name="dynamicVolumeSizeInput")
    def dynamic_volume_size_input(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize], jsii.get(self, "dynamicVolumeSizeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__613e7a2d66f34e38844d60d0378f8e6fe982d07e49a88736e2911852c0d2ac1c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__20c4e6d82a1c418b581ad783e12d2f57d3f67f04e70d7789d109bb946283454a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encrypted", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f01ce1f02ff72c7ea4dd17528c9f72434b4fc194261cfde0b769cc6661a2b634)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a8d2060620499127fbb5787379400730d95b6d17d58a2c5560094c82e80cbfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kmsKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf57e91da3ee86dffeca7e4d2df681289e5ed5828737ea7f94e7c091e4321970)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snapshotId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="throughput")
    def throughput(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "throughput"))

    @throughput.setter
    def throughput(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a80c0ea7262d6516e8a12f0b6526ca86ff55f70faa7bae44527a9abba93df8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "throughput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeSize")
    def volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumeSize"))

    @volume_size.setter
    def volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__488ec29ec7cdbda2eba3bef872c21573c5b823cb96eb4ab3da58586868b83f1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb887efc37371c308d708653670329711f0b35bd2a8011bd3bb90c570673ea06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbs]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8927785a5efd97e0cf5fc7f8fdcda2e5254c67c66aee6b7e728b7f9eda4d223a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecBlockDeviceMappingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85e3fa0d506a78905c7e96d214525692e0d7556233cb6d103b322332e875eb4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecBlockDeviceMappingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d89de593eb6e6046db3fb5dea8ba24419b0862edfa27b73fb7c909f6d640c8bf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecBlockDeviceMappingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9f392be673243566442e2ecddddea6ca03bf482a319d77d9fafc06513f3bc79)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f536404b5db0cb06eb97f9ab653728fdb7e857fa819a924a484a1ba7fd8d2dba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c03e77359ddca01cd9a17865eadb33f569ed81829969ce4bbf1ac003e12c92ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecBlockDeviceMappings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecBlockDeviceMappings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecBlockDeviceMappings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1084c45dd76a261967a1a8a9d387d3d633b98fa4718bf815c1afa1f90425be96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecBlockDeviceMappingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecBlockDeviceMappingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3016c38b1709cd274fbb5fadf0a63029bf97afb4e0830915b3c6f59e8f8bef68)
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
        dynamic_volume_size: typing.Optional[typing.Union[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize, typing.Dict[builtins.str, typing.Any]]] = None,
        encrypted: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        throughput: typing.Optional[jsii.Number] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_on_termination OceanAwsLaunchSpec#delete_on_termination}.
        :param dynamic_volume_size: dynamic_volume_size block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#dynamic_volume_size OceanAwsLaunchSpec#dynamic_volume_size}
        :param encrypted: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#encrypted OceanAwsLaunchSpec#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#iops OceanAwsLaunchSpec#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#kms_key_id OceanAwsLaunchSpec#kms_key_id}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#snapshot_id OceanAwsLaunchSpec#snapshot_id}.
        :param throughput: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#throughput OceanAwsLaunchSpec#throughput}.
        :param volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#volume_size OceanAwsLaunchSpec#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#volume_type OceanAwsLaunchSpec#volume_type}.
        '''
        value = OceanAwsLaunchSpecBlockDeviceMappingsEbs(
            delete_on_termination=delete_on_termination,
            dynamic_volume_size=dynamic_volume_size,
            encrypted=encrypted,
            iops=iops,
            kms_key_id=kms_key_id,
            snapshot_id=snapshot_id,
            throughput=throughput,
            volume_size=volume_size,
            volume_type=volume_type,
        )

        return typing.cast(None, jsii.invoke(self, "putEbs", [value]))

    @jsii.member(jsii_name="resetDeviceName")
    def reset_device_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeviceName", []))

    @jsii.member(jsii_name="resetEbs")
    def reset_ebs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbs", []))

    @jsii.member(jsii_name="resetNoDevice")
    def reset_no_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoDevice", []))

    @jsii.member(jsii_name="resetVirtualName")
    def reset_virtual_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualName", []))

    @builtins.property
    @jsii.member(jsii_name="ebs")
    def ebs(self) -> OceanAwsLaunchSpecBlockDeviceMappingsEbsOutputReference:
        return typing.cast(OceanAwsLaunchSpecBlockDeviceMappingsEbsOutputReference, jsii.get(self, "ebs"))

    @builtins.property
    @jsii.member(jsii_name="deviceNameInput")
    def device_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsInput")
    def ebs_input(self) -> typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbs]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbs], jsii.get(self, "ebsInput"))

    @builtins.property
    @jsii.member(jsii_name="noDeviceInput")
    def no_device_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "noDeviceInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualNameInput")
    def virtual_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualNameInput"))

    @builtins.property
    @jsii.member(jsii_name="deviceName")
    def device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deviceName"))

    @device_name.setter
    def device_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f192f441aee8af0861802722c597b684f92d4df51bee9d226e88eb9657c596)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noDevice")
    def no_device(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "noDevice"))

    @no_device.setter
    def no_device(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0083af98c48029e3e9db79ecfcf75e5e4f384584cda6a9555be4d80444c61540)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noDevice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualName")
    def virtual_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualName"))

    @virtual_name.setter
    def virtual_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__599ce4113b85f8e84c90ae4da6390180867d7530dcbe9aeb0d70a9214e398741)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecBlockDeviceMappings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecBlockDeviceMappings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecBlockDeviceMappings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b77274f555fc55cdb4dbdcf7a05e79bac55006e476046d2e2e083270f65ac23a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecConfig",
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
        "associate_public_ip_address": "associatePublicIpAddress",
        "autoscale_down": "autoscaleDown",
        "autoscale_headrooms": "autoscaleHeadrooms",
        "autoscale_headrooms_automatic": "autoscaleHeadroomsAutomatic",
        "block_device_mappings": "blockDeviceMappings",
        "create_options": "createOptions",
        "delete_options": "deleteOptions",
        "elastic_ip_pool": "elasticIpPool",
        "ephemeral_storage": "ephemeralStorage",
        "iam_instance_profile": "iamInstanceProfile",
        "id": "id",
        "image_id": "imageId",
        "images": "images",
        "instance_metadata_options": "instanceMetadataOptions",
        "instance_store_policy": "instanceStorePolicy",
        "instance_types": "instanceTypes",
        "instance_types_filters": "instanceTypesFilters",
        "labels": "labels",
        "name": "name",
        "preferred_od_types": "preferredOdTypes",
        "preferred_spot_types": "preferredSpotTypes",
        "reserved_enis": "reservedEnis",
        "resource_limits": "resourceLimits",
        "restrict_scale_down": "restrictScaleDown",
        "root_volume_size": "rootVolumeSize",
        "scheduling_shutdown_hours": "schedulingShutdownHours",
        "scheduling_task": "schedulingTask",
        "security_groups": "securityGroups",
        "startup_taints": "startupTaints",
        "strategy": "strategy",
        "subnet_ids": "subnetIds",
        "tags": "tags",
        "taints": "taints",
        "update_policy": "updatePolicy",
        "user_data": "userData",
    },
)
class OceanAwsLaunchSpecConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        associate_public_ip_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        autoscale_down: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleDown, typing.Dict[builtins.str, typing.Any]]]]] = None,
        autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
        autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]]] = None,
        block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]]] = None,
        create_options: typing.Optional[typing.Union["OceanAwsLaunchSpecCreateOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        delete_options: typing.Optional[typing.Union["OceanAwsLaunchSpecDeleteOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        elastic_ip_pool: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecElasticIpPool", typing.Dict[builtins.str, typing.Any]]]]] = None,
        ephemeral_storage: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecEphemeralStorage", typing.Dict[builtins.str, typing.Any]]]]] = None,
        iam_instance_profile: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        images: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecImages", typing.Dict[builtins.str, typing.Any]]]]] = None,
        instance_metadata_options: typing.Optional[typing.Union["OceanAwsLaunchSpecInstanceMetadataOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_store_policy: typing.Optional[typing.Union["OceanAwsLaunchSpecInstanceStorePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        instance_types_filters: typing.Optional[typing.Union["OceanAwsLaunchSpecInstanceTypesFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        preferred_od_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_spot_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        reserved_enis: typing.Optional[jsii.Number] = None,
        resource_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecResourceLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
        scheduling_shutdown_hours: typing.Optional[typing.Union["OceanAwsLaunchSpecSchedulingShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecSchedulingTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        startup_taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecStartupTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecTaints", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanAwsLaunchSpecUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        user_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ocean_id OceanAwsLaunchSpec#ocean_id}.
        :param associate_public_ip_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#associate_public_ip_address OceanAwsLaunchSpec#associate_public_ip_address}.
        :param autoscale_down: autoscale_down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_down OceanAwsLaunchSpec#autoscale_down}
        :param autoscale_headrooms: autoscale_headrooms block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_headrooms OceanAwsLaunchSpec#autoscale_headrooms}
        :param autoscale_headrooms_automatic: autoscale_headrooms_automatic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_headrooms_automatic OceanAwsLaunchSpec#autoscale_headrooms_automatic}
        :param block_device_mappings: block_device_mappings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#block_device_mappings OceanAwsLaunchSpec#block_device_mappings}
        :param create_options: create_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#create_options OceanAwsLaunchSpec#create_options}
        :param delete_options: delete_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_options OceanAwsLaunchSpec#delete_options}
        :param elastic_ip_pool: elastic_ip_pool block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#elastic_ip_pool OceanAwsLaunchSpec#elastic_ip_pool}
        :param ephemeral_storage: ephemeral_storage block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ephemeral_storage OceanAwsLaunchSpec#ephemeral_storage}
        :param iam_instance_profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#iam_instance_profile OceanAwsLaunchSpec#iam_instance_profile}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#id OceanAwsLaunchSpec#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param image_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#image_id OceanAwsLaunchSpec#image_id}.
        :param images: images block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#images OceanAwsLaunchSpec#images}
        :param instance_metadata_options: instance_metadata_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_metadata_options OceanAwsLaunchSpec#instance_metadata_options}
        :param instance_store_policy: instance_store_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_store_policy OceanAwsLaunchSpec#instance_store_policy}
        :param instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_types OceanAwsLaunchSpec#instance_types}.
        :param instance_types_filters: instance_types_filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_types_filters OceanAwsLaunchSpec#instance_types_filters}
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#labels OceanAwsLaunchSpec#labels}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#name OceanAwsLaunchSpec#name}.
        :param preferred_od_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#preferred_od_types OceanAwsLaunchSpec#preferred_od_types}.
        :param preferred_spot_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#preferred_spot_types OceanAwsLaunchSpec#preferred_spot_types}.
        :param reserved_enis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#reserved_enis OceanAwsLaunchSpec#reserved_enis}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#resource_limits OceanAwsLaunchSpec#resource_limits}
        :param restrict_scale_down: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#restrict_scale_down OceanAwsLaunchSpec#restrict_scale_down}.
        :param root_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#root_volume_size OceanAwsLaunchSpec#root_volume_size}.
        :param scheduling_shutdown_hours: scheduling_shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#scheduling_shutdown_hours OceanAwsLaunchSpec#scheduling_shutdown_hours}
        :param scheduling_task: scheduling_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#scheduling_task OceanAwsLaunchSpec#scheduling_task}
        :param security_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#security_groups OceanAwsLaunchSpec#security_groups}.
        :param startup_taints: startup_taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#startup_taints OceanAwsLaunchSpec#startup_taints}
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#strategy OceanAwsLaunchSpec#strategy}
        :param subnet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#subnet_ids OceanAwsLaunchSpec#subnet_ids}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tags OceanAwsLaunchSpec#tags}
        :param taints: taints block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#taints OceanAwsLaunchSpec#taints}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#update_policy OceanAwsLaunchSpec#update_policy}
        :param user_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#user_data OceanAwsLaunchSpec#user_data}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(create_options, dict):
            create_options = OceanAwsLaunchSpecCreateOptions(**create_options)
        if isinstance(delete_options, dict):
            delete_options = OceanAwsLaunchSpecDeleteOptions(**delete_options)
        if isinstance(instance_metadata_options, dict):
            instance_metadata_options = OceanAwsLaunchSpecInstanceMetadataOptions(**instance_metadata_options)
        if isinstance(instance_store_policy, dict):
            instance_store_policy = OceanAwsLaunchSpecInstanceStorePolicy(**instance_store_policy)
        if isinstance(instance_types_filters, dict):
            instance_types_filters = OceanAwsLaunchSpecInstanceTypesFilters(**instance_types_filters)
        if isinstance(scheduling_shutdown_hours, dict):
            scheduling_shutdown_hours = OceanAwsLaunchSpecSchedulingShutdownHours(**scheduling_shutdown_hours)
        if isinstance(update_policy, dict):
            update_policy = OceanAwsLaunchSpecUpdatePolicy(**update_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3eaa32f152ce09727f2c482e16e44d0e2037a182bf83bfc89b20148ea3301f89)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument ocean_id", value=ocean_id, expected_type=type_hints["ocean_id"])
            check_type(argname="argument associate_public_ip_address", value=associate_public_ip_address, expected_type=type_hints["associate_public_ip_address"])
            check_type(argname="argument autoscale_down", value=autoscale_down, expected_type=type_hints["autoscale_down"])
            check_type(argname="argument autoscale_headrooms", value=autoscale_headrooms, expected_type=type_hints["autoscale_headrooms"])
            check_type(argname="argument autoscale_headrooms_automatic", value=autoscale_headrooms_automatic, expected_type=type_hints["autoscale_headrooms_automatic"])
            check_type(argname="argument block_device_mappings", value=block_device_mappings, expected_type=type_hints["block_device_mappings"])
            check_type(argname="argument create_options", value=create_options, expected_type=type_hints["create_options"])
            check_type(argname="argument delete_options", value=delete_options, expected_type=type_hints["delete_options"])
            check_type(argname="argument elastic_ip_pool", value=elastic_ip_pool, expected_type=type_hints["elastic_ip_pool"])
            check_type(argname="argument ephemeral_storage", value=ephemeral_storage, expected_type=type_hints["ephemeral_storage"])
            check_type(argname="argument iam_instance_profile", value=iam_instance_profile, expected_type=type_hints["iam_instance_profile"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument image_id", value=image_id, expected_type=type_hints["image_id"])
            check_type(argname="argument images", value=images, expected_type=type_hints["images"])
            check_type(argname="argument instance_metadata_options", value=instance_metadata_options, expected_type=type_hints["instance_metadata_options"])
            check_type(argname="argument instance_store_policy", value=instance_store_policy, expected_type=type_hints["instance_store_policy"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument instance_types_filters", value=instance_types_filters, expected_type=type_hints["instance_types_filters"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument preferred_od_types", value=preferred_od_types, expected_type=type_hints["preferred_od_types"])
            check_type(argname="argument preferred_spot_types", value=preferred_spot_types, expected_type=type_hints["preferred_spot_types"])
            check_type(argname="argument reserved_enis", value=reserved_enis, expected_type=type_hints["reserved_enis"])
            check_type(argname="argument resource_limits", value=resource_limits, expected_type=type_hints["resource_limits"])
            check_type(argname="argument restrict_scale_down", value=restrict_scale_down, expected_type=type_hints["restrict_scale_down"])
            check_type(argname="argument root_volume_size", value=root_volume_size, expected_type=type_hints["root_volume_size"])
            check_type(argname="argument scheduling_shutdown_hours", value=scheduling_shutdown_hours, expected_type=type_hints["scheduling_shutdown_hours"])
            check_type(argname="argument scheduling_task", value=scheduling_task, expected_type=type_hints["scheduling_task"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument startup_taints", value=startup_taints, expected_type=type_hints["startup_taints"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument taints", value=taints, expected_type=type_hints["taints"])
            check_type(argname="argument update_policy", value=update_policy, expected_type=type_hints["update_policy"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
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
        if associate_public_ip_address is not None:
            self._values["associate_public_ip_address"] = associate_public_ip_address
        if autoscale_down is not None:
            self._values["autoscale_down"] = autoscale_down
        if autoscale_headrooms is not None:
            self._values["autoscale_headrooms"] = autoscale_headrooms
        if autoscale_headrooms_automatic is not None:
            self._values["autoscale_headrooms_automatic"] = autoscale_headrooms_automatic
        if block_device_mappings is not None:
            self._values["block_device_mappings"] = block_device_mappings
        if create_options is not None:
            self._values["create_options"] = create_options
        if delete_options is not None:
            self._values["delete_options"] = delete_options
        if elastic_ip_pool is not None:
            self._values["elastic_ip_pool"] = elastic_ip_pool
        if ephemeral_storage is not None:
            self._values["ephemeral_storage"] = ephemeral_storage
        if iam_instance_profile is not None:
            self._values["iam_instance_profile"] = iam_instance_profile
        if id is not None:
            self._values["id"] = id
        if image_id is not None:
            self._values["image_id"] = image_id
        if images is not None:
            self._values["images"] = images
        if instance_metadata_options is not None:
            self._values["instance_metadata_options"] = instance_metadata_options
        if instance_store_policy is not None:
            self._values["instance_store_policy"] = instance_store_policy
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if instance_types_filters is not None:
            self._values["instance_types_filters"] = instance_types_filters
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name
        if preferred_od_types is not None:
            self._values["preferred_od_types"] = preferred_od_types
        if preferred_spot_types is not None:
            self._values["preferred_spot_types"] = preferred_spot_types
        if reserved_enis is not None:
            self._values["reserved_enis"] = reserved_enis
        if resource_limits is not None:
            self._values["resource_limits"] = resource_limits
        if restrict_scale_down is not None:
            self._values["restrict_scale_down"] = restrict_scale_down
        if root_volume_size is not None:
            self._values["root_volume_size"] = root_volume_size
        if scheduling_shutdown_hours is not None:
            self._values["scheduling_shutdown_hours"] = scheduling_shutdown_hours
        if scheduling_task is not None:
            self._values["scheduling_task"] = scheduling_task
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if startup_taints is not None:
            self._values["startup_taints"] = startup_taints
        if strategy is not None:
            self._values["strategy"] = strategy
        if subnet_ids is not None:
            self._values["subnet_ids"] = subnet_ids
        if tags is not None:
            self._values["tags"] = tags
        if taints is not None:
            self._values["taints"] = taints
        if update_policy is not None:
            self._values["update_policy"] = update_policy
        if user_data is not None:
            self._values["user_data"] = user_data

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ocean_id OceanAwsLaunchSpec#ocean_id}.'''
        result = self._values.get("ocean_id")
        assert result is not None, "Required property 'ocean_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associate_public_ip_address(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#associate_public_ip_address OceanAwsLaunchSpec#associate_public_ip_address}.'''
        result = self._values.get("associate_public_ip_address")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def autoscale_down(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleDown]]]:
        '''autoscale_down block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_down OceanAwsLaunchSpec#autoscale_down}
        '''
        result = self._values.get("autoscale_down")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleDown]]], result)

    @builtins.property
    def autoscale_headrooms(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadrooms]]]:
        '''autoscale_headrooms block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_headrooms OceanAwsLaunchSpec#autoscale_headrooms}
        '''
        result = self._values.get("autoscale_headrooms")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadrooms]]], result)

    @builtins.property
    def autoscale_headrooms_automatic(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]]:
        '''autoscale_headrooms_automatic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#autoscale_headrooms_automatic OceanAwsLaunchSpec#autoscale_headrooms_automatic}
        '''
        result = self._values.get("autoscale_headrooms_automatic")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]], result)

    @builtins.property
    def block_device_mappings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecBlockDeviceMappings]]]:
        '''block_device_mappings block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#block_device_mappings OceanAwsLaunchSpec#block_device_mappings}
        '''
        result = self._values.get("block_device_mappings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecBlockDeviceMappings]]], result)

    @builtins.property
    def create_options(self) -> typing.Optional["OceanAwsLaunchSpecCreateOptions"]:
        '''create_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#create_options OceanAwsLaunchSpec#create_options}
        '''
        result = self._values.get("create_options")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecCreateOptions"], result)

    @builtins.property
    def delete_options(self) -> typing.Optional["OceanAwsLaunchSpecDeleteOptions"]:
        '''delete_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_options OceanAwsLaunchSpec#delete_options}
        '''
        result = self._values.get("delete_options")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecDeleteOptions"], result)

    @builtins.property
    def elastic_ip_pool(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecElasticIpPool"]]]:
        '''elastic_ip_pool block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#elastic_ip_pool OceanAwsLaunchSpec#elastic_ip_pool}
        '''
        result = self._values.get("elastic_ip_pool")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecElasticIpPool"]]], result)

    @builtins.property
    def ephemeral_storage(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecEphemeralStorage"]]]:
        '''ephemeral_storage block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ephemeral_storage OceanAwsLaunchSpec#ephemeral_storage}
        '''
        result = self._values.get("ephemeral_storage")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecEphemeralStorage"]]], result)

    @builtins.property
    def iam_instance_profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#iam_instance_profile OceanAwsLaunchSpec#iam_instance_profile}.'''
        result = self._values.get("iam_instance_profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#id OceanAwsLaunchSpec#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#image_id OceanAwsLaunchSpec#image_id}.'''
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def images(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecImages"]]]:
        '''images block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#images OceanAwsLaunchSpec#images}
        '''
        result = self._values.get("images")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecImages"]]], result)

    @builtins.property
    def instance_metadata_options(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecInstanceMetadataOptions"]:
        '''instance_metadata_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_metadata_options OceanAwsLaunchSpec#instance_metadata_options}
        '''
        result = self._values.get("instance_metadata_options")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecInstanceMetadataOptions"], result)

    @builtins.property
    def instance_store_policy(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecInstanceStorePolicy"]:
        '''instance_store_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_store_policy OceanAwsLaunchSpec#instance_store_policy}
        '''
        result = self._values.get("instance_store_policy")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecInstanceStorePolicy"], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_types OceanAwsLaunchSpec#instance_types}.'''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def instance_types_filters(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecInstanceTypesFilters"]:
        '''instance_types_filters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_types_filters OceanAwsLaunchSpec#instance_types_filters}
        '''
        result = self._values.get("instance_types_filters")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecInstanceTypesFilters"], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecLabels"]]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#labels OceanAwsLaunchSpec#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecLabels"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#name OceanAwsLaunchSpec#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_od_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#preferred_od_types OceanAwsLaunchSpec#preferred_od_types}.'''
        result = self._values.get("preferred_od_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preferred_spot_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#preferred_spot_types OceanAwsLaunchSpec#preferred_spot_types}.'''
        result = self._values.get("preferred_spot_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def reserved_enis(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#reserved_enis OceanAwsLaunchSpec#reserved_enis}.'''
        result = self._values.get("reserved_enis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resource_limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecResourceLimits"]]]:
        '''resource_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#resource_limits OceanAwsLaunchSpec#resource_limits}
        '''
        result = self._values.get("resource_limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecResourceLimits"]]], result)

    @builtins.property
    def restrict_scale_down(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#restrict_scale_down OceanAwsLaunchSpec#restrict_scale_down}.'''
        result = self._values.get("restrict_scale_down")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def root_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#root_volume_size OceanAwsLaunchSpec#root_volume_size}.'''
        result = self._values.get("root_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scheduling_shutdown_hours(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecSchedulingShutdownHours"]:
        '''scheduling_shutdown_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#scheduling_shutdown_hours OceanAwsLaunchSpec#scheduling_shutdown_hours}
        '''
        result = self._values.get("scheduling_shutdown_hours")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecSchedulingShutdownHours"], result)

    @builtins.property
    def scheduling_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTask"]]]:
        '''scheduling_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#scheduling_task OceanAwsLaunchSpec#scheduling_task}
        '''
        result = self._values.get("scheduling_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTask"]]], result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#security_groups OceanAwsLaunchSpec#security_groups}.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def startup_taints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStartupTaints"]]]:
        '''startup_taints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#startup_taints OceanAwsLaunchSpec#startup_taints}
        '''
        result = self._values.get("startup_taints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStartupTaints"]]], result)

    @builtins.property
    def strategy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStrategy"]]]:
        '''strategy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#strategy OceanAwsLaunchSpec#strategy}
        '''
        result = self._values.get("strategy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecStrategy"]]], result)

    @builtins.property
    def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#subnet_ids OceanAwsLaunchSpec#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tags OceanAwsLaunchSpec#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTags"]]], result)

    @builtins.property
    def taints(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTaints"]]]:
        '''taints block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#taints OceanAwsLaunchSpec#taints}
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecTaints"]]], result)

    @builtins.property
    def update_policy(self) -> typing.Optional["OceanAwsLaunchSpecUpdatePolicy"]:
        '''update_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#update_policy OceanAwsLaunchSpec#update_policy}
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecUpdatePolicy"], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#user_data OceanAwsLaunchSpec#user_data}.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecCreateOptions",
    jsii_struct_bases=[],
    name_mapping={"initial_nodes": "initialNodes"},
)
class OceanAwsLaunchSpecCreateOptions:
    def __init__(self, *, initial_nodes: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param initial_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#initial_nodes OceanAwsLaunchSpec#initial_nodes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc16252590c8f664b327a4827f03d3fc5bedb4eb886368a2e7a72d9d77e76173)
            check_type(argname="argument initial_nodes", value=initial_nodes, expected_type=type_hints["initial_nodes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if initial_nodes is not None:
            self._values["initial_nodes"] = initial_nodes

    @builtins.property
    def initial_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#initial_nodes OceanAwsLaunchSpec#initial_nodes}.'''
        result = self._values.get("initial_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecCreateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecCreateOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecCreateOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__74d26b9ac4b542b105e32988b87431225a09387806e4192078ad687b23763323)
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
            type_hints = typing.get_type_hints(_typecheckingstub__692fe36d67ef77ab00f24f6ca5d955b2f4cfb5d0c03a3329781bbd005ee0447b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initialNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAwsLaunchSpecCreateOptions]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecCreateOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecCreateOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9073d761928dac369df24609d94f2f315c31001612051aa75841af2a48bce453)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecDeleteOptions",
    jsii_struct_bases=[],
    name_mapping={"force_delete": "forceDelete", "delete_nodes": "deleteNodes"},
)
class OceanAwsLaunchSpecDeleteOptions:
    def __init__(
        self,
        *,
        force_delete: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        delete_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param force_delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#force_delete OceanAwsLaunchSpec#force_delete}.
        :param delete_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_nodes OceanAwsLaunchSpec#delete_nodes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5393ebcb720bf722f6370a2bc9e1d3fbd675d27d43574ecc5b8505255fac00)
            check_type(argname="argument force_delete", value=force_delete, expected_type=type_hints["force_delete"])
            check_type(argname="argument delete_nodes", value=delete_nodes, expected_type=type_hints["delete_nodes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "force_delete": force_delete,
        }
        if delete_nodes is not None:
            self._values["delete_nodes"] = delete_nodes

    @builtins.property
    def force_delete(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#force_delete OceanAwsLaunchSpec#force_delete}.'''
        result = self._values.get("force_delete")
        assert result is not None, "Required property 'force_delete' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def delete_nodes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#delete_nodes OceanAwsLaunchSpec#delete_nodes}.'''
        result = self._values.get("delete_nodes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecDeleteOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecDeleteOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecDeleteOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61e44eca7f364d1f8f700be83bfe4bc960843d48836c5b59425985062ad5fa74)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDeleteNodes")
    def reset_delete_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteNodes", []))

    @builtins.property
    @jsii.member(jsii_name="deleteNodesInput")
    def delete_nodes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="forceDeleteInput")
    def force_delete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceDeleteInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteNodes")
    def delete_nodes(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deleteNodes"))

    @delete_nodes.setter
    def delete_nodes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ec898f7f570ad5eadf5d8642d592f630c80249fef11be4fd52640e175323f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forceDelete")
    def force_delete(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceDelete"))

    @force_delete.setter
    def force_delete(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7782b9ee99a2f95ba5b21101e0ba66981f995470b673ce17c6f118c1cd8af690)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDelete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAwsLaunchSpecDeleteOptions]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecDeleteOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecDeleteOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f619f45e861c9404405fdbbe4b999e7cfcb6f41649ded655592927c0e6565f6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecElasticIpPool",
    jsii_struct_bases=[],
    name_mapping={"tag_selector": "tagSelector"},
)
class OceanAwsLaunchSpecElasticIpPool:
    def __init__(
        self,
        *,
        tag_selector: typing.Optional[typing.Union["OceanAwsLaunchSpecElasticIpPoolTagSelector", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param tag_selector: tag_selector block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_selector OceanAwsLaunchSpec#tag_selector}
        '''
        if isinstance(tag_selector, dict):
            tag_selector = OceanAwsLaunchSpecElasticIpPoolTagSelector(**tag_selector)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__286c1a921f484def92c6c633abdc67c3042d3c79d6ca44a4080bbdfa6aaab2fe)
            check_type(argname="argument tag_selector", value=tag_selector, expected_type=type_hints["tag_selector"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if tag_selector is not None:
            self._values["tag_selector"] = tag_selector

    @builtins.property
    def tag_selector(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecElasticIpPoolTagSelector"]:
        '''tag_selector block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_selector OceanAwsLaunchSpec#tag_selector}
        '''
        result = self._values.get("tag_selector")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecElasticIpPoolTagSelector"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecElasticIpPool(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecElasticIpPoolList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecElasticIpPoolList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3f40b603cbf5014582febef730181a1ffbadad5dcbd0a8f63a784789ed85a81)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecElasticIpPoolOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ebbd7ee8304bde1e137f4180d026de9693a1f17b302565b4bb9a490c1bfeeeb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecElasticIpPoolOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cc61b51c4818cfeb75c5ffb15029713fe333255c52b64f793d6f9bd00f0289)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e2a20ecf2f3b8a4f2385e37963534c2b2f5f064bddd7dfbfeb298abbd959f98)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e46fe05b592d457b9d9a0d7c5fd68196443d90d329a7dcdea0b413af5a3d7a37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecElasticIpPool]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecElasticIpPool]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecElasticIpPool]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8908280cb901bf0019919c7bb4d995dbb17be90fe349b72d9d7180cc13bb279)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecElasticIpPoolOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecElasticIpPoolOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__898a7805bf291b17b45a70a8e144905b2b8b9c40221c0678f303e931f94cc410)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTagSelector")
    def put_tag_selector(
        self,
        *,
        tag_key: builtins.str,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param tag_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_key OceanAwsLaunchSpec#tag_key}.
        :param tag_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_value OceanAwsLaunchSpec#tag_value}.
        '''
        value = OceanAwsLaunchSpecElasticIpPoolTagSelector(
            tag_key=tag_key, tag_value=tag_value
        )

        return typing.cast(None, jsii.invoke(self, "putTagSelector", [value]))

    @jsii.member(jsii_name="resetTagSelector")
    def reset_tag_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagSelector", []))

    @builtins.property
    @jsii.member(jsii_name="tagSelector")
    def tag_selector(
        self,
    ) -> "OceanAwsLaunchSpecElasticIpPoolTagSelectorOutputReference":
        return typing.cast("OceanAwsLaunchSpecElasticIpPoolTagSelectorOutputReference", jsii.get(self, "tagSelector"))

    @builtins.property
    @jsii.member(jsii_name="tagSelectorInput")
    def tag_selector_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecElasticIpPoolTagSelector"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecElasticIpPoolTagSelector"], jsii.get(self, "tagSelectorInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecElasticIpPool]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecElasticIpPool]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecElasticIpPool]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__159e3c6f503b84e8c2614b70c032096617f02f9fb3a5cad75e32a5ad1c9bc57b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecElasticIpPoolTagSelector",
    jsii_struct_bases=[],
    name_mapping={"tag_key": "tagKey", "tag_value": "tagValue"},
)
class OceanAwsLaunchSpecElasticIpPoolTagSelector:
    def __init__(
        self,
        *,
        tag_key: builtins.str,
        tag_value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param tag_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_key OceanAwsLaunchSpec#tag_key}.
        :param tag_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_value OceanAwsLaunchSpec#tag_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__892441ca29f30945fac3538212a37c29c131485de7bb1c4f450dca47f64defd2)
            check_type(argname="argument tag_key", value=tag_key, expected_type=type_hints["tag_key"])
            check_type(argname="argument tag_value", value=tag_value, expected_type=type_hints["tag_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "tag_key": tag_key,
        }
        if tag_value is not None:
            self._values["tag_value"] = tag_value

    @builtins.property
    def tag_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_key OceanAwsLaunchSpec#tag_key}.'''
        result = self._values.get("tag_key")
        assert result is not None, "Required property 'tag_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tag_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#tag_value OceanAwsLaunchSpec#tag_value}.'''
        result = self._values.get("tag_value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecElasticIpPoolTagSelector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecElasticIpPoolTagSelectorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecElasticIpPoolTagSelectorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__823368a6413eca3eaa98e74b8f7cff5ac80a02609c636aa7e3f7a3c56e212466)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__91e53458b8981ff1cbe468c0c4d0a8b4c799c7c84d2271e20f5cf3bafed014e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tagValue")
    def tag_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagValue"))

    @tag_value.setter
    def tag_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a25e60d367cc7e31981f9d26aa8c3adda872171de68947c6d5f8bae840406ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tagValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecElasticIpPoolTagSelector]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecElasticIpPoolTagSelector], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecElasticIpPoolTagSelector],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c145597115d269c77cc4b93651dd5be52f666f719ac59bc4470e90438f73b98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecEphemeralStorage",
    jsii_struct_bases=[],
    name_mapping={"ephemeral_storage_device_name": "ephemeralStorageDeviceName"},
)
class OceanAwsLaunchSpecEphemeralStorage:
    def __init__(
        self,
        *,
        ephemeral_storage_device_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ephemeral_storage_device_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ephemeral_storage_device_name OceanAwsLaunchSpec#ephemeral_storage_device_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70291128d605a0e8d8721105cd0ea62ca98fa0f4622458739eccd820dc1bae1f)
            check_type(argname="argument ephemeral_storage_device_name", value=ephemeral_storage_device_name, expected_type=type_hints["ephemeral_storage_device_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ephemeral_storage_device_name is not None:
            self._values["ephemeral_storage_device_name"] = ephemeral_storage_device_name

    @builtins.property
    def ephemeral_storage_device_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#ephemeral_storage_device_name OceanAwsLaunchSpec#ephemeral_storage_device_name}.'''
        result = self._values.get("ephemeral_storage_device_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecEphemeralStorage(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecEphemeralStorageList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecEphemeralStorageList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa188919f22843c3dd2be0dd5444010d6b0b7f410d47e46dcbf3101e77c1d49f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecEphemeralStorageOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12473295db22371980b71da20baab89f01e5fef6da17a88999eb55530149227a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecEphemeralStorageOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a8ac74f4fec78037e91e715e77c3a5a539e3c7df7797006dff57f304e27d70f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38c544d0ecff63c7f89bc1b7ed95a932fda13627e6e72846a825b0d778383dc3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8165f6bab311bf37cddc54b4a9289ce109975d7c4ee91a04513b5d3d01352df3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecEphemeralStorage]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecEphemeralStorage]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecEphemeralStorage]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__025c2553f5edeb6845e42f5ce46dc54774b1c3efd0b55c9ecc24d77d3f6147f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecEphemeralStorageOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecEphemeralStorageOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79b4683278c81a6417d1dba96574e8b268cd9a3a20e060386a9cc2c24b6fc966)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEphemeralStorageDeviceName")
    def reset_ephemeral_storage_device_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEphemeralStorageDeviceName", []))

    @builtins.property
    @jsii.member(jsii_name="ephemeralStorageDeviceNameInput")
    def ephemeral_storage_device_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ephemeralStorageDeviceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ephemeralStorageDeviceName")
    def ephemeral_storage_device_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ephemeralStorageDeviceName"))

    @ephemeral_storage_device_name.setter
    def ephemeral_storage_device_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d468b0ab96684cad61532af71c3fde7d3dc56cb3c8d37957598455044662077)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ephemeralStorageDeviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecEphemeralStorage]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecEphemeralStorage]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecEphemeralStorage]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95b934871961c89e62d392d1fb7fd4e9d94621a88277d07ed05839e21b3bd47c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecImages",
    jsii_struct_bases=[],
    name_mapping={"image_id": "imageId"},
)
class OceanAwsLaunchSpecImages:
    def __init__(self, *, image_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param image_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#image_id OceanAwsLaunchSpec#image_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__016c3056cd3e49fa06519b875b9538ab2bb9288ecbf35dffb523ccc262a1e145)
            check_type(argname="argument image_id", value=image_id, expected_type=type_hints["image_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if image_id is not None:
            self._values["image_id"] = image_id

    @builtins.property
    def image_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#image_id OceanAwsLaunchSpec#image_id}.'''
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecImages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecImagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecImagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c29e318df85b3b348497a5e0c4afc802c05ac281624c6534a053a93973c77b72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAwsLaunchSpecImagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f26bb8321b885dbe265c5dd59deabeb1023c33c2ec7e136403d4aecbf328b5e2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecImagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce0744dd39ae1861620a20745c1476430222f3eeea4b3ed6dcafd4d92d15079a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__253d3287c13576b382065fd4fb44bb55cdd7e31fa0b3405de8eedd4faadf9bf8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e96ed41de1e1b781fa0f44038d8265817bc6ec0c36d25ecde09f43f8327885cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecImages]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecImages]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecImages]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__848e201873502ae5d85e6a0dd650683dd0ed0836edfe3c301ae9a0e5b603a4bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecImagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecImagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9572f4e03afce63f7220cc29a468471fc159bbec8e99167d881c5df5e9add50b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetImageId")
    def reset_image_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageId", []))

    @builtins.property
    @jsii.member(jsii_name="imageIdInput")
    def image_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageIdInput"))

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2044431a188252683f064cd0df19a86ebc914c0477606031b611bcc8292860c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecImages]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecImages]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecImages]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea9c8c2d98b7c0e68c263b520e4883897da8275e8136fb56c64a021ab8e626e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecInstanceMetadataOptions",
    jsii_struct_bases=[],
    name_mapping={
        "http_tokens": "httpTokens",
        "http_put_response_hop_limit": "httpPutResponseHopLimit",
    },
)
class OceanAwsLaunchSpecInstanceMetadataOptions:
    def __init__(
        self,
        *,
        http_tokens: builtins.str,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param http_tokens: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#http_tokens OceanAwsLaunchSpec#http_tokens}.
        :param http_put_response_hop_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#http_put_response_hop_limit OceanAwsLaunchSpec#http_put_response_hop_limit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a0791c2ed5e86a67fc0906fe1215f13002026cde8313aa851f85660f980a68)
            check_type(argname="argument http_tokens", value=http_tokens, expected_type=type_hints["http_tokens"])
            check_type(argname="argument http_put_response_hop_limit", value=http_put_response_hop_limit, expected_type=type_hints["http_put_response_hop_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "http_tokens": http_tokens,
        }
        if http_put_response_hop_limit is not None:
            self._values["http_put_response_hop_limit"] = http_put_response_hop_limit

    @builtins.property
    def http_tokens(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#http_tokens OceanAwsLaunchSpec#http_tokens}.'''
        result = self._values.get("http_tokens")
        assert result is not None, "Required property 'http_tokens' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def http_put_response_hop_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#http_put_response_hop_limit OceanAwsLaunchSpec#http_put_response_hop_limit}.'''
        result = self._values.get("http_put_response_hop_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecInstanceMetadataOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecInstanceMetadataOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecInstanceMetadataOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1da963facf18d03deb295663c51dbf1a026fbb460c8b8b9e7043cb84fefa00b1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHttpPutResponseHopLimit")
    def reset_http_put_response_hop_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpPutResponseHopLimit", []))

    @builtins.property
    @jsii.member(jsii_name="httpPutResponseHopLimitInput")
    def http_put_response_hop_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpPutResponseHopLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="httpTokensInput")
    def http_tokens_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpTokensInput"))

    @builtins.property
    @jsii.member(jsii_name="httpPutResponseHopLimit")
    def http_put_response_hop_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpPutResponseHopLimit"))

    @http_put_response_hop_limit.setter
    def http_put_response_hop_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88ff0ea94d47f78bfb51f472961b91fb0d5ddac8628234579b9c109b8e4e09af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpPutResponseHopLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpTokens")
    def http_tokens(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpTokens"))

    @http_tokens.setter
    def http_tokens(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8f2337652287ba12239219d6d1bd96924b5fa94bcb9ad956f91a87588de871)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecInstanceMetadataOptions]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecInstanceMetadataOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecInstanceMetadataOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8749191449934eab74402c5213283bb5344442b8b8488145bb889f0956fe9382)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecInstanceStorePolicy",
    jsii_struct_bases=[],
    name_mapping={"instance_store_policy_type": "instanceStorePolicyType"},
)
class OceanAwsLaunchSpecInstanceStorePolicy:
    def __init__(
        self,
        *,
        instance_store_policy_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instance_store_policy_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_store_policy_type OceanAwsLaunchSpec#instance_store_policy_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9a33e6d64d2419ce6a6739f5dcba0bfa865c0260cf1ac8be438cf0eb73df133)
            check_type(argname="argument instance_store_policy_type", value=instance_store_policy_type, expected_type=type_hints["instance_store_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if instance_store_policy_type is not None:
            self._values["instance_store_policy_type"] = instance_store_policy_type

    @builtins.property
    def instance_store_policy_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#instance_store_policy_type OceanAwsLaunchSpec#instance_store_policy_type}.'''
        result = self._values.get("instance_store_policy_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecInstanceStorePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecInstanceStorePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecInstanceStorePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f659685eeb5f42219ee8a647e85081c1b2468501519d515c836d081c982c815)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetInstanceStorePolicyType")
    def reset_instance_store_policy_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceStorePolicyType", []))

    @builtins.property
    @jsii.member(jsii_name="instanceStorePolicyTypeInput")
    def instance_store_policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceStorePolicyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceStorePolicyType")
    def instance_store_policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceStorePolicyType"))

    @instance_store_policy_type.setter
    def instance_store_policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aea51c7866579b77cf1ac14bc4b76ebbd9442315921e458f2b3a14fb3e2c84d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceStorePolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAwsLaunchSpecInstanceStorePolicy]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecInstanceStorePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecInstanceStorePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2d10b68185e3a7232df688ea69b2a624ed587ad4792b576a796153e862ff59a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecInstanceTypesFilters",
    jsii_struct_bases=[],
    name_mapping={
        "categories": "categories",
        "disk_types": "diskTypes",
        "exclude_families": "excludeFamilies",
        "exclude_metal": "excludeMetal",
        "hypervisor": "hypervisor",
        "include_families": "includeFamilies",
        "is_ena_supported": "isEnaSupported",
        "max_gpu": "maxGpu",
        "max_memory_gib": "maxMemoryGib",
        "max_network_performance": "maxNetworkPerformance",
        "max_vcpu": "maxVcpu",
        "min_enis": "minEnis",
        "min_gpu": "minGpu",
        "min_memory_gib": "minMemoryGib",
        "min_network_performance": "minNetworkPerformance",
        "min_vcpu": "minVcpu",
        "root_device_types": "rootDeviceTypes",
        "virtualization_types": "virtualizationTypes",
    },
)
class OceanAwsLaunchSpecInstanceTypesFilters:
    def __init__(
        self,
        *,
        categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        disk_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        exclude_metal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hypervisor: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_families: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_ena_supported: typing.Optional[builtins.str] = None,
        max_gpu: typing.Optional[jsii.Number] = None,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_network_performance: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
        min_enis: typing.Optional[jsii.Number] = None,
        min_gpu: typing.Optional[jsii.Number] = None,
        min_memory_gib: typing.Optional[jsii.Number] = None,
        min_network_performance: typing.Optional[jsii.Number] = None,
        min_vcpu: typing.Optional[jsii.Number] = None,
        root_device_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        virtualization_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param categories: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#categories OceanAwsLaunchSpec#categories}.
        :param disk_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#disk_types OceanAwsLaunchSpec#disk_types}.
        :param exclude_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#exclude_families OceanAwsLaunchSpec#exclude_families}.
        :param exclude_metal: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#exclude_metal OceanAwsLaunchSpec#exclude_metal}.
        :param hypervisor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#hypervisor OceanAwsLaunchSpec#hypervisor}.
        :param include_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#include_families OceanAwsLaunchSpec#include_families}.
        :param is_ena_supported: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_ena_supported OceanAwsLaunchSpec#is_ena_supported}.
        :param max_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_gpu OceanAwsLaunchSpec#max_gpu}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_memory_gib OceanAwsLaunchSpec#max_memory_gib}.
        :param max_network_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_network_performance OceanAwsLaunchSpec#max_network_performance}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_vcpu OceanAwsLaunchSpec#max_vcpu}.
        :param min_enis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_enis OceanAwsLaunchSpec#min_enis}.
        :param min_gpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_gpu OceanAwsLaunchSpec#min_gpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_memory_gib OceanAwsLaunchSpec#min_memory_gib}.
        :param min_network_performance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_network_performance OceanAwsLaunchSpec#min_network_performance}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_vcpu OceanAwsLaunchSpec#min_vcpu}.
        :param root_device_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#root_device_types OceanAwsLaunchSpec#root_device_types}.
        :param virtualization_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#virtualization_types OceanAwsLaunchSpec#virtualization_types}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e3d61cd991c3d68f49a2fa70cc0447d1475f9b3c6725c4397fa621269019fd6)
            check_type(argname="argument categories", value=categories, expected_type=type_hints["categories"])
            check_type(argname="argument disk_types", value=disk_types, expected_type=type_hints["disk_types"])
            check_type(argname="argument exclude_families", value=exclude_families, expected_type=type_hints["exclude_families"])
            check_type(argname="argument exclude_metal", value=exclude_metal, expected_type=type_hints["exclude_metal"])
            check_type(argname="argument hypervisor", value=hypervisor, expected_type=type_hints["hypervisor"])
            check_type(argname="argument include_families", value=include_families, expected_type=type_hints["include_families"])
            check_type(argname="argument is_ena_supported", value=is_ena_supported, expected_type=type_hints["is_ena_supported"])
            check_type(argname="argument max_gpu", value=max_gpu, expected_type=type_hints["max_gpu"])
            check_type(argname="argument max_memory_gib", value=max_memory_gib, expected_type=type_hints["max_memory_gib"])
            check_type(argname="argument max_network_performance", value=max_network_performance, expected_type=type_hints["max_network_performance"])
            check_type(argname="argument max_vcpu", value=max_vcpu, expected_type=type_hints["max_vcpu"])
            check_type(argname="argument min_enis", value=min_enis, expected_type=type_hints["min_enis"])
            check_type(argname="argument min_gpu", value=min_gpu, expected_type=type_hints["min_gpu"])
            check_type(argname="argument min_memory_gib", value=min_memory_gib, expected_type=type_hints["min_memory_gib"])
            check_type(argname="argument min_network_performance", value=min_network_performance, expected_type=type_hints["min_network_performance"])
            check_type(argname="argument min_vcpu", value=min_vcpu, expected_type=type_hints["min_vcpu"])
            check_type(argname="argument root_device_types", value=root_device_types, expected_type=type_hints["root_device_types"])
            check_type(argname="argument virtualization_types", value=virtualization_types, expected_type=type_hints["virtualization_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if categories is not None:
            self._values["categories"] = categories
        if disk_types is not None:
            self._values["disk_types"] = disk_types
        if exclude_families is not None:
            self._values["exclude_families"] = exclude_families
        if exclude_metal is not None:
            self._values["exclude_metal"] = exclude_metal
        if hypervisor is not None:
            self._values["hypervisor"] = hypervisor
        if include_families is not None:
            self._values["include_families"] = include_families
        if is_ena_supported is not None:
            self._values["is_ena_supported"] = is_ena_supported
        if max_gpu is not None:
            self._values["max_gpu"] = max_gpu
        if max_memory_gib is not None:
            self._values["max_memory_gib"] = max_memory_gib
        if max_network_performance is not None:
            self._values["max_network_performance"] = max_network_performance
        if max_vcpu is not None:
            self._values["max_vcpu"] = max_vcpu
        if min_enis is not None:
            self._values["min_enis"] = min_enis
        if min_gpu is not None:
            self._values["min_gpu"] = min_gpu
        if min_memory_gib is not None:
            self._values["min_memory_gib"] = min_memory_gib
        if min_network_performance is not None:
            self._values["min_network_performance"] = min_network_performance
        if min_vcpu is not None:
            self._values["min_vcpu"] = min_vcpu
        if root_device_types is not None:
            self._values["root_device_types"] = root_device_types
        if virtualization_types is not None:
            self._values["virtualization_types"] = virtualization_types

    @builtins.property
    def categories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#categories OceanAwsLaunchSpec#categories}.'''
        result = self._values.get("categories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disk_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#disk_types OceanAwsLaunchSpec#disk_types}.'''
        result = self._values.get("disk_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exclude_families(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#exclude_families OceanAwsLaunchSpec#exclude_families}.'''
        result = self._values.get("exclude_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exclude_metal(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#exclude_metal OceanAwsLaunchSpec#exclude_metal}.'''
        result = self._values.get("exclude_metal")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hypervisor(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#hypervisor OceanAwsLaunchSpec#hypervisor}.'''
        result = self._values.get("hypervisor")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_families(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#include_families OceanAwsLaunchSpec#include_families}.'''
        result = self._values.get("include_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_ena_supported(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_ena_supported OceanAwsLaunchSpec#is_ena_supported}.'''
        result = self._values.get("is_ena_supported")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_gpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_gpu OceanAwsLaunchSpec#max_gpu}.'''
        result = self._values.get("max_gpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_memory_gib OceanAwsLaunchSpec#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_network_performance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_network_performance OceanAwsLaunchSpec#max_network_performance}.'''
        result = self._values.get("max_network_performance")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_vcpu OceanAwsLaunchSpec#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_enis(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_enis OceanAwsLaunchSpec#min_enis}.'''
        result = self._values.get("min_enis")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_gpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_gpu OceanAwsLaunchSpec#min_gpu}.'''
        result = self._values.get("min_gpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_memory_gib OceanAwsLaunchSpec#min_memory_gib}.'''
        result = self._values.get("min_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_network_performance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_network_performance OceanAwsLaunchSpec#min_network_performance}.'''
        result = self._values.get("min_network_performance")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_vcpu OceanAwsLaunchSpec#min_vcpu}.'''
        result = self._values.get("min_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def root_device_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#root_device_types OceanAwsLaunchSpec#root_device_types}.'''
        result = self._values.get("root_device_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def virtualization_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#virtualization_types OceanAwsLaunchSpec#virtualization_types}.'''
        result = self._values.get("virtualization_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecInstanceTypesFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecInstanceTypesFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecInstanceTypesFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac30592f2eab2537a1048778349802f56fbfe504dc49caa7ced64cd412442a78)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCategories")
    def reset_categories(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCategories", []))

    @jsii.member(jsii_name="resetDiskTypes")
    def reset_disk_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskTypes", []))

    @jsii.member(jsii_name="resetExcludeFamilies")
    def reset_exclude_families(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeFamilies", []))

    @jsii.member(jsii_name="resetExcludeMetal")
    def reset_exclude_metal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeMetal", []))

    @jsii.member(jsii_name="resetHypervisor")
    def reset_hypervisor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHypervisor", []))

    @jsii.member(jsii_name="resetIncludeFamilies")
    def reset_include_families(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeFamilies", []))

    @jsii.member(jsii_name="resetIsEnaSupported")
    def reset_is_ena_supported(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnaSupported", []))

    @jsii.member(jsii_name="resetMaxGpu")
    def reset_max_gpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxGpu", []))

    @jsii.member(jsii_name="resetMaxMemoryGib")
    def reset_max_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMemoryGib", []))

    @jsii.member(jsii_name="resetMaxNetworkPerformance")
    def reset_max_network_performance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxNetworkPerformance", []))

    @jsii.member(jsii_name="resetMaxVcpu")
    def reset_max_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxVcpu", []))

    @jsii.member(jsii_name="resetMinEnis")
    def reset_min_enis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinEnis", []))

    @jsii.member(jsii_name="resetMinGpu")
    def reset_min_gpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinGpu", []))

    @jsii.member(jsii_name="resetMinMemoryGib")
    def reset_min_memory_gib(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinMemoryGib", []))

    @jsii.member(jsii_name="resetMinNetworkPerformance")
    def reset_min_network_performance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinNetworkPerformance", []))

    @jsii.member(jsii_name="resetMinVcpu")
    def reset_min_vcpu(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinVcpu", []))

    @jsii.member(jsii_name="resetRootDeviceTypes")
    def reset_root_device_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootDeviceTypes", []))

    @jsii.member(jsii_name="resetVirtualizationTypes")
    def reset_virtualization_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualizationTypes", []))

    @builtins.property
    @jsii.member(jsii_name="categoriesInput")
    def categories_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "categoriesInput"))

    @builtins.property
    @jsii.member(jsii_name="diskTypesInput")
    def disk_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "diskTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeFamiliesInput")
    def exclude_families_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludeFamiliesInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeMetalInput")
    def exclude_metal_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeMetalInput"))

    @builtins.property
    @jsii.member(jsii_name="hypervisorInput")
    def hypervisor_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hypervisorInput"))

    @builtins.property
    @jsii.member(jsii_name="includeFamiliesInput")
    def include_families_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "includeFamiliesInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnaSupportedInput")
    def is_ena_supported_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "isEnaSupportedInput"))

    @builtins.property
    @jsii.member(jsii_name="maxGpuInput")
    def max_gpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxGpuInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGibInput")
    def max_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="maxNetworkPerformanceInput")
    def max_network_performance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxNetworkPerformanceInput"))

    @builtins.property
    @jsii.member(jsii_name="maxVcpuInput")
    def max_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="minEnisInput")
    def min_enis_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minEnisInput"))

    @builtins.property
    @jsii.member(jsii_name="minGpuInput")
    def min_gpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minGpuInput"))

    @builtins.property
    @jsii.member(jsii_name="minMemoryGibInput")
    def min_memory_gib_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minMemoryGibInput"))

    @builtins.property
    @jsii.member(jsii_name="minNetworkPerformanceInput")
    def min_network_performance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minNetworkPerformanceInput"))

    @builtins.property
    @jsii.member(jsii_name="minVcpuInput")
    def min_vcpu_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minVcpuInput"))

    @builtins.property
    @jsii.member(jsii_name="rootDeviceTypesInput")
    def root_device_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rootDeviceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualizationTypesInput")
    def virtualization_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "virtualizationTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="categories")
    def categories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "categories"))

    @categories.setter
    def categories(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ad833e1b35ebfe3c39a6b8cbc592af93432be2cd02affa2f8640508ee785ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "categories", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskTypes")
    def disk_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "diskTypes"))

    @disk_types.setter
    def disk_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d5dcbaadf188adffd1e756db1a69fe0956033288d76b44076c40e821f8b6e5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeFamilies")
    def exclude_families(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludeFamilies"))

    @exclude_families.setter
    def exclude_families(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b7ed29e1d653efa280b2b67b1362525e8dff444db9e4d696ca4603d357a3c69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeMetal")
    def exclude_metal(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludeMetal"))

    @exclude_metal.setter
    def exclude_metal(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98d24588051965603c56845bf7542bc60b7bd148d24acd5ddba6edd4b6b1087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeMetal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hypervisor")
    def hypervisor(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hypervisor"))

    @hypervisor.setter
    def hypervisor(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__237801519f14c6016d914d4694e56405f10f0cae2a3c23ba68c977a3856e26bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hypervisor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeFamilies")
    def include_families(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeFamilies"))

    @include_families.setter
    def include_families(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8731a8d104062d83eba5aaa9247c1e664f7acb60107ec9983582ca5cb2b6dc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isEnaSupported")
    def is_ena_supported(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "isEnaSupported"))

    @is_ena_supported.setter
    def is_ena_supported(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c141119f214a2ffc72e7c54b12ddb35265a86493f29476bd8e0479a472ff5b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnaSupported", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxGpu")
    def max_gpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxGpu"))

    @max_gpu.setter
    def max_gpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e923d5795278e579d8510f87999ea7380187796ecfc6882787099a003c4a930)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxGpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGib")
    def max_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemoryGib"))

    @max_memory_gib.setter
    def max_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69a75e3f9a4df2331236f43de4e995217a2a454e686b70de96c682b3c07fa003)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxNetworkPerformance")
    def max_network_performance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxNetworkPerformance"))

    @max_network_performance.setter
    def max_network_performance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4c04e266f0a5087f4d06093b026dabf2f255363e2d285b0d1ac98dee1e0ded0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxNetworkPerformance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4822c90faba0c9500d964194dabdd859885a69df57b24d96d55cae52fe032de3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minEnis")
    def min_enis(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minEnis"))

    @min_enis.setter
    def min_enis(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3c67083e80771780d2da8b0f03b4b2f492580ec1ed669d97b39fca7b8615751)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minEnis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minGpu")
    def min_gpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minGpu"))

    @min_gpu.setter
    def min_gpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c69686df3bffb070244328b5f9856665d6e0c8f69a27e6fb40b8cd2ce485c513)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minGpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemoryGib")
    def min_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemoryGib"))

    @min_memory_gib.setter
    def min_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__559dbd0b99a444633a3b9e2ef68c74bd83ae365241b9ae2e48f647bfcba38979)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minNetworkPerformance")
    def min_network_performance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNetworkPerformance"))

    @min_network_performance.setter
    def min_network_performance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfc6d2292317c36aca766aa9c662d6b88ea271dab9948b669ecffa6ca0d7880d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minNetworkPerformance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVcpu")
    def min_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpu"))

    @min_vcpu.setter
    def min_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be83017260e98727e05a4d6c6658f6c56c8029e9ca7f72ef9e07ba78f7ec49eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootDeviceTypes")
    def root_device_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "rootDeviceTypes"))

    @root_device_types.setter
    def root_device_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07fcd2bc0048ca412ddebb3ba4b1ec899a08d60d8bdfb59e7e70dd8f169c7780)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootDeviceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualizationTypes")
    def virtualization_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "virtualizationTypes"))

    @virtualization_types.setter
    def virtualization_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__038ddcd7a46a40851e8b92381f2a6efa8e3ab2bdfc511643f70e86ee35ea5f50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualizationTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAwsLaunchSpecInstanceTypesFilters]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecInstanceTypesFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecInstanceTypesFilters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99d534fe1d19a021657517fd317441ada2511dceda5cdd70e4fc6d4ff0b7e4e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class OceanAwsLaunchSpecLabels:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__395182d77175bb3a2ec9e546ee09076cc24f7005c33c44cc509204e8fa73d6f9)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ddb6a48c3bf89ccdd9d8786de14d84a4a7a9a74d9b268b1bfbcfd3525c545bc8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAwsLaunchSpecLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d527ad3d0def5552bf4ed6e81e96dc00093a5da3860cd3f80e92bf4bb2029b18)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b44be41795172b8a0c44da5a4b18b17c4cede7204fbf931d0b48f561ff037af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f59791ee6ff7cbc02bb9afa44cbd3d2afb21f299e3a355f03d19acfcc26c831)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5b5b7511cb1674192d06c9450e2d475e5271917b6932642c0b7b137036aa798)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b080a4fd12f2e5decb9632b3753ade931a6f92640b910b813bcd5b058aa8f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd587d5cbbef608d0e4d9b18380d11478858ecd8a04c5c987d128533bc150f26)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3117eb3dd2850608d5a0a9d9d6e588febe772bfca1396809a6894a740c3bc885)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b75b07da4d6cb265bab5bd60b6c28e8c0a680f4499f2d969fff7b17581e4650)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__813c6db13d6ce6a9c41f38b4c3defc5ef253b26d6d70c02c8a040d2f23df5d20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecResourceLimits",
    jsii_struct_bases=[],
    name_mapping={
        "max_instance_count": "maxInstanceCount",
        "min_instance_count": "minInstanceCount",
    },
)
class OceanAwsLaunchSpecResourceLimits:
    def __init__(
        self,
        *,
        max_instance_count: typing.Optional[jsii.Number] = None,
        min_instance_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_instance_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_instance_count OceanAwsLaunchSpec#max_instance_count}.
        :param min_instance_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_instance_count OceanAwsLaunchSpec#min_instance_count}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__297ff0bcba9a783d45967d6be877b6039829ccb29d28e3404328fe92db682a60)
            check_type(argname="argument max_instance_count", value=max_instance_count, expected_type=type_hints["max_instance_count"])
            check_type(argname="argument min_instance_count", value=min_instance_count, expected_type=type_hints["min_instance_count"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_instance_count is not None:
            self._values["max_instance_count"] = max_instance_count
        if min_instance_count is not None:
            self._values["min_instance_count"] = min_instance_count

    @builtins.property
    def max_instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#max_instance_count OceanAwsLaunchSpec#max_instance_count}.'''
        result = self._values.get("max_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_instance_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#min_instance_count OceanAwsLaunchSpec#min_instance_count}.'''
        result = self._values.get("min_instance_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecResourceLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecResourceLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecResourceLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a710f0b7b80ba61c1f1f6bfbd58b9a98401a3ce13c30d237a16c134424c471e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecResourceLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ee3d9817217cd79b61bc06b8ed9b631c5520068d71928b603517f6cf7f7cfe6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecResourceLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd1dde861fa18fb406792822ddf2eff5766e6dc1bc89bc933f42de6653dd9d46)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5dbed9c76bb511586b936833e2a4c95ac0a6065a5f20e37ab67d1535ce3492c2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e69c2c46c61caecd3f96b92990555e0f6c1323fd78c449e054f901ef83ca2cac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecResourceLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecResourceLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecResourceLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453787d6ad48ede58c01edf8a6eeebb411bdc2426819d1e3d4ed024a74a71094)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecResourceLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecResourceLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__efae5918e93573074e4688cf8dd441f571bc50a60c5d91163f44d41659bcb6f8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__16ac1504d81e20c857fbb7cede1e09912bb5d8fcf89bc25b732f9956b8d074b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e35e2127a91a20ce95f24c937d660d87b8e729da7eae23c14996af0af6d15dc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecResourceLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecResourceLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecResourceLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f9c71dcdeecb29b609935e2cd5e6187309aa766e81d0f8e6734f33a5314734b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingShutdownHours",
    jsii_struct_bases=[],
    name_mapping={"time_windows": "timeWindows", "is_enabled": "isEnabled"},
)
class OceanAwsLaunchSpecSchedulingShutdownHours:
    def __init__(
        self,
        *,
        time_windows: typing.Sequence[builtins.str],
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#time_windows OceanAwsLaunchSpec#time_windows}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_enabled OceanAwsLaunchSpec#is_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6340ebdfaf9531e8d1f66ff8e802e45adbc3dcd6802ad01207d67569d68f44b)
            check_type(argname="argument time_windows", value=time_windows, expected_type=type_hints["time_windows"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "time_windows": time_windows,
        }
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled

    @builtins.property
    def time_windows(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#time_windows OceanAwsLaunchSpec#time_windows}.'''
        result = self._values.get("time_windows")
        assert result is not None, "Required property 'time_windows' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_enabled OceanAwsLaunchSpec#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecSchedulingShutdownHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecSchedulingShutdownHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingShutdownHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff6d45df138625781b182d0acb70f97184cf96c480a601e60afd33ccf33d2619)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__8352e8dea11014ea14be7c47c7269333cd69f97e382a6c4203821803cf222ff6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindows")
    def time_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeWindows"))

    @time_windows.setter
    def time_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87ba5a3a9ceb4303e31a32001573a4956a1f2195117662828bf2d96b1cc01edf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecSchedulingShutdownHours]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecSchedulingShutdownHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecSchedulingShutdownHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6141d803e188b8fb2f2138917cf47f303ea56571724f87448e8acf61a1f4bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingTask",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "is_enabled": "isEnabled",
        "task_type": "taskType",
        "task_headroom": "taskHeadroom",
    },
)
class OceanAwsLaunchSpecSchedulingTask:
    def __init__(
        self,
        *,
        cron_expression: builtins.str,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        task_type: builtins.str,
        task_headroom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecSchedulingTaskTaskHeadroom", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#cron_expression OceanAwsLaunchSpec#cron_expression}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_enabled OceanAwsLaunchSpec#is_enabled}.
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#task_type OceanAwsLaunchSpec#task_type}.
        :param task_headroom: task_headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#task_headroom OceanAwsLaunchSpec#task_headroom}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45a6845fa570b1c607ca1e20366f4a4ed98964a831f8485a50abd9f8d6d6973d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#cron_expression OceanAwsLaunchSpec#cron_expression}.'''
        result = self._values.get("cron_expression")
        assert result is not None, "Required property 'cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#is_enabled OceanAwsLaunchSpec#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#task_type OceanAwsLaunchSpec#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_headroom(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTaskTaskHeadroom"]]]:
        '''task_headroom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#task_headroom OceanAwsLaunchSpec#task_headroom}
        '''
        result = self._values.get("task_headroom")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTaskTaskHeadroom"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecSchedulingTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecSchedulingTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8241dc7e68ed971e91e838f565e627c2b099a01363d2eb63331f570c613b6850)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecSchedulingTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6853807d0bc0e49f16ee5e74b6770a4db4b3fd05b47daa13b5a6f58215dc0cd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecSchedulingTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__573472154c0a13cb804073904b5d6c325550723ce684e322f49f5595fcc11a29)
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
            type_hints = typing.get_type_hints(_typecheckingstub__03f360c72f172d0b626dc76bbbb7e0f31042153e95bd0bf797ffe4269a879214)
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
            type_hints = typing.get_type_hints(_typecheckingstub__025114f3d18b16295496cdd9a53d5a77cde9c03f4bb40bd858d2c3e6f79198b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f00daaee5c955123e2381ef57aae5f5454149a0148b8934245467ec4488fc180)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecSchedulingTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__33ac16ef185010e913c7f879e4a482b7d46092089fca4c33241500361612abab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTaskHeadroom")
    def put_task_headroom(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanAwsLaunchSpecSchedulingTaskTaskHeadroom", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__284b1847af1f7e61cf470db5c08e2b79ea5caeeebff6bdb011257f7fa8664398)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaskHeadroom", [value]))

    @jsii.member(jsii_name="resetTaskHeadroom")
    def reset_task_headroom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskHeadroom", []))

    @builtins.property
    @jsii.member(jsii_name="taskHeadroom")
    def task_headroom(self) -> "OceanAwsLaunchSpecSchedulingTaskTaskHeadroomList":
        return typing.cast("OceanAwsLaunchSpecSchedulingTaskTaskHeadroomList", jsii.get(self, "taskHeadroom"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTaskTaskHeadroom"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanAwsLaunchSpecSchedulingTaskTaskHeadroom"]]], jsii.get(self, "taskHeadroomInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3ec9670977b2320764e4044e7e514d75e367791f99096ca141af38d512887049)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b861291aeb4a7325023baa993880dc9f5e7e000de19c0ebe3846d43159faaee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7fd2ac268e84e52c650618f86d5fffd6993b573e6baef7c9a2bc1c946a58801)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99ebea17e70819cb44c909e1ac506cc4fccc7f03439bd4240e10f63ff29053b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingTaskTaskHeadroom",
    jsii_struct_bases=[],
    name_mapping={
        "num_of_units": "numOfUnits",
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
    },
)
class OceanAwsLaunchSpecSchedulingTaskTaskHeadroom:
    def __init__(
        self,
        *,
        num_of_units: jsii.Number,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#num_of_units OceanAwsLaunchSpec#num_of_units}.
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#cpu_per_unit OceanAwsLaunchSpec#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#gpu_per_unit OceanAwsLaunchSpec#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#memory_per_unit OceanAwsLaunchSpec#memory_per_unit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5ce9768813e3d37b24568381bbbdb8a8600aaa5ced4cd230eceb8ff6f424abf)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#num_of_units OceanAwsLaunchSpec#num_of_units}.'''
        result = self._values.get("num_of_units")
        assert result is not None, "Required property 'num_of_units' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#cpu_per_unit OceanAwsLaunchSpec#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#gpu_per_unit OceanAwsLaunchSpec#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#memory_per_unit OceanAwsLaunchSpec#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecSchedulingTaskTaskHeadroom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecSchedulingTaskTaskHeadroomList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingTaskTaskHeadroomList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb976736cc4e95b8bd522ab5dcc00350a2793630dcac099694a140f6d2a50537)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecSchedulingTaskTaskHeadroomOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8e557fef5b770bac6e5d1fd987b1972fe7ffae44622e317e8c51603418f8c8d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecSchedulingTaskTaskHeadroomOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e385ea6c80c210fc6b0b8e1b96ff97b0d09994ba7e7b7177c9e84c27d6a3626)
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
            type_hints = typing.get_type_hints(_typecheckingstub__86323b83332beec8869188a582c58e3296955ca2635a171ac6328f0ee8b168d0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6f87302de4b7f53147268136c90c55e2a5d77fa308361a2ee5e3e7fd3fb1ae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__650f420d336f8f003802109350cdbdbbd70a1c4168b6c5aac1be92ca5c3e7ce3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecSchedulingTaskTaskHeadroomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecSchedulingTaskTaskHeadroomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb325328c972a91e3dbcf3846115fd4bdd1dd82d2246d08b50a3a99ecf18d956)
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
            type_hints = typing.get_type_hints(_typecheckingstub__13c707d2bf91a572e301b7945a22ecb66f3f8a85833f6fe7aa1c227423f8a19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8967490ea94aa5381083ed44b9b4cdef7180a9de8dad5f32521784fadf06fc4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__572aa9fd2aa70b54f75d27a905967dec9d62539ef01f6083ed0e25620324b94f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409abfa653e9412346f75acfe2c96e12c9c83ee99b1127a8e7e944d1bcbf7fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b65d75b62ee5a920270dcf66e94e5b5d244a40b0b9f5389aa914cae0a2b7d57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStartupTaints",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class OceanAwsLaunchSpecStartupTaints:
    def __init__(
        self,
        *,
        effect: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param effect: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#effect OceanAwsLaunchSpec#effect}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__804544686b0212c51f61719537905099fd1c9258465eb106807eb67364a4f636)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#effect OceanAwsLaunchSpec#effect}.'''
        result = self._values.get("effect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecStartupTaints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecStartupTaintsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStartupTaintsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c5eb39d2c771881ff8c97d07f64b7d35261ca295167f79346c01dc69d6cc97e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanAwsLaunchSpecStartupTaintsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce8abfe29ce91402a9ca62805a6453b9ac04e7bf291e68ccfd048cbfbe982428)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecStartupTaintsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d55ae89ec25d7526eda6bb1c4c81fd17620adaad2a0f13d1c1c67d3a1c41758f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6ac644f581d43077f57130857e711c04e9eca69ac403a4e1f01e78915c74399)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9200bca91ff64043d50d7bfe8bf67a56b7b8332cead3fdf97b6e9b002e567310)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStartupTaints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStartupTaints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStartupTaints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef7e636fd4735e694e2ff94b6697014b9b46ae4d507f345f8108128d845c2e90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecStartupTaintsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStartupTaintsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69d09c16201e3bccce679e6ac872f62bab20b1ced67091bd22ee9b6f980f705c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c71d5e7c290109b597e2768eb8fecec1b85e802b4b846a3b27e64fe92bb764d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b2dd296cb8c268f51b0d9a9fef51b5b10e9742eff88a31011abbacb67b0ef2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1683c2fe0e99e19b863c50f00348bc5270bb6c14257a52cdd479369b1ac9a78f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStartupTaints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStartupTaints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStartupTaints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c8ff85c4a87e4f770e13fcbdc61a666b147eb138181934bb0576c3a1907f237)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStrategy",
    jsii_struct_bases=[],
    name_mapping={
        "draining_timeout": "drainingTimeout",
        "orientation": "orientation",
        "spot_percentage": "spotPercentage",
        "utilize_commitments": "utilizeCommitments",
        "utilize_reserved_instances": "utilizeReservedInstances",
    },
)
class OceanAwsLaunchSpecStrategy:
    def __init__(
        self,
        *,
        draining_timeout: typing.Optional[jsii.Number] = None,
        orientation: typing.Optional[typing.Union["OceanAwsLaunchSpecStrategyOrientation", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_percentage: typing.Optional[jsii.Number] = None,
        utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        utilize_reserved_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#draining_timeout OceanAwsLaunchSpec#draining_timeout}.
        :param orientation: orientation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#orientation OceanAwsLaunchSpec#orientation}
        :param spot_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#spot_percentage OceanAwsLaunchSpec#spot_percentage}.
        :param utilize_commitments: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#utilize_commitments OceanAwsLaunchSpec#utilize_commitments}.
        :param utilize_reserved_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#utilize_reserved_instances OceanAwsLaunchSpec#utilize_reserved_instances}.
        '''
        if isinstance(orientation, dict):
            orientation = OceanAwsLaunchSpecStrategyOrientation(**orientation)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e426c17f6a5172528757217c705f9025e0609af797d17045b88d1f9ce21e264)
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument orientation", value=orientation, expected_type=type_hints["orientation"])
            check_type(argname="argument spot_percentage", value=spot_percentage, expected_type=type_hints["spot_percentage"])
            check_type(argname="argument utilize_commitments", value=utilize_commitments, expected_type=type_hints["utilize_commitments"])
            check_type(argname="argument utilize_reserved_instances", value=utilize_reserved_instances, expected_type=type_hints["utilize_reserved_instances"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if orientation is not None:
            self._values["orientation"] = orientation
        if spot_percentage is not None:
            self._values["spot_percentage"] = spot_percentage
        if utilize_commitments is not None:
            self._values["utilize_commitments"] = utilize_commitments
        if utilize_reserved_instances is not None:
            self._values["utilize_reserved_instances"] = utilize_reserved_instances

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#draining_timeout OceanAwsLaunchSpec#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def orientation(self) -> typing.Optional["OceanAwsLaunchSpecStrategyOrientation"]:
        '''orientation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#orientation OceanAwsLaunchSpec#orientation}
        '''
        result = self._values.get("orientation")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecStrategyOrientation"], result)

    @builtins.property
    def spot_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#spot_percentage OceanAwsLaunchSpec#spot_percentage}.'''
        result = self._values.get("spot_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def utilize_commitments(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#utilize_commitments OceanAwsLaunchSpec#utilize_commitments}.'''
        result = self._values.get("utilize_commitments")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def utilize_reserved_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#utilize_reserved_instances OceanAwsLaunchSpec#utilize_reserved_instances}.'''
        result = self._values.get("utilize_reserved_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecStrategyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStrategyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5cce69012664b78e54e51510cf968cc53522993a377f41f67c1f2dee028a9169)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAwsLaunchSpecStrategyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cbb9131cef8c8836d86a23fb880d9be9c63a661c5f75c6347e1482b7cd8ca4e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecStrategyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c3755bfc8a5f9865bd4402fb292e651b8de945efa4d1adaa358c4bb3fee3b65)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56779abf2602d9ec8247d191d9558bc013fe26f5783eaae82ff35b82c6079b11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c58e699a6499c3cfea35ab4acf96c7eda1a2a551935fd04d438f53175a9393e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStrategy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStrategy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStrategy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2e94b7b480c5e42c84bd6e046e950542575c0a57229396014b69c453a04145a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStrategyOrientation",
    jsii_struct_bases=[],
    name_mapping={"availability_vs_cost": "availabilityVsCost"},
)
class OceanAwsLaunchSpecStrategyOrientation:
    def __init__(
        self,
        *,
        availability_vs_cost: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability_vs_cost: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#availability_vs_cost OceanAwsLaunchSpec#availability_vs_cost}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ceb8564baa7f52257213012fa241dd8998a450afb8c0ce2ad6a4929f1536508)
            check_type(argname="argument availability_vs_cost", value=availability_vs_cost, expected_type=type_hints["availability_vs_cost"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if availability_vs_cost is not None:
            self._values["availability_vs_cost"] = availability_vs_cost

    @builtins.property
    def availability_vs_cost(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#availability_vs_cost OceanAwsLaunchSpec#availability_vs_cost}.'''
        result = self._values.get("availability_vs_cost")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecStrategyOrientation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecStrategyOrientationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStrategyOrientationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ddde66fc97c64c7b855c34f4376db9003465655069b4115bebe657d29f555cc4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAvailabilityVsCost")
    def reset_availability_vs_cost(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityVsCost", []))

    @builtins.property
    @jsii.member(jsii_name="availabilityVsCostInput")
    def availability_vs_cost_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityVsCostInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityVsCost")
    def availability_vs_cost(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityVsCost"))

    @availability_vs_cost.setter
    def availability_vs_cost(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7069dd889e4a658fc5439032c46f703ebaadf837f1c24b093d05137b74883af2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityVsCost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAwsLaunchSpecStrategyOrientation]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecStrategyOrientation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecStrategyOrientation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7f28219e26e5aba129fafa46b5a7f70adeadb267b3f4c65f93b4f70db94e6b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__484f3b03679f1e91013819f03617ec779fe2efa42bb3f13b7619e3cdc92f5a4e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putOrientation")
    def put_orientation(
        self,
        *,
        availability_vs_cost: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability_vs_cost: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#availability_vs_cost OceanAwsLaunchSpec#availability_vs_cost}.
        '''
        value = OceanAwsLaunchSpecStrategyOrientation(
            availability_vs_cost=availability_vs_cost
        )

        return typing.cast(None, jsii.invoke(self, "putOrientation", [value]))

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetOrientation")
    def reset_orientation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrientation", []))

    @jsii.member(jsii_name="resetSpotPercentage")
    def reset_spot_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotPercentage", []))

    @jsii.member(jsii_name="resetUtilizeCommitments")
    def reset_utilize_commitments(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUtilizeCommitments", []))

    @jsii.member(jsii_name="resetUtilizeReservedInstances")
    def reset_utilize_reserved_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUtilizeReservedInstances", []))

    @builtins.property
    @jsii.member(jsii_name="orientation")
    def orientation(self) -> OceanAwsLaunchSpecStrategyOrientationOutputReference:
        return typing.cast(OceanAwsLaunchSpecStrategyOrientationOutputReference, jsii.get(self, "orientation"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="orientationInput")
    def orientation_input(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecStrategyOrientation]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecStrategyOrientation], jsii.get(self, "orientationInput"))

    @builtins.property
    @jsii.member(jsii_name="spotPercentageInput")
    def spot_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "spotPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="utilizeCommitmentsInput")
    def utilize_commitments_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "utilizeCommitmentsInput"))

    @builtins.property
    @jsii.member(jsii_name="utilizeReservedInstancesInput")
    def utilize_reserved_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "utilizeReservedInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25eea886d57964df020f49181033b42827b6e3a9588d0b2481bdb66d0cabbe8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainingTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotPercentage")
    def spot_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "spotPercentage"))

    @spot_percentage.setter
    def spot_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69fa3537de6fc77cdd684dc51bd0e7403f98a39dd12d8391dd35cb7a4c2cb236)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="utilizeCommitments")
    def utilize_commitments(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "utilizeCommitments"))

    @utilize_commitments.setter
    def utilize_commitments(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4181fee630cfd241de6cbc7750bd3089495ce6029cc9ac54f71cc0cdd394365c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utilizeCommitments", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__01a8db14c851b23591bb81050bbdae8e98fe33a31bbb16e81c0ef9bcc1fa030e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "utilizeReservedInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStrategy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStrategy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8303de481bb3a6906e3f97dfa10fe0a692449df259bd83ea8a73b3e52bae36d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class OceanAwsLaunchSpecTags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c970069e174984575df43f08cee5602fbfac6445c07f88f25a0ca2a4bde5fd0b)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1eec154e70bf1427f1858631a3d7ac0b5ccebe8b9ef7b94f1b44ac7b6d47b793)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAwsLaunchSpecTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8f2a20424ac7ffa68fd5f2b53307eb80d533639ed464e5edd67c9c59799135a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4419bef82d5d79dece0bdeeaa05082a4353db3cad52f2e806f61cc3014e3a467)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e25697ad9f69b2c8d78cbdadfa5ebcdfc19199794b7d77f9556fc569a1b0ed00)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7d667f007d84ed965fadb5965b2bfc59f5e1863aabaa17cdaff43a23eb47fd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1ebeaf413e794627ad5730f07dc5c608fedc0d63a9e1d2a0252ccedf8f53685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e4a147bbe69e7142d82f39874056fd31960a5ca3af8672ce68fa77a5252c420)
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
            type_hints = typing.get_type_hints(_typecheckingstub__99660fabaff561ddd142f75417218fab2692efe010c682fd335199e545b801ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__654b08cef16b953c146c3ffcd08b9a3c385774eba371afda7a03c7d2e2897ef2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51e15a42e75351a7ef21e50ffb70c3054fa96e0fe2852f11cda61f7da55c8e58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecTaints",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class OceanAwsLaunchSpecTaints:
    def __init__(
        self,
        *,
        effect: builtins.str,
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param effect: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#effect OceanAwsLaunchSpec#effect}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff47a4f214315017a21d83778270eabc3ebf4e8eed12187fe23ad5d00d0a8c6b)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#effect OceanAwsLaunchSpec#effect}.'''
        result = self._values.get("effect")
        assert result is not None, "Required property 'effect' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#key OceanAwsLaunchSpec#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#value OceanAwsLaunchSpec#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecTaints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecTaintsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecTaintsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4d4bb5e805ebafb2f7181d051cb366dd33df749877f0d4ef2c4b272d67466c6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanAwsLaunchSpecTaintsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d97d0c7f152af6b867b1c586ace43cf61786d6075244650df7dd8fda29af22)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanAwsLaunchSpecTaintsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02044930b5fb817421e47fa8fc33e0a5a296d871d4c64f29af1cdf2d24134957)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6d90048cda95164094bf06505d9c863ed6f9c379189c0ac4fa698d7e185f489)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b991c4f49172a6644b65c6f9ebb3a604a7e830d56665aafb9442a1be2584518d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTaints]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTaints]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTaints]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a8e9cef03053be45f5bd8c5805bfcc697b1798c495c2c20889e9a97229b3c4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanAwsLaunchSpecTaintsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecTaintsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07908364fe368e4d68eae55b76b4ed91a53e6eca6f891f0462158ca0d66fa4f9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__195029f8c47cdceac2fe6894240f71f5bea6469d76e804f6a0c24d0c5e0cf994)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effect", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34d807039bcee80b3d374c6d8707fd5e4a34006850a5eef4710e0719e9d3644c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c886c7a83d71839dca5c9c84edcfc41aacf164088a61494ff3c47a2934fabbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTaints]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTaints]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTaints]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__617827d9d59bbaafa8291c660567d2c94e96326f04ddaafa6fbf14172e2b017c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecUpdatePolicy",
    jsii_struct_bases=[],
    name_mapping={"should_roll": "shouldRoll", "roll_config": "rollConfig"},
)
class OceanAwsLaunchSpecUpdatePolicy:
    def __init__(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        roll_config: typing.Optional[typing.Union["OceanAwsLaunchSpecUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#should_roll OceanAwsLaunchSpec#should_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#roll_config OceanAwsLaunchSpec#roll_config}
        '''
        if isinstance(roll_config, dict):
            roll_config = OceanAwsLaunchSpecUpdatePolicyRollConfig(**roll_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e0f75484b1245857e21a5cd98968984c9185c4c7edaf2d939f568b8964fed70)
            check_type(argname="argument should_roll", value=should_roll, expected_type=type_hints["should_roll"])
            check_type(argname="argument roll_config", value=roll_config, expected_type=type_hints["roll_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "should_roll": should_roll,
        }
        if roll_config is not None:
            self._values["roll_config"] = roll_config

    @builtins.property
    def should_roll(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#should_roll OceanAwsLaunchSpec#should_roll}.'''
        result = self._values.get("should_roll")
        assert result is not None, "Required property 'should_roll' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def roll_config(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecUpdatePolicyRollConfig"]:
        '''roll_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#roll_config OceanAwsLaunchSpec#roll_config}
        '''
        result = self._values.get("roll_config")
        return typing.cast(typing.Optional["OceanAwsLaunchSpecUpdatePolicyRollConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecUpdatePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecUpdatePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecUpdatePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7df825503d40546f714492be6c8682e7748320637f857ee09d6a3c2300944f15)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRollConfig")
    def put_roll_config(
        self,
        *,
        batch_size_percentage: jsii.Number,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#batch_size_percentage OceanAwsLaunchSpec#batch_size_percentage}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#respect_pdb OceanAwsLaunchSpec#respect_pdb}.
        '''
        value = OceanAwsLaunchSpecUpdatePolicyRollConfig(
            batch_size_percentage=batch_size_percentage, respect_pdb=respect_pdb
        )

        return typing.cast(None, jsii.invoke(self, "putRollConfig", [value]))

    @jsii.member(jsii_name="resetRollConfig")
    def reset_roll_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollConfig", []))

    @builtins.property
    @jsii.member(jsii_name="rollConfig")
    def roll_config(self) -> "OceanAwsLaunchSpecUpdatePolicyRollConfigOutputReference":
        return typing.cast("OceanAwsLaunchSpecUpdatePolicyRollConfigOutputReference", jsii.get(self, "rollConfig"))

    @builtins.property
    @jsii.member(jsii_name="rollConfigInput")
    def roll_config_input(
        self,
    ) -> typing.Optional["OceanAwsLaunchSpecUpdatePolicyRollConfig"]:
        return typing.cast(typing.Optional["OceanAwsLaunchSpecUpdatePolicyRollConfig"], jsii.get(self, "rollConfigInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__0644bd046398fb54d159d8a850cd84d4cfc6a438335cf52e460846ca8ce217ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanAwsLaunchSpecUpdatePolicy]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecUpdatePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecUpdatePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df65f5e31452f1bfd5b52f02407fc3dbfdf8361e51263662129ce607322e3687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecUpdatePolicyRollConfig",
    jsii_struct_bases=[],
    name_mapping={
        "batch_size_percentage": "batchSizePercentage",
        "respect_pdb": "respectPdb",
    },
)
class OceanAwsLaunchSpecUpdatePolicyRollConfig:
    def __init__(
        self,
        *,
        batch_size_percentage: jsii.Number,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#batch_size_percentage OceanAwsLaunchSpec#batch_size_percentage}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#respect_pdb OceanAwsLaunchSpec#respect_pdb}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c988807ba40abf0dd2b50663823c768e849efeec61b94b5d33a2beb2aa7ad7c4)
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument respect_pdb", value=respect_pdb, expected_type=type_hints["respect_pdb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "batch_size_percentage": batch_size_percentage,
        }
        if respect_pdb is not None:
            self._values["respect_pdb"] = respect_pdb

    @builtins.property
    def batch_size_percentage(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#batch_size_percentage OceanAwsLaunchSpec#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        assert result is not None, "Required property 'batch_size_percentage' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_aws_launch_spec#respect_pdb OceanAwsLaunchSpec#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanAwsLaunchSpecUpdatePolicyRollConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanAwsLaunchSpecUpdatePolicyRollConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanAwsLaunchSpec.OceanAwsLaunchSpecUpdatePolicyRollConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d8fc179042d3c2d00059908763831203c61ed59a763df8f4d9bf40d77dc234e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRespectPdb")
    def reset_respect_pdb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectPdb", []))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="respectPdbInput")
    def respect_pdb_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectPdbInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b062361e626f263b2b9835e2bd6278d7534e50a9c6d581ad70012aa53f28b95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__3be9dd6232d9484919c42f766ab442229aeb4ec87b2dc24386b5e828ba211fc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectPdb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanAwsLaunchSpecUpdatePolicyRollConfig]:
        return typing.cast(typing.Optional[OceanAwsLaunchSpecUpdatePolicyRollConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanAwsLaunchSpecUpdatePolicyRollConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e0aabf2ae1acd30ca78ab2000f81eeca8afb7063d4deeca90cfd15a163d7815)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanAwsLaunchSpec",
    "OceanAwsLaunchSpecAutoscaleDown",
    "OceanAwsLaunchSpecAutoscaleDownList",
    "OceanAwsLaunchSpecAutoscaleDownOutputReference",
    "OceanAwsLaunchSpecAutoscaleHeadrooms",
    "OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic",
    "OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticList",
    "OceanAwsLaunchSpecAutoscaleHeadroomsAutomaticOutputReference",
    "OceanAwsLaunchSpecAutoscaleHeadroomsList",
    "OceanAwsLaunchSpecAutoscaleHeadroomsOutputReference",
    "OceanAwsLaunchSpecBlockDeviceMappings",
    "OceanAwsLaunchSpecBlockDeviceMappingsEbs",
    "OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize",
    "OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSizeOutputReference",
    "OceanAwsLaunchSpecBlockDeviceMappingsEbsOutputReference",
    "OceanAwsLaunchSpecBlockDeviceMappingsList",
    "OceanAwsLaunchSpecBlockDeviceMappingsOutputReference",
    "OceanAwsLaunchSpecConfig",
    "OceanAwsLaunchSpecCreateOptions",
    "OceanAwsLaunchSpecCreateOptionsOutputReference",
    "OceanAwsLaunchSpecDeleteOptions",
    "OceanAwsLaunchSpecDeleteOptionsOutputReference",
    "OceanAwsLaunchSpecElasticIpPool",
    "OceanAwsLaunchSpecElasticIpPoolList",
    "OceanAwsLaunchSpecElasticIpPoolOutputReference",
    "OceanAwsLaunchSpecElasticIpPoolTagSelector",
    "OceanAwsLaunchSpecElasticIpPoolTagSelectorOutputReference",
    "OceanAwsLaunchSpecEphemeralStorage",
    "OceanAwsLaunchSpecEphemeralStorageList",
    "OceanAwsLaunchSpecEphemeralStorageOutputReference",
    "OceanAwsLaunchSpecImages",
    "OceanAwsLaunchSpecImagesList",
    "OceanAwsLaunchSpecImagesOutputReference",
    "OceanAwsLaunchSpecInstanceMetadataOptions",
    "OceanAwsLaunchSpecInstanceMetadataOptionsOutputReference",
    "OceanAwsLaunchSpecInstanceStorePolicy",
    "OceanAwsLaunchSpecInstanceStorePolicyOutputReference",
    "OceanAwsLaunchSpecInstanceTypesFilters",
    "OceanAwsLaunchSpecInstanceTypesFiltersOutputReference",
    "OceanAwsLaunchSpecLabels",
    "OceanAwsLaunchSpecLabelsList",
    "OceanAwsLaunchSpecLabelsOutputReference",
    "OceanAwsLaunchSpecResourceLimits",
    "OceanAwsLaunchSpecResourceLimitsList",
    "OceanAwsLaunchSpecResourceLimitsOutputReference",
    "OceanAwsLaunchSpecSchedulingShutdownHours",
    "OceanAwsLaunchSpecSchedulingShutdownHoursOutputReference",
    "OceanAwsLaunchSpecSchedulingTask",
    "OceanAwsLaunchSpecSchedulingTaskList",
    "OceanAwsLaunchSpecSchedulingTaskOutputReference",
    "OceanAwsLaunchSpecSchedulingTaskTaskHeadroom",
    "OceanAwsLaunchSpecSchedulingTaskTaskHeadroomList",
    "OceanAwsLaunchSpecSchedulingTaskTaskHeadroomOutputReference",
    "OceanAwsLaunchSpecStartupTaints",
    "OceanAwsLaunchSpecStartupTaintsList",
    "OceanAwsLaunchSpecStartupTaintsOutputReference",
    "OceanAwsLaunchSpecStrategy",
    "OceanAwsLaunchSpecStrategyList",
    "OceanAwsLaunchSpecStrategyOrientation",
    "OceanAwsLaunchSpecStrategyOrientationOutputReference",
    "OceanAwsLaunchSpecStrategyOutputReference",
    "OceanAwsLaunchSpecTags",
    "OceanAwsLaunchSpecTagsList",
    "OceanAwsLaunchSpecTagsOutputReference",
    "OceanAwsLaunchSpecTaints",
    "OceanAwsLaunchSpecTaintsList",
    "OceanAwsLaunchSpecTaintsOutputReference",
    "OceanAwsLaunchSpecUpdatePolicy",
    "OceanAwsLaunchSpecUpdatePolicyOutputReference",
    "OceanAwsLaunchSpecUpdatePolicyRollConfig",
    "OceanAwsLaunchSpecUpdatePolicyRollConfigOutputReference",
]

publication.publish()

def _typecheckingstub__5f32d702f716a2f5dff9548e1a3816b17b946225f283f7101fd3a2a28bce1f23(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    ocean_id: builtins.str,
    associate_public_ip_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autoscale_down: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleDown, typing.Dict[builtins.str, typing.Any]]]]] = None,
    autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]]] = None,
    block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    create_options: typing.Optional[typing.Union[OceanAwsLaunchSpecCreateOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    delete_options: typing.Optional[typing.Union[OceanAwsLaunchSpecDeleteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    elastic_ip_pool: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecElasticIpPool, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ephemeral_storage: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecEphemeralStorage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    iam_instance_profile: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    image_id: typing.Optional[builtins.str] = None,
    images: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecImages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_metadata_options: typing.Optional[typing.Union[OceanAwsLaunchSpecInstanceMetadataOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_store_policy: typing.Optional[typing.Union[OceanAwsLaunchSpecInstanceStorePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    instance_types_filters: typing.Optional[typing.Union[OceanAwsLaunchSpecInstanceTypesFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    preferred_od_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    preferred_spot_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    reserved_enis: typing.Optional[jsii.Number] = None,
    resource_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecResourceLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
    scheduling_shutdown_hours: typing.Optional[typing.Union[OceanAwsLaunchSpecSchedulingShutdownHours, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecSchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    startup_taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecStartupTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanAwsLaunchSpecUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    user_data: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__9ffb1d01bbf92ea2acb22ba4e50de8ae92fa97ed8a2131322e03e07fb720acc9(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c4a9adad79cf8bf8a3aed756fb98fc876d0b439de8d565ce4b2ae91029d09a0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleDown, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2eb35f9d318918ef62982e46870a180e6b86952c56fbedc22bd15696e54262f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a321f91d35e6eabe432037291c1923d3ad1bbe56fc7fbc8c7ec6d46d17654707(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56ec253792a01e9bcc397d21ed23fdd3e28c56e321872edb062245802a43d460(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__005b836f7f8079d42fd4c8afe58efa9bdcf6b59a6353f436e012d4dc8c358e45(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecElasticIpPool, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1268598b29d39f92c52479f978fe32c79c222f8064221d34c1cfbad568bbd921(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecEphemeralStorage, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ef59d89a96856d7619f9573fe6903cb6c656dce5c68eb9bb445fa8cea6b00ce(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecImages, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd52c19488371732a8e287f040bf6e7e78c648ccc201d4317ddf639a8a4a3e58(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6fe67483f81ff5c53da9d701848e429ce132407300223ce7c70be7ee4e69bc3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecResourceLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a5255d8a7c562990f2a0511eccc8ee4faff8b297c567040edc59fbeb3f8d567(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecSchedulingTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b549d52142f5386077ea053fe312cb800d9a1c16fb1975b7cb74541ba8faee4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecStartupTaints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba55e44db0b61ebdff3a75a3f0dcd897e564e0ccd8c9813d5910bcb8f822429e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecStrategy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b1034add65eac94422ad211039f4b5772713896227bcab79deea86dd1d0ab7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d980b3db4ad0b5a979ba99070063d524eaa6f0be444136c99963ff1e6adc4d72(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecTaints, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c5cc4576388a49f924ba6d183ab02ab6ae44f8d4cbc6fa54d0dbea3dae652c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb3db31e636a77d017cf37ec506c7c32e82df9b6201f46c917d1e0f7700f0489(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a69051fd18930c5d831db01e8424712c15faa1bd94f1a0e220304299bfa3be1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a73276661b0b20f0b014a4599232fc533b0b7130f59ff13e4bbcfb44b69641d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5235fba41453ec8f4ced5096e23ec94e16e72dbd449c36b7f190d1478600bee7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcabc90032713eb4d62e55d366f609a7a3b0f01be091287cfcd50133ae8d0252(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c7cb551a46240fe335a48d425fbac4a3693f9acada5612229fd7de1cf4cd9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8e19215e5038c8c4dd9900840282e6c2e062eae46db69f47bc7961d7e6b6e04(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b59a674534fe5aa7e4f8d1cf1e5cbb1ef58eb7840a105f909627e9862d84c6c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04f1e6f07b7d88c56bfd948475987367df4d440e9d1bd6d85dfa4eda900db455(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d33b1779883d296245af84965c4bd5c62360f54c8849330f8a8cbd41fc0143b5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d43888e6487dfebd56a5258dc18adcc383d26e37356aa6de5833c78e73bd360f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8827a694d0fac88474c53936c91f3bab007163d9f90e625d58c8da86b6991ddc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__197277b6d27ac6ed1d3cd2c86b4097a7bd7c8acd83dde5e43b8e03d3ad7d3b3c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dee50480cfe57e4807ce24cc39da55b7cfb5bf2c9192d7b958e8309914ef625f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ecf59a370015d46d98dc518167891f4d473473b7cc3539e0db8158bd51c5110(
    *,
    max_scale_down_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b440c85a8293255b6101a39d42c18eeff4bb7bda2123da1ebd739e726d228fcb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efe9b2a4685a77908622b70a0b2fbe72060b90b101615168d796a606e6c7f73(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84f968c8bd3ca231a349ac69d260582adffa072630eff3605fa607c7b7cbf2a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc2663b84b032090a3d7ec819710745eed2a3ab83009d93abcf47dc2355f06cd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2bd9bbaf901b9b6f7cd76951c68419633a1332be46e56dad5137c6a6718a301(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f3bd1e2c597a9ace21945c11f092a4728611cc3a2ce9ee2d1b8959b8119bc4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleDown]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc82eb769945cf27ae7d0a91dca72dfc0972d06ba1651c912ae8cadd65c9aca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794e30357086cc1ea487e4131fd090b20e893dbbb4198cfc9e4e2472e1b8afed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ddfa505fa3c0dac18f25e6c5ec3d2971e741bcc1278b9e3495b24f178955102(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleDown]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05a33c9ca5e8a3868d21439a4216439f821d9445d77fc63e40fb98aa40eec877(
    *,
    num_of_units: jsii.Number,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a58d0ff61a1d4abff3d7099d0d9700a409150a3c56b226f88dba0c4bd8f2263(
    *,
    auto_headroom_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f54d4ea5d13742bd558b11a78c2d4b33ce14ecee7431383fa6d19594afeb7ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8ae2e45ad0f3fa4bf5e07388b6c78f9800c372db506ca2c3ea03e8a51215ab5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d317c72c0c643fac416febd837bf6a844646cea9590e65d6b1e364f90959ab9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfb1ce78e77ad56611585d88f01bc7d6f91bc48a258675b514ddd3eb32b61f97(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66d242abbb4cd2559d6dc5bd4840abb91fefbef61ba75568e7bd4285751f8059(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d226c08dc1809d7b5cd90d32db3ae056c28293e4d4db4452e3b52c49053b0f90(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac58cc06667e66440228ce3a823809b3dc96c35a785c3b3c30a110fada57d274(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae034a3a125fa20f3e2155e4c7fee4c8abafdc33f85d677f3cc4fccc7a039bb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b645594ef9caf97e60469bfa06eae49694d18b2b4beecaf85a2772a188e8061a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ada662d29da9e8084232e7d7969b5b414213e19aaedc0e78416cc37b4ac9921(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22ec821188607539d89264131bc10bb79fcbd04f567da9663f81541f43c3057e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84988915683e154b058ec29001f2e58529c998bd760108d052121997485b3399(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__578b37254801eeeb0fd9d6d3b3a2198481c7540c2917359ca98b4ddd360c1bee(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceaa570fd9d8d1326a85f3331c3d7dfb88912a7ebd8c984f731b29e0b72687e6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bea01102db3d8d2f69329fb42ffb7d91b5af4dc139806d82fa1c8187e9b928d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecAutoscaleHeadrooms]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28478e53384f7764e0b62551934683c010c8dbbd7192ba0fbad995d7c049eeeb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bbccdb3e5f6f940d0922e66a0414ded5544e25ec3ec2fa07c879b972712ea79(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76a2fa6fdffe57cb960ff52b054bc488f864565154e13915edf1e5e7c436ec54(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7728df7d455e198394467c1efc22c19e3bca07f07dac8add1d7b67915aab7261(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a42fa2b6068d10cbbd4a8bee021a4cd27ee8f658ece50a05927c8fff9909e0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58f760681abb204b04823e8b4ed815661e2545beac9b437defc3e8a75a4bf346(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecAutoscaleHeadrooms]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d968a7e52ea3dc07c70e971c88b9e6de0e04403d869cd1f6d577a0eabd752cc7(
    *,
    device_name: typing.Optional[builtins.str] = None,
    ebs: typing.Optional[typing.Union[OceanAwsLaunchSpecBlockDeviceMappingsEbs, typing.Dict[builtins.str, typing.Any]]] = None,
    no_device: typing.Optional[builtins.str] = None,
    virtual_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c99cba1ddfbbbf2bd63e11c43861e7323380e4d54a7402351a1169ec2313265e(
    *,
    delete_on_termination: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dynamic_volume_size: typing.Optional[typing.Union[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__2674bc182e3263cad712c50bbe4c5a7dba451a1eb58f5fd55dea394a1e998ba9(
    *,
    base_size: jsii.Number,
    resource: builtins.str,
    size_per_resource_unit: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8125d70995719f5d880ddfe4e560998382576dfa24e62a3edee712453258cbb7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080f0c29e4b822e9b986ef66d227b9aa0b351536192b1347528808faf3da96db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb92f49ce976151713ccfba02b5fdf37608c5b4e163da54be8b4175e9267631b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f32f9351cd6e921760afacdae9d43e701203be01ba0724ceb750bbb0d3ae62bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33a34c7099c89674e7cc216c33ea54c835e83d2dd9105d2a204ac2700bfeb785(
    value: typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbsDynamicVolumeSize],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e620a899dc51852248ccf388a5e82cf521c26e9959b291c885b003879fa936e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__613e7a2d66f34e38844d60d0378f8e6fe982d07e49a88736e2911852c0d2ac1c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20c4e6d82a1c418b581ad783e12d2f57d3f67f04e70d7789d109bb946283454a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f01ce1f02ff72c7ea4dd17528c9f72434b4fc194261cfde0b769cc6661a2b634(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a8d2060620499127fbb5787379400730d95b6d17d58a2c5560094c82e80cbfd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf57e91da3ee86dffeca7e4d2df681289e5ed5828737ea7f94e7c091e4321970(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a80c0ea7262d6516e8a12f0b6526ca86ff55f70faa7bae44527a9abba93df8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__488ec29ec7cdbda2eba3bef872c21573c5b823cb96eb4ab3da58586868b83f1e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb887efc37371c308d708653670329711f0b35bd2a8011bd3bb90c570673ea06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8927785a5efd97e0cf5fc7f8fdcda2e5254c67c66aee6b7e728b7f9eda4d223a(
    value: typing.Optional[OceanAwsLaunchSpecBlockDeviceMappingsEbs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e3fa0d506a78905c7e96d214525692e0d7556233cb6d103b322332e875eb4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d89de593eb6e6046db3fb5dea8ba24419b0862edfa27b73fb7c909f6d640c8bf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9f392be673243566442e2ecddddea6ca03bf482a319d77d9fafc06513f3bc79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f536404b5db0cb06eb97f9ab653728fdb7e857fa819a924a484a1ba7fd8d2dba(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c03e77359ddca01cd9a17865eadb33f569ed81829969ce4bbf1ac003e12c92ba(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1084c45dd76a261967a1a8a9d387d3d633b98fa4718bf815c1afa1f90425be96(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecBlockDeviceMappings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3016c38b1709cd274fbb5fadf0a63029bf97afb4e0830915b3c6f59e8f8bef68(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f192f441aee8af0861802722c597b684f92d4df51bee9d226e88eb9657c596(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0083af98c48029e3e9db79ecfcf75e5e4f384584cda6a9555be4d80444c61540(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__599ce4113b85f8e84c90ae4da6390180867d7530dcbe9aeb0d70a9214e398741(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b77274f555fc55cdb4dbdcf7a05e79bac55006e476046d2e2e083270f65ac23a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecBlockDeviceMappings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eaa32f152ce09727f2c482e16e44d0e2037a182bf83bfc89b20148ea3301f89(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ocean_id: builtins.str,
    associate_public_ip_address: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    autoscale_down: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleDown, typing.Dict[builtins.str, typing.Any]]]]] = None,
    autoscale_headrooms: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadrooms, typing.Dict[builtins.str, typing.Any]]]]] = None,
    autoscale_headrooms_automatic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecAutoscaleHeadroomsAutomatic, typing.Dict[builtins.str, typing.Any]]]]] = None,
    block_device_mappings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecBlockDeviceMappings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    create_options: typing.Optional[typing.Union[OceanAwsLaunchSpecCreateOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    delete_options: typing.Optional[typing.Union[OceanAwsLaunchSpecDeleteOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    elastic_ip_pool: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecElasticIpPool, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ephemeral_storage: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecEphemeralStorage, typing.Dict[builtins.str, typing.Any]]]]] = None,
    iam_instance_profile: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    image_id: typing.Optional[builtins.str] = None,
    images: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecImages, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_metadata_options: typing.Optional[typing.Union[OceanAwsLaunchSpecInstanceMetadataOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_store_policy: typing.Optional[typing.Union[OceanAwsLaunchSpecInstanceStorePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    instance_types_filters: typing.Optional[typing.Union[OceanAwsLaunchSpecInstanceTypesFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    preferred_od_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    preferred_spot_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    reserved_enis: typing.Optional[jsii.Number] = None,
    resource_limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecResourceLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    restrict_scale_down: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
    scheduling_shutdown_hours: typing.Optional[typing.Union[OceanAwsLaunchSpecSchedulingShutdownHours, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduling_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecSchedulingTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    startup_taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecStartupTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    taints: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecTaints, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanAwsLaunchSpecUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    user_data: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc16252590c8f664b327a4827f03d3fc5bedb4eb886368a2e7a72d9d77e76173(
    *,
    initial_nodes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74d26b9ac4b542b105e32988b87431225a09387806e4192078ad687b23763323(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692fe36d67ef77ab00f24f6ca5d955b2f4cfb5d0c03a3329781bbd005ee0447b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9073d761928dac369df24609d94f2f315c31001612051aa75841af2a48bce453(
    value: typing.Optional[OceanAwsLaunchSpecCreateOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5393ebcb720bf722f6370a2bc9e1d3fbd675d27d43574ecc5b8505255fac00(
    *,
    force_delete: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    delete_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e44eca7f364d1f8f700be83bfe4bc960843d48836c5b59425985062ad5fa74(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ec898f7f570ad5eadf5d8642d592f630c80249fef11be4fd52640e175323f1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7782b9ee99a2f95ba5b21101e0ba66981f995470b673ce17c6f118c1cd8af690(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f619f45e861c9404405fdbbe4b999e7cfcb6f41649ded655592927c0e6565f6b(
    value: typing.Optional[OceanAwsLaunchSpecDeleteOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__286c1a921f484def92c6c633abdc67c3042d3c79d6ca44a4080bbdfa6aaab2fe(
    *,
    tag_selector: typing.Optional[typing.Union[OceanAwsLaunchSpecElasticIpPoolTagSelector, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3f40b603cbf5014582febef730181a1ffbadad5dcbd0a8f63a784789ed85a81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ebbd7ee8304bde1e137f4180d026de9693a1f17b302565b4bb9a490c1bfeeeb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cc61b51c4818cfeb75c5ffb15029713fe333255c52b64f793d6f9bd00f0289(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2a20ecf2f3b8a4f2385e37963534c2b2f5f064bddd7dfbfeb298abbd959f98(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e46fe05b592d457b9d9a0d7c5fd68196443d90d329a7dcdea0b413af5a3d7a37(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8908280cb901bf0019919c7bb4d995dbb17be90fe349b72d9d7180cc13bb279(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecElasticIpPool]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__898a7805bf291b17b45a70a8e144905b2b8b9c40221c0678f303e931f94cc410(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__159e3c6f503b84e8c2614b70c032096617f02f9fb3a5cad75e32a5ad1c9bc57b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecElasticIpPool]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__892441ca29f30945fac3538212a37c29c131485de7bb1c4f450dca47f64defd2(
    *,
    tag_key: builtins.str,
    tag_value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__823368a6413eca3eaa98e74b8f7cff5ac80a02609c636aa7e3f7a3c56e212466(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e53458b8981ff1cbe468c0c4d0a8b4c799c7c84d2271e20f5cf3bafed014e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a25e60d367cc7e31981f9d26aa8c3adda872171de68947c6d5f8bae840406ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c145597115d269c77cc4b93651dd5be52f666f719ac59bc4470e90438f73b98(
    value: typing.Optional[OceanAwsLaunchSpecElasticIpPoolTagSelector],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70291128d605a0e8d8721105cd0ea62ca98fa0f4622458739eccd820dc1bae1f(
    *,
    ephemeral_storage_device_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa188919f22843c3dd2be0dd5444010d6b0b7f410d47e46dcbf3101e77c1d49f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12473295db22371980b71da20baab89f01e5fef6da17a88999eb55530149227a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a8ac74f4fec78037e91e715e77c3a5a539e3c7df7797006dff57f304e27d70f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c544d0ecff63c7f89bc1b7ed95a932fda13627e6e72846a825b0d778383dc3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8165f6bab311bf37cddc54b4a9289ce109975d7c4ee91a04513b5d3d01352df3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__025c2553f5edeb6845e42f5ce46dc54774b1c3efd0b55c9ecc24d77d3f6147f5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecEphemeralStorage]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79b4683278c81a6417d1dba96574e8b268cd9a3a20e060386a9cc2c24b6fc966(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d468b0ab96684cad61532af71c3fde7d3dc56cb3c8d37957598455044662077(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95b934871961c89e62d392d1fb7fd4e9d94621a88277d07ed05839e21b3bd47c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecEphemeralStorage]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__016c3056cd3e49fa06519b875b9538ab2bb9288ecbf35dffb523ccc262a1e145(
    *,
    image_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c29e318df85b3b348497a5e0c4afc802c05ac281624c6534a053a93973c77b72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f26bb8321b885dbe265c5dd59deabeb1023c33c2ec7e136403d4aecbf328b5e2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce0744dd39ae1861620a20745c1476430222f3eeea4b3ed6dcafd4d92d15079a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__253d3287c13576b382065fd4fb44bb55cdd7e31fa0b3405de8eedd4faadf9bf8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e96ed41de1e1b781fa0f44038d8265817bc6ec0c36d25ecde09f43f8327885cd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__848e201873502ae5d85e6a0dd650683dd0ed0836edfe3c301ae9a0e5b603a4bc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecImages]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9572f4e03afce63f7220cc29a468471fc159bbec8e99167d881c5df5e9add50b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2044431a188252683f064cd0df19a86ebc914c0477606031b611bcc8292860c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea9c8c2d98b7c0e68c263b520e4883897da8275e8136fb56c64a021ab8e626e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecImages]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64a0791c2ed5e86a67fc0906fe1215f13002026cde8313aa851f85660f980a68(
    *,
    http_tokens: builtins.str,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1da963facf18d03deb295663c51dbf1a026fbb460c8b8b9e7043cb84fefa00b1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88ff0ea94d47f78bfb51f472961b91fb0d5ddac8628234579b9c109b8e4e09af(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8f2337652287ba12239219d6d1bd96924b5fa94bcb9ad956f91a87588de871(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8749191449934eab74402c5213283bb5344442b8b8488145bb889f0956fe9382(
    value: typing.Optional[OceanAwsLaunchSpecInstanceMetadataOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a33e6d64d2419ce6a6739f5dcba0bfa865c0260cf1ac8be438cf0eb73df133(
    *,
    instance_store_policy_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f659685eeb5f42219ee8a647e85081c1b2468501519d515c836d081c982c815(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aea51c7866579b77cf1ac14bc4b76ebbd9442315921e458f2b3a14fb3e2c84d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2d10b68185e3a7232df688ea69b2a624ed587ad4792b576a796153e862ff59a(
    value: typing.Optional[OceanAwsLaunchSpecInstanceStorePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e3d61cd991c3d68f49a2fa70cc0447d1475f9b3c6725c4397fa621269019fd6(
    *,
    categories: typing.Optional[typing.Sequence[builtins.str]] = None,
    disk_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    exclude_families: typing.Optional[typing.Sequence[builtins.str]] = None,
    exclude_metal: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hypervisor: typing.Optional[typing.Sequence[builtins.str]] = None,
    include_families: typing.Optional[typing.Sequence[builtins.str]] = None,
    is_ena_supported: typing.Optional[builtins.str] = None,
    max_gpu: typing.Optional[jsii.Number] = None,
    max_memory_gib: typing.Optional[jsii.Number] = None,
    max_network_performance: typing.Optional[jsii.Number] = None,
    max_vcpu: typing.Optional[jsii.Number] = None,
    min_enis: typing.Optional[jsii.Number] = None,
    min_gpu: typing.Optional[jsii.Number] = None,
    min_memory_gib: typing.Optional[jsii.Number] = None,
    min_network_performance: typing.Optional[jsii.Number] = None,
    min_vcpu: typing.Optional[jsii.Number] = None,
    root_device_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    virtualization_types: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac30592f2eab2537a1048778349802f56fbfe504dc49caa7ced64cd412442a78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ad833e1b35ebfe3c39a6b8cbc592af93432be2cd02affa2f8640508ee785ba2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d5dcbaadf188adffd1e756db1a69fe0956033288d76b44076c40e821f8b6e5e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b7ed29e1d653efa280b2b67b1362525e8dff444db9e4d696ca4603d357a3c69(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98d24588051965603c56845bf7542bc60b7bd148d24acd5ddba6edd4b6b1087(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__237801519f14c6016d914d4694e56405f10f0cae2a3c23ba68c977a3856e26bc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8731a8d104062d83eba5aaa9247c1e664f7acb60107ec9983582ca5cb2b6dc3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c141119f214a2ffc72e7c54b12ddb35265a86493f29476bd8e0479a472ff5b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e923d5795278e579d8510f87999ea7380187796ecfc6882787099a003c4a930(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69a75e3f9a4df2331236f43de4e995217a2a454e686b70de96c682b3c07fa003(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4c04e266f0a5087f4d06093b026dabf2f255363e2d285b0d1ac98dee1e0ded0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4822c90faba0c9500d964194dabdd859885a69df57b24d96d55cae52fe032de3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c67083e80771780d2da8b0f03b4b2f492580ec1ed669d97b39fca7b8615751(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c69686df3bffb070244328b5f9856665d6e0c8f69a27e6fb40b8cd2ce485c513(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__559dbd0b99a444633a3b9e2ef68c74bd83ae365241b9ae2e48f647bfcba38979(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfc6d2292317c36aca766aa9c662d6b88ea271dab9948b669ecffa6ca0d7880d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be83017260e98727e05a4d6c6658f6c56c8029e9ca7f72ef9e07ba78f7ec49eb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07fcd2bc0048ca412ddebb3ba4b1ec899a08d60d8bdfb59e7e70dd8f169c7780(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__038ddcd7a46a40851e8b92381f2a6efa8e3ab2bdfc511643f70e86ee35ea5f50(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99d534fe1d19a021657517fd317441ada2511dceda5cdd70e4fc6d4ff0b7e4e0(
    value: typing.Optional[OceanAwsLaunchSpecInstanceTypesFilters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__395182d77175bb3a2ec9e546ee09076cc24f7005c33c44cc509204e8fa73d6f9(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddb6a48c3bf89ccdd9d8786de14d84a4a7a9a74d9b268b1bfbcfd3525c545bc8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d527ad3d0def5552bf4ed6e81e96dc00093a5da3860cd3f80e92bf4bb2029b18(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b44be41795172b8a0c44da5a4b18b17c4cede7204fbf931d0b48f561ff037af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f59791ee6ff7cbc02bb9afa44cbd3d2afb21f299e3a355f03d19acfcc26c831(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5b5b7511cb1674192d06c9450e2d475e5271917b6932642c0b7b137036aa798(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b080a4fd12f2e5decb9632b3753ade931a6f92640b910b813bcd5b058aa8f8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd587d5cbbef608d0e4d9b18380d11478858ecd8a04c5c987d128533bc150f26(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3117eb3dd2850608d5a0a9d9d6e588febe772bfca1396809a6894a740c3bc885(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b75b07da4d6cb265bab5bd60b6c28e8c0a680f4499f2d969fff7b17581e4650(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__813c6db13d6ce6a9c41f38b4c3defc5ef253b26d6d70c02c8a040d2f23df5d20(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__297ff0bcba9a783d45967d6be877b6039829ccb29d28e3404328fe92db682a60(
    *,
    max_instance_count: typing.Optional[jsii.Number] = None,
    min_instance_count: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a710f0b7b80ba61c1f1f6bfbd58b9a98401a3ce13c30d237a16c134424c471e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ee3d9817217cd79b61bc06b8ed9b631c5520068d71928b603517f6cf7f7cfe6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd1dde861fa18fb406792822ddf2eff5766e6dc1bc89bc933f42de6653dd9d46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dbed9c76bb511586b936833e2a4c95ac0a6065a5f20e37ab67d1535ce3492c2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e69c2c46c61caecd3f96b92990555e0f6c1323fd78c449e054f901ef83ca2cac(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453787d6ad48ede58c01edf8a6eeebb411bdc2426819d1e3d4ed024a74a71094(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecResourceLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efae5918e93573074e4688cf8dd441f571bc50a60c5d91163f44d41659bcb6f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16ac1504d81e20c857fbb7cede1e09912bb5d8fcf89bc25b732f9956b8d074b4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e35e2127a91a20ce95f24c937d660d87b8e729da7eae23c14996af0af6d15dc5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f9c71dcdeecb29b609935e2cd5e6187309aa766e81d0f8e6734f33a5314734b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecResourceLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6340ebdfaf9531e8d1f66ff8e802e45adbc3dcd6802ad01207d67569d68f44b(
    *,
    time_windows: typing.Sequence[builtins.str],
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff6d45df138625781b182d0acb70f97184cf96c480a601e60afd33ccf33d2619(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8352e8dea11014ea14be7c47c7269333cd69f97e382a6c4203821803cf222ff6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87ba5a3a9ceb4303e31a32001573a4956a1f2195117662828bf2d96b1cc01edf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6141d803e188b8fb2f2138917cf47f303ea56571724f87448e8acf61a1f4bae(
    value: typing.Optional[OceanAwsLaunchSpecSchedulingShutdownHours],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45a6845fa570b1c607ca1e20366f4a4ed98964a831f8485a50abd9f8d6d6973d(
    *,
    cron_expression: builtins.str,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    task_type: builtins.str,
    task_headroom: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecSchedulingTaskTaskHeadroom, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8241dc7e68ed971e91e838f565e627c2b099a01363d2eb63331f570c613b6850(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6853807d0bc0e49f16ee5e74b6770a4db4b3fd05b47daa13b5a6f58215dc0cd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__573472154c0a13cb804073904b5d6c325550723ce684e322f49f5595fcc11a29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03f360c72f172d0b626dc76bbbb7e0f31042153e95bd0bf797ffe4269a879214(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__025114f3d18b16295496cdd9a53d5a77cde9c03f4bb40bd858d2c3e6f79198b0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00daaee5c955123e2381ef57aae5f5454149a0148b8934245467ec4488fc180(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33ac16ef185010e913c7f879e4a482b7d46092089fca4c33241500361612abab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__284b1847af1f7e61cf470db5c08e2b79ea5caeeebff6bdb011257f7fa8664398(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanAwsLaunchSpecSchedulingTaskTaskHeadroom, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ec9670977b2320764e4044e7e514d75e367791f99096ca141af38d512887049(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b861291aeb4a7325023baa993880dc9f5e7e000de19c0ebe3846d43159faaee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7fd2ac268e84e52c650618f86d5fffd6993b573e6baef7c9a2bc1c946a58801(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99ebea17e70819cb44c909e1ac506cc4fccc7f03439bd4240e10f63ff29053b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5ce9768813e3d37b24568381bbbdb8a8600aaa5ced4cd230eceb8ff6f424abf(
    *,
    num_of_units: jsii.Number,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb976736cc4e95b8bd522ab5dcc00350a2793630dcac099694a140f6d2a50537(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8e557fef5b770bac6e5d1fd987b1972fe7ffae44622e317e8c51603418f8c8d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e385ea6c80c210fc6b0b8e1b96ff97b0d09994ba7e7b7177c9e84c27d6a3626(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86323b83332beec8869188a582c58e3296955ca2635a171ac6328f0ee8b168d0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f87302de4b7f53147268136c90c55e2a5d77fa308361a2ee5e3e7fd3fb1ae8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__650f420d336f8f003802109350cdbdbbd70a1c4168b6c5aac1be92ca5c3e7ce3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb325328c972a91e3dbcf3846115fd4bdd1dd82d2246d08b50a3a99ecf18d956(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13c707d2bf91a572e301b7945a22ecb66f3f8a85833f6fe7aa1c227423f8a19b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8967490ea94aa5381083ed44b9b4cdef7180a9de8dad5f32521784fadf06fc4e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__572aa9fd2aa70b54f75d27a905967dec9d62539ef01f6083ed0e25620324b94f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409abfa653e9412346f75acfe2c96e12c9c83ee99b1127a8e7e944d1bcbf7fad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b65d75b62ee5a920270dcf66e94e5b5d244a40b0b9f5389aa914cae0a2b7d57(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecSchedulingTaskTaskHeadroom]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__804544686b0212c51f61719537905099fd1c9258465eb106807eb67364a4f636(
    *,
    effect: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c5eb39d2c771881ff8c97d07f64b7d35261ca295167f79346c01dc69d6cc97e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce8abfe29ce91402a9ca62805a6453b9ac04e7bf291e68ccfd048cbfbe982428(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d55ae89ec25d7526eda6bb1c4c81fd17620adaad2a0f13d1c1c67d3a1c41758f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6ac644f581d43077f57130857e711c04e9eca69ac403a4e1f01e78915c74399(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9200bca91ff64043d50d7bfe8bf67a56b7b8332cead3fdf97b6e9b002e567310(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef7e636fd4735e694e2ff94b6697014b9b46ae4d507f345f8108128d845c2e90(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStartupTaints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69d09c16201e3bccce679e6ac872f62bab20b1ced67091bd22ee9b6f980f705c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c71d5e7c290109b597e2768eb8fecec1b85e802b4b846a3b27e64fe92bb764d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b2dd296cb8c268f51b0d9a9fef51b5b10e9742eff88a31011abbacb67b0ef2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1683c2fe0e99e19b863c50f00348bc5270bb6c14257a52cdd479369b1ac9a78f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8ff85c4a87e4f770e13fcbdc61a666b147eb138181934bb0576c3a1907f237(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStartupTaints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e426c17f6a5172528757217c705f9025e0609af797d17045b88d1f9ce21e264(
    *,
    draining_timeout: typing.Optional[jsii.Number] = None,
    orientation: typing.Optional[typing.Union[OceanAwsLaunchSpecStrategyOrientation, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_percentage: typing.Optional[jsii.Number] = None,
    utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    utilize_reserved_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cce69012664b78e54e51510cf968cc53522993a377f41f67c1f2dee028a9169(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cbb9131cef8c8836d86a23fb880d9be9c63a661c5f75c6347e1482b7cd8ca4e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c3755bfc8a5f9865bd4402fb292e651b8de945efa4d1adaa358c4bb3fee3b65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56779abf2602d9ec8247d191d9558bc013fe26f5783eaae82ff35b82c6079b11(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c58e699a6499c3cfea35ab4acf96c7eda1a2a551935fd04d438f53175a9393e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2e94b7b480c5e42c84bd6e046e950542575c0a57229396014b69c453a04145a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecStrategy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ceb8564baa7f52257213012fa241dd8998a450afb8c0ce2ad6a4929f1536508(
    *,
    availability_vs_cost: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddde66fc97c64c7b855c34f4376db9003465655069b4115bebe657d29f555cc4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7069dd889e4a658fc5439032c46f703ebaadf837f1c24b093d05137b74883af2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7f28219e26e5aba129fafa46b5a7f70adeadb267b3f4c65f93b4f70db94e6b0(
    value: typing.Optional[OceanAwsLaunchSpecStrategyOrientation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__484f3b03679f1e91013819f03617ec779fe2efa42bb3f13b7619e3cdc92f5a4e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25eea886d57964df020f49181033b42827b6e3a9588d0b2481bdb66d0cabbe8f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69fa3537de6fc77cdd684dc51bd0e7403f98a39dd12d8391dd35cb7a4c2cb236(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4181fee630cfd241de6cbc7750bd3089495ce6029cc9ac54f71cc0cdd394365c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a8db14c851b23591bb81050bbdae8e98fe33a31bbb16e81c0ef9bcc1fa030e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8303de481bb3a6906e3f97dfa10fe0a692449df259bd83ea8a73b3e52bae36d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecStrategy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c970069e174984575df43f08cee5602fbfac6445c07f88f25a0ca2a4bde5fd0b(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eec154e70bf1427f1858631a3d7ac0b5ccebe8b9ef7b94f1b44ac7b6d47b793(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8f2a20424ac7ffa68fd5f2b53307eb80d533639ed464e5edd67c9c59799135a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4419bef82d5d79dece0bdeeaa05082a4353db3cad52f2e806f61cc3014e3a467(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e25697ad9f69b2c8d78cbdadfa5ebcdfc19199794b7d77f9556fc569a1b0ed00(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d667f007d84ed965fadb5965b2bfc59f5e1863aabaa17cdaff43a23eb47fd8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1ebeaf413e794627ad5730f07dc5c608fedc0d63a9e1d2a0252ccedf8f53685(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e4a147bbe69e7142d82f39874056fd31960a5ca3af8672ce68fa77a5252c420(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99660fabaff561ddd142f75417218fab2692efe010c682fd335199e545b801ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__654b08cef16b953c146c3ffcd08b9a3c385774eba371afda7a03c7d2e2897ef2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51e15a42e75351a7ef21e50ffb70c3054fa96e0fe2852f11cda61f7da55c8e58(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff47a4f214315017a21d83778270eabc3ebf4e8eed12187fe23ad5d00d0a8c6b(
    *,
    effect: builtins.str,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4d4bb5e805ebafb2f7181d051cb366dd33df749877f0d4ef2c4b272d67466c6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d97d0c7f152af6b867b1c586ace43cf61786d6075244650df7dd8fda29af22(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02044930b5fb817421e47fa8fc33e0a5a296d871d4c64f29af1cdf2d24134957(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6d90048cda95164094bf06505d9c863ed6f9c379189c0ac4fa698d7e185f489(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b991c4f49172a6644b65c6f9ebb3a604a7e830d56665aafb9442a1be2584518d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a8e9cef03053be45f5bd8c5805bfcc697b1798c495c2c20889e9a97229b3c4b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanAwsLaunchSpecTaints]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07908364fe368e4d68eae55b76b4ed91a53e6eca6f891f0462158ca0d66fa4f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__195029f8c47cdceac2fe6894240f71f5bea6469d76e804f6a0c24d0c5e0cf994(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34d807039bcee80b3d374c6d8707fd5e4a34006850a5eef4710e0719e9d3644c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c886c7a83d71839dca5c9c84edcfc41aacf164088a61494ff3c47a2934fabbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__617827d9d59bbaafa8291c660567d2c94e96326f04ddaafa6fbf14172e2b017c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanAwsLaunchSpecTaints]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e0f75484b1245857e21a5cd98968984c9185c4c7edaf2d939f568b8964fed70(
    *,
    should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    roll_config: typing.Optional[typing.Union[OceanAwsLaunchSpecUpdatePolicyRollConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7df825503d40546f714492be6c8682e7748320637f857ee09d6a3c2300944f15(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0644bd046398fb54d159d8a850cd84d4cfc6a438335cf52e460846ca8ce217ee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df65f5e31452f1bfd5b52f02407fc3dbfdf8361e51263662129ce607322e3687(
    value: typing.Optional[OceanAwsLaunchSpecUpdatePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c988807ba40abf0dd2b50663823c768e849efeec61b94b5d33a2beb2aa7ad7c4(
    *,
    batch_size_percentage: jsii.Number,
    respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d8fc179042d3c2d00059908763831203c61ed59a763df8f4d9bf40d77dc234e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b062361e626f263b2b9835e2bd6278d7534e50a9c6d581ad70012aa53f28b95(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3be9dd6232d9484919c42f766ab442229aeb4ec87b2dc24386b5e828ba211fc5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e0aabf2ae1acd30ca78ab2000f81eeca8afb7063d4deeca90cfd15a163d7815(
    value: typing.Optional[OceanAwsLaunchSpecUpdatePolicyRollConfig],
) -> None:
    """Type checking stubs"""
    pass
