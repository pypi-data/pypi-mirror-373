
from typing import List
from fairo.core.agent.base_agent import SimpleAgent


def output_workflow_tools(agents):
        tools = []
        seen_names = set()
        tool_num = 1

        for agent in agents:
            for tool in agent.tool_instances:
                if tool.name in seen_names:
                    continue

                seen_names.add(tool.name)
                tools.append({
                    "name": tool.name,
                    "schema": tool.args_schema.args_schema.model_json_schema() if tool.args_schema else None,
                    "returns": tool.returns,
                    "tool_num": tool_num,
                    "description": tool.description
                })
                tool_num += 1

        return tools

def output_workflow_dependencies(agents: List[SimpleAgent]):
    dependencies = []
    seen_dependencies = set()
    dependency_num = 1
    for agent in agents:
        for store in agent.knowledge_stores:
            if store.collection_name in seen_dependencies:
                continue
            seen_dependencies.add(store.collection_name)
            store_info = {
                "dependency_num": dependency_num,
                "name": store.collection_name
            }
            if hasattr(store, 'collection_uuid'):
                store_info['id'] = store.collection_uuid
            dependencies.append(store_info)
            dependency_num += 1
    return dependencies

def output_workflow_agent_nodes(tools, dependencies, agents: List[SimpleAgent]):
    tool_map = {t['name']: t['tool_num'] for t in tools}
    dependency_map = {t['name']: t['dependency_num'] for t in dependencies}
    _agents = []
    outputs = []
    agent_num = 1
    output_num = 1
    for agent in agents:
        agent_outputs = []
        agent_tools = [
            tool_map[tool.name]
            for tool in agent.tool_instances
            if tool.name in tool_map
        ]
        agent_dependencies = [
            dependency_map[store.collection_name]
            for store in agent.knowledge_stores
            if store.collection_name in dependency_map
        ]
        if agent.output and len(agent.output) > 0:
            for output in agent.output:
                outputs.append({
                    "name": output.name,
                    "source": f"Node-{agent_num}",
                    "description": output.description,
                    "destination": output.destination,
                    "num": output_num
                })
                agent_outputs.append(output_num)
                output_num += 1
        _agents.append({
            "goal": agent.goal,
            "name": agent.agent_name,
            "role": agent.role,
            "tool": agent_tools,
            "knowledge_store": agent_dependencies,
            "output": agent_outputs,
            "tigger": {},
            "backstory": agent.backstory,
        })
        agent_num += 1
    nodes = {
                "1": {
                    "id": "1",
                    "slug": "",
                    "stage": "middle",
                    "title": "Agent Executor",
                    "params": {
                        "agents": _agents
                    },
                    "handler": [{
                        "step": "2",
                        "type": "go_to",
                        "condition": {
                            "value": "is_success",
                            "test_value": True,
                            "condition_test": "=="
                        },
                        "edge_description": ""
                    }],
                    "node_type": "KNOWLEDGE_STORE_AGENT_EXECUTOR",
                    "position_x": 490.24,
                    "position_y": 66.4,
                    "description": ""
                },
            }
    if len(outputs) > 0:
        nodes["2"] = {
                        "id": "2",
                        "slug": "",
                        "stage": "end",
                        "title": "Outputs",
                        "params": {
                            "outputs": outputs
                        },
                        "handler": [
                            {
                                "step": None,
                                "type": "finish",
                                "condition": {
                                    "value": "output",
                                    "test_value": True,
                                    "condition_test": "=="
                                },
                                "edge_description": "=="
                            }
                        ],
                        "node_type": "KNOWLEDGE_STORE_OUTPUT",
                        "position_x": 1031.65,
                        "position_y": 66.4,
                        "description": ""
                    }
    return nodes

def output_workflow_process_graph(agents):
    tools = output_workflow_tools(agents)
    dependencies = output_workflow_dependencies(agents)
    tools_json = {"tool": {
            "id": "tool",
            "slug": "",
            "type": "KNOWLEDGE_STORE_TOOLS",
            "stage": "start",
            "title": "Tools",
            "params": {
                "tools": tools
            },
            "handler": [
                {
                    "step": "1",
                    "type": "go_to",
                    "condition": None,
                    "edge_description": ""
                }
            ],
            "position_x": -152.7,
            "position_y": 353,
            "description": ""
        }} if len(tools) > 0 else {}
    dependency_json = {"dependency": {
            "id": "dependency",
            "slug": "",
            "type": "KNOWLEDGE_STORE_DEPENDENCIES",
            "stage": "start",
            "title": "Dependencies",
            "params": {
                "dependencies": dependencies
            },
            "handler": [
                {
                    "step": "1",
                    "type": "go_to",
                    "condition": None,
                    "edge_description": ""
                }
            ],
            "position_x": -152.7,
            "position_y": 121.61,
            "description": ""
        }} if len(dependencies) > 0 else {}
    return {
        "nodes": output_workflow_agent_nodes(tools, dependencies, agents),
        **dependency_json,
        **tools_json,
    }        
            

def output_langchain_process_graph(agents):
    if not isinstance(agents, list):
        agents = [agents]

    tools = []
    tool_map = {}
    seen_tool_names = set()

    vector_stores = []
    seen_collections = set()

    tool_num = 1
    for agent in agents:
        for tool in getattr(agent, "tools", []):
            if tool.name not in seen_tool_names:
                seen_tool_names.add(tool.name)

                schema = None
                if getattr(tool, "args_schema", None):
                    schema_obj = tool.args_schema
                    if hasattr(schema_obj, "model_json_schema"):
                        schema = schema_obj.model_json_schema()

                tools.append(
                    {
                        "name": tool.name,
                        "schema": schema,
                        "returns": None,
                        "tool_num": tool_num,
                        "description": getattr(tool, "description", "")
                    }
                )
                tool_map[tool.name] = tool_num
                tool_num += 1

            fn = getattr(tool, "func", None)
            if fn and fn.__closure__:
                for cell in fn.__closure__:
                    val = cell.cell_contents
                    if type(val).__name__ in ("FairoVectorStore", "PostgresVectorStore") and val.collection_name not in seen_collections:
                        vector_stores.append(val)
                        seen_collections.add(val.collection_name)

    dependencies = []
    dependency_map = {}
    for idx, store in enumerate(vector_stores, start=1):
        dep = {
            "dependency_num": idx,
            "name": store.collection_name,
        }
        if hasattr(store, "collection_uuid"):
            dep["id"] = store.collection_uuid
        dependencies.append(dep)
        dependency_map[store.collection_name] = idx

    _agents = []
    for agent in agents:
        agent_tools = [
            tool_map[tool.name]
            for tool in getattr(agent, "tools", [])
            if tool.name in tool_map
        ]

        agent_deps = []
        for tool in getattr(agent, "tools", []):
            fn = getattr(tool, "func", None)
            if fn and fn.__closure__:
                for cell in fn.__closure__:
                    val = cell.cell_contents
                    if type(val).__name__ in ("FairoVectorStore", "PostgresVectorStore") and val.collection_name in dependency_map:
                        num = dependency_map[val.collection_name]
                        if num not in agent_deps:
                            agent_deps.append(num)

        agent_kwargs = getattr(agent, "agent_kwargs", {}) or {}
        _agents.append(
            {
                "goal": agent_kwargs.get("goal", ""),
                "name": getattr(agent, "name", "LangChain Agent"),
                "role": agent_kwargs.get("role", ""),
                "tool": agent_tools,
                "knowledge_store": agent_deps,
                "output": [],
                "trigger": {},
                "backstory": agent_kwargs.get("backstory", ""),
                "prompt": get_agent_prompt(agent),
                "prefix": agent_kwargs.get("prefix", ""),
                "suffix": agent_kwargs.get("suffix", ""),
                "schema": get_agent_schema(agent),
            }
        )

    nodes = {
        "1": {
            "id": "1",
            "slug": "",
            "stage": "middle",
            "title": "Agent Executor",
            "params": {"agents": _agents},
            "handler": [
                {
                    "step": None,
                    "type": "finish",
                    "condition": {"value": "output", "test_value": True, "condition_test": "=="},
                    "edge_description": "",
                }
            ],
            "node_type": "KNOWLEDGE_STORE_AGENT_EXECUTOR",
            "position_x": 490.24,
            "position_y": 66.4,
            "description": "",
        }
    }

    tools_json = {
        "tool": {
            "id": "tool",
            "slug": "",
            "type": "KNOWLEDGE_STORE_TOOLS",
            "stage": "start",
            "title": "Tools",
            "params": {"tools": tools},
            "handler": [
                {
                    "step": "1",
                    "type": "go_to",
                    "condition": None,
                    "edge_description": "",
                }
            ],
            "position_x": -152.7,
            "position_y": 353,
            "description": "",
        }
    } if tools else {}

    dependency_json = {
        "dependency": {
            "id": "dependency",
            "slug": "",
            "type": "KNOWLEDGE_STORE_DEPENDENCIES",
            "stage": "start",
            "title": "Dependencies",
            "params": {"dependencies": dependencies},
            "handler": [
                {
                    "step": "1",
                    "type": "go_to",
                    "condition": None,
                    "edge_description": "",
                }
            ],
            "position_x": -152.7,
            "position_y": 121.61,
            "description": "",
        }
    } if dependencies else {}

    return {
        "nodes": nodes,
        **dependency_json,
        **tools_json,
    }

def get_agent_prompt(agent) -> str:
    import inspect
    from collections import deque

    # Safe import of prompt classes – works even when LangChain is absent
    try:
        from langchain.prompts import PromptTemplate
        from langchain.prompts.chat import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
        )
        prompt_classes = (PromptTemplate, ChatPromptTemplate)
    except Exception:  # pragma: no cover
        PromptTemplate = ChatPromptTemplate = SystemMessagePromptTemplate = None
        prompt_classes = tuple()

    def _extract_prompt(val):
        """Return the underlying template string if *val* looks like a prompt."""
        # PromptTemplate
        if PromptTemplate and isinstance(val, PromptTemplate):
            return val.template

        # ChatPromptTemplate – look for a system‑message prompt first
        if ChatPromptTemplate and isinstance(val, ChatPromptTemplate):
            for msg in getattr(val, "messages", []):
                if (
                    SystemMessagePromptTemplate
                    and isinstance(msg, SystemMessagePromptTemplate)
                ):
                    tpl = getattr(msg, "prompt", None)
                    if PromptTemplate and isinstance(tpl, PromptTemplate):
                        return tpl.template
            # Fallback – some ChatPromptTemplates expose `.template`
            if hasattr(val, "template"):
                return getattr(val, "template")

        # Raw string prompt
        if isinstance(val, str):
            return val

        return None

    # 0. Unwrap AgentExecutor‑like containers
    runnable_agent = getattr(agent, "agent", None) or agent

    # 1. Quick path via agent_kwargs
    agent_kwargs = getattr(runnable_agent, "agent_kwargs", {}) or {}
    for key in ("system_message", "prefix", "prompt"):
        if agent_kwargs.get(key):
            return agent_kwargs[key]

    # 2. Breadth‑first search through common nesting patterns
    search_queue = deque([runnable_agent])
    visited_ids = set()

    candidate_attrs = (
        "prompt",
        "llm_chain",
        "chain",
        "default_chain",
        "router_chain",
        "destination_chains",
        "executor_chain",
        "retriever_chain",
        "runnable",
        "middle",
    )

    while search_queue:
        current = search_queue.popleft()
        if id(current) in visited_ids:
            continue
        visited_ids.add(id(current))

        # The object itself might be a prompt
        extracted = _extract_prompt(current)
        if extracted:
            return extracted

        # Explore child attributes
        for attr in candidate_attrs:
            if not hasattr(current, attr):
                continue
            child = getattr(current, attr)

            # Direct extraction
            extracted = _extract_prompt(child)
            if extracted:
                return extracted

            # Queue nested structures for further exploration
            if isinstance(child, (list, tuple, set)):
                search_queue.extend(child)
            elif isinstance(child, dict):
                search_queue.extend(child.values())
            else:
                # Ignore primitives, strings, callables, prompt classes themselves
                if (
                    not isinstance(child, (*prompt_classes, str))
                    and not inspect.isroutine(child)
                ):
                    search_queue.append(child)

    # Nothing found – return empty string
    return ""


def get_agent_schema(agent):
    """
    Returns a JSON schema dict when available, otherwise None.
    Checks common attributes across SimpleAgent and LangChain agents.
    """
    candidate_attrs = ("args_schema", "input_schema", "agent_schema", "schema")
    for attr in candidate_attrs:
        obj = getattr(agent, attr, None)
        if obj is None:
            continue
        try:
            if isinstance(obj, dict):
                return obj
            if hasattr(obj, "model_json_schema") and callable(getattr(obj, "model_json_schema")):
                return obj.model_json_schema()
            if hasattr(obj, "schema") and callable(getattr(obj, "schema")):
                return obj.schema()
        except Exception as e:
            pass

    inner = getattr(agent, "agent", None)
    if inner is not None and inner is not agent:
        return get_agent_schema(inner)

    return None