from cfneval.resource_attribute_generator import ResourceAttributeGenerator


class ParamStoreAttributeGenerator(ResourceAttributeGenerator):

    def get_attributes(self) -> dict:
        return {
            "Type": self._resource["Properties"]["Type"],
            "Value": self._resource["Properties"]["Value"],
        }

    def get_ref(self) -> str:
        return self._resource["Properties"].get(
            "Name", self.generate_random_resource_name()
        )


def register_bundled_types(registry):
    registry.register_resource_attributes(
        "AWS::SSM::Parameter", ParamStoreAttributeGenerator
    )
