"""Infrastructure stack."""
from aws_cdk import (
    Stack,
    aws_lambda as Lambda,
    aws_apigatewayv2_alpha as APIGW,
    aws_apigatewayv2_integrations_alpha as Integrations
)
from constructs import Construct
from os import path


class InfraStack(Stack):
    """Infrastructure stack."""

    def fxn(self, name: str) -> str:
        return path.join(path.dirname(path.realpath(__file__)), '..', '..', name)


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        function = Lambda.Function(
            self,
            "function",
            code=Lambda.Code.from_asset(self.fxn('achievements')),
            handler="main.handler",
            runtime=Lambda.Runtime.PYTHON_3_9,
            environment={
                'PYTHONPATH': './vendor',
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
