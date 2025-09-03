from collections.abc import Callable
from typing import Type

from .resource_attribute_bundle import register_bundled_types
from .resource_attribute_generator import ResourceAttributeGenerator


class ResourceAttributeRegistry:

    def __init__(self):
        self.registry = {}
        register_bundled_types(self)

    def register_resource_attributes(
        self, resource_type: str, klass: type[ResourceAttributeGenerator]
    ) -> None:
        self.registry[resource_type] = klass

    def evaluate_attributes(
        self,
        *,
        stack_name: str,
        resource_name: str,
        resource: dict,
        account_id: str,
        region: str
    ) -> str:
        resource_type = resource["Type"]
        if resource_type in self.registry:
            obj = self.registry[resource_type]()
            obj.stack_name = stack_name
            obj.resource_name = resource_name
            obj.resource_type = resource_type
            obj.resource = resource
            obj.account_id = account_id
            obj.region = region
            return obj.get_attributes()
        return None

    def evaluate_ref(
        self,
        *,
        stack_name: str,
        resource_name: str,
        resource: dict,
        account_id: str,
        region: str
    ) -> str:
        resource_type = resource["Type"]
        if resource_type in self.registry:
            obj = self.registry[resource_type]()
            obj.stack_name = stack_name
            obj.resource_name = resource_name
            obj.resource_type = resource_type
            obj.resource = resource
            obj.account_id = account_id
            obj.region = region
            return obj.get_ref()
        return None
