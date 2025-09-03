r'''
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
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3objectlambda-alpha.AccessPointAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "access_point_arn": "accessPointArn",
        "access_point_creation_date": "accessPointCreationDate",
    },
)
class AccessPointAttributes:
    def __init__(
        self,
        *,
        access_point_arn: builtins.str,
        access_point_creation_date: builtins.str,
    ) -> None:
        '''(experimental) The access point resource attributes.

        :param access_point_arn: (experimental) The ARN of the access point.
        :param access_point_creation_date: (experimental) The creation data of the access point.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_s3objectlambda_alpha as s3objectlambda_alpha
            
            access_point_attributes = s3objectlambda_alpha.AccessPointAttributes(
                access_point_arn="accessPointArn",
                access_point_creation_date="accessPointCreationDate"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0230e1b13ccb26118a2d6924aa169bbf363d9012ac28ab92e5bdece75adeba54)
            check_type(argname="argument access_point_arn", value=access_point_arn, expected_type=type_hints["access_point_arn"])
            check_type(argname="argument access_point_creation_date", value=access_point_creation_date, expected_type=type_hints["access_point_creation_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_point_arn": access_point_arn,
            "access_point_creation_date": access_point_creation_date,
        }

    @builtins.property
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        '''
        result = self._values.get("access_point_arn")
        assert result is not None, "Required property 'access_point_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        '''
        result = self._values.get("access_point_creation_date")
        assert result is not None, "Required property 'access_point_creation_date' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3objectlambda-alpha.AccessPointProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "handler": "handler",
        "access_point_name": "accessPointName",
        "cloud_watch_metrics_enabled": "cloudWatchMetricsEnabled",
        "payload": "payload",
        "supports_get_object_part_number": "supportsGetObjectPartNumber",
        "supports_get_object_range": "supportsGetObjectRange",
    },
)
class AccessPointProps:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        access_point_name: typing.Optional[builtins.str] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        supports_get_object_part_number: typing.Optional[builtins.bool] = None,
        supports_get_object_range: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) The S3 object lambda access point configuration.

        :param bucket: (experimental) The bucket to which this access point belongs.
        :param handler: (experimental) The Lambda function used to transform objects.
        :param access_point_name: (experimental) The name of the S3 object lambda access point. Default: a unique name will be generated
        :param cloud_watch_metrics_enabled: (experimental) Whether CloudWatch metrics are enabled for the access point. Default: false
        :param payload: (experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request. Default: - No data.
        :param supports_get_object_part_number: (experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests. Default: false
        :param supports_get_object_range: (experimental) Whether the Lambda function can process ``GetObject-Range`` requests. Default: false

        :stability: experimental
        :exampleMetadata: infused

        Example::

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
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7361024364627526d9d95a93129e98a3630928fbfc60102de59d835f2e578216)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
            check_type(argname="argument access_point_name", value=access_point_name, expected_type=type_hints["access_point_name"])
            check_type(argname="argument cloud_watch_metrics_enabled", value=cloud_watch_metrics_enabled, expected_type=type_hints["cloud_watch_metrics_enabled"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument supports_get_object_part_number", value=supports_get_object_part_number, expected_type=type_hints["supports_get_object_part_number"])
            check_type(argname="argument supports_get_object_range", value=supports_get_object_range, expected_type=type_hints["supports_get_object_range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "handler": handler,
        }
        if access_point_name is not None:
            self._values["access_point_name"] = access_point_name
        if cloud_watch_metrics_enabled is not None:
            self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled
        if payload is not None:
            self._values["payload"] = payload
        if supports_get_object_part_number is not None:
            self._values["supports_get_object_part_number"] = supports_get_object_part_number
        if supports_get_object_range is not None:
            self._values["supports_get_object_range"] = supports_get_object_range

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) The bucket to which this access point belongs.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def handler(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''(experimental) The Lambda function used to transform objects.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def access_point_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the S3 object lambda access point.

        :default: a unique name will be generated

        :stability: experimental
        '''
        result = self._values.get("access_point_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_watch_metrics_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether CloudWatch metrics are enabled for the access point.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("cloud_watch_metrics_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def payload(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request.

        :default: - No data.

        :stability: experimental
        '''
        result = self._values.get("payload")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def supports_get_object_part_number(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("supports_get_object_part_number")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def supports_get_object_range(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Lambda function can process ``GetObject-Range`` requests.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("supports_get_object_range")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-s3objectlambda-alpha.IAccessPoint")
class IAccessPoint(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) The interface that represents the AccessPoint resource.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The IPv4 DNS name of the access point.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The regional domain name of the access point.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) The virtual hosted-style URL of an S3 object through this access point.

        Specify ``regional: false`` at the options for non-regional URL.

        :param key: The S3 key of the object. If not specified, the URL of the bucket is returned.
        :param regional: Specifies the URL includes the region. Default: - true

        :return: an ObjectS3Url token

        :stability: experimental
        '''
        ...


class _IAccessPointProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) The interface that represents the AccessPoint resource.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-s3objectlambda-alpha.IAccessPoint"

    @builtins.property
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointCreationDate"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The IPv4 DNS name of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) The regional domain name of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) The virtual hosted-style URL of an S3 object through this access point.

        Specify ``regional: false`` at the options for non-regional URL.

        :param key: The S3 key of the object. If not specified, the URL of the bucket is returned.
        :param regional: Specifies the URL includes the region. Default: - true

        :return: an ObjectS3Url token

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67fface5f7e916cc919d9842615bb749d04e349ffaff48f6b7ee7f5062839d51)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        options = _aws_cdk_aws_s3_ceddda9d.VirtualHostedStyleUrlOptions(
            regional=regional
        )

        return typing.cast(builtins.str, jsii.invoke(self, "virtualHostedUrlForObject", [key, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccessPoint).__jsii_proxy_class__ = lambda : _IAccessPointProxy


@jsii.implements(IAccessPoint)
class AccessPoint(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-s3objectlambda-alpha.AccessPoint",
):
    '''(experimental) An S3 object lambda access point for intercepting and transforming ``GetObject`` requests.

    :stability: experimental
    :exampleMetadata: infused

    Example::

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
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        access_point_name: typing.Optional[builtins.str] = None,
        cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
        payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        supports_get_object_part_number: typing.Optional[builtins.bool] = None,
        supports_get_object_range: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket: (experimental) The bucket to which this access point belongs.
        :param handler: (experimental) The Lambda function used to transform objects.
        :param access_point_name: (experimental) The name of the S3 object lambda access point. Default: a unique name will be generated
        :param cloud_watch_metrics_enabled: (experimental) Whether CloudWatch metrics are enabled for the access point. Default: false
        :param payload: (experimental) Additional JSON that provides supplemental data passed to the Lambda function on every request. Default: - No data.
        :param supports_get_object_part_number: (experimental) Whether the Lambda function can process ``GetObject-PartNumber`` requests. Default: false
        :param supports_get_object_range: (experimental) Whether the Lambda function can process ``GetObject-Range`` requests. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67d3988c298656f8a20bc1bb8831c927675995c72e2536eb9a5a54701a50604d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AccessPointProps(
            bucket=bucket,
            handler=handler,
            access_point_name=access_point_name,
            cloud_watch_metrics_enabled=cloud_watch_metrics_enabled,
            payload=payload,
            supports_get_object_part_number=supports_get_object_part_number,
            supports_get_object_range=supports_get_object_range,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccessPointAttributes")
    @builtins.classmethod
    def from_access_point_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_point_arn: builtins.str,
        access_point_creation_date: builtins.str,
    ) -> IAccessPoint:
        '''(experimental) Reference an existing AccessPoint defined outside of the CDK code.

        :param scope: -
        :param id: -
        :param access_point_arn: (experimental) The ARN of the access point.
        :param access_point_creation_date: (experimental) The creation data of the access point.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f7a575152ecb79f8c1a581a6380dd1d19647cb5400ed33bf474e24ba006eec2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AccessPointAttributes(
            access_point_arn=access_point_arn,
            access_point_creation_date=access_point_creation_date,
        )

        return typing.cast(IAccessPoint, jsii.sinvoke(cls, "fromAccessPointAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="virtualHostedUrlForObject")
    def virtual_hosted_url_for_object(
        self,
        key: typing.Optional[builtins.str] = None,
        *,
        regional: typing.Optional[builtins.bool] = None,
    ) -> builtins.str:
        '''(experimental) Implement the ``IAccessPoint.virtualHostedUrlForObject`` method.

        :param key: -
        :param regional: Specifies the URL includes the region. Default: - true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09c101e5c7a6e056b459659f7b32d595e1b600b7f62871dd6060de26251f9f04)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        options = _aws_cdk_aws_s3_ceddda9d.VirtualHostedStyleUrlOptions(
            regional=regional
        )

        return typing.cast(builtins.str, jsii.invoke(self, "virtualHostedUrlForObject", [key, options]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @builtins.property
    @jsii.member(jsii_name="accessPointCreationDate")
    def access_point_creation_date(self) -> builtins.str:
        '''(experimental) The creation data of the access point.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointCreationDate"))

    @builtins.property
    @jsii.member(jsii_name="accessPointName")
    def access_point_name(self) -> builtins.str:
        '''(experimental) The ARN of the access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessPointName"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) Implement the ``IAccessPoint.domainName`` field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="regionalDomainName")
    def regional_domain_name(self) -> builtins.str:
        '''(experimental) Implement the ``IAccessPoint.regionalDomainName`` field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "regionalDomainName"))

    @builtins.property
    @jsii.member(jsii_name="s3AccessPointArn")
    def s3_access_point_arn(self) -> builtins.str:
        '''(experimental) The ARN of the S3 access point.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "s3AccessPointArn"))


__all__ = [
    "AccessPoint",
    "AccessPointAttributes",
    "AccessPointProps",
    "IAccessPoint",
]

publication.publish()

def _typecheckingstub__0230e1b13ccb26118a2d6924aa169bbf363d9012ac28ab92e5bdece75adeba54(
    *,
    access_point_arn: builtins.str,
    access_point_creation_date: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7361024364627526d9d95a93129e98a3630928fbfc60102de59d835f2e578216(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    access_point_name: typing.Optional[builtins.str] = None,
    cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
    payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    supports_get_object_part_number: typing.Optional[builtins.bool] = None,
    supports_get_object_range: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67fface5f7e916cc919d9842615bb749d04e349ffaff48f6b7ee7f5062839d51(
    key: typing.Optional[builtins.str] = None,
    *,
    regional: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67d3988c298656f8a20bc1bb8831c927675995c72e2536eb9a5a54701a50604d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    handler: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    access_point_name: typing.Optional[builtins.str] = None,
    cloud_watch_metrics_enabled: typing.Optional[builtins.bool] = None,
    payload: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    supports_get_object_part_number: typing.Optional[builtins.bool] = None,
    supports_get_object_range: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f7a575152ecb79f8c1a581a6380dd1d19647cb5400ed33bf474e24ba006eec2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_point_arn: builtins.str,
    access_point_creation_date: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09c101e5c7a6e056b459659f7b32d595e1b600b7f62871dd6060de26251f9f04(
    key: typing.Optional[builtins.str] = None,
    *,
    regional: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
