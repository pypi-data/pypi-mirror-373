import abc
from abc import ABC, abstractmethod
from gllm_agents.tools.bosa_connector import BOSAConnector as BOSAConnector
from pydantic import BaseModel as BaseModel

class BosaToolInterface(ABC, metaclass=abc.ABCMeta):
    """Interface for BOSA tools.

    Defines the abstract base class for tools that agents can use.

    Attributes:
        name (str): The name of the tool.
        description (Optional[str]): The description of the tool.
        args_schema (Optional[Type[BaseModel]]): The schema for the tool arguments.
        _bosa_connector (Optional[BOSAConnector]): The BosaConnector instance.
    """
    name: str
    description: str | None
    args_schema: type[BaseModel] | None
    @abstractmethod
    def __init__(self):
        """Initialize the BosaToolInterface.

        This method should be implemented by subclasses to define the tool's
        initialization logic. The _init_bosa_connector should be called here.
        """
