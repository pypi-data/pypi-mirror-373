# cfneval

cfneval is a Python tool for taking a CloudFormation template and evaluating all the conditional logic in order to come up with the `effective` template that actually gets used.  You can use the tool just to see what the effective version looks like, or you can run it as part of a [behave](https://github.com/behave/behave) test suite to automatically regression test your CloudFormation template.

## Step Documentation

[Quickstart Guide](https://github.com/Vanguard-oss/cfneval/blob/master/docs/quickstart.md)

[Step Reference](https://github.com/Vanguard-oss/cfneval/blob/master/docs/reference.md)

[Compatability Guide](https://github.com/Vanguard-oss/cfneval/blob/master/docs/compatability.md)

## CLI Usage

```
Usage: cfneval  [OPTIONS]

Options:
  -p, --parameter <TEXT TEXT>...
  -t, --template TEXT             [required]
  -o, --output TEXT
  --account-id TEXT
  --region TEXT
  --help                          Show this message and exit.

```

### template

Use the `-t` or `--template` argument to point to the CloudFormation template you want to evaluate.  cfneval will auto-detect whether the template is in `json` or `yaml` format.  It will use `cfnflip` to parse `yaml` templates.

### parameters

Use the `-p` or `--parameter` argument multiple times to specify the parameters that will be passed into the CloudFormation template.

### output

Use the `-o` or `--output` argument to specify the filename to write the effective template to.  If this argument is omitted, then the effective template will be written to stdout instead of to a file.  The output will be in the same format as the input.

### account-id

Use the `--account-id` argument to simulate evaluating the template in a specific account.  It defaults to `123456789012`.

### region

Use the `--region` argument to simulate evaluating the template in another region.  It defaults to `us-east-1`.

## Behave CLI usage

cfneval comes with a wrapper around *behave* called *behave-cfn*.  That wrapper comes with the cfneval given/when/then's pre-registered and ready to use.  You just need to put your features in a *features* folder.

## Behave steps usage

cfneval can be integrated directly into a *behave* project.  Add the following code into a step file within **features/steps/**.

```
from cfneval.behave_steps import register_behave_steps

register_behave_steps()
```

