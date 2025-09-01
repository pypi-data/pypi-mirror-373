r'''
[![NPM version](https://img.shields.io/npm/v/low-cost-ecs?color=brightgreen)](https://www.npmjs.com/package/low-cost-ecs)
[![PyPI version](https://img.shields.io/pypi/v/low-cost-ecs?color=brightgreen)](https://pypi.org/project/low-cost-ecs)
[![Release](https://github.com/rajyan/low-cost-ecs/workflows/release/badge.svg)](https://github.com/rajyan/low-cost-ecs/actions/workflows/release.yml)
[<img src="https://constructs.dev/badge?package=low-cost-ecs" width="150">](https://constructs.dev/packages/low-cost-ecs)

# Low-Cost ECS

A CDK construct that provides an easy and [low-cost](#cost) ECS on EC2 server setup without a load balancer.

# Why

ECS may often seem expensive when used for personal development purposes, due to the cost of the load balancer.
The application load balancer is a great service that is easy to set up managed ACM certificates, easy scaling, and has dynamic port mappings..., but it is over-featured for running 1 ECS task.

However, to run an ECS server without a load balancer, you need to associate an Elastic IP to the host instance and install your certificate to your service every time you start up the server.
This construct aims to automate these works and make it easy to deploy resources to run a low-cost ECS server.

# Try it out!

The easiest way to try the construct is to clone this repository and deploy the sample Nginx server.
Edit settings in [`examples/minimum.ts`](https://github.com/rajyan/low-cost-ecs/blob/main/examples/minimum.ts) and deploy the cdk construct. [Public hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/AboutHZWorkingWith.html) is required.

1. Clone and install packages

```
git clone https://github.com/rajyan/low-cost-ecs.git
yarn install
```

1. Edit email and domain in example.ts
   https://github.com/rajyan/low-cost-ecs/blob/3d1bbf7ef4b59d0f4e9d3cd9cb90584977b71c0a/examples/minimum.ts#L1-L15
2. Deploy!

```
cdk deploy
```

Access the configured `hostedZoneDomain` and see that the sample Nginx server has been deployed.

# Installation

To use this construct in your cdk stack as a library,

```
npm install low-cost-ecs
```

```python
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { LowCostECS } from 'low-cost-ecs';

class SampleStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        const vpc = { /** Your VPC */ };
        const securityGroup = { /** Your security group */ };
        const serverTaskDefinition = { /** Your task definition */ };

        new LowCostECS(this, 'LowCostECS', {
            hostedZoneDomain: "example.com",
            email: "test@example.com",
            vpc: vpc,
            securityGroup: securityGroup,
            serverTaskDefinition: serverTaskDefinition
        });
    }
}
```

The required fields are `hostedZoneDomain` and `email`.
You can configure your server task definition and other props. Read [`LowCostECSProps` documentation](https://github.com/rajyan/low-cost-ecs/blob/main/API.md#low-cost-ecs.LowCostECSProps) for details.

# Overview

Resources generated in this stack

* Route53 A record

  * Forwarding to host instance Elastic IP
* Certificate State Machine

  * Install and renew certificates to EFS using [certbot-dns-route53](https://certbot-dns-route53.readthedocs.io/en/stable/)
  * Scheduled automated renewal every 60 days
  * Email notification on certbot task failure
* ECS on EC2 host instance

  * ECS-optimized Amazon Linux 2 AMI instance auto-scaling group
  * Automatically associated with Elastic IP on instance initialization
* ECS Service

  * TLS/SSL certificate installation before default container startup
  * Certificate EFS mounted on default container as `/etc/letsencrypt`
* Others

  * VPC with only public subnets (no NAT Gateways to decrease cost)
  * Security groups with minimum inbounds
  * IAM roles with minimum privileges

# Cost

All resources except Route53 HostedZone should be included in [AWS Free Tier](https://docs.aws.amazon.com/whitepapers/latest/how-aws-pricing-works/get-started-with-the-aws-free-tier.html)
***if you are in the 12 Months Free period***.
After your 12 Months Free period, setting [`hostInstanceSpotPrice`](https://github.com/rajyan/low-cost-ecs/blob/main/API.md#low-cost-ecs.LowCostECSProps.property.hostInstanceSpotPrice) to use spot instances is recommended.

* EC2

  * t2.micro 750 instance hours (12 Months Free Tier)
  * 30GB EBS volume (12 Months Free Tier)
* ECS

  * No additional charge because using ECS on EC2
* EFS

  * Usage is very small, it should be free
* Cloud Watch

  * Usage is very small, and it should be included in the free tier
  * Enabling [`containerInsights`](https://github.com/rajyan/low-cost-ecs/blob/main/API.md#low-cost-ecs.LowCostECSProps.property.containerInsights) will charge for custom metrics

# Debugging

* SSM Session Manager

SSM manager is pre-installed in the host instance (by ECS-optimized Amazon Linux 2 AMI) and `AmazonSSMManagedInstanceCore` is added to the host instance role to access and debug in your host instance.

```
aws ssm start-session --target $INSTANCE_ID
```

* ECS Exec

Service ECS Exec is enabled, so execute commands can be used to debug your server task container.

```
aws ecs execute-command \
--cluster $CLUSTER_ID \
--task $TASK_ID \
--container nginx \
--command bash \
--interactive
```

# Limitations

Because the ECS service occupies a host port, only one task can be executed at a time.
The old task must be terminated before the new task launches, and this causes downtime on release.

Also, if you make changes that require recreating the service, you may need to manually terminate the task of the old service.
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
import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


class LowCostECS(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="low-cost-ecs.LowCostECS",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        hosted_zone_domain: builtins.str,
        aws_cli_docker_tag: typing.Optional[builtins.str] = None,
        certbot_docker_tag: typing.Optional[builtins.str] = None,
        certbot_schedule_interval: typing.Optional[jsii.Number] = None,
        container_insights: typing.Optional[builtins.bool] = None,
        host_instance_spot_price: typing.Optional[builtins.str] = None,
        host_instance_type: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        record_domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        server_task_definition: typing.Optional[typing.Union["LowCostECSTaskDefinitionOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param email: (experimental) Email for expiration emails to register to your let's encrypt account.
        :param hosted_zone_domain: (experimental) Domain name of the hosted zone.
        :param aws_cli_docker_tag: (experimental) Docker image tag of amazon/aws-cli. This image is used to associate elastic ip on host instance startup, and run certbot cfn on ecs container startup. Default: - latest
        :param certbot_docker_tag: (experimental) Docker image tag of certbot/dns-route53 to create certificates. Default: - v1.29.0
        :param certbot_schedule_interval: (experimental) Certbot task schedule interval in days to renew the certificate. Default: - 60
        :param container_insights: (experimental) Enable container insights or not. Default: - undefined (container insights disabled)
        :param host_instance_spot_price: (experimental) The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Host instance asg would use spot instances if hostInstanceSpotPrice is set. Default: - undefined
        :param host_instance_type: (experimental) Instance type of the ECS host instance. Default: - t2.micro
        :param log_group: (experimental) Log group of the certbot task and the aws-cli task. Default: - Creates default cdk log group
        :param record_domain_names: (experimental) Domain names for A records to elastic ip of ECS host instance. Default: - [ props.hostedZone.zoneName ]
        :param removal_policy: (experimental) Removal policy for the file system and log group (if using default). Default: - RemovalPolicy.DESTROY
        :param security_groups: (experimental) Security group of the ECS host instance. Default: - Creates security group with allowAllOutbound and ingress rule (ipv4, ipv6) => (tcp 80, 443).
        :param server_task_definition: (experimental) Task definition for the server ecs task. Default: - Nginx server task definition defined in sampleTaskDefinition()
        :param vpc: (experimental) VPC of the ECS cluster and EFS file system. Default: - Creates vpc with only public subnets and no NAT gateways.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0356d0ba92a1b88dbec557c9706dec10d39b53bd74af24510f519ceae784aea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LowCostECSProps(
            email=email,
            hosted_zone_domain=hosted_zone_domain,
            aws_cli_docker_tag=aws_cli_docker_tag,
            certbot_docker_tag=certbot_docker_tag,
            certbot_schedule_interval=certbot_schedule_interval,
            container_insights=container_insights,
            host_instance_spot_price=host_instance_spot_price,
            host_instance_type=host_instance_type,
            log_group=log_group,
            record_domain_names=record_domain_names,
            removal_policy=removal_policy,
            security_groups=security_groups,
            server_task_definition=server_task_definition,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="certFileSystem")
    def cert_file_system(self) -> _aws_cdk_aws_efs_ceddda9d.FileSystem:
        '''(experimental) EFS file system that the SSL/TLS certificates are installed.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_efs_ceddda9d.FileSystem, jsii.get(self, "certFileSystem"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.Cluster:
        '''(experimental) ECS cluster created in configured VPC.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.Cluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="hostAutoScalingGroup")
    def host_auto_scaling_group(
        self,
    ) -> _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup:
        '''(experimental) ECS on EC2 service host instance autoscaling group.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup, jsii.get(self, "hostAutoScalingGroup"))

    @builtins.property
    @jsii.member(jsii_name="serverTaskDefinition")
    def server_task_definition(self) -> _aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinition:
        '''(experimental) Server task definition generated from LowCostECSTaskDefinitionOptions.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinition, jsii.get(self, "serverTaskDefinition"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.Ec2Service:
        '''(experimental) ECS service of the server with desiredCount: 1, minHealthyPercent: 0, maxHealthyPercent: 100.

        :stability: experimental
        :link: https://github.com/rajyan/low-cost-ecs#limitations
        '''
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.Ec2Service, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="topic")
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        '''(experimental) SNS topic used to notify certbot renewal failure.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "topic"))


@jsii.data_type(
    jsii_type="low-cost-ecs.LowCostECSProps",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "hosted_zone_domain": "hostedZoneDomain",
        "aws_cli_docker_tag": "awsCliDockerTag",
        "certbot_docker_tag": "certbotDockerTag",
        "certbot_schedule_interval": "certbotScheduleInterval",
        "container_insights": "containerInsights",
        "host_instance_spot_price": "hostInstanceSpotPrice",
        "host_instance_type": "hostInstanceType",
        "log_group": "logGroup",
        "record_domain_names": "recordDomainNames",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "server_task_definition": "serverTaskDefinition",
        "vpc": "vpc",
    },
)
class LowCostECSProps:
    def __init__(
        self,
        *,
        email: builtins.str,
        hosted_zone_domain: builtins.str,
        aws_cli_docker_tag: typing.Optional[builtins.str] = None,
        certbot_docker_tag: typing.Optional[builtins.str] = None,
        certbot_schedule_interval: typing.Optional[jsii.Number] = None,
        container_insights: typing.Optional[builtins.bool] = None,
        host_instance_spot_price: typing.Optional[builtins.str] = None,
        host_instance_type: typing.Optional[builtins.str] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
        record_domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        server_task_definition: typing.Optional[typing.Union["LowCostECSTaskDefinitionOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param email: (experimental) Email for expiration emails to register to your let's encrypt account.
        :param hosted_zone_domain: (experimental) Domain name of the hosted zone.
        :param aws_cli_docker_tag: (experimental) Docker image tag of amazon/aws-cli. This image is used to associate elastic ip on host instance startup, and run certbot cfn on ecs container startup. Default: - latest
        :param certbot_docker_tag: (experimental) Docker image tag of certbot/dns-route53 to create certificates. Default: - v1.29.0
        :param certbot_schedule_interval: (experimental) Certbot task schedule interval in days to renew the certificate. Default: - 60
        :param container_insights: (experimental) Enable container insights or not. Default: - undefined (container insights disabled)
        :param host_instance_spot_price: (experimental) The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Host instance asg would use spot instances if hostInstanceSpotPrice is set. Default: - undefined
        :param host_instance_type: (experimental) Instance type of the ECS host instance. Default: - t2.micro
        :param log_group: (experimental) Log group of the certbot task and the aws-cli task. Default: - Creates default cdk log group
        :param record_domain_names: (experimental) Domain names for A records to elastic ip of ECS host instance. Default: - [ props.hostedZone.zoneName ]
        :param removal_policy: (experimental) Removal policy for the file system and log group (if using default). Default: - RemovalPolicy.DESTROY
        :param security_groups: (experimental) Security group of the ECS host instance. Default: - Creates security group with allowAllOutbound and ingress rule (ipv4, ipv6) => (tcp 80, 443).
        :param server_task_definition: (experimental) Task definition for the server ecs task. Default: - Nginx server task definition defined in sampleTaskDefinition()
        :param vpc: (experimental) VPC of the ECS cluster and EFS file system. Default: - Creates vpc with only public subnets and no NAT gateways.

        :stability: experimental
        '''
        if isinstance(server_task_definition, dict):
            server_task_definition = LowCostECSTaskDefinitionOptions(**server_task_definition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a4e374b4001b2d1a00530b347f4892645cdf6f0c73a3b5609e0b85fb859de79)
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument hosted_zone_domain", value=hosted_zone_domain, expected_type=type_hints["hosted_zone_domain"])
            check_type(argname="argument aws_cli_docker_tag", value=aws_cli_docker_tag, expected_type=type_hints["aws_cli_docker_tag"])
            check_type(argname="argument certbot_docker_tag", value=certbot_docker_tag, expected_type=type_hints["certbot_docker_tag"])
            check_type(argname="argument certbot_schedule_interval", value=certbot_schedule_interval, expected_type=type_hints["certbot_schedule_interval"])
            check_type(argname="argument container_insights", value=container_insights, expected_type=type_hints["container_insights"])
            check_type(argname="argument host_instance_spot_price", value=host_instance_spot_price, expected_type=type_hints["host_instance_spot_price"])
            check_type(argname="argument host_instance_type", value=host_instance_type, expected_type=type_hints["host_instance_type"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument record_domain_names", value=record_domain_names, expected_type=type_hints["record_domain_names"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument server_task_definition", value=server_task_definition, expected_type=type_hints["server_task_definition"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "email": email,
            "hosted_zone_domain": hosted_zone_domain,
        }
        if aws_cli_docker_tag is not None:
            self._values["aws_cli_docker_tag"] = aws_cli_docker_tag
        if certbot_docker_tag is not None:
            self._values["certbot_docker_tag"] = certbot_docker_tag
        if certbot_schedule_interval is not None:
            self._values["certbot_schedule_interval"] = certbot_schedule_interval
        if container_insights is not None:
            self._values["container_insights"] = container_insights
        if host_instance_spot_price is not None:
            self._values["host_instance_spot_price"] = host_instance_spot_price
        if host_instance_type is not None:
            self._values["host_instance_type"] = host_instance_type
        if log_group is not None:
            self._values["log_group"] = log_group
        if record_domain_names is not None:
            self._values["record_domain_names"] = record_domain_names
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if server_task_definition is not None:
            self._values["server_task_definition"] = server_task_definition
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def email(self) -> builtins.str:
        '''(experimental) Email for expiration emails to register to your let's encrypt account.

        :stability: experimental
        :link: https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone_domain(self) -> builtins.str:
        '''(experimental) Domain name of the hosted zone.

        :stability: experimental
        '''
        result = self._values.get("hosted_zone_domain")
        assert result is not None, "Required property 'hosted_zone_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_cli_docker_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docker image tag of amazon/aws-cli.

        This image is used to associate elastic ip on host instance startup, and run certbot cfn on ecs container startup.

        :default: - latest

        :stability: experimental
        '''
        result = self._values.get("aws_cli_docker_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certbot_docker_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docker image tag of certbot/dns-route53 to create certificates.

        :default: - v1.29.0

        :stability: experimental
        :link: https://hub.docker.com/r/certbot/dns-route53/tags
        '''
        result = self._values.get("certbot_docker_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certbot_schedule_interval(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Certbot task schedule interval in days to renew the certificate.

        :default: - 60

        :stability: experimental
        '''
        result = self._values.get("certbot_schedule_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def container_insights(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable container insights or not.

        :default: - undefined (container insights disabled)

        :stability: experimental
        '''
        result = self._values.get("container_insights")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def host_instance_spot_price(self) -> typing.Optional[builtins.str]:
        '''(experimental) The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request.

        Host instance asg would use spot instances if hostInstanceSpotPrice is set.

        :default: - undefined

        :stability: experimental
        :link: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ecs.AddCapacityOptions.html#spotprice
        '''
        result = self._values.get("host_instance_spot_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host_instance_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Instance type of the ECS host instance.

        :default: - t2.micro

        :stability: experimental
        '''
        result = self._values.get("host_instance_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup]:
        '''(experimental) Log group of the certbot task and the aws-cli task.

        :default: - Creates default cdk log group

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup], result)

    @builtins.property
    def record_domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Domain names for A records to elastic ip of ECS host instance.

        :default: - [ props.hostedZone.zoneName ]

        :stability: experimental
        '''
        result = self._values.get("record_domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Removal policy for the file system and log group (if using default).

        :default: - RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) Security group of the ECS host instance.

        :default: - Creates security group with allowAllOutbound and ingress rule (ipv4, ipv6) => (tcp 80, 443).

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def server_task_definition(
        self,
    ) -> typing.Optional["LowCostECSTaskDefinitionOptions"]:
        '''(experimental) Task definition for the server ecs task.

        :default: - Nginx server task definition defined in sampleTaskDefinition()

        :see: sampleTaskDefinition
        :stability: experimental
        '''
        result = self._values.get("server_task_definition")
        return typing.cast(typing.Optional["LowCostECSTaskDefinitionOptions"], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) VPC of the ECS cluster and EFS file system.

        :default: - Creates vpc with only public subnets and no NAT gateways.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LowCostECSProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="low-cost-ecs.LowCostECSTaskDefinitionOptions",
    jsii_struct_bases=[],
    name_mapping={
        "containers": "containers",
        "task_definition": "taskDefinition",
        "volumes": "volumes",
    },
)
class LowCostECSTaskDefinitionOptions:
    def __init__(
        self,
        *,
        containers: typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinitionOptions, typing.Dict[builtins.str, typing.Any]]],
        task_definition: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinitionProps, typing.Dict[builtins.str, typing.Any]]] = None,
        volumes: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.Volume, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param containers: 
        :param task_definition: 
        :param volumes: 

        :stability: experimental
        '''
        if isinstance(task_definition, dict):
            task_definition = _aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinitionProps(**task_definition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__002ebbd53d2519dadc4020acc93b39be5a360ef0d6f0ca12153b8e9f6ca81d6e)
            check_type(argname="argument containers", value=containers, expected_type=type_hints["containers"])
            check_type(argname="argument task_definition", value=task_definition, expected_type=type_hints["task_definition"])
            check_type(argname="argument volumes", value=volumes, expected_type=type_hints["volumes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "containers": containers,
        }
        if task_definition is not None:
            self._values["task_definition"] = task_definition
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def containers(
        self,
    ) -> typing.List[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinitionOptions]:
        '''
        :stability: experimental
        '''
        result = self._values.get("containers")
        assert result is not None, "Required property 'containers' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinitionOptions], result)

    @builtins.property
    def task_definition(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinitionProps]:
        '''
        :stability: experimental
        '''
        result = self._values.get("task_definition")
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinitionProps], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.Volume]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ecs_ceddda9d.Volume]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LowCostECSTaskDefinitionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LowCostECS",
    "LowCostECSProps",
    "LowCostECSTaskDefinitionOptions",
]

publication.publish()

def _typecheckingstub__c0356d0ba92a1b88dbec557c9706dec10d39b53bd74af24510f519ceae784aea(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    email: builtins.str,
    hosted_zone_domain: builtins.str,
    aws_cli_docker_tag: typing.Optional[builtins.str] = None,
    certbot_docker_tag: typing.Optional[builtins.str] = None,
    certbot_schedule_interval: typing.Optional[jsii.Number] = None,
    container_insights: typing.Optional[builtins.bool] = None,
    host_instance_spot_price: typing.Optional[builtins.str] = None,
    host_instance_type: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    record_domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    server_task_definition: typing.Optional[typing.Union[LowCostECSTaskDefinitionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a4e374b4001b2d1a00530b347f4892645cdf6f0c73a3b5609e0b85fb859de79(
    *,
    email: builtins.str,
    hosted_zone_domain: builtins.str,
    aws_cli_docker_tag: typing.Optional[builtins.str] = None,
    certbot_docker_tag: typing.Optional[builtins.str] = None,
    certbot_schedule_interval: typing.Optional[jsii.Number] = None,
    container_insights: typing.Optional[builtins.bool] = None,
    host_instance_spot_price: typing.Optional[builtins.str] = None,
    host_instance_type: typing.Optional[builtins.str] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_ceddda9d.ILogGroup] = None,
    record_domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    server_task_definition: typing.Optional[typing.Union[LowCostECSTaskDefinitionOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__002ebbd53d2519dadc4020acc93b39be5a360ef0d6f0ca12153b8e9f6ca81d6e(
    *,
    containers: typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.ContainerDefinitionOptions, typing.Dict[builtins.str, typing.Any]]],
    task_definition: typing.Optional[typing.Union[_aws_cdk_aws_ecs_ceddda9d.Ec2TaskDefinitionProps, typing.Dict[builtins.str, typing.Any]]] = None,
    volumes: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecs_ceddda9d.Volume, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
