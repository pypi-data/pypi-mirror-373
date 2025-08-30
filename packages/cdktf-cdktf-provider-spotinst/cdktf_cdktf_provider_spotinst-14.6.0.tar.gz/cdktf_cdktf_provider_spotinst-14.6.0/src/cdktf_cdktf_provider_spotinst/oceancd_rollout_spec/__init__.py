r'''
# `spotinst_oceancd_rollout_spec`

Refer to the Terraform Registry for docs: [`spotinst_oceancd_rollout_spec`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec).
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


class OceancdRolloutSpec(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpec",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec spotinst_oceancd_rollout_spec}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        rollout_spec_name: builtins.str,
        strategy: typing.Union["OceancdRolloutSpecStrategy", typing.Dict[builtins.str, typing.Any]],
        failure_policy: typing.Optional[typing.Union["OceancdRolloutSpecFailurePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        spot_deployment: typing.Optional[typing.Union["OceancdRolloutSpecSpotDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_deployments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecSpotDeployments", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic: typing.Optional[typing.Union["OceancdRolloutSpecTraffic", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec spotinst_oceancd_rollout_spec} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param rollout_spec_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#rollout_spec_name OceancdRolloutSpec#rollout_spec_name}.
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#strategy OceancdRolloutSpec#strategy}
        :param failure_policy: failure_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#failure_policy OceancdRolloutSpec#failure_policy}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#id OceancdRolloutSpec#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param spot_deployment: spot_deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment OceancdRolloutSpec#spot_deployment}
        :param spot_deployments: spot_deployments block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments OceancdRolloutSpec#spot_deployments}
        :param traffic: traffic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#traffic OceancdRolloutSpec#traffic}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f5db3660a2fb40c01efe44ff20bdc43623b2087ae229e419e6db665652aa721)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceancdRolloutSpecConfig(
            rollout_spec_name=rollout_spec_name,
            strategy=strategy,
            failure_policy=failure_policy,
            id=id,
            spot_deployment=spot_deployment,
            spot_deployments=spot_deployments,
            traffic=traffic,
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
        '''Generates CDKTF code for importing a OceancdRolloutSpec resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceancdRolloutSpec to import.
        :param import_from_id: The id of the existing OceancdRolloutSpec that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceancdRolloutSpec to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4336be3674617384e7d78a1d23faf0cc9a22b21759ca73160ba9dadd4165e3bb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putFailurePolicy")
    def put_failure_policy(self, *, action: builtins.str) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#action OceancdRolloutSpec#action}.
        '''
        value = OceancdRolloutSpecFailurePolicy(action=action)

        return typing.cast(None, jsii.invoke(self, "putFailurePolicy", [value]))

    @jsii.member(jsii_name="putSpotDeployment")
    def put_spot_deployment(
        self,
        *,
        spot_deployment_cluster_id: typing.Optional[builtins.str] = None,
        spot_deployment_name: typing.Optional[builtins.str] = None,
        spot_deployment_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param spot_deployment_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_cluster_id OceancdRolloutSpec#spot_deployment_cluster_id}.
        :param spot_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_name OceancdRolloutSpec#spot_deployment_name}.
        :param spot_deployment_namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_namespace OceancdRolloutSpec#spot_deployment_namespace}.
        '''
        value = OceancdRolloutSpecSpotDeployment(
            spot_deployment_cluster_id=spot_deployment_cluster_id,
            spot_deployment_name=spot_deployment_name,
            spot_deployment_namespace=spot_deployment_namespace,
        )

        return typing.cast(None, jsii.invoke(self, "putSpotDeployment", [value]))

    @jsii.member(jsii_name="putSpotDeployments")
    def put_spot_deployments(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecSpotDeployments", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2facde2ffcb38f5a81a5af491f9aac0e30f7749d440c64a689159a9f3730510)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSpotDeployments", [value]))

    @jsii.member(jsii_name="putStrategy")
    def put_strategy(
        self,
        *,
        strategy_name: builtins.str,
        args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecStrategyArgs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param strategy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#strategy_name OceancdRolloutSpec#strategy_name}.
        :param args: args block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#args OceancdRolloutSpec#args}
        '''
        value = OceancdRolloutSpecStrategy(strategy_name=strategy_name, args=args)

        return typing.cast(None, jsii.invoke(self, "putStrategy", [value]))

    @jsii.member(jsii_name="putTraffic")
    def put_traffic(
        self,
        *,
        alb: typing.Optional[typing.Union["OceancdRolloutSpecTrafficAlb", typing.Dict[builtins.str, typing.Any]]] = None,
        ambassador: typing.Optional[typing.Union["OceancdRolloutSpecTrafficAmbassador", typing.Dict[builtins.str, typing.Any]]] = None,
        canary_service: typing.Optional[builtins.str] = None,
        istio: typing.Optional[typing.Union["OceancdRolloutSpecTrafficIstio", typing.Dict[builtins.str, typing.Any]]] = None,
        nginx: typing.Optional[typing.Union["OceancdRolloutSpecTrafficNginx", typing.Dict[builtins.str, typing.Any]]] = None,
        ping_pong: typing.Optional[typing.Union["OceancdRolloutSpecTrafficPingPong", typing.Dict[builtins.str, typing.Any]]] = None,
        smi: typing.Optional[typing.Union["OceancdRolloutSpecTrafficSmi", typing.Dict[builtins.str, typing.Any]]] = None,
        stable_service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alb: alb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb OceancdRolloutSpec#alb}
        :param ambassador: ambassador block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ambassador OceancdRolloutSpec#ambassador}
        :param canary_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_service OceancdRolloutSpec#canary_service}.
        :param istio: istio block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#istio OceancdRolloutSpec#istio}
        :param nginx: nginx block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#nginx OceancdRolloutSpec#nginx}
        :param ping_pong: ping_pong block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ping_pong OceancdRolloutSpec#ping_pong}
        :param smi: smi block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#smi OceancdRolloutSpec#smi}
        :param stable_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_service OceancdRolloutSpec#stable_service}.
        '''
        value = OceancdRolloutSpecTraffic(
            alb=alb,
            ambassador=ambassador,
            canary_service=canary_service,
            istio=istio,
            nginx=nginx,
            ping_pong=ping_pong,
            smi=smi,
            stable_service=stable_service,
        )

        return typing.cast(None, jsii.invoke(self, "putTraffic", [value]))

    @jsii.member(jsii_name="resetFailurePolicy")
    def reset_failure_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailurePolicy", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSpotDeployment")
    def reset_spot_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeployment", []))

    @jsii.member(jsii_name="resetSpotDeployments")
    def reset_spot_deployments(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeployments", []))

    @jsii.member(jsii_name="resetTraffic")
    def reset_traffic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTraffic", []))

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
    @jsii.member(jsii_name="failurePolicy")
    def failure_policy(self) -> "OceancdRolloutSpecFailurePolicyOutputReference":
        return typing.cast("OceancdRolloutSpecFailurePolicyOutputReference", jsii.get(self, "failurePolicy"))

    @builtins.property
    @jsii.member(jsii_name="spotDeployment")
    def spot_deployment(self) -> "OceancdRolloutSpecSpotDeploymentOutputReference":
        return typing.cast("OceancdRolloutSpecSpotDeploymentOutputReference", jsii.get(self, "spotDeployment"))

    @builtins.property
    @jsii.member(jsii_name="spotDeployments")
    def spot_deployments(self) -> "OceancdRolloutSpecSpotDeploymentsList":
        return typing.cast("OceancdRolloutSpecSpotDeploymentsList", jsii.get(self, "spotDeployments"))

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "OceancdRolloutSpecStrategyOutputReference":
        return typing.cast("OceancdRolloutSpecStrategyOutputReference", jsii.get(self, "strategy"))

    @builtins.property
    @jsii.member(jsii_name="traffic")
    def traffic(self) -> "OceancdRolloutSpecTrafficOutputReference":
        return typing.cast("OceancdRolloutSpecTrafficOutputReference", jsii.get(self, "traffic"))

    @builtins.property
    @jsii.member(jsii_name="failurePolicyInput")
    def failure_policy_input(
        self,
    ) -> typing.Optional["OceancdRolloutSpecFailurePolicy"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecFailurePolicy"], jsii.get(self, "failurePolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="rolloutSpecNameInput")
    def rollout_spec_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rolloutSpecNameInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentInput")
    def spot_deployment_input(
        self,
    ) -> typing.Optional["OceancdRolloutSpecSpotDeployment"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecSpotDeployment"], jsii.get(self, "spotDeploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsInput")
    def spot_deployments_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecSpotDeployments"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecSpotDeployments"]]], jsii.get(self, "spotDeploymentsInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyInput")
    def strategy_input(self) -> typing.Optional["OceancdRolloutSpecStrategy"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecStrategy"], jsii.get(self, "strategyInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficInput")
    def traffic_input(self) -> typing.Optional["OceancdRolloutSpecTraffic"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecTraffic"], jsii.get(self, "trafficInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e42971c34ce6a17771d0b7b08e2fde967b885f968b9d94727342127c1fa9dcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rolloutSpecName")
    def rollout_spec_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rolloutSpecName"))

    @rollout_spec_name.setter
    def rollout_spec_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2e208ccfb7e0afe895f1bac22f76239d52e017de9e3c8215c58d1a658a206a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolloutSpecName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "rollout_spec_name": "rolloutSpecName",
        "strategy": "strategy",
        "failure_policy": "failurePolicy",
        "id": "id",
        "spot_deployment": "spotDeployment",
        "spot_deployments": "spotDeployments",
        "traffic": "traffic",
    },
)
class OceancdRolloutSpecConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        rollout_spec_name: builtins.str,
        strategy: typing.Union["OceancdRolloutSpecStrategy", typing.Dict[builtins.str, typing.Any]],
        failure_policy: typing.Optional[typing.Union["OceancdRolloutSpecFailurePolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        spot_deployment: typing.Optional[typing.Union["OceancdRolloutSpecSpotDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        spot_deployments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecSpotDeployments", typing.Dict[builtins.str, typing.Any]]]]] = None,
        traffic: typing.Optional[typing.Union["OceancdRolloutSpecTraffic", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param rollout_spec_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#rollout_spec_name OceancdRolloutSpec#rollout_spec_name}.
        :param strategy: strategy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#strategy OceancdRolloutSpec#strategy}
        :param failure_policy: failure_policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#failure_policy OceancdRolloutSpec#failure_policy}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#id OceancdRolloutSpec#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param spot_deployment: spot_deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment OceancdRolloutSpec#spot_deployment}
        :param spot_deployments: spot_deployments block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments OceancdRolloutSpec#spot_deployments}
        :param traffic: traffic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#traffic OceancdRolloutSpec#traffic}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(strategy, dict):
            strategy = OceancdRolloutSpecStrategy(**strategy)
        if isinstance(failure_policy, dict):
            failure_policy = OceancdRolloutSpecFailurePolicy(**failure_policy)
        if isinstance(spot_deployment, dict):
            spot_deployment = OceancdRolloutSpecSpotDeployment(**spot_deployment)
        if isinstance(traffic, dict):
            traffic = OceancdRolloutSpecTraffic(**traffic)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9cdf34806df25e7910cc4f3230c9daa6bf7c5b50515796eb5a264b92d7105ff)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument rollout_spec_name", value=rollout_spec_name, expected_type=type_hints["rollout_spec_name"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument failure_policy", value=failure_policy, expected_type=type_hints["failure_policy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument spot_deployment", value=spot_deployment, expected_type=type_hints["spot_deployment"])
            check_type(argname="argument spot_deployments", value=spot_deployments, expected_type=type_hints["spot_deployments"])
            check_type(argname="argument traffic", value=traffic, expected_type=type_hints["traffic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rollout_spec_name": rollout_spec_name,
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
        if failure_policy is not None:
            self._values["failure_policy"] = failure_policy
        if id is not None:
            self._values["id"] = id
        if spot_deployment is not None:
            self._values["spot_deployment"] = spot_deployment
        if spot_deployments is not None:
            self._values["spot_deployments"] = spot_deployments
        if traffic is not None:
            self._values["traffic"] = traffic

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
    def rollout_spec_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#rollout_spec_name OceancdRolloutSpec#rollout_spec_name}.'''
        result = self._values.get("rollout_spec_name")
        assert result is not None, "Required property 'rollout_spec_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def strategy(self) -> "OceancdRolloutSpecStrategy":
        '''strategy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#strategy OceancdRolloutSpec#strategy}
        '''
        result = self._values.get("strategy")
        assert result is not None, "Required property 'strategy' is missing"
        return typing.cast("OceancdRolloutSpecStrategy", result)

    @builtins.property
    def failure_policy(self) -> typing.Optional["OceancdRolloutSpecFailurePolicy"]:
        '''failure_policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#failure_policy OceancdRolloutSpec#failure_policy}
        '''
        result = self._values.get("failure_policy")
        return typing.cast(typing.Optional["OceancdRolloutSpecFailurePolicy"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#id OceancdRolloutSpec#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_deployment(self) -> typing.Optional["OceancdRolloutSpecSpotDeployment"]:
        '''spot_deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment OceancdRolloutSpec#spot_deployment}
        '''
        result = self._values.get("spot_deployment")
        return typing.cast(typing.Optional["OceancdRolloutSpecSpotDeployment"], result)

    @builtins.property
    def spot_deployments(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecSpotDeployments"]]]:
        '''spot_deployments block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments OceancdRolloutSpec#spot_deployments}
        '''
        result = self._values.get("spot_deployments")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecSpotDeployments"]]], result)

    @builtins.property
    def traffic(self) -> typing.Optional["OceancdRolloutSpecTraffic"]:
        '''traffic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#traffic OceancdRolloutSpec#traffic}
        '''
        result = self._values.get("traffic")
        return typing.cast(typing.Optional["OceancdRolloutSpecTraffic"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecFailurePolicy",
    jsii_struct_bases=[],
    name_mapping={"action": "action"},
)
class OceancdRolloutSpecFailurePolicy:
    def __init__(self, *, action: builtins.str) -> None:
        '''
        :param action: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#action OceancdRolloutSpec#action}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eda59a20a193e78207b0596d5823ba13e034311b5ceebd90965f623e0528a172)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
        }

    @builtins.property
    def action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#action OceancdRolloutSpec#action}.'''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecFailurePolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecFailurePolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecFailurePolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff3181428c6901df004b0a11122c634741c70a43744be01ca82b09ba92a80ff5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1f46eac590d7444e642ddbc492288adc4ac4e28ed4e64a917adb4ddb4539c81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecFailurePolicy]:
        return typing.cast(typing.Optional[OceancdRolloutSpecFailurePolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecFailurePolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a345a9a9c8a5165f637b773256db1b4180d24182a7d80fa270f75a0e58f44053)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecSpotDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "spot_deployment_cluster_id": "spotDeploymentClusterId",
        "spot_deployment_name": "spotDeploymentName",
        "spot_deployment_namespace": "spotDeploymentNamespace",
    },
)
class OceancdRolloutSpecSpotDeployment:
    def __init__(
        self,
        *,
        spot_deployment_cluster_id: typing.Optional[builtins.str] = None,
        spot_deployment_name: typing.Optional[builtins.str] = None,
        spot_deployment_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param spot_deployment_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_cluster_id OceancdRolloutSpec#spot_deployment_cluster_id}.
        :param spot_deployment_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_name OceancdRolloutSpec#spot_deployment_name}.
        :param spot_deployment_namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_namespace OceancdRolloutSpec#spot_deployment_namespace}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e3560ee11ac377d22f695e0f12bbc4a07fc075ee59795481df8e21a54103e1f)
            check_type(argname="argument spot_deployment_cluster_id", value=spot_deployment_cluster_id, expected_type=type_hints["spot_deployment_cluster_id"])
            check_type(argname="argument spot_deployment_name", value=spot_deployment_name, expected_type=type_hints["spot_deployment_name"])
            check_type(argname="argument spot_deployment_namespace", value=spot_deployment_namespace, expected_type=type_hints["spot_deployment_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if spot_deployment_cluster_id is not None:
            self._values["spot_deployment_cluster_id"] = spot_deployment_cluster_id
        if spot_deployment_name is not None:
            self._values["spot_deployment_name"] = spot_deployment_name
        if spot_deployment_namespace is not None:
            self._values["spot_deployment_namespace"] = spot_deployment_namespace

    @builtins.property
    def spot_deployment_cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_cluster_id OceancdRolloutSpec#spot_deployment_cluster_id}.'''
        result = self._values.get("spot_deployment_cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_deployment_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_name OceancdRolloutSpec#spot_deployment_name}.'''
        result = self._values.get("spot_deployment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_deployment_namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployment_namespace OceancdRolloutSpec#spot_deployment_namespace}.'''
        result = self._values.get("spot_deployment_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecSpotDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecSpotDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecSpotDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__02613ca5d6ed831f770880b152ede25bc9ab9b0faaf4d4e7983a848400520414)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSpotDeploymentClusterId")
    def reset_spot_deployment_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeploymentClusterId", []))

    @jsii.member(jsii_name="resetSpotDeploymentName")
    def reset_spot_deployment_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeploymentName", []))

    @jsii.member(jsii_name="resetSpotDeploymentNamespace")
    def reset_spot_deployment_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeploymentNamespace", []))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentClusterIdInput")
    def spot_deployment_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotDeploymentClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentNameInput")
    def spot_deployment_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotDeploymentNameInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentNamespaceInput")
    def spot_deployment_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotDeploymentNamespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentClusterId")
    def spot_deployment_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotDeploymentClusterId"))

    @spot_deployment_cluster_id.setter
    def spot_deployment_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59e283bc3b231f689461c4076f5449b22f8195531ab7273580c88844aca0dad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotDeploymentClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentName")
    def spot_deployment_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotDeploymentName"))

    @spot_deployment_name.setter
    def spot_deployment_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f7a500dda302a15b6217aeb609c01b48d6baa86e54507c0f67025da741b122f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotDeploymentName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentNamespace")
    def spot_deployment_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotDeploymentNamespace"))

    @spot_deployment_namespace.setter
    def spot_deployment_namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1860466901e9c0ee5dae73161b0a7afabbc179b180cb286642b1f726855b209)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotDeploymentNamespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecSpotDeployment]:
        return typing.cast(typing.Optional[OceancdRolloutSpecSpotDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecSpotDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5818a1c736bdda2bd4a5f6b94476343f2a21f6c6a083d8816cf261c0ea514d55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecSpotDeployments",
    jsii_struct_bases=[],
    name_mapping={
        "spot_deployments_cluster_id": "spotDeploymentsClusterId",
        "spot_deployments_name": "spotDeploymentsName",
        "spot_deployments_namespace": "spotDeploymentsNamespace",
    },
)
class OceancdRolloutSpecSpotDeployments:
    def __init__(
        self,
        *,
        spot_deployments_cluster_id: typing.Optional[builtins.str] = None,
        spot_deployments_name: typing.Optional[builtins.str] = None,
        spot_deployments_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param spot_deployments_cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments_cluster_id OceancdRolloutSpec#spot_deployments_cluster_id}.
        :param spot_deployments_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments_name OceancdRolloutSpec#spot_deployments_name}.
        :param spot_deployments_namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments_namespace OceancdRolloutSpec#spot_deployments_namespace}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__946558a01e1bba67ae3206465b7da98213be7c563c696014ef52836e08eafcb1)
            check_type(argname="argument spot_deployments_cluster_id", value=spot_deployments_cluster_id, expected_type=type_hints["spot_deployments_cluster_id"])
            check_type(argname="argument spot_deployments_name", value=spot_deployments_name, expected_type=type_hints["spot_deployments_name"])
            check_type(argname="argument spot_deployments_namespace", value=spot_deployments_namespace, expected_type=type_hints["spot_deployments_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if spot_deployments_cluster_id is not None:
            self._values["spot_deployments_cluster_id"] = spot_deployments_cluster_id
        if spot_deployments_name is not None:
            self._values["spot_deployments_name"] = spot_deployments_name
        if spot_deployments_namespace is not None:
            self._values["spot_deployments_namespace"] = spot_deployments_namespace

    @builtins.property
    def spot_deployments_cluster_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments_cluster_id OceancdRolloutSpec#spot_deployments_cluster_id}.'''
        result = self._values.get("spot_deployments_cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_deployments_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments_name OceancdRolloutSpec#spot_deployments_name}.'''
        result = self._values.get("spot_deployments_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_deployments_namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#spot_deployments_namespace OceancdRolloutSpec#spot_deployments_namespace}.'''
        result = self._values.get("spot_deployments_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecSpotDeployments(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecSpotDeploymentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecSpotDeploymentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52f8053222635fe3767cd42f3e069dc3d86a1cc41605219c416b3fe84493d9af)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdRolloutSpecSpotDeploymentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a23b929c92402c1620f819769b13de4251667c73af0f5a5da746fc1dabad3d6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdRolloutSpecSpotDeploymentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e84849253f7d6a0660384472103390a724293055ba14cf9e300cad147df50ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a89315643bcf12cf7d53e61935aa415bc0781cfef74f96b8fb6fcf2cd7d40f29)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18e2c11dc1071ef88524473d396f5e2b712866a98244c531d081fc320639c36c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecSpotDeployments]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecSpotDeployments]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecSpotDeployments]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a573f3baace5066323811f33e1b04a6d6bd5773b0dbacec6b05d635f61568f59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecSpotDeploymentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecSpotDeploymentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5291264f44f2f2ea19225c5e8342f207232fd46477e5cb6046317a142f2dfdea)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetSpotDeploymentsClusterId")
    def reset_spot_deployments_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeploymentsClusterId", []))

    @jsii.member(jsii_name="resetSpotDeploymentsName")
    def reset_spot_deployments_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeploymentsName", []))

    @jsii.member(jsii_name="resetSpotDeploymentsNamespace")
    def reset_spot_deployments_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpotDeploymentsNamespace", []))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsClusterIdInput")
    def spot_deployments_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotDeploymentsClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsNameInput")
    def spot_deployments_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotDeploymentsNameInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsNamespaceInput")
    def spot_deployments_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spotDeploymentsNamespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsClusterId")
    def spot_deployments_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotDeploymentsClusterId"))

    @spot_deployments_cluster_id.setter
    def spot_deployments_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88309320f25e81f70ef4adf6148d8dac82907d560117765525f192e7187eab54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotDeploymentsClusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsName")
    def spot_deployments_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotDeploymentsName"))

    @spot_deployments_name.setter
    def spot_deployments_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc63e6de52ab1639a34474cfa480e57c390ae29041e8d63bedbbf9266ccb91c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotDeploymentsName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spotDeploymentsNamespace")
    def spot_deployments_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "spotDeploymentsNamespace"))

    @spot_deployments_namespace.setter
    def spot_deployments_namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f8d9e43b10b9085c3c72266f5a4c6350cb7949d7407dde267596267c1135313)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spotDeploymentsNamespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecSpotDeployments]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecSpotDeployments]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecSpotDeployments]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b48e0945d1272411f88340448f142893ea2df1826ac84108a2a9c7bfb1d21df7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategy",
    jsii_struct_bases=[],
    name_mapping={"strategy_name": "strategyName", "args": "args"},
)
class OceancdRolloutSpecStrategy:
    def __init__(
        self,
        *,
        strategy_name: builtins.str,
        args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecStrategyArgs", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param strategy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#strategy_name OceancdRolloutSpec#strategy_name}.
        :param args: args block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#args OceancdRolloutSpec#args}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ad8b4cb2c5301d5f8dd33114bbc2c0fba84b99da9243792e4c2b7bc58609f65)
            check_type(argname="argument strategy_name", value=strategy_name, expected_type=type_hints["strategy_name"])
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "strategy_name": strategy_name,
        }
        if args is not None:
            self._values["args"] = args

    @builtins.property
    def strategy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#strategy_name OceancdRolloutSpec#strategy_name}.'''
        result = self._values.get("strategy_name")
        assert result is not None, "Required property 'strategy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecStrategyArgs"]]]:
        '''args block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#args OceancdRolloutSpec#args}
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecStrategyArgs"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgs",
    jsii_struct_bases=[],
    name_mapping={
        "arg_name": "argName",
        "arg_value": "argValue",
        "value_from": "valueFrom",
    },
)
class OceancdRolloutSpecStrategyArgs:
    def __init__(
        self,
        *,
        arg_name: builtins.str,
        arg_value: typing.Optional[builtins.str] = None,
        value_from: typing.Optional[typing.Union["OceancdRolloutSpecStrategyArgsValueFrom", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param arg_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#arg_name OceancdRolloutSpec#arg_name}.
        :param arg_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#arg_value OceancdRolloutSpec#arg_value}.
        :param value_from: value_from block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#value_from OceancdRolloutSpec#value_from}
        '''
        if isinstance(value_from, dict):
            value_from = OceancdRolloutSpecStrategyArgsValueFrom(**value_from)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a48d270daa288652bb4b8d4eda1cf3d9c6d0758a38b1996cff959587610686)
            check_type(argname="argument arg_name", value=arg_name, expected_type=type_hints["arg_name"])
            check_type(argname="argument arg_value", value=arg_value, expected_type=type_hints["arg_value"])
            check_type(argname="argument value_from", value=value_from, expected_type=type_hints["value_from"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arg_name": arg_name,
        }
        if arg_value is not None:
            self._values["arg_value"] = arg_value
        if value_from is not None:
            self._values["value_from"] = value_from

    @builtins.property
    def arg_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#arg_name OceancdRolloutSpec#arg_name}.'''
        result = self._values.get("arg_name")
        assert result is not None, "Required property 'arg_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def arg_value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#arg_value OceancdRolloutSpec#arg_value}.'''
        result = self._values.get("arg_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_from(self) -> typing.Optional["OceancdRolloutSpecStrategyArgsValueFrom"]:
        '''value_from block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#value_from OceancdRolloutSpec#value_from}
        '''
        result = self._values.get("value_from")
        return typing.cast(typing.Optional["OceancdRolloutSpecStrategyArgsValueFrom"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecStrategyArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecStrategyArgsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17719d0060668600050c8683b75801918e000e594651ec33719ec705937bc06e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdRolloutSpecStrategyArgsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11ac8fa952b77ee7b0e57841c7705c86885e31f479d02d837b714b46fbbd23cf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdRolloutSpecStrategyArgsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1429fe869e50ec8ef2025c843ca4b980922eacf02ae37e21d458e023bfb3874f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__86d02c03eea40f01c0e3b8e21ad52577026b6dda892c3abf96bf097209fdb509)
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
            type_hints = typing.get_type_hints(_typecheckingstub__34d17179764d79cbf96ef30de60fd4c11d049efd996a164c4dd5654cb5f058ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecStrategyArgs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecStrategyArgs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecStrategyArgs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a5d00db4f09d5f07aa63ed65d47bff2e2e20e473e1955ec66d1989c50f105a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecStrategyArgsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c202a0780b37d72420d283d3a845ac12d95e07ba08cef82d2aea851342cfa98)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putValueFrom")
    def put_value_from(
        self,
        *,
        field_ref: typing.Union["OceancdRolloutSpecStrategyArgsValueFromFieldRef", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param field_ref: field_ref block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#field_ref OceancdRolloutSpec#field_ref}
        '''
        value = OceancdRolloutSpecStrategyArgsValueFrom(field_ref=field_ref)

        return typing.cast(None, jsii.invoke(self, "putValueFrom", [value]))

    @jsii.member(jsii_name="resetArgValue")
    def reset_arg_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArgValue", []))

    @jsii.member(jsii_name="resetValueFrom")
    def reset_value_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValueFrom", []))

    @builtins.property
    @jsii.member(jsii_name="valueFrom")
    def value_from(self) -> "OceancdRolloutSpecStrategyArgsValueFromOutputReference":
        return typing.cast("OceancdRolloutSpecStrategyArgsValueFromOutputReference", jsii.get(self, "valueFrom"))

    @builtins.property
    @jsii.member(jsii_name="argNameInput")
    def arg_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "argNameInput"))

    @builtins.property
    @jsii.member(jsii_name="argValueInput")
    def arg_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "argValueInput"))

    @builtins.property
    @jsii.member(jsii_name="valueFromInput")
    def value_from_input(
        self,
    ) -> typing.Optional["OceancdRolloutSpecStrategyArgsValueFrom"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecStrategyArgsValueFrom"], jsii.get(self, "valueFromInput"))

    @builtins.property
    @jsii.member(jsii_name="argName")
    def arg_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "argName"))

    @arg_name.setter
    def arg_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__766ce071d5bdcc5d5065c9079596c7fb5101f1bf698a329e3c8200efd2e7ad80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="argValue")
    def arg_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "argValue"))

    @arg_value.setter
    def arg_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da000953360673cfc8db0d075d2f37effa44aaf56108463a62f049cf2510b274)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecStrategyArgs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecStrategyArgs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecStrategyArgs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07b15a3b2bd6220f00ac69e859bb1b5a349381e025126b4e3f2051ab9d5f08c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgsValueFrom",
    jsii_struct_bases=[],
    name_mapping={"field_ref": "fieldRef"},
)
class OceancdRolloutSpecStrategyArgsValueFrom:
    def __init__(
        self,
        *,
        field_ref: typing.Union["OceancdRolloutSpecStrategyArgsValueFromFieldRef", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param field_ref: field_ref block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#field_ref OceancdRolloutSpec#field_ref}
        '''
        if isinstance(field_ref, dict):
            field_ref = OceancdRolloutSpecStrategyArgsValueFromFieldRef(**field_ref)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1760bbdd09f5de467676556dc83621e5e53044f1f610951a81ecb512c36ad98a)
            check_type(argname="argument field_ref", value=field_ref, expected_type=type_hints["field_ref"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "field_ref": field_ref,
        }

    @builtins.property
    def field_ref(self) -> "OceancdRolloutSpecStrategyArgsValueFromFieldRef":
        '''field_ref block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#field_ref OceancdRolloutSpec#field_ref}
        '''
        result = self._values.get("field_ref")
        assert result is not None, "Required property 'field_ref' is missing"
        return typing.cast("OceancdRolloutSpecStrategyArgsValueFromFieldRef", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecStrategyArgsValueFrom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgsValueFromFieldRef",
    jsii_struct_bases=[],
    name_mapping={"field_path": "fieldPath"},
)
class OceancdRolloutSpecStrategyArgsValueFromFieldRef:
    def __init__(self, *, field_path: builtins.str) -> None:
        '''
        :param field_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#field_path OceancdRolloutSpec#field_path}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__449a67dcbccb8445d5f448e3391ad416d7fffc8d3ce97dc491ef23906f5a02df)
            check_type(argname="argument field_path", value=field_path, expected_type=type_hints["field_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "field_path": field_path,
        }

    @builtins.property
    def field_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#field_path OceancdRolloutSpec#field_path}.'''
        result = self._values.get("field_path")
        assert result is not None, "Required property 'field_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecStrategyArgsValueFromFieldRef(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecStrategyArgsValueFromFieldRefOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgsValueFromFieldRefOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0bf0f7815933293827c0491a24a58f8a429b9ab3e46f4d8e9638b70ebcae20d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="fieldPathInput")
    def field_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldPathInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldPath")
    def field_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldPath"))

    @field_path.setter
    def field_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__989db517e1dfabd17e2dae6b0eb4edc9e8b38ec0fa95ef766545dfe47afd7106)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdRolloutSpecStrategyArgsValueFromFieldRef]:
        return typing.cast(typing.Optional[OceancdRolloutSpecStrategyArgsValueFromFieldRef], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecStrategyArgsValueFromFieldRef],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e018e79a53508e28a399703ca92ddf18e7a4363f98236f9c7f497366a2fc1645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecStrategyArgsValueFromOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyArgsValueFromOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__33bb8bd4f9f4d06b7aee1c003bb8fd7f544e7b4f369c9274360a9278746d0e0a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putFieldRef")
    def put_field_ref(self, *, field_path: builtins.str) -> None:
        '''
        :param field_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#field_path OceancdRolloutSpec#field_path}.
        '''
        value = OceancdRolloutSpecStrategyArgsValueFromFieldRef(field_path=field_path)

        return typing.cast(None, jsii.invoke(self, "putFieldRef", [value]))

    @builtins.property
    @jsii.member(jsii_name="fieldRef")
    def field_ref(
        self,
    ) -> OceancdRolloutSpecStrategyArgsValueFromFieldRefOutputReference:
        return typing.cast(OceancdRolloutSpecStrategyArgsValueFromFieldRefOutputReference, jsii.get(self, "fieldRef"))

    @builtins.property
    @jsii.member(jsii_name="fieldRefInput")
    def field_ref_input(
        self,
    ) -> typing.Optional[OceancdRolloutSpecStrategyArgsValueFromFieldRef]:
        return typing.cast(typing.Optional[OceancdRolloutSpecStrategyArgsValueFromFieldRef], jsii.get(self, "fieldRefInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdRolloutSpecStrategyArgsValueFrom]:
        return typing.cast(typing.Optional[OceancdRolloutSpecStrategyArgsValueFrom], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecStrategyArgsValueFrom],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6df25effd35713755aabc11f636e6a440b43770ae206d762fa38517f0330bf3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecStrategyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecStrategyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__feda263f25efdddb679d23746b5c20ea33ea56c38dc6e840d5eb439c1604b181)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putArgs")
    def put_args(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecStrategyArgs, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e7ed85484cf05fe0e17ab45d0a37eee0e04533de5b0be03f2acba73ec690f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putArgs", [value]))

    @jsii.member(jsii_name="resetArgs")
    def reset_args(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArgs", []))

    @builtins.property
    @jsii.member(jsii_name="args")
    def args(self) -> OceancdRolloutSpecStrategyArgsList:
        return typing.cast(OceancdRolloutSpecStrategyArgsList, jsii.get(self, "args"))

    @builtins.property
    @jsii.member(jsii_name="argsInput")
    def args_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecStrategyArgs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecStrategyArgs]]], jsii.get(self, "argsInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyNameInput")
    def strategy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strategyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyName")
    def strategy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "strategyName"))

    @strategy_name.setter
    def strategy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fafac19294054a2123d742105e4de8df42b71baab793e7f2d5a0e6cbf243f91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strategyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecStrategy]:
        return typing.cast(typing.Optional[OceancdRolloutSpecStrategy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecStrategy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1acc3dc79f97141e16ba26dccc79658dc0c6f00c952e6ccc586f7954db21f0b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTraffic",
    jsii_struct_bases=[],
    name_mapping={
        "alb": "alb",
        "ambassador": "ambassador",
        "canary_service": "canaryService",
        "istio": "istio",
        "nginx": "nginx",
        "ping_pong": "pingPong",
        "smi": "smi",
        "stable_service": "stableService",
    },
)
class OceancdRolloutSpecTraffic:
    def __init__(
        self,
        *,
        alb: typing.Optional[typing.Union["OceancdRolloutSpecTrafficAlb", typing.Dict[builtins.str, typing.Any]]] = None,
        ambassador: typing.Optional[typing.Union["OceancdRolloutSpecTrafficAmbassador", typing.Dict[builtins.str, typing.Any]]] = None,
        canary_service: typing.Optional[builtins.str] = None,
        istio: typing.Optional[typing.Union["OceancdRolloutSpecTrafficIstio", typing.Dict[builtins.str, typing.Any]]] = None,
        nginx: typing.Optional[typing.Union["OceancdRolloutSpecTrafficNginx", typing.Dict[builtins.str, typing.Any]]] = None,
        ping_pong: typing.Optional[typing.Union["OceancdRolloutSpecTrafficPingPong", typing.Dict[builtins.str, typing.Any]]] = None,
        smi: typing.Optional[typing.Union["OceancdRolloutSpecTrafficSmi", typing.Dict[builtins.str, typing.Any]]] = None,
        stable_service: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alb: alb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb OceancdRolloutSpec#alb}
        :param ambassador: ambassador block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ambassador OceancdRolloutSpec#ambassador}
        :param canary_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_service OceancdRolloutSpec#canary_service}.
        :param istio: istio block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#istio OceancdRolloutSpec#istio}
        :param nginx: nginx block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#nginx OceancdRolloutSpec#nginx}
        :param ping_pong: ping_pong block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ping_pong OceancdRolloutSpec#ping_pong}
        :param smi: smi block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#smi OceancdRolloutSpec#smi}
        :param stable_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_service OceancdRolloutSpec#stable_service}.
        '''
        if isinstance(alb, dict):
            alb = OceancdRolloutSpecTrafficAlb(**alb)
        if isinstance(ambassador, dict):
            ambassador = OceancdRolloutSpecTrafficAmbassador(**ambassador)
        if isinstance(istio, dict):
            istio = OceancdRolloutSpecTrafficIstio(**istio)
        if isinstance(nginx, dict):
            nginx = OceancdRolloutSpecTrafficNginx(**nginx)
        if isinstance(ping_pong, dict):
            ping_pong = OceancdRolloutSpecTrafficPingPong(**ping_pong)
        if isinstance(smi, dict):
            smi = OceancdRolloutSpecTrafficSmi(**smi)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b0f45768ac3e4f38995f58297f4fbf626f88137519304b8d8f4f7f95143a3b)
            check_type(argname="argument alb", value=alb, expected_type=type_hints["alb"])
            check_type(argname="argument ambassador", value=ambassador, expected_type=type_hints["ambassador"])
            check_type(argname="argument canary_service", value=canary_service, expected_type=type_hints["canary_service"])
            check_type(argname="argument istio", value=istio, expected_type=type_hints["istio"])
            check_type(argname="argument nginx", value=nginx, expected_type=type_hints["nginx"])
            check_type(argname="argument ping_pong", value=ping_pong, expected_type=type_hints["ping_pong"])
            check_type(argname="argument smi", value=smi, expected_type=type_hints["smi"])
            check_type(argname="argument stable_service", value=stable_service, expected_type=type_hints["stable_service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alb is not None:
            self._values["alb"] = alb
        if ambassador is not None:
            self._values["ambassador"] = ambassador
        if canary_service is not None:
            self._values["canary_service"] = canary_service
        if istio is not None:
            self._values["istio"] = istio
        if nginx is not None:
            self._values["nginx"] = nginx
        if ping_pong is not None:
            self._values["ping_pong"] = ping_pong
        if smi is not None:
            self._values["smi"] = smi
        if stable_service is not None:
            self._values["stable_service"] = stable_service

    @builtins.property
    def alb(self) -> typing.Optional["OceancdRolloutSpecTrafficAlb"]:
        '''alb block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb OceancdRolloutSpec#alb}
        '''
        result = self._values.get("alb")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficAlb"], result)

    @builtins.property
    def ambassador(self) -> typing.Optional["OceancdRolloutSpecTrafficAmbassador"]:
        '''ambassador block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ambassador OceancdRolloutSpec#ambassador}
        '''
        result = self._values.get("ambassador")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficAmbassador"], result)

    @builtins.property
    def canary_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_service OceancdRolloutSpec#canary_service}.'''
        result = self._values.get("canary_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def istio(self) -> typing.Optional["OceancdRolloutSpecTrafficIstio"]:
        '''istio block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#istio OceancdRolloutSpec#istio}
        '''
        result = self._values.get("istio")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficIstio"], result)

    @builtins.property
    def nginx(self) -> typing.Optional["OceancdRolloutSpecTrafficNginx"]:
        '''nginx block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#nginx OceancdRolloutSpec#nginx}
        '''
        result = self._values.get("nginx")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficNginx"], result)

    @builtins.property
    def ping_pong(self) -> typing.Optional["OceancdRolloutSpecTrafficPingPong"]:
        '''ping_pong block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ping_pong OceancdRolloutSpec#ping_pong}
        '''
        result = self._values.get("ping_pong")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficPingPong"], result)

    @builtins.property
    def smi(self) -> typing.Optional["OceancdRolloutSpecTrafficSmi"]:
        '''smi block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#smi OceancdRolloutSpec#smi}
        '''
        result = self._values.get("smi")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficSmi"], result)

    @builtins.property
    def stable_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_service OceancdRolloutSpec#stable_service}.'''
        result = self._values.get("stable_service")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTraffic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficAlb",
    jsii_struct_bases=[],
    name_mapping={
        "alb_ingress": "albIngress",
        "alb_root_service": "albRootService",
        "service_port": "servicePort",
        "alb_annotation_prefix": "albAnnotationPrefix",
        "stickiness_config": "stickinessConfig",
    },
)
class OceancdRolloutSpecTrafficAlb:
    def __init__(
        self,
        *,
        alb_ingress: builtins.str,
        alb_root_service: builtins.str,
        service_port: jsii.Number,
        alb_annotation_prefix: typing.Optional[builtins.str] = None,
        stickiness_config: typing.Optional[typing.Union["OceancdRolloutSpecTrafficAlbStickinessConfig", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param alb_ingress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_ingress OceancdRolloutSpec#alb_ingress}.
        :param alb_root_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_root_service OceancdRolloutSpec#alb_root_service}.
        :param service_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#service_port OceancdRolloutSpec#service_port}.
        :param alb_annotation_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_annotation_prefix OceancdRolloutSpec#alb_annotation_prefix}.
        :param stickiness_config: stickiness_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stickiness_config OceancdRolloutSpec#stickiness_config}
        '''
        if isinstance(stickiness_config, dict):
            stickiness_config = OceancdRolloutSpecTrafficAlbStickinessConfig(**stickiness_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda4d5acd78aa78c9b80ae32198914b31003468d010c85703b96213777070b65)
            check_type(argname="argument alb_ingress", value=alb_ingress, expected_type=type_hints["alb_ingress"])
            check_type(argname="argument alb_root_service", value=alb_root_service, expected_type=type_hints["alb_root_service"])
            check_type(argname="argument service_port", value=service_port, expected_type=type_hints["service_port"])
            check_type(argname="argument alb_annotation_prefix", value=alb_annotation_prefix, expected_type=type_hints["alb_annotation_prefix"])
            check_type(argname="argument stickiness_config", value=stickiness_config, expected_type=type_hints["stickiness_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alb_ingress": alb_ingress,
            "alb_root_service": alb_root_service,
            "service_port": service_port,
        }
        if alb_annotation_prefix is not None:
            self._values["alb_annotation_prefix"] = alb_annotation_prefix
        if stickiness_config is not None:
            self._values["stickiness_config"] = stickiness_config

    @builtins.property
    def alb_ingress(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_ingress OceancdRolloutSpec#alb_ingress}.'''
        result = self._values.get("alb_ingress")
        assert result is not None, "Required property 'alb_ingress' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alb_root_service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_root_service OceancdRolloutSpec#alb_root_service}.'''
        result = self._values.get("alb_root_service")
        assert result is not None, "Required property 'alb_root_service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#service_port OceancdRolloutSpec#service_port}.'''
        result = self._values.get("service_port")
        assert result is not None, "Required property 'service_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def alb_annotation_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_annotation_prefix OceancdRolloutSpec#alb_annotation_prefix}.'''
        result = self._values.get("alb_annotation_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stickiness_config(
        self,
    ) -> typing.Optional["OceancdRolloutSpecTrafficAlbStickinessConfig"]:
        '''stickiness_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stickiness_config OceancdRolloutSpec#stickiness_config}
        '''
        result = self._values.get("stickiness_config")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficAlbStickinessConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficAlb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficAlbOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficAlbOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4f13b9029aeaff4958408023aabd73ce378547240451719d4cd1ffdeba9bb11)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putStickinessConfig")
    def put_stickiness_config(
        self,
        *,
        duration_seconds: typing.Optional[jsii.Number] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param duration_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#duration_seconds OceancdRolloutSpec#duration_seconds}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#enabled OceancdRolloutSpec#enabled}.
        '''
        value = OceancdRolloutSpecTrafficAlbStickinessConfig(
            duration_seconds=duration_seconds, enabled=enabled
        )

        return typing.cast(None, jsii.invoke(self, "putStickinessConfig", [value]))

    @jsii.member(jsii_name="resetAlbAnnotationPrefix")
    def reset_alb_annotation_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlbAnnotationPrefix", []))

    @jsii.member(jsii_name="resetStickinessConfig")
    def reset_stickiness_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStickinessConfig", []))

    @builtins.property
    @jsii.member(jsii_name="stickinessConfig")
    def stickiness_config(
        self,
    ) -> "OceancdRolloutSpecTrafficAlbStickinessConfigOutputReference":
        return typing.cast("OceancdRolloutSpecTrafficAlbStickinessConfigOutputReference", jsii.get(self, "stickinessConfig"))

    @builtins.property
    @jsii.member(jsii_name="albAnnotationPrefixInput")
    def alb_annotation_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "albAnnotationPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="albIngressInput")
    def alb_ingress_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "albIngressInput"))

    @builtins.property
    @jsii.member(jsii_name="albRootServiceInput")
    def alb_root_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "albRootServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="servicePortInput")
    def service_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "servicePortInput"))

    @builtins.property
    @jsii.member(jsii_name="stickinessConfigInput")
    def stickiness_config_input(
        self,
    ) -> typing.Optional["OceancdRolloutSpecTrafficAlbStickinessConfig"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficAlbStickinessConfig"], jsii.get(self, "stickinessConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="albAnnotationPrefix")
    def alb_annotation_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "albAnnotationPrefix"))

    @alb_annotation_prefix.setter
    def alb_annotation_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__858cfb1ef16ef528650e97f33f3738d0e461bc98516c6987e1634b69e4ac87d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "albAnnotationPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="albIngress")
    def alb_ingress(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "albIngress"))

    @alb_ingress.setter
    def alb_ingress(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9deda4a0d79f65610300c6abf0abe92c635f3df4350dc52a68154035d4f3ce9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "albIngress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="albRootService")
    def alb_root_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "albRootService"))

    @alb_root_service.setter
    def alb_root_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddd2f2ca84358ae91f7dca202c8ed1420c45fc3f2e2dd1520e49037543a89316)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "albRootService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="servicePort")
    def service_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "servicePort"))

    @service_port.setter
    def service_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39b3ac9910d75fed042f7bc40010d0a983ae03eba42a17beb7c8401f38a685df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTrafficAlb]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficAlb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficAlb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67a2641a6108a2fdb8e63a6c7732ea369e513049572274a75d97f46cf0f17639)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficAlbStickinessConfig",
    jsii_struct_bases=[],
    name_mapping={"duration_seconds": "durationSeconds", "enabled": "enabled"},
)
class OceancdRolloutSpecTrafficAlbStickinessConfig:
    def __init__(
        self,
        *,
        duration_seconds: typing.Optional[jsii.Number] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param duration_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#duration_seconds OceancdRolloutSpec#duration_seconds}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#enabled OceancdRolloutSpec#enabled}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a56d9147816f2afbc300642c7a17bcaa5ba2fd9062faf90418c6f18a82a13fb)
            check_type(argname="argument duration_seconds", value=duration_seconds, expected_type=type_hints["duration_seconds"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if duration_seconds is not None:
            self._values["duration_seconds"] = duration_seconds
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#duration_seconds OceancdRolloutSpec#duration_seconds}.'''
        result = self._values.get("duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#enabled OceancdRolloutSpec#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficAlbStickinessConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficAlbStickinessConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficAlbStickinessConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ad17974493496994664699df4e20f7530f0205aa4b2c75cb710c69033386fe3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDurationSeconds")
    def reset_duration_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDurationSeconds", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="durationSecondsInput")
    def duration_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "durationSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="durationSeconds")
    def duration_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "durationSeconds"))

    @duration_seconds.setter
    def duration_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__390ccab6ecf5970f1af62c042067afae63c294a36eeca4d1269fe9626fa47ec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "durationSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d99db8f50fcb1833a4b7cd95826e41004dfaa8ce037387dceb4b87f7fc1da139)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdRolloutSpecTrafficAlbStickinessConfig]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficAlbStickinessConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficAlbStickinessConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d62294a5690dd48e119559ea0110b0f314cf583570f91605ba7970b8f0e25041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficAmbassador",
    jsii_struct_bases=[],
    name_mapping={"mappings": "mappings"},
)
class OceancdRolloutSpecTrafficAmbassador:
    def __init__(self, *, mappings: typing.Sequence[builtins.str]) -> None:
        '''
        :param mappings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#mappings OceancdRolloutSpec#mappings}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c634daf27cca9fb1989960b0798a9808eb41648d5c442598db5fc65e97f8959d)
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mappings": mappings,
        }

    @builtins.property
    def mappings(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#mappings OceancdRolloutSpec#mappings}.'''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficAmbassador(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficAmbassadorOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficAmbassadorOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4c5175c7ca80df4fcd27b0a8b95361c30e89e6642f0ba2d28d1cd3330f129d76)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="mappingsInput")
    def mappings_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mappingsInput"))

    @builtins.property
    @jsii.member(jsii_name="mappings")
    def mappings(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mappings"))

    @mappings.setter
    def mappings(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4970986ec3c213f14ba4897da73b9855bad90b2644cb80b8bc03560ca3dc5f8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mappings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTrafficAmbassador]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficAmbassador], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficAmbassador],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa56ed9b3c47e26ecdfbad60597eb446d0c340608f479778f86ce7837d09cb5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstio",
    jsii_struct_bases=[],
    name_mapping={
        "virtual_services": "virtualServices",
        "destination_rule": "destinationRule",
    },
)
class OceancdRolloutSpecTrafficIstio:
    def __init__(
        self,
        *,
        virtual_services: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecTrafficIstioVirtualServices", typing.Dict[builtins.str, typing.Any]]]],
        destination_rule: typing.Optional[typing.Union["OceancdRolloutSpecTrafficIstioDestinationRule", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param virtual_services: virtual_services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_services OceancdRolloutSpec#virtual_services}
        :param destination_rule: destination_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#destination_rule OceancdRolloutSpec#destination_rule}
        '''
        if isinstance(destination_rule, dict):
            destination_rule = OceancdRolloutSpecTrafficIstioDestinationRule(**destination_rule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a2f357fac037f11b3790e328269f08b6d00c0694e765c1c5ba5b27840f1712)
            check_type(argname="argument virtual_services", value=virtual_services, expected_type=type_hints["virtual_services"])
            check_type(argname="argument destination_rule", value=destination_rule, expected_type=type_hints["destination_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "virtual_services": virtual_services,
        }
        if destination_rule is not None:
            self._values["destination_rule"] = destination_rule

    @builtins.property
    def virtual_services(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServices"]]:
        '''virtual_services block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_services OceancdRolloutSpec#virtual_services}
        '''
        result = self._values.get("virtual_services")
        assert result is not None, "Required property 'virtual_services' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServices"]], result)

    @builtins.property
    def destination_rule(
        self,
    ) -> typing.Optional["OceancdRolloutSpecTrafficIstioDestinationRule"]:
        '''destination_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#destination_rule OceancdRolloutSpec#destination_rule}
        '''
        result = self._values.get("destination_rule")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficIstioDestinationRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficIstio(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioDestinationRule",
    jsii_struct_bases=[],
    name_mapping={
        "canary_subset_name": "canarySubsetName",
        "destination_rule_name": "destinationRuleName",
        "stable_subset_name": "stableSubsetName",
    },
)
class OceancdRolloutSpecTrafficIstioDestinationRule:
    def __init__(
        self,
        *,
        canary_subset_name: builtins.str,
        destination_rule_name: builtins.str,
        stable_subset_name: builtins.str,
    ) -> None:
        '''
        :param canary_subset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_subset_name OceancdRolloutSpec#canary_subset_name}.
        :param destination_rule_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#destination_rule_name OceancdRolloutSpec#destination_rule_name}.
        :param stable_subset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_subset_name OceancdRolloutSpec#stable_subset_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e96dbe56fb984e9a4fcd071245a7c45fcfb166963c18688aca4fb777ba4ae96)
            check_type(argname="argument canary_subset_name", value=canary_subset_name, expected_type=type_hints["canary_subset_name"])
            check_type(argname="argument destination_rule_name", value=destination_rule_name, expected_type=type_hints["destination_rule_name"])
            check_type(argname="argument stable_subset_name", value=stable_subset_name, expected_type=type_hints["stable_subset_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "canary_subset_name": canary_subset_name,
            "destination_rule_name": destination_rule_name,
            "stable_subset_name": stable_subset_name,
        }

    @builtins.property
    def canary_subset_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_subset_name OceancdRolloutSpec#canary_subset_name}.'''
        result = self._values.get("canary_subset_name")
        assert result is not None, "Required property 'canary_subset_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination_rule_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#destination_rule_name OceancdRolloutSpec#destination_rule_name}.'''
        result = self._values.get("destination_rule_name")
        assert result is not None, "Required property 'destination_rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stable_subset_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_subset_name OceancdRolloutSpec#stable_subset_name}.'''
        result = self._values.get("stable_subset_name")
        assert result is not None, "Required property 'stable_subset_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficIstioDestinationRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficIstioDestinationRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioDestinationRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d404932e23c32112b8e1d377eca7636e35e96245db9d0f33b512b9a23a9ee593)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="canarySubsetNameInput")
    def canary_subset_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "canarySubsetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="destinationRuleNameInput")
    def destination_rule_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationRuleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="stableSubsetNameInput")
    def stable_subset_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stableSubsetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="canarySubsetName")
    def canary_subset_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "canarySubsetName"))

    @canary_subset_name.setter
    def canary_subset_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e646b6676ff3132c590a5429e94fdcf9623f7ea0f0f020a7bd37094d5093b1e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "canarySubsetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationRuleName")
    def destination_rule_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationRuleName"))

    @destination_rule_name.setter
    def destination_rule_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e4bb741ae681e6677ee2aea63cd5e387ddf4cea4c0b9d0a45b841b2dfedc079)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationRuleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stableSubsetName")
    def stable_subset_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stableSubsetName"))

    @stable_subset_name.setter
    def stable_subset_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc7e2f7327be36705aad8b8f11ded4ef6041ca35606e8935939882d7d236a7f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stableSubsetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdRolloutSpecTrafficIstioDestinationRule]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficIstioDestinationRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficIstioDestinationRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75de815ca1b8dd38425765aa93f42c67e2afa35a6b86033d9742629b1d524c6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecTrafficIstioOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__27d9e06b35261a5c022258dca09db8a560f7b0157e8047c54ccefbea65329528)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDestinationRule")
    def put_destination_rule(
        self,
        *,
        canary_subset_name: builtins.str,
        destination_rule_name: builtins.str,
        stable_subset_name: builtins.str,
    ) -> None:
        '''
        :param canary_subset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_subset_name OceancdRolloutSpec#canary_subset_name}.
        :param destination_rule_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#destination_rule_name OceancdRolloutSpec#destination_rule_name}.
        :param stable_subset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_subset_name OceancdRolloutSpec#stable_subset_name}.
        '''
        value = OceancdRolloutSpecTrafficIstioDestinationRule(
            canary_subset_name=canary_subset_name,
            destination_rule_name=destination_rule_name,
            stable_subset_name=stable_subset_name,
        )

        return typing.cast(None, jsii.invoke(self, "putDestinationRule", [value]))

    @jsii.member(jsii_name="putVirtualServices")
    def put_virtual_services(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecTrafficIstioVirtualServices", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ad6f0c7d9e6308f64ae7089591e34b2e993f1626a73b15c6e6f415b5b7e1f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVirtualServices", [value]))

    @jsii.member(jsii_name="resetDestinationRule")
    def reset_destination_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationRule", []))

    @builtins.property
    @jsii.member(jsii_name="destinationRule")
    def destination_rule(
        self,
    ) -> OceancdRolloutSpecTrafficIstioDestinationRuleOutputReference:
        return typing.cast(OceancdRolloutSpecTrafficIstioDestinationRuleOutputReference, jsii.get(self, "destinationRule"))

    @builtins.property
    @jsii.member(jsii_name="virtualServices")
    def virtual_services(self) -> "OceancdRolloutSpecTrafficIstioVirtualServicesList":
        return typing.cast("OceancdRolloutSpecTrafficIstioVirtualServicesList", jsii.get(self, "virtualServices"))

    @builtins.property
    @jsii.member(jsii_name="destinationRuleInput")
    def destination_rule_input(
        self,
    ) -> typing.Optional[OceancdRolloutSpecTrafficIstioDestinationRule]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficIstioDestinationRule], jsii.get(self, "destinationRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualServicesInput")
    def virtual_services_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServices"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServices"]]], jsii.get(self, "virtualServicesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTrafficIstio]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficIstio], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficIstio],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16c7a6641e3874727ac5b2384f38a0035b2097764639ae63ec172bb4865067a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioVirtualServices",
    jsii_struct_bases=[],
    name_mapping={
        "virtual_service_name": "virtualServiceName",
        "tls_routes": "tlsRoutes",
        "virtual_service_routes": "virtualServiceRoutes",
    },
)
class OceancdRolloutSpecTrafficIstioVirtualServices:
    def __init__(
        self,
        *,
        virtual_service_name: builtins.str,
        tls_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes", typing.Dict[builtins.str, typing.Any]]]]] = None,
        virtual_service_routes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param virtual_service_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_service_name OceancdRolloutSpec#virtual_service_name}.
        :param tls_routes: tls_routes block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#tls_routes OceancdRolloutSpec#tls_routes}
        :param virtual_service_routes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_service_routes OceancdRolloutSpec#virtual_service_routes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f01a692edfb29b413230f57f938794a3f64332d641038df74150a658f47d2546)
            check_type(argname="argument virtual_service_name", value=virtual_service_name, expected_type=type_hints["virtual_service_name"])
            check_type(argname="argument tls_routes", value=tls_routes, expected_type=type_hints["tls_routes"])
            check_type(argname="argument virtual_service_routes", value=virtual_service_routes, expected_type=type_hints["virtual_service_routes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "virtual_service_name": virtual_service_name,
        }
        if tls_routes is not None:
            self._values["tls_routes"] = tls_routes
        if virtual_service_routes is not None:
            self._values["virtual_service_routes"] = virtual_service_routes

    @builtins.property
    def virtual_service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_service_name OceancdRolloutSpec#virtual_service_name}.'''
        result = self._values.get("virtual_service_name")
        assert result is not None, "Required property 'virtual_service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tls_routes(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes"]]]:
        '''tls_routes block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#tls_routes OceancdRolloutSpec#tls_routes}
        '''
        result = self._values.get("tls_routes")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes"]]], result)

    @builtins.property
    def virtual_service_routes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_service_routes OceancdRolloutSpec#virtual_service_routes}.'''
        result = self._values.get("virtual_service_routes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficIstioVirtualServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficIstioVirtualServicesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioVirtualServicesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c78ed83abb396e7dcecdf621a13db718fec2cf43a86716af3cc8bb5464a0667)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdRolloutSpecTrafficIstioVirtualServicesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__531eb100455cc113437d7dfdb70cfc487478ecc25a54ead7586322b7b31b4b52)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdRolloutSpecTrafficIstioVirtualServicesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f75b506994b6e46a164d2b9a2200d4ac1aa25b352b34619ddac0d183c2317cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3a92a1835500958413302e0cd637a90d8f5b986470e7e29ccd041d67130e7a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cbbb99b30cd8a661f0852050edff026243fedfa061b76a5db1472eb2b339a4a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServices]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServices]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServices]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2091aaba3cabec8325a73ba72550b07b95281818f486b4025bdea7f0ec6c2188)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecTrafficIstioVirtualServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioVirtualServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__92d176e56ba5ff70d447a6f3a6605bcf2c46edc0f00fca2bf45852b6a8db0bd3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTlsRoutes")
    def put_tls_routes(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ed428a8987944572560cada554418e8f2af3421974e4c0ae7eac34f6fce72d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTlsRoutes", [value]))

    @jsii.member(jsii_name="resetTlsRoutes")
    def reset_tls_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsRoutes", []))

    @jsii.member(jsii_name="resetVirtualServiceRoutes")
    def reset_virtual_service_routes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualServiceRoutes", []))

    @builtins.property
    @jsii.member(jsii_name="tlsRoutes")
    def tls_routes(
        self,
    ) -> "OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesList":
        return typing.cast("OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesList", jsii.get(self, "tlsRoutes"))

    @builtins.property
    @jsii.member(jsii_name="tlsRoutesInput")
    def tls_routes_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes"]]], jsii.get(self, "tlsRoutesInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualServiceNameInput")
    def virtual_service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualServiceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualServiceRoutesInput")
    def virtual_service_routes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "virtualServiceRoutesInput"))

    @builtins.property
    @jsii.member(jsii_name="virtualServiceName")
    def virtual_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualServiceName"))

    @virtual_service_name.setter
    def virtual_service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad5d2b8e5302c03a4d52f09f4ba0b5edb391d22649c15b54ebddb880f74b3cb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualServiceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="virtualServiceRoutes")
    def virtual_service_routes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "virtualServiceRoutes"))

    @virtual_service_routes.setter
    def virtual_service_routes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3eebb8b1472dd81a47e7bab95562651d60d8066bcb78c0f5b2e4a72bdb8842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "virtualServiceRoutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServices]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServices]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServices]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee5ad2a3073570e71587422943f0ba683d2ea4d18268900810cb7a5a0aff9804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes",
    jsii_struct_bases=[],
    name_mapping={"port": "port", "sni_hosts": "sniHosts"},
)
class OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes:
    def __init__(
        self,
        *,
        port: typing.Optional[jsii.Number] = None,
        sni_hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#port OceancdRolloutSpec#port}.
        :param sni_hosts: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#sni_hosts OceancdRolloutSpec#sni_hosts}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__545ee260f441d3582aeaa11035f2168e8da049d6afd54a7d79a31cb88c102484)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument sni_hosts", value=sni_hosts, expected_type=type_hints["sni_hosts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if port is not None:
            self._values["port"] = port
        if sni_hosts is not None:
            self._values["sni_hosts"] = sni_hosts

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#port OceancdRolloutSpec#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sni_hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#sni_hosts OceancdRolloutSpec#sni_hosts}.'''
        result = self._values.get("sni_hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1d9badd1db16e999483527dd645af09cf460892aef0314d34af7632830b98a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bfa6a62a84229fee55a5cfceda9ed6d647d2e9442387fea01cf16f7c851f8d9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb7410324f564c2d78c86dd6c491236744394d4c9cda6b42143e63764644c5a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__81fb6126eca9c32372212b3d86538941bb7561f4167b641b4160651b567910ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab27d4d4dc459af4ca69170fc5f6fe22f6528d2ef1eeb5d19cec59370ed69fda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd604426c35b5d8a5c053b3d6848bd2318fbd3da7d0fa9d7e78032b5bf17b41f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcb73038ab400ae55b64aeb76cd202636c1cd7bdd2baf1937acbd42260d9b281)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSniHosts")
    def reset_sni_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSniHosts", []))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="sniHostsInput")
    def sni_hosts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sniHostsInput"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8336c2ad4a5d59e0bf4f0c0b76f0ce6b8d167a2bf8b6143ae5956469154a4ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sniHosts")
    def sni_hosts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sniHosts"))

    @sni_hosts.setter
    def sni_hosts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9016ca9c86c4ff574c7be45100b9a095cdbe4a32b2387f6e51a1e4b3dd7f1d85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sniHosts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c2e6c386252a8dbd8ba6f244a6cf80d8040287997dc2efa524381cc2d683f24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficNginx",
    jsii_struct_bases=[],
    name_mapping={
        "stable_ingress": "stableIngress",
        "additional_ingress_annotation": "additionalIngressAnnotation",
        "nginx_annotation_prefix": "nginxAnnotationPrefix",
    },
)
class OceancdRolloutSpecTrafficNginx:
    def __init__(
        self,
        *,
        stable_ingress: builtins.str,
        additional_ingress_annotation: typing.Optional[typing.Union["OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation", typing.Dict[builtins.str, typing.Any]]] = None,
        nginx_annotation_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param stable_ingress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_ingress OceancdRolloutSpec#stable_ingress}.
        :param additional_ingress_annotation: additional_ingress_annotation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#additional_ingress_annotation OceancdRolloutSpec#additional_ingress_annotation}
        :param nginx_annotation_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#nginx_annotation_prefix OceancdRolloutSpec#nginx_annotation_prefix}.
        '''
        if isinstance(additional_ingress_annotation, dict):
            additional_ingress_annotation = OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation(**additional_ingress_annotation)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__585c05b0b38812255e44ef4bbd2f7f5e1275da6476fc1a38f080be859311338d)
            check_type(argname="argument stable_ingress", value=stable_ingress, expected_type=type_hints["stable_ingress"])
            check_type(argname="argument additional_ingress_annotation", value=additional_ingress_annotation, expected_type=type_hints["additional_ingress_annotation"])
            check_type(argname="argument nginx_annotation_prefix", value=nginx_annotation_prefix, expected_type=type_hints["nginx_annotation_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "stable_ingress": stable_ingress,
        }
        if additional_ingress_annotation is not None:
            self._values["additional_ingress_annotation"] = additional_ingress_annotation
        if nginx_annotation_prefix is not None:
            self._values["nginx_annotation_prefix"] = nginx_annotation_prefix

    @builtins.property
    def stable_ingress(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_ingress OceancdRolloutSpec#stable_ingress}.'''
        result = self._values.get("stable_ingress")
        assert result is not None, "Required property 'stable_ingress' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_ingress_annotation(
        self,
    ) -> typing.Optional["OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation"]:
        '''additional_ingress_annotation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#additional_ingress_annotation OceancdRolloutSpec#additional_ingress_annotation}
        '''
        result = self._values.get("additional_ingress_annotation")
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation"], result)

    @builtins.property
    def nginx_annotation_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#nginx_annotation_prefix OceancdRolloutSpec#nginx_annotation_prefix}.'''
        result = self._values.get("nginx_annotation_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficNginx(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation",
    jsii_struct_bases=[],
    name_mapping={"canary_by_header": "canaryByHeader", "key1": "key1"},
)
class OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation:
    def __init__(
        self,
        *,
        canary_by_header: typing.Optional[builtins.str] = None,
        key1: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param canary_by_header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_by_header OceancdRolloutSpec#canary_by_header}.
        :param key1: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#key1 OceancdRolloutSpec#key1}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cce9459f93eeb8d6886222d0b081a04e84579bf339cf5b9a7240160e405a2e2c)
            check_type(argname="argument canary_by_header", value=canary_by_header, expected_type=type_hints["canary_by_header"])
            check_type(argname="argument key1", value=key1, expected_type=type_hints["key1"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if canary_by_header is not None:
            self._values["canary_by_header"] = canary_by_header
        if key1 is not None:
            self._values["key1"] = key1

    @builtins.property
    def canary_by_header(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_by_header OceancdRolloutSpec#canary_by_header}.'''
        result = self._values.get("canary_by_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key1(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#key1 OceancdRolloutSpec#key1}.'''
        result = self._values.get("key1")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abfbf8c80d33c0c3c4bd53e17894cc362bda92628139828b905009d911f7d084)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCanaryByHeader")
    def reset_canary_by_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCanaryByHeader", []))

    @jsii.member(jsii_name="resetKey1")
    def reset_key1(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey1", []))

    @builtins.property
    @jsii.member(jsii_name="canaryByHeaderInput")
    def canary_by_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "canaryByHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="key1Input")
    def key1_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "key1Input"))

    @builtins.property
    @jsii.member(jsii_name="canaryByHeader")
    def canary_by_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "canaryByHeader"))

    @canary_by_header.setter
    def canary_by_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cab361f1c2a8edeb920f7536e4c61a9ff7a081efb2f0b0b7120eca98d1b85bb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "canaryByHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key1")
    def key1(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key1"))

    @key1.setter
    def key1(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b26330b208d08f952b102dc82fc8664aaa65ff4a9786fb3910ca27e62fddeef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key1", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfe0835bb2ef46c7fb251eef08851b46cd13f7f41640e092b6b352c6960238e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecTrafficNginxOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficNginxOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__37a1a5876c2cdba05d4cd2e6c8d3dff1d0fd5d39e2b37de8c1ccc8eba755a312)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAdditionalIngressAnnotation")
    def put_additional_ingress_annotation(
        self,
        *,
        canary_by_header: typing.Optional[builtins.str] = None,
        key1: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param canary_by_header: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#canary_by_header OceancdRolloutSpec#canary_by_header}.
        :param key1: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#key1 OceancdRolloutSpec#key1}.
        '''
        value = OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation(
            canary_by_header=canary_by_header, key1=key1
        )

        return typing.cast(None, jsii.invoke(self, "putAdditionalIngressAnnotation", [value]))

    @jsii.member(jsii_name="resetAdditionalIngressAnnotation")
    def reset_additional_ingress_annotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalIngressAnnotation", []))

    @jsii.member(jsii_name="resetNginxAnnotationPrefix")
    def reset_nginx_annotation_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNginxAnnotationPrefix", []))

    @builtins.property
    @jsii.member(jsii_name="additionalIngressAnnotation")
    def additional_ingress_annotation(
        self,
    ) -> OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotationOutputReference:
        return typing.cast(OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotationOutputReference, jsii.get(self, "additionalIngressAnnotation"))

    @builtins.property
    @jsii.member(jsii_name="additionalIngressAnnotationInput")
    def additional_ingress_annotation_input(
        self,
    ) -> typing.Optional[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation], jsii.get(self, "additionalIngressAnnotationInput"))

    @builtins.property
    @jsii.member(jsii_name="nginxAnnotationPrefixInput")
    def nginx_annotation_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nginxAnnotationPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="stableIngressInput")
    def stable_ingress_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stableIngressInput"))

    @builtins.property
    @jsii.member(jsii_name="nginxAnnotationPrefix")
    def nginx_annotation_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nginxAnnotationPrefix"))

    @nginx_annotation_prefix.setter
    def nginx_annotation_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56581b86ab4c2bea02ec534c7fc5ac1e10c95ccff7e93748ab7743731b606c55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nginxAnnotationPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stableIngress")
    def stable_ingress(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stableIngress"))

    @stable_ingress.setter
    def stable_ingress(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82cc4bb79e63a0d55ca0e399137808aedbce1fb5d329f90574d1673abcefe66d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stableIngress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTrafficNginx]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficNginx], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficNginx],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1975d8dd3b48425aa39cbd0a1c7a97b1bfd375051a2189fc2264ff3ed4f0562c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdRolloutSpecTrafficOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d23832f9015fb7e505e5dc00284ba788f8512a0b7129380625c3b772a603f1c4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAlb")
    def put_alb(
        self,
        *,
        alb_ingress: builtins.str,
        alb_root_service: builtins.str,
        service_port: jsii.Number,
        alb_annotation_prefix: typing.Optional[builtins.str] = None,
        stickiness_config: typing.Optional[typing.Union[OceancdRolloutSpecTrafficAlbStickinessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param alb_ingress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_ingress OceancdRolloutSpec#alb_ingress}.
        :param alb_root_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_root_service OceancdRolloutSpec#alb_root_service}.
        :param service_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#service_port OceancdRolloutSpec#service_port}.
        :param alb_annotation_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#alb_annotation_prefix OceancdRolloutSpec#alb_annotation_prefix}.
        :param stickiness_config: stickiness_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stickiness_config OceancdRolloutSpec#stickiness_config}
        '''
        value = OceancdRolloutSpecTrafficAlb(
            alb_ingress=alb_ingress,
            alb_root_service=alb_root_service,
            service_port=service_port,
            alb_annotation_prefix=alb_annotation_prefix,
            stickiness_config=stickiness_config,
        )

        return typing.cast(None, jsii.invoke(self, "putAlb", [value]))

    @jsii.member(jsii_name="putAmbassador")
    def put_ambassador(self, *, mappings: typing.Sequence[builtins.str]) -> None:
        '''
        :param mappings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#mappings OceancdRolloutSpec#mappings}.
        '''
        value = OceancdRolloutSpecTrafficAmbassador(mappings=mappings)

        return typing.cast(None, jsii.invoke(self, "putAmbassador", [value]))

    @jsii.member(jsii_name="putIstio")
    def put_istio(
        self,
        *,
        virtual_services: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecTrafficIstioVirtualServices, typing.Dict[builtins.str, typing.Any]]]],
        destination_rule: typing.Optional[typing.Union[OceancdRolloutSpecTrafficIstioDestinationRule, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param virtual_services: virtual_services block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#virtual_services OceancdRolloutSpec#virtual_services}
        :param destination_rule: destination_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#destination_rule OceancdRolloutSpec#destination_rule}
        '''
        value = OceancdRolloutSpecTrafficIstio(
            virtual_services=virtual_services, destination_rule=destination_rule
        )

        return typing.cast(None, jsii.invoke(self, "putIstio", [value]))

    @jsii.member(jsii_name="putNginx")
    def put_nginx(
        self,
        *,
        stable_ingress: builtins.str,
        additional_ingress_annotation: typing.Optional[typing.Union[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation, typing.Dict[builtins.str, typing.Any]]] = None,
        nginx_annotation_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param stable_ingress: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#stable_ingress OceancdRolloutSpec#stable_ingress}.
        :param additional_ingress_annotation: additional_ingress_annotation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#additional_ingress_annotation OceancdRolloutSpec#additional_ingress_annotation}
        :param nginx_annotation_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#nginx_annotation_prefix OceancdRolloutSpec#nginx_annotation_prefix}.
        '''
        value = OceancdRolloutSpecTrafficNginx(
            stable_ingress=stable_ingress,
            additional_ingress_annotation=additional_ingress_annotation,
            nginx_annotation_prefix=nginx_annotation_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putNginx", [value]))

    @jsii.member(jsii_name="putPingPong")
    def put_ping_pong(
        self,
        *,
        ping_service: builtins.str,
        pong_service: builtins.str,
    ) -> None:
        '''
        :param ping_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ping_service OceancdRolloutSpec#ping_service}.
        :param pong_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#pong_service OceancdRolloutSpec#pong_service}.
        '''
        value = OceancdRolloutSpecTrafficPingPong(
            ping_service=ping_service, pong_service=pong_service
        )

        return typing.cast(None, jsii.invoke(self, "putPingPong", [value]))

    @jsii.member(jsii_name="putSmi")
    def put_smi(
        self,
        *,
        smi_root_service: typing.Optional[builtins.str] = None,
        traffic_split_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param smi_root_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#smi_root_service OceancdRolloutSpec#smi_root_service}.
        :param traffic_split_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#traffic_split_name OceancdRolloutSpec#traffic_split_name}.
        '''
        value = OceancdRolloutSpecTrafficSmi(
            smi_root_service=smi_root_service, traffic_split_name=traffic_split_name
        )

        return typing.cast(None, jsii.invoke(self, "putSmi", [value]))

    @jsii.member(jsii_name="resetAlb")
    def reset_alb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlb", []))

    @jsii.member(jsii_name="resetAmbassador")
    def reset_ambassador(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmbassador", []))

    @jsii.member(jsii_name="resetCanaryService")
    def reset_canary_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCanaryService", []))

    @jsii.member(jsii_name="resetIstio")
    def reset_istio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIstio", []))

    @jsii.member(jsii_name="resetNginx")
    def reset_nginx(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNginx", []))

    @jsii.member(jsii_name="resetPingPong")
    def reset_ping_pong(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPingPong", []))

    @jsii.member(jsii_name="resetSmi")
    def reset_smi(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmi", []))

    @jsii.member(jsii_name="resetStableService")
    def reset_stable_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStableService", []))

    @builtins.property
    @jsii.member(jsii_name="alb")
    def alb(self) -> OceancdRolloutSpecTrafficAlbOutputReference:
        return typing.cast(OceancdRolloutSpecTrafficAlbOutputReference, jsii.get(self, "alb"))

    @builtins.property
    @jsii.member(jsii_name="ambassador")
    def ambassador(self) -> OceancdRolloutSpecTrafficAmbassadorOutputReference:
        return typing.cast(OceancdRolloutSpecTrafficAmbassadorOutputReference, jsii.get(self, "ambassador"))

    @builtins.property
    @jsii.member(jsii_name="istio")
    def istio(self) -> OceancdRolloutSpecTrafficIstioOutputReference:
        return typing.cast(OceancdRolloutSpecTrafficIstioOutputReference, jsii.get(self, "istio"))

    @builtins.property
    @jsii.member(jsii_name="nginx")
    def nginx(self) -> OceancdRolloutSpecTrafficNginxOutputReference:
        return typing.cast(OceancdRolloutSpecTrafficNginxOutputReference, jsii.get(self, "nginx"))

    @builtins.property
    @jsii.member(jsii_name="pingPong")
    def ping_pong(self) -> "OceancdRolloutSpecTrafficPingPongOutputReference":
        return typing.cast("OceancdRolloutSpecTrafficPingPongOutputReference", jsii.get(self, "pingPong"))

    @builtins.property
    @jsii.member(jsii_name="smi")
    def smi(self) -> "OceancdRolloutSpecTrafficSmiOutputReference":
        return typing.cast("OceancdRolloutSpecTrafficSmiOutputReference", jsii.get(self, "smi"))

    @builtins.property
    @jsii.member(jsii_name="albInput")
    def alb_input(self) -> typing.Optional[OceancdRolloutSpecTrafficAlb]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficAlb], jsii.get(self, "albInput"))

    @builtins.property
    @jsii.member(jsii_name="ambassadorInput")
    def ambassador_input(self) -> typing.Optional[OceancdRolloutSpecTrafficAmbassador]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficAmbassador], jsii.get(self, "ambassadorInput"))

    @builtins.property
    @jsii.member(jsii_name="canaryServiceInput")
    def canary_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "canaryServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="istioInput")
    def istio_input(self) -> typing.Optional[OceancdRolloutSpecTrafficIstio]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficIstio], jsii.get(self, "istioInput"))

    @builtins.property
    @jsii.member(jsii_name="nginxInput")
    def nginx_input(self) -> typing.Optional[OceancdRolloutSpecTrafficNginx]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficNginx], jsii.get(self, "nginxInput"))

    @builtins.property
    @jsii.member(jsii_name="pingPongInput")
    def ping_pong_input(self) -> typing.Optional["OceancdRolloutSpecTrafficPingPong"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficPingPong"], jsii.get(self, "pingPongInput"))

    @builtins.property
    @jsii.member(jsii_name="smiInput")
    def smi_input(self) -> typing.Optional["OceancdRolloutSpecTrafficSmi"]:
        return typing.cast(typing.Optional["OceancdRolloutSpecTrafficSmi"], jsii.get(self, "smiInput"))

    @builtins.property
    @jsii.member(jsii_name="stableServiceInput")
    def stable_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stableServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="canaryService")
    def canary_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "canaryService"))

    @canary_service.setter
    def canary_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__209da29fa12a847f785e2ff9e67b669a46959c1845c90c0091ad123a387591e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "canaryService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stableService")
    def stable_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stableService"))

    @stable_service.setter
    def stable_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8e46eabadd922f62c8fa9a0929e595d72410098d233bbb4eef49ef5e14879c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stableService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTraffic]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTraffic], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceancdRolloutSpecTraffic]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57b2ab84190d82b6ab657798e8236e5309af418741327a9873254df613e51fe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficPingPong",
    jsii_struct_bases=[],
    name_mapping={"ping_service": "pingService", "pong_service": "pongService"},
)
class OceancdRolloutSpecTrafficPingPong:
    def __init__(
        self,
        *,
        ping_service: builtins.str,
        pong_service: builtins.str,
    ) -> None:
        '''
        :param ping_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ping_service OceancdRolloutSpec#ping_service}.
        :param pong_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#pong_service OceancdRolloutSpec#pong_service}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c915684d23fa450b80f9a8068e9b5b0147b5cc82a9d88a40791f009b9a4a62d)
            check_type(argname="argument ping_service", value=ping_service, expected_type=type_hints["ping_service"])
            check_type(argname="argument pong_service", value=pong_service, expected_type=type_hints["pong_service"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ping_service": ping_service,
            "pong_service": pong_service,
        }

    @builtins.property
    def ping_service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#ping_service OceancdRolloutSpec#ping_service}.'''
        result = self._values.get("ping_service")
        assert result is not None, "Required property 'ping_service' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pong_service(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#pong_service OceancdRolloutSpec#pong_service}.'''
        result = self._values.get("pong_service")
        assert result is not None, "Required property 'pong_service' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficPingPong(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficPingPongOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficPingPongOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6f61286703305e377d5126596b8027cade72b722bfde04301fa5b8725c537be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="pingServiceInput")
    def ping_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pingServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="pongServiceInput")
    def pong_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pongServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="pingService")
    def ping_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pingService"))

    @ping_service.setter
    def ping_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__849b68c6b729089c01c420f03e5177dc5e995c43abda3d2fc459d850ac2d863c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pingService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pongService")
    def pong_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pongService"))

    @pong_service.setter
    def pong_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7baba2550256fa128afbb25cdd0c6ce23b26201b4da76da67329a6c838f3ee9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pongService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTrafficPingPong]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficPingPong], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficPingPong],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b33266de5cfff8177e20b4515d052cac88c2290a1c12fbf0aad5844711149b02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficSmi",
    jsii_struct_bases=[],
    name_mapping={
        "smi_root_service": "smiRootService",
        "traffic_split_name": "trafficSplitName",
    },
)
class OceancdRolloutSpecTrafficSmi:
    def __init__(
        self,
        *,
        smi_root_service: typing.Optional[builtins.str] = None,
        traffic_split_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param smi_root_service: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#smi_root_service OceancdRolloutSpec#smi_root_service}.
        :param traffic_split_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#traffic_split_name OceancdRolloutSpec#traffic_split_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dd6e368c63425c3c625da36776c26f2836da21046be12038bc24cc0ef69e4ce)
            check_type(argname="argument smi_root_service", value=smi_root_service, expected_type=type_hints["smi_root_service"])
            check_type(argname="argument traffic_split_name", value=traffic_split_name, expected_type=type_hints["traffic_split_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if smi_root_service is not None:
            self._values["smi_root_service"] = smi_root_service
        if traffic_split_name is not None:
            self._values["traffic_split_name"] = traffic_split_name

    @builtins.property
    def smi_root_service(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#smi_root_service OceancdRolloutSpec#smi_root_service}.'''
        result = self._values.get("smi_root_service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def traffic_split_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_rollout_spec#traffic_split_name OceancdRolloutSpec#traffic_split_name}.'''
        result = self._values.get("traffic_split_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdRolloutSpecTrafficSmi(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdRolloutSpecTrafficSmiOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdRolloutSpec.OceancdRolloutSpecTrafficSmiOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17a2ac862f3e674d95411fa1b5576366c78e7d371f4aba13ef0272e9b0b43b25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSmiRootService")
    def reset_smi_root_service(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmiRootService", []))

    @jsii.member(jsii_name="resetTrafficSplitName")
    def reset_traffic_split_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrafficSplitName", []))

    @builtins.property
    @jsii.member(jsii_name="smiRootServiceInput")
    def smi_root_service_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smiRootServiceInput"))

    @builtins.property
    @jsii.member(jsii_name="trafficSplitNameInput")
    def traffic_split_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trafficSplitNameInput"))

    @builtins.property
    @jsii.member(jsii_name="smiRootService")
    def smi_root_service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smiRootService"))

    @smi_root_service.setter
    def smi_root_service(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7abd4743b2f3ad30a232be9583d3e241462f2eead3bacd2593d977cb37ee821)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smiRootService", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trafficSplitName")
    def traffic_split_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trafficSplitName"))

    @traffic_split_name.setter
    def traffic_split_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc8eca27e3ced75585a18ed956b50bfd23c2e42ca368012a2024be1f2bd8554)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trafficSplitName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdRolloutSpecTrafficSmi]:
        return typing.cast(typing.Optional[OceancdRolloutSpecTrafficSmi], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdRolloutSpecTrafficSmi],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bea6d3e8825fdcacfaa94866cfd4379750a11bd4ef73f6f5dc40035c943f23bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceancdRolloutSpec",
    "OceancdRolloutSpecConfig",
    "OceancdRolloutSpecFailurePolicy",
    "OceancdRolloutSpecFailurePolicyOutputReference",
    "OceancdRolloutSpecSpotDeployment",
    "OceancdRolloutSpecSpotDeploymentOutputReference",
    "OceancdRolloutSpecSpotDeployments",
    "OceancdRolloutSpecSpotDeploymentsList",
    "OceancdRolloutSpecSpotDeploymentsOutputReference",
    "OceancdRolloutSpecStrategy",
    "OceancdRolloutSpecStrategyArgs",
    "OceancdRolloutSpecStrategyArgsList",
    "OceancdRolloutSpecStrategyArgsOutputReference",
    "OceancdRolloutSpecStrategyArgsValueFrom",
    "OceancdRolloutSpecStrategyArgsValueFromFieldRef",
    "OceancdRolloutSpecStrategyArgsValueFromFieldRefOutputReference",
    "OceancdRolloutSpecStrategyArgsValueFromOutputReference",
    "OceancdRolloutSpecStrategyOutputReference",
    "OceancdRolloutSpecTraffic",
    "OceancdRolloutSpecTrafficAlb",
    "OceancdRolloutSpecTrafficAlbOutputReference",
    "OceancdRolloutSpecTrafficAlbStickinessConfig",
    "OceancdRolloutSpecTrafficAlbStickinessConfigOutputReference",
    "OceancdRolloutSpecTrafficAmbassador",
    "OceancdRolloutSpecTrafficAmbassadorOutputReference",
    "OceancdRolloutSpecTrafficIstio",
    "OceancdRolloutSpecTrafficIstioDestinationRule",
    "OceancdRolloutSpecTrafficIstioDestinationRuleOutputReference",
    "OceancdRolloutSpecTrafficIstioOutputReference",
    "OceancdRolloutSpecTrafficIstioVirtualServices",
    "OceancdRolloutSpecTrafficIstioVirtualServicesList",
    "OceancdRolloutSpecTrafficIstioVirtualServicesOutputReference",
    "OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes",
    "OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesList",
    "OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutesOutputReference",
    "OceancdRolloutSpecTrafficNginx",
    "OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation",
    "OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotationOutputReference",
    "OceancdRolloutSpecTrafficNginxOutputReference",
    "OceancdRolloutSpecTrafficOutputReference",
    "OceancdRolloutSpecTrafficPingPong",
    "OceancdRolloutSpecTrafficPingPongOutputReference",
    "OceancdRolloutSpecTrafficSmi",
    "OceancdRolloutSpecTrafficSmiOutputReference",
]

publication.publish()

def _typecheckingstub__4f5db3660a2fb40c01efe44ff20bdc43623b2087ae229e419e6db665652aa721(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    rollout_spec_name: builtins.str,
    strategy: typing.Union[OceancdRolloutSpecStrategy, typing.Dict[builtins.str, typing.Any]],
    failure_policy: typing.Optional[typing.Union[OceancdRolloutSpecFailurePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    spot_deployment: typing.Optional[typing.Union[OceancdRolloutSpecSpotDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_deployments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecSpotDeployments, typing.Dict[builtins.str, typing.Any]]]]] = None,
    traffic: typing.Optional[typing.Union[OceancdRolloutSpecTraffic, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__4336be3674617384e7d78a1d23faf0cc9a22b21759ca73160ba9dadd4165e3bb(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2facde2ffcb38f5a81a5af491f9aac0e30f7749d440c64a689159a9f3730510(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecSpotDeployments, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e42971c34ce6a17771d0b7b08e2fde967b885f968b9d94727342127c1fa9dcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2e208ccfb7e0afe895f1bac22f76239d52e017de9e3c8215c58d1a658a206a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9cdf34806df25e7910cc4f3230c9daa6bf7c5b50515796eb5a264b92d7105ff(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    rollout_spec_name: builtins.str,
    strategy: typing.Union[OceancdRolloutSpecStrategy, typing.Dict[builtins.str, typing.Any]],
    failure_policy: typing.Optional[typing.Union[OceancdRolloutSpecFailurePolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    spot_deployment: typing.Optional[typing.Union[OceancdRolloutSpecSpotDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    spot_deployments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecSpotDeployments, typing.Dict[builtins.str, typing.Any]]]]] = None,
    traffic: typing.Optional[typing.Union[OceancdRolloutSpecTraffic, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eda59a20a193e78207b0596d5823ba13e034311b5ceebd90965f623e0528a172(
    *,
    action: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff3181428c6901df004b0a11122c634741c70a43744be01ca82b09ba92a80ff5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f46eac590d7444e642ddbc492288adc4ac4e28ed4e64a917adb4ddb4539c81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a345a9a9c8a5165f637b773256db1b4180d24182a7d80fa270f75a0e58f44053(
    value: typing.Optional[OceancdRolloutSpecFailurePolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e3560ee11ac377d22f695e0f12bbc4a07fc075ee59795481df8e21a54103e1f(
    *,
    spot_deployment_cluster_id: typing.Optional[builtins.str] = None,
    spot_deployment_name: typing.Optional[builtins.str] = None,
    spot_deployment_namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02613ca5d6ed831f770880b152ede25bc9ab9b0faaf4d4e7983a848400520414(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59e283bc3b231f689461c4076f5449b22f8195531ab7273580c88844aca0dad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f7a500dda302a15b6217aeb609c01b48d6baa86e54507c0f67025da741b122f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1860466901e9c0ee5dae73161b0a7afabbc179b180cb286642b1f726855b209(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5818a1c736bdda2bd4a5f6b94476343f2a21f6c6a083d8816cf261c0ea514d55(
    value: typing.Optional[OceancdRolloutSpecSpotDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__946558a01e1bba67ae3206465b7da98213be7c563c696014ef52836e08eafcb1(
    *,
    spot_deployments_cluster_id: typing.Optional[builtins.str] = None,
    spot_deployments_name: typing.Optional[builtins.str] = None,
    spot_deployments_namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52f8053222635fe3767cd42f3e069dc3d86a1cc41605219c416b3fe84493d9af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a23b929c92402c1620f819769b13de4251667c73af0f5a5da746fc1dabad3d6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e84849253f7d6a0660384472103390a724293055ba14cf9e300cad147df50ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a89315643bcf12cf7d53e61935aa415bc0781cfef74f96b8fb6fcf2cd7d40f29(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18e2c11dc1071ef88524473d396f5e2b712866a98244c531d081fc320639c36c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a573f3baace5066323811f33e1b04a6d6bd5773b0dbacec6b05d635f61568f59(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecSpotDeployments]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5291264f44f2f2ea19225c5e8342f207232fd46477e5cb6046317a142f2dfdea(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88309320f25e81f70ef4adf6148d8dac82907d560117765525f192e7187eab54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc63e6de52ab1639a34474cfa480e57c390ae29041e8d63bedbbf9266ccb91c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f8d9e43b10b9085c3c72266f5a4c6350cb7949d7407dde267596267c1135313(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b48e0945d1272411f88340448f142893ea2df1826ac84108a2a9c7bfb1d21df7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecSpotDeployments]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ad8b4cb2c5301d5f8dd33114bbc2c0fba84b99da9243792e4c2b7bc58609f65(
    *,
    strategy_name: builtins.str,
    args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecStrategyArgs, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a48d270daa288652bb4b8d4eda1cf3d9c6d0758a38b1996cff959587610686(
    *,
    arg_name: builtins.str,
    arg_value: typing.Optional[builtins.str] = None,
    value_from: typing.Optional[typing.Union[OceancdRolloutSpecStrategyArgsValueFrom, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17719d0060668600050c8683b75801918e000e594651ec33719ec705937bc06e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11ac8fa952b77ee7b0e57841c7705c86885e31f479d02d837b714b46fbbd23cf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1429fe869e50ec8ef2025c843ca4b980922eacf02ae37e21d458e023bfb3874f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86d02c03eea40f01c0e3b8e21ad52577026b6dda892c3abf96bf097209fdb509(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34d17179764d79cbf96ef30de60fd4c11d049efd996a164c4dd5654cb5f058ac(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5d00db4f09d5f07aa63ed65d47bff2e2e20e473e1955ec66d1989c50f105a0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecStrategyArgs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c202a0780b37d72420d283d3a845ac12d95e07ba08cef82d2aea851342cfa98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__766ce071d5bdcc5d5065c9079596c7fb5101f1bf698a329e3c8200efd2e7ad80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da000953360673cfc8db0d075d2f37effa44aaf56108463a62f049cf2510b274(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07b15a3b2bd6220f00ac69e859bb1b5a349381e025126b4e3f2051ab9d5f08c8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecStrategyArgs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1760bbdd09f5de467676556dc83621e5e53044f1f610951a81ecb512c36ad98a(
    *,
    field_ref: typing.Union[OceancdRolloutSpecStrategyArgsValueFromFieldRef, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__449a67dcbccb8445d5f448e3391ad416d7fffc8d3ce97dc491ef23906f5a02df(
    *,
    field_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0bf0f7815933293827c0491a24a58f8a429b9ab3e46f4d8e9638b70ebcae20d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__989db517e1dfabd17e2dae6b0eb4edc9e8b38ec0fa95ef766545dfe47afd7106(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e018e79a53508e28a399703ca92ddf18e7a4363f98236f9c7f497366a2fc1645(
    value: typing.Optional[OceancdRolloutSpecStrategyArgsValueFromFieldRef],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33bb8bd4f9f4d06b7aee1c003bb8fd7f544e7b4f369c9274360a9278746d0e0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6df25effd35713755aabc11f636e6a440b43770ae206d762fa38517f0330bf3f(
    value: typing.Optional[OceancdRolloutSpecStrategyArgsValueFrom],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feda263f25efdddb679d23746b5c20ea33ea56c38dc6e840d5eb439c1604b181(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e7ed85484cf05fe0e17ab45d0a37eee0e04533de5b0be03f2acba73ec690f1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecStrategyArgs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fafac19294054a2123d742105e4de8df42b71baab793e7f2d5a0e6cbf243f91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1acc3dc79f97141e16ba26dccc79658dc0c6f00c952e6ccc586f7954db21f0b4(
    value: typing.Optional[OceancdRolloutSpecStrategy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b0f45768ac3e4f38995f58297f4fbf626f88137519304b8d8f4f7f95143a3b(
    *,
    alb: typing.Optional[typing.Union[OceancdRolloutSpecTrafficAlb, typing.Dict[builtins.str, typing.Any]]] = None,
    ambassador: typing.Optional[typing.Union[OceancdRolloutSpecTrafficAmbassador, typing.Dict[builtins.str, typing.Any]]] = None,
    canary_service: typing.Optional[builtins.str] = None,
    istio: typing.Optional[typing.Union[OceancdRolloutSpecTrafficIstio, typing.Dict[builtins.str, typing.Any]]] = None,
    nginx: typing.Optional[typing.Union[OceancdRolloutSpecTrafficNginx, typing.Dict[builtins.str, typing.Any]]] = None,
    ping_pong: typing.Optional[typing.Union[OceancdRolloutSpecTrafficPingPong, typing.Dict[builtins.str, typing.Any]]] = None,
    smi: typing.Optional[typing.Union[OceancdRolloutSpecTrafficSmi, typing.Dict[builtins.str, typing.Any]]] = None,
    stable_service: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda4d5acd78aa78c9b80ae32198914b31003468d010c85703b96213777070b65(
    *,
    alb_ingress: builtins.str,
    alb_root_service: builtins.str,
    service_port: jsii.Number,
    alb_annotation_prefix: typing.Optional[builtins.str] = None,
    stickiness_config: typing.Optional[typing.Union[OceancdRolloutSpecTrafficAlbStickinessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f13b9029aeaff4958408023aabd73ce378547240451719d4cd1ffdeba9bb11(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__858cfb1ef16ef528650e97f33f3738d0e461bc98516c6987e1634b69e4ac87d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9deda4a0d79f65610300c6abf0abe92c635f3df4350dc52a68154035d4f3ce9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddd2f2ca84358ae91f7dca202c8ed1420c45fc3f2e2dd1520e49037543a89316(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39b3ac9910d75fed042f7bc40010d0a983ae03eba42a17beb7c8401f38a685df(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67a2641a6108a2fdb8e63a6c7732ea369e513049572274a75d97f46cf0f17639(
    value: typing.Optional[OceancdRolloutSpecTrafficAlb],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a56d9147816f2afbc300642c7a17bcaa5ba2fd9062faf90418c6f18a82a13fb(
    *,
    duration_seconds: typing.Optional[jsii.Number] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ad17974493496994664699df4e20f7530f0205aa4b2c75cb710c69033386fe3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__390ccab6ecf5970f1af62c042067afae63c294a36eeca4d1269fe9626fa47ec3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d99db8f50fcb1833a4b7cd95826e41004dfaa8ce037387dceb4b87f7fc1da139(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d62294a5690dd48e119559ea0110b0f314cf583570f91605ba7970b8f0e25041(
    value: typing.Optional[OceancdRolloutSpecTrafficAlbStickinessConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c634daf27cca9fb1989960b0798a9808eb41648d5c442598db5fc65e97f8959d(
    *,
    mappings: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c5175c7ca80df4fcd27b0a8b95361c30e89e6642f0ba2d28d1cd3330f129d76(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4970986ec3c213f14ba4897da73b9855bad90b2644cb80b8bc03560ca3dc5f8f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa56ed9b3c47e26ecdfbad60597eb446d0c340608f479778f86ce7837d09cb5d(
    value: typing.Optional[OceancdRolloutSpecTrafficAmbassador],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a2f357fac037f11b3790e328269f08b6d00c0694e765c1c5ba5b27840f1712(
    *,
    virtual_services: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecTrafficIstioVirtualServices, typing.Dict[builtins.str, typing.Any]]]],
    destination_rule: typing.Optional[typing.Union[OceancdRolloutSpecTrafficIstioDestinationRule, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e96dbe56fb984e9a4fcd071245a7c45fcfb166963c18688aca4fb777ba4ae96(
    *,
    canary_subset_name: builtins.str,
    destination_rule_name: builtins.str,
    stable_subset_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d404932e23c32112b8e1d377eca7636e35e96245db9d0f33b512b9a23a9ee593(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e646b6676ff3132c590a5429e94fdcf9623f7ea0f0f020a7bd37094d5093b1e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e4bb741ae681e6677ee2aea63cd5e387ddf4cea4c0b9d0a45b841b2dfedc079(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc7e2f7327be36705aad8b8f11ded4ef6041ca35606e8935939882d7d236a7f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75de815ca1b8dd38425765aa93f42c67e2afa35a6b86033d9742629b1d524c6a(
    value: typing.Optional[OceancdRolloutSpecTrafficIstioDestinationRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27d9e06b35261a5c022258dca09db8a560f7b0157e8047c54ccefbea65329528(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ad6f0c7d9e6308f64ae7089591e34b2e993f1626a73b15c6e6f415b5b7e1f0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecTrafficIstioVirtualServices, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16c7a6641e3874727ac5b2384f38a0035b2097764639ae63ec172bb4865067a(
    value: typing.Optional[OceancdRolloutSpecTrafficIstio],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f01a692edfb29b413230f57f938794a3f64332d641038df74150a658f47d2546(
    *,
    virtual_service_name: builtins.str,
    tls_routes: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes, typing.Dict[builtins.str, typing.Any]]]]] = None,
    virtual_service_routes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c78ed83abb396e7dcecdf621a13db718fec2cf43a86716af3cc8bb5464a0667(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__531eb100455cc113437d7dfdb70cfc487478ecc25a54ead7586322b7b31b4b52(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f75b506994b6e46a164d2b9a2200d4ac1aa25b352b34619ddac0d183c2317cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3a92a1835500958413302e0cd637a90d8f5b986470e7e29ccd041d67130e7a6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbbb99b30cd8a661f0852050edff026243fedfa061b76a5db1472eb2b339a4a7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2091aaba3cabec8325a73ba72550b07b95281818f486b4025bdea7f0ec6c2188(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServices]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92d176e56ba5ff70d447a6f3a6605bcf2c46edc0f00fca2bf45852b6a8db0bd3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed428a8987944572560cada554418e8f2af3421974e4c0ae7eac34f6fce72d2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad5d2b8e5302c03a4d52f09f4ba0b5edb391d22649c15b54ebddb880f74b3cb8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3eebb8b1472dd81a47e7bab95562651d60d8066bcb78c0f5b2e4a72bdb8842(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee5ad2a3073570e71587422943f0ba683d2ea4d18268900810cb7a5a0aff9804(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServices]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__545ee260f441d3582aeaa11035f2168e8da049d6afd54a7d79a31cb88c102484(
    *,
    port: typing.Optional[jsii.Number] = None,
    sni_hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1d9badd1db16e999483527dd645af09cf460892aef0314d34af7632830b98a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bfa6a62a84229fee55a5cfceda9ed6d647d2e9442387fea01cf16f7c851f8d9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb7410324f564c2d78c86dd6c491236744394d4c9cda6b42143e63764644c5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81fb6126eca9c32372212b3d86538941bb7561f4167b641b4160651b567910ac(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab27d4d4dc459af4ca69170fc5f6fe22f6528d2ef1eeb5d19cec59370ed69fda(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd604426c35b5d8a5c053b3d6848bd2318fbd3da7d0fa9d7e78032b5bf17b41f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb73038ab400ae55b64aeb76cd202636c1cd7bdd2baf1937acbd42260d9b281(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8336c2ad4a5d59e0bf4f0c0b76f0ce6b8d167a2bf8b6143ae5956469154a4ed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9016ca9c86c4ff574c7be45100b9a095cdbe4a32b2387f6e51a1e4b3dd7f1d85(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c2e6c386252a8dbd8ba6f244a6cf80d8040287997dc2efa524381cc2d683f24(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdRolloutSpecTrafficIstioVirtualServicesTlsRoutes]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__585c05b0b38812255e44ef4bbd2f7f5e1275da6476fc1a38f080be859311338d(
    *,
    stable_ingress: builtins.str,
    additional_ingress_annotation: typing.Optional[typing.Union[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation, typing.Dict[builtins.str, typing.Any]]] = None,
    nginx_annotation_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cce9459f93eeb8d6886222d0b081a04e84579bf339cf5b9a7240160e405a2e2c(
    *,
    canary_by_header: typing.Optional[builtins.str] = None,
    key1: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abfbf8c80d33c0c3c4bd53e17894cc362bda92628139828b905009d911f7d084(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cab361f1c2a8edeb920f7536e4c61a9ff7a081efb2f0b0b7120eca98d1b85bb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b26330b208d08f952b102dc82fc8664aaa65ff4a9786fb3910ca27e62fddeef3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfe0835bb2ef46c7fb251eef08851b46cd13f7f41640e092b6b352c6960238e1(
    value: typing.Optional[OceancdRolloutSpecTrafficNginxAdditionalIngressAnnotation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a1a5876c2cdba05d4cd2e6c8d3dff1d0fd5d39e2b37de8c1ccc8eba755a312(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56581b86ab4c2bea02ec534c7fc5ac1e10c95ccff7e93748ab7743731b606c55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82cc4bb79e63a0d55ca0e399137808aedbce1fb5d329f90574d1673abcefe66d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1975d8dd3b48425aa39cbd0a1c7a97b1bfd375051a2189fc2264ff3ed4f0562c(
    value: typing.Optional[OceancdRolloutSpecTrafficNginx],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23832f9015fb7e505e5dc00284ba788f8512a0b7129380625c3b772a603f1c4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__209da29fa12a847f785e2ff9e67b669a46959c1845c90c0091ad123a387591e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8e46eabadd922f62c8fa9a0929e595d72410098d233bbb4eef49ef5e14879c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57b2ab84190d82b6ab657798e8236e5309af418741327a9873254df613e51fe4(
    value: typing.Optional[OceancdRolloutSpecTraffic],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c915684d23fa450b80f9a8068e9b5b0147b5cc82a9d88a40791f009b9a4a62d(
    *,
    ping_service: builtins.str,
    pong_service: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f61286703305e377d5126596b8027cade72b722bfde04301fa5b8725c537be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__849b68c6b729089c01c420f03e5177dc5e995c43abda3d2fc459d850ac2d863c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7baba2550256fa128afbb25cdd0c6ce23b26201b4da76da67329a6c838f3ee9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33266de5cfff8177e20b4515d052cac88c2290a1c12fbf0aad5844711149b02(
    value: typing.Optional[OceancdRolloutSpecTrafficPingPong],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dd6e368c63425c3c625da36776c26f2836da21046be12038bc24cc0ef69e4ce(
    *,
    smi_root_service: typing.Optional[builtins.str] = None,
    traffic_split_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17a2ac862f3e674d95411fa1b5576366c78e7d371f4aba13ef0272e9b0b43b25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7abd4743b2f3ad30a232be9583d3e241462f2eead3bacd2593d977cb37ee821(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc8eca27e3ced75585a18ed956b50bfd23c2e42ca368012a2024be1f2bd8554(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bea6d3e8825fdcacfaa94866cfd4379750a11bd4ef73f6f5dc40035c943f23bd(
    value: typing.Optional[OceancdRolloutSpecTrafficSmi],
) -> None:
    """Type checking stubs"""
    pass
