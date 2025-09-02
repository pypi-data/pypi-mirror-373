from gllm_agents.tools.bosa_connector import BOSAConnector as BOSAConnector
from gllm_agents.tools.bosa_tools_interface import BosaToolInterface as BosaToolInterface
from gllm_agents.tools.constants import BOSA_API_BASE_URL as BOSA_API_BASE_URL, BOSA_API_KEY as BOSA_API_KEY
from langchain_core.callbacks import AsyncCallbackManagerForToolRun as AsyncCallbackManagerForToolRun

class BaseBosaTool(BosaToolInterface):
    """Base class for tools with BOSA Connector integration."""
    def __init__(self, **kwargs) -> None:
        """Initialize the BaseBosaTool.

        This method calls the _init_bosa_connector method to initialize the BosaConnector.
        """
