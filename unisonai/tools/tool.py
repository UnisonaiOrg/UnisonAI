from abc import abstractmethod
class Field:
    def __init__(self, name: str, description: str, default_value=None, required: bool = True):
        self.name = name
        self.description = description
        self.default_value = default_value
        self.required = required

    def format(self):  # Method to convert Field to dictionary
        return f"""
     {self.name}:
       - description: {self.description}
       - default_value: {self.default_value}
       - required: {self.required}
        """

class BaseTool:
    name: str
    description: str
    params: list[Field] # Now a list of Field objects

    @abstractmethod
    def _run(**kwargs):
        raise NotImplementedError("Please Implement the Logic in _run function")