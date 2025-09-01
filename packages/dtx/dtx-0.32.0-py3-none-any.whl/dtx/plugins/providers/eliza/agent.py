import re

import requests

from dtx.core.exceptions.agents import RemoteResponseError
from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponseBuilder,
)

from ..base.agent import BaseAgent

class ElizaAgent(BaseAgent):
    def __init__(self, base_url, agent_name=None):
        self.base_url = base_url
        self.agent_name = agent_name
        self.agent_id = None
        self._parse_agent_from_url()
        self._initialize_agent()

    def _parse_agent_from_url(self):
        """
        Checks if the base_url contains "/agent/<agent_name>".
        If found, extracts the agent name and updates the base_url.
        """
        pattern = r"/agent/([^/]+)"
        match = re.search(pattern, self.base_url)
        if match:
            self.agent_name = match.group(1)
            self.base_url = re.sub(pattern, "", self.base_url)

    def _initialize_agent(self):
        """
        Fetches the list of agents from the `/agents` endpoint and sets the agent ID.
        If `agent_name` is None, selects the first agent from the list.
        """
        try:
            # Fetch agents
            response = requests.get(f"{self.base_url}/agents")
            if response.status_code == 200:
                agents_data = response.json()
                agents = agents_data.get("agents", [])

                if not agents:
                    raise ValueError("No agents found in the response.")

                if self.agent_name:
                    # Find the agent by name
                    for agent in agents:
                        if agent["name"] == self.agent_name:
                            self.agent_id = agent["id"]
                            break
                    else:
                        raise ValueError(
                            f"Agent with name '{self.agent_name}' not found."
                        )
                else:
                    # Pick the first agent
                    self.agent_id = agents[0]["id"]
                    self.agent_name = agents[0]["name"]
            else:
                raise ValueError(f"Failed to fetch agents: {response.status_code}")
        except requests.RequestException as e:
            raise ValueError(f"An error occurred while fetching agents: {str(e)}")

    def generate(self, prompt) -> str:
        """
        Sends a POST request to the upstream server with the given prompt and agent ID.

        Args:
            prompt (str): The text prompt to send.

        Returns:
            str: The response text from the server.
        """
        if not self.agent_id:
            return "Agent ID is not initialized."

        # Define the request payload as form-data
        payload = {"text": prompt, "user": self.agent_name}

        try:
            # Construct the endpoint for the selected agent
            endpoint = f"{self.base_url}/{self.agent_id}/message"
            response = requests.post(endpoint, data=payload)

            if response.status_code == 200:
                response_json = response.json()
                if response_json and isinstance(response_json, list):
                    return response_json[0].get("text", "Empty Response from the Agent")
                else:
                    raise RemoteResponseError(
                        "Invalid response format received from server. Expected Json Format"
                    )
            else:
                raise RemoteResponseError(
                    f"Invalid response code received from server: Status Code {response.status_code}"
                )
        except requests.RequestException as e:
            raise RemoteResponseError(
                f"An error occurred while sending the request: {str(e)}"
            )

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        """
        Perform a multi-turn conversation with the agent.
        Ensures a USER -> ASSISTANT -> USER -> ASSISTANT sequence.
        If an ASSISTANT turn is missing, it is inserted by copying the preceding USER turn.
        """

        builder = BaseMultiTurnResponseBuilder()

        if prompt.has_system_turn():
            builder.add_turn(prompt.get_system_turn())

        for turn in prompt.get_user_turns():
            response = self.generate(turn.message)
            builder.add_prompt_and_response(turn.message, response)
            builder.add_prompt_attributes(prompt)

        return builder.build()
