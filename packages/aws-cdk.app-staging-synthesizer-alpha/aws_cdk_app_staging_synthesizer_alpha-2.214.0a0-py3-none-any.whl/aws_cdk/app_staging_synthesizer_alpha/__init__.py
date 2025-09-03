r'''
# App Staging Synthesizer

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This library includes constructs aimed at replacing the current model of bootstrapping and providing
greater control of the bootstrap experience to the CDK user. The important constructs in this library
are as follows:

* the `IStagingResources` interface: a framework for an app-level bootstrap stack that handles
  file assets and docker assets.
* the `DefaultStagingStack`, which is a works-out-of-the-box implementation of the `IStagingResources`
  interface.
* the `AppStagingSynthesizer`, a new CDK synthesizer that will synthesize CDK applications with
  the staging resources provided.

> As this library is `experimental`, there are features that are not yet implemented. Please look
> at the list of [Known Limitations](#known-limitations) before getting started.

To get started, update your CDK App with a new `defaultStackSynthesizer`:

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",  # put a unique id here
        staging_bucket_encryption=BucketEncryption.S3_MANAGED
    )
)
```

This will introduce a `DefaultStagingStack` in your CDK App and staging assets of your App
will live in the resources from that stack rather than the CDK Bootstrap stack.

If you are migrating from a different version of synthesis your updated CDK App will target
the resources in the `DefaultStagingStack` and no longer be tied to the bootstrapped resources
in your account.

## Bootstrap Model

In our default bootstrapping process, when you run `cdk bootstrap aws://<account>/<region>`, the following
resources are created:

* It creates Roles to assume for cross-account deployments and for Pipeline deployments;
* It creates staging resources: a global S3 bucket and global ECR repository to hold CDK assets;
* It creates Roles to write to the S3 bucket and ECR repository;

Because the bootstrapping resources include regional resources, you need to bootstrap
every region you plan to deploy to individually. All assets of all CDK apps deploying
to that account and region will be written to the single S3 Bucket and ECR repository.

By using the synthesizer in this library, instead of the
`DefaultStackSynthesizer`, a different set of staging resources will be created
for every CDK application, and they will be created automatically as part of a
regular deployment, in a separate Stack that is deployed before your application
Stacks. The staging resources will be one S3 bucket, and *one ECR repository per
image*, and Roles necessary to access those buckets and ECR repositories. The
Roles from the default bootstrap stack are still used (though their use can be
turned off).

This has the following advantages:

* Because staging resources are now application-specific, they can be fully cleaned up when you clean up
  the application.
* Because there is now one ECR repository per image instead of one ECR repository for all images, it is
  possible to effectively use ECR life cycle rules (for example, retain only the most recent 5 images)
  to cut down on storage costs.
* Resources between separate CDK Apps are separated so they can be cleaned up and lifecycle
  controlled individually.
* Because the only shared bootstrapping resources required are Roles, which are global resources,
  you now only need to bootstrap every account in one Region (instead of every Region). This makes it
  easier to do with CloudFormation StackSets.

For the deployment roles, this synthesizer still uses the Roles from the default
bootstrap stack, and nothing else. The staging resources from that bootstrap
stack will be unused. You can customize the template to remove those resources
if you prefer.  In the future, we will provide a bootstrap stack template with
only those Roles, specifically for use with this synthesizer.

## Using the Default Staging Stack per Environment

The most common use case will be to use the built-in default resources. In this scenario, the
synthesizer will create a new Staging Stack in each environment the CDK App is deployed to store
its staging resources. To use this kind of synthesizer, use `AppStagingSynthesizer.defaultResources()`.

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,

        # The following line is optional. By default it is assumed you have bootstrapped in the same
        # region(s) as the stack(s) you are deploying.
        deployment_identities=DeploymentIdentities.default_bootstrap_roles(bootstrap_region="us-east-1")
    )
)
```

Every CDK App that uses the `DefaultStagingStack` must include an `appId`. This should
be an identifier unique to the app and is used to differentiate staging resources associated
with the app.

### Default Staging Stack

The Default Staging Stack includes all the staging resources necessary for CDK Assets. The below example
is of a CDK App using the `AppStagingSynthesizer` and creating a file asset for the Lambda Function
source code. As part of the `DefaultStagingStack`, an S3 bucket and IAM role will be created that will be
used to upload the asset to S3.

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED
    )
)

stack = Stack(app, "my-stack")

lambda_.Function(stack, "lambda",
    code=lambda_.AssetCode.from_asset(path.join(__dirname, "assets")),
    handler="index.handler",
    runtime=lambda_.Runtime.PYTHON_3_9
)

app.synth()
```

### Custom Roles

You can customize some or all of the roles you'd like to use in the synthesizer as well,
if all you need is to supply custom roles (and not change anything else in the `DefaultStagingStack`):

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        deployment_identities=DeploymentIdentities.specify_roles(
            cloud_formation_execution_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Execute"),
            deployment_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Deploy"),
            lookup_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Lookup")
        )
    )
)
```

Or, you can ask to use the CLI credentials that exist at deploy-time.
These credentials must have the ability to perform CloudFormation calls,
lookup resources in your account, and perform CloudFormation deployment.
For a full list of what is necessary, see `LookupRole`, `DeploymentActionRole`,
and `CloudFormationExecutionRole` in the
[bootstrap template](https://github.com/aws/aws-cdk-cli/blob/main/packages/aws-cdk/lib/api/bootstrap/bootstrap-template.yaml).

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        deployment_identities=DeploymentIdentities.cli_credentials()
    )
)
```

The default staging stack will create roles to publish to the S3 bucket and ECR repositories,
assumable by the deployment role. You can also specify an existing IAM role for the
`fileAssetPublishingRole` or `imageAssetPublishingRole`:

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        file_asset_publishing_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/S3Access"),
        image_asset_publishing_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/ECRAccess")
    )
)
```

### Deploy Time S3 Assets

There are two types of assets:

* Assets used only during deployment. These are used to hand off a large piece of data to another
  service, that will make a private copy of that data. After deployment, the asset is only necessary for
  a potential future rollback.
* Assets accessed throughout the running life time of the application.

Examples of assets that are only used at deploy time are CloudFormation Templates and Lambda Code
bundles. Examples of assets accessed throughout the life time of the application are script files
downloaded to run in a CodeBuild Project, or on EC2 instance startup. ECR images are always application
life-time assets. S3 deploy time assets are stored with a `deploy-time/` prefix, and a lifecycle rule will collect them after a configurable number of days.

Lambda assets are by default marked as deploy time assets:

```python
# stack: Stack

lambda_.Function(stack, "lambda",
    code=lambda_.AssetCode.from_asset(path.join(__dirname, "assets")),  # lambda marks deployTime = true
    handler="index.handler",
    runtime=lambda_.Runtime.PYTHON_3_9
)
```

Or, if you want to create your own deploy time asset:

```python
from aws_cdk.aws_s3_assets import Asset

# stack: Stack

asset = Asset(stack, "deploy-time-asset",
    deploy_time=True,
    path=path.join(__dirname, "deploy-time-asset")
)
```

By default, we store deploy time assets for 30 days, but you can change this number by specifying
`deployTimeFileAssetLifetime`. The number you specify here is how long you will be able to roll back
to a previous version of an application just by doing a CloudFormation deployment with the old
template, without rebuilding and republishing assets.

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        deploy_time_file_asset_lifetime=Duration.days(100)
    )
)
```

### Lifecycle Rules on ECR Repositories

By default, we store a maximum of 3 revisions of a particular docker image asset. This allows
for smooth faciliation of rollback scenarios where we may reference previous versions of an
image. When more than 3 revisions of an asset exist in the ECR repository, the oldest one is
purged.

To change the number of revisions stored, use `imageAssetVersionCount`:

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        image_asset_version_count=10
    )
)
```

### Auto Delete Staging Assets on Deletion

By default, the staging resources will be cleaned up on stack deletion. That means that the
S3 Bucket and ECR Repositories are set to `RemovalPolicy.DESTROY` and have `autoDeleteObjects`
or `emptyOnDelete` turned on. This creates custom resources under the hood to facilitate
cleanup. To turn this off, specify `autoDeleteStagingAssets: false`.

```python
from aws_cdk.aws_s3 import BucketEncryption


app = App(
    default_stack_synthesizer=AppStagingSynthesizer.default_resources(
        app_id="my-app-id",
        staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        auto_delete_staging_assets=False
    )
)
```

### Staging Bucket Encryption

You must explicitly specify the encryption type for the staging bucket via the `stagingBucketEncryption` property. In
future versions of this package, the default will be `BucketEncryption.S3_MANAGED`.

In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost
$1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module
we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3
managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required.

If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to
`BucketEncryption.KMS`. If you are creating a new staging bucket, you can set this property to
`BucketEncryption.S3_MANAGED` to avoid the cost of a KMS key.

You can learn more about choosing a bucket encryption type in the
[S3 documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html).

## Using a Custom Staging Stack per Environment

If you want to customize some behavior that is not configurable via properties,
you can implement your own class that implements `IStagingResources`. To get a head start,
you can subclass `DefaultStagingStack`.

```python
class CustomStagingStack(DefaultStagingStack):
    pass
```

Or you can roll your own staging resources from scratch, as long as it implements `IStagingResources`.

```python
@jsii.implements(IStagingResources)
class CustomStagingStack(Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, notificationArns=None, synthesizer=None, terminationProtection=None, analyticsReporting=None, crossRegionReferences=None, permissionsBoundary=None, suppressTemplateIndentation=None, propertyInjectors=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, notificationArns=notificationArns, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting, crossRegionReferences=crossRegionReferences, permissionsBoundary=permissionsBoundary, suppressTemplateIndentation=suppressTemplateIndentation, propertyInjectors=propertyInjectors)

    def add_file(self, *, sourceHash, executable=None, fileName=None, packaging=None, deployTime=None, displayName=None):
        return FileStagingLocation(
            bucket_name="amzn-s3-demo-bucket",
            assume_role_arn="myArn",
            dependency_stack=self
        )

    def add_docker_image(self, *, sourceHash, executable=None, directoryName=None, dockerBuildArgs=None, dockerBuildSecrets=None, dockerBuildSsh=None, dockerBuildTarget=None, dockerFile=None, repositoryName=None, networkMode=None, platform=None, dockerOutputs=None, assetName=None, dockerCacheFrom=None, dockerCacheTo=None, dockerCacheDisabled=None, displayName=None):
        return ImageStagingLocation(
            repo_name="myRepo",
            assume_role_arn="myArn",
            dependency_stack=self
        )
```

Using your custom staging resources means implementing a `CustomFactory` class and calling the
`AppStagingSynthesizer.customFactory()` static method. This has the benefit of providing a
custom Staging Stack that can be created in every environment the CDK App is deployed to.

```python
@jsii.implements(IStagingResourcesFactory)
class CustomFactory:
    def obtain_staging_resources(self, stack, *, environmentString, deployRoleArn=None, qualifier):
        my_app = App.of(stack)

        return CustomStagingStack(my_app, f"CustomStagingStack-{context.environmentString}")

app = App(
    default_stack_synthesizer=AppStagingSynthesizer.custom_factory(
        factory=CustomFactory(),
        once_per_env=True
    )
)
```

## Using an Existing Staging Stack

Use `AppStagingSynthesizer.customResources()` to supply an existing stack as the Staging Stack.
Make sure that the custom stack you provide implements `IStagingResources`.

```python
resource_app = App()
resources = CustomStagingStack(resource_app, "CustomStagingStack")

app = App(
    default_stack_synthesizer=AppStagingSynthesizer.custom_resources(
        resources=resources
    )
)
```

## Known Limitations

Since this module is experimental, there are some known limitations:

* Currently this module does not support CDK Pipelines. You must deploy CDK Apps using this
  synthesizer via `cdk deploy`. Please upvote [this issue](https://github.com/aws/aws-cdk/issues/26118)
  to indicate you want this.
* This synthesizer only needs a bootstrap stack with Roles, without staging resources. We
  haven't written such a bootstrap stack yet; at the moment you can use the existing modern
  bootstrap stack, the staging resources in them will just go unused. You can customize the
  template to remove them if desired.
* Due to limitations on the CloudFormation template size, CDK Applications can have
  at most 20 independent ECR images. Please upvote [this issue](https://github.com/aws/aws-cdk/issues/26119)
  if you need more than this.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ecr as _aws_cdk_aws_ecr_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_ceddda9d.IReusableStackSynthesizer)
class AppStagingSynthesizer(
    _aws_cdk_ceddda9d.StackSynthesizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.AppStagingSynthesizer",
):
    '''(experimental) App Staging Synthesizer.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
        
        # deployment_identities: app_staging_synthesizer_alpha.DeploymentIdentities
        # staging_resources_factory: app_staging_synthesizer_alpha.IStagingResourcesFactory
        
        app_staging_synthesizer = app_staging_synthesizer_alpha.AppStagingSynthesizer.custom_factory(
            factory=staging_resources_factory,
        
            # the properties below are optional
            bootstrap_qualifier="bootstrapQualifier",
            deployment_identities=deployment_identities,
            once_per_env=False
        )
    '''

    @jsii.member(jsii_name="customFactory")
    @builtins.classmethod
    def custom_factory(
        cls,
        *,
        factory: "IStagingResourcesFactory",
        once_per_env: typing.Optional[builtins.bool] = None,
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional["DeploymentIdentities"] = None,
    ) -> "AppStagingSynthesizer":
        '''(experimental) Supply your own stagingStackFactory method for creating an IStagingStack when a stack is bound to the synthesizer.

        By default, ``oncePerEnv = true``, which means that a new instance of the IStagingStack
        will be created in new environments. Set ``oncePerEnv = false`` to turn off that behavior.

        :param factory: (experimental) The factory that will be used to return staging resources for each stack.
        :param once_per_env: (experimental) Reuse the answer from the factory for stacks in the same environment. Default: true
        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles

        :stability: experimental
        '''
        options = CustomFactoryOptions(
            factory=factory,
            once_per_env=once_per_env,
            bootstrap_qualifier=bootstrap_qualifier,
            deployment_identities=deployment_identities,
        )

        return typing.cast("AppStagingSynthesizer", jsii.sinvoke(cls, "customFactory", [options]))

    @jsii.member(jsii_name="customResources")
    @builtins.classmethod
    def custom_resources(
        cls,
        *,
        resources: "IStagingResources",
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional["DeploymentIdentities"] = None,
    ) -> "AppStagingSynthesizer":
        '''(experimental) Use these exact staging resources for every stack that this synthesizer is used for.

        :param resources: (experimental) Use these exact staging resources for every stack that this synthesizer is used for.
        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles

        :stability: experimental
        '''
        options = CustomResourcesOptions(
            resources=resources,
            bootstrap_qualifier=bootstrap_qualifier,
            deployment_identities=deployment_identities,
        )

        return typing.cast("AppStagingSynthesizer", jsii.sinvoke(cls, "customResources", [options]))

    @jsii.member(jsii_name="defaultResources")
    @builtins.classmethod
    def default_resources(
        cls,
        *,
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional["DeploymentIdentities"] = None,
        app_id: builtins.str,
        staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
        deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        file_asset_publishing_role: typing.Optional["BootstrapRole"] = None,
        image_asset_publishing_role: typing.Optional["BootstrapRole"] = None,
        image_asset_version_count: typing.Optional[jsii.Number] = None,
        staging_bucket_name: typing.Optional[builtins.str] = None,
        staging_stack_name_prefix: typing.Optional[builtins.str] = None,
    ) -> "AppStagingSynthesizer":
        '''(experimental) Use the Default Staging Resources, creating a single stack per environment this app is deployed in.

        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles
        :param app_id: (experimental) A unique identifier for the application that the staging stack belongs to. This identifier will be used in the name of staging resources created for this application, and should be unique across CDK apps. The identifier should include lowercase characters and dashes ('-') only and have a maximum of 20 characters.
        :param staging_bucket_encryption: (experimental) Encryption type for staging bucket. In future versions of this package, the default will be BucketEncryption.S3_MANAGED. In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3 managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required. If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.
        :param auto_delete_staging_assets: (experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories. Default: true
        :param deploy_time_file_asset_lifetime: (experimental) The lifetime for deploy time file assets. Assets that are only necessary at deployment time (for instance, CloudFormation templates and Lambda source code bundles) will be automatically deleted after this many days. Assets that may be read from the staging bucket during your application's run time will not be deleted. Set this to the length of time you wish to be able to roll back to previous versions of your application without having to do a new ``cdk synth`` and re-upload of assets. Default: - Duration.days(30)
        :param file_asset_publishing_role: (experimental) Pass in an existing role to be used as the file publishing role. Default: - a new role will be created
        :param image_asset_publishing_role: (experimental) Pass in an existing role to be used as the image publishing role. Default: - a new role will be created
        :param image_asset_version_count: (experimental) The maximum number of image versions to store in a repository. Previous versions of an image can be stored for rollback purposes. Once a repository has more than 3 image versions stored, the oldest version will be discarded. This allows for sensible garbage collection while maintaining a few previous versions for rollback scenarios. Default: - up to 3 versions stored
        :param staging_bucket_name: (experimental) Explicit name for the staging bucket. Default: - a well-known name unique to this app/env.
        :param staging_stack_name_prefix: (experimental) Specify a custom prefix to be used as the staging stack name and construct ID. The prefix will be appended before the appId, which is required to be part of the stack name and construct ID to ensure uniqueness. Default: 'StagingStack'

        :stability: experimental
        '''
        options = DefaultResourcesOptions(
            bootstrap_qualifier=bootstrap_qualifier,
            deployment_identities=deployment_identities,
            app_id=app_id,
            staging_bucket_encryption=staging_bucket_encryption,
            auto_delete_staging_assets=auto_delete_staging_assets,
            deploy_time_file_asset_lifetime=deploy_time_file_asset_lifetime,
            file_asset_publishing_role=file_asset_publishing_role,
            image_asset_publishing_role=image_asset_publishing_role,
            image_asset_version_count=image_asset_version_count,
            staging_bucket_name=staging_bucket_name,
            staging_stack_name_prefix=staging_stack_name_prefix,
        )

        return typing.cast("AppStagingSynthesizer", jsii.sinvoke(cls, "defaultResources", [options]))

    @jsii.member(jsii_name="addDockerImageAsset")
    def add_docker_image_asset(
        self,
        *,
        source_hash: builtins.str,
        asset_name: typing.Optional[builtins.str] = None,
        directory_name: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_ssh: typing.Optional[builtins.str] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_cache_disabled: typing.Optional[builtins.bool] = None,
        docker_cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        docker_cache_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_file: typing.Optional[builtins.str] = None,
        docker_outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_ceddda9d.DockerImageAssetLocation:
        '''(experimental) Implemented for legacy purposes;

        this will never be called.

        :param source_hash: The hash of the contents of the docker build context. This hash is used throughout the system to identify this image and avoid duplicate work in case the source did not change. NOTE: this means that if you wish to update your docker image, you must make a modification to the source (e.g. add some metadata to your Dockerfile).
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param directory_name: The directory where the Dockerfile is stored, must be relative to the cloud assembly root. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param docker_build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build args are passed
        :param docker_build_secrets: Build secrets to pass to the ``docker build`` command. Since Docker build secrets are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build secrets are passed
        :param docker_build_ssh: SSH agent socket or keys to pass to the ``docker buildx`` command. Default: - no ssh arg is passed
        :param docker_build_target: Docker target to build to. Only allowed when ``directoryName`` is specified. Default: - no target
        :param docker_cache_disabled: Disable the cache and pass ``--no-cache`` to the ``docker build`` command. Default: - cache is used
        :param docker_cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from args are passed
        :param docker_cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to args are passed
        :param docker_file: Path to the Dockerfile (relative to the directory). Only allowed when ``directoryName`` is specified. Default: - no file
        :param docker_outputs: Outputs to pass to the ``docker build`` command. Default: - no build args are passed
        :param executable: An external command that will produce the packaged asset. The command should produce the name of a local Docker image on ``stdout``. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param network_mode: Networking mode for the RUN commands during build. *Requires Docker Engine API v1.25+*. Specify this property to build images on a specific networking mode. Default: - no networking mode specified
        :param platform: Platform to build for. *Requires Docker Buildx*. Specify this property to build images on a specific platform. Default: - no platform specified (the current machine architecture will be used)

        :stability: experimental
        '''
        _asset = _aws_cdk_ceddda9d.DockerImageAssetSource(
            source_hash=source_hash,
            asset_name=asset_name,
            directory_name=directory_name,
            display_name=display_name,
            docker_build_args=docker_build_args,
            docker_build_secrets=docker_build_secrets,
            docker_build_ssh=docker_build_ssh,
            docker_build_target=docker_build_target,
            docker_cache_disabled=docker_cache_disabled,
            docker_cache_from=docker_cache_from,
            docker_cache_to=docker_cache_to,
            docker_file=docker_file,
            docker_outputs=docker_outputs,
            executable=executable,
            network_mode=network_mode,
            platform=platform,
        )

        return typing.cast(_aws_cdk_ceddda9d.DockerImageAssetLocation, jsii.invoke(self, "addDockerImageAsset", [_asset]))

    @jsii.member(jsii_name="addFileAsset")
    def add_file_asset(
        self,
        *,
        source_hash: builtins.str,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        file_name: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[_aws_cdk_ceddda9d.FileAssetPackaging] = None,
    ) -> _aws_cdk_ceddda9d.FileAssetLocation:
        '''(experimental) Implemented for legacy purposes;

        this will never be called.

        :param source_hash: A hash on the content source. This hash is used to uniquely identify this asset throughout the system. If this value doesn't change, the asset will not be rebuilt or republished.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param executable: An external command that will produce the packaged asset. The command should produce the location of a ZIP file on ``stdout``. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param file_name: The path, relative to the root of the cloud assembly, in which this asset source resides. This can be a path to a file or a directory, depending on the packaging type. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param packaging: Which type of packaging to perform. Default: - Required if ``fileName`` is specified.

        :stability: experimental
        '''
        _asset = _aws_cdk_ceddda9d.FileAssetSource(
            source_hash=source_hash,
            deploy_time=deploy_time,
            display_name=display_name,
            executable=executable,
            file_name=file_name,
            packaging=packaging,
        )

        return typing.cast(_aws_cdk_ceddda9d.FileAssetLocation, jsii.invoke(self, "addFileAsset", [_asset]))

    @jsii.member(jsii_name="bind")
    def bind(self, _stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(experimental) Implemented for legacy purposes;

        this will never be called.

        :param _stack: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95a4aa84673edcde5f9edcbb6e0abc3d396e902014631ead660cc26b087ff3aa)
            check_type(argname="argument _stack", value=_stack, expected_type=type_hints["_stack"])
        return typing.cast(None, jsii.invoke(self, "bind", [_stack]))

    @jsii.member(jsii_name="reusableBind")
    def reusable_bind(
        self,
        stack: _aws_cdk_ceddda9d.Stack,
    ) -> _aws_cdk_ceddda9d.IBoundStackSynthesizer:
        '''(experimental) Returns a version of the synthesizer bound to a stack.

        :param stack: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__459a43a0e219bcfa7acb8fb227bd72f30f82856a9f03031cf7bdb5fa56b9c968)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(_aws_cdk_ceddda9d.IBoundStackSynthesizer, jsii.invoke(self, "reusableBind", [stack]))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self, _session: _aws_cdk_ceddda9d.ISynthesisSession) -> None:
        '''(experimental) Implemented for legacy purposes;

        this will never be called.

        :param _session: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78deb50795e0693e69c3000edfbc5a762dc7ada84b5c564be0d8625416b06213)
            check_type(argname="argument _session", value=_session, expected_type=type_hints["_session"])
        return typing.cast(None, jsii.invoke(self, "synthesize", [_session]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_CLOUDFORMATION_ROLE_ARN")
    def DEFAULT_CLOUDFORMATION_ROLE_ARN(cls) -> builtins.str:
        '''(experimental) Default CloudFormation role ARN.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_CLOUDFORMATION_ROLE_ARN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_DEPLOY_ROLE_ARN")
    def DEFAULT_DEPLOY_ROLE_ARN(cls) -> builtins.str:
        '''(experimental) Default deploy role ARN.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_DEPLOY_ROLE_ARN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_LOOKUP_ROLE_ARN")
    def DEFAULT_LOOKUP_ROLE_ARN(cls) -> builtins.str:
        '''(experimental) Default lookup role ARN for missing values.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_LOOKUP_ROLE_ARN"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DEFAULT_QUALIFIER")
    def DEFAULT_QUALIFIER(cls) -> builtins.str:
        '''(experimental) Default ARN qualifier.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DEFAULT_QUALIFIER"))


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.AppStagingSynthesizerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "bootstrap_qualifier": "bootstrapQualifier",
        "deployment_identities": "deploymentIdentities",
    },
)
class AppStagingSynthesizerOptions:
    def __init__(
        self,
        *,
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional["DeploymentIdentities"] = None,
    ) -> None:
        '''(experimental) Options that apply to all AppStagingSynthesizer variants.

        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
            
            # deployment_identities: app_staging_synthesizer_alpha.DeploymentIdentities
            
            app_staging_synthesizer_options = app_staging_synthesizer_alpha.AppStagingSynthesizerOptions(
                bootstrap_qualifier="bootstrapQualifier",
                deployment_identities=deployment_identities
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5eda98d3f47545949dd20b5c6d9a83068e0456ecdca7b7dae9779adbe1ac33a)
            check_type(argname="argument bootstrap_qualifier", value=bootstrap_qualifier, expected_type=type_hints["bootstrap_qualifier"])
            check_type(argname="argument deployment_identities", value=deployment_identities, expected_type=type_hints["deployment_identities"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bootstrap_qualifier is not None:
            self._values["bootstrap_qualifier"] = bootstrap_qualifier
        if deployment_identities is not None:
            self._values["deployment_identities"] = deployment_identities

    @builtins.property
    def bootstrap_qualifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account.

        This qualifier is only used to reference bootstrapped resources. It will not
        be used in the creation of app-specific staging resources: ``appId`` is used for that
        instead.

        :default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``

        :stability: experimental
        '''
        result = self._values.get("bootstrap_qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_identities(self) -> typing.Optional["DeploymentIdentities"]:
        '''(experimental) What roles to use to deploy applications.

        These are the roles that have permissions to interact with CloudFormation
        on your behalf. By default these are the standard bootstrapped CDK roles,
        but you can customize them or turn them off and use the CLI credentials
        to deploy.

        :default: - The standard bootstrapped CDK roles

        :stability: experimental
        '''
        result = self._values.get("deployment_identities")
        return typing.cast(typing.Optional["DeploymentIdentities"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppStagingSynthesizerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BootstrapRole(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.BootstrapRole",
):
    '''(experimental) Bootstrapped role specifier.

    These roles must exist already.
    This class does not create new IAM Roles.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_s3 import BucketEncryption
        
        
        app = App(
            default_stack_synthesizer=AppStagingSynthesizer.default_resources(
                app_id="my-app-id",
                staging_bucket_encryption=BucketEncryption.S3_MANAGED,
                deployment_identities=DeploymentIdentities.specify_roles(
                    cloud_formation_execution_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Execute"),
                    deployment_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Deploy"),
                    lookup_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Lookup")
                )
            )
        )
    '''

    @jsii.member(jsii_name="cliCredentials")
    @builtins.classmethod
    def cli_credentials(cls) -> "BootstrapRole":
        '''(experimental) Use the currently assumed role/credentials.

        :stability: experimental
        '''
        return typing.cast("BootstrapRole", jsii.sinvoke(cls, "cliCredentials", []))

    @jsii.member(jsii_name="fromRoleArn")
    @builtins.classmethod
    def from_role_arn(cls, arn: builtins.str) -> "BootstrapRole":
        '''(experimental) Specify an existing IAM Role to assume.

        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cd108fb347d84df5492e4c7eb7ac7b451a8fd974100ef9a599abf606d702a47)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("BootstrapRole", jsii.sinvoke(cls, "fromRoleArn", [arn]))

    @jsii.member(jsii_name="isCliCredentials")
    def is_cli_credentials(self) -> builtins.bool:
        '''(experimental) Whether or not this is object was created using BootstrapRole.cliCredentials().

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "isCliCredentials", []))


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.BootstrapRoles",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_formation_execution_role": "cloudFormationExecutionRole",
        "deployment_role": "deploymentRole",
        "lookup_role": "lookupRole",
    },
)
class BootstrapRoles:
    def __init__(
        self,
        *,
        cloud_formation_execution_role: typing.Optional[BootstrapRole] = None,
        deployment_role: typing.Optional[BootstrapRole] = None,
        lookup_role: typing.Optional[BootstrapRole] = None,
    ) -> None:
        '''(experimental) Roles that are bootstrapped to your account.

        :param cloud_formation_execution_role: (experimental) CloudFormation Execution Role. Default: - use bootstrapped role
        :param deployment_role: (experimental) Deployment Action Role. Default: - use boostrapped role
        :param lookup_role: (experimental) Lookup Role. Default: - use bootstrapped role

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_s3 import BucketEncryption
            
            
            app = App(
                default_stack_synthesizer=AppStagingSynthesizer.default_resources(
                    app_id="my-app-id",
                    staging_bucket_encryption=BucketEncryption.S3_MANAGED,
                    deployment_identities=DeploymentIdentities.specify_roles(
                        cloud_formation_execution_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Execute"),
                        deployment_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Deploy"),
                        lookup_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/Lookup")
                    )
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38d27899a562cc928ca61e855b3c0f897e0453494a65e5c8fbe70ef67074507f)
            check_type(argname="argument cloud_formation_execution_role", value=cloud_formation_execution_role, expected_type=type_hints["cloud_formation_execution_role"])
            check_type(argname="argument deployment_role", value=deployment_role, expected_type=type_hints["deployment_role"])
            check_type(argname="argument lookup_role", value=lookup_role, expected_type=type_hints["lookup_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_formation_execution_role is not None:
            self._values["cloud_formation_execution_role"] = cloud_formation_execution_role
        if deployment_role is not None:
            self._values["deployment_role"] = deployment_role
        if lookup_role is not None:
            self._values["lookup_role"] = lookup_role

    @builtins.property
    def cloud_formation_execution_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) CloudFormation Execution Role.

        :default: - use bootstrapped role

        :stability: experimental
        '''
        result = self._values.get("cloud_formation_execution_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def deployment_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Deployment Action Role.

        :default: - use boostrapped role

        :stability: experimental
        '''
        result = self._values.get("deployment_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def lookup_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Lookup Role.

        :default: - use bootstrapped role

        :stability: experimental
        '''
        result = self._values.get("lookup_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BootstrapRoles(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.CustomFactoryOptions",
    jsii_struct_bases=[AppStagingSynthesizerOptions],
    name_mapping={
        "bootstrap_qualifier": "bootstrapQualifier",
        "deployment_identities": "deploymentIdentities",
        "factory": "factory",
        "once_per_env": "oncePerEnv",
    },
)
class CustomFactoryOptions(AppStagingSynthesizerOptions):
    def __init__(
        self,
        *,
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional["DeploymentIdentities"] = None,
        factory: "IStagingResourcesFactory",
        once_per_env: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for customFactory static method.

        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles
        :param factory: (experimental) The factory that will be used to return staging resources for each stack.
        :param once_per_env: (experimental) Reuse the answer from the factory for stacks in the same environment. Default: true

        :stability: experimental
        :exampleMetadata: fixture=with-custom-staging infused

        Example::

            @jsii.implements(IStagingResourcesFactory)
            class CustomFactory:
                def obtain_staging_resources(self, stack, *, environmentString, deployRoleArn=None, qualifier):
                    my_app = App.of(stack)
            
                    return CustomStagingStack(my_app, f"CustomStagingStack-{context.environmentString}")
            
            app = App(
                default_stack_synthesizer=AppStagingSynthesizer.custom_factory(
                    factory=CustomFactory(),
                    once_per_env=True
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50a2376bb9cd02f3f3f5ad3eaaf334854ec7611a4f38af5e1139b5f5c16b0a34)
            check_type(argname="argument bootstrap_qualifier", value=bootstrap_qualifier, expected_type=type_hints["bootstrap_qualifier"])
            check_type(argname="argument deployment_identities", value=deployment_identities, expected_type=type_hints["deployment_identities"])
            check_type(argname="argument factory", value=factory, expected_type=type_hints["factory"])
            check_type(argname="argument once_per_env", value=once_per_env, expected_type=type_hints["once_per_env"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "factory": factory,
        }
        if bootstrap_qualifier is not None:
            self._values["bootstrap_qualifier"] = bootstrap_qualifier
        if deployment_identities is not None:
            self._values["deployment_identities"] = deployment_identities
        if once_per_env is not None:
            self._values["once_per_env"] = once_per_env

    @builtins.property
    def bootstrap_qualifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account.

        This qualifier is only used to reference bootstrapped resources. It will not
        be used in the creation of app-specific staging resources: ``appId`` is used for that
        instead.

        :default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``

        :stability: experimental
        '''
        result = self._values.get("bootstrap_qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_identities(self) -> typing.Optional["DeploymentIdentities"]:
        '''(experimental) What roles to use to deploy applications.

        These are the roles that have permissions to interact with CloudFormation
        on your behalf. By default these are the standard bootstrapped CDK roles,
        but you can customize them or turn them off and use the CLI credentials
        to deploy.

        :default: - The standard bootstrapped CDK roles

        :stability: experimental
        '''
        result = self._values.get("deployment_identities")
        return typing.cast(typing.Optional["DeploymentIdentities"], result)

    @builtins.property
    def factory(self) -> "IStagingResourcesFactory":
        '''(experimental) The factory that will be used to return staging resources for each stack.

        :stability: experimental
        '''
        result = self._values.get("factory")
        assert result is not None, "Required property 'factory' is missing"
        return typing.cast("IStagingResourcesFactory", result)

    @builtins.property
    def once_per_env(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Reuse the answer from the factory for stacks in the same environment.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("once_per_env")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomFactoryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.CustomResourcesOptions",
    jsii_struct_bases=[AppStagingSynthesizerOptions],
    name_mapping={
        "bootstrap_qualifier": "bootstrapQualifier",
        "deployment_identities": "deploymentIdentities",
        "resources": "resources",
    },
)
class CustomResourcesOptions(AppStagingSynthesizerOptions):
    def __init__(
        self,
        *,
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional["DeploymentIdentities"] = None,
        resources: "IStagingResources",
    ) -> None:
        '''(experimental) Properties for customResources static method.

        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles
        :param resources: (experimental) Use these exact staging resources for every stack that this synthesizer is used for.

        :stability: experimental
        :exampleMetadata: fixture=with-custom-staging infused

        Example::

            resource_app = App()
            resources = CustomStagingStack(resource_app, "CustomStagingStack")
            
            app = App(
                default_stack_synthesizer=AppStagingSynthesizer.custom_resources(
                    resources=resources
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805f0ab344edba46f7346788f4acc732cf8b6652895ea8485d87dfdf693e0541)
            check_type(argname="argument bootstrap_qualifier", value=bootstrap_qualifier, expected_type=type_hints["bootstrap_qualifier"])
            check_type(argname="argument deployment_identities", value=deployment_identities, expected_type=type_hints["deployment_identities"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resources": resources,
        }
        if bootstrap_qualifier is not None:
            self._values["bootstrap_qualifier"] = bootstrap_qualifier
        if deployment_identities is not None:
            self._values["deployment_identities"] = deployment_identities

    @builtins.property
    def bootstrap_qualifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account.

        This qualifier is only used to reference bootstrapped resources. It will not
        be used in the creation of app-specific staging resources: ``appId`` is used for that
        instead.

        :default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``

        :stability: experimental
        '''
        result = self._values.get("bootstrap_qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_identities(self) -> typing.Optional["DeploymentIdentities"]:
        '''(experimental) What roles to use to deploy applications.

        These are the roles that have permissions to interact with CloudFormation
        on your behalf. By default these are the standard bootstrapped CDK roles,
        but you can customize them or turn them off and use the CLI credentials
        to deploy.

        :default: - The standard bootstrapped CDK roles

        :stability: experimental
        '''
        result = self._values.get("deployment_identities")
        return typing.cast(typing.Optional["DeploymentIdentities"], result)

    @builtins.property
    def resources(self) -> "IStagingResources":
        '''(experimental) Use these exact staging resources for every stack that this synthesizer is used for.

        :stability: experimental
        '''
        result = self._values.get("resources")
        assert result is not None, "Required property 'resources' is missing"
        return typing.cast("IStagingResources", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomResourcesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.DefaultBootstrapRolesOptions",
    jsii_struct_bases=[],
    name_mapping={"bootstrap_region": "bootstrapRegion"},
)
class DefaultBootstrapRolesOptions:
    def __init__(
        self,
        *,
        bootstrap_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``DeploymentIdentities.defaultBootstrappedRoles``.

        :param bootstrap_region: (experimental) The region where the default bootstrap roles have been created. By default, the region in which the stack is deployed is used. Default: - the stack's current region

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_s3 import BucketEncryption
            
            
            app = App(
                default_stack_synthesizer=AppStagingSynthesizer.default_resources(
                    app_id="my-app-id",
                    staging_bucket_encryption=BucketEncryption.S3_MANAGED,
            
                    # The following line is optional. By default it is assumed you have bootstrapped in the same
                    # region(s) as the stack(s) you are deploying.
                    deployment_identities=DeploymentIdentities.default_bootstrap_roles(bootstrap_region="us-east-1")
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04df2201aac14a17d1f202664f0ecfab35edb0a3e63061b1cb8c73c369ae2804)
            check_type(argname="argument bootstrap_region", value=bootstrap_region, expected_type=type_hints["bootstrap_region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bootstrap_region is not None:
            self._values["bootstrap_region"] = bootstrap_region

    @builtins.property
    def bootstrap_region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where the default bootstrap roles have been created.

        By default, the region in which the stack is deployed is used.

        :default: - the stack's current region

        :stability: experimental
        '''
        result = self._values.get("bootstrap_region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultBootstrapRolesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.DefaultStagingStackOptions",
    jsii_struct_bases=[],
    name_mapping={
        "app_id": "appId",
        "staging_bucket_encryption": "stagingBucketEncryption",
        "auto_delete_staging_assets": "autoDeleteStagingAssets",
        "deploy_time_file_asset_lifetime": "deployTimeFileAssetLifetime",
        "file_asset_publishing_role": "fileAssetPublishingRole",
        "image_asset_publishing_role": "imageAssetPublishingRole",
        "image_asset_version_count": "imageAssetVersionCount",
        "staging_bucket_name": "stagingBucketName",
        "staging_stack_name_prefix": "stagingStackNamePrefix",
    },
)
class DefaultStagingStackOptions:
    def __init__(
        self,
        *,
        app_id: builtins.str,
        staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
        deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_version_count: typing.Optional[jsii.Number] = None,
        staging_bucket_name: typing.Optional[builtins.str] = None,
        staging_stack_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) User configurable options to the DefaultStagingStack.

        :param app_id: (experimental) A unique identifier for the application that the staging stack belongs to. This identifier will be used in the name of staging resources created for this application, and should be unique across CDK apps. The identifier should include lowercase characters and dashes ('-') only and have a maximum of 20 characters.
        :param staging_bucket_encryption: (experimental) Encryption type for staging bucket. In future versions of this package, the default will be BucketEncryption.S3_MANAGED. In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3 managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required. If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.
        :param auto_delete_staging_assets: (experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories. Default: true
        :param deploy_time_file_asset_lifetime: (experimental) The lifetime for deploy time file assets. Assets that are only necessary at deployment time (for instance, CloudFormation templates and Lambda source code bundles) will be automatically deleted after this many days. Assets that may be read from the staging bucket during your application's run time will not be deleted. Set this to the length of time you wish to be able to roll back to previous versions of your application without having to do a new ``cdk synth`` and re-upload of assets. Default: - Duration.days(30)
        :param file_asset_publishing_role: (experimental) Pass in an existing role to be used as the file publishing role. Default: - a new role will be created
        :param image_asset_publishing_role: (experimental) Pass in an existing role to be used as the image publishing role. Default: - a new role will be created
        :param image_asset_version_count: (experimental) The maximum number of image versions to store in a repository. Previous versions of an image can be stored for rollback purposes. Once a repository has more than 3 image versions stored, the oldest version will be discarded. This allows for sensible garbage collection while maintaining a few previous versions for rollback scenarios. Default: - up to 3 versions stored
        :param staging_bucket_name: (experimental) Explicit name for the staging bucket. Default: - a well-known name unique to this app/env.
        :param staging_stack_name_prefix: (experimental) Specify a custom prefix to be used as the staging stack name and construct ID. The prefix will be appended before the appId, which is required to be part of the stack name and construct ID to ensure uniqueness. Default: 'StagingStack'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_s3 import BucketEncryption
            
            default_staging_stack = DefaultStagingStack.factory(app_id="my-app-id", staging_bucket_encryption=BucketEncryption.S3_MANAGED)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09dbc6ce5bcfd58fa48337caac574e10727d4bf9a43dc89866fbe7541b026219)
            check_type(argname="argument app_id", value=app_id, expected_type=type_hints["app_id"])
            check_type(argname="argument staging_bucket_encryption", value=staging_bucket_encryption, expected_type=type_hints["staging_bucket_encryption"])
            check_type(argname="argument auto_delete_staging_assets", value=auto_delete_staging_assets, expected_type=type_hints["auto_delete_staging_assets"])
            check_type(argname="argument deploy_time_file_asset_lifetime", value=deploy_time_file_asset_lifetime, expected_type=type_hints["deploy_time_file_asset_lifetime"])
            check_type(argname="argument file_asset_publishing_role", value=file_asset_publishing_role, expected_type=type_hints["file_asset_publishing_role"])
            check_type(argname="argument image_asset_publishing_role", value=image_asset_publishing_role, expected_type=type_hints["image_asset_publishing_role"])
            check_type(argname="argument image_asset_version_count", value=image_asset_version_count, expected_type=type_hints["image_asset_version_count"])
            check_type(argname="argument staging_bucket_name", value=staging_bucket_name, expected_type=type_hints["staging_bucket_name"])
            check_type(argname="argument staging_stack_name_prefix", value=staging_stack_name_prefix, expected_type=type_hints["staging_stack_name_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_id": app_id,
            "staging_bucket_encryption": staging_bucket_encryption,
        }
        if auto_delete_staging_assets is not None:
            self._values["auto_delete_staging_assets"] = auto_delete_staging_assets
        if deploy_time_file_asset_lifetime is not None:
            self._values["deploy_time_file_asset_lifetime"] = deploy_time_file_asset_lifetime
        if file_asset_publishing_role is not None:
            self._values["file_asset_publishing_role"] = file_asset_publishing_role
        if image_asset_publishing_role is not None:
            self._values["image_asset_publishing_role"] = image_asset_publishing_role
        if image_asset_version_count is not None:
            self._values["image_asset_version_count"] = image_asset_version_count
        if staging_bucket_name is not None:
            self._values["staging_bucket_name"] = staging_bucket_name
        if staging_stack_name_prefix is not None:
            self._values["staging_stack_name_prefix"] = staging_stack_name_prefix

    @builtins.property
    def app_id(self) -> builtins.str:
        '''(experimental) A unique identifier for the application that the staging stack belongs to.

        This identifier will be used in the name of staging resources
        created for this application, and should be unique across CDK apps.

        The identifier should include lowercase characters and dashes ('-') only
        and have a maximum of 20 characters.

        :stability: experimental
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def staging_bucket_encryption(self) -> _aws_cdk_aws_s3_ceddda9d.BucketEncryption:
        '''(experimental) Encryption type for staging bucket.

        In future versions of this package, the default will be BucketEncryption.S3_MANAGED.

        In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost
        $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module
        we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3
        managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required.

        If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to
        BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to
        BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.

        :stability: experimental
        '''
        result = self._values.get("staging_bucket_encryption")
        assert result is not None, "Required property 'staging_bucket_encryption' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.BucketEncryption, result)

    @builtins.property
    def auto_delete_staging_assets(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_delete_staging_assets")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_time_file_asset_lifetime(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The lifetime for deploy time file assets.

        Assets that are only necessary at deployment time (for instance,
        CloudFormation templates and Lambda source code bundles) will be
        automatically deleted after this many days. Assets that may be
        read from the staging bucket during your application's run time
        will not be deleted.

        Set this to the length of time you wish to be able to roll back to
        previous versions of your application without having to do a new
        ``cdk synth`` and re-upload of assets.

        :default: - Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("deploy_time_file_asset_lifetime")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def file_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Pass in an existing role to be used as the file publishing role.

        :default: - a new role will be created

        :stability: experimental
        '''
        result = self._values.get("file_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def image_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Pass in an existing role to be used as the image publishing role.

        :default: - a new role will be created

        :stability: experimental
        '''
        result = self._values.get("image_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def image_asset_version_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of image versions to store in a repository.

        Previous versions of an image can be stored for rollback purposes.
        Once a repository has more than 3 image versions stored, the oldest
        version will be discarded. This allows for sensible garbage collection
        while maintaining a few previous versions for rollback scenarios.

        :default: - up to 3 versions stored

        :stability: experimental
        '''
        result = self._values.get("image_asset_version_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def staging_bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Explicit name for the staging bucket.

        :default: - a well-known name unique to this app/env.

        :stability: experimental
        '''
        result = self._values.get("staging_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def staging_stack_name_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specify a custom prefix to be used as the staging stack name and construct ID.

        The prefix will be appended before the appId, which
        is required to be part of the stack name and construct ID to
        ensure uniqueness.

        :default: 'StagingStack'

        :stability: experimental
        '''
        result = self._values.get("staging_stack_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultStagingStackOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.DefaultStagingStackProps",
    jsii_struct_bases=[DefaultStagingStackOptions, _aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "app_id": "appId",
        "staging_bucket_encryption": "stagingBucketEncryption",
        "auto_delete_staging_assets": "autoDeleteStagingAssets",
        "deploy_time_file_asset_lifetime": "deployTimeFileAssetLifetime",
        "file_asset_publishing_role": "fileAssetPublishingRole",
        "image_asset_publishing_role": "imageAssetPublishingRole",
        "image_asset_version_count": "imageAssetVersionCount",
        "staging_bucket_name": "stagingBucketName",
        "staging_stack_name_prefix": "stagingStackNamePrefix",
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "property_injectors": "propertyInjectors",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "qualifier": "qualifier",
        "deploy_role_arn": "deployRoleArn",
    },
)
class DefaultStagingStackProps(
    DefaultStagingStackOptions,
    _aws_cdk_ceddda9d.StackProps,
):
    def __init__(
        self,
        *,
        app_id: builtins.str,
        staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
        deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_version_count: typing.Optional[jsii.Number] = None,
        staging_bucket_name: typing.Optional[builtins.str] = None,
        staging_stack_name_prefix: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        qualifier: builtins.str,
        deploy_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Default Staging Stack Properties.

        :param app_id: (experimental) A unique identifier for the application that the staging stack belongs to. This identifier will be used in the name of staging resources created for this application, and should be unique across CDK apps. The identifier should include lowercase characters and dashes ('-') only and have a maximum of 20 characters.
        :param staging_bucket_encryption: (experimental) Encryption type for staging bucket. In future versions of this package, the default will be BucketEncryption.S3_MANAGED. In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3 managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required. If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.
        :param auto_delete_staging_assets: (experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories. Default: true
        :param deploy_time_file_asset_lifetime: (experimental) The lifetime for deploy time file assets. Assets that are only necessary at deployment time (for instance, CloudFormation templates and Lambda source code bundles) will be automatically deleted after this many days. Assets that may be read from the staging bucket during your application's run time will not be deleted. Set this to the length of time you wish to be able to roll back to previous versions of your application without having to do a new ``cdk synth`` and re-upload of assets. Default: - Duration.days(30)
        :param file_asset_publishing_role: (experimental) Pass in an existing role to be used as the file publishing role. Default: - a new role will be created
        :param image_asset_publishing_role: (experimental) Pass in an existing role to be used as the image publishing role. Default: - a new role will be created
        :param image_asset_version_count: (experimental) The maximum number of image versions to store in a repository. Previous versions of an image can be stored for rollback purposes. Once a repository has more than 3 image versions stored, the oldest version will be discarded. This allows for sensible garbage collection while maintaining a few previous versions for rollback scenarios. Default: - up to 3 versions stored
        :param staging_bucket_name: (experimental) Explicit name for the staging bucket. Default: - a well-known name unique to this app/env.
        :param staging_stack_name_prefix: (experimental) Specify a custom prefix to be used as the staging stack name and construct ID. The prefix will be appended before the appId, which is required to be part of the stack name and construct ID to ensure uniqueness. Default: 'StagingStack'
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param property_injectors: A list of IPropertyInjector attached to this Stack. Default: - no PropertyInjectors
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Tags that will be applied to the Stack. These tags are applied to the CloudFormation Stack itself. They will not appear in the CloudFormation template. However, at deployment time, CloudFormation will apply these tags to all resources in the stack that support tagging. You will not be able to exempt resources from tagging (using the ``excludeResourceTypes`` property of ``Tags.of(...).add()``) for tags applied in this way. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param qualifier: (experimental) The qualifier used to specialize strings. Can be used to specify custom bootstrapped role names
        :param deploy_role_arn: (experimental) The ARN of the deploy action role, if given. This role will need permissions to read from to the staging resources. Default: - The CLI credentials are assumed, no additional permissions are granted.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_s3 as s3
            
            # bootstrap_role: app_staging_synthesizer_alpha.BootstrapRole
            # permissions_boundary: cdk.PermissionsBoundary
            # property_injector: cdk.IPropertyInjector
            # stack_synthesizer: cdk.StackSynthesizer
            
            default_staging_stack_props = app_staging_synthesizer_alpha.DefaultStagingStackProps(
                app_id="appId",
                qualifier="qualifier",
                staging_bucket_encryption=s3.BucketEncryption.UNENCRYPTED,
            
                # the properties below are optional
                analytics_reporting=False,
                auto_delete_staging_assets=False,
                cross_region_references=False,
                deploy_role_arn="deployRoleArn",
                deploy_time_file_asset_lifetime=cdk.Duration.minutes(30),
                description="description",
                env=cdk.Environment(
                    account="account",
                    region="region"
                ),
                file_asset_publishing_role=bootstrap_role,
                image_asset_publishing_role=bootstrap_role,
                image_asset_version_count=123,
                notification_arns=["notificationArns"],
                permissions_boundary=permissions_boundary,
                property_injectors=[property_injector],
                stack_name="stackName",
                staging_bucket_name="stagingBucketName",
                staging_stack_name_prefix="stagingStackNamePrefix",
                suppress_template_indentation=False,
                synthesizer=stack_synthesizer,
                tags={
                    "tags_key": "tags"
                },
                termination_protection=False
            )
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac9f132bcac8375ac08c16bf3c9bb7407b641e71cfd23cea8b50befa3cf79bbf)
            check_type(argname="argument app_id", value=app_id, expected_type=type_hints["app_id"])
            check_type(argname="argument staging_bucket_encryption", value=staging_bucket_encryption, expected_type=type_hints["staging_bucket_encryption"])
            check_type(argname="argument auto_delete_staging_assets", value=auto_delete_staging_assets, expected_type=type_hints["auto_delete_staging_assets"])
            check_type(argname="argument deploy_time_file_asset_lifetime", value=deploy_time_file_asset_lifetime, expected_type=type_hints["deploy_time_file_asset_lifetime"])
            check_type(argname="argument file_asset_publishing_role", value=file_asset_publishing_role, expected_type=type_hints["file_asset_publishing_role"])
            check_type(argname="argument image_asset_publishing_role", value=image_asset_publishing_role, expected_type=type_hints["image_asset_publishing_role"])
            check_type(argname="argument image_asset_version_count", value=image_asset_version_count, expected_type=type_hints["image_asset_version_count"])
            check_type(argname="argument staging_bucket_name", value=staging_bucket_name, expected_type=type_hints["staging_bucket_name"])
            check_type(argname="argument staging_stack_name_prefix", value=staging_stack_name_prefix, expected_type=type_hints["staging_stack_name_prefix"])
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument property_injectors", value=property_injectors, expected_type=type_hints["property_injectors"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument qualifier", value=qualifier, expected_type=type_hints["qualifier"])
            check_type(argname="argument deploy_role_arn", value=deploy_role_arn, expected_type=type_hints["deploy_role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_id": app_id,
            "staging_bucket_encryption": staging_bucket_encryption,
            "qualifier": qualifier,
        }
        if auto_delete_staging_assets is not None:
            self._values["auto_delete_staging_assets"] = auto_delete_staging_assets
        if deploy_time_file_asset_lifetime is not None:
            self._values["deploy_time_file_asset_lifetime"] = deploy_time_file_asset_lifetime
        if file_asset_publishing_role is not None:
            self._values["file_asset_publishing_role"] = file_asset_publishing_role
        if image_asset_publishing_role is not None:
            self._values["image_asset_publishing_role"] = image_asset_publishing_role
        if image_asset_version_count is not None:
            self._values["image_asset_version_count"] = image_asset_version_count
        if staging_bucket_name is not None:
            self._values["staging_bucket_name"] = staging_bucket_name
        if staging_stack_name_prefix is not None:
            self._values["staging_stack_name_prefix"] = staging_stack_name_prefix
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if property_injectors is not None:
            self._values["property_injectors"] = property_injectors
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if deploy_role_arn is not None:
            self._values["deploy_role_arn"] = deploy_role_arn

    @builtins.property
    def app_id(self) -> builtins.str:
        '''(experimental) A unique identifier for the application that the staging stack belongs to.

        This identifier will be used in the name of staging resources
        created for this application, and should be unique across CDK apps.

        The identifier should include lowercase characters and dashes ('-') only
        and have a maximum of 20 characters.

        :stability: experimental
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def staging_bucket_encryption(self) -> _aws_cdk_aws_s3_ceddda9d.BucketEncryption:
        '''(experimental) Encryption type for staging bucket.

        In future versions of this package, the default will be BucketEncryption.S3_MANAGED.

        In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost
        $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module
        we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3
        managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required.

        If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to
        BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to
        BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.

        :stability: experimental
        '''
        result = self._values.get("staging_bucket_encryption")
        assert result is not None, "Required property 'staging_bucket_encryption' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.BucketEncryption, result)

    @builtins.property
    def auto_delete_staging_assets(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_delete_staging_assets")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_time_file_asset_lifetime(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The lifetime for deploy time file assets.

        Assets that are only necessary at deployment time (for instance,
        CloudFormation templates and Lambda source code bundles) will be
        automatically deleted after this many days. Assets that may be
        read from the staging bucket during your application's run time
        will not be deleted.

        Set this to the length of time you wish to be able to roll back to
        previous versions of your application without having to do a new
        ``cdk synth`` and re-upload of assets.

        :default: - Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("deploy_time_file_asset_lifetime")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def file_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Pass in an existing role to be used as the file publishing role.

        :default: - a new role will be created

        :stability: experimental
        '''
        result = self._values.get("file_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def image_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Pass in an existing role to be used as the image publishing role.

        :default: - a new role will be created

        :stability: experimental
        '''
        result = self._values.get("image_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def image_asset_version_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of image versions to store in a repository.

        Previous versions of an image can be stored for rollback purposes.
        Once a repository has more than 3 image versions stored, the oldest
        version will be discarded. This allows for sensible garbage collection
        while maintaining a few previous versions for rollback scenarios.

        :default: - up to 3 versions stored

        :stability: experimental
        '''
        result = self._values.get("image_asset_version_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def staging_bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Explicit name for the staging bucket.

        :default: - a well-known name unique to this app/env.

        :stability: experimental
        '''
        result = self._values.get("staging_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def staging_stack_name_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specify a custom prefix to be used as the staging stack name and construct ID.

        The prefix will be appended before the appId, which
        is required to be part of the stack name and construct ID to
        ensure uniqueness.

        :default: 'StagingStack'

        :stability: experimental
        '''
        result = self._values.get("staging_stack_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            # Use a concrete account and region to deploy this stack to:
            # `.account` and `.region` will simply return these values.
            Stack(app, "Stack1",
                env=Environment(
                    account="123456789012",
                    region="us-east-1"
                )
            )
            
            # Use the CLI's current credentials to determine the target environment:
            # `.account` and `.region` will reflect the account+region the CLI
            # is configured to use (based on the user CLI credentials)
            Stack(app, "Stack2",
                env=Environment(
                    account=process.env.CDK_DEFAULT_ACCOUNT,
                    region=process.env.CDK_DEFAULT_REGION
                )
            )
            
            # Define multiple stacks stage associated with an environment
            my_stage = Stage(app, "MyStage",
                env=Environment(
                    account="123456789012",
                    region="us-east-1"
                )
            )
            
            # both of these stacks will use the stage's account/region:
            # `.account` and `.region` will resolve to the concrete values as above
            MyStack(my_stage, "Stack1")
            YourStack(my_stage, "Stack2")
            
            # Define an environment-agnostic stack:
            # `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            # which will only resolve to actual values by CloudFormation during deployment.
            MyStack(app, "Stack1")
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notfication arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def property_injectors(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPropertyInjector]]:
        '''A list of IPropertyInjector attached to this Stack.

        :default: - no PropertyInjectors
        '''
        result = self._values.get("property_injectors")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPropertyInjector]], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Tags that will be applied to the Stack.

        These tags are applied to the CloudFormation Stack itself. They will not
        appear in the CloudFormation template.

        However, at deployment time, CloudFormation will apply these tags to all
        resources in the stack that support tagging. You will not be able to exempt
        resources from tagging (using the ``excludeResourceTypes`` property of
        ``Tags.of(...).add()``) for tags applied in this way.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def qualifier(self) -> builtins.str:
        '''(experimental) The qualifier used to specialize strings.

        Can be used to specify custom bootstrapped role names

        :stability: experimental
        '''
        result = self._values.get("qualifier")
        assert result is not None, "Required property 'qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deploy_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the deploy action role, if given.

        This role will need permissions to read from to the staging resources.

        :default: - The CLI credentials are assumed, no additional permissions are granted.

        :stability: experimental
        '''
        result = self._values.get("deploy_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultStagingStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DeploymentIdentities(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.DeploymentIdentities",
):
    '''(experimental) Deployment identities are the class of roles to be assumed by the CDK when deploying the App.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from aws_cdk.aws_s3 import BucketEncryption
        
        
        app = App(
            default_stack_synthesizer=AppStagingSynthesizer.default_resources(
                app_id="my-app-id",
                staging_bucket_encryption=BucketEncryption.S3_MANAGED,
        
                # The following line is optional. By default it is assumed you have bootstrapped in the same
                # region(s) as the stack(s) you are deploying.
                deployment_identities=DeploymentIdentities.default_bootstrap_roles(bootstrap_region="us-east-1")
            )
        )
    '''

    @jsii.member(jsii_name="cliCredentials")
    @builtins.classmethod
    def cli_credentials(cls) -> "DeploymentIdentities":
        '''(experimental) Use CLI credentials for all deployment identities.

        :stability: experimental
        '''
        return typing.cast("DeploymentIdentities", jsii.sinvoke(cls, "cliCredentials", []))

    @jsii.member(jsii_name="defaultBootstrapRoles")
    @builtins.classmethod
    def default_bootstrap_roles(
        cls,
        *,
        bootstrap_region: typing.Optional[builtins.str] = None,
    ) -> "DeploymentIdentities":
        '''(experimental) Use the Roles that have been created by the default bootstrap stack.

        :param bootstrap_region: (experimental) The region where the default bootstrap roles have been created. By default, the region in which the stack is deployed is used. Default: - the stack's current region

        :stability: experimental
        '''
        options = DefaultBootstrapRolesOptions(bootstrap_region=bootstrap_region)

        return typing.cast("DeploymentIdentities", jsii.sinvoke(cls, "defaultBootstrapRoles", [options]))

    @jsii.member(jsii_name="specifyRoles")
    @builtins.classmethod
    def specify_roles(
        cls,
        *,
        cloud_formation_execution_role: typing.Optional[BootstrapRole] = None,
        deployment_role: typing.Optional[BootstrapRole] = None,
        lookup_role: typing.Optional[BootstrapRole] = None,
    ) -> "DeploymentIdentities":
        '''(experimental) Specify your own roles for all deployment identities.

        These roles
        must already exist.

        :param cloud_formation_execution_role: (experimental) CloudFormation Execution Role. Default: - use bootstrapped role
        :param deployment_role: (experimental) Deployment Action Role. Default: - use boostrapped role
        :param lookup_role: (experimental) Lookup Role. Default: - use bootstrapped role

        :stability: experimental
        '''
        roles = BootstrapRoles(
            cloud_formation_execution_role=cloud_formation_execution_role,
            deployment_role=deployment_role,
            lookup_role=lookup_role,
        )

        return typing.cast("DeploymentIdentities", jsii.sinvoke(cls, "specifyRoles", [roles]))

    @builtins.property
    @jsii.member(jsii_name="cloudFormationExecutionRole")
    def cloud_formation_execution_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) CloudFormation Execution Role.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[BootstrapRole], jsii.get(self, "cloudFormationExecutionRole"))

    @builtins.property
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Deployment Action Role.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[BootstrapRole], jsii.get(self, "deploymentRole"))

    @builtins.property
    @jsii.member(jsii_name="lookupRole")
    def lookup_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Lookup Role.

        :default: - use bootstrapped role

        :stability: experimental
        '''
        return typing.cast(typing.Optional[BootstrapRole], jsii.get(self, "lookupRole"))


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.FileStagingLocation",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "assume_role_arn": "assumeRoleArn",
        "dependency_stack": "dependencyStack",
        "prefix": "prefix",
    },
)
class FileStagingLocation:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        assume_role_arn: typing.Optional[builtins.str] = None,
        dependency_stack: typing.Optional[_aws_cdk_ceddda9d.Stack] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Information returned by the Staging Stack for each file asset.

        :param bucket_name: (experimental) The name of the staging bucket.
        :param assume_role_arn: (experimental) The ARN to assume to write files to this bucket. Default: - Don't assume a role
        :param dependency_stack: (experimental) The stack that creates this bucket (leads to dependencies on it). Default: - Don't add dependencies
        :param prefix: (experimental) A prefix to add to the keys. Default: ''

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
            import aws_cdk as cdk
            
            # stack: cdk.Stack
            
            file_staging_location = app_staging_synthesizer_alpha.FileStagingLocation(
                bucket_name="bucketName",
            
                # the properties below are optional
                assume_role_arn="assumeRoleArn",
                dependency_stack=stack,
                prefix="prefix"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c00dd9c0937fe689685a2606ff5beb696deda888ebdd50fae7f6bbfaa8764eda)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument assume_role_arn", value=assume_role_arn, expected_type=type_hints["assume_role_arn"])
            check_type(argname="argument dependency_stack", value=dependency_stack, expected_type=type_hints["dependency_stack"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket_name": bucket_name,
        }
        if assume_role_arn is not None:
            self._values["assume_role_arn"] = assume_role_arn
        if dependency_stack is not None:
            self._values["dependency_stack"] = dependency_stack
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''(experimental) The name of the staging bucket.

        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN to assume to write files to this bucket.

        :default: - Don't assume a role

        :stability: experimental
        '''
        result = self._values.get("assume_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependency_stack(self) -> typing.Optional[_aws_cdk_ceddda9d.Stack]:
        '''(experimental) The stack that creates this bucket (leads to dependencies on it).

        :default: - Don't add dependencies

        :stability: experimental
        '''
        result = self._values.get("dependency_stack")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Stack], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix to add to the keys.

        :default: ''

        :stability: experimental
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileStagingLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/app-staging-synthesizer-alpha.IStagingResources")
class IStagingResources(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''(experimental) Staging Resource interface.

    :stability: experimental
    '''

    @jsii.member(jsii_name="addDockerImage")
    def add_docker_image(
        self,
        *,
        source_hash: builtins.str,
        asset_name: typing.Optional[builtins.str] = None,
        directory_name: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_ssh: typing.Optional[builtins.str] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_cache_disabled: typing.Optional[builtins.bool] = None,
        docker_cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        docker_cache_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_file: typing.Optional[builtins.str] = None,
        docker_outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
    ) -> "ImageStagingLocation":
        '''(experimental) Return staging resource information for a docker asset.

        :param source_hash: The hash of the contents of the docker build context. This hash is used throughout the system to identify this image and avoid duplicate work in case the source did not change. NOTE: this means that if you wish to update your docker image, you must make a modification to the source (e.g. add some metadata to your Dockerfile).
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param directory_name: The directory where the Dockerfile is stored, must be relative to the cloud assembly root. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param docker_build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build args are passed
        :param docker_build_secrets: Build secrets to pass to the ``docker build`` command. Since Docker build secrets are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build secrets are passed
        :param docker_build_ssh: SSH agent socket or keys to pass to the ``docker buildx`` command. Default: - no ssh arg is passed
        :param docker_build_target: Docker target to build to. Only allowed when ``directoryName`` is specified. Default: - no target
        :param docker_cache_disabled: Disable the cache and pass ``--no-cache`` to the ``docker build`` command. Default: - cache is used
        :param docker_cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from args are passed
        :param docker_cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to args are passed
        :param docker_file: Path to the Dockerfile (relative to the directory). Only allowed when ``directoryName`` is specified. Default: - no file
        :param docker_outputs: Outputs to pass to the ``docker build`` command. Default: - no build args are passed
        :param executable: An external command that will produce the packaged asset. The command should produce the name of a local Docker image on ``stdout``. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param network_mode: Networking mode for the RUN commands during build. *Requires Docker Engine API v1.25+*. Specify this property to build images on a specific networking mode. Default: - no networking mode specified
        :param platform: Platform to build for. *Requires Docker Buildx*. Specify this property to build images on a specific platform. Default: - no platform specified (the current machine architecture will be used)

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addFile")
    def add_file(
        self,
        *,
        source_hash: builtins.str,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        file_name: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[_aws_cdk_ceddda9d.FileAssetPackaging] = None,
    ) -> FileStagingLocation:
        '''(experimental) Return staging resource information for a file asset.

        :param source_hash: A hash on the content source. This hash is used to uniquely identify this asset throughout the system. If this value doesn't change, the asset will not be rebuilt or republished.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param executable: An external command that will produce the packaged asset. The command should produce the location of a ZIP file on ``stdout``. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param file_name: The path, relative to the root of the cloud assembly, in which this asset source resides. This can be a path to a file or a directory, depending on the packaging type. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param packaging: Which type of packaging to perform. Default: - Required if ``fileName`` is specified.

        :stability: experimental
        '''
        ...


class _IStagingResourcesProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''(experimental) Staging Resource interface.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/app-staging-synthesizer-alpha.IStagingResources"

    @jsii.member(jsii_name="addDockerImage")
    def add_docker_image(
        self,
        *,
        source_hash: builtins.str,
        asset_name: typing.Optional[builtins.str] = None,
        directory_name: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_ssh: typing.Optional[builtins.str] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_cache_disabled: typing.Optional[builtins.bool] = None,
        docker_cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        docker_cache_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_file: typing.Optional[builtins.str] = None,
        docker_outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
    ) -> "ImageStagingLocation":
        '''(experimental) Return staging resource information for a docker asset.

        :param source_hash: The hash of the contents of the docker build context. This hash is used throughout the system to identify this image and avoid duplicate work in case the source did not change. NOTE: this means that if you wish to update your docker image, you must make a modification to the source (e.g. add some metadata to your Dockerfile).
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param directory_name: The directory where the Dockerfile is stored, must be relative to the cloud assembly root. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param docker_build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build args are passed
        :param docker_build_secrets: Build secrets to pass to the ``docker build`` command. Since Docker build secrets are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build secrets are passed
        :param docker_build_ssh: SSH agent socket or keys to pass to the ``docker buildx`` command. Default: - no ssh arg is passed
        :param docker_build_target: Docker target to build to. Only allowed when ``directoryName`` is specified. Default: - no target
        :param docker_cache_disabled: Disable the cache and pass ``--no-cache`` to the ``docker build`` command. Default: - cache is used
        :param docker_cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from args are passed
        :param docker_cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to args are passed
        :param docker_file: Path to the Dockerfile (relative to the directory). Only allowed when ``directoryName`` is specified. Default: - no file
        :param docker_outputs: Outputs to pass to the ``docker build`` command. Default: - no build args are passed
        :param executable: An external command that will produce the packaged asset. The command should produce the name of a local Docker image on ``stdout``. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param network_mode: Networking mode for the RUN commands during build. *Requires Docker Engine API v1.25+*. Specify this property to build images on a specific networking mode. Default: - no networking mode specified
        :param platform: Platform to build for. *Requires Docker Buildx*. Specify this property to build images on a specific platform. Default: - no platform specified (the current machine architecture will be used)

        :stability: experimental
        '''
        asset = _aws_cdk_ceddda9d.DockerImageAssetSource(
            source_hash=source_hash,
            asset_name=asset_name,
            directory_name=directory_name,
            display_name=display_name,
            docker_build_args=docker_build_args,
            docker_build_secrets=docker_build_secrets,
            docker_build_ssh=docker_build_ssh,
            docker_build_target=docker_build_target,
            docker_cache_disabled=docker_cache_disabled,
            docker_cache_from=docker_cache_from,
            docker_cache_to=docker_cache_to,
            docker_file=docker_file,
            docker_outputs=docker_outputs,
            executable=executable,
            network_mode=network_mode,
            platform=platform,
        )

        return typing.cast("ImageStagingLocation", jsii.invoke(self, "addDockerImage", [asset]))

    @jsii.member(jsii_name="addFile")
    def add_file(
        self,
        *,
        source_hash: builtins.str,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        file_name: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[_aws_cdk_ceddda9d.FileAssetPackaging] = None,
    ) -> FileStagingLocation:
        '''(experimental) Return staging resource information for a file asset.

        :param source_hash: A hash on the content source. This hash is used to uniquely identify this asset throughout the system. If this value doesn't change, the asset will not be rebuilt or republished.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param executable: An external command that will produce the packaged asset. The command should produce the location of a ZIP file on ``stdout``. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param file_name: The path, relative to the root of the cloud assembly, in which this asset source resides. This can be a path to a file or a directory, depending on the packaging type. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param packaging: Which type of packaging to perform. Default: - Required if ``fileName`` is specified.

        :stability: experimental
        '''
        asset = _aws_cdk_ceddda9d.FileAssetSource(
            source_hash=source_hash,
            deploy_time=deploy_time,
            display_name=display_name,
            executable=executable,
            file_name=file_name,
            packaging=packaging,
        )

        return typing.cast(FileStagingLocation, jsii.invoke(self, "addFile", [asset]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStagingResources).__jsii_proxy_class__ = lambda : _IStagingResourcesProxy


@jsii.interface(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.IStagingResourcesFactory"
)
class IStagingResourcesFactory(typing_extensions.Protocol):
    '''(experimental) Staging Resource Factory interface.

    The function included in this class will be called by the synthesizer
    to create or reference an IStagingResources construct that has the necessary
    staging resources for the stack.

    :stability: experimental
    '''

    @jsii.member(jsii_name="obtainStagingResources")
    def obtain_staging_resources(
        self,
        stack: _aws_cdk_ceddda9d.Stack,
        *,
        environment_string: builtins.str,
        qualifier: builtins.str,
        deploy_role_arn: typing.Optional[builtins.str] = None,
    ) -> IStagingResources:
        '''(experimental) Return an object that will manage staging resources for the given stack.

        This is called whenever the the ``AppStagingSynthesizer`` binds to a specific
        stack, and allows selecting where the staging resources go.

        This method can choose to either create a new construct (perhaps a stack)
        and return it, or reference an existing construct.

        :param stack: - stack to return an appropriate IStagingStack for.
        :param environment_string: (experimental) A unique string describing the environment that is guaranteed not to have tokens in it.
        :param qualifier: (experimental) The qualifier passed to the synthesizer. The staging stack shouldn't need this, but it might.
        :param deploy_role_arn: (experimental) The ARN of the deploy action role, if given. This role will need permissions to read from to the staging resources. Default: - Deploy role ARN is unknown

        :stability: experimental
        '''
        ...


class _IStagingResourcesFactoryProxy:
    '''(experimental) Staging Resource Factory interface.

    The function included in this class will be called by the synthesizer
    to create or reference an IStagingResources construct that has the necessary
    staging resources for the stack.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/app-staging-synthesizer-alpha.IStagingResourcesFactory"

    @jsii.member(jsii_name="obtainStagingResources")
    def obtain_staging_resources(
        self,
        stack: _aws_cdk_ceddda9d.Stack,
        *,
        environment_string: builtins.str,
        qualifier: builtins.str,
        deploy_role_arn: typing.Optional[builtins.str] = None,
    ) -> IStagingResources:
        '''(experimental) Return an object that will manage staging resources for the given stack.

        This is called whenever the the ``AppStagingSynthesizer`` binds to a specific
        stack, and allows selecting where the staging resources go.

        This method can choose to either create a new construct (perhaps a stack)
        and return it, or reference an existing construct.

        :param stack: - stack to return an appropriate IStagingStack for.
        :param environment_string: (experimental) A unique string describing the environment that is guaranteed not to have tokens in it.
        :param qualifier: (experimental) The qualifier passed to the synthesizer. The staging stack shouldn't need this, but it might.
        :param deploy_role_arn: (experimental) The ARN of the deploy action role, if given. This role will need permissions to read from to the staging resources. Default: - Deploy role ARN is unknown

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c07d714262124bb4037640535eebd244a0472e001ca0ec2747a8c7dee56c74da)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        context = ObtainStagingResourcesContext(
            environment_string=environment_string,
            qualifier=qualifier,
            deploy_role_arn=deploy_role_arn,
        )

        return typing.cast(IStagingResources, jsii.invoke(self, "obtainStagingResources", [stack, context]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStagingResourcesFactory).__jsii_proxy_class__ = lambda : _IStagingResourcesFactoryProxy


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.ImageStagingLocation",
    jsii_struct_bases=[],
    name_mapping={
        "repo_name": "repoName",
        "assume_role_arn": "assumeRoleArn",
        "dependency_stack": "dependencyStack",
    },
)
class ImageStagingLocation:
    def __init__(
        self,
        *,
        repo_name: builtins.str,
        assume_role_arn: typing.Optional[builtins.str] = None,
        dependency_stack: typing.Optional[_aws_cdk_ceddda9d.Stack] = None,
    ) -> None:
        '''(experimental) Information returned by the Staging Stack for each image asset.

        :param repo_name: (experimental) The name of the staging repository.
        :param assume_role_arn: (experimental) The arn to assume to write files to this repository. Default: - Don't assume a role
        :param dependency_stack: (experimental) The stack that creates this repository (leads to dependencies on it). Default: - Don't add dependencies

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
            import aws_cdk as cdk
            
            # stack: cdk.Stack
            
            image_staging_location = app_staging_synthesizer_alpha.ImageStagingLocation(
                repo_name="repoName",
            
                # the properties below are optional
                assume_role_arn="assumeRoleArn",
                dependency_stack=stack
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37cd9611881b62fac905d03f84a9c8e75eb8ef790f95bf345815f078f2269776)
            check_type(argname="argument repo_name", value=repo_name, expected_type=type_hints["repo_name"])
            check_type(argname="argument assume_role_arn", value=assume_role_arn, expected_type=type_hints["assume_role_arn"])
            check_type(argname="argument dependency_stack", value=dependency_stack, expected_type=type_hints["dependency_stack"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repo_name": repo_name,
        }
        if assume_role_arn is not None:
            self._values["assume_role_arn"] = assume_role_arn
        if dependency_stack is not None:
            self._values["dependency_stack"] = dependency_stack

    @builtins.property
    def repo_name(self) -> builtins.str:
        '''(experimental) The name of the staging repository.

        :stability: experimental
        '''
        result = self._values.get("repo_name")
        assert result is not None, "Required property 'repo_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The arn to assume to write files to this repository.

        :default: - Don't assume a role

        :stability: experimental
        '''
        result = self._values.get("assume_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependency_stack(self) -> typing.Optional[_aws_cdk_ceddda9d.Stack]:
        '''(experimental) The stack that creates this repository (leads to dependencies on it).

        :default: - Don't add dependencies

        :stability: experimental
        '''
        result = self._values.get("dependency_stack")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Stack], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageStagingLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.ObtainStagingResourcesContext",
    jsii_struct_bases=[],
    name_mapping={
        "environment_string": "environmentString",
        "qualifier": "qualifier",
        "deploy_role_arn": "deployRoleArn",
    },
)
class ObtainStagingResourcesContext:
    def __init__(
        self,
        *,
        environment_string: builtins.str,
        qualifier: builtins.str,
        deploy_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Context parameters for the 'obtainStagingResources' function.

        :param environment_string: (experimental) A unique string describing the environment that is guaranteed not to have tokens in it.
        :param qualifier: (experimental) The qualifier passed to the synthesizer. The staging stack shouldn't need this, but it might.
        :param deploy_role_arn: (experimental) The ARN of the deploy action role, if given. This role will need permissions to read from to the staging resources. Default: - Deploy role ARN is unknown

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
            
            obtain_staging_resources_context = app_staging_synthesizer_alpha.ObtainStagingResourcesContext(
                environment_string="environmentString",
                qualifier="qualifier",
            
                # the properties below are optional
                deploy_role_arn="deployRoleArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eae5ff501db29c7e6379aff099cd28738d673d835ab1439cec2f27dbc70acd1e)
            check_type(argname="argument environment_string", value=environment_string, expected_type=type_hints["environment_string"])
            check_type(argname="argument qualifier", value=qualifier, expected_type=type_hints["qualifier"])
            check_type(argname="argument deploy_role_arn", value=deploy_role_arn, expected_type=type_hints["deploy_role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "environment_string": environment_string,
            "qualifier": qualifier,
        }
        if deploy_role_arn is not None:
            self._values["deploy_role_arn"] = deploy_role_arn

    @builtins.property
    def environment_string(self) -> builtins.str:
        '''(experimental) A unique string describing the environment that is guaranteed not to have tokens in it.

        :stability: experimental
        '''
        result = self._values.get("environment_string")
        assert result is not None, "Required property 'environment_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def qualifier(self) -> builtins.str:
        '''(experimental) The qualifier passed to the synthesizer.

        The staging stack shouldn't need this, but it might.

        :stability: experimental
        '''
        result = self._values.get("qualifier")
        assert result is not None, "Required property 'qualifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deploy_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the deploy action role, if given.

        This role will need permissions to read from to the staging resources.

        :default: - Deploy role ARN is unknown

        :stability: experimental
        '''
        result = self._values.get("deploy_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObtainStagingResourcesContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.StagingRoles",
    jsii_struct_bases=[],
    name_mapping={
        "docker_asset_publishing_role": "dockerAssetPublishingRole",
        "file_asset_publishing_role": "fileAssetPublishingRole",
    },
)
class StagingRoles:
    def __init__(
        self,
        *,
        docker_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    ) -> None:
        '''(experimental) Roles that are included in the Staging Stack (for access to Staging Resources).

        :param docker_asset_publishing_role: (experimental) Docker Asset Publishing Role. Default: - staging stack creates a docker asset publishing role
        :param file_asset_publishing_role: (experimental) File Asset Publishing Role. Default: - staging stack creates a file asset publishing role

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
            
            # bootstrap_role: app_staging_synthesizer_alpha.BootstrapRole
            
            staging_roles = app_staging_synthesizer_alpha.StagingRoles(
                docker_asset_publishing_role=bootstrap_role,
                file_asset_publishing_role=bootstrap_role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af6caa7d6610d852e545b0ead1af401b1939626fc332fff489f4ff50b5d62c27)
            check_type(argname="argument docker_asset_publishing_role", value=docker_asset_publishing_role, expected_type=type_hints["docker_asset_publishing_role"])
            check_type(argname="argument file_asset_publishing_role", value=file_asset_publishing_role, expected_type=type_hints["file_asset_publishing_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if docker_asset_publishing_role is not None:
            self._values["docker_asset_publishing_role"] = docker_asset_publishing_role
        if file_asset_publishing_role is not None:
            self._values["file_asset_publishing_role"] = file_asset_publishing_role

    @builtins.property
    def docker_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Docker Asset Publishing Role.

        :default: - staging stack creates a docker asset publishing role

        :stability: experimental
        '''
        result = self._values.get("docker_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def file_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) File Asset Publishing Role.

        :default: - staging stack creates a file asset publishing role

        :stability: experimental
        '''
        result = self._values.get("file_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StagingRoles(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UsingAppStagingSynthesizer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.UsingAppStagingSynthesizer",
):
    '''(experimental) This is a dummy construct meant to signify that a stack is utilizing the AppStagingSynthesizer.

    It does not do anything, and is not meant
    to be created on its own. This construct will be a part of the
    construct tree only and not the Cfn template. The construct tree is
    then encoded in the AWS::CDK::Metadata resource of the stack and
    injested in our metrics like every other construct.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.app_staging_synthesizer_alpha as app_staging_synthesizer_alpha
        
        using_app_staging_synthesizer = app_staging_synthesizer_alpha.UsingAppStagingSynthesizer(self, "MyUsingAppStagingSynthesizer")
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2450a25d8e0af64a0996ad931b80e0eac3d8b11c4c148ebd044357f128d25670)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])


@jsii.data_type(
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.DefaultResourcesOptions",
    jsii_struct_bases=[AppStagingSynthesizerOptions, DefaultStagingStackOptions],
    name_mapping={
        "bootstrap_qualifier": "bootstrapQualifier",
        "deployment_identities": "deploymentIdentities",
        "app_id": "appId",
        "staging_bucket_encryption": "stagingBucketEncryption",
        "auto_delete_staging_assets": "autoDeleteStagingAssets",
        "deploy_time_file_asset_lifetime": "deployTimeFileAssetLifetime",
        "file_asset_publishing_role": "fileAssetPublishingRole",
        "image_asset_publishing_role": "imageAssetPublishingRole",
        "image_asset_version_count": "imageAssetVersionCount",
        "staging_bucket_name": "stagingBucketName",
        "staging_stack_name_prefix": "stagingStackNamePrefix",
    },
)
class DefaultResourcesOptions(AppStagingSynthesizerOptions, DefaultStagingStackOptions):
    def __init__(
        self,
        *,
        bootstrap_qualifier: typing.Optional[builtins.str] = None,
        deployment_identities: typing.Optional[DeploymentIdentities] = None,
        app_id: builtins.str,
        staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
        deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_version_count: typing.Optional[jsii.Number] = None,
        staging_bucket_name: typing.Optional[builtins.str] = None,
        staging_stack_name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for stackPerEnv static method.

        :param bootstrap_qualifier: (experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account. This qualifier is only used to reference bootstrapped resources. It will not be used in the creation of app-specific staging resources: ``appId`` is used for that instead. Default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``
        :param deployment_identities: (experimental) What roles to use to deploy applications. These are the roles that have permissions to interact with CloudFormation on your behalf. By default these are the standard bootstrapped CDK roles, but you can customize them or turn them off and use the CLI credentials to deploy. Default: - The standard bootstrapped CDK roles
        :param app_id: (experimental) A unique identifier for the application that the staging stack belongs to. This identifier will be used in the name of staging resources created for this application, and should be unique across CDK apps. The identifier should include lowercase characters and dashes ('-') only and have a maximum of 20 characters.
        :param staging_bucket_encryption: (experimental) Encryption type for staging bucket. In future versions of this package, the default will be BucketEncryption.S3_MANAGED. In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3 managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required. If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.
        :param auto_delete_staging_assets: (experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories. Default: true
        :param deploy_time_file_asset_lifetime: (experimental) The lifetime for deploy time file assets. Assets that are only necessary at deployment time (for instance, CloudFormation templates and Lambda source code bundles) will be automatically deleted after this many days. Assets that may be read from the staging bucket during your application's run time will not be deleted. Set this to the length of time you wish to be able to roll back to previous versions of your application without having to do a new ``cdk synth`` and re-upload of assets. Default: - Duration.days(30)
        :param file_asset_publishing_role: (experimental) Pass in an existing role to be used as the file publishing role. Default: - a new role will be created
        :param image_asset_publishing_role: (experimental) Pass in an existing role to be used as the image publishing role. Default: - a new role will be created
        :param image_asset_version_count: (experimental) The maximum number of image versions to store in a repository. Previous versions of an image can be stored for rollback purposes. Once a repository has more than 3 image versions stored, the oldest version will be discarded. This allows for sensible garbage collection while maintaining a few previous versions for rollback scenarios. Default: - up to 3 versions stored
        :param staging_bucket_name: (experimental) Explicit name for the staging bucket. Default: - a well-known name unique to this app/env.
        :param staging_stack_name_prefix: (experimental) Specify a custom prefix to be used as the staging stack name and construct ID. The prefix will be appended before the appId, which is required to be part of the stack name and construct ID to ensure uniqueness. Default: 'StagingStack'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.aws_s3 import BucketEncryption
            
            
            app = App(
                default_stack_synthesizer=AppStagingSynthesizer.default_resources(
                    app_id="my-app-id",
                    staging_bucket_encryption=BucketEncryption.S3_MANAGED,
                    file_asset_publishing_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/S3Access"),
                    image_asset_publishing_role=BootstrapRole.from_role_arn("arn:aws:iam::123456789012:role/ECRAccess")
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29102b1165011d046c95963e887fe565a9300d7ed93d8499af73ef05f0e32e60)
            check_type(argname="argument bootstrap_qualifier", value=bootstrap_qualifier, expected_type=type_hints["bootstrap_qualifier"])
            check_type(argname="argument deployment_identities", value=deployment_identities, expected_type=type_hints["deployment_identities"])
            check_type(argname="argument app_id", value=app_id, expected_type=type_hints["app_id"])
            check_type(argname="argument staging_bucket_encryption", value=staging_bucket_encryption, expected_type=type_hints["staging_bucket_encryption"])
            check_type(argname="argument auto_delete_staging_assets", value=auto_delete_staging_assets, expected_type=type_hints["auto_delete_staging_assets"])
            check_type(argname="argument deploy_time_file_asset_lifetime", value=deploy_time_file_asset_lifetime, expected_type=type_hints["deploy_time_file_asset_lifetime"])
            check_type(argname="argument file_asset_publishing_role", value=file_asset_publishing_role, expected_type=type_hints["file_asset_publishing_role"])
            check_type(argname="argument image_asset_publishing_role", value=image_asset_publishing_role, expected_type=type_hints["image_asset_publishing_role"])
            check_type(argname="argument image_asset_version_count", value=image_asset_version_count, expected_type=type_hints["image_asset_version_count"])
            check_type(argname="argument staging_bucket_name", value=staging_bucket_name, expected_type=type_hints["staging_bucket_name"])
            check_type(argname="argument staging_stack_name_prefix", value=staging_stack_name_prefix, expected_type=type_hints["staging_stack_name_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_id": app_id,
            "staging_bucket_encryption": staging_bucket_encryption,
        }
        if bootstrap_qualifier is not None:
            self._values["bootstrap_qualifier"] = bootstrap_qualifier
        if deployment_identities is not None:
            self._values["deployment_identities"] = deployment_identities
        if auto_delete_staging_assets is not None:
            self._values["auto_delete_staging_assets"] = auto_delete_staging_assets
        if deploy_time_file_asset_lifetime is not None:
            self._values["deploy_time_file_asset_lifetime"] = deploy_time_file_asset_lifetime
        if file_asset_publishing_role is not None:
            self._values["file_asset_publishing_role"] = file_asset_publishing_role
        if image_asset_publishing_role is not None:
            self._values["image_asset_publishing_role"] = image_asset_publishing_role
        if image_asset_version_count is not None:
            self._values["image_asset_version_count"] = image_asset_version_count
        if staging_bucket_name is not None:
            self._values["staging_bucket_name"] = staging_bucket_name
        if staging_stack_name_prefix is not None:
            self._values["staging_stack_name_prefix"] = staging_stack_name_prefix

    @builtins.property
    def bootstrap_qualifier(self) -> typing.Optional[builtins.str]:
        '''(experimental) Qualifier to disambiguate multiple bootstrapped environments in the same account.

        This qualifier is only used to reference bootstrapped resources. It will not
        be used in the creation of app-specific staging resources: ``appId`` is used for that
        instead.

        :default: - Value of context key '@aws-cdk/core:bootstrapQualifier' if set, otherwise ``DEFAULT_QUALIFIER``

        :stability: experimental
        '''
        result = self._values.get("bootstrap_qualifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_identities(self) -> typing.Optional[DeploymentIdentities]:
        '''(experimental) What roles to use to deploy applications.

        These are the roles that have permissions to interact with CloudFormation
        on your behalf. By default these are the standard bootstrapped CDK roles,
        but you can customize them or turn them off and use the CLI credentials
        to deploy.

        :default: - The standard bootstrapped CDK roles

        :stability: experimental
        '''
        result = self._values.get("deployment_identities")
        return typing.cast(typing.Optional[DeploymentIdentities], result)

    @builtins.property
    def app_id(self) -> builtins.str:
        '''(experimental) A unique identifier for the application that the staging stack belongs to.

        This identifier will be used in the name of staging resources
        created for this application, and should be unique across CDK apps.

        The identifier should include lowercase characters and dashes ('-') only
        and have a maximum of 20 characters.

        :stability: experimental
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def staging_bucket_encryption(self) -> _aws_cdk_aws_s3_ceddda9d.BucketEncryption:
        '''(experimental) Encryption type for staging bucket.

        In future versions of this package, the default will be BucketEncryption.S3_MANAGED.

        In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost
        $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module
        we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3
        managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required.

        If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to
        BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to
        BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.

        :stability: experimental
        '''
        result = self._values.get("staging_bucket_encryption")
        assert result is not None, "Required property 'staging_bucket_encryption' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.BucketEncryption, result)

    @builtins.property
    def auto_delete_staging_assets(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_delete_staging_assets")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def deploy_time_file_asset_lifetime(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The lifetime for deploy time file assets.

        Assets that are only necessary at deployment time (for instance,
        CloudFormation templates and Lambda source code bundles) will be
        automatically deleted after this many days. Assets that may be
        read from the staging bucket during your application's run time
        will not be deleted.

        Set this to the length of time you wish to be able to roll back to
        previous versions of your application without having to do a new
        ``cdk synth`` and re-upload of assets.

        :default: - Duration.days(30)

        :stability: experimental
        '''
        result = self._values.get("deploy_time_file_asset_lifetime")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def file_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Pass in an existing role to be used as the file publishing role.

        :default: - a new role will be created

        :stability: experimental
        '''
        result = self._values.get("file_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def image_asset_publishing_role(self) -> typing.Optional[BootstrapRole]:
        '''(experimental) Pass in an existing role to be used as the image publishing role.

        :default: - a new role will be created

        :stability: experimental
        '''
        result = self._values.get("image_asset_publishing_role")
        return typing.cast(typing.Optional[BootstrapRole], result)

    @builtins.property
    def image_asset_version_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of image versions to store in a repository.

        Previous versions of an image can be stored for rollback purposes.
        Once a repository has more than 3 image versions stored, the oldest
        version will be discarded. This allows for sensible garbage collection
        while maintaining a few previous versions for rollback scenarios.

        :default: - up to 3 versions stored

        :stability: experimental
        '''
        result = self._values.get("image_asset_version_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def staging_bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Explicit name for the staging bucket.

        :default: - a well-known name unique to this app/env.

        :stability: experimental
        '''
        result = self._values.get("staging_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def staging_stack_name_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specify a custom prefix to be used as the staging stack name and construct ID.

        The prefix will be appended before the appId, which
        is required to be part of the stack name and construct ID to
        ensure uniqueness.

        :default: 'StagingStack'

        :stability: experimental
        '''
        result = self._values.get("staging_stack_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefaultResourcesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IStagingResources)
class DefaultStagingStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/app-staging-synthesizer-alpha.DefaultStagingStack",
):
    '''(experimental) A default Staging Stack that implements IStagingResources.

    :stability: experimental

    Example::

        from aws_cdk.aws_s3 import BucketEncryption
        
        default_staging_stack = DefaultStagingStack.factory(app_id="my-app-id", staging_bucket_encryption=BucketEncryption.S3_MANAGED)
    '''

    def __init__(
        self,
        scope: _aws_cdk_ceddda9d.App,
        id: builtins.str,
        *,
        qualifier: builtins.str,
        deploy_role_arn: typing.Optional[builtins.str] = None,
        app_id: builtins.str,
        staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
        deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_version_count: typing.Optional[jsii.Number] = None,
        staging_bucket_name: typing.Optional[builtins.str] = None,
        staging_stack_name_prefix: typing.Optional[builtins.str] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param qualifier: (experimental) The qualifier used to specialize strings. Can be used to specify custom bootstrapped role names
        :param deploy_role_arn: (experimental) The ARN of the deploy action role, if given. This role will need permissions to read from to the staging resources. Default: - The CLI credentials are assumed, no additional permissions are granted.
        :param app_id: (experimental) A unique identifier for the application that the staging stack belongs to. This identifier will be used in the name of staging resources created for this application, and should be unique across CDK apps. The identifier should include lowercase characters and dashes ('-') only and have a maximum of 20 characters.
        :param staging_bucket_encryption: (experimental) Encryption type for staging bucket. In future versions of this package, the default will be BucketEncryption.S3_MANAGED. In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3 managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required. If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.
        :param auto_delete_staging_assets: (experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories. Default: true
        :param deploy_time_file_asset_lifetime: (experimental) The lifetime for deploy time file assets. Assets that are only necessary at deployment time (for instance, CloudFormation templates and Lambda source code bundles) will be automatically deleted after this many days. Assets that may be read from the staging bucket during your application's run time will not be deleted. Set this to the length of time you wish to be able to roll back to previous versions of your application without having to do a new ``cdk synth`` and re-upload of assets. Default: - Duration.days(30)
        :param file_asset_publishing_role: (experimental) Pass in an existing role to be used as the file publishing role. Default: - a new role will be created
        :param image_asset_publishing_role: (experimental) Pass in an existing role to be used as the image publishing role. Default: - a new role will be created
        :param image_asset_version_count: (experimental) The maximum number of image versions to store in a repository. Previous versions of an image can be stored for rollback purposes. Once a repository has more than 3 image versions stored, the oldest version will be discarded. This allows for sensible garbage collection while maintaining a few previous versions for rollback scenarios. Default: - up to 3 versions stored
        :param staging_bucket_name: (experimental) Explicit name for the staging bucket. Default: - a well-known name unique to this app/env.
        :param staging_stack_name_prefix: (experimental) Specify a custom prefix to be used as the staging stack name and construct ID. The prefix will be appended before the appId, which is required to be part of the stack name and construct ID to ensure uniqueness. Default: 'StagingStack'
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notfication arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param property_injectors: A list of IPropertyInjector attached to this Stack. Default: - no PropertyInjectors
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Tags that will be applied to the Stack. These tags are applied to the CloudFormation Stack itself. They will not appear in the CloudFormation template. However, at deployment time, CloudFormation will apply these tags to all resources in the stack that support tagging. You will not be able to exempt resources from tagging (using the ``excludeResourceTypes`` property of ``Tags.of(...).add()``) for tags applied in this way. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca741a4572a1f95a8d82e9d029388b8a2d72acacb69715277b6a785b4968e662)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DefaultStagingStackProps(
            qualifier=qualifier,
            deploy_role_arn=deploy_role_arn,
            app_id=app_id,
            staging_bucket_encryption=staging_bucket_encryption,
            auto_delete_staging_assets=auto_delete_staging_assets,
            deploy_time_file_asset_lifetime=deploy_time_file_asset_lifetime,
            file_asset_publishing_role=file_asset_publishing_role,
            image_asset_publishing_role=image_asset_publishing_role,
            image_asset_version_count=image_asset_version_count,
            staging_bucket_name=staging_bucket_name,
            staging_stack_name_prefix=staging_stack_name_prefix,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            property_injectors=property_injectors,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="factory")
    @builtins.classmethod
    def factory(
        cls,
        *,
        app_id: builtins.str,
        staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
        auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
        deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
        image_asset_version_count: typing.Optional[jsii.Number] = None,
        staging_bucket_name: typing.Optional[builtins.str] = None,
        staging_stack_name_prefix: typing.Optional[builtins.str] = None,
    ) -> IStagingResourcesFactory:
        '''(experimental) Return a factory that will create DefaultStagingStacks.

        :param app_id: (experimental) A unique identifier for the application that the staging stack belongs to. This identifier will be used in the name of staging resources created for this application, and should be unique across CDK apps. The identifier should include lowercase characters and dashes ('-') only and have a maximum of 20 characters.
        :param staging_bucket_encryption: (experimental) Encryption type for staging bucket. In future versions of this package, the default will be BucketEncryption.S3_MANAGED. In previous versions of this package, the default was to use KMS encryption for the staging bucket. KMS keys cost $1/month, which could result in unexpected costs for users who are not aware of this. As we stabilize this module we intend to make the default S3-managed encryption, which is free. However, the migration path from KMS to S3 managed encryption for existing buckets is not straightforward. Therefore, for now, this property is required. If you have an existing staging bucket encrypted with a KMS key, you will likely want to set this property to BucketEncryption.KMS. If you are creating a new staging bucket, you can set this property to BucketEncryption.S3_MANAGED to avoid the cost of a KMS key.
        :param auto_delete_staging_assets: (experimental) Auto deletes objects in the staging S3 bucket and images in the staging ECR repositories. Default: true
        :param deploy_time_file_asset_lifetime: (experimental) The lifetime for deploy time file assets. Assets that are only necessary at deployment time (for instance, CloudFormation templates and Lambda source code bundles) will be automatically deleted after this many days. Assets that may be read from the staging bucket during your application's run time will not be deleted. Set this to the length of time you wish to be able to roll back to previous versions of your application without having to do a new ``cdk synth`` and re-upload of assets. Default: - Duration.days(30)
        :param file_asset_publishing_role: (experimental) Pass in an existing role to be used as the file publishing role. Default: - a new role will be created
        :param image_asset_publishing_role: (experimental) Pass in an existing role to be used as the image publishing role. Default: - a new role will be created
        :param image_asset_version_count: (experimental) The maximum number of image versions to store in a repository. Previous versions of an image can be stored for rollback purposes. Once a repository has more than 3 image versions stored, the oldest version will be discarded. This allows for sensible garbage collection while maintaining a few previous versions for rollback scenarios. Default: - up to 3 versions stored
        :param staging_bucket_name: (experimental) Explicit name for the staging bucket. Default: - a well-known name unique to this app/env.
        :param staging_stack_name_prefix: (experimental) Specify a custom prefix to be used as the staging stack name and construct ID. The prefix will be appended before the appId, which is required to be part of the stack name and construct ID to ensure uniqueness. Default: 'StagingStack'

        :stability: experimental
        '''
        options = DefaultStagingStackOptions(
            app_id=app_id,
            staging_bucket_encryption=staging_bucket_encryption,
            auto_delete_staging_assets=auto_delete_staging_assets,
            deploy_time_file_asset_lifetime=deploy_time_file_asset_lifetime,
            file_asset_publishing_role=file_asset_publishing_role,
            image_asset_publishing_role=image_asset_publishing_role,
            image_asset_version_count=image_asset_version_count,
            staging_bucket_name=staging_bucket_name,
            staging_stack_name_prefix=staging_stack_name_prefix,
        )

        return typing.cast(IStagingResourcesFactory, jsii.sinvoke(cls, "factory", [options]))

    @jsii.member(jsii_name="addDockerImage")
    def add_docker_image(
        self,
        *,
        source_hash: builtins.str,
        asset_name: typing.Optional[builtins.str] = None,
        directory_name: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_ssh: typing.Optional[builtins.str] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_cache_disabled: typing.Optional[builtins.bool] = None,
        docker_cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        docker_cache_to: typing.Optional[typing.Union[_aws_cdk_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        docker_file: typing.Optional[builtins.str] = None,
        docker_outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
    ) -> ImageStagingLocation:
        '''(experimental) Return staging resource information for a docker asset.

        :param source_hash: The hash of the contents of the docker build context. This hash is used throughout the system to identify this image and avoid duplicate work in case the source did not change. NOTE: this means that if you wish to update your docker image, you must make a modification to the source (e.g. add some metadata to your Dockerfile).
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param directory_name: The directory where the Dockerfile is stored, must be relative to the cloud assembly root. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param docker_build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build args are passed
        :param docker_build_secrets: Build secrets to pass to the ``docker build`` command. Since Docker build secrets are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build secrets are passed
        :param docker_build_ssh: SSH agent socket or keys to pass to the ``docker buildx`` command. Default: - no ssh arg is passed
        :param docker_build_target: Docker target to build to. Only allowed when ``directoryName`` is specified. Default: - no target
        :param docker_cache_disabled: Disable the cache and pass ``--no-cache`` to the ``docker build`` command. Default: - cache is used
        :param docker_cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from args are passed
        :param docker_cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to args are passed
        :param docker_file: Path to the Dockerfile (relative to the directory). Only allowed when ``directoryName`` is specified. Default: - no file
        :param docker_outputs: Outputs to pass to the ``docker build`` command. Default: - no build args are passed
        :param executable: An external command that will produce the packaged asset. The command should produce the name of a local Docker image on ``stdout``. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param network_mode: Networking mode for the RUN commands during build. *Requires Docker Engine API v1.25+*. Specify this property to build images on a specific networking mode. Default: - no networking mode specified
        :param platform: Platform to build for. *Requires Docker Buildx*. Specify this property to build images on a specific platform. Default: - no platform specified (the current machine architecture will be used)

        :stability: experimental
        '''
        asset = _aws_cdk_ceddda9d.DockerImageAssetSource(
            source_hash=source_hash,
            asset_name=asset_name,
            directory_name=directory_name,
            display_name=display_name,
            docker_build_args=docker_build_args,
            docker_build_secrets=docker_build_secrets,
            docker_build_ssh=docker_build_ssh,
            docker_build_target=docker_build_target,
            docker_cache_disabled=docker_cache_disabled,
            docker_cache_from=docker_cache_from,
            docker_cache_to=docker_cache_to,
            docker_file=docker_file,
            docker_outputs=docker_outputs,
            executable=executable,
            network_mode=network_mode,
            platform=platform,
        )

        return typing.cast(ImageStagingLocation, jsii.invoke(self, "addDockerImage", [asset]))

    @jsii.member(jsii_name="addFile")
    def add_file(
        self,
        *,
        source_hash: builtins.str,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        file_name: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[_aws_cdk_ceddda9d.FileAssetPackaging] = None,
    ) -> FileStagingLocation:
        '''(experimental) Return staging resource information for a file asset.

        :param source_hash: A hash on the content source. This hash is used to uniquely identify this asset throughout the system. If this value doesn't change, the asset will not be rebuilt or republished.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. Default: - The asset hash is used to display the asset
        :param executable: An external command that will produce the packaged asset. The command should produce the location of a ZIP file on ``stdout``. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param file_name: The path, relative to the root of the cloud assembly, in which this asset source resides. This can be a path to a file or a directory, depending on the packaging type. Default: - Exactly one of ``fileName`` and ``executable`` is required
        :param packaging: Which type of packaging to perform. Default: - Required if ``fileName`` is specified.

        :stability: experimental
        '''
        asset = _aws_cdk_ceddda9d.FileAssetSource(
            source_hash=source_hash,
            deploy_time=deploy_time,
            display_name=display_name,
            executable=executable,
            file_name=file_name,
            packaging=packaging,
        )

        return typing.cast(FileStagingLocation, jsii.invoke(self, "addFile", [asset]))

    @builtins.property
    @jsii.member(jsii_name="dependencyStack")
    def dependency_stack(self) -> _aws_cdk_ceddda9d.Stack:
        '''(experimental) The stack to add dependencies to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.get(self, "dependencyStack"))

    @builtins.property
    @jsii.member(jsii_name="stagingRepos")
    def staging_repos(
        self,
    ) -> typing.Mapping[builtins.str, _aws_cdk_aws_ecr_ceddda9d.Repository]:
        '''(experimental) The app-scoped, environment-keyed ecr repositories associated with this app.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _aws_cdk_aws_ecr_ceddda9d.Repository], jsii.get(self, "stagingRepos"))

    @builtins.property
    @jsii.member(jsii_name="stagingBucket")
    def staging_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''(experimental) The app-scoped, evironment-keyed staging bucket.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "stagingBucket"))


__all__ = [
    "AppStagingSynthesizer",
    "AppStagingSynthesizerOptions",
    "BootstrapRole",
    "BootstrapRoles",
    "CustomFactoryOptions",
    "CustomResourcesOptions",
    "DefaultBootstrapRolesOptions",
    "DefaultResourcesOptions",
    "DefaultStagingStack",
    "DefaultStagingStackOptions",
    "DefaultStagingStackProps",
    "DeploymentIdentities",
    "FileStagingLocation",
    "IStagingResources",
    "IStagingResourcesFactory",
    "ImageStagingLocation",
    "ObtainStagingResourcesContext",
    "StagingRoles",
    "UsingAppStagingSynthesizer",
]

publication.publish()

def _typecheckingstub__95a4aa84673edcde5f9edcbb6e0abc3d396e902014631ead660cc26b087ff3aa(
    _stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__459a43a0e219bcfa7acb8fb227bd72f30f82856a9f03031cf7bdb5fa56b9c968(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78deb50795e0693e69c3000edfbc5a762dc7ada84b5c564be0d8625416b06213(
    _session: _aws_cdk_ceddda9d.ISynthesisSession,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5eda98d3f47545949dd20b5c6d9a83068e0456ecdca7b7dae9779adbe1ac33a(
    *,
    bootstrap_qualifier: typing.Optional[builtins.str] = None,
    deployment_identities: typing.Optional[DeploymentIdentities] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cd108fb347d84df5492e4c7eb7ac7b451a8fd974100ef9a599abf606d702a47(
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38d27899a562cc928ca61e855b3c0f897e0453494a65e5c8fbe70ef67074507f(
    *,
    cloud_formation_execution_role: typing.Optional[BootstrapRole] = None,
    deployment_role: typing.Optional[BootstrapRole] = None,
    lookup_role: typing.Optional[BootstrapRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50a2376bb9cd02f3f3f5ad3eaaf334854ec7611a4f38af5e1139b5f5c16b0a34(
    *,
    bootstrap_qualifier: typing.Optional[builtins.str] = None,
    deployment_identities: typing.Optional[DeploymentIdentities] = None,
    factory: IStagingResourcesFactory,
    once_per_env: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805f0ab344edba46f7346788f4acc732cf8b6652895ea8485d87dfdf693e0541(
    *,
    bootstrap_qualifier: typing.Optional[builtins.str] = None,
    deployment_identities: typing.Optional[DeploymentIdentities] = None,
    resources: IStagingResources,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04df2201aac14a17d1f202664f0ecfab35edb0a3e63061b1cb8c73c369ae2804(
    *,
    bootstrap_region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09dbc6ce5bcfd58fa48337caac574e10727d4bf9a43dc89866fbe7541b026219(
    *,
    app_id: builtins.str,
    staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
    auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
    deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_version_count: typing.Optional[jsii.Number] = None,
    staging_bucket_name: typing.Optional[builtins.str] = None,
    staging_stack_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac9f132bcac8375ac08c16bf3c9bb7407b641e71cfd23cea8b50befa3cf79bbf(
    *,
    app_id: builtins.str,
    staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
    auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
    deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_version_count: typing.Optional[jsii.Number] = None,
    staging_bucket_name: typing.Optional[builtins.str] = None,
    staging_stack_name_prefix: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    qualifier: builtins.str,
    deploy_role_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c00dd9c0937fe689685a2606ff5beb696deda888ebdd50fae7f6bbfaa8764eda(
    *,
    bucket_name: builtins.str,
    assume_role_arn: typing.Optional[builtins.str] = None,
    dependency_stack: typing.Optional[_aws_cdk_ceddda9d.Stack] = None,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c07d714262124bb4037640535eebd244a0472e001ca0ec2747a8c7dee56c74da(
    stack: _aws_cdk_ceddda9d.Stack,
    *,
    environment_string: builtins.str,
    qualifier: builtins.str,
    deploy_role_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37cd9611881b62fac905d03f84a9c8e75eb8ef790f95bf345815f078f2269776(
    *,
    repo_name: builtins.str,
    assume_role_arn: typing.Optional[builtins.str] = None,
    dependency_stack: typing.Optional[_aws_cdk_ceddda9d.Stack] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eae5ff501db29c7e6379aff099cd28738d673d835ab1439cec2f27dbc70acd1e(
    *,
    environment_string: builtins.str,
    qualifier: builtins.str,
    deploy_role_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af6caa7d6610d852e545b0ead1af401b1939626fc332fff489f4ff50b5d62c27(
    *,
    docker_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2450a25d8e0af64a0996ad931b80e0eac3d8b11c4c148ebd044357f128d25670(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29102b1165011d046c95963e887fe565a9300d7ed93d8499af73ef05f0e32e60(
    *,
    bootstrap_qualifier: typing.Optional[builtins.str] = None,
    deployment_identities: typing.Optional[DeploymentIdentities] = None,
    app_id: builtins.str,
    staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
    auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
    deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_version_count: typing.Optional[jsii.Number] = None,
    staging_bucket_name: typing.Optional[builtins.str] = None,
    staging_stack_name_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca741a4572a1f95a8d82e9d029388b8a2d72acacb69715277b6a785b4968e662(
    scope: _aws_cdk_ceddda9d.App,
    id: builtins.str,
    *,
    qualifier: builtins.str,
    deploy_role_arn: typing.Optional[builtins.str] = None,
    app_id: builtins.str,
    staging_bucket_encryption: _aws_cdk_aws_s3_ceddda9d.BucketEncryption,
    auto_delete_staging_assets: typing.Optional[builtins.bool] = None,
    deploy_time_file_asset_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    file_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_publishing_role: typing.Optional[BootstrapRole] = None,
    image_asset_version_count: typing.Optional[jsii.Number] = None,
    staging_bucket_name: typing.Optional[builtins.str] = None,
    staging_stack_name_prefix: typing.Optional[builtins.str] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
