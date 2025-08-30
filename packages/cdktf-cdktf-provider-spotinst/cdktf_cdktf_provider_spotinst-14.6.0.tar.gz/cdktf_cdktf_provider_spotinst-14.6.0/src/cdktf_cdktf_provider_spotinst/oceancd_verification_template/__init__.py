r'''
# `spotinst_oceancd_verification_template`

Refer to the Terraform Registry for docs: [`spotinst_oceancd_verification_template`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template).
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


class OceancdVerificationTemplate(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplate",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template spotinst_oceancd_verification_template}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateArgs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetrics", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template spotinst_oceancd_verification_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#name OceancdVerificationTemplate#name}.
        :param args: args block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#args OceancdVerificationTemplate#args}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#id OceancdVerificationTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metrics: metrics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metrics OceancdVerificationTemplate#metrics}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a12fda4f6878c20e82681e9263b5110dbe2eb3d066dbba2cc9ff19ce6aecbcd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceancdVerificationTemplateConfig(
            name=name,
            args=args,
            id=id,
            metrics=metrics,
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
        '''Generates CDKTF code for importing a OceancdVerificationTemplate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceancdVerificationTemplate to import.
        :param import_from_id: The id of the existing OceancdVerificationTemplate that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceancdVerificationTemplate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__782e40265bf9577923bec620a65f9e32425fda1af1bb4af264f90444ca2d089f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putArgs")
    def put_args(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateArgs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3212cbc442b9e88edb29c54af51521659de211af6f5e541f74426271bc0a76c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putArgs", [value]))

    @jsii.member(jsii_name="putMetrics")
    def put_metrics(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetrics", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba32a316a1466409ea6d304d710790c9089974895473ae77edfa010d746f36a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMetrics", [value]))

    @jsii.member(jsii_name="resetArgs")
    def reset_args(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArgs", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMetrics")
    def reset_metrics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetrics", []))

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
    @jsii.member(jsii_name="args")
    def args(self) -> "OceancdVerificationTemplateArgsList":
        return typing.cast("OceancdVerificationTemplateArgsList", jsii.get(self, "args"))

    @builtins.property
    @jsii.member(jsii_name="metrics")
    def metrics(self) -> "OceancdVerificationTemplateMetricsList":
        return typing.cast("OceancdVerificationTemplateMetricsList", jsii.get(self, "metrics"))

    @builtins.property
    @jsii.member(jsii_name="argsInput")
    def args_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateArgs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateArgs"]]], jsii.get(self, "argsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="metricsInput")
    def metrics_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetrics"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetrics"]]], jsii.get(self, "metricsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f84b4063ed012eabefa6ccee5ac6e70e3613a0d5c602e80041b9a8586c58faef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__613d2e71f2d1c32a93c20b005f6d6c39eb365957de8f871c603230f6a3d0203a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgs",
    jsii_struct_bases=[],
    name_mapping={"arg_name": "argName", "value": "value", "value_from": "valueFrom"},
)
class OceancdVerificationTemplateArgs:
    def __init__(
        self,
        *,
        arg_name: builtins.str,
        value: typing.Optional[builtins.str] = None,
        value_from: typing.Optional[typing.Union["OceancdVerificationTemplateArgsValueFrom", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param arg_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#arg_name OceancdVerificationTemplate#arg_name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#value OceancdVerificationTemplate#value}.
        :param value_from: value_from block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#value_from OceancdVerificationTemplate#value_from}
        '''
        if isinstance(value_from, dict):
            value_from = OceancdVerificationTemplateArgsValueFrom(**value_from)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e452c216ef7320fd9314d56f6bf3b765421707e2aa22f53e3bb19f5585a1f6c)
            check_type(argname="argument arg_name", value=arg_name, expected_type=type_hints["arg_name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument value_from", value=value_from, expected_type=type_hints["value_from"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arg_name": arg_name,
        }
        if value is not None:
            self._values["value"] = value
        if value_from is not None:
            self._values["value_from"] = value_from

    @builtins.property
    def arg_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#arg_name OceancdVerificationTemplate#arg_name}.'''
        result = self._values.get("arg_name")
        assert result is not None, "Required property 'arg_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#value OceancdVerificationTemplate#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value_from(self) -> typing.Optional["OceancdVerificationTemplateArgsValueFrom"]:
        '''value_from block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#value_from OceancdVerificationTemplate#value_from}
        '''
        result = self._values.get("value_from")
        return typing.cast(typing.Optional["OceancdVerificationTemplateArgsValueFrom"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateArgsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ed30b5b940ecdf0cac0344b3970703456af2962b284f6d3aadaaadc027150c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateArgsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39eb0386acfcc47c32365100b9af024e2cd62e5fb7c4b9c083df3789c0f58bf9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateArgsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30dca440edbe58d5dffaa570feadf67db3b896dce8364f16e6307a1136e25314)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4062d9a81dfcbec3c7e11d4f7fee5a739cb051254225497caa3eaa60364f17c3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41f06077cf24857181e754a5c35fb382c55e5500f0b2e58abe51993f9a1a8618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateArgs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateArgs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateArgs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d4162220d1e2247fde65944a45543adb83f2a56b8329bac19f553912d95db95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateArgsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3d9adf58d3f9190707c13eaa513f43fd88b034d7aa925d63a5e86c4d726043d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putValueFrom")
    def put_value_from(
        self,
        *,
        secret_key_ref: typing.Optional[typing.Union["OceancdVerificationTemplateArgsValueFromSecretKeyRef", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param secret_key_ref: secret_key_ref block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#secret_key_ref OceancdVerificationTemplate#secret_key_ref}
        '''
        value = OceancdVerificationTemplateArgsValueFrom(secret_key_ref=secret_key_ref)

        return typing.cast(None, jsii.invoke(self, "putValueFrom", [value]))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @jsii.member(jsii_name="resetValueFrom")
    def reset_value_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValueFrom", []))

    @builtins.property
    @jsii.member(jsii_name="valueFrom")
    def value_from(self) -> "OceancdVerificationTemplateArgsValueFromOutputReference":
        return typing.cast("OceancdVerificationTemplateArgsValueFromOutputReference", jsii.get(self, "valueFrom"))

    @builtins.property
    @jsii.member(jsii_name="argNameInput")
    def arg_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "argNameInput"))

    @builtins.property
    @jsii.member(jsii_name="valueFromInput")
    def value_from_input(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateArgsValueFrom"]:
        return typing.cast(typing.Optional["OceancdVerificationTemplateArgsValueFrom"], jsii.get(self, "valueFromInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="argName")
    def arg_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "argName"))

    @arg_name.setter
    def arg_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d51a5d4aeca15a4669f7a6c22d3cd938a6da69915a889c31bf291dd7b41c1fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "argName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c58a641e2ee7765d953e80830cc71bb679ef4fb7e9327f009293be6731d076)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateArgs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateArgs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateArgs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96fdd0840f9bd81e846ada99687cc1a110f56f0ac81edb974d38c07057702c09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgsValueFrom",
    jsii_struct_bases=[],
    name_mapping={"secret_key_ref": "secretKeyRef"},
)
class OceancdVerificationTemplateArgsValueFrom:
    def __init__(
        self,
        *,
        secret_key_ref: typing.Optional[typing.Union["OceancdVerificationTemplateArgsValueFromSecretKeyRef", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param secret_key_ref: secret_key_ref block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#secret_key_ref OceancdVerificationTemplate#secret_key_ref}
        '''
        if isinstance(secret_key_ref, dict):
            secret_key_ref = OceancdVerificationTemplateArgsValueFromSecretKeyRef(**secret_key_ref)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f6f24546ef78d4b314bd70c9949c5b52b8124a1f76e55d0ba6b630d86c3b924)
            check_type(argname="argument secret_key_ref", value=secret_key_ref, expected_type=type_hints["secret_key_ref"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if secret_key_ref is not None:
            self._values["secret_key_ref"] = secret_key_ref

    @builtins.property
    def secret_key_ref(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateArgsValueFromSecretKeyRef"]:
        '''secret_key_ref block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#secret_key_ref OceancdVerificationTemplate#secret_key_ref}
        '''
        result = self._values.get("secret_key_ref")
        return typing.cast(typing.Optional["OceancdVerificationTemplateArgsValueFromSecretKeyRef"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateArgsValueFrom(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateArgsValueFromOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgsValueFromOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e59188e742c55f04ee4d0f28b7d7fdca0830dadace3d3486b740975e19fb05e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSecretKeyRef")
    def put_secret_key_ref(self, *, key: builtins.str, name: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#key OceancdVerificationTemplate#key}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#name OceancdVerificationTemplate#name}.
        '''
        value = OceancdVerificationTemplateArgsValueFromSecretKeyRef(
            key=key, name=name
        )

        return typing.cast(None, jsii.invoke(self, "putSecretKeyRef", [value]))

    @jsii.member(jsii_name="resetSecretKeyRef")
    def reset_secret_key_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretKeyRef", []))

    @builtins.property
    @jsii.member(jsii_name="secretKeyRef")
    def secret_key_ref(
        self,
    ) -> "OceancdVerificationTemplateArgsValueFromSecretKeyRefOutputReference":
        return typing.cast("OceancdVerificationTemplateArgsValueFromSecretKeyRefOutputReference", jsii.get(self, "secretKeyRef"))

    @builtins.property
    @jsii.member(jsii_name="secretKeyRefInput")
    def secret_key_ref_input(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateArgsValueFromSecretKeyRef"]:
        return typing.cast(typing.Optional["OceancdVerificationTemplateArgsValueFromSecretKeyRef"], jsii.get(self, "secretKeyRefInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateArgsValueFrom]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateArgsValueFrom], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateArgsValueFrom],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e879d65073d3157335924f0154baae4415d8a9eef617b46eeb862247724011b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgsValueFromSecretKeyRef",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "name": "name"},
)
class OceancdVerificationTemplateArgsValueFromSecretKeyRef:
    def __init__(self, *, key: builtins.str, name: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#key OceancdVerificationTemplate#key}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#name OceancdVerificationTemplate#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ade934b5799c68438c6e674226d54b0555366a4923c9b0743eb0d7c220a883d7)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "name": name,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#key OceancdVerificationTemplate#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#name OceancdVerificationTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateArgsValueFromSecretKeyRef(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateArgsValueFromSecretKeyRefOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateArgsValueFromSecretKeyRefOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e3eb2a44a05237e6cb6246eecbeb6bef09a2ef61747d381bd3ef207da23609c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caaf5a76ac3d2bee673b052f7b5b5d81c50ccb88dca9ed16ca42929907a193b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e83f48fe7b8551bfe3e0990f2e2d0ddebb464c5698a21eb820c359352dfe26e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateArgsValueFromSecretKeyRef]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateArgsValueFromSecretKeyRef], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateArgsValueFromSecretKeyRef],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__670c07b7470a703c3aa38b4f1b0f86edb1c83e914b6b1ccaaec285e6d6d67ea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateConfig",
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
        "args": "args",
        "id": "id",
        "metrics": "metrics",
    },
)
class OceancdVerificationTemplateConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateArgs, typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetrics", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#name OceancdVerificationTemplate#name}.
        :param args: args block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#args OceancdVerificationTemplate#args}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#id OceancdVerificationTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metrics: metrics block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metrics OceancdVerificationTemplate#metrics}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__314bc0934431d84bd5cc373437a5d41d2c7e1077d468aef9f10868e14d92b80c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument args", value=args, expected_type=type_hints["args"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument metrics", value=metrics, expected_type=type_hints["metrics"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
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
        if args is not None:
            self._values["args"] = args
        if id is not None:
            self._values["id"] = id
        if metrics is not None:
            self._values["metrics"] = metrics

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#name OceancdVerificationTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateArgs]]]:
        '''args block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#args OceancdVerificationTemplate#args}
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateArgs]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#id OceancdVerificationTemplate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metrics(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetrics"]]]:
        '''metrics block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metrics OceancdVerificationTemplate#metrics}
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetrics"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetrics",
    jsii_struct_bases=[],
    name_mapping={
        "metrics_name": "metricsName",
        "provider": "provider",
        "baseline": "baseline",
        "consecutive_error_limit": "consecutiveErrorLimit",
        "count": "count",
        "dry_run": "dryRun",
        "failure_condition": "failureCondition",
        "failure_limit": "failureLimit",
        "initial_delay": "initialDelay",
        "interval": "interval",
        "success_condition": "successCondition",
    },
)
class OceancdVerificationTemplateMetrics:
    def __init__(
        self,
        *,
        metrics_name: builtins.str,
        provider: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProvider", typing.Dict[builtins.str, typing.Any]]]],
        baseline: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsBaseline", typing.Dict[builtins.str, typing.Any]]] = None,
        consecutive_error_limit: typing.Optional[jsii.Number] = None,
        count: typing.Optional[jsii.Number] = None,
        dry_run: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        failure_condition: typing.Optional[builtins.str] = None,
        failure_limit: typing.Optional[jsii.Number] = None,
        initial_delay: typing.Optional[builtins.str] = None,
        interval: typing.Optional[builtins.str] = None,
        success_condition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metrics_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metrics_name OceancdVerificationTemplate#metrics_name}.
        :param provider: provider block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#provider OceancdVerificationTemplate#provider}
        :param baseline: baseline block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#baseline OceancdVerificationTemplate#baseline}
        :param consecutive_error_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#consecutive_error_limit OceancdVerificationTemplate#consecutive_error_limit}.
        :param count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#count OceancdVerificationTemplate#count}.
        :param dry_run: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dry_run OceancdVerificationTemplate#dry_run}.
        :param failure_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#failure_condition OceancdVerificationTemplate#failure_condition}.
        :param failure_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#failure_limit OceancdVerificationTemplate#failure_limit}.
        :param initial_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#initial_delay OceancdVerificationTemplate#initial_delay}.
        :param interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#interval OceancdVerificationTemplate#interval}.
        :param success_condition: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#success_condition OceancdVerificationTemplate#success_condition}.
        '''
        if isinstance(baseline, dict):
            baseline = OceancdVerificationTemplateMetricsBaseline(**baseline)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67c26268471e62a5a9dbd7c0c74bc9e79ff13e9392ae878fe532ecad11a841e7)
            check_type(argname="argument metrics_name", value=metrics_name, expected_type=type_hints["metrics_name"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument baseline", value=baseline, expected_type=type_hints["baseline"])
            check_type(argname="argument consecutive_error_limit", value=consecutive_error_limit, expected_type=type_hints["consecutive_error_limit"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument dry_run", value=dry_run, expected_type=type_hints["dry_run"])
            check_type(argname="argument failure_condition", value=failure_condition, expected_type=type_hints["failure_condition"])
            check_type(argname="argument failure_limit", value=failure_limit, expected_type=type_hints["failure_limit"])
            check_type(argname="argument initial_delay", value=initial_delay, expected_type=type_hints["initial_delay"])
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument success_condition", value=success_condition, expected_type=type_hints["success_condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metrics_name": metrics_name,
            "provider": provider,
        }
        if baseline is not None:
            self._values["baseline"] = baseline
        if consecutive_error_limit is not None:
            self._values["consecutive_error_limit"] = consecutive_error_limit
        if count is not None:
            self._values["count"] = count
        if dry_run is not None:
            self._values["dry_run"] = dry_run
        if failure_condition is not None:
            self._values["failure_condition"] = failure_condition
        if failure_limit is not None:
            self._values["failure_limit"] = failure_limit
        if initial_delay is not None:
            self._values["initial_delay"] = initial_delay
        if interval is not None:
            self._values["interval"] = interval
        if success_condition is not None:
            self._values["success_condition"] = success_condition

    @builtins.property
    def metrics_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metrics_name OceancdVerificationTemplate#metrics_name}.'''
        result = self._values.get("metrics_name")
        assert result is not None, "Required property 'metrics_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProvider"]]:
        '''provider block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#provider OceancdVerificationTemplate#provider}
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProvider"]], result)

    @builtins.property
    def baseline(self) -> typing.Optional["OceancdVerificationTemplateMetricsBaseline"]:
        '''baseline block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#baseline OceancdVerificationTemplate#baseline}
        '''
        result = self._values.get("baseline")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsBaseline"], result)

    @builtins.property
    def consecutive_error_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#consecutive_error_limit OceancdVerificationTemplate#consecutive_error_limit}.'''
        result = self._values.get("consecutive_error_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#count OceancdVerificationTemplate#count}.'''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dry_run(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dry_run OceancdVerificationTemplate#dry_run}.'''
        result = self._values.get("dry_run")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def failure_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#failure_condition OceancdVerificationTemplate#failure_condition}.'''
        result = self._values.get("failure_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failure_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#failure_limit OceancdVerificationTemplate#failure_limit}.'''
        result = self._values.get("failure_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def initial_delay(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#initial_delay OceancdVerificationTemplate#initial_delay}.'''
        result = self._values.get("initial_delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#interval OceancdVerificationTemplate#interval}.'''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def success_condition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#success_condition OceancdVerificationTemplate#success_condition}.'''
        result = self._values.get("success_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetrics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaseline",
    jsii_struct_bases=[],
    name_mapping={
        "baseline_provider": "baselineProvider",
        "threshold": "threshold",
        "max_range": "maxRange",
        "min_range": "minRange",
    },
)
class OceancdVerificationTemplateMetricsBaseline:
    def __init__(
        self,
        *,
        baseline_provider: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsBaselineBaselineProvider", typing.Dict[builtins.str, typing.Any]]]],
        threshold: builtins.str,
        max_range: typing.Optional[jsii.Number] = None,
        min_range: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param baseline_provider: baseline_provider block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#baseline_provider OceancdVerificationTemplate#baseline_provider}
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#threshold OceancdVerificationTemplate#threshold}.
        :param max_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#max_range OceancdVerificationTemplate#max_range}.
        :param min_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#min_range OceancdVerificationTemplate#min_range}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6760d59051d8a9f62139d3e2e5dd74729bb50bb6d76f62edc01bca26dbd5dec3)
            check_type(argname="argument baseline_provider", value=baseline_provider, expected_type=type_hints["baseline_provider"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument max_range", value=max_range, expected_type=type_hints["max_range"])
            check_type(argname="argument min_range", value=min_range, expected_type=type_hints["min_range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "baseline_provider": baseline_provider,
            "threshold": threshold,
        }
        if max_range is not None:
            self._values["max_range"] = max_range
        if min_range is not None:
            self._values["min_range"] = min_range

    @builtins.property
    def baseline_provider(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsBaselineBaselineProvider"]]:
        '''baseline_provider block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#baseline_provider OceancdVerificationTemplate#baseline_provider}
        '''
        result = self._values.get("baseline_provider")
        assert result is not None, "Required property 'baseline_provider' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsBaselineBaselineProvider"]], result)

    @builtins.property
    def threshold(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#threshold OceancdVerificationTemplate#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_range(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#max_range OceancdVerificationTemplate#max_range}.'''
        result = self._values.get("max_range")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_range(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#min_range OceancdVerificationTemplate#min_range}.'''
        result = self._values.get("min_range")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsBaseline(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProvider",
    jsii_struct_bases=[],
    name_mapping={
        "datadog": "datadog",
        "new_relic": "newRelic",
        "prometheus": "prometheus",
    },
)
class OceancdVerificationTemplateMetricsBaselineBaselineProvider:
    def __init__(
        self,
        *,
        datadog: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog", typing.Dict[builtins.str, typing.Any]]] = None,
        new_relic: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic", typing.Dict[builtins.str, typing.Any]]] = None,
        prometheus: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param datadog: datadog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog OceancdVerificationTemplate#datadog}
        :param new_relic: new_relic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic OceancdVerificationTemplate#new_relic}
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus OceancdVerificationTemplate#prometheus}
        '''
        if isinstance(datadog, dict):
            datadog = OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog(**datadog)
        if isinstance(new_relic, dict):
            new_relic = OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic(**new_relic)
        if isinstance(prometheus, dict):
            prometheus = OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus(**prometheus)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dadf6c5328ae4d6782d1c8c52f99a80bd8b3d41fa3477ff4e65c3d7f3f6b6a6)
            check_type(argname="argument datadog", value=datadog, expected_type=type_hints["datadog"])
            check_type(argname="argument new_relic", value=new_relic, expected_type=type_hints["new_relic"])
            check_type(argname="argument prometheus", value=prometheus, expected_type=type_hints["prometheus"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if datadog is not None:
            self._values["datadog"] = datadog
        if new_relic is not None:
            self._values["new_relic"] = new_relic
        if prometheus is not None:
            self._values["prometheus"] = prometheus

    @builtins.property
    def datadog(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog"]:
        '''datadog block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog OceancdVerificationTemplate#datadog}
        '''
        result = self._values.get("datadog")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog"], result)

    @builtins.property
    def new_relic(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic"]:
        '''new_relic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic OceancdVerificationTemplate#new_relic}
        '''
        result = self._values.get("new_relic")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic"], result)

    @builtins.property
    def prometheus(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus"]:
        '''prometheus block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus OceancdVerificationTemplate#prometheus}
        '''
        result = self._values.get("prometheus")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsBaselineBaselineProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog",
    jsii_struct_bases=[],
    name_mapping={"datadog_query": "datadogQuery", "duration": "duration"},
)
class OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog:
    def __init__(
        self,
        *,
        datadog_query: builtins.str,
        duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datadog_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog_query OceancdVerificationTemplate#datadog_query}.
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a20390d7eb3d24958dd544030b8bf7733c841b981049504c937b6dc6e9eda59)
            check_type(argname="argument datadog_query", value=datadog_query, expected_type=type_hints["datadog_query"])
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datadog_query": datadog_query,
        }
        if duration is not None:
            self._values["duration"] = duration

    @builtins.property
    def datadog_query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog_query OceancdVerificationTemplate#datadog_query}.'''
        result = self._values.get("datadog_query")
        assert result is not None, "Required property 'datadog_query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e1c48a57b78018b3c163dad151b91a101568c18443ba623cc7faeffbf1decdef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @builtins.property
    @jsii.member(jsii_name="datadogQueryInput")
    def datadog_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datadogQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="datadogQuery")
    def datadog_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datadogQuery"))

    @datadog_query.setter
    def datadog_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de1aa6357772e50290a74f00c809d6f297d2774330ccafa51a0fcace2ca608eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datadogQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec25feadcf6ce383d292c9e3f4c923b76e37a710ad09b2176cd9180cf74f5e01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69feb638cdd59773db5814076e247251f6421d1a8e74c1e1d68b3fe038e8dac4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsBaselineBaselineProviderList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c86fba526d9a33d306e7446284c6ecbbe35564377322da74cfad6cabd572130f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsBaselineBaselineProviderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d579059e6f15ad2cd5cc13b47984e4e5f5e75769ab84d4cbebb0bd6fc67fa2b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsBaselineBaselineProviderOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1db1c74cedeaf5be6f507b7b9cacb02c1a8729e8002bd7d85c546880e816dfd7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e34830be59ba56beb4cdea16aa604bf63cf9d3cc42c175873b49d1efd057c817)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7fe4acd679ca24657f4efeb833f28fcb9e1932a16aa7f738023d5b3187833a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsBaselineBaselineProvider]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsBaselineBaselineProvider]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsBaselineBaselineProvider]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__033d33a1567fbb071079349404f577468d4d3ef8d74298b6de63244c77a6dc65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic",
    jsii_struct_bases=[],
    name_mapping={"new_relic_query": "newRelicQuery", "profile": "profile"},
)
class OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic:
    def __init__(
        self,
        *,
        new_relic_query: builtins.str,
        profile: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param new_relic_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic_query OceancdVerificationTemplate#new_relic_query}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#profile OceancdVerificationTemplate#profile}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70859eb8cafe290d4da95a8c482bbbcf0322eb1ee797412d1bac8e3f61b324e0)
            check_type(argname="argument new_relic_query", value=new_relic_query, expected_type=type_hints["new_relic_query"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "new_relic_query": new_relic_query,
        }
        if profile is not None:
            self._values["profile"] = profile

    @builtins.property
    def new_relic_query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic_query OceancdVerificationTemplate#new_relic_query}.'''
        result = self._values.get("new_relic_query")
        assert result is not None, "Required property 'new_relic_query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#profile OceancdVerificationTemplate#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelicOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelicOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__be65c270841ae2954c3576a8160e5d5db896b45c06aeb9c0212f94f2ed0e3f67)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @builtins.property
    @jsii.member(jsii_name="newRelicQueryInput")
    def new_relic_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "newRelicQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="newRelicQuery")
    def new_relic_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newRelicQuery"))

    @new_relic_query.setter
    def new_relic_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40f8e0f879c0e898459c52fad9b94af61b451ff8021204033eca77f30a9bbb67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newRelicQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce12b78f6d36d9d9adb426dfd8980f88c11739f546a8b627ef2637c16de43edb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1fc0e9add38ab12740c3bdb6acab8c1e5e4864174793e4d9d643762b05a71e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsBaselineBaselineProviderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd9cbbf8af4aadbcc2aa4519314e99407aea0e843f38afbf091cadc38f7081cf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDatadog")
    def put_datadog(
        self,
        *,
        datadog_query: builtins.str,
        duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datadog_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog_query OceancdVerificationTemplate#datadog_query}.
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.
        '''
        value = OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog(
            datadog_query=datadog_query, duration=duration
        )

        return typing.cast(None, jsii.invoke(self, "putDatadog", [value]))

    @jsii.member(jsii_name="putNewRelic")
    def put_new_relic(
        self,
        *,
        new_relic_query: builtins.str,
        profile: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param new_relic_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic_query OceancdVerificationTemplate#new_relic_query}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#profile OceancdVerificationTemplate#profile}.
        '''
        value = OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic(
            new_relic_query=new_relic_query, profile=profile
        )

        return typing.cast(None, jsii.invoke(self, "putNewRelic", [value]))

    @jsii.member(jsii_name="putPrometheus")
    def put_prometheus(self, *, prometheus_query: builtins.str) -> None:
        '''
        :param prometheus_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus_query OceancdVerificationTemplate#prometheus_query}.
        '''
        value = OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus(
            prometheus_query=prometheus_query
        )

        return typing.cast(None, jsii.invoke(self, "putPrometheus", [value]))

    @jsii.member(jsii_name="resetDatadog")
    def reset_datadog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatadog", []))

    @jsii.member(jsii_name="resetNewRelic")
    def reset_new_relic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewRelic", []))

    @jsii.member(jsii_name="resetPrometheus")
    def reset_prometheus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrometheus", []))

    @builtins.property
    @jsii.member(jsii_name="datadog")
    def datadog(
        self,
    ) -> OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadogOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadogOutputReference, jsii.get(self, "datadog"))

    @builtins.property
    @jsii.member(jsii_name="newRelic")
    def new_relic(
        self,
    ) -> OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelicOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelicOutputReference, jsii.get(self, "newRelic"))

    @builtins.property
    @jsii.member(jsii_name="prometheus")
    def prometheus(
        self,
    ) -> "OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheusOutputReference":
        return typing.cast("OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheusOutputReference", jsii.get(self, "prometheus"))

    @builtins.property
    @jsii.member(jsii_name="datadogInput")
    def datadog_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog], jsii.get(self, "datadogInput"))

    @builtins.property
    @jsii.member(jsii_name="newRelicInput")
    def new_relic_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic], jsii.get(self, "newRelicInput"))

    @builtins.property
    @jsii.member(jsii_name="prometheusInput")
    def prometheus_input(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus"]:
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus"], jsii.get(self, "prometheusInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsBaselineBaselineProvider]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsBaselineBaselineProvider]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsBaselineBaselineProvider]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dbc04acd579bcd96985f1cdfc35347bd59fce11f6883f5b8cbc751eb855c5ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus",
    jsii_struct_bases=[],
    name_mapping={"prometheus_query": "prometheusQuery"},
)
class OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus:
    def __init__(self, *, prometheus_query: builtins.str) -> None:
        '''
        :param prometheus_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus_query OceancdVerificationTemplate#prometheus_query}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__010671dc3bdfb540db27cd689f98c569eba3af0245c33018758b913ecf2c1608)
            check_type(argname="argument prometheus_query", value=prometheus_query, expected_type=type_hints["prometheus_query"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "prometheus_query": prometheus_query,
        }

    @builtins.property
    def prometheus_query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus_query OceancdVerificationTemplate#prometheus_query}.'''
        result = self._values.get("prometheus_query")
        assert result is not None, "Required property 'prometheus_query' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea81d5ba9ed9c2fff65ef0c22adf93dbd2a7b151f5922d3960cb44abdfc220e4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="prometheusQueryInput")
    def prometheus_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prometheusQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="prometheusQuery")
    def prometheus_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prometheusQuery"))

    @prometheus_query.setter
    def prometheus_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9992e2b20cd7734751c7e20b08b5b2eb465281baa7cf81d41cdae2e9db8e4dbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prometheusQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aadff29d6e93a4f9b3d8433fe95f61d0caea7f15dfef92ca4620d80b5258a0af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsBaselineOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsBaselineOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40d2f7b07d1d3c50a5c566dd403107b39d5896ead0132009509d16c62578d559)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putBaselineProvider")
    def put_baseline_provider(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProvider, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb46d879af005330c4915f2a7810720fb3e5ba93d4628dc69286419448028ee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putBaselineProvider", [value]))

    @jsii.member(jsii_name="resetMaxRange")
    def reset_max_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRange", []))

    @jsii.member(jsii_name="resetMinRange")
    def reset_min_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinRange", []))

    @builtins.property
    @jsii.member(jsii_name="baselineProvider")
    def baseline_provider(
        self,
    ) -> OceancdVerificationTemplateMetricsBaselineBaselineProviderList:
        return typing.cast(OceancdVerificationTemplateMetricsBaselineBaselineProviderList, jsii.get(self, "baselineProvider"))

    @builtins.property
    @jsii.member(jsii_name="baselineProviderInput")
    def baseline_provider_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsBaselineBaselineProvider]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsBaselineBaselineProvider]]], jsii.get(self, "baselineProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRangeInput")
    def max_range_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="minRangeInput")
    def min_range_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minRangeInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRange")
    def max_range(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRange"))

    @max_range.setter
    def max_range(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c05b3767603a3e0aa105a79ea122110a5fe7c136b8c664fe681db0c5338e6f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minRange")
    def min_range(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minRange"))

    @min_range.setter
    def min_range(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__254389ad44d9793ebd5303daf6177e7b92f4e1e97c716ae872d16431d32af1a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minRange", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0c2e2b403f8af3d5f791ef9b91a3d00c21239d8632156cbd9abdd7d7c897152)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaseline]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaseline], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsBaseline],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04add745f6b0976bee4f35a15cfd437b4bb3b6006100a21d3f7d4533cca6fae2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc4334cb98f561be4c52e158d8780816ddf2eab6cce79543bffba29b43cd055d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__016b740d68981ad20d7b73284abf9a18e7aee8aa1faf38b93369f03b48a93f5d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b3f58ef70267d7004bccc41ef8e7426a46de3686c7de8d2304c7ba22b9b16eb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__50c2a7e19de3187a90d326c7b5d24143126b8bd2fa73495f2fb45c4c0f9d8c18)
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
            type_hints = typing.get_type_hints(_typecheckingstub__acc5dc1f20f57aef656470ff18a05eff0c4c47b23a4587e22e419f5ee9443463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetrics]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetrics]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetrics]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79683e865095dfcb85e32fa7a2033f314c737aec2cb493159b42dd65ad65251a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d002a81226424d3188635998eaab7a8c8ff75c57afa5291ddb646ce90f11eb49)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putBaseline")
    def put_baseline(
        self,
        *,
        baseline_provider: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProvider, typing.Dict[builtins.str, typing.Any]]]],
        threshold: builtins.str,
        max_range: typing.Optional[jsii.Number] = None,
        min_range: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param baseline_provider: baseline_provider block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#baseline_provider OceancdVerificationTemplate#baseline_provider}
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#threshold OceancdVerificationTemplate#threshold}.
        :param max_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#max_range OceancdVerificationTemplate#max_range}.
        :param min_range: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#min_range OceancdVerificationTemplate#min_range}.
        '''
        value = OceancdVerificationTemplateMetricsBaseline(
            baseline_provider=baseline_provider,
            threshold=threshold,
            max_range=max_range,
            min_range=min_range,
        )

        return typing.cast(None, jsii.invoke(self, "putBaseline", [value]))

    @jsii.member(jsii_name="putProvider")
    def put_provider(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProvider", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bcb52dcc4271cf650effc1bc2800ce25ff7f3420a448ee043be31a3317bc009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putProvider", [value]))

    @jsii.member(jsii_name="resetBaseline")
    def reset_baseline(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseline", []))

    @jsii.member(jsii_name="resetConsecutiveErrorLimit")
    def reset_consecutive_error_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsecutiveErrorLimit", []))

    @jsii.member(jsii_name="resetCount")
    def reset_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCount", []))

    @jsii.member(jsii_name="resetDryRun")
    def reset_dry_run(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDryRun", []))

    @jsii.member(jsii_name="resetFailureCondition")
    def reset_failure_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureCondition", []))

    @jsii.member(jsii_name="resetFailureLimit")
    def reset_failure_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureLimit", []))

    @jsii.member(jsii_name="resetInitialDelay")
    def reset_initial_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitialDelay", []))

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetSuccessCondition")
    def reset_success_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuccessCondition", []))

    @builtins.property
    @jsii.member(jsii_name="baseline")
    def baseline(self) -> OceancdVerificationTemplateMetricsBaselineOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsBaselineOutputReference, jsii.get(self, "baseline"))

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> "OceancdVerificationTemplateMetricsProviderList":
        return typing.cast("OceancdVerificationTemplateMetricsProviderList", jsii.get(self, "provider"))

    @builtins.property
    @jsii.member(jsii_name="baselineInput")
    def baseline_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsBaseline]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsBaseline], jsii.get(self, "baselineInput"))

    @builtins.property
    @jsii.member(jsii_name="consecutiveErrorLimitInput")
    def consecutive_error_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "consecutiveErrorLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="countInput")
    def count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "countInput"))

    @builtins.property
    @jsii.member(jsii_name="dryRunInput")
    def dry_run_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dryRunInput"))

    @builtins.property
    @jsii.member(jsii_name="failureConditionInput")
    def failure_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="failureLimitInput")
    def failure_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failureLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="initialDelayInput")
    def initial_delay_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "initialDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property
    @jsii.member(jsii_name="metricsNameInput")
    def metrics_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricsNameInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProvider"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProvider"]]], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="successConditionInput")
    def success_condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "successConditionInput"))

    @builtins.property
    @jsii.member(jsii_name="consecutiveErrorLimit")
    def consecutive_error_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "consecutiveErrorLimit"))

    @consecutive_error_limit.setter
    def consecutive_error_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__801b0d3abe5301e4cc39afee1dd69c28c23cc9d67d6b4f50d92a4a3798371376)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consecutiveErrorLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53dad91af7ebaa6af15566506d209b834bac88b18d2709195887364cb7f4e12c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "count", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dryRun")
    def dry_run(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dryRun"))

    @dry_run.setter
    def dry_run(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2d4ac99f9ccd592f15458a506a781cef953b61c3e5ee08e838fbaf43701b709)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dryRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failureCondition")
    def failure_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failureCondition"))

    @failure_condition.setter
    def failure_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1552cad160f23c95005ef9bbb72d89e06581e16f7098f33b28e2ff99e10fc6f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failureCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failureLimit")
    def failure_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "failureLimit"))

    @failure_limit.setter
    def failure_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d174020623026423d9056268537c293a11fbdd24d7049976999c22ea2f943370)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failureLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="initialDelay")
    def initial_delay(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "initialDelay"))

    @initial_delay.setter
    def initial_delay(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a63dfb6f0655429cd1c6c1e61871b8ee391a687fc24da914d6f12c2f5ea9e4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initialDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2caa9983db82c325e4d1062dfe8320757862c1a3913c5b3338f748c834906fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metricsName")
    def metrics_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricsName"))

    @metrics_name.setter
    def metrics_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f243dd8964420734ce670498fa310d9d74c20f6d2df5f2b6d65c749aeae7b40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricsName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="successCondition")
    def success_condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "successCondition"))

    @success_condition.setter
    def success_condition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26df54ec76e3b1c694f4e3eb4c12a1c972c7fb2fa998f9f1af5bd7935392533a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "successCondition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetrics]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetrics]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetrics]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcd1c76858e29ba054f97a7b4ce6dc4610ebe9165f8438436479ce2cb9b409ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProvider",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_watch": "cloudWatch",
        "datadog": "datadog",
        "jenkins": "jenkins",
        "job": "job",
        "new_relic": "newRelic",
        "prometheus": "prometheus",
        "web": "web",
    },
)
class OceancdVerificationTemplateMetricsProvider:
    def __init__(
        self,
        *,
        cloud_watch: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderCloudWatch", typing.Dict[builtins.str, typing.Any]]] = None,
        datadog: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderDatadog", typing.Dict[builtins.str, typing.Any]]] = None,
        jenkins: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderJenkins", typing.Dict[builtins.str, typing.Any]]] = None,
        job: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderJob", typing.Dict[builtins.str, typing.Any]]] = None,
        new_relic: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderNewRelic", typing.Dict[builtins.str, typing.Any]]] = None,
        prometheus: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderPrometheus", typing.Dict[builtins.str, typing.Any]]] = None,
        web: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderWeb", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param cloud_watch: cloud_watch block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#cloud_watch OceancdVerificationTemplate#cloud_watch}
        :param datadog: datadog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog OceancdVerificationTemplate#datadog}
        :param jenkins: jenkins block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins OceancdVerificationTemplate#jenkins}
        :param job: job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#job OceancdVerificationTemplate#job}
        :param new_relic: new_relic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic OceancdVerificationTemplate#new_relic}
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus OceancdVerificationTemplate#prometheus}
        :param web: web block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web OceancdVerificationTemplate#web}
        '''
        if isinstance(cloud_watch, dict):
            cloud_watch = OceancdVerificationTemplateMetricsProviderCloudWatch(**cloud_watch)
        if isinstance(datadog, dict):
            datadog = OceancdVerificationTemplateMetricsProviderDatadog(**datadog)
        if isinstance(jenkins, dict):
            jenkins = OceancdVerificationTemplateMetricsProviderJenkins(**jenkins)
        if isinstance(job, dict):
            job = OceancdVerificationTemplateMetricsProviderJob(**job)
        if isinstance(new_relic, dict):
            new_relic = OceancdVerificationTemplateMetricsProviderNewRelic(**new_relic)
        if isinstance(prometheus, dict):
            prometheus = OceancdVerificationTemplateMetricsProviderPrometheus(**prometheus)
        if isinstance(web, dict):
            web = OceancdVerificationTemplateMetricsProviderWeb(**web)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb6437c93f4d27d774e3254fc682f9513c141edc665a7e0c8ac2e73b020b2f36)
            check_type(argname="argument cloud_watch", value=cloud_watch, expected_type=type_hints["cloud_watch"])
            check_type(argname="argument datadog", value=datadog, expected_type=type_hints["datadog"])
            check_type(argname="argument jenkins", value=jenkins, expected_type=type_hints["jenkins"])
            check_type(argname="argument job", value=job, expected_type=type_hints["job"])
            check_type(argname="argument new_relic", value=new_relic, expected_type=type_hints["new_relic"])
            check_type(argname="argument prometheus", value=prometheus, expected_type=type_hints["prometheus"])
            check_type(argname="argument web", value=web, expected_type=type_hints["web"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_watch is not None:
            self._values["cloud_watch"] = cloud_watch
        if datadog is not None:
            self._values["datadog"] = datadog
        if jenkins is not None:
            self._values["jenkins"] = jenkins
        if job is not None:
            self._values["job"] = job
        if new_relic is not None:
            self._values["new_relic"] = new_relic
        if prometheus is not None:
            self._values["prometheus"] = prometheus
        if web is not None:
            self._values["web"] = web

    @builtins.property
    def cloud_watch(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderCloudWatch"]:
        '''cloud_watch block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#cloud_watch OceancdVerificationTemplate#cloud_watch}
        '''
        result = self._values.get("cloud_watch")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderCloudWatch"], result)

    @builtins.property
    def datadog(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderDatadog"]:
        '''datadog block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog OceancdVerificationTemplate#datadog}
        '''
        result = self._values.get("datadog")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderDatadog"], result)

    @builtins.property
    def jenkins(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderJenkins"]:
        '''jenkins block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins OceancdVerificationTemplate#jenkins}
        '''
        result = self._values.get("jenkins")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderJenkins"], result)

    @builtins.property
    def job(self) -> typing.Optional["OceancdVerificationTemplateMetricsProviderJob"]:
        '''job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#job OceancdVerificationTemplate#job}
        '''
        result = self._values.get("job")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderJob"], result)

    @builtins.property
    def new_relic(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderNewRelic"]:
        '''new_relic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic OceancdVerificationTemplate#new_relic}
        '''
        result = self._values.get("new_relic")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderNewRelic"], result)

    @builtins.property
    def prometheus(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderPrometheus"]:
        '''prometheus block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus OceancdVerificationTemplate#prometheus}
        '''
        result = self._values.get("prometheus")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderPrometheus"], result)

    @builtins.property
    def web(self) -> typing.Optional["OceancdVerificationTemplateMetricsProviderWeb"]:
        '''web block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web OceancdVerificationTemplate#web}
        '''
        result = self._values.get("web")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderWeb"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatch",
    jsii_struct_bases=[],
    name_mapping={"metric_data_queries": "metricDataQueries", "duration": "duration"},
)
class OceancdVerificationTemplateMetricsProviderCloudWatch:
    def __init__(
        self,
        *,
        metric_data_queries: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries", typing.Dict[builtins.str, typing.Any]]]],
        duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_data_queries: metric_data_queries block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_data_queries OceancdVerificationTemplate#metric_data_queries}
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d68ba641f0fe9eac98315c628fdae941233f445aa1b43b60a91508724a4be4a6)
            check_type(argname="argument metric_data_queries", value=metric_data_queries, expected_type=type_hints["metric_data_queries"])
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_data_queries": metric_data_queries,
        }
        if duration is not None:
            self._values["duration"] = duration

    @builtins.property
    def metric_data_queries(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries"]]:
        '''metric_data_queries block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_data_queries OceancdVerificationTemplate#metric_data_queries}
        '''
        result = self._values.get("metric_data_queries")
        assert result is not None, "Required property 'metric_data_queries' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries"]], result)

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderCloudWatch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "expression": "expression",
        "label": "label",
        "metric_stat": "metricStat",
        "period": "period",
        "return_data": "returnData",
    },
)
class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries:
    def __init__(
        self,
        *,
        id: builtins.str,
        expression: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        metric_stat: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat", typing.Dict[builtins.str, typing.Any]]] = None,
        period: typing.Optional[jsii.Number] = None,
        return_data: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#id OceancdVerificationTemplate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param expression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#expression OceancdVerificationTemplate#expression}.
        :param label: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#label OceancdVerificationTemplate#label}.
        :param metric_stat: metric_stat block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_stat OceancdVerificationTemplate#metric_stat}
        :param period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#period OceancdVerificationTemplate#period}.
        :param return_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#return_data OceancdVerificationTemplate#return_data}.
        '''
        if isinstance(metric_stat, dict):
            metric_stat = OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat(**metric_stat)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f7e4ae014fb1b75c96919fe431fd2945ee2062115cc3594998c1ae10f0b8107)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument expression", value=expression, expected_type=type_hints["expression"])
            check_type(argname="argument label", value=label, expected_type=type_hints["label"])
            check_type(argname="argument metric_stat", value=metric_stat, expected_type=type_hints["metric_stat"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument return_data", value=return_data, expected_type=type_hints["return_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if expression is not None:
            self._values["expression"] = expression
        if label is not None:
            self._values["label"] = label
        if metric_stat is not None:
            self._values["metric_stat"] = metric_stat
        if period is not None:
            self._values["period"] = period
        if return_data is not None:
            self._values["return_data"] = return_data

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#id OceancdVerificationTemplate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def expression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#expression OceancdVerificationTemplate#expression}.'''
        result = self._values.get("expression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#label OceancdVerificationTemplate#label}.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_stat(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat"]:
        '''metric_stat block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_stat OceancdVerificationTemplate#metric_stat}
        '''
        result = self._values.get("metric_stat")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat"], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#period OceancdVerificationTemplate#period}.'''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def return_data(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#return_data OceancdVerificationTemplate#return_data}.'''
        result = self._values.get("return_data")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8ae39b4f7bc13f7ccd98514ad9a89a979632ba12f7b341ad24b7dd0ef2c941c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98d8be9eb2ad4fe5f7e9e13bae8ee64cfed67643788b1d71d5223a45ee5eb1cc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b527155660bbab0dbb7a2d015b2f8611cf906c2fae0f2c1e327f300af5f73d65)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5ec0e480c0075b6a4de1d10641373d4bab148efa378d43d99694206a678d495)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb11ec362cdb38db6bb13f4ed9845e91d0d1f917b25e6a7b02ae8660d3132a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d8144894bab70691f8481a928526e629ace217c6644df3f595f6400a216fe51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat",
    jsii_struct_bases=[],
    name_mapping={
        "metric": "metric",
        "metric_period": "metricPeriod",
        "stat": "stat",
        "unit": "unit",
    },
)
class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat:
    def __init__(
        self,
        *,
        metric: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric", typing.Dict[builtins.str, typing.Any]]] = None,
        metric_period: typing.Optional[jsii.Number] = None,
        stat: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric: metric block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric OceancdVerificationTemplate#metric}
        :param metric_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_period OceancdVerificationTemplate#metric_period}.
        :param stat: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#stat OceancdVerificationTemplate#stat}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#unit OceancdVerificationTemplate#unit}.
        '''
        if isinstance(metric, dict):
            metric = OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric(**metric)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73e26d500b1ea010a61b8859537844e9e0c304f7e4f906f9f52205b27b6ceb09)
            check_type(argname="argument metric", value=metric, expected_type=type_hints["metric"])
            check_type(argname="argument metric_period", value=metric_period, expected_type=type_hints["metric_period"])
            check_type(argname="argument stat", value=stat, expected_type=type_hints["stat"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if metric is not None:
            self._values["metric"] = metric
        if metric_period is not None:
            self._values["metric_period"] = metric_period
        if stat is not None:
            self._values["stat"] = stat
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def metric(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric"]:
        '''metric block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric OceancdVerificationTemplate#metric}
        '''
        result = self._values.get("metric")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric"], result)

    @builtins.property
    def metric_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_period OceancdVerificationTemplate#metric_period}.'''
        result = self._values.get("metric_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def stat(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#stat OceancdVerificationTemplate#stat}.'''
        result = self._values.get("stat")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#unit OceancdVerificationTemplate#unit}.'''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "dimensions": "dimensions",
        "namespace": "namespace",
    },
)
class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_name OceancdVerificationTemplate#metric_name}.
        :param dimensions: dimensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimensions OceancdVerificationTemplate#dimensions}
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#namespace OceancdVerificationTemplate#namespace}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b2071ff26767a6370615cf7f378075a7380a84b891a8a6781d87077d9c889b)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_name": metric_name,
        }
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_name OceancdVerificationTemplate#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimensions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions"]]]:
        '''dimensions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimensions OceancdVerificationTemplate#dimensions}
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions"]]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#namespace OceancdVerificationTemplate#namespace}.'''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions",
    jsii_struct_bases=[],
    name_mapping={
        "dimension_name": "dimensionName",
        "dimension_value": "dimensionValue",
    },
)
class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions:
    def __init__(
        self,
        *,
        dimension_name: builtins.str,
        dimension_value: builtins.str,
    ) -> None:
        '''
        :param dimension_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimension_name OceancdVerificationTemplate#dimension_name}.
        :param dimension_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimension_value OceancdVerificationTemplate#dimension_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48ee0a73729388ca6a73ac101e89babc6f956f24e9561fbcc57831b1d2c84fdb)
            check_type(argname="argument dimension_name", value=dimension_name, expected_type=type_hints["dimension_name"])
            check_type(argname="argument dimension_value", value=dimension_value, expected_type=type_hints["dimension_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dimension_name": dimension_name,
            "dimension_value": dimension_value,
        }

    @builtins.property
    def dimension_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimension_name OceancdVerificationTemplate#dimension_name}.'''
        result = self._values.get("dimension_name")
        assert result is not None, "Required property 'dimension_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimension_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimension_value OceancdVerificationTemplate#dimension_value}.'''
        result = self._values.get("dimension_value")
        assert result is not None, "Required property 'dimension_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__173581dfedbeabbdeb374b1425d2048583a7acbbee878ab5e15cdee1d427e685)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b79a8870acb48a8a327dd615228a92a3cad6ba4f60d4623d64bc1485e2c1c400)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8853bab7c3828adbbb965bad3b27a0320de9d02a360239e6a60d95c73520402d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__758af417f3e997fcae6ba41d23f734037159f33bd1e23a1cb9a5f616e165b888)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bff41e3687644da64ea9ca8fd4df5063405d0fcc1c9bf42beae564f0c0a6d895)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9e63fad30426bd9f18fd7772f1e7b5e862ca4eef2eb6a9a304d67a8c70cc7f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__010135167b3d903738f4b914862515528aeb8d6e9726f66e804b8eb33c9f6a1e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="dimensionNameInput")
    def dimension_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dimensionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionValueInput")
    def dimension_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dimensionValueInput"))

    @builtins.property
    @jsii.member(jsii_name="dimensionName")
    def dimension_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dimensionName"))

    @dimension_name.setter
    def dimension_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f88703840f4e339a8be92fe141a8dd2376f510f62c1599c21535baba2d74f3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimensionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dimensionValue")
    def dimension_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dimensionValue"))

    @dimension_value.setter
    def dimension_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa4b6ba1a6c1381b98b4de7cbb76e58534818749460cef5aab0fd890dc053d40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dimensionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e729c6d40ad58767057e775d5fe22bb37416d674f2f5f00350ec71550f3ee326)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95a436da873c4769865f0b0fbe61fe8bec34ff6f627514b9575ebc444254be12)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDimensions")
    def put_dimensions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ab0658bb9568d8ef5666b30e0b93ac7d10639750ace1b15e9b3bad0ab1da331)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDimensions", [value]))

    @jsii.member(jsii_name="resetDimensions")
    def reset_dimensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDimensions", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @builtins.property
    @jsii.member(jsii_name="dimensions")
    def dimensions(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsList:
        return typing.cast(OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsList, jsii.get(self, "dimensions"))

    @builtins.property
    @jsii.member(jsii_name="dimensionsInput")
    def dimensions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]], jsii.get(self, "dimensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__069e54c1e81901b117cb0c654a99ff79ac2ecdb706be7f8a1749bb3188819ff2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d2672baac08cc8a020c4a8742da44a469ac32c050fce4381d7687ab599064b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a56f3cf4d96b29851b4b21dc8e3db1f06d3848f03f69f4e9b3d0872e6360a30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8cbfd2fcc7d8778f0f7078b019c1eed6cd4c3835089f0209c976fb4bf1ddc1d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMetric")
    def put_metric(
        self,
        *,
        metric_name: builtins.str,
        dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_name OceancdVerificationTemplate#metric_name}.
        :param dimensions: dimensions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#dimensions OceancdVerificationTemplate#dimensions}
        :param namespace: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#namespace OceancdVerificationTemplate#namespace}.
        '''
        value = OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric(
            metric_name=metric_name, dimensions=dimensions, namespace=namespace
        )

        return typing.cast(None, jsii.invoke(self, "putMetric", [value]))

    @jsii.member(jsii_name="resetMetric")
    def reset_metric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetric", []))

    @jsii.member(jsii_name="resetMetricPeriod")
    def reset_metric_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricPeriod", []))

    @jsii.member(jsii_name="resetStat")
    def reset_stat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStat", []))

    @jsii.member(jsii_name="resetUnit")
    def reset_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnit", []))

    @builtins.property
    @jsii.member(jsii_name="metric")
    def metric(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricOutputReference, jsii.get(self, "metric"))

    @builtins.property
    @jsii.member(jsii_name="metricInput")
    def metric_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric], jsii.get(self, "metricInput"))

    @builtins.property
    @jsii.member(jsii_name="metricPeriodInput")
    def metric_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "metricPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="statInput")
    def stat_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statInput"))

    @builtins.property
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property
    @jsii.member(jsii_name="metricPeriod")
    def metric_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "metricPeriod"))

    @metric_period.setter
    def metric_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__829107bdd2271c694442c23bd3fea18ed57e976be639d8ebc7adc4ff732763ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stat")
    def stat(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stat"))

    @stat.setter
    def stat(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6a8f6d433dce024dc62d2d8f2851b245c4e2aa0eb417579688ea97dca32c225)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daffc83aa07db727b008037c1648b5be4a25e12a3de0310c1548dd547f1d846d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59ef5a56da54b1fd58bed2a1ec89b26858012dd26336a41e1c181de1c43cee6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f5cb9f91f88346ffe122ab0f080f07d7719c5ce95f254def3821f495b9994f20)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putMetricStat")
    def put_metric_stat(
        self,
        *,
        metric: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric, typing.Dict[builtins.str, typing.Any]]] = None,
        metric_period: typing.Optional[jsii.Number] = None,
        stat: typing.Optional[builtins.str] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric: metric block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric OceancdVerificationTemplate#metric}
        :param metric_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_period OceancdVerificationTemplate#metric_period}.
        :param stat: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#stat OceancdVerificationTemplate#stat}.
        :param unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#unit OceancdVerificationTemplate#unit}.
        '''
        value = OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat(
            metric=metric, metric_period=metric_period, stat=stat, unit=unit
        )

        return typing.cast(None, jsii.invoke(self, "putMetricStat", [value]))

    @jsii.member(jsii_name="resetExpression")
    def reset_expression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpression", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetMetricStat")
    def reset_metric_stat(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricStat", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetReturnData")
    def reset_return_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReturnData", []))

    @builtins.property
    @jsii.member(jsii_name="metricStat")
    def metric_stat(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatOutputReference, jsii.get(self, "metricStat"))

    @builtins.property
    @jsii.member(jsii_name="expressionInput")
    def expression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expressionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="labelInput")
    def label_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "labelInput"))

    @builtins.property
    @jsii.member(jsii_name="metricStatInput")
    def metric_stat_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat], jsii.get(self, "metricStatInput"))

    @builtins.property
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "periodInput"))

    @builtins.property
    @jsii.member(jsii_name="returnDataInput")
    def return_data_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "returnDataInput"))

    @builtins.property
    @jsii.member(jsii_name="expression")
    def expression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expression"))

    @expression.setter
    def expression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06e6171008f29ec06de92d797fdeef7411a56fb6ed75012dac2815b1f7f3ac30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__316abc64873edf4328d5dcec26f191183507ae0aff5ebd314b37ebf0ea0fb2f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @label.setter
    def label(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4efd21c3b52df79f5c68325e4c579fe7665b75e1b597b760f02bb218559ae384)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "label", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98ffc4af92d387a875b1f610446a13d7ecfaaeb6c83eb0b40d49bb9fd17de697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="returnData")
    def return_data(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "returnData"))

    @return_data.setter
    def return_data(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfbfdf4f9c58f3a285f0aab4ab445b21f740f2e7e6754f0bd3334675f2f24221)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca3b1e44925567d96b5e0c4e456068e815c55e17139faa67461c0aa4fcda2de2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderCloudWatchOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderCloudWatchOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61f7fc41b9976a3e0e88fe6bbfc0f667c785fa9778fad8e5c64874cfc5a0e7c0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putMetricDataQueries")
    def put_metric_data_queries(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a3a95a6e372f5e2246f104f778c6622e389a34c29d4693391e0472a1be76f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMetricDataQueries", [value]))

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @builtins.property
    @jsii.member(jsii_name="metricDataQueries")
    def metric_data_queries(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesList:
        return typing.cast(OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesList, jsii.get(self, "metricDataQueries"))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="metricDataQueriesInput")
    def metric_data_queries_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]], jsii.get(self, "metricDataQueriesInput"))

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fc599c35bcdbcc97a2da54ba9045ba6b3a2cb6789ac86ee070cff722edf942c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatch]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatch], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatch],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__743532dc96dfd97ef4191f4cea6290a5cf3b3ef77a17323a27dd88e92803197c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderDatadog",
    jsii_struct_bases=[],
    name_mapping={"datadog_query": "datadogQuery", "duration": "duration"},
)
class OceancdVerificationTemplateMetricsProviderDatadog:
    def __init__(
        self,
        *,
        datadog_query: typing.Optional[builtins.str] = None,
        duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datadog_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog_query OceancdVerificationTemplate#datadog_query}.
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2002de9ffe344f9718caf39b725c5f34beaf91f259270e0dd764f9a41a57118)
            check_type(argname="argument datadog_query", value=datadog_query, expected_type=type_hints["datadog_query"])
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if datadog_query is not None:
            self._values["datadog_query"] = datadog_query
        if duration is not None:
            self._values["duration"] = duration

    @builtins.property
    def datadog_query(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog_query OceancdVerificationTemplate#datadog_query}.'''
        result = self._values.get("datadog_query")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.'''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderDatadog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderDatadogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderDatadogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__62662c4782edfb6baeb34f8bfbb5ae5983b5e9d35dba434e227e16653e4abe6f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDatadogQuery")
    def reset_datadog_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatadogQuery", []))

    @jsii.member(jsii_name="resetDuration")
    def reset_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDuration", []))

    @builtins.property
    @jsii.member(jsii_name="datadogQueryInput")
    def datadog_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datadogQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="durationInput")
    def duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "durationInput"))

    @builtins.property
    @jsii.member(jsii_name="datadogQuery")
    def datadog_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datadogQuery"))

    @datadog_query.setter
    def datadog_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b31f717669dcb5f3edc305f462e1fda726b19544fe1703a7c5b0ffea4bbf378)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datadogQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7d2b6232923ab63529ac3dfc4b0cfcf9007ec265dc2466d55373c00db8bd63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderDatadog]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderDatadog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderDatadog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b878548d5f893f9531d62445adccb7945c8d65062e916ca03d1727e131087f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJenkins",
    jsii_struct_bases=[],
    name_mapping={
        "jenkins_interval": "jenkinsInterval",
        "pipeline_name": "pipelineName",
        "timeout": "timeout",
        "jenkins_parameters": "jenkinsParameters",
        "tls_verification": "tlsVerification",
    },
)
class OceancdVerificationTemplateMetricsProviderJenkins:
    def __init__(
        self,
        *,
        jenkins_interval: builtins.str,
        pipeline_name: builtins.str,
        timeout: builtins.str,
        jenkins_parameters: typing.Optional[typing.Union["OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters", typing.Dict[builtins.str, typing.Any]]] = None,
        tls_verification: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param jenkins_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins_interval OceancdVerificationTemplate#jenkins_interval}.
        :param pipeline_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#pipeline_name OceancdVerificationTemplate#pipeline_name}.
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#timeout OceancdVerificationTemplate#timeout}.
        :param jenkins_parameters: jenkins_parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins_parameters OceancdVerificationTemplate#jenkins_parameters}
        :param tls_verification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#tls_verification OceancdVerificationTemplate#tls_verification}.
        '''
        if isinstance(jenkins_parameters, dict):
            jenkins_parameters = OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters(**jenkins_parameters)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22527b8229c283d77542079d948411898d2b3cde06b2e4296d76595a8b97ee15)
            check_type(argname="argument jenkins_interval", value=jenkins_interval, expected_type=type_hints["jenkins_interval"])
            check_type(argname="argument pipeline_name", value=pipeline_name, expected_type=type_hints["pipeline_name"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument jenkins_parameters", value=jenkins_parameters, expected_type=type_hints["jenkins_parameters"])
            check_type(argname="argument tls_verification", value=tls_verification, expected_type=type_hints["tls_verification"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "jenkins_interval": jenkins_interval,
            "pipeline_name": pipeline_name,
            "timeout": timeout,
        }
        if jenkins_parameters is not None:
            self._values["jenkins_parameters"] = jenkins_parameters
        if tls_verification is not None:
            self._values["tls_verification"] = tls_verification

    @builtins.property
    def jenkins_interval(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins_interval OceancdVerificationTemplate#jenkins_interval}.'''
        result = self._values.get("jenkins_interval")
        assert result is not None, "Required property 'jenkins_interval' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipeline_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#pipeline_name OceancdVerificationTemplate#pipeline_name}.'''
        result = self._values.get("pipeline_name")
        assert result is not None, "Required property 'pipeline_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#timeout OceancdVerificationTemplate#timeout}.'''
        result = self._values.get("timeout")
        assert result is not None, "Required property 'timeout' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def jenkins_parameters(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters"]:
        '''jenkins_parameters block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins_parameters OceancdVerificationTemplate#jenkins_parameters}
        '''
        result = self._values.get("jenkins_parameters")
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters"], result)

    @builtins.property
    def tls_verification(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#tls_verification OceancdVerificationTemplate#tls_verification}.'''
        result = self._values.get("tls_verification")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJenkins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_key": "parameterKey",
        "parameter_value": "parameterValue",
    },
)
class OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters:
    def __init__(
        self,
        *,
        parameter_key: builtins.str,
        parameter_value: builtins.str,
    ) -> None:
        '''
        :param parameter_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#parameter_key OceancdVerificationTemplate#parameter_key}.
        :param parameter_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#parameter_value OceancdVerificationTemplate#parameter_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c33fdfb6b4cb9c9fd31f72dd6bc55c83bf0421d2abc7d113834a32f51401c2)
            check_type(argname="argument parameter_key", value=parameter_key, expected_type=type_hints["parameter_key"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "parameter_key": parameter_key,
            "parameter_value": parameter_value,
        }

    @builtins.property
    def parameter_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#parameter_key OceancdVerificationTemplate#parameter_key}.'''
        result = self._values.get("parameter_key")
        assert result is not None, "Required property 'parameter_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#parameter_value OceancdVerificationTemplate#parameter_value}.'''
        result = self._values.get("parameter_value")
        assert result is not None, "Required property 'parameter_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParametersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParametersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cc3e7bba05ee4783cb4cb0e844f40eaad5582f00ddc74e003c45956176dc43d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="parameterKeyInput")
    def parameter_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterValueInput")
    def parameter_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterValueInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterKey")
    def parameter_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterKey"))

    @parameter_key.setter
    def parameter_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f51920f13a35d6afb6ceff22119313ab6131b8af9e2289789d2a7b2c798865c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterValue")
    def parameter_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterValue"))

    @parameter_value.setter
    def parameter_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c1381ba408c5e78493a0ad14b32c87fa10ae7aac2f13e39fc1ca02a3c686300)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aab9b1f11f68fcc1928271394123a8c2cfc5163f9bc2672605929c3f00bfdbef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJenkinsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJenkinsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__214b5dec3e8cc16b6f4d9a47b47feec4a16d7e799b9cc92e2e24da60ffccacc3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putJenkinsParameters")
    def put_jenkins_parameters(
        self,
        *,
        parameter_key: builtins.str,
        parameter_value: builtins.str,
    ) -> None:
        '''
        :param parameter_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#parameter_key OceancdVerificationTemplate#parameter_key}.
        :param parameter_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#parameter_value OceancdVerificationTemplate#parameter_value}.
        '''
        value = OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters(
            parameter_key=parameter_key, parameter_value=parameter_value
        )

        return typing.cast(None, jsii.invoke(self, "putJenkinsParameters", [value]))

    @jsii.member(jsii_name="resetJenkinsParameters")
    def reset_jenkins_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJenkinsParameters", []))

    @jsii.member(jsii_name="resetTlsVerification")
    def reset_tls_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsVerification", []))

    @builtins.property
    @jsii.member(jsii_name="jenkinsParameters")
    def jenkins_parameters(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParametersOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParametersOutputReference, jsii.get(self, "jenkinsParameters"))

    @builtins.property
    @jsii.member(jsii_name="jenkinsIntervalInput")
    def jenkins_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jenkinsIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="jenkinsParametersInput")
    def jenkins_parameters_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters], jsii.get(self, "jenkinsParametersInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineNameInput")
    def pipeline_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineNameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsVerificationInput")
    def tls_verification_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsVerificationInput"))

    @builtins.property
    @jsii.member(jsii_name="jenkinsInterval")
    def jenkins_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jenkinsInterval"))

    @jenkins_interval.setter
    def jenkins_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c1440f5a34d8e704ec85f7f6a42bf19d0dcbf5f11b410a9168f71b2698fee37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jenkinsInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipelineName"))

    @pipeline_name.setter
    def pipeline_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13c90f2439e65c7a9ebd92084e8c3592d460f1d29643a68d0d5fb7193db3714)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipelineName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d6c28318126e00c6ce336c3558b0ac0b3c544f18f0a7ba7ef6c92a69c74bc04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsVerification")
    def tls_verification(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tlsVerification"))

    @tls_verification.setter
    def tls_verification(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f4f0ace644bb61aaa7ce8a1605ba22f01e86cd250be392c67e6bae2d4bcd639)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsVerification", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderJenkins]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderJenkins], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderJenkins],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b2d9cb6f77b4451ee8b15275b013709c996a22e5878b8b5b93a673efdf3a14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJob",
    jsii_struct_bases=[],
    name_mapping={"spec": "spec"},
)
class OceancdVerificationTemplateMetricsProviderJob:
    def __init__(
        self,
        *,
        spec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderJobSpec", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#spec OceancdVerificationTemplate#spec}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__024dcc65d49d9aedc20c38f6c1f545412ce337fb4852cd914a9e282222c9ae6d)
            check_type(argname="argument spec", value=spec, expected_type=type_hints["spec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "spec": spec,
        }

    @builtins.property
    def spec(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpec"]]:
        '''spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#spec OceancdVerificationTemplate#spec}
        '''
        result = self._values.get("spec")
        assert result is not None, "Required property 'spec' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpec"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ba94398937549a43ea26a3e91aa26a01c35b75938e93d4745ae05937f20e864)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putSpec")
    def put_spec(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderJobSpec", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cc806c4156582abbec248f55b76e181b4b9cb2ff3af046baaeb05552ab540f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSpec", [value]))

    @builtins.property
    @jsii.member(jsii_name="spec")
    def spec(self) -> "OceancdVerificationTemplateMetricsProviderJobSpecList":
        return typing.cast("OceancdVerificationTemplateMetricsProviderJobSpecList", jsii.get(self, "spec"))

    @builtins.property
    @jsii.member(jsii_name="specInput")
    def spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpec"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpec"]]], jsii.get(self, "specInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderJob]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderJob], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderJob],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__252d39db417bfc85595d2b804fbb1eafef005f78f1b23389a69b7bcfa560bafa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpec",
    jsii_struct_bases=[],
    name_mapping={"job_template": "jobTemplate", "backoff_limit": "backoffLimit"},
)
class OceancdVerificationTemplateMetricsProviderJobSpec:
    def __init__(
        self,
        *,
        job_template: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate", typing.Dict[builtins.str, typing.Any]]]],
        backoff_limit: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param job_template: job_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#job_template OceancdVerificationTemplate#job_template}
        :param backoff_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#backoff_limit OceancdVerificationTemplate#backoff_limit}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aea98e2d74eada400bc756a8331912403fc446c68244aa86a7bf3cd9d2231d53)
            check_type(argname="argument job_template", value=job_template, expected_type=type_hints["job_template"])
            check_type(argname="argument backoff_limit", value=backoff_limit, expected_type=type_hints["backoff_limit"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "job_template": job_template,
        }
        if backoff_limit is not None:
            self._values["backoff_limit"] = backoff_limit

    @builtins.property
    def job_template(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate"]]:
        '''job_template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#job_template OceancdVerificationTemplate#job_template}
        '''
        result = self._values.get("job_template")
        assert result is not None, "Required property 'job_template' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate"]], result)

    @builtins.property
    def backoff_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#backoff_limit OceancdVerificationTemplate#backoff_limit}.'''
        result = self._values.get("backoff_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJobSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate",
    jsii_struct_bases=[],
    name_mapping={"template_spec": "templateSpec"},
)
class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate:
    def __init__(
        self,
        *,
        template_spec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param template_spec: template_spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#template_spec OceancdVerificationTemplate#template_spec}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cad3834432a413920433f220a14cd57ef873fd27d2487c3f65901bf1a1d067a6)
            check_type(argname="argument template_spec", value=template_spec, expected_type=type_hints["template_spec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "template_spec": template_spec,
        }

    @builtins.property
    def template_spec(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec"]]:
        '''template_spec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#template_spec OceancdVerificationTemplate#template_spec}
        '''
        result = self._values.get("template_spec")
        assert result is not None, "Required property 'template_spec' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a4569197b8a93ee77d8619b35c20d6f681853604b83f6e50301f8a23a578122f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35abc0e00ca94073a3060396eadcfd14d5de3dc3f3bb0178fbc4399ac7c0bb10)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d8a19d407f53fd69a44911e1fc47b4604aa70f04bcf0634c19de0a9cd5cdcb1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__25d1c96346d86ec0b9927b47c3d001bba545e174d74b2a6ef8f6d81c6f308b8c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae1fb25c121ee5c0f326e4e4bfe79c69806a145f615763866d13d1c744a60712)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aef66836396cd51146b6926d01bf458d84885834e411ea17426462669a8c470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e63a9ce0883e3dee27f38ae7ef6519e4f182482de525cd44362a222480792851)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTemplateSpec")
    def put_template_spec(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ad0987dfe6e74eb827c0ca6adeeeec5abf514f79cf9a7a1280bed001574f46c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTemplateSpec", [value]))

    @builtins.property
    @jsii.member(jsii_name="templateSpec")
    def template_spec(
        self,
    ) -> "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecList":
        return typing.cast("OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecList", jsii.get(self, "templateSpec"))

    @builtins.property
    @jsii.member(jsii_name="templateSpecInput")
    def template_spec_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec"]]], jsii.get(self, "templateSpecInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__965c425ebe66202b4c4b392cda510659f1b5f6ed911d7ed827e8d3950e9d55c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec",
    jsii_struct_bases=[],
    name_mapping={"containers": "containers", "restart_policy": "restartPolicy"},
)
class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec:
    def __init__(
        self,
        *,
        containers: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers", typing.Dict[builtins.str, typing.Any]]]],
        restart_policy: builtins.str,
    ) -> None:
        '''
        :param containers: containers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#containers OceancdVerificationTemplate#containers}
        :param restart_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#restart_policy OceancdVerificationTemplate#restart_policy}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__037b9d80869b76df66d27df0cae370795d3deb9da9282c70a128b20d92c86aaf)
            check_type(argname="argument containers", value=containers, expected_type=type_hints["containers"])
            check_type(argname="argument restart_policy", value=restart_policy, expected_type=type_hints["restart_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "containers": containers,
            "restart_policy": restart_policy,
        }

    @builtins.property
    def containers(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers"]]:
        '''containers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#containers OceancdVerificationTemplate#containers}
        '''
        result = self._values.get("containers")
        assert result is not None, "Required property 'containers' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers"]], result)

    @builtins.property
    def restart_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#restart_policy OceancdVerificationTemplate#restart_policy}.'''
        result = self._values.get("restart_policy")
        assert result is not None, "Required property 'restart_policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "container_name": "containerName",
        "image": "image",
    },
)
class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers:
    def __init__(
        self,
        *,
        command: typing.Sequence[builtins.str],
        container_name: builtins.str,
        image: builtins.str,
    ) -> None:
        '''
        :param command: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#command OceancdVerificationTemplate#command}.
        :param container_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#container_name OceancdVerificationTemplate#container_name}.
        :param image: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#image OceancdVerificationTemplate#image}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dceff0345ee96145c0cabd8086706bd9c233d051050436b8cab1e7aadf89782)
            check_type(argname="argument command", value=command, expected_type=type_hints["command"])
            check_type(argname="argument container_name", value=container_name, expected_type=type_hints["container_name"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "command": command,
            "container_name": container_name,
            "image": image,
        }

    @builtins.property
    def command(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#command OceancdVerificationTemplate#command}.'''
        result = self._values.get("command")
        assert result is not None, "Required property 'command' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def container_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#container_name OceancdVerificationTemplate#container_name}.'''
        result = self._values.get("container_name")
        assert result is not None, "Required property 'container_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#image OceancdVerificationTemplate#image}.'''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__56eac0db77865be51b1e1a932d21239934bb807c635efecec9a78d4b21688966)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d215737581f42ace58548a5db932d1518aabcbc770a2c66864543faaff20f59)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__265b9de71c6ef4bf9fd1f214fb9940a33f2388453341dd784f189325d60bcb43)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d38715c5b4ade39931f9de17ec69a4ee3706f849a300ae74f13e830bd493266)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7486c1960e8f93cac555aa829b529ca13c33a21842e76b36a9abc91ab7e6edd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a49b9d55733dfc0aa05658340665926d559247279eecf947124e21f7b0b0c92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d98d6dfff1bbbb45aaeec8718727553a90e0dcc6b95f3a3039aef2d159d13727)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="commandInput")
    def command_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "commandInput"))

    @builtins.property
    @jsii.member(jsii_name="containerNameInput")
    def container_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf25120a0ee51400d3556e39ecb39b3e5a6811466632f88e45cde922ab2a43a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "command", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38bd46a51170ea2feb2ebc9ee0c664ddd361d7c0a36c333fe781dc39649b2ee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd100476a430bd549064a08259693a018ac42393716bdda8bcd2ddc1e7b70ebd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "image", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a718ce8f27d7f00865c50613ae428b404523abae7043a46d1618bb5b366b7d39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe949b77845c5323c167d5595c9685df06f47ffc1276bf4ba55a34afed257123)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32418baaa0589b5f4f1a24a0e10d24a3e46d5b5d26a373bc6cbd001f92fd89ad)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b008af2251519c54b6ac342d5fb537c0bf440257ea5ba23868d78f8260615f7d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__430ddf60bfe64fdbdb625aeb48152037aee3d0efb8e746d53eb6d55e985071c7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e528ae30554268edf5f21e9797312667ee11b6f38c3988f1fffbccff33813c08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c66876ac7fa9e54e995f9439d19bfefe09227a9e27ae68d6265ce1b552433a0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8df4e68db4a0b770340450fea11c713ab4620b30f8e0adabc36c50873d799d1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putContainers")
    def put_containers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39637cc8282ba87f1d0ab1da83f77f9db04c758aa7d7234bb8039396e07ef952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putContainers", [value]))

    @builtins.property
    @jsii.member(jsii_name="containers")
    def containers(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersList:
        return typing.cast(OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersList, jsii.get(self, "containers"))

    @builtins.property
    @jsii.member(jsii_name="containersInput")
    def containers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]], jsii.get(self, "containersInput"))

    @builtins.property
    @jsii.member(jsii_name="restartPolicyInput")
    def restart_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restartPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restartPolicy"))

    @restart_policy.setter
    def restart_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e93c58554ff664d28fe25135a76eaa59f3a64b540bd3a8036260eabb75d43f09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restartPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e488df4652eeee37340eaa4ff3682fb801f6df0be106b07f23042cebaebacda2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJobSpecList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f393c353cab03cf57bbf5c5283cc837b7facdba472aa34ba9e79c297a92434c2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderJobSpecOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de3e1bdeab5e053a652fc0160bf0f12a6c161d57f95b0aada48be1c1793118b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderJobSpecOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e012ecb4ad5ae117084bb2a6af1a463362bc1f4d20ff5b6736f2b88d41495ca8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__26c812766371d6eb3424648a8325e5f41006f5f740d7bdddade27284672ec511)
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
            type_hints = typing.get_type_hints(_typecheckingstub__51fe312e40fb4eeb47d0b240999d6fc7ccf2e558fd10f03a644ba8c2233135ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpec]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpec]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpec]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4d1943a367d438de0cb92f0049d0b1429aba126fbefa8760248d0bb6b61cd1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderJobSpecOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderJobSpecOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e8c095b54243e60ea3632e9379fc18f47169c683b20e2d600eb0784591a262b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putJobTemplate")
    def put_job_template(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf8aee579a8c595ea8b8a858384b5fefa36b92d40de9c695aadcea3b5397c33e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putJobTemplate", [value]))

    @jsii.member(jsii_name="resetBackoffLimit")
    def reset_backoff_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackoffLimit", []))

    @builtins.property
    @jsii.member(jsii_name="jobTemplate")
    def job_template(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateList:
        return typing.cast(OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateList, jsii.get(self, "jobTemplate"))

    @builtins.property
    @jsii.member(jsii_name="backoffLimitInput")
    def backoff_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backoffLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="jobTemplateInput")
    def job_template_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]], jsii.get(self, "jobTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="backoffLimit")
    def backoff_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backoffLimit"))

    @backoff_limit.setter
    def backoff_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2e1aeb9777d7d292f31a8649979f0623cfe23ea8c3c219556dec65cd348e63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backoffLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpec]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpec]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpec]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9cad6cd7353084eb670bff7bfb5905a4580784833a4becd027a5241a726a8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71f6e935233b30924368e0d2efa6bf3562b536d423a5da20d50b76864f40cce7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84fc69e50efb199751ef261f6ab7d571b675ca4b55e0fe481d77a267130490e4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__925ebe777dc080f4ca7f8cf293f1b5746b51620b7a0c85a557c80806e4ab1c3a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31337c968582e2d182bef41c0bb918e80aa56f2091ae6a23a2d77f727338922a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__84f328807f031ea29639c3d57d570ec629d5117a9ac697d3988b4d9986eb2f45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProvider]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProvider]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProvider]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b6dc7b0a704f6cf0d56d58e6b61c4e7b174ec828dc9c54197bf37751f7f9b29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderNewRelic",
    jsii_struct_bases=[],
    name_mapping={"new_relic_query": "newRelicQuery", "profile": "profile"},
)
class OceancdVerificationTemplateMetricsProviderNewRelic:
    def __init__(
        self,
        *,
        new_relic_query: builtins.str,
        profile: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param new_relic_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic_query OceancdVerificationTemplate#new_relic_query}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#profile OceancdVerificationTemplate#profile}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__153a3eb557debbf37dc0d0674006c2d984daaf9f773e0370278f6183f0e28055)
            check_type(argname="argument new_relic_query", value=new_relic_query, expected_type=type_hints["new_relic_query"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "new_relic_query": new_relic_query,
        }
        if profile is not None:
            self._values["profile"] = profile

    @builtins.property
    def new_relic_query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic_query OceancdVerificationTemplate#new_relic_query}.'''
        result = self._values.get("new_relic_query")
        assert result is not None, "Required property 'new_relic_query' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#profile OceancdVerificationTemplate#profile}.'''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderNewRelic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderNewRelicOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderNewRelicOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb94d4d8ffc63c111447b7f2a9cd6892319d1f1537a08b3de73cde9829e3a099)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @builtins.property
    @jsii.member(jsii_name="newRelicQueryInput")
    def new_relic_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "newRelicQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="newRelicQuery")
    def new_relic_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "newRelicQuery"))

    @new_relic_query.setter
    def new_relic_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e65f736cda572954948907264620e0fe0dc668bb57152b48c8da70d1857e9d8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "newRelicQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a909d0dd34c21e6d626210dadf184e6bd04e80a6e6a26b4d2711f95fecf1fabb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderNewRelic]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderNewRelic], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderNewRelic],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__405e34961448f9ae29f067aa15e0c3bbd56be498e08b9e463213c774ffa2f5e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f1ee2d1c6ab2dcbe22fe1d2f2232eac7e869a0d30f6d4e56a383e8f7e3561ee7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCloudWatch")
    def put_cloud_watch(
        self,
        *,
        metric_data_queries: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries, typing.Dict[builtins.str, typing.Any]]]],
        duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_data_queries: metric_data_queries block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#metric_data_queries OceancdVerificationTemplate#metric_data_queries}
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.
        '''
        value = OceancdVerificationTemplateMetricsProviderCloudWatch(
            metric_data_queries=metric_data_queries, duration=duration
        )

        return typing.cast(None, jsii.invoke(self, "putCloudWatch", [value]))

    @jsii.member(jsii_name="putDatadog")
    def put_datadog(
        self,
        *,
        datadog_query: typing.Optional[builtins.str] = None,
        duration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param datadog_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#datadog_query OceancdVerificationTemplate#datadog_query}.
        :param duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#duration OceancdVerificationTemplate#duration}.
        '''
        value = OceancdVerificationTemplateMetricsProviderDatadog(
            datadog_query=datadog_query, duration=duration
        )

        return typing.cast(None, jsii.invoke(self, "putDatadog", [value]))

    @jsii.member(jsii_name="putJenkins")
    def put_jenkins(
        self,
        *,
        jenkins_interval: builtins.str,
        pipeline_name: builtins.str,
        timeout: builtins.str,
        jenkins_parameters: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters, typing.Dict[builtins.str, typing.Any]]] = None,
        tls_verification: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param jenkins_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins_interval OceancdVerificationTemplate#jenkins_interval}.
        :param pipeline_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#pipeline_name OceancdVerificationTemplate#pipeline_name}.
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#timeout OceancdVerificationTemplate#timeout}.
        :param jenkins_parameters: jenkins_parameters block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#jenkins_parameters OceancdVerificationTemplate#jenkins_parameters}
        :param tls_verification: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#tls_verification OceancdVerificationTemplate#tls_verification}.
        '''
        value = OceancdVerificationTemplateMetricsProviderJenkins(
            jenkins_interval=jenkins_interval,
            pipeline_name=pipeline_name,
            timeout=timeout,
            jenkins_parameters=jenkins_parameters,
            tls_verification=tls_verification,
        )

        return typing.cast(None, jsii.invoke(self, "putJenkins", [value]))

    @jsii.member(jsii_name="putJob")
    def put_job(
        self,
        *,
        spec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpec, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param spec: spec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#spec OceancdVerificationTemplate#spec}
        '''
        value = OceancdVerificationTemplateMetricsProviderJob(spec=spec)

        return typing.cast(None, jsii.invoke(self, "putJob", [value]))

    @jsii.member(jsii_name="putNewRelic")
    def put_new_relic(
        self,
        *,
        new_relic_query: builtins.str,
        profile: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param new_relic_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#new_relic_query OceancdVerificationTemplate#new_relic_query}.
        :param profile: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#profile OceancdVerificationTemplate#profile}.
        '''
        value = OceancdVerificationTemplateMetricsProviderNewRelic(
            new_relic_query=new_relic_query, profile=profile
        )

        return typing.cast(None, jsii.invoke(self, "putNewRelic", [value]))

    @jsii.member(jsii_name="putPrometheus")
    def put_prometheus(self, *, prometheus_query: builtins.str) -> None:
        '''
        :param prometheus_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus_query OceancdVerificationTemplate#prometheus_query}.
        '''
        value = OceancdVerificationTemplateMetricsProviderPrometheus(
            prometheus_query=prometheus_query
        )

        return typing.cast(None, jsii.invoke(self, "putPrometheus", [value]))

    @jsii.member(jsii_name="putWeb")
    def put_web(
        self,
        *,
        url: builtins.str,
        body: typing.Optional[builtins.str] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        json_path: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
        web_header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderWebWebHeader", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#url OceancdVerificationTemplate#url}.
        :param body: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#body OceancdVerificationTemplate#body}.
        :param insecure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#insecure OceancdVerificationTemplate#insecure}.
        :param json_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#json_path OceancdVerificationTemplate#json_path}.
        :param method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#method OceancdVerificationTemplate#method}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#timeout_seconds OceancdVerificationTemplate#timeout_seconds}.
        :param web_header: web_header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header OceancdVerificationTemplate#web_header}
        '''
        value = OceancdVerificationTemplateMetricsProviderWeb(
            url=url,
            body=body,
            insecure=insecure,
            json_path=json_path,
            method=method,
            timeout_seconds=timeout_seconds,
            web_header=web_header,
        )

        return typing.cast(None, jsii.invoke(self, "putWeb", [value]))

    @jsii.member(jsii_name="resetCloudWatch")
    def reset_cloud_watch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudWatch", []))

    @jsii.member(jsii_name="resetDatadog")
    def reset_datadog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatadog", []))

    @jsii.member(jsii_name="resetJenkins")
    def reset_jenkins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJenkins", []))

    @jsii.member(jsii_name="resetJob")
    def reset_job(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJob", []))

    @jsii.member(jsii_name="resetNewRelic")
    def reset_new_relic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewRelic", []))

    @jsii.member(jsii_name="resetPrometheus")
    def reset_prometheus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrometheus", []))

    @jsii.member(jsii_name="resetWeb")
    def reset_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWeb", []))

    @builtins.property
    @jsii.member(jsii_name="cloudWatch")
    def cloud_watch(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderCloudWatchOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderCloudWatchOutputReference, jsii.get(self, "cloudWatch"))

    @builtins.property
    @jsii.member(jsii_name="datadog")
    def datadog(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderDatadogOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderDatadogOutputReference, jsii.get(self, "datadog"))

    @builtins.property
    @jsii.member(jsii_name="jenkins")
    def jenkins(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderJenkinsOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderJenkinsOutputReference, jsii.get(self, "jenkins"))

    @builtins.property
    @jsii.member(jsii_name="job")
    def job(self) -> OceancdVerificationTemplateMetricsProviderJobOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderJobOutputReference, jsii.get(self, "job"))

    @builtins.property
    @jsii.member(jsii_name="newRelic")
    def new_relic(
        self,
    ) -> OceancdVerificationTemplateMetricsProviderNewRelicOutputReference:
        return typing.cast(OceancdVerificationTemplateMetricsProviderNewRelicOutputReference, jsii.get(self, "newRelic"))

    @builtins.property
    @jsii.member(jsii_name="prometheus")
    def prometheus(
        self,
    ) -> "OceancdVerificationTemplateMetricsProviderPrometheusOutputReference":
        return typing.cast("OceancdVerificationTemplateMetricsProviderPrometheusOutputReference", jsii.get(self, "prometheus"))

    @builtins.property
    @jsii.member(jsii_name="web")
    def web(self) -> "OceancdVerificationTemplateMetricsProviderWebOutputReference":
        return typing.cast("OceancdVerificationTemplateMetricsProviderWebOutputReference", jsii.get(self, "web"))

    @builtins.property
    @jsii.member(jsii_name="cloudWatchInput")
    def cloud_watch_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatch]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatch], jsii.get(self, "cloudWatchInput"))

    @builtins.property
    @jsii.member(jsii_name="datadogInput")
    def datadog_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderDatadog]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderDatadog], jsii.get(self, "datadogInput"))

    @builtins.property
    @jsii.member(jsii_name="jenkinsInput")
    def jenkins_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderJenkins]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderJenkins], jsii.get(self, "jenkinsInput"))

    @builtins.property
    @jsii.member(jsii_name="jobInput")
    def job_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderJob]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderJob], jsii.get(self, "jobInput"))

    @builtins.property
    @jsii.member(jsii_name="newRelicInput")
    def new_relic_input(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderNewRelic]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderNewRelic], jsii.get(self, "newRelicInput"))

    @builtins.property
    @jsii.member(jsii_name="prometheusInput")
    def prometheus_input(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderPrometheus"]:
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderPrometheus"], jsii.get(self, "prometheusInput"))

    @builtins.property
    @jsii.member(jsii_name="webInput")
    def web_input(
        self,
    ) -> typing.Optional["OceancdVerificationTemplateMetricsProviderWeb"]:
        return typing.cast(typing.Optional["OceancdVerificationTemplateMetricsProviderWeb"], jsii.get(self, "webInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProvider]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProvider]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProvider]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d63048f2958b195c872286b9c29fa822a5461b308c7ca164cfaa4e7c8c06708)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderPrometheus",
    jsii_struct_bases=[],
    name_mapping={"prometheus_query": "prometheusQuery"},
)
class OceancdVerificationTemplateMetricsProviderPrometheus:
    def __init__(self, *, prometheus_query: builtins.str) -> None:
        '''
        :param prometheus_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus_query OceancdVerificationTemplate#prometheus_query}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21445fdabfba233c339df7b497f487605e9d6d5f07810b2b5274145599dee1da)
            check_type(argname="argument prometheus_query", value=prometheus_query, expected_type=type_hints["prometheus_query"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "prometheus_query": prometheus_query,
        }

    @builtins.property
    def prometheus_query(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#prometheus_query OceancdVerificationTemplate#prometheus_query}.'''
        result = self._values.get("prometheus_query")
        assert result is not None, "Required property 'prometheus_query' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderPrometheus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderPrometheusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderPrometheusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__51cde5cf5a68dc4adaccc90ac30d9b45885578aa146dc1095dd54ef77804b2ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="prometheusQueryInput")
    def prometheus_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prometheusQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="prometheusQuery")
    def prometheus_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prometheusQuery"))

    @prometheus_query.setter
    def prometheus_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cccc2cd82b037cf5a730b4b9039ebfad4ef09dbe3fb5fdeb3242e6f129f46bf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prometheusQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderPrometheus]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderPrometheus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderPrometheus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a2b06cf1debe1c2e828015bd2ae7c663ffb013178639e660d57984698405b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderWeb",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "body": "body",
        "insecure": "insecure",
        "json_path": "jsonPath",
        "method": "method",
        "timeout_seconds": "timeoutSeconds",
        "web_header": "webHeader",
    },
)
class OceancdVerificationTemplateMetricsProviderWeb:
    def __init__(
        self,
        *,
        url: builtins.str,
        body: typing.Optional[builtins.str] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        json_path: typing.Optional[builtins.str] = None,
        method: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
        web_header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderWebWebHeader", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#url OceancdVerificationTemplate#url}.
        :param body: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#body OceancdVerificationTemplate#body}.
        :param insecure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#insecure OceancdVerificationTemplate#insecure}.
        :param json_path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#json_path OceancdVerificationTemplate#json_path}.
        :param method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#method OceancdVerificationTemplate#method}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#timeout_seconds OceancdVerificationTemplate#timeout_seconds}.
        :param web_header: web_header block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header OceancdVerificationTemplate#web_header}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8331eba10c417449ba896a3d09bfefb0413988008590b2fd336c09d9ca50afae)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
            check_type(argname="argument insecure", value=insecure, expected_type=type_hints["insecure"])
            check_type(argname="argument json_path", value=json_path, expected_type=type_hints["json_path"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument timeout_seconds", value=timeout_seconds, expected_type=type_hints["timeout_seconds"])
            check_type(argname="argument web_header", value=web_header, expected_type=type_hints["web_header"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
        }
        if body is not None:
            self._values["body"] = body
        if insecure is not None:
            self._values["insecure"] = insecure
        if json_path is not None:
            self._values["json_path"] = json_path
        if method is not None:
            self._values["method"] = method
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds
        if web_header is not None:
            self._values["web_header"] = web_header

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#url OceancdVerificationTemplate#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def body(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#body OceancdVerificationTemplate#body}.'''
        result = self._values.get("body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#insecure OceancdVerificationTemplate#insecure}.'''
        result = self._values.get("insecure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def json_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#json_path OceancdVerificationTemplate#json_path}.'''
        result = self._values.get("json_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#method OceancdVerificationTemplate#method}.'''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#timeout_seconds OceancdVerificationTemplate#timeout_seconds}.'''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def web_header(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderWebWebHeader"]]]:
        '''web_header block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header OceancdVerificationTemplate#web_header}
        '''
        result = self._values.get("web_header")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderWebWebHeader"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderWeb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderWebOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderWebOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a26f67b943f162892fe2c27f9817509e616ff4e67faf4d631c1dd4a537e1fd8a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putWebHeader")
    def put_web_header(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OceancdVerificationTemplateMetricsProviderWebWebHeader", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dff1da99bf10e9facd239a7577e4fa1ef89b53296da64146b7f580a1a2d5f66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWebHeader", [value]))

    @jsii.member(jsii_name="resetBody")
    def reset_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBody", []))

    @jsii.member(jsii_name="resetInsecure")
    def reset_insecure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecure", []))

    @jsii.member(jsii_name="resetJsonPath")
    def reset_json_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJsonPath", []))

    @jsii.member(jsii_name="resetMethod")
    def reset_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethod", []))

    @jsii.member(jsii_name="resetTimeoutSeconds")
    def reset_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutSeconds", []))

    @jsii.member(jsii_name="resetWebHeader")
    def reset_web_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebHeader", []))

    @builtins.property
    @jsii.member(jsii_name="webHeader")
    def web_header(
        self,
    ) -> "OceancdVerificationTemplateMetricsProviderWebWebHeaderList":
        return typing.cast("OceancdVerificationTemplateMetricsProviderWebWebHeaderList", jsii.get(self, "webHeader"))

    @builtins.property
    @jsii.member(jsii_name="bodyInput")
    def body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bodyInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureInput")
    def insecure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureInput"))

    @builtins.property
    @jsii.member(jsii_name="jsonPathInput")
    def json_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jsonPathInput"))

    @builtins.property
    @jsii.member(jsii_name="methodInput")
    def method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "methodInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutSecondsInput")
    def timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="webHeaderInput")
    def web_header_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderWebWebHeader"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OceancdVerificationTemplateMetricsProviderWebWebHeader"]]], jsii.get(self, "webHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @body.setter
    def body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e0655fd515db9a651484098f9b43a33093e4b3395c1a3efbea88ca4a16bc732)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "body", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecure")
    def insecure(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecure"))

    @insecure.setter
    def insecure(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4071a35b0c024d0c7c96e15e91fb4ce361a8ed111697dad11c3de2b09f948c42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jsonPath")
    def json_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jsonPath"))

    @json_path.setter
    def json_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df59116610223fd137003d10ea384743b2b420eb59a28be5487c202ccaaef04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jsonPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__031f06a6c4ccf93b1124a5fd37b1e98f0fcc570c669c501a17cfb7f30cf325de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeoutSeconds")
    def timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSeconds"))

    @timeout_seconds.setter
    def timeout_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f05fda890b03b096c90332cdf1a7a5eeb8487787ae9d3e584348d145d9d8e50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dc6f22b74f99809eb4ea74fd9951be1c7069b478ccf77ce953c8dc8b4886437)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[OceancdVerificationTemplateMetricsProviderWeb]:
        return typing.cast(typing.Optional[OceancdVerificationTemplateMetricsProviderWeb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationTemplateMetricsProviderWeb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df8faae4034a3cef318958a44cc4d2164fa8efcaf4b1a83fef6f19cc015b47f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderWebWebHeader",
    jsii_struct_bases=[],
    name_mapping={
        "web_header_key": "webHeaderKey",
        "web_header_value": "webHeaderValue",
    },
)
class OceancdVerificationTemplateMetricsProviderWebWebHeader:
    def __init__(
        self,
        *,
        web_header_key: builtins.str,
        web_header_value: builtins.str,
    ) -> None:
        '''
        :param web_header_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header_key OceancdVerificationTemplate#web_header_key}.
        :param web_header_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header_value OceancdVerificationTemplate#web_header_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36d545ad5aca6c050fe87673616b729eebc4a7530112610b58907e4e2990d171)
            check_type(argname="argument web_header_key", value=web_header_key, expected_type=type_hints["web_header_key"])
            check_type(argname="argument web_header_value", value=web_header_value, expected_type=type_hints["web_header_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "web_header_key": web_header_key,
            "web_header_value": web_header_value,
        }

    @builtins.property
    def web_header_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header_key OceancdVerificationTemplate#web_header_key}.'''
        result = self._values.get("web_header_key")
        assert result is not None, "Required property 'web_header_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def web_header_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_template#web_header_value OceancdVerificationTemplate#web_header_value}.'''
        result = self._values.get("web_header_value")
        assert result is not None, "Required property 'web_header_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationTemplateMetricsProviderWebWebHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationTemplateMetricsProviderWebWebHeaderList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderWebWebHeaderList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3efe034e754469c627dba62d6670728800fea78ec53d766126cdf85859846f53)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "OceancdVerificationTemplateMetricsProviderWebWebHeaderOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3732fc3a1b902b19b24f130ce1b0369df25495f780cdffdf8097f8d322734bbf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OceancdVerificationTemplateMetricsProviderWebWebHeaderOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c478b15f56205982244fbc688e897b9bbfae09457ae45efe10df088e1cf6cc9a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b265157159df8e3071c3d82f0caf5c800fa3b50f95073c2892707ee23c2b8f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__12872b58eaa7acb4b2b651d64ee5dda89d52b5086877ca28efae0a942326ebe5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderWebWebHeader]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderWebWebHeader]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderWebWebHeader]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8556597a57e4ae382ebdbe5cd95c142a273beafdfb53b7d8e49fd992128b6b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OceancdVerificationTemplateMetricsProviderWebWebHeaderOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationTemplate.OceancdVerificationTemplateMetricsProviderWebWebHeaderOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15346a7d59503bc5c93c663e304c3ab8cb26062c94f625effe3ce72235ff0b23)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="webHeaderKeyInput")
    def web_header_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webHeaderKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="webHeaderValueInput")
    def web_header_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webHeaderValueInput"))

    @builtins.property
    @jsii.member(jsii_name="webHeaderKey")
    def web_header_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webHeaderKey"))

    @web_header_key.setter
    def web_header_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f2a81b6b0328aefeb0118f29b3667189a7b55e0583ccbfd98b69d0e349a09ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webHeaderKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webHeaderValue")
    def web_header_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webHeaderValue"))

    @web_header_value.setter
    def web_header_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d91edd08080b1c3a209e1d88ca102540cda479dfa9897bb14b05e09c2359670e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webHeaderValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderWebWebHeader]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderWebWebHeader]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderWebWebHeader]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6545583aecd34ae6f6de535c5f44ca065194fe734ae9f2540f2c61753b8e12f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceancdVerificationTemplate",
    "OceancdVerificationTemplateArgs",
    "OceancdVerificationTemplateArgsList",
    "OceancdVerificationTemplateArgsOutputReference",
    "OceancdVerificationTemplateArgsValueFrom",
    "OceancdVerificationTemplateArgsValueFromOutputReference",
    "OceancdVerificationTemplateArgsValueFromSecretKeyRef",
    "OceancdVerificationTemplateArgsValueFromSecretKeyRefOutputReference",
    "OceancdVerificationTemplateConfig",
    "OceancdVerificationTemplateMetrics",
    "OceancdVerificationTemplateMetricsBaseline",
    "OceancdVerificationTemplateMetricsBaselineBaselineProvider",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadogOutputReference",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderList",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelicOutputReference",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderOutputReference",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus",
    "OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheusOutputReference",
    "OceancdVerificationTemplateMetricsBaselineOutputReference",
    "OceancdVerificationTemplateMetricsList",
    "OceancdVerificationTemplateMetricsOutputReference",
    "OceancdVerificationTemplateMetricsProvider",
    "OceancdVerificationTemplateMetricsProviderCloudWatch",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesList",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsList",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensionsOutputReference",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricOutputReference",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatOutputReference",
    "OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesOutputReference",
    "OceancdVerificationTemplateMetricsProviderCloudWatchOutputReference",
    "OceancdVerificationTemplateMetricsProviderDatadog",
    "OceancdVerificationTemplateMetricsProviderDatadogOutputReference",
    "OceancdVerificationTemplateMetricsProviderJenkins",
    "OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters",
    "OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParametersOutputReference",
    "OceancdVerificationTemplateMetricsProviderJenkinsOutputReference",
    "OceancdVerificationTemplateMetricsProviderJob",
    "OceancdVerificationTemplateMetricsProviderJobOutputReference",
    "OceancdVerificationTemplateMetricsProviderJobSpec",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateList",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateOutputReference",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersList",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainersOutputReference",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecList",
    "OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecOutputReference",
    "OceancdVerificationTemplateMetricsProviderJobSpecList",
    "OceancdVerificationTemplateMetricsProviderJobSpecOutputReference",
    "OceancdVerificationTemplateMetricsProviderList",
    "OceancdVerificationTemplateMetricsProviderNewRelic",
    "OceancdVerificationTemplateMetricsProviderNewRelicOutputReference",
    "OceancdVerificationTemplateMetricsProviderOutputReference",
    "OceancdVerificationTemplateMetricsProviderPrometheus",
    "OceancdVerificationTemplateMetricsProviderPrometheusOutputReference",
    "OceancdVerificationTemplateMetricsProviderWeb",
    "OceancdVerificationTemplateMetricsProviderWebOutputReference",
    "OceancdVerificationTemplateMetricsProviderWebWebHeader",
    "OceancdVerificationTemplateMetricsProviderWebWebHeaderList",
    "OceancdVerificationTemplateMetricsProviderWebWebHeaderOutputReference",
]

publication.publish()

def _typecheckingstub__2a12fda4f6878c20e82681e9263b5110dbe2eb3d066dbba2cc9ff19ce6aecbcd(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateArgs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetrics, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__782e40265bf9577923bec620a65f9e32425fda1af1bb4af264f90444ca2d089f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3212cbc442b9e88edb29c54af51521659de211af6f5e541f74426271bc0a76c6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateArgs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba32a316a1466409ea6d304d710790c9089974895473ae77edfa010d746f36a5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetrics, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f84b4063ed012eabefa6ccee5ac6e70e3613a0d5c602e80041b9a8586c58faef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__613d2e71f2d1c32a93c20b005f6d6c39eb365957de8f871c603230f6a3d0203a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e452c216ef7320fd9314d56f6bf3b765421707e2aa22f53e3bb19f5585a1f6c(
    *,
    arg_name: builtins.str,
    value: typing.Optional[builtins.str] = None,
    value_from: typing.Optional[typing.Union[OceancdVerificationTemplateArgsValueFrom, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ed30b5b940ecdf0cac0344b3970703456af2962b284f6d3aadaaadc027150c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39eb0386acfcc47c32365100b9af024e2cd62e5fb7c4b9c083df3789c0f58bf9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30dca440edbe58d5dffaa570feadf67db3b896dce8364f16e6307a1136e25314(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4062d9a81dfcbec3c7e11d4f7fee5a739cb051254225497caa3eaa60364f17c3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41f06077cf24857181e754a5c35fb382c55e5500f0b2e58abe51993f9a1a8618(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d4162220d1e2247fde65944a45543adb83f2a56b8329bac19f553912d95db95(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateArgs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d9adf58d3f9190707c13eaa513f43fd88b034d7aa925d63a5e86c4d726043d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d51a5d4aeca15a4669f7a6c22d3cd938a6da69915a889c31bf291dd7b41c1fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c58a641e2ee7765d953e80830cc71bb679ef4fb7e9327f009293be6731d076(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96fdd0840f9bd81e846ada99687cc1a110f56f0ac81edb974d38c07057702c09(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateArgs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f6f24546ef78d4b314bd70c9949c5b52b8124a1f76e55d0ba6b630d86c3b924(
    *,
    secret_key_ref: typing.Optional[typing.Union[OceancdVerificationTemplateArgsValueFromSecretKeyRef, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59188e742c55f04ee4d0f28b7d7fdca0830dadace3d3486b740975e19fb05e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e879d65073d3157335924f0154baae4415d8a9eef617b46eeb862247724011b4(
    value: typing.Optional[OceancdVerificationTemplateArgsValueFrom],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ade934b5799c68438c6e674226d54b0555366a4923c9b0743eb0d7c220a883d7(
    *,
    key: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e3eb2a44a05237e6cb6246eecbeb6bef09a2ef61747d381bd3ef207da23609c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caaf5a76ac3d2bee673b052f7b5b5d81c50ccb88dca9ed16ca42929907a193b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e83f48fe7b8551bfe3e0990f2e2d0ddebb464c5698a21eb820c359352dfe26e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__670c07b7470a703c3aa38b4f1b0f86edb1c83e914b6b1ccaaec285e6d6d67ea0(
    value: typing.Optional[OceancdVerificationTemplateArgsValueFromSecretKeyRef],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__314bc0934431d84bd5cc373437a5d41d2c7e1077d468aef9f10868e14d92b80c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    args: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateArgs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    metrics: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetrics, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67c26268471e62a5a9dbd7c0c74bc9e79ff13e9392ae878fe532ecad11a841e7(
    *,
    metrics_name: builtins.str,
    provider: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProvider, typing.Dict[builtins.str, typing.Any]]]],
    baseline: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsBaseline, typing.Dict[builtins.str, typing.Any]]] = None,
    consecutive_error_limit: typing.Optional[jsii.Number] = None,
    count: typing.Optional[jsii.Number] = None,
    dry_run: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    failure_condition: typing.Optional[builtins.str] = None,
    failure_limit: typing.Optional[jsii.Number] = None,
    initial_delay: typing.Optional[builtins.str] = None,
    interval: typing.Optional[builtins.str] = None,
    success_condition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6760d59051d8a9f62139d3e2e5dd74729bb50bb6d76f62edc01bca26dbd5dec3(
    *,
    baseline_provider: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProvider, typing.Dict[builtins.str, typing.Any]]]],
    threshold: builtins.str,
    max_range: typing.Optional[jsii.Number] = None,
    min_range: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dadf6c5328ae4d6782d1c8c52f99a80bd8b3d41fa3477ff4e65c3d7f3f6b6a6(
    *,
    datadog: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog, typing.Dict[builtins.str, typing.Any]]] = None,
    new_relic: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic, typing.Dict[builtins.str, typing.Any]]] = None,
    prometheus: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a20390d7eb3d24958dd544030b8bf7733c841b981049504c937b6dc6e9eda59(
    *,
    datadog_query: builtins.str,
    duration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1c48a57b78018b3c163dad151b91a101568c18443ba623cc7faeffbf1decdef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1aa6357772e50290a74f00c809d6f297d2774330ccafa51a0fcace2ca608eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec25feadcf6ce383d292c9e3f4c923b76e37a710ad09b2176cd9180cf74f5e01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69feb638cdd59773db5814076e247251f6421d1a8e74c1e1d68b3fe038e8dac4(
    value: typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderDatadog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86fba526d9a33d306e7446284c6ecbbe35564377322da74cfad6cabd572130f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d579059e6f15ad2cd5cc13b47984e4e5f5e75769ab84d4cbebb0bd6fc67fa2b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1db1c74cedeaf5be6f507b7b9cacb02c1a8729e8002bd7d85c546880e816dfd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e34830be59ba56beb4cdea16aa604bf63cf9d3cc42c175873b49d1efd057c817(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7fe4acd679ca24657f4efeb833f28fcb9e1932a16aa7f738023d5b3187833a9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__033d33a1567fbb071079349404f577468d4d3ef8d74298b6de63244c77a6dc65(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsBaselineBaselineProvider]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70859eb8cafe290d4da95a8c482bbbcf0322eb1ee797412d1bac8e3f61b324e0(
    *,
    new_relic_query: builtins.str,
    profile: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be65c270841ae2954c3576a8160e5d5db896b45c06aeb9c0212f94f2ed0e3f67(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40f8e0f879c0e898459c52fad9b94af61b451ff8021204033eca77f30a9bbb67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce12b78f6d36d9d9adb426dfd8980f88c11739f546a8b627ef2637c16de43edb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc1fc0e9add38ab12740c3bdb6acab8c1e5e4864174793e4d9d643762b05a71e(
    value: typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderNewRelic],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9cbbf8af4aadbcc2aa4519314e99407aea0e843f38afbf091cadc38f7081cf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dbc04acd579bcd96985f1cdfc35347bd59fce11f6883f5b8cbc751eb855c5ac(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsBaselineBaselineProvider]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__010671dc3bdfb540db27cd689f98c569eba3af0245c33018758b913ecf2c1608(
    *,
    prometheus_query: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea81d5ba9ed9c2fff65ef0c22adf93dbd2a7b151f5922d3960cb44abdfc220e4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9992e2b20cd7734751c7e20b08b5b2eb465281baa7cf81d41cdae2e9db8e4dbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aadff29d6e93a4f9b3d8433fe95f61d0caea7f15dfef92ca4620d80b5258a0af(
    value: typing.Optional[OceancdVerificationTemplateMetricsBaselineBaselineProviderPrometheus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40d2f7b07d1d3c50a5c566dd403107b39d5896ead0132009509d16c62578d559(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb46d879af005330c4915f2a7810720fb3e5ba93d4628dc69286419448028ee7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsBaselineBaselineProvider, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c05b3767603a3e0aa105a79ea122110a5fe7c136b8c664fe681db0c5338e6f1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__254389ad44d9793ebd5303daf6177e7b92f4e1e97c716ae872d16431d32af1a4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0c2e2b403f8af3d5f791ef9b91a3d00c21239d8632156cbd9abdd7d7c897152(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04add745f6b0976bee4f35a15cfd437b4bb3b6006100a21d3f7d4533cca6fae2(
    value: typing.Optional[OceancdVerificationTemplateMetricsBaseline],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc4334cb98f561be4c52e158d8780816ddf2eab6cce79543bffba29b43cd055d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__016b740d68981ad20d7b73284abf9a18e7aee8aa1faf38b93369f03b48a93f5d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3f58ef70267d7004bccc41ef8e7426a46de3686c7de8d2304c7ba22b9b16eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c2a7e19de3187a90d326c7b5d24143126b8bd2fa73495f2fb45c4c0f9d8c18(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acc5dc1f20f57aef656470ff18a05eff0c4c47b23a4587e22e419f5ee9443463(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79683e865095dfcb85e32fa7a2033f314c737aec2cb493159b42dd65ad65251a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetrics]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d002a81226424d3188635998eaab7a8c8ff75c57afa5291ddb646ce90f11eb49(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bcb52dcc4271cf650effc1bc2800ce25ff7f3420a448ee043be31a3317bc009(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProvider, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__801b0d3abe5301e4cc39afee1dd69c28c23cc9d67d6b4f50d92a4a3798371376(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53dad91af7ebaa6af15566506d209b834bac88b18d2709195887364cb7f4e12c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2d4ac99f9ccd592f15458a506a781cef953b61c3e5ee08e838fbaf43701b709(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1552cad160f23c95005ef9bbb72d89e06581e16f7098f33b28e2ff99e10fc6f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d174020623026423d9056268537c293a11fbdd24d7049976999c22ea2f943370(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a63dfb6f0655429cd1c6c1e61871b8ee391a687fc24da914d6f12c2f5ea9e4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2caa9983db82c325e4d1062dfe8320757862c1a3913c5b3338f748c834906fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f243dd8964420734ce670498fa310d9d74c20f6d2df5f2b6d65c749aeae7b40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26df54ec76e3b1c694f4e3eb4c12a1c972c7fb2fa998f9f1af5bd7935392533a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcd1c76858e29ba054f97a7b4ce6dc4610ebe9165f8438436479ce2cb9b409ec(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetrics]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb6437c93f4d27d774e3254fc682f9513c141edc665a7e0c8ac2e73b020b2f36(
    *,
    cloud_watch: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatch, typing.Dict[builtins.str, typing.Any]]] = None,
    datadog: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderDatadog, typing.Dict[builtins.str, typing.Any]]] = None,
    jenkins: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderJenkins, typing.Dict[builtins.str, typing.Any]]] = None,
    job: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderJob, typing.Dict[builtins.str, typing.Any]]] = None,
    new_relic: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderNewRelic, typing.Dict[builtins.str, typing.Any]]] = None,
    prometheus: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderPrometheus, typing.Dict[builtins.str, typing.Any]]] = None,
    web: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderWeb, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68ba641f0fe9eac98315c628fdae941233f445aa1b43b60a91508724a4be4a6(
    *,
    metric_data_queries: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries, typing.Dict[builtins.str, typing.Any]]]],
    duration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f7e4ae014fb1b75c96919fe431fd2945ee2062115cc3594998c1ae10f0b8107(
    *,
    id: builtins.str,
    expression: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    metric_stat: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat, typing.Dict[builtins.str, typing.Any]]] = None,
    period: typing.Optional[jsii.Number] = None,
    return_data: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8ae39b4f7bc13f7ccd98514ad9a89a979632ba12f7b341ad24b7dd0ef2c941c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98d8be9eb2ad4fe5f7e9e13bae8ee64cfed67643788b1d71d5223a45ee5eb1cc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b527155660bbab0dbb7a2d015b2f8611cf906c2fae0f2c1e327f300af5f73d65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5ec0e480c0075b6a4de1d10641373d4bab148efa378d43d99694206a678d495(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb11ec362cdb38db6bb13f4ed9845e91d0d1f917b25e6a7b02ae8660d3132a23(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d8144894bab70691f8481a928526e629ace217c6644df3f595f6400a216fe51(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73e26d500b1ea010a61b8859537844e9e0c304f7e4f906f9f52205b27b6ceb09(
    *,
    metric: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric, typing.Dict[builtins.str, typing.Any]]] = None,
    metric_period: typing.Optional[jsii.Number] = None,
    stat: typing.Optional[builtins.str] = None,
    unit: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b2071ff26767a6370615cf7f378075a7380a84b891a8a6781d87077d9c889b(
    *,
    metric_name: builtins.str,
    dimensions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ee0a73729388ca6a73ac101e89babc6f956f24e9561fbcc57831b1d2c84fdb(
    *,
    dimension_name: builtins.str,
    dimension_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__173581dfedbeabbdeb374b1425d2048583a7acbbee878ab5e15cdee1d427e685(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b79a8870acb48a8a327dd615228a92a3cad6ba4f60d4623d64bc1485e2c1c400(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8853bab7c3828adbbb965bad3b27a0320de9d02a360239e6a60d95c73520402d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__758af417f3e997fcae6ba41d23f734037159f33bd1e23a1cb9a5f616e165b888(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bff41e3687644da64ea9ca8fd4df5063405d0fcc1c9bf42beae564f0c0a6d895(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9e63fad30426bd9f18fd7772f1e7b5e862ca4eef2eb6a9a304d67a8c70cc7f1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__010135167b3d903738f4b914862515528aeb8d6e9726f66e804b8eb33c9f6a1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f88703840f4e339a8be92fe141a8dd2376f510f62c1599c21535baba2d74f3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa4b6ba1a6c1381b98b4de7cbb76e58534818749460cef5aab0fd890dc053d40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e729c6d40ad58767057e775d5fe22bb37416d674f2f5f00350ec71550f3ee326(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95a436da873c4769865f0b0fbe61fe8bec34ff6f627514b9575ebc444254be12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ab0658bb9568d8ef5666b30e0b93ac7d10639750ace1b15e9b3bad0ab1da331(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetricDimensions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069e54c1e81901b117cb0c654a99ff79ac2ecdb706be7f8a1749bb3188819ff2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d2672baac08cc8a020c4a8742da44a469ac32c050fce4381d7687ab599064b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a56f3cf4d96b29851b4b21dc8e3db1f06d3848f03f69f4e9b3d0872e6360a30(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStatMetric],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cbfd2fcc7d8778f0f7078b019c1eed6cd4c3835089f0209c976fb4bf1ddc1d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__829107bdd2271c694442c23bd3fea18ed57e976be639d8ebc7adc4ff732763ee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6a8f6d433dce024dc62d2d8f2851b245c4e2aa0eb417579688ea97dca32c225(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daffc83aa07db727b008037c1648b5be4a25e12a3de0310c1548dd547f1d846d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59ef5a56da54b1fd58bed2a1ec89b26858012dd26336a41e1c181de1c43cee6e(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueriesMetricStat],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5cb9f91f88346ffe122ab0f080f07d7719c5ce95f254def3821f495b9994f20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06e6171008f29ec06de92d797fdeef7411a56fb6ed75012dac2815b1f7f3ac30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__316abc64873edf4328d5dcec26f191183507ae0aff5ebd314b37ebf0ea0fb2f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4efd21c3b52df79f5c68325e4c579fe7665b75e1b597b760f02bb218559ae384(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98ffc4af92d387a875b1f610446a13d7ecfaaeb6c83eb0b40d49bb9fd17de697(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfbfdf4f9c58f3a285f0aab4ab445b21f740f2e7e6754f0bd3334675f2f24221(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca3b1e44925567d96b5e0c4e456068e815c55e17139faa67461c0aa4fcda2de2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f7fc41b9976a3e0e88fe6bbfc0f667c785fa9778fad8e5c64874cfc5a0e7c0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a3a95a6e372f5e2246f104f778c6622e389a34c29d4693391e0472a1be76f6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderCloudWatchMetricDataQueries, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fc599c35bcdbcc97a2da54ba9045ba6b3a2cb6789ac86ee070cff722edf942c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__743532dc96dfd97ef4191f4cea6290a5cf3b3ef77a17323a27dd88e92803197c(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderCloudWatch],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2002de9ffe344f9718caf39b725c5f34beaf91f259270e0dd764f9a41a57118(
    *,
    datadog_query: typing.Optional[builtins.str] = None,
    duration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62662c4782edfb6baeb34f8bfbb5ae5983b5e9d35dba434e227e16653e4abe6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b31f717669dcb5f3edc305f462e1fda726b19544fe1703a7c5b0ffea4bbf378(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7d2b6232923ab63529ac3dfc4b0cfcf9007ec265dc2466d55373c00db8bd63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b878548d5f893f9531d62445adccb7945c8d65062e916ca03d1727e131087f3(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderDatadog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22527b8229c283d77542079d948411898d2b3cde06b2e4296d76595a8b97ee15(
    *,
    jenkins_interval: builtins.str,
    pipeline_name: builtins.str,
    timeout: builtins.str,
    jenkins_parameters: typing.Optional[typing.Union[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters, typing.Dict[builtins.str, typing.Any]]] = None,
    tls_verification: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c33fdfb6b4cb9c9fd31f72dd6bc55c83bf0421d2abc7d113834a32f51401c2(
    *,
    parameter_key: builtins.str,
    parameter_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc3e7bba05ee4783cb4cb0e844f40eaad5582f00ddc74e003c45956176dc43d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f51920f13a35d6afb6ceff22119313ab6131b8af9e2289789d2a7b2c798865c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c1381ba408c5e78493a0ad14b32c87fa10ae7aac2f13e39fc1ca02a3c686300(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aab9b1f11f68fcc1928271394123a8c2cfc5163f9bc2672605929c3f00bfdbef(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderJenkinsJenkinsParameters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__214b5dec3e8cc16b6f4d9a47b47feec4a16d7e799b9cc92e2e24da60ffccacc3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c1440f5a34d8e704ec85f7f6a42bf19d0dcbf5f11b410a9168f71b2698fee37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13c90f2439e65c7a9ebd92084e8c3592d460f1d29643a68d0d5fb7193db3714(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d6c28318126e00c6ce336c3558b0ac0b3c544f18f0a7ba7ef6c92a69c74bc04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f4f0ace644bb61aaa7ce8a1605ba22f01e86cd250be392c67e6bae2d4bcd639(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b2d9cb6f77b4451ee8b15275b013709c996a22e5878b8b5b93a673efdf3a14(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderJenkins],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__024dcc65d49d9aedc20c38f6c1f545412ce337fb4852cd914a9e282222c9ae6d(
    *,
    spec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpec, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ba94398937549a43ea26a3e91aa26a01c35b75938e93d4745ae05937f20e864(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc806c4156582abbec248f55b76e181b4b9cb2ff3af046baaeb05552ab540f5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpec, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__252d39db417bfc85595d2b804fbb1eafef005f78f1b23389a69b7bcfa560bafa(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderJob],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aea98e2d74eada400bc756a8331912403fc446c68244aa86a7bf3cd9d2231d53(
    *,
    job_template: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate, typing.Dict[builtins.str, typing.Any]]]],
    backoff_limit: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cad3834432a413920433f220a14cd57ef873fd27d2487c3f65901bf1a1d067a6(
    *,
    template_spec: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4569197b8a93ee77d8619b35c20d6f681853604b83f6e50301f8a23a578122f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35abc0e00ca94073a3060396eadcfd14d5de3dc3f3bb0178fbc4399ac7c0bb10(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d8a19d407f53fd69a44911e1fc47b4604aa70f04bcf0634c19de0a9cd5cdcb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25d1c96346d86ec0b9927b47c3d001bba545e174d74b2a6ef8f6d81c6f308b8c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1fb25c121ee5c0f326e4e4bfe79c69806a145f615763866d13d1c744a60712(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aef66836396cd51146b6926d01bf458d84885834e411ea17426462669a8c470(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e63a9ce0883e3dee27f38ae7ef6519e4f182482de525cd44362a222480792851(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ad0987dfe6e74eb827c0ca6adeeeec5abf514f79cf9a7a1280bed001574f46c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__965c425ebe66202b4c4b392cda510659f1b5f6ed911d7ed827e8d3950e9d55c6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__037b9d80869b76df66d27df0cae370795d3deb9da9282c70a128b20d92c86aaf(
    *,
    containers: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers, typing.Dict[builtins.str, typing.Any]]]],
    restart_policy: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dceff0345ee96145c0cabd8086706bd9c233d051050436b8cab1e7aadf89782(
    *,
    command: typing.Sequence[builtins.str],
    container_name: builtins.str,
    image: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56eac0db77865be51b1e1a932d21239934bb807c635efecec9a78d4b21688966(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d215737581f42ace58548a5db932d1518aabcbc770a2c66864543faaff20f59(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265b9de71c6ef4bf9fd1f214fb9940a33f2388453341dd784f189325d60bcb43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d38715c5b4ade39931f9de17ec69a4ee3706f849a300ae74f13e830bd493266(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7486c1960e8f93cac555aa829b529ca13c33a21842e76b36a9abc91ab7e6edd5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a49b9d55733dfc0aa05658340665926d559247279eecf947124e21f7b0b0c92(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d98d6dfff1bbbb45aaeec8718727553a90e0dcc6b95f3a3039aef2d159d13727(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf25120a0ee51400d3556e39ecb39b3e5a6811466632f88e45cde922ab2a43a7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38bd46a51170ea2feb2ebc9ee0c664ddd361d7c0a36c333fe781dc39649b2ee2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd100476a430bd549064a08259693a018ac42393716bdda8bcd2ddc1e7b70ebd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a718ce8f27d7f00865c50613ae428b404523abae7043a46d1618bb5b366b7d39(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe949b77845c5323c167d5595c9685df06f47ffc1276bf4ba55a34afed257123(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32418baaa0589b5f4f1a24a0e10d24a3e46d5b5d26a373bc6cbd001f92fd89ad(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b008af2251519c54b6ac342d5fb537c0bf440257ea5ba23868d78f8260615f7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__430ddf60bfe64fdbdb625aeb48152037aee3d0efb8e746d53eb6d55e985071c7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e528ae30554268edf5f21e9797312667ee11b6f38c3988f1fffbccff33813c08(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c66876ac7fa9e54e995f9439d19bfefe09227a9e27ae68d6265ce1b552433a0f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8df4e68db4a0b770340450fea11c713ab4620b30f8e0adabc36c50873d799d1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39637cc8282ba87f1d0ab1da83f77f9db04c758aa7d7234bb8039396e07ef952(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpecContainers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e93c58554ff664d28fe25135a76eaa59f3a64b540bd3a8036260eabb75d43f09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e488df4652eeee37340eaa4ff3682fb801f6df0be106b07f23042cebaebacda2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpecJobTemplateTemplateSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f393c353cab03cf57bbf5c5283cc837b7facdba472aa34ba9e79c297a92434c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de3e1bdeab5e053a652fc0160bf0f12a6c161d57f95b0aada48be1c1793118b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e012ecb4ad5ae117084bb2a6af1a463362bc1f4d20ff5b6736f2b88d41495ca8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26c812766371d6eb3424648a8325e5f41006f5f740d7bdddade27284672ec511(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51fe312e40fb4eeb47d0b240999d6fc7ccf2e558fd10f03a644ba8c2233135ed(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4d1943a367d438de0cb92f0049d0b1429aba126fbefa8760248d0bb6b61cd1e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderJobSpec]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e8c095b54243e60ea3632e9379fc18f47169c683b20e2d600eb0784591a262b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf8aee579a8c595ea8b8a858384b5fefa36b92d40de9c695aadcea3b5397c33e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderJobSpecJobTemplate, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2e1aeb9777d7d292f31a8649979f0623cfe23ea8c3c219556dec65cd348e63(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9cad6cd7353084eb670bff7bfb5905a4580784833a4becd027a5241a726a8d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderJobSpec]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71f6e935233b30924368e0d2efa6bf3562b536d423a5da20d50b76864f40cce7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84fc69e50efb199751ef261f6ab7d571b675ca4b55e0fe481d77a267130490e4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__925ebe777dc080f4ca7f8cf293f1b5746b51620b7a0c85a557c80806e4ab1c3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31337c968582e2d182bef41c0bb918e80aa56f2091ae6a23a2d77f727338922a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84f328807f031ea29639c3d57d570ec629d5117a9ac697d3988b4d9986eb2f45(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b6dc7b0a704f6cf0d56d58e6b61c4e7b174ec828dc9c54197bf37751f7f9b29(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProvider]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__153a3eb557debbf37dc0d0674006c2d984daaf9f773e0370278f6183f0e28055(
    *,
    new_relic_query: builtins.str,
    profile: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb94d4d8ffc63c111447b7f2a9cd6892319d1f1537a08b3de73cde9829e3a099(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e65f736cda572954948907264620e0fe0dc668bb57152b48c8da70d1857e9d8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a909d0dd34c21e6d626210dadf184e6bd04e80a6e6a26b4d2711f95fecf1fabb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__405e34961448f9ae29f067aa15e0c3bbd56be498e08b9e463213c774ffa2f5e8(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderNewRelic],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ee2d1c6ab2dcbe22fe1d2f2232eac7e869a0d30f6d4e56a383e8f7e3561ee7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d63048f2958b195c872286b9c29fa822a5461b308c7ca164cfaa4e7c8c06708(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProvider]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21445fdabfba233c339df7b497f487605e9d6d5f07810b2b5274145599dee1da(
    *,
    prometheus_query: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51cde5cf5a68dc4adaccc90ac30d9b45885578aa146dc1095dd54ef77804b2ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cccc2cd82b037cf5a730b4b9039ebfad4ef09dbe3fb5fdeb3242e6f129f46bf4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a2b06cf1debe1c2e828015bd2ae7c663ffb013178639e660d57984698405b6(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderPrometheus],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8331eba10c417449ba896a3d09bfefb0413988008590b2fd336c09d9ca50afae(
    *,
    url: builtins.str,
    body: typing.Optional[builtins.str] = None,
    insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    json_path: typing.Optional[builtins.str] = None,
    method: typing.Optional[builtins.str] = None,
    timeout_seconds: typing.Optional[jsii.Number] = None,
    web_header: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderWebWebHeader, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a26f67b943f162892fe2c27f9817509e616ff4e67faf4d631c1dd4a537e1fd8a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dff1da99bf10e9facd239a7577e4fa1ef89b53296da64146b7f580a1a2d5f66(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OceancdVerificationTemplateMetricsProviderWebWebHeader, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e0655fd515db9a651484098f9b43a33093e4b3395c1a3efbea88ca4a16bc732(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4071a35b0c024d0c7c96e15e91fb4ce361a8ed111697dad11c3de2b09f948c42(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df59116610223fd137003d10ea384743b2b420eb59a28be5487c202ccaaef04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__031f06a6c4ccf93b1124a5fd37b1e98f0fcc570c669c501a17cfb7f30cf325de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f05fda890b03b096c90332cdf1a7a5eeb8487787ae9d3e584348d145d9d8e50(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dc6f22b74f99809eb4ea74fd9951be1c7069b478ccf77ce953c8dc8b4886437(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df8faae4034a3cef318958a44cc4d2164fa8efcaf4b1a83fef6f19cc015b47f3(
    value: typing.Optional[OceancdVerificationTemplateMetricsProviderWeb],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36d545ad5aca6c050fe87673616b729eebc4a7530112610b58907e4e2990d171(
    *,
    web_header_key: builtins.str,
    web_header_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3efe034e754469c627dba62d6670728800fea78ec53d766126cdf85859846f53(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3732fc3a1b902b19b24f130ce1b0369df25495f780cdffdf8097f8d322734bbf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c478b15f56205982244fbc688e897b9bbfae09457ae45efe10df088e1cf6cc9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b265157159df8e3071c3d82f0caf5c800fa3b50f95073c2892707ee23c2b8f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12872b58eaa7acb4b2b651d64ee5dda89d52b5086877ca28efae0a942326ebe5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8556597a57e4ae382ebdbe5cd95c142a273beafdfb53b7d8e49fd992128b6b47(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OceancdVerificationTemplateMetricsProviderWebWebHeader]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15346a7d59503bc5c93c663e304c3ab8cb26062c94f625effe3ce72235ff0b23(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f2a81b6b0328aefeb0118f29b3667189a7b55e0583ccbfd98b69d0e349a09ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d91edd08080b1c3a209e1d88ca102540cda479dfa9897bb14b05e09c2359670e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6545583aecd34ae6f6de535c5f44ca065194fe734ae9f2540f2c61753b8e12f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OceancdVerificationTemplateMetricsProviderWebWebHeader]],
) -> None:
    """Type checking stubs"""
    pass
