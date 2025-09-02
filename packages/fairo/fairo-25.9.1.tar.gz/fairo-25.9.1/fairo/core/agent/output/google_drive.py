from .base_output import BaseOutput

class GoogleDriveOutput(BaseOutput):
    name = "Google Drive Output"
    description = """
        This agent node handles writing files directly to a specified Google Drive folder.
        Ideal for saving processed results, logs, or exported reports in cloud storage.
    """
    file_format = "txt"
    def __init__(self, destination, source, file_format = "txt"):
        self.file_format = file_format
        super().__init__(
                name=self.name, 
                description=self.description, 
                destination=destination,
                source=source,
            )
    def execute(self, final_answer: str):
        """
            @TODO Implement Output
        """
        pass


class KnowledgeStoreOutput(BaseOutput):
    name = "Knowledge Store Output"
    description = """
            This agent node handles chunking and saving embeddings to a knowledge store. 
        """

    def __init__(self, destination, source):
        super().__init__(
            name=self.name,
            description=self.description,
            destination=destination,
            source=source,
        )

    def execute(self, final_answer: str):
        """
            @TODO Implement Output
        """
        pass

class DatabricksNotebookOutput(BaseOutput):
    name = "Databricks Notebook Output"
    description = """
        This agent node handles writing files directly to a specified Databricks notebook.  
    """
    file_format = "sql"

    def __init__(self, destination, source, file_format="txt"):
        self.file_format = file_format
        super().__init__(
            name=self.name,
            description=self.description,
            destination=destination,
            source=source,
        )

    def execute(self, final_answer: str):
        """
            @TODO Implement Output
        """
        pass