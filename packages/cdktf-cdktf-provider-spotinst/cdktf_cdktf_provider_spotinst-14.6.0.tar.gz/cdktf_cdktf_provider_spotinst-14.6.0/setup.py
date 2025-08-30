import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdktf-provider-spotinst",
    "version": "14.6.0",
    "description": "Prebuilt spotinst Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-provider-spotinst.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-provider-spotinst.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdktf_provider_spotinst",
        "cdktf_cdktf_provider_spotinst._jsii",
        "cdktf_cdktf_provider_spotinst.account",
        "cdktf_cdktf_provider_spotinst.account_aws",
        "cdktf_cdktf_provider_spotinst.credentials_aws",
        "cdktf_cdktf_provider_spotinst.credentials_azure",
        "cdktf_cdktf_provider_spotinst.credentials_gcp",
        "cdktf_cdktf_provider_spotinst.data_integration",
        "cdktf_cdktf_provider_spotinst.elastigroup_aws",
        "cdktf_cdktf_provider_spotinst.elastigroup_aws_beanstalk",
        "cdktf_cdktf_provider_spotinst.elastigroup_aws_suspension",
        "cdktf_cdktf_provider_spotinst.elastigroup_azure_v3",
        "cdktf_cdktf_provider_spotinst.elastigroup_gcp",
        "cdktf_cdktf_provider_spotinst.elastigroup_gke",
        "cdktf_cdktf_provider_spotinst.health_check",
        "cdktf_cdktf_provider_spotinst.managed_instance_aws",
        "cdktf_cdktf_provider_spotinst.mrscaler_aws",
        "cdktf_cdktf_provider_spotinst.notification_center",
        "cdktf_cdktf_provider_spotinst.ocean_aks_np",
        "cdktf_cdktf_provider_spotinst.ocean_aks_np_virtual_node_group",
        "cdktf_cdktf_provider_spotinst.ocean_aws",
        "cdktf_cdktf_provider_spotinst.ocean_aws_extended_resource_definition",
        "cdktf_cdktf_provider_spotinst.ocean_aws_launch_spec",
        "cdktf_cdktf_provider_spotinst.ocean_ecs",
        "cdktf_cdktf_provider_spotinst.ocean_ecs_launch_spec",
        "cdktf_cdktf_provider_spotinst.ocean_gke_import",
        "cdktf_cdktf_provider_spotinst.ocean_gke_launch_spec",
        "cdktf_cdktf_provider_spotinst.ocean_gke_launch_spec_import",
        "cdktf_cdktf_provider_spotinst.ocean_right_sizing_rule",
        "cdktf_cdktf_provider_spotinst.ocean_spark",
        "cdktf_cdktf_provider_spotinst.ocean_spark_virtual_node_group",
        "cdktf_cdktf_provider_spotinst.oceancd_rollout_spec",
        "cdktf_cdktf_provider_spotinst.oceancd_strategy",
        "cdktf_cdktf_provider_spotinst.oceancd_verification_provider",
        "cdktf_cdktf_provider_spotinst.oceancd_verification_template",
        "cdktf_cdktf_provider_spotinst.organization_policy",
        "cdktf_cdktf_provider_spotinst.organization_programmatic_user",
        "cdktf_cdktf_provider_spotinst.organization_user",
        "cdktf_cdktf_provider_spotinst.organization_user_group",
        "cdktf_cdktf_provider_spotinst.provider",
        "cdktf_cdktf_provider_spotinst.stateful_node_azure",
        "cdktf_cdktf_provider_spotinst.subscription"
    ],
    "package_data": {
        "cdktf_cdktf_provider_spotinst._jsii": [
            "provider-spotinst@14.6.0.jsii.tgz"
        ],
        "cdktf_cdktf_provider_spotinst": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.21.0, <0.22.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
