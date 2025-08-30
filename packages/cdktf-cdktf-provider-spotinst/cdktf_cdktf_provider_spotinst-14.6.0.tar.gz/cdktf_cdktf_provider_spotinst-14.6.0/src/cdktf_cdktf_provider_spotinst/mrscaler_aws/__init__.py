r'''
# `spotinst_mrscaler_aws`

Refer to the Terraform Registry for docs: [`spotinst_mrscaler_aws`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws).
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


class MrscalerAws(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAws",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws spotinst_mrscaler_aws}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        strategy: builtins.str,
        additional_info: typing.Optional[builtins.str] = None,
        additional_primary_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_replica_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        applications: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsApplications", typing.Dict[builtins.str, typing.Any]]]]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsBootstrapActionsFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        configurations_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsConfigurationsFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_desired_capacity: typing.Optional[jsii.Number] = None,
        core_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        core_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        core_lifecycle: typing.Optional[builtins.str] = None,
        core_max_size: typing.Optional[jsii.Number] = None,
        core_min_size: typing.Optional[jsii.Number] = None,
        core_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_unit: typing.Optional[builtins.str] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        ebs_root_volume_size: typing.Optional[jsii.Number] = None,
        ec2_key_name: typing.Optional[builtins.str] = None,
        expose_cluster_id: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_weights: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsInstanceWeights", typing.Dict[builtins.str, typing.Any]]]]] = None,
        job_flow_role: typing.Optional[builtins.str] = None,
        keep_job_flow_alive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_uri: typing.Optional[builtins.str] = None,
        managed_primary_security_group: typing.Optional[builtins.str] = None,
        managed_replica_security_group: typing.Optional[builtins.str] = None,
        master_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsMasterEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]]] = None,
        master_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        master_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        master_lifecycle: typing.Optional[builtins.str] = None,
        master_target: typing.Optional[jsii.Number] = None,
        provisioning_timeout: typing.Optional[typing.Union["MrscalerAwsProvisioningTimeout", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
        release_label: typing.Optional[builtins.str] = None,
        repo_upgrade_on_boot: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security_config: typing.Optional[builtins.str] = None,
        service_access_security_group: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[builtins.str] = None,
        steps_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsStepsFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_desired_capacity: typing.Optional[jsii.Number] = None,
        task_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        task_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        task_lifecycle: typing.Optional[builtins.str] = None,
        task_max_size: typing.Optional[jsii.Number] = None,
        task_min_size: typing.Optional[jsii.Number] = None,
        task_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_unit: typing.Optional[builtins.str] = None,
        termination_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTerminationPolicies", typing.Dict[builtins.str, typing.Any]]]]] = None,
        termination_protected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        visible_to_all_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws spotinst_mrscaler_aws} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#name MrscalerAws#name}.
        :param strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#strategy MrscalerAws#strategy}.
        :param additional_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_info MrscalerAws#additional_info}.
        :param additional_primary_security_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_primary_security_groups MrscalerAws#additional_primary_security_groups}.
        :param additional_replica_security_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_replica_security_groups MrscalerAws#additional_replica_security_groups}.
        :param applications: applications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#applications MrscalerAws#applications}
        :param availability_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#availability_zones MrscalerAws#availability_zones}.
        :param bootstrap_actions_file: bootstrap_actions_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bootstrap_actions_file MrscalerAws#bootstrap_actions_file}
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cluster_id MrscalerAws#cluster_id}.
        :param configurations_file: configurations_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#configurations_file MrscalerAws#configurations_file}
        :param core_desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_desired_capacity MrscalerAws#core_desired_capacity}.
        :param core_ebs_block_device: core_ebs_block_device block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_ebs_block_device MrscalerAws#core_ebs_block_device}
        :param core_ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_ebs_optimized MrscalerAws#core_ebs_optimized}.
        :param core_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_instance_types MrscalerAws#core_instance_types}.
        :param core_lifecycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_lifecycle MrscalerAws#core_lifecycle}.
        :param core_max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_max_size MrscalerAws#core_max_size}.
        :param core_min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_min_size MrscalerAws#core_min_size}.
        :param core_scaling_down_policy: core_scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_scaling_down_policy MrscalerAws#core_scaling_down_policy}
        :param core_scaling_up_policy: core_scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_scaling_up_policy MrscalerAws#core_scaling_up_policy}
        :param core_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_unit MrscalerAws#core_unit}.
        :param custom_ami_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#custom_ami_id MrscalerAws#custom_ami_id}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#description MrscalerAws#description}.
        :param ebs_root_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#ebs_root_volume_size MrscalerAws#ebs_root_volume_size}.
        :param ec2_key_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#ec2_key_name MrscalerAws#ec2_key_name}.
        :param expose_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#expose_cluster_id MrscalerAws#expose_cluster_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#id MrscalerAws#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_weights: instance_weights block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_weights MrscalerAws#instance_weights}
        :param job_flow_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#job_flow_role MrscalerAws#job_flow_role}.
        :param keep_job_flow_alive: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#keep_job_flow_alive MrscalerAws#keep_job_flow_alive}.
        :param log_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#log_uri MrscalerAws#log_uri}.
        :param managed_primary_security_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#managed_primary_security_group MrscalerAws#managed_primary_security_group}.
        :param managed_replica_security_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#managed_replica_security_group MrscalerAws#managed_replica_security_group}.
        :param master_ebs_block_device: master_ebs_block_device block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_ebs_block_device MrscalerAws#master_ebs_block_device}
        :param master_ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_ebs_optimized MrscalerAws#master_ebs_optimized}.
        :param master_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_instance_types MrscalerAws#master_instance_types}.
        :param master_lifecycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_lifecycle MrscalerAws#master_lifecycle}.
        :param master_target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_target MrscalerAws#master_target}.
        :param provisioning_timeout: provisioning_timeout block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#provisioning_timeout MrscalerAws#provisioning_timeout}
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#region MrscalerAws#region}.
        :param release_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#release_label MrscalerAws#release_label}.
        :param repo_upgrade_on_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#repo_upgrade_on_boot MrscalerAws#repo_upgrade_on_boot}.
        :param retries: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#retries MrscalerAws#retries}.
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#scheduled_task MrscalerAws#scheduled_task}
        :param security_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#security_config MrscalerAws#security_config}.
        :param service_access_security_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#service_access_security_group MrscalerAws#service_access_security_group}.
        :param service_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#service_role MrscalerAws#service_role}.
        :param steps_file: steps_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#steps_file MrscalerAws#steps_file}
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#tags MrscalerAws#tags}
        :param task_desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_desired_capacity MrscalerAws#task_desired_capacity}.
        :param task_ebs_block_device: task_ebs_block_device block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_ebs_block_device MrscalerAws#task_ebs_block_device}
        :param task_ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_ebs_optimized MrscalerAws#task_ebs_optimized}.
        :param task_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_instance_types MrscalerAws#task_instance_types}.
        :param task_lifecycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_lifecycle MrscalerAws#task_lifecycle}.
        :param task_max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_max_size MrscalerAws#task_max_size}.
        :param task_min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_min_size MrscalerAws#task_min_size}.
        :param task_scaling_down_policy: task_scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_scaling_down_policy MrscalerAws#task_scaling_down_policy}
        :param task_scaling_up_policy: task_scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_scaling_up_policy MrscalerAws#task_scaling_up_policy}
        :param task_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_unit MrscalerAws#task_unit}.
        :param termination_policies: termination_policies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#termination_policies MrscalerAws#termination_policies}
        :param termination_protected: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#termination_protected MrscalerAws#termination_protected}.
        :param visible_to_all_users: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#visible_to_all_users MrscalerAws#visible_to_all_users}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31c78e829881099c8a568bbfbf56aadc23e2bacd798cfaf5c48e25c1d7ba171c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MrscalerAwsConfig(
            name=name,
            strategy=strategy,
            additional_info=additional_info,
            additional_primary_security_groups=additional_primary_security_groups,
            additional_replica_security_groups=additional_replica_security_groups,
            applications=applications,
            availability_zones=availability_zones,
            bootstrap_actions_file=bootstrap_actions_file,
            cluster_id=cluster_id,
            configurations_file=configurations_file,
            core_desired_capacity=core_desired_capacity,
            core_ebs_block_device=core_ebs_block_device,
            core_ebs_optimized=core_ebs_optimized,
            core_instance_types=core_instance_types,
            core_lifecycle=core_lifecycle,
            core_max_size=core_max_size,
            core_min_size=core_min_size,
            core_scaling_down_policy=core_scaling_down_policy,
            core_scaling_up_policy=core_scaling_up_policy,
            core_unit=core_unit,
            custom_ami_id=custom_ami_id,
            description=description,
            ebs_root_volume_size=ebs_root_volume_size,
            ec2_key_name=ec2_key_name,
            expose_cluster_id=expose_cluster_id,
            id=id,
            instance_weights=instance_weights,
            job_flow_role=job_flow_role,
            keep_job_flow_alive=keep_job_flow_alive,
            log_uri=log_uri,
            managed_primary_security_group=managed_primary_security_group,
            managed_replica_security_group=managed_replica_security_group,
            master_ebs_block_device=master_ebs_block_device,
            master_ebs_optimized=master_ebs_optimized,
            master_instance_types=master_instance_types,
            master_lifecycle=master_lifecycle,
            master_target=master_target,
            provisioning_timeout=provisioning_timeout,
            region=region,
            release_label=release_label,
            repo_upgrade_on_boot=repo_upgrade_on_boot,
            retries=retries,
            scheduled_task=scheduled_task,
            security_config=security_config,
            service_access_security_group=service_access_security_group,
            service_role=service_role,
            steps_file=steps_file,
            tags=tags,
            task_desired_capacity=task_desired_capacity,
            task_ebs_block_device=task_ebs_block_device,
            task_ebs_optimized=task_ebs_optimized,
            task_instance_types=task_instance_types,
            task_lifecycle=task_lifecycle,
            task_max_size=task_max_size,
            task_min_size=task_min_size,
            task_scaling_down_policy=task_scaling_down_policy,
            task_scaling_up_policy=task_scaling_up_policy,
            task_unit=task_unit,
            termination_policies=termination_policies,
            termination_protected=termination_protected,
            visible_to_all_users=visible_to_all_users,
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
        '''Generates CDKTF code for importing a MrscalerAws resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MrscalerAws to import.
        :param import_from_id: The id of the existing MrscalerAws that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MrscalerAws to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35172109fdfdfd7a3714918fe66883d37257d49546d4362185fef996d5fb4b23)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putApplications")
    def put_applications(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsApplications", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd41554ad0395378c0f6fdab082d9cb280f9061845c9281972edb9a00394eba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApplications", [value]))

    @jsii.member(jsii_name="putBootstrapActionsFile")
    def put_bootstrap_actions_file(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsBootstrapActionsFile", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d64eb5c37233a28288caf6acd710e044a3861c77865f2485470996db5af858fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBootstrapActionsFile", [value]))

    @jsii.member(jsii_name="putConfigurationsFile")
    def put_configurations_file(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsConfigurationsFile", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ce3fa0ffa50fce9100fbf2b19943bebeecd8ad0c0e0febee6ad12369ceacdb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putConfigurationsFile", [value]))

    @jsii.member(jsii_name="putCoreEbsBlockDevice")
    def put_core_ebs_block_device(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4d8ccc7b4eb834bd856f6e41e7c21855cdf2308e92e8f34d1fdd48cd39050b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCoreEbsBlockDevice", [value]))

    @jsii.member(jsii_name="putCoreScalingDownPolicy")
    def put_core_scaling_down_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a5f4d17aa08240f1e933cbf2074b420ce0b89d4bf4c8be63ff714d395de31d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCoreScalingDownPolicy", [value]))

    @jsii.member(jsii_name="putCoreScalingUpPolicy")
    def put_core_scaling_up_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__382f5a5e0ded3b02a9c69b05e95493f4d354d32cdb4ca03f7d1a0696d731e266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCoreScalingUpPolicy", [value]))

    @jsii.member(jsii_name="putInstanceWeights")
    def put_instance_weights(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsInstanceWeights", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__609e720f56d51c4f4fe2618f5ce0dc0894e710e30dbd6cc67761c2f6f6c0c1f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putInstanceWeights", [value]))

    @jsii.member(jsii_name="putMasterEbsBlockDevice")
    def put_master_ebs_block_device(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsMasterEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605d533b2509b3acfc89b2cce1fd0a8620f14d0952d24551e1eb065a6b28071d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMasterEbsBlockDevice", [value]))

    @jsii.member(jsii_name="putProvisioningTimeout")
    def put_provisioning_timeout(
        self,
        *,
        timeout: jsii.Number,
        timeout_action: builtins.str,
    ) -> None:
        '''
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#timeout MrscalerAws#timeout}.
        :param timeout_action: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#timeout_action MrscalerAws#timeout_action}.
        '''
        value = MrscalerAwsProvisioningTimeout(
            timeout=timeout, timeout_action=timeout_action
        )

        return typing.cast(None, jsii.invoke(self, "putProvisioningTimeout", [value]))

    @jsii.member(jsii_name="putScheduledTask")
    def put_scheduled_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsScheduledTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1831eb6e7a670a04697ec67112ae9a09915d32874ca3d18e3e28976aaaa995d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScheduledTask", [value]))

    @jsii.member(jsii_name="putStepsFile")
    def put_steps_file(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsStepsFile", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c1dfdf1bba7fca1420a6a497f486a27dc8ae932317b6d0d6786ed0c0f11856f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStepsFile", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af6965d530e68d33853e46276db8f941875879592412db8520ca54184d3a32cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putTaskEbsBlockDevice")
    def put_task_ebs_block_device(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58a7de5040d346a768d5f8765aa8a60931538eef2efb9539259ee120ddf28db9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaskEbsBlockDevice", [value]))

    @jsii.member(jsii_name="putTaskScalingDownPolicy")
    def put_task_scaling_down_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b67b1cda2adc0d12f4c7e5c72fd41f6e237e9c92ccbcc2a400d6bf29246094a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaskScalingDownPolicy", [value]))

    @jsii.member(jsii_name="putTaskScalingUpPolicy")
    def put_task_scaling_up_policy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffd75d55ea75d75282d7a87ad11f3f27a13519d5829c258f903797430091dd34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTaskScalingUpPolicy", [value]))

    @jsii.member(jsii_name="putTerminationPolicies")
    def put_termination_policies(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTerminationPolicies", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5da96db93bd292899ea0b2a516cf099905712f7a3b205cdf409d8ee9eb91f0bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTerminationPolicies", [value]))

    @jsii.member(jsii_name="resetAdditionalInfo")
    def reset_additional_info(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalInfo", []))

    @jsii.member(jsii_name="resetAdditionalPrimarySecurityGroups")
    def reset_additional_primary_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalPrimarySecurityGroups", []))

    @jsii.member(jsii_name="resetAdditionalReplicaSecurityGroups")
    def reset_additional_replica_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalReplicaSecurityGroups", []))

    @jsii.member(jsii_name="resetApplications")
    def reset_applications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplications", []))

    @jsii.member(jsii_name="resetAvailabilityZones")
    def reset_availability_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZones", []))

    @jsii.member(jsii_name="resetBootstrapActionsFile")
    def reset_bootstrap_actions_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootstrapActionsFile", []))

    @jsii.member(jsii_name="resetClusterId")
    def reset_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterId", []))

    @jsii.member(jsii_name="resetConfigurationsFile")
    def reset_configurations_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationsFile", []))

    @jsii.member(jsii_name="resetCoreDesiredCapacity")
    def reset_core_desired_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreDesiredCapacity", []))

    @jsii.member(jsii_name="resetCoreEbsBlockDevice")
    def reset_core_ebs_block_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreEbsBlockDevice", []))

    @jsii.member(jsii_name="resetCoreEbsOptimized")
    def reset_core_ebs_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreEbsOptimized", []))

    @jsii.member(jsii_name="resetCoreInstanceTypes")
    def reset_core_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreInstanceTypes", []))

    @jsii.member(jsii_name="resetCoreLifecycle")
    def reset_core_lifecycle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreLifecycle", []))

    @jsii.member(jsii_name="resetCoreMaxSize")
    def reset_core_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreMaxSize", []))

    @jsii.member(jsii_name="resetCoreMinSize")
    def reset_core_min_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreMinSize", []))

    @jsii.member(jsii_name="resetCoreScalingDownPolicy")
    def reset_core_scaling_down_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreScalingDownPolicy", []))

    @jsii.member(jsii_name="resetCoreScalingUpPolicy")
    def reset_core_scaling_up_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreScalingUpPolicy", []))

    @jsii.member(jsii_name="resetCoreUnit")
    def reset_core_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCoreUnit", []))

    @jsii.member(jsii_name="resetCustomAmiId")
    def reset_custom_ami_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAmiId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEbsRootVolumeSize")
    def reset_ebs_root_volume_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsRootVolumeSize", []))

    @jsii.member(jsii_name="resetEc2KeyName")
    def reset_ec2_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2KeyName", []))

    @jsii.member(jsii_name="resetExposeClusterId")
    def reset_expose_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExposeClusterId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceWeights")
    def reset_instance_weights(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceWeights", []))

    @jsii.member(jsii_name="resetJobFlowRole")
    def reset_job_flow_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobFlowRole", []))

    @jsii.member(jsii_name="resetKeepJobFlowAlive")
    def reset_keep_job_flow_alive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepJobFlowAlive", []))

    @jsii.member(jsii_name="resetLogUri")
    def reset_log_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogUri", []))

    @jsii.member(jsii_name="resetManagedPrimarySecurityGroup")
    def reset_managed_primary_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedPrimarySecurityGroup", []))

    @jsii.member(jsii_name="resetManagedReplicaSecurityGroup")
    def reset_managed_replica_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedReplicaSecurityGroup", []))

    @jsii.member(jsii_name="resetMasterEbsBlockDevice")
    def reset_master_ebs_block_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterEbsBlockDevice", []))

    @jsii.member(jsii_name="resetMasterEbsOptimized")
    def reset_master_ebs_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterEbsOptimized", []))

    @jsii.member(jsii_name="resetMasterInstanceTypes")
    def reset_master_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterInstanceTypes", []))

    @jsii.member(jsii_name="resetMasterLifecycle")
    def reset_master_lifecycle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterLifecycle", []))

    @jsii.member(jsii_name="resetMasterTarget")
    def reset_master_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterTarget", []))

    @jsii.member(jsii_name="resetProvisioningTimeout")
    def reset_provisioning_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisioningTimeout", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetReleaseLabel")
    def reset_release_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReleaseLabel", []))

    @jsii.member(jsii_name="resetRepoUpgradeOnBoot")
    def reset_repo_upgrade_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepoUpgradeOnBoot", []))

    @jsii.member(jsii_name="resetRetries")
    def reset_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetries", []))

    @jsii.member(jsii_name="resetScheduledTask")
    def reset_scheduled_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledTask", []))

    @jsii.member(jsii_name="resetSecurityConfig")
    def reset_security_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityConfig", []))

    @jsii.member(jsii_name="resetServiceAccessSecurityGroup")
    def reset_service_access_security_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccessSecurityGroup", []))

    @jsii.member(jsii_name="resetServiceRole")
    def reset_service_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceRole", []))

    @jsii.member(jsii_name="resetStepsFile")
    def reset_steps_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStepsFile", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTaskDesiredCapacity")
    def reset_task_desired_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskDesiredCapacity", []))

    @jsii.member(jsii_name="resetTaskEbsBlockDevice")
    def reset_task_ebs_block_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskEbsBlockDevice", []))

    @jsii.member(jsii_name="resetTaskEbsOptimized")
    def reset_task_ebs_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskEbsOptimized", []))

    @jsii.member(jsii_name="resetTaskInstanceTypes")
    def reset_task_instance_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskInstanceTypes", []))

    @jsii.member(jsii_name="resetTaskLifecycle")
    def reset_task_lifecycle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskLifecycle", []))

    @jsii.member(jsii_name="resetTaskMaxSize")
    def reset_task_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskMaxSize", []))

    @jsii.member(jsii_name="resetTaskMinSize")
    def reset_task_min_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskMinSize", []))

    @jsii.member(jsii_name="resetTaskScalingDownPolicy")
    def reset_task_scaling_down_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskScalingDownPolicy", []))

    @jsii.member(jsii_name="resetTaskScalingUpPolicy")
    def reset_task_scaling_up_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskScalingUpPolicy", []))

    @jsii.member(jsii_name="resetTaskUnit")
    def reset_task_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskUnit", []))

    @jsii.member(jsii_name="resetTerminationPolicies")
    def reset_termination_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationPolicies", []))

    @jsii.member(jsii_name="resetTerminationProtected")
    def reset_termination_protected(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationProtected", []))

    @jsii.member(jsii_name="resetVisibleToAllUsers")
    def reset_visible_to_all_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibleToAllUsers", []))

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
    @jsii.member(jsii_name="applications")
    def applications(self) -> "MrscalerAwsApplicationsList":
        return typing.cast("MrscalerAwsApplicationsList", jsii.get(self, "applications"))

    @builtins.property
    @jsii.member(jsii_name="bootstrapActionsFile")
    def bootstrap_actions_file(self) -> "MrscalerAwsBootstrapActionsFileList":
        return typing.cast("MrscalerAwsBootstrapActionsFileList", jsii.get(self, "bootstrapActionsFile"))

    @builtins.property
    @jsii.member(jsii_name="configurationsFile")
    def configurations_file(self) -> "MrscalerAwsConfigurationsFileList":
        return typing.cast("MrscalerAwsConfigurationsFileList", jsii.get(self, "configurationsFile"))

    @builtins.property
    @jsii.member(jsii_name="coreEbsBlockDevice")
    def core_ebs_block_device(self) -> "MrscalerAwsCoreEbsBlockDeviceList":
        return typing.cast("MrscalerAwsCoreEbsBlockDeviceList", jsii.get(self, "coreEbsBlockDevice"))

    @builtins.property
    @jsii.member(jsii_name="coreScalingDownPolicy")
    def core_scaling_down_policy(self) -> "MrscalerAwsCoreScalingDownPolicyList":
        return typing.cast("MrscalerAwsCoreScalingDownPolicyList", jsii.get(self, "coreScalingDownPolicy"))

    @builtins.property
    @jsii.member(jsii_name="coreScalingUpPolicy")
    def core_scaling_up_policy(self) -> "MrscalerAwsCoreScalingUpPolicyList":
        return typing.cast("MrscalerAwsCoreScalingUpPolicyList", jsii.get(self, "coreScalingUpPolicy"))

    @builtins.property
    @jsii.member(jsii_name="instanceWeights")
    def instance_weights(self) -> "MrscalerAwsInstanceWeightsList":
        return typing.cast("MrscalerAwsInstanceWeightsList", jsii.get(self, "instanceWeights"))

    @builtins.property
    @jsii.member(jsii_name="masterEbsBlockDevice")
    def master_ebs_block_device(self) -> "MrscalerAwsMasterEbsBlockDeviceList":
        return typing.cast("MrscalerAwsMasterEbsBlockDeviceList", jsii.get(self, "masterEbsBlockDevice"))

    @builtins.property
    @jsii.member(jsii_name="outputClusterId")
    def output_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputClusterId"))

    @builtins.property
    @jsii.member(jsii_name="provisioningTimeout")
    def provisioning_timeout(self) -> "MrscalerAwsProvisioningTimeoutOutputReference":
        return typing.cast("MrscalerAwsProvisioningTimeoutOutputReference", jsii.get(self, "provisioningTimeout"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTask")
    def scheduled_task(self) -> "MrscalerAwsScheduledTaskList":
        return typing.cast("MrscalerAwsScheduledTaskList", jsii.get(self, "scheduledTask"))

    @builtins.property
    @jsii.member(jsii_name="stepsFile")
    def steps_file(self) -> "MrscalerAwsStepsFileList":
        return typing.cast("MrscalerAwsStepsFileList", jsii.get(self, "stepsFile"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "MrscalerAwsTagsList":
        return typing.cast("MrscalerAwsTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="taskEbsBlockDevice")
    def task_ebs_block_device(self) -> "MrscalerAwsTaskEbsBlockDeviceList":
        return typing.cast("MrscalerAwsTaskEbsBlockDeviceList", jsii.get(self, "taskEbsBlockDevice"))

    @builtins.property
    @jsii.member(jsii_name="taskScalingDownPolicy")
    def task_scaling_down_policy(self) -> "MrscalerAwsTaskScalingDownPolicyList":
        return typing.cast("MrscalerAwsTaskScalingDownPolicyList", jsii.get(self, "taskScalingDownPolicy"))

    @builtins.property
    @jsii.member(jsii_name="taskScalingUpPolicy")
    def task_scaling_up_policy(self) -> "MrscalerAwsTaskScalingUpPolicyList":
        return typing.cast("MrscalerAwsTaskScalingUpPolicyList", jsii.get(self, "taskScalingUpPolicy"))

    @builtins.property
    @jsii.member(jsii_name="terminationPolicies")
    def termination_policies(self) -> "MrscalerAwsTerminationPoliciesList":
        return typing.cast("MrscalerAwsTerminationPoliciesList", jsii.get(self, "terminationPolicies"))

    @builtins.property
    @jsii.member(jsii_name="additionalInfoInput")
    def additional_info_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "additionalInfoInput"))

    @builtins.property
    @jsii.member(jsii_name="additionalPrimarySecurityGroupsInput")
    def additional_primary_security_groups_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "additionalPrimarySecurityGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="additionalReplicaSecurityGroupsInput")
    def additional_replica_security_groups_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "additionalReplicaSecurityGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationsInput")
    def applications_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsApplications"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsApplications"]]], jsii.get(self, "applicationsInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZonesInput")
    def availability_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "availabilityZonesInput"))

    @builtins.property
    @jsii.member(jsii_name="bootstrapActionsFileInput")
    def bootstrap_actions_file_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsBootstrapActionsFile"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsBootstrapActionsFile"]]], jsii.get(self, "bootstrapActionsFileInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configurationsFileInput")
    def configurations_file_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsConfigurationsFile"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsConfigurationsFile"]]], jsii.get(self, "configurationsFileInput"))

    @builtins.property
    @jsii.member(jsii_name="coreDesiredCapacityInput")
    def core_desired_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coreDesiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="coreEbsBlockDeviceInput")
    def core_ebs_block_device_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreEbsBlockDevice"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreEbsBlockDevice"]]], jsii.get(self, "coreEbsBlockDeviceInput"))

    @builtins.property
    @jsii.member(jsii_name="coreEbsOptimizedInput")
    def core_ebs_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "coreEbsOptimizedInput"))

    @builtins.property
    @jsii.member(jsii_name="coreInstanceTypesInput")
    def core_instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "coreInstanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="coreLifecycleInput")
    def core_lifecycle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "coreLifecycleInput"))

    @builtins.property
    @jsii.member(jsii_name="coreMaxSizeInput")
    def core_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coreMaxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="coreMinSizeInput")
    def core_min_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coreMinSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="coreScalingDownPolicyInput")
    def core_scaling_down_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingDownPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingDownPolicy"]]], jsii.get(self, "coreScalingDownPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="coreScalingUpPolicyInput")
    def core_scaling_up_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingUpPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingUpPolicy"]]], jsii.get(self, "coreScalingUpPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="coreUnitInput")
    def core_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "coreUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="customAmiIdInput")
    def custom_ami_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customAmiIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="ebsRootVolumeSizeInput")
    def ebs_root_volume_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ebsRootVolumeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ec2KeyNameInput")
    def ec2_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2KeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="exposeClusterIdInput")
    def expose_cluster_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "exposeClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceWeightsInput")
    def instance_weights_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsInstanceWeights"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsInstanceWeights"]]], jsii.get(self, "instanceWeightsInput"))

    @builtins.property
    @jsii.member(jsii_name="jobFlowRoleInput")
    def job_flow_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobFlowRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="keepJobFlowAliveInput")
    def keep_job_flow_alive_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "keepJobFlowAliveInput"))

    @builtins.property
    @jsii.member(jsii_name="logUriInput")
    def log_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logUriInput"))

    @builtins.property
    @jsii.member(jsii_name="managedPrimarySecurityGroupInput")
    def managed_primary_security_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedPrimarySecurityGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="managedReplicaSecurityGroupInput")
    def managed_replica_security_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedReplicaSecurityGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="masterEbsBlockDeviceInput")
    def master_ebs_block_device_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsMasterEbsBlockDevice"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsMasterEbsBlockDevice"]]], jsii.get(self, "masterEbsBlockDeviceInput"))

    @builtins.property
    @jsii.member(jsii_name="masterEbsOptimizedInput")
    def master_ebs_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "masterEbsOptimizedInput"))

    @builtins.property
    @jsii.member(jsii_name="masterInstanceTypesInput")
    def master_instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "masterInstanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="masterLifecycleInput")
    def master_lifecycle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterLifecycleInput"))

    @builtins.property
    @jsii.member(jsii_name="masterTargetInput")
    def master_target_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "masterTargetInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="provisioningTimeoutInput")
    def provisioning_timeout_input(
        self,
    ) -> typing.Optional["MrscalerAwsProvisioningTimeout"]:
        return typing.cast(typing.Optional["MrscalerAwsProvisioningTimeout"], jsii.get(self, "provisioningTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="releaseLabelInput")
    def release_label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "releaseLabelInput"))

    @builtins.property
    @jsii.member(jsii_name="repoUpgradeOnBootInput")
    def repo_upgrade_on_boot_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repoUpgradeOnBootInput"))

    @builtins.property
    @jsii.member(jsii_name="retriesInput")
    def retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retriesInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTaskInput")
    def scheduled_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsScheduledTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsScheduledTask"]]], jsii.get(self, "scheduledTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="securityConfigInput")
    def security_config_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccessSecurityGroupInput")
    def service_access_security_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccessSecurityGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceRoleInput")
    def service_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="stepsFileInput")
    def steps_file_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsStepsFile"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsStepsFile"]]], jsii.get(self, "stepsFileInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="taskDesiredCapacityInput")
    def task_desired_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "taskDesiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="taskEbsBlockDeviceInput")
    def task_ebs_block_device_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskEbsBlockDevice"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskEbsBlockDevice"]]], jsii.get(self, "taskEbsBlockDeviceInput"))

    @builtins.property
    @jsii.member(jsii_name="taskEbsOptimizedInput")
    def task_ebs_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "taskEbsOptimizedInput"))

    @builtins.property
    @jsii.member(jsii_name="taskInstanceTypesInput")
    def task_instance_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "taskInstanceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="taskLifecycleInput")
    def task_lifecycle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskLifecycleInput"))

    @builtins.property
    @jsii.member(jsii_name="taskMaxSizeInput")
    def task_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "taskMaxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="taskMinSizeInput")
    def task_min_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "taskMinSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="taskScalingDownPolicyInput")
    def task_scaling_down_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingDownPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingDownPolicy"]]], jsii.get(self, "taskScalingDownPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="taskScalingUpPolicyInput")
    def task_scaling_up_policy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingUpPolicy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingUpPolicy"]]], jsii.get(self, "taskScalingUpPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="taskUnitInput")
    def task_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationPoliciesInput")
    def termination_policies_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPolicies"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPolicies"]]], jsii.get(self, "terminationPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationProtectedInput")
    def termination_protected_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "terminationProtectedInput"))

    @builtins.property
    @jsii.member(jsii_name="visibleToAllUsersInput")
    def visible_to_all_users_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "visibleToAllUsersInput"))

    @builtins.property
    @jsii.member(jsii_name="additionalInfo")
    def additional_info(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "additionalInfo"))

    @additional_info.setter
    def additional_info(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b2a361350df8db1639eb0754828d88d5466aa060e60d45e60b2cb97c35d111e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalInfo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="additionalPrimarySecurityGroups")
    def additional_primary_security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalPrimarySecurityGroups"))

    @additional_primary_security_groups.setter
    def additional_primary_security_groups(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27d65ee786dd7be679d0b097c2ed129587c71ccde50d1886758c5bfed56b5dea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalPrimarySecurityGroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="additionalReplicaSecurityGroups")
    def additional_replica_security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalReplicaSecurityGroups"))

    @additional_replica_security_groups.setter
    def additional_replica_security_groups(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5870eef5f373cc9b462f829bb8d50ce6a52607018321b20bdd47245d21d8aab7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalReplicaSecurityGroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @availability_zones.setter
    def availability_zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80b5417a4d54d2340fd0850750c1512e461aefc32c8bac656b00ea7dc45c9f2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZones", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68a79c053d498c047c71fbc47cef436f81904ef46ec56d6ad55ab949debc00b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreDesiredCapacity")
    def core_desired_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "coreDesiredCapacity"))

    @core_desired_capacity.setter
    def core_desired_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cad8b1ca899674d9a87e4c73b143f4a7196c464c06cb1ffd83b92b3a4ce3dee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreDesiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreEbsOptimized")
    def core_ebs_optimized(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "coreEbsOptimized"))

    @core_ebs_optimized.setter
    def core_ebs_optimized(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd406520e498621bd34e6264b914bcb2b84c1e62912d228022850939b39348ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreEbsOptimized", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreInstanceTypes")
    def core_instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "coreInstanceTypes"))

    @core_instance_types.setter
    def core_instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a58e42627278c0fd359323849aacfcf720de97abcb02ce0c9e7e8d71e7cd8f22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreInstanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreLifecycle")
    def core_lifecycle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coreLifecycle"))

    @core_lifecycle.setter
    def core_lifecycle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cda135ebd8a65009d49ff964e15bad28bbd52a503e1845fc61900ef6d3e643c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreLifecycle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreMaxSize")
    def core_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "coreMaxSize"))

    @core_max_size.setter
    def core_max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a11de294363ba1fdb0371cdcbd54ab28937bc1a9a513a13f74c47e3c85022b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreMaxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreMinSize")
    def core_min_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "coreMinSize"))

    @core_min_size.setter
    def core_min_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c1b71f389793f7f47bd791ba9f7315dbe5eef733826e6ccb30a6a67b3d0bc6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreMinSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="coreUnit")
    def core_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coreUnit"))

    @core_unit.setter
    def core_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74479544bc58fdfa0f4b8d8803ae3bdb5ac29a3253f5af10c4719b03895aa999)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coreUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customAmiId")
    def custom_ami_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customAmiId"))

    @custom_ami_id.setter
    def custom_ami_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4bb560663490b4ab224d26a38ec6fdded2a62f855dd7f6fe0ba2da1e2754305)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAmiId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3c309b328f8b39da211cbf86793d32cb21fbc12edb7c9c4591c9d02b41698ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ebsRootVolumeSize")
    def ebs_root_volume_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ebsRootVolumeSize"))

    @ebs_root_volume_size.setter
    def ebs_root_volume_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013037d4cd33fc56b1e62a79eae25b66a266b4d1d9bfa5cd8a14b24a27c56781)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ebsRootVolumeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ec2KeyName")
    def ec2_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2KeyName"))

    @ec2_key_name.setter
    def ec2_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05b34ef9769fa766f03d3e188a8ca4fb1a31ef40f7d4f7e026c0ccaa3d4d6ed5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ec2KeyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exposeClusterId")
    def expose_cluster_id(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "exposeClusterId"))

    @expose_cluster_id.setter
    def expose_cluster_id(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dc5696a7430bdf45c7748308802b852e5a1af093355dcb760821ed6667f8834)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exposeClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7a4c68536527a7e00c9b7e5e0dbb531409217d976678cdf0294f5210f7fbee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jobFlowRole")
    def job_flow_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobFlowRole"))

    @job_flow_role.setter
    def job_flow_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d03f0631d010079087c8987548a6e9c733d5df9f8320c7f403e6d27af225a2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobFlowRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keepJobFlowAlive")
    def keep_job_flow_alive(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "keepJobFlowAlive"))

    @keep_job_flow_alive.setter
    def keep_job_flow_alive(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__464b9b53f0177a688d3c319dc2dc00554abc37306e5bfd4534f621fd420c5628)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepJobFlowAlive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logUri")
    def log_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logUri"))

    @log_uri.setter
    def log_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74b3ee8bf59e08fbacc2f5da14b82b7d025d4a1a88b1fad42c624dbed3d0f907)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedPrimarySecurityGroup")
    def managed_primary_security_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedPrimarySecurityGroup"))

    @managed_primary_security_group.setter
    def managed_primary_security_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e959de129818b7f222033092c4552aa89b1b0e70efc5c765b697f40ba3230bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedPrimarySecurityGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedReplicaSecurityGroup")
    def managed_replica_security_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedReplicaSecurityGroup"))

    @managed_replica_security_group.setter
    def managed_replica_security_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__363c3fae1b64863e897389bb9b95f58a26b5c6b11b53d6bf13b6f0beeaf78f15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedReplicaSecurityGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="masterEbsOptimized")
    def master_ebs_optimized(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "masterEbsOptimized"))

    @master_ebs_optimized.setter
    def master_ebs_optimized(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be5080425feffb5b1ede811b09dadcc22be4bc8ca046608c70a84d3458012921)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterEbsOptimized", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="masterInstanceTypes")
    def master_instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "masterInstanceTypes"))

    @master_instance_types.setter
    def master_instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2ca18db785ea4c9420947676f62124ad6fc5bcf015d61f5accb184dacb1498c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterInstanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="masterLifecycle")
    def master_lifecycle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterLifecycle"))

    @master_lifecycle.setter
    def master_lifecycle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__651be13b65c00030a48340c408f1ce18e341178984145fc7252a63bd870654b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterLifecycle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="masterTarget")
    def master_target(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "masterTarget"))

    @master_target.setter
    def master_target(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f12659e59d642754da97b3afd49a837887c533ed5d26be00a4eb6f6c606edb97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "masterTarget", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ff0eea9e608c2117598c5b0d6f55431f8b6eb41da364dee268c10914b9d31ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6912f7a0fc896c300854e3976660e76cd68770d0a687935669d8f1f24dc879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="releaseLabel")
    def release_label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "releaseLabel"))

    @release_label.setter
    def release_label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f17d1fdaf98ecf06ad223c3434d7b42d0e182c26378a891aa84084529125312)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "releaseLabel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repoUpgradeOnBoot")
    def repo_upgrade_on_boot(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoUpgradeOnBoot"))

    @repo_upgrade_on_boot.setter
    def repo_upgrade_on_boot(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e95372f5798d8cf5b168860f2adb43b5e43d7fac651d599ba1db83c2b8d2490a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repoUpgradeOnBoot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retries")
    def retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retries"))

    @retries.setter
    def retries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35de908783c0cb02dce0d329203d54375ffe5fb07c742452dec56dbb10c6f902)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="securityConfig")
    def security_config(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityConfig"))

    @security_config.setter
    def security_config(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7df878fb5151cb858fb49703f25da196b713252ca62c1f0fdc79a991a38395a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "securityConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccessSecurityGroup")
    def service_access_security_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccessSecurityGroup"))

    @service_access_security_group.setter
    def service_access_security_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__077c78b5986727564599617f8e8600c125873239bec9ae47a6d54dec7b034d75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccessSecurityGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a53bc6cee5e7fda1427dd3d922c2d7f94c47b80e976eb17620368c8ae0dcc964)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "strategy"))

    @strategy.setter
    def strategy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f91a06cfe4080a0e715802b6c74cef948c72100a1bb07be0de4e0afeaef317e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskDesiredCapacity")
    def task_desired_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "taskDesiredCapacity"))

    @task_desired_capacity.setter
    def task_desired_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b3e84210e1341e0e23be719e5edb341fb4632aa444c27f808957d0c1f6fda30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskDesiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskEbsOptimized")
    def task_ebs_optimized(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "taskEbsOptimized"))

    @task_ebs_optimized.setter
    def task_ebs_optimized(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e00e46fbb015a006513f33a18756f0da48dc6d2d38e63ef92440bacd9ac22d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskEbsOptimized", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskInstanceTypes")
    def task_instance_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "taskInstanceTypes"))

    @task_instance_types.setter
    def task_instance_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fee650df61d94a8081b5649b92dd93c1e8706525fa5ffd5dddc255079ac96479)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskInstanceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskLifecycle")
    def task_lifecycle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskLifecycle"))

    @task_lifecycle.setter
    def task_lifecycle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9904adc936d08d1e2beaed9b36ddaa825937957308de50c32c669a4f08971ba7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskLifecycle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskMaxSize")
    def task_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "taskMaxSize"))

    @task_max_size.setter
    def task_max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b43c2ca54fcefd5ea7f2341d8237b6d0d92a504b33f9bb02338099f46462f6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskMaxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskMinSize")
    def task_min_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "taskMinSize"))

    @task_min_size.setter
    def task_min_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed6d14f941ae7d804faec95d4c431916052dd90bbd3b8b0f7fe644064dee6af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskMinSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskUnit")
    def task_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskUnit"))

    @task_unit.setter
    def task_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10304a915b54da186d6c80d5c07b7888ca3a235c2dd12482037a269d3e45cb89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminationProtected")
    def termination_protected(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "terminationProtected"))

    @termination_protected.setter
    def termination_protected(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba345a94b0c9a15b09591a29145ff0243f844f42740c74b0705f485263d36680)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationProtected", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="visibleToAllUsers")
    def visible_to_all_users(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "visibleToAllUsers"))

    @visible_to_all_users.setter
    def visible_to_all_users(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecb4bd43632c7942dcab9ce39a416b46310c23e7912c5b6120537bdcc4ecfac5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibleToAllUsers", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsApplications",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "args": "args", "version": "version"},
)
class MrscalerAwsApplications:
    def __init__(
        self,
        *,
        name: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#name MrscalerAws#name}.
        :param args: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#args MrscalerAws#args}.
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#version MrscalerAws#version}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae56ff67def4e984b583ef2f691687d5fa3802db4aea118d44ee95d18a3b0d10)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if args is not None:
            self._values["args"] = args
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#name MrscalerAws#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#args MrscalerAws#args}.'''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#version MrscalerAws#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsApplications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsApplicationsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsApplicationsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ff528ef5242b5fd9673d7ac9dbd553147f946dd9eda49518cf12b687b22e43f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsApplicationsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88a1c4c6764eafd54f3c59c72fe9c69e533f253ad30881ccb43d2ed82e0eb688)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsApplicationsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcc6f783f605dfc2be76605fe4f102be595150fc6718f5e70ddc5533cd1cbc86)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5828f3ed8e499f83ba32ea999e80bf8c4dcff4a0e76703ffc3461a23d6707389)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd3de63ba96b2d81ab85d9055e8cc1593f92c26ebe72b63e2db8e8adec018812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsApplications]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsApplications]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsApplications]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40ad9e6cd84281eb9d05be5e0a96b6d32af4fc4de50bc8a731884f070df5ea63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsApplicationsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsApplicationsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f41b04bfe63ff2c9ebbee74d8f5ba7e5de006b026c7f0b2f4f4b99e8f05678b1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetArgs")
    def reset_args(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArgs", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property
    @jsii.member(jsii_name="argsInput")
    def args_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "argsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="args")
    def args(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "args"))

    @args.setter
    def args(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c94cabb01fec19b25178261973667d1c5a0f3fc273ff171605e17b9bfc3211ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "args", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2f2dc913c70489ea16df9d499320a4a91f957214e2adc4fb51c00ef3c5686ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8008e1a3c742c2a99fede8e80365a3668a4b28a97f3f22aa422eb6a11729358f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsApplications]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsApplications]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsApplications]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90d45f9e4211dd69e822efacd0db9a2953ac9bb28b5d7bdef169563262f4b441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsBootstrapActionsFile",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key"},
)
class MrscalerAwsBootstrapActionsFile:
    def __init__(self, *, bucket: builtins.str, key: builtins.str) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bucket MrscalerAws#bucket}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__705eb2415527798362a957d28d1d4e06a8b87c134584a90b9195c991013e482a)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bucket MrscalerAws#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsBootstrapActionsFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsBootstrapActionsFileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsBootstrapActionsFileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__12f98c648a56c287eff86f107363d2ddea6385437e31e428480f62cba89afa8c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsBootstrapActionsFileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4b7c4cd4e0616c0b09b4851e848641dac806e971bf27850abf1e8bcb9cde75b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsBootstrapActionsFileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9ef25eef165a69a7d111b9f86ee294f420841c0d81d77953d436fef5aac3bf5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__37f1990c32e2140d35adbdc612ee3e5eda0d98051a1367ee90ddb629aac1fd70)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1cc6b6cd84a5df5ce39b02b98ee7dff68d2533bfe5ec59fee2aa907ddf8cba78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsBootstrapActionsFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsBootstrapActionsFile]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsBootstrapActionsFile]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2db102dac528e68b8dc142a4465bf668538da0753ab887a8aee66582652eb4bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsBootstrapActionsFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsBootstrapActionsFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39150cf413760e30ace04b9424711bfe778ae1c75e9a680db4135eff5fb22563)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5243e5458156aecd3102d9ec6d0c1ef030df8707443430b51f19fe2624d3b436)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ad4b3fe3a6190df076d27ecab9b588eedb1a5ef6e619f8ff57c108fc914a6e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsBootstrapActionsFile]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsBootstrapActionsFile]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsBootstrapActionsFile]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e547957db1e5f9a6f57d402e42e3f6aa3a2ff1820a252a531b236ca6480a976)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsConfig",
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
        "strategy": "strategy",
        "additional_info": "additionalInfo",
        "additional_primary_security_groups": "additionalPrimarySecurityGroups",
        "additional_replica_security_groups": "additionalReplicaSecurityGroups",
        "applications": "applications",
        "availability_zones": "availabilityZones",
        "bootstrap_actions_file": "bootstrapActionsFile",
        "cluster_id": "clusterId",
        "configurations_file": "configurationsFile",
        "core_desired_capacity": "coreDesiredCapacity",
        "core_ebs_block_device": "coreEbsBlockDevice",
        "core_ebs_optimized": "coreEbsOptimized",
        "core_instance_types": "coreInstanceTypes",
        "core_lifecycle": "coreLifecycle",
        "core_max_size": "coreMaxSize",
        "core_min_size": "coreMinSize",
        "core_scaling_down_policy": "coreScalingDownPolicy",
        "core_scaling_up_policy": "coreScalingUpPolicy",
        "core_unit": "coreUnit",
        "custom_ami_id": "customAmiId",
        "description": "description",
        "ebs_root_volume_size": "ebsRootVolumeSize",
        "ec2_key_name": "ec2KeyName",
        "expose_cluster_id": "exposeClusterId",
        "id": "id",
        "instance_weights": "instanceWeights",
        "job_flow_role": "jobFlowRole",
        "keep_job_flow_alive": "keepJobFlowAlive",
        "log_uri": "logUri",
        "managed_primary_security_group": "managedPrimarySecurityGroup",
        "managed_replica_security_group": "managedReplicaSecurityGroup",
        "master_ebs_block_device": "masterEbsBlockDevice",
        "master_ebs_optimized": "masterEbsOptimized",
        "master_instance_types": "masterInstanceTypes",
        "master_lifecycle": "masterLifecycle",
        "master_target": "masterTarget",
        "provisioning_timeout": "provisioningTimeout",
        "region": "region",
        "release_label": "releaseLabel",
        "repo_upgrade_on_boot": "repoUpgradeOnBoot",
        "retries": "retries",
        "scheduled_task": "scheduledTask",
        "security_config": "securityConfig",
        "service_access_security_group": "serviceAccessSecurityGroup",
        "service_role": "serviceRole",
        "steps_file": "stepsFile",
        "tags": "tags",
        "task_desired_capacity": "taskDesiredCapacity",
        "task_ebs_block_device": "taskEbsBlockDevice",
        "task_ebs_optimized": "taskEbsOptimized",
        "task_instance_types": "taskInstanceTypes",
        "task_lifecycle": "taskLifecycle",
        "task_max_size": "taskMaxSize",
        "task_min_size": "taskMinSize",
        "task_scaling_down_policy": "taskScalingDownPolicy",
        "task_scaling_up_policy": "taskScalingUpPolicy",
        "task_unit": "taskUnit",
        "termination_policies": "terminationPolicies",
        "termination_protected": "terminationProtected",
        "visible_to_all_users": "visibleToAllUsers",
    },
)
class MrscalerAwsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        strategy: builtins.str,
        additional_info: typing.Optional[builtins.str] = None,
        additional_primary_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_replica_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        applications: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsApplications, typing.Dict[builtins.str, typing.Any]]]]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap_actions_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsBootstrapActionsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: typing.Optional[builtins.str] = None,
        configurations_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsConfigurationsFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_desired_capacity: typing.Optional[jsii.Number] = None,
        core_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        core_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        core_lifecycle: typing.Optional[builtins.str] = None,
        core_max_size: typing.Optional[jsii.Number] = None,
        core_min_size: typing.Optional[jsii.Number] = None,
        core_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsCoreScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        core_unit: typing.Optional[builtins.str] = None,
        custom_ami_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        ebs_root_volume_size: typing.Optional[jsii.Number] = None,
        ec2_key_name: typing.Optional[builtins.str] = None,
        expose_cluster_id: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_weights: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsInstanceWeights", typing.Dict[builtins.str, typing.Any]]]]] = None,
        job_flow_role: typing.Optional[builtins.str] = None,
        keep_job_flow_alive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_uri: typing.Optional[builtins.str] = None,
        managed_primary_security_group: typing.Optional[builtins.str] = None,
        managed_replica_security_group: typing.Optional[builtins.str] = None,
        master_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsMasterEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]]] = None,
        master_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        master_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        master_lifecycle: typing.Optional[builtins.str] = None,
        master_target: typing.Optional[jsii.Number] = None,
        provisioning_timeout: typing.Optional[typing.Union["MrscalerAwsProvisioningTimeout", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
        release_label: typing.Optional[builtins.str] = None,
        repo_upgrade_on_boot: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        security_config: typing.Optional[builtins.str] = None,
        service_access_security_group: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[builtins.str] = None,
        steps_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsStepsFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_desired_capacity: typing.Optional[jsii.Number] = None,
        task_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskEbsBlockDevice", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        task_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        task_lifecycle: typing.Optional[builtins.str] = None,
        task_max_size: typing.Optional[jsii.Number] = None,
        task_min_size: typing.Optional[jsii.Number] = None,
        task_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskScalingDownPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTaskScalingUpPolicy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        task_unit: typing.Optional[builtins.str] = None,
        termination_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTerminationPolicies", typing.Dict[builtins.str, typing.Any]]]]] = None,
        termination_protected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        visible_to_all_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#name MrscalerAws#name}.
        :param strategy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#strategy MrscalerAws#strategy}.
        :param additional_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_info MrscalerAws#additional_info}.
        :param additional_primary_security_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_primary_security_groups MrscalerAws#additional_primary_security_groups}.
        :param additional_replica_security_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_replica_security_groups MrscalerAws#additional_replica_security_groups}.
        :param applications: applications block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#applications MrscalerAws#applications}
        :param availability_zones: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#availability_zones MrscalerAws#availability_zones}.
        :param bootstrap_actions_file: bootstrap_actions_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bootstrap_actions_file MrscalerAws#bootstrap_actions_file}
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cluster_id MrscalerAws#cluster_id}.
        :param configurations_file: configurations_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#configurations_file MrscalerAws#configurations_file}
        :param core_desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_desired_capacity MrscalerAws#core_desired_capacity}.
        :param core_ebs_block_device: core_ebs_block_device block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_ebs_block_device MrscalerAws#core_ebs_block_device}
        :param core_ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_ebs_optimized MrscalerAws#core_ebs_optimized}.
        :param core_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_instance_types MrscalerAws#core_instance_types}.
        :param core_lifecycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_lifecycle MrscalerAws#core_lifecycle}.
        :param core_max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_max_size MrscalerAws#core_max_size}.
        :param core_min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_min_size MrscalerAws#core_min_size}.
        :param core_scaling_down_policy: core_scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_scaling_down_policy MrscalerAws#core_scaling_down_policy}
        :param core_scaling_up_policy: core_scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_scaling_up_policy MrscalerAws#core_scaling_up_policy}
        :param core_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_unit MrscalerAws#core_unit}.
        :param custom_ami_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#custom_ami_id MrscalerAws#custom_ami_id}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#description MrscalerAws#description}.
        :param ebs_root_volume_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#ebs_root_volume_size MrscalerAws#ebs_root_volume_size}.
        :param ec2_key_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#ec2_key_name MrscalerAws#ec2_key_name}.
        :param expose_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#expose_cluster_id MrscalerAws#expose_cluster_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#id MrscalerAws#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_weights: instance_weights block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_weights MrscalerAws#instance_weights}
        :param job_flow_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#job_flow_role MrscalerAws#job_flow_role}.
        :param keep_job_flow_alive: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#keep_job_flow_alive MrscalerAws#keep_job_flow_alive}.
        :param log_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#log_uri MrscalerAws#log_uri}.
        :param managed_primary_security_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#managed_primary_security_group MrscalerAws#managed_primary_security_group}.
        :param managed_replica_security_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#managed_replica_security_group MrscalerAws#managed_replica_security_group}.
        :param master_ebs_block_device: master_ebs_block_device block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_ebs_block_device MrscalerAws#master_ebs_block_device}
        :param master_ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_ebs_optimized MrscalerAws#master_ebs_optimized}.
        :param master_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_instance_types MrscalerAws#master_instance_types}.
        :param master_lifecycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_lifecycle MrscalerAws#master_lifecycle}.
        :param master_target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_target MrscalerAws#master_target}.
        :param provisioning_timeout: provisioning_timeout block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#provisioning_timeout MrscalerAws#provisioning_timeout}
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#region MrscalerAws#region}.
        :param release_label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#release_label MrscalerAws#release_label}.
        :param repo_upgrade_on_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#repo_upgrade_on_boot MrscalerAws#repo_upgrade_on_boot}.
        :param retries: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#retries MrscalerAws#retries}.
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#scheduled_task MrscalerAws#scheduled_task}
        :param security_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#security_config MrscalerAws#security_config}.
        :param service_access_security_group: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#service_access_security_group MrscalerAws#service_access_security_group}.
        :param service_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#service_role MrscalerAws#service_role}.
        :param steps_file: steps_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#steps_file MrscalerAws#steps_file}
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#tags MrscalerAws#tags}
        :param task_desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_desired_capacity MrscalerAws#task_desired_capacity}.
        :param task_ebs_block_device: task_ebs_block_device block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_ebs_block_device MrscalerAws#task_ebs_block_device}
        :param task_ebs_optimized: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_ebs_optimized MrscalerAws#task_ebs_optimized}.
        :param task_instance_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_instance_types MrscalerAws#task_instance_types}.
        :param task_lifecycle: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_lifecycle MrscalerAws#task_lifecycle}.
        :param task_max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_max_size MrscalerAws#task_max_size}.
        :param task_min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_min_size MrscalerAws#task_min_size}.
        :param task_scaling_down_policy: task_scaling_down_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_scaling_down_policy MrscalerAws#task_scaling_down_policy}
        :param task_scaling_up_policy: task_scaling_up_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_scaling_up_policy MrscalerAws#task_scaling_up_policy}
        :param task_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_unit MrscalerAws#task_unit}.
        :param termination_policies: termination_policies block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#termination_policies MrscalerAws#termination_policies}
        :param termination_protected: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#termination_protected MrscalerAws#termination_protected}.
        :param visible_to_all_users: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#visible_to_all_users MrscalerAws#visible_to_all_users}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(provisioning_timeout, dict):
            provisioning_timeout = MrscalerAwsProvisioningTimeout(**provisioning_timeout)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fd3f84c4798aa9acffa9f47fd926fb3a611a32927961b59ee0010b4da12c2bc)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument additional_info", value=additional_info, expected_type=type_hints["additional_info"])
            check_type(argname="argument additional_primary_security_groups", value=additional_primary_security_groups, expected_type=type_hints["additional_primary_security_groups"])
            check_type(argname="argument additional_replica_security_groups", value=additional_replica_security_groups, expected_type=type_hints["additional_replica_security_groups"])
            check_type(argname="argument applications", value=applications, expected_type=type_hints["applications"])
            check_type(argname="argument availability_zones", value=availability_zones, expected_type=type_hints["availability_zones"])
            check_type(argname="argument bootstrap_actions_file", value=bootstrap_actions_file, expected_type=type_hints["bootstrap_actions_file"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument configurations_file", value=configurations_file, expected_type=type_hints["configurations_file"])
            check_type(argname="argument core_desired_capacity", value=core_desired_capacity, expected_type=type_hints["core_desired_capacity"])
            check_type(argname="argument core_ebs_block_device", value=core_ebs_block_device, expected_type=type_hints["core_ebs_block_device"])
            check_type(argname="argument core_ebs_optimized", value=core_ebs_optimized, expected_type=type_hints["core_ebs_optimized"])
            check_type(argname="argument core_instance_types", value=core_instance_types, expected_type=type_hints["core_instance_types"])
            check_type(argname="argument core_lifecycle", value=core_lifecycle, expected_type=type_hints["core_lifecycle"])
            check_type(argname="argument core_max_size", value=core_max_size, expected_type=type_hints["core_max_size"])
            check_type(argname="argument core_min_size", value=core_min_size, expected_type=type_hints["core_min_size"])
            check_type(argname="argument core_scaling_down_policy", value=core_scaling_down_policy, expected_type=type_hints["core_scaling_down_policy"])
            check_type(argname="argument core_scaling_up_policy", value=core_scaling_up_policy, expected_type=type_hints["core_scaling_up_policy"])
            check_type(argname="argument core_unit", value=core_unit, expected_type=type_hints["core_unit"])
            check_type(argname="argument custom_ami_id", value=custom_ami_id, expected_type=type_hints["custom_ami_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument ebs_root_volume_size", value=ebs_root_volume_size, expected_type=type_hints["ebs_root_volume_size"])
            check_type(argname="argument ec2_key_name", value=ec2_key_name, expected_type=type_hints["ec2_key_name"])
            check_type(argname="argument expose_cluster_id", value=expose_cluster_id, expected_type=type_hints["expose_cluster_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_weights", value=instance_weights, expected_type=type_hints["instance_weights"])
            check_type(argname="argument job_flow_role", value=job_flow_role, expected_type=type_hints["job_flow_role"])
            check_type(argname="argument keep_job_flow_alive", value=keep_job_flow_alive, expected_type=type_hints["keep_job_flow_alive"])
            check_type(argname="argument log_uri", value=log_uri, expected_type=type_hints["log_uri"])
            check_type(argname="argument managed_primary_security_group", value=managed_primary_security_group, expected_type=type_hints["managed_primary_security_group"])
            check_type(argname="argument managed_replica_security_group", value=managed_replica_security_group, expected_type=type_hints["managed_replica_security_group"])
            check_type(argname="argument master_ebs_block_device", value=master_ebs_block_device, expected_type=type_hints["master_ebs_block_device"])
            check_type(argname="argument master_ebs_optimized", value=master_ebs_optimized, expected_type=type_hints["master_ebs_optimized"])
            check_type(argname="argument master_instance_types", value=master_instance_types, expected_type=type_hints["master_instance_types"])
            check_type(argname="argument master_lifecycle", value=master_lifecycle, expected_type=type_hints["master_lifecycle"])
            check_type(argname="argument master_target", value=master_target, expected_type=type_hints["master_target"])
            check_type(argname="argument provisioning_timeout", value=provisioning_timeout, expected_type=type_hints["provisioning_timeout"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument release_label", value=release_label, expected_type=type_hints["release_label"])
            check_type(argname="argument repo_upgrade_on_boot", value=repo_upgrade_on_boot, expected_type=type_hints["repo_upgrade_on_boot"])
            check_type(argname="argument retries", value=retries, expected_type=type_hints["retries"])
            check_type(argname="argument scheduled_task", value=scheduled_task, expected_type=type_hints["scheduled_task"])
            check_type(argname="argument security_config", value=security_config, expected_type=type_hints["security_config"])
            check_type(argname="argument service_access_security_group", value=service_access_security_group, expected_type=type_hints["service_access_security_group"])
            check_type(argname="argument service_role", value=service_role, expected_type=type_hints["service_role"])
            check_type(argname="argument steps_file", value=steps_file, expected_type=type_hints["steps_file"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument task_desired_capacity", value=task_desired_capacity, expected_type=type_hints["task_desired_capacity"])
            check_type(argname="argument task_ebs_block_device", value=task_ebs_block_device, expected_type=type_hints["task_ebs_block_device"])
            check_type(argname="argument task_ebs_optimized", value=task_ebs_optimized, expected_type=type_hints["task_ebs_optimized"])
            check_type(argname="argument task_instance_types", value=task_instance_types, expected_type=type_hints["task_instance_types"])
            check_type(argname="argument task_lifecycle", value=task_lifecycle, expected_type=type_hints["task_lifecycle"])
            check_type(argname="argument task_max_size", value=task_max_size, expected_type=type_hints["task_max_size"])
            check_type(argname="argument task_min_size", value=task_min_size, expected_type=type_hints["task_min_size"])
            check_type(argname="argument task_scaling_down_policy", value=task_scaling_down_policy, expected_type=type_hints["task_scaling_down_policy"])
            check_type(argname="argument task_scaling_up_policy", value=task_scaling_up_policy, expected_type=type_hints["task_scaling_up_policy"])
            check_type(argname="argument task_unit", value=task_unit, expected_type=type_hints["task_unit"])
            check_type(argname="argument termination_policies", value=termination_policies, expected_type=type_hints["termination_policies"])
            check_type(argname="argument termination_protected", value=termination_protected, expected_type=type_hints["termination_protected"])
            check_type(argname="argument visible_to_all_users", value=visible_to_all_users, expected_type=type_hints["visible_to_all_users"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "strategy": strategy,
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
        if additional_info is not None:
            self._values["additional_info"] = additional_info
        if additional_primary_security_groups is not None:
            self._values["additional_primary_security_groups"] = additional_primary_security_groups
        if additional_replica_security_groups is not None:
            self._values["additional_replica_security_groups"] = additional_replica_security_groups
        if applications is not None:
            self._values["applications"] = applications
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if bootstrap_actions_file is not None:
            self._values["bootstrap_actions_file"] = bootstrap_actions_file
        if cluster_id is not None:
            self._values["cluster_id"] = cluster_id
        if configurations_file is not None:
            self._values["configurations_file"] = configurations_file
        if core_desired_capacity is not None:
            self._values["core_desired_capacity"] = core_desired_capacity
        if core_ebs_block_device is not None:
            self._values["core_ebs_block_device"] = core_ebs_block_device
        if core_ebs_optimized is not None:
            self._values["core_ebs_optimized"] = core_ebs_optimized
        if core_instance_types is not None:
            self._values["core_instance_types"] = core_instance_types
        if core_lifecycle is not None:
            self._values["core_lifecycle"] = core_lifecycle
        if core_max_size is not None:
            self._values["core_max_size"] = core_max_size
        if core_min_size is not None:
            self._values["core_min_size"] = core_min_size
        if core_scaling_down_policy is not None:
            self._values["core_scaling_down_policy"] = core_scaling_down_policy
        if core_scaling_up_policy is not None:
            self._values["core_scaling_up_policy"] = core_scaling_up_policy
        if core_unit is not None:
            self._values["core_unit"] = core_unit
        if custom_ami_id is not None:
            self._values["custom_ami_id"] = custom_ami_id
        if description is not None:
            self._values["description"] = description
        if ebs_root_volume_size is not None:
            self._values["ebs_root_volume_size"] = ebs_root_volume_size
        if ec2_key_name is not None:
            self._values["ec2_key_name"] = ec2_key_name
        if expose_cluster_id is not None:
            self._values["expose_cluster_id"] = expose_cluster_id
        if id is not None:
            self._values["id"] = id
        if instance_weights is not None:
            self._values["instance_weights"] = instance_weights
        if job_flow_role is not None:
            self._values["job_flow_role"] = job_flow_role
        if keep_job_flow_alive is not None:
            self._values["keep_job_flow_alive"] = keep_job_flow_alive
        if log_uri is not None:
            self._values["log_uri"] = log_uri
        if managed_primary_security_group is not None:
            self._values["managed_primary_security_group"] = managed_primary_security_group
        if managed_replica_security_group is not None:
            self._values["managed_replica_security_group"] = managed_replica_security_group
        if master_ebs_block_device is not None:
            self._values["master_ebs_block_device"] = master_ebs_block_device
        if master_ebs_optimized is not None:
            self._values["master_ebs_optimized"] = master_ebs_optimized
        if master_instance_types is not None:
            self._values["master_instance_types"] = master_instance_types
        if master_lifecycle is not None:
            self._values["master_lifecycle"] = master_lifecycle
        if master_target is not None:
            self._values["master_target"] = master_target
        if provisioning_timeout is not None:
            self._values["provisioning_timeout"] = provisioning_timeout
        if region is not None:
            self._values["region"] = region
        if release_label is not None:
            self._values["release_label"] = release_label
        if repo_upgrade_on_boot is not None:
            self._values["repo_upgrade_on_boot"] = repo_upgrade_on_boot
        if retries is not None:
            self._values["retries"] = retries
        if scheduled_task is not None:
            self._values["scheduled_task"] = scheduled_task
        if security_config is not None:
            self._values["security_config"] = security_config
        if service_access_security_group is not None:
            self._values["service_access_security_group"] = service_access_security_group
        if service_role is not None:
            self._values["service_role"] = service_role
        if steps_file is not None:
            self._values["steps_file"] = steps_file
        if tags is not None:
            self._values["tags"] = tags
        if task_desired_capacity is not None:
            self._values["task_desired_capacity"] = task_desired_capacity
        if task_ebs_block_device is not None:
            self._values["task_ebs_block_device"] = task_ebs_block_device
        if task_ebs_optimized is not None:
            self._values["task_ebs_optimized"] = task_ebs_optimized
        if task_instance_types is not None:
            self._values["task_instance_types"] = task_instance_types
        if task_lifecycle is not None:
            self._values["task_lifecycle"] = task_lifecycle
        if task_max_size is not None:
            self._values["task_max_size"] = task_max_size
        if task_min_size is not None:
            self._values["task_min_size"] = task_min_size
        if task_scaling_down_policy is not None:
            self._values["task_scaling_down_policy"] = task_scaling_down_policy
        if task_scaling_up_policy is not None:
            self._values["task_scaling_up_policy"] = task_scaling_up_policy
        if task_unit is not None:
            self._values["task_unit"] = task_unit
        if termination_policies is not None:
            self._values["termination_policies"] = termination_policies
        if termination_protected is not None:
            self._values["termination_protected"] = termination_protected
        if visible_to_all_users is not None:
            self._values["visible_to_all_users"] = visible_to_all_users

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#name MrscalerAws#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def strategy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#strategy MrscalerAws#strategy}.'''
        result = self._values.get("strategy")
        assert result is not None, "Required property 'strategy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_info(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_info MrscalerAws#additional_info}.'''
        result = self._values.get("additional_info")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def additional_primary_security_groups(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_primary_security_groups MrscalerAws#additional_primary_security_groups}.'''
        result = self._values.get("additional_primary_security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def additional_replica_security_groups(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#additional_replica_security_groups MrscalerAws#additional_replica_security_groups}.'''
        result = self._values.get("additional_replica_security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def applications(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsApplications]]]:
        '''applications block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#applications MrscalerAws#applications}
        '''
        result = self._values.get("applications")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsApplications]]], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#availability_zones MrscalerAws#availability_zones}.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bootstrap_actions_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsBootstrapActionsFile]]]:
        '''bootstrap_actions_file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bootstrap_actions_file MrscalerAws#bootstrap_actions_file}
        '''
        result = self._values.get("bootstrap_actions_file")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsBootstrapActionsFile]]], result)

    @builtins.property
    def cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cluster_id MrscalerAws#cluster_id}.'''
        result = self._values.get("cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configurations_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsConfigurationsFile"]]]:
        '''configurations_file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#configurations_file MrscalerAws#configurations_file}
        '''
        result = self._values.get("configurations_file")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsConfigurationsFile"]]], result)

    @builtins.property
    def core_desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_desired_capacity MrscalerAws#core_desired_capacity}.'''
        result = self._values.get("core_desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def core_ebs_block_device(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreEbsBlockDevice"]]]:
        '''core_ebs_block_device block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_ebs_block_device MrscalerAws#core_ebs_block_device}
        '''
        result = self._values.get("core_ebs_block_device")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreEbsBlockDevice"]]], result)

    @builtins.property
    def core_ebs_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_ebs_optimized MrscalerAws#core_ebs_optimized}.'''
        result = self._values.get("core_ebs_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def core_instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_instance_types MrscalerAws#core_instance_types}.'''
        result = self._values.get("core_instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def core_lifecycle(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_lifecycle MrscalerAws#core_lifecycle}.'''
        result = self._values.get("core_lifecycle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def core_max_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_max_size MrscalerAws#core_max_size}.'''
        result = self._values.get("core_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def core_min_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_min_size MrscalerAws#core_min_size}.'''
        result = self._values.get("core_min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def core_scaling_down_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingDownPolicy"]]]:
        '''core_scaling_down_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_scaling_down_policy MrscalerAws#core_scaling_down_policy}
        '''
        result = self._values.get("core_scaling_down_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingDownPolicy"]]], result)

    @builtins.property
    def core_scaling_up_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingUpPolicy"]]]:
        '''core_scaling_up_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_scaling_up_policy MrscalerAws#core_scaling_up_policy}
        '''
        result = self._values.get("core_scaling_up_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsCoreScalingUpPolicy"]]], result)

    @builtins.property
    def core_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#core_unit MrscalerAws#core_unit}.'''
        result = self._values.get("core_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_ami_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#custom_ami_id MrscalerAws#custom_ami_id}.'''
        result = self._values.get("custom_ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#description MrscalerAws#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs_root_volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#ebs_root_volume_size MrscalerAws#ebs_root_volume_size}.'''
        result = self._values.get("ebs_root_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2_key_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#ec2_key_name MrscalerAws#ec2_key_name}.'''
        result = self._values.get("ec2_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expose_cluster_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#expose_cluster_id MrscalerAws#expose_cluster_id}.'''
        result = self._values.get("expose_cluster_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#id MrscalerAws#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_weights(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsInstanceWeights"]]]:
        '''instance_weights block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_weights MrscalerAws#instance_weights}
        '''
        result = self._values.get("instance_weights")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsInstanceWeights"]]], result)

    @builtins.property
    def job_flow_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#job_flow_role MrscalerAws#job_flow_role}.'''
        result = self._values.get("job_flow_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keep_job_flow_alive(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#keep_job_flow_alive MrscalerAws#keep_job_flow_alive}.'''
        result = self._values.get("keep_job_flow_alive")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#log_uri MrscalerAws#log_uri}.'''
        result = self._values.get("log_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_primary_security_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#managed_primary_security_group MrscalerAws#managed_primary_security_group}.'''
        result = self._values.get("managed_primary_security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_replica_security_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#managed_replica_security_group MrscalerAws#managed_replica_security_group}.'''
        result = self._values.get("managed_replica_security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_ebs_block_device(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsMasterEbsBlockDevice"]]]:
        '''master_ebs_block_device block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_ebs_block_device MrscalerAws#master_ebs_block_device}
        '''
        result = self._values.get("master_ebs_block_device")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsMasterEbsBlockDevice"]]], result)

    @builtins.property
    def master_ebs_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_ebs_optimized MrscalerAws#master_ebs_optimized}.'''
        result = self._values.get("master_ebs_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def master_instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_instance_types MrscalerAws#master_instance_types}.'''
        result = self._values.get("master_instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def master_lifecycle(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_lifecycle MrscalerAws#master_lifecycle}.'''
        result = self._values.get("master_lifecycle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_target(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#master_target MrscalerAws#master_target}.'''
        result = self._values.get("master_target")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def provisioning_timeout(self) -> typing.Optional["MrscalerAwsProvisioningTimeout"]:
        '''provisioning_timeout block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#provisioning_timeout MrscalerAws#provisioning_timeout}
        '''
        result = self._values.get("provisioning_timeout")
        return typing.cast(typing.Optional["MrscalerAwsProvisioningTimeout"], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#region MrscalerAws#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#release_label MrscalerAws#release_label}.'''
        result = self._values.get("release_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repo_upgrade_on_boot(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#repo_upgrade_on_boot MrscalerAws#repo_upgrade_on_boot}.'''
        result = self._values.get("repo_upgrade_on_boot")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#retries MrscalerAws#retries}.'''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def scheduled_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsScheduledTask"]]]:
        '''scheduled_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#scheduled_task MrscalerAws#scheduled_task}
        '''
        result = self._values.get("scheduled_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsScheduledTask"]]], result)

    @builtins.property
    def security_config(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#security_config MrscalerAws#security_config}.'''
        result = self._values.get("security_config")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_access_security_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#service_access_security_group MrscalerAws#service_access_security_group}.'''
        result = self._values.get("service_access_security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#service_role MrscalerAws#service_role}.'''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def steps_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsStepsFile"]]]:
        '''steps_file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#steps_file MrscalerAws#steps_file}
        '''
        result = self._values.get("steps_file")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsStepsFile"]]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#tags MrscalerAws#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTags"]]], result)

    @builtins.property
    def task_desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_desired_capacity MrscalerAws#task_desired_capacity}.'''
        result = self._values.get("task_desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def task_ebs_block_device(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskEbsBlockDevice"]]]:
        '''task_ebs_block_device block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_ebs_block_device MrscalerAws#task_ebs_block_device}
        '''
        result = self._values.get("task_ebs_block_device")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskEbsBlockDevice"]]], result)

    @builtins.property
    def task_ebs_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_ebs_optimized MrscalerAws#task_ebs_optimized}.'''
        result = self._values.get("task_ebs_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def task_instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_instance_types MrscalerAws#task_instance_types}.'''
        result = self._values.get("task_instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def task_lifecycle(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_lifecycle MrscalerAws#task_lifecycle}.'''
        result = self._values.get("task_lifecycle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task_max_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_max_size MrscalerAws#task_max_size}.'''
        result = self._values.get("task_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def task_min_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_min_size MrscalerAws#task_min_size}.'''
        result = self._values.get("task_min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def task_scaling_down_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingDownPolicy"]]]:
        '''task_scaling_down_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_scaling_down_policy MrscalerAws#task_scaling_down_policy}
        '''
        result = self._values.get("task_scaling_down_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingDownPolicy"]]], result)

    @builtins.property
    def task_scaling_up_policy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingUpPolicy"]]]:
        '''task_scaling_up_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_scaling_up_policy MrscalerAws#task_scaling_up_policy}
        '''
        result = self._values.get("task_scaling_up_policy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTaskScalingUpPolicy"]]], result)

    @builtins.property
    def task_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_unit MrscalerAws#task_unit}.'''
        result = self._values.get("task_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def termination_policies(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPolicies"]]]:
        '''termination_policies block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#termination_policies MrscalerAws#termination_policies}
        '''
        result = self._values.get("termination_policies")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPolicies"]]], result)

    @builtins.property
    def termination_protected(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#termination_protected MrscalerAws#termination_protected}.'''
        result = self._values.get("termination_protected")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def visible_to_all_users(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#visible_to_all_users MrscalerAws#visible_to_all_users}.'''
        result = self._values.get("visible_to_all_users")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsConfigurationsFile",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key"},
)
class MrscalerAwsConfigurationsFile:
    def __init__(self, *, bucket: builtins.str, key: builtins.str) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bucket MrscalerAws#bucket}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e58a27a2ef3a2f811fa7ed5f8dc32c9795f7b0d6c99a5c11ddbf77db08b64c5)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bucket MrscalerAws#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsConfigurationsFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsConfigurationsFileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsConfigurationsFileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea2fef2def68cfa74a0c0bfe5317c0b2ebcca8727376efd2052f66e31d802e93)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsConfigurationsFileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8edf143bd6144d0d82ee9534f87bc04bfb3e43512b60ceadd8529cf59a087e23)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsConfigurationsFileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df5e413199c4ebafe258eba81bbd35aa411a82d9d30169882830b01010f12577)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fb104fbabcf850af0f57f5ebc9205abbddc8c4b4a440ba79662d5279d51205e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2cc5c6cb0e1f82b64629b19f377a8d65073f5785406bae7c99e056f00793e90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsConfigurationsFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsConfigurationsFile]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsConfigurationsFile]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c816e3530d807924ba2d492bef9713f78836dad1f26ebee2bc9499bbe43bede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsConfigurationsFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsConfigurationsFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d719f59345fb014b89f72cd782a1538e15ae585310b76a4a011b2a9472d0859c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a18e34aebfbd8cd271b0aa3b43c50c63d0db621fe9b4952183d60b98552716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3928a7c1fed04cb77104e31756650ac9e67d10ff7a4a4b2b29c41ccf72d04e52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsConfigurationsFile]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsConfigurationsFile]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsConfigurationsFile]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f3bf0712b03997fbad43eb6a1bcfed2076ef79c60af5aee4a91f8096f97d632)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreEbsBlockDevice",
    jsii_struct_bases=[],
    name_mapping={
        "size_in_gb": "sizeInGb",
        "volume_type": "volumeType",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class MrscalerAwsCoreEbsBlockDevice:
    def __init__(
        self,
        *,
        size_in_gb: jsii.Number,
        volume_type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size_in_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#size_in_gb MrscalerAws#size_in_gb}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volume_type MrscalerAws#volume_type}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#iops MrscalerAws#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volumes_per_instance MrscalerAws#volumes_per_instance}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac54b248fa050634f592a97b3b16bef65223bcb1036b0ca8911b9e8dde555dc)
            check_type(argname="argument size_in_gb", value=size_in_gb, expected_type=type_hints["size_in_gb"])
            check_type(argname="argument volume_type", value=volume_type, expected_type=type_hints["volume_type"])
            check_type(argname="argument iops", value=iops, expected_type=type_hints["iops"])
            check_type(argname="argument volumes_per_instance", value=volumes_per_instance, expected_type=type_hints["volumes_per_instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "size_in_gb": size_in_gb,
            "volume_type": volume_type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size_in_gb(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#size_in_gb MrscalerAws#size_in_gb}.'''
        result = self._values.get("size_in_gb")
        assert result is not None, "Required property 'size_in_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def volume_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volume_type MrscalerAws#volume_type}.'''
        result = self._values.get("volume_type")
        assert result is not None, "Required property 'volume_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#iops MrscalerAws#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volumes_per_instance MrscalerAws#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsCoreEbsBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsCoreEbsBlockDeviceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreEbsBlockDeviceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5433d2b9ccd4e000d552c20d8f1c038b8af0dba0fba75acf63c2923bd063474)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsCoreEbsBlockDeviceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f70c556ea463921e4af695153b70d54fe0f0d5f610c8cb53d7bd90d73d566b3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsCoreEbsBlockDeviceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f45b59cbe9ac10e704acfabcaf05e89aa16ed8874b78347a3d3c96674252530)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f47216f214bcafc529839e4f4ac64f41bc0f708b7da8b4bf0a7daeb14c565e51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82edb5484e3963848f51252b5385cad949c9086efb8fce4da1af882a014b09a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreEbsBlockDevice]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreEbsBlockDevice]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreEbsBlockDevice]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63dc14ba834336b334dec00764d86189d8f999fe1fa92736fe1546d3d50b9fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsCoreEbsBlockDeviceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreEbsBlockDeviceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6b7da1e03ef904001d1909b40dba7e960c82f9fc2aba7c11803f5877b227113f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetVolumesPerInstance")
    def reset_volumes_per_instance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumesPerInstance", []))

    @builtins.property
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInGbInput")
    def size_in_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInGbInput"))

    @builtins.property
    @jsii.member(jsii_name="volumesPerInstanceInput")
    def volumes_per_instance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumesPerInstanceInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9319afe2a59862ca02f5b4344ecaba3cfb671f70dfbd432586fc2967b6ca4ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeInGb")
    def size_in_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeInGb"))

    @size_in_gb.setter
    def size_in_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48b0130f3e1271e3e8f3ef80605e42ffa48de4b3acdff6c21d6d4c4cd245f662)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeInGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumesPerInstance")
    def volumes_per_instance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumesPerInstance"))

    @volumes_per_instance.setter
    def volumes_per_instance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38011d5d331d5f3d5a4413c0df2ea14e01e4bee394133f629f661897e0cadc4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumesPerInstance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ab5f03e3d561de2e6a6ef53b07290c4bd984ac971c3d523a6978ae3cd8a42ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreEbsBlockDevice]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreEbsBlockDevice]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreEbsBlockDevice]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d34219a4e8373926902b85eeb9d7abb909e8c6b8aa70b7a738075d49630419f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreScalingDownPolicy",
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
        "maximum": "maximum",
        "max_target_capacity": "maxTargetCapacity",
        "minimum": "minimum",
        "min_target_capacity": "minTargetCapacity",
        "operator": "operator",
        "period": "period",
        "statistic": "statistic",
        "target": "target",
    },
)
class MrscalerAwsCoreScalingDownPolicy:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        policy_name: builtins.str,
        threshold: jsii.Number,
        unit: builtins.str,
        action_type: typing.Optional[builtins.str] = None,
        adjustment: typing.Optional[builtins.str] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        maximum: typing.Optional[builtins.str] = None,
        max_target_capacity: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        min_target_capacity: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.
        :param dimensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.
        :param max_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.
        :param min_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53a28d95f56e0d7879e294434228c1b77137bf2f146dbe55f9198702b9dd16a1)
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
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument max_target_capacity", value=max_target_capacity, expected_type=type_hints["max_target_capacity"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
            check_type(argname="argument min_target_capacity", value=min_target_capacity, expected_type=type_hints["min_target_capacity"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
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
        if maximum is not None:
            self._values["maximum"] = maximum
        if max_target_capacity is not None:
            self._values["max_target_capacity"] = max_target_capacity
        if minimum is not None:
            self._values["minimum"] = minimum
        if min_target_capacity is not None:
            self._values["min_target_capacity"] = min_target_capacity
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if statistic is not None:
            self._values["statistic"] = statistic
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.'''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.'''
        result = self._values.get("max_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.'''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.'''
        result = self._values.get("min_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsCoreScalingDownPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsCoreScalingDownPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreScalingDownPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a84509548c4b9bb0724ace007ea401e859349b2265ec99a50e0654dbd1d43fa6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsCoreScalingDownPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71b16cfeb0a9286f331c2d2058f8287c2d3012240711e831b130c84aa6093cc8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsCoreScalingDownPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74ba0cb7d7a5670fe27c4a1eb279df56afa93f6c4430566f50295911934029df)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2baa01221d515a3e6201418c4629a9f714134307cade88d072dfecb8b7d9c31)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ad445879371dd0c73a8ac8499663556428d083f3239ab07140b088f2076a419)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingDownPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingDownPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingDownPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71ef72109d2670803825346bf20d8a6ba33b9113370debf1db38cb3954ede69f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsCoreScalingDownPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreScalingDownPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__86b52bd90b61f954824b7f34cad9394fb819f4abb5af60f535d08c7b242e30ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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

    @jsii.member(jsii_name="resetMaximum")
    def reset_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximum", []))

    @jsii.member(jsii_name="resetMaxTargetCapacity")
    def reset_max_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTargetCapacity", []))

    @jsii.member(jsii_name="resetMinimum")
    def reset_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimum", []))

    @jsii.member(jsii_name="resetMinTargetCapacity")
    def reset_min_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTargetCapacity", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumInput")
    def maximum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacityInput")
    def max_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTargetCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInput")
    def minimum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumInput"))

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacityInput")
    def min_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minTargetCapacityInput"))

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
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__a9a5488ed174d075b56beb9ec4b66423ca3e6cd703547d6f105df9d2a740d4c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6f7a53739525b82f1387947ffb7adbdff565abb5f0342c119ca277f8bbd655a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7229ee56482859f5bfe329fa3ec1517f6d9eac25abeac9650408886a5c9a1538)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afba621086114143c0c096042b163f1f5d2e8d4aa224f5601a3001042bc0530d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8b6e5b0d2ea126eb73225d419e7f421a9faf62abed3ab9c0156b56869f4e52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximum"))

    @maximum.setter
    def maximum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac2dc8d9963dd0c433df8b7df06f8f201311de689b37266932e77786081abfbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacity")
    def max_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTargetCapacity"))

    @max_target_capacity.setter
    def max_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e8db23110d8f200118d687406e95d5297df1b6a4e46d6e3431a4e34bf365ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2400a74eb65c6b29523f7d3801a03d7b92a9c4c3a72ae7c4f5edf8cdd0505dd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimum"))

    @minimum.setter
    def minimum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cf6e1c81742436dd0bb5e28868da5f6a53e06f398f329aa0346b828583f684a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacity")
    def min_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minTargetCapacity"))

    @min_target_capacity.setter
    def min_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27fad4d7df358e7be0ceeb7bf85f48942d82efff594f586cfe1fa8f9a7e4747a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c9e093f4a634a1ed649904cfd2fd498b5513b5e69cc37e44701a639586f6496)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24f89b2a6ffd8ff5d8e0ab89958a1c3b7cbec6417fe105243fda4935e3ec8d80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76bcb355560a6e98382533fe549b9477a29ba605742501a463c341d2300b168a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acad1cdef874f1ec83bfcb6dc7c1b7569aebc10d3b1b196b19240529feff214e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a4622fc4aac24483279e29265fa63d513c31e646b5fa1b285ae25df619464ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b0b37de1ea8ba063cf06441a90df6a34b3c424f2e05d42e1b70c078ab596719)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abe553a6f97c62b62a1dd63dc8ade39fd9d95ca7a168dabcdd5afb482356d81b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a4571332be562c8509316294970a6ccba53ddd96375f1ba55d6e2ec7625643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingDownPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingDownPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingDownPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a59598c5f2f84ccf293227140e578f9cfd9179d6f5368e0f8978189eb7b99b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreScalingUpPolicy",
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
        "maximum": "maximum",
        "max_target_capacity": "maxTargetCapacity",
        "minimum": "minimum",
        "min_target_capacity": "minTargetCapacity",
        "operator": "operator",
        "period": "period",
        "statistic": "statistic",
        "target": "target",
    },
)
class MrscalerAwsCoreScalingUpPolicy:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        policy_name: builtins.str,
        threshold: jsii.Number,
        unit: builtins.str,
        action_type: typing.Optional[builtins.str] = None,
        adjustment: typing.Optional[builtins.str] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        maximum: typing.Optional[builtins.str] = None,
        max_target_capacity: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        min_target_capacity: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.
        :param dimensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.
        :param max_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.
        :param min_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd7b4f2a28e1edf851f73f3a3b0f6c45a6a700afa5fa6de753a40ab8d3820d64)
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
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument max_target_capacity", value=max_target_capacity, expected_type=type_hints["max_target_capacity"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
            check_type(argname="argument min_target_capacity", value=min_target_capacity, expected_type=type_hints["min_target_capacity"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
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
        if maximum is not None:
            self._values["maximum"] = maximum
        if max_target_capacity is not None:
            self._values["max_target_capacity"] = max_target_capacity
        if minimum is not None:
            self._values["minimum"] = minimum
        if min_target_capacity is not None:
            self._values["min_target_capacity"] = min_target_capacity
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if statistic is not None:
            self._values["statistic"] = statistic
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.'''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.'''
        result = self._values.get("max_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.'''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.'''
        result = self._values.get("min_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsCoreScalingUpPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsCoreScalingUpPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreScalingUpPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e40436a685d4deb371baa203335866d9fd7a7924511a755294ef5c6c1ca21cbb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsCoreScalingUpPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cd2289b2e9dd883e719e0a99596ac9302001942057e6c361787627d1d02da4c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsCoreScalingUpPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38b6bcf7e5fc556e18a5ee96785d296a17829e29b35049bb01b03cadc481eb5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__98cba9a5e0adc8604dd1f626d0c2bea13be4c98fc5d340718fc2c24ddc0ea93f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__deccaf68dd8e12765111ee56731b46955266782076f56ff84eed5e3d63e60a74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingUpPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingUpPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingUpPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6839d96a72477c19a50def466e503ccadd8862d5d540c7484322251ab11d66e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsCoreScalingUpPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsCoreScalingUpPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9143be8cfb15bbb0a34b9f4980b8e7662b3b59ea46c14421c00b7821ffd3076d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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

    @jsii.member(jsii_name="resetMaximum")
    def reset_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximum", []))

    @jsii.member(jsii_name="resetMaxTargetCapacity")
    def reset_max_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTargetCapacity", []))

    @jsii.member(jsii_name="resetMinimum")
    def reset_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimum", []))

    @jsii.member(jsii_name="resetMinTargetCapacity")
    def reset_min_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTargetCapacity", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumInput")
    def maximum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacityInput")
    def max_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTargetCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInput")
    def minimum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumInput"))

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacityInput")
    def min_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minTargetCapacityInput"))

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
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__d3f278ddd6a34ef75cb14a0a4427093dd2da235c8a75aa9698e4b6002cf8b5f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd9286ff100d791731bdbdcc8be8a2617aeed5c0b39965a2a91161e00ba2bb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93b0af547d1c36de6dc9bdc870a6ff11a91a91616d4519a79c93ecc86800d3d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__105f169055b9edc6cb6fc05669959666fae62f30a561d2d9b427f995f1323b84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b71aacae9d3459f2af1f54c0d408175e7c0cb9a91655fd2aec0be15e69d95fef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximum"))

    @maximum.setter
    def maximum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e71cdd9cbf2480cb775913bb74ce9a40cf3e705d1931f265dba66ec1ff6844)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacity")
    def max_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTargetCapacity"))

    @max_target_capacity.setter
    def max_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d8e785c3572109e0b3160d42960042c2238b7efbc752eca396b8b5eb4fb0736)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76376cf32c6aaad3fa459d564e536c6341df5315da28def704ee4c87ae8066dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimum"))

    @minimum.setter
    def minimum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88471549e41f4688b843f065bbe77b8501d9b7aa451155c1b54c58beed3f76c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacity")
    def min_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minTargetCapacity"))

    @min_target_capacity.setter
    def min_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79cd13a311342c2e19a14f26b7f4c0a41b60c8aaae5a749148dd8bca6a0bec4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f35a31875851c9220de593ab6ab5b91464494aa77cf5ffa6e9ea17dca2ff9fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da1dfc34ebdcfa90a802c0385e5f3dc734d0feea2d9aec0dc0ce81be3f14e112)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76d2813fb9caeb5386ba4c48f9c53fde71ca0889667d20c43ead7a0920382360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b863c88b1460bb76d9247bfbb14072ffad16d956a2cd180beca46cdeb3ce34d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13baa13b686f25003829e52f95aa68576c7e681fd0f38497fbb8d0d65700b61d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13a869c867cac9aa5ef672121c0763fe5fff667f517a15a603fdec6bdaa2cb52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45f0c14059513db52d8f010b35fdec2c16b63c2ba1262215ec76a4b56ce2fb4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__613fc6d577a49e2897a86bd0e67319f80a5b5bdebd2d552153ff8ab74b99ac73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingUpPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingUpPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingUpPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99c3d8d373913fb59615a84aa9b66d320040fd1e3f59e6d14cf941d114afee3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsInstanceWeights",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "weighted_capacity": "weightedCapacity",
    },
)
class MrscalerAwsInstanceWeights:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        weighted_capacity: jsii.Number,
    ) -> None:
        '''
        :param instance_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_type MrscalerAws#instance_type}.
        :param weighted_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#weighted_capacity MrscalerAws#weighted_capacity}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2479dccf4b583fc6d832282aef83692ef08a7a6da043095fca0365ddefe96f69)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument weighted_capacity", value=weighted_capacity, expected_type=type_hints["weighted_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
            "weighted_capacity": weighted_capacity,
        }

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_type MrscalerAws#instance_type}.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def weighted_capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#weighted_capacity MrscalerAws#weighted_capacity}.'''
        result = self._values.get("weighted_capacity")
        assert result is not None, "Required property 'weighted_capacity' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsInstanceWeights(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsInstanceWeightsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsInstanceWeightsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdc7482e3b3e60ffb65cb393d6bb0668e5a9280616c84e4741fcc9eb4c0b9582)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsInstanceWeightsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6a1c604d75fbdcc5947f028d9e9770a91b986f675feb7f18b2acc0f650161c8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsInstanceWeightsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b569b7996f0a2cba345a939f927e00b995a054b9277159ab754169b84b4e470)
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
            type_hints = typing.get_type_hints(_typecheckingstub__26fdb533d378a769437c3c42ab0015bb969d5a24ab318a7a063ea251d2a53a02)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3439186de70beaba3f007ed4f8b57914ef9b1782e478958213212e3cdbd834ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsInstanceWeights]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsInstanceWeights]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsInstanceWeights]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51a0c6fa51bf92eb817570c07bbf01ae395b2fc79e045507480325671675b6c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsInstanceWeightsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsInstanceWeightsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__edad60461a7745ba44716d5a40837adef5f809e6402336e30a18dae145b0e65c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="weightedCapacityInput")
    def weighted_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightedCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dbe6a7f6059c292a92a76a6be3a67138a29b2b636f1263a642df78b5283711f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="weightedCapacity")
    def weighted_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weightedCapacity"))

    @weighted_capacity.setter
    def weighted_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37648b53d6cc00cdee1e9a2e8f77894b754ab67bdf45c304d725f1b6e3b3eca6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weightedCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsInstanceWeights]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsInstanceWeights]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsInstanceWeights]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0338ecb9ea1cd9e641c65b55f2f4fb6c5958f47f8453f359a02fbb87952f9e52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsMasterEbsBlockDevice",
    jsii_struct_bases=[],
    name_mapping={
        "size_in_gb": "sizeInGb",
        "volume_type": "volumeType",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class MrscalerAwsMasterEbsBlockDevice:
    def __init__(
        self,
        *,
        size_in_gb: jsii.Number,
        volume_type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size_in_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#size_in_gb MrscalerAws#size_in_gb}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volume_type MrscalerAws#volume_type}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#iops MrscalerAws#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volumes_per_instance MrscalerAws#volumes_per_instance}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88b0e95ee04d342a6e479cde3f2f86604cbfb152f400ae65ae4aabdf803c2b3f)
            check_type(argname="argument size_in_gb", value=size_in_gb, expected_type=type_hints["size_in_gb"])
            check_type(argname="argument volume_type", value=volume_type, expected_type=type_hints["volume_type"])
            check_type(argname="argument iops", value=iops, expected_type=type_hints["iops"])
            check_type(argname="argument volumes_per_instance", value=volumes_per_instance, expected_type=type_hints["volumes_per_instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "size_in_gb": size_in_gb,
            "volume_type": volume_type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size_in_gb(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#size_in_gb MrscalerAws#size_in_gb}.'''
        result = self._values.get("size_in_gb")
        assert result is not None, "Required property 'size_in_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def volume_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volume_type MrscalerAws#volume_type}.'''
        result = self._values.get("volume_type")
        assert result is not None, "Required property 'volume_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#iops MrscalerAws#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volumes_per_instance MrscalerAws#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsMasterEbsBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsMasterEbsBlockDeviceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsMasterEbsBlockDeviceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c8968aa648183efb1afb00dd3c88d562c3c5e464ed97099897a0b31fa514bb9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsMasterEbsBlockDeviceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70905dc1f23dfe4887cabc19eed8fca2350f40a88aaca941656fc8f9a98f8bd8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsMasterEbsBlockDeviceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d843f28b5221636f5025d02d3e3b5d2095ed354798108b03f516e1bbf338aad)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d2fd4bf7359e8cc5f7dec41c855d53a556622ce3fa181a2b06a05870cc54a47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6576f703fcac9c969d00753100e434dc0a5fafce09ee999ad01218604e79f3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsMasterEbsBlockDevice]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsMasterEbsBlockDevice]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsMasterEbsBlockDevice]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e06c0c1e2adf0ce3bbc4230a281406731a5ae4dea79ba3331f18ad150e659d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsMasterEbsBlockDeviceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsMasterEbsBlockDeviceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b320746ea79da3539f72ff92691a9337cf6293521544bb0b0276f4d3226ebfa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetVolumesPerInstance")
    def reset_volumes_per_instance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumesPerInstance", []))

    @builtins.property
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInGbInput")
    def size_in_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInGbInput"))

    @builtins.property
    @jsii.member(jsii_name="volumesPerInstanceInput")
    def volumes_per_instance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumesPerInstanceInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02a29bfedb88c6c25bebd3886e12d7e01973c7de17fba093b12eb1ab9327a0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeInGb")
    def size_in_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeInGb"))

    @size_in_gb.setter
    def size_in_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02e14ec1e16d010c317ddcf8f3898e85baddd97e5b005cdc5f60785d04a16192)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeInGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumesPerInstance")
    def volumes_per_instance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumesPerInstance"))

    @volumes_per_instance.setter
    def volumes_per_instance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06bfdef1c092f2c4ab8f3501695d5b96895b1d1b3c60667890cf7d49a718ba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumesPerInstance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b91c8fefcebc9602787dadbb7583ebb748b4e24f4832ad7991b7791407798e85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsMasterEbsBlockDevice]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsMasterEbsBlockDevice]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsMasterEbsBlockDevice]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555322fd007ad96ba9cc840f6484878152ed5a25fe6d4867eb57b40ed299e56d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsProvisioningTimeout",
    jsii_struct_bases=[],
    name_mapping={"timeout": "timeout", "timeout_action": "timeoutAction"},
)
class MrscalerAwsProvisioningTimeout:
    def __init__(self, *, timeout: jsii.Number, timeout_action: builtins.str) -> None:
        '''
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#timeout MrscalerAws#timeout}.
        :param timeout_action: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#timeout_action MrscalerAws#timeout_action}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ce4db7d37e0833fff2fb9689ea720cdba57f5251d50517690c89d2fce31cd38)
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument timeout_action", value=timeout_action, expected_type=type_hints["timeout_action"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "timeout": timeout,
            "timeout_action": timeout_action,
        }

    @builtins.property
    def timeout(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#timeout MrscalerAws#timeout}.'''
        result = self._values.get("timeout")
        assert result is not None, "Required property 'timeout' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def timeout_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#timeout_action MrscalerAws#timeout_action}.'''
        result = self._values.get("timeout_action")
        assert result is not None, "Required property 'timeout_action' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsProvisioningTimeout(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsProvisioningTimeoutOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsProvisioningTimeoutOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d50c3d7dd4b73c0645e51c67aa0c164fd4f896a1361c2f0f9c9bb3d60b9be9b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="timeoutActionInput")
    def timeout_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutActionInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f7f6530920dfd911e20b99c9288f405c195e454288b56120255341028a7bcea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeoutAction")
    def timeout_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeoutAction"))

    @timeout_action.setter
    def timeout_action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7845adeff8b4c5a20287bb43ef9fd5eda5b0114638a5522651d20d0ccc1caf20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutAction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MrscalerAwsProvisioningTimeout]:
        return typing.cast(typing.Optional[MrscalerAwsProvisioningTimeout], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MrscalerAwsProvisioningTimeout],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c11e70153bf6e7c3ef58e91e7c036cde0ee5605899ae39d403fd654818991915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsScheduledTask",
    jsii_struct_bases=[],
    name_mapping={
        "cron": "cron",
        "instance_group_type": "instanceGroupType",
        "task_type": "taskType",
        "desired_capacity": "desiredCapacity",
        "is_enabled": "isEnabled",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
    },
)
class MrscalerAwsScheduledTask:
    def __init__(
        self,
        *,
        cron: builtins.str,
        instance_group_type: builtins.str,
        task_type: builtins.str,
        desired_capacity: typing.Optional[builtins.str] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_capacity: typing.Optional[builtins.str] = None,
        min_capacity: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cron: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cron MrscalerAws#cron}.
        :param instance_group_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_group_type MrscalerAws#instance_group_type}.
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_type MrscalerAws#task_type}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#desired_capacity MrscalerAws#desired_capacity}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#is_enabled MrscalerAws#is_enabled}.
        :param max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_capacity MrscalerAws#max_capacity}.
        :param min_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_capacity MrscalerAws#min_capacity}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d62be76a5206c108b843168eb0204e205d73d7e52d351c73ad1206a2aee24917)
            check_type(argname="argument cron", value=cron, expected_type=type_hints["cron"])
            check_type(argname="argument instance_group_type", value=instance_group_type, expected_type=type_hints["instance_group_type"])
            check_type(argname="argument task_type", value=task_type, expected_type=type_hints["task_type"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron": cron,
            "instance_group_type": instance_group_type,
            "task_type": task_type,
        }
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity

    @builtins.property
    def cron(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cron MrscalerAws#cron}.'''
        result = self._values.get("cron")
        assert result is not None, "Required property 'cron' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_group_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#instance_group_type MrscalerAws#instance_group_type}.'''
        result = self._values.get("instance_group_type")
        assert result is not None, "Required property 'instance_group_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#task_type MrscalerAws#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#desired_capacity MrscalerAws#desired_capacity}.'''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#is_enabled MrscalerAws#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_capacity MrscalerAws#max_capacity}.'''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_capacity MrscalerAws#min_capacity}.'''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsScheduledTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsScheduledTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsScheduledTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0618dc47b6ee1de1ba517d38305d54dfdd2fa1b57f4315782bfab2164c49122)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsScheduledTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1741c981229854bf6c022a6bd738619d8a093355cc1b98fa507e1ef8ee4a2333)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsScheduledTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cff6f78963f49fcd2cf81864c2c9aac3ba8d1ea574b0f4523cc2e496280cff0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e6fc7c4d66eb7f29df3c287e945010661379da67f1d34db404d6f3bad72caa47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c21e5dd899b5ab672095d269fe948fb16329f8a1d84629bb8b08cc8dde9f186)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsScheduledTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsScheduledTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsScheduledTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13767b579fd578f8d849a1a4dc6872b0cc680362ccd10b616f7b48d6d1922dfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsScheduledTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsScheduledTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f264ea9e9ec6b5813fc044cafa713c8e57509508f4935c26ee73ebca935ccab9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDesiredCapacity")
    def reset_desired_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDesiredCapacity", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetMaxCapacity")
    def reset_max_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCapacity", []))

    @jsii.member(jsii_name="resetMinCapacity")
    def reset_min_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCapacity", []))

    @builtins.property
    @jsii.member(jsii_name="cronInput")
    def cron_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cronInput"))

    @builtins.property
    @jsii.member(jsii_name="desiredCapacityInput")
    def desired_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "desiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceGroupTypeInput")
    def instance_group_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceGroupTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCapacityInput")
    def max_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="minCapacityInput")
    def min_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="taskTypeInput")
    def task_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cron")
    def cron(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cron"))

    @cron.setter
    def cron(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2ad6703af622c3f50e79003c64bb2c8555509c165d476804ce1fcdd69085e8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cron", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="desiredCapacity")
    def desired_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "desiredCapacity"))

    @desired_capacity.setter
    def desired_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2625e655bef4d4bef4e5900532cedd54ff1b0e8af0ba8880b26fd43dc45b57b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceGroupType")
    def instance_group_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceGroupType"))

    @instance_group_type.setter
    def instance_group_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5da6bfe1ac79f2ff62bb06730752e7fcebb4ebe2545c18e6084d9ba1be1a083)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceGroupType", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__4e16cd43051053183d7be5f4ae1b2c237787574b947b263c0777c5cb4525ef26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e7e5f059fcb13dd21b3c6c0ca03a66919d3db88bbadc380938baf654d4dc1bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCapacity")
    def min_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minCapacity"))

    @min_capacity.setter
    def min_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bea32febd59334e31bfab531c76e6c7e97125d264cdfe382fbe230af34c59d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__227cdac360f11ec2c644c4191ee70cbdff0aaa659bf4426e0620569146c6a3ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsScheduledTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsScheduledTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsScheduledTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efc348828c579b04519d839a66ea40d414f59a75f3d77a33fc3cb5a5425d3379)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsStepsFile",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "key": "key"},
)
class MrscalerAwsStepsFile:
    def __init__(self, *, bucket: builtins.str, key: builtins.str) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bucket MrscalerAws#bucket}.
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__678827bb26a92b646953eb8f7c415feee1ed4ab21cc9879ce3115055b829f377)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#bucket MrscalerAws#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsStepsFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsStepsFileList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsStepsFileList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72e4c567eb3717122a1fcc85eedcdeca8e49002cc71752c75d1127a40559ce8f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsStepsFileOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710fab9f6d3ebe75b8899443f97a834c99eaafd854b1eb1b221a515987439dd3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsStepsFileOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ef9e85886cac8c9f334329ddb431dcd32f905e630f625419c9df17b19028f48)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8d0efafc691dac8715ffc555d1d5c033f3d826e4d639f726f1514a60de45362)
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
            type_hints = typing.get_type_hints(_typecheckingstub__550170e093d12b13000c72fcd0b454ce72c400ac83c29e20159f15f1c2aa9e34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsStepsFile]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsStepsFile]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsStepsFile]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6490755677bf85075dfd26ceb5880e780fbc03d698cbe2dc76d1156e3780334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsStepsFileOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsStepsFileOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__84216a787906854229900a17a64e4327f25eacf71a59293ef816f615722b20f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb69e53a3826884bea2297570606b8aaa232b372cad3aeeed4efad5a207ed396)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e30c57a49a16e4c65220b3ad70289dbde7a98bf95d6fecf48592312a5c55e895)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsStepsFile]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsStepsFile]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsStepsFile]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f21c818a64edf5a34a2c95696107ae141dcda1f0e1fc00f55bfadcb0f3f742a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class MrscalerAwsTags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#value MrscalerAws#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0270fdd124a61e495fad367ee893f4d43876248ca5ae9a043a96b6de438028a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#key MrscalerAws#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#value MrscalerAws#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8da5668ee5d58aa58b9c5697af43f3a508ed18ae1a59ea3c5f790097a4f2103)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffebc576474eadee0d8c3797dbf9e70f2e3aaff7bd3907891227a76249baefd7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2e620b3e7f5448935ee6fdb434aa96ae3a99c2fdfe1d24507529e34ba10a429)
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
            type_hints = typing.get_type_hints(_typecheckingstub__82ca8f74ea322ab293d33f561ab3e33bb2724afed987810eeb2820ca57042b5c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5fb3d155bfa5d088798a248659c61451a04e970c641f6dbdeaae2eaa6df68b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be75ca3b0a13406918cc0a79ba3a5febd21af239f829a1aa06c4e5698cac0503)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b517fa50013200ccc3476c33f92ef6a32a58d3252125f6855504d617e809b512)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8ab01175cfcaeead65d339fefa78d9a7d6154f42f16f9fb2c7ffc40e8329253)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e3636a71d1d4d01691e9cb362065532a396a99c6e78f162990c30606b0603f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24ac295df8350986a398f22471653bb53a6aa3ad8926a9705ff55b9819a6eee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskEbsBlockDevice",
    jsii_struct_bases=[],
    name_mapping={
        "size_in_gb": "sizeInGb",
        "volume_type": "volumeType",
        "iops": "iops",
        "volumes_per_instance": "volumesPerInstance",
    },
)
class MrscalerAwsTaskEbsBlockDevice:
    def __init__(
        self,
        *,
        size_in_gb: jsii.Number,
        volume_type: builtins.str,
        iops: typing.Optional[jsii.Number] = None,
        volumes_per_instance: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param size_in_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#size_in_gb MrscalerAws#size_in_gb}.
        :param volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volume_type MrscalerAws#volume_type}.
        :param iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#iops MrscalerAws#iops}.
        :param volumes_per_instance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volumes_per_instance MrscalerAws#volumes_per_instance}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a5f6e47b9ceedb9bd87fff8a8327fa9cc7c3ad9e4d8b46f63db9bc1caa1f603)
            check_type(argname="argument size_in_gb", value=size_in_gb, expected_type=type_hints["size_in_gb"])
            check_type(argname="argument volume_type", value=volume_type, expected_type=type_hints["volume_type"])
            check_type(argname="argument iops", value=iops, expected_type=type_hints["iops"])
            check_type(argname="argument volumes_per_instance", value=volumes_per_instance, expected_type=type_hints["volumes_per_instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "size_in_gb": size_in_gb,
            "volume_type": volume_type,
        }
        if iops is not None:
            self._values["iops"] = iops
        if volumes_per_instance is not None:
            self._values["volumes_per_instance"] = volumes_per_instance

    @builtins.property
    def size_in_gb(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#size_in_gb MrscalerAws#size_in_gb}.'''
        result = self._values.get("size_in_gb")
        assert result is not None, "Required property 'size_in_gb' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def volume_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volume_type MrscalerAws#volume_type}.'''
        result = self._values.get("volume_type")
        assert result is not None, "Required property 'volume_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#iops MrscalerAws#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes_per_instance(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#volumes_per_instance MrscalerAws#volumes_per_instance}.'''
        result = self._values.get("volumes_per_instance")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsTaskEbsBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsTaskEbsBlockDeviceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskEbsBlockDeviceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__93aff499b29fa5690360a5c248f7b485332a4fa729a4ef6ab9d19b46053f127a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "MrscalerAwsTaskEbsBlockDeviceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c8f6966617e14d8455f5f79b68d36388b37f36384680194038ff1b8413966af)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsTaskEbsBlockDeviceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d07fbefd4766e45b0277b469ccdbcd40068ce8aceb01fa597ab5904bb0d3d01e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c004db2fc99e7fbfed7263a1861c4b13e708b520d04f92cfd8f1910353756e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__30d958a1bb1e4ef99cea8806da4802ad26374ea52c511958351ab52afbc6db6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskEbsBlockDevice]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskEbsBlockDevice]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskEbsBlockDevice]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7f403971ba5bf078bbdddf5b6e60526db049883a9e20452564324a7d9fe7e7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsTaskEbsBlockDeviceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskEbsBlockDeviceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff41d02c31b629cadc0af5045a4126c5393a4ede0c87ef973fb93fc4ef0af829)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetVolumesPerInstance")
    def reset_volumes_per_instance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumesPerInstance", []))

    @builtins.property
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInGbInput")
    def size_in_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInGbInput"))

    @builtins.property
    @jsii.member(jsii_name="volumesPerInstanceInput")
    def volumes_per_instance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "volumesPerInstanceInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeTypeInput")
    def volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a226fb2113dca1be1978b79c3bff18827aa10e782abcf5e9e58bd6c930d7fec5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeInGb")
    def size_in_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeInGb"))

    @size_in_gb.setter
    def size_in_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36a04e4e469f0f4d77c8f9d167d5b79f5c581d9c82285b5eae9368b62ba28e51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeInGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumesPerInstance")
    def volumes_per_instance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "volumesPerInstance"))

    @volumes_per_instance.setter
    def volumes_per_instance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ca8776c28f378b20f9f754a9a1e14055223b46880c05b61ea4d4597d2efcd42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumesPerInstance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeType")
    def volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeType"))

    @volume_type.setter
    def volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8672743a6b87395ccbbf7792adb79623610420826b0d870d19cfa6b8ee451f7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskEbsBlockDevice]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskEbsBlockDevice]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskEbsBlockDevice]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6643f7ead57aa4a88ce635cb26018d8a8656bda07fece8e436e5a2dfdeb75531)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskScalingDownPolicy",
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
        "maximum": "maximum",
        "max_target_capacity": "maxTargetCapacity",
        "minimum": "minimum",
        "min_target_capacity": "minTargetCapacity",
        "operator": "operator",
        "period": "period",
        "statistic": "statistic",
        "target": "target",
    },
)
class MrscalerAwsTaskScalingDownPolicy:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        policy_name: builtins.str,
        threshold: jsii.Number,
        unit: builtins.str,
        action_type: typing.Optional[builtins.str] = None,
        adjustment: typing.Optional[builtins.str] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        maximum: typing.Optional[builtins.str] = None,
        max_target_capacity: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        min_target_capacity: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.
        :param dimensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.
        :param max_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.
        :param min_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11edbcd01868d9b0df798a0fac7d590c0a5cf7aae53cf76435b743c5a0efc6a2)
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
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument max_target_capacity", value=max_target_capacity, expected_type=type_hints["max_target_capacity"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
            check_type(argname="argument min_target_capacity", value=min_target_capacity, expected_type=type_hints["min_target_capacity"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
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
        if maximum is not None:
            self._values["maximum"] = maximum
        if max_target_capacity is not None:
            self._values["max_target_capacity"] = max_target_capacity
        if minimum is not None:
            self._values["minimum"] = minimum
        if min_target_capacity is not None:
            self._values["min_target_capacity"] = min_target_capacity
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if statistic is not None:
            self._values["statistic"] = statistic
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.'''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.'''
        result = self._values.get("max_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.'''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.'''
        result = self._values.get("min_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsTaskScalingDownPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsTaskScalingDownPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskScalingDownPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bd87d3c6e04e9a8ddbe82bd65b69af3b9ee7359e47276ce198c9140c1080671)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsTaskScalingDownPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5077d6cd8230259ff3332d926b9981c8e4aed0c38396d0998ea05eb07ceacdc5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsTaskScalingDownPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85c45aef4310769a30d4f5f492c299c3d1c4cfc3f831f1aa30bf44f81233c317)
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
            type_hints = typing.get_type_hints(_typecheckingstub__64ef06868bbc62ba6445b7772c124396105907b1ccdeff8b5dc2c483d6fefa96)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f375387b02dad9ef421d827f4b9d494538ba88f5f7998040fce11b861fcd7363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingDownPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingDownPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingDownPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e936235e39165b34964d7d2c2ffee353dcb4d437a2ab35302ef0640998ec4d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsTaskScalingDownPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskScalingDownPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26cd704a60db32aa922f8b351b5bd3364ed96b71de538cd00f8e3d092bd7da44)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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

    @jsii.member(jsii_name="resetMaximum")
    def reset_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximum", []))

    @jsii.member(jsii_name="resetMaxTargetCapacity")
    def reset_max_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTargetCapacity", []))

    @jsii.member(jsii_name="resetMinimum")
    def reset_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimum", []))

    @jsii.member(jsii_name="resetMinTargetCapacity")
    def reset_min_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTargetCapacity", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumInput")
    def maximum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacityInput")
    def max_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTargetCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInput")
    def minimum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumInput"))

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacityInput")
    def min_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minTargetCapacityInput"))

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
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c674c18f7c9bd7743031705ed7d593bc064074086560b5fdfb3e608886fe8d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8ac515857043e08991d75ea9972d2a6864f130aec557186b8d30bda917b78fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bde0d42ab1ae439f67f45d2f82190add58c2186b336b538122dbc4a8426c44aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1532252e099c7f85eb4d02b795e7d463e142ed45721c7f2be32dcedcf2e94246)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43f3548a056f8807dbeb22de4440687b36ad92321e94ffd99a437ef63bb5a47c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximum"))

    @maximum.setter
    def maximum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19b574d05aede48e12f58d307f8b1b0e1845d261072632b6e2d8f04d98203d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacity")
    def max_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTargetCapacity"))

    @max_target_capacity.setter
    def max_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d9d8e7421546c2e35ec6de3b63eef5e2f03837d2340435907884a1479cdf80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0d6756e9bf5d8e770105f0734e934d2528b9a3148cd21fd541ca8d4630615d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimum"))

    @minimum.setter
    def minimum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08d7dc714785d8c1805e84e20ab0851421415edc4ee90453f11d8bc183b0edbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacity")
    def min_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minTargetCapacity"))

    @min_target_capacity.setter
    def min_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c7cae8220f0996944af45ca8e2cea4e11c3df85860e9463e714f7032f9236c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e55f05b20d5705e0389df9010ffd28b858cf3b5194f6915638716f0adc2a147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b41156d68b34d5278e02b2116684da18da296e14b0d2d683078623798e862b25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afb5f1c84a9cd4ab3bfbbcc6123087efe7342211ed486ff239eb091ea961451d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8018899da4fcccd2f51d8266b1021ba401663753163c119028197c7b426b2442)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0f51e0e7c84c228bce08f76a67acbbee494915283429957715091a733aadd67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46509f98ef250b403eaabc34bb509c7e630a92593f3dac03575f5a8c2101774b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14cf46d85ff46c5f68e3beda604ee818fc7771f897e30c6ce4d69ff5c5740e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d0c1315a5f649933a8bd5e6d35683bd6c03f7322ea7996989545b9718f8e523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingDownPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingDownPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingDownPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0221c4e4e4eaac4a596711d32a6a2e31420ec221fec56281346f0233ac0ad60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskScalingUpPolicy",
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
        "maximum": "maximum",
        "max_target_capacity": "maxTargetCapacity",
        "minimum": "minimum",
        "min_target_capacity": "minTargetCapacity",
        "operator": "operator",
        "period": "period",
        "statistic": "statistic",
        "target": "target",
    },
)
class MrscalerAwsTaskScalingUpPolicy:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        policy_name: builtins.str,
        threshold: jsii.Number,
        unit: builtins.str,
        action_type: typing.Optional[builtins.str] = None,
        adjustment: typing.Optional[builtins.str] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        maximum: typing.Optional[builtins.str] = None,
        max_target_capacity: typing.Optional[builtins.str] = None,
        minimum: typing.Optional[builtins.str] = None,
        min_target_capacity: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.
        :param action_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.
        :param dimensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.
        :param maximum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.
        :param max_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.
        :param minimum: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.
        :param min_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.
        :param target: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a391aa9cda31e88d3a4b3569f8fed923322e8406cdd0585a0241c61c93e4051)
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
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument max_target_capacity", value=max_target_capacity, expected_type=type_hints["max_target_capacity"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
            check_type(argname="argument min_target_capacity", value=min_target_capacity, expected_type=type_hints["min_target_capacity"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
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
        if maximum is not None:
            self._values["maximum"] = maximum
        if max_target_capacity is not None:
            self._values["max_target_capacity"] = max_target_capacity
        if minimum is not None:
            self._values["minimum"] = minimum
        if min_target_capacity is not None:
            self._values["min_target_capacity"] = min_target_capacity
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if statistic is not None:
            self._values["statistic"] = statistic
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#policy_name MrscalerAws#policy_name}.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.'''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#action_type MrscalerAws#action_type}.'''
        result = self._values.get("action_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#adjustment MrscalerAws#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#cooldown MrscalerAws#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dimensions(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#dimensions MrscalerAws#dimensions}.'''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maximum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#maximum MrscalerAws#maximum}.'''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#max_target_capacity MrscalerAws#max_target_capacity}.'''
        result = self._values.get("max_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#minimum MrscalerAws#minimum}.'''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#min_target_capacity MrscalerAws#min_target_capacity}.'''
        result = self._values.get("min_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#target MrscalerAws#target}.'''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsTaskScalingUpPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsTaskScalingUpPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskScalingUpPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__940755bdca38b24d556635f7c42a3d6e11e14ed27ee49209037fb36552b93318)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsTaskScalingUpPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d98b7fe34d396797248cfa93aa3d769e571fa1c6efab0654045b99cb34e15620)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsTaskScalingUpPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7965f41e51b798b914489f9984b3abe2d65b8415bf312f9352231370daa53d7d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c641a57e1dbdb7780a9483ca9e8db0143011be5cce8b7334ec7c2c11fdb23b9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28473315ccfbcad4eea5eede04766355147a4ca8d136774e32b0708ff0f40421)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingUpPolicy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingUpPolicy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingUpPolicy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e769b4f6b32293b93180a696731ae8be7cfb259d2aa665f3050ba573cd4f5bc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsTaskScalingUpPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTaskScalingUpPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7fa71e6b507b9a52e455b0be35a217cca387671a1130df4beb3ff5e7b61cd4f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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

    @jsii.member(jsii_name="resetMaximum")
    def reset_maximum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaximum", []))

    @jsii.member(jsii_name="resetMaxTargetCapacity")
    def reset_max_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTargetCapacity", []))

    @jsii.member(jsii_name="resetMinimum")
    def reset_minimum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimum", []))

    @jsii.member(jsii_name="resetMinTargetCapacity")
    def reset_min_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTargetCapacity", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @builtins.property
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustmentInput")
    def adjustment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adjustmentInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="maximumInput")
    def maximum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maximumInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacityInput")
    def max_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTargetCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumInput")
    def minimum_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumInput"))

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacityInput")
    def min_target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minTargetCapacityInput"))

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
    @jsii.member(jsii_name="statisticInput")
    def statistic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statisticInput"))

    @builtins.property
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__e2df06fa06556f92508b184a7878efe09a4f52bad83b0a8602a471d372c695e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__595f83f7cfa2fc95d9387f8cdbf6e621d540dba0b54014d3b27803eb4264005f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4370bbb1b3ebe5c301dc0bfc40eaa42c6588f4fea39bb83b57c9b0e768c11405)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "dimensions"))

    @dimensions.setter
    def dimensions(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__212fcd0d9e184cebee3cc1c0b1dff7e431c4ef87aa14c80bdfba06100edf0aab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ca377c310dca476992744c103373093e9918394d33085db40e6e7b2d6dfb080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maximum"))

    @maximum.setter
    def maximum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e73218946194b5df3f256b1ff2c4deba26dd991ca080e2619d87e54f2fc7c9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maximum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTargetCapacity")
    def max_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTargetCapacity"))

    @max_target_capacity.setter
    def max_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af640838044e5c4f9e8bc238dd342fc219fd5f7d05e2e7a68829216b2bad4373)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa6e3df14400b7e95da6d6753b21df79646c9edabe05942de0a37320cd7ec9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimum"))

    @minimum.setter
    def minimum(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74da95add8b89d7f2369844a2e8a4955fa100b4196063483fd5d21412a206789)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minTargetCapacity")
    def min_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minTargetCapacity"))

    @min_target_capacity.setter
    def min_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc4991216ab10c1a7c1e36c735b034963bda4d53821a844f450f839473d88028)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbded019a0d408b78b7dad46a4e4459e61cc89acc19aa760c97c66f635a3a8a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__373c31c6ccfb7a98f301e1cce5e433c92c60236a30741f980cf9da6b96fb12dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8725cc600ab90894e4d840eeb50061a48f629d0234fb642ae978898ec546f3e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fe619003523e3d09d53b0c75129f071358427e7a55ec1360cd1969f6ba618e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3a658e232469a4c755c4e107c26e3616916dce055b00363a0e005d1e1f613de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d12e9fcfbcbabd8ba032952428f20a8385b52287e5907bd6b159523925cfe90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "target", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac7ab9fcfe117567526c3901e14826f766877994a96e4f785ad5f53b70295d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36a7c2eb8ade81938e7f5a09285e6e9e51ab9f758421f216bb3667a2c7c08d91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingUpPolicy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingUpPolicy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingUpPolicy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2cdbcabe912a9faca15018e389b6504381d8613ee2400f1ef74508318dc321)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTerminationPolicies",
    jsii_struct_bases=[],
    name_mapping={"statements": "statements"},
)
class MrscalerAwsTerminationPolicies:
    def __init__(
        self,
        *,
        statements: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTerminationPoliciesStatements", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param statements: statements block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statements MrscalerAws#statements}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8dc23f038a3b40d70a0e8fbb8b0046686e4f60d80d1ac684c0e75a9b0f8ad51)
            check_type(argname="argument statements", value=statements, expected_type=type_hints["statements"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "statements": statements,
        }

    @builtins.property
    def statements(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPoliciesStatements"]]:
        '''statements block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statements MrscalerAws#statements}
        '''
        result = self._values.get("statements")
        assert result is not None, "Required property 'statements' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPoliciesStatements"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsTerminationPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsTerminationPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTerminationPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a2e6a504c43d7a50a654964dcc7ff8631b05198ccf01c8fa93f8ba59850da96)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsTerminationPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b61904c14792acd964bef88a257b780da21676faac09b9cf37de50a95e614dc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsTerminationPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfbad589929b4ae03e49aeb0a63ba667c09c34243fba3ad7e24d3cf4b1544485)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4454c5ead00463984045bca662d7be24f00b48df9357a812c9da58bd1c4a8312)
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
            type_hints = typing.get_type_hints(_typecheckingstub__496acc2f0dede17aadf92b3f067cadb01c39bd65dadb618a30d1941be211df4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPolicies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPolicies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40a6d81651d2c22158b555fb59f655db77aca3cfe86b7089df60bd6aa2b1e0ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsTerminationPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTerminationPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e976af347d0a6800002af2fb1a99884bccb3faec33c0813bacbc5bbad8b78ad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putStatements")
    def put_statements(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MrscalerAwsTerminationPoliciesStatements", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d911a0d915e44938b8f2196ad7a3d848610a88f8f68a1140d6660d6334125164)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStatements", [value]))

    @builtins.property
    @jsii.member(jsii_name="statements")
    def statements(self) -> "MrscalerAwsTerminationPoliciesStatementsList":
        return typing.cast("MrscalerAwsTerminationPoliciesStatementsList", jsii.get(self, "statements"))

    @builtins.property
    @jsii.member(jsii_name="statementsInput")
    def statements_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPoliciesStatements"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MrscalerAwsTerminationPoliciesStatements"]]], jsii.get(self, "statementsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPolicies]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPolicies]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPolicies]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8a5f8ac1cec7d800040d7b3c4f823b31352443eb49a4f3f6dbe575b2ea6255e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTerminationPoliciesStatements",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "namespace": "namespace",
        "threshold": "threshold",
        "evaluation_periods": "evaluationPeriods",
        "operator": "operator",
        "period": "period",
        "statistic": "statistic",
        "unit": "unit",
    },
)
class MrscalerAwsTerminationPoliciesStatements:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        namespace: builtins.str,
        threshold: jsii.Number,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        operator: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.
        :param statistic: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3beeabe220022b009b56a9857090794b4eae6f10e79303ec83232912fffb877)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument statistic", value=statistic, expected_type=type_hints["statistic"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_name": metric_name,
            "namespace": namespace,
            "threshold": threshold,
        }
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if operator is not None:
            self._values["operator"] = operator
        if period is not None:
            self._values["period"] = period
        if statistic is not None:
            self._values["statistic"] = statistic
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#metric_name MrscalerAws#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#namespace MrscalerAws#namespace}.'''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#threshold MrscalerAws#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#evaluation_periods MrscalerAws#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#operator MrscalerAws#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#period MrscalerAws#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def statistic(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#statistic MrscalerAws#statistic}.'''
        result = self._values.get("statistic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/mrscaler_aws#unit MrscalerAws#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MrscalerAwsTerminationPoliciesStatements(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MrscalerAwsTerminationPoliciesStatementsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTerminationPoliciesStatementsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b53614e5f004417f66af64f11692b6c6d6604912250ec34033de790c2718c217)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "MrscalerAwsTerminationPoliciesStatementsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea81d6c16eb1a9f1d13cdd6ab0835655c391aec71ae7eea70183ad7262e782d6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("MrscalerAwsTerminationPoliciesStatementsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d15aa679682a6aba4bae7b6ccfa4fe9bf50151e97121cab9ef3b65362639133)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8de4272896bb2e4623e2004dbb43d15ddba4cca1bab9a30a36af9ca8abe41190)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6259d31ada04671d7897d69d11ea2534b7a1828963d481073588b8a09c52989)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPoliciesStatements]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPoliciesStatements]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPoliciesStatements]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64b0b66981b6be9f298b4a310f66299e77fe2b7176b53a3a9c56c507bceaf287)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class MrscalerAwsTerminationPoliciesStatementsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.mrscalerAws.MrscalerAwsTerminationPoliciesStatementsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10b405eef79928256c3ca899f541f54586e96029c42f4a5dbb8e07851425a171)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEvaluationPeriods")
    def reset_evaluation_periods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluationPeriods", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetStatistic")
    def reset_statistic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatistic", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

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
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a90db6e98ba5f25b05844e21537a630e2992aa6536c7738eae10e96587dc2bb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3531fa6bd438a451faa17f6145f76cd364f58365adc4dba8366f1f83e5cae106)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f05b08d11483973fab510148429a3172a444b25f18c0e3e148840df866f08f88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5bb427cf840a1f6f6da8b92e8fc0052dcde8be28efffb0381d3d221abb04f05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__208c34b47d593acb814172caac072cb4ff4c037f4ece7a91395459f6dbe225f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statistic")
    def statistic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statistic"))

    @statistic.setter
    def statistic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19a31adb26500746a1c5b062d529d0f21a3ad2e83b9b5795e59e5bf27c34f88c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statistic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e12d926fb5acd06e719bba6bf66142f84b187ce89a68daa8164a244f6360ca63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fe8c8aeab9b1fa100301cf83447c272568bed53e875fdcabcb918dac85cb772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPoliciesStatements]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPoliciesStatements]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPoliciesStatements]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b09fec0b88d50c78c1cc44f4d01429a6be09cd62bc3e640bbddc8e9a1daae96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MrscalerAws",
    "MrscalerAwsApplications",
    "MrscalerAwsApplicationsList",
    "MrscalerAwsApplicationsOutputReference",
    "MrscalerAwsBootstrapActionsFile",
    "MrscalerAwsBootstrapActionsFileList",
    "MrscalerAwsBootstrapActionsFileOutputReference",
    "MrscalerAwsConfig",
    "MrscalerAwsConfigurationsFile",
    "MrscalerAwsConfigurationsFileList",
    "MrscalerAwsConfigurationsFileOutputReference",
    "MrscalerAwsCoreEbsBlockDevice",
    "MrscalerAwsCoreEbsBlockDeviceList",
    "MrscalerAwsCoreEbsBlockDeviceOutputReference",
    "MrscalerAwsCoreScalingDownPolicy",
    "MrscalerAwsCoreScalingDownPolicyList",
    "MrscalerAwsCoreScalingDownPolicyOutputReference",
    "MrscalerAwsCoreScalingUpPolicy",
    "MrscalerAwsCoreScalingUpPolicyList",
    "MrscalerAwsCoreScalingUpPolicyOutputReference",
    "MrscalerAwsInstanceWeights",
    "MrscalerAwsInstanceWeightsList",
    "MrscalerAwsInstanceWeightsOutputReference",
    "MrscalerAwsMasterEbsBlockDevice",
    "MrscalerAwsMasterEbsBlockDeviceList",
    "MrscalerAwsMasterEbsBlockDeviceOutputReference",
    "MrscalerAwsProvisioningTimeout",
    "MrscalerAwsProvisioningTimeoutOutputReference",
    "MrscalerAwsScheduledTask",
    "MrscalerAwsScheduledTaskList",
    "MrscalerAwsScheduledTaskOutputReference",
    "MrscalerAwsStepsFile",
    "MrscalerAwsStepsFileList",
    "MrscalerAwsStepsFileOutputReference",
    "MrscalerAwsTags",
    "MrscalerAwsTagsList",
    "MrscalerAwsTagsOutputReference",
    "MrscalerAwsTaskEbsBlockDevice",
    "MrscalerAwsTaskEbsBlockDeviceList",
    "MrscalerAwsTaskEbsBlockDeviceOutputReference",
    "MrscalerAwsTaskScalingDownPolicy",
    "MrscalerAwsTaskScalingDownPolicyList",
    "MrscalerAwsTaskScalingDownPolicyOutputReference",
    "MrscalerAwsTaskScalingUpPolicy",
    "MrscalerAwsTaskScalingUpPolicyList",
    "MrscalerAwsTaskScalingUpPolicyOutputReference",
    "MrscalerAwsTerminationPolicies",
    "MrscalerAwsTerminationPoliciesList",
    "MrscalerAwsTerminationPoliciesOutputReference",
    "MrscalerAwsTerminationPoliciesStatements",
    "MrscalerAwsTerminationPoliciesStatementsList",
    "MrscalerAwsTerminationPoliciesStatementsOutputReference",
]

publication.publish()

def _typecheckingstub__31c78e829881099c8a568bbfbf56aadc23e2bacd798cfaf5c48e25c1d7ba171c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    strategy: builtins.str,
    additional_info: typing.Optional[builtins.str] = None,
    additional_primary_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_replica_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    applications: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsApplications, typing.Dict[builtins.str, typing.Any]]]]] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsBootstrapActionsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    configurations_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsConfigurationsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_desired_capacity: typing.Optional[jsii.Number] = None,
    core_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    core_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    core_lifecycle: typing.Optional[builtins.str] = None,
    core_max_size: typing.Optional[jsii.Number] = None,
    core_min_size: typing.Optional[jsii.Number] = None,
    core_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_unit: typing.Optional[builtins.str] = None,
    custom_ami_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    ebs_root_volume_size: typing.Optional[jsii.Number] = None,
    ec2_key_name: typing.Optional[builtins.str] = None,
    expose_cluster_id: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_weights: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsInstanceWeights, typing.Dict[builtins.str, typing.Any]]]]] = None,
    job_flow_role: typing.Optional[builtins.str] = None,
    keep_job_flow_alive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_uri: typing.Optional[builtins.str] = None,
    managed_primary_security_group: typing.Optional[builtins.str] = None,
    managed_replica_security_group: typing.Optional[builtins.str] = None,
    master_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsMasterEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]]] = None,
    master_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    master_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    master_lifecycle: typing.Optional[builtins.str] = None,
    master_target: typing.Optional[jsii.Number] = None,
    provisioning_timeout: typing.Optional[typing.Union[MrscalerAwsProvisioningTimeout, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
    release_label: typing.Optional[builtins.str] = None,
    repo_upgrade_on_boot: typing.Optional[builtins.str] = None,
    retries: typing.Optional[jsii.Number] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security_config: typing.Optional[builtins.str] = None,
    service_access_security_group: typing.Optional[builtins.str] = None,
    service_role: typing.Optional[builtins.str] = None,
    steps_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsStepsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_desired_capacity: typing.Optional[jsii.Number] = None,
    task_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    task_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    task_lifecycle: typing.Optional[builtins.str] = None,
    task_max_size: typing.Optional[jsii.Number] = None,
    task_min_size: typing.Optional[jsii.Number] = None,
    task_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_unit: typing.Optional[builtins.str] = None,
    termination_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTerminationPolicies, typing.Dict[builtins.str, typing.Any]]]]] = None,
    termination_protected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    visible_to_all_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__35172109fdfdfd7a3714918fe66883d37257d49546d4362185fef996d5fb4b23(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd41554ad0395378c0f6fdab082d9cb280f9061845c9281972edb9a00394eba(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsApplications, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d64eb5c37233a28288caf6acd710e044a3861c77865f2485470996db5af858fd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsBootstrapActionsFile, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ce3fa0ffa50fce9100fbf2b19943bebeecd8ad0c0e0febee6ad12369ceacdb1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsConfigurationsFile, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4d8ccc7b4eb834bd856f6e41e7c21855cdf2308e92e8f34d1fdd48cd39050b6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a5f4d17aa08240f1e933cbf2074b420ce0b89d4bf4c8be63ff714d395de31d4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__382f5a5e0ded3b02a9c69b05e95493f4d354d32cdb4ca03f7d1a0696d731e266(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__609e720f56d51c4f4fe2618f5ce0dc0894e710e30dbd6cc67761c2f6f6c0c1f1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsInstanceWeights, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605d533b2509b3acfc89b2cce1fd0a8620f14d0952d24551e1eb065a6b28071d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsMasterEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1831eb6e7a670a04697ec67112ae9a09915d32874ca3d18e3e28976aaaa995d2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsScheduledTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c1dfdf1bba7fca1420a6a497f486a27dc8ae932317b6d0d6786ed0c0f11856f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsStepsFile, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af6965d530e68d33853e46276db8f941875879592412db8520ca54184d3a32cb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58a7de5040d346a768d5f8765aa8a60931538eef2efb9539259ee120ddf28db9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b67b1cda2adc0d12f4c7e5c72fd41f6e237e9c92ccbcc2a400d6bf29246094a5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd75d55ea75d75282d7a87ad11f3f27a13519d5829c258f903797430091dd34(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5da96db93bd292899ea0b2a516cf099905712f7a3b205cdf409d8ee9eb91f0bc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTerminationPolicies, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b2a361350df8db1639eb0754828d88d5466aa060e60d45e60b2cb97c35d111e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27d65ee786dd7be679d0b097c2ed129587c71ccde50d1886758c5bfed56b5dea(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5870eef5f373cc9b462f829bb8d50ce6a52607018321b20bdd47245d21d8aab7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b5417a4d54d2340fd0850750c1512e461aefc32c8bac656b00ea7dc45c9f2a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68a79c053d498c047c71fbc47cef436f81904ef46ec56d6ad55ab949debc00b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cad8b1ca899674d9a87e4c73b143f4a7196c464c06cb1ffd83b92b3a4ce3dee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd406520e498621bd34e6264b914bcb2b84c1e62912d228022850939b39348ca(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a58e42627278c0fd359323849aacfcf720de97abcb02ce0c9e7e8d71e7cd8f22(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cda135ebd8a65009d49ff964e15bad28bbd52a503e1845fc61900ef6d3e643c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64a11de294363ba1fdb0371cdcbd54ab28937bc1a9a513a13f74c47e3c85022b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c1b71f389793f7f47bd791ba9f7315dbe5eef733826e6ccb30a6a67b3d0bc6e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74479544bc58fdfa0f4b8d8803ae3bdb5ac29a3253f5af10c4719b03895aa999(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4bb560663490b4ab224d26a38ec6fdded2a62f855dd7f6fe0ba2da1e2754305(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3c309b328f8b39da211cbf86793d32cb21fbc12edb7c9c4591c9d02b41698ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013037d4cd33fc56b1e62a79eae25b66a266b4d1d9bfa5cd8a14b24a27c56781(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b34ef9769fa766f03d3e188a8ca4fb1a31ef40f7d4f7e026c0ccaa3d4d6ed5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dc5696a7430bdf45c7748308802b852e5a1af093355dcb760821ed6667f8834(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7a4c68536527a7e00c9b7e5e0dbb531409217d976678cdf0294f5210f7fbee9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d03f0631d010079087c8987548a6e9c733d5df9f8320c7f403e6d27af225a2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__464b9b53f0177a688d3c319dc2dc00554abc37306e5bfd4534f621fd420c5628(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b3ee8bf59e08fbacc2f5da14b82b7d025d4a1a88b1fad42c624dbed3d0f907(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e959de129818b7f222033092c4552aa89b1b0e70efc5c765b697f40ba3230bef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__363c3fae1b64863e897389bb9b95f58a26b5c6b11b53d6bf13b6f0beeaf78f15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be5080425feffb5b1ede811b09dadcc22be4bc8ca046608c70a84d3458012921(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2ca18db785ea4c9420947676f62124ad6fc5bcf015d61f5accb184dacb1498c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__651be13b65c00030a48340c408f1ce18e341178984145fc7252a63bd870654b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f12659e59d642754da97b3afd49a837887c533ed5d26be00a4eb6f6c606edb97(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ff0eea9e608c2117598c5b0d6f55431f8b6eb41da364dee268c10914b9d31ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6912f7a0fc896c300854e3976660e76cd68770d0a687935669d8f1f24dc879(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f17d1fdaf98ecf06ad223c3434d7b42d0e182c26378a891aa84084529125312(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e95372f5798d8cf5b168860f2adb43b5e43d7fac651d599ba1db83c2b8d2490a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35de908783c0cb02dce0d329203d54375ffe5fb07c742452dec56dbb10c6f902(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7df878fb5151cb858fb49703f25da196b713252ca62c1f0fdc79a991a38395a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__077c78b5986727564599617f8e8600c125873239bec9ae47a6d54dec7b034d75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a53bc6cee5e7fda1427dd3d922c2d7f94c47b80e976eb17620368c8ae0dcc964(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f91a06cfe4080a0e715802b6c74cef948c72100a1bb07be0de4e0afeaef317e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b3e84210e1341e0e23be719e5edb341fb4632aa444c27f808957d0c1f6fda30(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e00e46fbb015a006513f33a18756f0da48dc6d2d38e63ef92440bacd9ac22d7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fee650df61d94a8081b5649b92dd93c1e8706525fa5ffd5dddc255079ac96479(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9904adc936d08d1e2beaed9b36ddaa825937957308de50c32c669a4f08971ba7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b43c2ca54fcefd5ea7f2341d8237b6d0d92a504b33f9bb02338099f46462f6a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6d14f941ae7d804faec95d4c431916052dd90bbd3b8b0f7fe644064dee6af8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10304a915b54da186d6c80d5c07b7888ca3a235c2dd12482037a269d3e45cb89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba345a94b0c9a15b09591a29145ff0243f844f42740c74b0705f485263d36680(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecb4bd43632c7942dcab9ce39a416b46310c23e7912c5b6120537bdcc4ecfac5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae56ff67def4e984b583ef2f691687d5fa3802db4aea118d44ee95d18a3b0d10(
    *,
    name: builtins.str,
    args: typing.Optional[typing.Sequence[builtins.str]] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ff528ef5242b5fd9673d7ac9dbd553147f946dd9eda49518cf12b687b22e43f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88a1c4c6764eafd54f3c59c72fe9c69e533f253ad30881ccb43d2ed82e0eb688(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcc6f783f605dfc2be76605fe4f102be595150fc6718f5e70ddc5533cd1cbc86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5828f3ed8e499f83ba32ea999e80bf8c4dcff4a0e76703ffc3461a23d6707389(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd3de63ba96b2d81ab85d9055e8cc1593f92c26ebe72b63e2db8e8adec018812(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40ad9e6cd84281eb9d05be5e0a96b6d32af4fc4de50bc8a731884f070df5ea63(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsApplications]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f41b04bfe63ff2c9ebbee74d8f5ba7e5de006b026c7f0b2f4f4b99e8f05678b1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c94cabb01fec19b25178261973667d1c5a0f3fc273ff171605e17b9bfc3211ec(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2f2dc913c70489ea16df9d499320a4a91f957214e2adc4fb51c00ef3c5686ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8008e1a3c742c2a99fede8e80365a3668a4b28a97f3f22aa422eb6a11729358f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90d45f9e4211dd69e822efacd0db9a2953ac9bb28b5d7bdef169563262f4b441(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsApplications]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__705eb2415527798362a957d28d1d4e06a8b87c134584a90b9195c991013e482a(
    *,
    bucket: builtins.str,
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12f98c648a56c287eff86f107363d2ddea6385437e31e428480f62cba89afa8c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b7c4cd4e0616c0b09b4851e848641dac806e971bf27850abf1e8bcb9cde75b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9ef25eef165a69a7d111b9f86ee294f420841c0d81d77953d436fef5aac3bf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37f1990c32e2140d35adbdc612ee3e5eda0d98051a1367ee90ddb629aac1fd70(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cc6b6cd84a5df5ce39b02b98ee7dff68d2533bfe5ec59fee2aa907ddf8cba78(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2db102dac528e68b8dc142a4465bf668538da0753ab887a8aee66582652eb4bb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsBootstrapActionsFile]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39150cf413760e30ace04b9424711bfe778ae1c75e9a680db4135eff5fb22563(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5243e5458156aecd3102d9ec6d0c1ef030df8707443430b51f19fe2624d3b436(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ad4b3fe3a6190df076d27ecab9b588eedb1a5ef6e619f8ff57c108fc914a6e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e547957db1e5f9a6f57d402e42e3f6aa3a2ff1820a252a531b236ca6480a976(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsBootstrapActionsFile]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fd3f84c4798aa9acffa9f47fd926fb3a611a32927961b59ee0010b4da12c2bc(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    strategy: builtins.str,
    additional_info: typing.Optional[builtins.str] = None,
    additional_primary_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_replica_security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    applications: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsApplications, typing.Dict[builtins.str, typing.Any]]]]] = None,
    availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap_actions_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsBootstrapActionsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: typing.Optional[builtins.str] = None,
    configurations_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsConfigurationsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_desired_capacity: typing.Optional[jsii.Number] = None,
    core_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    core_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    core_lifecycle: typing.Optional[builtins.str] = None,
    core_max_size: typing.Optional[jsii.Number] = None,
    core_min_size: typing.Optional[jsii.Number] = None,
    core_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsCoreScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    core_unit: typing.Optional[builtins.str] = None,
    custom_ami_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    ebs_root_volume_size: typing.Optional[jsii.Number] = None,
    ec2_key_name: typing.Optional[builtins.str] = None,
    expose_cluster_id: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_weights: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsInstanceWeights, typing.Dict[builtins.str, typing.Any]]]]] = None,
    job_flow_role: typing.Optional[builtins.str] = None,
    keep_job_flow_alive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_uri: typing.Optional[builtins.str] = None,
    managed_primary_security_group: typing.Optional[builtins.str] = None,
    managed_replica_security_group: typing.Optional[builtins.str] = None,
    master_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsMasterEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]]] = None,
    master_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    master_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    master_lifecycle: typing.Optional[builtins.str] = None,
    master_target: typing.Optional[jsii.Number] = None,
    provisioning_timeout: typing.Optional[typing.Union[MrscalerAwsProvisioningTimeout, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
    release_label: typing.Optional[builtins.str] = None,
    repo_upgrade_on_boot: typing.Optional[builtins.str] = None,
    retries: typing.Optional[jsii.Number] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    security_config: typing.Optional[builtins.str] = None,
    service_access_security_group: typing.Optional[builtins.str] = None,
    service_role: typing.Optional[builtins.str] = None,
    steps_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsStepsFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_desired_capacity: typing.Optional[jsii.Number] = None,
    task_ebs_block_device: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskEbsBlockDevice, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_ebs_optimized: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    task_instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    task_lifecycle: typing.Optional[builtins.str] = None,
    task_max_size: typing.Optional[jsii.Number] = None,
    task_min_size: typing.Optional[jsii.Number] = None,
    task_scaling_down_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskScalingDownPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_scaling_up_policy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTaskScalingUpPolicy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    task_unit: typing.Optional[builtins.str] = None,
    termination_policies: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTerminationPolicies, typing.Dict[builtins.str, typing.Any]]]]] = None,
    termination_protected: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    visible_to_all_users: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e58a27a2ef3a2f811fa7ed5f8dc32c9795f7b0d6c99a5c11ddbf77db08b64c5(
    *,
    bucket: builtins.str,
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea2fef2def68cfa74a0c0bfe5317c0b2ebcca8727376efd2052f66e31d802e93(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8edf143bd6144d0d82ee9534f87bc04bfb3e43512b60ceadd8529cf59a087e23(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df5e413199c4ebafe258eba81bbd35aa411a82d9d30169882830b01010f12577(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb104fbabcf850af0f57f5ebc9205abbddc8c4b4a440ba79662d5279d51205e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2cc5c6cb0e1f82b64629b19f377a8d65073f5785406bae7c99e056f00793e90(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c816e3530d807924ba2d492bef9713f78836dad1f26ebee2bc9499bbe43bede(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsConfigurationsFile]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d719f59345fb014b89f72cd782a1538e15ae585310b76a4a011b2a9472d0859c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a18e34aebfbd8cd271b0aa3b43c50c63d0db621fe9b4952183d60b98552716(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3928a7c1fed04cb77104e31756650ac9e67d10ff7a4a4b2b29c41ccf72d04e52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f3bf0712b03997fbad43eb6a1bcfed2076ef79c60af5aee4a91f8096f97d632(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsConfigurationsFile]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aac54b248fa050634f592a97b3b16bef65223bcb1036b0ca8911b9e8dde555dc(
    *,
    size_in_gb: jsii.Number,
    volume_type: builtins.str,
    iops: typing.Optional[jsii.Number] = None,
    volumes_per_instance: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5433d2b9ccd4e000d552c20d8f1c038b8af0dba0fba75acf63c2923bd063474(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f70c556ea463921e4af695153b70d54fe0f0d5f610c8cb53d7bd90d73d566b3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f45b59cbe9ac10e704acfabcaf05e89aa16ed8874b78347a3d3c96674252530(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f47216f214bcafc529839e4f4ac64f41bc0f708b7da8b4bf0a7daeb14c565e51(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82edb5484e3963848f51252b5385cad949c9086efb8fce4da1af882a014b09a4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63dc14ba834336b334dec00764d86189d8f999fe1fa92736fe1546d3d50b9fad(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreEbsBlockDevice]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b7da1e03ef904001d1909b40dba7e960c82f9fc2aba7c11803f5877b227113f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9319afe2a59862ca02f5b4344ecaba3cfb671f70dfbd432586fc2967b6ca4ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48b0130f3e1271e3e8f3ef80605e42ffa48de4b3acdff6c21d6d4c4cd245f662(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38011d5d331d5f3d5a4413c0df2ea14e01e4bee394133f629f661897e0cadc4c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ab5f03e3d561de2e6a6ef53b07290c4bd984ac971c3d523a6978ae3cd8a42ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d34219a4e8373926902b85eeb9d7abb909e8c6b8aa70b7a738075d49630419f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreEbsBlockDevice]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53a28d95f56e0d7879e294434228c1b77137bf2f146dbe55f9198702b9dd16a1(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    policy_name: builtins.str,
    threshold: jsii.Number,
    unit: builtins.str,
    action_type: typing.Optional[builtins.str] = None,
    adjustment: typing.Optional[builtins.str] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    maximum: typing.Optional[builtins.str] = None,
    max_target_capacity: typing.Optional[builtins.str] = None,
    minimum: typing.Optional[builtins.str] = None,
    min_target_capacity: typing.Optional[builtins.str] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    statistic: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a84509548c4b9bb0724ace007ea401e859349b2265ec99a50e0654dbd1d43fa6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71b16cfeb0a9286f331c2d2058f8287c2d3012240711e831b130c84aa6093cc8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74ba0cb7d7a5670fe27c4a1eb279df56afa93f6c4430566f50295911934029df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2baa01221d515a3e6201418c4629a9f714134307cade88d072dfecb8b7d9c31(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ad445879371dd0c73a8ac8499663556428d083f3239ab07140b088f2076a419(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71ef72109d2670803825346bf20d8a6ba33b9113370debf1db38cb3954ede69f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingDownPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86b52bd90b61f954824b7f34cad9394fb819f4abb5af60f535d08c7b242e30ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9a5488ed174d075b56beb9ec4b66423ca3e6cd703547d6f105df9d2a740d4c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6f7a53739525b82f1387947ffb7adbdff565abb5f0342c119ca277f8bbd655a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7229ee56482859f5bfe329fa3ec1517f6d9eac25abeac9650408886a5c9a1538(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afba621086114143c0c096042b163f1f5d2e8d4aa224f5601a3001042bc0530d(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8b6e5b0d2ea126eb73225d419e7f421a9faf62abed3ab9c0156b56869f4e52(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac2dc8d9963dd0c433df8b7df06f8f201311de689b37266932e77786081abfbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e8db23110d8f200118d687406e95d5297df1b6a4e46d6e3431a4e34bf365ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2400a74eb65c6b29523f7d3801a03d7b92a9c4c3a72ae7c4f5edf8cdd0505dd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf6e1c81742436dd0bb5e28868da5f6a53e06f398f329aa0346b828583f684a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27fad4d7df358e7be0ceeb7bf85f48942d82efff594f586cfe1fa8f9a7e4747a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c9e093f4a634a1ed649904cfd2fd498b5513b5e69cc37e44701a639586f6496(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24f89b2a6ffd8ff5d8e0ab89958a1c3b7cbec6417fe105243fda4935e3ec8d80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76bcb355560a6e98382533fe549b9477a29ba605742501a463c341d2300b168a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acad1cdef874f1ec83bfcb6dc7c1b7569aebc10d3b1b196b19240529feff214e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a4622fc4aac24483279e29265fa63d513c31e646b5fa1b285ae25df619464ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b0b37de1ea8ba063cf06441a90df6a34b3c424f2e05d42e1b70c078ab596719(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abe553a6f97c62b62a1dd63dc8ade39fd9d95ca7a168dabcdd5afb482356d81b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a4571332be562c8509316294970a6ccba53ddd96375f1ba55d6e2ec7625643(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a59598c5f2f84ccf293227140e578f9cfd9179d6f5368e0f8978189eb7b99b4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingDownPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7b4f2a28e1edf851f73f3a3b0f6c45a6a700afa5fa6de753a40ab8d3820d64(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    policy_name: builtins.str,
    threshold: jsii.Number,
    unit: builtins.str,
    action_type: typing.Optional[builtins.str] = None,
    adjustment: typing.Optional[builtins.str] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    maximum: typing.Optional[builtins.str] = None,
    max_target_capacity: typing.Optional[builtins.str] = None,
    minimum: typing.Optional[builtins.str] = None,
    min_target_capacity: typing.Optional[builtins.str] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    statistic: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e40436a685d4deb371baa203335866d9fd7a7924511a755294ef5c6c1ca21cbb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cd2289b2e9dd883e719e0a99596ac9302001942057e6c361787627d1d02da4c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b6bcf7e5fc556e18a5ee96785d296a17829e29b35049bb01b03cadc481eb5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98cba9a5e0adc8604dd1f626d0c2bea13be4c98fc5d340718fc2c24ddc0ea93f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deccaf68dd8e12765111ee56731b46955266782076f56ff84eed5e3d63e60a74(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6839d96a72477c19a50def466e503ccadd8862d5d540c7484322251ab11d66e8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsCoreScalingUpPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9143be8cfb15bbb0a34b9f4980b8e7662b3b59ea46c14421c00b7821ffd3076d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3f278ddd6a34ef75cb14a0a4427093dd2da235c8a75aa9698e4b6002cf8b5f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd9286ff100d791731bdbdcc8be8a2617aeed5c0b39965a2a91161e00ba2bb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93b0af547d1c36de6dc9bdc870a6ff11a91a91616d4519a79c93ecc86800d3d3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__105f169055b9edc6cb6fc05669959666fae62f30a561d2d9b427f995f1323b84(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b71aacae9d3459f2af1f54c0d408175e7c0cb9a91655fd2aec0be15e69d95fef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e71cdd9cbf2480cb775913bb74ce9a40cf3e705d1931f265dba66ec1ff6844(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d8e785c3572109e0b3160d42960042c2238b7efbc752eca396b8b5eb4fb0736(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76376cf32c6aaad3fa459d564e536c6341df5315da28def704ee4c87ae8066dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88471549e41f4688b843f065bbe77b8501d9b7aa451155c1b54c58beed3f76c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79cd13a311342c2e19a14f26b7f4c0a41b60c8aaae5a749148dd8bca6a0bec4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f35a31875851c9220de593ab6ab5b91464494aa77cf5ffa6e9ea17dca2ff9fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da1dfc34ebdcfa90a802c0385e5f3dc734d0feea2d9aec0dc0ce81be3f14e112(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d2813fb9caeb5386ba4c48f9c53fde71ca0889667d20c43ead7a0920382360(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b863c88b1460bb76d9247bfbb14072ffad16d956a2cd180beca46cdeb3ce34d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13baa13b686f25003829e52f95aa68576c7e681fd0f38497fbb8d0d65700b61d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a869c867cac9aa5ef672121c0763fe5fff667f517a15a603fdec6bdaa2cb52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45f0c14059513db52d8f010b35fdec2c16b63c2ba1262215ec76a4b56ce2fb4b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__613fc6d577a49e2897a86bd0e67319f80a5b5bdebd2d552153ff8ab74b99ac73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99c3d8d373913fb59615a84aa9b66d320040fd1e3f59e6d14cf941d114afee3e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsCoreScalingUpPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2479dccf4b583fc6d832282aef83692ef08a7a6da043095fca0365ddefe96f69(
    *,
    instance_type: builtins.str,
    weighted_capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdc7482e3b3e60ffb65cb393d6bb0668e5a9280616c84e4741fcc9eb4c0b9582(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6a1c604d75fbdcc5947f028d9e9770a91b986f675feb7f18b2acc0f650161c8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b569b7996f0a2cba345a939f927e00b995a054b9277159ab754169b84b4e470(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26fdb533d378a769437c3c42ab0015bb969d5a24ab318a7a063ea251d2a53a02(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3439186de70beaba3f007ed4f8b57914ef9b1782e478958213212e3cdbd834ed(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51a0c6fa51bf92eb817570c07bbf01ae395b2fc79e045507480325671675b6c9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsInstanceWeights]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edad60461a7745ba44716d5a40837adef5f809e6402336e30a18dae145b0e65c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dbe6a7f6059c292a92a76a6be3a67138a29b2b636f1263a642df78b5283711f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37648b53d6cc00cdee1e9a2e8f77894b754ab67bdf45c304d725f1b6e3b3eca6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0338ecb9ea1cd9e641c65b55f2f4fb6c5958f47f8453f359a02fbb87952f9e52(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsInstanceWeights]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88b0e95ee04d342a6e479cde3f2f86604cbfb152f400ae65ae4aabdf803c2b3f(
    *,
    size_in_gb: jsii.Number,
    volume_type: builtins.str,
    iops: typing.Optional[jsii.Number] = None,
    volumes_per_instance: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c8968aa648183efb1afb00dd3c88d562c3c5e464ed97099897a0b31fa514bb9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70905dc1f23dfe4887cabc19eed8fca2350f40a88aaca941656fc8f9a98f8bd8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d843f28b5221636f5025d02d3e3b5d2095ed354798108b03f516e1bbf338aad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d2fd4bf7359e8cc5f7dec41c855d53a556622ce3fa181a2b06a05870cc54a47(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6576f703fcac9c969d00753100e434dc0a5fafce09ee999ad01218604e79f3c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4e06c0c1e2adf0ce3bbc4230a281406731a5ae4dea79ba3331f18ad150e659d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsMasterEbsBlockDevice]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b320746ea79da3539f72ff92691a9337cf6293521544bb0b0276f4d3226ebfa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02a29bfedb88c6c25bebd3886e12d7e01973c7de17fba093b12eb1ab9327a0b9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02e14ec1e16d010c317ddcf8f3898e85baddd97e5b005cdc5f60785d04a16192(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06bfdef1c092f2c4ab8f3501695d5b96895b1d1b3c60667890cf7d49a718ba2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b91c8fefcebc9602787dadbb7583ebb748b4e24f4832ad7991b7791407798e85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555322fd007ad96ba9cc840f6484878152ed5a25fe6d4867eb57b40ed299e56d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsMasterEbsBlockDevice]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ce4db7d37e0833fff2fb9689ea720cdba57f5251d50517690c89d2fce31cd38(
    *,
    timeout: jsii.Number,
    timeout_action: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50c3d7dd4b73c0645e51c67aa0c164fd4f896a1361c2f0f9c9bb3d60b9be9b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f7f6530920dfd911e20b99c9288f405c195e454288b56120255341028a7bcea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7845adeff8b4c5a20287bb43ef9fd5eda5b0114638a5522651d20d0ccc1caf20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c11e70153bf6e7c3ef58e91e7c036cde0ee5605899ae39d403fd654818991915(
    value: typing.Optional[MrscalerAwsProvisioningTimeout],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d62be76a5206c108b843168eb0204e205d73d7e52d351c73ad1206a2aee24917(
    *,
    cron: builtins.str,
    instance_group_type: builtins.str,
    task_type: builtins.str,
    desired_capacity: typing.Optional[builtins.str] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_capacity: typing.Optional[builtins.str] = None,
    min_capacity: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0618dc47b6ee1de1ba517d38305d54dfdd2fa1b57f4315782bfab2164c49122(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1741c981229854bf6c022a6bd738619d8a093355cc1b98fa507e1ef8ee4a2333(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cff6f78963f49fcd2cf81864c2c9aac3ba8d1ea574b0f4523cc2e496280cff0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6fc7c4d66eb7f29df3c287e945010661379da67f1d34db404d6f3bad72caa47(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c21e5dd899b5ab672095d269fe948fb16329f8a1d84629bb8b08cc8dde9f186(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13767b579fd578f8d849a1a4dc6872b0cc680362ccd10b616f7b48d6d1922dfa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsScheduledTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f264ea9e9ec6b5813fc044cafa713c8e57509508f4935c26ee73ebca935ccab9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2ad6703af622c3f50e79003c64bb2c8555509c165d476804ce1fcdd69085e8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2625e655bef4d4bef4e5900532cedd54ff1b0e8af0ba8880b26fd43dc45b57b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5da6bfe1ac79f2ff62bb06730752e7fcebb4ebe2545c18e6084d9ba1be1a083(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e16cd43051053183d7be5f4ae1b2c237787574b947b263c0777c5cb4525ef26(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e7e5f059fcb13dd21b3c6c0ca03a66919d3db88bbadc380938baf654d4dc1bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bea32febd59334e31bfab531c76e6c7e97125d264cdfe382fbe230af34c59d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__227cdac360f11ec2c644c4191ee70cbdff0aaa659bf4426e0620569146c6a3ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc348828c579b04519d839a66ea40d414f59a75f3d77a33fc3cb5a5425d3379(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsScheduledTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678827bb26a92b646953eb8f7c415feee1ed4ab21cc9879ce3115055b829f377(
    *,
    bucket: builtins.str,
    key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e4c567eb3717122a1fcc85eedcdeca8e49002cc71752c75d1127a40559ce8f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710fab9f6d3ebe75b8899443f97a834c99eaafd854b1eb1b221a515987439dd3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ef9e85886cac8c9f334329ddb431dcd32f905e630f625419c9df17b19028f48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d0efafc691dac8715ffc555d1d5c033f3d826e4d639f726f1514a60de45362(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__550170e093d12b13000c72fcd0b454ce72c400ac83c29e20159f15f1c2aa9e34(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6490755677bf85075dfd26ceb5880e780fbc03d698cbe2dc76d1156e3780334(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsStepsFile]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84216a787906854229900a17a64e4327f25eacf71a59293ef816f615722b20f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb69e53a3826884bea2297570606b8aaa232b372cad3aeeed4efad5a207ed396(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e30c57a49a16e4c65220b3ad70289dbde7a98bf95d6fecf48592312a5c55e895(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f21c818a64edf5a34a2c95696107ae141dcda1f0e1fc00f55bfadcb0f3f742a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsStepsFile]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0270fdd124a61e495fad367ee893f4d43876248ca5ae9a043a96b6de438028a(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8da5668ee5d58aa58b9c5697af43f3a508ed18ae1a59ea3c5f790097a4f2103(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffebc576474eadee0d8c3797dbf9e70f2e3aaff7bd3907891227a76249baefd7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2e620b3e7f5448935ee6fdb434aa96ae3a99c2fdfe1d24507529e34ba10a429(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ca8f74ea322ab293d33f561ab3e33bb2724afed987810eeb2820ca57042b5c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5fb3d155bfa5d088798a248659c61451a04e970c641f6dbdeaae2eaa6df68b9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be75ca3b0a13406918cc0a79ba3a5febd21af239f829a1aa06c4e5698cac0503(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b517fa50013200ccc3476c33f92ef6a32a58d3252125f6855504d617e809b512(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8ab01175cfcaeead65d339fefa78d9a7d6154f42f16f9fb2c7ffc40e8329253(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e3636a71d1d4d01691e9cb362065532a396a99c6e78f162990c30606b0603f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24ac295df8350986a398f22471653bb53a6aa3ad8926a9705ff55b9819a6eee(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a5f6e47b9ceedb9bd87fff8a8327fa9cc7c3ad9e4d8b46f63db9bc1caa1f603(
    *,
    size_in_gb: jsii.Number,
    volume_type: builtins.str,
    iops: typing.Optional[jsii.Number] = None,
    volumes_per_instance: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93aff499b29fa5690360a5c248f7b485332a4fa729a4ef6ab9d19b46053f127a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c8f6966617e14d8455f5f79b68d36388b37f36384680194038ff1b8413966af(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d07fbefd4766e45b0277b469ccdbcd40068ce8aceb01fa597ab5904bb0d3d01e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c004db2fc99e7fbfed7263a1861c4b13e708b520d04f92cfd8f1910353756e0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30d958a1bb1e4ef99cea8806da4802ad26374ea52c511958351ab52afbc6db6b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7f403971ba5bf078bbdddf5b6e60526db049883a9e20452564324a7d9fe7e7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskEbsBlockDevice]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff41d02c31b629cadc0af5045a4126c5393a4ede0c87ef973fb93fc4ef0af829(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a226fb2113dca1be1978b79c3bff18827aa10e782abcf5e9e58bd6c930d7fec5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a04e4e469f0f4d77c8f9d167d5b79f5c581d9c82285b5eae9368b62ba28e51(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca8776c28f378b20f9f754a9a1e14055223b46880c05b61ea4d4597d2efcd42(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8672743a6b87395ccbbf7792adb79623610420826b0d870d19cfa6b8ee451f7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6643f7ead57aa4a88ce635cb26018d8a8656bda07fece8e436e5a2dfdeb75531(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskEbsBlockDevice]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11edbcd01868d9b0df798a0fac7d590c0a5cf7aae53cf76435b743c5a0efc6a2(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    policy_name: builtins.str,
    threshold: jsii.Number,
    unit: builtins.str,
    action_type: typing.Optional[builtins.str] = None,
    adjustment: typing.Optional[builtins.str] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    maximum: typing.Optional[builtins.str] = None,
    max_target_capacity: typing.Optional[builtins.str] = None,
    minimum: typing.Optional[builtins.str] = None,
    min_target_capacity: typing.Optional[builtins.str] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    statistic: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd87d3c6e04e9a8ddbe82bd65b69af3b9ee7359e47276ce198c9140c1080671(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5077d6cd8230259ff3332d926b9981c8e4aed0c38396d0998ea05eb07ceacdc5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85c45aef4310769a30d4f5f492c299c3d1c4cfc3f831f1aa30bf44f81233c317(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ef06868bbc62ba6445b7772c124396105907b1ccdeff8b5dc2c483d6fefa96(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f375387b02dad9ef421d827f4b9d494538ba88f5f7998040fce11b861fcd7363(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e936235e39165b34964d7d2c2ffee353dcb4d437a2ab35302ef0640998ec4d8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingDownPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26cd704a60db32aa922f8b351b5bd3364ed96b71de538cd00f8e3d092bd7da44(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c674c18f7c9bd7743031705ed7d593bc064074086560b5fdfb3e608886fe8d52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8ac515857043e08991d75ea9972d2a6864f130aec557186b8d30bda917b78fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde0d42ab1ae439f67f45d2f82190add58c2186b336b538122dbc4a8426c44aa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1532252e099c7f85eb4d02b795e7d463e142ed45721c7f2be32dcedcf2e94246(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43f3548a056f8807dbeb22de4440687b36ad92321e94ffd99a437ef63bb5a47c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19b574d05aede48e12f58d307f8b1b0e1845d261072632b6e2d8f04d98203d58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d9d8e7421546c2e35ec6de3b63eef5e2f03837d2340435907884a1479cdf80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0d6756e9bf5d8e770105f0734e934d2528b9a3148cd21fd541ca8d4630615d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08d7dc714785d8c1805e84e20ab0851421415edc4ee90453f11d8bc183b0edbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c7cae8220f0996944af45ca8e2cea4e11c3df85860e9463e714f7032f9236c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e55f05b20d5705e0389df9010ffd28b858cf3b5194f6915638716f0adc2a147(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b41156d68b34d5278e02b2116684da18da296e14b0d2d683078623798e862b25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afb5f1c84a9cd4ab3bfbbcc6123087efe7342211ed486ff239eb091ea961451d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8018899da4fcccd2f51d8266b1021ba401663753163c119028197c7b426b2442(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0f51e0e7c84c228bce08f76a67acbbee494915283429957715091a733aadd67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46509f98ef250b403eaabc34bb509c7e630a92593f3dac03575f5a8c2101774b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14cf46d85ff46c5f68e3beda604ee818fc7771f897e30c6ce4d69ff5c5740e8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d0c1315a5f649933a8bd5e6d35683bd6c03f7322ea7996989545b9718f8e523(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0221c4e4e4eaac4a596711d32a6a2e31420ec221fec56281346f0233ac0ad60(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingDownPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a391aa9cda31e88d3a4b3569f8fed923322e8406cdd0585a0241c61c93e4051(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    policy_name: builtins.str,
    threshold: jsii.Number,
    unit: builtins.str,
    action_type: typing.Optional[builtins.str] = None,
    adjustment: typing.Optional[builtins.str] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    dimensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    maximum: typing.Optional[builtins.str] = None,
    max_target_capacity: typing.Optional[builtins.str] = None,
    minimum: typing.Optional[builtins.str] = None,
    min_target_capacity: typing.Optional[builtins.str] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    statistic: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__940755bdca38b24d556635f7c42a3d6e11e14ed27ee49209037fb36552b93318(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d98b7fe34d396797248cfa93aa3d769e571fa1c6efab0654045b99cb34e15620(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7965f41e51b798b914489f9984b3abe2d65b8415bf312f9352231370daa53d7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c641a57e1dbdb7780a9483ca9e8db0143011be5cce8b7334ec7c2c11fdb23b9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28473315ccfbcad4eea5eede04766355147a4ca8d136774e32b0708ff0f40421(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e769b4f6b32293b93180a696731ae8be7cfb259d2aa665f3050ba573cd4f5bc5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTaskScalingUpPolicy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7fa71e6b507b9a52e455b0be35a217cca387671a1130df4beb3ff5e7b61cd4f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2df06fa06556f92508b184a7878efe09a4f52bad83b0a8602a471d372c695e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__595f83f7cfa2fc95d9387f8cdbf6e621d540dba0b54014d3b27803eb4264005f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4370bbb1b3ebe5c301dc0bfc40eaa42c6588f4fea39bb83b57c9b0e768c11405(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__212fcd0d9e184cebee3cc1c0b1dff7e431c4ef87aa14c80bdfba06100edf0aab(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ca377c310dca476992744c103373093e9918394d33085db40e6e7b2d6dfb080(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e73218946194b5df3f256b1ff2c4deba26dd991ca080e2619d87e54f2fc7c9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af640838044e5c4f9e8bc238dd342fc219fd5f7d05e2e7a68829216b2bad4373(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfa6e3df14400b7e95da6d6753b21df79646c9edabe05942de0a37320cd7ec9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74da95add8b89d7f2369844a2e8a4955fa100b4196063483fd5d21412a206789(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc4991216ab10c1a7c1e36c735b034963bda4d53821a844f450f839473d88028(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbded019a0d408b78b7dad46a4e4459e61cc89acc19aa760c97c66f635a3a8a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__373c31c6ccfb7a98f301e1cce5e433c92c60236a30741f980cf9da6b96fb12dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8725cc600ab90894e4d840eeb50061a48f629d0234fb642ae978898ec546f3e6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe619003523e3d09d53b0c75129f071358427e7a55ec1360cd1969f6ba618e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a658e232469a4c755c4e107c26e3616916dce055b00363a0e005d1e1f613de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d12e9fcfbcbabd8ba032952428f20a8385b52287e5907bd6b159523925cfe90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac7ab9fcfe117567526c3901e14826f766877994a96e4f785ad5f53b70295d2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a7c2eb8ade81938e7f5a09285e6e9e51ab9f758421f216bb3667a2c7c08d91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2cdbcabe912a9faca15018e389b6504381d8613ee2400f1ef74508318dc321(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTaskScalingUpPolicy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8dc23f038a3b40d70a0e8fbb8b0046686e4f60d80d1ac684c0e75a9b0f8ad51(
    *,
    statements: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTerminationPoliciesStatements, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a2e6a504c43d7a50a654964dcc7ff8631b05198ccf01c8fa93f8ba59850da96(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b61904c14792acd964bef88a257b780da21676faac09b9cf37de50a95e614dc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfbad589929b4ae03e49aeb0a63ba667c09c34243fba3ad7e24d3cf4b1544485(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4454c5ead00463984045bca662d7be24f00b48df9357a812c9da58bd1c4a8312(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__496acc2f0dede17aadf92b3f067cadb01c39bd65dadb618a30d1941be211df4c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40a6d81651d2c22158b555fb59f655db77aca3cfe86b7089df60bd6aa2b1e0ba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPolicies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e976af347d0a6800002af2fb1a99884bccb3faec33c0813bacbc5bbad8b78ad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d911a0d915e44938b8f2196ad7a3d848610a88f8f68a1140d6660d6334125164(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MrscalerAwsTerminationPoliciesStatements, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8a5f8ac1cec7d800040d7b3c4f823b31352443eb49a4f3f6dbe575b2ea6255e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPolicies]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3beeabe220022b009b56a9857090794b4eae6f10e79303ec83232912fffb877(
    *,
    metric_name: builtins.str,
    namespace: builtins.str,
    threshold: jsii.Number,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    operator: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b53614e5f004417f66af64f11692b6c6d6604912250ec34033de790c2718c217(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea81d6c16eb1a9f1d13cdd6ab0835655c391aec71ae7eea70183ad7262e782d6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d15aa679682a6aba4bae7b6ccfa4fe9bf50151e97121cab9ef3b65362639133(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8de4272896bb2e4623e2004dbb43d15ddba4cca1bab9a30a36af9ca8abe41190(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6259d31ada04671d7897d69d11ea2534b7a1828963d481073588b8a09c52989(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64b0b66981b6be9f298b4a310f66299e77fe2b7176b53a3a9c56c507bceaf287(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MrscalerAwsTerminationPoliciesStatements]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b405eef79928256c3ca899f541f54586e96029c42f4a5dbb8e07851425a171(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a90db6e98ba5f25b05844e21537a630e2992aa6536c7738eae10e96587dc2bb9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3531fa6bd438a451faa17f6145f76cd364f58365adc4dba8366f1f83e5cae106(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f05b08d11483973fab510148429a3172a444b25f18c0e3e148840df866f08f88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5bb427cf840a1f6f6da8b92e8fc0052dcde8be28efffb0381d3d221abb04f05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__208c34b47d593acb814172caac072cb4ff4c037f4ece7a91395459f6dbe225f8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19a31adb26500746a1c5b062d529d0f21a3ad2e83b9b5795e59e5bf27c34f88c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e12d926fb5acd06e719bba6bf66142f84b187ce89a68daa8164a244f6360ca63(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe8c8aeab9b1fa100301cf83447c272568bed53e875fdcabcb918dac85cb772(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b09fec0b88d50c78c1cc44f4d01429a6be09cd62bc3e640bbddc8e9a1daae96(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, MrscalerAwsTerminationPoliciesStatements]],
) -> None:
    """Type checking stubs"""
    pass
