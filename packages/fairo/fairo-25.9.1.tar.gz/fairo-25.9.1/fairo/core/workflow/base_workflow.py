import mlflow
import requests
import os

from enum import Enum
from typing import List, Union
from fairo.core.agent.base_agent import SimpleAgent
from fairo.core.agent.tools.utils import FlowOutput, LLMAgentOutput
from fairo.core.client.client import BaseClient

from fairo.core.execution.executor import FairoExecutor
from fairo.core.runnable.runnable import Runnable
from fairo.core.workflow.utils import output_workflow_process_graph
from fairo.settings import (
    get_fairo_api_key, 
    get_fairo_api_secret,
    get_fairo_base_url,
    get_mlflow_experiment_path,
    get_mlflow_password, 
    get_mlflow_token, 
    get_mlflow_user, 
    get_use_databricks_tracking_server, 
    get_mlflow_server
)


class WorkflowRunStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"
class BaseWorkflow:
    api_key: str = ""
    api_secret: str = ""
    mlflow_server: str = ""
    mlflow_user: str = ""
    mlflow_password: str = ""
    mlflow_token: str = ""
    agents: List[SimpleAgent] = []
    autolog = True
    workflow_summary = ""
    description: str = ""
    workflow_run_id = None
    use_databricks_tracking_server = False
    
    def __init__(self, 
                 agents,
                 workflow_summary: str,
                 autolog: bool = True,
                 description: str = "",
                 api_key: str = None,
                 api_secret: str = None,
                 mlflow_server: str = None,
                 mlflow_user: str = None,
                 mlflow_password: str = None,
                 mlflow_token: str = None,
                 fairo_base_url: str = None,
                 mlflow_base_url: str = None,
                 use_databricks_tracking_server: bool = False,
                 ):
        assert agents and isinstance(agents, list), "agents must be a non-empty list"
        assert workflow_summary, "workflow_summary is required and cannot be empty"

        # Fairo API credentials
        self.api_key = api_key if api_key else get_fairo_api_key()
        self.api_secret = api_secret if api_secret else get_fairo_api_secret()
        self.fairo_base_url = fairo_base_url if fairo_base_url else get_fairo_base_url()
        self.mlflow_base_url = mlflow_base_url if mlflow_base_url else get_mlflow_server()

        # MLFlow configuration
        self.mlflow_server = mlflow_server if mlflow_server else get_mlflow_server()
        self.mlflow_user = mlflow_user if mlflow_user else get_mlflow_user()
        self.mlflow_password = mlflow_password if mlflow_password else get_mlflow_password()
        self.mlflow_token = mlflow_token if mlflow_token else get_mlflow_token()
        
        self.agents = agents
        self.workflow_summary = workflow_summary
        self.autolog = autolog
        self.description = description
        self.use_databricks_tracking_server = use_databricks_tracking_server if use_databricks_tracking_server else get_use_databricks_tracking_server()
    
    @property
    def base_url(self):
        return self.fairo_base_url

    @classmethod
    def get_session(cls):
        sess = requests.Session()
        sess.auth = (cls.api_key, cls.api_secret)
        return sess
    
    def setup_mlflow(self):
        
        def _clean_mlflow_env_vars():
            for env_var in ["MLFLOW_TRACKING_USERNAME", "MLFLOW_TRACKING_PASSWORD", "MLFLOW_TRACKING_TOKEN"]:
                if env_var in os.environ:
                    del os.environ[env_var]

        def setup_mlflow_tracking_server():
            if self.mlflow_user and self.mlflow_password:
                os.environ["MLFLOW_TRACKING_USERNAME"] = self.mlflow_user
                os.environ["MLFLOW_TRACKING_PASSWORD"] = self.mlflow_password
            elif self.mlflow_token:
                os.environ["MLFLOW_TRACKING_TOKEN"] = self.mlflow_token
            
            mlflow.set_tracking_uri(self.mlflow_base_url)
            mlflow.set_experiment(self.workflow_summary)
        
        def setup_databricks_tracking_server():
            os.environ["DATABRICKS_HOST"] = self.mlflow_server
            os.environ["DATABRICKS_TOKEN"] = self.mlflow_token
            mlflow.set_tracking_uri("databricks")
            experiment_path = get_mlflow_experiment_path()
            path = f"{experiment_path}/{self.workflow_summary}" if experiment_path else self.workflow_summary
            mlflow.set_experiment(experiment_name=path)
        # Databricks settings
        _clean_mlflow_env_vars()
        if self.use_databricks_tracking_server:
            setup_databricks_tracking_server()
        else:
            setup_mlflow_tracking_server()

    def run_autolog(self, run_num, prompt):
        """
        Run with MLflow autologging turned on.
        Propagates any exceptions from agents.
        """
        self.setup_mlflow()
        run_name = f"{self.workflow_summary} run {run_num}"
        with mlflow.start_run(run_name=run_name):
            mlflow.langchain.autolog(
                log_traces=True,
                log_input_examples=True,
                # log_models=True,
                # log_model_signatures=True
            )
            # No try/except here - let exceptions propagate up
            return self.execute(prompt)

    def create_workflow(self, workflow_type_id: str):
        try:
            response = requests.post(f"{self.base_url}/workflows", json=True, data={
                'summary': self.workflow_summary,
                'type': workflow_type_id,
                'description': self.description
            }, auth=(self.api_key, self.api_secret))
            return response.json()
        except Exception as e:
            print(e)
    
    def patch_workflow_process_graph(self, workflow_id, process_graph):
        try:
            response = requests.patch(f"{self.base_url}/workflows/{workflow_id}", json={
                "process_graph": process_graph
            }, auth=(self.api_key, self.api_secret))
            return response.json()
        except Exception as e:
            print(e)
            
    def get_workflow_type(self, name = "AI Agent"):
        try:
            response = requests.get(f"{self.base_url}/workflow_types?fairo_data=true&name[]={name}", auth=(self.api_key, self.api_secret)).json()
            results = response.get('results')
            if len(results) > 0:
                return results[0]
            return None
        except Exception as e:
            print(e)

    def get_or_create_workflow(self):
        try:
            response = requests.get(f"{self.base_url}/workflows?summary[]={self.workflow_summary}", auth=(self.api_key, self.api_secret)).json()
            results = response.get('results')
            if len(results) > 0:
                return results[0]
            else:
                workflow_type = self.get_workflow_type()
                if workflow_type:
                    return self.create_workflow(workflow_type.get('id'))
                raise Exception("Workflow type agent not found on server")
        except Exception as e:
            print(e)
            raise e
            
    def create_workflow_run(self, workflow_id):
        try:
            response = requests.post(f"{self.base_url}/workflow_runs", json=True, data={
                'workflow': workflow_id,
                'status': 'RUNNING'
            }, auth=(self.api_key, self.api_secret))
            return response.json()
        except Exception as e:
            print(e)
            
    def patch_workflow_run(self, workflow_run_id, payload):
        try:
            response = requests.patch(f"{self.base_url}/workflow_runs/{workflow_run_id}", json=payload, auth=(self.api_key, self.api_secret))
            return response.json()
        except Exception as e:
            print(e)
            
    def add_workflow_run_node_output(self, output: Union[LLMAgentOutput, FlowOutput]):
        try:
            response = requests.post(f"{self.base_url}/workflow_runs/{self.workflow_run_id}/add_node_output", json=output, auth=(self.api_key, self.api_secret))
            return response.json()
        except Exception as e:
            print(e)
    
    def patch_workflow_run_status(self, workflow_run_id, status: WorkflowRunStatus):
        try:
            return self.patch_workflow_run(workflow_run_id, {
                'status': status.value
            })
        except Exception as e:
            print(e)
            
    def execute(self, initial_prompt):
        """
        Execute the workflow with the given initial prompt.
        Propagates any exceptions from agents.
        """
        client = BaseClient(base_url=self.base_url, username=self.api_key, password=self.api_secret)
        executor = FairoExecutor(
            agents=self.agents,
            verbose=False,
            patch_run_output_json=self.add_workflow_run_node_output,
            client=client,
            workflow_run_id=self.workflow_run_id
        )

        # Don't catch exceptions here - let them propagate up to be handled in the run method
        return executor.run(initial_prompt)

    def run(self, prompt):
        workflow_id = self.get_or_create_workflow().get('id')
        self.patch_workflow_process_graph(workflow_id, output_workflow_process_graph(self.agents))
        run = self.create_workflow_run(workflow_id)
        self.workflow_run_id = run.get('id')
        try:
            if self.autolog:
                self.run_autolog(run_num=run.get('workflow_run_num'), prompt=prompt)
            else: 
                self.execute(initial_prompt=prompt)
            self.patch_workflow_run_status(workflow_run_id=run.get('id'), status=WorkflowRunStatus.COMPLETED)
        except Exception as e:
            # Mark the workflow run as failed
            self.patch_workflow_run_status(workflow_run_id=run.get('id'), status=WorkflowRunStatus.FAILED)

            # Properly format and re-raise the exception
            error_message = f"Run failed with exception: {str(e)}"
            raise RuntimeError(error_message) from e
            
    