import click
import json
from cfn_flip import to_json, to_yaml
from cfneval.template_evaluator import TemplateEvaluator


@click.command()
@click.option("--parameter", "-p", "params", type=(str, str), multiple=True)
@click.option("--template", "-t", "template_path", type=str, required=True)
@click.option("--output", "-o", "output", type=str)
@click.option("--account-id", "account_id", type=str, default="123456789012")
@click.option("--region", "region", type=str, default="us-east-1")
def cli(params, template_path, output, account_id, region):
    p = dict(params)

    evaluator = TemplateEvaluator()
    evaluator.region = region
    evaluator.account_id = account_id
    evaluator.add_parameters(p)

    with open(template_path, "r") as f:
        contents = f.read()
    try:
        template = json.loads(to_json(contents))
        fmt = "yaml"
    except:
        template = json.loads(contents)
        fmt = "json"

    evaluator.set_template(template)
    evaluator.generate_effective_template()

    o = evaluator.get_effective_template()

    if output:
        with open(output, "w") as f:
            if fmt == "json":
                f.write(json.dumps(o, indent=2))
            else:
                f.write(to_yaml(json.dumps(o, indent=2)))
    else:
        if fmt == "json":
            print(json.dumps(o, indent=2))
        else:
            print(to_yaml(json.dumps(o, indent=2)))


if __name__ == "__main__":
    cli()
