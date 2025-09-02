from typing import Any, Dict
import mlflow
import cloudpickle
import os
import sys
from pathlib import Path
from langchain_core.runnables import RunnableLambda, Runnable
from langchain.chains import SimpleSequentialChain
import logging
import types
import threading
import pandas as pd
logger = logging.getLogger(__name__)

class CustomPythonModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.agent = None
    
    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("lock", None)
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()
    
    def load_context(self, context):
        import sys
        import os
        import shutil
        
        agent_code_path = context.model_config["agent_code"]
        agent_code_dir = os.path.dirname(agent_code_path)
        
        if agent_code_dir not in sys.path:
            sys.path.insert(0, agent_code_dir)
        
        for artifact_name, artifact_path in context.model_config.items():
            if artifact_name.startswith("local_module_"):
                module_name = artifact_name.replace("local_module_", "")
                module_filename = f"{module_name}.py"
                dest_path = os.path.join(agent_code_dir, module_filename)
                
                if not os.path.exists(dest_path):
                    shutil.copy2(artifact_path, dest_path)
                    print(f"Restored local module: {module_name}")
        
        try:
            import agent_code
            from agent_code import create_simple_agent
            self.agent_func = create_simple_agent
            self.agent = self.agent_func()
        except ImportError as e:
            raise ImportError(f"Failed to import agent_code: {e}")
    
    def predict(self, context, model_input):
        if isinstance(model_input, list):
            return [self.agent.run(query) for query in model_input]
        else:
            return self.agent.run(model_input)

class AgentChainWrapper:
    def __init__(self, chain_class = SimpleSequentialChain, agent_functions_list = []):
        self.chain_class = chain_class
        self.agents = [func() for func in agent_functions_list]
        self.agent_functions = agent_functions_list
    
    def _wrap_agent_runnable(self, agent) -> RunnableLambda:
        """
        Wraps the agent's .run() method into a RunnableLambda with a custom function name.
        Properly propagates errors instead of continuing to the next agent.
        """
        def base_fn(inputs: Dict[str, Any]) -> Dict[str, Any]:            
            # Run the agent, but don't catch exceptions - let them propagate
            # This will stop the entire pipeline on agent failure
            return agent.invoke(inputs)
            
            # Check if result starts with "An error occurred" which indicates agent failure
            # if isinstance(result, str) and result.startswith("An error occurred during execution:"):
            #     # Propagate the error by raising an exception to stop the execution
            #     raise RuntimeError(f"Agent {agent.__class__.__name__} failed: {result}")
                
            # return result

        # Clone function and set custom name
        fn_name = f"runnable_{agent.__class__.__name__.lower().replace(' ', '_')}"
        runnable_fn = types.FunctionType(
            base_fn.__code__,
            base_fn.__globals__,
            name=fn_name,
            argdefs=base_fn.__defaults__,
            closure=base_fn.__closure__,
        )

        return RunnableLambda(runnable_fn)
    
    def run(self, query):
        result = query
        def is_dataframe(obj) -> bool:
            try:
                return isinstance(obj, pd.DataFrame)
            except Exception as e:
                return False
        if is_dataframe(result):
            result = result.to_dict(orient='records')[0]
        runnables = []
        for agent in self.agents:
            if isinstance(agent, Runnable):
                runnables.append(agent)
            else:
                runnables.append(
                    self._wrap_agent_runnable(agent)
                )
        if self.chain_class is SimpleSequentialChain:
            pipeline = runnables[0]
            for r in runnables[1:]:
                pipeline = pipeline | r
            if is_dataframe(query):
                query = query.to_dict(orient='records')[0]
            return pipeline.invoke(query)
        chain = self.chain_class(
            chains=runnables,
        )
        return chain.run(result)
    
    def predict(self, context = "", model_input = ""):
        return self.run(model_input)

class CustomChainModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.agent_chain = None
        self.agents = []
    
    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("lock", None)
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()
    
    def load_context(self, context):
        import sys
        import os
        import shutil
        import importlib.util
        
        # Get the directory where artifacts are stored
        base_dir = os.path.dirname(list(context.artifacts.values())[0])
        
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        
        # Restore local modules
        for artifact_name, artifact_path in context.artifacts.items():
            if artifact_name.startswith("local_module_"):
                module_name = artifact_name.replace("local_module_", "")
                module_filename = f"{module_name}.py"
                dest_path = os.path.join(base_dir, module_filename)
                
                if not os.path.exists(dest_path):
                    shutil.copy2(artifact_path, dest_path)
                    print(f"Restored local module: {module_name}")
        
        # Load chain configuration
        chain_config_path = context.artifacts["chain_config"]
        spec = importlib.util.spec_from_file_location("chain_config", chain_config_path)
        chain_config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chain_config_module)
        
        chain_config = chain_config_module.CHAIN_CONFIG
        
        # Load each agent
        agent_functions = []
        for agent_info in chain_config["agents"]:
            agent_code_file = agent_info["agent_code_file"]
            function_name = agent_info["function_name"]
            
            # Load the agent module - handle the artifact key mapping
            artifact_key = agent_code_file.replace(".py", "")
            if artifact_key not in context.artifacts:
                # Try with agent_code_ prefix for consistency
                artifact_key = f"agent_code_{agent_info['name'].split('_')[-1]}"
            agent_code_path = context.artifacts[artifact_key]
            spec = importlib.util.spec_from_file_location("agent_module", agent_code_path)
            agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent_module)
            
            # Get the agent function
            agent_function = getattr(agent_module, function_name)
            agent_functions.append(agent_function)
        
        # Create the agent chain
        self.agent_chain = AgentChainWrapper(agent_functions_list=agent_functions)
    
    def predict(self, context, model_input):
        if isinstance(model_input, list):
            return [self.agent_chain.run(query) for query in model_input]
        else:
            return self.agent_chain.run(model_input)

class CrewAgentWrapper:
    def __init__(self, agent_func=None):
        if agent_func is not None:
            # During logging phase
            try:
                from crew_agent import create_crew_agent
                self.base_agent = create_crew_agent()
            except ImportError:
                raise ImportError("Could not import CrewAI agent functions")
        else:
            # During model loading phase
            try:
                from agent_code import create_crew_agent
                self.base_agent = create_crew_agent()
            except ImportError:
                try:
                    from crew_agent import create_crew_agent
                    self.base_agent = create_crew_agent()
                except ImportError:
                    raise ImportError("Could not import CrewAI agent")
    
    def run(self, query):
        try:
            if hasattr(self, 'base_agent'):
                # Import create_crew_with_task function
                try:
                    from agent_code import create_crew_with_task
                except ImportError:
                    from crew_agent import create_crew_with_task
                
                crew = create_crew_with_task(query)
                result = crew.kickoff()
                return str(result)
            else:
                return "Error: Agent not properly initialized"
        except Exception as e:
            print(f"Error running CrewAI crew: {e}")
            return f"Error executing query '{query}': {str(e)}"
    
    def predict(self, context, model_input):
        return self.run(model_input)

class CustomCrewModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.agent = None
    
    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("lock", None)
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.lock = threading.Lock()
    
    def load_context(self, context):
        import sys
        import os
        import shutil
        
        agent_code_path = context.model_config["agent_code"]
        agent_code_dir = os.path.dirname(agent_code_path)
        
        if agent_code_dir not in sys.path:
            sys.path.insert(0, agent_code_dir)
        
        for artifact_name, artifact_path in context.model_config.items():
            if artifact_name.startswith("local_module_"):
                module_name = artifact_name.replace("local_module_", "")
                module_filename = f"{module_name}.py"
                dest_path = os.path.join(agent_code_dir, module_filename)
                
                if not os.path.exists(dest_path):
                    shutil.copy2(artifact_path, dest_path)
                    print(f"Restored local module: {module_name}")
        
        try:
            import agent_code
            from agent_code import CrewAgentWrapper
            self.agent = CrewAgentWrapper()
        except ImportError as e:
            raise ImportError(f"Failed to import CrewAI agent_code: {e}")
    
    def predict(self, context, model_input):
        if isinstance(model_input, list):
            return [self.agent.run(query) for query in model_input]
        else:
            return self.agent.run(model_input)