from cfneval.resource_attribute_generator import ResourceAttributeGenerator


class ElbTargetGroupAttributeGenerator(ResourceAttributeGenerator):

    def get_attributes(self) -> dict:
        name = service_name = self._resource["Properties"].get(
            "Name", self.generate_random_resource_name()
        )
        uid = "1234"
        arn = f"arn:{self._partition}:elasticloadbalancing:{self._region}:{self._account_id}:targetgroup/{name}/{uid}"
        return {
            "LoadBalancerArns": None,
            "TargetGroupArn": arn,
            "TargetGroupFullName": f"targetgroup/{name}/{uid}",
            "TargetGroupName": service_name,
        }

    def get_ref(self) -> str:
        return self.get_attributes()["TargetGroupArn"]


def register_bundled_types(registry):
    registry.register_resource_attributes(
        "AWS::ElasticLoadBalancingV2::TargetGroup", ElbTargetGroupAttributeGenerator
    )
