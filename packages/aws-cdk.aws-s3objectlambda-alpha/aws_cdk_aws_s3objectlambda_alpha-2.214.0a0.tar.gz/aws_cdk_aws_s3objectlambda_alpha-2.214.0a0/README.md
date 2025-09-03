# AWS::S3ObjectLambda Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This construct library allows you to define S3 object lambda access points.

```python
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
import aws_cdk as cdk

stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_LATEST,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    payload={
        "prop": "value"
    }
)
```

## Handling range and part number requests

Lambdas are currently limited to only transforming `GetObject` requests. However, they can additionally support `GetObject-Range` and `GetObject-PartNumber` requests, which needs to be specified in the access point configuration:

```python
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
import aws_cdk as cdk

stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_LATEST,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    supports_get_object_range=True,
    supports_get_object_part_number=True
)
```

## Pass additional data to Lambda function

You can specify an additional object that provides supplemental data to the Lambda function used to transform objects. The data is delivered as a JSON payload to the Lambda:

```python
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda
import aws_cdk as cdk

stack = cdk.Stack()
bucket = s3.Bucket(stack, "MyBucket")
handler = lambda_.Function(stack, "MyFunction",
    runtime=lambda_.Runtime.NODEJS_LATEST,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda.zip")
)
s3objectlambda.AccessPoint(stack, "MyObjectLambda",
    bucket=bucket,
    handler=handler,
    access_point_name="my-access-point",
    payload={
        "prop": "value"
    }
)
```

## Accessing the S3 AccessPoint ARN

If you need access to the s3 accesspoint, you can get its ARN like so:

```python
import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda

# access_point: s3objectlambda.AccessPoint
s3_access_point_arn = access_point.s3_access_point_arn
```

This is only supported for AccessPoints created in the stack - currently you're unable to get the S3 AccessPoint ARN for imported AccessPoints. To do that you'd have to know the S3 bucket name beforehand.
