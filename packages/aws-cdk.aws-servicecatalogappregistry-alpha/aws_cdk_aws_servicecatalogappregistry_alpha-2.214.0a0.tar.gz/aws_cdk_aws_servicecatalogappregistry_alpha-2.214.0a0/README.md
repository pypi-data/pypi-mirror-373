# AWS ServiceCatalogAppRegistry Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[AWS Service Catalog App Registry](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/appregistry.html)
enables organizations to create and manage repositories of applications and associated resources.

## Table Of Contents

* [Application](#application)
* [Application-Associator](#application-associator)
* [Attribute-Group](#attribute-group)
* [Associations](#associations)

  * [Associating application with an attribute group](#attribute-group-association)
  * [Associating application with a stack](#resource-association)
* [Sharing](#sharing)

  * [Sharing an application](#sharing-an-application)
  * [Sharing an attribute group](#sharing-an-attribute-group)

The `@aws-cdk/aws-servicecatalogappregistry-alpha` package contains resources that enable users to automate governance and management of their AWS resources at scale.

```python
import aws_cdk.aws_servicecatalogappregistry_alpha as appreg
```

## Application

An AppRegistry application enables you to define your applications and associated resources.
The application name must be unique at the account level and it's immutable.

```python
application = appreg.Application(self, "MyFirstApplication",
    application_name="MyFirstApplicationName",
    description="description for my application"
)
```

An application that has been created outside of the stack can be imported into your CDK app.
Applications can be imported by their ARN via the `Application.fromApplicationArn()` API:

```python
imported_application = appreg.Application.from_application_arn(self, "MyImportedApplication", "arn:aws:servicecatalog:us-east-1:012345678910:/applications/0aqmvxvgmry0ecc4mjhwypun6i")
```

## Application-Associator

`ApplicationAssociator` defines an AppRegistry application to contain all the stacks in deployed through your cdk package. This helps to manage all the
cdk deployed resources.

### Create a new application to associate all the stacks in the cdk.App scope

If you want to create an Application named `MyAssociatedApplication` in account `123456789012` and region `us-east-1`
and want to associate all stacks in the `App` scope to `MyAssociatedApplication`, then use as shown in the example below:

```python
app = App()
associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
    applications=[appreg.TargetApplication.create_application_stack(
        application_name="MyAssociatedApplication",
        # 'Application containing stacks deployed via CDK.' is the default
        application_description="Associated Application description",
        stack_name="MyAssociatedApplicationStack",
        # AWS Account and Region that are implied by the current CLI configuration is the default
        env=Environment(account="123456789012", region="us-east-1")
    )]
)
```

This will create a stack `MyAssociatedApplicationStack` containing an application `MyAssociatedApplication`
with the `TagKey` as `managedBy` and `TagValue` as `CDK_Application_Associator`.

By default, the stack will have System Managed Application Manager console URL as its output for the application created.
If you want to remove the output, then use as shown in the example below:

```python
app = App()
associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
    applications=[appreg.TargetApplication.create_application_stack(
        application_name="MyAssociatedApplication",
        # 'Application containing stacks deployed via CDK.' is the default
        application_description="Associated Application description",
        stack_name="MyAssociatedApplicationStack",
        # Disables emitting Application Manager url as output
        emit_application_manager_url_as_output=False,
        # AWS Account and Region that are implied by the current CLI configuration is the default
        env=Environment(account="123456789012", region="us-east-1")
    )]
)
```

### Import existing application to associate all the stacks in the cdk.App scope

If you want to re-use an existing Application with ARN: `arn:aws:servicecatalog:us-east-1:123456789012:/applications/applicationId`
and want to associate all stacks in the `App` scope to your imported application, then use as shown in the example below:

```python
app = App()
associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
    applications=[appreg.TargetApplication.existing_application_from_arn(
        application_arn_value="arn:aws:servicecatalog:us-east-1:123456789012:/applications/applicationId",
        stack_name="MyAssociatedApplicationStack"
    )]
)
```

### Associate attribute group to the application used by `ApplicationAssociator`

If you want to associate an Attribute Group with application created by `ApplicationAssociator`, then use as shown in the example below:

```python
import aws_cdk as cdk


app = App()

associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
    applications=[appreg.TargetApplication.create_application_stack(
        application_name="MyAssociatedApplication",
        # 'Application containing stacks deployed via CDK.' is the default
        application_description="Associated Application description",
        stack_name="MyAssociatedApplicationStack",
        # AWS Account and Region that are implied by the current CLI configuration is the default
        env=cdk.Environment(account="123456789012", region="us-east-1")
    )]
)

# Associate application to the attribute group.
associated_app.app_registry_application.add_attribute_group("MyAttributeGroup",
    attribute_group_name="MyAttributeGroupName",
    description="Test attribute group",
    attributes={}
)
```

### Associate stacks deployed by CDK pipelines

If you are using CDK Pipelines to deploy your application, the application stacks will be inside Stages, and
ApplicationAssociator will not be able to find them. Call `associateStage` on each Stage object before adding it to the
Pipeline, as shown in the example below:

```python
import aws_cdk as cdk
import aws_cdk.pipelines as codepipeline
import aws_cdk.aws_codecommit as codecommit
# repo: codecommit.Repository
# pipeline: codepipeline.CodePipeline
# beta: cdk.Stage

class ApplicationPipelineStack(cdk.Stack):
    def __init__(self, scope, id, *, application, description=None, env=None, stackName=None, tags=None, notificationArns=None, synthesizer=None, terminationProtection=None, analyticsReporting=None, crossRegionReferences=None, permissionsBoundary=None, suppressTemplateIndentation=None, propertyInjectors=None):
        super().__init__(scope, id, application=application, description=description, env=env, stackName=stackName, tags=tags, notificationArns=notificationArns, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting, crossRegionReferences=crossRegionReferences, permissionsBoundary=permissionsBoundary, suppressTemplateIndentation=suppressTemplateIndentation, propertyInjectors=propertyInjectors)

        # associate the stage to application associator.
        application.associate_stage(beta)
        pipeline.add_stage(beta)

app = App()
associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
    applications=[appreg.TargetApplication.create_application_stack(
        application_name="MyPipelineAssociatedApplication",
        stack_name="MyPipelineAssociatedApplicationStack",
        env=cdk.Environment(account="123456789012", region="us-east-1")
    )]
)

cdk_pipeline = ApplicationPipelineStack(app, "CDKApplicationPipelineStack",
    application=associated_app,
    env=cdk.Environment(account="123456789012", region="us-east-1")
)
```

### Associate cross-account stack

By default, ApplicationAssociator will not perform cross-account stack associations with the target Application,
to avoid deployment failures for accounts which have not been setup for cross-account associations.
To enable cross-account stack associations, make sure all accounts are in the same organization as the
target Application's account and that resource sharing is enabled within the organization.
If you wish to turn on cross-account sharing and associations, set the `associateCrossAccountStacks` field to `true`,
as shown in the example below:

```python
app = App()
associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
    applications=[appreg.TargetApplication.create_application_stack(
        associate_cross_account_stacks=True,
        application_name="MyAssociatedApplication",
        env=Environment(account="123456789012", region="us-east-1")
    )]
)
```

### Associate cross-region stack

Currently, cross-region stack association is not supported.

## Attribute Group

An AppRegistry attribute group acts as a container for user-defined attributes for an application.
Metadata is attached in a machine-readable format to integrate with automated workflows and tools.
The attribute group name must be unique at the account level and it's immutable.

```python
attribute_group = appreg.AttributeGroup(self, "MyFirstAttributeGroup",
    attribute_group_name="MyFirstAttributeGroupName",
    description="description for my attribute group",  # the description is optional,
    attributes={
        "project": "foo",
        "team": ["member1", "member2", "member3"],
        "public": False,
        "stages": {
            "alpha": "complete",
            "beta": "incomplete",
            "release": "not started"
        }
    }
)
```

An attribute group that has been created outside of the stack can be imported into your CDK app.
Attribute groups can be imported by their ARN via the `AttributeGroup.fromAttributeGroupArn()` API:

```python
imported_attribute_group = appreg.AttributeGroup.from_attribute_group_arn(self, "MyImportedAttrGroup", "arn:aws:servicecatalog:us-east-1:012345678910:/attribute-groups/0aqmvxvgmry0ecc4mjhwypun6i")
```

## Associations

You can associate your appregistry application with attribute groups and resources.
Resources are CloudFormation stacks that you can associate with an application to group relevant
stacks together to enable metadata rich insights into your applications and resources.
A Cloudformation stack can only be associated with one appregistry application.
If a stack is associated with multiple applications in your app or is already associated with one,
CDK will fail at deploy time.

### Associating application with a new attribute group

You can create and associate an attribute group to an application with the `addAttributeGroup()` API:

```python
# application: appreg.Application
# attribute_group: appreg.AttributeGroup

application.add_attribute_group("MyAttributeGroupId",
    attribute_group_name="MyAttributeGroupName",
    description="Test attribute group",
    attributes={}
)
```

### Associating an attribute group with application

You can associate an application with an attribute group with `associateWith`:

```python
# application: appreg.Application
# attribute_group: appreg.AttributeGroup

attribute_group.associate_with(application)
```

### Associating application with a Stack

You can associate a stack with an application with the `associateApplicationWithStack()` API:

```python
# application: appreg.Application
app = App()
my_stack = Stack(app, "MyStack")
application.associate_application_with_stack(my_stack)
```

## Sharing

You can share your AppRegistry applications and attribute groups with AWS Organizations, Organizational Units (OUs), AWS accounts within an organization, as well as IAM roles and users. AppRegistry requires that AWS Organizations is enabled in an account before deploying a share of an application or attribute group.

### Sharing an application

```python
import aws_cdk.aws_iam as iam
# application: appreg.Application
# my_role: iam.IRole
# my_user: iam.IUser

application.share_application("MyShareId",
    name="MyShare",
    accounts=["123456789012"],
    organization_arns=["arn:aws:organizations::123456789012:organization/o-my-org-id"],
    roles=[my_role],
    users=[my_user]
)
```

E.g., sharing an application with multiple accounts and allowing the accounts to associate resources to the application.

```python
import aws_cdk.aws_iam as iam
# application: appreg.Application

application.share_application("MyShareId",
    name="MyShare",
    accounts=["123456789012", "234567890123"],
    share_permission=appreg.SharePermission.ALLOW_ACCESS
)
```

### Sharing an attribute group

```python
import aws_cdk.aws_iam as iam
# attribute_group: appreg.AttributeGroup
# my_role: iam.IRole
# my_user: iam.IUser

attribute_group.share_attribute_group("MyShareId",
    name="MyShare",
    accounts=["123456789012"],
    organization_arns=["arn:aws:organizations::123456789012:organization/o-my-org-id"],
    roles=[my_role],
    users=[my_user]
)
```

E.g., sharing an application with multiple accounts and allowing the accounts to associate applications to the attribute group.

```python
import aws_cdk.aws_iam as iam
# attribute_group: appreg.AttributeGroup

attribute_group.share_attribute_group("MyShareId",
    name="MyShare",
    accounts=["123456789012", "234567890123"],
    share_permission=appreg.SharePermission.ALLOW_ACCESS
)
```
