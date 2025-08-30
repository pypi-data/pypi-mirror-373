r'''
# `spotinst_oceancd_strategy`

Refer to the Terraform Registry for docs: [`spotinst_oceancd_strategy`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy).
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


class OceancdStrategy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategy",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy spotinst_oceancd_strategy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        strategy_name: builtins.str,
        canary: typing.Optional[typing.Union["OceancdStrategyCanary", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        rolling: typing.Optional[typing.Union["OceancdStrategyRolling", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy spotinst_oceancd_strategy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param strategy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#strategy_name OceancdStrategy#strategy_name}.
        :param canary: canary block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#canary OceancdStrategy#canary}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#id OceancdStrategy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rolling: rolling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#rolling OceancdStrategy#rolling}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28611b9d23fa8b84337b291924c2f7e3149c8b4aca37b169c6adc263d07ddc53)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceancdStrategyConfig(
            strategy_name=strategy_name,
            canary=canary,
            id=id,
            rolling=rolling,
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
        '''Generates CDKTF code for importing a OceancdStrategy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceancdStrategy to import.
        :param import_from_id: The id of the existing OceancdStrategy that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceancdStrategy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__486753df8bc2430ae34d171c83a1849dc53f0933879b2d7126d775fe63a84645)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCanary")
    def put_canary(
        self,
        *,
        steps: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyCanarySteps", typing.Dict[builtins.str, typing.Any]]]],
        background_verification: typing.Optional[typing.Union["OceancdStrategyCanaryBackgroundVerification", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param steps: steps block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps OceancdStrategy#steps}
        :param background_verification: background_verification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#background_verification OceancdStrategy#background_verification}
        '''
        value = OceancdStrategyCanary(
            steps=steps, background_verification=background_verification
        )

        return typing.cast(None, jsii.invoke(self, "putCanary", [value]))

    @jsii.member(jsii_name="putRolling")
    def put_rolling(
        self,
        *,
        steps: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyRollingSteps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param steps: steps block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps OceancdStrategy#steps}
        '''
        value = OceancdStrategyRolling(steps=steps)

        return typing.cast(None, jsii.invoke(self, "putRolling", [value]))

    @jsii.member(jsii_name="resetCanary")
    def reset_canary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCanary", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRolling")
    def reset_rolling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRolling", []))

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
    @jsii.member(jsii_name="canary")
    def canary(self) -> "OceancdStrategyCanaryOutputReference":
        return typing.cast("OceancdStrategyCanaryOutputReference", jsii.get(self, "canary"))

    @builtins.property
    @jsii.member(jsii_name="rolling")
    def rolling(self) -> "OceancdStrategyRollingOutputReference":
        return typing.cast("OceancdStrategyRollingOutputReference", jsii.get(self, "rolling"))

    @builtins.property
    @jsii.member(jsii_name="canaryInput")
    def canary_input(self) -> typing.Optional["OceancdStrategyCanary"]:
        return typing.cast(typing.Optional["OceancdStrategyCanary"], jsii.get(self, "canaryInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="rollingInput")
    def rolling_input(self) -> typing.Optional["OceancdStrategyRolling"]:
        return typing.cast(typing.Optional["OceancdStrategyRolling"], jsii.get(self, "rollingInput"))

    @builtins.property
    @jsii.member(jsii_name="strategyNameInput")
    def strategy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "strategyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a4686fe8020550fed9c1762200cabb563acb6da446a09521dbc1eec05f39d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strategyName")
    def strategy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "strategyName"))

    @strategy_name.setter
    def strategy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8bc9a846f8283bf4008d5fc9c96cab3c4c798f79884e87ca3d39799c7e354cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strategyName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanary",
    jsii_struct_bases=[],
    name_mapping={
        "steps": "steps",
        "background_verification": "backgroundVerification",
    },
)
class OceancdStrategyCanary:
    def __init__(
        self,
        *,
        steps: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyCanarySteps", typing.Dict[builtins.str, typing.Any]]]],
        background_verification: typing.Optional[typing.Union["OceancdStrategyCanaryBackgroundVerification", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param steps: steps block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps OceancdStrategy#steps}
        :param background_verification: background_verification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#background_verification OceancdStrategy#background_verification}
        '''
        if isinstance(background_verification, dict):
            background_verification = OceancdStrategyCanaryBackgroundVerification(**background_verification)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83648f82c2bebe31311ba07d982cd2e32d68d6e1016fbfb3c3dc722ea640199d)
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
            check_type(argname="argument background_verification", value=background_verification, expected_type=type_hints["background_verification"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "steps": steps,
        }
        if background_verification is not None:
            self._values["background_verification"] = background_verification

    @builtins.property
    def steps(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyCanarySteps"]]:
        '''steps block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps OceancdStrategy#steps}
        '''
        result = self._values.get("steps")
        assert result is not None, "Required property 'steps' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyCanarySteps"]], result)

    @builtins.property
    def background_verification(
        self,
    ) -> typing.Optional["OceancdStrategyCanaryBackgroundVerification"]:
        '''background_verification block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#background_verification OceancdStrategy#background_verification}
        '''
        result = self._values.get("background_verification")
        return typing.cast(typing.Optional["OceancdStrategyCanaryBackgroundVerification"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanary(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryBackgroundVerification",
    jsii_struct_bases=[],
    name_mapping={"template_names": "templateNames"},
)
class OceancdStrategyCanaryBackgroundVerification:
    def __init__(self, *, template_names: typing.Sequence[builtins.str]) -> None:
        '''
        :param template_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e0fb7822a66bdbdcb57a88f94e722ff9771f02079be1c11c61ae4f0b576158a)
            check_type(argname="argument template_names", value=template_names, expected_type=type_hints["template_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "template_names": template_names,
        }

    @builtins.property
    def template_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.'''
        result = self._values.get("template_names")
        assert result is not None, "Required property 'template_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryBackgroundVerification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyCanaryBackgroundVerificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryBackgroundVerificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff17a585f7d2cf0aaef82f5df7573e06b103e1229295ac3963ccaf863aad844f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="templateNamesInput")
    def template_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "templateNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="templateNames")
    def template_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "templateNames"))

    @template_names.setter
    def template_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f26be4c59379f462ad7b84f76e7cbdb1f94eecfb221ae7e393ace749fe74129)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdStrategyCanaryBackgroundVerification]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryBackgroundVerification], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyCanaryBackgroundVerification],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2f8d910af07e49f3ca958f1b1ffccbff5b9e7229fbb83ad937f278db8e53727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdStrategyCanaryOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9852bee7d4dddbd5d8f497dc11c50d4fe9cb0d80c31205d2b59065967224c0fe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBackgroundVerification")
    def put_background_verification(
        self,
        *,
        template_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param template_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.
        '''
        value = OceancdStrategyCanaryBackgroundVerification(
            template_names=template_names
        )

        return typing.cast(None, jsii.invoke(self, "putBackgroundVerification", [value]))

    @jsii.member(jsii_name="putSteps")
    def put_steps(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyCanarySteps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__677143b8cef6c0de12fa7189a33ce604a7925edb9ecf8191509db9fef6cc9ed4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSteps", [value]))

    @jsii.member(jsii_name="resetBackgroundVerification")
    def reset_background_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackgroundVerification", []))

    @builtins.property
    @jsii.member(jsii_name="backgroundVerification")
    def background_verification(
        self,
    ) -> OceancdStrategyCanaryBackgroundVerificationOutputReference:
        return typing.cast(OceancdStrategyCanaryBackgroundVerificationOutputReference, jsii.get(self, "backgroundVerification"))

    @builtins.property
    @jsii.member(jsii_name="steps")
    def steps(self) -> "OceancdStrategyCanaryStepsList":
        return typing.cast("OceancdStrategyCanaryStepsList", jsii.get(self, "steps"))

    @builtins.property
    @jsii.member(jsii_name="backgroundVerificationInput")
    def background_verification_input(
        self,
    ) -> typing.Optional[OceancdStrategyCanaryBackgroundVerification]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryBackgroundVerification], jsii.get(self, "backgroundVerificationInput"))

    @builtins.property
    @jsii.member(jsii_name="stepsInput")
    def steps_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyCanarySteps"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyCanarySteps"]]], jsii.get(self, "stepsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdStrategyCanary]:
        return typing.cast(typing.Optional[OceancdStrategyCanary], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceancdStrategyCanary]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4ef887b0eb9ec9e5b5577e013dbb7aef894d74a627004bb83d2cdeea2f1a6fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanarySteps",
    jsii_struct_bases=[],
    name_mapping={
        "pause": "pause",
        "set_canary_scale": "setCanaryScale",
        "set_header_route": "setHeaderRoute",
        "set_weight": "setWeight",
        "step_name": "stepName",
        "verification": "verification",
    },
)
class OceancdStrategyCanarySteps:
    def __init__(
        self,
        *,
        pause: typing.Optional[typing.Union["OceancdStrategyCanaryStepsPause", typing.Dict[builtins.str, typing.Any]]] = None,
        set_canary_scale: typing.Optional[typing.Union["OceancdStrategyCanaryStepsSetCanaryScale", typing.Dict[builtins.str, typing.Any]]] = None,
        set_header_route: typing.Optional[typing.Union["OceancdStrategyCanaryStepsSetHeaderRoute", typing.Dict[builtins.str, typing.Any]]] = None,
        set_weight: typing.Optional[jsii.Number] = None,
        step_name: typing.Optional[builtins.str] = None,
        verification: typing.Optional[typing.Union["OceancdStrategyCanaryStepsVerification", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param pause: pause block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#pause OceancdStrategy#pause}
        :param set_canary_scale: set_canary_scale block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#set_canary_scale OceancdStrategy#set_canary_scale}
        :param set_header_route: set_header_route block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#set_header_route OceancdStrategy#set_header_route}
        :param set_weight: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#set_weight OceancdStrategy#set_weight}.
        :param step_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#step_name OceancdStrategy#step_name}.
        :param verification: verification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#verification OceancdStrategy#verification}
        '''
        if isinstance(pause, dict):
            pause = OceancdStrategyCanaryStepsPause(**pause)
        if isinstance(set_canary_scale, dict):
            set_canary_scale = OceancdStrategyCanaryStepsSetCanaryScale(**set_canary_scale)
        if isinstance(set_header_route, dict):
            set_header_route = OceancdStrategyCanaryStepsSetHeaderRoute(**set_header_route)
        if isinstance(verification, dict):
            verification = OceancdStrategyCanaryStepsVerification(**verification)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86fd045cc62f8b717b93d3785ac94ca804edf5628aae059f2fdfae6b9e1c1a0c)
            check_type(argname="argument pause", value=pause, expected_type=type_hints["pause"])
            check_type(argname="argument set_canary_scale", value=set_canary_scale, expected_type=type_hints["set_canary_scale"])
            check_type(argname="argument set_header_route", value=set_header_route, expected_type=type_hints["set_header_route"])
            check_type(argname="argument set_weight", value=set_weight, expected_type=type_hints["set_weight"])
            check_type(argname="argument step_name", value=step_name, expected_type=type_hints["step_name"])
            check_type(argname="argument verification", value=verification, expected_type=type_hints["verification"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pause is not None:
            self._values["pause"] = pause
        if set_canary_scale is not None:
            self._values["set_canary_scale"] = set_canary_scale
        if set_header_route is not None:
            self._values["set_header_route"] = set_header_route
        if set_weight is not None:
            self._values["set_weight"] = set_weight
        if step_name is not None:
            self._values["step_name"] = step_name
        if verification is not None:
            self._values["verification"] = verification

    @builtins.property
    def pause(self) -> typing.Optional["OceancdStrategyCanaryStepsPause"]:
        '''pause block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#pause OceancdStrategy#pause}
        '''
        result = self._values.get("pause")
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsPause"], result)

    @builtins.property
    def set_canary_scale(
        self,
    ) -> typing.Optional["OceancdStrategyCanaryStepsSetCanaryScale"]:
        '''set_canary_scale block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#set_canary_scale OceancdStrategy#set_canary_scale}
        '''
        result = self._values.get("set_canary_scale")
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsSetCanaryScale"], result)

    @builtins.property
    def set_header_route(
        self,
    ) -> typing.Optional["OceancdStrategyCanaryStepsSetHeaderRoute"]:
        '''set_header_route block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#set_header_route OceancdStrategy#set_header_route}
        '''
        result = self._values.get("set_header_route")
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsSetHeaderRoute"], result)

    @builtins.property
    def set_weight(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#set_weight OceancdStrategy#set_weight}.'''
        result = self._values.get("set_weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def step_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#step_name OceancdStrategy#step_name}.'''
        result = self._values.get("step_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verification(self) -> typing.Optional["OceancdStrategyCanaryStepsVerification"]:
        '''verification block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#verification OceancdStrategy#verification}
        '''
        result = self._values.get("verification")
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsVerification"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanarySteps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyCanaryStepsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a159c127f63881987bc8dbe067d4465bf9576cd4ef3380eb5883f5c71b81418)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceancdStrategyCanaryStepsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3ad9dd209b016ba03377a96df6b0f9f093bcfc3e7e86f3f52dbd4f6c7eecb0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdStrategyCanaryStepsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a7461475c4c703d382d72b7214a3d83df6b9f2098fe852df27c398149a11219)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6419a44ee7a5fe8c29cfc46d64206a8274726bb123fa288c8682c8222cebad74)
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
            type_hints = typing.get_type_hints(_typecheckingstub__04d1120183c9bee82878a357efc3b0ce4884df52618683f0865cc4afd82e4294)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanarySteps]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanarySteps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanarySteps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__379a8caa0601e94a26dea5ff92687a53c3407843fa20ec6190b1356424e9eefd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdStrategyCanaryStepsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5aa9f866b044d51dc10fa2b55bc731b46ceddb49e18b5fa34762c7310941ae8c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPause")
    def put_pause(self, *, duration: typing.Optional[builtins.str] = None) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#duration OceancdStrategy#duration}.
        '''
        value = OceancdStrategyCanaryStepsPause(duration=duration)

        return typing.cast(None, jsii.invoke(self, "putPause", [value]))

    @jsii.member(jsii_name="putSetCanaryScale")
    def put_set_canary_scale(
        self,
        *,
        match_traffic_weight: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        replicas: typing.Optional[jsii.Number] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param match_traffic_weight: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#match_traffic_weight OceancdStrategy#match_traffic_weight}.
        :param replicas: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#replicas OceancdStrategy#replicas}.
        :param weight: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#weight OceancdStrategy#weight}.
        '''
        value = OceancdStrategyCanaryStepsSetCanaryScale(
            match_traffic_weight=match_traffic_weight, replicas=replicas, weight=weight
        )

        return typing.cast(None, jsii.invoke(self, "putSetCanaryScale", [value]))

    @jsii.member(jsii_name="putSetHeaderRoute")
    def put_set_header_route(
        self,
        *,
        header_route_name: builtins.str,
        match: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyCanaryStepsSetHeaderRouteMatch", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param header_route_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_route_name OceancdStrategy#header_route_name}.
        :param match: match block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#match OceancdStrategy#match}
        '''
        value = OceancdStrategyCanaryStepsSetHeaderRoute(
            header_route_name=header_route_name, match=match
        )

        return typing.cast(None, jsii.invoke(self, "putSetHeaderRoute", [value]))

    @jsii.member(jsii_name="putVerification")
    def put_verification(
        self,
        *,
        template_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param template_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.
        '''
        value = OceancdStrategyCanaryStepsVerification(template_names=template_names)

        return typing.cast(None, jsii.invoke(self, "putVerification", [value]))

    @jsii.member(jsii_name="resetPause")
    def reset_pause(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPause", []))

    @jsii.member(jsii_name="resetSetCanaryScale")
    def reset_set_canary_scale(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetCanaryScale", []))

    @jsii.member(jsii_name="resetSetHeaderRoute")
    def reset_set_header_route(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetHeaderRoute", []))

    @jsii.member(jsii_name="resetSetWeight")
    def reset_set_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetWeight", []))

    @jsii.member(jsii_name="resetStepName")
    def reset_step_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStepName", []))

    @jsii.member(jsii_name="resetVerification")
    def reset_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerification", []))

    @builtins.property
    @jsii.member(jsii_name="pause")
    def pause(self) -> "OceancdStrategyCanaryStepsPauseOutputReference":
        return typing.cast("OceancdStrategyCanaryStepsPauseOutputReference", jsii.get(self, "pause"))

    @builtins.property
    @jsii.member(jsii_name="setCanaryScale")
    def set_canary_scale(
        self,
    ) -> "OceancdStrategyCanaryStepsSetCanaryScaleOutputReference":
        return typing.cast("OceancdStrategyCanaryStepsSetCanaryScaleOutputReference", jsii.get(self, "setCanaryScale"))

    @builtins.property
    @jsii.member(jsii_name="setHeaderRoute")
    def set_header_route(
        self,
    ) -> "OceancdStrategyCanaryStepsSetHeaderRouteOutputReference":
        return typing.cast("OceancdStrategyCanaryStepsSetHeaderRouteOutputReference", jsii.get(self, "setHeaderRoute"))

    @builtins.property
    @jsii.member(jsii_name="verification")
    def verification(self) -> "OceancdStrategyCanaryStepsVerificationOutputReference":
        return typing.cast("OceancdStrategyCanaryStepsVerificationOutputReference", jsii.get(self, "verification"))

    @builtins.property
    @jsii.member(jsii_name="pauseInput")
    def pause_input(self) -> typing.Optional["OceancdStrategyCanaryStepsPause"]:
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsPause"], jsii.get(self, "pauseInput"))

    @builtins.property
    @jsii.member(jsii_name="setCanaryScaleInput")
    def set_canary_scale_input(
        self,
    ) -> typing.Optional["OceancdStrategyCanaryStepsSetCanaryScale"]:
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsSetCanaryScale"], jsii.get(self, "setCanaryScaleInput"))

    @builtins.property
    @jsii.member(jsii_name="setHeaderRouteInput")
    def set_header_route_input(
        self,
    ) -> typing.Optional["OceancdStrategyCanaryStepsSetHeaderRoute"]:
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsSetHeaderRoute"], jsii.get(self, "setHeaderRouteInput"))

    @builtins.property
    @jsii.member(jsii_name="setWeightInput")
    def set_weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "setWeightInput"))

    @builtins.property
    @jsii.member(jsii_name="stepNameInput")
    def step_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stepNameInput"))

    @builtins.property
    @jsii.member(jsii_name="verificationInput")
    def verification_input(
        self,
    ) -> typing.Optional["OceancdStrategyCanaryStepsVerification"]:
        return typing.cast(typing.Optional["OceancdStrategyCanaryStepsVerification"], jsii.get(self, "verificationInput"))

    @builtins.property
    @jsii.member(jsii_name="setWeight")
    def set_weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "setWeight"))

    @set_weight.setter
    def set_weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9facbbea3d67af83afac53485dd1d94d85fa447ab744dadcfed0ac9a71ee9fc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "setWeight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stepName")
    def step_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stepName"))

    @step_name.setter
    def step_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79c979bea962a1a2004f873903c9f9ac66c6643b677c63f3d05335e18c038432)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stepName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanarySteps]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanarySteps]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanarySteps]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eef28f05a5acdaecfbf6ec50b2653840ea44bde83bf7749010869521f834cc50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsPause",
    jsii_struct_bases=[],
    name_mapping={"duration": "duration"},
)
class OceancdStrategyCanaryStepsPause:
    def __init__(self, *, duration: typing.Optional[builtins.str] = None) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#duration OceancdStrategy#duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__168624ba1b014777751d37a6ada51d445bbed173670b34bc8d817c4d4a6469c0)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#duration OceancdStrategy#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryStepsPause(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyCanaryStepsPauseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsPauseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2a8aa197809fb3ee0d2f14d259eb0a2fa095813e82607b789bced6941806656)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22abd24aca0f55e3991183b3e8e9d006dd9b5ec78d4371fa34a9f6091293ea41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdStrategyCanaryStepsPause]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryStepsPause], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyCanaryStepsPause],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f3f952cb941c7e63aa0f110bf1077388994e2324b8e1224ec8e1de603a12dde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetCanaryScale",
    jsii_struct_bases=[],
    name_mapping={
        "match_traffic_weight": "matchTrafficWeight",
        "replicas": "replicas",
        "weight": "weight",
    },
)
class OceancdStrategyCanaryStepsSetCanaryScale:
    def __init__(
        self,
        *,
        match_traffic_weight: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        replicas: typing.Optional[jsii.Number] = None,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param match_traffic_weight: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#match_traffic_weight OceancdStrategy#match_traffic_weight}.
        :param replicas: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#replicas OceancdStrategy#replicas}.
        :param weight: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#weight OceancdStrategy#weight}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c67775b608a7fa6cf0f910669f85c4b3a8fc4feded08260f0559c85a5ae80fa6)
            check_type(argname="argument match_traffic_weight", value=match_traffic_weight, expected_type=type_hints["match_traffic_weight"])
            check_type(argname="argument replicas", value=replicas, expected_type=type_hints["replicas"])
            check_type(argname="argument weight", value=weight, expected_type=type_hints["weight"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if match_traffic_weight is not None:
            self._values["match_traffic_weight"] = match_traffic_weight
        if replicas is not None:
            self._values["replicas"] = replicas
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def match_traffic_weight(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#match_traffic_weight OceancdStrategy#match_traffic_weight}.'''
        result = self._values.get("match_traffic_weight")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#replicas OceancdStrategy#replicas}.'''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#weight OceancdStrategy#weight}.'''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryStepsSetCanaryScale(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyCanaryStepsSetCanaryScaleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetCanaryScaleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3a19b8c2966a25a5fca46b4b7d2dae704838401ce05dca76cf31f9a13a332fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMatchTrafficWeight")
    def reset_match_traffic_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatchTrafficWeight", []))

    @jsii.member(jsii_name="resetReplicas")
    def reset_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicas", []))

    @jsii.member(jsii_name="resetWeight")
    def reset_weight(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeight", []))

    @builtins.property
    @jsii.member(jsii_name="matchTrafficWeightInput")
    def match_traffic_weight_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "matchTrafficWeightInput"))

    @builtins.property
    @jsii.member(jsii_name="replicasInput")
    def replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicasInput"))

    @builtins.property
    @jsii.member(jsii_name="weightInput")
    def weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightInput"))

    @builtins.property
    @jsii.member(jsii_name="matchTrafficWeight")
    def match_traffic_weight(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "matchTrafficWeight"))

    @match_traffic_weight.setter
    def match_traffic_weight(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4699e609bffeb4dac97322bae273227995336d417f1d35233b7184f7cd1e4bb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "matchTrafficWeight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replicas")
    def replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicas"))

    @replicas.setter
    def replicas(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7bae541472376229a1ae3c5ce01d153424d7b5ab59c7c6f8f70d00049f99367)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replicas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @weight.setter
    def weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0b173524d4afc12a6f4948967e3a223189bfa6c10bd2847613a3f0eb6955036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdStrategyCanaryStepsSetCanaryScale]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryStepsSetCanaryScale], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyCanaryStepsSetCanaryScale],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6767c30b2330b3a3ca6e6b4fa7d556f7081119f035d0182d0a65f629a13a5d16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRoute",
    jsii_struct_bases=[],
    name_mapping={"header_route_name": "headerRouteName", "match": "match"},
)
class OceancdStrategyCanaryStepsSetHeaderRoute:
    def __init__(
        self,
        *,
        header_route_name: builtins.str,
        match: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyCanaryStepsSetHeaderRouteMatch", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param header_route_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_route_name OceancdStrategy#header_route_name}.
        :param match: match block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#match OceancdStrategy#match}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0772a75048b8dfe65281dc74c1fbff992c0cef00faa307a666d1bb08aa621afb)
            check_type(argname="argument header_route_name", value=header_route_name, expected_type=type_hints["header_route_name"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "header_route_name": header_route_name,
            "match": match,
        }

    @builtins.property
    def header_route_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_route_name OceancdStrategy#header_route_name}.'''
        result = self._values.get("header_route_name")
        assert result is not None, "Required property 'header_route_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def match(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyCanaryStepsSetHeaderRouteMatch"]]:
        '''match block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#match OceancdStrategy#match}
        '''
        result = self._values.get("match")
        assert result is not None, "Required property 'match' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyCanaryStepsSetHeaderRouteMatch"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryStepsSetHeaderRoute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRouteMatch",
    jsii_struct_bases=[],
    name_mapping={"header_name": "headerName", "header_value": "headerValue"},
)
class OceancdStrategyCanaryStepsSetHeaderRouteMatch:
    def __init__(
        self,
        *,
        header_name: builtins.str,
        header_value: typing.Union["OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param header_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_name OceancdStrategy#header_name}.
        :param header_value: header_value block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_value OceancdStrategy#header_value}
        '''
        if isinstance(header_value, dict):
            header_value = OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue(**header_value)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__533c473f974ad763eaf5727ca36cce6e939b27ee42d5ae2adcc6250e65486573)
            check_type(argname="argument header_name", value=header_name, expected_type=type_hints["header_name"])
            check_type(argname="argument header_value", value=header_value, expected_type=type_hints["header_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "header_name": header_name,
            "header_value": header_value,
        }

    @builtins.property
    def header_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_name OceancdStrategy#header_name}.'''
        result = self._values.get("header_name")
        assert result is not None, "Required property 'header_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def header_value(
        self,
    ) -> "OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue":
        '''header_value block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#header_value OceancdStrategy#header_value}
        '''
        result = self._values.get("header_value")
        assert result is not None, "Required property 'header_value' is missing"
        return typing.cast("OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryStepsSetHeaderRouteMatch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue",
    jsii_struct_bases=[],
    name_mapping={"exact": "exact", "prefix": "prefix", "regex": "regex"},
)
class OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue:
    def __init__(
        self,
        *,
        exact: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        regex: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exact: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#exact OceancdStrategy#exact}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#prefix OceancdStrategy#prefix}.
        :param regex: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#regex OceancdStrategy#regex}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62d034910a727b6367093ee465da5b30fb3d9e2638115914028ee80476ea6c1b)
            check_type(argname="argument exact", value=exact, expected_type=type_hints["exact"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument regex", value=regex, expected_type=type_hints["regex"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if exact is not None:
            self._values["exact"] = exact
        if prefix is not None:
            self._values["prefix"] = prefix
        if regex is not None:
            self._values["regex"] = regex

    @builtins.property
    def exact(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#exact OceancdStrategy#exact}.'''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#prefix OceancdStrategy#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#regex OceancdStrategy#regex}.'''
        result = self._values.get("regex")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValueOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValueOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ccb45524693bbe795a7dc63c626ae505808f9cceb87e5422d77b358e54f04aeb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExact")
    def reset_exact(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExact", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetRegex")
    def reset_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegex", []))

    @builtins.property
    @jsii.member(jsii_name="exactInput")
    def exact_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exactInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="regexInput")
    def regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regexInput"))

    @builtins.property
    @jsii.member(jsii_name="exact")
    def exact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exact"))

    @exact.setter
    def exact(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77d352a6dfba3c7c8034218f958089f1eea39582f346df97832c614cf75bc9c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exact", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1c2f7af4279f955053e0fc601d3912b41f597bc10cee6d6cbee5cf05363abec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regex")
    def regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regex"))

    @regex.setter
    def regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6787715e90815a7a7e29c956b4973459e284dca9197aaf189c3ac8d3ca7257f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94ca463f9c0b9ea22205ab3f548daea8479b09252d9cb14d6140fc2f830f1332)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdStrategyCanaryStepsSetHeaderRouteMatchList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRouteMatchList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce7eeefd2fe1f6238453fb1dd28677584dc125e9155a461a7733d7c25e5fc7c5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdStrategyCanaryStepsSetHeaderRouteMatchOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f96c7148b410c3b445ebdfea151aa4f128200414577bd76d45ff255a6f344ce)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdStrategyCanaryStepsSetHeaderRouteMatchOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8ad37822013f0ce30884a38fd817ad5449e92b7923208222780b73fd50ff239)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0e110ba1dd79c5ce1f87fd642d299013d808beebf3041db395ebfd7eb0d1d55)
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
            type_hints = typing.get_type_hints(_typecheckingstub__177a69e080d547db30d35a004cff974282f5f6ec0e37c96d5fa01b73a385ff7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanaryStepsSetHeaderRouteMatch]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanaryStepsSetHeaderRouteMatch]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanaryStepsSetHeaderRouteMatch]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f06f9d6ad5bdc67efde5b4017b8e688671c2702afc9aec57b71fdc32d7ae2fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdStrategyCanaryStepsSetHeaderRouteMatchOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRouteMatchOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ff907c3f98825b9ed55beeb4b6251d7eb9aa5d178699e6548c4dc786698250d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHeaderValue")
    def put_header_value(
        self,
        *,
        exact: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        regex: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exact: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#exact OceancdStrategy#exact}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#prefix OceancdStrategy#prefix}.
        :param regex: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#regex OceancdStrategy#regex}.
        '''
        value = OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue(
            exact=exact, prefix=prefix, regex=regex
        )

        return typing.cast(None, jsii.invoke(self, "putHeaderValue", [value]))

    @builtins.property
    @jsii.member(jsii_name="headerValue")
    def header_value(
        self,
    ) -> OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValueOutputReference:
        return typing.cast(OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValueOutputReference, jsii.get(self, "headerValue"))

    @builtins.property
    @jsii.member(jsii_name="headerNameInput")
    def header_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="headerValueInput")
    def header_value_input(
        self,
    ) -> typing.Optional[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue], jsii.get(self, "headerValueInput"))

    @builtins.property
    @jsii.member(jsii_name="headerName")
    def header_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerName"))

    @header_name.setter
    def header_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2466c71a4130dcf594ce01e1bbce1b85ec30d25fd4e4b0f70aaaf10c0fa196c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanaryStepsSetHeaderRouteMatch]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanaryStepsSetHeaderRouteMatch]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanaryStepsSetHeaderRouteMatch]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1add723e1ce81fd492a3bd0fabefb68d1c029a06eae48829891a7517f06937b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdStrategyCanaryStepsSetHeaderRouteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsSetHeaderRouteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__061c208ac12902e984f794c758de78da33fb884024e68e8e3e9ec60cd803bd7a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMatch")
    def put_match(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyCanaryStepsSetHeaderRouteMatch, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b427862f4d36c8d271b173e9a0495376ae1ba43a11a1112688a76bcffa322d4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMatch", [value]))

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> OceancdStrategyCanaryStepsSetHeaderRouteMatchList:
        return typing.cast(OceancdStrategyCanaryStepsSetHeaderRouteMatchList, jsii.get(self, "match"))

    @builtins.property
    @jsii.member(jsii_name="headerRouteNameInput")
    def header_route_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerRouteNameInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanaryStepsSetHeaderRouteMatch]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanaryStepsSetHeaderRouteMatch]]], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="headerRouteName")
    def header_route_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerRouteName"))

    @header_route_name.setter
    def header_route_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08de43ff960d38996e10793bf67f6097770c2baf5f20f1f9320918e7b40725af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headerRouteName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdStrategyCanaryStepsSetHeaderRoute]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryStepsSetHeaderRoute], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyCanaryStepsSetHeaderRoute],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5dbef95c08346dcd15cb690ad78a0f3cfe757113618bdc50d1984ef1630af11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsVerification",
    jsii_struct_bases=[],
    name_mapping={"template_names": "templateNames"},
)
class OceancdStrategyCanaryStepsVerification:
    def __init__(self, *, template_names: typing.Sequence[builtins.str]) -> None:
        '''
        :param template_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65442edb96daa72ac0a95cf1b41248bbce28482fe24801f69166b645e8e77419)
            check_type(argname="argument template_names", value=template_names, expected_type=type_hints["template_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "template_names": template_names,
        }

    @builtins.property
    def template_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.'''
        result = self._values.get("template_names")
        assert result is not None, "Required property 'template_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyCanaryStepsVerification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyCanaryStepsVerificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyCanaryStepsVerificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d40402e14b8eafa14993e9700200fac8f19fe4f7ddeaf28c76b1d7d1e784120b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="templateNamesInput")
    def template_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "templateNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="templateNames")
    def template_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "templateNames"))

    @template_names.setter
    def template_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc96bd3092d0936113e1f78937a22f21f1f06abe5ea0c6d822f3909a6cbae7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdStrategyCanaryStepsVerification]:
        return typing.cast(typing.Optional[OceancdStrategyCanaryStepsVerification], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyCanaryStepsVerification],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07dfa716d996d13e5f020907c88bdba4060bc6e5218087434f715f0389fcfd2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "strategy_name": "strategyName",
        "canary": "canary",
        "id": "id",
        "rolling": "rolling",
    },
)
class OceancdStrategyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        strategy_name: builtins.str,
        canary: typing.Optional[typing.Union[OceancdStrategyCanary, typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        rolling: typing.Optional[typing.Union["OceancdStrategyRolling", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param strategy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#strategy_name OceancdStrategy#strategy_name}.
        :param canary: canary block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#canary OceancdStrategy#canary}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#id OceancdStrategy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rolling: rolling block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#rolling OceancdStrategy#rolling}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(canary, dict):
            canary = OceancdStrategyCanary(**canary)
        if isinstance(rolling, dict):
            rolling = OceancdStrategyRolling(**rolling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6eb898f66c5400da92d8a80c50de04a4099ca0cf1c0b5bf8e95328c1f9f577d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument strategy_name", value=strategy_name, expected_type=type_hints["strategy_name"])
            check_type(argname="argument canary", value=canary, expected_type=type_hints["canary"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rolling", value=rolling, expected_type=type_hints["rolling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "strategy_name": strategy_name,
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
        if canary is not None:
            self._values["canary"] = canary
        if id is not None:
            self._values["id"] = id
        if rolling is not None:
            self._values["rolling"] = rolling

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
    def strategy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#strategy_name OceancdStrategy#strategy_name}.'''
        result = self._values.get("strategy_name")
        assert result is not None, "Required property 'strategy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def canary(self) -> typing.Optional[OceancdStrategyCanary]:
        '''canary block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#canary OceancdStrategy#canary}
        '''
        result = self._values.get("canary")
        return typing.cast(typing.Optional[OceancdStrategyCanary], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#id OceancdStrategy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rolling(self) -> typing.Optional["OceancdStrategyRolling"]:
        '''rolling block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#rolling OceancdStrategy#rolling}
        '''
        result = self._values.get("rolling")
        return typing.cast(typing.Optional["OceancdStrategyRolling"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRolling",
    jsii_struct_bases=[],
    name_mapping={"steps": "steps"},
)
class OceancdStrategyRolling:
    def __init__(
        self,
        *,
        steps: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyRollingSteps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param steps: steps block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps OceancdStrategy#steps}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a6a5cbf6efcc11108e3e9087428360f7c784aaa0fa27bf18e3f1254edb6c9c0)
            check_type(argname="argument steps", value=steps, expected_type=type_hints["steps"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "steps": steps,
        }

    @builtins.property
    def steps(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyRollingSteps"]]:
        '''steps block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps OceancdStrategy#steps}
        '''
        result = self._values.get("steps")
        assert result is not None, "Required property 'steps' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyRollingSteps"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyRolling(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyRollingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e51f81e0bdc09ac2e60948e1946fcd5a3eef0a1d6bfce1b817733cb3b5209de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSteps")
    def put_steps(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdStrategyRollingSteps", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02f5c225801110604d2b7813d9fba731b3bfba56508bdd7ff5f665b7322534de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSteps", [value]))

    @builtins.property
    @jsii.member(jsii_name="steps")
    def steps(self) -> "OceancdStrategyRollingStepsList":
        return typing.cast("OceancdStrategyRollingStepsList", jsii.get(self, "steps"))

    @builtins.property
    @jsii.member(jsii_name="stepsInput")
    def steps_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyRollingSteps"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdStrategyRollingSteps"]]], jsii.get(self, "stepsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdStrategyRolling]:
        return typing.cast(typing.Optional[OceancdStrategyRolling], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OceancdStrategyRolling]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__679844bf3f0b3d542b571839bebeda461124987d469a6f73644bea7349b910b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingSteps",
    jsii_struct_bases=[],
    name_mapping={
        "pause": "pause",
        "steps_name": "stepsName",
        "verification": "verification",
    },
)
class OceancdStrategyRollingSteps:
    def __init__(
        self,
        *,
        pause: typing.Optional[typing.Union["OceancdStrategyRollingStepsPause", typing.Dict[builtins.str, typing.Any]]] = None,
        steps_name: typing.Optional[builtins.str] = None,
        verification: typing.Optional[typing.Union["OceancdStrategyRollingStepsVerification", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param pause: pause block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#pause OceancdStrategy#pause}
        :param steps_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps_name OceancdStrategy#steps_name}.
        :param verification: verification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#verification OceancdStrategy#verification}
        '''
        if isinstance(pause, dict):
            pause = OceancdStrategyRollingStepsPause(**pause)
        if isinstance(verification, dict):
            verification = OceancdStrategyRollingStepsVerification(**verification)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f65c67018d6125a5ad948db7b71a983d036707bad0cc4369da019b525a553b3d)
            check_type(argname="argument pause", value=pause, expected_type=type_hints["pause"])
            check_type(argname="argument steps_name", value=steps_name, expected_type=type_hints["steps_name"])
            check_type(argname="argument verification", value=verification, expected_type=type_hints["verification"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pause is not None:
            self._values["pause"] = pause
        if steps_name is not None:
            self._values["steps_name"] = steps_name
        if verification is not None:
            self._values["verification"] = verification

    @builtins.property
    def pause(self) -> typing.Optional["OceancdStrategyRollingStepsPause"]:
        '''pause block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#pause OceancdStrategy#pause}
        '''
        result = self._values.get("pause")
        return typing.cast(typing.Optional["OceancdStrategyRollingStepsPause"], result)

    @builtins.property
    def steps_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#steps_name OceancdStrategy#steps_name}.'''
        result = self._values.get("steps_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verification(
        self,
    ) -> typing.Optional["OceancdStrategyRollingStepsVerification"]:
        '''verification block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#verification OceancdStrategy#verification}
        '''
        result = self._values.get("verification")
        return typing.cast(typing.Optional["OceancdStrategyRollingStepsVerification"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyRollingSteps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyRollingStepsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingStepsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__24df36adbfcda1e16c155c9ecf3a3382f2318e380aa18700ae99b0e43849a306)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OceancdStrategyRollingStepsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a0624af3139cb48f9e44be637fb8f7569e37307b8f57fd2da5c76cd590c2c0a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdStrategyRollingStepsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ff208d2f2e3ae942facd8e92f3006319ce87e5b6421ef024f7e6b0792bed8b8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__312641f18267f98c163ca46dead6329f7d71a71efb5683790185b664b90fb90e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5be66e8adc28b1387ff03643e50e58ef8c2b989a2752f37b6c9ff1056fd36c8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyRollingSteps]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyRollingSteps]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyRollingSteps]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0e8fa42bc21ca3fd57168d4247725d810b92979dd61708cabd09a169794643a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdStrategyRollingStepsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingStepsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c4799b6d5480851a1a8253323320dda247db316d584ee29aa6c78fca7f34829b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putPause")
    def put_pause(self, *, duration: typing.Optional[builtins.str] = None) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#duration OceancdStrategy#duration}.
        '''
        value = OceancdStrategyRollingStepsPause(duration=duration)

        return typing.cast(None, jsii.invoke(self, "putPause", [value]))

    @jsii.member(jsii_name="putVerification")
    def put_verification(
        self,
        *,
        template_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param template_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.
        '''
        value = OceancdStrategyRollingStepsVerification(template_names=template_names)

        return typing.cast(None, jsii.invoke(self, "putVerification", [value]))

    @jsii.member(jsii_name="resetPause")
    def reset_pause(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPause", []))

    @jsii.member(jsii_name="resetStepsName")
    def reset_steps_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStepsName", []))

    @jsii.member(jsii_name="resetVerification")
    def reset_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerification", []))

    @builtins.property
    @jsii.member(jsii_name="pause")
    def pause(self) -> "OceancdStrategyRollingStepsPauseOutputReference":
        return typing.cast("OceancdStrategyRollingStepsPauseOutputReference", jsii.get(self, "pause"))

    @builtins.property
    @jsii.member(jsii_name="verification")
    def verification(self) -> "OceancdStrategyRollingStepsVerificationOutputReference":
        return typing.cast("OceancdStrategyRollingStepsVerificationOutputReference", jsii.get(self, "verification"))

    @builtins.property
    @jsii.member(jsii_name="pauseInput")
    def pause_input(self) -> typing.Optional["OceancdStrategyRollingStepsPause"]:
        return typing.cast(typing.Optional["OceancdStrategyRollingStepsPause"], jsii.get(self, "pauseInput"))

    @builtins.property
    @jsii.member(jsii_name="stepsNameInput")
    def steps_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stepsNameInput"))

    @builtins.property
    @jsii.member(jsii_name="verificationInput")
    def verification_input(
        self,
    ) -> typing.Optional["OceancdStrategyRollingStepsVerification"]:
        return typing.cast(typing.Optional["OceancdStrategyRollingStepsVerification"], jsii.get(self, "verificationInput"))

    @builtins.property
    @jsii.member(jsii_name="stepsName")
    def steps_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stepsName"))

    @steps_name.setter
    def steps_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8306a57f797d7d37f0e947a986c4c2999b6683a1ad03aa95b0ce0b736d7586f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stepsName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyRollingSteps]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyRollingSteps]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyRollingSteps]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e6a76438e81ff8793a12c3098702086459492f827e59fd21a9ec0c68e07e60f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingStepsPause",
    jsii_struct_bases=[],
    name_mapping={"duration": "duration"},
)
class OceancdStrategyRollingStepsPause:
    def __init__(self, *, duration: typing.Optional[builtins.str] = None) -> None:
        '''
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#duration OceancdStrategy#duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c51b79d2c8d6bc2cc552e6e50052434a2088c4f0090e157ecfa3e8885434d73e)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#duration OceancdStrategy#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyRollingStepsPause(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyRollingStepsPauseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingStepsPauseOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5127d6bc8d00ad20abf2b4b7473b47ac13009944132e9704092813351592cd7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a9e088a5de97bc5244532b2422710a85085a8ddb427a31e0a272f368a6919dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdStrategyRollingStepsPause]:
        return typing.cast(typing.Optional[OceancdStrategyRollingStepsPause], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyRollingStepsPause],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9579b00f96f1272f17ea02b71d8e9820f260be34efc68dfa7d8a29a6a557e7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingStepsVerification",
    jsii_struct_bases=[],
    name_mapping={"template_names": "templateNames"},
)
class OceancdStrategyRollingStepsVerification:
    def __init__(self, *, template_names: typing.Sequence[builtins.str]) -> None:
        '''
        :param template_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5012f1f9a5debea5087dc97affe0967ba321447f83c1622337d81ab3a3d8305c)
            check_type(argname="argument template_names", value=template_names, expected_type=type_hints["template_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "template_names": template_names,
        }

    @builtins.property
    def template_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_strategy#template_names OceancdStrategy#template_names}.'''
        result = self._values.get("template_names")
        assert result is not None, "Required property 'template_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdStrategyRollingStepsVerification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdStrategyRollingStepsVerificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdStrategy.OceancdStrategyRollingStepsVerificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a188ab4d082e72e2386254a40a8262ff3b461d2fe611f6fe10fbfb4e302d59d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="templateNamesInput")
    def template_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "templateNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="templateNames")
    def template_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "templateNames"))

    @template_names.setter
    def template_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d24ca5a35b40664ad2352a626586ca567b983b45eff4f033b6b428b8ebaf25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdStrategyRollingStepsVerification]:
        return typing.cast(typing.Optional[OceancdStrategyRollingStepsVerification], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdStrategyRollingStepsVerification],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5e85a2762ae4849b932f193e3907534d04c2ccdef8baffa1869e69c94c1bd08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceancdStrategy",
    "OceancdStrategyCanary",
    "OceancdStrategyCanaryBackgroundVerification",
    "OceancdStrategyCanaryBackgroundVerificationOutputReference",
    "OceancdStrategyCanaryOutputReference",
    "OceancdStrategyCanarySteps",
    "OceancdStrategyCanaryStepsList",
    "OceancdStrategyCanaryStepsOutputReference",
    "OceancdStrategyCanaryStepsPause",
    "OceancdStrategyCanaryStepsPauseOutputReference",
    "OceancdStrategyCanaryStepsSetCanaryScale",
    "OceancdStrategyCanaryStepsSetCanaryScaleOutputReference",
    "OceancdStrategyCanaryStepsSetHeaderRoute",
    "OceancdStrategyCanaryStepsSetHeaderRouteMatch",
    "OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue",
    "OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValueOutputReference",
    "OceancdStrategyCanaryStepsSetHeaderRouteMatchList",
    "OceancdStrategyCanaryStepsSetHeaderRouteMatchOutputReference",
    "OceancdStrategyCanaryStepsSetHeaderRouteOutputReference",
    "OceancdStrategyCanaryStepsVerification",
    "OceancdStrategyCanaryStepsVerificationOutputReference",
    "OceancdStrategyConfig",
    "OceancdStrategyRolling",
    "OceancdStrategyRollingOutputReference",
    "OceancdStrategyRollingSteps",
    "OceancdStrategyRollingStepsList",
    "OceancdStrategyRollingStepsOutputReference",
    "OceancdStrategyRollingStepsPause",
    "OceancdStrategyRollingStepsPauseOutputReference",
    "OceancdStrategyRollingStepsVerification",
    "OceancdStrategyRollingStepsVerificationOutputReference",
]

publication.publish()

def _typecheckingstub__28611b9d23fa8b84337b291924c2f7e3149c8b4aca37b169c6adc263d07ddc53(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    strategy_name: builtins.str,
    canary: typing.Optional[typing.Union[OceancdStrategyCanary, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    rolling: typing.Optional[typing.Union[OceancdStrategyRolling, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__486753df8bc2430ae34d171c83a1849dc53f0933879b2d7126d775fe63a84645(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a4686fe8020550fed9c1762200cabb563acb6da446a09521dbc1eec05f39d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8bc9a846f8283bf4008d5fc9c96cab3c4c798f79884e87ca3d39799c7e354cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83648f82c2bebe31311ba07d982cd2e32d68d6e1016fbfb3c3dc722ea640199d(
    *,
    steps: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyCanarySteps, typing.Dict[builtins.str, typing.Any]]]],
    background_verification: typing.Optional[typing.Union[OceancdStrategyCanaryBackgroundVerification, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e0fb7822a66bdbdcb57a88f94e722ff9771f02079be1c11c61ae4f0b576158a(
    *,
    template_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff17a585f7d2cf0aaef82f5df7573e06b103e1229295ac3963ccaf863aad844f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f26be4c59379f462ad7b84f76e7cbdb1f94eecfb221ae7e393ace749fe74129(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f8d910af07e49f3ca958f1b1ffccbff5b9e7229fbb83ad937f278db8e53727(
    value: typing.Optional[OceancdStrategyCanaryBackgroundVerification],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9852bee7d4dddbd5d8f497dc11c50d4fe9cb0d80c31205d2b59065967224c0fe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677143b8cef6c0de12fa7189a33ce604a7925edb9ecf8191509db9fef6cc9ed4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyCanarySteps, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ef887b0eb9ec9e5b5577e013dbb7aef894d74a627004bb83d2cdeea2f1a6fe(
    value: typing.Optional[OceancdStrategyCanary],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86fd045cc62f8b717b93d3785ac94ca804edf5628aae059f2fdfae6b9e1c1a0c(
    *,
    pause: typing.Optional[typing.Union[OceancdStrategyCanaryStepsPause, typing.Dict[builtins.str, typing.Any]]] = None,
    set_canary_scale: typing.Optional[typing.Union[OceancdStrategyCanaryStepsSetCanaryScale, typing.Dict[builtins.str, typing.Any]]] = None,
    set_header_route: typing.Optional[typing.Union[OceancdStrategyCanaryStepsSetHeaderRoute, typing.Dict[builtins.str, typing.Any]]] = None,
    set_weight: typing.Optional[jsii.Number] = None,
    step_name: typing.Optional[builtins.str] = None,
    verification: typing.Optional[typing.Union[OceancdStrategyCanaryStepsVerification, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a159c127f63881987bc8dbe067d4465bf9576cd4ef3380eb5883f5c71b81418(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3ad9dd209b016ba03377a96df6b0f9f093bcfc3e7e86f3f52dbd4f6c7eecb0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a7461475c4c703d382d72b7214a3d83df6b9f2098fe852df27c398149a11219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6419a44ee7a5fe8c29cfc46d64206a8274726bb123fa288c8682c8222cebad74(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04d1120183c9bee82878a357efc3b0ce4884df52618683f0865cc4afd82e4294(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__379a8caa0601e94a26dea5ff92687a53c3407843fa20ec6190b1356424e9eefd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanarySteps]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aa9f866b044d51dc10fa2b55bc731b46ceddb49e18b5fa34762c7310941ae8c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9facbbea3d67af83afac53485dd1d94d85fa447ab744dadcfed0ac9a71ee9fc5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79c979bea962a1a2004f873903c9f9ac66c6643b677c63f3d05335e18c038432(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eef28f05a5acdaecfbf6ec50b2653840ea44bde83bf7749010869521f834cc50(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanarySteps]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__168624ba1b014777751d37a6ada51d445bbed173670b34bc8d817c4d4a6469c0(
    *,
    duration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2a8aa197809fb3ee0d2f14d259eb0a2fa095813e82607b789bced6941806656(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22abd24aca0f55e3991183b3e8e9d006dd9b5ec78d4371fa34a9f6091293ea41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f3f952cb941c7e63aa0f110bf1077388994e2324b8e1224ec8e1de603a12dde(
    value: typing.Optional[OceancdStrategyCanaryStepsPause],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c67775b608a7fa6cf0f910669f85c4b3a8fc4feded08260f0559c85a5ae80fa6(
    *,
    match_traffic_weight: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    replicas: typing.Optional[jsii.Number] = None,
    weight: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3a19b8c2966a25a5fca46b4b7d2dae704838401ce05dca76cf31f9a13a332fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4699e609bffeb4dac97322bae273227995336d417f1d35233b7184f7cd1e4bb9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7bae541472376229a1ae3c5ce01d153424d7b5ab59c7c6f8f70d00049f99367(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0b173524d4afc12a6f4948967e3a223189bfa6c10bd2847613a3f0eb6955036(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6767c30b2330b3a3ca6e6b4fa7d556f7081119f035d0182d0a65f629a13a5d16(
    value: typing.Optional[OceancdStrategyCanaryStepsSetCanaryScale],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0772a75048b8dfe65281dc74c1fbff992c0cef00faa307a666d1bb08aa621afb(
    *,
    header_route_name: builtins.str,
    match: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyCanaryStepsSetHeaderRouteMatch, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__533c473f974ad763eaf5727ca36cce6e939b27ee42d5ae2adcc6250e65486573(
    *,
    header_name: builtins.str,
    header_value: typing.Union[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62d034910a727b6367093ee465da5b30fb3d9e2638115914028ee80476ea6c1b(
    *,
    exact: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    regex: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccb45524693bbe795a7dc63c626ae505808f9cceb87e5422d77b358e54f04aeb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77d352a6dfba3c7c8034218f958089f1eea39582f346df97832c614cf75bc9c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1c2f7af4279f955053e0fc601d3912b41f597bc10cee6d6cbee5cf05363abec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6787715e90815a7a7e29c956b4973459e284dca9197aaf189c3ac8d3ca7257f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94ca463f9c0b9ea22205ab3f548daea8479b09252d9cb14d6140fc2f830f1332(
    value: typing.Optional[OceancdStrategyCanaryStepsSetHeaderRouteMatchHeaderValue],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7eeefd2fe1f6238453fb1dd28677584dc125e9155a461a7733d7c25e5fc7c5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f96c7148b410c3b445ebdfea151aa4f128200414577bd76d45ff255a6f344ce(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8ad37822013f0ce30884a38fd817ad5449e92b7923208222780b73fd50ff239(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0e110ba1dd79c5ce1f87fd642d299013d808beebf3041db395ebfd7eb0d1d55(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__177a69e080d547db30d35a004cff974282f5f6ec0e37c96d5fa01b73a385ff7a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f06f9d6ad5bdc67efde5b4017b8e688671c2702afc9aec57b71fdc32d7ae2fd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyCanaryStepsSetHeaderRouteMatch]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ff907c3f98825b9ed55beeb4b6251d7eb9aa5d178699e6548c4dc786698250d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2466c71a4130dcf594ce01e1bbce1b85ec30d25fd4e4b0f70aaaf10c0fa196c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1add723e1ce81fd492a3bd0fabefb68d1c029a06eae48829891a7517f06937b5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyCanaryStepsSetHeaderRouteMatch]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__061c208ac12902e984f794c758de78da33fb884024e68e8e3e9ec60cd803bd7a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b427862f4d36c8d271b173e9a0495376ae1ba43a11a1112688a76bcffa322d4b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyCanaryStepsSetHeaderRouteMatch, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08de43ff960d38996e10793bf67f6097770c2baf5f20f1f9320918e7b40725af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5dbef95c08346dcd15cb690ad78a0f3cfe757113618bdc50d1984ef1630af11(
    value: typing.Optional[OceancdStrategyCanaryStepsSetHeaderRoute],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65442edb96daa72ac0a95cf1b41248bbce28482fe24801f69166b645e8e77419(
    *,
    template_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d40402e14b8eafa14993e9700200fac8f19fe4f7ddeaf28c76b1d7d1e784120b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc96bd3092d0936113e1f78937a22f21f1f06abe5ea0c6d822f3909a6cbae7d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07dfa716d996d13e5f020907c88bdba4060bc6e5218087434f715f0389fcfd2f(
    value: typing.Optional[OceancdStrategyCanaryStepsVerification],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6eb898f66c5400da92d8a80c50de04a4099ca0cf1c0b5bf8e95328c1f9f577d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    strategy_name: builtins.str,
    canary: typing.Optional[typing.Union[OceancdStrategyCanary, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    rolling: typing.Optional[typing.Union[OceancdStrategyRolling, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6a5cbf6efcc11108e3e9087428360f7c784aaa0fa27bf18e3f1254edb6c9c0(
    *,
    steps: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyRollingSteps, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e51f81e0bdc09ac2e60948e1946fcd5a3eef0a1d6bfce1b817733cb3b5209de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02f5c225801110604d2b7813d9fba731b3bfba56508bdd7ff5f665b7322534de(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdStrategyRollingSteps, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679844bf3f0b3d542b571839bebeda461124987d469a6f73644bea7349b910b4(
    value: typing.Optional[OceancdStrategyRolling],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f65c67018d6125a5ad948db7b71a983d036707bad0cc4369da019b525a553b3d(
    *,
    pause: typing.Optional[typing.Union[OceancdStrategyRollingStepsPause, typing.Dict[builtins.str, typing.Any]]] = None,
    steps_name: typing.Optional[builtins.str] = None,
    verification: typing.Optional[typing.Union[OceancdStrategyRollingStepsVerification, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24df36adbfcda1e16c155c9ecf3a3382f2318e380aa18700ae99b0e43849a306(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a0624af3139cb48f9e44be637fb8f7569e37307b8f57fd2da5c76cd590c2c0a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ff208d2f2e3ae942facd8e92f3006319ce87e5b6421ef024f7e6b0792bed8b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__312641f18267f98c163ca46dead6329f7d71a71efb5683790185b664b90fb90e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5be66e8adc28b1387ff03643e50e58ef8c2b989a2752f37b6c9ff1056fd36c8b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e8fa42bc21ca3fd57168d4247725d810b92979dd61708cabd09a169794643a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdStrategyRollingSteps]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4799b6d5480851a1a8253323320dda247db316d584ee29aa6c78fca7f34829b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8306a57f797d7d37f0e947a986c4c2999b6683a1ad03aa95b0ce0b736d7586f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e6a76438e81ff8793a12c3098702086459492f827e59fd21a9ec0c68e07e60f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdStrategyRollingSteps]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c51b79d2c8d6bc2cc552e6e50052434a2088c4f0090e157ecfa3e8885434d73e(
    *,
    duration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5127d6bc8d00ad20abf2b4b7473b47ac13009944132e9704092813351592cd7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a9e088a5de97bc5244532b2422710a85085a8ddb427a31e0a272f368a6919dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9579b00f96f1272f17ea02b71d8e9820f260be34efc68dfa7d8a29a6a557e7d(
    value: typing.Optional[OceancdStrategyRollingStepsPause],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5012f1f9a5debea5087dc97affe0967ba321447f83c1622337d81ab3a3d8305c(
    *,
    template_names: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a188ab4d082e72e2386254a40a8262ff3b461d2fe611f6fe10fbfb4e302d59d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59d24ca5a35b40664ad2352a626586ca567b983b45eff4f033b6b428b8ebaf25(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5e85a2762ae4849b932f193e3907534d04c2ccdef8baffa1869e69c94c1bd08(
    value: typing.Optional[OceancdStrategyRollingStepsVerification],
) -> None:
    """Type checking stubs"""
    pass
