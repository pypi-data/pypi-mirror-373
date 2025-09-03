# AWS::CodeStar Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## GitHub Repository

To create a new GitHub Repository and commit the assets from S3 bucket into the repository after it is created:

```python
import aws_cdk.aws_codestar_alpha as codestar
import aws_cdk.aws_s3 as s3


codestar.GitHubRepository(self, "GitHubRepo",
    owner="aws",
    repository_name="aws-cdk",
    access_token=SecretValue.secrets_manager("my-github-token",
        json_field="token"
    ),
    contents_bucket=s3.Bucket.from_bucket_name(self, "Bucket", "amzn-s3-demo-bucket"),
    contents_key="import.zip"
)
```

## Update or Delete the GitHubRepository

At this moment, updates to the `GitHubRepository` are not supported and the repository will not be deleted upon the deletion of the CloudFormation stack. You will need to update or delete the GitHub repository manually.
