r'''
# `spotinst_ocean_right_sizing_rule`

Refer to the Terraform Registry for docs: [`spotinst_ocean_right_sizing_rule`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule).
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


class OceanRightSizingRule(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRule",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule spotinst_ocean_right_sizing_rule}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        recommendation_application_intervals: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervals", typing.Dict[builtins.str, typing.Any]]]],
        rule_name: builtins.str,
        attach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleAttachWorkloads", typing.Dict[builtins.str, typing.Any]]]]] = None,
        detach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloads", typing.Dict[builtins.str, typing.Any]]]]] = None,
        exclude_preliminary_recommendations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        ocean_id: typing.Optional[builtins.str] = None,
        recommendation_application_boundaries: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationBoundaries", typing.Dict[builtins.str, typing.Any]]]]] = None,
        recommendation_application_hpa: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationHpa", typing.Dict[builtins.str, typing.Any]]]]] = None,
        recommendation_application_min_threshold: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationMinThreshold", typing.Dict[builtins.str, typing.Any]]]]] = None,
        recommendation_application_overhead_values: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationOverheadValues", typing.Dict[builtins.str, typing.Any]]]]] = None,
        restart_replicas: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule spotinst_ocean_right_sizing_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param recommendation_application_intervals: recommendation_application_intervals block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_intervals OceanRightSizingRule#recommendation_application_intervals}
        :param rule_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#rule_name OceanRightSizingRule#rule_name}.
        :param attach_workloads: attach_workloads block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#attach_workloads OceanRightSizingRule#attach_workloads}
        :param detach_workloads: detach_workloads block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#detach_workloads OceanRightSizingRule#detach_workloads}
        :param exclude_preliminary_recommendations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#exclude_preliminary_recommendations OceanRightSizingRule#exclude_preliminary_recommendations}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#id OceanRightSizingRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#ocean_id OceanRightSizingRule#ocean_id}.
        :param recommendation_application_boundaries: recommendation_application_boundaries block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_boundaries OceanRightSizingRule#recommendation_application_boundaries}
        :param recommendation_application_hpa: recommendation_application_hpa block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_hpa OceanRightSizingRule#recommendation_application_hpa}
        :param recommendation_application_min_threshold: recommendation_application_min_threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_min_threshold OceanRightSizingRule#recommendation_application_min_threshold}
        :param recommendation_application_overhead_values: recommendation_application_overhead_values block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_overhead_values OceanRightSizingRule#recommendation_application_overhead_values}
        :param restart_replicas: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#restart_replicas OceanRightSizingRule#restart_replicas}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa26bb85f524a60b527ad3cb1e375d316bd2766476e2e27dd8bc884b9ac669fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceanRightSizingRuleConfig(
            recommendation_application_intervals=recommendation_application_intervals,
            rule_name=rule_name,
            attach_workloads=attach_workloads,
            detach_workloads=detach_workloads,
            exclude_preliminary_recommendations=exclude_preliminary_recommendations,
            id=id,
            ocean_id=ocean_id,
            recommendation_application_boundaries=recommendation_application_boundaries,
            recommendation_application_hpa=recommendation_application_hpa,
            recommendation_application_min_threshold=recommendation_application_min_threshold,
            recommendation_application_overhead_values=recommendation_application_overhead_values,
            restart_replicas=restart_replicas,
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
        '''Generates CDKTF code for importing a OceanRightSizingRule resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceanRightSizingRule to import.
        :param import_from_id: The id of the existing OceanRightSizingRule that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceanRightSizingRule to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a61bd7cb8eb8e47076583133307f70c1e5e14ca72f597cb45b3184129be3623a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAttachWorkloads")
    def put_attach_workloads(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleAttachWorkloads", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0957f54a82ccab02a92c090a52ba507bcde36247baf6f14baf7a7bf6939d2f28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAttachWorkloads", [value]))

    @jsii.member(jsii_name="putDetachWorkloads")
    def put_detach_workloads(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloads", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c150752c03c2f71537846c611906bac39726a6ea815cb4363456cbcef4d42d60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDetachWorkloads", [value]))

    @jsii.member(jsii_name="putRecommendationApplicationBoundaries")
    def put_recommendation_application_boundaries(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationBoundaries", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e1829e2026a0801ac53b1ac8dfd3ce4acb70afbd598431ff5925e1f300077d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecommendationApplicationBoundaries", [value]))

    @jsii.member(jsii_name="putRecommendationApplicationHpa")
    def put_recommendation_application_hpa(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationHpa", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a92732a87ab496ad3ff15e5bf764553939cb76d3319e34197d55f91e4a40bb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecommendationApplicationHpa", [value]))

    @jsii.member(jsii_name="putRecommendationApplicationIntervals")
    def put_recommendation_application_intervals(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervals", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6739e33e0f15149c24996bc0485ac8d1fcc4df3b9afc1664642e840f6b54882d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecommendationApplicationIntervals", [value]))

    @jsii.member(jsii_name="putRecommendationApplicationMinThreshold")
    def put_recommendation_application_min_threshold(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationMinThreshold", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de7cb298d260c1cddb513f107e62a6ead88b56e3247516c180192580611e67d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecommendationApplicationMinThreshold", [value]))

    @jsii.member(jsii_name="putRecommendationApplicationOverheadValues")
    def put_recommendation_application_overhead_values(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationOverheadValues", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f1b51e0c8c62519aacf9ca3890448ac9116dc3a0b0b58cce721a1cc2c0685f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRecommendationApplicationOverheadValues", [value]))

    @jsii.member(jsii_name="resetAttachWorkloads")
    def reset_attach_workloads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttachWorkloads", []))

    @jsii.member(jsii_name="resetDetachWorkloads")
    def reset_detach_workloads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDetachWorkloads", []))

    @jsii.member(jsii_name="resetExcludePreliminaryRecommendations")
    def reset_exclude_preliminary_recommendations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludePreliminaryRecommendations", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOceanId")
    def reset_ocean_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOceanId", []))

    @jsii.member(jsii_name="resetRecommendationApplicationBoundaries")
    def reset_recommendation_application_boundaries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecommendationApplicationBoundaries", []))

    @jsii.member(jsii_name="resetRecommendationApplicationHpa")
    def reset_recommendation_application_hpa(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecommendationApplicationHpa", []))

    @jsii.member(jsii_name="resetRecommendationApplicationMinThreshold")
    def reset_recommendation_application_min_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecommendationApplicationMinThreshold", []))

    @jsii.member(jsii_name="resetRecommendationApplicationOverheadValues")
    def reset_recommendation_application_overhead_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecommendationApplicationOverheadValues", []))

    @jsii.member(jsii_name="resetRestartReplicas")
    def reset_restart_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartReplicas", []))

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
    @jsii.member(jsii_name="attachWorkloads")
    def attach_workloads(self) -> "OceanRightSizingRuleAttachWorkloadsList":
        return typing.cast("OceanRightSizingRuleAttachWorkloadsList", jsii.get(self, "attachWorkloads"))

    @builtins.property
    @jsii.member(jsii_name="detachWorkloads")
    def detach_workloads(self) -> "OceanRightSizingRuleDetachWorkloadsList":
        return typing.cast("OceanRightSizingRuleDetachWorkloadsList", jsii.get(self, "detachWorkloads"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationBoundaries")
    def recommendation_application_boundaries(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationBoundariesList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationBoundariesList", jsii.get(self, "recommendationApplicationBoundaries"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationHpa")
    def recommendation_application_hpa(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationHpaList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationHpaList", jsii.get(self, "recommendationApplicationHpa"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationIntervals")
    def recommendation_application_intervals(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsList", jsii.get(self, "recommendationApplicationIntervals"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationMinThreshold")
    def recommendation_application_min_threshold(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationMinThresholdList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationMinThresholdList", jsii.get(self, "recommendationApplicationMinThreshold"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationOverheadValues")
    def recommendation_application_overhead_values(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationOverheadValuesList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationOverheadValuesList", jsii.get(self, "recommendationApplicationOverheadValues"))

    @builtins.property
    @jsii.member(jsii_name="attachWorkloadsInput")
    def attach_workloads_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloads"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloads"]]], jsii.get(self, "attachWorkloadsInput"))

    @builtins.property
    @jsii.member(jsii_name="detachWorkloadsInput")
    def detach_workloads_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloads"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloads"]]], jsii.get(self, "detachWorkloadsInput"))

    @builtins.property
    @jsii.member(jsii_name="excludePreliminaryRecommendationsInput")
    def exclude_preliminary_recommendations_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludePreliminaryRecommendationsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="oceanIdInput")
    def ocean_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oceanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationBoundariesInput")
    def recommendation_application_boundaries_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationBoundaries"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationBoundaries"]]], jsii.get(self, "recommendationApplicationBoundariesInput"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationHpaInput")
    def recommendation_application_hpa_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationHpa"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationHpa"]]], jsii.get(self, "recommendationApplicationHpaInput"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationIntervalsInput")
    def recommendation_application_intervals_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervals"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervals"]]], jsii.get(self, "recommendationApplicationIntervalsInput"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationMinThresholdInput")
    def recommendation_application_min_threshold_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationMinThreshold"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationMinThreshold"]]], jsii.get(self, "recommendationApplicationMinThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="recommendationApplicationOverheadValuesInput")
    def recommendation_application_overhead_values_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationOverheadValues"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationOverheadValues"]]], jsii.get(self, "recommendationApplicationOverheadValuesInput"))

    @builtins.property
    @jsii.member(jsii_name="restartReplicasInput")
    def restart_replicas_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restartReplicasInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleNameInput")
    def rule_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="excludePreliminaryRecommendations")
    def exclude_preliminary_recommendations(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludePreliminaryRecommendations"))

    @exclude_preliminary_recommendations.setter
    def exclude_preliminary_recommendations(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cc73b2ecb7475f5c1654f139661e5a9fffacfe1df96e8cf0a872a3b52e251fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludePreliminaryRecommendations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__703c529605f2dd55f96945a70922720f7230899f92e5d933c4c5b8ebe646cffe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oceanId")
    def ocean_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oceanId"))

    @ocean_id.setter
    def ocean_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e588cb0b729f78d54078af300245d1e3c95c6e1f4c6988db3f1edcf7e295d65e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oceanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restartReplicas")
    def restart_replicas(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restartReplicas"))

    @restart_replicas.setter
    def restart_replicas(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17935e34d8efacd4b5a40cc2915d3ca979497f498020322f554b66d243a11e9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartReplicas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ruleName")
    def rule_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleName"))

    @rule_name.setter
    def rule_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca1da33853da973f330668ebe773b7cb114bdb37d9f7b23ca551dbc75651c6d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloads",
    jsii_struct_bases=[],
    name_mapping={"namespaces": "namespaces"},
)
class OceanRightSizingRuleAttachWorkloads:
    def __init__(
        self,
        *,
        namespaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleAttachWorkloadsNamespaces", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param namespaces: namespaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespaces OceanRightSizingRule#namespaces}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e15b392454437dcff8d788eb02f89c88e29b7b113795860336ec1683213c7bfe)
            check_type(argname="argument namespaces", value=namespaces, expected_type=type_hints["namespaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespaces": namespaces,
        }

    @builtins.property
    def namespaces(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespaces"]]:
        '''namespaces block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespaces OceanRightSizingRule#namespaces}
        '''
        result = self._values.get("namespaces")
        assert result is not None, "Required property 'namespaces' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespaces"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleAttachWorkloads(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleAttachWorkloadsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa54cb5255544d7341515b6c39ec4553fecbba830135880905bc03c4e3550fd5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleAttachWorkloadsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810feda6168a537bcb6eb31438dda2fa46de17f6b961db28906e46c39a760fc1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleAttachWorkloadsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2716843c235b91a0777f9e151256998125eddcd65a721189cd28453304463b4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2187190791eab87a4b5d77988e30090165acd42cb266ebefd974df59a7353e3a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__48d842cde660202b965566ce68ff4b438b3ff8a6fab6742271acc859c9129160)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloads]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloads]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloads]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a347c803b3ff552b895a097283e905989fda45eb76631e5b8e046b661230210b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespaces",
    jsii_struct_bases=[],
    name_mapping={
        "namespace_name": "namespaceName",
        "labels": "labels",
        "workloads": "workloads",
    },
)
class OceanRightSizingRuleAttachWorkloadsNamespaces:
    def __init__(
        self,
        *,
        namespace_name: builtins.str,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleAttachWorkloadsNamespacesLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param namespace_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespace_name OceanRightSizingRule#namespace_name}.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#labels OceanRightSizingRule#labels}
        :param workloads: workloads block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workloads OceanRightSizingRule#workloads}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e7c487d4d2eddf69180b7bf44cc6ba71270175cdaac19a9ec2cd3ac3e0516ab)
            check_type(argname="argument namespace_name", value=namespace_name, expected_type=type_hints["namespace_name"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument workloads", value=workloads, expected_type=type_hints["workloads"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespace_name": namespace_name,
        }
        if labels is not None:
            self._values["labels"] = labels
        if workloads is not None:
            self._values["workloads"] = workloads

    @builtins.property
    def namespace_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespace_name OceanRightSizingRule#namespace_name}.'''
        result = self._values.get("namespace_name")
        assert result is not None, "Required property 'namespace_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespacesLabels"]]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#labels OceanRightSizingRule#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespacesLabels"]]], result)

    @builtins.property
    def workloads(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads"]]]:
        '''workloads block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workloads OceanRightSizingRule#workloads}
        '''
        result = self._values.get("workloads")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleAttachWorkloadsNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class OceanRightSizingRuleAttachWorkloadsNamespacesLabels:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#key OceanRightSizingRule#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#value OceanRightSizingRule#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12cbdf6a46dddf9aa1044bab04062731a8de389dafe14353fa52acf49010b4e0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#key OceanRightSizingRule#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#value OceanRightSizingRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleAttachWorkloadsNamespacesLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleAttachWorkloadsNamespacesLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__43940318b40f79cd85b072c9b284d6fcdff44b884ba5e359a84349a4a35558b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleAttachWorkloadsNamespacesLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__426cd2feb093ec4e07dcc6c807493bfa8c77de2a64edf3ee9d8ba1f254ebc450)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleAttachWorkloadsNamespacesLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9557e6d437d3e2d66d0438f5a89e16e0f8e4afb09cdf761a709f7a618b7e7e3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7085465e8bd305f74fa8a2477b64e99b549d4dacbaf39c9a16b7fbd6988ec6bb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41904e147fe6c600be15909a88614dbfa71b64ce6c91760fbbbc13698ab5fa3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb59492f7b164aad05813c4cd978051185ee5757ee44e036622b3c5fc70ee5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleAttachWorkloadsNamespacesLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__87660d09a4c19b3f61ed45e6b182346b6bdcbd49f9eaae819e7689a6b07ce301)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d8912d3042e071f6e08da7a02fdb28f7622dd18556d858b246a33e86b6a52a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77cecd00725ccea1aa2a6ab8ee64658f57df6e5ac65e123d434af9ec8341d463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__867af875624e6a34abb896eef6910d1fa16106960c96e6d79aeb3fef1ffa5aac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleAttachWorkloadsNamespacesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__677526cc4ed492732fdd3ffa4aa909dc75d19c26de942b5918ddb97c537a91f0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleAttachWorkloadsNamespacesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6466e936d7f4642049f29e7bfe237ce9871a69db77e45d223d89fd946891c1bf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleAttachWorkloadsNamespacesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2d470053bd1c99106fa43aeb3960eb34e6322b3438fd2bfb97b670fe4f6b842)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef5d2ee257a1691b3172b7b58055cf9ea6be35c7428a924f620ba51352a00e0e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__892a9f33365ac0af980cce5937d54e5554a0d3d79990bc30877df951346ce0ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98c62fa6faa6c78c06290ca5f076d36abea689f2c888f7dddcf66a7174d348b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleAttachWorkloadsNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6b64e9f9beabc2f3a87fe52052f82cf3d188c9fc3f93058d4e2bbadc98c27cf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putLabels")
    def put_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespacesLabels, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e69ddab2c0c9c649b2fdc49e7fc0e74af1f87acaac059d3aecdc7421ade37d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLabels", [value]))

    @jsii.member(jsii_name="putWorkloads")
    def put_workloads(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9897083f9a57fdcc794925613c2e050608a3b7c4aa334c1ff317e80a5992bec1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWorkloads", [value]))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetWorkloads")
    def reset_workloads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloads", []))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> OceanRightSizingRuleAttachWorkloadsNamespacesLabelsList:
        return typing.cast(OceanRightSizingRuleAttachWorkloadsNamespacesLabelsList, jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="workloads")
    def workloads(self) -> "OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsList":
        return typing.cast("OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsList", jsii.get(self, "workloads"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceNameInput")
    def namespace_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadsInput")
    def workloads_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads"]]], jsii.get(self, "workloadsInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceName"))

    @namespace_name.setter
    def namespace_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d34971c0c54dd09bb15bec5a91bb643eb0dc1c6b8f433868cf6f51fd3fd49080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97f27ebe75bf506616e2e824a6c99f3258911cace7451859595eb1853197a5d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads",
    jsii_struct_bases=[],
    name_mapping={
        "workload_type": "workloadType",
        "regex_name": "regexName",
        "workload_name": "workloadName",
    },
)
class OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads:
    def __init__(
        self,
        *,
        workload_type: builtins.str,
        regex_name: typing.Optional[builtins.str] = None,
        workload_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param workload_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_type OceanRightSizingRule#workload_type}.
        :param regex_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#regex_name OceanRightSizingRule#regex_name}.
        :param workload_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_name OceanRightSizingRule#workload_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc94e48e07e1afce7565229ed4cf21ebc5322601edebe2ae7369023cf0f2c2dc)
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
            check_type(argname="argument regex_name", value=regex_name, expected_type=type_hints["regex_name"])
            check_type(argname="argument workload_name", value=workload_name, expected_type=type_hints["workload_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "workload_type": workload_type,
        }
        if regex_name is not None:
            self._values["regex_name"] = regex_name
        if workload_name is not None:
            self._values["workload_name"] = workload_name

    @builtins.property
    def workload_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_type OceanRightSizingRule#workload_type}.'''
        result = self._values.get("workload_type")
        assert result is not None, "Required property 'workload_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def regex_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#regex_name OceanRightSizingRule#regex_name}.'''
        result = self._values.get("regex_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workload_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_name OceanRightSizingRule#workload_name}.'''
        result = self._values.get("workload_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__35b187376effabb3c71dd678410ce1502fb4a54a5788caa1bdd009e2e6378238)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f2db7f065039321b0e1e7fe3cafc623c3f2f021321fadac9f003400f7a5d946)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4be6e13d2c70992f81684fe3210f024f6213d040197c39d3c5b32f719bbe8416)
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
            type_hints = typing.get_type_hints(_typecheckingstub__27b78723a66bedcf484b28757216943cd028a2e553b550d00a7f87dd65fa2f99)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0033969cb873575b2a6cb5ade77b69c071318de42eae50e62bb0aac3aeb61322)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb5462945e02ad5702e6107dcb31783f1b46c030e1593e6a49a8076549ca110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__22b35511160717d66f5fc59fb8965fd7e3bbf7f626819820c783280cbb6bebd3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetRegexName")
    def reset_regex_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegexName", []))

    @jsii.member(jsii_name="resetWorkloadName")
    def reset_workload_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadName", []))

    @builtins.property
    @jsii.member(jsii_name="regexNameInput")
    def regex_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadNameInput")
    def workload_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="regexName")
    def regex_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regexName"))

    @regex_name.setter
    def regex_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d2a989c4bf8b1ce94d830e1760a6db9c7742e796c5d10c8b1e743827abd694d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regexName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadName")
    def workload_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadName"))

    @workload_name.setter
    def workload_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d261f49564b905cc4292fca6c1a046fc6a2cadb8ec095eeff8ac447cbf70a8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadType"))

    @workload_type.setter
    def workload_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7adaa51f22ffd5c91cbeac538728481a102622266b21014257df9dc023edf43f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e76b393509c8b1b894c8de64d3f1874e4c9c669aeceea0aeb76a0590c3bc210)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleAttachWorkloadsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleAttachWorkloadsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c249cddf8b51c5f9d61669c2f76d7cbb08b148b6a980d86ec1ab307dbc16702)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNamespaces")
    def put_namespaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__339f0e45b533751497efdb079b52c4252173a7c951be1e6d477544b45384466e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNamespaces", [value]))

    @builtins.property
    @jsii.member(jsii_name="namespaces")
    def namespaces(self) -> OceanRightSizingRuleAttachWorkloadsNamespacesList:
        return typing.cast(OceanRightSizingRuleAttachWorkloadsNamespacesList, jsii.get(self, "namespaces"))

    @builtins.property
    @jsii.member(jsii_name="namespacesInput")
    def namespaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespaces]]], jsii.get(self, "namespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloads]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloads]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloads]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bf3617a863a04f8e4272f0f64cf2fb488bc48336edf12ab8e0d311c72a81079)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "recommendation_application_intervals": "recommendationApplicationIntervals",
        "rule_name": "ruleName",
        "attach_workloads": "attachWorkloads",
        "detach_workloads": "detachWorkloads",
        "exclude_preliminary_recommendations": "excludePreliminaryRecommendations",
        "id": "id",
        "ocean_id": "oceanId",
        "recommendation_application_boundaries": "recommendationApplicationBoundaries",
        "recommendation_application_hpa": "recommendationApplicationHpa",
        "recommendation_application_min_threshold": "recommendationApplicationMinThreshold",
        "recommendation_application_overhead_values": "recommendationApplicationOverheadValues",
        "restart_replicas": "restartReplicas",
    },
)
class OceanRightSizingRuleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        recommendation_application_intervals: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervals", typing.Dict[builtins.str, typing.Any]]]],
        rule_name: builtins.str,
        attach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
        detach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloads", typing.Dict[builtins.str, typing.Any]]]]] = None,
        exclude_preliminary_recommendations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        ocean_id: typing.Optional[builtins.str] = None,
        recommendation_application_boundaries: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationBoundaries", typing.Dict[builtins.str, typing.Any]]]]] = None,
        recommendation_application_hpa: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationHpa", typing.Dict[builtins.str, typing.Any]]]]] = None,
        recommendation_application_min_threshold: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationMinThreshold", typing.Dict[builtins.str, typing.Any]]]]] = None,
        recommendation_application_overhead_values: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationOverheadValues", typing.Dict[builtins.str, typing.Any]]]]] = None,
        restart_replicas: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param recommendation_application_intervals: recommendation_application_intervals block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_intervals OceanRightSizingRule#recommendation_application_intervals}
        :param rule_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#rule_name OceanRightSizingRule#rule_name}.
        :param attach_workloads: attach_workloads block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#attach_workloads OceanRightSizingRule#attach_workloads}
        :param detach_workloads: detach_workloads block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#detach_workloads OceanRightSizingRule#detach_workloads}
        :param exclude_preliminary_recommendations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#exclude_preliminary_recommendations OceanRightSizingRule#exclude_preliminary_recommendations}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#id OceanRightSizingRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ocean_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#ocean_id OceanRightSizingRule#ocean_id}.
        :param recommendation_application_boundaries: recommendation_application_boundaries block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_boundaries OceanRightSizingRule#recommendation_application_boundaries}
        :param recommendation_application_hpa: recommendation_application_hpa block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_hpa OceanRightSizingRule#recommendation_application_hpa}
        :param recommendation_application_min_threshold: recommendation_application_min_threshold block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_min_threshold OceanRightSizingRule#recommendation_application_min_threshold}
        :param recommendation_application_overhead_values: recommendation_application_overhead_values block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_overhead_values OceanRightSizingRule#recommendation_application_overhead_values}
        :param restart_replicas: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#restart_replicas OceanRightSizingRule#restart_replicas}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e04bbd12d1fe27d52aacecc88cd22a4ecc424576b3df22febe23d7781cb65411)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument recommendation_application_intervals", value=recommendation_application_intervals, expected_type=type_hints["recommendation_application_intervals"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument attach_workloads", value=attach_workloads, expected_type=type_hints["attach_workloads"])
            check_type(argname="argument detach_workloads", value=detach_workloads, expected_type=type_hints["detach_workloads"])
            check_type(argname="argument exclude_preliminary_recommendations", value=exclude_preliminary_recommendations, expected_type=type_hints["exclude_preliminary_recommendations"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ocean_id", value=ocean_id, expected_type=type_hints["ocean_id"])
            check_type(argname="argument recommendation_application_boundaries", value=recommendation_application_boundaries, expected_type=type_hints["recommendation_application_boundaries"])
            check_type(argname="argument recommendation_application_hpa", value=recommendation_application_hpa, expected_type=type_hints["recommendation_application_hpa"])
            check_type(argname="argument recommendation_application_min_threshold", value=recommendation_application_min_threshold, expected_type=type_hints["recommendation_application_min_threshold"])
            check_type(argname="argument recommendation_application_overhead_values", value=recommendation_application_overhead_values, expected_type=type_hints["recommendation_application_overhead_values"])
            check_type(argname="argument restart_replicas", value=restart_replicas, expected_type=type_hints["restart_replicas"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "recommendation_application_intervals": recommendation_application_intervals,
            "rule_name": rule_name,
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
        if attach_workloads is not None:
            self._values["attach_workloads"] = attach_workloads
        if detach_workloads is not None:
            self._values["detach_workloads"] = detach_workloads
        if exclude_preliminary_recommendations is not None:
            self._values["exclude_preliminary_recommendations"] = exclude_preliminary_recommendations
        if id is not None:
            self._values["id"] = id
        if ocean_id is not None:
            self._values["ocean_id"] = ocean_id
        if recommendation_application_boundaries is not None:
            self._values["recommendation_application_boundaries"] = recommendation_application_boundaries
        if recommendation_application_hpa is not None:
            self._values["recommendation_application_hpa"] = recommendation_application_hpa
        if recommendation_application_min_threshold is not None:
            self._values["recommendation_application_min_threshold"] = recommendation_application_min_threshold
        if recommendation_application_overhead_values is not None:
            self._values["recommendation_application_overhead_values"] = recommendation_application_overhead_values
        if restart_replicas is not None:
            self._values["restart_replicas"] = restart_replicas

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
    def recommendation_application_intervals(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervals"]]:
        '''recommendation_application_intervals block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_intervals OceanRightSizingRule#recommendation_application_intervals}
        '''
        result = self._values.get("recommendation_application_intervals")
        assert result is not None, "Required property 'recommendation_application_intervals' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervals"]], result)

    @builtins.property
    def rule_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#rule_name OceanRightSizingRule#rule_name}.'''
        result = self._values.get("rule_name")
        assert result is not None, "Required property 'rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attach_workloads(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloads]]]:
        '''attach_workloads block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#attach_workloads OceanRightSizingRule#attach_workloads}
        '''
        result = self._values.get("attach_workloads")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloads]]], result)

    @builtins.property
    def detach_workloads(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloads"]]]:
        '''detach_workloads block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#detach_workloads OceanRightSizingRule#detach_workloads}
        '''
        result = self._values.get("detach_workloads")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloads"]]], result)

    @builtins.property
    def exclude_preliminary_recommendations(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#exclude_preliminary_recommendations OceanRightSizingRule#exclude_preliminary_recommendations}.'''
        result = self._values.get("exclude_preliminary_recommendations")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#id OceanRightSizingRule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ocean_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#ocean_id OceanRightSizingRule#ocean_id}.'''
        result = self._values.get("ocean_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recommendation_application_boundaries(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationBoundaries"]]]:
        '''recommendation_application_boundaries block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_boundaries OceanRightSizingRule#recommendation_application_boundaries}
        '''
        result = self._values.get("recommendation_application_boundaries")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationBoundaries"]]], result)

    @builtins.property
    def recommendation_application_hpa(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationHpa"]]]:
        '''recommendation_application_hpa block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_hpa OceanRightSizingRule#recommendation_application_hpa}
        '''
        result = self._values.get("recommendation_application_hpa")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationHpa"]]], result)

    @builtins.property
    def recommendation_application_min_threshold(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationMinThreshold"]]]:
        '''recommendation_application_min_threshold block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_min_threshold OceanRightSizingRule#recommendation_application_min_threshold}
        '''
        result = self._values.get("recommendation_application_min_threshold")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationMinThreshold"]]], result)

    @builtins.property
    def recommendation_application_overhead_values(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationOverheadValues"]]]:
        '''recommendation_application_overhead_values block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#recommendation_application_overhead_values OceanRightSizingRule#recommendation_application_overhead_values}
        '''
        result = self._values.get("recommendation_application_overhead_values")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationOverheadValues"]]], result)

    @builtins.property
    def restart_replicas(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#restart_replicas OceanRightSizingRule#restart_replicas}.'''
        result = self._values.get("restart_replicas")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloads",
    jsii_struct_bases=[],
    name_mapping={"namespaces": "namespaces"},
)
class OceanRightSizingRuleDetachWorkloads:
    def __init__(
        self,
        *,
        namespaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloadsNamespaces", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param namespaces: namespaces block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespaces OceanRightSizingRule#namespaces}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__850fe6f62ca0c7bd1e860fdd19b1f85cb5b8aa9a8cdb32d8cf0d7e99a0014463)
            check_type(argname="argument namespaces", value=namespaces, expected_type=type_hints["namespaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespaces": namespaces,
        }

    @builtins.property
    def namespaces(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespaces"]]:
        '''namespaces block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespaces OceanRightSizingRule#namespaces}
        '''
        result = self._values.get("namespaces")
        assert result is not None, "Required property 'namespaces' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespaces"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleDetachWorkloads(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleDetachWorkloadsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__97abda1141bc0a111c1027f77f45f37bc37272713efe5cf2f139457dfce553d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleDetachWorkloadsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9699e94c25e2715917d94fda504bc8f6c3b82425ad11db9e04eafb46e8f9f2a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleDetachWorkloadsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80b93d2d099a57d3f4a2ce475a87fb5e1d1367a22ce973245f6a68828574ca6f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3bda113cad3d9e9cb6a0610c4359a4df2f8aa6ed59570420ffb42c0249a76104)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe61deb236e136d2d42e7e97e78b4d05257b514237b7c1720495e4ae9aa702f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloads]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloads]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloads]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f14b21af0389c97f1e3c86f8f12eb5865606e088de075ad1db333205328cc5d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespaces",
    jsii_struct_bases=[],
    name_mapping={
        "namespace_name": "namespaceName",
        "labels": "labels",
        "workloads": "workloads",
    },
)
class OceanRightSizingRuleDetachWorkloadsNamespaces:
    def __init__(
        self,
        *,
        namespace_name: builtins.str,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloadsNamespacesLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param namespace_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespace_name OceanRightSizingRule#namespace_name}.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#labels OceanRightSizingRule#labels}
        :param workloads: workloads block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workloads OceanRightSizingRule#workloads}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50d48e93ce3f96aa341ebd5162cab51451827787e7e4dd7d239f592ac83edda0)
            check_type(argname="argument namespace_name", value=namespace_name, expected_type=type_hints["namespace_name"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument workloads", value=workloads, expected_type=type_hints["workloads"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespace_name": namespace_name,
        }
        if labels is not None:
            self._values["labels"] = labels
        if workloads is not None:
            self._values["workloads"] = workloads

    @builtins.property
    def namespace_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#namespace_name OceanRightSizingRule#namespace_name}.'''
        result = self._values.get("namespace_name")
        assert result is not None, "Required property 'namespace_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespacesLabels"]]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#labels OceanRightSizingRule#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespacesLabels"]]], result)

    @builtins.property
    def workloads(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads"]]]:
        '''workloads block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workloads OceanRightSizingRule#workloads}
        '''
        result = self._values.get("workloads")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleDetachWorkloadsNamespaces(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class OceanRightSizingRuleDetachWorkloadsNamespacesLabels:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#key OceanRightSizingRule#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#value OceanRightSizingRule#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54c4255de6c97ddf2d49cb4bdec4792ad6b47d689171fb94037538bec669a5cc)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#key OceanRightSizingRule#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#value OceanRightSizingRule#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleDetachWorkloadsNamespacesLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleDetachWorkloadsNamespacesLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9bd596fa10f5bf4fb775ab20722488061d004e67fdaa35eb5a0e9ad8e380ebe9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleDetachWorkloadsNamespacesLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a63580b33e082b422c9857315f00b4da8f0f52c41690b7b4e9263f19e8a5dd3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleDetachWorkloadsNamespacesLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__297ed8190f71a865c36fc79794d315a2cbf9977f41bbb773421dda720adbea7b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7c3a99ef67766540871302650ddc680fa1026bc8dc989b08f4a1ff7aed6bb3d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c8d8d471af46958770a1194a4015fe3f4f34ee90caaea64b4ece47c21554d5c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f118b8212fc9366eddf60408d1903f6e406d2deae3571da2fc89c5ed26ea82a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleDetachWorkloadsNamespacesLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5401331e16343418387082af12808ae06151b93077aeb0cdbcbe9cdb22a36de3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__62a7bf739e7c3b2ba2fab1348825c2e2b252a6ad6e635705399cd14188067764)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a36e225b8226980b47124f3a0920c8f68684e425135f3f4d07e18074b5f0ed01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f3945dc209ff670f544513d3506dab2152f79cbc25fa017993a9fa138cdca25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleDetachWorkloadsNamespacesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f81ac893dcc370f4b16bc379a28ed3e2f7d88b4b135c05d214df311f52e6edb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleDetachWorkloadsNamespacesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a420af20d96801b5f0286610ada1ceaaa93ba555f862d2e99a5f0b5d0bab7be)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleDetachWorkloadsNamespacesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2796ab116565b5c5d277465d085c9373feaf7491657611aa123244b0ef775ca6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8bba9ca87561409ab44ccfa8ebddb80eb26115b0c12f4cf03b9b2629331d254d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4f666d69c217ef1591219d99e3080de569778189a01376ffa47049569ff35e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespaces]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespaces]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0052379942a501ff1649fc5f3e35fc00808f111f11609c48b289fa649c817867)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleDetachWorkloadsNamespacesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89ff007fca970f752e69f988ebd23d7a15165c49172c8c8c6028154a2c5857d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putLabels")
    def put_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespacesLabels, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7a385d6db6a6f7647d8b1900e773a29f7c1e148761c889317a883e650bd0a4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLabels", [value]))

    @jsii.member(jsii_name="putWorkloads")
    def put_workloads(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ca656192812a29b9e1b4ddfd9767a4eb49d9221400392102008f9f7bc6703a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWorkloads", [value]))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetWorkloads")
    def reset_workloads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloads", []))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> OceanRightSizingRuleDetachWorkloadsNamespacesLabelsList:
        return typing.cast(OceanRightSizingRuleDetachWorkloadsNamespacesLabelsList, jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="workloads")
    def workloads(self) -> "OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsList":
        return typing.cast("OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsList", jsii.get(self, "workloads"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceNameInput")
    def namespace_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadsInput")
    def workloads_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads"]]], jsii.get(self, "workloadsInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceName"))

    @namespace_name.setter
    def namespace_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a5a1515751ec2f32b6358f20d597c7fdbe71f4b7c64de013d53944adf91b781)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespaces]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespaces]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespaces]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35189e961f6996d1cd14f881b69e07dc1e538b72a59ce8ac290da1449d57be8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads",
    jsii_struct_bases=[],
    name_mapping={
        "workload_type": "workloadType",
        "regex_name": "regexName",
        "workload_name": "workloadName",
    },
)
class OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads:
    def __init__(
        self,
        *,
        workload_type: builtins.str,
        regex_name: typing.Optional[builtins.str] = None,
        workload_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param workload_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_type OceanRightSizingRule#workload_type}.
        :param regex_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#regex_name OceanRightSizingRule#regex_name}.
        :param workload_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_name OceanRightSizingRule#workload_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afdb3049f2edd8d74ee60eff38f8ac9d8b5ce7307e72dcdfa28f5fd8e0b3524e)
            check_type(argname="argument workload_type", value=workload_type, expected_type=type_hints["workload_type"])
            check_type(argname="argument regex_name", value=regex_name, expected_type=type_hints["regex_name"])
            check_type(argname="argument workload_name", value=workload_name, expected_type=type_hints["workload_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "workload_type": workload_type,
        }
        if regex_name is not None:
            self._values["regex_name"] = regex_name
        if workload_name is not None:
            self._values["workload_name"] = workload_name

    @builtins.property
    def workload_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_type OceanRightSizingRule#workload_type}.'''
        result = self._values.get("workload_type")
        assert result is not None, "Required property 'workload_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def regex_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#regex_name OceanRightSizingRule#regex_name}.'''
        result = self._values.get("regex_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workload_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#workload_name OceanRightSizingRule#workload_name}.'''
        result = self._values.get("workload_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e9aadde141f6159f3e7bbb4a26aed3e22ff5f576abcd465073b32cf12769d1b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e8c4d5d40cfa040671d662298b45d54cbb42ba0a351633e2df028a4ed74df45)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26efd30cf57601fba229916543f5dff0d423574c9e03278d2aa793736a6d8a2e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__07cddb3db7296db0de002190d2b462a0d7a09a56a76cb1481b720d233ff7e86e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e43c4d710becf744054c69993dffc7bb1d4747b12f802cfb2cc8773efee78176)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0213355d1c2dfc819a3301bf4e7f6cab0fba848090d4e6e0ab808905a3ccaa2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d8d543a2ded16102f009acb16aa39e46104b70f7f094d85c1607a65333abf05)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetRegexName")
    def reset_regex_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegexName", []))

    @jsii.member(jsii_name="resetWorkloadName")
    def reset_workload_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkloadName", []))

    @builtins.property
    @jsii.member(jsii_name="regexNameInput")
    def regex_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadNameInput")
    def workload_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadNameInput"))

    @builtins.property
    @jsii.member(jsii_name="workloadTypeInput")
    def workload_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workloadTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="regexName")
    def regex_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regexName"))

    @regex_name.setter
    def regex_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b21992758c0b6d1fa8d636f5c2a0d4cb8f26cd4e2a8cef3e1a66bf48742a35c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regexName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadName")
    def workload_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadName"))

    @workload_name.setter
    def workload_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12ccd243023cfbb44da577b568296ed3c9d5d3642b8d3a5b7ae435155b1489be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workloadType")
    def workload_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workloadType"))

    @workload_type.setter
    def workload_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a885b8736732860bcfaeb1844d14c980c0798b2b72c8a9b69f1c4d6a1e91ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workloadType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01e370b5688c02efa2acfae01a1c63b99a7946845d41ab1f6229bdd17b789731)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleDetachWorkloadsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleDetachWorkloadsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67f012a0495997e0f8fe33d1d4bd3a9617a44bbbba11ad91bbb79809d3327b62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putNamespaces")
    def put_namespaces(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespaces, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a50b40955ca7bfd602b5011ed54f4b0377d16f75928c66573ea75048b7eb021)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNamespaces", [value]))

    @builtins.property
    @jsii.member(jsii_name="namespaces")
    def namespaces(self) -> OceanRightSizingRuleDetachWorkloadsNamespacesList:
        return typing.cast(OceanRightSizingRuleDetachWorkloadsNamespacesList, jsii.get(self, "namespaces"))

    @builtins.property
    @jsii.member(jsii_name="namespacesInput")
    def namespaces_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespaces]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespaces]]], jsii.get(self, "namespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloads]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloads]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloads]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0231adcaa0131cbe0d61dbbad484d35fcb248f0c00b351655e7eadd14abc263b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationBoundaries",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_max": "cpuMax",
        "cpu_min": "cpuMin",
        "memory_max": "memoryMax",
        "memory_min": "memoryMin",
    },
)
class OceanRightSizingRuleRecommendationApplicationBoundaries:
    def __init__(
        self,
        *,
        cpu_max: typing.Optional[jsii.Number] = None,
        cpu_min: typing.Optional[jsii.Number] = None,
        memory_max: typing.Optional[jsii.Number] = None,
        memory_min: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_max: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_max OceanRightSizingRule#cpu_max}.
        :param cpu_min: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_min OceanRightSizingRule#cpu_min}.
        :param memory_max: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_max OceanRightSizingRule#memory_max}.
        :param memory_min: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_min OceanRightSizingRule#memory_min}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d09aa51ccaf7ccc4d5918303580e3cda296ec32555d70f194dbf0590a0eaa33)
            check_type(argname="argument cpu_max", value=cpu_max, expected_type=type_hints["cpu_max"])
            check_type(argname="argument cpu_min", value=cpu_min, expected_type=type_hints["cpu_min"])
            check_type(argname="argument memory_max", value=memory_max, expected_type=type_hints["memory_max"])
            check_type(argname="argument memory_min", value=memory_min, expected_type=type_hints["memory_min"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_max is not None:
            self._values["cpu_max"] = cpu_max
        if cpu_min is not None:
            self._values["cpu_min"] = cpu_min
        if memory_max is not None:
            self._values["memory_max"] = memory_max
        if memory_min is not None:
            self._values["memory_min"] = memory_min

    @builtins.property
    def cpu_max(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_max OceanRightSizingRule#cpu_max}.'''
        result = self._values.get("cpu_max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_min(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_min OceanRightSizingRule#cpu_min}.'''
        result = self._values.get("cpu_min")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_max(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_max OceanRightSizingRule#memory_max}.'''
        result = self._values.get("memory_max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_min(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_min OceanRightSizingRule#memory_min}.'''
        result = self._values.get("memory_min")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationBoundaries(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationBoundariesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationBoundariesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a0eeb87fb0f8ab570b9066a0be262c4e07dc5c081c4ee4c7f7b26869fa2130a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationBoundariesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e71f19b955d88a373bfe108ab648efde0eea6162ebb76d597b7f4b6d8e377286)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationBoundariesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86005ce760b86e41679a5ce54ccaa4efab34434c4c7c1106bcc6cad5b81abd1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2fed5312574f1c388b1e4302de230505debec00bde7006680c2893da37c8cb6a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f5677703aeb89160fcc78f7807f3602a7dc8aac75a216ea4b8bf8a90547a7e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationBoundaries]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationBoundaries]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationBoundaries]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__660809ccb97ca207429c91909d627a4a08b7969292342250ff0e8270a503d89a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationBoundariesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationBoundariesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ad8ad1ef2fbb059dc0f6639cf5147bdea648838bf0e321e5c0590e744fa62d1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCpuMax")
    def reset_cpu_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuMax", []))

    @jsii.member(jsii_name="resetCpuMin")
    def reset_cpu_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuMin", []))

    @jsii.member(jsii_name="resetMemoryMax")
    def reset_memory_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryMax", []))

    @jsii.member(jsii_name="resetMemoryMin")
    def reset_memory_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryMin", []))

    @builtins.property
    @jsii.member(jsii_name="cpuMaxInput")
    def cpu_max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuMinInput")
    def cpu_min_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuMinInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryMaxInput")
    def memory_max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryMinInput")
    def memory_min_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryMinInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuMax")
    def cpu_max(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuMax"))

    @cpu_max.setter
    def cpu_max(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a43371971b7c1f232bfed8b7ae711163706d74e81fc19a0a9fdf0a590abc423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuMin")
    def cpu_min(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuMin"))

    @cpu_min.setter
    def cpu_min(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13858f4823a515ac2cf6a5f9555a0b40ae4728a66510861894ac236570b0916c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryMax")
    def memory_max(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryMax"))

    @memory_max.setter
    def memory_max(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf6655d0bd214a2660af84fb7258cac604dff7aac2cf5ddd8305a1f617822afb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryMin")
    def memory_min(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryMin"))

    @memory_min.setter
    def memory_min(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2d899f8c7535a5a070cc7763e044e8908e5dbbd7127c87a53d210aa2aeb04b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationBoundaries]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationBoundaries]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationBoundaries]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e170f33a97f0415e1aacd2be681e62dcb9562a2d4dc2f108b1707823ce4225a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationHpa",
    jsii_struct_bases=[],
    name_mapping={"allow_hpa_recommendations": "allowHpaRecommendations"},
)
class OceanRightSizingRuleRecommendationApplicationHpa:
    def __init__(
        self,
        *,
        allow_hpa_recommendations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param allow_hpa_recommendations: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#allow_hpa_recommendations OceanRightSizingRule#allow_hpa_recommendations}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b35ebc62aac7854d85595cef5daa68df570478eb1f4416527d5406fee051aab9)
            check_type(argname="argument allow_hpa_recommendations", value=allow_hpa_recommendations, expected_type=type_hints["allow_hpa_recommendations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_hpa_recommendations is not None:
            self._values["allow_hpa_recommendations"] = allow_hpa_recommendations

    @builtins.property
    def allow_hpa_recommendations(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#allow_hpa_recommendations OceanRightSizingRule#allow_hpa_recommendations}.'''
        result = self._values.get("allow_hpa_recommendations")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationHpa(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationHpaList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationHpaList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__450d8b9a47f88d8dc25c5c3962b469cf3bd2765950add390f6ff7990a62993f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationHpaOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f5e7da8a9d0a3eab730d5633245c2049b3434b5d7db3e58e80f8d2c6df3c920)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationHpaOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68d5de123306adb63e89db51a5ff530c93ff03e0d73affd5a29b1167d1df8ce3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1088bd7bd028393314e393cfb94bd34adac9897365e2e788225d51def9c1eab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0930c783beee47de3636fb001f631dd7f890fb4dfcd8ddaf38b18ed8561ce5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationHpa]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationHpa]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationHpa]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d29aa9b19aaf56267ef7f6077596fc36ec4a0b9538376c4649ad4157a2069cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationHpaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationHpaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__723246d82e8e1b0bc4a5af5cf170c764619e42affd9f576fa2a80bc5a4f3fcc3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAllowHpaRecommendations")
    def reset_allow_hpa_recommendations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowHpaRecommendations", []))

    @builtins.property
    @jsii.member(jsii_name="allowHpaRecommendationsInput")
    def allow_hpa_recommendations_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowHpaRecommendationsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowHpaRecommendations")
    def allow_hpa_recommendations(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowHpaRecommendations"))

    @allow_hpa_recommendations.setter
    def allow_hpa_recommendations(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbfad36a7dd2fa830abdbd307c7cabd8615fd5d3a5e250f2b4d5fb4058537147)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowHpaRecommendations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationHpa]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationHpa]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationHpa]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1240109921ffed1b91ed0ecaeaa02a7f4c9964931baabd8cedc38e712b0b99e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervals",
    jsii_struct_bases=[],
    name_mapping={
        "repetition_basis": "repetitionBasis",
        "monthly_repetition_basis": "monthlyRepetitionBasis",
        "weekly_repetition_basis": "weeklyRepetitionBasis",
    },
)
class OceanRightSizingRuleRecommendationApplicationIntervals:
    def __init__(
        self,
        *,
        repetition_basis: builtins.str,
        monthly_repetition_basis: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis", typing.Dict[builtins.str, typing.Any]]]]] = None,
        weekly_repetition_basis: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param repetition_basis: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#repetition_basis OceanRightSizingRule#repetition_basis}.
        :param monthly_repetition_basis: monthly_repetition_basis block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#monthly_repetition_basis OceanRightSizingRule#monthly_repetition_basis}
        :param weekly_repetition_basis: weekly_repetition_basis block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#weekly_repetition_basis OceanRightSizingRule#weekly_repetition_basis}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9265926c98e368447c68265629561869e6ba5f1b7ed2e7ba1fa06c7e6d5a3805)
            check_type(argname="argument repetition_basis", value=repetition_basis, expected_type=type_hints["repetition_basis"])
            check_type(argname="argument monthly_repetition_basis", value=monthly_repetition_basis, expected_type=type_hints["monthly_repetition_basis"])
            check_type(argname="argument weekly_repetition_basis", value=weekly_repetition_basis, expected_type=type_hints["weekly_repetition_basis"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repetition_basis": repetition_basis,
        }
        if monthly_repetition_basis is not None:
            self._values["monthly_repetition_basis"] = monthly_repetition_basis
        if weekly_repetition_basis is not None:
            self._values["weekly_repetition_basis"] = weekly_repetition_basis

    @builtins.property
    def repetition_basis(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#repetition_basis OceanRightSizingRule#repetition_basis}.'''
        result = self._values.get("repetition_basis")
        assert result is not None, "Required property 'repetition_basis' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def monthly_repetition_basis(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis"]]]:
        '''monthly_repetition_basis block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#monthly_repetition_basis OceanRightSizingRule#monthly_repetition_basis}
        '''
        result = self._values.get("monthly_repetition_basis")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis"]]], result)

    @builtins.property
    def weekly_repetition_basis(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis"]]]:
        '''weekly_repetition_basis block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#weekly_repetition_basis OceanRightSizingRule#weekly_repetition_basis}
        '''
        result = self._values.get("weekly_repetition_basis")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationIntervals(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationIntervalsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0039591deda4ed145edc708dc9cfab329bfdf314161c4cfa440b998a40d986fd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35c803f0c68c135bff7cac212eb58b1a71ef542d35a7226c32d6754641875bdd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86d488709dedfbbf303d3c5230b6d96c69a0d3cb0c57511e11212908f9e6006)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d671fe91bd4d8d0634be3663d5a2b8cd726ff0c71a2e4b310806c87ce1fd0f0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a539f5d86bbd10ca62a36200c881359a02a401b2f10b0cd283f7a106490b9e9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervals]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervals]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervals]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cccaafc8c59fe4476be7c4ff9f70f6014ab0431b9436c2959af080c23de47da7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis",
    jsii_struct_bases=[],
    name_mapping={
        "interval_months": "intervalMonths",
        "week_of_the_month": "weekOfTheMonth",
        "weekly_repetition_basis": "weeklyRepetitionBasis",
    },
)
class OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis:
    def __init__(
        self,
        *,
        interval_months: typing.Sequence[jsii.Number],
        week_of_the_month: typing.Sequence[builtins.str],
        weekly_repetition_basis: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param interval_months: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_months OceanRightSizingRule#interval_months}.
        :param week_of_the_month: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#week_of_the_month OceanRightSizingRule#week_of_the_month}.
        :param weekly_repetition_basis: weekly_repetition_basis block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#weekly_repetition_basis OceanRightSizingRule#weekly_repetition_basis}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f60d3efc74875df318e41744c18571073363ff9747cd65a91d414e515f034d)
            check_type(argname="argument interval_months", value=interval_months, expected_type=type_hints["interval_months"])
            check_type(argname="argument week_of_the_month", value=week_of_the_month, expected_type=type_hints["week_of_the_month"])
            check_type(argname="argument weekly_repetition_basis", value=weekly_repetition_basis, expected_type=type_hints["weekly_repetition_basis"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "interval_months": interval_months,
            "week_of_the_month": week_of_the_month,
        }
        if weekly_repetition_basis is not None:
            self._values["weekly_repetition_basis"] = weekly_repetition_basis

    @builtins.property
    def interval_months(self) -> typing.List[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_months OceanRightSizingRule#interval_months}.'''
        result = self._values.get("interval_months")
        assert result is not None, "Required property 'interval_months' is missing"
        return typing.cast(typing.List[jsii.Number], result)

    @builtins.property
    def week_of_the_month(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#week_of_the_month OceanRightSizingRule#week_of_the_month}.'''
        result = self._values.get("week_of_the_month")
        assert result is not None, "Required property 'week_of_the_month' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def weekly_repetition_basis(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis"]]]:
        '''weekly_repetition_basis block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#weekly_repetition_basis OceanRightSizingRule#weekly_repetition_basis}
        '''
        result = self._values.get("weekly_repetition_basis")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b674f136908a8f322469f85004f6c661434aff150a395c859bea36278461aa61)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bd0a428b7c144a55865060df8efaf18262b083b25d0847d349ef18d114a7e1a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb16c65c6a9e88de1ad0342256c72f66920ebebf23a2b1d67e729f095e2dc860)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b3656d65f2b3230a1a1db3aa405ccac370d0693d62f4b31d491cb231612ab1d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c9aaa9c9860ec696867c2b85f714a8123615d6f7d08e03332b7d87ea0fde94a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59aa1e56f6378c540c5751cbee5b5a1f5d8aafb31135ef9364049167dd2b0849)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc7ebb25ea8d08c3f7a3cdffc3a670732ff5e61a001d3c77d3dd41e416f6bc7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putWeeklyRepetitionBasis")
    def put_weekly_repetition_basis(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18791dea866837cc063e2f9e6396ed6acaa827cc8a64ae033040123c47c93874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWeeklyRepetitionBasis", [value]))

    @jsii.member(jsii_name="resetWeeklyRepetitionBasis")
    def reset_weekly_repetition_basis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyRepetitionBasis", []))

    @builtins.property
    @jsii.member(jsii_name="weeklyRepetitionBasis")
    def weekly_repetition_basis(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisList", jsii.get(self, "weeklyRepetitionBasis"))

    @builtins.property
    @jsii.member(jsii_name="intervalMonthsInput")
    def interval_months_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "intervalMonthsInput"))

    @builtins.property
    @jsii.member(jsii_name="weeklyRepetitionBasisInput")
    def weekly_repetition_basis_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis"]]], jsii.get(self, "weeklyRepetitionBasisInput"))

    @builtins.property
    @jsii.member(jsii_name="weekOfTheMonthInput")
    def week_of_the_month_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "weekOfTheMonthInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalMonths")
    def interval_months(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "intervalMonths"))

    @interval_months.setter
    def interval_months(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f200d750cbd895f278c5071327a2d648a4545dd77b01e0cc7922d44b5a67964)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalMonths", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="weekOfTheMonth")
    def week_of_the_month(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "weekOfTheMonth"))

    @week_of_the_month.setter
    def week_of_the_month(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8249c1e88193a33565848369cb69d45e7fe4a594aa9fb3e099875fd9b595aa0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weekOfTheMonth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66c9474318ac379f030e7244a16acafcde83b73c485f31de4ba8c9081b5b00f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis",
    jsii_struct_bases=[],
    name_mapping={
        "interval_days": "intervalDays",
        "interval_hours_end_time": "intervalHoursEndTime",
        "interval_hours_start_time": "intervalHoursStartTime",
    },
)
class OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis:
    def __init__(
        self,
        *,
        interval_days: typing.Sequence[builtins.str],
        interval_hours_end_time: builtins.str,
        interval_hours_start_time: builtins.str,
    ) -> None:
        '''
        :param interval_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_days OceanRightSizingRule#interval_days}.
        :param interval_hours_end_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_end_time OceanRightSizingRule#interval_hours_end_time}.
        :param interval_hours_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_start_time OceanRightSizingRule#interval_hours_start_time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69b5643d3b39748ce8df0b88853e1557774e8f9d33b4ac29b0e05f451fc3699d)
            check_type(argname="argument interval_days", value=interval_days, expected_type=type_hints["interval_days"])
            check_type(argname="argument interval_hours_end_time", value=interval_hours_end_time, expected_type=type_hints["interval_hours_end_time"])
            check_type(argname="argument interval_hours_start_time", value=interval_hours_start_time, expected_type=type_hints["interval_hours_start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "interval_days": interval_days,
            "interval_hours_end_time": interval_hours_end_time,
            "interval_hours_start_time": interval_hours_start_time,
        }

    @builtins.property
    def interval_days(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_days OceanRightSizingRule#interval_days}.'''
        result = self._values.get("interval_days")
        assert result is not None, "Required property 'interval_days' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def interval_hours_end_time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_end_time OceanRightSizingRule#interval_hours_end_time}.'''
        result = self._values.get("interval_hours_end_time")
        assert result is not None, "Required property 'interval_hours_end_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def interval_hours_start_time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_start_time OceanRightSizingRule#interval_hours_start_time}.'''
        result = self._values.get("interval_hours_start_time")
        assert result is not None, "Required property 'interval_hours_start_time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a22358f9d0b179cb08e94d8160e51ce75e55e4d73f23c02485c9cc484841ad49)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50ad70052cef62236b65252f23757aa1ec7f8d44ad22cd45f21491dcc0f53a59)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c182967edb647dc16d7434e59a6a74e768951e93688cbc824144955094def51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a64662289c56d865c912b8e69970066f748e90c66504c75529f8aeeed129fdcd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__660c31ede0ab196b4443108f948a6f02799bd809bc8fdf2f622e6dc3726c08d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d614d990dad2ec789d82ad93fbf7b0b322326fe1a2509ec0fcb737cef1541a0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__44017a368482745ae2b4d4d27f60b16a6c118d349a742d6a9722acadb821c8e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="intervalDaysInput")
    def interval_days_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "intervalDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalHoursEndTimeInput")
    def interval_hours_end_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalHoursEndTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalHoursStartTimeInput")
    def interval_hours_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalHoursStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalDays")
    def interval_days(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "intervalDays"))

    @interval_days.setter
    def interval_days(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3baf638a2e3dab853165377711c58a88fb2db349a3f5d957ad09b5054c5c8c34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalHoursEndTime")
    def interval_hours_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalHoursEndTime"))

    @interval_hours_end_time.setter
    def interval_hours_end_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03b1274eae8ba7b288e7ee815bfbbe302a410f3cf8bf45a6430bba5443f87455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalHoursEndTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalHoursStartTime")
    def interval_hours_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalHoursStartTime"))

    @interval_hours_start_time.setter
    def interval_hours_start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08144f1d6e170685bec5d3d2c0f101d3d1d8f919b835f8c39cf8670a7d5948b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalHoursStartTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acfc9bab51e54187f56ef9c11737169c66acd8886ae6f20569a5b8e2aaf286c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationIntervalsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2a3baeee197088c3b42b420894a862ecbf40d16118044e3e2e60704224faf06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putMonthlyRepetitionBasis")
    def put_monthly_repetition_basis(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89e758c51a74fcd72e3b465069b3f5ba7a66df3fb22bb46fad60eb4adbe3debe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMonthlyRepetitionBasis", [value]))

    @jsii.member(jsii_name="putWeeklyRepetitionBasis")
    def put_weekly_repetition_basis(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58013ba66e73fcc203f21cf6ab7bf7927ead7a1911e7ec371e78804bb3238a9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWeeklyRepetitionBasis", [value]))

    @jsii.member(jsii_name="resetMonthlyRepetitionBasis")
    def reset_monthly_repetition_basis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonthlyRepetitionBasis", []))

    @jsii.member(jsii_name="resetWeeklyRepetitionBasis")
    def reset_weekly_repetition_basis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeeklyRepetitionBasis", []))

    @builtins.property
    @jsii.member(jsii_name="monthlyRepetitionBasis")
    def monthly_repetition_basis(
        self,
    ) -> OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisList:
        return typing.cast(OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisList, jsii.get(self, "monthlyRepetitionBasis"))

    @builtins.property
    @jsii.member(jsii_name="weeklyRepetitionBasis")
    def weekly_repetition_basis(
        self,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisList":
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisList", jsii.get(self, "weeklyRepetitionBasis"))

    @builtins.property
    @jsii.member(jsii_name="monthlyRepetitionBasisInput")
    def monthly_repetition_basis_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]], jsii.get(self, "monthlyRepetitionBasisInput"))

    @builtins.property
    @jsii.member(jsii_name="repetitionBasisInput")
    def repetition_basis_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repetitionBasisInput"))

    @builtins.property
    @jsii.member(jsii_name="weeklyRepetitionBasisInput")
    def weekly_repetition_basis_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis"]]], jsii.get(self, "weeklyRepetitionBasisInput"))

    @builtins.property
    @jsii.member(jsii_name="repetitionBasis")
    def repetition_basis(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repetitionBasis"))

    @repetition_basis.setter
    def repetition_basis(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__798a59605abdafe8255fa2064d6eef9d7755daf2451bcbd1a39ebd0a62873e65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repetitionBasis", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervals]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervals]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervals]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af5253b6b1702559c7cd289d330f6f30b146974cfe5548c0b961539feaac5c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis",
    jsii_struct_bases=[],
    name_mapping={
        "interval_days": "intervalDays",
        "interval_hours_end_time": "intervalHoursEndTime",
        "interval_hours_start_time": "intervalHoursStartTime",
    },
)
class OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis:
    def __init__(
        self,
        *,
        interval_days: typing.Sequence[builtins.str],
        interval_hours_end_time: builtins.str,
        interval_hours_start_time: builtins.str,
    ) -> None:
        '''
        :param interval_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_days OceanRightSizingRule#interval_days}.
        :param interval_hours_end_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_end_time OceanRightSizingRule#interval_hours_end_time}.
        :param interval_hours_start_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_start_time OceanRightSizingRule#interval_hours_start_time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43fe17ac24d4ed434afd64464e69edb74dc0466a00f08065a971b1b0b9611431)
            check_type(argname="argument interval_days", value=interval_days, expected_type=type_hints["interval_days"])
            check_type(argname="argument interval_hours_end_time", value=interval_hours_end_time, expected_type=type_hints["interval_hours_end_time"])
            check_type(argname="argument interval_hours_start_time", value=interval_hours_start_time, expected_type=type_hints["interval_hours_start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "interval_days": interval_days,
            "interval_hours_end_time": interval_hours_end_time,
            "interval_hours_start_time": interval_hours_start_time,
        }

    @builtins.property
    def interval_days(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_days OceanRightSizingRule#interval_days}.'''
        result = self._values.get("interval_days")
        assert result is not None, "Required property 'interval_days' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def interval_hours_end_time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_end_time OceanRightSizingRule#interval_hours_end_time}.'''
        result = self._values.get("interval_hours_end_time")
        assert result is not None, "Required property 'interval_hours_end_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def interval_hours_start_time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#interval_hours_start_time OceanRightSizingRule#interval_hours_start_time}.'''
        result = self._values.get("interval_hours_start_time")
        assert result is not None, "Required property 'interval_hours_start_time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89801ddda06444f7106dfc8e2c8761f0d2a293befd71de0b5102e938ea98ac07)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5943b2b75a0916e00079ca3335d0f4a68d6079b92d4902c8c43194428d6ca35)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44b168af055c250675461b37eb3d578a2dedc45c7613526441636cd0ec7cd3d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__235d5960ab455f131477f8e0a19df056f4ff2422002f11edb79caee5f54707d5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd5e3b83d155eb0ab02a086d69146492c74b62c93db0a8970a637a8c26882c87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__985969d1a70a5b7bc31d3685be3b6a818bc76094ffe6037ab06680f9bfc4ec28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__83ba254794ca656dbc377223fc141ff3c0bd32ed3621612a13768e99c5ac0bb1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="intervalDaysInput")
    def interval_days_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "intervalDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalHoursEndTimeInput")
    def interval_hours_end_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalHoursEndTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalHoursStartTimeInput")
    def interval_hours_start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalHoursStartTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalDays")
    def interval_days(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "intervalDays"))

    @interval_days.setter
    def interval_days(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f19ae91659ca6019f5243525e0c28468687d7198f6bfc78fc3b5193092003543)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalHoursEndTime")
    def interval_hours_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalHoursEndTime"))

    @interval_hours_end_time.setter
    def interval_hours_end_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94ef71b532d40cc8cac594c9a6f495d64f1a96c00949e617f4683c0c022c55d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalHoursEndTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalHoursStartTime")
    def interval_hours_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalHoursStartTime"))

    @interval_hours_start_time.setter
    def interval_hours_start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d60f7cb7b38161759dc9873988eb14aea22636158d5654f128acfb6e977310c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalHoursStartTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fb9a30274072e9811017adab5a1c2652a83f60ca20082a5c3c5dbbd5287ef2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationMinThreshold",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_percentage": "cpuPercentage",
        "memory_percentage": "memoryPercentage",
    },
)
class OceanRightSizingRuleRecommendationApplicationMinThreshold:
    def __init__(
        self,
        *,
        cpu_percentage: typing.Optional[jsii.Number] = None,
        memory_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_percentage OceanRightSizingRule#cpu_percentage}.
        :param memory_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_percentage OceanRightSizingRule#memory_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8c18ae84a623a8f45a96c1db7a2b033a474993c1d85aa7b994325ef0b5081c1)
            check_type(argname="argument cpu_percentage", value=cpu_percentage, expected_type=type_hints["cpu_percentage"])
            check_type(argname="argument memory_percentage", value=memory_percentage, expected_type=type_hints["memory_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_percentage is not None:
            self._values["cpu_percentage"] = cpu_percentage
        if memory_percentage is not None:
            self._values["memory_percentage"] = memory_percentage

    @builtins.property
    def cpu_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_percentage OceanRightSizingRule#cpu_percentage}.'''
        result = self._values.get("cpu_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_percentage OceanRightSizingRule#memory_percentage}.'''
        result = self._values.get("memory_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationMinThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationMinThresholdList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationMinThresholdList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c10bc0a0065eb46512773c042862d4f29c1414a09c6b282b2643b0a0519f5d8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationMinThresholdOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d468216462d334d6ff3e5a344a73225933032bc86460d59d5144b3cdb8d61ca)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationMinThresholdOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e17c1cd2dac574a3a0276c9cabd8cc5fa21119fa3bebca0218f99c979d08011)
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
            type_hints = typing.get_type_hints(_typecheckingstub__01f3228243b5df39e4bf6b5dbb40154094ed0ab9a8b30e1bbd69837c0a772c03)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2c710ef8998bdd456e2e49fcca9f44e8d771aa10cfe98c4cbab82e8cc53fd66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationMinThreshold]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationMinThreshold]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationMinThreshold]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a59e40b8782b83185df3d4d8991f3c88bc77a3e6fe11bdf25e8a5e68d62e6dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationMinThresholdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationMinThresholdOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91da4e58e3f9c5bd2ee31abb49dbc0c5dbe39ed90785502dbaea9d4fb05f45b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCpuPercentage")
    def reset_cpu_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuPercentage", []))

    @jsii.member(jsii_name="resetMemoryPercentage")
    def reset_memory_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryPercentage", []))

    @builtins.property
    @jsii.member(jsii_name="cpuPercentageInput")
    def cpu_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryPercentageInput")
    def memory_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuPercentage")
    def cpu_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuPercentage"))

    @cpu_percentage.setter
    def cpu_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c7ae8061fe961123314ed4897c1968aa4481c0d5174e5768e56e83d75fea5b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPercentage")
    def memory_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPercentage"))

    @memory_percentage.setter
    def memory_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c916b7af4db048b0d47e70eafc3acd8d6088f0b9a07f824ff6ab5b7bfb35b2ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationMinThreshold]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationMinThreshold]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationMinThreshold]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf6c599f1c6d04192174e1f37c87d2afe1ee527add1d1b9c9646fdc9cc63e141)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationOverheadValues",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_percentage": "cpuPercentage",
        "memory_percentage": "memoryPercentage",
    },
)
class OceanRightSizingRuleRecommendationApplicationOverheadValues:
    def __init__(
        self,
        *,
        cpu_percentage: typing.Optional[jsii.Number] = None,
        memory_percentage: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cpu_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_percentage OceanRightSizingRule#cpu_percentage}.
        :param memory_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_percentage OceanRightSizingRule#memory_percentage}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd99063cb71d93c7634f5a5227c60b4f2718973fdf07aa134ee18cbb76591b3)
            check_type(argname="argument cpu_percentage", value=cpu_percentage, expected_type=type_hints["cpu_percentage"])
            check_type(argname="argument memory_percentage", value=memory_percentage, expected_type=type_hints["memory_percentage"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_percentage is not None:
            self._values["cpu_percentage"] = cpu_percentage
        if memory_percentage is not None:
            self._values["memory_percentage"] = memory_percentage

    @builtins.property
    def cpu_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#cpu_percentage OceanRightSizingRule#cpu_percentage}.'''
        result = self._values.get("cpu_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/ocean_right_sizing_rule#memory_percentage OceanRightSizingRule#memory_percentage}.'''
        result = self._values.get("memory_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceanRightSizingRuleRecommendationApplicationOverheadValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceanRightSizingRuleRecommendationApplicationOverheadValuesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationOverheadValuesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__254aefda83ec4b8876b5a1563d3f1b9a9c0e94d9741b0def487e323dfa905526)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceanRightSizingRuleRecommendationApplicationOverheadValuesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd02c5f128257370bc463f2ee03360e77db77852a6460ba808f6831b74ffa1c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceanRightSizingRuleRecommendationApplicationOverheadValuesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b6b033b49299c42c352c8959147ee4d8c8dd3f8a3d5198286e95debc47c8641)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba3284ba7561ac225fe4d9f1a8ac85045289dd09f4432de9b815e52034506799)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16b5e1976420a1511dded73cdfcf8da78938864d78d8cbdca27725565c03af2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationOverheadValues]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationOverheadValues]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationOverheadValues]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bee9bb0f038399d5e42da0430524ff4a55f5dcc424ed0697a4ef8420cecd3c07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceanRightSizingRuleRecommendationApplicationOverheadValuesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceanRightSizingRule.OceanRightSizingRuleRecommendationApplicationOverheadValuesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__093d3b4abbba779c2fb7a22a5a5c70b7bccaf26cd0932110bf33edcd0ca14879)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCpuPercentage")
    def reset_cpu_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuPercentage", []))

    @jsii.member(jsii_name="resetMemoryPercentage")
    def reset_memory_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryPercentage", []))

    @builtins.property
    @jsii.member(jsii_name="cpuPercentageInput")
    def cpu_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="memoryPercentageInput")
    def memory_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuPercentage")
    def cpu_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuPercentage"))

    @cpu_percentage.setter
    def cpu_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c32b1cddf7c420efb08e9e929e5863fe98a9f4d023208f281860fa0c9e845e3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryPercentage")
    def memory_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryPercentage"))

    @memory_percentage.setter
    def memory_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12103240e868fdd0b2eb55aea4722c1cd15d62ee5ca38e12d311bfc2781db2bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationOverheadValues]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationOverheadValues]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationOverheadValues]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__412da4089a5129835cbb106a1383cc391f6e0c1864288ce7526ecb220d4a9dd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceanRightSizingRule",
    "OceanRightSizingRuleAttachWorkloads",
    "OceanRightSizingRuleAttachWorkloadsList",
    "OceanRightSizingRuleAttachWorkloadsNamespaces",
    "OceanRightSizingRuleAttachWorkloadsNamespacesLabels",
    "OceanRightSizingRuleAttachWorkloadsNamespacesLabelsList",
    "OceanRightSizingRuleAttachWorkloadsNamespacesLabelsOutputReference",
    "OceanRightSizingRuleAttachWorkloadsNamespacesList",
    "OceanRightSizingRuleAttachWorkloadsNamespacesOutputReference",
    "OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads",
    "OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsList",
    "OceanRightSizingRuleAttachWorkloadsNamespacesWorkloadsOutputReference",
    "OceanRightSizingRuleAttachWorkloadsOutputReference",
    "OceanRightSizingRuleConfig",
    "OceanRightSizingRuleDetachWorkloads",
    "OceanRightSizingRuleDetachWorkloadsList",
    "OceanRightSizingRuleDetachWorkloadsNamespaces",
    "OceanRightSizingRuleDetachWorkloadsNamespacesLabels",
    "OceanRightSizingRuleDetachWorkloadsNamespacesLabelsList",
    "OceanRightSizingRuleDetachWorkloadsNamespacesLabelsOutputReference",
    "OceanRightSizingRuleDetachWorkloadsNamespacesList",
    "OceanRightSizingRuleDetachWorkloadsNamespacesOutputReference",
    "OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads",
    "OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsList",
    "OceanRightSizingRuleDetachWorkloadsNamespacesWorkloadsOutputReference",
    "OceanRightSizingRuleDetachWorkloadsOutputReference",
    "OceanRightSizingRuleRecommendationApplicationBoundaries",
    "OceanRightSizingRuleRecommendationApplicationBoundariesList",
    "OceanRightSizingRuleRecommendationApplicationBoundariesOutputReference",
    "OceanRightSizingRuleRecommendationApplicationHpa",
    "OceanRightSizingRuleRecommendationApplicationHpaList",
    "OceanRightSizingRuleRecommendationApplicationHpaOutputReference",
    "OceanRightSizingRuleRecommendationApplicationIntervals",
    "OceanRightSizingRuleRecommendationApplicationIntervalsList",
    "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis",
    "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisList",
    "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisOutputReference",
    "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis",
    "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisList",
    "OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasisOutputReference",
    "OceanRightSizingRuleRecommendationApplicationIntervalsOutputReference",
    "OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis",
    "OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisList",
    "OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasisOutputReference",
    "OceanRightSizingRuleRecommendationApplicationMinThreshold",
    "OceanRightSizingRuleRecommendationApplicationMinThresholdList",
    "OceanRightSizingRuleRecommendationApplicationMinThresholdOutputReference",
    "OceanRightSizingRuleRecommendationApplicationOverheadValues",
    "OceanRightSizingRuleRecommendationApplicationOverheadValuesList",
    "OceanRightSizingRuleRecommendationApplicationOverheadValuesOutputReference",
]

publication.publish()

def _typecheckingstub__fa26bb85f524a60b527ad3cb1e375d316bd2766476e2e27dd8bc884b9ac669fa(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    recommendation_application_intervals: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervals, typing.Dict[builtins.str, typing.Any]]]],
    rule_name: builtins.str,
    attach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
    detach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
    exclude_preliminary_recommendations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    ocean_id: typing.Optional[builtins.str] = None,
    recommendation_application_boundaries: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationBoundaries, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_hpa: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationHpa, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_min_threshold: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationMinThreshold, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_overhead_values: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationOverheadValues, typing.Dict[builtins.str, typing.Any]]]]] = None,
    restart_replicas: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a61bd7cb8eb8e47076583133307f70c1e5e14ca72f597cb45b3184129be3623a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0957f54a82ccab02a92c090a52ba507bcde36247baf6f14baf7a7bf6939d2f28(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloads, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c150752c03c2f71537846c611906bac39726a6ea815cb4363456cbcef4d42d60(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloads, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e1829e2026a0801ac53b1ac8dfd3ce4acb70afbd598431ff5925e1f300077d5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationBoundaries, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a92732a87ab496ad3ff15e5bf764553939cb76d3319e34197d55f91e4a40bb1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationHpa, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6739e33e0f15149c24996bc0485ac8d1fcc4df3b9afc1664642e840f6b54882d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervals, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7cb298d260c1cddb513f107e62a6ead88b56e3247516c180192580611e67d9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationMinThreshold, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f1b51e0c8c62519aacf9ca3890448ac9116dc3a0b0b58cce721a1cc2c0685f6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationOverheadValues, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cc73b2ecb7475f5c1654f139661e5a9fffacfe1df96e8cf0a872a3b52e251fc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__703c529605f2dd55f96945a70922720f7230899f92e5d933c4c5b8ebe646cffe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e588cb0b729f78d54078af300245d1e3c95c6e1f4c6988db3f1edcf7e295d65e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17935e34d8efacd4b5a40cc2915d3ca979497f498020322f554b66d243a11e9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca1da33853da973f330668ebe773b7cb114bdb37d9f7b23ca551dbc75651c6d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e15b392454437dcff8d788eb02f89c88e29b7b113795860336ec1683213c7bfe(
    *,
    namespaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa54cb5255544d7341515b6c39ec4553fecbba830135880905bc03c4e3550fd5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810feda6168a537bcb6eb31438dda2fa46de17f6b961db28906e46c39a760fc1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2716843c235b91a0777f9e151256998125eddcd65a721189cd28453304463b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2187190791eab87a4b5d77988e30090165acd42cb266ebefd974df59a7353e3a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48d842cde660202b965566ce68ff4b438b3ff8a6fab6742271acc859c9129160(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a347c803b3ff552b895a097283e905989fda45eb76631e5b8e046b661230210b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloads]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e7c487d4d2eddf69180b7bf44cc6ba71270175cdaac19a9ec2cd3ac3e0516ab(
    *,
    namespace_name: builtins.str,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespacesLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12cbdf6a46dddf9aa1044bab04062731a8de389dafe14353fa52acf49010b4e0(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43940318b40f79cd85b072c9b284d6fcdff44b884ba5e359a84349a4a35558b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__426cd2feb093ec4e07dcc6c807493bfa8c77de2a64edf3ee9d8ba1f254ebc450(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9557e6d437d3e2d66d0438f5a89e16e0f8e4afb09cdf761a709f7a618b7e7e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7085465e8bd305f74fa8a2477b64e99b549d4dacbaf39c9a16b7fbd6988ec6bb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41904e147fe6c600be15909a88614dbfa71b64ce6c91760fbbbc13698ab5fa3b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb59492f7b164aad05813c4cd978051185ee5757ee44e036622b3c5fc70ee5a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87660d09a4c19b3f61ed45e6b182346b6bdcbd49f9eaae819e7689a6b07ce301(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d8912d3042e071f6e08da7a02fdb28f7622dd18556d858b246a33e86b6a52a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77cecd00725ccea1aa2a6ab8ee64658f57df6e5ac65e123d434af9ec8341d463(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__867af875624e6a34abb896eef6910d1fa16106960c96e6d79aeb3fef1ffa5aac(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677526cc4ed492732fdd3ffa4aa909dc75d19c26de942b5918ddb97c537a91f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6466e936d7f4642049f29e7bfe237ce9871a69db77e45d223d89fd946891c1bf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d470053bd1c99106fa43aeb3960eb34e6322b3438fd2bfb97b670fe4f6b842(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef5d2ee257a1691b3172b7b58055cf9ea6be35c7428a924f620ba51352a00e0e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__892a9f33365ac0af980cce5937d54e5554a0d3d79990bc30877df951346ce0ca(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98c62fa6faa6c78c06290ca5f076d36abea689f2c888f7dddcf66a7174d348b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6b64e9f9beabc2f3a87fe52052f82cf3d188c9fc3f93058d4e2bbadc98c27cf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e69ddab2c0c9c649b2fdc49e7fc0e74af1f87acaac059d3aecdc7421ade37d0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespacesLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9897083f9a57fdcc794925613c2e050608a3b7c4aa334c1ff317e80a5992bec1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d34971c0c54dd09bb15bec5a91bb643eb0dc1c6b8f433868cf6f51fd3fd49080(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97f27ebe75bf506616e2e824a6c99f3258911cace7451859595eb1853197a5d1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc94e48e07e1afce7565229ed4cf21ebc5322601edebe2ae7369023cf0f2c2dc(
    *,
    workload_type: builtins.str,
    regex_name: typing.Optional[builtins.str] = None,
    workload_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35b187376effabb3c71dd678410ce1502fb4a54a5788caa1bdd009e2e6378238(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f2db7f065039321b0e1e7fe3cafc623c3f2f021321fadac9f003400f7a5d946(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4be6e13d2c70992f81684fe3210f024f6213d040197c39d3c5b32f719bbe8416(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b78723a66bedcf484b28757216943cd028a2e553b550d00a7f87dd65fa2f99(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0033969cb873575b2a6cb5ade77b69c071318de42eae50e62bb0aac3aeb61322(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb5462945e02ad5702e6107dcb31783f1b46c030e1593e6a49a8076549ca110(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b35511160717d66f5fc59fb8965fd7e3bbf7f626819820c783280cbb6bebd3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d2a989c4bf8b1ce94d830e1760a6db9c7742e796c5d10c8b1e743827abd694d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d261f49564b905cc4292fca6c1a046fc6a2cadb8ec095eeff8ac447cbf70a8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7adaa51f22ffd5c91cbeac538728481a102622266b21014257df9dc023edf43f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e76b393509c8b1b894c8de64d3f1874e4c9c669aeceea0aeb76a0590c3bc210(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloadsNamespacesWorkloads]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c249cddf8b51c5f9d61669c2f76d7cbb08b148b6a980d86ec1ab307dbc16702(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__339f0e45b533751497efdb079b52c4252173a7c951be1e6d477544b45384466e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloadsNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bf3617a863a04f8e4272f0f64cf2fb488bc48336edf12ab8e0d311c72a81079(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleAttachWorkloads]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e04bbd12d1fe27d52aacecc88cd22a4ecc424576b3df22febe23d7781cb65411(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_intervals: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervals, typing.Dict[builtins.str, typing.Any]]]],
    rule_name: builtins.str,
    attach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleAttachWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
    detach_workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
    exclude_preliminary_recommendations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    ocean_id: typing.Optional[builtins.str] = None,
    recommendation_application_boundaries: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationBoundaries, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_hpa: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationHpa, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_min_threshold: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationMinThreshold, typing.Dict[builtins.str, typing.Any]]]]] = None,
    recommendation_application_overhead_values: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationOverheadValues, typing.Dict[builtins.str, typing.Any]]]]] = None,
    restart_replicas: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__850fe6f62ca0c7bd1e860fdd19b1f85cb5b8aa9a8cdb32d8cf0d7e99a0014463(
    *,
    namespaces: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97abda1141bc0a111c1027f77f45f37bc37272713efe5cf2f139457dfce553d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9699e94c25e2715917d94fda504bc8f6c3b82425ad11db9e04eafb46e8f9f2a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b93d2d099a57d3f4a2ce475a87fb5e1d1367a22ce973245f6a68828574ca6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bda113cad3d9e9cb6a0610c4359a4df2f8aa6ed59570420ffb42c0249a76104(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe61deb236e136d2d42e7e97e78b4d05257b514237b7c1720495e4ae9aa702f5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f14b21af0389c97f1e3c86f8f12eb5865606e088de075ad1db333205328cc5d4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloads]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50d48e93ce3f96aa341ebd5162cab51451827787e7e4dd7d239f592ac83edda0(
    *,
    namespace_name: builtins.str,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespacesLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workloads: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54c4255de6c97ddf2d49cb4bdec4792ad6b47d689171fb94037538bec669a5cc(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd596fa10f5bf4fb775ab20722488061d004e67fdaa35eb5a0e9ad8e380ebe9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a63580b33e082b422c9857315f00b4da8f0f52c41690b7b4e9263f19e8a5dd3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__297ed8190f71a865c36fc79794d315a2cbf9977f41bbb773421dda720adbea7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7c3a99ef67766540871302650ddc680fa1026bc8dc989b08f4a1ff7aed6bb3d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d8d471af46958770a1194a4015fe3f4f34ee90caaea64b4ece47c21554d5c8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f118b8212fc9366eddf60408d1903f6e406d2deae3571da2fc89c5ed26ea82a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5401331e16343418387082af12808ae06151b93077aeb0cdbcbe9cdb22a36de3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62a7bf739e7c3b2ba2fab1348825c2e2b252a6ad6e635705399cd14188067764(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a36e225b8226980b47124f3a0920c8f68684e425135f3f4d07e18074b5f0ed01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f3945dc209ff670f544513d3506dab2152f79cbc25fa017993a9fa138cdca25(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f81ac893dcc370f4b16bc379a28ed3e2f7d88b4b135c05d214df311f52e6edb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a420af20d96801b5f0286610ada1ceaaa93ba555f862d2e99a5f0b5d0bab7be(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2796ab116565b5c5d277465d085c9373feaf7491657611aa123244b0ef775ca6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bba9ca87561409ab44ccfa8ebddb80eb26115b0c12f4cf03b9b2629331d254d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f666d69c217ef1591219d99e3080de569778189a01376ffa47049569ff35e3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0052379942a501ff1649fc5f3e35fc00808f111f11609c48b289fa649c817867(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespaces]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89ff007fca970f752e69f988ebd23d7a15165c49172c8c8c6028154a2c5857d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7a385d6db6a6f7647d8b1900e773a29f7c1e148761c889317a883e650bd0a4c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespacesLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ca656192812a29b9e1b4ddfd9767a4eb49d9221400392102008f9f7bc6703a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a5a1515751ec2f32b6358f20d597c7fdbe71f4b7c64de013d53944adf91b781(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35189e961f6996d1cd14f881b69e07dc1e538b72a59ce8ac290da1449d57be8a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespaces]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afdb3049f2edd8d74ee60eff38f8ac9d8b5ce7307e72dcdfa28f5fd8e0b3524e(
    *,
    workload_type: builtins.str,
    regex_name: typing.Optional[builtins.str] = None,
    workload_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e9aadde141f6159f3e7bbb4a26aed3e22ff5f576abcd465073b32cf12769d1b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e8c4d5d40cfa040671d662298b45d54cbb42ba0a351633e2df028a4ed74df45(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26efd30cf57601fba229916543f5dff0d423574c9e03278d2aa793736a6d8a2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07cddb3db7296db0de002190d2b462a0d7a09a56a76cb1481b720d233ff7e86e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e43c4d710becf744054c69993dffc7bb1d4747b12f802cfb2cc8773efee78176(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0213355d1c2dfc819a3301bf4e7f6cab0fba848090d4e6e0ab808905a3ccaa2b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d8d543a2ded16102f009acb16aa39e46104b70f7f094d85c1607a65333abf05(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b21992758c0b6d1fa8d636f5c2a0d4cb8f26cd4e2a8cef3e1a66bf48742a35c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12ccd243023cfbb44da577b568296ed3c9d5d3642b8d3a5b7ae435155b1489be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a885b8736732860bcfaeb1844d14c980c0798b2b72c8a9b69f1c4d6a1e91ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01e370b5688c02efa2acfae01a1c63b99a7946845d41ab1f6229bdd17b789731(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloadsNamespacesWorkloads]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67f012a0495997e0f8fe33d1d4bd3a9617a44bbbba11ad91bbb79809d3327b62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a50b40955ca7bfd602b5011ed54f4b0377d16f75928c66573ea75048b7eb021(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleDetachWorkloadsNamespaces, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0231adcaa0131cbe0d61dbbad484d35fcb248f0c00b351655e7eadd14abc263b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleDetachWorkloads]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d09aa51ccaf7ccc4d5918303580e3cda296ec32555d70f194dbf0590a0eaa33(
    *,
    cpu_max: typing.Optional[jsii.Number] = None,
    cpu_min: typing.Optional[jsii.Number] = None,
    memory_max: typing.Optional[jsii.Number] = None,
    memory_min: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a0eeb87fb0f8ab570b9066a0be262c4e07dc5c081c4ee4c7f7b26869fa2130a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71f19b955d88a373bfe108ab648efde0eea6162ebb76d597b7f4b6d8e377286(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86005ce760b86e41679a5ce54ccaa4efab34434c4c7c1106bcc6cad5b81abd1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fed5312574f1c388b1e4302de230505debec00bde7006680c2893da37c8cb6a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f5677703aeb89160fcc78f7807f3602a7dc8aac75a216ea4b8bf8a90547a7e9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__660809ccb97ca207429c91909d627a4a08b7969292342250ff0e8270a503d89a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationBoundaries]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ad8ad1ef2fbb059dc0f6639cf5147bdea648838bf0e321e5c0590e744fa62d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a43371971b7c1f232bfed8b7ae711163706d74e81fc19a0a9fdf0a590abc423(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13858f4823a515ac2cf6a5f9555a0b40ae4728a66510861894ac236570b0916c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf6655d0bd214a2660af84fb7258cac604dff7aac2cf5ddd8305a1f617822afb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2d899f8c7535a5a070cc7763e044e8908e5dbbd7127c87a53d210aa2aeb04b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e170f33a97f0415e1aacd2be681e62dcb9562a2d4dc2f108b1707823ce4225a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationBoundaries]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35ebc62aac7854d85595cef5daa68df570478eb1f4416527d5406fee051aab9(
    *,
    allow_hpa_recommendations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__450d8b9a47f88d8dc25c5c3962b469cf3bd2765950add390f6ff7990a62993f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f5e7da8a9d0a3eab730d5633245c2049b3434b5d7db3e58e80f8d2c6df3c920(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68d5de123306adb63e89db51a5ff530c93ff03e0d73affd5a29b1167d1df8ce3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1088bd7bd028393314e393cfb94bd34adac9897365e2e788225d51def9c1eab(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0930c783beee47de3636fb001f631dd7f890fb4dfcd8ddaf38b18ed8561ce5e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d29aa9b19aaf56267ef7f6077596fc36ec4a0b9538376c4649ad4157a2069cc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationHpa]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__723246d82e8e1b0bc4a5af5cf170c764619e42affd9f576fa2a80bc5a4f3fcc3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbfad36a7dd2fa830abdbd307c7cabd8615fd5d3a5e250f2b4d5fb4058537147(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1240109921ffed1b91ed0ecaeaa02a7f4c9964931baabd8cedc38e712b0b99e9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationHpa]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9265926c98e368447c68265629561869e6ba5f1b7ed2e7ba1fa06c7e6d5a3805(
    *,
    repetition_basis: builtins.str,
    monthly_repetition_basis: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]]] = None,
    weekly_repetition_basis: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0039591deda4ed145edc708dc9cfab329bfdf314161c4cfa440b998a40d986fd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35c803f0c68c135bff7cac212eb58b1a71ef542d35a7226c32d6754641875bdd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86d488709dedfbbf303d3c5230b6d96c69a0d3cb0c57511e11212908f9e6006(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d671fe91bd4d8d0634be3663d5a2b8cd726ff0c71a2e4b310806c87ce1fd0f0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a539f5d86bbd10ca62a36200c881359a02a401b2f10b0cd283f7a106490b9e9c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cccaafc8c59fe4476be7c4ff9f70f6014ab0431b9436c2959af080c23de47da7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervals]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f60d3efc74875df318e41744c18571073363ff9747cd65a91d414e515f034d(
    *,
    interval_months: typing.Sequence[jsii.Number],
    week_of_the_month: typing.Sequence[builtins.str],
    weekly_repetition_basis: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b674f136908a8f322469f85004f6c661434aff150a395c859bea36278461aa61(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bd0a428b7c144a55865060df8efaf18262b083b25d0847d349ef18d114a7e1a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb16c65c6a9e88de1ad0342256c72f66920ebebf23a2b1d67e729f095e2dc860(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b3656d65f2b3230a1a1db3aa405ccac370d0693d62f4b31d491cb231612ab1d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c9aaa9c9860ec696867c2b85f714a8123615d6f7d08e03332b7d87ea0fde94a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59aa1e56f6378c540c5751cbee5b5a1f5d8aafb31135ef9364049167dd2b0849(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc7ebb25ea8d08c3f7a3cdffc3a670732ff5e61a001d3c77d3dd41e416f6bc7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18791dea866837cc063e2f9e6396ed6acaa827cc8a64ae033040123c47c93874(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f200d750cbd895f278c5071327a2d648a4545dd77b01e0cc7922d44b5a67964(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8249c1e88193a33565848369cb69d45e7fe4a594aa9fb3e099875fd9b595aa0b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66c9474318ac379f030e7244a16acafcde83b73c485f31de4ba8c9081b5b00f0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b5643d3b39748ce8df0b88853e1557774e8f9d33b4ac29b0e05f451fc3699d(
    *,
    interval_days: typing.Sequence[builtins.str],
    interval_hours_end_time: builtins.str,
    interval_hours_start_time: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a22358f9d0b179cb08e94d8160e51ce75e55e4d73f23c02485c9cc484841ad49(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50ad70052cef62236b65252f23757aa1ec7f8d44ad22cd45f21491dcc0f53a59(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c182967edb647dc16d7434e59a6a74e768951e93688cbc824144955094def51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a64662289c56d865c912b8e69970066f748e90c66504c75529f8aeeed129fdcd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__660c31ede0ab196b4443108f948a6f02799bd809bc8fdf2f622e6dc3726c08d4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d614d990dad2ec789d82ad93fbf7b0b322326fe1a2509ec0fcb737cef1541a0a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44017a368482745ae2b4d4d27f60b16a6c118d349a742d6a9722acadb821c8e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3baf638a2e3dab853165377711c58a88fb2db349a3f5d957ad09b5054c5c8c34(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03b1274eae8ba7b288e7ee815bfbbe302a410f3cf8bf45a6430bba5443f87455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08144f1d6e170685bec5d3d2c0f101d3d1d8f919b835f8c39cf8670a7d5948b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acfc9bab51e54187f56ef9c11737169c66acd8886ae6f20569a5b8e2aaf286c0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasisWeeklyRepetitionBasis]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a3baeee197088c3b42b420894a862ecbf40d16118044e3e2e60704224faf06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e758c51a74fcd72e3b465069b3f5ba7a66df3fb22bb46fad60eb4adbe3debe(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsMonthlyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58013ba66e73fcc203f21cf6ab7bf7927ead7a1911e7ec371e78804bb3238a9d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__798a59605abdafe8255fa2064d6eef9d7755daf2451bcbd1a39ebd0a62873e65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af5253b6b1702559c7cd289d330f6f30b146974cfe5548c0b961539feaac5c72(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervals]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43fe17ac24d4ed434afd64464e69edb74dc0466a00f08065a971b1b0b9611431(
    *,
    interval_days: typing.Sequence[builtins.str],
    interval_hours_end_time: builtins.str,
    interval_hours_start_time: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89801ddda06444f7106dfc8e2c8761f0d2a293befd71de0b5102e938ea98ac07(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5943b2b75a0916e00079ca3335d0f4a68d6079b92d4902c8c43194428d6ca35(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44b168af055c250675461b37eb3d578a2dedc45c7613526441636cd0ec7cd3d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__235d5960ab455f131477f8e0a19df056f4ff2422002f11edb79caee5f54707d5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd5e3b83d155eb0ab02a086d69146492c74b62c93db0a8970a637a8c26882c87(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__985969d1a70a5b7bc31d3685be3b6a818bc76094ffe6037ab06680f9bfc4ec28(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83ba254794ca656dbc377223fc141ff3c0bd32ed3621612a13768e99c5ac0bb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f19ae91659ca6019f5243525e0c28468687d7198f6bfc78fc3b5193092003543(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94ef71b532d40cc8cac594c9a6f495d64f1a96c00949e617f4683c0c022c55d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d60f7cb7b38161759dc9873988eb14aea22636158d5654f128acfb6e977310c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fb9a30274072e9811017adab5a1c2652a83f60ca20082a5c3c5dbbd5287ef2c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationIntervalsWeeklyRepetitionBasis]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8c18ae84a623a8f45a96c1db7a2b033a474993c1d85aa7b994325ef0b5081c1(
    *,
    cpu_percentage: typing.Optional[jsii.Number] = None,
    memory_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c10bc0a0065eb46512773c042862d4f29c1414a09c6b282b2643b0a0519f5d8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d468216462d334d6ff3e5a344a73225933032bc86460d59d5144b3cdb8d61ca(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e17c1cd2dac574a3a0276c9cabd8cc5fa21119fa3bebca0218f99c979d08011(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01f3228243b5df39e4bf6b5dbb40154094ed0ab9a8b30e1bbd69837c0a772c03(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c710ef8998bdd456e2e49fcca9f44e8d771aa10cfe98c4cbab82e8cc53fd66(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a59e40b8782b83185df3d4d8991f3c88bc77a3e6fe11bdf25e8a5e68d62e6dd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationMinThreshold]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91da4e58e3f9c5bd2ee31abb49dbc0c5dbe39ed90785502dbaea9d4fb05f45b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c7ae8061fe961123314ed4897c1968aa4481c0d5174e5768e56e83d75fea5b1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c916b7af4db048b0d47e70eafc3acd8d6088f0b9a07f824ff6ab5b7bfb35b2ab(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf6c599f1c6d04192174e1f37c87d2afe1ee527add1d1b9c9646fdc9cc63e141(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationMinThreshold]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd99063cb71d93c7634f5a5227c60b4f2718973fdf07aa134ee18cbb76591b3(
    *,
    cpu_percentage: typing.Optional[jsii.Number] = None,
    memory_percentage: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__254aefda83ec4b8876b5a1563d3f1b9a9c0e94d9741b0def487e323dfa905526(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd02c5f128257370bc463f2ee03360e77db77852a6460ba808f6831b74ffa1c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b6b033b49299c42c352c8959147ee4d8c8dd3f8a3d5198286e95debc47c8641(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba3284ba7561ac225fe4d9f1a8ac85045289dd09f4432de9b815e52034506799(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16b5e1976420a1511dded73cdfcf8da78938864d78d8cbdca27725565c03af2f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee9bb0f038399d5e42da0430524ff4a55f5dcc424ed0697a4ef8420cecd3c07(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceanRightSizingRuleRecommendationApplicationOverheadValues]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__093d3b4abbba779c2fb7a22a5a5c70b7bccaf26cd0932110bf33edcd0ca14879(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c32b1cddf7c420efb08e9e929e5863fe98a9f4d023208f281860fa0c9e845e3a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12103240e868fdd0b2eb55aea4722c1cd15d62ee5ca38e12d311bfc2781db2bd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__412da4089a5129835cbb106a1383cc391f6e0c1864288ce7526ecb220d4a9dd7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceanRightSizingRuleRecommendationApplicationOverheadValues]],
) -> None:
    """Type checking stubs"""
    pass
