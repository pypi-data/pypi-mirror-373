from typing import Any, List, Literal, Optional

from fairo.core.agent.base_agent import SimpleAgent
from fairo.core.client.client import BaseClient
from fairo.core.workflow.utils import output_workflow_process_graph
from fairo.settings import get_fairo_base_url, get_fairo_api_key, get_fairo_api_secret

class Runnable:
    def __init__(self,
                 id: Optional[str] = None,
                 name: Optional[str] = None,
                 version: Optional[int] = None,
                 type: Optional[Literal["Agent", "Workflow", "Default"]] = None,
                 chain: Optional[List[Any]] = [],
                 agent: Optional[SimpleAgent] = None,
                 artifact_path: Optional[str] = None,
                 description: Optional[str] = ""):
        self.id = id
        self.process_graph = None
        self.name = name
        self.version = version
        self.type = type
        self.chain = chain
        self.agent = agent
        self.artifact_path = artifact_path
        self.description = description
        self.client = BaseClient(
            base_url=get_fairo_base_url(), 
            username=get_fairo_api_key(), 
            password=get_fairo_api_secret()
        )
        
        self.load_version()
        
    
    def load_version(self):
        try:
            if self.id:
                runnable_obj = self.client.get(f"/runnables/{self.id}")
                if runnable_obj:
                    self.artifact_path = runnable_obj.get('artifact_path')
                    self.type = runnable_obj.get('type')
                    self.description = runnable_obj.get('description')
                    self.id = runnable_obj.get('id')
                    self.process_graph = runnable_obj.get('process_graph')
            elif self.name and self.version: 
                response = self.client.get(f"/runnables?version={self.version}&name={self.name}&page_size=1")
                if len(response.get('results')) > 0:
                    runnable_obj = response.get('results')[0]
                    self.artifact_path = runnable_obj.get('artifact_path')
                    self.type = runnable_obj.get('type')
                    self.description = runnable_obj.get('description')
                    self.id = runnable_obj.get('id')
                    self.process_graph = runnable_obj.get('process_graph')
            else:
                response = None
        except Exception as e:
            print("Failed to check existing runnable version")
            raise e
    
    def create_version(self, artifact_path, registered_model_id):
        try:
            process_graph = output_workflow_process_graph(self.chain) if all(isinstance(agent, SimpleAgent) for agent in self.chain) else None
            payload = {
                "name": self.name,
                "version": self.version,
                "artifact_path": artifact_path,
                "description": self.description,
                "type": self.type,
                "registered_model_id": registered_model_id,
                "process_graph": process_graph
            }
            response = self.client.post(f"/runnables", json=payload)
            self.id = response.get('id')
            self.process_graph = response.get('process_graph')
        except Exception as e:
            print("Failed to create runnable version")
            raise e
        
    def patch_process_graph(self):
        try:
            process_graph = output_workflow_process_graph(self.chain)
            response = self.client.patch(f"/runnables/{self.id}", json={
                "process_graph": process_graph
            }, auth=(self.api_key, self.api_secret))
            return response.json()
        except Exception as e:
            print(e)
            