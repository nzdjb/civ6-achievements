"""Construct for storing an environment variable in an SSM Parameter"""

from aws_cdk import aws_ssm as SSM
from constructs import Construct
from os import getenv


class EnvStringParameter(SSM.StringParameter):
    def __init__(
        self, scope: Construct, id: str, parameter_name, env_variable_name
    ) -> None:

        if getenv(env_variable_name):
            value = getenv(env_variable_name)
        else:
            value = SSM.StringParameter.from_string_parameter_attributes(
                scope, f"retrieved_${id}", parameter_name=parameter_name
            ).string_value

        super().__init__(scope, id, parameter_name=parameter_name, string_value=value)
