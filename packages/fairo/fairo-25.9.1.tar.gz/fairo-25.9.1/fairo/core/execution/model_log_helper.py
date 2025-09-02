import mlflow
import mlflow.pyfunc
import os
import sys
import pkg_resources
import ast
import importlib.util
import shutil
import inspect
from pathlib import Path
from typing import List, Literal, Union, Callable
from fairo.core.execution.agent_serializer import CustomChainModel

class ModelLogHelper:
    def __init__(self, 
                 agent_type: Literal["CrewAI", "Langchain"], 
                 signature,
                 agents: List[Union[Callable, str]]):
        """
        Initialize ModelLogHelper
        
        Args:
            agent_type: Type of agent framework ("CrewAI" or "Langchain")
            agents: List of agent functions or file paths
            signature: The agent signature
        """
        self.agent_type = agent_type.lower()
        self.agents = agents
        self.signature = signature
        
        # Validate agent type
        if self.agent_type not in ["crewai", "langchain"]:
            raise ValueError("agent_type must be 'CrewAI' or 'Langchain'")
        
        # Set up MLflow
    
    def get_conda_env(self):
        """Generate conda environment specification based on current environment"""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        if self.agent_type == "crewai":
            required_packages = [
                "mlflow",
                "langchain",
                "langchain-aws", 
                "boto3",
                "cloudpickle",
                "crewai",
                "crewai-tools"
            ]
        else:
            required_packages = [
                "mlflow",
                "langchain",
                "langchain-aws", 
                "boto3",
                "cloudpickle"
            ]
        
        pip_packages = []
        for package in required_packages:
            try:
                dist = pkg_resources.get_distribution(package)
                pip_packages.append(f"{package}=={dist.version}")
            except pkg_resources.DistributionNotFound:
                pip_packages.append(package)
        
        conda_env = {
            "channels": ["defaults", "conda-forge"],
            "dependencies": [
                f"python={python_version}",
                "pip",
                {
                    "pip": pip_packages
                }
            ],
            "name": f"{self.agent_type}_env"
        }
        
        return conda_env
    
    def detect_local_dependencies(self, file_path):
        """Detect local module dependencies in a Python file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        local_modules = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    if self.is_local_module(module_name, file_path):
                        local_modules.append(module_name)
            
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                if module_name and self.is_local_module(module_name, file_path):
                    local_modules.append(module_name)
        
        return list(set(local_modules))
    
    def is_local_module(self, module_name, current_file_path):
        """Check if a module is a local file rather than an installed package"""
        if not module_name:
            return False
        
        current_dir = os.path.dirname(current_file_path)
        
        # Handle dotted module paths (e.g., "example_functions.hello_world")
        module_parts = module_name.split('.')
        
        # Check if it's a direct .py file in current directory
        if len(module_parts) == 1:
            module_file = f"{module_name}.py"
            local_path = os.path.join(current_dir, module_file)
            if os.path.exists(local_path):
                return True
        
        # Check if it's a subdirectory with Python files
        else:
            # For "example_functions.hello_world", check if "example_functions/hello_world.py" exists
            subdir_path = os.path.join(current_dir, *module_parts[:-1])
            module_file = f"{module_parts[-1]}.py"
            full_path = os.path.join(subdir_path, module_file)
            
            if os.path.exists(full_path):
                return True
            
            # Also check if the first part is a directory (package)
            first_part_dir = os.path.join(current_dir, module_parts[0])
            if os.path.isdir(first_part_dir):
                return True
        
        # Fallback: check if it's an installed package
        try:
            importlib.util.find_spec(module_name)
            # If find_spec succeeds but it's not in our local paths, it's installed
            return False
        except ImportError:
            # If find_spec fails, check again for local files
            if len(module_parts) == 1:
                module_file = f"{module_name}.py"
                local_path = os.path.join(current_dir, module_file)
                return os.path.exists(local_path)
        
        return False
    
    def bundle_local_modules(self, local_modules, base_dir):
        """Prepare local module files for MLflow artifacts, preserving directory structure"""
        bundled_files = {}
        processed_init_files = set()  # Track __init__.py files to avoid duplicates
        
        for module_name in local_modules:
            module_parts = module_name.split('.')
            
            # Handle single file modules (e.g., "hello_world")
            if len(module_parts) == 1:
                module_file = f"{module_name}.py"
                source_path = os.path.join(base_dir, module_file)
                
                if os.path.exists(source_path):
                    # Use filename as artifact key for root level files
                    bundled_files[module_file] = source_path
            
            # Handle subdirectory modules (e.g., "example_functions.hello_world")
            else:
                # Create the subdirectory structure in artifacts
                subdir_parts = module_parts[:-1]
                module_file = f"{module_parts[-1]}.py"
                
                # Source path: base_dir/example_functions/hello_world.py
                source_subdir = os.path.join(base_dir, *subdir_parts)
                source_path = os.path.join(source_subdir, module_file)
                
                if os.path.exists(source_path):
                    # Use relative path as artifact key to preserve directory structure
                    artifact_path = "/".join(subdir_parts + [module_file])
                    bundled_files[artifact_path] = source_path
                
                # Also check if we need to include __init__.py files to make it a proper package
                for i in range(len(subdir_parts)):
                    partial_subdir_source = os.path.join(base_dir, *subdir_parts[:i+1])
                    init_source = os.path.join(partial_subdir_source, "__init__.py")
                    
                    if os.path.exists(init_source):
                        # Use relative path as artifact key
                        init_artifact_path = "/".join(subdir_parts[:i+1] + ["__init__.py"])
                        
                        # Avoid adding the same __init__.py multiple times
                        if init_artifact_path not in processed_init_files:
                            bundled_files[init_artifact_path] = init_source
                            processed_init_files.add(init_artifact_path)
        
        return bundled_files
    
    def auto_detect_agent_files(self):
        """Automatically detect agent file paths from function objects using introspection with pathlib"""
        agent_files = []
        current_dir = Path(__file__).parent
        
        
        for i, agent_func in enumerate(self.agents):
            detected_file = None
            
            # Method 1: Function introspection with pathlib (most reliable)
            try:
                source_file = inspect.getfile(agent_func)
                source_path = Path(source_file)
                filename = source_path.name
                
                # Verify the file exists in current directory using pathlib
                if source_path.exists() and source_path.is_file():
                    detected_file = source_path
                
            except (OSError, TypeError) as e:
                print(f"  Agent {i+1}: Introspection failed ({e}), trying other methods...")
            
            # Method 2: Content scanning (additional verification)
            if detected_file:
                verified_file = self.verify_function_in_file(agent_func, detected_file)
                if verified_file != detected_file:
                    detected_file = verified_file
            
            # Convert Path objects to string filenames for consistency
            if isinstance(detected_file, Path):
                agent_files.append(detected_file.name)
            else:
                agent_files.append(detected_file)
        
        return agent_files
    
    def verify_function_in_file(self, agent_func, suspected_file):
        """Verify that a function actually exists in the suspected file using pathlib"""
        func_name = getattr(agent_func, '__name__', '')
        if not func_name:
            return suspected_file
        
        current_dir = Path(__file__).parent
        file_path = current_dir / suspected_file
        
        # Check if the suspected file exists and contains the function using pathlib
        if file_path.exists() and file_path.is_file():
            try:
                content = file_path.read_text(encoding='utf-8')
                if f"def {func_name}" in content:
                    return suspected_file
            except Exception:
                pass
        
        # If verification fails, scan other potential files
        return self.scan_directory_for_function(func_name) or suspected_file
    
    def scan_directory_for_function(self, func_name):
        """Scan directory for files containing the specified function using pathlib"""
        current_dir = Path(__file__).parent
        
        # Look for Python files that might contain agents using pathlib
        potential_files = [
            f for f in current_dir.iterdir() 
            if f.suffix == '.py' and any(keyword in f.name for keyword in ['agent', 'crew'])
        ]
        
        for file_path in potential_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                if f"def {func_name}" in content:
                    return file_path.name
            except Exception:
                continue
        
        return None
    
    def get_default_agent_files(self):
        """Get default file paths based on agent type and count"""
        if self.agent_type == "crewai":
            return ["crew_agent.py"]
        else:
            if len(self.agents) == 1:
                return ["agent.py"]
            elif len(self.agents) == 2:
                return ["agent.py", "agent_2.py"]
            else:
                return [f"agent_{i+1}.py" if i > 0 else "agent.py" 
                       for i in range(len(self.agents))]
    
    def create_custom_model(self):
        """Create custom model - always use chain model for consistency"""
        # Always use CustomChainModel since we always have an array of agents
        return CustomChainModel()
    
    
    def log_model(self, agent_files: List[str] = None, auto_detect: bool = True):
        """
        Log the agent model to MLflow
        
        Args:
            agent_files: List of agent file paths. If None, will auto-detect
            auto_detect: Whether to automatically detect file paths when agent_files is None
        """
        # Create custom model
        custom_model = self.create_custom_model()
        model_path = ""
        
        # Determine agent files using auto-detection or fallback with pathlib
        if agent_files is None:
            if auto_detect:
                try:
                    agent_files = self.auto_detect_agent_files()
                        
                except Exception as e:
                    print(f"Auto-detection failed ({e}), using defaults...")
                    agent_files = self.get_default_agent_files()
            else:
                agent_files = self.get_default_agent_files()
        
        agent_file = inspect.getfile(self.agents[0])
        base_dir = os.path.dirname(os.path.abspath(agent_file))
        artifacts_dir = os.path.join(base_dir, "temp_artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        
        try:
            artifacts = {}
            all_local_modules = set()
            
            # Process each agent file
            for i, agent_file in enumerate(agent_files):
                agent_file_path = os.path.join(base_dir, agent_file)
                
                if not os.path.exists(agent_file_path):
                    print(f"Warning: Agent file {agent_file} not found, skipping...")
                    continue
                
                
                # Copy agent file - always use indexed naming for consistency
                agent_code_path = os.path.join(artifacts_dir, f"agent_code_{i}.py")
                artifact_key = f"agent_code_{i}"
                
                with open(agent_file_path, 'r') as src, open(agent_code_path, 'w') as dst:
                    dst.write(src.read())
                
                artifacts[artifact_key] = agent_code_path
                
                # Detect local dependencies
                local_modules = self.detect_local_dependencies(agent_file_path)
                all_local_modules.update(local_modules)
            
            # Bundle all unique local modules
            nested_artifacts = {}
            if all_local_modules:
                bundled_modules = self.bundle_local_modules(
                    list(all_local_modules), 
                    base_dir
                )
                
                for artifact_path, source_path in bundled_modules.items():
                    # Separate nested artifacts from flat artifacts
                    if "/" in artifact_path:
                        nested_artifacts[artifact_path] = source_path
                    else:
                        artifacts[artifact_path] = source_path
            
            # Create chain configuration - always create for consistency
            chain_config = {
                "agents": [
                    {
                        "name": f"agent_{i}",
                        "function_name": getattr(agent_func, '__name__', f"agent_function_{i}"),
                        "agent_code_file": f"agent_code_{i}.py"
                    }
                    for i, agent_func in enumerate(self.agents)
                ],
                "execution_mode": "sequential",
                "agent_type": self.agent_type,
                "total_agents": len(self.agents)
            }
            
            chain_config_path = os.path.join(artifacts_dir, "chain_config.py")
            with open(chain_config_path, 'w') as f:
                f.write(f"CHAIN_CONFIG = {repr(chain_config)}\n")
            
            artifacts["chain_config"] = chain_config_path
            
            # Generate conda environment
            conda_env = self.get_conda_env()
            # Log the model
            model = mlflow.pyfunc.log_model(
                python_model=custom_model,
                artifacts=artifacts,
                conda_env=conda_env,
                signature=self.signature,
            )
            for key, value in artifacts.items():
                artifact_dir = os.path.dirname(f"{model.artifact_path}/artifacts/{key}")
                mlflow.log_artifact(value, artifact_dir)
            # Set active model immediately after logging to link future traces
            mlflow.set_active_model(model_id=model.model_id)
            
            # Log nested artifacts separately to preserve directory structure
            for artifact_path, source_path in nested_artifacts.items():
                # Extract directory path from artifact_path (remove filename)
                artifact_dir = os.path.dirname(f"custom/{artifact_path}")
                mlflow.log_artifact(source_path, artifact_dir)
            
            
        finally:
            if os.path.exists(artifacts_dir):
                shutil.rmtree(artifacts_dir)