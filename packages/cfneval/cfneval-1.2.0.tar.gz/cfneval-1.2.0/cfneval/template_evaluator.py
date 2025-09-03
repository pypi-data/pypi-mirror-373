from benedict import benedict
from cfneval.resource_attributes import ResourceAttributeRegistry


class TemplateEvaluator:
    """
    Class that can generate the effective Cloudformation template
    """

    def __init__(self):
        self._template: dict = {}
        self._params: dict = {}
        self._region: str = "us-east-1"
        self._partition: str = "aws"
        self._account_id: str = "123456789012"
        self._stack_name: str = "mystack"
        self._ssm: dict = {}
        self._exports: dict = {}
        self._mocks: dict = {}
        self._result: dict = {
            "Parameters": {},
            "Conditions": {},
            "Resources": {},
            "Outputs": {},
        }
        self._resource_attrs: ResourceAttributeRegistry = ResourceAttributeRegistry()
        self._parameter_checking = True
        self._reference_checking = True

    @property
    def region(self) -> str:
        return self._region

    @region.setter
    def region(self, value: str):
        self._region = value

    @property
    def partition(self) -> str:
        return self._partition

    @partition.setter
    def partition(self, value: str):
        self._partition = value

    @property
    def account_id(self) -> str:
        return self._account_id

    @account_id.setter
    def account_id(self, value: str):
        self._account_id = value

    @property
    def stack_name(self) -> str:
        return self._stack_name

    @stack_name.setter
    def stack_name(self, value: str):
        self._stack_name = value

    @property
    def parameter_checking(self) -> bool:
        return self._parameter_checking

    @parameter_checking.setter
    def parameter_checking(self, value: bool):
        self._parameter_checking = value

    @property
    def reference_checking(self) -> bool:
        return self._reference_checking

    @reference_checking.setter
    def reference_checking(self, value: bool):
        self._reference_checking = value

    def add_mock(self, resource_name: str, response: dict):
        """
        Add a mock response for a resource
        """
        self._mocks[resource_name] = response

    def add_parameter(self, key: str, value):
        """
        Add a parameter value
        """
        self._params[key] = value

    def add_parameters(self, values: dict):
        """
        Add multiple parameter values
        """
        self._params.update(values)

    def add_export(self, key: str, value):
        """
        Add a export value
        """
        self._exports[key] = value

    def add_exports(self, values: dict):
        """
        Add multiple export values
        """
        self._exports.update(values)

    def set_template(self, template: dict):
        """
        Set the template to use.  Must be parsed from json
        """
        self._template = template

    def _calculate_params(self):
        """
        Calculate what the effective parameters are
        """
        self._calc_params = {}
        for k, d in self._template.get("Parameters", {}).items():
            if d.get("Type") == "CommaDelimitedList":
                if k in self._params:
                    self._calc_params[k] = self._params[k].split(",")
                elif "Default" in d:
                    self._calc_params[k] = d["Default"].split(",")
                elif self.parameter_checking:
                    raise Exception(f"Missing required param {k}")
            else:
                if k in self._params:
                    self._calc_params[k] = str(self._params[k])
                elif "Default" in d:
                    self._calc_params[k] = str(d["Default"])
                elif self.parameter_checking:
                    raise Exception(f"Missing required param {k}")
            if self.parameter_checking and k in self._calc_params:
                self._result["Parameters"][k] = {
                    "Type": d.get("Type"),
                    "Default": self._calc_params[k],
                }

    def _calculate_conditions(self):
        """
        Calculate the boolean result of each condition
        """
        self._calc_conditions = {}

        for k, d in self._template.get("Conditions", {}).items():
            self._calc_conditions[k] = self._eval_condition(d)

            self._result["Conditions"][k] = self._calc_conditions[k]

    def _eval_condition(self, cond_data: dict):
        """
        Recursively evaluate a single Condition dictionary
        """
        if "Ref" in cond_data:
            return self._get_ref(cond_data["Ref"])
        elif "Fn::Not" in cond_data:
            return not self._eval_condition(cond_data["Fn::Not"][0])
        elif "Condition" in cond_data:
            condition_name = cond_data["Condition"]
            if condition_name not in self._calc_conditions:
                self._calc_conditions[condition_name] = self._eval_condition(
                    self._template.get("Conditions", {})[condition_name]
                )
            return self._calc_conditions[condition_name]
        elif "Fn::Equals" in cond_data:
            return self._eval_condition(
                cond_data["Fn::Equals"][0]
            ) == self._eval_condition(cond_data["Fn::Equals"][1])
        elif "Fn::Join" in cond_data:
            delim = cond_data["Fn::Join"][0]
            values = cond_data["Fn::Join"][1]
            if type(values) == dict:
                values = self._eval_condition(values)

            if not self.reference_checking:
                values = map(
                    lambda x: x["Ref"] if type(x) == dict and "Ref" in x else x, values
                )

            values = list(map(lambda x: self._eval_condition(x), values))
            res = delim.join(values)
            return res
        elif "Fn::Select" in cond_data:
            idx = cond_data["Fn::Select"][0]
            values = cond_data["Fn::Select"][1]
            if type(values) == dict:
                values = self._eval_condition(values)
            return values[idx]
        elif "Fn::Split" in cond_data:
            delim = cond_data["Fn::Split"][0]
            values = cond_data["Fn::Split"][1]
            if type(values) == dict:
                values = self._eval_condition(values)
            return values.split(delim)
        elif "Fn::And" in cond_data:
            res = True
            for v in cond_data["Fn::And"]:
                res = res and self._eval_condition(v)
            return res
        elif "Fn::Or" in cond_data:
            res = False
            for v in cond_data["Fn::Or"]:
                res = res or self._eval_condition(v)
            return res
        elif type(cond_data) == dict:
            k = list(cond_data.keys())[0]
            raise Exception(f"Unknown intrinsic {k}")
        elif type(cond_data) == str:
            return cond_data

    def _get_ref(self, value):
        if value in self._calc_params:
            return self._calc_params[value]
        if value == "AWS::Region":
            return self._region
        if value == "AWS::AccountId":
            return self._account_id
        if value == "AWS::StackName":
            return self._stack_name
        if value == "AWS::NoValue":
            return None
        if value in self._template.get("Resources", {}):
            # This is a resource

            if value in self._mocks:
                return self._mocks[value]

            ref = self._resource_attrs.evaluate_ref(
                stack_name=self._stack_name,
                resource_name=value,
                resource=self._calculate_resource_node(
                    self._template["Resources"][value]
                ),
                account_id=self._account_id,
                region=self._region,
            )

            if ref is not None:
                return ref
            else:
                # If we have no mock, then return the name of the resource back
                return value

        if not self.reference_checking:
            # If we have disabled reference checking, then just return the Ref back
            return {"Ref": value}

        raise Exception(f"Unknown Ref {value}")

    def _calculate_resources(self):
        """
        Calculate the effective json for each resource in the template
        """
        for k, d in list(self._template.get("Resources", {}).items()):
            if "Condition" in d:
                condition_name = d["Condition"]
                if self.is_condition_true(condition_name):
                    self._result["Resources"][k] = self._calculate_resource(d)
            else:
                self._result["Resources"][k] = self._calculate_resource(d)

    def _calculate_resource(self, res):
        """
        Calculate the effective json for a single resource
        """
        resp = self._calculate_resource_node(res)

        # Don't bother keeping the Condition field
        if "Condition" in resp:
            del resp["Condition"]
        return resp

    def _calculate_outputs(self):
        """
        Calculate the effective json for each resource in the template
        """
        for k, d in list(self._template.get("Outputs", {}).items()):
            if "Condition" in d:
                condition_name = d["Condition"]
                if self.is_condition_true(condition_name):
                    self._result["Outputs"][k] = self._calculate_resource_node(
                        self._calculate_output(d)
                    )
            else:
                self._result["Outputs"][k] = self._calculate_resource_node(
                    self._calculate_output(d)
                )

    def _calculate_output(self, res):
        res["Value"] = self._calculate_resource_node(res["Value"])
        return res

    def _is_instrinsic(self, node):
        """
        Determine if the node is an instrinsic lookup
        """
        # Handle an empty dict
        if len(node) != 1:
            return False
        k = list(node.keys())[0]
        if k == "Ref" or k.startswith("Fn::"):
            return True
        return False

    def _get_att(self, path_list: list, *, extra_values: dict = None):
        res_name = path_list[0]

        d = benedict(self._mocks)
        path = ".".join(path_list)
        if path in d:
            return d[path]

        res = self._resource_attrs.evaluate_attributes(
            stack_name=self._stack_name,
            resource_name=res_name,
            resource=self._calculate_resource_node(
                self._template["Resources"][res_name]
            ),
            account_id=self._account_id,
            region=self._region,
        )
        if res is not None:
            if path_list[1] in res:
                return res[path_list[1]]
            raise Exception(f"Could not find attribute {path_list[1]} in {res}")

        if not self.reference_checking:
            return path

        raise Exception(f"Missing mock for {path}")

    def _eval_instrinsic(self, node: dict):
        """
        Evaluate an instrinsic in the Resources or Outputs section
        """
        if "Ref" in node:
            return self._get_ref(node["Ref"])
        elif "Fn::GetAtt" in node:
            return self._get_att(node["Fn::GetAtt"])

        elif "Fn::Sub" in node:
            value = ""
            extra_values = {}
            if type(node["Fn::Sub"]) == str:
                value = node["Fn::Sub"]
            elif type(node["Fn::Sub"]) == dict:
                if self._is_instrinsic(node["Fn::Sub"]):
                    value = self._eval_instrinsic(node["Fn::Sub"])
                else:
                    raise Exception("Fn::Sub called with invalid intrinsic")
            else:
                value = node["Fn::Sub"][0]
                extra_values = self._calculate_resource_node(node["Fn::Sub"][1])
            while "${" in value:
                idx = value.find("${")
                # Find the first '}' that happens after the ${}
                end_of_var = value[idx + 2 :].find("}") + idx + 2
                var_name = value[idx + 2 : end_of_var]

                if "." in var_name:
                    lookup_value = self._get_att(
                        var_name.split("."), extra_values=extra_values
                    )
                elif var_name in extra_values:
                    lookup_value = extra_values[var_name]
                else:
                    lookup_value = self._get_ref(var_name)

                if (
                    not self.reference_checking
                    and type(lookup_value) == dict
                    and "Ref" in lookup_value
                ):
                    value = value[0:idx] + lookup_value["Ref"] + value[end_of_var + 1 :]
                else:
                    value = value[0:idx] + lookup_value + value[end_of_var + 1 :]

            return value

        elif "Fn::Join" in node:
            delim = node["Fn::Join"][0]
            values = node["Fn::Join"][1]
            if type(values) == dict:
                values = self._eval_instrinsic(values)
            values = list(
                filter(
                    lambda x: x is not None,
                    map(lambda x: self._eval_instrinsic(x), values),
                )
            )
            if not self.reference_checking:
                values = map(
                    lambda x: x["Ref"] if type(x) == dict and "Ref" in x else x, values
                )
            res = delim.join(values)
            return res
        elif "Fn::If" in node:
            condition_name = node["Fn::If"][0]
            path1 = node["Fn::If"][1]
            path2 = node["Fn::If"][2]

            if condition_name not in self._calc_conditions:
                raise Exception(f"Unknown condition named {condition_name}")
            if self._calc_conditions[condition_name]:
                return self._calculate_resource_node(path1)
            else:
                return self._calculate_resource_node(path2)

        elif "Fn::FindInMap" in node:
            mapping_name = node["Fn::FindInMap"][0]
            key1 = self._calculate_resource_node(node["Fn::FindInMap"][1])
            key2 = self._calculate_resource_node(node["Fn::FindInMap"][2])
            return self._template["Mappings"][mapping_name][key1][key2]
        elif "Fn::Select" in node:
            idx = node["Fn::Select"][0]
            values = node["Fn::Select"][1]
            if type(values) == dict:
                values = self._eval_instrinsic(values)
            return self._calculate_resource_node(values[idx])
        elif "Fn::Split" in node:
            delim = node["Fn::Split"][0]
            values = node["Fn::Split"][1]
            if type(values) == dict:
                values = self._eval_instrinsic(values)
            return self._calculate_resource_node(values.split(delim))
        elif "Fn::ImportValue" in node:
            values = node["Fn::ImportValue"]
            if type(values) == dict:
                values = self._eval_instrinsic(values)
            return self._exports[values]
        elif type(node) == str:
            return node
        elif type(node) == dict:
            k = list(node.keys())[0]
            raise Exception(f"Unknown intrinsic {k}")
        else:
            return self._calculate_resource_node(node)

    def _calculate_resource_node(self, node):
        if type(node) == list:
            return list(
                filter(
                    lambda x: x is not None,
                    map(lambda x: self._calculate_resource_node(x), node),
                )
            )
        elif type(node) == dict and self._is_instrinsic(node):
            return self._eval_instrinsic(node)
        elif type(node) == dict:
            resp = {}
            for k, v in node.items():
                value = self._calculate_resource_node(v)
                if value is not None:
                    resp[k] = value
            return resp
        else:
            return node

    def generate_effective_template(self):
        """
        Generate and return the effective template
        """
        self._calculate_params()
        self._calculate_conditions()
        self._calculate_resources()
        self._calculate_outputs()
        return self._result

    def is_condition_true(self, name):
        """
        Check if a Condition would evaluate to true given the parameters
        """
        return self._calc_conditions[name]

    def will_resource_be_created(self, name):
        """
        Check if a resource would be created given the Conditions
        """
        return name in self._result["Resources"]

    def get_effective_template(self):
        """
        Return the effective template
        """
        return self._result
