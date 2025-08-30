r'''
# `spotinst_oceancd_verification_provider`

Refer to the Terraform Registry for docs: [`spotinst_oceancd_verification_provider`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider).
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


class OceancdVerificationProvider(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider spotinst_oceancd_verification_provider}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_ids: typing.Sequence[builtins.str],
        name: builtins.str,
        cloud_watch: typing.Optional[typing.Union["OceancdVerificationProviderCloudWatch", typing.Dict[builtins.str, typing.Any]]] = None,
        datadog: typing.Optional[typing.Union["OceancdVerificationProviderDatadog", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        jenkins: typing.Optional[typing.Union["OceancdVerificationProviderJenkins", typing.Dict[builtins.str, typing.Any]]] = None,
        new_relic: typing.Optional[typing.Union["OceancdVerificationProviderNewRelic", typing.Dict[builtins.str, typing.Any]]] = None,
        prometheus: typing.Optional[typing.Union["OceancdVerificationProviderPrometheus", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider spotinst_oceancd_verification_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#cluster_ids OceancdVerificationProvider#cluster_ids}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#name OceancdVerificationProvider#name}.
        :param cloud_watch: cloud_watch block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#cloud_watch OceancdVerificationProvider#cloud_watch}
        :param datadog: datadog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#datadog OceancdVerificationProvider#datadog}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#id OceancdVerificationProvider#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jenkins: jenkins block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#jenkins OceancdVerificationProvider#jenkins}
        :param new_relic: new_relic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#new_relic OceancdVerificationProvider#new_relic}
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#prometheus OceancdVerificationProvider#prometheus}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49746daf239d6d0230ff222fa699ae49df2508214e23925927917f9bed42d777)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OceancdVerificationProviderConfig(
            cluster_ids=cluster_ids,
            name=name,
            cloud_watch=cloud_watch,
            datadog=datadog,
            id=id,
            jenkins=jenkins,
            new_relic=new_relic,
            prometheus=prometheus,
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
        '''Generates CDKTF code for importing a OceancdVerificationProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OceancdVerificationProvider to import.
        :param import_from_id: The id of the existing OceancdVerificationProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OceancdVerificationProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2abfd72a63d871814fcf1b92872d13f9f3954f40f4ea7034f6bc1d3919daf19)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCloudWatch")
    def put_cloud_watch(self, *, iam_arn: builtins.str) -> None:
        '''
        :param iam_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#iam_arn OceancdVerificationProvider#iam_arn}.
        '''
        value = OceancdVerificationProviderCloudWatch(iam_arn=iam_arn)

        return typing.cast(None, jsii.invoke(self, "putCloudWatch", [value]))

    @jsii.member(jsii_name="putDatadog")
    def put_datadog(
        self,
        *,
        address: builtins.str,
        api_key: builtins.str,
        app_key: builtins.str,
    ) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#address OceancdVerificationProvider#address}.
        :param api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#api_key OceancdVerificationProvider#api_key}.
        :param app_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#app_key OceancdVerificationProvider#app_key}.
        '''
        value = OceancdVerificationProviderDatadog(
            address=address, api_key=api_key, app_key=app_key
        )

        return typing.cast(None, jsii.invoke(self, "putDatadog", [value]))

    @jsii.member(jsii_name="putJenkins")
    def put_jenkins(
        self,
        *,
        api_token: builtins.str,
        base_url: builtins.str,
        username: builtins.str,
    ) -> None:
        '''
        :param api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#api_token OceancdVerificationProvider#api_token}.
        :param base_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url OceancdVerificationProvider#base_url}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#username OceancdVerificationProvider#username}.
        '''
        value = OceancdVerificationProviderJenkins(
            api_token=api_token, base_url=base_url, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putJenkins", [value]))

    @jsii.member(jsii_name="putNewRelic")
    def put_new_relic(
        self,
        *,
        account_id: builtins.str,
        personal_api_key: builtins.str,
        base_url_nerd_graph: typing.Optional[builtins.str] = None,
        base_url_rest: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#account_id OceancdVerificationProvider#account_id}.
        :param personal_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#personal_api_key OceancdVerificationProvider#personal_api_key}.
        :param base_url_nerd_graph: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url_nerd_graph OceancdVerificationProvider#base_url_nerd_graph}.
        :param base_url_rest: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url_rest OceancdVerificationProvider#base_url_rest}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#region OceancdVerificationProvider#region}.
        '''
        value = OceancdVerificationProviderNewRelic(
            account_id=account_id,
            personal_api_key=personal_api_key,
            base_url_nerd_graph=base_url_nerd_graph,
            base_url_rest=base_url_rest,
            region=region,
        )

        return typing.cast(None, jsii.invoke(self, "putNewRelic", [value]))

    @jsii.member(jsii_name="putPrometheus")
    def put_prometheus(self, *, address: builtins.str) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#address OceancdVerificationProvider#address}.
        '''
        value = OceancdVerificationProviderPrometheus(address=address)

        return typing.cast(None, jsii.invoke(self, "putPrometheus", [value]))

    @jsii.member(jsii_name="resetCloudWatch")
    def reset_cloud_watch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudWatch", []))

    @jsii.member(jsii_name="resetDatadog")
    def reset_datadog(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatadog", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJenkins")
    def reset_jenkins(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJenkins", []))

    @jsii.member(jsii_name="resetNewRelic")
    def reset_new_relic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNewRelic", []))

    @jsii.member(jsii_name="resetPrometheus")
    def reset_prometheus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrometheus", []))

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
    @jsii.member(jsii_name="cloudWatch")
    def cloud_watch(self) -> "OceancdVerificationProviderCloudWatchOutputReference":
        return typing.cast("OceancdVerificationProviderCloudWatchOutputReference", jsii.get(self, "cloudWatch"))

    @builtins.property
    @jsii.member(jsii_name="datadog")
    def datadog(self) -> "OceancdVerificationProviderDatadogOutputReference":
        return typing.cast("OceancdVerificationProviderDatadogOutputReference", jsii.get(self, "datadog"))

    @builtins.property
    @jsii.member(jsii_name="jenkins")
    def jenkins(self) -> "OceancdVerificationProviderJenkinsOutputReference":
        return typing.cast("OceancdVerificationProviderJenkinsOutputReference", jsii.get(self, "jenkins"))

    @builtins.property
    @jsii.member(jsii_name="newRelic")
    def new_relic(self) -> "OceancdVerificationProviderNewRelicOutputReference":
        return typing.cast("OceancdVerificationProviderNewRelicOutputReference", jsii.get(self, "newRelic"))

    @builtins.property
    @jsii.member(jsii_name="prometheus")
    def prometheus(self) -> "OceancdVerificationProviderPrometheusOutputReference":
        return typing.cast("OceancdVerificationProviderPrometheusOutputReference", jsii.get(self, "prometheus"))

    @builtins.property
    @jsii.member(jsii_name="cloudWatchInput")
    def cloud_watch_input(
        self,
    ) -> typing.Optional["OceancdVerificationProviderCloudWatch"]:
        return typing.cast(typing.Optional["OceancdVerificationProviderCloudWatch"], jsii.get(self, "cloudWatchInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdsInput")
    def cluster_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clusterIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="datadogInput")
    def datadog_input(self) -> typing.Optional["OceancdVerificationProviderDatadog"]:
        return typing.cast(typing.Optional["OceancdVerificationProviderDatadog"], jsii.get(self, "datadogInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="jenkinsInput")
    def jenkins_input(self) -> typing.Optional["OceancdVerificationProviderJenkins"]:
        return typing.cast(typing.Optional["OceancdVerificationProviderJenkins"], jsii.get(self, "jenkinsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="newRelicInput")
    def new_relic_input(self) -> typing.Optional["OceancdVerificationProviderNewRelic"]:
        return typing.cast(typing.Optional["OceancdVerificationProviderNewRelic"], jsii.get(self, "newRelicInput"))

    @builtins.property
    @jsii.member(jsii_name="prometheusInput")
    def prometheus_input(
        self,
    ) -> typing.Optional["OceancdVerificationProviderPrometheus"]:
        return typing.cast(typing.Optional["OceancdVerificationProviderPrometheus"], jsii.get(self, "prometheusInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIds")
    def cluster_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clusterIds"))

    @cluster_ids.setter
    def cluster_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0fe0ed02502db7f28e9571e3abdba98537020ba378a94d7447b29e27bda635b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1623e60521541aff44c6790bbd3c4846ee2c2dee88a63022a4c3cdaf304bd8f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fea45dcac1514cbbe86ec4e5837dca39b69b8aedcde8113a2bbedffb363a9d4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderCloudWatch",
    jsii_struct_bases=[],
    name_mapping={"iam_arn": "iamArn"},
)
class OceancdVerificationProviderCloudWatch:
    def __init__(self, *, iam_arn: builtins.str) -> None:
        '''
        :param iam_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#iam_arn OceancdVerificationProvider#iam_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00a781482e63d346cfbd059fb3f273bedf6b304e461b428425955c6f7c7642f1)
            check_type(argname="argument iam_arn", value=iam_arn, expected_type=type_hints["iam_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "iam_arn": iam_arn,
        }

    @builtins.property
    def iam_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#iam_arn OceancdVerificationProvider#iam_arn}.'''
        result = self._values.get("iam_arn")
        assert result is not None, "Required property 'iam_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationProviderCloudWatch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationProviderCloudWatchOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderCloudWatchOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__27a059dbf205bdaa7bff7ac24d5337af2247773c326d1556e0d0008832e00c9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="iamArnInput")
    def iam_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamArnInput"))

    @builtins.property
    @jsii.member(jsii_name="iamArn")
    def iam_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamArn"))

    @iam_arn.setter
    def iam_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0368eb2ffdbc7f917209e4709c96b576bea491baa839b3d359592d628f6e5cb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdVerificationProviderCloudWatch]:
        return typing.cast(typing.Optional[OceancdVerificationProviderCloudWatch], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationProviderCloudWatch],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7ae5e5b423fe7063db45ff6f23c55f80c02d5fab6ef0e129567b4c6ad9291fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_ids": "clusterIds",
        "name": "name",
        "cloud_watch": "cloudWatch",
        "datadog": "datadog",
        "id": "id",
        "jenkins": "jenkins",
        "new_relic": "newRelic",
        "prometheus": "prometheus",
    },
)
class OceancdVerificationProviderConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_ids: typing.Sequence[builtins.str],
        name: builtins.str,
        cloud_watch: typing.Optional[typing.Union[OceancdVerificationProviderCloudWatch, typing.Dict[builtins.str, typing.Any]]] = None,
        datadog: typing.Optional[typing.Union["OceancdVerificationProviderDatadog", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        jenkins: typing.Optional[typing.Union["OceancdVerificationProviderJenkins", typing.Dict[builtins.str, typing.Any]]] = None,
        new_relic: typing.Optional[typing.Union["OceancdVerificationProviderNewRelic", typing.Dict[builtins.str, typing.Any]]] = None,
        prometheus: typing.Optional[typing.Union["OceancdVerificationProviderPrometheus", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#cluster_ids OceancdVerificationProvider#cluster_ids}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#name OceancdVerificationProvider#name}.
        :param cloud_watch: cloud_watch block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#cloud_watch OceancdVerificationProvider#cloud_watch}
        :param datadog: datadog block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#datadog OceancdVerificationProvider#datadog}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#id OceancdVerificationProvider#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jenkins: jenkins block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#jenkins OceancdVerificationProvider#jenkins}
        :param new_relic: new_relic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#new_relic OceancdVerificationProvider#new_relic}
        :param prometheus: prometheus block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#prometheus OceancdVerificationProvider#prometheus}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cloud_watch, dict):
            cloud_watch = OceancdVerificationProviderCloudWatch(**cloud_watch)
        if isinstance(datadog, dict):
            datadog = OceancdVerificationProviderDatadog(**datadog)
        if isinstance(jenkins, dict):
            jenkins = OceancdVerificationProviderJenkins(**jenkins)
        if isinstance(new_relic, dict):
            new_relic = OceancdVerificationProviderNewRelic(**new_relic)
        if isinstance(prometheus, dict):
            prometheus = OceancdVerificationProviderPrometheus(**prometheus)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4529d5722993e97291f33a093269265a9a17e48ea773571f3f4f5bc087c531bb)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_ids", value=cluster_ids, expected_type=type_hints["cluster_ids"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument cloud_watch", value=cloud_watch, expected_type=type_hints["cloud_watch"])
            check_type(argname="argument datadog", value=datadog, expected_type=type_hints["datadog"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jenkins", value=jenkins, expected_type=type_hints["jenkins"])
            check_type(argname="argument new_relic", value=new_relic, expected_type=type_hints["new_relic"])
            check_type(argname="argument prometheus", value=prometheus, expected_type=type_hints["prometheus"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_ids": cluster_ids,
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
        if cloud_watch is not None:
            self._values["cloud_watch"] = cloud_watch
        if datadog is not None:
            self._values["datadog"] = datadog
        if id is not None:
            self._values["id"] = id
        if jenkins is not None:
            self._values["jenkins"] = jenkins
        if new_relic is not None:
            self._values["new_relic"] = new_relic
        if prometheus is not None:
            self._values["prometheus"] = prometheus

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
    def cluster_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#cluster_ids OceancdVerificationProvider#cluster_ids}.'''
        result = self._values.get("cluster_ids")
        assert result is not None, "Required property 'cluster_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#name OceancdVerificationProvider#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloud_watch(self) -> typing.Optional[OceancdVerificationProviderCloudWatch]:
        '''cloud_watch block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#cloud_watch OceancdVerificationProvider#cloud_watch}
        '''
        result = self._values.get("cloud_watch")
        return typing.cast(typing.Optional[OceancdVerificationProviderCloudWatch], result)

    @builtins.property
    def datadog(self) -> typing.Optional["OceancdVerificationProviderDatadog"]:
        '''datadog block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#datadog OceancdVerificationProvider#datadog}
        '''
        result = self._values.get("datadog")
        return typing.cast(typing.Optional["OceancdVerificationProviderDatadog"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#id OceancdVerificationProvider#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jenkins(self) -> typing.Optional["OceancdVerificationProviderJenkins"]:
        '''jenkins block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#jenkins OceancdVerificationProvider#jenkins}
        '''
        result = self._values.get("jenkins")
        return typing.cast(typing.Optional["OceancdVerificationProviderJenkins"], result)

    @builtins.property
    def new_relic(self) -> typing.Optional["OceancdVerificationProviderNewRelic"]:
        '''new_relic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#new_relic OceancdVerificationProvider#new_relic}
        '''
        result = self._values.get("new_relic")
        return typing.cast(typing.Optional["OceancdVerificationProviderNewRelic"], result)

    @builtins.property
    def prometheus(self) -> typing.Optional["OceancdVerificationProviderPrometheus"]:
        '''prometheus block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#prometheus OceancdVerificationProvider#prometheus}
        '''
        result = self._values.get("prometheus")
        return typing.cast(typing.Optional["OceancdVerificationProviderPrometheus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderDatadog",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "api_key": "apiKey", "app_key": "appKey"},
)
class OceancdVerificationProviderDatadog:
    def __init__(
        self,
        *,
        address: builtins.str,
        api_key: builtins.str,
        app_key: builtins.str,
    ) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#address OceancdVerificationProvider#address}.
        :param api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#api_key OceancdVerificationProvider#api_key}.
        :param app_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#app_key OceancdVerificationProvider#app_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b7ca53e7347a8897b983833dd518a0b0b0fb7543fc1cdcf6bb0a7319e7300a6)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument app_key", value=app_key, expected_type=type_hints["app_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "api_key": api_key,
            "app_key": app_key,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#address OceancdVerificationProvider#address}.'''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#api_key OceancdVerificationProvider#api_key}.'''
        result = self._values.get("api_key")
        assert result is not None, "Required property 'api_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#app_key OceancdVerificationProvider#app_key}.'''
        result = self._values.get("app_key")
        assert result is not None, "Required property 'app_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationProviderDatadog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationProviderDatadogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderDatadogOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6434d04dbd964eaa19985a60e0493722554f7341fc0e93864bee8a567c5e4690)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="appKeyInput")
    def app_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bd9b98918f8c0fb849402838512f95c5cf21f936393751a44195638a46551f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dffb3fbcc567f357867d1fadf128f6c90519999895705dac919292ab78593bbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="appKey")
    def app_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appKey"))

    @app_key.setter
    def app_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb4eb19f766255db1165cb8039f64756b77c9eac28b0722a7a06c70f60b78bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdVerificationProviderDatadog]:
        return typing.cast(typing.Optional[OceancdVerificationProviderDatadog], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationProviderDatadog],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e4da5220b2f73dff536d8d3baf18367a22b6b7d7c19772f227a772fe0451e56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderJenkins",
    jsii_struct_bases=[],
    name_mapping={
        "api_token": "apiToken",
        "base_url": "baseUrl",
        "username": "username",
    },
)
class OceancdVerificationProviderJenkins:
    def __init__(
        self,
        *,
        api_token: builtins.str,
        base_url: builtins.str,
        username: builtins.str,
    ) -> None:
        '''
        :param api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#api_token OceancdVerificationProvider#api_token}.
        :param base_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url OceancdVerificationProvider#base_url}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#username OceancdVerificationProvider#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18324ba38b68915c2a6cacada77d80b357eed24f2e2070ed646048f9fdf1565b)
            check_type(argname="argument api_token", value=api_token, expected_type=type_hints["api_token"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_token": api_token,
            "base_url": base_url,
            "username": username,
        }

    @builtins.property
    def api_token(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#api_token OceancdVerificationProvider#api_token}.'''
        result = self._values.get("api_token")
        assert result is not None, "Required property 'api_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url OceancdVerificationProvider#base_url}.'''
        result = self._values.get("base_url")
        assert result is not None, "Required property 'base_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#username OceancdVerificationProvider#username}.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationProviderJenkins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationProviderJenkinsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderJenkinsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__993200fb8f6f54689bed032f1733ebced6887a8b7cd4fb30b96979c8625f06f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="apiTokenInput")
    def api_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="apiToken")
    def api_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiToken"))

    @api_token.setter
    def api_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13d4437992e3a1e6396e9b7537a0a550d59e1adef2dd833af58a097b5ab198d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22a0db0e66242aa16594fe494526dbba9076eda336ddf7d78c822a669821dfdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__907684a8f1d5ca2b97eed1b9d88753084ed29f0e647f3d3b9743942a2c4f67dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdVerificationProviderJenkins]:
        return typing.cast(typing.Optional[OceancdVerificationProviderJenkins], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationProviderJenkins],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0416d4ad10265456c6c9c8c34292ed6c3a8e8b47a518f767583ade4fb2aea33c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderNewRelic",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "personal_api_key": "personalApiKey",
        "base_url_nerd_graph": "baseUrlNerdGraph",
        "base_url_rest": "baseUrlRest",
        "region": "region",
    },
)
class OceancdVerificationProviderNewRelic:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        personal_api_key: builtins.str,
        base_url_nerd_graph: typing.Optional[builtins.str] = None,
        base_url_rest: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#account_id OceancdVerificationProvider#account_id}.
        :param personal_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#personal_api_key OceancdVerificationProvider#personal_api_key}.
        :param base_url_nerd_graph: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url_nerd_graph OceancdVerificationProvider#base_url_nerd_graph}.
        :param base_url_rest: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url_rest OceancdVerificationProvider#base_url_rest}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#region OceancdVerificationProvider#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efe70f568ec552cd03a2bba90d1d209c6648c6b51c0d4745cebef16fb663029e)
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument personal_api_key", value=personal_api_key, expected_type=type_hints["personal_api_key"])
            check_type(argname="argument base_url_nerd_graph", value=base_url_nerd_graph, expected_type=type_hints["base_url_nerd_graph"])
            check_type(argname="argument base_url_rest", value=base_url_rest, expected_type=type_hints["base_url_rest"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "personal_api_key": personal_api_key,
        }
        if base_url_nerd_graph is not None:
            self._values["base_url_nerd_graph"] = base_url_nerd_graph
        if base_url_rest is not None:
            self._values["base_url_rest"] = base_url_rest
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#account_id OceancdVerificationProvider#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def personal_api_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#personal_api_key OceancdVerificationProvider#personal_api_key}.'''
        result = self._values.get("personal_api_key")
        assert result is not None, "Required property 'personal_api_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base_url_nerd_graph(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url_nerd_graph OceancdVerificationProvider#base_url_nerd_graph}.'''
        result = self._values.get("base_url_nerd_graph")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_url_rest(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#base_url_rest OceancdVerificationProvider#base_url_rest}.'''
        result = self._values.get("base_url_rest")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#region OceancdVerificationProvider#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationProviderNewRelic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationProviderNewRelicOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderNewRelicOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef2211186fde374a4e204c28584a238756552217203dab9135d710f78591f18f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBaseUrlNerdGraph")
    def reset_base_url_nerd_graph(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrlNerdGraph", []))

    @jsii.member(jsii_name="resetBaseUrlRest")
    def reset_base_url_rest(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrlRest", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrlNerdGraphInput")
    def base_url_nerd_graph_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlNerdGraphInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrlRestInput")
    def base_url_rest_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlRestInput"))

    @builtins.property
    @jsii.member(jsii_name="personalApiKeyInput")
    def personal_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "personalApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__742a8ef8a0ff1275e62d0abe0ea1dfe4882238d8728bfcbdb17d6f5a044d5b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrlNerdGraph")
    def base_url_nerd_graph(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrlNerdGraph"))

    @base_url_nerd_graph.setter
    def base_url_nerd_graph(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb2824bf2eb8093963c498b54d719dc9f4f7e0df1e5226daa1023c8b6dff868b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrlNerdGraph", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrlRest")
    def base_url_rest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrlRest"))

    @base_url_rest.setter
    def base_url_rest(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a9a3b7271add122d2d7b91f2d09afcc438e030b513dd16de2e4402d749b2af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrlRest", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="personalApiKey")
    def personal_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "personalApiKey"))

    @personal_api_key.setter
    def personal_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3acaca1febd8da542b9d319360f57782885968540ca988b5b4da95ebbf87df0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "personalApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df49440d34db12ea6729814a2048107dcd299eb219750d098ff897370828fbe3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdVerificationProviderNewRelic]:
        return typing.cast(typing.Optional[OceancdVerificationProviderNewRelic], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationProviderNewRelic],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7a9d62a2782ca37240e0f96a710dc46f59a41d1597cdb3da14e45bb30c409ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderPrometheus",
    jsii_struct_bases=[],
    name_mapping={"address": "address"},
)
class OceancdVerificationProviderPrometheus:
    def __init__(self, *, address: builtins.str) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#address OceancdVerificationProvider#address}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63864e4640534f6c1a9d27eb86d2b1fd7001d8166321ce73ed34e24203efe022)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/oceancd_verification_provider#address OceancdVerificationProvider#address}.'''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OceancdVerificationProviderPrometheus(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OceancdVerificationProviderPrometheusOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.oceancdVerificationProvider.OceancdVerificationProviderPrometheusOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e321045788c24e8287257f8c7128773c4fa4e25cb4309e66be64f827362b7fe6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e9bb6fdd5cb0b1c900f22e0d92821a6523cf575a35916d02e13b9e30e4e4a13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OceancdVerificationProviderPrometheus]:
        return typing.cast(typing.Optional[OceancdVerificationProviderPrometheus], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OceancdVerificationProviderPrometheus],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a817900e96ddf6d96262eda594d0463fd0377636d549dc3f79f468b178a7fd75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OceancdVerificationProvider",
    "OceancdVerificationProviderCloudWatch",
    "OceancdVerificationProviderCloudWatchOutputReference",
    "OceancdVerificationProviderConfig",
    "OceancdVerificationProviderDatadog",
    "OceancdVerificationProviderDatadogOutputReference",
    "OceancdVerificationProviderJenkins",
    "OceancdVerificationProviderJenkinsOutputReference",
    "OceancdVerificationProviderNewRelic",
    "OceancdVerificationProviderNewRelicOutputReference",
    "OceancdVerificationProviderPrometheus",
    "OceancdVerificationProviderPrometheusOutputReference",
]

publication.publish()

def _typecheckingstub__49746daf239d6d0230ff222fa699ae49df2508214e23925927917f9bed42d777(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_ids: typing.Sequence[builtins.str],
    name: builtins.str,
    cloud_watch: typing.Optional[typing.Union[OceancdVerificationProviderCloudWatch, typing.Dict[builtins.str, typing.Any]]] = None,
    datadog: typing.Optional[typing.Union[OceancdVerificationProviderDatadog, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    jenkins: typing.Optional[typing.Union[OceancdVerificationProviderJenkins, typing.Dict[builtins.str, typing.Any]]] = None,
    new_relic: typing.Optional[typing.Union[OceancdVerificationProviderNewRelic, typing.Dict[builtins.str, typing.Any]]] = None,
    prometheus: typing.Optional[typing.Union[OceancdVerificationProviderPrometheus, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__b2abfd72a63d871814fcf1b92872d13f9f3954f40f4ea7034f6bc1d3919daf19(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0fe0ed02502db7f28e9571e3abdba98537020ba378a94d7447b29e27bda635b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1623e60521541aff44c6790bbd3c4846ee2c2dee88a63022a4c3cdaf304bd8f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fea45dcac1514cbbe86ec4e5837dca39b69b8aedcde8113a2bbedffb363a9d4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00a781482e63d346cfbd059fb3f273bedf6b304e461b428425955c6f7c7642f1(
    *,
    iam_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27a059dbf205bdaa7bff7ac24d5337af2247773c326d1556e0d0008832e00c9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0368eb2ffdbc7f917209e4709c96b576bea491baa839b3d359592d628f6e5cb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ae5e5b423fe7063db45ff6f23c55f80c02d5fab6ef0e129567b4c6ad9291fd(
    value: typing.Optional[OceancdVerificationProviderCloudWatch],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4529d5722993e97291f33a093269265a9a17e48ea773571f3f4f5bc087c531bb(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_ids: typing.Sequence[builtins.str],
    name: builtins.str,
    cloud_watch: typing.Optional[typing.Union[OceancdVerificationProviderCloudWatch, typing.Dict[builtins.str, typing.Any]]] = None,
    datadog: typing.Optional[typing.Union[OceancdVerificationProviderDatadog, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    jenkins: typing.Optional[typing.Union[OceancdVerificationProviderJenkins, typing.Dict[builtins.str, typing.Any]]] = None,
    new_relic: typing.Optional[typing.Union[OceancdVerificationProviderNewRelic, typing.Dict[builtins.str, typing.Any]]] = None,
    prometheus: typing.Optional[typing.Union[OceancdVerificationProviderPrometheus, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b7ca53e7347a8897b983833dd518a0b0b0fb7543fc1cdcf6bb0a7319e7300a6(
    *,
    address: builtins.str,
    api_key: builtins.str,
    app_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6434d04dbd964eaa19985a60e0493722554f7341fc0e93864bee8a567c5e4690(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bd9b98918f8c0fb849402838512f95c5cf21f936393751a44195638a46551f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dffb3fbcc567f357867d1fadf128f6c90519999895705dac919292ab78593bbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb4eb19f766255db1165cb8039f64756b77c9eac28b0722a7a06c70f60b78bfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e4da5220b2f73dff536d8d3baf18367a22b6b7d7c19772f227a772fe0451e56(
    value: typing.Optional[OceancdVerificationProviderDatadog],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18324ba38b68915c2a6cacada77d80b357eed24f2e2070ed646048f9fdf1565b(
    *,
    api_token: builtins.str,
    base_url: builtins.str,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__993200fb8f6f54689bed032f1733ebced6887a8b7cd4fb30b96979c8625f06f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13d4437992e3a1e6396e9b7537a0a550d59e1adef2dd833af58a097b5ab198d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22a0db0e66242aa16594fe494526dbba9076eda336ddf7d78c822a669821dfdf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__907684a8f1d5ca2b97eed1b9d88753084ed29f0e647f3d3b9743942a2c4f67dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0416d4ad10265456c6c9c8c34292ed6c3a8e8b47a518f767583ade4fb2aea33c(
    value: typing.Optional[OceancdVerificationProviderJenkins],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efe70f568ec552cd03a2bba90d1d209c6648c6b51c0d4745cebef16fb663029e(
    *,
    account_id: builtins.str,
    personal_api_key: builtins.str,
    base_url_nerd_graph: typing.Optional[builtins.str] = None,
    base_url_rest: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef2211186fde374a4e204c28584a238756552217203dab9135d710f78591f18f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__742a8ef8a0ff1275e62d0abe0ea1dfe4882238d8728bfcbdb17d6f5a044d5b47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb2824bf2eb8093963c498b54d719dc9f4f7e0df1e5226daa1023c8b6dff868b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a9a3b7271add122d2d7b91f2d09afcc438e030b513dd16de2e4402d749b2af8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3acaca1febd8da542b9d319360f57782885968540ca988b5b4da95ebbf87df0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df49440d34db12ea6729814a2048107dcd299eb219750d098ff897370828fbe3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a9d62a2782ca37240e0f96a710dc46f59a41d1597cdb3da14e45bb30c409ae(
    value: typing.Optional[OceancdVerificationProviderNewRelic],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63864e4640534f6c1a9d27eb86d2b1fd7001d8166321ce73ed34e24203efe022(
    *,
    address: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e321045788c24e8287257f8c7128773c4fa4e25cb4309e66be64f827362b7fe6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e9bb6fdd5cb0b1c900f22e0d92821a6523cf575a35916d02e13b9e30e4e4a13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a817900e96ddf6d96262eda594d0463fd0377636d549dc3f79f468b178a7fd75(
    value: typing.Optional[OceancdVerificationProviderPrometheus],
) -> None:
    """Type checking stubs"""
    pass
