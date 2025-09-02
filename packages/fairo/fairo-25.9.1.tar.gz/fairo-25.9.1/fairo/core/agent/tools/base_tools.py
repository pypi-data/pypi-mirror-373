from pydantic import BaseModel, ValidationError
import json
from langchain_community.tools import Tool

from fairo.core.client.client import BaseClient



class APISchema:
    def __init__(self, schema):
        if isinstance(schema, BaseModel):
            self.args_schema = schema
        elif isinstance(schema, type) and issubclass(schema, BaseModel):
            self.args_schema = schema
        elif isinstance(schema, (dict, str)):
            self.args_schema = self._validate_json_schema(schema)
        else:
            raise Exception("Invalid schema type")

    @property
    def schema(self):
        return self.args_schema

    @staticmethod
    def _validate_json_schema(schema):
        schema_obj = json.loads(schema) if isinstance(schema, str) else schema
        if "requestBody" in schema_obj and "content" in schema_obj["requestBody"]:
            if "application/json" in schema_obj["requestBody"]["content"]:
                schema_obj = schema_obj["requestBody"]["content"]["application/json"]["schema"]
            else:
                raise Exception("Sorry, Fairo only accepts JSON Schema") # TODO <-- Django Exception

        def validate_schema_object(obj, path=""):
            if not isinstance(obj, dict):
                raise Exception(f"Schema at {path} must be a JSON object")

            # Disallow $ref as
            if "$ref" in obj:
                raise Exception(f"$ref is not supported at {path}. Please specify the schema explicitly.") # TODO <- django exception

            # Basic type validation
            if "type" not in obj:
                raise Exception(f"Schema at {path} must have a 'type' field")
            
            # Validate type is one of the allowed OpenAPI types
            valid_types = ["object", "array", "string", "number", "integer", "boolean", "null"]
            schema_type = obj.get("type")
            if schema_type not in valid_types:
                raise Exception(f"Invalid type '{schema_type}' at {path}. Must be one of: {', '.join(valid_types)}")
            
            # validate types
            if schema_type == "object":
                # Properties are required for object type in OpenAPI 3.0
                if "properties" not in obj:
                    raise Exception(f"Object schema at {path} must have 'properties' field")
                
                if not isinstance(obj["properties"], dict):
                    raise Exception(f"Properties at {path} must be a JSON object")
                
                for prop_name, prop_schema in obj["properties"].items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    validate_schema_object(prop_schema, prop_path)
                
                # Check that required properties are listed in properties
                if "required" in obj:
                    if not isinstance(obj["required"], list):
                        raise Exception(f"Required field at {path} must be an array")
                    
                    for req_prop in obj["required"]:
                        if req_prop not in obj["properties"]:
                            raise Exception(f"Required property '{req_prop}' at {path} not found in properties")
            
            elif schema_type == "array":
                if "items" not in obj:
                    raise Exception(f"Array schema at {path} must have 'items' field")
                
                # Validate items schema recursively
                items_path = f"{path}.items" if path else "items"
                validate_schema_object(obj["items"], items_path)
            
            # Validate formats for primitive types
            if "format" in obj:
                valid_formats = {
                    "string": ["date", "date-time", "password", "byte", "binary", "email", "uuid", "uri", "hostname", "ipv4", "ipv6"],
                    "integer": ["int32", "int64"],
                    "number": ["float", "double"]
                }
                
                schema_format = obj.get("format")
                if schema_type in valid_formats:
                    if schema_format not in valid_formats[schema_type]:
                        raise Exception(f"Invalid format '{schema_format}' for type '{schema_type}' at {path}. Valid formats are: {', '.join(valid_formats[schema_type])}")
                else:
                    raise Exception(f"Format is not allowed for type '{schema_type}' at {path}")
            
            # Validate minimum/maximum constraints for numeric types
            if schema_type in ["number", "integer"]:
                if "minimum" in obj and not isinstance(obj["minimum"], (int, float)):
                    raise Exception(f"'minimum' must be a number at {path}")
                if "maximum" in obj and not isinstance(obj["maximum"], (int, float)):
                    raise Exception(f"'maximum' must be a number at {path}")
                if "multipleOf" in obj and not isinstance(obj["multipleOf"], (int, float)):
                    raise Exception(f"'multipleOf' must be a number at {path}")
            
            # Validate string constraints
            if schema_type == "string":
                if "minLength" in obj and not isinstance(obj["minLength"], int):
                    raise Exception(f"'minLength' must be an integer at {path}")
                if "maxLength" in obj and not isinstance(obj["maxLength"], int):
                    raise Exception(f"'maxLength' must be an integer at {path}")
                if "pattern" in obj and not isinstance(obj["pattern"], str):
                    raise Exception(f"'pattern' must be a string at {path}")
            
            # Validate array constraints
            if schema_type == "array":
                if "minItems" in obj and not isinstance(obj["minItems"], int):
                    raise Exception(f"'minItems' must be an integer at {path}")
                if "maxItems" in obj and not isinstance(obj["maxItems"], int):
                    raise Exception(f"'maxItems' must be an integer at {path}")
                if "uniqueItems" in obj and not isinstance(obj["uniqueItems"], bool):
                    raise Exception(f"'uniqueItems' must be a boolean at {path}")
            
            # Validate allOf, anyOf, oneOf if present (each item should be a valid schema)
            for combiner in ["allOf", "anyOf", "oneOf"]:
                if combiner in obj:
                    if not isinstance(obj[combiner], list):
                        raise Exception(f"{combiner} at {path} must be an array")
                    
                    for i, subschema in enumerate(obj[combiner]):
                        combiner_path = f"{path}.{combiner}[{i}]" if path else f"{combiner}[{i}]"
                        validate_schema_object(subschema, combiner_path)

        # Start recursive validation
        validate_schema_object(schema_obj)
        
        return schema_obj

    def _validate_args_json(self, payload):
        """
        Validates the provided payload against the JSON schema.
        
        Args:
            payload: A string (JSON) or dict containing the arguments to validate.
            
        Returns:
            dict: The validated arguments with any default values applied.
            
        Raises:
            Exception: If validation fails.
        """
        # Parse JSON if payload is a string
        payload_obj = json.loads(payload) if isinstance(payload, str) else payload
        
        if not isinstance(self.args_schema, dict):
            raise Exception("JSON schema is not properly initialized")
        
        # Define recursive validation function
        def validate_against_schema(data, schema, path=""):
            """
            Recursively validate data against a schema.
            
            Args:
                data: The data to validate
                schema: The schema to validate against
                path: The current path in the data for error reporting
                
            Returns:
                The validated data with any default values applied
                
            Raises:
                Exception: If validation fails
            """
            # Verify data type matches schema type
            schema_type = schema.get("type")
            
            # Handle object type
            if schema_type == "object":
                if not isinstance(data, dict):
                    raise Exception(f"Expected object at {path}, got {type(data).__name__}")
                
                result = {}
                properties = schema.get("properties", {})
                required_props = schema.get("required", [])
                
                # Check for required properties
                for prop in required_props:
                    if prop not in data:
                        raise Exception(f"Missing required property: {prop} at {path}")
                
                # Validate each provided property
                for prop_name, prop_value in data.items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    
                    if prop_name not in properties:
                        # Check if additionalProperties is allowed
                        if schema.get("additionalProperties") is False:
                            raise Exception(f"Unknown property: {prop_name} at {path}")
                        elif isinstance(schema.get("additionalProperties"), dict):
                            # Validate against additionalProperties schema
                            result[prop_name] = validate_against_schema(
                                prop_value, 
                                schema["additionalProperties"],
                                prop_path
                            )
                        else:
                            # Allow additional properties
                            result[prop_name] = prop_value
                    else:
                        # Validate against property schema
                        result[prop_name] = validate_against_schema(
                            prop_value,
                            properties[prop_name],
                            prop_path
                        )
                
                # Apply defaults for missing non-required properties
                for prop_name, prop_schema in properties.items():
                    if prop_name not in data and "default" in prop_schema:
                        result[prop_name] = prop_schema["default"]
                
                return result
            
            # Handle array type
            elif schema_type == "array":
                if not isinstance(data, list):
                    raise Exception(f"Expected array at {path}, got {type(data).__name__}")
                
                items_schema = schema.get("items", {})
                result = []
                
                # Validate each array item
                for i, item in enumerate(data):
                    item_path = f"{path}[{i}]"
                    validated_item = validate_against_schema(item, items_schema, item_path)
                    result.append(validated_item)
                
                # Validate array constraints
                if "minItems" in schema and len(result) < schema["minItems"]:
                    raise Exception(f"Array at {path} must have at least {schema['minItems']} items")
                
                if "maxItems" in schema and len(result) > schema["maxItems"]:
                    raise Exception(f"Array at {path} must have at most {schema['maxItems']} items")
                
                if schema.get("uniqueItems", False) and len(result) != len(set(map(str, result))):
                    raise Exception(f"Array at {path} must have unique items")
                
                return result
            
            # Handle string type
            elif schema_type == "string":
                if not isinstance(data, str):
                    raise Exception(f"Expected string at {path}, got {type(data).__name__}")
                
                # Validate string constraints
                if "minLength" in schema and len(data) < schema["minLength"]:
                    raise Exception(f"String at {path} must be at least {schema['minLength']} characters")
                
                if "maxLength" in schema and len(data) > schema["maxLength"]:
                    raise Exception(f"String at {path} must be at most {schema['maxLength']} characters")
                
                if "pattern" in schema:
                    import re
                    if not re.match(schema["pattern"], data):
                        raise Exception(f"String at {path} must match pattern: {schema['pattern']}")
                
                # Validate format if specified
                if "format" in schema:
                    # Simple format validation could be expanded
                    format_type = schema["format"]
                    if format_type == "date-time":
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(data.replace('Z', '+00:00'))
                        except ValueError:
                            raise Exception(f"String at {path} must be a valid ISO 8601 date-time")
                    # Add other format validations as needed
                
                return data
            
            # Handle number and integer types
            elif schema_type in ["number", "integer"]:
                if schema_type == "integer" and not isinstance(data, int):
                    raise Exception(f"Expected integer at {path}, got {type(data).__name__}")
                elif not isinstance(data, (int, float)):
                    raise Exception(f"Expected number at {path}, got {type(data).__name__}")
                
                # Validate numeric constraints
                if "minimum" in schema and data < schema["minimum"]:
                    raise Exception(f"Value at {path} must be >= {schema['minimum']}")
                
                if "maximum" in schema and data > schema["maximum"]:
                    raise Exception(f"Value at {path} must be <= {schema['maximum']}")
                
                if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
                    raise Exception(f"Value at {path} must be > {schema['exclusiveMinimum']}")
                
                if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
                    raise Exception(f"Value at {path} must be < {schema['exclusiveMaximum']}")
                
                if "multipleOf" in schema and data % schema["multipleOf"] != 0:
                    raise Exception(f"Value at {path} must be a multiple of {schema['multipleOf']}")
                
                return data
            
            # Handle boolean type
            elif schema_type == "boolean":
                if not isinstance(data, bool):
                    raise Exception(f"Expected boolean at {path}, got {type(data).__name__}")
                return data
            
            # Handle null type
            elif schema_type == "null":
                if data is not None:
                    raise Exception(f"Expected null at {path}, got {type(data).__name__}")
                return data
            
            # Handle enum validation
            if "enum" in schema and data not in schema["enum"]:
                raise Exception(f"Value at {path} must be one of: {', '.join(map(str, schema['enum']))}")
            
            return data
        
        # Start validation from the root
        return validate_against_schema(payload_obj, self.args_schema)

    def _validate_args_pydantic(self, payload):
        """
        Validates the provided payload against the Pydantic schema.
        
        Args:
            payload: A string (JSON) or dict containing the arguments to validate.
            
        Returns:
            dict: The validated arguments with any default values applied.
            
        Raises:
            ValidationError: If validation fails according to Pydantic rules.
        """
        payload_obj = json.loads(payload) if isinstance(payload, str) else payload
        try:
            # Use model_validate or parse_obj depending on pydantic version
            if hasattr(self.args_schema, 'model_validate'):
                # Pydantic v2
                validated_model = self.args_schema.model_validate(payload_obj)
            else:
                # Pydantic v1
                validated_model = self.args_schema.parse_obj(payload_obj)
                
            # Return validated data as a dict
            validated_args = validated_model.model_dump() if hasattr(validated_model, 'model_dump') else validated_model.dict()
        except ValidationError as e:
            # TODO <- Django exception that returns 404 w/clear error for LLM or User
            raise e
        return validated_args

    def validate_args(self, payload):
        """
        Validates arguments against the schema, whether it's a Pydantic model or JSON schema.
        
        This method serves as the main entry point for validating payloads against the schema.
        It delegates to the appropriate validation method based on the schema type.
        
        Args:
            payload: A string (JSON) or dict containing the arguments to validate.
            
        Returns:
            dict: The validated arguments with any default values applied.
            
        Raises:
            Exception: If validation fails or the schema is not properly initialized.
            ValidationError: If Pydantic validation fails.
        """
        if isinstance(self.args_schema, BaseModel) or (isinstance(self.args_schema, type) and issubclass(self.args_schema, BaseModel)):
            # Validate using Pydantic schema
            try:
                validated_args = self._validate_args_pydantic(payload)
            except ValidationError as e:
                # TODO <- Django exception that returns 404 w/clear error for LLM or User
                raise e
        elif isinstance(self.args_schema, dict):
            try:
                validated_args = self._validate_args_json(payload)
            except Exception as e:
                # Propagate JSON schema validation errors
                raise e
        else:
            raise Exception("Args schema is not properly initialized")
        
        return validated_args
        
    @property
    def prompt_schema(self):
        """
        Get the schema in a format suitable for LLM prompts.
        
        Returns:
            dict: The schema as a JSON-compatible dictionary.
        """
        # For Pydantic model classes, convert to JSON schema
        if isinstance(self.args_schema, type) and issubclass(self.args_schema, BaseModel):
            # Use model_json_schema() for Pydantic v2, or schema() for v1
            return (self.args_schema.model_json_schema() if hasattr(self.args_schema, 'model_json_schema') 
                    else self.args_schema.schema())
        # For JSON schema, return as is
        elif isinstance(self.args_schema, dict):
            return self.args_schema
        else:
            raise Exception("Schema is not properly initialized for prompt format")


class BaseTool:
    """
    A simple base class for tools that can be used by AI agents.
    Supports both Pydantic schemas and OpenAPI-style parameter dictionaries,
    wrapped in the APISchema class.
    """
    name = ""
    description = ""
    returns = ""
    args_schema = None  # This should be an APISchema instance
    authentication = None
    client = None

    def __init__(self, args_schema, name=None, description=None, returns=None, authentication=None, client=None):
        if name is not None:
            self.name = name
        elif not self.name:
            self.name = self.__class__.__name__
            
        # Set description from docstring if not provided
        if description is not None:
            self.description = description
        elif not self.description and self.__class__.__doc__:
            # Extract first paragraph from docstring
            docstring = self.__class__.__doc__.strip()
            # Use the first paragraph (up to first blank line) as the description
            self.description = docstring.split('\n\n')[0].replace('\n', ' ').strip()
            
        if returns is not None:
            self.returns = returns
            
        # Ensure args_schema is an APISchema instance
        if isinstance(args_schema, APISchema):
            self.args_schema = args_schema
        else:
            try:
                # Create an APISchema from a raw schema
                self.args_schema = APISchema(args_schema)
            except Exception as e:
                raise Exception(f"Must pass valid args schema, args schema failed with {e}")
                
        if authentication is not None:
            self.authentication = authentication
        self.client = client
            
    @classmethod
    def as_langchain_tool(cls, **init_params):
        @Tool(description=cls.description)
        def tool_func(**kwargs):
            return cls.validate_and_execute(**kwargs)

        return tool_func
    
    def set_client(self, client: BaseClient):
        self.client = client

    def execute(self, **kwargs):
        """
        Execute the tool with the args provided from the LLM.
        
        This is an abstract method that should be overridden by subclasses.
        It contains the core functionality of the tool.
        
        Args:
            **kwargs: Arguments passed to the tool from the LLM, which have been
                     validated against the tool's schema.
                     
        Returns:
            The result of executing the tool, which will be passed back to the LLM.
            The return type should match what's described in the `returns` attribute.
        """
        raise NotImplementedError("Subclasses must implement execute()")
        
    def validate_and_execute(self, **kwargs):
        try:
            validated_args = self.args_schema.validate_args(kwargs)
            result = self.execute(**validated_args)
            return result
        except Exception as e:
            # Provide clear error message for agent
            error_type = "validation" if "validate_args" in str(e) else "execution"
            error_msg = f"Error during {error_type} of tool '{self.name}': {str(e)}"
            raise Exception(error_msg)

    def get_prompt_format(self):
        """
        Get the tool description formatted for inclusion in an LLM prompt.
        
        This method generates a standardized string representation of the tool,
        including its name, description, parameters, and return value.
        
        Returns:
            str: A formatted string describing the tool for an LLM prompt
        """
        return (
            f"TOOL: {self.name}\n"
            f"DESCRIPTION: {self.description}\n"
            f"PARAMETER_SCHEMA: {self.args_schema.prompt_schema}\n"
            f"RETURNS: {self.returns}"
        )
        
    def to_dict(self, include_type: bool = False):
        docstring = self.__class__.__doc__.strip()
        description = docstring.split('\n\n')[0].replace('\n', ' ').strip()
        
        tool = {
            'name': self.name,
            'description': description,
            'input_schema': self.args_schema.args_schema.model_json_schema()
        }
        if include_type:
            tool['type'] = 'function'
        return tool