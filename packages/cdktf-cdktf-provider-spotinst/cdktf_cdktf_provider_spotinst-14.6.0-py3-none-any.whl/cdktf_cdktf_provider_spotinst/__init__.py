r'''
# CDKTF prebuilt bindings for spotinst/spotinst provider version 1.226.0

This repo builds and publishes the [Terraform spotinst provider](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-spotinst](https://www.npmjs.com/package/@cdktf/provider-spotinst).

`npm install @cdktf/provider-spotinst`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-spotinst](https://pypi.org/project/cdktf-cdktf-provider-spotinst).

`pipenv install cdktf-cdktf-provider-spotinst`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Spotinst](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Spotinst).

`dotnet add package HashiCorp.Cdktf.Providers.Spotinst`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-spotinst](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-spotinst).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-spotinst</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-spotinst-go`](https://github.com/cdktf/cdktf-provider-spotinst-go) package.

`go get github.com/cdktf/cdktf-provider-spotinst-go/spotinst/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-spotinst-go/blob/main/spotinst/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-spotinst).

## Versioning

This project is explicitly not tracking the Terraform spotinst provider version 1:1. In fact, it always tracks `latest` of `~> 1.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform spotinst provider](https://registry.terraform.io/providers/spotinst/spotinst/1.226.0)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "account",
    "account_aws",
    "credentials_aws",
    "credentials_azure",
    "credentials_gcp",
    "data_integration",
    "elastigroup_aws",
    "elastigroup_aws_beanstalk",
    "elastigroup_aws_suspension",
    "elastigroup_azure_v3",
    "elastigroup_gcp",
    "elastigroup_gke",
    "health_check",
    "managed_instance_aws",
    "mrscaler_aws",
    "notification_center",
    "ocean_aks_np",
    "ocean_aks_np_virtual_node_group",
    "ocean_aws",
    "ocean_aws_extended_resource_definition",
    "ocean_aws_launch_spec",
    "ocean_ecs",
    "ocean_ecs_launch_spec",
    "ocean_gke_import",
    "ocean_gke_launch_spec",
    "ocean_gke_launch_spec_import",
    "ocean_right_sizing_rule",
    "ocean_spark",
    "ocean_spark_virtual_node_group",
    "oceancd_rollout_spec",
    "oceancd_strategy",
    "oceancd_verification_provider",
    "oceancd_verification_template",
    "organization_policy",
    "organization_programmatic_user",
    "organization_user",
    "organization_user_group",
    "provider",
    "stateful_node_azure",
    "subscription",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import account
from . import account_aws
from . import credentials_aws
from . import credentials_azure
from . import credentials_gcp
from . import data_integration
from . import elastigroup_aws
from . import elastigroup_aws_beanstalk
from . import elastigroup_aws_suspension
from . import elastigroup_azure_v3
from . import elastigroup_gcp
from . import elastigroup_gke
from . import health_check
from . import managed_instance_aws
from . import mrscaler_aws
from . import notification_center
from . import ocean_aks_np
from . import ocean_aks_np_virtual_node_group
from . import ocean_aws
from . import ocean_aws_extended_resource_definition
from . import ocean_aws_launch_spec
from . import ocean_ecs
from . import ocean_ecs_launch_spec
from . import ocean_gke_import
from . import ocean_gke_launch_spec
from . import ocean_gke_launch_spec_import
from . import ocean_right_sizing_rule
from . import ocean_spark
from . import ocean_spark_virtual_node_group
from . import oceancd_rollout_spec
from . import oceancd_strategy
from . import oceancd_verification_provider
from . import oceancd_verification_template
from . import organization_policy
from . import organization_programmatic_user
from . import organization_user
from . import organization_user_group
from . import provider
from . import stateful_node_azure
from . import subscription
