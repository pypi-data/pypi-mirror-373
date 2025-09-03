class ResourceAttributeGenerator:

    def __init__(self):
        self._partition: str = "aws"
        self._account_id: str = None
        self._region: str = None
        self._resource: dict = {}
        self._resource_name: str = None
        self._resource_type: str = None
        self._stack_name: str = None

    @property
    def partition(self) -> str:
        return self._partition

    @partition.setter
    def partition(self, value: str):
        self._partition = value

    @property
    def region(self) -> str:
        return self._region

    @region.setter
    def region(self, value: str):
        self._region = value

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
    def resource_name(self) -> str:
        return self._resource_name

    @resource_name.setter
    def resource_name(self, value: str):
        self._resource_name = value

    @property
    def resource_type(self) -> str:
        return self._resource_type

    @resource_type.setter
    def resource_type(self, value: str):
        self._resource_type = value

    @property
    def resource(self) -> dict:
        return self._resource

    @resource.setter
    def resource(self, value: dict):
        self._resource = value

    def generate_random_resource_name(self):
        return f"{self._stack_name}-{self._resource_name}-ABCDEF"

    def get_attributes(self) -> dict:
        return None

    def get_ref(self) -> str:
        return self._resource_name
