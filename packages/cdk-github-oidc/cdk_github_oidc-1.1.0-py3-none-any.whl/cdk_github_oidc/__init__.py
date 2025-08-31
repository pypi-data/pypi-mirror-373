r'''
# `@blimmer/cdk-github-oidc`

A CDK construct library that enables secure authentication between GitHub Actions and AWS using OpenID Connect (OIDC).
This eliminates the need for long-lived AWS credentials in your GitHub repositories.

## What is OIDC?

OIDC (OpenID Connect) allows GitHub Actions to authenticate directly with AWS using short-lived tokens instead of
storing AWS credentials. The process is described in
[GitHub's documentation](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect).

## Security Benefits

Using OIDC for GitHub Actions authentication:

* Eliminates the need to store AWS credentials as GitHub secrets
* Provides short-lived, automatically rotated credentials
* Enables fine-grained access control based on repository, branch, environment, or other conditions
* Follows security best practices for cloud access

## Installation

### Node.js

```shell
npm install --save @blimmer/cdk-github-oidc
```

or

```shell
yarn add @blimmer/cdk-github-oidc
```

### Python

```bash
pip install cdk-github-oidc
```

For Python, see [below](#python).

### Create or Import a Provider

Each AWS account must be bootstrapped with a single OIDC provider.

To create it in your stack, use the `GithubActionsIdentityProvider` construct.

```python
import { GithubActionsIdentityProvider } from "@blimmer/cdk-github-oidc";

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const provider = new GithubActionsIdentityProvider(this, "Provider");
  }
}
```

Or, if another stack created the provider, you can import it using the `GithubActionsIdentityProvider.fromAccount()`
method.

```python
import { GithubActionsIdentityProvider } from "@blimmer/cdk-github-oidc";

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const provider = GithubActionsIdentityProvider.fromAccount(this);
  }
}
```

### Create a Role

Once you have a handle to a provider, you can create a role assumed by GitHub Actions. You grant this role permission to
access the resources/APIs you need (more on that [below](#granting-permissions-to-the-role)).

```python
import { GithubActionsRole, GithubActionsIdentityProvider, BranchFilter } from "@blimmer/cdk-github-oidc";

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const provider = new GithubActionsIdentityProvider(this, "Provider");

    const role = new GithubActionsRole(this, "Role", {
      provider,
      roleName: "my-github-actions-role",
      description: "Role assumed by GitHub Actions",
      subjectFilters: [new BranchFilter({ owner: "blimmer", repository: "cdk-github-oidc", branch: "*" })],
    });
  }
}
```

### Subject Filters

You must pass one or more `SubjectFilter`s to the `GithubActionsRole` construct. These filters are used to determine
which GitHub Actions workflows can assume the role.

This construct exposes first class support for the following filters:

* [`AllowAllFilter`](/API.md#allowallfilter)

  ```python
  // Allow all branches, tags, environments, pull requests, etc.
  new AllowAllFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
  });
  ```
* [`BranchFilter`](/API.md#branchfilter)

  ```python
  // Allow all branches
  new BranchFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    branch: "*",
  });

  // Specify a branch
  new BranchFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    branch: "main",
  });

  // Specify a branch pattern
  new BranchFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    branch: "feature/*",
  });
  ```
* [`TagFilter`](/API.md#tagfilter)

  ```python
  // Allow all tags
  new TagFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    tag: "*",
  });

  // Specify a tag
  new TagFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    tag: "v1.0.0",
  });

  // Specify a tag pattern
  new TagFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    tag: "v1.*",
  });
  ```
* [`EnvironmentFilter`](/API.md#environmentfilter)

  ```python
  // Allow all environments
  new EnvironmentFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    environment: "*",
  });

  // Specify an environment
  new EnvironmentFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
    environment: "staging",
  });
  ```
* [`PullRequestFilter`](/API.md#pullrequestfilter)

  ```python
  // Allow all pull requests
  new PullRequestFilter({
    owner: "blimmer",
    repository: "cdk-github-oidc",
  });
  ```

If none of these filters fit your use case, you can implement your own via the
[`IGithubActionOidcFilter`](/API.md#igithubactionoidcfilter) interface, or use the
[`CustomFilter`](/API.md#customfilter) construct.

You can learn more about subject filters in the
[Github docs](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#configuring-the-subject-in-your-cloud-provider)

### Granting Permissions to the Role

The `GithubActionsRole` construct *is a* `Role` construct, so you can use all of the same properties and methods as you
would with a normal
[CDK IAM `Role` construct](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html).

```python
import { GithubActionsRole, GithubActionsIdentityProvider, BranchFilter } from "@blimmer/cdk-github-oidc";
import { Bucket } from "aws-cdk-lib/aws-s3";
import { PolicyStatement } from "aws-cdk-lib/aws-iam";

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const bucket = new Bucket(this, "Bucket");

    const provider = new GithubActionsIdentityProvider(this, "Provider");
    const role = new GithubActionsRole(this, "Role", {
      provider,
      roleName: "my-github-actions-role",
      description: "Role assumed by GitHub Actions",
      subjectFilters: [
        new BranchFilter({
          owner: "blimmer",
          repository: "cdk-github-oidc",
          branch: "*",
        }),
      ],
    });

    // Grant access via CDK `grant*` methods
    // https://docs.aws.amazon.com/cdk/v2/guide/permissions.html#permissions_grants
    role.grantReadWrite(bucket);

    // Add a custom policy
    role.addToPolicy(
      new PolicyStatement({
        actions: ["s3:PutObject"],
        resources: ["arn:aws:s3:::my-bucket/*"],
      }),
    );
  }
}
```

### Using a Role in a Workflow

To use a role in a GitHub Actions workflow, you can use the `aws-actions/configure-aws-credentials` action.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write # Required for OIDC role assumption
    steps:
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/my-github-actions-role
          region: us-west-2
```

See [the `aws-actions/configure-aws-credentials` docs](https://github.com/aws-actions/configure-aws-credentials) for
more details.

## Usage

For detailed API docs, see [API.md](/API.md).

## Troubleshooting

### Common Issues

1. **Role assumption fails**: Ensure your GitHub Action has the required permissions:

```yaml
permissions:
  id-token: write # Required for OIDC
  contents: read # Required for checking out code
```

1. **Provider already exists**: Only one OIDC provider can exist per AWS account. Use
   `GithubActionsIdentityProvider.fromAccount()` if one already exists.
2. **Subject filter not matching**: Double check your subject filter configuration matches your GitHub workflow context.
   Use logging to debug the actual subject string being provided.

## Migrating from `aws-cdk-github-oidc`

This package was inspired by [`aws-cdk-github-oidc`](https://github.com/aripalo/aws-cdk-github-oidc), but that package
became unmaintained.

For a role that looked like this in `aws-cdk-github-oidc`:

```python
import { GithubActionsIdentityProvider, GithubActionsRole } from "aws-cdk-github-oidc";

const provider = new GithubActionsIdentityProvider(scope, "GithubProvider");
const deployRole = new GithubActionsRole(scope, "DeployRole", {
  provider,
  owner: "octo-org",
  repo: "octo-repo",
  roleName: "MyDeployRole",
  description: "This role deploys stuff to AWS",
  maxSessionDuration: cdk.Duration.hours(2),
});
```

The equivalent role in this package looks like this:

```python
import { GithubActionsIdentityProvider, GithubActionsRole, AllowAllFilter } from "@blimmer/cdk-github-oidc";

const provider = new GithubActionsIdentityProvider(scope, "GithubProvider");
const deployRole = new GithubActionsRole(scope, "DeployRole", {
  provider,
  roleName: "MyDeployRole",
  description: "This role deploys stuff to AWS",
  subjectFilters: [
    // I encourage you to scope this down to a different filter (e.g., BranchFilter, TagFilter, PullRequestFilter, etc.)
    new AllowAllFilter({ owner: "octo-org", repository: "octo-repo" }),
  ],
  maxSessionDuration: cdk.Duration.hours(2),
});
```

### Resource Replacement

By default, CloudFormation will create resources before destroying the old ones. This is a problem when transitioning
between `aws-cdk-github-oidc` and `@blimmer/cdk-github-oidc` because the `GithubActionsIdentityProvider` is a singleton.
It might also affect your roles, if you specified a `roleName`.

To work around this issue, delete the old provider and role(s) before migrating to use this package. Note that this will
make the role unavailable for a few minutes while things are recreated

## Resources

* [Security hardening your deployments](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments)
  on Github Docs.
* [Assuming a role with `aws-actions/configure-aws-credentials`](https://github.com/aws-actions/configure-aws-credentials#assuming-a-role)

## Contributing

Contributions, issues, and feedback are welcome!
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


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.GithubActionOidcFilterProps",
    jsii_struct_bases=[],
    name_mapping={"owner": "owner", "repository": "repository"},
)
class GithubActionOidcFilterProps:
    def __init__(self, *, owner: builtins.str, repository: builtins.str) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b489f50724214af66c7164524f9257e68cd8a9a307369822a1146e44d3e0353)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repository": repository,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''The org or user that owns the repository.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubActionOidcFilterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.GithubActionsIdentityProviderImportProps",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "partition": "partition"},
)
class GithubActionsIdentityProviderImportProps:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: An explicit account ID where the provider is defined. Default: - the current stack's account
        :param partition: An explicit partition where the provider is defined. Default: - the current stack's partition
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c06058a1c7ffb2b7b0b0bceac3dd19f6bf5bd9a030e89831eada477e4b2c8e1d)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if partition is not None:
            self._values["partition"] = partition

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''An explicit account ID where the provider is defined.

        :default: - the current stack's account
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''An explicit partition where the provider is defined.

        :default: - the current stack's partition
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubActionsIdentityProviderImportProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.GithubActionsIdentityProviderProps",
    jsii_struct_bases=[],
    name_mapping={"thumbprints": "thumbprints"},
)
class GithubActionsIdentityProviderProps:
    def __init__(
        self,
        *,
        thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param thumbprints: Pass a list of thumbprints for the GitHub Actions OIDC provider. Default: - [d89e3bd43d5d909b47a18977aa9d5ce36cee184c]
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be520d55844d668ff4b3f6110a7973d08ddcbcaf28446856ff6c8ba4365e0e4)
            check_type(argname="argument thumbprints", value=thumbprints, expected_type=type_hints["thumbprints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if thumbprints is not None:
            self._values["thumbprints"] = thumbprints

    @builtins.property
    def thumbprints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Pass a list of thumbprints for the GitHub Actions OIDC provider.

        :default: - [d89e3bd43d5d909b47a18977aa9d5ce36cee184c]
        '''
        result = self._values.get("thumbprints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubActionsIdentityProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GithubActionsRole(
    _aws_cdk_aws_iam_ceddda9d.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.GithubActionsRole",
):
    '''A role that can be assumed by Github Actions via OIDC.

    Learn more at https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        provider: "IGithubActionsIdentityProvider",
        subject_filters: typing.Sequence["IGithubActionOidcFilter"],
        description: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param provider: Reference to the Github Actions OpenID Connect Provider configured in AWS IAM. Either pass an construct defined by ``new GithubActionsOidcProvider`` or a retrieved reference from ``GithubActionsOidcProvider.fromAccount``. There can be only one (per AWS Account).
        :param subject_filters: Subject filters to apply to the Github Actions OIDC token. This filters restrict which repo/branch/tag/etc. can assume the role. This construct exposes many common filters, but you can also pass a custom filter if you need to. For a basic starting point, you can allow all branches to access the role via: const subjectFilters = [ new BranchFilter({ owner: "my-org", repository: "my-repo", branch: "*" }), ]
        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97ad31c5347c27fd99570a465a05f09324dba5edd0a1c54575c19afbca9a2dea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GithubActionsRoleProps(
            provider=provider,
            subject_filters=subject_filters,
            description=description,
            external_ids=external_ids,
            inline_policies=inline_policies,
            managed_policies=managed_policies,
            max_session_duration=max_session_duration,
            path=path,
            permissions_boundary=permissions_boundary,
            role_name=role_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.GithubActionsRoleConfiguration",
    jsii_struct_bases=[],
    name_mapping={"provider": "provider", "subject_filters": "subjectFilters"},
)
class GithubActionsRoleConfiguration:
    def __init__(
        self,
        *,
        provider: "IGithubActionsIdentityProvider",
        subject_filters: typing.Sequence["IGithubActionOidcFilter"],
    ) -> None:
        '''
        :param provider: Reference to the Github Actions OpenID Connect Provider configured in AWS IAM. Either pass an construct defined by ``new GithubActionsOidcProvider`` or a retrieved reference from ``GithubActionsOidcProvider.fromAccount``. There can be only one (per AWS Account).
        :param subject_filters: Subject filters to apply to the Github Actions OIDC token. This filters restrict which repo/branch/tag/etc. can assume the role. This construct exposes many common filters, but you can also pass a custom filter if you need to. For a basic starting point, you can allow all branches to access the role via: const subjectFilters = [ new BranchFilter({ owner: "my-org", repository: "my-repo", branch: "*" }), ]
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8a09e585860640c974959213bede9e1d0a52f19c8b79ddc464dede1c2222045)
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument subject_filters", value=subject_filters, expected_type=type_hints["subject_filters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "provider": provider,
            "subject_filters": subject_filters,
        }

    @builtins.property
    def provider(self) -> "IGithubActionsIdentityProvider":
        '''Reference to the Github Actions OpenID Connect Provider configured in AWS IAM.

        Either pass an construct defined by ``new GithubActionsOidcProvider``
        or a retrieved reference from ``GithubActionsOidcProvider.fromAccount``.
        There can be only one (per AWS Account).
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast("IGithubActionsIdentityProvider", result)

    @builtins.property
    def subject_filters(self) -> typing.List["IGithubActionOidcFilter"]:
        '''Subject filters to apply to the Github Actions OIDC token.

        This filters restrict which repo/branch/tag/etc. can assume the role. This construct
        exposes many common filters, but you can also pass a custom filter if you need to.

        For a basic starting point, you can allow all branches to access the role via:

        const subjectFilters = [
        new BranchFilter({ owner: "my-org", repository: "my-repo", branch: "*" }),
        ]
        '''
        result = self._values.get("subject_filters")
        assert result is not None, "Required property 'subject_filters' is missing"
        return typing.cast(typing.List["IGithubActionOidcFilter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubActionsRoleConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class IGithubActionOidcFilter(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@blimmer/cdk-github-oidc.IGithubActionOidcFilter",
):
    '''An abstract class that represents a filter for a Github Actions OIDC filter.

    You can implement this class to create your own filters.
    '''

    def __init__(self, *, owner: builtins.str, repository: builtins.str) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = GithubActionOidcFilterProps(owner=owner, repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    @abc.abstractmethod
    def to_subject(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="owner")
    def _owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def _repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))


class _IGithubActionOidcFilterProxy(IGithubActionOidcFilter):
    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, IGithubActionOidcFilter).__jsii_proxy_class__ = lambda : _IGithubActionOidcFilterProxy


@jsii.interface(jsii_type="@blimmer/cdk-github-oidc.IGithubActionsIdentityProvider")
class IGithubActionsIdentityProvider(typing_extensions.Protocol):
    '''Interface representing a Github Actions OIDC provider.'''

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        ...


class _IGithubActionsIdentityProviderProxy:
    '''Interface representing a Github Actions OIDC provider.'''

    __jsii_type__: typing.ClassVar[str] = "@blimmer/cdk-github-oidc.IGithubActionsIdentityProvider"

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGithubActionsIdentityProvider).__jsii_proxy_class__ = lambda : _IGithubActionsIdentityProviderProxy


class PullRequestFilter(
    IGithubActionOidcFilter,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.PullRequestFilter",
):
    '''Allow assuming a role from (non-environment-specific) pull requests.

    https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#filtering-for-pull_request-events
    '''

    def __init__(self, *, owner: builtins.str, repository: builtins.str) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = GithubActionOidcFilterProps(owner=owner, repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.RoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "external_ids": "externalIds",
        "inline_policies": "inlinePolicies",
        "managed_policies": "managedPolicies",
        "max_session_duration": "maxSessionDuration",
        "path": "path",
        "permissions_boundary": "permissionsBoundary",
        "role_name": "roleName",
    },
)
class RoleProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''RoleProps.

        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13f1c81e969b409c4500abb45dd788a18c2ff9dae9583d8d1ccd45e8a7b18bbc)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument external_ids", value=external_ids, expected_type=type_hints["external_ids"])
            check_type(argname="argument inline_policies", value=inline_policies, expected_type=type_hints["inline_policies"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument max_session_duration", value=max_session_duration, expected_type=type_hints["max_session_duration"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if external_ids is not None:
            self._values["external_ids"] = external_ids
        if inline_policies is not None:
            self._values["inline_policies"] = inline_policies
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if max_session_duration is not None:
            self._values["max_session_duration"] = max_session_duration
        if path is not None:
            self._values["path"] = path
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the role.

        It can be up to 1000 characters long.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IDs that the role assumer needs to provide one of when assuming this role.

        If the configured and provided external IDs do not match, the
        AssumeRole operation will fail.

        :default: No external ID required
        '''
        result = self._values.get("external_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def inline_policies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]]:
        '''A list of named policies to inline into this role.

        These policies will be
        created with the role, whereas those added by ``addToPolicy`` are added
        using a separate CloudFormation resource (allowing a way around circular
        dependencies that could otherwise be introduced).

        :default: - No policy is inlined in the Role resource.
        '''
        result = self._values.get("inline_policies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        '''A list of managed policies associated with this role.

        You can add managed policies later using
        ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``.

        :default: - No managed policies.
        '''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def max_session_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum session duration that you want to set for the specified role.

        This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours.

        Anyone who assumes the role from the AWS CLI or API can use the
        DurationSeconds API parameter or the duration-seconds CLI parameter to
        request a longer session. The MaxSessionDuration setting determines the
        maximum duration that can be requested using the DurationSeconds
        parameter.

        If users don't specify a value for the DurationSeconds parameter, their
        security credentials are valid for one hour by default. This applies when
        you use the AssumeRole* API operations or the assume-role* CLI operations
        but does not apply when you use those operations to create a console URL.

        :default: Duration.hours(1)

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html
        '''
        result = self._values.get("max_session_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path associated with this role.

        For information about IAM paths, see
        Friendly Names and Paths in IAM User Guide.

        :default: /
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]:
        '''AWS supports permissions boundaries for IAM entities (users or roles).

        A permissions boundary is an advanced feature for using a managed policy
        to set the maximum permissions that an identity-based policy can grant to
        an IAM entity. An entity's permissions boundary allows it to perform only
        the actions that are allowed by both its identity-based policies and its
        permissions boundaries.

        :default: - No permissions boundary.

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''A name for the IAM role.

        For valid values, see the RoleName parameter for
        the CreateRole action in the IAM API Reference.

        IMPORTANT: If you specify a name, you cannot perform updates that require
        replacement of this resource. You can perform updates that require no or
        some interruption. If you must replace the resource, specify a new name.

        If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
        acknowledge your template's capabilities. For more information, see
        Acknowledging IAM Resources in AWS CloudFormation Templates.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the role name.
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TagFilter(
    IGithubActionOidcFilter,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.TagFilter",
):
    '''Allow assuming a role for a specific Github tag.

    https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#filtering-for-a-specific-tag
    '''

    def __init__(
        self,
        *,
        tag: builtins.str,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param tag: The name of the tag to filter on. You can also use wildcards. To allow all tags, pass ``*``.
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = TagFilterProps(tag=tag, owner=owner, repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.TagFilterProps",
    jsii_struct_bases=[GithubActionOidcFilterProps],
    name_mapping={"owner": "owner", "repository": "repository", "tag": "tag"},
)
class TagFilterProps(GithubActionOidcFilterProps):
    def __init__(
        self,
        *,
        owner: builtins.str,
        repository: builtins.str,
        tag: builtins.str,
    ) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        :param tag: The name of the tag to filter on. You can also use wildcards. To allow all tags, pass ``*``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76be0804c94384fbb5e870492ef31c03732b233aa2523574464ad9a3c2a26acc)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repository": repository,
            "tag": tag,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''The org or user that owns the repository.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tag(self) -> builtins.str:
        '''The name of the tag to filter on. You can also use wildcards.

        To allow all tags, pass ``*``.
        '''
        result = self._values.get("tag")
        assert result is not None, "Required property 'tag' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagFilterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AllowAllFilter(
    IGithubActionOidcFilter,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.AllowAllFilter",
):
    '''Allow assuming a role for all Github workflows (branches, tags, pull requests, environments, etc.).'''

    def __init__(self, *, owner: builtins.str, repository: builtins.str) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = GithubActionOidcFilterProps(owner=owner, repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))


class BranchFilter(
    IGithubActionOidcFilter,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.BranchFilter",
):
    '''Allow assuming a role for a specific Github branch.

    https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#filtering-for-a-specific-branch
    '''

    def __init__(
        self,
        *,
        branch: builtins.str,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param branch: The name of the branch to filter on. You can also use wildcards. To allow all branches, pass ``*``.
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = BranchFilterProps(branch=branch, owner=owner, repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.BranchFilterProps",
    jsii_struct_bases=[GithubActionOidcFilterProps],
    name_mapping={"owner": "owner", "repository": "repository", "branch": "branch"},
)
class BranchFilterProps(GithubActionOidcFilterProps):
    def __init__(
        self,
        *,
        owner: builtins.str,
        repository: builtins.str,
        branch: builtins.str,
    ) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        :param branch: The name of the branch to filter on. You can also use wildcards. To allow all branches, pass ``*``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fc754d9915c93b9422a4d3ee5541636bdad93e4994f930d716598de9a677167)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repository": repository,
            "branch": branch,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''The org or user that owns the repository.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''The name of the branch to filter on. You can also use wildcards.

        To allow all branches, pass ``*``.
        '''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchFilterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomFilter(
    IGithubActionOidcFilter,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.CustomFilter",
):
    '''Allow assuming a role for a specific Github filter.

    Use this as an escape hatch if we don't expose a first-class IGithubActionOidcFilter for your use case.
    '''

    def __init__(
        self,
        *,
        filter: builtins.str,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param filter: The filter to apply. The construct will automatically prefix the filter with ``repo:${owner}/${repository}:``. See https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#configuring-the-subject-in-your-cloud-provider
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = CustomFilterProps(filter=filter, owner=owner, repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.CustomFilterProps",
    jsii_struct_bases=[GithubActionOidcFilterProps],
    name_mapping={"owner": "owner", "repository": "repository", "filter": "filter"},
)
class CustomFilterProps(GithubActionOidcFilterProps):
    def __init__(
        self,
        *,
        owner: builtins.str,
        repository: builtins.str,
        filter: builtins.str,
    ) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        :param filter: The filter to apply. The construct will automatically prefix the filter with ``repo:${owner}/${repository}:``. See https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#configuring-the-subject-in-your-cloud-provider
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22202160f3a690f57c30978056c0697342283720f3ecf7c28b3023949f41f073)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repository": repository,
            "filter": filter,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''The org or user that owns the repository.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(self) -> builtins.str:
        '''The filter to apply. The construct will automatically prefix the filter with ``repo:${owner}/${repository}:``.

        See https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#configuring-the-subject-in-your-cloud-provider
        '''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomFilterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnvironmentFilter(
    IGithubActionOidcFilter,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.EnvironmentFilter",
):
    '''Allow assuming a role for a specific Github environment.

    https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect#filtering-for-a-specific-environment
    '''

    def __init__(
        self,
        *,
        environment: builtins.str,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param environment: The name of the Github environment to allow assuming this role.
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        '''
        props = EnvironmentFilterProps(
            environment=environment, owner=owner, repository=repository
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toSubject")
    def to_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toSubject", []))


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.EnvironmentFilterProps",
    jsii_struct_bases=[GithubActionOidcFilterProps],
    name_mapping={
        "owner": "owner",
        "repository": "repository",
        "environment": "environment",
    },
)
class EnvironmentFilterProps(GithubActionOidcFilterProps):
    def __init__(
        self,
        *,
        owner: builtins.str,
        repository: builtins.str,
        environment: builtins.str,
    ) -> None:
        '''
        :param owner: The org or user that owns the repository.
        :param repository: The name of the repository.
        :param environment: The name of the Github environment to allow assuming this role.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fd097ec7493f1b6ec09289666c8154731c74d1c1710703f7dc2f2bd729bd8af)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repository": repository,
            "environment": environment,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''The org or user that owns the repository.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''The name of the repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment(self) -> builtins.str:
        '''The name of the Github environment to allow assuming this role.'''
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvironmentFilterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IGithubActionsIdentityProvider)
class GithubActionsIdentityProvider(
    _aws_cdk_aws_iam_ceddda9d.CfnOIDCProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@blimmer/cdk-github-oidc.GithubActionsIdentityProvider",
):
    '''This construct creates an ODIC provider to allow AWS access from Github Actions workflows.

    You'll need to instantiate
    this construct once per AWS account.

    You can import a existing provider using ``GithubActionsIdentityProvider.fromAccount``.

    To create a role that can be assumed by GitHub Actions workflows, use the ``GithubActionsRole`` construct.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param thumbprints: Pass a list of thumbprints for the GitHub Actions OIDC provider. Default: - [d89e3bd43d5d909b47a18977aa9d5ce36cee184c]
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af1ad4fee574b17a4765e5891403662d354c93268a1351000fcc3ce5f4a0c69a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GithubActionsIdentityProviderProps(thumbprints=thumbprints)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccount")
    @builtins.classmethod
    def from_account(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        account: typing.Optional[builtins.str] = None,
        partition: typing.Optional[builtins.str] = None,
    ) -> IGithubActionsIdentityProvider:
        '''Retrieve a reference to existing Github OIDC provider in your AWS account.

        An AWS account can only have single Github OIDC provider configured into it,
        so internally the reference is made by constructing the ARN from AWS
        Account ID & Github issuer URL.

        :param scope: -
        :param account: An explicit account ID where the provider is defined. Default: - the current stack's account
        :param partition: An explicit partition where the provider is defined. Default: - the current stack's partition
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79b39dfc3b7445d69533891152755fd500dd26fd384569d2506469fa56d2126f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = GithubActionsIdentityProviderImportProps(
            account=account, partition=partition
        )

        return typing.cast(IGithubActionsIdentityProvider, jsii.sinvoke(cls, "fromAccount", [scope, props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="issuer")
    def ISSUER(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "issuer"))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))


@jsii.data_type(
    jsii_type="@blimmer/cdk-github-oidc.GithubActionsRoleProps",
    jsii_struct_bases=[GithubActionsRoleConfiguration, RoleProps],
    name_mapping={
        "provider": "provider",
        "subject_filters": "subjectFilters",
        "description": "description",
        "external_ids": "externalIds",
        "inline_policies": "inlinePolicies",
        "managed_policies": "managedPolicies",
        "max_session_duration": "maxSessionDuration",
        "path": "path",
        "permissions_boundary": "permissionsBoundary",
        "role_name": "roleName",
    },
)
class GithubActionsRoleProps(GithubActionsRoleConfiguration, RoleProps):
    def __init__(
        self,
        *,
        provider: IGithubActionsIdentityProvider,
        subject_filters: typing.Sequence[IGithubActionOidcFilter],
        description: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param provider: Reference to the Github Actions OpenID Connect Provider configured in AWS IAM. Either pass an construct defined by ``new GithubActionsOidcProvider`` or a retrieved reference from ``GithubActionsOidcProvider.fromAccount``. There can be only one (per AWS Account).
        :param subject_filters: Subject filters to apply to the Github Actions OIDC token. This filters restrict which repo/branch/tag/etc. can assume the role. This construct exposes many common filters, but you can also pass a custom filter if you need to. For a basic starting point, you can allow all branches to access the role via: const subjectFilters = [ new BranchFilter({ owner: "my-org", repository: "my-repo", branch: "*" }), ]
        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__513b1782b8713a55aab3a4b5b9fabd17edb8b3f6655cd01d447fc73137f9b7e6)
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument subject_filters", value=subject_filters, expected_type=type_hints["subject_filters"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument external_ids", value=external_ids, expected_type=type_hints["external_ids"])
            check_type(argname="argument inline_policies", value=inline_policies, expected_type=type_hints["inline_policies"])
            check_type(argname="argument managed_policies", value=managed_policies, expected_type=type_hints["managed_policies"])
            check_type(argname="argument max_session_duration", value=max_session_duration, expected_type=type_hints["max_session_duration"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "provider": provider,
            "subject_filters": subject_filters,
        }
        if description is not None:
            self._values["description"] = description
        if external_ids is not None:
            self._values["external_ids"] = external_ids
        if inline_policies is not None:
            self._values["inline_policies"] = inline_policies
        if managed_policies is not None:
            self._values["managed_policies"] = managed_policies
        if max_session_duration is not None:
            self._values["max_session_duration"] = max_session_duration
        if path is not None:
            self._values["path"] = path
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def provider(self) -> IGithubActionsIdentityProvider:
        '''Reference to the Github Actions OpenID Connect Provider configured in AWS IAM.

        Either pass an construct defined by ``new GithubActionsOidcProvider``
        or a retrieved reference from ``GithubActionsOidcProvider.fromAccount``.
        There can be only one (per AWS Account).
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(IGithubActionsIdentityProvider, result)

    @builtins.property
    def subject_filters(self) -> typing.List[IGithubActionOidcFilter]:
        '''Subject filters to apply to the Github Actions OIDC token.

        This filters restrict which repo/branch/tag/etc. can assume the role. This construct
        exposes many common filters, but you can also pass a custom filter if you need to.

        For a basic starting point, you can allow all branches to access the role via:

        const subjectFilters = [
        new BranchFilter({ owner: "my-org", repository: "my-repo", branch: "*" }),
        ]
        '''
        result = self._values.get("subject_filters")
        assert result is not None, "Required property 'subject_filters' is missing"
        return typing.cast(typing.List[IGithubActionOidcFilter], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the role.

        It can be up to 1000 characters long.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IDs that the role assumer needs to provide one of when assuming this role.

        If the configured and provided external IDs do not match, the
        AssumeRole operation will fail.

        :default: No external ID required
        '''
        result = self._values.get("external_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def inline_policies(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]]:
        '''A list of named policies to inline into this role.

        These policies will be
        created with the role, whereas those added by ``addToPolicy`` are added
        using a separate CloudFormation resource (allowing a way around circular
        dependencies that could otherwise be introduced).

        :default: - No policy is inlined in the Role resource.
        '''
        result = self._values.get("inline_policies")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]], result)

    @builtins.property
    def managed_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]]:
        '''A list of managed policies associated with this role.

        You can add managed policies later using
        ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``.

        :default: - No managed policies.
        '''
        result = self._values.get("managed_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]], result)

    @builtins.property
    def max_session_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum session duration that you want to set for the specified role.

        This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours.

        Anyone who assumes the role from the AWS CLI or API can use the
        DurationSeconds API parameter or the duration-seconds CLI parameter to
        request a longer session. The MaxSessionDuration setting determines the
        maximum duration that can be requested using the DurationSeconds
        parameter.

        If users don't specify a value for the DurationSeconds parameter, their
        security credentials are valid for one hour by default. This applies when
        you use the AssumeRole* API operations or the assume-role* CLI operations
        but does not apply when you use those operations to create a console URL.

        :default: Duration.hours(1)

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html
        '''
        result = self._values.get("max_session_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path associated with this role.

        For information about IAM paths, see
        Friendly Names and Paths in IAM User Guide.

        :default: /
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]:
        '''AWS supports permissions boundaries for IAM entities (users or roles).

        A permissions boundary is an advanced feature for using a managed policy
        to set the maximum permissions that an identity-based policy can grant to
        an IAM entity. An entity's permissions boundary allows it to perform only
        the actions that are allowed by both its identity-based policies and its
        permissions boundaries.

        :default: - No permissions boundary.

        :link: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''A name for the IAM role.

        For valid values, see the RoleName parameter for
        the CreateRole action in the IAM API Reference.

        IMPORTANT: If you specify a name, you cannot perform updates that require
        replacement of this resource. You can perform updates that require no or
        some interruption. If you must replace the resource, specify a new name.

        If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to
        acknowledge your template's capabilities. For more information, see
        Acknowledging IAM Resources in AWS CloudFormation Templates.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that ID
        for the role name.
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubActionsRoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AllowAllFilter",
    "BranchFilter",
    "BranchFilterProps",
    "CustomFilter",
    "CustomFilterProps",
    "EnvironmentFilter",
    "EnvironmentFilterProps",
    "GithubActionOidcFilterProps",
    "GithubActionsIdentityProvider",
    "GithubActionsIdentityProviderImportProps",
    "GithubActionsIdentityProviderProps",
    "GithubActionsRole",
    "GithubActionsRoleConfiguration",
    "GithubActionsRoleProps",
    "IGithubActionOidcFilter",
    "IGithubActionsIdentityProvider",
    "PullRequestFilter",
    "RoleProps",
    "TagFilter",
    "TagFilterProps",
]

publication.publish()

def _typecheckingstub__4b489f50724214af66c7164524f9257e68cd8a9a307369822a1146e44d3e0353(
    *,
    owner: builtins.str,
    repository: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c06058a1c7ffb2b7b0b0bceac3dd19f6bf5bd9a030e89831eada477e4b2c8e1d(
    *,
    account: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6be520d55844d668ff4b3f6110a7973d08ddcbcaf28446856ff6c8ba4365e0e4(
    *,
    thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97ad31c5347c27fd99570a465a05f09324dba5edd0a1c54575c19afbca9a2dea(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    provider: IGithubActionsIdentityProvider,
    subject_filters: typing.Sequence[IGithubActionOidcFilter],
    description: typing.Optional[builtins.str] = None,
    external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    path: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8a09e585860640c974959213bede9e1d0a52f19c8b79ddc464dede1c2222045(
    *,
    provider: IGithubActionsIdentityProvider,
    subject_filters: typing.Sequence[IGithubActionOidcFilter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13f1c81e969b409c4500abb45dd788a18c2ff9dae9583d8d1ccd45e8a7b18bbc(
    *,
    description: typing.Optional[builtins.str] = None,
    external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    path: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76be0804c94384fbb5e870492ef31c03732b233aa2523574464ad9a3c2a26acc(
    *,
    owner: builtins.str,
    repository: builtins.str,
    tag: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fc754d9915c93b9422a4d3ee5541636bdad93e4994f930d716598de9a677167(
    *,
    owner: builtins.str,
    repository: builtins.str,
    branch: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22202160f3a690f57c30978056c0697342283720f3ecf7c28b3023949f41f073(
    *,
    owner: builtins.str,
    repository: builtins.str,
    filter: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fd097ec7493f1b6ec09289666c8154731c74d1c1710703f7dc2f2bd729bd8af(
    *,
    owner: builtins.str,
    repository: builtins.str,
    environment: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af1ad4fee574b17a4765e5891403662d354c93268a1351000fcc3ce5f4a0c69a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    thumbprints: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79b39dfc3b7445d69533891152755fd500dd26fd384569d2506469fa56d2126f(
    scope: _constructs_77d1e7e8.Construct,
    *,
    account: typing.Optional[builtins.str] = None,
    partition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__513b1782b8713a55aab3a4b5b9fabd17edb8b3f6655cd01d447fc73137f9b7e6(
    *,
    provider: IGithubActionsIdentityProvider,
    subject_filters: typing.Sequence[IGithubActionOidcFilter],
    description: typing.Optional[builtins.str] = None,
    external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    inline_policies: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_iam_ceddda9d.PolicyDocument]] = None,
    managed_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy]] = None,
    max_session_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    path: typing.Optional[builtins.str] = None,
    permissions_boundary: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IManagedPolicy] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
