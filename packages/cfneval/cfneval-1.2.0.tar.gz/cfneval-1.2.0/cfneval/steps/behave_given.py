import json
from behave import given
from cfn_flip import to_json
from cfneval.template_evaluator import TemplateEvaluator


@given('the cfn template "{path}"')
def step_impl(context, path):
    context.evaluator = TemplateEvaluator()

    with open(path, "r") as f:
        contents = f.read()
    try:
        template = json.loads(to_json(contents))
    except:
        template = json.loads(contents)
    context.evaluator.set_template(template)


@given('the resource "{name}" will output')
def step_impl(context, name):
    context.evaluator.add_mock(name, json.loads(context.text))


@given("I have params")
def step_impl(context):
    if context.table is not None:
        for row in context.table:
            context.evaluator.add_parameter(row["key"], row["value"])
    else:
        context.evaluator.add_parameters(json.loads(context.text))


@given("I have exports")
def step_impl(context):
    if context.table is not None:
        for row in context.table:
            context.evaluator.add_export(row["key"], row["value"])
    else:
        context.evaluator.add_exports(json.loads(context.text))


@given("parameter checking is disabled")
def step_impl(context):
    context.evaluator.parameter_checking = False


@given("reference checking is disabled")
def step_impl(context):
    context.evaluator.reference_checking = False
