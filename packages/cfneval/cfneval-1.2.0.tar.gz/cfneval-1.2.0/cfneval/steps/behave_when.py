import traceback

from behave import when


@when("I evaluate the template")
def step_impl(context):
    context.evaluator.generate_effective_template()


@when("I attempt to evaluate the template")
def step_impl(context):
    try:
        context.evaluator.generate_effective_template()
        context.exception = None
    except Exception as e:
        traceback.print_exc()
        context.exception = e
