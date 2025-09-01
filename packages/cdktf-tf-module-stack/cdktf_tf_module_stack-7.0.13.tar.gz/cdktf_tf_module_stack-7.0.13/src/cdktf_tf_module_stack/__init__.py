r'''
# cdktf-tf-module-stack

![Status: Tech Preview](https://img.shields.io/badge/status-experimental-EAAA32) [![Releases](https://img.shields.io/github/release/cdktf/cdktf-tf-module-stack.svg)](https://github.com/cdktf/cdktf-tf-module-stack/releases)
[![LICENSE](https://img.shields.io/github/license/cdktf/cdktf-tf-module-stack.svg)](https://github.com/cdktf/cdktf-tf-module-stack/blob/main/LICENSE)
[![build](https://github.com/cdktf/cdktf-tf-module-stack/actions/workflows/build.yml/badge.svg)](https://github.com/cdktf/cdktf-tf-module-stack/actions/workflows/build.yml)

A drop-in replacement for cdktf.TerraformStack that lets you define Terraform modules as constructs.

*cdktf-tf-module-stack* is in technical preview, which means it's a community supported project. It still requires extensive testing and polishing to mature into a HashiCorp officially supported project. Please [file issues](https://github.com/cdktf/cdktf-tf-module-stack/issues/new/choose) generously and detail your experience while using the library. We welcome your feedback.

By using the software in this repository, you acknowledge that:

* *cdktf-tf-module-stack* is still in development, may change, and has not been released as a commercial product by HashiCorp and is not currently supported in any way by HashiCorp.
* *cdktf-tf-module-stack* is provided on an "as-is" basis, and may include bugs, errors, or other issues.
* *cdktf-tf-module-stack* is NOT INTENDED FOR PRODUCTION USE, use of the Software may result in unexpected results, loss of data, or other unexpected results, and HashiCorp disclaims any and all liability resulting from use of *cdktf-tf-module-stack*.
* HashiCorp reserves all rights to make all decisions about the features, functionality and commercial release (or non-release) of *cdktf-tf-module-stack*, at any time and without any obligation or liability whatsoever.

## Compatibility

* `cdktf` >= 0.21.0
* `constructs` >= 10.4.2

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/tf-module-stack](https://www.npmjs.com/package/@cdktf/tf-module-stack).

`npm install @cdktf/tf-module-stack`

NOTE: Originally, this package was named `cdktf-tf-module-stack`, and the legacy versions (<= 0.2.0) can be found on npm [here](https://www.npmjs.com/package/cdktf-tf-module-stack).

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-tf-module-stack](https://pypi.org/project/cdktf-tf-module-stack).

`pipenv install cdktf-tf-module-stack`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.TfModuleStack](https://www.nuget.org/packages/HashiCorp.Cdktf.TfModuleStack).

`dotnet add package HashiCorp.Cdktf.TfModuleStack`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-tf-module-stack](https://mvnrepository.com/artifact/com.hashicorp/cdktf-tf-module-stack).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-tf-module-stack</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-tf-module-stack-go`](https://github.com/cdktf/cdktf-tf-module-stack-go) package.

`go get github.com/cdktf/cdktf-tf-module-stack-go/tfmodulestack`

## Usage

### Typescript

```python
import { App } from "cdktf";
import {
  TFModuleStack,
  TFModuleVariable,
  TFModuleOutput,
  ProviderRequirement,
} from "@cdktf/tf-module-stack";
import { Resource } from '@cdktf/provider-null/lib/resource';

class MyAwesomeModule extends TFModuleStack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new ProviderRequirement(this, "null", "~> 2.0");
    const resource = new Resource(this, "resource");

    new TFModuleVariable(this, "my_var", {
      type: "string",
      description: "A variable",
      default: "default",
    });

    new TFModuleOutput(this, "my_output", {
      value: resource.id,
    });
  }
}

const app = new App();
new MyAwesomeModule(app, "my-awesome-module");
app.synth();
```

### Python

```python
from constructs import Construct
from cdktf import App, TerraformStack
from imports.null.resource import Resource
from cdktf_tf_module_stack import TFModuleStack, TFModuleVariable, TFModuleOutput, ProviderRequirement


class MyAwesomeModule(TFModuleStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        ProviderRequirement(self, "null", provider_version_constraint="~> 2.0")

        TFModuleVariable(self, "my_var", type="string", description="A variable", default="default")

        resource = Resource(self, "resource")

        TFModuleOutput(self, "my_output", value=resource.id)


app = App()
MyAwesomeModule(app, "my-awesome-module")
app.synth()
```

This will synthesize a Terraform JSON file that looks like this:

```json
{
  "output": {
    "my_output": [
      {
        "value": "${null_resource.resource.id}"
      }
    ]
  },
  "resource": {
    "null_resource": {
      "resource": {}
    }
  },
  "terraform": {
    "required_providers": {
      "null": {
        "source": "null",
        "version": "~> 2.0"
      }
    },
    "variable": {
      "my_var": {
        "default": "default",
        "description": "A variable",
        "type": "string"
      }
    }
  }
}
```

Please note that the provider section is missing, so that the Terraform Workspace using the generated module can be used with any provider matching the version.
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

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class ProviderRequirement(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/tf-module-stack.ProviderRequirement",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        provider_name: builtins.str,
        provider_version_constraint: typing.Optional[builtins.str] = None,
        terraform_provider_source: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param provider_name: -
        :param provider_version_constraint: -
        :param terraform_provider_source: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e172559df3264e94fc792fe49aaa3ac047776e2b77f008751e365feb920e5eb2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument provider_version_constraint", value=provider_version_constraint, expected_type=type_hints["provider_version_constraint"])
            check_type(argname="argument terraform_provider_source", value=terraform_provider_source, expected_type=type_hints["terraform_provider_source"])
        jsii.create(self.__class__, self, [scope, provider_name, provider_version_constraint, terraform_provider_source])


class TFModuleApp(
    _cdktf_9a9027ec.App,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/tf-module-stack.TFModuleApp",
):
    def __init__(
        self,
        *,
        context: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        hcl_output: typing.Optional[builtins.bool] = None,
        outdir: typing.Optional[builtins.str] = None,
        skip_backend_validation: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
        stack_traces: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param context: (experimental) Additional context values for the application. Context set by the CLI or the ``context`` key in ``cdktf.json`` has precedence. Context can be read from any construct using ``node.getContext(key)``. Default: - no additional context
        :param hcl_output: 
        :param outdir: (experimental) The directory to output Terraform resources. If you are using the CDKTF CLI, this value is automatically set from one of the following three sources: - The ``-o`` / ``--output`` CLI option - The ``CDKTF_OUTDIR`` environment variable - The ``outdir`` key in ``cdktf.json`` If you are using the CDKTF CLI and want to set a different value here, you will also need to set the same value via one of the three ways specified above. The most common case to set this value is when you are using the CDKTF library directly (e.g. when writing unit tests). Default: - CDKTF_OUTDIR if defined, otherwise "cdktf.out"
        :param skip_backend_validation: (experimental) Whether to skip backend validation during synthesis of the app. Default: - false
        :param skip_validation: (experimental) Whether to skip all validations during synthesis of the app. Default: - false
        :param stack_traces: 
        '''
        options = _cdktf_9a9027ec.AppConfig(
            context=context,
            hcl_output=hcl_output,
            outdir=outdir,
            skip_backend_validation=skip_backend_validation,
            skip_validation=skip_validation,
            stack_traces=stack_traces,
        )

        jsii.create(self.__class__, self, [options])


class TFModuleOutput(
    _cdktf_9a9027ec.TerraformOutput,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/tf-module-stack.TFModuleOutput",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        name: builtins.str,
        *,
        value: typing.Any,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        description: typing.Optional[builtins.str] = None,
        precondition: typing.Optional[typing.Union[_cdktf_9a9027ec.Precondition, typing.Dict[builtins.str, typing.Any]]] = None,
        sensitive: typing.Optional[builtins.bool] = None,
        static_id: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param value: 
        :param depends_on: 
        :param description: 
        :param precondition: 
        :param sensitive: 
        :param static_id: (experimental) If set to true the synthesized Terraform Output will be named after the ``id`` passed to the constructor instead of the default (TerraformOutput.friendlyUniqueId). Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8ce78db918637259276c624004acb4ab77b97d8c5c822715ab8a887c4fbbfd3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        config = _cdktf_9a9027ec.TerraformOutputConfig(
            value=value,
            depends_on=depends_on,
            description=description,
            precondition=precondition,
            sensitive=sensitive,
            static_id=static_id,
        )

        jsii.create(self.__class__, self, [scope, name, config])

    @jsii.member(jsii_name="toTerraform")
    def to_terraform(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "toTerraform", []))


class TFModuleStack(
    _cdktf_9a9027ec.TerraformStack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/tf-module-stack.TFModuleStack",
):
    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db8110ec567f8a7a5e92c6631584dddce9ca36eb4acfb9bfe3b9b5be7e36d8e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="toTerraform")
    def to_terraform(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "toTerraform", []))


class TFModuleVariable(
    _cdktf_9a9027ec.TerraformVariable,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/tf-module-stack.TFModuleVariable",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        name: builtins.str,
        *,
        default: typing.Any = None,
        description: typing.Optional[builtins.str] = None,
        nullable: typing.Optional[builtins.bool] = None,
        sensitive: typing.Optional[builtins.bool] = None,
        type: typing.Optional[builtins.str] = None,
        validation: typing.Optional[typing.Sequence[typing.Union[_cdktf_9a9027ec.TerraformVariableValidationConfig, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param default: 
        :param description: 
        :param nullable: 
        :param sensitive: 
        :param type: (experimental) The type argument in a variable block allows you to restrict the type of value that will be accepted as the value for a variable. If no type constraint is set then a value of any type is accepted. While type constraints are optional, we recommend specifying them; they serve as easy reminders for users of the module, and allow Terraform to return a helpful error message if the wrong type is used. Type constraints are created from a mixture of type keywords and type constructors. The supported type keywords are: - string - number - bool The type constructors allow you to specify complex types such as collections: - list(<TYPE>) - set(<TYPE>) - map(<TYPE>) - object({<ATTR NAME> = <TYPE>, ... }) - tuple([<TYPE>, ...]) The keyword any may be used to indicate that any type is acceptable. For more information on the meaning and behavior of these different types, as well as detailed information about automatic conversion of complex types, refer to {@link https://developer.hashicorp.com/terraform/language/expressions/type-constraints Type Constraints}. If both the type and default arguments are specified, the given default value must be convertible to the specified type.
        :param validation: (experimental) Specify arbitrary custom validation rules for a particular variable using a validation block nested within the corresponding variable block.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1455bbc0008397773a0e0d63b2d227aa5b0dc3b1898e8d89c766047ee4f9e44)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        config = _cdktf_9a9027ec.TerraformVariableConfig(
            default=default,
            description=description,
            nullable=nullable,
            sensitive=sensitive,
            type=type,
            validation=validation,
        )

        jsii.create(self.__class__, self, [scope, name, config])

    @jsii.member(jsii_name="toTerraform")
    def to_terraform(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "toTerraform", []))


__all__ = [
    "ProviderRequirement",
    "TFModuleApp",
    "TFModuleOutput",
    "TFModuleStack",
    "TFModuleVariable",
]

publication.publish()

def _typecheckingstub__e172559df3264e94fc792fe49aaa3ac047776e2b77f008751e365feb920e5eb2(
    scope: _constructs_77d1e7e8.Construct,
    provider_name: builtins.str,
    provider_version_constraint: typing.Optional[builtins.str] = None,
    terraform_provider_source: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8ce78db918637259276c624004acb4ab77b97d8c5c822715ab8a887c4fbbfd3(
    scope: _constructs_77d1e7e8.Construct,
    name: builtins.str,
    *,
    value: typing.Any,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    description: typing.Optional[builtins.str] = None,
    precondition: typing.Optional[typing.Union[_cdktf_9a9027ec.Precondition, typing.Dict[builtins.str, typing.Any]]] = None,
    sensitive: typing.Optional[builtins.bool] = None,
    static_id: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db8110ec567f8a7a5e92c6631584dddce9ca36eb4acfb9bfe3b9b5be7e36d8e0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1455bbc0008397773a0e0d63b2d227aa5b0dc3b1898e8d89c766047ee4f9e44(
    scope: _constructs_77d1e7e8.Construct,
    name: builtins.str,
    *,
    default: typing.Any = None,
    description: typing.Optional[builtins.str] = None,
    nullable: typing.Optional[builtins.bool] = None,
    sensitive: typing.Optional[builtins.bool] = None,
    type: typing.Optional[builtins.str] = None,
    validation: typing.Optional[typing.Sequence[typing.Union[_cdktf_9a9027ec.TerraformVariableValidationConfig, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
