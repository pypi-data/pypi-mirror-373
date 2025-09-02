from fairo.core.agent.tools.utils import FlowOutput

class BaseOutput:
    name: str = ""
    source: str = ""
    destination: str = ""
    description: str = ""
    
    def __init__(self, name, source, destination, description):
        self.name = name
        self.source = source
        self.destination = destination
        self.description = description
        
    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "destination": self.destination,
            "description": self.description,
        }
        
    def execute(self, final_answer: str):
        raise NotImplementedError("Subclasses must implement execute()")
    
    def to_fairo_output(self):
        return FlowOutput(node_name=self.name, source=self.source, destination=self.destination).to_dict()