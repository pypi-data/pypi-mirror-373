import base64
import os
from typing import Dict, Any

from pydantic import BaseModel

from fairo.core.agent.tools.base_tools import BaseTool
from fairo.core.models.custom_field_value import get_custom_field_value
from fairo.core.models.resources import get_resource_by_id

class CodeAnalysisToolSchema(BaseModel):
    resource_id: str

class CodeAnalysisTool(BaseTool):
    """
        Retrieve the code of a resource based on a UUID
    """
    name = "code_analysis_tool"
    returns = "A string containing the code from the related resource"

    def __init__(self):
        super().__init__(args_schema=CodeAnalysisToolSchema)
    
    def execute(self, resource_id: str) -> Dict[str, Any]:
        try:
            custom_field_value = get_custom_field_value(client=self.client, object_id=resource_id, field_key="code")
            return base64.b64decode(custom_field_value.get('value', "")).decode("utf-8")
        except Exception as e:
            return "Resource object not found"