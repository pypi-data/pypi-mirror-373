from cfneval.resource_attribute_generator import ResourceAttributeGenerator


class EcsServiceAttributeGenerator(ResourceAttributeGenerator):

    def get_attributes(self) -> dict:
        service_name = self._resource["Properties"].get(
            "ServiceName", self.generate_random_resource_name()
        )
        return {
            "Name": service_name,
            "ServiceArn": f"aws:{self._partition}:ecs:{self._region}:{self._account_id}:service/{service_name}",
        }

    def get_ref(self) -> str:
        return self.get_attributes()["ServiceArn"]


class EcsClusterAttributeGenerator(ResourceAttributeGenerator):

    def get_attributes(self) -> dict:
        name = self._resource["Properties"].get(
            "ClusterName", self.generate_random_resource_name()
        )
        return {
            "Arn": f"aws:{self._partition}:ecs:{self._region}:{self._account_id}:cluster/{name}",
        }

    def get_ref(self) -> str:
        name = self._resource["Properties"].get(
            "ClusterName", self.generate_random_resource_name()
        )
        return name


def register_bundled_types(registry):
    registry.register_resource_attributes(
        "AWS::ECS::Service", EcsServiceAttributeGenerator
    )
    registry.register_resource_attributes(
        "AWS::ECS::Cluster", EcsClusterAttributeGenerator
    )
