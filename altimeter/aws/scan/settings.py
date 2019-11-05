"""AWS Resource classes."""
from typing import Tuple, Type

from altimeter.aws.resource.resource_spec import AWSResourceSpec
from altimeter.aws.resource.account import AccountResourceSpec
from altimeter.aws.resource.awslambda.function import LambdaFunctionResourceSpec
from altimeter.aws.resource.dynamodb.dynamodb_table import DynamoDbTableResourceSpec
from altimeter.aws.resource.ec2.image import EC2ImageResourceSpec
from altimeter.aws.resource.ec2.instance import EC2InstanceResourceSpec
from altimeter.aws.resource.ec2.network_interface import EC2NetworkInterfaceResourceSpec
from altimeter.aws.resource.ec2.region import RegionResourceSpec
from altimeter.aws.resource.ec2.route_table import EC2RouteTableResourceSpec
from altimeter.aws.resource.ec2.transit_gateway_vpc_attachment import (
    TransitGatewayVpcAttachmentResourceSpec,
)
from altimeter.aws.resource.ec2.security_group import SecurityGroupResourceSpec
from altimeter.aws.resource.ec2.snapshot import EBSSnapshotResourceSpec
from altimeter.aws.resource.ec2.subnet import SubnetResourceSpec
from altimeter.aws.resource.ec2.transit_gateway import TransitGatewayResourceSpec
from altimeter.aws.resource.ec2.volume import EBSVolumeResourceSpec
from altimeter.aws.resource.ec2.vpc import VPCResourceSpec
from altimeter.aws.resource.elasticloadbalancing.load_balancer import LoadBalancerResourceSpec
from altimeter.aws.resource.elasticloadbalancing.target_group import TargetGroupResourceSpec
from altimeter.aws.resource.events.cloudwatchevents_rule import EventsRuleResourceSpec
from altimeter.aws.resource.iam.iam_saml_provider import IAMSAMLProviderResourceSpec
from altimeter.aws.resource.iam.policy import IAMPolicyResourceSpec
from altimeter.aws.resource.iam.role import IAMRoleResourceSpec
from altimeter.aws.resource.iam.user import IAMUserResourceSpec
from altimeter.aws.resource.kms.key import KMSKeyResourceSpec
from altimeter.aws.resource.organizations.org import OrgResourceSpec
from altimeter.aws.resource.organizations.ou import OUResourceSpec
from altimeter.aws.resource.organizations.account import OrgsAccountResourceSpec
from altimeter.aws.resource.rds.instance import RDSInstanceResourceSpec
from altimeter.aws.resource.rds.snapshot import RDSSnapshotResourceSpec
from altimeter.aws.resource.s3.bucket import S3BucketResourceSpec

# To enable a resource to be scanned, add it here.
RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    DynamoDbTableResourceSpec,
    EBSSnapshotResourceSpec,
    EBSVolumeResourceSpec,
    EC2ImageResourceSpec,
    EC2InstanceResourceSpec,
    EC2NetworkInterfaceResourceSpec,
    EC2RouteTableResourceSpec,
    EventsRuleResourceSpec,
    IAMPolicyResourceSpec,
    IAMRoleResourceSpec,
    IAMSAMLProviderResourceSpec,
    IAMUserResourceSpec,
    KMSKeyResourceSpec,
    LambdaFunctionResourceSpec,
    LoadBalancerResourceSpec,
    RDSInstanceResourceSpec,
    RDSSnapshotResourceSpec,
    S3BucketResourceSpec,
    SecurityGroupResourceSpec,
    SubnetResourceSpec,
    TargetGroupResourceSpec,
    TransitGatewayResourceSpec,
    TransitGatewayVpcAttachmentResourceSpec,
    VPCResourceSpec,
)

INFRA_RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    AccountResourceSpec,
    RegionResourceSpec,
)

ORG_RESOURCE_SPEC_CLASSES: Tuple[Type[AWSResourceSpec], ...] = (
    OrgResourceSpec,
    OrgsAccountResourceSpec,
    OUResourceSpec,
)