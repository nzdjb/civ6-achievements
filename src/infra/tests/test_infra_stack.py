import aws_cdk as core
import aws_cdk.assertions as assertions

from pytest import fixture

from infra.infra_stack import InfraStack


def test_lambda_created(stack_template):
    """Test that the lambda is created correctly."""

    stack_template.has_resource_properties("AWS::Lambda::Function", {})


@fixture(autouse=True)
def stack_template():
    """Stack template fixture"""
    app = core.App()
    stack = InfraStack(app, "infra")
    template = assertions.Template.from_stack(stack)
    yield template
