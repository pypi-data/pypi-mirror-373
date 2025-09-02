r'''
# CDK For Terraform Resolver

The `CdkTfResolver` is able to resolve any [`TerraformOutput`](https://developer.hashicorp.com/terraform/cdktf/concepts/variables-and-outputs#output-values)
defined by your CDKTF application. In this example, we create an S3 `Bucket` with the CDKTF, and pass its (deploy time generated)
name as an environment variable to a Kubernetes `CronJob` resource.

```python
import * as tf from "cdktf";
import * as aws from "@cdktf/provider-aws";
import * as k8s from 'cdk8s';
import * as kplus from 'cdk8s-plus-26';

import { CdkTfResolver } from '@cdk8s/cdktf-resolver';

const awsApp = new tf.App();
const stack = new tf.TerraformStack(awsApp, 'aws');

const k8sApp = new k8s.App({ resolvers: [new resolver.CdktfResolver({ app: awsApp })] });
const manifest = new k8s.Chart(k8sApp, 'Manifest', { resolver });

const bucket = new aws.s3Bucket.S3Bucket(stack, 'Bucket');
const bucketName = new tf.TerraformOutput(constrcut, 'BucketName', {
  value: bucket.bucket,
});

new kplus.CronJob(manifest, 'CronJob', {
  schedule: k8s.Cron.daily(),
  containers: [{
    image: 'job',
    envVariables: {
      // directly passing the value of the `TerraformOutput` containing
      // the deploy time bucket name
      BUCKET_NAME: kplus.EnvValue.fromValue(bucketName.value),
    }
 }]
});

awsApp.synth();
k8sApp.synth();
```

During cdk8s synthesis, the custom resolver will detect that `bucketName.value` is not a concrete value,
but rather a value of a `TerraformOutput`. It will then perform `cdktf` CLI commands in order to fetch the
actual value from the deployed infrastructure in your account. This means that in order
for `cdk8s synth` to succeed, it must be executed *after* the CDKTF resources have been deployed.
So your deployment workflow should (conceptually) be:

1. `cdktf deploy`
2. `cdk8s synth`

> Note that the `CdkTfResolver` is **only** able to fetch tokens that have a `TerraformOutput` defined for them.

##### Permissions

Since running `cdk8s synth` will now require reading terraform outputs, it must have permissions to do so.
In case a remote state file is used, this means providing a set of credentials for the account that have access
to where the state is stored. This will vary depending on your cloud provider, but in most cases will involve giving
read permissions on a blob storage device (e.g S3 bucket).

Note that the permissions cdk8s require are far more scoped down than those normally required for the
deployment of CDKTF applications. It is therefore recommended to not reuse the same set of credentials,
and instead create a scoped down `ReadOnly` role dedicated for cdk8s resolvers.

Following are the set of commands the resolver will execute:

* [`cdktf output`](https://developer.hashicorp.com/terraform/cdktf/cli-reference/commands#output)

## Cross Repository Workflow

As we've seen, your `cdk8s` application needs access to the objects defined in your cloud application. If both applications
are defined within the same file, this is trivial to achieve. If they are in different files, a simple `import` statement will suffice.
However, what if the applications are managed in two separate repositories? This makes it a little trickier, but still possible.

In this scenario, `cdktf.ts` in the CDKTF application, stored in a dedicated repository.

```python
import * as tf from "cdktf";
import * as aws from "@cdktf/provider-aws";

import { CdkTfResolver } from '@cdk8s/cdktf-resolver';

const awsApp = new tf.App();
const stack = new tf.TerraformStack(awsApp, 'aws');

const bucket = new aws.s3Bucket.S3Bucket(stack, 'Bucket');
const bucketName = new tf.TerraformOutput(constrcut, 'BucketName', {
  value: bucket.bucket,
});

awsApp.synth();
```

In order for the `cdk8s` application to have cross repository access, the CDKTF object instances
that we want to expose need to be available via a package repository. To do this, break up the
CDKTF application into the following files:

`app.ts`

```python
import * as tf from "cdktf";
import * as aws from "@cdktf/provider-aws";

import { CdkTfResolver } from '@cdk8s/cdktf-resolver';

// export the app so we can pass it to the cdk8s resolver
export const awsApp = new tf.App();
const stack = new tf.TerraformStack(awsApp, 'aws');

const bucket = new aws.s3Bucket.S3Bucket(stack, 'Bucket');
// export the thing we want to have available for cdk8s applications
export const bucketName = new tf.TerraformOutput(constrcut, 'BucketName', {
  value: bucket.bucket,
});

// note that we don't call awsApp.synth here
```

`main.ts`

```python
import { awsApp } from './app.ts'

awsApp.synth();
```

Now, publish the `app.ts` file to a package manager, so that your `cdk8s` application can install and import it.
This approach might be somewhat counter intuitive, because normally we only publish classes to the package manager,
not instances. Indeed, these types of applications introduce a new use-case that requires the sharing of instances.
Conceptually, this is no different than writing state<sup>*</sup> to an SSM parameter or an S3 bucket, and it allows us to remain
in the boundaries of our programming language, and the typing guarantees it provides.

> <sup>*</sup> Actually, we are only publishing instructions for fetching state, not the state itself.

Assuming `app.ts` was published as the `my-cdktf-app` package, our `cdk8s` application will now look like so:

```python
import * as k8s from 'cdk8s';
import * as kplus from 'cdk8s-plus-27';

// import the desired instance from the CDKTF app.
import { bucketName, awsApp } from 'my-cdktf-app';

import { CdkTfResolver } from '@cdk8s/cdktf-resolver';

const k8sApp = new k8s.App({ resolvers: [new resolver.CdktfResolver({ app: awsApp })] });
const manifest = new k8s.Chart(k8sApp, 'Manifest');

new kplus.CronJob(manifest, 'CronJob', {
  schedule: k8s.Cron.daily(),
  containers: [{
    image: 'job',
    envVariables: {
      // directly passing the value of the `TerraformOutput` containing
      // the deploy time bucket name
      BUCKET_NAME: kplus.EnvValue.fromValue(bucketName.value),
    }
 }]
});

k8sApp.synth();
```
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

import cdk8s as _cdk8s_d3d9af27
import cdktf as _cdktf_9a9027ec


@jsii.implements(_cdk8s_d3d9af27.IResolver)
class CdktfResolver(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk8s/cdktf-resolver.CdktfResolver",
):
    def __init__(self, *, app: _cdktf_9a9027ec.App) -> None:
        '''
        :param app: The CDKTF App instance in which the outputs are deinfed in.
        '''
        props = CdktfResolverProps(app=app)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="resolve")
    def resolve(self, context: _cdk8s_d3d9af27.ResolutionContext) -> None:
        '''This function is invoked on every property during cdk8s synthesis.

        To replace a value, implementations must invoke ``context.replaceValue``.

        :param context: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed5e4fe407d684d6d09bae5d7f77dcfa3a9d76a13545aaf1dda580bbdfe1f81)
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
        return typing.cast(None, jsii.invoke(self, "resolve", [context]))


@jsii.data_type(
    jsii_type="@cdk8s/cdktf-resolver.CdktfResolverProps",
    jsii_struct_bases=[],
    name_mapping={"app": "app"},
)
class CdktfResolverProps:
    def __init__(self, *, app: _cdktf_9a9027ec.App) -> None:
        '''
        :param app: The CDKTF App instance in which the outputs are deinfed in.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e3c0add3b279e01102c9f26c89245bdfe2e4d7d4a25811b3ffc6b92f2134a52)
            check_type(argname="argument app", value=app, expected_type=type_hints["app"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app": app,
        }

    @builtins.property
    def app(self) -> _cdktf_9a9027ec.App:
        '''The CDKTF App instance in which the outputs are deinfed in.'''
        result = self._values.get("app")
        assert result is not None, "Required property 'app' is missing"
        return typing.cast(_cdktf_9a9027ec.App, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdktfResolverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CdktfResolver",
    "CdktfResolverProps",
]

publication.publish()

def _typecheckingstub__4ed5e4fe407d684d6d09bae5d7f77dcfa3a9d76a13545aaf1dda580bbdfe1f81(
    context: _cdk8s_d3d9af27.ResolutionContext,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e3c0add3b279e01102c9f26c89245bdfe2e4d7d4a25811b3ffc6b92f2134a52(
    *,
    app: _cdktf_9a9027ec.App,
) -> None:
    """Type checking stubs"""
    pass
