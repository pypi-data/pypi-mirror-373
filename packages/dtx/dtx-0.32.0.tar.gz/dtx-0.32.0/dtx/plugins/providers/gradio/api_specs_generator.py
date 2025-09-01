from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from gradio_client import Client

from dtx.core import logging
from dtx_models.providers.gradio import (
    GradioApiSignatureParam,
    GradioApiSpec,
    GradioApiSpecs,
)


class GradioApiSpecGenerator:
    """
    Generates Gradio API specifications by extracting endpoint details from a Gradio-based service.
    """

    def __init__(self, url: str):
        """
        Initializes the generator with the given Gradio API base URL.

        :param url: The base URL of the Gradio API service.
        """
        self.url = self.normalize_url(url)
        self.client = self._initialize_client()

    def _initialize_client(self) -> Optional[Client]:
        """
        Attempts to create a Gradio client instance.

        :return: A Client object if successful, otherwise None.
        """
        try:
            logging.debug(f"Initializing Gradio client for URL: {self.url}")
            return Client(self.url, verbose=False)
        except Exception as ex:
            logging.error(f"Failed to initialize Gradio client: {ex}")
            return None

    def generate_api_specs(self) -> Optional[GradioApiSpecs]:
        """
        Generates Gradio API specifications by fetching and parsing API metadata.

        :return: A GradioApiSpecs object containing the API details.
        """
        if not self.client:
            logging.error("Gradio client is not initialized.")
            return None

        api_specs = []
        for api_name, parameters, _ in self._enumerate_api_specs():
            api_spec = GradioApiSpec(
                api_name=api_name,
                params=[
                    GradioApiSignatureParam(
                        name=param["name"],
                        has_default_value=param["has_default_value"],
                        default_value=param["default_value"],
                        python_type=param["python_type"],
                    )
                    for param in parameters
                ],
                # response=response_format,  # Store response format
            )
            api_specs.append(api_spec)

        return GradioApiSpecs(apis=api_specs)

    def _enumerate_api_specs(self) -> List[Tuple[str, List[dict], Dict[str, Any]]]:
        """
        Retrieves and parses API endpoint specifications, including response formats.

        :return: A list of tuples containing API names, parameter details, and response format.
        """
        try:
            named_endpoints_dict = self.client.view_api(
                print_info=False, return_format="dict"
            )["named_endpoints"]
            return list(self._parse_named_endpoints(named_endpoints_dict))
        except Exception as ex:
            logging.error(f"Error while fetching API specs: {ex}")
            return []

    def _parse_named_endpoints(
        self, named_endpoints_dict
    ) -> List[Tuple[str, List[dict], Dict[str, Any]]]:
        """
        Parses named API endpoints to extract parameters and response format.

        :param named_endpoints_dict: Dictionary containing named API endpoints.
        :return: A generator of tuples containing API names, parameter specifications, and response formats.
        """
        for name, details in named_endpoints_dict.items():
            if details.get("parameters") and details.get("returns"):
                yield (
                    name,
                    self._extract_api_info(details["parameters"]),
                    details["returns"],  # API response format
                )

    def _extract_api_info(self, data: List[dict]) -> List[dict]:
        """
        Extracts parameter information from API metadata.

        :param data: A list of parameter metadata dictionaries.
        :return: A list of dictionaries representing extracted parameter details.
        """
        parameters = []
        for param in data:
            parameters.append(
                {
                    "name": param["parameter_name"],
                    "has_default_value": param["parameter_has_default"],
                    "default_value": param["parameter_default"],
                    "python_type": param["python_type"]["type"],
                }
            )
        return parameters

    def normalize_url(self, url: str) -> str:
        """
        Normalizes a Gradio URL, handling special cases such as Hugging Face Spaces.

        :param url: The URL to normalize.
        :return: The normalized URL or a Hugging Face space identifier if applicable.
        """
        hf_space_name = self._extract_hugging_face_space_name(url)
        return hf_space_name if hf_space_name else url

    def _extract_hugging_face_space_name(self, url: str) -> str:
        """
        Extracts the Hugging Face Space name from a URL.

        :param url: The URL to parse.
        :return: The Hugging Face Space identifier if applicable, otherwise an empty string.
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_segments = parsed_url.path.strip("/").split("/")

        if domain == "huggingface.co" and len(path_segments) >= 2:
            orgname, app = path_segments[-2], path_segments[-1]
            return f"{orgname}/{app}"
        return ""


# Example usage
if __name__ == "__main__":
    from dtx.plugins.providers.gradio.api_specs_generator import (
        GradioApiSpecGenerator,
    )

    gradio_url = "https://example.gradio.app"
    generator = GradioApiSpecGenerator(gradio_url)
    api_specs = generator.generate_api_specs()

    if api_specs:
        print(api_specs.json(indent=2))
    else:
        print("Failed to generate API specifications.")
