import json
from behave import then
from jsonpath_ng.ext import parser


@then('the Condition "{name}" is {value}')
def step_impl(context, name, value):
    assert context.evaluator.is_condition_true(name) == (value == "true")


@then('the Resource "{name}" will not be created')
def step_impl(context, name):
    assert not context.evaluator.will_resource_be_created(name)


@then('the Resource "{name}" will be created')
def step_impl(context, name):
    assert context.evaluator.will_resource_be_created(name)


@then('the Resource "{name}" path "{expr}" exists')
def step_impl(context, name, expr):
    jpexpr = parser.parse(expr)
    haystack = context.evaluator.get_effective_template()["Resources"][name]
    results = jpexpr.find(haystack)
    assert len(results) > 0


@then('the Resource "{name}" path "{expr}" does not exist')
def step_impl(context, name, expr):
    jpexpr = parser.parse(expr)
    haystack = context.evaluator.get_effective_template()["Resources"][name]
    results = jpexpr.find(haystack)
    assert len(results) == 0


@then('the Resource "{name}" path "{expr}" matches "{value}"')
def step_impl(context, name, expr, value):
    jpexpr = parser.parse(expr)
    haystack = context.evaluator.get_effective_template()["Resources"][name]
    results = jpexpr.find(haystack)
    assert len(results) == 1
    print(str(results[0].value))
    assert str(results[0].value) == value


@then('the Resource "{name}" path "{expr}" length is "{value}"')
def step_impl(context, name, expr, value):
    jpexpr = parser.parse(expr)
    haystack = context.evaluator.get_effective_template()["Resources"][name]
    results = jpexpr.find(haystack)
    assert len(results) == 1
    assert len(results[0].value) == int(value)


@then('the Resource "{name}" path "{expr}" contains "{value}"')
def step_impl(context, name, expr, value):
    jpexpr = parser.parse(expr)
    haystack = context.evaluator.get_effective_template()["Resources"][name]
    results = jpexpr.find(haystack)
    assert len(results) == 1
    assert value in results[0].value


@then('the Output "{name}" will be set to "{value}"')
def step_impl(context, name, value):
    print(str(context.evaluator.get_effective_template()["Outputs"]))
    assert context.evaluator.get_effective_template()["Outputs"][name]["Value"] == value


@then('the Output "{name}" path "{path}" matches "{value}"')
def step_impl(context, name, path, value):
    jpexpr = parser.parse(path)
    haystack = context.evaluator.get_effective_template()["Outputs"][name]["Value"]
    results = jpexpr.find(haystack)
    assert len(results) == 1
    assert str(results[0].value) == value


@then('the Output "{name}" will be created')
def step_impl(context, name):
    assert name in context.evaluator.get_effective_template()["Outputs"]


@then('the Output "{name}" will not be created')
def step_impl(context, name):
    assert name not in context.evaluator.get_effective_template()["Outputs"]


@then('the evaluation failed with error "{msg}"')
def step_impl(context, msg):
    if context.exception is None:
        print(context.evaluator.get_effective_template())
    assert context.exception is not None
    print(str(context.exception))
    assert msg in str(context.exception)
