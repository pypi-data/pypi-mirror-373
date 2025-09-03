# AWS Cloud9 Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

AWS Cloud9 is a cloud-based integrated development environment (IDE) that lets you write, run, and debug your code with just a
browser. It includes a code editor, debugger, and terminal. Cloud9 comes prepackaged with essential tools for popular
programming languages, including JavaScript, Python, PHP, and more, so you don’t need to install files or configure your
development machine to start new projects. Since your Cloud9 IDE is cloud-based, you can work on your projects from your
office, home, or anywhere using an internet-connected machine. Cloud9 also provides a seamless experience for developing
serverless applications enabling you to easily define resources, debug, and switch between local and remote execution of
serverless applications. With Cloud9, you can quickly share your development environment with your team, enabling you to pair
program and track each other's inputs in real time.

## Creating EC2 Environment

EC2 Environments are defined with `Ec2Environment`. To create an EC2 environment in the private subnet, specify
`subnetSelection` with private `subnetType`.

```python
# create a cloud9 ec2 environment in a new VPC
vpc = ec2.Vpc(self, "VPC", max_azs=3)
cloud9.Ec2Environment(self, "Cloud9Env", vpc=vpc, image_id=cloud9.ImageId.AMAZON_LINUX_2)

# or create the cloud9 environment in the default VPC with specific instanceType
default_vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
cloud9.Ec2Environment(self, "Cloud9Env2",
    vpc=default_vpc,
    instance_type=ec2.InstanceType("t3.large"),
    image_id=cloud9.ImageId.AMAZON_LINUX_2
)

# or specify in a different subnetSelection
c9env = cloud9.Ec2Environment(self, "Cloud9Env3",
    vpc=vpc,
    subnet_selection=ec2.SubnetSelection(
        subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
    ),
    image_id=cloud9.ImageId.AMAZON_LINUX_2
)

# print the Cloud9 IDE URL in the output
CfnOutput(self, "URL", value=c9env.ide_url)
```

## Specifying EC2 AMI

Use `imageId` to specify the EC2 AMI image to be used:

```python
default_vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
cloud9.Ec2Environment(self, "Cloud9Env2",
    vpc=default_vpc,
    instance_type=ec2.InstanceType("t3.large"),
    image_id=cloud9.ImageId.UBUNTU_18_04
)
```

## Cloning Repositories

Use `clonedRepositories` to clone one or multiple AWS Codecommit repositories into the environment:

```python
import aws_cdk.aws_codecommit as codecommit

# create a new Cloud9 environment and clone the two repositories
# vpc: ec2.Vpc


# create a codecommit repository to clone into the cloud9 environment
repo_new = codecommit.Repository(self, "RepoNew",
    repository_name="new-repo"
)

# import an existing codecommit repository to clone into the cloud9 environment
repo_existing = codecommit.Repository.from_repository_name(self, "RepoExisting", "existing-repo")
cloud9.Ec2Environment(self, "C9Env",
    vpc=vpc,
    cloned_repositories=[
        cloud9.CloneRepository.from_code_commit(repo_new, "/src/new-repo"),
        cloud9.CloneRepository.from_code_commit(repo_existing, "/src/existing-repo")
    ],
    image_id=cloud9.ImageId.AMAZON_LINUX_2
)
```

## Specifying Owners

Every Cloud9 Environment has an **owner**. An owner has full control over the environment, and can invite additional members to the environment for collaboration purposes. For more information, see [Working with shared environments in AWS Cloud9](https://docs.aws.amazon.com/cloud9/latest/user-guide/share-environment.html)).

By default, the owner will be the identity that creates the Environment, which is most likely your CloudFormation Execution Role when the Environment is created using CloudFormation. Provider a value for the `owner` property to assign a different owner, either a specific IAM User or the AWS Account Root User.

`Owner` is an IAM entity that owns a Cloud9 environment. `Owner` has their own access permissions, and resources. You can specify an `Owner`in an EC2 environment which could be of the following types:

1. Account Root
2. IAM User
3. IAM Federated User
4. IAM Assumed Role

The ARN of the owner must satisfy the following regular expression: `^arn:(aws|aws-cn|aws-us-gov|aws-iso|aws-iso-b):(iam|sts)::\d+:(root|(user\/[\w+=/:,.@-]{1,64}|federated-user\/[\w+=/:,.@-]{2,32}|assumed-role\/[\w+=:,.@-]{1,64}\/[\w+=,.@-]{1,64}))$`

Note: Using the account root user is not recommended, see [environment sharing best practices](https://docs.aws.amazon.com/cloud9/latest/user-guide/share-environment.html#share-environment-best-practices).

To specify the AWS Account Root User as the environment owner, use `Owner.accountRoot()`

```python
# vpc: ec2.Vpc

cloud9.Ec2Environment(self, "C9Env",
    vpc=vpc,
    image_id=cloud9.ImageId.AMAZON_LINUX_2,
    owner=cloud9.Owner.account_root("111111111")
)
```

To specify a specific IAM User as the environment owner, use `Owner.user()`. The user should have the `AWSCloud9Administrator` managed policy

The user should have the `AWSCloud9User` (preferred) or `AWSCloud9Administrator` managed policy attached.

```python
import aws_cdk.aws_iam as iam
# vpc: ec2.Vpc


user = iam.User(self, "user")
user.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloud9Administrator"))
cloud9.Ec2Environment(self, "C9Env",
    vpc=vpc,
    image_id=cloud9.ImageId.AMAZON_LINUX_2,

    owner=cloud9.Owner.user(user)
)
```

To specify a specific IAM Federated User as the environment owner, use `Owner.federatedUser(accountId, userName)`.

The user should have the `AWSCloud9User` (preferred) or `AWSCloud9Administrator` managed policy attached.

```python
import aws_cdk.aws_iam as iam

# vpc: ec2.Vpc

cloud9.Ec2Environment(self, "C9Env",
    vpc=vpc,
    image_id=cloud9.ImageId.AMAZON_LINUX_2,
    owner=cloud9.Owner.federated_user(Stack.of(self).account, "Admin/johndoe")
)
```

To specify an IAM Assumed Role as the environment owner, use `Owner.assumedRole(accountId: string, roleName: string)`.

The role should have the `AWSCloud9User` (preferred) or `AWSCloud9Administrator` managed policy attached.

```python
import aws_cdk.aws_iam as iam

# vpc: ec2.Vpc

cloud9.Ec2Environment(self, "C9Env",
    vpc=vpc,
    image_id=cloud9.ImageId.AMAZON_LINUX_2,
    owner=cloud9.Owner.assumed_role(Stack.of(self).account, "Admin/johndoe-role")
)
```

## Auto-Hibernation

A Cloud9 environment can automatically start and stop the associated EC2 instance to reduce costs.

Use `automaticStop` to specify the number of minutes until the running instance is shut down after the environment was last used.

```python
default_vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
cloud9.Ec2Environment(self, "Cloud9Env2",
    vpc=default_vpc,
    image_id=cloud9.ImageId.AMAZON_LINUX_2,
    automatic_stop=Duration.minutes(30)
)
```
