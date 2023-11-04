from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_logs as logs,
    Duration
)
from constructs import Construct
from aws_cdk import aws_iam as iam

class Ec2LookupExampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ec2_lookup_lambda = _lambda.Function(
            self, 'EC2LookupHandler',
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('lambda'),
            handler='poc-v1-ec2-lookup.lambda_handler',
            timeout=Duration.seconds(10),
            vpc_subnets=<private subnet>,
            security_groups=<private security group>

        apigw.LambdaRestApi(
            self, 'POC_V1_EC2_Lookup_Endpoint',
            handler=ec2_lookup_lambda,
        )

        '''
        lambda_pricing_role = iam.Role(
            self, 
            id='lambda-pricing-role',
            role_name='lambda-pricing-role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        '''

        lambda_pricing_role = ec2_lookup_lambda.role
        
        lambda_pricing_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["pricing:GetProducts"]
            )
        )