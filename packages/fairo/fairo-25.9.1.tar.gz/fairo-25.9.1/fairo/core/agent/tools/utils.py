from typing import Dict, List, Literal, Optional, Any
from pydantic import BaseModel, Field
import json
class ToolResultOutput:
    thought: str
    action: str
    response: str
    action_input: str

class ToolResult:
    tool_name: str
    thought: str
    response: str
    action_input: str
    
    def __init__(self, tool_name, thought, response, action_input):
        self.tool_name = tool_name
        self.thought = thought
        self.response = response
        self.action_input = action_input
        
    def to_dict(self):
        return {
            "tool_name": self.tool_name,
            "thought": self.thought,
            "response": self.response,
            "action_input": self.action_input,
        }


class Iteration:
    duration: str
    prompt: str
    response: str
    tool_results: Optional[List[ToolResult]]
    
    def __init__(self, prompt, response, tool_results = None, duration = "0s"):
        self.prompt = prompt
        self.response = response
        self.tool_results = tool_results if tool_results is not None else []
        self.duration = duration

    def add_tool_result(self, tool_result: ToolResult):
        self.tool_results.append(tool_result)
    
    def add_duration(self, duration: str):
        self.duration = duration
    
    def to_dict(self):
        return {
            "duration": self.duration,
            "prompt": self.prompt,
            "response": self.response,
            "tool_results": [tool.to_dict() for tool in self.tool_results]
        }
class LLMAgentOutput:
    node_name: str
    status: Literal["success", "failed"]
    task: str
    duration: str
    context: str
    query_result: List[str]
    memory: Optional[List[str]]
    iterations: List[Iteration]
    error_message: Optional[str]
    
    def __init__(self, node_name, task, context, query_result, memory):
        self.task = task
        self.context = context
        self.query_result = query_result
        self.memory = memory
        self.node_name = node_name
        self.iterations = []
        self.status = "success"
        self.duration = "0s"
        self.error_message = None
    
    def add_duration(self, duration):
        self.duration = duration
    
    def add_iteration(self, iteration: Iteration = None):
        self.iterations.append(iteration)
        
    def add_error(self, error_message: str, traceback_details: str = None):
        """
        Record an error message and set status to failed
        
        Args:
            error_message: The main error message
            traceback_details: Optional detailed traceback information
        """
        self.status = "failed"
        
        if not self.error_message:
            self.error_message = error_message
            
            if traceback_details:
                self.traceback_details = traceback_details
        
    
    def to_dict(self):
        result = {
            "node_name": self.node_name,
            "status": self.status,
            "task": self.task,
            "duration": self.duration,
            "context": self.context,
            "query_result": self.query_result,
            "memory": self.memory,
            "iterations": [i.to_dict() for i in self.iterations]
        }
        
        # Add optional fields only if they have values
        if self.error_message:
            # Include traceback in error message if it exists
            if hasattr(self, 'traceback_details') and self.traceback_details:
                result["error_message"] = f"{self.error_message}\n\n{self.traceback_details}"
                result["traceback_details"] = self.traceback_details
            else:
                result["error_message"] = self.error_message
            
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

class FlowOutput:
    node_name: str
    source: str
    destination: str
    
    def __init__(self, node_name, source, destination):
        self.node_name = node_name
        self.source = source
        self.destination = destination
    
    def to_dict(self):
        return {
            "node_name": self.node_name,
            "destination": self.destination,
            "source": self.source
        }