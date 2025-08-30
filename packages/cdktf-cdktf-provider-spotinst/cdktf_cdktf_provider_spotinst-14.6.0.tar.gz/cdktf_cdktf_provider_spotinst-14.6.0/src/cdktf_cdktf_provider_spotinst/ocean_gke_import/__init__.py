r'''
# `spotinst_ocean_gke_import`

Refer to the Terraform Registry for docs: [`spotinst_ocean_gke_import`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import).
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


class OceanGkeImport(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImport",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import spotinst_ocean_gke_import}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_name: builtins.str,
        location: builtins.str,
        autoscaler: typing.Optional[typing.Union["OceanGkeImportAutoscaler", typing.Dict[builtins.str, typing.Any]]] = None,
        auto_update: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportAutoUpdate", typing.Dict[builtins.str, typing.Any]]]]] = None,
        backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportBackendServices", typing.Dict[builtins.str, typing.Any]]]]] = None,
        blacklist: typing.Optional[typing.Sequence[builtins.str]] = None,
        controller_cluster_id: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        filters: typing.Optional[typing.Union["OceanGkeImportFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        root_volume_type: typing.Optional[builtins.str] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        shielded_instance_config: typing.Optional[typing.Union["OceanGkeImportShieldedInstanceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanGkeImportUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        use_as_template_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import spotinst_ocean_gke_import} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cluster_name OceanGkeImport#cluster_name}.
        :param location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#location OceanGkeImport#location}.
        :param autoscaler: autoscaler block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#autoscaler OceanGkeImport#autoscaler}
        :param auto_update: auto_update block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#auto_update OceanGkeImport#auto_update}
        :param backend_services: backend_services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#backend_services OceanGkeImport#backend_services}
        :param blacklist: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#blacklist OceanGkeImport#blacklist}.
        :param controller_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#controller_cluster_id OceanGkeImport#controller_cluster_id}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#desired_capacity OceanGkeImport#desired_capacity}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#filters OceanGkeImport#filters}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#id OceanGkeImport#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_size OceanGkeImport#max_size}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_size OceanGkeImport#min_size}.
        :param root_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#root_volume_type OceanGkeImport#root_volume_type}.
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scheduled_task OceanGkeImport#scheduled_task}
        :param shielded_instance_config: shielded_instance_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#shielded_instance_config OceanGkeImport#shielded_instance_config}
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#strategy OceanGkeImport#strategy}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#update_policy OceanGkeImport#update_policy}
        :param use_as_template_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#use_as_template_only OceanGkeImport#use_as_template_only}.
        :param whitelist: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#whitelist OceanGkeImport#whitelist}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67352a7d95b89b2a90348dfed9cc26141aad6a80e92731c133671b54056fc5ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanGkeImportConfig(
            cluster_name=cluster_name,
            location=location,
            autoscaler=autoscaler,
            auto_update=auto_update,
            backend_services=backend_services,
            blacklist=blacklist,
            controller_cluster_id=controller_cluster_id,
            desired_capacity=desired_capacity,
            filters=filters,
            id=id,
            max_size=max_size,
            min_size=min_size,
            root_volume_type=root_volume_type,
            scheduled_task=scheduled_task,
            shielded_instance_config=shielded_instance_config,
            strategy=strategy,
            update_policy=update_policy,
            use_as_template_only=use_as_template_only,
            whitelist=whitelist,
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
        '''Generates CDKTF code for importing a OceanGkeImport resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanGkeImport to import.
        :param import_from_id: The id of the existing OceanGkeImport that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanGkeImport to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79035f4d0d1eefa115c086d7be79e7c6c50bb31c4ef151144b8a03472f2d26f8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAutoscaler")
    def put_autoscaler(
        self,
        *,
        auto_headroom_percentage: typing.Optional[jsii.Number] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        down: typing.Optional[typing.Union["OceanGkeImportAutoscalerDown", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_automatic_and_manual_headroom: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        headroom: typing.Optional[typing.Union["OceanGkeImportAutoscalerHeadroom", typing.Dict[builtins.str, typing.Any]]] = None,
        is_auto_config: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        resource_limits: typing.Optional[typing.Union["OceanGkeImportAutoscalerResourceLimits", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param auto_headroom_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#auto_headroom_percentage OceanGkeImport#auto_headroom_percentage}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cooldown OceanGkeImport#cooldown}.
        :param down: down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#down OceanGkeImport#down}
        :param enable_automatic_and_manual_headroom: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_automatic_and_manual_headroom OceanGkeImport#enable_automatic_and_manual_headroom}.
        :param headroom: headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#headroom OceanGkeImport#headroom}
        :param is_auto_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_auto_config OceanGkeImport#is_auto_config}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#resource_limits OceanGkeImport#resource_limits}
        '''
        value = OceanGkeImportAutoscaler(
            auto_headroom_percentage=auto_headroom_percentage,
            cooldown=cooldown,
            down=down,
            enable_automatic_and_manual_headroom=enable_automatic_and_manual_headroom,
            headroom=headroom,
            is_auto_config=is_auto_config,
            is_enabled=is_enabled,
            resource_limits=resource_limits,
        )

        return typing.cast(None, jsii.invoke(self, "putAutoscaler", [value]))

    @jsii.member(jsii_name="putAutoUpdate")
    def put_auto_update(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportAutoUpdate", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f42d3bcfebe58330957466a53968172733e4a204bf55ea17addd7004e9a3f2d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAutoUpdate", [value]))

    @jsii.member(jsii_name="putBackendServices")
    def put_backend_services(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportBackendServices", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99b94d817dff03fd8d7cd284f5a53ce683fdfd23de7ceeec564587aad0c89215)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBackendServices", [value]))

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
        :param exclude_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#exclude_families OceanGkeImport#exclude_families}.
        :param include_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#include_families OceanGkeImport#include_families}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_memory_gib OceanGkeImport#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_vcpu OceanGkeImport#max_vcpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_memory_gib OceanGkeImport#min_memory_gib}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_vcpu OceanGkeImport#min_vcpu}.
        '''
        value = OceanGkeImportFilters(
            exclude_families=exclude_families,
            include_families=include_families,
            max_memory_gib=max_memory_gib,
            max_vcpu=max_vcpu,
            min_memory_gib=min_memory_gib,
            min_vcpu=min_vcpu,
        )

        return typing.cast(None, jsii.invoke(self, "putFilters", [value]))

    @jsii.member(jsii_name="putScheduledTask")
    def put_scheduled_task(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportScheduledTask", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70056f79e26bba4c77282430716ce00d4e5ae5bf9f6ce92ce8cbb4490182070a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putScheduledTask", [value]))

    @jsii.member(jsii_name="putShieldedInstanceConfig")
    def put_shielded_instance_config(
        self,
        *,
        enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enable_integrity_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_integrity_monitoring OceanGkeImport#enable_integrity_monitoring}.
        :param enable_secure_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_secure_boot OceanGkeImport#enable_secure_boot}.
        '''
        value = OceanGkeImportShieldedInstanceConfig(
            enable_integrity_monitoring=enable_integrity_monitoring,
            enable_secure_boot=enable_secure_boot,
        )

        return typing.cast(None, jsii.invoke(self, "putShieldedInstanceConfig", [value]))

    @jsii.member(jsii_name="putStrategy")
    def put_strategy(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportStrategy", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beaf570efc232b300cbae73fcdd10c59f4d02a2f668621beb7662ed1112a284e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStrategy", [value]))

    @jsii.member(jsii_name="putUpdatePolicy")
    def put_update_policy(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_config: typing.Optional[typing.Union["OceanGkeImportUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#should_roll OceanGkeImport#should_roll}.
        :param conditioned_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#conditioned_roll OceanGkeImport#conditioned_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#roll_config OceanGkeImport#roll_config}
        '''
        value = OceanGkeImportUpdatePolicy(
            should_roll=should_roll,
            conditioned_roll=conditioned_roll,
            roll_config=roll_config,
        )

        return typing.cast(None, jsii.invoke(self, "putUpdatePolicy", [value]))

    @jsii.member(jsii_name="resetAutoscaler")
    def reset_autoscaler(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoscaler", []))

    @jsii.member(jsii_name="resetAutoUpdate")
    def reset_auto_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoUpdate", []))

    @jsii.member(jsii_name="resetBackendServices")
    def reset_backend_services(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackendServices", []))

    @jsii.member(jsii_name="resetBlacklist")
    def reset_blacklist(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlacklist", []))

    @jsii.member(jsii_name="resetControllerClusterId")
    def reset_controller_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetControllerClusterId", []))

    @jsii.member(jsii_name="resetDesiredCapacity")
    def reset_desired_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDesiredCapacity", []))

    @jsii.member(jsii_name="resetFilters")
    def reset_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilters", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxSize")
    def reset_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxSize", []))

    @jsii.member(jsii_name="resetMinSize")
    def reset_min_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinSize", []))

    @jsii.member(jsii_name="resetRootVolumeType")
    def reset_root_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootVolumeType", []))

    @jsii.member(jsii_name="resetScheduledTask")
    def reset_scheduled_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledTask", []))

    @jsii.member(jsii_name="resetShieldedInstanceConfig")
    def reset_shielded_instance_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShieldedInstanceConfig", []))

    @jsii.member(jsii_name="resetStrategy")
    def reset_strategy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrategy", []))

    @jsii.member(jsii_name="resetUpdatePolicy")
    def reset_update_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdatePolicy", []))

    @jsii.member(jsii_name="resetUseAsTemplateOnly")
    def reset_use_as_template_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseAsTemplateOnly", []))

    @jsii.member(jsii_name="resetWhitelist")
    def reset_whitelist(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhitelist", []))

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
    def autoscaler(self) -> "OceanGkeImportAutoscalerOutputReference":
        return typing.cast("OceanGkeImportAutoscalerOutputReference", jsii.get(self, "autoscaler"))

    @builtins.property
    @jsii.member(jsii_name="autoUpdate")
    def auto_update(self) -> "OceanGkeImportAutoUpdateList":
        return typing.cast("OceanGkeImportAutoUpdateList", jsii.get(self, "autoUpdate"))

    @builtins.property
    @jsii.member(jsii_name="backendServices")
    def backend_services(self) -> "OceanGkeImportBackendServicesList":
        return typing.cast("OceanGkeImportBackendServicesList", jsii.get(self, "backendServices"))

    @builtins.property
    @jsii.member(jsii_name="clusterControllerId")
    def cluster_controller_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterControllerId"))

    @builtins.property
    @jsii.member(jsii_name="filters")
    def filters(self) -> "OceanGkeImportFiltersOutputReference":
        return typing.cast("OceanGkeImportFiltersOutputReference", jsii.get(self, "filters"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTask")
    def scheduled_task(self) -> "OceanGkeImportScheduledTaskList":
        return typing.cast("OceanGkeImportScheduledTaskList", jsii.get(self, "scheduledTask"))

    @builtins.property
    @jsii.member(jsii_name="shieldedInstanceConfig")
    def shielded_instance_config(
        self,
    ) -> "OceanGkeImportShieldedInstanceConfigOutputReference":
        return typing.cast("OceanGkeImportShieldedInstanceConfigOutputReference", jsii.get(self, "shieldedInstanceConfig"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "OceanGkeImportStrategyList":
        return typing.cast("OceanGkeImportStrategyList", jsii.get(self, "strategy"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicy")
    def update_policy(self) -> "OceanGkeImportUpdatePolicyOutputReference":
        return typing.cast("OceanGkeImportUpdatePolicyOutputReference", jsii.get(self, "updatePolicy"))

    @builtins.property
    @jsii.member(jsii_name="autoscalerInput")
    def autoscaler_input(self) -> typing.Optional["OceanGkeImportAutoscaler"]:
        return typing.cast(typing.Optional["OceanGkeImportAutoscaler"], jsii.get(self, "autoscalerInput"))

    @builtins.property
    @jsii.member(jsii_name="autoUpdateInput")
    def auto_update_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportAutoUpdate"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportAutoUpdate"]]], jsii.get(self, "autoUpdateInput"))

    @builtins.property
    @jsii.member(jsii_name="backendServicesInput")
    def backend_services_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportBackendServices"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportBackendServices"]]], jsii.get(self, "backendServicesInput"))

    @builtins.property
    @jsii.member(jsii_name="blacklistInput")
    def blacklist_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "blacklistInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="controllerClusterIdInput")
    def controller_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "controllerClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="desiredCapacityInput")
    def desired_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "desiredCapacityInput"))

    @builtins.property
    @jsii.member(jsii_name="filtersInput")
    def filters_input(self) -> typing.Optional["OceanGkeImportFilters"]:
        return typing.cast(typing.Optional["OceanGkeImportFilters"], jsii.get(self, "filtersInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="maxSizeInput")
    def max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="minSizeInput")
    def min_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="rootVolumeTypeInput")
    def root_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduledTaskInput")
    def scheduled_task_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTask"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTask"]]], jsii.get(self, "scheduledTaskInput"))

    @builtins.property
    @jsii.member(jsii_name="shieldedInstanceConfigInput")
    def shielded_instance_config_input(
        self,
    ) -> typing.Optional["OceanGkeImportShieldedInstanceConfig"]:
        return typing.cast(typing.Optional["OceanGkeImportShieldedInstanceConfig"], jsii.get(self, "shieldedInstanceConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportStrategy"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportStrategy"]]], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="updatePolicyInput")
    def update_policy_input(self) -> typing.Optional["OceanGkeImportUpdatePolicy"]:
        return typing.cast(typing.Optional["OceanGkeImportUpdatePolicy"], jsii.get(self, "updatePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="useAsTemplateOnlyInput")
    def use_as_template_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useAsTemplateOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="whitelistInput")
    def whitelist_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "whitelistInput"))

    @builtins.property
    @jsii.member(jsii_name="blacklist")
    def blacklist(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "blacklist"))

    @blacklist.setter
    def blacklist(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a727b343f0b7f19388cd113485f0055fb8bc8f5fabb2697a2ad884613f7a920)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blacklist", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ab72beb7f144b671dbc233c6b952cd5a582a352658cdd7a73fefa67c2d8607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="controllerClusterId")
    def controller_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "controllerClusterId"))

    @controller_cluster_id.setter
    def controller_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c1b2c8243380a33d1046aa6b1fba2316e7f0127450cfbbabc4baf1d0f2de8de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "controllerClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="desiredCapacity")
    def desired_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "desiredCapacity"))

    @desired_capacity.setter
    def desired_capacity(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4728b0f386ccda692672e8291e7518136a3c5d462c965032a57e93807e07394a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "desiredCapacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2330214ea2ceff01e87dd97205b1c60cdcd9fc50e9319fe7fa2cc86e155525c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f90dc6fb1f4c2fab06589a214671ee30d8fbfb94e184beab9723758a37b68d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxSize")
    def max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxSize"))

    @max_size.setter
    def max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c15f7504eec6a10ce9aa6e24af9ca84986e3e716e532ff0bba0756078d717142)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minSize")
    def min_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSize"))

    @min_size.setter
    def min_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af69003e73e74a70dbb8303759e0b2ce0eaef3bbae068d54d8cffec81a82950)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootVolumeType")
    def root_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootVolumeType"))

    @root_volume_type.setter
    def root_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__952f0c2c5777b0000a35132c2f1a654d2f17cb29fbe8516a962fef907b615360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useAsTemplateOnly")
    def use_as_template_only(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useAsTemplateOnly"))

    @use_as_template_only.setter
    def use_as_template_only(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__078174ff077980881a2fdb7d098843260ffdc79e2e0c30aa4f6c056085a55d0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useAsTemplateOnly", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="whitelist")
    def whitelist(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "whitelist"))

    @whitelist.setter
    def whitelist(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b76a41e52e26c924e6022f94f1199565b83d1813fde516f2162a75596ce5728a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "whitelist", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoUpdate",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled"},
)
class OceanGkeImportAutoUpdate:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa0d4557aecf5262507e8ce5fdd28efa723e26ae62158f2b5c7798bc3d716e7d)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportAutoUpdate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportAutoUpdateList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoUpdateList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9245b21d65bed5be4c427eb61ae8ffd99b2292230c0aa32018113c9c890d49f5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeImportAutoUpdateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17266a92e279d4ad070876d8e30190da0f0c8cb2314e4b2d7da6f32e6f7e9af8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeImportAutoUpdateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b0c728c54bec0631618e225de51dbc4df8b54c0121399bf0892e7c3325e4fb4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__22888dd068305906274e84abb04b031f931b735a44b3617a3995b1882fd3f58a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5e5a0ea503b48771cd18395101a268e6f15a15e065a2c2d820a9642f310b597)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportAutoUpdate]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportAutoUpdate]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportAutoUpdate]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60748516cad4eaff6112d4ffceddbae00303477545a44b9e878be1c79a4bdda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportAutoUpdateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoUpdateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__46752b35bea62b49a0f806fa6cc4faf8cc7dcaa0b36bfd6ccf2fafe66b2e3286)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c752169fc62654a54cb3f9f5fa5a2d37297d33d0f04fe5e5013e71f21859566b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportAutoUpdate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportAutoUpdate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportAutoUpdate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f54487c47272e8c688d82100285979b488291a2ade7c00f2c9b0d02e6e8c1a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscaler",
    jsii_struct_bases=[],
    name_mapping={
        "auto_headroom_percentage": "autoHeadroomPercentage",
        "cooldown": "cooldown",
        "down": "down",
        "enable_automatic_and_manual_headroom": "enableAutomaticAndManualHeadroom",
        "headroom": "headroom",
        "is_auto_config": "isAutoConfig",
        "is_enabled": "isEnabled",
        "resource_limits": "resourceLimits",
    },
)
class OceanGkeImportAutoscaler:
    def __init__(
        self,
        *,
        auto_headroom_percentage: typing.Optional[jsii.Number] = None,
        cooldown: typing.Optional[jsii.Number] = None,
        down: typing.Optional[typing.Union["OceanGkeImportAutoscalerDown", typing.Dict[builtins.str, typing.Any]]] = None,
        enable_automatic_and_manual_headroom: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        headroom: typing.Optional[typing.Union["OceanGkeImportAutoscalerHeadroom", typing.Dict[builtins.str, typing.Any]]] = None,
        is_auto_config: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        resource_limits: typing.Optional[typing.Union["OceanGkeImportAutoscalerResourceLimits", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param auto_headroom_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#auto_headroom_percentage OceanGkeImport#auto_headroom_percentage}.
        :param cooldown: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cooldown OceanGkeImport#cooldown}.
        :param down: down block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#down OceanGkeImport#down}
        :param enable_automatic_and_manual_headroom: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_automatic_and_manual_headroom OceanGkeImport#enable_automatic_and_manual_headroom}.
        :param headroom: headroom block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#headroom OceanGkeImport#headroom}
        :param is_auto_config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_auto_config OceanGkeImport#is_auto_config}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.
        :param resource_limits: resource_limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#resource_limits OceanGkeImport#resource_limits}
        '''
        if isinstance(down, dict):
            down = OceanGkeImportAutoscalerDown(**down)
        if isinstance(headroom, dict):
            headroom = OceanGkeImportAutoscalerHeadroom(**headroom)
        if isinstance(resource_limits, dict):
            resource_limits = OceanGkeImportAutoscalerResourceLimits(**resource_limits)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b1686952a444b05612bdd8c60355440f74976f79b8dd47aa44bd7db5282a693)
            check_type(argname="argument auto_headroom_percentage", value=auto_headroom_percentage, expected_type=type_hints["auto_headroom_percentage"])
            check_type(argname="argument cooldown", value=cooldown, expected_type=type_hints["cooldown"])
            check_type(argname="argument down", value=down, expected_type=type_hints["down"])
            check_type(argname="argument enable_automatic_and_manual_headroom", value=enable_automatic_and_manual_headroom, expected_type=type_hints["enable_automatic_and_manual_headroom"])
            check_type(argname="argument headroom", value=headroom, expected_type=type_hints["headroom"])
            check_type(argname="argument is_auto_config", value=is_auto_config, expected_type=type_hints["is_auto_config"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument resource_limits", value=resource_limits, expected_type=type_hints["resource_limits"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auto_headroom_percentage is not None:
            self._values["auto_headroom_percentage"] = auto_headroom_percentage
        if cooldown is not None:
            self._values["cooldown"] = cooldown
        if down is not None:
            self._values["down"] = down
        if enable_automatic_and_manual_headroom is not None:
            self._values["enable_automatic_and_manual_headroom"] = enable_automatic_and_manual_headroom
        if headroom is not None:
            self._values["headroom"] = headroom
        if is_auto_config is not None:
            self._values["is_auto_config"] = is_auto_config
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled
        if resource_limits is not None:
            self._values["resource_limits"] = resource_limits

    @builtins.property
    def auto_headroom_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#auto_headroom_percentage OceanGkeImport#auto_headroom_percentage}.'''
        result = self._values.get("auto_headroom_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cooldown OceanGkeImport#cooldown}.'''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def down(self) -> typing.Optional["OceanGkeImportAutoscalerDown"]:
        '''down block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#down OceanGkeImport#down}
        '''
        result = self._values.get("down")
        return typing.cast(typing.Optional["OceanGkeImportAutoscalerDown"], result)

    @builtins.property
    def enable_automatic_and_manual_headroom(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_automatic_and_manual_headroom OceanGkeImport#enable_automatic_and_manual_headroom}.'''
        result = self._values.get("enable_automatic_and_manual_headroom")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def headroom(self) -> typing.Optional["OceanGkeImportAutoscalerHeadroom"]:
        '''headroom block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#headroom OceanGkeImport#headroom}
        '''
        result = self._values.get("headroom")
        return typing.cast(typing.Optional["OceanGkeImportAutoscalerHeadroom"], result)

    @builtins.property
    def is_auto_config(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_auto_config OceanGkeImport#is_auto_config}.'''
        result = self._values.get("is_auto_config")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def resource_limits(
        self,
    ) -> typing.Optional["OceanGkeImportAutoscalerResourceLimits"]:
        '''resource_limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#resource_limits OceanGkeImport#resource_limits}
        '''
        result = self._values.get("resource_limits")
        return typing.cast(typing.Optional["OceanGkeImportAutoscalerResourceLimits"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportAutoscaler(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerDown",
    jsii_struct_bases=[],
    name_mapping={
        "evaluation_periods": "evaluationPeriods",
        "is_aggressive_scale_down_enabled": "isAggressiveScaleDownEnabled",
        "max_scale_down_percentage": "maxScaleDownPercentage",
    },
)
class OceanGkeImportAutoscalerDown:
    def __init__(
        self,
        *,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        is_aggressive_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_scale_down_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#evaluation_periods OceanGkeImport#evaluation_periods}.
        :param is_aggressive_scale_down_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_aggressive_scale_down_enabled OceanGkeImport#is_aggressive_scale_down_enabled}.
        :param max_scale_down_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_scale_down_percentage OceanGkeImport#max_scale_down_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a0ddcd893ead90f58f19603d8c69e072ddb6dc0b0781bb15c9000ebc0b89682)
            check_type(argname="argument evaluation_periods", value=evaluation_periods, expected_type=type_hints["evaluation_periods"])
            check_type(argname="argument is_aggressive_scale_down_enabled", value=is_aggressive_scale_down_enabled, expected_type=type_hints["is_aggressive_scale_down_enabled"])
            check_type(argname="argument max_scale_down_percentage", value=max_scale_down_percentage, expected_type=type_hints["max_scale_down_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if evaluation_periods is not None:
            self._values["evaluation_periods"] = evaluation_periods
        if is_aggressive_scale_down_enabled is not None:
            self._values["is_aggressive_scale_down_enabled"] = is_aggressive_scale_down_enabled
        if max_scale_down_percentage is not None:
            self._values["max_scale_down_percentage"] = max_scale_down_percentage

    @builtins.property
    def evaluation_periods(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#evaluation_periods OceanGkeImport#evaluation_periods}.'''
        result = self._values.get("evaluation_periods")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def is_aggressive_scale_down_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_aggressive_scale_down_enabled OceanGkeImport#is_aggressive_scale_down_enabled}.'''
        result = self._values.get("is_aggressive_scale_down_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_scale_down_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_scale_down_percentage OceanGkeImport#max_scale_down_percentage}.'''
        result = self._values.get("max_scale_down_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportAutoscalerDown(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportAutoscalerDownOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerDownOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9350120b8d944d0c06129df2accb4171d7cab0fac651e74b3267e8647d7def4b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEvaluationPeriods")
    def reset_evaluation_periods(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvaluationPeriods", []))

    @jsii.member(jsii_name="resetIsAggressiveScaleDownEnabled")
    def reset_is_aggressive_scale_down_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsAggressiveScaleDownEnabled", []))

    @jsii.member(jsii_name="resetMaxScaleDownPercentage")
    def reset_max_scale_down_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxScaleDownPercentage", []))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriodsInput")
    def evaluation_periods_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "evaluationPeriodsInput"))

    @builtins.property
    @jsii.member(jsii_name="isAggressiveScaleDownEnabledInput")
    def is_aggressive_scale_down_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isAggressiveScaleDownEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="maxScaleDownPercentageInput")
    def max_scale_down_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxScaleDownPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="evaluationPeriods")
    def evaluation_periods(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "evaluationPeriods"))

    @evaluation_periods.setter
    def evaluation_periods(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b12f8748755b5fa8a24548d64214fe7920a33a1d5a32227ebae35bca6a1d2fec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evaluationPeriods", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isAggressiveScaleDownEnabled")
    def is_aggressive_scale_down_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isAggressiveScaleDownEnabled"))

    @is_aggressive_scale_down_enabled.setter
    def is_aggressive_scale_down_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fa1f949f5c31044c68b4c3d1d24444892455ef388ac32f34a95360e6f34348e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isAggressiveScaleDownEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxScaleDownPercentage")
    def max_scale_down_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxScaleDownPercentage"))

    @max_scale_down_percentage.setter
    def max_scale_down_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a41b1e429dd9928677519558591e70ecf75e59a6b41a3bdde04612d668d67e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxScaleDownPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportAutoscalerDown]:
        return typing.cast(typing.Optional[OceanGkeImportAutoscalerDown], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportAutoscalerDown],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e255980306ddccb7ba6545b4a717267bda2112927be468217a31a9c85b8a4b7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerHeadroom",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_per_unit": "cpuPerUnit",
        "gpu_per_unit": "gpuPerUnit",
        "memory_per_unit": "memoryPerUnit",
        "num_of_units": "numOfUnits",
    },
)
class OceanGkeImportAutoscalerHeadroom:
    def __init__(
        self,
        *,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
        num_of_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cpu_per_unit OceanGkeImport#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#gpu_per_unit OceanGkeImport#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#memory_per_unit OceanGkeImport#memory_per_unit}.
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#num_of_units OceanGkeImport#num_of_units}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__298336ff0256d37fe46a5716fe5852a813fb8dc4d53140c4f9919d2d9ad974c8)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cpu_per_unit OceanGkeImport#cpu_per_unit}.'''
        result = self._values.get("cpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gpu_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#gpu_per_unit OceanGkeImport#gpu_per_unit}.'''
        result = self._values.get("gpu_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_per_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#memory_per_unit OceanGkeImport#memory_per_unit}.'''
        result = self._values.get("memory_per_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_of_units(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#num_of_units OceanGkeImport#num_of_units}.'''
        result = self._values.get("num_of_units")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportAutoscalerHeadroom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportAutoscalerHeadroomOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerHeadroomOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__339b71934d6c209a041c0712cd0ab46d90d020aa6ead66e55b544f6fc6340813)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__15de092144b52557ec311e93db0fe9809bca54f08495088d36e137e0fe78e584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gpuPerUnit")
    def gpu_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "gpuPerUnit"))

    @gpu_per_unit.setter
    def gpu_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f17a9557ff4e9c81f0375de48b169c86678011465f6587ef91789bd8f68af13c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpuPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPerUnit")
    def memory_per_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPerUnit"))

    @memory_per_unit.setter
    def memory_per_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0283d98799464576709c00aa4949aef0610077f2499142f453a10c04b57b15ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPerUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numOfUnits")
    def num_of_units(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numOfUnits"))

    @num_of_units.setter
    def num_of_units(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e764ebafb759cebce8f40d917a033c8d9520e78c50250cd28521b392d6817f0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numOfUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportAutoscalerHeadroom]:
        return typing.cast(typing.Optional[OceanGkeImportAutoscalerHeadroom], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportAutoscalerHeadroom],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06184e2b152069b4062ccf90786b17246aec049811a629d6be56101c7179e33d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportAutoscalerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__56795a3bd1a04e7e16ee871c016977e3a8dc581886cf02dd98fbae1857771fd0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDown")
    def put_down(
        self,
        *,
        evaluation_periods: typing.Optional[jsii.Number] = None,
        is_aggressive_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_scale_down_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param evaluation_periods: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#evaluation_periods OceanGkeImport#evaluation_periods}.
        :param is_aggressive_scale_down_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_aggressive_scale_down_enabled OceanGkeImport#is_aggressive_scale_down_enabled}.
        :param max_scale_down_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_scale_down_percentage OceanGkeImport#max_scale_down_percentage}.
        '''
        value = OceanGkeImportAutoscalerDown(
            evaluation_periods=evaluation_periods,
            is_aggressive_scale_down_enabled=is_aggressive_scale_down_enabled,
            max_scale_down_percentage=max_scale_down_percentage,
        )

        return typing.cast(None, jsii.invoke(self, "putDown", [value]))

    @jsii.member(jsii_name="putHeadroom")
    def put_headroom(
        self,
        *,
        cpu_per_unit: typing.Optional[jsii.Number] = None,
        gpu_per_unit: typing.Optional[jsii.Number] = None,
        memory_per_unit: typing.Optional[jsii.Number] = None,
        num_of_units: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cpu_per_unit OceanGkeImport#cpu_per_unit}.
        :param gpu_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#gpu_per_unit OceanGkeImport#gpu_per_unit}.
        :param memory_per_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#memory_per_unit OceanGkeImport#memory_per_unit}.
        :param num_of_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#num_of_units OceanGkeImport#num_of_units}.
        '''
        value = OceanGkeImportAutoscalerHeadroom(
            cpu_per_unit=cpu_per_unit,
            gpu_per_unit=gpu_per_unit,
            memory_per_unit=memory_per_unit,
            num_of_units=num_of_units,
        )

        return typing.cast(None, jsii.invoke(self, "putHeadroom", [value]))

    @jsii.member(jsii_name="putResourceLimits")
    def put_resource_limits(
        self,
        *,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_memory_gib OceanGkeImport#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_vcpu OceanGkeImport#max_vcpu}.
        '''
        value = OceanGkeImportAutoscalerResourceLimits(
            max_memory_gib=max_memory_gib, max_vcpu=max_vcpu
        )

        return typing.cast(None, jsii.invoke(self, "putResourceLimits", [value]))

    @jsii.member(jsii_name="resetAutoHeadroomPercentage")
    def reset_auto_headroom_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHeadroomPercentage", []))

    @jsii.member(jsii_name="resetCooldown")
    def reset_cooldown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldown", []))

    @jsii.member(jsii_name="resetDown")
    def reset_down(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDown", []))

    @jsii.member(jsii_name="resetEnableAutomaticAndManualHeadroom")
    def reset_enable_automatic_and_manual_headroom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAutomaticAndManualHeadroom", []))

    @jsii.member(jsii_name="resetHeadroom")
    def reset_headroom(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeadroom", []))

    @jsii.member(jsii_name="resetIsAutoConfig")
    def reset_is_auto_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsAutoConfig", []))

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @jsii.member(jsii_name="resetResourceLimits")
    def reset_resource_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceLimits", []))

    @builtins.property
    @jsii.member(jsii_name="down")
    def down(self) -> OceanGkeImportAutoscalerDownOutputReference:
        return typing.cast(OceanGkeImportAutoscalerDownOutputReference, jsii.get(self, "down"))

    @builtins.property
    @jsii.member(jsii_name="headroom")
    def headroom(self) -> OceanGkeImportAutoscalerHeadroomOutputReference:
        return typing.cast(OceanGkeImportAutoscalerHeadroomOutputReference, jsii.get(self, "headroom"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimits")
    def resource_limits(
        self,
    ) -> "OceanGkeImportAutoscalerResourceLimitsOutputReference":
        return typing.cast("OceanGkeImportAutoscalerResourceLimitsOutputReference", jsii.get(self, "resourceLimits"))

    @builtins.property
    @jsii.member(jsii_name="autoHeadroomPercentageInput")
    def auto_headroom_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoHeadroomPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownInput")
    def cooldown_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownInput"))

    @builtins.property
    @jsii.member(jsii_name="downInput")
    def down_input(self) -> typing.Optional[OceanGkeImportAutoscalerDown]:
        return typing.cast(typing.Optional[OceanGkeImportAutoscalerDown], jsii.get(self, "downInput"))

    @builtins.property
    @jsii.member(jsii_name="enableAutomaticAndManualHeadroomInput")
    def enable_automatic_and_manual_headroom_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableAutomaticAndManualHeadroomInput"))

    @builtins.property
    @jsii.member(jsii_name="headroomInput")
    def headroom_input(self) -> typing.Optional[OceanGkeImportAutoscalerHeadroom]:
        return typing.cast(typing.Optional[OceanGkeImportAutoscalerHeadroom], jsii.get(self, "headroomInput"))

    @builtins.property
    @jsii.member(jsii_name="isAutoConfigInput")
    def is_auto_config_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isAutoConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceLimitsInput")
    def resource_limits_input(
        self,
    ) -> typing.Optional["OceanGkeImportAutoscalerResourceLimits"]:
        return typing.cast(typing.Optional["OceanGkeImportAutoscalerResourceLimits"], jsii.get(self, "resourceLimitsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoHeadroomPercentage")
    def auto_headroom_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoHeadroomPercentage"))

    @auto_headroom_percentage.setter
    def auto_headroom_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86edc331911cb973a456eb980eff80e9f49a54595fed535ce047cd7b6b2b9372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoHeadroomPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldown")
    def cooldown(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldown"))

    @cooldown.setter
    def cooldown(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cb0ce12f57b133d72cb48d97ec1b81cee2976b74f732b785767c132daf417e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldown", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableAutomaticAndManualHeadroom")
    def enable_automatic_and_manual_headroom(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableAutomaticAndManualHeadroom"))

    @enable_automatic_and_manual_headroom.setter
    def enable_automatic_and_manual_headroom(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efd665da5316bd61f1e0cea531e03e694d40da651acf9f52d234fb6455e6838)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableAutomaticAndManualHeadroom", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isAutoConfig")
    def is_auto_config(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isAutoConfig"))

    @is_auto_config.setter
    def is_auto_config(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6f6c27e267421d76dffb611c717634afa0d702d5d54ca3fa1de5fe016771a7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isAutoConfig", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__8a25b9fb377e952f57c67d15e5b1670de23e3edfcf2c79a3939224eeb9136011)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportAutoscaler]:
        return typing.cast(typing.Optional[OceanGkeImportAutoscaler], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanGkeImportAutoscaler]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66b81f306ab49b1d988c862bad02295b495ad1dd7985daa090e33b53b7020221)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerResourceLimits",
    jsii_struct_bases=[],
    name_mapping={"max_memory_gib": "maxMemoryGib", "max_vcpu": "maxVcpu"},
)
class OceanGkeImportAutoscalerResourceLimits:
    def __init__(
        self,
        *,
        max_memory_gib: typing.Optional[jsii.Number] = None,
        max_vcpu: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_memory_gib OceanGkeImport#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_vcpu OceanGkeImport#max_vcpu}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bdc99b91e189383a6aae8036bdb6fbb8671409aace8c9a2369b118f1f9932c9)
            check_type(argname="argument max_memory_gib", value=max_memory_gib, expected_type=type_hints["max_memory_gib"])
            check_type(argname="argument max_vcpu", value=max_vcpu, expected_type=type_hints["max_vcpu"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_memory_gib is not None:
            self._values["max_memory_gib"] = max_memory_gib
        if max_vcpu is not None:
            self._values["max_vcpu"] = max_vcpu

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_memory_gib OceanGkeImport#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_vcpu OceanGkeImport#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportAutoscalerResourceLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportAutoscalerResourceLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportAutoscalerResourceLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64e0b185e68801fc74e46fa9b5f2690b809c7916a370e04e1802d7bf9741963a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0a2dbe0bb5b020a8300a9066d23660a2c4f766fdee0109c9e37e79d164ec22ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f279b0967bad435010afba44fcb15d5e0fbfdb4fac7c352f96617e5b66e8f2dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportAutoscalerResourceLimits]:
        return typing.cast(typing.Optional[OceanGkeImportAutoscalerResourceLimits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportAutoscalerResourceLimits],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5cb17986bb7b27906e1c149627390ed37f30211eb01e7bf4c17bd07b896a3cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportBackendServices",
    jsii_struct_bases=[],
    name_mapping={
        "service_name": "serviceName",
        "location_type": "locationType",
        "named_ports": "namedPorts",
        "scheme": "scheme",
    },
)
class OceanGkeImportBackendServices:
    def __init__(
        self,
        *,
        service_name: builtins.str,
        location_type: typing.Optional[builtins.str] = None,
        named_ports: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportBackendServicesNamedPorts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        scheme: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#service_name OceanGkeImport#service_name}.
        :param location_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#location_type OceanGkeImport#location_type}.
        :param named_ports: named_ports block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#named_ports OceanGkeImport#named_ports}
        :param scheme: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scheme OceanGkeImport#scheme}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfeb7ff618071ef13bc94fc426d9fc0d89406b58d39d08a3e2e6780b0af3fa17)
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
            check_type(argname="argument location_type", value=location_type, expected_type=type_hints["location_type"])
            check_type(argname="argument named_ports", value=named_ports, expected_type=type_hints["named_ports"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_name": service_name,
        }
        if location_type is not None:
            self._values["location_type"] = location_type
        if named_ports is not None:
            self._values["named_ports"] = named_ports
        if scheme is not None:
            self._values["scheme"] = scheme

    @builtins.property
    def service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#service_name OceanGkeImport#service_name}.'''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#location_type OceanGkeImport#location_type}.'''
        result = self._values.get("location_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def named_ports(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportBackendServicesNamedPorts"]]]:
        '''named_ports block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#named_ports OceanGkeImport#named_ports}
        '''
        result = self._values.get("named_ports")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportBackendServicesNamedPorts"]]], result)

    @builtins.property
    def scheme(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scheme OceanGkeImport#scheme}.'''
        result = self._values.get("scheme")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportBackendServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportBackendServicesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportBackendServicesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__114fce57adfd19f19c5acc7ad9c5d6b90b1442a42480df47f0874925173201c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeImportBackendServicesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__407a031a1cda1d172f5888fe07053fcf6c103df90a2cb5f1026d6cbf69f6156e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeImportBackendServicesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29cc14bf0af2a14407a72b1df23e51c17016998f768b4ed21dadc42c8dabf5d6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__351fb37f7a5bedc70ae8ced5017cb77da836b3404e232259923d8e0e42ddb4df)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f600f4a99f3494f812a28c3a8ebda3bc416757a38f40c08ce47a751d5d317ac4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServices]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServices]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServices]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a039cb9e376618f3eb78f7dc615f74c56e84f0ab29467d18262d91be992c17f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportBackendServicesNamedPorts",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "ports": "ports"},
)
class OceanGkeImportBackendServicesNamedPorts:
    def __init__(
        self,
        *,
        name: builtins.str,
        ports: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#name OceanGkeImport#name}.
        :param ports: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#ports OceanGkeImport#ports}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab881a79ece9e28c311c6b1ebbffada472fc6f866d16faaa21190f6e548086a8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ports", value=ports, expected_type=type_hints["ports"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "ports": ports,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#name OceanGkeImport#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ports(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#ports OceanGkeImport#ports}.'''
        result = self._values.get("ports")
        assert result is not None, "Required property 'ports' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportBackendServicesNamedPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportBackendServicesNamedPortsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportBackendServicesNamedPortsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__731c041c69de323a0e7d10a7d416a3896b328af582488c413738f49df99981de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeImportBackendServicesNamedPortsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7f59a2f5fa577e2752a78eedd62b77d247f4ebcb7cbce5dd7d07a1d03e4987a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeImportBackendServicesNamedPortsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ff22d5e4ac2a2c089d5dfc3db335b993eb42068718a495ff1a08aa5a29c89f3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__202864e7393a9c22a091a7cb8165d4c35d3c3c8663f3b0b0ebb1493b1d3aae4f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__62914d0f1deb86c99c31f29760e8876eb997baaa1e0708b1c3274e50f0bdb7d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServicesNamedPorts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServicesNamedPorts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServicesNamedPorts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0028d1587a135e2fc6f6a183c56fa60388a26322e5b975a4085baf5f4866dff5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportBackendServicesNamedPortsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportBackendServicesNamedPortsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62eaace54a506c3303081e37815126181b7aafc9f929cd9a29f7d05c60b4d267)
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
            type_hints = typing.get_type_hints(_typecheckingstub__674a77480b86a005323ea2576b9351f23613b3eb528d6bc3d9c1da464604778b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce7a203378ab001046afc76f12a7b26ac8efc64f8670580b5b1c3a8acc77265e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ports", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServicesNamedPorts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServicesNamedPorts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServicesNamedPorts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59f9d1f2db5c634a047d1ae4ad24f5a6f493fda9f783e953c3ad9eb84068daf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportBackendServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportBackendServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__973639b77d3f6a1d3c020b896a22f4da573b26e08834f3e265ef33d855b60e25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNamedPorts")
    def put_named_ports(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServicesNamedPorts, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05fb3c526c70f00950a09c3b998e53250cea4edd7765f49382cbf5626977adbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNamedPorts", [value]))

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
    @jsii.member(jsii_name="namedPorts")
    def named_ports(self) -> OceanGkeImportBackendServicesNamedPortsList:
        return typing.cast(OceanGkeImportBackendServicesNamedPortsList, jsii.get(self, "namedPorts"))

    @builtins.property
    @jsii.member(jsii_name="locationTypeInput")
    def location_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="namedPortsInput")
    def named_ports_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServicesNamedPorts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServicesNamedPorts]]], jsii.get(self, "namedPortsInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__c45c7888bf973fd128a589dd7fc7caf5736f558038e6496fd551c756d79d874b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97afaf5fc4c3bedc115cabce9e5105cc736edb2b6f64ec7397a2a92548c84751)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2781a59bb7d04f0d45db310a9bb628b890488f23f43a8faa7d41c261e7e55d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServices]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServices]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServices]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f0754cad8129d1039714e1687ed7e6635e96e0eb180e91e2faf45f1991bb01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_name": "clusterName",
        "location": "location",
        "autoscaler": "autoscaler",
        "auto_update": "autoUpdate",
        "backend_services": "backendServices",
        "blacklist": "blacklist",
        "controller_cluster_id": "controllerClusterId",
        "desired_capacity": "desiredCapacity",
        "filters": "filters",
        "id": "id",
        "max_size": "maxSize",
        "min_size": "minSize",
        "root_volume_type": "rootVolumeType",
        "scheduled_task": "scheduledTask",
        "shielded_instance_config": "shieldedInstanceConfig",
        "strategy": "strategy",
        "update_policy": "updatePolicy",
        "use_as_template_only": "useAsTemplateOnly",
        "whitelist": "whitelist",
    },
)
class OceanGkeImportConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_name: builtins.str,
        location: builtins.str,
        autoscaler: typing.Optional[typing.Union[OceanGkeImportAutoscaler, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_update: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportAutoUpdate, typing.Dict[builtins.str, typing.Any]]]]] = None,
        backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
        blacklist: typing.Optional[typing.Sequence[builtins.str]] = None,
        controller_cluster_id: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        filters: typing.Optional[typing.Union["OceanGkeImportFilters", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        root_volume_type: typing.Optional[builtins.str] = None,
        scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportScheduledTask", typing.Dict[builtins.str, typing.Any]]]]] = None,
        shielded_instance_config: typing.Optional[typing.Union["OceanGkeImportShieldedInstanceConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportStrategy", typing.Dict[builtins.str, typing.Any]]]]] = None,
        update_policy: typing.Optional[typing.Union["OceanGkeImportUpdatePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        use_as_template_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cluster_name OceanGkeImport#cluster_name}.
        :param location: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#location OceanGkeImport#location}.
        :param autoscaler: autoscaler block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#autoscaler OceanGkeImport#autoscaler}
        :param auto_update: auto_update block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#auto_update OceanGkeImport#auto_update}
        :param backend_services: backend_services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#backend_services OceanGkeImport#backend_services}
        :param blacklist: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#blacklist OceanGkeImport#blacklist}.
        :param controller_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#controller_cluster_id OceanGkeImport#controller_cluster_id}.
        :param desired_capacity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#desired_capacity OceanGkeImport#desired_capacity}.
        :param filters: filters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#filters OceanGkeImport#filters}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#id OceanGkeImport#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_size OceanGkeImport#max_size}.
        :param min_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_size OceanGkeImport#min_size}.
        :param root_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#root_volume_type OceanGkeImport#root_volume_type}.
        :param scheduled_task: scheduled_task block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scheduled_task OceanGkeImport#scheduled_task}
        :param shielded_instance_config: shielded_instance_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#shielded_instance_config OceanGkeImport#shielded_instance_config}
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#strategy OceanGkeImport#strategy}
        :param update_policy: update_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#update_policy OceanGkeImport#update_policy}
        :param use_as_template_only: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#use_as_template_only OceanGkeImport#use_as_template_only}.
        :param whitelist: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#whitelist OceanGkeImport#whitelist}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(autoscaler, dict):
            autoscaler = OceanGkeImportAutoscaler(**autoscaler)
        if isinstance(filters, dict):
            filters = OceanGkeImportFilters(**filters)
        if isinstance(shielded_instance_config, dict):
            shielded_instance_config = OceanGkeImportShieldedInstanceConfig(**shielded_instance_config)
        if isinstance(update_policy, dict):
            update_policy = OceanGkeImportUpdatePolicy(**update_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8ad51a65eb42b78c4689e48d67c150f0c9b58ad229861fdb476b2b19dc7501a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument autoscaler", value=autoscaler, expected_type=type_hints["autoscaler"])
            check_type(argname="argument auto_update", value=auto_update, expected_type=type_hints["auto_update"])
            check_type(argname="argument backend_services", value=backend_services, expected_type=type_hints["backend_services"])
            check_type(argname="argument blacklist", value=blacklist, expected_type=type_hints["blacklist"])
            check_type(argname="argument controller_cluster_id", value=controller_cluster_id, expected_type=type_hints["controller_cluster_id"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument root_volume_type", value=root_volume_type, expected_type=type_hints["root_volume_type"])
            check_type(argname="argument scheduled_task", value=scheduled_task, expected_type=type_hints["scheduled_task"])
            check_type(argname="argument shielded_instance_config", value=shielded_instance_config, expected_type=type_hints["shielded_instance_config"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument update_policy", value=update_policy, expected_type=type_hints["update_policy"])
            check_type(argname="argument use_as_template_only", value=use_as_template_only, expected_type=type_hints["use_as_template_only"])
            check_type(argname="argument whitelist", value=whitelist, expected_type=type_hints["whitelist"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
            "location": location,
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
        if auto_update is not None:
            self._values["auto_update"] = auto_update
        if backend_services is not None:
            self._values["backend_services"] = backend_services
        if blacklist is not None:
            self._values["blacklist"] = blacklist
        if controller_cluster_id is not None:
            self._values["controller_cluster_id"] = controller_cluster_id
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if filters is not None:
            self._values["filters"] = filters
        if id is not None:
            self._values["id"] = id
        if max_size is not None:
            self._values["max_size"] = max_size
        if min_size is not None:
            self._values["min_size"] = min_size
        if root_volume_type is not None:
            self._values["root_volume_type"] = root_volume_type
        if scheduled_task is not None:
            self._values["scheduled_task"] = scheduled_task
        if shielded_instance_config is not None:
            self._values["shielded_instance_config"] = shielded_instance_config
        if strategy is not None:
            self._values["strategy"] = strategy
        if update_policy is not None:
            self._values["update_policy"] = update_policy
        if use_as_template_only is not None:
            self._values["use_as_template_only"] = use_as_template_only
        if whitelist is not None:
            self._values["whitelist"] = whitelist

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
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cluster_name OceanGkeImport#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#location OceanGkeImport#location}.'''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autoscaler(self) -> typing.Optional[OceanGkeImportAutoscaler]:
        '''autoscaler block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#autoscaler OceanGkeImport#autoscaler}
        '''
        result = self._values.get("autoscaler")
        return typing.cast(typing.Optional[OceanGkeImportAutoscaler], result)

    @builtins.property
    def auto_update(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportAutoUpdate]]]:
        '''auto_update block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#auto_update OceanGkeImport#auto_update}
        '''
        result = self._values.get("auto_update")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportAutoUpdate]]], result)

    @builtins.property
    def backend_services(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServices]]]:
        '''backend_services block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#backend_services OceanGkeImport#backend_services}
        '''
        result = self._values.get("backend_services")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServices]]], result)

    @builtins.property
    def blacklist(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#blacklist OceanGkeImport#blacklist}.'''
        result = self._values.get("blacklist")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def controller_cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#controller_cluster_id OceanGkeImport#controller_cluster_id}.'''
        result = self._values.get("controller_cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#desired_capacity OceanGkeImport#desired_capacity}.'''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def filters(self) -> typing.Optional["OceanGkeImportFilters"]:
        '''filters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#filters OceanGkeImport#filters}
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional["OceanGkeImportFilters"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#id OceanGkeImport#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_size OceanGkeImport#max_size}.'''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_size OceanGkeImport#min_size}.'''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def root_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#root_volume_type OceanGkeImport#root_volume_type}.'''
        result = self._values.get("root_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheduled_task(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTask"]]]:
        '''scheduled_task block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scheduled_task OceanGkeImport#scheduled_task}
        '''
        result = self._values.get("scheduled_task")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTask"]]], result)

    @builtins.property
    def shielded_instance_config(
        self,
    ) -> typing.Optional["OceanGkeImportShieldedInstanceConfig"]:
        '''shielded_instance_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#shielded_instance_config OceanGkeImport#shielded_instance_config}
        '''
        result = self._values.get("shielded_instance_config")
        return typing.cast(typing.Optional["OceanGkeImportShieldedInstanceConfig"], result)

    @builtins.property
    def strategy(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportStrategy"]]]:
        '''strategy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#strategy OceanGkeImport#strategy}
        '''
        result = self._values.get("strategy")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportStrategy"]]], result)

    @builtins.property
    def update_policy(self) -> typing.Optional["OceanGkeImportUpdatePolicy"]:
        '''update_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#update_policy OceanGkeImport#update_policy}
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional["OceanGkeImportUpdatePolicy"], result)

    @builtins.property
    def use_as_template_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#use_as_template_only OceanGkeImport#use_as_template_only}.'''
        result = self._values.get("use_as_template_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def whitelist(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#whitelist OceanGkeImport#whitelist}.'''
        result = self._values.get("whitelist")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportFilters",
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
class OceanGkeImportFilters:
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
        :param exclude_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#exclude_families OceanGkeImport#exclude_families}.
        :param include_families: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#include_families OceanGkeImport#include_families}.
        :param max_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_memory_gib OceanGkeImport#max_memory_gib}.
        :param max_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_vcpu OceanGkeImport#max_vcpu}.
        :param min_memory_gib: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_memory_gib OceanGkeImport#min_memory_gib}.
        :param min_vcpu: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_vcpu OceanGkeImport#min_vcpu}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f33e41b8de8fe017b0f0de2cdc9a4bbce2884bf74f86e58ce7bd30a5ee6c046)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#exclude_families OceanGkeImport#exclude_families}.'''
        result = self._values.get("exclude_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_families(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#include_families OceanGkeImport#include_families}.'''
        result = self._values.get("include_families")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_memory_gib OceanGkeImport#max_memory_gib}.'''
        result = self._values.get("max_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#max_vcpu OceanGkeImport#max_vcpu}.'''
        result = self._values.get("max_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_memory_gib(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_memory_gib OceanGkeImport#min_memory_gib}.'''
        result = self._values.get("min_memory_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_vcpu(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#min_vcpu OceanGkeImport#min_vcpu}.'''
        result = self._values.get("min_vcpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportFilters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportFiltersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportFiltersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e890a4db5a2c8e6f1c563e56de774c6a505d27c14ab82ac54e879f422023f165)
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
            type_hints = typing.get_type_hints(_typecheckingstub__de51815b32712d286c011ea3346d01f36085823591cd138841ad57a149d97b49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeFamilies")
    def include_families(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "includeFamilies"))

    @include_families.setter
    def include_families(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__defcaa8fde7585d7e345333f68b0fe4a29a50ff850396eeee73c923179a32358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeFamilies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMemoryGib")
    def max_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxMemoryGib"))

    @max_memory_gib.setter
    def max_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ef55308a1d817a74dbe72e7cfe9d59ea8957ffcdf0ca745028345421119fb30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVcpu")
    def max_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVcpu"))

    @max_vcpu.setter
    def max_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3295260fd863b42072cb323515eccfee386a00e3daa2293d479e5ffbc4757421)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minMemoryGib")
    def min_memory_gib(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minMemoryGib"))

    @min_memory_gib.setter
    def min_memory_gib(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a33a74ee0adf96e513475dec1c12c0cc5aaf1b739429a8219e381c3f756d8d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minMemoryGib", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minVcpu")
    def min_vcpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minVcpu"))

    @min_vcpu.setter
    def min_vcpu(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__491a548f342e26d0f2b0da1b252c607b337791c3967c7e9b9f119a87b46e6566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minVcpu", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportFilters]:
        return typing.cast(typing.Optional[OceanGkeImportFilters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceanGkeImportFilters]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f58ca2c3a95222e4b17ccd209f73b73c6d59753d8b18ceb543fe1f21e929ee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTask",
    jsii_struct_bases=[],
    name_mapping={"shutdown_hours": "shutdownHours", "tasks": "tasks"},
)
class OceanGkeImportScheduledTask:
    def __init__(
        self,
        *,
        shutdown_hours: typing.Optional[typing.Union["OceanGkeImportScheduledTaskShutdownHours", typing.Dict[builtins.str, typing.Any]]] = None,
        tasks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportScheduledTaskTasks", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param shutdown_hours: shutdown_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#shutdown_hours OceanGkeImport#shutdown_hours}
        :param tasks: tasks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#tasks OceanGkeImport#tasks}
        '''
        if isinstance(shutdown_hours, dict):
            shutdown_hours = OceanGkeImportScheduledTaskShutdownHours(**shutdown_hours)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__629648838059e4b07e84dc211a482acaa31c89c30c38ea63215f83cd4918e7d1)
            check_type(argname="argument shutdown_hours", value=shutdown_hours, expected_type=type_hints["shutdown_hours"])
            check_type(argname="argument tasks", value=tasks, expected_type=type_hints["tasks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if shutdown_hours is not None:
            self._values["shutdown_hours"] = shutdown_hours
        if tasks is not None:
            self._values["tasks"] = tasks

    @builtins.property
    def shutdown_hours(
        self,
    ) -> typing.Optional["OceanGkeImportScheduledTaskShutdownHours"]:
        '''shutdown_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#shutdown_hours OceanGkeImport#shutdown_hours}
        '''
        result = self._values.get("shutdown_hours")
        return typing.cast(typing.Optional["OceanGkeImportScheduledTaskShutdownHours"], result)

    @builtins.property
    def tasks(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTaskTasks"]]]:
        '''tasks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#tasks OceanGkeImport#tasks}
        '''
        result = self._values.get("tasks")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTaskTasks"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportScheduledTask(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportScheduledTaskList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d50df939e3f10bb97bf9901ac8e56a41a680d829af37f0da3cd0696868ebd9e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeImportScheduledTaskOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6627cce062a63d32eeec489ff2d31e0e3927af830aa162a3ae510811f86c3b0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeImportScheduledTaskOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f77899e92c50734bf94d8872a82570c70310a92a75a32e9c0149f848cadc1d66)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c9d9e4a9bb289c987a520bfcdcac4d74a7ed5b3943d821297a519af6916f8f0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fc347e5af2af571a9135b0b0b6825eba0443e761104f745738b15ce36dbde22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTask]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTask]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTask]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adc797dca065f0e09b847b17105c9b026a748c132e5b135998d91727c7d8e63f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportScheduledTaskOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2560bd6f81f60f5e6efa149979656bc6e300ab759fa70a14b18ff673520ee4d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putShutdownHours")
    def put_shutdown_hours(
        self,
        *,
        time_windows: typing.Sequence[builtins.str],
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#time_windows OceanGkeImport#time_windows}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.
        '''
        value = OceanGkeImportScheduledTaskShutdownHours(
            time_windows=time_windows, is_enabled=is_enabled
        )

        return typing.cast(None, jsii.invoke(self, "putShutdownHours", [value]))

    @jsii.member(jsii_name="putTasks")
    def put_tasks(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanGkeImportScheduledTaskTasks", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fced1e9df5eb6dd039c688f5946c40a2c836ac19f3826b117535a5f1842281c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTasks", [value]))

    @jsii.member(jsii_name="resetShutdownHours")
    def reset_shutdown_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShutdownHours", []))

    @jsii.member(jsii_name="resetTasks")
    def reset_tasks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTasks", []))

    @builtins.property
    @jsii.member(jsii_name="shutdownHours")
    def shutdown_hours(
        self,
    ) -> "OceanGkeImportScheduledTaskShutdownHoursOutputReference":
        return typing.cast("OceanGkeImportScheduledTaskShutdownHoursOutputReference", jsii.get(self, "shutdownHours"))

    @builtins.property
    @jsii.member(jsii_name="tasks")
    def tasks(self) -> "OceanGkeImportScheduledTaskTasksList":
        return typing.cast("OceanGkeImportScheduledTaskTasksList", jsii.get(self, "tasks"))

    @builtins.property
    @jsii.member(jsii_name="shutdownHoursInput")
    def shutdown_hours_input(
        self,
    ) -> typing.Optional["OceanGkeImportScheduledTaskShutdownHours"]:
        return typing.cast(typing.Optional["OceanGkeImportScheduledTaskShutdownHours"], jsii.get(self, "shutdownHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="tasksInput")
    def tasks_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTaskTasks"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanGkeImportScheduledTaskTasks"]]], jsii.get(self, "tasksInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTask]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTask]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTask]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6b0535d96a3bfd301f8d7475bcd82372683778a62d5afd3cb149aaff0ffd918)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskShutdownHours",
    jsii_struct_bases=[],
    name_mapping={"time_windows": "timeWindows", "is_enabled": "isEnabled"},
)
class OceanGkeImportScheduledTaskShutdownHours:
    def __init__(
        self,
        *,
        time_windows: typing.Sequence[builtins.str],
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param time_windows: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#time_windows OceanGkeImport#time_windows}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39e3131182b1796177add371d60b9772623dc30eb049a14fde5175c31ba2de8f)
            check_type(argname="argument time_windows", value=time_windows, expected_type=type_hints["time_windows"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "time_windows": time_windows,
        }
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled

    @builtins.property
    def time_windows(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#time_windows OceanGkeImport#time_windows}.'''
        result = self._values.get("time_windows")
        assert result is not None, "Required property 'time_windows' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.'''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportScheduledTaskShutdownHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportScheduledTaskShutdownHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskShutdownHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2052b6aa77bb1a6a09a7807f70ee16d9e8df36047faf5600d5a3bbc611b1465a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebe00492e21e1d270ef7000cd84caab5557d5f6433696204dca8cdca9ff2984c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeWindows")
    def time_windows(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "timeWindows"))

    @time_windows.setter
    def time_windows(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45b56e95bba709aa3b76ff9ed60187cfd28bcdb00ad0230349ddc47ac12e057b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeWindows", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanGkeImportScheduledTaskShutdownHours]:
        return typing.cast(typing.Optional[OceanGkeImportScheduledTaskShutdownHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportScheduledTaskShutdownHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92854a6c191198172b99680c502dac4dea21ad0787875bade4c09ea1cc272ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasks",
    jsii_struct_bases=[],
    name_mapping={
        "cron_expression": "cronExpression",
        "is_enabled": "isEnabled",
        "task_type": "taskType",
        "task_parameters": "taskParameters",
    },
)
class OceanGkeImportScheduledTaskTasks:
    def __init__(
        self,
        *,
        cron_expression: builtins.str,
        is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        task_type: builtins.str,
        task_parameters: typing.Optional[typing.Union["OceanGkeImportScheduledTaskTasksTaskParameters", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cron_expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cron_expression OceanGkeImport#cron_expression}.
        :param is_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.
        :param task_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#task_type OceanGkeImport#task_type}.
        :param task_parameters: task_parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#task_parameters OceanGkeImport#task_parameters}
        '''
        if isinstance(task_parameters, dict):
            task_parameters = OceanGkeImportScheduledTaskTasksTaskParameters(**task_parameters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c13536d304752323e2d2d407fcb94bf96fe1eb6b80e498265bfcd6d00eca7cf1)
            check_type(argname="argument cron_expression", value=cron_expression, expected_type=type_hints["cron_expression"])
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
            check_type(argname="argument task_type", value=task_type, expected_type=type_hints["task_type"])
            check_type(argname="argument task_parameters", value=task_parameters, expected_type=type_hints["task_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cron_expression": cron_expression,
            "is_enabled": is_enabled,
            "task_type": task_type,
        }
        if task_parameters is not None:
            self._values["task_parameters"] = task_parameters

    @builtins.property
    def cron_expression(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cron_expression OceanGkeImport#cron_expression}.'''
        result = self._values.get("cron_expression")
        assert result is not None, "Required property 'cron_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#is_enabled OceanGkeImport#is_enabled}.'''
        result = self._values.get("is_enabled")
        assert result is not None, "Required property 'is_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def task_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#task_type OceanGkeImport#task_type}.'''
        result = self._values.get("task_type")
        assert result is not None, "Required property 'task_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_parameters(
        self,
    ) -> typing.Optional["OceanGkeImportScheduledTaskTasksTaskParameters"]:
        '''task_parameters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#task_parameters OceanGkeImport#task_parameters}
        '''
        result = self._values.get("task_parameters")
        return typing.cast(typing.Optional["OceanGkeImportScheduledTaskTasksTaskParameters"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportScheduledTaskTasks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportScheduledTaskTasksList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasksList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9b51ba84ccb300264dd605fcc6cfff0d122ce2946c142bd9e3026da1e74f126)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanGkeImportScheduledTaskTasksOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a427418b146c6ea3ac305bc4cdf18d515e230e71c9b8e0bd011d9d8309f7e81)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeImportScheduledTaskTasksOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6cc7dfe7a5aaede1c7e7f3e9a0722a99de2f7aa0f7e1bec1e7bd3d37e8bc16b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02eaab1fd09ac8bbb5ad3b492d1cb3cd67d11e411b68b8181f34d38a423aa797)
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
            type_hints = typing.get_type_hints(_typecheckingstub__45b54f87ec5ae4f88a1501a14ed3a686e2883cafc71a99dbbaa791686f9c54c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTaskTasks]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTaskTasks]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTaskTasks]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9bd1e43a7de96877c0c998e0e0b23bf6d09813d40bf962b844c4a5ce1fd0e98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportScheduledTaskTasksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5aeac62b0491406838e8c4f4c11137689c76ca09b670807a2c3cb280e617f02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTaskParameters")
    def put_task_parameters(
        self,
        *,
        cluster_roll: typing.Optional[typing.Union["OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cluster_roll: cluster_roll block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cluster_roll OceanGkeImport#cluster_roll}
        '''
        value = OceanGkeImportScheduledTaskTasksTaskParameters(
            cluster_roll=cluster_roll
        )

        return typing.cast(None, jsii.invoke(self, "putTaskParameters", [value]))

    @jsii.member(jsii_name="resetTaskParameters")
    def reset_task_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaskParameters", []))

    @builtins.property
    @jsii.member(jsii_name="taskParameters")
    def task_parameters(
        self,
    ) -> "OceanGkeImportScheduledTaskTasksTaskParametersOutputReference":
        return typing.cast("OceanGkeImportScheduledTaskTasksTaskParametersOutputReference", jsii.get(self, "taskParameters"))

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
    @jsii.member(jsii_name="taskParametersInput")
    def task_parameters_input(
        self,
    ) -> typing.Optional["OceanGkeImportScheduledTaskTasksTaskParameters"]:
        return typing.cast(typing.Optional["OceanGkeImportScheduledTaskTasksTaskParameters"], jsii.get(self, "taskParametersInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__3d93d0dedc55388433acdad4b5812015cfb8576790b38c9526476c2653ff27a0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0d377f6aae21732fb7aad733d9aafe645a01ff255e962a284837153b6bc808e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taskType")
    def task_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskType"))

    @task_type.setter
    def task_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81128af4cd6b2b0e4ca377fee1a420e334341c1dc59b7d6ed320c8791284205a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taskType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTaskTasks]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTaskTasks]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTaskTasks]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca07eaeeb86e0973163d8d4e7b934c1bd071c38c5cdab298c433bf24eabeaba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasksTaskParameters",
    jsii_struct_bases=[],
    name_mapping={"cluster_roll": "clusterRoll"},
)
class OceanGkeImportScheduledTaskTasksTaskParameters:
    def __init__(
        self,
        *,
        cluster_roll: typing.Optional[typing.Union["OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cluster_roll: cluster_roll block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cluster_roll OceanGkeImport#cluster_roll}
        '''
        if isinstance(cluster_roll, dict):
            cluster_roll = OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll(**cluster_roll)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c836496998aeee1e38cc6f84f435092ddfba906114258394dfe606f06048ce3c)
            check_type(argname="argument cluster_roll", value=cluster_roll, expected_type=type_hints["cluster_roll"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cluster_roll is not None:
            self._values["cluster_roll"] = cluster_roll

    @builtins.property
    def cluster_roll(
        self,
    ) -> typing.Optional["OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll"]:
        '''cluster_roll block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#cluster_roll OceanGkeImport#cluster_roll}
        '''
        result = self._values.get("cluster_roll")
        return typing.cast(typing.Optional["OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportScheduledTaskTasksTaskParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll",
    jsii_struct_bases=[],
    name_mapping={
        "batch_min_healthy_percentage": "batchMinHealthyPercentage",
        "batch_size_percentage": "batchSizePercentage",
        "comment": "comment",
        "respect_pdb": "respectPdb",
    },
)
class OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll:
    def __init__(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_min_healthy_percentage OceanGkeImport#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_size_percentage OceanGkeImport#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#comment OceanGkeImport#comment}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#respect_pdb OceanGkeImport#respect_pdb}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__734a060bb0496acb6393ca2612bbb7610439321df635596cce79565176645571)
            check_type(argname="argument batch_min_healthy_percentage", value=batch_min_healthy_percentage, expected_type=type_hints["batch_min_healthy_percentage"])
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument respect_pdb", value=respect_pdb, expected_type=type_hints["respect_pdb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if batch_min_healthy_percentage is not None:
            self._values["batch_min_healthy_percentage"] = batch_min_healthy_percentage
        if batch_size_percentage is not None:
            self._values["batch_size_percentage"] = batch_size_percentage
        if comment is not None:
            self._values["comment"] = comment
        if respect_pdb is not None:
            self._values["respect_pdb"] = respect_pdb

    @builtins.property
    def batch_min_healthy_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_min_healthy_percentage OceanGkeImport#batch_min_healthy_percentage}.'''
        result = self._values.get("batch_min_healthy_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def batch_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_size_percentage OceanGkeImport#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#comment OceanGkeImport#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#respect_pdb OceanGkeImport#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportScheduledTaskTasksTaskParametersClusterRollOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasksTaskParametersClusterRollOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e76993a79728ba7f8f54f75a1d3fff828b80e65b4d7a825eab9615f185c4e4e0)
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
    @jsii.member(jsii_name="batchMinHealthyPercentage")
    def batch_min_healthy_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchMinHealthyPercentage"))

    @batch_min_healthy_percentage.setter
    def batch_min_healthy_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b06c2475f4e54b6a9335a4ee701f8dfcc73e9de3ef69105ace126e2e7b59f516)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchMinHealthyPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b47e393ce47d69835ba473469638fe1ac08061e825e053f4476fc59508b618e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d1f29fea28f706d4779190de609d6afe564e73ccb218afade7fc16b1d9f1b93)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fd7d22040ac9c14839455156b2101a629acf0647391a79cca1ff03019857493)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectPdb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll]:
        return typing.cast(typing.Optional[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c0eccb2e3576e970e42be1b3c77a2915ba380b974242ef5393a48aca1ae13d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportScheduledTaskTasksTaskParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportScheduledTaskTasksTaskParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5d336f8c60ac640a5997079b22807ca179f32dba37b406a3500245e01e90407)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putClusterRoll")
    def put_cluster_roll(
        self,
        *,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        batch_size_percentage: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_min_healthy_percentage OceanGkeImport#batch_min_healthy_percentage}.
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_size_percentage OceanGkeImport#batch_size_percentage}.
        :param comment: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#comment OceanGkeImport#comment}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#respect_pdb OceanGkeImport#respect_pdb}.
        '''
        value = OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll(
            batch_min_healthy_percentage=batch_min_healthy_percentage,
            batch_size_percentage=batch_size_percentage,
            comment=comment,
            respect_pdb=respect_pdb,
        )

        return typing.cast(None, jsii.invoke(self, "putClusterRoll", [value]))

    @jsii.member(jsii_name="resetClusterRoll")
    def reset_cluster_roll(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRoll", []))

    @builtins.property
    @jsii.member(jsii_name="clusterRoll")
    def cluster_roll(
        self,
    ) -> OceanGkeImportScheduledTaskTasksTaskParametersClusterRollOutputReference:
        return typing.cast(OceanGkeImportScheduledTaskTasksTaskParametersClusterRollOutputReference, jsii.get(self, "clusterRoll"))

    @builtins.property
    @jsii.member(jsii_name="clusterRollInput")
    def cluster_roll_input(
        self,
    ) -> typing.Optional[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll]:
        return typing.cast(typing.Optional[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll], jsii.get(self, "clusterRollInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceanGkeImportScheduledTaskTasksTaskParameters]:
        return typing.cast(typing.Optional[OceanGkeImportScheduledTaskTasksTaskParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportScheduledTaskTasksTaskParameters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__765cdebc2b4878f17183d11f7e15695cd455bf5b6fabc2043356342209a5b29a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportShieldedInstanceConfig",
    jsii_struct_bases=[],
    name_mapping={
        "enable_integrity_monitoring": "enableIntegrityMonitoring",
        "enable_secure_boot": "enableSecureBoot",
    },
)
class OceanGkeImportShieldedInstanceConfig:
    def __init__(
        self,
        *,
        enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param enable_integrity_monitoring: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_integrity_monitoring OceanGkeImport#enable_integrity_monitoring}.
        :param enable_secure_boot: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_secure_boot OceanGkeImport#enable_secure_boot}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00c697eec4cbab40fe8f7e03d4db25408bb85fbf483859549336756efc685ef9)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_integrity_monitoring OceanGkeImport#enable_integrity_monitoring}.'''
        result = self._values.get("enable_integrity_monitoring")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_secure_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#enable_secure_boot OceanGkeImport#enable_secure_boot}.'''
        result = self._values.get("enable_secure_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportShieldedInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportShieldedInstanceConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportShieldedInstanceConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6a23d0e489dc826e620cf9539cb8b273d6483bc6d4db61adc0454477310a71c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aaa5c25c44b70c9900f7779abc6f8f2ac1d02b173b09c79aae61b9ce5cca9967)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b41a7756fba22d642802ce090958ef540255aee1a2d1f68940b222d39c8f1296)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSecureBoot", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportShieldedInstanceConfig]:
        return typing.cast(typing.Optional[OceanGkeImportShieldedInstanceConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportShieldedInstanceConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1dd44b9167e3b2d4f81393cf2ac6673c99a636d69b8f572b7ce390a31a7f829)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportStrategy",
    jsii_struct_bases=[],
    name_mapping={
        "draining_timeout": "drainingTimeout",
        "preemptible_percentage": "preemptiblePercentage",
        "provisioning_model": "provisioningModel",
        "scaling_orientation": "scalingOrientation",
        "should_utilize_commitments": "shouldUtilizeCommitments",
    },
)
class OceanGkeImportStrategy:
    def __init__(
        self,
        *,
        draining_timeout: typing.Optional[jsii.Number] = None,
        preemptible_percentage: typing.Optional[jsii.Number] = None,
        provisioning_model: typing.Optional[builtins.str] = None,
        scaling_orientation: typing.Optional[builtins.str] = None,
        should_utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param draining_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#draining_timeout OceanGkeImport#draining_timeout}.
        :param preemptible_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#preemptible_percentage OceanGkeImport#preemptible_percentage}.
        :param provisioning_model: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#provisioning_model OceanGkeImport#provisioning_model}.
        :param scaling_orientation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scaling_orientation OceanGkeImport#scaling_orientation}.
        :param should_utilize_commitments: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#should_utilize_commitments OceanGkeImport#should_utilize_commitments}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41f01af3d96d19ae641bab1a24be60b69bf64dfbc2248f10c5705bceba76ab19)
            check_type(argname="argument draining_timeout", value=draining_timeout, expected_type=type_hints["draining_timeout"])
            check_type(argname="argument preemptible_percentage", value=preemptible_percentage, expected_type=type_hints["preemptible_percentage"])
            check_type(argname="argument provisioning_model", value=provisioning_model, expected_type=type_hints["provisioning_model"])
            check_type(argname="argument scaling_orientation", value=scaling_orientation, expected_type=type_hints["scaling_orientation"])
            check_type(argname="argument should_utilize_commitments", value=should_utilize_commitments, expected_type=type_hints["should_utilize_commitments"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if draining_timeout is not None:
            self._values["draining_timeout"] = draining_timeout
        if preemptible_percentage is not None:
            self._values["preemptible_percentage"] = preemptible_percentage
        if provisioning_model is not None:
            self._values["provisioning_model"] = provisioning_model
        if scaling_orientation is not None:
            self._values["scaling_orientation"] = scaling_orientation
        if should_utilize_commitments is not None:
            self._values["should_utilize_commitments"] = should_utilize_commitments

    @builtins.property
    def draining_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#draining_timeout OceanGkeImport#draining_timeout}.'''
        result = self._values.get("draining_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preemptible_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#preemptible_percentage OceanGkeImport#preemptible_percentage}.'''
        result = self._values.get("preemptible_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def provisioning_model(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#provisioning_model OceanGkeImport#provisioning_model}.'''
        result = self._values.get("provisioning_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scaling_orientation(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#scaling_orientation OceanGkeImport#scaling_orientation}.'''
        result = self._values.get("scaling_orientation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def should_utilize_commitments(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#should_utilize_commitments OceanGkeImport#should_utilize_commitments}.'''
        result = self._values.get("should_utilize_commitments")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportStrategyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportStrategyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c38fba0e3189b31294cb8b20d314659cd4cd2e2cf65e1809e3bef24799d4682f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceanGkeImportStrategyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9f35129726debf60b633f891ea1c50119420e1db9da1e191cd18aef03529a87)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanGkeImportStrategyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6407972b266c7df558bcdb729e6de9698731fc23b31efb91c3c5d62a97643d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f005319356752a322bdc543a7654c867c15a84c0806d81ea43b66c8ce0aadeb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6c0e453cf05de03c1dd8ee0cb7e29b6c3d68627bff4f3a1db0725efa9ba7694)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportStrategy]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportStrategy]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportStrategy]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed242fe02c40112a5c5cae92826237f9cde70dec3981d60e92c50be99d31771f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanGkeImportStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf652cb8b365faf72343bfe7337a31ff6b52a269f09cb2c8c00476dfe22ba8f5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDrainingTimeout")
    def reset_draining_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainingTimeout", []))

    @jsii.member(jsii_name="resetPreemptiblePercentage")
    def reset_preemptible_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreemptiblePercentage", []))

    @jsii.member(jsii_name="resetProvisioningModel")
    def reset_provisioning_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvisioningModel", []))

    @jsii.member(jsii_name="resetScalingOrientation")
    def reset_scaling_orientation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingOrientation", []))

    @jsii.member(jsii_name="resetShouldUtilizeCommitments")
    def reset_should_utilize_commitments(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldUtilizeCommitments", []))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeoutInput")
    def draining_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "drainingTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="preemptiblePercentageInput")
    def preemptible_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "preemptiblePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="provisioningModelInput")
    def provisioning_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provisioningModelInput"))

    @builtins.property
    @jsii.member(jsii_name="scalingOrientationInput")
    def scaling_orientation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scalingOrientationInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldUtilizeCommitmentsInput")
    def should_utilize_commitments_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldUtilizeCommitmentsInput"))

    @builtins.property
    @jsii.member(jsii_name="drainingTimeout")
    def draining_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "drainingTimeout"))

    @draining_timeout.setter
    def draining_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__382f29c9a91354ccf7a1f5f50d006ba013c28d1b9840ce0e5af69af20695c4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "drainingTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preemptiblePercentage")
    def preemptible_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preemptiblePercentage"))

    @preemptible_percentage.setter
    def preemptible_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b116499391e94ebab5f8d89da4361f006ca3c2a401b396749ebf118de2950e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preemptiblePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provisioningModel")
    def provisioning_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provisioningModel"))

    @provisioning_model.setter
    def provisioning_model(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fda575d0bf1833e665474ef314c5466dc3e5297927dbf611ccea400536bf673)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provisioningModel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scalingOrientation")
    def scaling_orientation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scalingOrientation"))

    @scaling_orientation.setter
    def scaling_orientation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c92759f894f881ad5630701794df0438e3dfb1b1ba66fc2a659e91284c00c512)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scalingOrientation", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__0c9d74749b1fd3efcab361a199f2357a1fdcf90932d94670bd7f52499a5665d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldUtilizeCommitments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportStrategy]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportStrategy]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportStrategy]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2e0244cdcee631ecf93f2ad95f2bd7981369658a2759713c5e05018be4543f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportUpdatePolicy",
    jsii_struct_bases=[],
    name_mapping={
        "should_roll": "shouldRoll",
        "conditioned_roll": "conditionedRoll",
        "roll_config": "rollConfig",
    },
)
class OceanGkeImportUpdatePolicy:
    def __init__(
        self,
        *,
        should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        roll_config: typing.Optional[typing.Union["OceanGkeImportUpdatePolicyRollConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param should_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#should_roll OceanGkeImport#should_roll}.
        :param conditioned_roll: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#conditioned_roll OceanGkeImport#conditioned_roll}.
        :param roll_config: roll_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#roll_config OceanGkeImport#roll_config}
        '''
        if isinstance(roll_config, dict):
            roll_config = OceanGkeImportUpdatePolicyRollConfig(**roll_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08bb1b375d22b17f01679b170a59d54e7356d5e7f4b6f64e640e952569dc116d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#should_roll OceanGkeImport#should_roll}.'''
        result = self._values.get("should_roll")
        assert result is not None, "Required property 'should_roll' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def conditioned_roll(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#conditioned_roll OceanGkeImport#conditioned_roll}.'''
        result = self._values.get("conditioned_roll")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def roll_config(self) -> typing.Optional["OceanGkeImportUpdatePolicyRollConfig"]:
        '''roll_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#roll_config OceanGkeImport#roll_config}
        '''
        result = self._values.get("roll_config")
        return typing.cast(typing.Optional["OceanGkeImportUpdatePolicyRollConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportUpdatePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportUpdatePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportUpdatePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e05008e5559823af7c2c997bfed0af4c5d922600f4548dae0fae5d2e005b10b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRollConfig")
    def put_roll_config(
        self,
        *,
        batch_size_percentage: jsii.Number,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        launch_spec_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_size_percentage OceanGkeImport#batch_size_percentage}.
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_min_healthy_percentage OceanGkeImport#batch_min_healthy_percentage}.
        :param launch_spec_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#launch_spec_ids OceanGkeImport#launch_spec_ids}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#respect_pdb OceanGkeImport#respect_pdb}.
        '''
        value = OceanGkeImportUpdatePolicyRollConfig(
            batch_size_percentage=batch_size_percentage,
            batch_min_healthy_percentage=batch_min_healthy_percentage,
            launch_spec_ids=launch_spec_ids,
            respect_pdb=respect_pdb,
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
    def roll_config(self) -> "OceanGkeImportUpdatePolicyRollConfigOutputReference":
        return typing.cast("OceanGkeImportUpdatePolicyRollConfigOutputReference", jsii.get(self, "rollConfig"))

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
    ) -> typing.Optional["OceanGkeImportUpdatePolicyRollConfig"]:
        return typing.cast(typing.Optional["OceanGkeImportUpdatePolicyRollConfig"], jsii.get(self, "rollConfigInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__a3661aa3833671b76def6d2977c7c7bee340022f7cd521c088716b63b40b05c6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f80dd284528741e8133cc11320b042f35f7d417722f22298cf2b2191a2ada9f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldRoll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportUpdatePolicy]:
        return typing.cast(typing.Optional[OceanGkeImportUpdatePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportUpdatePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72aae5cf1dbbb1e8c5e20e550b23d38eb783fa37bb6ed5e9a95f4f2b8b43e204)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportUpdatePolicyRollConfig",
    jsii_struct_bases=[],
    name_mapping={
        "batch_size_percentage": "batchSizePercentage",
        "batch_min_healthy_percentage": "batchMinHealthyPercentage",
        "launch_spec_ids": "launchSpecIds",
        "respect_pdb": "respectPdb",
    },
)
class OceanGkeImportUpdatePolicyRollConfig:
    def __init__(
        self,
        *,
        batch_size_percentage: jsii.Number,
        batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
        launch_spec_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param batch_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_size_percentage OceanGkeImport#batch_size_percentage}.
        :param batch_min_healthy_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_min_healthy_percentage OceanGkeImport#batch_min_healthy_percentage}.
        :param launch_spec_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#launch_spec_ids OceanGkeImport#launch_spec_ids}.
        :param respect_pdb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#respect_pdb OceanGkeImport#respect_pdb}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ef3aa899d919b74876f86c92d9b032f034be4cd6825dcbf25ae759df0fd391f)
            check_type(argname="argument batch_size_percentage", value=batch_size_percentage, expected_type=type_hints["batch_size_percentage"])
            check_type(argname="argument batch_min_healthy_percentage", value=batch_min_healthy_percentage, expected_type=type_hints["batch_min_healthy_percentage"])
            check_type(argname="argument launch_spec_ids", value=launch_spec_ids, expected_type=type_hints["launch_spec_ids"])
            check_type(argname="argument respect_pdb", value=respect_pdb, expected_type=type_hints["respect_pdb"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "batch_size_percentage": batch_size_percentage,
        }
        if batch_min_healthy_percentage is not None:
            self._values["batch_min_healthy_percentage"] = batch_min_healthy_percentage
        if launch_spec_ids is not None:
            self._values["launch_spec_ids"] = launch_spec_ids
        if respect_pdb is not None:
            self._values["respect_pdb"] = respect_pdb

    @builtins.property
    def batch_size_percentage(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_size_percentage OceanGkeImport#batch_size_percentage}.'''
        result = self._values.get("batch_size_percentage")
        assert result is not None, "Required property 'batch_size_percentage' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def batch_min_healthy_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#batch_min_healthy_percentage OceanGkeImport#batch_min_healthy_percentage}.'''
        result = self._values.get("batch_min_healthy_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def launch_spec_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#launch_spec_ids OceanGkeImport#launch_spec_ids}.'''
        result = self._values.get("launch_spec_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def respect_pdb(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_gke_import#respect_pdb OceanGkeImport#respect_pdb}.'''
        result = self._values.get("respect_pdb")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanGkeImportUpdatePolicyRollConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanGkeImportUpdatePolicyRollConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanGkeImport.OceanGkeImportUpdatePolicyRollConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb2c260ec879249d9d2899d99438692f7d264149fe35d0668ef283a80f8f9770)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBatchMinHealthyPercentage")
    def reset_batch_min_healthy_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchMinHealthyPercentage", []))

    @jsii.member(jsii_name="resetLaunchSpecIds")
    def reset_launch_spec_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLaunchSpecIds", []))

    @jsii.member(jsii_name="resetRespectPdb")
    def reset_respect_pdb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRespectPdb", []))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentageInput")
    def batch_min_healthy_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchMinHealthyPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentageInput")
    def batch_size_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "batchSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="launchSpecIdsInput")
    def launch_spec_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "launchSpecIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="respectPdbInput")
    def respect_pdb_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "respectPdbInput"))

    @builtins.property
    @jsii.member(jsii_name="batchMinHealthyPercentage")
    def batch_min_healthy_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchMinHealthyPercentage"))

    @batch_min_healthy_percentage.setter
    def batch_min_healthy_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c49c5f59f17e0b421f0f801fd0d2e67a8d0c8affb22998f8b5f9214eb11a3fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchMinHealthyPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchSizePercentage")
    def batch_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "batchSizePercentage"))

    @batch_size_percentage.setter
    def batch_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ab219e35da76d103a17dad994b30dd7eb28716a2bc1caa923e40e1ee56bbef2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="launchSpecIds")
    def launch_spec_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "launchSpecIds"))

    @launch_spec_ids.setter
    def launch_spec_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f65da1ebfebd5df136ec256b54d3c3b20973cb1960e205e49b27812960e01bab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "launchSpecIds", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__5db032f7fc630cbeebf0ea19630779a19b5d3452a6d4a4aaef978eb1f1addc5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "respectPdb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceanGkeImportUpdatePolicyRollConfig]:
        return typing.cast(typing.Optional[OceanGkeImportUpdatePolicyRollConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceanGkeImportUpdatePolicyRollConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65efe525300c6744483e806f225c1cf9cccd8dd922faca510aa846df188e6a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanGkeImport",
    "OceanGkeImportAutoUpdate",
    "OceanGkeImportAutoUpdateList",
    "OceanGkeImportAutoUpdateOutputReference",
    "OceanGkeImportAutoscaler",
    "OceanGkeImportAutoscalerDown",
    "OceanGkeImportAutoscalerDownOutputReference",
    "OceanGkeImportAutoscalerHeadroom",
    "OceanGkeImportAutoscalerHeadroomOutputReference",
    "OceanGkeImportAutoscalerOutputReference",
    "OceanGkeImportAutoscalerResourceLimits",
    "OceanGkeImportAutoscalerResourceLimitsOutputReference",
    "OceanGkeImportBackendServices",
    "OceanGkeImportBackendServicesList",
    "OceanGkeImportBackendServicesNamedPorts",
    "OceanGkeImportBackendServicesNamedPortsList",
    "OceanGkeImportBackendServicesNamedPortsOutputReference",
    "OceanGkeImportBackendServicesOutputReference",
    "OceanGkeImportConfig",
    "OceanGkeImportFilters",
    "OceanGkeImportFiltersOutputReference",
    "OceanGkeImportScheduledTask",
    "OceanGkeImportScheduledTaskList",
    "OceanGkeImportScheduledTaskOutputReference",
    "OceanGkeImportScheduledTaskShutdownHours",
    "OceanGkeImportScheduledTaskShutdownHoursOutputReference",
    "OceanGkeImportScheduledTaskTasks",
    "OceanGkeImportScheduledTaskTasksList",
    "OceanGkeImportScheduledTaskTasksOutputReference",
    "OceanGkeImportScheduledTaskTasksTaskParameters",
    "OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll",
    "OceanGkeImportScheduledTaskTasksTaskParametersClusterRollOutputReference",
    "OceanGkeImportScheduledTaskTasksTaskParametersOutputReference",
    "OceanGkeImportShieldedInstanceConfig",
    "OceanGkeImportShieldedInstanceConfigOutputReference",
    "OceanGkeImportStrategy",
    "OceanGkeImportStrategyList",
    "OceanGkeImportStrategyOutputReference",
    "OceanGkeImportUpdatePolicy",
    "OceanGkeImportUpdatePolicyOutputReference",
    "OceanGkeImportUpdatePolicyRollConfig",
    "OceanGkeImportUpdatePolicyRollConfigOutputReference",
]

publication.publish()

def _typecheckingstub__67352a7d95b89b2a90348dfed9cc26141aad6a80e92731c133671b54056fc5ad(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_name: builtins.str,
    location: builtins.str,
    autoscaler: typing.Optional[typing.Union[OceanGkeImportAutoscaler, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_update: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportAutoUpdate, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    blacklist: typing.Optional[typing.Sequence[builtins.str]] = None,
    controller_cluster_id: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    filters: typing.Optional[typing.Union[OceanGkeImportFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    root_volume_type: typing.Optional[builtins.str] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    shielded_instance_config: typing.Optional[typing.Union[OceanGkeImportShieldedInstanceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanGkeImportUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    use_as_template_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__79035f4d0d1eefa115c086d7be79e7c6c50bb31c4ef151144b8a03472f2d26f8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f42d3bcfebe58330957466a53968172733e4a204bf55ea17addd7004e9a3f2d2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportAutoUpdate, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99b94d817dff03fd8d7cd284f5a53ce683fdfd23de7ceeec564587aad0c89215(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServices, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70056f79e26bba4c77282430716ce00d4e5ae5bf9f6ce92ce8cbb4490182070a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportScheduledTask, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beaf570efc232b300cbae73fcdd10c59f4d02a2f668621beb7662ed1112a284e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportStrategy, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a727b343f0b7f19388cd113485f0055fb8bc8f5fabb2697a2ad884613f7a920(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ab72beb7f144b671dbc233c6b952cd5a582a352658cdd7a73fefa67c2d8607(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c1b2c8243380a33d1046aa6b1fba2316e7f0127450cfbbabc4baf1d0f2de8de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4728b0f386ccda692672e8291e7518136a3c5d462c965032a57e93807e07394a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2330214ea2ceff01e87dd97205b1c60cdcd9fc50e9319fe7fa2cc86e155525c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f90dc6fb1f4c2fab06589a214671ee30d8fbfb94e184beab9723758a37b68d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c15f7504eec6a10ce9aa6e24af9ca84986e3e716e532ff0bba0756078d717142(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af69003e73e74a70dbb8303759e0b2ce0eaef3bbae068d54d8cffec81a82950(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__952f0c2c5777b0000a35132c2f1a654d2f17cb29fbe8516a962fef907b615360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078174ff077980881a2fdb7d098843260ffdc79e2e0c30aa4f6c056085a55d0e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b76a41e52e26c924e6022f94f1199565b83d1813fde516f2162a75596ce5728a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa0d4557aecf5262507e8ce5fdd28efa723e26ae62158f2b5c7798bc3d716e7d(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9245b21d65bed5be4c427eb61ae8ffd99b2292230c0aa32018113c9c890d49f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17266a92e279d4ad070876d8e30190da0f0c8cb2314e4b2d7da6f32e6f7e9af8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b0c728c54bec0631618e225de51dbc4df8b54c0121399bf0892e7c3325e4fb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22888dd068305906274e84abb04b031f931b735a44b3617a3995b1882fd3f58a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e5a0ea503b48771cd18395101a268e6f15a15e065a2c2d820a9642f310b597(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60748516cad4eaff6112d4ffceddbae00303477545a44b9e878be1c79a4bdda(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportAutoUpdate]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46752b35bea62b49a0f806fa6cc4faf8cc7dcaa0b36bfd6ccf2fafe66b2e3286(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c752169fc62654a54cb3f9f5fa5a2d37297d33d0f04fe5e5013e71f21859566b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f54487c47272e8c688d82100285979b488291a2ade7c00f2c9b0d02e6e8c1a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportAutoUpdate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b1686952a444b05612bdd8c60355440f74976f79b8dd47aa44bd7db5282a693(
    *,
    auto_headroom_percentage: typing.Optional[jsii.Number] = None,
    cooldown: typing.Optional[jsii.Number] = None,
    down: typing.Optional[typing.Union[OceanGkeImportAutoscalerDown, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_automatic_and_manual_headroom: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    headroom: typing.Optional[typing.Union[OceanGkeImportAutoscalerHeadroom, typing.Dict[builtins.str, typing.Any]]] = None,
    is_auto_config: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    resource_limits: typing.Optional[typing.Union[OceanGkeImportAutoscalerResourceLimits, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a0ddcd893ead90f58f19603d8c69e072ddb6dc0b0781bb15c9000ebc0b89682(
    *,
    evaluation_periods: typing.Optional[jsii.Number] = None,
    is_aggressive_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_scale_down_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9350120b8d944d0c06129df2accb4171d7cab0fac651e74b3267e8647d7def4b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b12f8748755b5fa8a24548d64214fe7920a33a1d5a32227ebae35bca6a1d2fec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fa1f949f5c31044c68b4c3d1d24444892455ef388ac32f34a95360e6f34348e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a41b1e429dd9928677519558591e70ecf75e59a6b41a3bdde04612d668d67e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e255980306ddccb7ba6545b4a717267bda2112927be468217a31a9c85b8a4b7d(
    value: typing.Optional[OceanGkeImportAutoscalerDown],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__298336ff0256d37fe46a5716fe5852a813fb8dc4d53140c4f9919d2d9ad974c8(
    *,
    cpu_per_unit: typing.Optional[jsii.Number] = None,
    gpu_per_unit: typing.Optional[jsii.Number] = None,
    memory_per_unit: typing.Optional[jsii.Number] = None,
    num_of_units: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__339b71934d6c209a041c0712cd0ab46d90d020aa6ead66e55b544f6fc6340813(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15de092144b52557ec311e93db0fe9809bca54f08495088d36e137e0fe78e584(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17a9557ff4e9c81f0375de48b169c86678011465f6587ef91789bd8f68af13c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0283d98799464576709c00aa4949aef0610077f2499142f453a10c04b57b15ee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e764ebafb759cebce8f40d917a033c8d9520e78c50250cd28521b392d6817f0d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06184e2b152069b4062ccf90786b17246aec049811a629d6be56101c7179e33d(
    value: typing.Optional[OceanGkeImportAutoscalerHeadroom],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56795a3bd1a04e7e16ee871c016977e3a8dc581886cf02dd98fbae1857771fd0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86edc331911cb973a456eb980eff80e9f49a54595fed535ce047cd7b6b2b9372(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cb0ce12f57b133d72cb48d97ec1b81cee2976b74f732b785767c132daf417e4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efd665da5316bd61f1e0cea531e03e694d40da651acf9f52d234fb6455e6838(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6f6c27e267421d76dffb611c717634afa0d702d5d54ca3fa1de5fe016771a7e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a25b9fb377e952f57c67d15e5b1670de23e3edfcf2c79a3939224eeb9136011(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66b81f306ab49b1d988c862bad02295b495ad1dd7985daa090e33b53b7020221(
    value: typing.Optional[OceanGkeImportAutoscaler],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bdc99b91e189383a6aae8036bdb6fbb8671409aace8c9a2369b118f1f9932c9(
    *,
    max_memory_gib: typing.Optional[jsii.Number] = None,
    max_vcpu: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64e0b185e68801fc74e46fa9b5f2690b809c7916a370e04e1802d7bf9741963a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a2dbe0bb5b020a8300a9066d23660a2c4f766fdee0109c9e37e79d164ec22ff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f279b0967bad435010afba44fcb15d5e0fbfdb4fac7c352f96617e5b66e8f2dd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5cb17986bb7b27906e1c149627390ed37f30211eb01e7bf4c17bd07b896a3cc(
    value: typing.Optional[OceanGkeImportAutoscalerResourceLimits],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfeb7ff618071ef13bc94fc426d9fc0d89406b58d39d08a3e2e6780b0af3fa17(
    *,
    service_name: builtins.str,
    location_type: typing.Optional[builtins.str] = None,
    named_ports: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServicesNamedPorts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    scheme: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__114fce57adfd19f19c5acc7ad9c5d6b90b1442a42480df47f0874925173201c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__407a031a1cda1d172f5888fe07053fcf6c103df90a2cb5f1026d6cbf69f6156e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29cc14bf0af2a14407a72b1df23e51c17016998f768b4ed21dadc42c8dabf5d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__351fb37f7a5bedc70ae8ced5017cb77da836b3404e232259923d8e0e42ddb4df(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f600f4a99f3494f812a28c3a8ebda3bc416757a38f40c08ce47a751d5d317ac4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a039cb9e376618f3eb78f7dc615f74c56e84f0ab29467d18262d91be992c17f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServices]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab881a79ece9e28c311c6b1ebbffada472fc6f866d16faaa21190f6e548086a8(
    *,
    name: builtins.str,
    ports: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731c041c69de323a0e7d10a7d416a3896b328af582488c413738f49df99981de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7f59a2f5fa577e2752a78eedd62b77d247f4ebcb7cbce5dd7d07a1d03e4987a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ff22d5e4ac2a2c089d5dfc3db335b993eb42068718a495ff1a08aa5a29c89f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__202864e7393a9c22a091a7cb8165d4c35d3c3c8663f3b0b0ebb1493b1d3aae4f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62914d0f1deb86c99c31f29760e8876eb997baaa1e0708b1c3274e50f0bdb7d1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0028d1587a135e2fc6f6a183c56fa60388a26322e5b975a4085baf5f4866dff5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportBackendServicesNamedPorts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62eaace54a506c3303081e37815126181b7aafc9f929cd9a29f7d05c60b4d267(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__674a77480b86a005323ea2576b9351f23613b3eb528d6bc3d9c1da464604778b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7a203378ab001046afc76f12a7b26ac8efc64f8670580b5b1c3a8acc77265e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59f9d1f2db5c634a047d1ae4ad24f5a6f493fda9f783e953c3ad9eb84068daf8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServicesNamedPorts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__973639b77d3f6a1d3c020b896a22f4da573b26e08834f3e265ef33d855b60e25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05fb3c526c70f00950a09c3b998e53250cea4edd7765f49382cbf5626977adbc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServicesNamedPorts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c45c7888bf973fd128a589dd7fc7caf5736f558038e6496fd551c756d79d874b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97afaf5fc4c3bedc115cabce9e5105cc736edb2b6f64ec7397a2a92548c84751(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2781a59bb7d04f0d45db310a9bb628b890488f23f43a8faa7d41c261e7e55d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f0754cad8129d1039714e1687ed7e6635e96e0eb180e91e2faf45f1991bb01(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportBackendServices]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8ad51a65eb42b78c4689e48d67c150f0c9b58ad229861fdb476b2b19dc7501a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_name: builtins.str,
    location: builtins.str,
    autoscaler: typing.Optional[typing.Union[OceanGkeImportAutoscaler, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_update: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportAutoUpdate, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend_services: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportBackendServices, typing.Dict[builtins.str, typing.Any]]]]] = None,
    blacklist: typing.Optional[typing.Sequence[builtins.str]] = None,
    controller_cluster_id: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    filters: typing.Optional[typing.Union[OceanGkeImportFilters, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    root_volume_type: typing.Optional[builtins.str] = None,
    scheduled_task: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportScheduledTask, typing.Dict[builtins.str, typing.Any]]]]] = None,
    shielded_instance_config: typing.Optional[typing.Union[OceanGkeImportShieldedInstanceConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    strategy: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportStrategy, typing.Dict[builtins.str, typing.Any]]]]] = None,
    update_policy: typing.Optional[typing.Union[OceanGkeImportUpdatePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    use_as_template_only: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f33e41b8de8fe017b0f0de2cdc9a4bbce2884bf74f86e58ce7bd30a5ee6c046(
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

def _typecheckingstub__e890a4db5a2c8e6f1c563e56de774c6a505d27c14ab82ac54e879f422023f165(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de51815b32712d286c011ea3346d01f36085823591cd138841ad57a149d97b49(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__defcaa8fde7585d7e345333f68b0fe4a29a50ff850396eeee73c923179a32358(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ef55308a1d817a74dbe72e7cfe9d59ea8957ffcdf0ca745028345421119fb30(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3295260fd863b42072cb323515eccfee386a00e3daa2293d479e5ffbc4757421(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a33a74ee0adf96e513475dec1c12c0cc5aaf1b739429a8219e381c3f756d8d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__491a548f342e26d0f2b0da1b252c607b337791c3967c7e9b9f119a87b46e6566(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f58ca2c3a95222e4b17ccd209f73b73c6d59753d8b18ceb543fe1f21e929ee9(
    value: typing.Optional[OceanGkeImportFilters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__629648838059e4b07e84dc211a482acaa31c89c30c38ea63215f83cd4918e7d1(
    *,
    shutdown_hours: typing.Optional[typing.Union[OceanGkeImportScheduledTaskShutdownHours, typing.Dict[builtins.str, typing.Any]]] = None,
    tasks: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportScheduledTaskTasks, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d50df939e3f10bb97bf9901ac8e56a41a680d829af37f0da3cd0696868ebd9e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6627cce062a63d32eeec489ff2d31e0e3927af830aa162a3ae510811f86c3b0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f77899e92c50734bf94d8872a82570c70310a92a75a32e9c0149f848cadc1d66(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c9d9e4a9bb289c987a520bfcdcac4d74a7ed5b3943d821297a519af6916f8f0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fc347e5af2af571a9135b0b0b6825eba0443e761104f745738b15ce36dbde22(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adc797dca065f0e09b847b17105c9b026a748c132e5b135998d91727c7d8e63f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTask]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2560bd6f81f60f5e6efa149979656bc6e300ab759fa70a14b18ff673520ee4d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fced1e9df5eb6dd039c688f5946c40a2c836ac19f3826b117535a5f1842281c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanGkeImportScheduledTaskTasks, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6b0535d96a3bfd301f8d7475bcd82372683778a62d5afd3cb149aaff0ffd918(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTask]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39e3131182b1796177add371d60b9772623dc30eb049a14fde5175c31ba2de8f(
    *,
    time_windows: typing.Sequence[builtins.str],
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2052b6aa77bb1a6a09a7807f70ee16d9e8df36047faf5600d5a3bbc611b1465a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebe00492e21e1d270ef7000cd84caab5557d5f6433696204dca8cdca9ff2984c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b56e95bba709aa3b76ff9ed60187cfd28bcdb00ad0230349ddc47ac12e057b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92854a6c191198172b99680c502dac4dea21ad0787875bade4c09ea1cc272ab(
    value: typing.Optional[OceanGkeImportScheduledTaskShutdownHours],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c13536d304752323e2d2d407fcb94bf96fe1eb6b80e498265bfcd6d00eca7cf1(
    *,
    cron_expression: builtins.str,
    is_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    task_type: builtins.str,
    task_parameters: typing.Optional[typing.Union[OceanGkeImportScheduledTaskTasksTaskParameters, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9b51ba84ccb300264dd605fcc6cfff0d122ce2946c142bd9e3026da1e74f126(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a427418b146c6ea3ac305bc4cdf18d515e230e71c9b8e0bd011d9d8309f7e81(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6cc7dfe7a5aaede1c7e7f3e9a0722a99de2f7aa0f7e1bec1e7bd3d37e8bc16b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02eaab1fd09ac8bbb5ad3b492d1cb3cd67d11e411b68b8181f34d38a423aa797(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b54f87ec5ae4f88a1501a14ed3a686e2883cafc71a99dbbaa791686f9c54c6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9bd1e43a7de96877c0c998e0e0b23bf6d09813d40bf962b844c4a5ce1fd0e98(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportScheduledTaskTasks]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5aeac62b0491406838e8c4f4c11137689c76ca09b670807a2c3cb280e617f02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d93d0dedc55388433acdad4b5812015cfb8576790b38c9526476c2653ff27a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0d377f6aae21732fb7aad733d9aafe645a01ff255e962a284837153b6bc808e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81128af4cd6b2b0e4ca377fee1a420e334341c1dc59b7d6ed320c8791284205a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca07eaeeb86e0973163d8d4e7b934c1bd071c38c5cdab298c433bf24eabeaba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportScheduledTaskTasks]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c836496998aeee1e38cc6f84f435092ddfba906114258394dfe606f06048ce3c(
    *,
    cluster_roll: typing.Optional[typing.Union[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__734a060bb0496acb6393ca2612bbb7610439321df635596cce79565176645571(
    *,
    batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
    batch_size_percentage: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76993a79728ba7f8f54f75a1d3fff828b80e65b4d7a825eab9615f185c4e4e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b06c2475f4e54b6a9335a4ee701f8dfcc73e9de3ef69105ace126e2e7b59f516(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b47e393ce47d69835ba473469638fe1ac08061e825e053f4476fc59508b618e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1f29fea28f706d4779190de609d6afe564e73ccb218afade7fc16b1d9f1b93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fd7d22040ac9c14839455156b2101a629acf0647391a79cca1ff03019857493(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c0eccb2e3576e970e42be1b3c77a2915ba380b974242ef5393a48aca1ae13d(
    value: typing.Optional[OceanGkeImportScheduledTaskTasksTaskParametersClusterRoll],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5d336f8c60ac640a5997079b22807ca179f32dba37b406a3500245e01e90407(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__765cdebc2b4878f17183d11f7e15695cd455bf5b6fabc2043356342209a5b29a(
    value: typing.Optional[OceanGkeImportScheduledTaskTasksTaskParameters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00c697eec4cbab40fe8f7e03d4db25408bb85fbf483859549336756efc685ef9(
    *,
    enable_integrity_monitoring: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_secure_boot: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6a23d0e489dc826e620cf9539cb8b273d6483bc6d4db61adc0454477310a71c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaa5c25c44b70c9900f7779abc6f8f2ac1d02b173b09c79aae61b9ce5cca9967(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b41a7756fba22d642802ce090958ef540255aee1a2d1f68940b222d39c8f1296(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1dd44b9167e3b2d4f81393cf2ac6673c99a636d69b8f572b7ce390a31a7f829(
    value: typing.Optional[OceanGkeImportShieldedInstanceConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41f01af3d96d19ae641bab1a24be60b69bf64dfbc2248f10c5705bceba76ab19(
    *,
    draining_timeout: typing.Optional[jsii.Number] = None,
    preemptible_percentage: typing.Optional[jsii.Number] = None,
    provisioning_model: typing.Optional[builtins.str] = None,
    scaling_orientation: typing.Optional[builtins.str] = None,
    should_utilize_commitments: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c38fba0e3189b31294cb8b20d314659cd4cd2e2cf65e1809e3bef24799d4682f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9f35129726debf60b633f891ea1c50119420e1db9da1e191cd18aef03529a87(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6407972b266c7df558bcdb729e6de9698731fc23b31efb91c3c5d62a97643d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f005319356752a322bdc543a7654c867c15a84c0806d81ea43b66c8ce0aadeb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c0e453cf05de03c1dd8ee0cb7e29b6c3d68627bff4f3a1db0725efa9ba7694(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed242fe02c40112a5c5cae92826237f9cde70dec3981d60e92c50be99d31771f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanGkeImportStrategy]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf652cb8b365faf72343bfe7337a31ff6b52a269f09cb2c8c00476dfe22ba8f5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__382f29c9a91354ccf7a1f5f50d006ba013c28d1b9840ce0e5af69af20695c4de(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b116499391e94ebab5f8d89da4361f006ca3c2a401b396749ebf118de2950e9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fda575d0bf1833e665474ef314c5466dc3e5297927dbf611ccea400536bf673(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c92759f894f881ad5630701794df0438e3dfb1b1ba66fc2a659e91284c00c512(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c9d74749b1fd3efcab361a199f2357a1fdcf90932d94670bd7f52499a5665d1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2e0244cdcee631ecf93f2ad95f2bd7981369658a2759713c5e05018be4543f6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanGkeImportStrategy]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08bb1b375d22b17f01679b170a59d54e7356d5e7f4b6f64e640e952569dc116d(
    *,
    should_roll: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    conditioned_roll: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    roll_config: typing.Optional[typing.Union[OceanGkeImportUpdatePolicyRollConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e05008e5559823af7c2c997bfed0af4c5d922600f4548dae0fae5d2e005b10b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3661aa3833671b76def6d2977c7c7bee340022f7cd521c088716b63b40b05c6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f80dd284528741e8133cc11320b042f35f7d417722f22298cf2b2191a2ada9f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72aae5cf1dbbb1e8c5e20e550b23d38eb783fa37bb6ed5e9a95f4f2b8b43e204(
    value: typing.Optional[OceanGkeImportUpdatePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ef3aa899d919b74876f86c92d9b032f034be4cd6825dcbf25ae759df0fd391f(
    *,
    batch_size_percentage: jsii.Number,
    batch_min_healthy_percentage: typing.Optional[jsii.Number] = None,
    launch_spec_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    respect_pdb: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb2c260ec879249d9d2899d99438692f7d264149fe35d0668ef283a80f8f9770(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c49c5f59f17e0b421f0f801fd0d2e67a8d0c8affb22998f8b5f9214eb11a3fb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ab219e35da76d103a17dad994b30dd7eb28716a2bc1caa923e40e1ee56bbef2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f65da1ebfebd5df136ec256b54d3c3b20973cb1960e205e49b27812960e01bab(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5db032f7fc630cbeebf0ea19630779a19b5d3452a6d4a4aaef978eb1f1addc5f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65efe525300c6744483e806f225c1cf9cccd8dd922faca510aa846df188e6a15(
    value: typing.Optional[OceanGkeImportUpdatePolicyRollConfig],
) -> None:
    """Type checking stubs"""
    pass
