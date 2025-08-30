r'''
# `spotinst_elastigroup_aws_beanstalk`

Refer to the Terraform Registry for docs: [`spotinst_elastigroup_aws_beanstalk`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk).
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


class ElastigroupAwsBeanstalk(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalk",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk spotinst_elastigroup_aws_beanstalk}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        desired_capacity: jsii.Number,
        instance_types_spot: typing.Sequence[builtins.str],
        max_size: jsii.Number,
        min_size: jsii.Number,
        name: builtins.str,
        product: builtins.str,
        region: builtins.str,
        beanstalk_environment_id: typing.Optional[builtins.str] = None,
        beanstalk_environment_name: typing.Optional[builtins.str] = None,
        deployment_preferences: typing.Optional[typing.Union["ElastigroupAwsBeanstalkDeploymentPreferences", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance: typing.Optional[builtins.str] = None,
        managed_actions: typing.Optional[typing.Union["ElastigroupAwsBeanstalkManagedActions", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAwsBeanstalkScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk spotinst_elastigroup_aws_beanstalk} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#desired_capacity ElastigroupAwsBeanstalk#desired_capacity}.
        :param instance_types_spot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#instance_types_spot ElastigroupAwsBeanstalk#instance_types_spot}.
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#max_size ElastigroupAwsBeanstalk#max_size}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#min_size ElastigroupAwsBeanstalk#min_size}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#name ElastigroupAwsBeanstalk#name}.
        :param product: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#product ElastigroupAwsBeanstalk#product}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#region ElastigroupAwsBeanstalk#region}.
        :param beanstalk_environment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#beanstalk_environment_id ElastigroupAwsBeanstalk#beanstalk_environment_id}.
        :param beanstalk_environment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#beanstalk_environment_name ElastigroupAwsBeanstalk#beanstalk_environment_name}.
        :param deployment_preferences: deployment_preferences block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#deployment_preferences ElastigroupAwsBeanstalk#deployment_preferences}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#id ElastigroupAwsBeanstalk#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#maintenance ElastigroupAwsBeanstalk#maintenance}.
        :param managed_actions: managed_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#managed_actions ElastigroupAwsBeanstalk#managed_actions}
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scheduled_task ElastigroupAwsBeanstalk#scheduled_task}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0214bccd61c44ec9662f88a6f1565c3a1a05724b62375a7e13bae9f8bcb80b74)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ElastigroupAwsBeanstalkConfig(
            desired_capacity=desired_capacity,
            instance_types_spot=instance_types_spot,
            max_size=max_size,
            min_size=min_size,
            name=name,
            product=product,
            region=region,
            beanstalk_environment_id=beanstalk_environment_id,
            beanstalk_environment_name=beanstalk_environment_name,
            deployment_preferences=deployment_preferences,
            id=id,
            maintenance=maintenance,
            managed_actions=managed_actions,
            scheduled_task=scheduled_task,
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
        '''Generates CDKTF code for importing a ElastigroupAwsBeanstalk resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ElastigroupAwsBeanstalk to import.
        :param import_from_id: The id of the existing ElastigroupAwsBeanstalk that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ElastigroupAwsBeanstalk to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d2e095004838d5ffee8cec5e304da6e68c3e3f37a8d9d3d30d272289bf443db)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDeploymentPreferences")
    def put_deployment_preferences(
        self,
        *,
        automatic_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        grace_period: typing.Optional[jsii.Number] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param automatic_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#automatic_roll ElastigroupAwsBeanstalk#automatic_roll}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#batch_size_percentage ElastigroupAwsBeanstalk#batch_size_percentage}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#grace_period ElastigroupAwsBeanstalk#grace_period}.
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#strategy ElastigroupAwsBeanstalk#strategy}
        '''
        value = ElastigroupAwsBeanstalkDeploymentPreferences(
            automatic_roll=automatic_roll,
            batch_size_percentage=batch_size_percentage,
            grace_period=grace_period,
            strategy=strategy,
        )

        return typing.cast(None, jsii.invoke(self, "putDeploymentPreferences", [value]))

    @jsii.member(jsii_name="putManagedActions")
    def put_managed_actions(
        self,
        *,
        platform_update: typing.Optional[typing.Union["ElastigroupAwsBeanstalkManagedActionsPlatformUpdate", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param platform_update: platform_update block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#platform_update ElastigroupAwsBeanstalk#platform_update}
        '''
        value = ElastigroupAwsBeanstalkManagedActions(platform_update=platform_update)

        return typing.cast(None, jsii.invoke(self, "putManagedActions", [value]))

    @jsii.member(jsii_name="putScheduledTask")
    def put_scheduled_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAwsBeanstalkScheduledTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f71c2d941f17d721d339c7c862fb9b6b51d64add66901c0573760a63ee3a623)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScheduledTask", [value]))

    @jsii.member(jsii_name="resetBeanstalkEnvironmentId")
    def reset_beanstalk_environment_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBeanstalkEnvironmentId", []))

    @jsii.member(jsii_name="resetBeanstalkEnvironmentName")
    def reset_beanstalk_environment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBeanstalkEnvironmentName", []))

    @jsii.member(jsii_name="resetDeploymentPreferences")
    def reset_deployment_preferences(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeploymentPreferences", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaintenance")
    def reset_maintenance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenance", []))

    @jsii.member(jsii_name="resetManagedActions")
    def reset_managed_actions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedActions", []))

    @jsii.member(jsii_name="resetScheduledTask")
    def reset_scheduled_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledTask", []))

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
    @jsii.member(jsii_name="deploymentPreferences")
    def deployment_preferences(
        self,
    ) -> "ElastigroupAwsBeanstalkDeploymentPreferencesOutputReference":
        return typing.cast("ElastigroupAwsBeanstalkDeploymentPreferencesOutputReference", jsii.get(self, "deploymentPreferences"))

    @builtins.property
    @jsii.member(jsii_name="managedActions")
    def managed_actions(self) -> "ElastigroupAwsBeanstalkManagedActionsOutputReference":
        return typing.cast("ElastigroupAwsBeanstalkManagedActionsOutputReference", jsii.get(self, "managedActions"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTask")
    def scheduled_task(self) -> "ElastigroupAwsBeanstalkScheduledTaskList":
        return typing.cast("ElastigroupAwsBeanstalkScheduledTaskList", jsii.get(self, "scheduledTask"))

    @builtins.property
    @jsii.member(jsii_name="beanstalkEnvironmentIdInput")
    def beanstalk_environment_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "beanstalkEnvironmentIdInput"))

    @builtins.property
    @jsii.member(jsii_name="beanstalkEnvironmentNameInput")
    def beanstalk_environment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "beanstalkEnvironmentNameInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentPreferencesInput")
    def deployment_preferences_input(
        self,
    ) -> typing.Optional["ElastigroupAwsBeanstalkDeploymentPreferences"]:
        return typing.cast(typing.Optional["ElastigroupAwsBeanstalkDeploymentPreferences"], jsii.get(self, "deploymentPreferencesInput"))

    @builtins.property
    @jsii.member(jsii_name="desiredCapacityInput")
    def desired_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "desiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceTypesSpotInput")
    def instance_types_spot_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceTypesSpotInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceInput")
    def maintenance_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceInput"))

    @builtins.property
    @jsii.member(jsii_name="managedActionsInput")
    def managed_actions_input(
        self,
    ) -> typing.Optional["ElastigroupAwsBeanstalkManagedActions"]:
        return typing.cast(typing.Optional["ElastigroupAwsBeanstalkManagedActions"], jsii.get(self, "managedActionsInput"))

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
    @jsii.member(jsii_name="productInput")
    def product_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "productInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTaskInput")
    def scheduled_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkScheduledTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkScheduledTask"]]], jsii.get(self, "scheduledTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="beanstalkEnvironmentId")
    def beanstalk_environment_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "beanstalkEnvironmentId"))

    @beanstalk_environment_id.setter
    def beanstalk_environment_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__517a2e1565f257411b26e290287b297bd0662a2be7dd8286c85f0d6094a7417f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "beanstalkEnvironmentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="beanstalkEnvironmentName")
    def beanstalk_environment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "beanstalkEnvironmentName"))

    @beanstalk_environment_name.setter
    def beanstalk_environment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__148439f227f34910a6a7b8fc8e1ae44743a9a415992c12eafe4abfbaf3185ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "beanstalkEnvironmentName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="desiredCapacity")
    def desired_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "desiredCapacity"))

    @desired_capacity.setter
    def desired_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b4b9411071a66a076221b447ba7bf937a071745b50ffce38c392189ac188a2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ff5ce7692e510c704ef3049f7ac67d822f33e621d576a361a270f5a9755bb02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceTypesSpot")
    def instance_types_spot(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceTypesSpot"))

    @instance_types_spot.setter
    def instance_types_spot(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0386a5b009b0787b7a8ce2ee3d02f5b9c3fcd29b0244f7945234e925d231c558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceTypesSpot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintenance")
    def maintenance(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenance"))

    @maintenance.setter
    def maintenance(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c6ced020e68ca57d8c7533264eb9de1f2572315b6918e54a513f180bc46df6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintenance", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxSize")
    def max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSize"))

    @max_size.setter
    def max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cc3063860d8b608af954dc9bacc3b471c713f883065d5b6ed8866f86fb9bcdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minSize")
    def min_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSize"))

    @min_size.setter
    def min_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98bb2e369590690ebe7ff226441b26cbd9fece0cf6e234647e38f53be65523a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47244b2fe70b4a6378fc816a6820814fd2060aab2aa7134ec423296faeec017d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="product")
    def product(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "product"))

    @product.setter
    def product(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62272147604f48152e70074686f050e8aa8a92fc5b93b1859aeef623d811caa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "product", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a42818b8f3b75ec5bdcaf4c6319f942b9ec9792b401d48d840c3d518486d3475)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "desired_capacity": "desiredCapacity",
        "instance_types_spot": "instanceTypesSpot",
        "max_size": "maxSize",
        "min_size": "minSize",
        "name": "name",
        "product": "product",
        "region": "region",
        "beanstalk_environment_id": "beanstalkEnvironmentId",
        "beanstalk_environment_name": "beanstalkEnvironmentName",
        "deployment_preferences": "deploymentPreferences",
        "id": "id",
        "maintenance": "maintenance",
        "managed_actions": "managedActions",
        "scheduled_task": "scheduledTask",
    },
)
class ElastigroupAwsBeanstalkConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        desired_capacity: jsii.Number,
        instance_types_spot: typing.Sequence[builtins.str],
        max_size: jsii.Number,
        min_size: jsii.Number,
        name: builtins.str,
        product: builtins.str,
        region: builtins.str,
        beanstalk_environment_id: typing.Optional[builtins.str] = None,
        beanstalk_environment_name: typing.Optional[builtins.str] = None,
        deployment_preferences: typing.Optional[typing.Union["ElastigroupAwsBeanstalkDeploymentPreferences", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance: typing.Optional[builtins.str] = None,
        managed_actions: typing.Optional[typing.Union["ElastigroupAwsBeanstalkManagedActions", typing.Dict[builtins.str, typing.Any]]] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAwsBeanstalkScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#desired_capacity ElastigroupAwsBeanstalk#desired_capacity}.
        :param instance_types_spot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#instance_types_spot ElastigroupAwsBeanstalk#instance_types_spot}.
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#max_size ElastigroupAwsBeanstalk#max_size}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#min_size ElastigroupAwsBeanstalk#min_size}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#name ElastigroupAwsBeanstalk#name}.
        :param product: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#product ElastigroupAwsBeanstalk#product}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#region ElastigroupAwsBeanstalk#region}.
        :param beanstalk_environment_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#beanstalk_environment_id ElastigroupAwsBeanstalk#beanstalk_environment_id}.
        :param beanstalk_environment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#beanstalk_environment_name ElastigroupAwsBeanstalk#beanstalk_environment_name}.
        :param deployment_preferences: deployment_preferences block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#deployment_preferences ElastigroupAwsBeanstalk#deployment_preferences}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#id ElastigroupAwsBeanstalk#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#maintenance ElastigroupAwsBeanstalk#maintenance}.
        :param managed_actions: managed_actions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#managed_actions ElastigroupAwsBeanstalk#managed_actions}
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scheduled_task ElastigroupAwsBeanstalk#scheduled_task}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment_preferences, dict):
            deployment_preferences = ElastigroupAwsBeanstalkDeploymentPreferences(**deployment_preferences)
        if isinstance(managed_actions, dict):
            managed_actions = ElastigroupAwsBeanstalkManagedActions(**managed_actions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__575034abe4176a143c5aa72e9f3fde4822d1b606f5b9c06e2b6e665d64d7b21b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument instance_types_spot", value=instance_types_spot, expected_type=type_hints["instance_types_spot"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument product", value=product, expected_type=type_hints["product"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument beanstalk_environment_id", value=beanstalk_environment_id, expected_type=type_hints["beanstalk_environment_id"])
            check_type(argname="argument beanstalk_environment_name", value=beanstalk_environment_name, expected_type=type_hints["beanstalk_environment_name"])
            check_type(argname="argument deployment_preferences", value=deployment_preferences, expected_type=type_hints["deployment_preferences"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument maintenance", value=maintenance, expected_type=type_hints["maintenance"])
            check_type(argname="argument managed_actions", value=managed_actions, expected_type=type_hints["managed_actions"])
            check_type(argname="argument scheduled_task", value=scheduled_task, expected_type=type_hints["scheduled_task"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "desired_capacity": desired_capacity,
            "instance_types_spot": instance_types_spot,
            "max_size": max_size,
            "min_size": min_size,
            "name": name,
            "product": product,
            "region": region,
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
        if beanstalk_environment_id is not None:
            self._values["beanstalk_environment_id"] = beanstalk_environment_id
        if beanstalk_environment_name is not None:
            self._values["beanstalk_environment_name"] = beanstalk_environment_name
        if deployment_preferences is not None:
            self._values["deployment_preferences"] = deployment_preferences
        if id is not None:
            self._values["id"] = id
        if maintenance is not None:
            self._values["maintenance"] = maintenance
        if managed_actions is not None:
            self._values["managed_actions"] = managed_actions
        if scheduled_task is not None:
            self._values["scheduled_task"] = scheduled_task

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
    def desired_capacity(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#desired_capacity ElastigroupAwsBeanstalk#desired_capacity}.'''
        result = self._values.get("desired_capacity")
        assert result is not None, "Required property 'desired_capacity' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def instance_types_spot(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#instance_types_spot ElastigroupAwsBeanstalk#instance_types_spot}.'''
        result = self._values.get("instance_types_spot")
        assert result is not None, "Required property 'instance_types_spot' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def max_size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#max_size ElastigroupAwsBeanstalk#max_size}.'''
        result = self._values.get("max_size")
        assert result is not None, "Required property 'max_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#min_size ElastigroupAwsBeanstalk#min_size}.'''
        result = self._values.get("min_size")
        assert result is not None, "Required property 'min_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#name ElastigroupAwsBeanstalk#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def product(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#product ElastigroupAwsBeanstalk#product}.'''
        result = self._values.get("product")
        assert result is not None, "Required property 'product' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#region ElastigroupAwsBeanstalk#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def beanstalk_environment_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#beanstalk_environment_id ElastigroupAwsBeanstalk#beanstalk_environment_id}.'''
        result = self._values.get("beanstalk_environment_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def beanstalk_environment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#beanstalk_environment_name ElastigroupAwsBeanstalk#beanstalk_environment_name}.'''
        result = self._values.get("beanstalk_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_preferences(
        self,
    ) -> typing.Optional["ElastigroupAwsBeanstalkDeploymentPreferences"]:
        '''deployment_preferences block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#deployment_preferences ElastigroupAwsBeanstalk#deployment_preferences}
        '''
        result = self._values.get("deployment_preferences")
        return typing.cast(typing.Optional["ElastigroupAwsBeanstalkDeploymentPreferences"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#id ElastigroupAwsBeanstalk#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#maintenance ElastigroupAwsBeanstalk#maintenance}.'''
        result = self._values.get("maintenance")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_actions(
        self,
    ) -> typing.Optional["ElastigroupAwsBeanstalkManagedActions"]:
        '''managed_actions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#managed_actions ElastigroupAwsBeanstalk#managed_actions}
        '''
        result = self._values.get("managed_actions")
        return typing.cast(typing.Optional["ElastigroupAwsBeanstalkManagedActions"], result)

    @builtins.property
    def scheduled_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkScheduledTask"]]]:
        '''scheduled_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scheduled_task ElastigroupAwsBeanstalk#scheduled_task}
        '''
        result = self._values.get("scheduled_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkScheduledTask"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAwsBeanstalkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkDeploymentPreferences",
    jsii_struct_bases=[],
    name_mapping={
        "automatic_roll": "automaticRoll",
        "batch_size_percentage": "batchSizePercentage",
        "grace_period": "gracePeriod",
        "strategy": "strategy",
    },
)
class ElastigroupAwsBeanstalkDeploymentPreferences:
    def __init__(
        self,
        *,
        automatic_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        grace_period: typing.Optional[jsii.Number] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param automatic_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#automatic_roll ElastigroupAwsBeanstalk#automatic_roll}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#batch_size_percentage ElastigroupAwsBeanstalk#batch_size_percentage}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#grace_period ElastigroupAwsBeanstalk#grace_period}.
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#strategy ElastigroupAwsBeanstalk#strategy}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24e87010a066f8d55fdd4fbde8b67d867e25b336e3eae520fe32a8a78703cb5e)
            check_type(argname="argument automatic_roll", value=automatic_roll, expected_type=type_hints["automatic_roll"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automatic_roll is not None:
            self._values["automatic_roll"] = automatic_roll
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if grace_period is not None:
            self._values["grace_period"] = grace_period
        if strategy is not None:
            self._values["strategy"] = strategy

    @builtins.property
    def automatic_roll(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#automatic_roll ElastigroupAwsBeanstalk#automatic_roll}.'''
        result = self._values.get("automatic_roll")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#batch_size_percentage ElastigroupAwsBeanstalk#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def grace_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#grace_period ElastigroupAwsBeanstalk#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def strategy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy"]]]:
        '''strategy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#strategy ElastigroupAwsBeanstalk#strategy}
        '''
        result = self._values.get("strategy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAwsBeanstalkDeploymentPreferences(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAwsBeanstalkDeploymentPreferencesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkDeploymentPreferencesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72ec99970f29bad91258a0dee32efc6cb5095396603eec59f383a2daeb7fa326)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putStrategy")
    def put_strategy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5aacc7c39b1080881b0ec2456701cd52522d582f06cf59cdd870b81f0ab14a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStrategy", [value]))

    @jsii.member(jsii_name="resetAutomaticRoll")
    def reset_automatic_roll(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomaticRoll", []))

    @jsii.member(jsii_name="resetBatchSizePercentage")
    def reset_batch_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchSizePercentage", []))

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

    @jsii.member(jsii_name="resetStrategy")
    def reset_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrategy", []))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "ElastigroupAwsBeanstalkDeploymentPreferencesStrategyList":
        return typing.cast("ElastigroupAwsBeanstalkDeploymentPreferencesStrategyList", jsii.get(self, "strategy"))

    @builtins.property
    @jsii.member(jsii_name="automaticRollInput")
    def automatic_roll_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automaticRollInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="gracePeriodInput")
    def grace_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "gracePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ElastigroupAwsBeanstalkDeploymentPreferencesStrategy"]]], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="automaticRoll")
    def automatic_roll(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "automaticRoll"))

    @automatic_roll.setter
    def automatic_roll(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd20a11ed83a602e69124dc8cc5ec39dba648ae79946ae52647bb81acfce0fea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automaticRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9a5c647641688bfd9582a0b6b1f77c801188dcbd576af809e26b5225ebd119a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c515bf7814e3640e76fe74a22c838848865418f7738dd524a5a67c3634306dc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gracePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAwsBeanstalkDeploymentPreferences]:
        return typing.cast(typing.Optional[ElastigroupAwsBeanstalkDeploymentPreferences], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAwsBeanstalkDeploymentPreferences],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3c178b5bc9fd5ef17f07e0b8314ff1cabded20df8c572093ed9be8061ab0787)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkDeploymentPreferencesStrategy",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "should_drain_instances": "shouldDrainInstances",
    },
)
class ElastigroupAwsBeanstalkDeploymentPreferencesStrategy:
    def __init__(
        self,
        *,
        action: typing.Optional[builtins.str] = None,
        should_drain_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#action ElastigroupAwsBeanstalk#action}.
        :param should_drain_instances: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#should_drain_instances ElastigroupAwsBeanstalk#should_drain_instances}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c6e8fc4c351b9a3e2c9eac9dbbea5305101f6c7da2bd759b6a78ef83a6c2c4)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument should_drain_instances", value=should_drain_instances, expected_type=type_hints["should_drain_instances"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if action is not None:
            self._values["action"] = action
        if should_drain_instances is not None:
            self._values["should_drain_instances"] = should_drain_instances

    @builtins.property
    def action(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#action ElastigroupAwsBeanstalk#action}.'''
        result = self._values.get("action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def should_drain_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#should_drain_instances ElastigroupAwsBeanstalk#should_drain_instances}.'''
        result = self._values.get("should_drain_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAwsBeanstalkDeploymentPreferencesStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAwsBeanstalkDeploymentPreferencesStrategyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkDeploymentPreferencesStrategyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__16df345f3b4c870270f9b46ecfa70496ab3016a04769250630e567953982a832)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAwsBeanstalkDeploymentPreferencesStrategyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb92f58ea12f5c17136e41e29a46754369dfb598cb9de72bf829ac1cad1ba3e5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAwsBeanstalkDeploymentPreferencesStrategyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc97c04420eadda62e5176706c9d32315a79df7aee5f8403314e681fa25b82a2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f9429c3614905371daf5e8f3dbd916f2ee7d7f4cdc32e2ee1e4bd68b557768c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__967c4e81238e1ce4a4010667353a2383d7dc46df694058dc75b1f4771700f061)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__708033e716a63f9990c2ea170f63445d39336981aa69788ef45281948d54b2c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAwsBeanstalkDeploymentPreferencesStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkDeploymentPreferencesStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0f983d6729d4c444138e0da93ba1f1a7cb0eedd9b42f3bd06df692e9209f0fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAction")
    def reset_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAction", []))

    @jsii.member(jsii_name="resetShouldDrainInstances")
    def reset_should_drain_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldDrainInstances", []))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldDrainInstancesInput")
    def should_drain_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldDrainInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2a94f35e2180a66072e9e0b4702ce585ff0ccc141f876ebc493485265723a1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldDrainInstances")
    def should_drain_instances(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldDrainInstances"))

    @should_drain_instances.setter
    def should_drain_instances(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__552c811c0d2b67bdb0dc977606f63408c267e14285e49d8c7547804b7cdee886)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldDrainInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb279a8ae34a52b05a755fa39961772bc7025301307addf80778d615bfa97626)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkManagedActions",
    jsii_struct_bases=[],
    name_mapping={"platform_update": "platformUpdate"},
)
class ElastigroupAwsBeanstalkManagedActions:
    def __init__(
        self,
        *,
        platform_update: typing.Optional[typing.Union["ElastigroupAwsBeanstalkManagedActionsPlatformUpdate", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param platform_update: platform_update block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#platform_update ElastigroupAwsBeanstalk#platform_update}
        '''
        if isinstance(platform_update, dict):
            platform_update = ElastigroupAwsBeanstalkManagedActionsPlatformUpdate(**platform_update)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddb5617a64fdcb36eb00bbe5d5560edcd5934dbe3439ee50c8b397164b5041d6)
            check_type(argname="argument platform_update", value=platform_update, expected_type=type_hints["platform_update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if platform_update is not None:
            self._values["platform_update"] = platform_update

    @builtins.property
    def platform_update(
        self,
    ) -> typing.Optional["ElastigroupAwsBeanstalkManagedActionsPlatformUpdate"]:
        '''platform_update block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#platform_update ElastigroupAwsBeanstalk#platform_update}
        '''
        result = self._values.get("platform_update")
        return typing.cast(typing.Optional["ElastigroupAwsBeanstalkManagedActionsPlatformUpdate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAwsBeanstalkManagedActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAwsBeanstalkManagedActionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkManagedActionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e3962916c5d34176b3709cfbf95516bcd7891858a49e7d117d4fa03c832ffae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPlatformUpdate")
    def put_platform_update(
        self,
        *,
        perform_at: typing.Optional[builtins.str] = None,
        time_window: typing.Optional[builtins.str] = None,
        update_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#perform_at ElastigroupAwsBeanstalk#perform_at}.
        :param time_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#time_window ElastigroupAwsBeanstalk#time_window}.
        :param update_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#update_level ElastigroupAwsBeanstalk#update_level}.
        '''
        value = ElastigroupAwsBeanstalkManagedActionsPlatformUpdate(
            perform_at=perform_at, time_window=time_window, update_level=update_level
        )

        return typing.cast(None, jsii.invoke(self, "putPlatformUpdate", [value]))

    @jsii.member(jsii_name="resetPlatformUpdate")
    def reset_platform_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatformUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="platformUpdate")
    def platform_update(
        self,
    ) -> "ElastigroupAwsBeanstalkManagedActionsPlatformUpdateOutputReference":
        return typing.cast("ElastigroupAwsBeanstalkManagedActionsPlatformUpdateOutputReference", jsii.get(self, "platformUpdate"))

    @builtins.property
    @jsii.member(jsii_name="platformUpdateInput")
    def platform_update_input(
        self,
    ) -> typing.Optional["ElastigroupAwsBeanstalkManagedActionsPlatformUpdate"]:
        return typing.cast(typing.Optional["ElastigroupAwsBeanstalkManagedActionsPlatformUpdate"], jsii.get(self, "platformUpdateInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ElastigroupAwsBeanstalkManagedActions]:
        return typing.cast(typing.Optional[ElastigroupAwsBeanstalkManagedActions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAwsBeanstalkManagedActions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bfd6f07418a14956cf920b4c9ae17242ab70be4fa987cdb46a34b46be42b737)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkManagedActionsPlatformUpdate",
    jsii_struct_bases=[],
    name_mapping={
        "perform_at": "performAt",
        "time_window": "timeWindow",
        "update_level": "updateLevel",
    },
)
class ElastigroupAwsBeanstalkManagedActionsPlatformUpdate:
    def __init__(
        self,
        *,
        perform_at: typing.Optional[builtins.str] = None,
        time_window: typing.Optional[builtins.str] = None,
        update_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param perform_at: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#perform_at ElastigroupAwsBeanstalk#perform_at}.
        :param time_window: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#time_window ElastigroupAwsBeanstalk#time_window}.
        :param update_level: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#update_level ElastigroupAwsBeanstalk#update_level}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d91ded92d7e22f1278af7d283adf256a94ddb845a6c67c0f91bf9bb09b7c48c)
            check_type(argname="argument perform_at", value=perform_at, expected_type=type_hints["perform_at"])
            check_type(argname="argument time_window", value=time_window, expected_type=type_hints["time_window"])
            check_type(argname="argument update_level", value=update_level, expected_type=type_hints["update_level"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if perform_at is not None:
            self._values["perform_at"] = perform_at
        if time_window is not None:
            self._values["time_window"] = time_window
        if update_level is not None:
            self._values["update_level"] = update_level

    @builtins.property
    def perform_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#perform_at ElastigroupAwsBeanstalk#perform_at}.'''
        result = self._values.get("perform_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#time_window ElastigroupAwsBeanstalk#time_window}.'''
        result = self._values.get("time_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#update_level ElastigroupAwsBeanstalk#update_level}.'''
        result = self._values.get("update_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAwsBeanstalkManagedActionsPlatformUpdate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAwsBeanstalkManagedActionsPlatformUpdateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkManagedActionsPlatformUpdateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e321dcfa50e684098a16cff9c3e31f8910661c381e6105b39b62ca36ca09f69e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPerformAt")
    def reset_perform_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformAt", []))

    @jsii.member(jsii_name="resetTimeWindow")
    def reset_time_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeWindow", []))

    @jsii.member(jsii_name="resetUpdateLevel")
    def reset_update_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateLevel", []))

    @builtins.property
    @jsii.member(jsii_name="performAtInput")
    def perform_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "performAtInput"))

    @builtins.property
    @jsii.member(jsii_name="timeWindowInput")
    def time_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="updateLevelInput")
    def update_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="performAt")
    def perform_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "performAt"))

    @perform_at.setter
    def perform_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b71f3dd24f17a591f0c87593670ae34a18c35e5f05a00309f46172bd08c37839)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "performAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindow")
    def time_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeWindow"))

    @time_window.setter
    def time_window(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b40ceadff1e3b9e2605a429423bf3c7f3bce05d4e66830d1540662b8c63a531)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updateLevel")
    def update_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updateLevel"))

    @update_level.setter
    def update_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5efff598583123e7d39786802ede9fb040d8aa2b35425cae31bb4f108044948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updateLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ElastigroupAwsBeanstalkManagedActionsPlatformUpdate]:
        return typing.cast(typing.Optional[ElastigroupAwsBeanstalkManagedActionsPlatformUpdate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ElastigroupAwsBeanstalkManagedActionsPlatformUpdate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc8191f7e2eccb796d6a04ca74bfea3e21a7f9aa889b9761bae4f672f9ccf01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkScheduledTask",
    jsii_struct_bases=[],
    name_mapping={
        "task_type": "taskType",
        "adjustment": "adjustment",
        "adjustment_percentage": "adjustmentPercentage",
        "batch_size_percentage": "batchSizePercentage",
        "cron_expression": "cronExpression",
        "frequency": "frequency",
        "grace_period": "gracePeriod",
        "is_enabled": "isEnabled",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
        "scale_max_capacity": "scaleMaxCapacity",
        "scale_min_capacity": "scaleMinCapacity",
        "scale_target_capacity": "scaleTargetCapacity",
        "start_time": "startTime",
        "target_capacity": "targetCapacity",
    },
)
class ElastigroupAwsBeanstalkScheduledTask:
    def __init__(
        self,
        *,
        task_type: builtins.str,
        adjustment: typing.Optional[builtins.str] = None,
        adjustment_percentage: typing.Optional[builtins.str] = None,
        batch_size_percentage: typing.Optional[builtins.str] = None,
        cron_expression: typing.Optional[builtins.str] = None,
        frequency: typing.Optional[builtins.str] = None,
        grace_period: typing.Optional[builtins.str] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_capacity: typing.Optional[builtins.str] = None,
        min_capacity: typing.Optional[builtins.str] = None,
        scale_max_capacity: typing.Optional[builtins.str] = None,
        scale_min_capacity: typing.Optional[builtins.str] = None,
        scale_target_capacity: typing.Optional[builtins.str] = None,
        start_time: typing.Optional[builtins.str] = None,
        target_capacity: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#task_type ElastigroupAwsBeanstalk#task_type}.
        :param adjustment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#adjustment ElastigroupAwsBeanstalk#adjustment}.
        :param adjustment_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#adjustment_percentage ElastigroupAwsBeanstalk#adjustment_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#batch_size_percentage ElastigroupAwsBeanstalk#batch_size_percentage}.
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#cron_expression ElastigroupAwsBeanstalk#cron_expression}.
        :param frequency: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#frequency ElastigroupAwsBeanstalk#frequency}.
        :param grace_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#grace_period ElastigroupAwsBeanstalk#grace_period}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#is_enabled ElastigroupAwsBeanstalk#is_enabled}.
        :param max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#max_capacity ElastigroupAwsBeanstalk#max_capacity}.
        :param min_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#min_capacity ElastigroupAwsBeanstalk#min_capacity}.
        :param scale_max_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scale_max_capacity ElastigroupAwsBeanstalk#scale_max_capacity}.
        :param scale_min_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scale_min_capacity ElastigroupAwsBeanstalk#scale_min_capacity}.
        :param scale_target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scale_target_capacity ElastigroupAwsBeanstalk#scale_target_capacity}.
        :param start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#start_time ElastigroupAwsBeanstalk#start_time}.
        :param target_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#target_capacity ElastigroupAwsBeanstalk#target_capacity}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b246c15b1e02d37f24e15d1f55d37b1521abb1c56a12d8547ab8db03608885)
            check_type(argname="argument task_type", value=task_type, expected_type=type_hints["task_type"])
            check_type(argname="argument adjustment", value=adjustment, expected_type=type_hints["adjustment"])
            check_type(argname="argument adjustment_percentage", value=adjustment_percentage, expected_type=type_hints["adjustment_percentage"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument frequency", value=frequency, expected_type=type_hints["frequency"])
            check_type(argname="argument grace_period", value=grace_period, expected_type=type_hints["grace_period"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
            check_type(argname="argument scale_max_capacity", value=scale_max_capacity, expected_type=type_hints["scale_max_capacity"])
            check_type(argname="argument scale_min_capacity", value=scale_min_capacity, expected_type=type_hints["scale_min_capacity"])
            check_type(argname="argument scale_target_capacity", value=scale_target_capacity, expected_type=type_hints["scale_target_capacity"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
            check_type(argname="argument target_capacity", value=target_capacity, expected_type=type_hints["target_capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "task_type": task_type,
        }
        if adjustment is not None:
            self._values["adjustment"] = adjustment
        if adjustment_percentage is not None:
            self._values["adjustment_percentage"] = adjustment_percentage
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if cron_expression is not None:
            self._values["cron_expression"] = cron_expression
        if frequency is not None:
            self._values["frequency"] = frequency
        if grace_period is not None:
            self._values["grace_period"] = grace_period
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity
        if scale_max_capacity is not None:
            self._values["scale_max_capacity"] = scale_max_capacity
        if scale_min_capacity is not None:
            self._values["scale_min_capacity"] = scale_min_capacity
        if scale_target_capacity is not None:
            self._values["scale_target_capacity"] = scale_target_capacity
        if start_time is not None:
            self._values["start_time"] = start_time
        if target_capacity is not None:
            self._values["target_capacity"] = target_capacity

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#task_type ElastigroupAwsBeanstalk#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def adjustment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#adjustment ElastigroupAwsBeanstalk#adjustment}.'''
        result = self._values.get("adjustment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def adjustment_percentage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#adjustment_percentage ElastigroupAwsBeanstalk#adjustment_percentage}.'''
        result = self._values.get("adjustment_percentage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#batch_size_percentage ElastigroupAwsBeanstalk#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cron_expression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#cron_expression ElastigroupAwsBeanstalk#cron_expression}.'''
        result = self._values.get("cron_expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#frequency ElastigroupAwsBeanstalk#frequency}.'''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def grace_period(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#grace_period ElastigroupAwsBeanstalk#grace_period}.'''
        result = self._values.get("grace_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#is_enabled ElastigroupAwsBeanstalk#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#max_capacity ElastigroupAwsBeanstalk#max_capacity}.'''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#min_capacity ElastigroupAwsBeanstalk#min_capacity}.'''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_max_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scale_max_capacity ElastigroupAwsBeanstalk#scale_max_capacity}.'''
        result = self._values.get("scale_max_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_min_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scale_min_capacity ElastigroupAwsBeanstalk#scale_min_capacity}.'''
        result = self._values.get("scale_min_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scale_target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#scale_target_capacity ElastigroupAwsBeanstalk#scale_target_capacity}.'''
        result = self._values.get("scale_target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#start_time ElastigroupAwsBeanstalk#start_time}.'''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_capacity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/elastigroup_aws_beanstalk#target_capacity ElastigroupAwsBeanstalk#target_capacity}.'''
        result = self._values.get("target_capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElastigroupAwsBeanstalkScheduledTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElastigroupAwsBeanstalkScheduledTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkScheduledTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__703299ae3288e94dce437ad399f398808b5eaf3acf817fbab4952fca5a9fe5bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ElastigroupAwsBeanstalkScheduledTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7698c71f3df2e826cd47a382661fddc2d6b480b12aa48e194a8f6ec6deeaa9ad)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ElastigroupAwsBeanstalkScheduledTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b93e7579158c518e3dd2092418f31ba406168694df54bf05e2081c3588af2a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__79ae68cb7100410fe8cd2d8cda29ecb766c51d2ba071f9b2163a6a023b70e4ec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__749cc081b2838fcdf8510f890b1a1ce37fc05b1fb0961eb55b4da6d1c95fc832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkScheduledTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkScheduledTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkScheduledTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2abe19ef1694609998cb163bd5b17870d06d302775603255fbdda97268b61f98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ElastigroupAwsBeanstalkScheduledTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.elastigroupAwsBeanstalk.ElastigroupAwsBeanstalkScheduledTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc54fdd5f9ccfc4e80aaa63cd91b702658f8aef47ef29fda13317b7ab2c28a7a)
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

    @jsii.member(jsii_name="resetCronExpression")
    def reset_cron_expression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCronExpression", []))

    @jsii.member(jsii_name="resetFrequency")
    def reset_frequency(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequency", []))

    @jsii.member(jsii_name="resetGracePeriod")
    def reset_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGracePeriod", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetMaxCapacity")
    def reset_max_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCapacity", []))

    @jsii.member(jsii_name="resetMinCapacity")
    def reset_min_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCapacity", []))

    @jsii.member(jsii_name="resetScaleMaxCapacity")
    def reset_scale_max_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleMaxCapacity", []))

    @jsii.member(jsii_name="resetScaleMinCapacity")
    def reset_scale_min_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleMinCapacity", []))

    @jsii.member(jsii_name="resetScaleTargetCapacity")
    def reset_scale_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScaleTargetCapacity", []))

    @jsii.member(jsii_name="resetStartTime")
    def reset_start_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartTime", []))

    @jsii.member(jsii_name="resetTargetCapacity")
    def reset_target_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetCapacity", []))

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
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

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
    @jsii.member(jsii_name="maxCapacityInput")
    def max_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="minCapacityInput")
    def min_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minCapacityInput"))

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
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="targetCapacityInput")
    def target_capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="taskTypeInput")
    def task_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="adjustment")
    def adjustment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustment"))

    @adjustment.setter
    def adjustment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7767222e57b7a628c1ad397e593f3c20bceb30b8a5c770c3a108ad1f995bfb06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="adjustmentPercentage")
    def adjustment_percentage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adjustmentPercentage"))

    @adjustment_percentage.setter
    def adjustment_percentage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39d1e54f8d859a895505f67cc4600c50d9d3d5b5d5c66fcba26de5e44e38b946)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adjustmentPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bb2b0fad7f7cfd0b1c8b651ab1b08ff62ffda2a16f8183d71c59432d1c52340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cronExpression")
    def cron_expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cronExpression"))

    @cron_expression.setter
    def cron_expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e2213e029722ad297ca6b426b1a2e809ee0ab3a7f511201d8fa21c50843c81b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cronExpression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48a4e47224178386e9ffd84f407d8deed50539139665926bc0475d91bbe344b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequency", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gracePeriod")
    def grace_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gracePeriod"))

    @grace_period.setter
    def grace_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eef269b0927686c4da80689c0b89544b0e47d8fe6e62a1ad737d3d60fec88b0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f000f3519f6e8e1198383020241cf6c85e83956a41df0f2b28d42c3e46f5733e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc6edd18f576f6bb46b973551eef1a3ca21f69a8f30d6e3f29fb3975d89d46d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCapacity")
    def min_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minCapacity"))

    @min_capacity.setter
    def min_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ea5e4a9612175b8ac09dc54a54c82895b3107b4a3c40a98f56642df3dcaf8cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleMaxCapacity")
    def scale_max_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleMaxCapacity"))

    @scale_max_capacity.setter
    def scale_max_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06973c2bec0820ec642ac5407855808dd2ab7bd2a7b677d58f82f0e48e256404)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleMaxCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleMinCapacity")
    def scale_min_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleMinCapacity"))

    @scale_min_capacity.setter
    def scale_min_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__429a6127a94a77460af95706792ea5ed8b819fe5d26bc9c9129f381c74177691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleMinCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleTargetCapacity")
    def scale_target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scaleTargetCapacity"))

    @scale_target_capacity.setter
    def scale_target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce2d81056fcd8e330ad2c7233c7a967de5d8c39b1a3b845b9f74ff2afa41f39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleTargetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68be60d2a57d022e4a65c383868c40332ad3bee53965a4aefcc8458be214599c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetCapacity")
    def target_capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetCapacity"))

    @target_capacity.setter
    def target_capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7dd4c28554057ea7fc1fbc9133a42fae4f3ac4360e828a47d21c3ce839287cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c64040ce548b609d55c692f81212a9cc1cb10787617ccb95c9990db70cf8584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkScheduledTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkScheduledTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkScheduledTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0fd5e0a98e31f1afccb58d49cbb465b12bce8e6bcc498096ff9b00ab15485e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ElastigroupAwsBeanstalk",
    "ElastigroupAwsBeanstalkConfig",
    "ElastigroupAwsBeanstalkDeploymentPreferences",
    "ElastigroupAwsBeanstalkDeploymentPreferencesOutputReference",
    "ElastigroupAwsBeanstalkDeploymentPreferencesStrategy",
    "ElastigroupAwsBeanstalkDeploymentPreferencesStrategyList",
    "ElastigroupAwsBeanstalkDeploymentPreferencesStrategyOutputReference",
    "ElastigroupAwsBeanstalkManagedActions",
    "ElastigroupAwsBeanstalkManagedActionsOutputReference",
    "ElastigroupAwsBeanstalkManagedActionsPlatformUpdate",
    "ElastigroupAwsBeanstalkManagedActionsPlatformUpdateOutputReference",
    "ElastigroupAwsBeanstalkScheduledTask",
    "ElastigroupAwsBeanstalkScheduledTaskList",
    "ElastigroupAwsBeanstalkScheduledTaskOutputReference",
]

publication.publish()

def _typecheckingstub__0214bccd61c44ec9662f88a6f1565c3a1a05724b62375a7e13bae9f8bcb80b74(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    desired_capacity: jsii.Number,
    instance_types_spot: typing.Sequence[builtins.str],
    max_size: jsii.Number,
    min_size: jsii.Number,
    name: builtins.str,
    product: builtins.str,
    region: builtins.str,
    beanstalk_environment_id: typing.Optional[builtins.str] = None,
    beanstalk_environment_name: typing.Optional[builtins.str] = None,
    deployment_preferences: typing.Optional[typing.Union[ElastigroupAwsBeanstalkDeploymentPreferences, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance: typing.Optional[builtins.str] = None,
    managed_actions: typing.Optional[typing.Union[ElastigroupAwsBeanstalkManagedActions, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAwsBeanstalkScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__5d2e095004838d5ffee8cec5e304da6e68c3e3f37a8d9d3d30d272289bf443db(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f71c2d941f17d721d339c7c862fb9b6b51d64add66901c0573760a63ee3a623(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAwsBeanstalkScheduledTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__517a2e1565f257411b26e290287b297bd0662a2be7dd8286c85f0d6094a7417f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__148439f227f34910a6a7b8fc8e1ae44743a9a415992c12eafe4abfbaf3185ca4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b4b9411071a66a076221b447ba7bf937a071745b50ffce38c392189ac188a2d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ff5ce7692e510c704ef3049f7ac67d822f33e621d576a361a270f5a9755bb02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0386a5b009b0787b7a8ce2ee3d02f5b9c3fcd29b0244f7945234e925d231c558(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c6ced020e68ca57d8c7533264eb9de1f2572315b6918e54a513f180bc46df6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cc3063860d8b608af954dc9bacc3b471c713f883065d5b6ed8866f86fb9bcdb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98bb2e369590690ebe7ff226441b26cbd9fece0cf6e234647e38f53be65523a6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47244b2fe70b4a6378fc816a6820814fd2060aab2aa7134ec423296faeec017d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62272147604f48152e70074686f050e8aa8a92fc5b93b1859aeef623d811caa9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a42818b8f3b75ec5bdcaf4c6319f942b9ec9792b401d48d840c3d518486d3475(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__575034abe4176a143c5aa72e9f3fde4822d1b606f5b9c06e2b6e665d64d7b21b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    desired_capacity: jsii.Number,
    instance_types_spot: typing.Sequence[builtins.str],
    max_size: jsii.Number,
    min_size: jsii.Number,
    name: builtins.str,
    product: builtins.str,
    region: builtins.str,
    beanstalk_environment_id: typing.Optional[builtins.str] = None,
    beanstalk_environment_name: typing.Optional[builtins.str] = None,
    deployment_preferences: typing.Optional[typing.Union[ElastigroupAwsBeanstalkDeploymentPreferences, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance: typing.Optional[builtins.str] = None,
    managed_actions: typing.Optional[typing.Union[ElastigroupAwsBeanstalkManagedActions, typing.Dict[builtins.str, typing.Any]]] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAwsBeanstalkScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24e87010a066f8d55fdd4fbde8b67d867e25b336e3eae520fe32a8a78703cb5e(
    *,
    automatic_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    batch_size_percentage: typing.Optional[jsii.Number] = None,
    grace_period: typing.Optional[jsii.Number] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAwsBeanstalkDeploymentPreferencesStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72ec99970f29bad91258a0dee32efc6cb5095396603eec59f383a2daeb7fa326(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5aacc7c39b1080881b0ec2456701cd52522d582f06cf59cdd870b81f0ab14a6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ElastigroupAwsBeanstalkDeploymentPreferencesStrategy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd20a11ed83a602e69124dc8cc5ec39dba648ae79946ae52647bb81acfce0fea(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a5c647641688bfd9582a0b6b1f77c801188dcbd576af809e26b5225ebd119a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c515bf7814e3640e76fe74a22c838848865418f7738dd524a5a67c3634306dc6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c178b5bc9fd5ef17f07e0b8314ff1cabded20df8c572093ed9be8061ab0787(
    value: typing.Optional[ElastigroupAwsBeanstalkDeploymentPreferences],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c6e8fc4c351b9a3e2c9eac9dbbea5305101f6c7da2bd759b6a78ef83a6c2c4(
    *,
    action: typing.Optional[builtins.str] = None,
    should_drain_instances: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16df345f3b4c870270f9b46ecfa70496ab3016a04769250630e567953982a832(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb92f58ea12f5c17136e41e29a46754369dfb598cb9de72bf829ac1cad1ba3e5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc97c04420eadda62e5176706c9d32315a79df7aee5f8403314e681fa25b82a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f9429c3614905371daf5e8f3dbd916f2ee7d7f4cdc32e2ee1e4bd68b557768c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__967c4e81238e1ce4a4010667353a2383d7dc46df694058dc75b1f4771700f061(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__708033e716a63f9990c2ea170f63445d39336981aa69788ef45281948d54b2c8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0f983d6729d4c444138e0da93ba1f1a7cb0eedd9b42f3bd06df692e9209f0fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2a94f35e2180a66072e9e0b4702ce585ff0ccc141f876ebc493485265723a1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__552c811c0d2b67bdb0dc977606f63408c267e14285e49d8c7547804b7cdee886(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb279a8ae34a52b05a755fa39961772bc7025301307addf80778d615bfa97626(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkDeploymentPreferencesStrategy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddb5617a64fdcb36eb00bbe5d5560edcd5934dbe3439ee50c8b397164b5041d6(
    *,
    platform_update: typing.Optional[typing.Union[ElastigroupAwsBeanstalkManagedActionsPlatformUpdate, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e3962916c5d34176b3709cfbf95516bcd7891858a49e7d117d4fa03c832ffae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bfd6f07418a14956cf920b4c9ae17242ab70be4fa987cdb46a34b46be42b737(
    value: typing.Optional[ElastigroupAwsBeanstalkManagedActions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d91ded92d7e22f1278af7d283adf256a94ddb845a6c67c0f91bf9bb09b7c48c(
    *,
    perform_at: typing.Optional[builtins.str] = None,
    time_window: typing.Optional[builtins.str] = None,
    update_level: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e321dcfa50e684098a16cff9c3e31f8910661c381e6105b39b62ca36ca09f69e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b71f3dd24f17a591f0c87593670ae34a18c35e5f05a00309f46172bd08c37839(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b40ceadff1e3b9e2605a429423bf3c7f3bce05d4e66830d1540662b8c63a531(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5efff598583123e7d39786802ede9fb040d8aa2b35425cae31bb4f108044948(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc8191f7e2eccb796d6a04ca74bfea3e21a7f9aa889b9761bae4f672f9ccf01(
    value: typing.Optional[ElastigroupAwsBeanstalkManagedActionsPlatformUpdate],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b246c15b1e02d37f24e15d1f55d37b1521abb1c56a12d8547ab8db03608885(
    *,
    task_type: builtins.str,
    adjustment: typing.Optional[builtins.str] = None,
    adjustment_percentage: typing.Optional[builtins.str] = None,
    batch_size_percentage: typing.Optional[builtins.str] = None,
    cron_expression: typing.Optional[builtins.str] = None,
    frequency: typing.Optional[builtins.str] = None,
    grace_period: typing.Optional[builtins.str] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_capacity: typing.Optional[builtins.str] = None,
    min_capacity: typing.Optional[builtins.str] = None,
    scale_max_capacity: typing.Optional[builtins.str] = None,
    scale_min_capacity: typing.Optional[builtins.str] = None,
    scale_target_capacity: typing.Optional[builtins.str] = None,
    start_time: typing.Optional[builtins.str] = None,
    target_capacity: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__703299ae3288e94dce437ad399f398808b5eaf3acf817fbab4952fca5a9fe5bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7698c71f3df2e826cd47a382661fddc2d6b480b12aa48e194a8f6ec6deeaa9ad(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b93e7579158c518e3dd2092418f31ba406168694df54bf05e2081c3588af2a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79ae68cb7100410fe8cd2d8cda29ecb766c51d2ba071f9b2163a6a023b70e4ec(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__749cc081b2838fcdf8510f890b1a1ce37fc05b1fb0961eb55b4da6d1c95fc832(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2abe19ef1694609998cb163bd5b17870d06d302775603255fbdda97268b61f98(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ElastigroupAwsBeanstalkScheduledTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc54fdd5f9ccfc4e80aaa63cd91b702658f8aef47ef29fda13317b7ab2c28a7a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7767222e57b7a628c1ad397e593f3c20bceb30b8a5c770c3a108ad1f995bfb06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39d1e54f8d859a895505f67cc4600c50d9d3d5b5d5c66fcba26de5e44e38b946(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bb2b0fad7f7cfd0b1c8b651ab1b08ff62ffda2a16f8183d71c59432d1c52340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e2213e029722ad297ca6b426b1a2e809ee0ab3a7f511201d8fa21c50843c81b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48a4e47224178386e9ffd84f407d8deed50539139665926bc0475d91bbe344b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eef269b0927686c4da80689c0b89544b0e47d8fe6e62a1ad737d3d60fec88b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f000f3519f6e8e1198383020241cf6c85e83956a41df0f2b28d42c3e46f5733e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc6edd18f576f6bb46b973551eef1a3ca21f69a8f30d6e3f29fb3975d89d46d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ea5e4a9612175b8ac09dc54a54c82895b3107b4a3c40a98f56642df3dcaf8cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06973c2bec0820ec642ac5407855808dd2ab7bd2a7b677d58f82f0e48e256404(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__429a6127a94a77460af95706792ea5ed8b819fe5d26bc9c9129f381c74177691(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce2d81056fcd8e330ad2c7233c7a967de5d8c39b1a3b845b9f74ff2afa41f39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68be60d2a57d022e4a65c383868c40332ad3bee53965a4aefcc8458be214599c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7dd4c28554057ea7fc1fbc9133a42fae4f3ac4360e828a47d21c3ce839287cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c64040ce548b609d55c692f81212a9cc1cb10787617ccb95c9990db70cf8584(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0fd5e0a98e31f1afccb58d49cbb465b12bce8e6bcc498096ff9b00ab15485e8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ElastigroupAwsBeanstalkScheduledTask]],
) -> None:
    """Type checking stubs"""
    pass
