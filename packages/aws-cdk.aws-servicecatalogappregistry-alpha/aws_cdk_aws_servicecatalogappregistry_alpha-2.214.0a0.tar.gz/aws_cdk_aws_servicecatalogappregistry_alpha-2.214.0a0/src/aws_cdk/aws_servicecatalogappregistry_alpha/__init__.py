r'''
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
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class ApplicationAssociator(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.ApplicationAssociator",
):
    '''(experimental) An AppRegistry construct to automatically create an application with the given name and description.

    The application name must be unique at the account level per region and it's immutable.
    This construct will automatically associate all stacks in the given scope, however
    in case of a ``Pipeline`` stack, stage underneath the pipeline will not automatically be associated and
    needs to be associated separately.

    If cross account stack is detected and ``associateCrossAccountStacks`` in ``TargetApplicationOptions`` is ``true``,
    then the application will automatically be shared with the consumer accounts to allow associations.
    Otherwise, the application will not be shared.
    Cross account feature will only work for non environment agnostic stacks.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(
        self,
        scope: _aws_cdk_ceddda9d.App,
        id: builtins.str,
        *,
        applications: typing.Sequence["TargetApplication"],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param applications: (experimental) Application associator properties. Default: - Empty array.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf70fe013f8883665f67795a3e892e124b1c97eee77c8691a45e94a03fd3b3f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationAssociatorProps(applications=applications)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="associateStage")
    def associate_stage(
        self,
        stage: _aws_cdk_ceddda9d.Stage,
    ) -> _aws_cdk_ceddda9d.Stage:
        '''(experimental) Associate this application with the given stage.

        :param stage: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c562e37ce20cae0e25f66edcda715d4ced81af5946d6243931500bb560b566c)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        return typing.cast(_aws_cdk_ceddda9d.Stage, jsii.invoke(self, "associateStage", [stage]))

    @jsii.member(jsii_name="isStageAssociated")
    def is_stage_associated(self, stage: _aws_cdk_ceddda9d.Stage) -> builtins.bool:
        '''(experimental) Validates if a stage is already associated to the application.

        :param stage: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e907bed5984ca51a19f28a830c059d5147fb84b71013dd72756e86f116955fef)
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        return typing.cast(builtins.bool, jsii.invoke(self, "isStageAssociated", [stage]))

    @builtins.property
    @jsii.member(jsii_name="appRegistryApplication")
    def app_registry_application(self) -> "IApplication":
        '''(experimental) Get the AppRegistry application.

        :stability: experimental
        '''
        return typing.cast("IApplication", jsii.get(self, "appRegistryApplication"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.ApplicationAssociatorProps",
    jsii_struct_bases=[],
    name_mapping={"applications": "applications"},
)
class ApplicationAssociatorProps:
    def __init__(self, *, applications: typing.Sequence["TargetApplication"]) -> None:
        '''(experimental) Properties for Service Catalog AppRegistry Application Associator.

        :param applications: (experimental) Application associator properties. Default: - Empty array.

        :stability: experimental
        :exampleMetadata: infused

        Example::

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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30616d49bde91e4252f2107159acc6af6c7e69963df724abfd3d0e3887b7d07c)
            check_type(argname="argument applications", value=applications, expected_type=type_hints["applications"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "applications": applications,
        }

    @builtins.property
    def applications(self) -> typing.List["TargetApplication"]:
        '''(experimental) Application associator properties.

        :default: - Empty array.

        :stability: experimental
        '''
        result = self._values.get("applications")
        assert result is not None, "Required property 'applications' is missing"
        return typing.cast(typing.List["TargetApplication"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationAssociatorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.ApplicationProps",
    jsii_struct_bases=[],
    name_mapping={"application_name": "applicationName", "description": "description"},
)
class ApplicationProps:
    def __init__(
        self,
        *,
        application_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Service Catalog AppRegistry Application.

        :param application_name: (experimental) Enforces a particular physical application name.
        :param description: (experimental) Description for application. Default: - No description provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

            application = appreg.Application(self, "MyFirstApplication",
                application_name="MyFirstApplicationName",
                description="description for my application"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be7bfb8b322f2a1baa56fe1681c794a77811f78b07db4c1d82e108ccfd5d114)
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_name": application_name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def application_name(self) -> builtins.str:
        '''(experimental) Enforces a particular physical application name.

        :stability: experimental
        '''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for application.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.AttributeGroupAssociationProps",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_group_name": "attributeGroupName",
        "attributes": "attributes",
        "description": "description",
    },
)
class AttributeGroupAssociationProps:
    def __init__(
        self,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Service Catalog AppRegistry Attribute Group.

        :param attribute_group_name: (experimental) Name for attribute group.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8a31a208756b4841c915f0bb2b6daf73ce7e89ace38c60d6b8ae50bf54631b5)
            check_type(argname="argument attribute_group_name", value=attribute_group_name, expected_type=type_hints["attribute_group_name"])
            check_type(argname="argument attributes", value=attributes, expected_type=type_hints["attributes"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_group_name": attribute_group_name,
            "attributes": attributes,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def attribute_group_name(self) -> builtins.str:
        '''(experimental) Name for attribute group.

        :stability: experimental
        '''
        result = self._values.get("attribute_group_name")
        assert result is not None, "Required property 'attribute_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) A JSON of nested key-value pairs that represent the attributes in the group.

        Attributes maybe an empty JSON '{}', but must be explicitly stated.

        :stability: experimental
        '''
        result = self._values.get("attributes")
        assert result is not None, "Required property 'attributes' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for attribute group.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttributeGroupAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.AttributeGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_group_name": "attributeGroupName",
        "attributes": "attributes",
        "description": "description",
    },
)
class AttributeGroupProps:
    def __init__(
        self,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Service Catalog AppRegistry Attribute Group.

        :param attribute_group_name: (experimental) Enforces a particular physical attribute group name.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3622c2b8fdb683c749e737f012cde1fbfc02d34fadd8639e26812b7ef1494b30)
            check_type(argname="argument attribute_group_name", value=attribute_group_name, expected_type=type_hints["attribute_group_name"])
            check_type(argname="argument attributes", value=attributes, expected_type=type_hints["attributes"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute_group_name": attribute_group_name,
            "attributes": attributes,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def attribute_group_name(self) -> builtins.str:
        '''(experimental) Enforces a particular physical attribute group name.

        :stability: experimental
        '''
        result = self._values.get("attribute_group_name")
        assert result is not None, "Required property 'attribute_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) A JSON of nested key-value pairs that represent the attributes in the group.

        Attributes maybe an empty JSON '{}', but must be explicitly stated.

        :stability: experimental
        '''
        result = self._values.get("attributes")
        assert result is not None, "Required property 'attributes' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for attribute group.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttributeGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.BindTargetApplicationResult",
    jsii_struct_bases=[],
    name_mapping={
        "application": "application",
        "associate_cross_account_stacks": "associateCrossAccountStacks",
    },
)
class BindTargetApplicationResult:
    def __init__(
        self,
        *,
        application: "IApplication",
        associate_cross_account_stacks: builtins.bool,
    ) -> None:
        '''(experimental) Properties for Service Catalog AppRegistry Application Associator to work with.

        :param application: (experimental) Created or imported application.
        :param associate_cross_account_stacks: (experimental) Enables cross-account associations with the target application.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_servicecatalogappregistry_alpha as servicecatalogappregistry_alpha
            
            # application: servicecatalogappregistry_alpha.Application
            
            bind_target_application_result = servicecatalogappregistry_alpha.BindTargetApplicationResult(
                application=application,
                associate_cross_account_stacks=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49f1fbb4ffc705c29064e5565593f9a0e87b46c7dbf27ddfa01428e7ccb10675)
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument associate_cross_account_stacks", value=associate_cross_account_stacks, expected_type=type_hints["associate_cross_account_stacks"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application": application,
            "associate_cross_account_stacks": associate_cross_account_stacks,
        }

    @builtins.property
    def application(self) -> "IApplication":
        '''(experimental) Created or imported application.

        :stability: experimental
        '''
        result = self._values.get("application")
        assert result is not None, "Required property 'application' is missing"
        return typing.cast("IApplication", result)

    @builtins.property
    def associate_cross_account_stacks(self) -> builtins.bool:
        '''(experimental) Enables cross-account associations with the target application.

        :stability: experimental
        '''
        result = self._values.get("associate_cross_account_stacks")
        assert result is not None, "Required property 'associate_cross_account_stacks' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BindTargetApplicationResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.IApplication")
class IApplication(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) A Service Catalog AppRegistry Application.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addAttributeGroup")
    def add_attribute_group(
        self,
        id: builtins.str,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> "IAttributeGroup":
        '''(experimental) Create an attribute group and associate this application with the created attribute group.

        :param id: name of the AttributeGroup construct to be created.
        :param attribute_group_name: (experimental) Name for attribute group.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateAllStacksInScope")
    def associate_all_stacks_in_scope(
        self,
        construct: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Associate this application with all stacks under the construct node.

        NOTE: This method won't automatically register stacks under pipeline stages,
        and requires association of each pipeline stage by calling this method with stage Construct.

        :param construct: cdk Construct.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateApplicationWithStack")
    def associate_application_with_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(experimental) Associate a Cloudformation stack with the application in the given stack.

        :param stack: a CFN stack.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateAttributeGroup")
    def associate_attribute_group(self, attribute_group: "IAttributeGroup") -> None:
        '''(experimental) Associate this application with an attribute group.

        :param attribute_group: AppRegistry attribute group.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateStack")
    def associate_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(deprecated) Associate this application with a CloudFormation stack.

        :param stack: a CFN stack.

        :deprecated: Use ``associateApplicationWithStack`` instead.

        :stability: deprecated
        '''
        ...

    @jsii.member(jsii_name="shareApplication")
    def share_application(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, "SharePermission"]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) Share this application with other IAM entities, accounts, or OUs.

        :param id: The construct name for the share.
        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        ...


class _IApplicationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) A Service Catalog AppRegistry Application.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-servicecatalogappregistry-alpha.IApplication"

    @builtins.property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationName"))

    @jsii.member(jsii_name="addAttributeGroup")
    def add_attribute_group(
        self,
        id: builtins.str,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> "IAttributeGroup":
        '''(experimental) Create an attribute group and associate this application with the created attribute group.

        :param id: name of the AttributeGroup construct to be created.
        :param attribute_group_name: (experimental) Name for attribute group.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6e56523a23930a5302f7745145d7e79e64f84e5dda30d498f2444fd145b6471)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attribute_group_props = AttributeGroupAssociationProps(
            attribute_group_name=attribute_group_name,
            attributes=attributes,
            description=description,
        )

        return typing.cast("IAttributeGroup", jsii.invoke(self, "addAttributeGroup", [id, attribute_group_props]))

    @jsii.member(jsii_name="associateAllStacksInScope")
    def associate_all_stacks_in_scope(
        self,
        construct: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Associate this application with all stacks under the construct node.

        NOTE: This method won't automatically register stacks under pipeline stages,
        and requires association of each pipeline stage by calling this method with stage Construct.

        :param construct: cdk Construct.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb25bb53fbac36a075a6c682dbd5e647d5dd5b0436b1b1e29a37205679f60c97)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(None, jsii.invoke(self, "associateAllStacksInScope", [construct]))

    @jsii.member(jsii_name="associateApplicationWithStack")
    def associate_application_with_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(experimental) Associate a Cloudformation stack with the application in the given stack.

        :param stack: a CFN stack.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e92370f5ca96b4ac3a6918c6020df4c61044935affc14afe329d14f7b6cfc872)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(None, jsii.invoke(self, "associateApplicationWithStack", [stack]))

    @jsii.member(jsii_name="associateAttributeGroup")
    def associate_attribute_group(self, attribute_group: "IAttributeGroup") -> None:
        '''(experimental) Associate this application with an attribute group.

        :param attribute_group: AppRegistry attribute group.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013b061a2eaf66f5f2c454cad6c31f5138ef6eacf9ce64ea456c3acc549750b7)
            check_type(argname="argument attribute_group", value=attribute_group, expected_type=type_hints["attribute_group"])
        return typing.cast(None, jsii.invoke(self, "associateAttributeGroup", [attribute_group]))

    @jsii.member(jsii_name="associateStack")
    def associate_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(deprecated) Associate this application with a CloudFormation stack.

        :param stack: a CFN stack.

        :deprecated: Use ``associateApplicationWithStack`` instead.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6355fcb9bf431963c17f1d72e211e52e508a3bb085de7597c2deed4b88eda46f)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(None, jsii.invoke(self, "associateStack", [stack]))

    @jsii.member(jsii_name="shareApplication")
    def share_application(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, "SharePermission"]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) Share this application with other IAM entities, accounts, or OUs.

        :param id: The construct name for the share.
        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5b3f721ad9957880a449b41bb0776258353b84213884a6400b5578d59722790)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        share_options = ShareOptions(
            name=name,
            accounts=accounts,
            organization_arns=organization_arns,
            roles=roles,
            share_permission=share_permission,
            users=users,
        )

        return typing.cast(None, jsii.invoke(self, "shareApplication", [id, share_options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApplication).__jsii_proxy_class__ = lambda : _IApplicationProxy


@jsii.interface(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.IAttributeGroup"
)
class IAttributeGroup(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) A Service Catalog AppRegistry Attribute Group.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="attributeGroupArn")
    def attribute_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="attributeGroupId")
    def attribute_group_id(self) -> builtins.str:
        '''(experimental) The ID of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="associateWith")
    def associate_with(self, application: IApplication) -> None:
        '''(experimental) Associate an application with attribute group If the attribute group is already associated, it will ignore duplicate request.

        :param application: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="shareAttributeGroup")
    def share_attribute_group(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, "SharePermission"]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) Share the attribute group resource with other IAM entities, accounts, or OUs.

        :param id: The construct name for the share.
        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        ...


class _IAttributeGroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) A Service Catalog AppRegistry Attribute Group.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-servicecatalogappregistry-alpha.IAttributeGroup"

    @builtins.property
    @jsii.member(jsii_name="attributeGroupArn")
    def attribute_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="attributeGroupId")
    def attribute_group_id(self) -> builtins.str:
        '''(experimental) The ID of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupId"))

    @jsii.member(jsii_name="associateWith")
    def associate_with(self, application: IApplication) -> None:
        '''(experimental) Associate an application with attribute group If the attribute group is already associated, it will ignore duplicate request.

        :param application: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8deea2d110031fb5cbf4a6c6f8bcd29cdaf0f6f555ea3ec0b6f4af243a6e705)
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
        return typing.cast(None, jsii.invoke(self, "associateWith", [application]))

    @jsii.member(jsii_name="shareAttributeGroup")
    def share_attribute_group(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, "SharePermission"]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) Share the attribute group resource with other IAM entities, accounts, or OUs.

        :param id: The construct name for the share.
        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8527499e260d535a445a87b97e1ad8075918b7d3129ed6da2aa14e2d042a0da)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        share_options = ShareOptions(
            name=name,
            accounts=accounts,
            organization_arns=organization_arns,
            roles=roles,
            share_permission=share_permission,
            users=users,
        )

        return typing.cast(None, jsii.invoke(self, "shareAttributeGroup", [id, share_options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAttributeGroup).__jsii_proxy_class__ = lambda : _IAttributeGroupProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.ShareOptions",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "accounts": "accounts",
        "organization_arns": "organizationArns",
        "roles": "roles",
        "share_permission": "sharePermission",
        "users": "users",
    },
)
class ShareOptions:
    def __init__(
        self,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, "SharePermission"]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) The options that are passed into a share of an Application or Attribute Group.

        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        :exampleMetadata: infused

        Example::

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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f20907f839e03d66b58888eece0b2a80abd0c0240c29a95fb103642e09cbfa2e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument accounts", value=accounts, expected_type=type_hints["accounts"])
            check_type(argname="argument organization_arns", value=organization_arns, expected_type=type_hints["organization_arns"])
            check_type(argname="argument roles", value=roles, expected_type=type_hints["roles"])
            check_type(argname="argument share_permission", value=share_permission, expected_type=type_hints["share_permission"])
            check_type(argname="argument users", value=users, expected_type=type_hints["users"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if accounts is not None:
            self._values["accounts"] = accounts
        if organization_arns is not None:
            self._values["organization_arns"] = organization_arns
        if roles is not None:
            self._values["roles"] = roles
        if share_permission is not None:
            self._values["share_permission"] = share_permission
        if users is not None:
            self._values["users"] = users

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of the share.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of AWS accounts that the application will be shared with.

        :default: - No accounts specified for share

        :stability: experimental
        '''
        result = self._values.get("accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def organization_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with.

        :default: - No AWS Organizations or OUs specified for share

        :stability: experimental
        '''
        result = self._values.get("organization_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def roles(self) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]]:
        '''(experimental) A list of AWS IAM roles that the application will be shared with.

        :default: - No IAM roles specified for share

        :stability: experimental
        '''
        result = self._values.get("roles")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]], result)

    @builtins.property
    def share_permission(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, "SharePermission"]]:
        '''(experimental) An option to manage access to the application or attribute group.

        :default: - Principals will be assigned read only permissions on the application or attribute group.

        :stability: experimental
        '''
        result = self._values.get("share_permission")
        return typing.cast(typing.Optional[typing.Union[builtins.str, "SharePermission"]], result)

    @builtins.property
    def users(self) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IUser]]:
        '''(experimental) A list of AWS IAM users that the application will be shared with.

        :default: - No IAM Users specified for share

        :stability: experimental
        '''
        result = self._values.get("users")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IUser]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ShareOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.SharePermission")
class SharePermission(enum.Enum):
    '''(experimental) Supported permissions for sharing applications or attribute groups with principals using AWS RAM.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_iam as iam
        # application: appreg.Application
        
        application.share_application("MyShareId",
            name="MyShare",
            accounts=["123456789012", "234567890123"],
            share_permission=appreg.SharePermission.ALLOW_ACCESS
        )
    '''

    READ_ONLY = "READ_ONLY"
    '''(experimental) Allows principals in the share to only view the application or attribute group.

    :stability: experimental
    '''
    ALLOW_ACCESS = "ALLOW_ACCESS"
    '''(experimental) Allows principals in the share to associate resources and attribute groups with applications.

    :stability: experimental
    '''


class TargetApplication(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.TargetApplication",
):
    '''(experimental) Contains static factory methods with which you can build the input needed for application associator to work.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="createApplicationStack")
    @builtins.classmethod
    def create_application_stack(
        cls,
        *,
        application_name: builtins.str,
        application_description: typing.Optional[builtins.str] = None,
        emit_application_manager_url_as_output: typing.Optional[builtins.bool] = None,
        associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
        stack_id: typing.Optional[builtins.str] = None,
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
    ) -> "TargetApplication":
        '''(experimental) Factory method to build the input using the provided application name and stack props.

        :param application_name: (experimental) Enforces a particular physical application name.
        :param application_description: (experimental) Application description. Default: - Application containing stacks deployed via CDK.
        :param emit_application_manager_url_as_output: (experimental) Whether create cloudFormation Output for application manager URL. Default: - true
        :param associate_cross_account_stacks: (experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application. If set to ``true``, the application will first be shared with the accounts that own the stacks. Default: - false
        :param stack_id: (deprecated) Stack ID in which application will be created or imported. The id of a stack is also the identifier that you use to refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_. Default: - The value of ``stackName`` will be used as stack id
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
        options = CreateTargetApplicationOptions(
            application_name=application_name,
            application_description=application_description,
            emit_application_manager_url_as_output=emit_application_manager_url_as_output,
            associate_cross_account_stacks=associate_cross_account_stacks,
            stack_id=stack_id,
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

        return typing.cast("TargetApplication", jsii.sinvoke(cls, "createApplicationStack", [options]))

    @jsii.member(jsii_name="existingApplicationFromArn")
    @builtins.classmethod
    def existing_application_from_arn(
        cls,
        *,
        application_arn_value: builtins.str,
        associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
        stack_id: typing.Optional[builtins.str] = None,
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
    ) -> "TargetApplication":
        '''(experimental) Factory method to build the input using the provided application ARN.

        :param application_arn_value: (experimental) Enforces a particular application arn.
        :param associate_cross_account_stacks: (experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application. If set to ``true``, the application will first be shared with the accounts that own the stacks. Default: - false
        :param stack_id: (deprecated) Stack ID in which application will be created or imported. The id of a stack is also the identifier that you use to refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_. Default: - The value of ``stackName`` will be used as stack id
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
        options = ExistingTargetApplicationOptions(
            application_arn_value=application_arn_value,
            associate_cross_account_stacks=associate_cross_account_stacks,
            stack_id=stack_id,
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

        return typing.cast("TargetApplication", jsii.sinvoke(cls, "existingApplicationFromArn", [options]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> BindTargetApplicationResult:
        '''(experimental) Called when the ApplicationAssociator is initialized.

        :param scope: -

        :stability: experimental
        '''
        ...


class _TargetApplicationProxy(TargetApplication):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> BindTargetApplicationResult:
        '''(experimental) Called when the ApplicationAssociator is initialized.

        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__676c526376ea5a57da1d842b32eeaba48f39014bebf2de107e52abfb0ef30471)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(BindTargetApplicationResult, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, TargetApplication).__jsii_proxy_class__ = lambda : _TargetApplicationProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.TargetApplicationCommonOptions",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
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
        "associate_cross_account_stacks": "associateCrossAccountStacks",
        "stack_id": "stackId",
    },
)
class TargetApplicationCommonOptions(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
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
        associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
        stack_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties used to define targetapplication.

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
        :param associate_cross_account_stacks: (experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application. If set to ``true``, the application will first be shared with the accounts that own the stacks. Default: - false
        :param stack_id: (deprecated) Stack ID in which application will be created or imported. The id of a stack is also the identifier that you use to refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_. Default: - The value of ``stackName`` will be used as stack id

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_servicecatalogappregistry_alpha as servicecatalogappregistry_alpha
            import aws_cdk as cdk
            
            # permissions_boundary: cdk.PermissionsBoundary
            # property_injector: cdk.IPropertyInjector
            # stack_synthesizer: cdk.StackSynthesizer
            
            target_application_common_options = servicecatalogappregistry_alpha.TargetApplicationCommonOptions(
                analytics_reporting=False,
                associate_cross_account_stacks=False,
                cross_region_references=False,
                description="description",
                env=cdk.Environment(
                    account="account",
                    region="region"
                ),
                notification_arns=["notificationArns"],
                permissions_boundary=permissions_boundary,
                property_injectors=[property_injector],
                stack_id="stackId",
                stack_name="stackName",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e9a8c85d5db3b4596f192c3fe206a4e30e4143fb84b5be58ef7f29131edc782)
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
            check_type(argname="argument associate_cross_account_stacks", value=associate_cross_account_stacks, expected_type=type_hints["associate_cross_account_stacks"])
            check_type(argname="argument stack_id", value=stack_id, expected_type=type_hints["stack_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if associate_cross_account_stacks is not None:
            self._values["associate_cross_account_stacks"] = associate_cross_account_stacks
        if stack_id is not None:
            self._values["stack_id"] = stack_id

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
    def associate_cross_account_stacks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application.

        If set to ``true``, the application will first be shared with the accounts that own the stacks.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("associate_cross_account_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stack_id(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Stack ID in which application will be created or imported.

        The id of a stack is also the identifier that you use to
        refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_.

        :default: - The value of ``stackName`` will be used as stack id

        :deprecated: - Use ``stackName`` instead to control the name and id of the stack

        :stability: deprecated
        '''
        result = self._values.get("stack_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetApplicationCommonOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IApplication)
class Application(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.Application",
):
    '''(experimental) A Service Catalog AppRegistry Application.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        application = appreg.Application(self, "MyFirstApplication",
            application_name="MyFirstApplicationName",
            description="description for my application"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_name: (experimental) Enforces a particular physical application name.
        :param description: (experimental) Description for application. Default: - No description provided

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d00f48aa19f1be0379562df9ddbae70ebc3518362d0411437cb95dfcdd2d2163)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApplicationProps(
            application_name=application_name, description=description
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromApplicationArn")
    @builtins.classmethod
    def from_application_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        application_arn: builtins.str,
    ) -> IApplication:
        '''(experimental) Imports an Application construct that represents an external application.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param application_arn: the Amazon Resource Name of the existing AppRegistry Application.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9f55f3016c1743f9bf17bd3321531f86b5a2fcff42b5b44073089b900c1bc3e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument application_arn", value=application_arn, expected_type=type_hints["application_arn"])
        return typing.cast(IApplication, jsii.sinvoke(cls, "fromApplicationArn", [scope, id, application_arn]))

    @jsii.member(jsii_name="addAttributeGroup")
    def add_attribute_group(
        self,
        id: builtins.str,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> IAttributeGroup:
        '''(experimental) Create an attribute group and associate this application with the created attribute group.

        :param id: -
        :param attribute_group_name: (experimental) Name for attribute group.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d313645bc5dac0eb81e5ee1b777e6cfb17ba542f778305a7e308999d286c8e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AttributeGroupAssociationProps(
            attribute_group_name=attribute_group_name,
            attributes=attributes,
            description=description,
        )

        return typing.cast(IAttributeGroup, jsii.invoke(self, "addAttributeGroup", [id, props]))

    @jsii.member(jsii_name="associateAllStacksInScope")
    def associate_all_stacks_in_scope(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''(experimental) Associate all stacks present in construct's aspect with application, including cross-account stacks.

        NOTE: This method won't automatically register stacks under pipeline stages,
        and requires association of each pipeline stage by calling this method with stage Construct.

        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c009ad74ae52d87dcfb6e1aee6e9569d5807c9f2c9f0bc6691cc089dacece4a8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(None, jsii.invoke(self, "associateAllStacksInScope", [scope]))

    @jsii.member(jsii_name="associateApplicationWithStack")
    def associate_application_with_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(experimental) Associate stack with the application in the stack passed as parameter.

        A stack can only be associated with one application.

        :param stack: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__875f08936c5ec9d623a247709774d3625560a74cad5380509cb4624eecad2f27)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(None, jsii.invoke(self, "associateApplicationWithStack", [stack]))

    @jsii.member(jsii_name="associateAttributeGroup")
    def associate_attribute_group(self, attribute_group: IAttributeGroup) -> None:
        '''(deprecated) Associate an attribute group with application If the attribute group is already associated, it will ignore duplicate request.

        :param attribute_group: -

        :deprecated: Use ``AttributeGroup.associateWith`` instead.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e09d5799ecd5be55b6bce6f34e72f3f0d7d0c179ac0824b4e961e49687e3871)
            check_type(argname="argument attribute_group", value=attribute_group, expected_type=type_hints["attribute_group"])
        return typing.cast(None, jsii.invoke(self, "associateAttributeGroup", [attribute_group]))

    @jsii.member(jsii_name="associateStack")
    def associate_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> None:
        '''(deprecated) Associate a stack with the application If the resource is already associated, it will ignore duplicate request.

        A stack can only be associated with one application.

        :param stack: -

        :deprecated: Use ``associateApplicationWithStack`` instead.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09e36e72eb27ec19021721817f2caa31bde7114fd6069eedbb069641910066e0)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(None, jsii.invoke(self, "associateStack", [stack]))

    @jsii.member(jsii_name="generateUniqueHash")
    def _generate_unique_hash(self, resource_address: builtins.str) -> builtins.str:
        '''(experimental) Create a unique id.

        :param resource_address: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80266c77c192e878af5d982db7685162f1f646d9574aad4d8a432ef62520b1ab)
            check_type(argname="argument resource_address", value=resource_address, expected_type=type_hints["resource_address"])
        return typing.cast(builtins.str, jsii.invoke(self, "generateUniqueHash", [resource_address]))

    @jsii.member(jsii_name="shareApplication")
    def share_application(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) Share an application with accounts, organizations and OUs, and IAM roles and users.

        The application will become available to end users within those principals.

        :param id: The construct name for the share.
        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__005627e01baaa24d6e68e7eda178c3e444c916edf3f6d4db40130b203601246f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        share_options = ShareOptions(
            name=name,
            accounts=accounts,
            organization_arns=organization_arns,
            roles=roles,
            share_permission=share_permission,
            users=users,
        )

        return typing.cast(None, jsii.invoke(self, "shareApplication", [id, share_options]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @builtins.property
    @jsii.member(jsii_name="applicationManagerUrl")
    def application_manager_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Application manager URL for the Application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationManagerUrl"))

    @builtins.property
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the application.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationName"))


@jsii.implements(IAttributeGroup)
class AttributeGroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.AttributeGroup",
):
    '''(experimental) A Service Catalog AppRegistry Attribute Group.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param attribute_group_name: (experimental) Enforces a particular physical attribute group name.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91ce42b356b8555b9df82de3713a41ca962e33062b181b37794c5e3b82d7b12f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AttributeGroupProps(
            attribute_group_name=attribute_group_name,
            attributes=attributes,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAttributeGroupArn")
    @builtins.classmethod
    def from_attribute_group_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        attribute_group_arn: builtins.str,
    ) -> IAttributeGroup:
        '''(experimental) Imports an attribute group construct that represents an external attribute group.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param attribute_group_arn: the Amazon Resource Name of the existing AppRegistry attribute group.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d090f29cba3280a4ce331eeac9f6003b4c6b25cc65422ee58257d036241687aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument attribute_group_arn", value=attribute_group_arn, expected_type=type_hints["attribute_group_arn"])
        return typing.cast(IAttributeGroup, jsii.sinvoke(cls, "fromAttributeGroupArn", [scope, id, attribute_group_arn]))

    @jsii.member(jsii_name="associateWith")
    def associate_with(self, application: IApplication) -> None:
        '''(experimental) Associate an application with attribute group If the attribute group is already associated, it will ignore duplicate request.

        :param application: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb2739d20384742c58279649b10f27ec2378888080e5e70f7095f650366edaa)
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
        return typing.cast(None, jsii.invoke(self, "associateWith", [application]))

    @jsii.member(jsii_name="generateUniqueHash")
    def _generate_unique_hash(self, resource_address: builtins.str) -> builtins.str:
        '''(experimental) Create a unique hash.

        :param resource_address: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6056779cdba1398ba21a85efe380ab878cc63756ae242884454f73e4197ec40)
            check_type(argname="argument resource_address", value=resource_address, expected_type=type_hints["resource_address"])
        return typing.cast(builtins.str, jsii.invoke(self, "generateUniqueHash", [resource_address]))

    @jsii.member(jsii_name="getAttributeGroupSharePermissionARN")
    def _get_attribute_group_share_permission_arn(
        self,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> builtins.str:
        '''(experimental) Get the correct permission ARN based on the SharePermission.

        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        share_options = ShareOptions(
            name=name,
            accounts=accounts,
            organization_arns=organization_arns,
            roles=roles,
            share_permission=share_permission,
            users=users,
        )

        return typing.cast(builtins.str, jsii.invoke(self, "getAttributeGroupSharePermissionARN", [share_options]))

    @jsii.member(jsii_name="shareAttributeGroup")
    def share_attribute_group(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
        users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
    ) -> None:
        '''(experimental) Share the attribute group resource with other IAM entities, accounts, or OUs.

        :param id: -
        :param name: (experimental) Name of the share.
        :param accounts: (experimental) A list of AWS accounts that the application will be shared with. Default: - No accounts specified for share
        :param organization_arns: (experimental) A list of AWS Organization or Organizational Units (OUs) ARNs that the application will be shared with. Default: - No AWS Organizations or OUs specified for share
        :param roles: (experimental) A list of AWS IAM roles that the application will be shared with. Default: - No IAM roles specified for share
        :param share_permission: (experimental) An option to manage access to the application or attribute group. Default: - Principals will be assigned read only permissions on the application or attribute group.
        :param users: (experimental) A list of AWS IAM users that the application will be shared with. Default: - No IAM Users specified for share

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffb9721cdfd83ff81e1e45f6b9baea8c4e0299de4717e6ca56ef6d07b78b3729)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        share_options = ShareOptions(
            name=name,
            accounts=accounts,
            organization_arns=organization_arns,
            roles=roles,
            share_permission=share_permission,
            users=users,
        )

        return typing.cast(None, jsii.invoke(self, "shareAttributeGroup", [id, share_options]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="attributeGroupArn")
    def attribute_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attribute group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="attributeGroupId")
    def attribute_group_id(self) -> builtins.str:
        '''(experimental) The ID of the attribute group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.CreateTargetApplicationOptions",
    jsii_struct_bases=[TargetApplicationCommonOptions],
    name_mapping={
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
        "associate_cross_account_stacks": "associateCrossAccountStacks",
        "stack_id": "stackId",
        "application_name": "applicationName",
        "application_description": "applicationDescription",
        "emit_application_manager_url_as_output": "emitApplicationManagerUrlAsOutput",
    },
)
class CreateTargetApplicationOptions(TargetApplicationCommonOptions):
    def __init__(
        self,
        *,
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
        associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
        stack_id: typing.Optional[builtins.str] = None,
        application_name: builtins.str,
        application_description: typing.Optional[builtins.str] = None,
        emit_application_manager_url_as_output: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties used to define New TargetApplication.

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
        :param associate_cross_account_stacks: (experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application. If set to ``true``, the application will first be shared with the accounts that own the stacks. Default: - false
        :param stack_id: (deprecated) Stack ID in which application will be created or imported. The id of a stack is also the identifier that you use to refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_. Default: - The value of ``stackName`` will be used as stack id
        :param application_name: (experimental) Enforces a particular physical application name.
        :param application_description: (experimental) Application description. Default: - Application containing stacks deployed via CDK.
        :param emit_application_manager_url_as_output: (experimental) Whether create cloudFormation Output for application manager URL. Default: - true

        :stability: experimental
        :exampleMetadata: infused

        Example::

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
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed0057efe5c9760fa6e858501ef3eab5baeb0561c53a3dd7c2e611aed0aa51d)
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
            check_type(argname="argument associate_cross_account_stacks", value=associate_cross_account_stacks, expected_type=type_hints["associate_cross_account_stacks"])
            check_type(argname="argument stack_id", value=stack_id, expected_type=type_hints["stack_id"])
            check_type(argname="argument application_name", value=application_name, expected_type=type_hints["application_name"])
            check_type(argname="argument application_description", value=application_description, expected_type=type_hints["application_description"])
            check_type(argname="argument emit_application_manager_url_as_output", value=emit_application_manager_url_as_output, expected_type=type_hints["emit_application_manager_url_as_output"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_name": application_name,
        }
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
        if associate_cross_account_stacks is not None:
            self._values["associate_cross_account_stacks"] = associate_cross_account_stacks
        if stack_id is not None:
            self._values["stack_id"] = stack_id
        if application_description is not None:
            self._values["application_description"] = application_description
        if emit_application_manager_url_as_output is not None:
            self._values["emit_application_manager_url_as_output"] = emit_application_manager_url_as_output

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
    def associate_cross_account_stacks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application.

        If set to ``true``, the application will first be shared with the accounts that own the stacks.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("associate_cross_account_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stack_id(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Stack ID in which application will be created or imported.

        The id of a stack is also the identifier that you use to
        refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_.

        :default: - The value of ``stackName`` will be used as stack id

        :deprecated: - Use ``stackName`` instead to control the name and id of the stack

        :stability: deprecated
        '''
        result = self._values.get("stack_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_name(self) -> builtins.str:
        '''(experimental) Enforces a particular physical application name.

        :stability: experimental
        '''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Application description.

        :default: - Application containing stacks deployed via CDK.

        :stability: experimental
        '''
        result = self._values.get("application_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def emit_application_manager_url_as_output(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether create cloudFormation Output for application manager URL.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("emit_application_manager_url_as_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateTargetApplicationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.ExistingTargetApplicationOptions",
    jsii_struct_bases=[TargetApplicationCommonOptions],
    name_mapping={
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
        "associate_cross_account_stacks": "associateCrossAccountStacks",
        "stack_id": "stackId",
        "application_arn_value": "applicationArnValue",
    },
)
class ExistingTargetApplicationOptions(TargetApplicationCommonOptions):
    def __init__(
        self,
        *,
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
        associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
        stack_id: typing.Optional[builtins.str] = None,
        application_arn_value: builtins.str,
    ) -> None:
        '''(experimental) Properties used to define Existing TargetApplication.

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
        :param associate_cross_account_stacks: (experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application. If set to ``true``, the application will first be shared with the accounts that own the stacks. Default: - false
        :param stack_id: (deprecated) Stack ID in which application will be created or imported. The id of a stack is also the identifier that you use to refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_. Default: - The value of ``stackName`` will be used as stack id
        :param application_arn_value: (experimental) Enforces a particular application arn.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            app = App()
            associated_app = appreg.ApplicationAssociator(app, "AssociatedApplication",
                applications=[appreg.TargetApplication.existing_application_from_arn(
                    application_arn_value="arn:aws:servicecatalog:us-east-1:123456789012:/applications/applicationId",
                    stack_name="MyAssociatedApplicationStack"
                )]
            )
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__346e88991c2535a9b273e7054098c865f76770acd250aee2bc0348d5774c686e)
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
            check_type(argname="argument associate_cross_account_stacks", value=associate_cross_account_stacks, expected_type=type_hints["associate_cross_account_stacks"])
            check_type(argname="argument stack_id", value=stack_id, expected_type=type_hints["stack_id"])
            check_type(argname="argument application_arn_value", value=application_arn_value, expected_type=type_hints["application_arn_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_arn_value": application_arn_value,
        }
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
        if associate_cross_account_stacks is not None:
            self._values["associate_cross_account_stacks"] = associate_cross_account_stacks
        if stack_id is not None:
            self._values["stack_id"] = stack_id

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
    def associate_cross_account_stacks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines whether any cross-account stacks defined in the CDK app definition should be associated with the target application.

        If set to ``true``, the application will first be shared with the accounts that own the stacks.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("associate_cross_account_stacks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stack_id(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Stack ID in which application will be created or imported.

        The id of a stack is also the identifier that you use to
        refer to it in the `AWS CDK Toolkit <https://docs.aws.amazon.com/cdk/v2/guide/cli.html>`_.

        :default: - The value of ``stackName`` will be used as stack id

        :deprecated: - Use ``stackName`` instead to control the name and id of the stack

        :stability: deprecated
        '''
        result = self._values.get("stack_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_arn_value(self) -> builtins.str:
        '''(experimental) Enforces a particular application arn.

        :stability: experimental
        '''
        result = self._values.get("application_arn_value")
        assert result is not None, "Required property 'application_arn_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExistingTargetApplicationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Application",
    "ApplicationAssociator",
    "ApplicationAssociatorProps",
    "ApplicationProps",
    "AttributeGroup",
    "AttributeGroupAssociationProps",
    "AttributeGroupProps",
    "BindTargetApplicationResult",
    "CreateTargetApplicationOptions",
    "ExistingTargetApplicationOptions",
    "IApplication",
    "IAttributeGroup",
    "ShareOptions",
    "SharePermission",
    "TargetApplication",
    "TargetApplicationCommonOptions",
]

publication.publish()

def _typecheckingstub__fdf70fe013f8883665f67795a3e892e124b1c97eee77c8691a45e94a03fd3b3f(
    scope: _aws_cdk_ceddda9d.App,
    id: builtins.str,
    *,
    applications: typing.Sequence[TargetApplication],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c562e37ce20cae0e25f66edcda715d4ced81af5946d6243931500bb560b566c(
    stage: _aws_cdk_ceddda9d.Stage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e907bed5984ca51a19f28a830c059d5147fb84b71013dd72756e86f116955fef(
    stage: _aws_cdk_ceddda9d.Stage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30616d49bde91e4252f2107159acc6af6c7e69963df724abfd3d0e3887b7d07c(
    *,
    applications: typing.Sequence[TargetApplication],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be7bfb8b322f2a1baa56fe1681c794a77811f78b07db4c1d82e108ccfd5d114(
    *,
    application_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8a31a208756b4841c915f0bb2b6daf73ce7e89ace38c60d6b8ae50bf54631b5(
    *,
    attribute_group_name: builtins.str,
    attributes: typing.Mapping[builtins.str, typing.Any],
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3622c2b8fdb683c749e737f012cde1fbfc02d34fadd8639e26812b7ef1494b30(
    *,
    attribute_group_name: builtins.str,
    attributes: typing.Mapping[builtins.str, typing.Any],
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49f1fbb4ffc705c29064e5565593f9a0e87b46c7dbf27ddfa01428e7ccb10675(
    *,
    application: IApplication,
    associate_cross_account_stacks: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6e56523a23930a5302f7745145d7e79e64f84e5dda30d498f2444fd145b6471(
    id: builtins.str,
    *,
    attribute_group_name: builtins.str,
    attributes: typing.Mapping[builtins.str, typing.Any],
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb25bb53fbac36a075a6c682dbd5e647d5dd5b0436b1b1e29a37205679f60c97(
    construct: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e92370f5ca96b4ac3a6918c6020df4c61044935affc14afe329d14f7b6cfc872(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013b061a2eaf66f5f2c454cad6c31f5138ef6eacf9ce64ea456c3acc549750b7(
    attribute_group: IAttributeGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6355fcb9bf431963c17f1d72e211e52e508a3bb085de7597c2deed4b88eda46f(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b3f721ad9957880a449b41bb0776258353b84213884a6400b5578d59722790(
    id: builtins.str,
    *,
    name: builtins.str,
    accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
    users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8deea2d110031fb5cbf4a6c6f8bcd29cdaf0f6f555ea3ec0b6f4af243a6e705(
    application: IApplication,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8527499e260d535a445a87b97e1ad8075918b7d3129ed6da2aa14e2d042a0da(
    id: builtins.str,
    *,
    name: builtins.str,
    accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
    users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f20907f839e03d66b58888eece0b2a80abd0c0240c29a95fb103642e09cbfa2e(
    *,
    name: builtins.str,
    accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
    users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__676c526376ea5a57da1d842b32eeaba48f39014bebf2de107e52abfb0ef30471(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e9a8c85d5db3b4596f192c3fe206a4e30e4143fb84b5be58ef7f29131edc782(
    *,
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
    associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
    stack_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d00f48aa19f1be0379562df9ddbae70ebc3518362d0411437cb95dfcdd2d2163(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9f55f3016c1743f9bf17bd3321531f86b5a2fcff42b5b44073089b900c1bc3e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    application_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d313645bc5dac0eb81e5ee1b777e6cfb17ba542f778305a7e308999d286c8e(
    id: builtins.str,
    *,
    attribute_group_name: builtins.str,
    attributes: typing.Mapping[builtins.str, typing.Any],
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c009ad74ae52d87dcfb6e1aee6e9569d5807c9f2c9f0bc6691cc089dacece4a8(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__875f08936c5ec9d623a247709774d3625560a74cad5380509cb4624eecad2f27(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e09d5799ecd5be55b6bce6f34e72f3f0d7d0c179ac0824b4e961e49687e3871(
    attribute_group: IAttributeGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09e36e72eb27ec19021721817f2caa31bde7114fd6069eedbb069641910066e0(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80266c77c192e878af5d982db7685162f1f646d9574aad4d8a432ef62520b1ab(
    resource_address: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__005627e01baaa24d6e68e7eda178c3e444c916edf3f6d4db40130b203601246f(
    id: builtins.str,
    *,
    name: builtins.str,
    accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
    users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91ce42b356b8555b9df82de3713a41ca962e33062b181b37794c5e3b82d7b12f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    attribute_group_name: builtins.str,
    attributes: typing.Mapping[builtins.str, typing.Any],
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d090f29cba3280a4ce331eeac9f6003b4c6b25cc65422ee58257d036241687aa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    attribute_group_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb2739d20384742c58279649b10f27ec2378888080e5e70f7095f650366edaa(
    application: IApplication,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6056779cdba1398ba21a85efe380ab878cc63756ae242884454f73e4197ec40(
    resource_address: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffb9721cdfd83ff81e1e45f6b9baea8c4e0299de4717e6ca56ef6d07b78b3729(
    id: builtins.str,
    *,
    name: builtins.str,
    accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    organization_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    share_permission: typing.Optional[typing.Union[builtins.str, SharePermission]] = None,
    users: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IUser]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed0057efe5c9760fa6e858501ef3eab5baeb0561c53a3dd7c2e611aed0aa51d(
    *,
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
    associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
    stack_id: typing.Optional[builtins.str] = None,
    application_name: builtins.str,
    application_description: typing.Optional[builtins.str] = None,
    emit_application_manager_url_as_output: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__346e88991c2535a9b273e7054098c865f76770acd250aee2bc0348d5774c686e(
    *,
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
    associate_cross_account_stacks: typing.Optional[builtins.bool] = None,
    stack_id: typing.Optional[builtins.str] = None,
    application_arn_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
