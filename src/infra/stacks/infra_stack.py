"""Infrastructure stack."""
from aws_cdk import (
    Fn,
    Stack,
    aws_lambda as Lambda,
    aws_cloudfront as CloudFront,
    aws_cloudfront_origins as CloudFrontOrigins,
    aws_s3 as S3,
    aws_s3_deployment as Deployment,
    aws_ssm as SSM,
    aws_route53 as Route53,
    aws_route53_targets as Targets,
    aws_certificatemanager as ACM,
)
import aws_cdk.aws_apigatewayv2_alpha as APIGW
import aws_cdk.aws_apigatewayv2_integrations_alpha as Integrations
from constructs import Construct
from util.env_string_parameter import EnvStringParameter
from os import path, getenv


class InfraStack(Stack):
    """Infrastructure stack."""

    def fxn(self, name: str) -> str:
        return path.join(self.root(), "dist", f"src.{name}", "lambda.zip")

    def root(self) -> str:
        return path.join(path.dirname(path.realpath(__file__)), "..", "..", "..")

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain_name = scope.node.try_get_context("domain_name")
        hosted_zone_name = scope.node.try_get_context("hosted_zone_name")

        api_key = EnvStringParameter(
            self, "api_key_parameter", "/steam_achievements/API_KEY", "STEAM_API_KEY"
        )

        function = Lambda.Function(
            self,
            "function",
            function_name="steam-achievements-achievements",
            code=Lambda.Code.from_asset(self.fxn("achievements")),
            handler="lambdex_handler.handler",
            runtime=Lambda.Runtime.PYTHON_3_9,
            environment={"STEAM_API_PARAMETER": api_key.parameter_name},
        )
        api_key.grant_read(function)

        http_api = APIGW.HttpApi(self, "api", api_name="achievements_api")

        uris = [
            "/achievements",
            "/achievements/{app_id}",
            "/achievements/{app_id}/{steam_id}",
        ]
        integration = Integrations.HttpLambdaIntegration("integration", function)
        for uri in uris:
            APIGW.HttpRoute(
                self,
                "route-" + uri,
                route_key=APIGW.HttpRouteKey.with_(uri, APIGW.HttpMethod.GET),
                http_api=http_api,
                integration=integration,
            )
        bucket = S3.Bucket(self, "bucket")

        certificate = None
        if hosted_zone_name:
            hosted_zone = Route53.HostedZone.from_lookup(
                self, "hosted_zone", domain_name=hosted_zone_name
            )
            certificate = ACM.DnsValidatedCertificate(
                self,
                "certificate",
                domain_name=domain_name,
                hosted_zone=hosted_zone,
                validation=ACM.CertificateValidation.from_dns(hosted_zone),
                region="us-east-1",
            )

        distribution = CloudFront.Distribution(
            self,
            "distribution",
            default_behavior=CloudFront.BehaviorOptions(
                origin=CloudFrontOrigins.S3Origin(bucket),
                viewer_protocol_policy=CloudFront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
            additional_behaviors={
                "/achievements/*": CloudFront.BehaviorOptions(
                    origin=CloudFrontOrigins.HttpOrigin(
                        Fn.select(1, Fn.split("://", http_api.api_endpoint))
                    ),
                    viewer_protocol_policy=CloudFront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                )
            },
            domain_names=[domain_name] if domain_name is not None else None,
            certificate=certificate,
        )

        Deployment.BucketDeployment(
            self,
            "web-deployment",
            destination_bucket=bucket,
            sources=[Deployment.Source.asset(path.join(self.root(), "src", "web"))],
            distribution=distribution,
        )

        if hosted_zone_name:
            Route53.ARecord(
                self,
                "record",
                zone=hosted_zone,
                record_name=domain_name,
                target=Route53.RecordTarget.from_alias(
                    Targets.CloudFrontTarget(distribution)
                ),
            )
