r'''
[![NPM version](https://badge.fury.io/js/cdk-budibase.svg)](https://badge.fury.io/js/cdk-budibase)
[![PyPI version](https://badge.fury.io/py/cdk-budibase.svg)](https://badge.fury.io/py/cdk-budibase)
[![release](https://github.com/neilkuan/cdk-budibase/actions/workflows/release.yml/badge.svg)](https://github.com/neilkuan/cdk-budibase/actions/workflows/release.yml)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk-budibase?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-budibase?label=pypi&color=blue)

# Welcome to `cdk-budibase`

> [`BudiBase`](https://github.com/Budibase/budibase)  is open source! is Build apps, forms, and workflows that perfectly fit your business - so you can move forward, faster. Best of all.
> Use AWS CDK to create budibase server.
> data store in efs

* base resource:

  * vpc, ecs cluster, ecs service, efs

> ref: https://medium.com/devops-techable/learn-how-to-use-the-efs-mount-point-in-your-ecs-cluster-running-fargate-with-aws-cdk-e5c9df435c8b

### Architecture

![](./docs/arch.png)

### Deploy cdk-budibase via example [code](./src/integ.api.ts).

![](/docs/cdk-deploy.png)

```bash
# example cdk app diff.
npx aws-cdk@latest diff --app='npx ts-node src/integ.api.ts'

# example cdk app deploy.
npx aws-cdk@latest deploy --app='npx ts-node src/integ.api.ts'

# example cdk app destroy (in case you miss remove efs, you need to remove efs, and log group manually on aws console or via aws cli, sdk etc...).
npx aws-cdk@latest destroy --app='npx ts-node src/integ.api.ts'
```

### Use Constructs Library in CDK APP.

```python
import { BudiBaseBaseResource } from 'cdk-budibase';

const app = new App();
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const stack = new Stack(app, 'MyStack', { env });
new BudiBaseBaseResource(stack, 'BudiBaseBaseResource');
```

### EFS

![](/docs/efs.png)

### BudiBase

![](/docs/admin-sign-up.png)
![](/docs/budibase-console.png)
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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import constructs as _constructs_77d1e7e8


class BudiBaseBaseResource(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-budibase.BudiBaseBaseResource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Optional["IBudiBaseBaseResourceProps"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d745f491f9223437331a699f44afcdd0b4f2abe936dbcdef675d3289ff24e867)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])


@jsii.interface(jsii_type="cdk-budibase.IBudiBaseBaseResourceProps")
class IBudiBaseBaseResourceProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''
        :stability: experimental
        '''
        ...


class _IBudiBaseBaseResourcePropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk-budibase.IBudiBaseBaseResourceProps"

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], jsii.get(self, "vpc"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBudiBaseBaseResourceProps).__jsii_proxy_class__ = lambda : _IBudiBaseBaseResourcePropsProxy


__all__ = [
    "BudiBaseBaseResource",
    "IBudiBaseBaseResourceProps",
]

publication.publish()

def _typecheckingstub__d745f491f9223437331a699f44afcdd0b4f2abe936dbcdef675d3289ff24e867(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Optional[IBudiBaseBaseResourceProps] = None,
) -> None:
    """Type checking stubs"""
    pass
