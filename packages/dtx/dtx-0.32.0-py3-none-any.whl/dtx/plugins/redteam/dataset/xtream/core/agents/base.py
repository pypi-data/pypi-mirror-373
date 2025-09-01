from dtx.core import logging

import os
from random import uniform
from time import sleep
from typing import Dict, List, Optional, Tuple, Union

from openai import OpenAI


class APICallError(Exception):
    """Custom exception for API call failures"""

    pass


class BaseAgent:
    """Base agent for OpenAI and OpenRouter."""

    def __init__(self, config: Dict):
        self.config = config
        self.provider = config["provider"]
        self.max_retries = config.get("max_retries", 3)
        self.api_key = config.get("api_key") or None
        try:
            if self.provider == "openai":
                # if any(f"o{i}" in config["model"] for i in range(1, 6)):
                self.client = OpenAI(api_key=self.api_key)
                self.model = config["model"]
                # else:
                # self.client = ai.Client(api_key=self.api_key)
                # self.model = f"{self.provider}:{config['model']}"
            elif self.provider == "openrouter":
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY", ""),
                )
                self.model = config["model"]
                self.http_referer = config.get("http_referer")
                self.x_title = config.get("x_title")
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            raise APICallError(f"Error initializing {self.provider} client: {str(e)}")

    def call_api(
        self,
        messages: List[Dict],
        temperature: float = None,
        response_format: Optional[Dict] = None,
        return_messages: bool = False,
    ) -> Union[str, Tuple[str, List[Dict]]]:
        temperature = temperature or self.config["temperature"]
        # print(
        #     f"{Fore.GREEN}Model is {self.model}, temperature is {temperature}{Style.RESET_ALL}"
        # )

        provider_configs = {
            "openai": {"base_delay": 1, "retry_delay": 3, "jitter": 1},
            "openrouter": {"base_delay": 1, "retry_delay": 3, "jitter": 1},
        }

        config = provider_configs[self.provider]

        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = config["retry_delay"] * attempt + uniform(
                        0, config["jitter"]
                    )
                    print(
                        f"\nRetry attempt {attempt + 1}/{self.max_retries}. Waiting {delay:.2f}s..."
                    )
                    sleep(delay)

                if self.provider == "openai":
                    if any(f"o{i}" in self.model for i in range(1, 6)):
                        response = self._call_openai_o1_model(messages)
                    else:
                        api_params = {
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature,
                        }
                        if response_format:
                            api_params["response_format"] = response_format

                        response = self.client.chat.completions.create(**api_params)
                        response = response.choices[0].message.content
                elif self.provider == "openrouter":
                    extra_headers = {}
                    if self.http_referer:
                        extra_headers["HTTP-Referer"] = self.http_referer
                    if self.x_title:
                        extra_headers["X-Title"] = self.x_title

                    api_params = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                    }
                    if response_format:
                        api_params["response_format"] = response_format
                    if extra_headers:
                        api_params["extra_headers"] = extra_headers

                    response = self.client.chat.completions.create(**api_params)
                    response = response.choices[0].message.content

                return (response, messages) if return_messages else response

            except Exception as e:
                error_msg = str(e)
                logging.error(
                    f"BaseAgent: API call failed for {self.provider} (Attempt {attempt + 1}/{self.max_retries})",
                    exc_info=e,
                )

                if attempt == self.max_retries - 1:
                    raise APICallError(
                        f"BaseAgent: Failed to get response from {self.provider}: {error_msg}"
                    )
                continue

    def _call_openai_o1_model(self, messages: List[Dict]) -> str:
        """Handle OpenAI o1 models (special handling)."""
        print(
            "\nWarning: OpenAI o1 model only accepts user messages. System messages will be ignored."
        )

        formatted_messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": messages[-1]["content"]}],
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model, messages=formatted_messages
        )
        return response.choices[0].message.content


def main():
    """Test OpenAI and OpenRouter models."""
    test_configs = [
        {
            "provider": "openai",
            "model": "gpt-4o",
            "max_retries": 3,
            "temperature": 0,
        },
        {
            "provider": "openai",
            "model": "o1-preview",
            "max_retries": 3,
            "temperature": 0,
        },
        {
            "provider": "openrouter",
            "model": "deepseek/deepseek-r1",
            "max_retries": 3,
            "temperature": 0,
        },
    ]

    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    for config in test_configs:
        print("\n" + "=" * 50)
        print(f"Testing {config['provider']} with model {config['model']}")
        print("=" * 50)

        try:
            agent = BaseAgent(config)
            response, messages = agent.call_api(
                messages=test_messages,
                temperature=config["temperature"],
                return_messages=True,
            )
            print(f"\nMessages sent: {messages}")
            print(f"\nResponse: {response}")
            print("\nTest completed successfully!")

        except Exception as e:
            print(f"Error testing configuration: {str(e)}")

        print("-" * 50)


if __name__ == "__main__":
    main()
