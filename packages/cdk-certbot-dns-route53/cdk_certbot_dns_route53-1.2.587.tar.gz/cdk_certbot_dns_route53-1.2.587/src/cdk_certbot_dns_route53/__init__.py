r'''
[![NPM version](https://badge.fury.io/js/cdk-certbot-dns-route53.svg)](https://badge.fury.io/js/cdk-certbot-dns-route53)
[![PyPI version](https://badge.fury.io/py/cdk-certbot-dns-route53.svg)](https://badge.fury.io/py/cdk-certbot-dns-route53)
[![Release](https://github.com/neilkuan/cdk-certbot-dns-route53/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/neilkuan/cdk-certbot-dns-route53/actions/workflows/release.yml)

# cdk-certbot-dns-route53

**cdk-certbot-dns-route53** is a CDK construct library that allows you to create [Certbot](https://github.com/certbot/certbot) Lambda Function on AWS with CDK, and setting schedule cron job to renew certificate to store on S3 Bucket.

## Install

```bash
Use the npm dist tag to opt in CDKv1 or CDKv2:

// for CDKv2
npm install cdk-certbot-dns-route53
or
npm install cdk-certbot-dns-route53@latest

// for CDKv1
npm install cdk-certbot-dns-route53@cdkv1
```

```python
import * as r53 from '@aws-cdk/aws-route53';
import * as s3 from '@aws-cdk/aws-s3';
import * as cdk from '@aws-cdk/core';
import { CertbotDnsRoute53Job } from 'cdk-certbot-dns-route53';

const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new cdk.App();

const stack = new cdk.Stack(app, 'lambda-certbot-dev', { env: devEnv });

new CertbotDnsRoute53Job(stack, 'Demo', {
  certbotOptions: {
    domainName: '*.example.com',
    email: 'user@example.com',
  },
  zone: r53.HostedZone.fromHostedZoneAttributes(stack, 'myZone', {
    zoneName: 'example.com',
    hostedZoneId:  'mockId',
  }),
  destinationBucket: s3.Bucket.fromBucketName(stack, 'myBucket', 'mybucket'),
});
```

### You can define Lambda Image Architecture now. 2022/04/19

```python
import * as r53 from '@aws-cdk/aws-route53';
import * as s3 from '@aws-cdk/aws-s3';
import * as cdk from '@aws-cdk/core';
import * as lambda from '@aws-cdk/aws-lambda';
import { CertbotDnsRoute53Job } from 'cdk-certbot-dns-route53';
const mockApp = new cdk.App();
const stack = new cdk.Stack(mockApp, 'teststack', { env: devEnv });
const bucket = new s3.Bucket(stack, 'testingBucket');
const zone = r53.HostedZone.fromHostedZoneAttributes(stack, 'zone', {
  zoneName: mock.zoneName, hostedZoneId: mock.zoneId,
});
new CertbotDnsRoute53Job(stack, 'Testtask', {
  certbotOptions: {
    domainName: 'example.com',
    email: 'user@example.com',
    customPrefixDirectory: '/',
  },
  zone,
  destinationBucket: bucket,
  schedule: events.Schedule.cron({ month: '2' }),
  architecture: lambda.Architecture.ARM_64, // <- like this way.
});
```

### Example: Invoke Lambda Function log.

![](./images/lambda-logs.png)

### Example: Renew certificate to store on S3 Bucket

![](./images/s3-bucket.png)
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

import aws_cdk.aws_events as _aws_cdk_aws_events_efcdfa54
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_5443dbc3
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_f47b29d4
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_55f001a5
import aws_cdk.core as _aws_cdk_core_f4b25747


class BashExecFunction(
    _aws_cdk_core_f4b25747.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-certbot-dns-route53.BashExecFunction",
):
    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        script: builtins.str,
        architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param script: The path of the shell script to be executed.
        :param architecture: Custom lambda Image Architecture. Default: - lambda.Architecture.X86_64
        :param dockerfile: The path of your custom dockerfile.
        :param environment: Lambda environment variables.
        :param role: Custom lambda execution role. Default: - auto generated role.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: - Duration.seconds(60)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__815f799bcd1da799b09597ee7c6997343bfe9bc4b2fafae83eb748bb8733f0b5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BashExecFunctionProps(
            script=script,
            architecture=architecture,
            dockerfile=dockerfile,
            environment=environment,
            role=role,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="handler")
    def handler(self) -> _aws_cdk_aws_lambda_5443dbc3.DockerImageFunction:
        return typing.cast(_aws_cdk_aws_lambda_5443dbc3.DockerImageFunction, jsii.get(self, "handler"))


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.BashExecFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "script": "script",
        "architecture": "architecture",
        "dockerfile": "dockerfile",
        "environment": "environment",
        "role": "role",
        "timeout": "timeout",
    },
)
class BashExecFunctionProps:
    def __init__(
        self,
        *,
        script: builtins.str,
        architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    ) -> None:
        '''
        :param script: The path of the shell script to be executed.
        :param architecture: Custom lambda Image Architecture. Default: - lambda.Architecture.X86_64
        :param dockerfile: The path of your custom dockerfile.
        :param environment: Lambda environment variables.
        :param role: Custom lambda execution role. Default: - auto generated role.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: - Duration.seconds(60)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a349fede69d30c87337677bfecf574460d5cf03361d4e1e24ce7ab874e3e6f83)
            check_type(argname="argument script", value=script, expected_type=type_hints["script"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument dockerfile", value=dockerfile, expected_type=type_hints["dockerfile"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "script": script,
        }
        if architecture is not None:
            self._values["architecture"] = architecture
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if environment is not None:
            self._values["environment"] = environment
        if role is not None:
            self._values["role"] = role
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def script(self) -> builtins.str:
        '''The path of the shell script to be executed.'''
        result = self._values.get("script")
        assert result is not None, "Required property 'script' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def architecture(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture]:
        '''Custom lambda Image Architecture.

        :default: - lambda.Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''The path of your custom dockerfile.'''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Lambda environment variables.'''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''Custom lambda execution role.

        :default: - auto generated role.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value based on the function's expected execution time.

        :default: - Duration.seconds(60)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BashExecFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertbotDnsRoute53Job(
    _aws_cdk_core_f4b25747.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-certbot-dns-route53.CertbotDnsRoute53Job",
):
    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        certbot_options: typing.Union["CertbotOptions", typing.Dict[builtins.str, typing.Any]],
        destination_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        zone: _aws_cdk_aws_route53_f47b29d4.IHostedZone,
        architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
        enabled_lambda_function_url: typing.Optional[builtins.bool] = None,
        function_url_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certbot_options: certbot cmd options.
        :param destination_bucket: The S3 bucket to store certificate.
        :param zone: The HostZone on route53 to dns-01 challenge.
        :param architecture: Custom lambda Image Architecture. Default: - lambda.Architecture.X86_64
        :param enabled_lambda_function_url: Enabled Lambda Function URL. Default: - false
        :param function_url_options: Options to add a url to a Lambda function. Default: - authType: lambda.FunctionUrlAuthType.NONE
        :param schedule: run the Job with defined schedule. Default: - no schedule
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da05d26f3781f773b2fdfb2cd3b2355cd748de456a029d8d8fc5853a09ecc6be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CertbotDnsRoute53JobProps(
            certbot_options=certbot_options,
            destination_bucket=destination_bucket,
            zone=zone,
            architecture=architecture,
            enabled_lambda_function_url=enabled_lambda_function_url,
            function_url_options=function_url_options,
            schedule=schedule,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.CertbotDnsRoute53JobProps",
    jsii_struct_bases=[],
    name_mapping={
        "certbot_options": "certbotOptions",
        "destination_bucket": "destinationBucket",
        "zone": "zone",
        "architecture": "architecture",
        "enabled_lambda_function_url": "enabledLambdaFunctionUrl",
        "function_url_options": "functionUrlOptions",
        "schedule": "schedule",
    },
)
class CertbotDnsRoute53JobProps:
    def __init__(
        self,
        *,
        certbot_options: typing.Union["CertbotOptions", typing.Dict[builtins.str, typing.Any]],
        destination_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        zone: _aws_cdk_aws_route53_f47b29d4.IHostedZone,
        architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
        enabled_lambda_function_url: typing.Optional[builtins.bool] = None,
        function_url_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
    ) -> None:
        '''
        :param certbot_options: certbot cmd options.
        :param destination_bucket: The S3 bucket to store certificate.
        :param zone: The HostZone on route53 to dns-01 challenge.
        :param architecture: Custom lambda Image Architecture. Default: - lambda.Architecture.X86_64
        :param enabled_lambda_function_url: Enabled Lambda Function URL. Default: - false
        :param function_url_options: Options to add a url to a Lambda function. Default: - authType: lambda.FunctionUrlAuthType.NONE
        :param schedule: run the Job with defined schedule. Default: - no schedule
        '''
        if isinstance(certbot_options, dict):
            certbot_options = CertbotOptions(**certbot_options)
        if isinstance(function_url_options, dict):
            function_url_options = _aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions(**function_url_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2babfa71523bcd78147c91e40cba55e1fb4817d7a9f75a74440df56b87a4ac77)
            check_type(argname="argument certbot_options", value=certbot_options, expected_type=type_hints["certbot_options"])
            check_type(argname="argument destination_bucket", value=destination_bucket, expected_type=type_hints["destination_bucket"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument architecture", value=architecture, expected_type=type_hints["architecture"])
            check_type(argname="argument enabled_lambda_function_url", value=enabled_lambda_function_url, expected_type=type_hints["enabled_lambda_function_url"])
            check_type(argname="argument function_url_options", value=function_url_options, expected_type=type_hints["function_url_options"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certbot_options": certbot_options,
            "destination_bucket": destination_bucket,
            "zone": zone,
        }
        if architecture is not None:
            self._values["architecture"] = architecture
        if enabled_lambda_function_url is not None:
            self._values["enabled_lambda_function_url"] = enabled_lambda_function_url
        if function_url_options is not None:
            self._values["function_url_options"] = function_url_options
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def certbot_options(self) -> "CertbotOptions":
        '''certbot cmd options.'''
        result = self._values.get("certbot_options")
        assert result is not None, "Required property 'certbot_options' is missing"
        return typing.cast("CertbotOptions", result)

    @builtins.property
    def destination_bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''The S3 bucket to store certificate.'''
        result = self._values.get("destination_bucket")
        assert result is not None, "Required property 'destination_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def zone(self) -> _aws_cdk_aws_route53_f47b29d4.IHostedZone:
        '''The HostZone on route53 to dns-01 challenge.'''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.IHostedZone, result)

    @builtins.property
    def architecture(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture]:
        '''Custom lambda Image Architecture.

        :default: - lambda.Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture], result)

    @builtins.property
    def enabled_lambda_function_url(self) -> typing.Optional[builtins.bool]:
        '''Enabled Lambda Function URL.

        :default: - false
        '''
        result = self._values.get("enabled_lambda_function_url")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def function_url_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions]:
        '''Options to add a url to a Lambda function.

        :default: - authType: lambda.FunctionUrlAuthType.NONE
        '''
        result = self._values.get("function_url_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule]:
        '''run the Job with defined schedule.

        :default: - no schedule
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotDnsRoute53JobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.CertbotOptions",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "email": "email",
        "custom_prefix_directory": "customPrefixDirectory",
    },
)
class CertbotOptions:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        email: builtins.str,
        custom_prefix_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain_name: the domain must host on route53 like example.com.
        :param email: Email address for important account notifications.
        :param custom_prefix_directory: Custom prefix directory on s3 bucket object path. Default: - ``s3://YOUR_BUCKET_NAME/2021-01-01/your.domain.name/``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e7e742801dbdf780cc5cf2c7e7f9285935bc961d4ebc9445704722c53801ca1)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument custom_prefix_directory", value=custom_prefix_directory, expected_type=type_hints["custom_prefix_directory"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
            "email": email,
        }
        if custom_prefix_directory is not None:
            self._values["custom_prefix_directory"] = custom_prefix_directory

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''the domain must host on route53 like example.com.

        Example::

            - `*.example.com` or `a.example.com` .
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''Email address for important account notifications.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_prefix_directory(self) -> typing.Optional[builtins.str]:
        '''Custom prefix directory on s3 bucket object path.

        :default: - ``s3://YOUR_BUCKET_NAME/2021-01-01/your.domain.name/``

        Example::

            - customPrefixDirectory: 'abc' -> `s3://YOUR_BUCKET_NAME/abc/your.domain.name/`
        '''
        result = self._values.get("custom_prefix_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BashExecFunction",
    "BashExecFunctionProps",
    "CertbotDnsRoute53Job",
    "CertbotDnsRoute53JobProps",
    "CertbotOptions",
]

publication.publish()

def _typecheckingstub__815f799bcd1da799b09597ee7c6997343bfe9bc4b2fafae83eb748bb8733f0b5(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    script: builtins.str,
    architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
    dockerfile: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a349fede69d30c87337677bfecf574460d5cf03361d4e1e24ce7ab874e3e6f83(
    *,
    script: builtins.str,
    architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
    dockerfile: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da05d26f3781f773b2fdfb2cd3b2355cd748de456a029d8d8fc5853a09ecc6be(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    certbot_options: typing.Union[CertbotOptions, typing.Dict[builtins.str, typing.Any]],
    destination_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    zone: _aws_cdk_aws_route53_f47b29d4.IHostedZone,
    architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
    enabled_lambda_function_url: typing.Optional[builtins.bool] = None,
    function_url_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2babfa71523bcd78147c91e40cba55e1fb4817d7a9f75a74440df56b87a4ac77(
    *,
    certbot_options: typing.Union[CertbotOptions, typing.Dict[builtins.str, typing.Any]],
    destination_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    zone: _aws_cdk_aws_route53_f47b29d4.IHostedZone,
    architecture: typing.Optional[_aws_cdk_aws_lambda_5443dbc3.Architecture] = None,
    enabled_lambda_function_url: typing.Optional[builtins.bool] = None,
    function_url_options: typing.Optional[typing.Union[_aws_cdk_aws_lambda_5443dbc3.FunctionUrlOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_efcdfa54.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e7e742801dbdf780cc5cf2c7e7f9285935bc961d4ebc9445704722c53801ca1(
    *,
    domain_name: builtins.str,
    email: builtins.str,
    custom_prefix_directory: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
