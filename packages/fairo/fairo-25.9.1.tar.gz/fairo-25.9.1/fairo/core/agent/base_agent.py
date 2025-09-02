import time
import json
import re
import uuid
import traceback
import sys

from typing import Dict, List, Optional, Callable, Any, Tuple
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables.config import RunnableConfig
from fairo.core.agent.output.base_output import BaseOutput
from fairo.core.agent.tools.base_tools import BaseTool
from fairo.core.agent.tools.utils import Iteration, LLMAgentOutput, ToolResult
from langchain_core.messages.tool import ToolCall
from fairo.core.chat.chat import FairoChat
from fairo.core.client.client import BaseClient
from fairo.core.workflow.dependency import BaseVectorStore
from fairo.core.agent.utils import truncate_content, truncate_obj_content
from fairo.settings import get_mlflow_gateway_chat_route, get_mlflow_gateway_uri


class SimpleAgent:
    """
    A simplified AI Agent inspired by CrewAI, designed to run as a loop of LangChain calls.
    Uses prompt templates from a JSON file for easy customization.
    """

    def __init__(
            self,
            agent_name: str,
            role: str,
            goal: str,
            backstory: str,
            verbose: bool = False,
            llm: Optional[Any] = None,
            tools: Optional[List[BaseTool]] = None,
            memory: Optional[List[Dict]] = None,
            template_path: str = "prompt_template.json",
            output: Optional[List[BaseOutput]] = [],
            patch_run_output_json: Callable[[LLMAgentOutput], None] = None,
            client: BaseClient = None,
            knowledge_stores: Optional[List[BaseVectorStore]] = None,
            max_iterations: int = 10,
            workflow_run_id: str = "",
    ):
        """
        Initialize the SimpleAgent with its characteristics and capabilities.

        Args:
            role: The role of the agent (e.g., "Data Analyst", "Manager")
            goal: The goal the agent is trying to achieve
            backstory: Background information about the agent
            verbose: Whether to print detailed logs
            debug: Whether to print debug information, including prompts
            llm: LangChain language model to use (defaults to ChatMLflow with configured gateway)
            tools: List of BaseTool instances
            memory: Optional list of memory items
            knowledge_stores: Optional list of FAISS vector store instances to use for context retrieval
            template_path: Path to the JSON file containing prompt templates
        """
        self.agent_name = agent_name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.use_langchain_mlflow_chat = True if not llm else False
        self.workflow_run_id = workflow_run_id
        self.llm = llm or FairoChat(
            endpoint=get_mlflow_gateway_chat_route(),
            workflow_run_id=self.workflow_run_id
        )
        self.memory = memory or []
        self.conversation_history = []

        # Store the BaseTool instances
        self.tool_instances = tools or []
        
        # Create tool execution dictionary from instances
        self.tools = {}
        for tool in self.tool_instances:
            tool.set_client(client)
            if not isinstance(tool, BaseTool):
                raise ValueError(f"Expected BaseTool instance, got {type(tool)}")
            self.tools[tool.name] = tool.execute

        # Prepare tool names for formatting
        self.tool_names = list(self.tools.keys())
        self.available_tools_formatted = [tool.to_dict(include_type=self.use_langchain_mlflow_chat) for tool in self.tool_instances]

        # Load prompt templates from JSON file
        self.templates = self._load_templates(template_path)
        self.output = output
        self.patch_run_output_json = patch_run_output_json
        self.client = client
        
        self.input_key = f"input_{self.agent_name}"
        self.output_key = f"output_{self.agent_name}"
        self.knowledge_stores = knowledge_stores or []

        self.max_iterations = max_iterations

    @staticmethod
    def _load_templates(template_path: str) -> Dict:
        """Load prompt templates from a JSON file."""
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            print(f"Error loading template file: {e}")
            print("Using default templates instead.")
        # Return empty dict to use fallback templates
        return {}

    def _get_role_playing_prompt(self) -> str:
        """Generate the role playing part of the prompt."""
        template = self.templates.get(
            'role_playing',
            "You are {role}. {backstory}\n"
            "Your personal goal is: {goal}"
            "You should use reason, but provide one step at a time in order to await further feedback and instructions."
        )
        return template.format(role=self.role, backstory=self.backstory, goal=self.goal)

    def _get_tools_prompt(self) -> str:
        """Generate the tools part of the prompt if tools are available."""
        if not self.tools:
            # Use the no_tools template if available, otherwise use default
            return self.templates.get(
                'no_tools',
                "\nTo give my best complete final answer to the task respond using the exact following format:\n\n"
                "Thought: I now can give a great answer\n"
                "Final Answer: Your final answer must be the great and the most complete as possible, it must be outcome "
                "described.\n\n I MUST use these formats, my job depends on it!"
            )

        # Get tool descriptions using BaseTool's get_prompt_format method
        tools_descriptions = "\n\n".join([tool.get_prompt_format() for tool in self.tool_instances])

        # Use the tools template if available, otherwise use default
        tools_template = self.templates.get(
            'tools',
            "\n\nTo help you answer questions accurately, you have access to the following tools, and ONLY these tools. "
            "You should NEVER make up tools that are not listed here:\n\n"
            "{tools}\n\n"
            "IMPORTANT: If you would like to use a tool you MUST use the following format in your response:\n\n"
            "```\n"
            "Thought: you should always think about what to do, and explain what you will use the tool for.\n"
            "Action: The action you plan to take with the tool, only one name of [{tool_names}], "
            "just the name, exactly as it's written.\n"
            "Action Input: The input to the tool, just a simple JSON object, enclosed in curly braces, "
            "using \" to wrap keys and values.\n"
            "```\n\n"
            "IMPORTANT: After you provide this info to the tool, you should no longer generate any output until the"
            " tool response is provided to you. Any text you generate after this point will be erased. \n\n "
            "The tool will provide a Result in the format:\n\n"
            "```\n"
            "Observation: the tools response, usually JSON but not always\n"
            "```\n\n"
            "This Thought/Action/Action Input/Result can repeat N times until you no longer need to use a tool."
            "When you do not wish to use a tool, you must provide a final answer."
            "You MUST either use a tool (use one at time) OR give your best final answer not both at the same time.\n"
            "A final answer must be returned in the following format:\n\n"
            "```\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n"
            "```\n"
            "In the event you know the final answer without using tools, please justify why in your thoughts."
        )

        return tools_template.format(tools=tools_descriptions, tool_names=', '.join(self.tool_names))

    def _get_knowledge_store_context(self, query: str, k: int = None) -> str:
        """
        Retrieve relevant context from all knowledge stores based on the query.
        
        Args:
            query: The query to use for retrieving context
            k: Number of results to retrieve from each knowledge store
            
        Returns:
            String containing relevant context from all knowledge stores
        """
        if not self.knowledge_stores:
            return ""
            
        all_contexts = []
        
        for store in self.knowledge_stores:
            try:
                # Get collection metadata if available
                store_name = "Knowledge Store"
                store_instructions = ""
                
                if hasattr(store, 'collection_metadata') and store.collection_metadata:
                    if 'name' in store.collection_metadata:
                        store_name = store.collection_metadata['name']
                    if 'ai_instructions' in store.collection_metadata:
                        store_instructions = store.collection_metadata['ai_instructions']
                
                # Retrieve relevant documents
                results = store.similarity_search(query, k=k)

                if results:
                    # Format the context
                    context_items = []

                    # Add store name and instructions
                    context_header = f"## {store_name}"
                    if store_instructions:
                        context_header += f"\n{store_instructions}"
                    context_items.append(context_header)

                    # Add each document's content
                    for i, doc in enumerate(results, 1):
                        # Format metadata as string if present
                        metadata_str = ""
                        if doc.metadata:
                            metadata_items = []
                            # keep the metadata reasonable length
                            truncated_metadata = truncate_obj_content(doc.metadata, 100)
                            for key, value in truncated_metadata.items():
                                if store.collection_metadata.get('metadata_include'):
                                    if key in store.collection_metadata.get('metadata_include'):
                                        metadata_items.append(f"{key}: {value}")
                                else:
                                    metadata_items.append(f"{key}: {value}")
                            metadata_str = "Document Metadata: " + ", ".join(metadata_items)

                        context_items.append(f"### Result {i}:\n{doc.page_content}\n{metadata_str}")

                    all_contexts.append("\n\n".join(context_items))
            
            except Exception as e:
                if self.verbose:
                    print(f"Error retrieving context from knowledge store: {str(e)}")
        
        # Combine all contexts
        if all_contexts:
            return "\n\n" + "\n\n".join(all_contexts)
        
        return ""

    def _get_memory_prompt(self) -> str:
        """Generate the memory part of the prompt if memory is available."""
        if not self.memory:
            return ""

        memory_str = "\n".join([f"- {mem.get('content', '')}" for mem in self.memory])

        # Use the memory template if available, otherwise use default
        memory_template = self.templates.get(
            'memory',
            "\n\n# Useful context: \n{memory}"
        )
        return memory_template.format(memory=memory_str)

    def _build_system_prompt(self) -> str:
        """Build the complete system prompt for the agent."""
        role_playing = self._get_role_playing_prompt()
        tools_prompt = self._get_tools_prompt()
        memory_prompt = self._get_memory_prompt()

        return f"{role_playing}{tools_prompt}{memory_prompt}"

    def _build_task_prompt(self, task: str, context: Optional[str] = None) -> str:
        """Build the task prompt for the agent."""
        # Use the task template if available, otherwise use default
        task_template = self.templates.get(
            'task',
            "\nCurrent Task: \n\n {input} \n\n"
            "Begin! This is VERY important to you, use the tools available and give your best Final Answer,"
            " your job depends on it!"
        )

        base_task = task_template.format(input=task)
        knowledge_context = self._get_knowledge_store_context(task)

        # Combine user-provided context and knowledge store context
        combined_context = ""
        if context:
            combined_context += context
        if knowledge_context:
            combined_context += knowledge_context
            
        if combined_context:
            # Use the task_with_context template if available, otherwise append context
            context_template = self.templates.get('task_with_context',
                                                  "{task}\n\nThis is the context you're working with:\n{context}")
            return context_template.format(task=base_task, context=combined_context)

        return base_task

    def _parse_response(self, response: str) -> Dict:
        """
        Parse the LLM response to extract thought, action, action input, and final answer.

        Returns:
            Dict with keys 'thought', 'action', 'action_input', and 'final_answer'
        """
        result = {
            'thought': None,
            'action': None,
            'action_input': None,
            'final_answer': None,
            'observation': None
        }

        # Extract thought
        thought_match = re.search(r'Thought:(.*?)(?:Action:|Final Answer:|$)', response, re.DOTALL)
        if thought_match:
            result['thought'] = thought_match.group(1).strip()

        # Extract action and action input
        action_match = re.search(r'Action:(.*?)(?:Action Input:|$)', response, re.DOTALL)
        if action_match:
            result['action'] = action_match.group(1).strip()

            action_input_match = re.search(r'Action Input:(.*?)(?:\n|$)', response, re.DOTALL)
            if action_input_match:
                action_input_str = action_input_match.group(1).strip()
                try:
                    # Try to parse JSON
                    result['action_input'] = json.loads(action_input_str)
                except json.JSONDecodeError as e:
                    # Set error message for LLM output
                    error_msg = f"Invalid JSON format in Action Input: {str(e)}"
                    # Get traceback
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                    traceback_details = ''.join(tb_lines)
                    # Store error info in result dict - errors will be handled by caller
                    result['error'] = error_msg
                    raise Exception(error_msg)

        # Extract final answer
        final_answer_match = re.search(r'Final Answer:(.*?)(?:$)', response, re.DOTALL)
        if final_answer_match:
            result['final_answer'] = final_answer_match.group(1).strip()

        # Extract observation if present
        observation_match = re.search(r'Observation:(.*?)(?:Thought:|$)', response, re.DOTALL)
        if observation_match:
            result['observation'] = observation_match.group(1).strip()

        return result

    @staticmethod
    def _get_error_details(e: Exception) -> Tuple[str, str]:
        """
        Get detailed error information including traceback.

        Args:
            e: The exception object

        Returns:
            A tuple of (error_message, detailed_traceback)
        """
        error_message = str(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        detailed_traceback = ''.join(tb_lines)
        return error_message, detailed_traceback

    @staticmethod
    def _truncate_response_at_action(response: str) -> str:
        """
        Truncate the LLM response to remove any hallucinated observation text.

        This keeps only the Thought and Action parts, removing any Observation that might
        have been hallucinated by the model.

        Args:
            response: The full LLM response

        Returns:
            The truncated response string
        """
        # Look for the code block closing marker after the Action Input
        action_input_match = re.search(r'Action Input:', response, re.DOTALL)
        if not action_input_match:
            # If no Action Input found, just use the full response
            return response

        # First try to find the ending of a JSON object (a closing brace followed by a newline)
        # This assumes the action input is a JSON object
        json_end_match = re.search(r'}\s*\n', response[action_input_match.end():], re.DOTALL)
        if json_end_match:
            # Calculate the absolute position in the original string
            end_position = action_input_match.end() + json_end_match.end()

            # Check if there's a closing marker (```) immediately after the JSON
            # This means it should be on the next line
            remaining_text = response[end_position:]

            # We're looking for either:
            # 1. ```\n (closing marker at start of line followed by newline)
            # 2. ```$ (closing marker at start of line followed by end of string)
            closing_marker_immediate = re.match(r'^\s*```(?:\n|$)', remaining_text)

            if closing_marker_immediate:
                # Include the closing marker plus newline if present
                match_end = closing_marker_immediate.end()
                end_position += match_end

            return response[:end_position].strip()

        # If no JSON ending found, look for the code block closing marker (```)
        closing_marker_match = re.search(r'\n```', response[action_input_match.end():], re.DOTALL)
        if closing_marker_match:
            # Calculate the absolute position in the original string
            end_position = action_input_match.end() + closing_marker_match.end()
            return response[:end_position].strip()

        # Fallback 1: search for "Observation:" and truncate before it
        observation_match = re.search(r'Observation:', response, re.DOTALL)
        if observation_match:
            return response[:observation_match.start()].strip()

        # Fallback 2: Just return the part until the next line after Action Input
        # This handles cases where there might not be a code block
        next_line_match = re.search(r'\n', response[action_input_match.end():], re.DOTALL)
        if next_line_match:
            end_position = action_input_match.end() + next_line_match.end()
            return response[:end_position].strip()

        # If all else fails, return the original response
        return response
    
    def get_tool_name(self, action) -> str:
        tool_instance = next((t for t in self.tool_instances if t.name == action), None)
        return tool_instance.name if tool_instance else ""

    def execute_tool(self, tool_name: str, tool_input: Any) -> str:
        """
        Execute a tool with the given input.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool (typically a dict)

        Returns:
            Result of the tool execution as a string

        Raises:
            Exception: If there is any error during tool execution
        """
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not found. Available tools: {', '.join(self.tool_names)}"
            raise Exception(error_msg)

        # Find the tool instance
        tool_instance = next((t for t in self.tool_instances if t.name == tool_name), None)

        if not tool_instance:
            error_msg = f"Could not find tool instance for '{tool_name}'"
            raise Exception(error_msg)

        # Use validate_and_execute to handle validation and execution
        try:
            if isinstance(tool_input, dict):
                result = tool_instance.validate_and_execute(**tool_input)
            else:
                # Handle case where input might be a string or other non-dict
                result = tool_instance.validate_and_execute(input=tool_input)
                
            return str(result)
        except Exception as e:
            return f"Error with tool '{tool_name}': {str(e)}"

    def set_client(self, client: BaseClient):
        self.client = client
        for tool in self.tool_instances:
            tool.set_client(client)
    
    def set_workflow_run_id(self, workflow_run_id: str):
        self.set_workflow_run_id = workflow_run_id
        self.llm.extra_params = {"workflow_run_id": workflow_run_id}

    def run(self, task: str, context: Optional[str] = None, max_iterations: int = None) -> str:
        """
        Run the agent on a task.

        Args:
            task: The task for the agent to complete
            context: Optional additional context
            max_iterations: Maximum number of thought-action cycles

        Returns:
            Final answer from the agent
        """
        start_time = time.time()
        
        # Initialize variables outside the try block so they're accessible in the except block
        output = None
        system_prompt = None
        task_prompt = None
        initial_prompt = None
        final_answer = None

        try:
            tool_check = False
            system_prompt = self._build_system_prompt()
            task_prompt = self._build_task_prompt(task, context)
            print_index = 0

            output = LLMAgentOutput(
                node_name=self.agent_name,
                task=task,
                context=context,
                query_result=None,
                memory=None,
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=task_prompt)
            ]

            if max_iterations is None:
                max_iterations = self.max_iterations

            # Add conversation history if available
            for msg in self.conversation_history:
                messages.append(msg)

            iterations = 0
            final_answer = None

            # Store the initial prompt in case of early errors
            initial_prompt = system_prompt + "\n\n" + task_prompt

            def truncate_tool_response(message):
                """
                Truncate tool response messages to 5 lines for better readability.

                Args:
                    message: LangChain BaseMessage object

                Returns:
                    String with truncated content if it's a tool_response, original content otherwise
                """
                # Check if this is a tool response message
                if isinstance(message, ToolMessage):
                    content = message.content
                    return truncate_content(content, 5)
                return message.content

            while iterations < max_iterations and final_answer is None:
                iteration_start_time = time.time()
                iteration_prompt = "".join([(truncate_tool_response(message) + "\n") for message in messages[print_index:]])
                if self.verbose:
                    print(f"\n============================================================== Iteration {iterations + 1} ==="
                          f"===========================================================")
                    print(iteration_prompt)
                print_index = len(messages)

                # Get response from LLM with error handling for context window limits
                try:
                    # save response content with hallucinations truncated
                    response_content = self._truncate_response_at_action(
                        self.llm.invoke(messages, tools=self.available_tools_formatted).content
                    )

                except Exception as e:
                    # Check if it's a boto3 ValidationException
                    if 'ValidationException' in str(e):
                        from .utils import truncate_long_message, summarize_with_llm

                        if self.verbose:
                            print("Context window limit exceeded. Truncating messages and generating summaries...")

                        # Process tool_output messages - they're usually the longest

                        if self.verbose:
                            print("============================================================== UPDATED MESSAGES =="
                                  "============================================================")

                        for i, msg in enumerate(messages):
                            if hasattr(msg, 'name') and msg.name == 'tool_response' and hasattr(msg, 'content'):
                                # Save original content
                                original_content = msg.content

                                # Only process if it's long enough to need truncation
                                if len(original_content.split('\n')) > 100:
                                    # Get AI summary using same LLM
                                    summary = summarize_with_llm(
                                        content=original_content,
                                        llm=self.llm,
                                        prompt="You are reviewing tool output. Summarize the key details from this "
                                               " output in 2-3 sentences. Focus on the most important findings or "
                                               "results:\n\n{content}"
                                    )
                                    # Truncate the message
                                    truncated = truncate_long_message(original_content)

                                    # Combine truncated content with summary
                                    messages[i].content = f"{truncated}\n\n### AI-GENERATED SUMMARY ###\n{summary}"

                                    if self.verbose:
                                        print(
                                            f"UPDATED MESSAGE {i} -- \n\n{truncate_tool_response(msg)}"
                                            f"\n\n### AI-GENERATED SUMMARY ###\n{summary} \n\n"
                                        )

                        # Try again with truncated messages
                        try:
                            response_content = self._truncate_response_at_action(
                                self.llm.invoke(messages, tools=self.available_tools_formatted).content
                            )
                        except Exception as e2:
                            # If still failing, get detailed error info and record it
                            error_msg, traceback_details = self._get_error_details(e2)
                            error_msg = f"Error: The conversation is too complex for the model even after truncation: {error_msg}"

                            # Add an iteration for the error
                            error_iteration = Iteration(
                                prompt=iteration_prompt,
                                response=f"Error: {error_msg}"
                            )
                            output.add_iteration(error_iteration)
                            output.add_error(error_msg, traceback_details)

                            # Make sure to patch the output with the error just once
                            # We're returning this output, so don't patch here
                            return error_msg
                    else:
                        # For other errors, get detailed error info and record it
                        error_msg, traceback_details = self._get_error_details(e)
                        error_msg = f"Error during LLM invocation: {error_msg}"

                        # Record the error
                        output.add_error(error_msg, traceback_details)

                        # Add completion time to the output
                        end_time = time.time()
                        total_execution_time = end_time - start_time
                        output.add_duration(f"{total_execution_time:.2f}s")

                        # Re-throw the error - will be handled in the outer try-except
                        raise

                # Parse the response
                try:
                    parsed = self._parse_response(response_content)
                    # Check for tool_use
                    tool_call = None
                    if parsed['action'] and parsed['action'] in self.tools:
                        tool_call = ToolCall(id=f"call_{uuid.uuid4()}", name=parsed['action'], args=parsed['action_input'])
                        messages.append(AIMessage(content=response_content, tool_calls=[tool_call]))
                        # For iterations with tools, filter out the duplicated thought/action/action input
                        # from response as it will be included in the tool_result
                        # Remove just the Thought/Action/Action Input sections using regex
                        # First attempt to remove the entire code block if present (```)
                        filtered_response = re.sub(r'```\n?Thought:.*?```\n?', '', response_content, flags=re.DOTALL)

                        # If code block removal didn't happen (no match), remove each section separately
                        if filtered_response == response_content:
                            # Remove 'Thought:' section
                            filtered_response = re.sub(r'Thought:.*?(?=\n\w+:|$)', '', response_content, flags=re.DOTALL)
                            # Remove 'Action:' section
                            filtered_response = re.sub(r'Action:.*?(?=\n\w+:|$)', '', filtered_response, flags=re.DOTALL)
                            # Remove 'Action Input:' section
                            filtered_response = re.sub(r'Action Input:.*?(?=\n\w+:|$)', '', filtered_response, flags=re.DOTALL)
                        # Clean up multiple newlines
                        filtered_response = re.sub(r'\n{3,}', '\n\n', filtered_response)
                    else:
                        messages.append(AIMessage(content=response_content))
                        filtered_response = response_content
                    iteration = Iteration(
                        prompt=iteration_prompt,
                        response=filtered_response
                    )
                except Exception as e:
                    # Get detailed error information
                    error_msg, traceback_details = self._get_error_details(e)
                    error_msg = f"Error parsing response: {error_msg}"
                    # Record the error in the output object
                    output.add_error(error_msg, traceback_details)
                    # Create iteration with error
                    iteration = Iteration(
                        prompt=iteration_prompt,
                        response=f"Error: {str(e)}"
                    )
                    # Add to messages for next iteration
                    messages.append(HumanMessage(content=f"Error: {str(e)}. Please fix your response format."))
                    # Create empty parsed result with error
                    parsed = {'action': None, 'thought': None, 'action_input': None, 'final_answer': None, 'error': error_msg}

                if self.verbose:
                    print(f"\n============================================================== Response {iterations + 1} "
                          f"==============================================================\n")
                    print(response_content)
                print_index += 1

                # If we have a final answer, return it
                if parsed['final_answer'] and (tool_check or not self.tools):
                    final_answer = parsed['final_answer']
                    # Save output object """
                    iteration_end_time = time.time()
                    iteration_execution_time = iteration_end_time - iteration_start_time
                    iteration = Iteration(
                        prompt=iteration_prompt,
                        response=final_answer,
                        duration=f"{iteration_execution_time:.2f}s"
                    )
                    output.add_iteration(iteration)
                    break
                elif parsed['action'] and parsed['action'] in self.tools:
                    tool_check = True  # makes sure to remind agent to try a tool
                    tool_name = parsed['action']
                    tool_id = tool_call.get('id')
                    tool_args = parsed['action_input']
                    try:
                        observation = self.execute_tool(tool_name, tool_args)
                        # Add the tool output to the iteration output
                        iteration.add_tool_result(ToolResult(
                            tool_name=self.get_tool_name(tool_name),
                            thought=parsed['thought'],
                            action_input=tool_args,
                            response=observation
                        ))
                        # Create a ToolMessage with the appropriate tool_call_id from the response
                        messages.append(ToolMessage(content=observation, tool_call_id=tool_id))
                    except Exception as e:
                        # Get detailed error information
                        error_msg, traceback_details = self._get_error_details(e)
                        error_msg = f"Error executing tool '{parsed['action']}': {error_msg}"
                        # Record the error in the output object (just once)
                        output.add_error(error_msg, traceback_details)
                        observation = f"Error: {str(e)}"
                        # Add the error to the current iteration's tool results
                        iteration.add_tool_result(ToolResult(
                            tool_name=self.get_tool_name(parsed['action']),
                            thought=parsed['thought'],
                            action_input=parsed['action_input'],
                            response=observation
                        ))
                        # Create a ToolMessage with the appropriate tool_call_id from the response
                        tool_call_id = tool_call.id if hasattr(tool_call, 'id') else tool_call.get('id', f"call_{uuid.uuid4()}")
                        messages.append(ToolMessage(content=observation, tool_call_id=tool_call_id))
                else:
                    if parsed['action']:
                        error_msg = (f"Error: Tool '{parsed['action']}' not found or invalid. Available tools: "
                                     f"{', '.join(self.tool_names)}")
                        # Record the error in the output object with call stack info
                        traceback_details = ''.join(traceback.format_stack())
                        output.add_error(error_msg, traceback_details)
                        messages.append(HumanMessage(content=error_msg))

                        if self.verbose:
                            print(error_msg)
                    else:
                        # Force a final answer if no action was taken and tool_check was applied
                        if tool_check:
                            force_msg = "You must either use a tool or provide a final answer. Please try again."
                        else:
                            force_msg = ("Why didn't you use the provided tools?  "
                                         "Only give final answer if you are ABSOLUTELY SURE a tool can't help you.\n")
                            tool_check = True
                        messages.append(HumanMessage(content=force_msg))

                        if self.verbose:
                            print(force_msg)
                iteration_end_time = time.time()
                iteration_execution_time = iteration_end_time - iteration_start_time
                iteration.add_duration(f"{iteration_execution_time:.2f}s")
                output.add_iteration(iteration)
                iterations += 1

            # If we've reached the maximum number of iterations without a final answer
            if final_answer is None:
                final_answer = "I was unable to complete the task within the maximum number of iterations."

            # Add messages to conversation history
            self.conversation_history.append(messages)

            # Calculate total execution time
            end_time = time.time()
            total_execution_time = end_time - start_time
            output.add_duration(f"{total_execution_time:.2f}s")

            # Save output
            # if self.patch_run_output_json:
            #     self.patch_run_output_json(output.to_dict())

            # Execute output
            # if self.output and len(self.output) > 0:
            #     self.execute_outputs(final_answer)

            return final_answer

        except Exception as e:
            # Get detailed error information
            error_msg, traceback_details = self._get_error_details(e)
            error_msg = f"Unexpected error during agent execution: {error_msg}"

            # Create an output object if it doesn't exist yet
            if output is None:
                output = LLMAgentOutput(
                    node_name=self.agent_name,
                    task=task,
                    context=context,
                    query_result=None,
                    memory=None,
                )

            # If we don't have any iterations yet, add one with the initial prompt
            if not output.iterations and initial_prompt:
                error_iteration = Iteration(
                    prompt=initial_prompt,
                    response=f"Error: {error_msg}"
                )
                output.add_iteration(error_iteration)

            # Record the error
            output.add_error(error_msg, traceback_details)

            # Add timing information
            end_time = time.time()
            total_execution_time = end_time - start_time
            output.add_duration(f"{total_execution_time:.2f}s")

            # Make sure to patch the output with the error
            # if self.patch_run_output_json:
            #     self.patch_run_output_json(output.to_dict())

            # Re-throw the exception with more context
            raise Exception(f"Agent execution failed: {error_msg}") from e
    
    def execute_outputs(self, final_answer) -> None:
        """
        Execute all output handlers with the final answer.

        Args:
            final_answer: The final answer from the agent to pass to output handlers
        """
        output_errors = []

        for output_handler in self.output:
            try:
                # Execute the output handler
                output_handler.execute(final_answer)

                # Patch with successful output
                if self.patch_run_output_json:
                    self.patch_run_output_json(output_handler.to_fairo_output())
            except Exception as e:
                # Get detailed error information
                error_msg, traceback_details = self._get_error_details(e)
                error_msg = f"Error in output handler '{output_handler.name}': {error_msg}"

                # Store errors to report once after the loop
                output_errors.append((error_msg, traceback_details))

        # Report errors after processing all outputs to avoid multiple error records for the same run
        # if output_errors and self.patch_run_output_json:
        #     # Create a single error output object with all errors
        #     error_output = LLMAgentOutput(
        #         node_name=self.agent_name,
        #         task="Output execution",
        #         context=None,
        #         query_result=None,
        #         memory=None
        #     )

        #     # Add all collected errors
        #     for error_msg, traceback_details in output_errors:
        #         error_output.add_error(error_msg, traceback_details)

        #     # Patch once with all errors
        #     self.patch_run_output_json(error_output.to_dict())

    def add_memory(self, content: str) -> None:
        """
        Add an item to the agent's memory.

        Args:
            content: Content to add to memory
        """
        self.memory.append({"content": content})