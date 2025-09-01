from typing import Any, Dict, List, Optional

from gradio_client import Client  # Gradio API client
from jinja2 import Template  # Jinja2 for template rendering

from dtx.core import logging
from dtx_models.providers.gradio import (
    GradioProvider,
    GradioProviderApi,
    GradioProviderApiParam,
)

from .parsers.response.response_parser import GradioResponseParser

# Configure logging
logger = logging.getLogger(__name__)


class GradioProviderClient:
    """
    A client for interacting with a Gradio API provider.
    """

    def __init__(self, url: str = None, client: Client = None):
        """
        Initializes the client with a Gradio API provider configuration.

        :param provider: The GradioProvider instance containing API details.
        """
        self.client = client or Client(url)  # Initialize Gradio Client
        logger.debug("GradioProviderClient initialized with URL: %s", url)

    def generate(
        self, api: GradioProviderApi, prompt: str, vars: Dict[str, Any]
    ) -> Any:
        logger.info("Starting response generation process")
        logger.debug("Prompt: %s", prompt)
        logger.debug("Variables for template rendering: %s", vars)

        response_parser = GradioResponseParser(api.transform_response)
        raw_response = self.generate_raw(api=api, vars=vars)
        parsed_response = response_parser.parse(prompt=prompt, response=raw_response)

        logger.info("Response generation completed")
        logger.debug("Parsed Response: %s", parsed_response)
        return parsed_response

    def generate_raw(self, api: GradioProviderApi, vars: Dict[str, Any]) -> Any:
        """
        Calls the first available Gradio API with provided parameters after rendering Jinja templates.
        """
        logger.info("Calling Gradio API at path: %s", api.path)
        request_params = self._render_jinja_templates(api.params, vars)

        logger.debug("Request parameters after Jinja rendering: %s", request_params)

        try:
            response = self.client.predict(**request_params, api_name=api.path)
            logger.info("API call successful")
            logger.debug("Raw API Response: %s", response)
            return response
        except Exception as e:
            logger.error("Failed to generate response from %s: %s", api.path, e)
            raise RuntimeError("Generation error: %s" % e)

    def _render_jinja_templates(
        self,
        api_params: Optional[List[GradioProviderApiParam]],
        user_params: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Renders Jinja templates in API parameters using user-supplied values.
        """
        logger.debug("Rendering Jinja templates for API parameters")
        final_params = {}

        for param in api_params or []:
            value = param.value
            logger.debug("Processing param: %s with value: %s", param.name, value)
            if isinstance(value, str) and "{{" in value and "}}" in value:
                try:
                    template = Template(value)
                    value = template.render(user_params)
                    logger.debug(
                        "Rendered template for param '%s': %s", param.name, value
                    )
                except Exception as e:
                    logger.warning(
                        "Jinja template rendering failed for param '%s': %s",
                        param.name,
                        e,
                    )
            final_params[param.name] = value

        logger.debug("Final rendered parameters: %s", final_params)
        return final_params


if __name__ == "__main__":
    from dtx_models.providers.gradio import GradioProviderConfig

    provider_config = GradioProviderConfig(
        url="ibm-granite/granite-3.1-8b-instruct",
        apis=[GradioProviderApi(
            path="/chat",
            params=[
                GradioProviderApiParam(name="message", value="{{prompt}}"),
                GradioProviderApiParam(name="param_2", value=0.7),
                GradioProviderApiParam(name="param_3", value=1.05),
                GradioProviderApiParam(name="param_4", value=0.85),
                GradioProviderApiParam(name="param_5", value=50),
                GradioProviderApiParam(name="param_6", value=1024),
            ],
        )],
    )

    provider = GradioProvider(config=provider_config)
    client = GradioProviderClient(provider_config.url)
    logger.info("Testing raw generation with test prompt")
    print(client.generate_raw(api=provider_config.apis[0], vars={"prompt": "[[FUZZ]]"}))
