from abc import ABC, abstractmethod
from typing import Dict, List

from  dtx.plugins.providers.base.agent import BaseAgent

from dtx_models.prompts import RoleType
from dtx_models.prompts import (
    BaseMultiTurnConversation,
    Turn,
)

class BaseTargetModel(ABC):
    """
    Abstract base class for any target model.

    A target model is expected to maintain a history of messages and
    generate responses to attacker inputs.
    """

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    @abstractmethod
    def generate_response(self, attacker_message: str) -> str:
        """Generate a response given an attacker message."""
        pass


class BaseCustomTargetModel(ABC):
    """
    Abstract base class for custom/manual target models.

    Provides a default implementation for updating message history,
    but requires subclasses to implement fetch_response().
    """

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def generate_response(self, attacker_message: str) -> str:
        """
        Handle attacker message, update conversation history,
        and fetch a manual/custom response.
        """
        if not self.messages:
            self.messages = [{"role": "user", "content": attacker_message}]
        else:
            self.messages.append({"role": "user", "content": attacker_message})

        response = self.fetch_response(self.messages)
        self.messages.append({"role": "assistant", "content": response})

        return response

    @abstractmethod
    def fetch_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Abstract method to fetch a custom/manual response
        based on the conversation history.
        """
        pass


class AgentTargetModel(BaseCustomTargetModel):
    """
    Target model that wraps around a BaseAgent instance.
    
    It uses the agent's converse() method to generate responses.
    """

    def __init__(self, agent: BaseAgent):
        super().__init__()
        self.agent = agent

    def fetch_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Fetch a response from the wrapped BaseAgent by performing multi-turn conversation.
        """
        # Convert messages into BaseMultiTurnConversation instance
        conversation = BaseMultiTurnConversation(turns=[
            Turn(role=RoleType(role_dict["role"].upper()), message=role_dict["content"])
            for role_dict in messages
        ])
        
        # Use the agent's converse method
        response_conversation = self.agent.converse(conversation)
        
        # Return the last assistant response
        return response_conversation.last_assistant_response()


class TargetModelSessionFactory:
    """
    Factory for creating new TargetModel sessions based on the provider.

    Supports dynamic registration of providers and their corresponding classes.
    """

    def __init__(self, agent: BaseAgent):
        """
        Initialize the factory with the given configuration.

        """
        self._agent = agent


    def get_session(self) -> BaseTargetModel:
        """
        Create and return a new session for the configured provider.

        Returns:
            An instance of the corresponding model class.

        Raises:
            ValueError: If no class is registered for the provider.
        """

        return AgentTargetModel(agent=self._agent)
