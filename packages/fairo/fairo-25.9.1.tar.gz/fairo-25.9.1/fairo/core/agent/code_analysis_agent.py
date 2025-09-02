from fairo.core.agent.base_agent import SimpleAgent
from fairo.core.agent.tools.code_analysis import CodeAnalysisTool

class CodeAnalysis:
    name = "Code Analysis Agent"
    code_analyse_tool = CodeAnalysisTool()
    def __init__(self, agent_name="Code Analysis Agent", verbose: bool = False, llm=None, tools=None):
        self.agent = SimpleAgent(
            agent_name=agent_name,
            role="Code Analyst",
            goal="Analyze code files and provide insightful summaries for loading into Knowledge Store to help AI "
                 "Agents find relevant code blocks.",
            backstory="""You are an expert code analyst with deep understanding of software 
            engineering and programming languages. You excel at reading code, identifying patterns, 
            and explaining code in clear terms. You understand how different components interact
            and can provide concise, informative summaries of code functionality.
            
            You use these skills to help structure code summaries that will be loaded into Knowledge Stores designed
            to help future language-model-based pipelined retrieve relevant context. 
            """,
            verbose=verbose,
            llm=llm,
            tools=tools or [self.code_analyse_tool],
        )