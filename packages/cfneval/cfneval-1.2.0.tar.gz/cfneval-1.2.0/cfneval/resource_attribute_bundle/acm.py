from cfneval.resource_attribute_generator import ResourceAttributeGenerator


class CertAttributeGenerator(ResourceAttributeGenerator):

    def get_ref(self) -> str:
        return f"arn:{self._partition}:acm:{self._region}:{self._account_id}:certificate/1234"


def register_bundled_types(registry):
    registry.register_resource_attributes(
        "AWS::CertificateManager::Certificate", CertAttributeGenerator
    )
