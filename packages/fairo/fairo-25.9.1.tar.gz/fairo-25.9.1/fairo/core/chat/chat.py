
from langchain_community.chat_models.mlflow import ChatMlflow
from mlflow.deployments import get_deploy_client
from mlflow.deployments.base import BaseDeploymentClient
from fairo.settings import get_mlflow_gateway_chat_route, get_mlflow_gateway_uri, get_mlflow_user, get_mlflow_password
import requests
from requests.auth import HTTPBasicAuth
import json
import os

class FairoDeploymentClient(BaseDeploymentClient):
    """Custom deployment client that implements predict_stream for Fairo endpoints."""
    
    def __init__(self, target_uri: str, endpoint: str):
        self.target_uri = target_uri
        self.endpoint = endpoint
        
    def predict_stream(self, deployment_name=None, inputs=None, endpoint=None):
        """
        Implement streaming predictions by making HTTP requests to the Fairo gateway.
        """
        endpoint = endpoint or self.endpoint
        
        # Use the gateway URL to make streaming requests
        gateway_url = f"{self.target_uri.rstrip('/')}/gateway/{endpoint}/invocations"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
        
        # Add authentication if needed
        auth = None
        if os.environ.get('FAIRO_API_ACCESS_KEY_ID') and os.environ.get('FAIRO_API_SECRET'):
            auth = HTTPBasicAuth(
                os.environ.get('FAIRO_API_ACCESS_KEY_ID'),
                os.environ.get('FAIRO_API_SECRET')
            )
        
        # Make streaming request
        try:
            response = requests.post(
                gateway_url,
                json={**inputs, "stream": True},
                headers=headers,
                auth=auth,
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"HTTP {response.status_code}: {error_text}")
                
            # Check if response is actually streaming
            content_type = response.headers.get('content-type', '')
            
            chunk_count = 0
            
            # Parse streaming response
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    # Handle different streaming formats
                    if line.startswith('data: '):
                        try:
                            data_str = line[6:]  # Remove 'data: ' prefix
                            if data_str.strip() == '[DONE]':
                                break
                            data = json.loads(data_str)
                            chunk_count += 1
                            yield data
                        except json.JSONDecodeError as e:
                            continue
                    else:
                        # Try parsing as direct JSON
                        try:
                            data = json.loads(line)
                            chunk_count += 1
                            yield data
                        except json.JSONDecodeError:
                            continue
                            
            
            # If no chunks were yielded, fall back to non-streaming
            if chunk_count == 0:
                # Try to get the full response as JSON
                try:
                    if hasattr(response, 'json'):
                        result = response.json()
                        yield result
                except:
                    # Create a minimal response to avoid the error
                    yield {
                        "choices": [{
                            "delta": {"content": "", "role": "assistant"},
                            "finish_reason": "stop"
                        }]
                    }
                    
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def predict(self, deployment_name=None, inputs=None, endpoint=None):
        """
        Implement synchronous predictions by making HTTP requests to the Fairo gateway.
        """
        endpoint = endpoint or self.endpoint
        
        # Use the gateway URL to make requests
        gateway_url = f"{self.target_uri.rstrip('/')}/gateway/{endpoint}/invocations"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add authentication if needed
        auth = None
        if os.environ.get('FAIRO_API_ACCESS_KEY_ID') and os.environ.get('FAIRO_API_SECRET'):
            auth = HTTPBasicAuth(
                os.environ.get('FAIRO_API_ACCESS_KEY_ID'),
                os.environ.get('FAIRO_API_SECRET')
            )
        
        if os.environ.get('MLFLOW_TRACKING_TOKEN'):
            headers['Authorization'] = f"Bearer {os.environ.get('MLFLOW_TRACKING_TOKEN')}"
        
        # Make request
        response = requests.post(
            gateway_url,
            json=inputs,
            headers=headers,
            auth=auth
        )
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
        return response.json()
    
    def get_deployment(self, name, endpoint=None):
        """Get deployment information."""
        raise NotImplementedError("get_deployment not implemented")
        
    def list_deployments(self, endpoint=None):
        """List available deployments."""
        raise NotImplementedError("list_deployments not implemented")
        
    def get_endpoint(self, endpoint):
        """Get endpoint information."""
        raise NotImplementedError("get_endpoint not implemented")
        
    def list_endpoints(self):
        """List available endpoints."""
        raise NotImplementedError("list_endpoints not implemented")
        
    def create_deployment(self, name, config, endpoint=None):
        """Create a new deployment."""
        raise NotImplementedError("create_deployment not implemented")
        
    def update_deployment(self, name, config, endpoint=None):
        """Update an existing deployment."""
        raise NotImplementedError("update_deployment not implemented")
        
    def delete_deployment(self, name, endpoint=None):
        """Delete a deployment."""
        raise NotImplementedError("delete_deployment not implemented")
        
    def create_endpoint(self, name, config):
        """Create a new endpoint."""
        raise NotImplementedError("create_endpoint not implemented")
        
    def update_endpoint(self, name, config):
        """Update an existing endpoint."""
        raise NotImplementedError("update_endpoint not implemented")
        
    def delete_endpoint(self, name):
        """Delete an endpoint."""
        raise NotImplementedError("delete_endpoint not implemented")


class ChatFairo(ChatMlflow):

    def __init__(self, **kwargs):

        super().__init__(
            target_uri=os.environ.get('MLFLOW_GATEWAY_URI', get_mlflow_gateway_uri()),
            endpoint=os.environ.get('MLFLOW_GATEWAY_ROUTE', get_mlflow_gateway_chat_route()),
            **kwargs
        )
        
        self._client = FairoDeploymentClient(self.target_uri, self.endpoint)

    @property
    def _target_uri(self):
        return os.environ.get("MLFLOW_GATEWAY_URI", None)

    @property
    def _endpoint(self):
        return os.environ.get("MLFLOW_GATEWAY_ROUTE", None)

    def invoke(self, *args, **kwargs):
        # Override invoke to use dynamic target_uri
        self.target_uri = self._target_uri
        self._client = FairoDeploymentClient(self.target_uri, self.endpoint)
        return super().invoke(*args, **kwargs)
    
    def stream(self, *args, **kwargs):
        # Override stream to use dynamic target_uri
        self.target_uri = self._target_uri
        self._client = FairoDeploymentClient(self.target_uri, self.endpoint)
        return super().stream(*args, **kwargs)
    
    def bind_tools(self, tools, **kwargs):
        result = super().bind_tools(tools, **kwargs)
        result._uses_tools = True
        return result
    
    def _stream(self, *args, **kwargs):
        response = self.invoke(*args, **kwargs)
        
        from langchain_core.messages import AIMessage, AIMessageChunk
        from langchain_core.outputs import ChatGenerationChunk
        
        if isinstance(response, AIMessage):
            initial_chunk = AIMessageChunk(content="", role="assistant")
            yield ChatGenerationChunk(message=initial_chunk)
            
            if response.content:
                content_chunk = AIMessageChunk(content=response.content, role="assistant")
                yield ChatGenerationChunk(message=content_chunk)
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_chunk = AIMessageChunk(
                    content="", 
                    role="assistant",
                    tool_calls=response.tool_calls
                )
                yield ChatGenerationChunk(message=tool_chunk)
            else:
                final_chunk = AIMessageChunk(content="", role="assistant")
                yield ChatGenerationChunk(message=final_chunk)
        else:
            chunk = AIMessageChunk(content=str(response), role="assistant")
            yield ChatGenerationChunk(message=chunk)


class FairoChat(ChatMlflow):
    def __init__(self, endpoint, **kwargs):
        super().__init__(
            target_uri=os.environ.get('MLFLOW_GATEWAY_URI', None),
            endpoint=endpoint,
            # extra_params={"workflow_run_id": workflow_run_id},
            **kwargs
        )

    @property
    def _target_uri(self):
        return os.environ.get("MLFLOW_GATEWAY_URI", None)
    
    def invoke(self, *args, **kwargs):
        # Override invoke to use dynamic target_uri
        self.target_uri = self._target_uri
        self._client = get_deploy_client(self.target_uri)
        return super().invoke(*args, **kwargs)