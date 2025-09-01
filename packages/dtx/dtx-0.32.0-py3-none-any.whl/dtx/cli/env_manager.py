import importlib.resources as pkg_resources
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from dotenv import load_dotenv

from dtx.core import logging


class EnvValidator:
    logger = logging.getLogger("EnvValidator")

    # Dataset environment variable requirements
    DATASET_ENV_MAP = {
        "STINGRAY": {"all": [], "any": []},
        "STARGAZER": {"all": [], "any": ["OPENAI_API_KEY", "DETOXIO_API_KEY"]},
        "HF_BEAVERTAILS": {"all": [], "any": []},
        "HF_HACKAPROMPT": {"all": [], "any": []},
        "HF_JAILBREAKBENCH": {"all": [], "any": []},
        "HF_SAFEMTDATA": {"all": [], "any": []},
        "HF_FLIPGUARDDATA": {"all": [], "any": []},
        "HF_JAILBREAKV": {"all": [], "any": []},
        "HF_LMSYS": {"all": ["HF_TOKEN"], "any": []},
        "HF_AISAFETY": {"all": [], "any": []},
        "HF_AIRBENCH": {"all": [], "any": []},
    }

    # Eval environment variable requirements
    EVAL_ENV_MAP = {
        "any": {"all": [], "any": []},
        "keyword": {"all": [], "any": []},
        "jsonpath": {"all": [], "any": []},
        "ibm": {"all": [], "any": []},
        "ibm38": {"all": [], "any": []},
        "ibm125": {"all": [], "any": []},
        "openai": {"all": ["OPENAI_API_KEY"], "any": []},
        "ollama": {"all": [], "any": []},
        "llamaguard": {"all": [], "any": []},
    }

    @classmethod
    def validate(cls, dataset: str = None, eval_name: str = None):
        missing_vars = set()
        any_var_missing = []

        if dataset:
            dataset_upper = dataset.upper()
            dataset_envs = cls.DATASET_ENV_MAP.get(
                dataset_upper, {"all": [], "any": []}
            )
            cls.logger.info(
                f"🔍 Checking env vars for dataset '{dataset_upper}': {dataset_envs}"
            )

            missing_vars.update(cls._check_all(dataset_envs["all"]))
            if dataset_envs["any"] and not cls._check_any(dataset_envs["any"]):
                any_var_missing.append(
                    f"Dataset '{dataset_upper}' requires at least one of: {', '.join(dataset_envs['any'])}"
                )

        if eval_name:
            eval_name_lower = eval_name.lower()
            eval_envs = cls.EVAL_ENV_MAP.get(eval_name_lower, {"all": [], "any": []})
            cls.logger.info(
                f"🔍 Checking env vars for eval '{eval_name_lower}': {eval_envs}"
            )

            missing_vars.update(cls._check_all(eval_envs["all"]))
            if eval_envs["any"] and not cls._check_any(eval_envs["any"]):
                any_var_missing.append(
                    f"Eval '{eval_name_lower}' requires at least one of: {', '.join(eval_envs['any'])}"
                )

        if missing_vars or any_var_missing:
            message = []
            if missing_vars:
                message.append(
                    f"🚨 Missing environment variables: {', '.join(sorted(missing_vars))}"
                )
            if any_var_missing:
                message.append("🚨 " + " | ".join(any_var_missing))

            # 🔍 Check for .env file
            env_file = cls._find_env_file()
            if env_file:
                message.append(
                    f"\n💡 You can update your environment variables in: {env_file}"
                )
            else:
                message.append(
                    "\n💡 Consider creating a .env file to store environment variables."
                )

            raise EnvironmentError("\n".join(message))

        cls.logger.info("✅ Environment check passed.")

    @staticmethod
    def _check_all(vars_list):
        return {var for var in vars_list if not os.getenv(var)}

    @staticmethod
    def _check_any(vars_list):
        return any(os.getenv(var) for var in vars_list)

    @staticmethod
    def _find_env_file():
        possible_paths = [
            os.path.join(os.getcwd(), ".env"),
            os.path.join(str(Path.home()), ".dtx", ".env"),
            os.path.join(os.getcwd(), "config", ".env"),
        ]
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        return None


class EnvTemplateManager:
    logger = logging.getLogger("EnvTemplateManager")

    def __init__(
        self,
        base_dir: str,
        package_name: str = "dtx",
        env_filename: str = ".env",
        template_filename: str = "env.template",
    ):
        self.package_name = package_name
        self.env_filename = env_filename
        self.template_filename = template_filename
        self.env_path = Path(base_dir) / self.env_filename

    def ensure_env_file(self):
        if self.env_path.exists():
            self.logger.info(
                f"'{self.env_filename}' file already exists at: {self.env_path}"
            )
            return

        self.logger.warning(
            f"'{self.env_filename}' file not found. Attempting to create from template..."
        )

        template_content = self.locate_template_content()

        if not template_content:
            self.logger.error(
                f"Could not find {self.template_filename} in any known locations."
            )
            self.logger.error(
                "Please create a '.env' file manually with required environment variables."
            )
            return

        self.write_env_file(template_content)
        self.logger.info(f"'{self.env_filename}' file created at: {self.env_path}")
        self.logger.info(
            "Please update the '.env' file with your environment variables before running again."
        )

    def locate_template_content(self) -> Optional[str]:
        strategies = [
            self._from_local_directory,
            self._from_script_directory,
            self._from_package_resources,
        ]

        for strategy in strategies:
            content = strategy()
            if content:
                return content
        return None

    def _from_local_directory(self) -> Optional[str]:
        path = Path.cwd() / self.template_filename
        if path.exists():
            self.logger.debug(f"Found template in current working directory: {path}")
            return path.read_text()
        return None

    def _from_script_directory(self) -> Optional[str]:
        path = Path(__file__).parent / self.template_filename
        if path.exists():
            self.logger.debug(f"Found template in script directory: {path}")
            return path.read_text()
        return None

    def _from_package_resources(self) -> Optional[str]:
        try:
            with pkg_resources.open_text(
                self.package_name, self.template_filename
            ) as template_file:
                self.logger.debug(
                    f"Found template in package resources: {self.package_name}/{self.template_filename}"
                )
                return template_file.read()
        except (FileNotFoundError, ModuleNotFoundErrorError) as e:
            self.logger.debug(f"Template not found in package resources: {e}")
            return None

    def write_env_file(self, content: str):
        with open(self.env_path, "w") as env_file:
            env_file.write(content)
        self.logger.warning(
            f"Template content written to: {self.env_path}. Manually update the .env file to specify your environment variables."
        )


class EnvLoader:
    logger = logging.getLogger("EnvLoader")

    def __init__(self, env_path: Path = None):
        self.env_path = env_path

        # Read environment variables (will update after load_env)
        self.detoxio_base_url = None
        self.detoxio_api_key = None
        self.openai_api_key = None
        self.openai_api_base_url = None

    def load_env(self):
        if self.env_path and self.env_path.exists():
            self.logger.debug(f"Loaded environment variables from: {self.env_path}")
            load_dotenv(dotenv_path=self.env_path)
        else:
            self.logger.debug("Loading env from local env")
            load_dotenv()

        # Update internal state after loading
        self.detoxio_base_url = os.getenv("DETOXIO_BASE_URL", "https://api.detoxio.ai/")
        self.detoxio_api_key = os.getenv("DETOXIO_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base_url = os.getenv("OPENAI_API_BASE_URL")

    def configure(self):
        """
        Configure environment variables:
        - If OPENAI_API_KEY is missing, use DETOXIO_API_KEY
        - Set os.environ accordingly
        """
        if not self.openai_api_key and self.detoxio_api_key:
            self.openai_api_key = self.detoxio_api_key
            self.openai_api_base_url = urljoin(
                self.detoxio_base_url,
                "dtx.services.llms.v1.LlmPlatformProxyService/openai/v1/",
            )
            self.logger.info("Using Detoxio API Key and Proxy for OpenAI.")

        if self.openai_api_key and self.openai_api_base_url:
            os.environ["OPENAI_BASE_URL"] = self.openai_api_base_url
            self.logger.debug(
                f"OPENAI_BASE_URL set to: {os.environ.get('OPENAI_BASE_URL')}"
            )
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
            self.logger.debug(
                f"OPENAI_API_KEY set: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}"
            )

    def validate(self, required_vars=None):
        """
        Validate required environment variables.
        You can pass a list of variable names, or use default common ones.
        """
        if required_vars is None:
            required_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL"]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            self.logger.warning(
                f"Missing environment variables: {missing_vars}. Certain Features will not be available."
            )
        else:
            self.logger.info("✅ All required environment variables are set.")
