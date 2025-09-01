import os
import json
from jsonschema import validate, RefResolver, ValidationError


class SchemaValidation:
    class Dummy(ValidationError):
        """Include so ruff doesnot complain about the ValidationError class not being used. Want it to be propagated."""

        pass

    def __init__(self, schema_file_path: str):
        self.schema_file_path = schema_file_path
        with open(schema_file_path, "r") as f:
            self.schema = json.load(f)

        # Create a resolver for handling $ref references in the schema
        schema_path = os.path.abspath(schema_file_path)
        schema_uri = f"file://{schema_path}"
        self.resolver = RefResolver(schema_uri, self.schema)

    def get_component_schema(self, component_name):
        if (
            "components" not in self.schema
            or "schemas" not in self.schema["components"]
        ):
            raise ValueError("Schema does not contain components/schemas section")

        if component_name not in self.schema["components"]["schemas"]:
            raise ValueError(f"Schema component '{component_name}' not found")

        return self.schema["components"]["schemas"][component_name]

    def validate_against_component(self, data, component_name):
        component_schema = self.get_component_schema(component_name)
        validate(instance=data, schema=component_schema, resolver=self.resolver)
        return True

    def validate_file(self, json_file_path, component_name):
        with open(json_file_path, "r") as f:
            data = json.load(f)
        return self.validate_against_component(data, component_name)
