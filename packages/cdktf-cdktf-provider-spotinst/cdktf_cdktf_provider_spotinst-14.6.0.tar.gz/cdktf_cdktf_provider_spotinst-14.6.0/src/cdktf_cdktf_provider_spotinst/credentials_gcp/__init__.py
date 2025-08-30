r'''
# `spotinst_credentials_gcp`

Refer to the Terraform Registry for docs: [`spotinst_credentials_gcp`](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp).
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


class CredentialsGcp(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-spotinst.credentialsGcp.CredentialsGcp",
):
    '''Represents a {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp spotinst_credentials_gcp}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        account_id: builtins.str,
        auth_provider_x509_cert_url: builtins.str,
        auth_uri: builtins.str,
        client_email: builtins.str,
        client_id: builtins.str,
        client_x509_cert_url: builtins.str,
        private_key: builtins.str,
        private_key_id: builtins.str,
        project_id: builtins.str,
        token_uri: builtins.str,
        type: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp spotinst_credentials_gcp} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#account_id CredentialsGcp#account_id}.
        :param auth_provider_x509_cert_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#auth_provider_x509_cert_url CredentialsGcp#auth_provider_x509_cert_url}.
        :param auth_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#auth_uri CredentialsGcp#auth_uri}.
        :param client_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_email CredentialsGcp#client_email}.
        :param client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_id CredentialsGcp#client_id}.
        :param client_x509_cert_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_x509_cert_url CredentialsGcp#client_x509_cert_url}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#private_key CredentialsGcp#private_key}.
        :param private_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#private_key_id CredentialsGcp#private_key_id}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#project_id CredentialsGcp#project_id}.
        :param token_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#token_uri CredentialsGcp#token_uri}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#type CredentialsGcp#type}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#id CredentialsGcp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b8c6dd4d6d043a8358e3954141ff74f90ebf30d59951eba980b922840b9d98c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CredentialsGcpConfig(
            account_id=account_id,
            auth_provider_x509_cert_url=auth_provider_x509_cert_url,
            auth_uri=auth_uri,
            client_email=client_email,
            client_id=client_id,
            client_x509_cert_url=client_x509_cert_url,
            private_key=private_key,
            private_key_id=private_key_id,
            project_id=project_id,
            token_uri=token_uri,
            type=type,
            id=id,
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
        '''Generates CDKTF code for importing a CredentialsGcp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CredentialsGcp to import.
        :param import_from_id: The id of the existing CredentialsGcp that should be imported. Refer to the {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CredentialsGcp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1085f82fb5a993e74c11ea00c1ccf005b0b1bfee7278ec25035bc7d4e017161)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="authProviderX509CertUrlInput")
    def auth_provider_x509_cert_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authProviderX509CertUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="authUriInput")
    def auth_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authUriInput"))

    @builtins.property
    @jsii.member(jsii_name="clientEmailInput")
    def client_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientX509CertUrlInput")
    def client_x509_cert_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientX509CertUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyIdInput")
    def private_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenUriInput")
    def token_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenUriInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc612c2731e67b4afa468489b4f8dc0ddf3eea9168a939bfd93e97ea1a66e88a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authProviderX509CertUrl")
    def auth_provider_x509_cert_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authProviderX509CertUrl"))

    @auth_provider_x509_cert_url.setter
    def auth_provider_x509_cert_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb8c15ceffe653fb8f18f3b6f95a1d21cc4976c2d2f6cc1fd3909f5552220658)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authProviderX509CertUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authUri")
    def auth_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authUri"))

    @auth_uri.setter
    def auth_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__535189ba6e4e4e8d1e931dc931f9c0da06360a3a5166571272a92c4313e0e9c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientEmail")
    def client_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientEmail"))

    @client_email.setter
    def client_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5761e48e759c466a42ba6a6282c5d20f9c585ab87a276237363ab237dbffad14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd392d92eab7bbd358ccbe40a27795660f09ae8cdcfb5b9faa0583310d47e4b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientX509CertUrl")
    def client_x509_cert_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientX509CertUrl"))

    @client_x509_cert_url.setter
    def client_x509_cert_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d9f61858166763bfd2af01a37539558c18982b1bbbae06359563e79b7a80e2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientX509CertUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__069e1288e3eff5b34fdd821a9958f5c4bac161812efe341f357588443c13d73c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6585811aeedd4e06fa262aee107bc7d3e893d0302df18495388040b07b94fae2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyId")
    def private_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyId"))

    @private_key_id.setter
    def private_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7673ca1f512b49c06cf1bc6f44fc94d67b81aea044e08d37a5a4b8f8e14826b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de9a1d128f4749d51fe7aa3e9b9b11c0ab98f26bf642c5edb61427ff2e025e2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenUri")
    def token_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenUri"))

    @token_uri.setter
    def token_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87255d322cb0b0f3bc960977fa9fbf057cd10f2824c16637fd7469dc26892c49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d3ba9dca409f39d6ce636b15ed28702e0fc02476da66309b684c67da7f0b3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-spotinst.credentialsGcp.CredentialsGcpConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "auth_provider_x509_cert_url": "authProviderX509CertUrl",
        "auth_uri": "authUri",
        "client_email": "clientEmail",
        "client_id": "clientId",
        "client_x509_cert_url": "clientX509CertUrl",
        "private_key": "privateKey",
        "private_key_id": "privateKeyId",
        "project_id": "projectId",
        "token_uri": "tokenUri",
        "type": "type",
        "id": "id",
    },
)
class CredentialsGcpConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: builtins.str,
        auth_provider_x509_cert_url: builtins.str,
        auth_uri: builtins.str,
        client_email: builtins.str,
        client_id: builtins.str,
        client_x509_cert_url: builtins.str,
        private_key: builtins.str,
        private_key_id: builtins.str,
        project_id: builtins.str,
        token_uri: builtins.str,
        type: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#account_id CredentialsGcp#account_id}.
        :param auth_provider_x509_cert_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#auth_provider_x509_cert_url CredentialsGcp#auth_provider_x509_cert_url}.
        :param auth_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#auth_uri CredentialsGcp#auth_uri}.
        :param client_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_email CredentialsGcp#client_email}.
        :param client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_id CredentialsGcp#client_id}.
        :param client_x509_cert_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_x509_cert_url CredentialsGcp#client_x509_cert_url}.
        :param private_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#private_key CredentialsGcp#private_key}.
        :param private_key_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#private_key_id CredentialsGcp#private_key_id}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#project_id CredentialsGcp#project_id}.
        :param token_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#token_uri CredentialsGcp#token_uri}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#type CredentialsGcp#type}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#id CredentialsGcp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a52a9a385fcfce80acc7adc13998d9e8c97c8fb5b33015bbf7c7f9e09a5f177e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument auth_provider_x509_cert_url", value=auth_provider_x509_cert_url, expected_type=type_hints["auth_provider_x509_cert_url"])
            check_type(argname="argument auth_uri", value=auth_uri, expected_type=type_hints["auth_uri"])
            check_type(argname="argument client_email", value=client_email, expected_type=type_hints["client_email"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_x509_cert_url", value=client_x509_cert_url, expected_type=type_hints["client_x509_cert_url"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument private_key_id", value=private_key_id, expected_type=type_hints["private_key_id"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument token_uri", value=token_uri, expected_type=type_hints["token_uri"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
            "auth_uri": auth_uri,
            "client_email": client_email,
            "client_id": client_id,
            "client_x509_cert_url": client_x509_cert_url,
            "private_key": private_key,
            "private_key_id": private_key_id,
            "project_id": project_id,
            "token_uri": token_uri,
            "type": type,
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
        if id is not None:
            self._values["id"] = id

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
    def account_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#account_id CredentialsGcp#account_id}.'''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_provider_x509_cert_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#auth_provider_x509_cert_url CredentialsGcp#auth_provider_x509_cert_url}.'''
        result = self._values.get("auth_provider_x509_cert_url")
        assert result is not None, "Required property 'auth_provider_x509_cert_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#auth_uri CredentialsGcp#auth_uri}.'''
        result = self._values.get("auth_uri")
        assert result is not None, "Required property 'auth_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_email CredentialsGcp#client_email}.'''
        result = self._values.get("client_email")
        assert result is not None, "Required property 'client_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_id CredentialsGcp#client_id}.'''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_x509_cert_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#client_x509_cert_url CredentialsGcp#client_x509_cert_url}.'''
        result = self._values.get("client_x509_cert_url")
        assert result is not None, "Required property 'client_x509_cert_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#private_key CredentialsGcp#private_key}.'''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#private_key_id CredentialsGcp#private_key_id}.'''
        result = self._values.get("private_key_id")
        assert result is not None, "Required property 'private_key_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#project_id CredentialsGcp#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def token_uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#token_uri CredentialsGcp#token_uri}.'''
        result = self._values.get("token_uri")
        assert result is not None, "Required property 'token_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#type CredentialsGcp#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs/resources/credentials_gcp#id CredentialsGcp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CredentialsGcpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CredentialsGcp",
    "CredentialsGcpConfig",
]

publication.publish()

def _typecheckingstub__3b8c6dd4d6d043a8358e3954141ff74f90ebf30d59951eba980b922840b9d98c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    account_id: builtins.str,
    auth_provider_x509_cert_url: builtins.str,
    auth_uri: builtins.str,
    client_email: builtins.str,
    client_id: builtins.str,
    client_x509_cert_url: builtins.str,
    private_key: builtins.str,
    private_key_id: builtins.str,
    project_id: builtins.str,
    token_uri: builtins.str,
    type: builtins.str,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__f1085f82fb5a993e74c11ea00c1ccf005b0b1bfee7278ec25035bc7d4e017161(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc612c2731e67b4afa468489b4f8dc0ddf3eea9168a939bfd93e97ea1a66e88a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb8c15ceffe653fb8f18f3b6f95a1d21cc4976c2d2f6cc1fd3909f5552220658(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__535189ba6e4e4e8d1e931dc931f9c0da06360a3a5166571272a92c4313e0e9c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5761e48e759c466a42ba6a6282c5d20f9c585ab87a276237363ab237dbffad14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd392d92eab7bbd358ccbe40a27795660f09ae8cdcfb5b9faa0583310d47e4b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d9f61858166763bfd2af01a37539558c18982b1bbbae06359563e79b7a80e2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069e1288e3eff5b34fdd821a9958f5c4bac161812efe341f357588443c13d73c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6585811aeedd4e06fa262aee107bc7d3e893d0302df18495388040b07b94fae2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7673ca1f512b49c06cf1bc6f44fc94d67b81aea044e08d37a5a4b8f8e14826b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de9a1d128f4749d51fe7aa3e9b9b11c0ab98f26bf642c5edb61427ff2e025e2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87255d322cb0b0f3bc960977fa9fbf057cd10f2824c16637fd7469dc26892c49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d3ba9dca409f39d6ce636b15ed28702e0fc02476da66309b684c67da7f0b3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a52a9a385fcfce80acc7adc13998d9e8c97c8fb5b33015bbf7c7f9e09a5f177e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    auth_provider_x509_cert_url: builtins.str,
    auth_uri: builtins.str,
    client_email: builtins.str,
    client_id: builtins.str,
    client_x509_cert_url: builtins.str,
    private_key: builtins.str,
    private_key_id: builtins.str,
    project_id: builtins.str,
    token_uri: builtins.str,
    type: builtins.str,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
