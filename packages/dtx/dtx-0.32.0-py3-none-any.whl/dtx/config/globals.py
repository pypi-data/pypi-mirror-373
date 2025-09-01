import os
import re
from threading import Lock
from typing import List, Optional

import yaml
from pydantic import BaseModel

from dtx.core.exceptions.base import ModelNotFoundError
from dtx.core.base.evaluator import BaseEvaluator
from dtx_models.evaluator import EvaluationModelName, EvaluationModelType
from dtx_models.providers.hf import (
    HFModels, HuggingFaceProviderConfig, 
    HuggingFaceTask, 
    HuggingFaceProviderParams, 
    SupportedFormat
)

from dtx.plugins.redteam.dataset.hf.hf_prompts_repo import (
    HFPromptsGenerator,
)
from dtx.plugins.redteam.evaluators.hf.toxicity.granite_toxicity_evaluator import (
    GraniteToxicityEvaluator,
)
from dtx.plugins.redteam.evaluators.llamaguard._ollama import Ollama_LlamaGuard
from dtx.plugins.redteam.evaluators.openai.pbe import OpenAIBasedPolicyEvaluator
from dtx.plugins.redteam.evaluators.xray.any_json_path_expr_match import (
    AnyJsonPathExpressionMatch,
)
from dtx.plugins.redteam.evaluators.xray.any_keyword_match import AnyKeywordMatch
from dtx.plugins.redteam.tactics.repo import TacticRepo
from dtx.plugins.redteam.dataset.base.adv_repo import AdvBenchRepo
from dtx.plugins.redteam.dataset.base.harm_repo import HarmfulBehaviourRepo
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError


from .providers import OllamaLlamaGuardConfig, OpenAIConfig


class DependencyFactory:
    """Manages dependencies required for red team evaluation."""

    def __init__(self):
        self.hf_prompt_generator = HFPromptsGenerator()

class GlobalConfig(BaseModel):
    openai: Optional[OpenAIConfig] = OpenAIConfig()
    ollamaguard: Optional[OllamaLlamaGuardConfig] = OllamaLlamaGuardConfig()


# Lock to ensure thread-safe initialization
_initialize_lock = Lock()


# Global variables
global_config: Optional["GlobalConfig"] = None
deps_factory: Optional["DependencyFactory"] = None
eval_factory: Optional["ModelEvaluatorsFactory"] = None
llm_models: Optional["HFModelsRepo"] = None
tactics_repo: Optional[TacticRepo] = None
adv_repo: Optional[AdvBenchRepo] = None
harmb_repo: Optional[HarmfulBehaviourRepo] = None


# Add to the parameters of ensure_initialized
def ensure_initialized(
    init_global_config: bool = False,
    init_deps_factory: bool = False,
    init_eval_factory: bool = False,
    init_llm_models: bool = False,
    init_tactics_repo: bool = False,
    init_adv_repo: bool = False,
    init_harmb_repo: bool = False,
    init_plugin_repo: bool = False,
    init_aif_repo: bool = False,
    init_plugin2framework_mapper: bool = False,
):
    """Idempotent, thread-safe initializer for global services."""
    global global_config, deps_factory, eval_factory, llm_models,  tactics_repo, adv_repo, harmb_repo,  plugin_repo, aif_repo, plugin2framework_mapper

    with _initialize_lock:
        if any([
            init_global_config, init_deps_factory, init_eval_factory, init_llm_models,
            init_tactics_repo, init_adv_repo, init_harmb_repo,
            init_plugin_repo, init_aif_repo, init_plugin2framework_mapper
        ]):
            if init_global_config and not global_config:
                global_config = GlobalConfig()
            if init_deps_factory and not deps_factory:
                deps_factory = DependencyFactory()
            if init_eval_factory and not eval_factory:
                eval_factory = ModelEvaluatorsFactory(config=global_config)
            if init_llm_models and not llm_models:
                llm_models = HFModelsRepo()
            if init_tactics_repo and not tactics_repo:
                tactics_repo = TacticRepo()
            if init_adv_repo and not adv_repo:
                adv_repo = AdvBenchRepo()
            if init_harmb_repo and not harmb_repo:
                harmb_repo = HarmfulBehaviourRepo()
        else:
            if not global_config:
                global_config = GlobalConfig()
            if not deps_factory:
                deps_factory = DependencyFactory()
            if not eval_factory:
                eval_factory = ModelEvaluatorsFactory(config=global_config)
            if not llm_models:
                llm_models = HFModelsRepo()
            if not tactics_repo:
                tactics_repo = TacticRepo()
            if not adv_repo:
                adv_repo = AdvBenchRepo()
            if not harmb_repo:
                harmb_repo = HarmfulBehaviourRepo()

# Add getter function for AdvRepo
def get_adv_repo(only: bool = False) -> AdvBenchRepo:
    ensure_initialized(init_adv_repo=True if only else False)
    return adv_repo

def get_harmb_repo(only: bool = False) -> HarmfulBehaviourRepo:
    ensure_initialized(init_harmb_repo=True if only else False)
    return harmb_repo


def get_global_config(only: bool = False) -> "GlobalConfig":
    ensure_initialized(init_global_config=True if only else False)
    return global_config


def get_deps_factory(only: bool = False) -> "DependencyFactory":
    ensure_initialized(init_deps_factory=True if only else False)
    return deps_factory


def get_eval_factory(only: bool = False) -> "ModelEvaluatorsFactory":
    ensure_initialized(init_eval_factory=True if only else False)
    return eval_factory


def get_llm_models(only: bool = False) -> "HFModelsRepo":
    ensure_initialized(init_llm_models=True if only else False)
    return llm_models


def get_tactics_repo(only: bool = False) -> TacticRepo:
    ensure_initialized(init_tactics_repo=True if only else False)
    return tactics_repo


class HuggingFaceModelFetcher:
    """
    Responsible for fetching model metadata from Hugging Face Hub
    when it's not present in local configuration.
    """

    TASK_TAGS_TO_ENUM = {
        "text-generation": HuggingFaceTask.TEXT_GENERATION,
        "text2text-generation": HuggingFaceTask.TEXT2TEXT_GENERATION,
        "text-classification": HuggingFaceTask.TEXT_CLASSIFICATION,
        "token-classification": HuggingFaceTask.TOKEN_CLASSIFICATION,
        "fill-mask": HuggingFaceTask.FILL_MASK,
        "feature-extraction": HuggingFaceTask.FEATURE_EXTRACTION,
        "sentence-similarity": HuggingFaceTask.SENTENCE_SIMILARITY,
    }

    DEFAULT_CONFIGS = {
        HuggingFaceTask.TEXT_GENERATION: {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9},
        HuggingFaceTask.TEXT2TEXT_GENERATION: {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9},
        HuggingFaceTask.FILL_MASK: {},
        HuggingFaceTask.TEXT_CLASSIFICATION: {},
        HuggingFaceTask.TOKEN_CLASSIFICATION: {},
        HuggingFaceTask.FEATURE_EXTRACTION: {},
        HuggingFaceTask.SENTENCE_SIMILARITY: {},
    }

    def __init__(self):
        self.api = HfApi()

    def fetch(self, model_name: str) -> HuggingFaceProviderConfig:
        """
        Fetch model metadata from Hugging Face Hub and return a new
        HuggingFaceProviderConfig, including any generation defaults.
        Raises ModelNotFoundError if not found.
        """
        try:
            info = self.api.model_info(model_name)

            # Determine task
            task_enum = next(
                (self.TASK_TAGS_TO_ENUM[tag] for tag in info.tags if tag in self.TASK_TAGS_TO_ENUM),
                HuggingFaceTask.TEXT_GENERATION
            )

            # Detect multi-turn support
            support_multi = any(
                re.search(r"(chat|dialog|instruct|conversational)", tag, re.IGNORECASE)
                for tag in info.tags
            )

            # Base defaults
            cfg = self.DEFAULT_CONFIGS.get(task_enum, {}).copy()
            # Try to pull generation_config from the model's config if present
            gen_cfg = info.config.get("generation_config") or {}
            for k, v in gen_cfg.items():
                # Only override if field exists on provider params
                if k in HuggingFaceProviderParams.__fields__:
                    cfg[k] = v

            params = HuggingFaceProviderParams(**cfg)

            return HuggingFaceProviderConfig(
                model=model_name,
                task=task_enum,
                support_multi_turn=support_multi,
                supported_input_format=SupportedFormat.OPENAI,
                params=params
            )

        except HfHubHTTPError as e:
            raise ModelNotFoundError(model_name) from e



class HFModelsRepo:
    """
    Loads models from a YAML file and retrieves configurations.
    """

    def __init__(self, models_path: str = None, fetcher: HuggingFaceModelFetcher = None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self._models_path = os.path.join(script_dir, models_path or "./hf_models.yml")
        self.models = self._load_from_file()
        self.fetcher = fetcher or HuggingFaceModelFetcher()

    def _load_from_file(self) -> HFModels:
        if not os.path.exists(self._models_path):
            return HFModels(huggingface=[])
        with open(self._models_path, "r") as file:
            data = yaml.safe_load(file) or {}
        return HFModels(
            huggingface=[HuggingFaceProviderConfig(**model) for model in data.get("huggingface", [])]
        )

    def get_huggingface_model(self, model_name: str) -> HuggingFaceProviderConfig:
        """
        Retrieve a model config by name; fetch from Hugging Face if missing.
        """
        # Try local first
        for provider in self.models.huggingface:
            if provider.model == model_name:
                return provider

        # Not found locally, fetch remotely
        new_provider = self.fetcher.fetch(model_name)
        print(new_provider)
        # Cache locally
        self.models.huggingface.append(new_provider)
        return new_provider


class ModelEvaluatorsFactory:
    """Factory class for initializing and managing different evaluation models."""

    EVALUATORS = [
        (AnyKeywordMatch, {}),
        (AnyJsonPathExpressionMatch, {}),
        (
            GraniteToxicityEvaluator,
            {
                "model_name": "ibm-granite/granite-guardian-hap-125m",
                "eval_name": EvaluationModelName.IBM_GRANITE_TOXICITY_HAP_125M,
            },
        ),
        (
            GraniteToxicityEvaluator,
            {
                "model_name": "ibm-granite/granite-guardian-hap-38m",
                "eval_name": EvaluationModelName.IBM_GRANITE_TOXICITY_HAP_38M,
            },
        ),
        (Ollama_LlamaGuard, {"config_class": OllamaLlamaGuardConfig}),
        (OpenAIBasedPolicyEvaluator, {"model_name": "gpt-4o-mini"}),
    ]

    def __init__(self, config: GlobalConfig):
        """Initializes the evaluator factory with the given configuration."""
        self._evaluators: List[BaseEvaluator] = []
        self._init_evaluators(config)

    def _add_evaluator(self, evaluator: BaseEvaluator):
        """Adds an evaluator to the internal list."""
        self._evaluators.append(evaluator)

    def get_evaluator_by_name(
        self, name: EvaluationModelName
    ) -> Optional[BaseEvaluator]:
        """Retrieves an evaluator instance by its name."""
        return next(
            (
                evaluator
                for evaluator in self._evaluators
                if evaluator.get_name() == name
            ),
            None,
        )

    def get_evaluators_by_type(
        self, eval_type: EvaluationModelType
    ) -> List[BaseEvaluator]:
        """Retrieves a list of evaluators filtered by their type."""
        return [
            evaluator
            for evaluator in self._evaluators
            if evaluator.get_type() == eval_type
        ]

    def select_evaluator(
        self, eval_model_name: EvaluationModelName, eval_model_type: EvaluationModelType
    ) -> BaseEvaluator:
        """
        Selects an appropriate evaluator based on model name or type.
        """
        evaluator = (
            self.get_evaluator_by_name(eval_model_name) if eval_model_name else None
        )
        if not evaluator:
            evaluators = self.get_evaluators_by_type(eval_model_type)
            evaluator = evaluators[0] if evaluators else None
        return evaluator

    def _init_evaluators(self, config: GlobalConfig):
        """Initializes evaluators, including those with and without configuration dependencies."""
        for evaluator_class, param_data in self.EVALUATORS:
            params = {}
            for k, v in param_data.items():
                if k == "config_class":
                    params["config"] = next(
                        (
                            getattr(config, attr)
                            for attr in config.model_fields
                            if isinstance(getattr(config, attr, None), v)
                        ),
                        None,
                    )
                else:
                    params[k] = v

            evaluator = (
                evaluator_class(**params["config"].model_dump())
                if "config" in params and isinstance(params["config"], BaseModel)
                else evaluator_class(**params)
            )

            if evaluator.is_available():
                self._add_evaluator(evaluator)
