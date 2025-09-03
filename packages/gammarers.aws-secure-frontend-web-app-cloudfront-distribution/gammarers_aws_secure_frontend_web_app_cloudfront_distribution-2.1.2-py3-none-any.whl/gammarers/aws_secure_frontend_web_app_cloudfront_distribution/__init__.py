r'''
# AWS Secure Frontend Web App CloudFront Distribution (for AWS CDK v2)

[![GitHub](https://img.shields.io/github/license/gammarers/aws-secure-frontend-web-app-cloudfront-distribution?style=flat-square)](https://github.com/gammarers/aws-secure-frontend-web-app-cloudfront-distribution/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarers/aws-secure-frontend-web-app-cloudfront-distribution?style=flat-square)](https://www.npmjs.com/package/@gammarers/aws-secure-frontend-web-app-cloudfront-distribution)
[![PyPI](https://img.shields.io/pypi/v/gammarers.aws-secure-frontend-web-app-cloudfront-distribution?style=flat-square)](https://pypi.org/project/gammarers.aws-secure-frontend-web-app-cloudfront-distribution/)
[![Nuget](https://img.shields.io/nuget/v/Gammarers.CDK.AWS.SecureFrontendWebAppCloudFrontDistribution?style=flat-square)](https://www.nuget.org/packages/Gammarers.CDK.AWS.SecureFrontendWebAppCloudFrontDistribution/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarers/aws-secure-frontend-web-app-cloudfront-distribution/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarers/aws-secure-frontend-web-app-cloudfront-distribution/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarers/aws-secure-frontend-web-app-cloudfront-distribution?sort=semver&style=flat-square)](https://github.com/gammarers/aws-secure-frontend-web-app-cloudfront-distribution/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarers/aws-secure-frontend-web-app-cloudfront-distribution)](https://constructs.dev/packages/@gammarers/aws-secure-frontend-web-app-cloudfront-distribution)

AWS CloudFront distribution for frontend web app (spa) optimized.

## Install

### TypeScript

#### npm

```shell
npm install @gammarers/aws-secure-frontend-web-app-cloudfront-distribution
```

#### yarn

```shell
yarn add @gammarers/aws-secure-frontend-web-app-cloudfront-distribution
```

### Python

```shell
pip install gammarers.aws-secure-frontend-web-app-cloudfront-distribution
```

### C# / .NET

```shell
dotnet add package Gammarers.CDK.AWS.SecureFrontendWebAppCloudFrontDistribution
```

## Example

### for Origin Access Control

```python
import { SecureFrontendWebAppCloudFrontDistribution } from '@gammarers/aws-secure-frontend-web-app-cloudfront-distribution';

declare const originBucket: s3.Bucket;
declare const accessLogBucket: s3.Bucket;
declare const certificate: acm.Certificate;

new SecureFrontendWebAppCloudFrontDistribution(stack, 'SecureFrontendWebAppCloudFrontDistribution', {
  comment: 'frontend web app distribution.', // optional
  accessLogBucket: accessLogBucket, // optional
  certificate: certificate,
  distributionDomainName: 'example.com',
  originBucket: originBucket,
});
```

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk.aws_certificatemanager as _aws_cdk_aws_certificatemanager_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class SecureFrontendWebAppCloudFrontDistribution(
    _aws_cdk_aws_cloudfront_ceddda9d.Distribution,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarers/aws-secure-frontend-web-app-cloudfront-distribution.SecureFrontendWebAppCloudFrontDistribution",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        domain_name: builtins.str,
        origin_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        comment: typing.Optional[builtins.str] = None,
        price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificate: 
        :param domain_name: 
        :param origin_bucket: 
        :param access_log_bucket: 
        :param comment: 
        :param price_class: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27bb91c3363183223a83e2b62e72a23f865cc4a5ac5007df30bdca4a8d2b8c31)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SecureFrontendWebAppCloudFrontDistributionProps(
            certificate=certificate,
            domain_name=domain_name,
            origin_bucket=origin_bucket,
            access_log_bucket=access_log_bucket,
            comment=comment,
            price_class=price_class,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-frontend-web-app-cloudfront-distribution.SecureFrontendWebAppCloudFrontDistributionProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "domain_name": "domainName",
        "origin_bucket": "originBucket",
        "access_log_bucket": "accessLogBucket",
        "comment": "comment",
        "price_class": "priceClass",
    },
)
class SecureFrontendWebAppCloudFrontDistributionProps:
    def __init__(
        self,
        *,
        certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
        domain_name: builtins.str,
        origin_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        comment: typing.Optional[builtins.str] = None,
        price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
    ) -> None:
        '''
        :param certificate: 
        :param domain_name: 
        :param origin_bucket: 
        :param access_log_bucket: 
        :param comment: 
        :param price_class: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20de9be6839609623d6f64167c31f2c827c962f152756cf3bb49f1576bd73dd2)
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument origin_bucket", value=origin_bucket, expected_type=type_hints["origin_bucket"])
            check_type(argname="argument access_log_bucket", value=access_log_bucket, expected_type=type_hints["access_log_bucket"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument price_class", value=price_class, expected_type=type_hints["price_class"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
            "domain_name": domain_name,
            "origin_bucket": origin_bucket,
        }
        if access_log_bucket is not None:
            self._values["access_log_bucket"] = access_log_bucket
        if comment is not None:
            self._values["comment"] = comment
        if price_class is not None:
            self._values["price_class"] = price_class

    @builtins.property
    def certificate(self) -> _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate:
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(_aws_cdk_aws_certificatemanager_ceddda9d.ICertificate, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def origin_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        result = self._values.get("origin_bucket")
        assert result is not None, "Required property 'origin_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def access_log_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        result = self._values.get("access_log_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def price_class(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass]:
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureFrontendWebAppCloudFrontDistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecureFrontendWebAppCloudFrontDistribution",
    "SecureFrontendWebAppCloudFrontDistributionProps",
]

publication.publish()

def _typecheckingstub__27bb91c3363183223a83e2b62e72a23f865cc4a5ac5007df30bdca4a8d2b8c31(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    domain_name: builtins.str,
    origin_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    comment: typing.Optional[builtins.str] = None,
    price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20de9be6839609623d6f64167c31f2c827c962f152756cf3bb49f1576bd73dd2(
    *,
    certificate: _aws_cdk_aws_certificatemanager_ceddda9d.ICertificate,
    domain_name: builtins.str,
    origin_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    access_log_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    comment: typing.Optional[builtins.str] = None,
    price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
) -> None:
    """Type checking stubs"""
    pass
