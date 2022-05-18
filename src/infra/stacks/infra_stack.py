"""Infrastructure stack."""
from aws_cdk import (
    Fn,
    Stack,
    aws_lambda as Lambda,
    aws_cloudfront as CloudFront,
    aws_cloudfront_origins as CloudFrontOrigins,
    aws_s3 as S3,
    aws_s3_deployment as Deployment,
)
import aws_cdk.aws_apigatewayv2_alpha as APIGW
import aws_cdk.aws_apigatewayv2_integrations_alpha as Integrations
from constructs import Construct
from os import path


class InfraStack(Stack):
    """Infrastructure stack."""

    def fxn(self, name: str) -> str:
        return path.join(self.root(), 'dist', f'src.{name}', 'lambda.zip')

    def root(self) -> str:
        return path.join(path.dirname(path.realpath(__file__)), '..', '..', '..')

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        function = Lambda.Function(
            self,
            "function",
            code=Lambda.Code.from_asset(self.fxn('achievements')),
            handler="lambdex_handler.handler",
            runtime=Lambda.Runtime.PYTHON_3_9,
            environment={
                'STEAM_API_KEY': ''
            }
        )

        http_api = APIGW.HttpApi(self, 'api', api_name='achievements_api')

        uris = [
            '/achievements',
            '/achievements/{app_id}',
            '/achievements/{app_id}/{steam_id}'
        ]
        integration = Integrations.HttpLambdaIntegration('integration', function)
        for uri in uris:
            APIGW.HttpRoute(
                self,
                'route-'+uri, 
                route_key=APIGW.HttpRouteKey.with_(uri, APIGW.HttpMethod.GET),
                http_api=http_api,
                integration=integration
            )
        bucket = S3.Bucket(self, 'bucket')
        distribution = CloudFront.Distribution(
                self,
                'distribution',
                default_behavior=CloudFront.BehaviorOptions(
                    origin=CloudFrontOrigins.S3Origin(bucket),
                ),
                default_root_object='index.html',
                additional_behaviors={
                    '/achievements/*': CloudFront.BehaviorOptions(
                        origin=CloudFrontOrigins.HttpOrigin(
                            Fn.select(1, Fn.split('://', http_api.api_endpoint))
                        )
                    )
                }
            )
        Deployment.BucketDeployment(
            self,
            'web-deployment',
            destination_bucket=bucket,
            sources=[
                Deployment.Source.asset(path.join(self.root(), 'src', 'web'))
            ],
            distribution=distribution
        )
