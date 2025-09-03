import inspect
from typing import Callable, Dict, Any, Type, List
from pydantic import BaseModel

_SKILL_METADATA_KEY = "__articom_skill_metadata__"
_TOOL_METADATA_KEY = "__articom_tool_metadata__"

class ArticomSkill:
    """
    A class decorator to define a skill and its metadata.
    It discovers all methods decorated with @Tool.
    """
    def __init__(self, name: str, version: str, author: str, description: str):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.tools: Dict[str, Dict[str, Any]] = {}

    def __call__(self, cls: Type[Any]) -> Type[Any]:
        # Store metadata on the class for later retrieval
        setattr(cls, _SKILL_METADATA_KEY, self)
        
        # Discover tools
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, _TOOL_METADATA_KEY):
                tool_metadata = getattr(method, _TOOL_METADATA_KEY)
                
                # Extract type hints for automatic schema generation
                sig = inspect.signature(method)
                params = list(sig.parameters.values())
                
                if len(params) != 2: # Expects (self, data: BaseModel)
                    raise TypeError(f"Tool method '{name}' must have exactly two arguments: self and a Pydantic model for data.")
                
                input_model = params[1].annotation
                output_model = sig.return_annotation

                if not issubclass(input_model, BaseModel):
                     raise TypeError(f"Input type for tool '{name}' must be a Pydantic BaseModel.")
                if not issubclass(output_model, BaseModel):
                    raise TypeError(f"Return type for tool '{name}' must be a Pydantic BaseModel.")

                tool_metadata['input_schema'] = input_model.model_json_schema()
                tool_metadata['output_schema'] = output_model.model_json_schema()
                tool_metadata['handler'] = method
                
                self.tools[tool_metadata['name']] = tool_metadata
        
        # Add instance methods to the class for easy access
        skill_metadata = self  # Capture the metadata instance
        
        cls.get_skill_metadata = lambda instance: {
            "name": skill_metadata.name,
            "version": skill_metadata.version,
            "author": skill_metadata.author,
            "description": skill_metadata.description,
        }
        
        cls.get_tools = lambda instance: skill_metadata.tools
        
        cls.generate_manifest = lambda instance: skill_metadata._generate_manifest_method()
        
        cls._generate_manifest = skill_metadata._generate_manifest_method
        
        return cls
        
    def _generate_manifest_method(self) -> Dict[str, Any]:
        """Generates the skill.json manifest."""
        manifest_tools: List[Dict[str, Any]] = []
        for tool_name, tool_data in self.tools.items():
            manifest_tools.append({
                "name": tool_data['name'],
                "description": tool_data['description'],
                "input_schema": tool_data['input_schema'],
                "output_schema": tool_data['output_schema'],
            })
            
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "tools": manifest_tools
        }


def Tool(name: str, description: str) -> Callable:
    """A function decorator to define a tool within a skill."""
    def decorator(func: Callable) -> Callable:
        setattr(func, _TOOL_METADATA_KEY, {"name": name, "description": description})
        return func
    return decorator
