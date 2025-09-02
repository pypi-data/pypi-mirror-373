import json
import os
from typing import List, Any, Callable, Dict, Optional, Type, Union
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain.chains import SimpleSequentialChain
import logging

from pydantic import BaseModel

import mlflow

from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec
from fairo.core.client.client import BaseClient
from fairo.core.execution.agent_serializer import AgentChainWrapper
from fairo.core.execution.env_finder import read_variables
from fairo.core.execution.model_log_helper import ModelLogHelper
from fairo.core.runnable.runnable import Runnable
from fairo.core.workflow.utils import output_langchain_process_graph
from fairo.settings import get_fairo_api_key, get_fairo_api_secret, get_mlflow_experiment_name, get_mlflow_server, get_fairo_base_url


logger = logging.getLogger(__name__)

class FairoExecutor:
    def __init__(
        self,
        agent_type: str = "Langchain",
        agents: List[Any] = [],
        verbose: bool = False,
        patch_run_output_json: Callable[[Any], None] = None,
        workflow_run_id: str = "",
        runnable: Runnable = None,
        experiment_name: str = None,
        chain_class = SimpleSequentialChain,
        input_fields: List[str] = [],
        input_schema: Optional[Type[BaseModel]] = None,
    ):
        if agents and runnable:
            raise ValueError("FairoExecutor cannot be initialized with both 'agents' and 'runnable'. Please provide only one.")
        if not input_fields and not input_schema:
            raise ValueError("Missing required parameters: please provide at least one of 'input_fields' or 'input_schema'")
        self.input_schema = input_schema
        self.agents = agents
        self.agent_type = agent_type
        self.verbose = verbose
        self.patch_run_output_json = patch_run_output_json
        self.workflow_run_id = workflow_run_id
        self.runnable = runnable
        self.experiment_name = experiment_name if experiment_name else get_mlflow_experiment_name()
        self.setup_mlflow()
        self.chain_class = chain_class
        self.client = BaseClient(
            base_url=get_fairo_base_url(),
            password=get_fairo_api_secret(),
            username=get_fairo_api_key()
        )
        self.input_fields = input_fields
        # Inject shared attributes into agents
        for agent in self.agents:
            if hasattr(agent, 'set_client'):
                agent.set_client(self.client)
            if hasattr(agent, 'verbose'):
                agent.verbose = self.verbose

    def _build_pipeline(self) -> RunnableSequence:
        if not self.agents and not self.runnable:
            raise ValueError("At least one agent or runnable must be provided.")
        
        if self.runnable:
            pipeline = mlflow.pyfunc.load_model(self.runnable.artifact_path)
        else:
            pipeline = AgentChainWrapper(chain_class=self.chain_class, agent_functions_list=self.agents)
            # Convert Pydantic schema to MLflow Schema
            if hasattr(self.input_schema, 'model_json_schema'):
                # Extract field names from Pydantic schema
                pydantic_schema = self.input_schema.model_json_schema()
                properties = pydantic_schema.get('properties', {})
                cols = []
                for field_name, field_info in properties.items():
                    field_type = field_info.get('type', 'string')
                    # Map Pydantic types to MLflow types
                    mlflow_type = 'string'  # Default to string
                    if field_type in ['integer', 'number']:
                        mlflow_type = 'double'
                    elif field_type == 'boolean':
                        mlflow_type = 'boolean'
                    cols.append(ColSpec(type=mlflow_type, name=field_name))
                input_schema = Schema(cols)
            else:
                # Fallback to input_fields if schema is not Pydantic
                cols = [ColSpec(type="string", name=field) for field in self.input_fields]
                input_schema = Schema(cols)

            output_schema = Schema([
                ColSpec(type="string", name="output"),
            ])
            current_run = mlflow.active_run()
            # Log Model
            ModelLogHelper(
                agent_type=self.agent_type,
                signature=ModelSignature(inputs=input_schema, outputs=output_schema),
                agents=self.agents,
            ).log_model()
            
        def save_process_graph():
            if len(self.agents) > 0:
                process_graph = output_langchain_process_graph([ag() for ag in self.agents])
                if len(self.agents) > 1:
                    type = "Workflow"
                else:
                    type = "Agent"
            elif self.runnable:
                process_graph = self.runnable.process_graph
                type = self.runnable.type
            else:
                process_graph = None
                type = None
            fairo_settings = {
                "type": type,
                "process_graph": process_graph,
                "schema": self.input_schema.model_json_schema() if self.input_schema else None,
                "input_fields": list(self.input_schema.model_fields.keys()) if self.input_schema else self.input_fields,
            }
            if process_graph:
                mlflow.log_text(json.dumps(fairo_settings, ensure_ascii=False, indent=2), artifact_file="fairo_settings.txt")
        
        if self.agents:
            try:
                save_process_graph()
            except Exception as e:
                logger.warning("It wasn't possible to generate and save process graph")
        try:
            # Find environment variables used in the project
            all_env_vars = read_variables()
            # Log the file as an artifact
            mlflow.log_text(all_env_vars, artifact_file="environment/variables.txt")
            if self.verbose:
                logger.info(f"Logged {len(all_env_vars)} environment variables as artifact")
        except Exception as e:
            logger.warning(f"Failed to log environment variables: {str(e)}")

        # If runnable object was added, set runnable_id tag for the trace
        if self.runnable:
            mlflow.set_tags({
                "runnable_id": self.runnable.id,
                "environment": "development",
            })
        else:
            mlflow.set_tags({
                "environment": "development",
            })   
        return pipeline

    def run(self, input_data: Union[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Execute the pipeline using the provided input.
        Properly handles and propagates errors from agents.
        """
        if self.verbose:
            logger.info("Running agent pipeline...")
            logger.info(f"Initial input: {input_data}")

        try:
            # Run the pipeline but don't catch exceptions
            with mlflow.start_run() as run:
                mlflow.autolog(
                    log_traces=True,
                    log_input_examples=True,
                )
                self.pipeline = self._build_pipeline()
                if self.runnable:
                    result = self.pipeline.predict(input_data)
                else:
                    result = self.pipeline.predict(model_input=input_data)
                
                if self.verbose:
                    logger.info("Pipeline execution completed")
                    logger.info(f"Final output: {result}")
                    
                return result
            
        except Exception as e:
            # Log the error
            if self.verbose:
                logger.error(f"Pipeline execution failed: {str(e)}")
            
            # Propagate the exception so calling code can handle it
            raise e
    
    def setup_mlflow(self):
        def _clean_mlflow_env_vars():
            for env_var in ["MLFLOW_TRACKING_USERNAME", "MLFLOW_TRACKING_PASSWORD", "MLFLOW_TRACKING_TOKEN"]:
                if env_var in os.environ:
                    del os.environ[env_var]
        def setup_mlflow_tracking_server():
            os.environ["MLFLOW_TRACKING_USERNAME"] = get_fairo_api_key()
            os.environ["MLFLOW_TRACKING_PASSWORD"] = get_fairo_api_secret()
            mlflow.set_tracking_uri(get_mlflow_server())
            mlflow.set_experiment(experiment_name=self.experiment_name)
        _clean_mlflow_env_vars()
        setup_mlflow_tracking_server()