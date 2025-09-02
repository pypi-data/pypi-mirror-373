from pydantic import BaseModel
from typing import Type, Any


class StructIngest:
    def _resolve_refs(self, schema_part: Any, full_schema: dict):
        """
        Recursively traverses the schema, replaces '$ref' pointers,
        and removes all 'title' keys.
        """
        if isinstance(schema_part, dict):
            if "$ref" in schema_part:
                ref_path = schema_part["$ref"].split("/")
                def_name = ref_path[-1]
                definition = full_schema.get("$defs", {}).get(def_name, {})
                return self._resolve_refs(definition, full_schema)
            else:
                # Traverse the dictionary, but exclude any key that is 'title'
                return {
                    k: self._resolve_refs(v, full_schema)
                    for k, v in schema_part.items()
                    if k != "title"
                }
        elif isinstance(schema_part, list):
            return [self._resolve_refs(item, full_schema) for item in schema_part]
        else:
            return schema_part

    def format(self, pydanticObject: Type[BaseModel]):
        """
        Dynamically generates a JSON Schema properties dictionary and a list of
        required fields from a Pydantic model, with all nested references resolved
        and title keys removed.
        """
        schema = pydanticObject.model_json_schema()

        derivedProperties = schema.get("properties", {})

        requiredProperties = schema.get("required", [])

        resolved_properties = self._resolve_refs(derivedProperties, schema)

        return resolved_properties, requiredProperties


class StructFormatter:

    @staticmethod
    def ingest(schemaName: str, schemaDescription: str, schemaObject: Type[BaseModel]):
        # ensure that the objects are not none
        assert isinstance(schemaName, str), f"The `SchemaName` has to be a string"
        assert isinstance(
            schemaDescription, str
        ), f"The `schemaDescription` has to be a string"
        assert (
            not schemaObject is None
        ), f"The `schemaObject` should be a valid pydantic model and not None"
        assert issubclass(
            schemaObject, BaseModel
        ), f"The `schemaObject` should be a valid pydantic model"

        # format
        derived, required = StructIngest().format(pydanticObject=schemaObject)

        # This is the full, valid structure you would pass to the LLM
        response_format_for_llm = {
            "type": "json_schema",
            "json_schema": {
                # Give your schema a descriptive name
                "name": schemaName,
                # Describe its purpose
                "description": schemaDescription,
                "schema": {
                    "type": "object",
                    "properties": derived,
                    "required": required,
                },
            },
        }

        return response_format_for_llm
