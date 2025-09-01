from typing import Optional

import openai

from dtx_models.prompts import (
    BaseMultiTurnConversation,
    RoleType,
    Turn,
)
from dtx_models.providers.openai import OpenaiProvider, OpenaiProviderConfig
from dtx_models.template.prompts.base import BasePromptTemplateRepo

from .base import BaseOpenAICompatibleAgent

""" 
id: openai
config:
  model: gpt-4o
  task: generation
  endpoint: https://api.openai.com/v1
  params:
    temperature: 0.7
    top_k: 40
    top_p: 0.9
    repeat_penalty: 1.1
    max_tokens: 512
    num_return_sequences: 1
    extra_params:
      stop: ["###", "User:"]
"""

""" 
id: openai
config:
  model: gpt-4o
"""


class OpenAIAgent(BaseOpenAICompatibleAgent):
    def __init__(
        self,
        provider: OpenaiProvider,
        client: Optional[openai.OpenAI] = None,
        prompt_template: BasePromptTemplateRepo = None,
    ):
        super().__init__(
            provider=provider,
            client=client,
            prompt_template=prompt_template,
        )


if __name__ == "__main__":
    from dtx_models.providers.openai import (
        OpenaiProvider,
        OpenaiProviderConfig,
        ProviderParams,
    )
    from dtx.plugins.providers.openai.agent import OpenAIAgent

    provider_config = OpenaiProviderConfig(
        model="gpt-4o",
        endpoint="https://api.openai.com/v1",
        params=ProviderParams(
            temperature=0.7,
        ),
    )

    provider = OpenaiProvider(config=provider_config)
    agent = OpenAIAgent(provider)

    conversation = BaseMultiTurnConversation(
        turns=[
            Turn(role=RoleType.SYSTEM, message="You are a helpful assistant."),
            Turn(role=RoleType.USER, message="Hi, who won the World Cup in 2022?"),
            Turn(role=RoleType.USER, message="Where was it held?"),
        ],
    )

    response = agent.converse(conversation)
    print(response)
