import os
from typing import Iterator, List, Optional

import yaml
from pydantic import BaseModel

from dtx.core import logging
from dtx_models.analysis import (
    PromptVariable,
    RiskItem,
    TestPromptsWithModEval,
    TestPromptWithModEval,
)
from dtx_models.evaluator import (
    EvalModuleParam,
    ModuleBasedPromptEvaluation
)
from dtx.plugins.redteam.dataset.stingray.domain.modelio import ProbeContext

# Import Stingray components
from dtx.plugins.redteam.dataset.stingray.generators.manager import (
    PromptsGeneratorContext,
    PromptsGeneratorFilter,
    StingrayPromptsGenerator,
)


class StingrayFilter(BaseModel):
    """
    Represents the filter applied to a Stingray plugin.
    Contains an optional subcategory and a list of techniques.
    """

    category: Optional[str] = ""
    technique: Optional[List[str]] = []


class StingrayPlugin(BaseModel):
    """
    Represents a single Stingray plugin with an associated plugin ID and filter.
    """

    plugin_id: str  # Unique identifier for the plugin
    stingray: Optional[dict] = None  # Optional stingray filter data

    def get_filter(self) -> StingrayFilter:
        """
        Retrieves the filter associated with this plugin.
        Returns a default filter if none exists.
        """
        if self.stingray and "filter" in self.stingray:
            return StingrayFilter(**self.stingray["filter"])
        return StingrayFilter()


class StingrayPluginMap(BaseModel):
    """
    Represents the entire mapping of Stingray plugins.
    Contains a list of plugins and methods for filtering.
    """

    plugins: List[StingrayPlugin]  # List of all plugins

    @classmethod
    def from_yaml(cls, file_path: str):
        """
        Loads the Stingray plugin map from a YAML file.

        Args:
            file_path (str): Path to the YAML file.

        Returns:
            StingrayPluginMap: An instance of the class populated with plugins.
        """
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)  # Load YAML data
        return cls(**data)

    @classmethod
    def get_default(cls):
        script_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # Get the current script directory
        yaml_path = os.path.join(
            script_dir, "stingray2plugins.yml"
        )  # Construct relative path
        return cls.from_yaml(yaml_path)

    def get_plugins_by_technique(self, technique: str) -> List[StingrayPlugin]:
        """
        Retrieves plugins that match a specific technique.

        Args:
            technique (str): The technique to filter plugins by.

        Returns:
            List[StingrayPlugin]: A list of matching plugins.
        """
        return [
            plugin
            for plugin in self.plugins
            if technique in plugin.get_filter().technique
        ]

    def get_plugins_by_subcategory(self, subcategory: str) -> List[StingrayPlugin]:
        """
        Retrieves plugins that match a specific subcategory.

        Args:
            subcategory (str): The subcategory to filter plugins by.

        Returns:
            List[StingrayPlugin]: A list of matching plugins.
        """
        return [
            plugin
            for plugin in self.plugins
            if plugin.get_filter().subcategory == subcategory
        ]

    def get_filter_by_plugin_id(self, plugin_id: str) -> Optional[StingrayFilter]:
        """
        Retrieves the filter for a specific plugin by its plugin_id.

        Args:
            plugin_id (str): The plugin ID to search for.

        Returns:
            Optional[StingrayFilter]: The filter associated with the plugin, or None if not found.
        """
        for plugin in self.plugins:
            if plugin.plugin_id == plugin_id:
                return plugin.get_filter()
        return None


# ---- Stingray Prompts Generator ----


class Stringray_PromptsGenerator:
    """
    Generates test prompts and evaluation criteria for each attack strategy.
    """

    def __init__(self):
        """Initializes Stingray Plugin Map"""
        self.spm = StingrayPluginMap.get_default()

    def _get_template_values(self, tv: str) -> List[str]:
        """
        Return the template variable value
        """

        value_map = {"model_name": ["OpenAI-4o"]}

        return value_map.get(tv, ["Unknown"])

    def generate(
        self,
        app_name: str,
        threat_desc: str,
        risks: List[RiskItem],
        max_prompts: int = 10,
        max_prompts_per_plugin: int = 5,
        max_goals_per_plugin: int = 5
    ) -> Iterator[TestPromptsWithModEval]:
        """
        Generates test prompts and evaluation criteria for attack strategies of each risk,
        distributing the total max_prompts as evenly as possible across risks. Any remainder
        is given to the earliest risks. If a risk cannot use its full share, the leftover
        allowance is carried forward to later risks.
        """
        if not risks or max_prompts <= 0:
            return

        total_prompts = 0

        # Get all the module names, to match them in the attack strategy
        srg = StingrayPromptsGenerator()
        module_names = srg.get_all_module_names()

        n_risks = len(risks)
        base_quota = max_prompts // n_risks
        remainder = max_prompts % n_risks
        carry_over = 0  # unused allowance from earlier risks

        for r_idx, risk in enumerate(risks):
            if total_prompts >= max_prompts:
                break  # global stop

            # Equal-share quota for this risk (+1 for the first `remainder` risks)
            equal_quota = base_quota + (1 if r_idx < remainder else 0)

            # Allow this risk to also consume any leftover allowance from earlier risks
            allowed_for_this_risk = equal_quota + carry_over

            # Respect per-risk cap if it is stricter than our equal-share allowance
            if max_prompts_per_plugin is not None:
                allowed_for_this_risk = min(allowed_for_this_risk, max_prompts_per_plugin)

            # Never exceed the remaining global budget
            allowed_for_this_risk = min(allowed_for_this_risk, max_prompts - total_prompts)

            if allowed_for_this_risk <= 0:
                carry_over = 0
                continue

            logging.info(f"Generating up to {allowed_for_this_risk} prompts for risk: {risk.risk}")

            generated_here = 0
            test_prompts: List[TestPromptWithModEval] = []

            # Iterate attack strategies and matched modules until we hit this risk's allowance
            stop_risk = False
            for attack_strategy in risk.attack_strategies:
                if stop_risk or total_prompts >= max_prompts:
                    break

                for mod in module_names:
                    if stop_risk or total_prompts >= max_prompts:
                        break

                    if mod not in attack_strategy:
                        continue

                    # Create a filter/context for the generator
                    filter_config = PromptsGeneratorFilter(technique=mod)
                    context = PromptsGeneratorContext(filter=filter_config)
                    generator = StingrayPromptsGenerator(context=context)

                    # Pull instances until we satisfy the allowance
                    for i, prompt_instance in enumerate(generator.generate()):
                        if (
                            generated_here >= allowed_for_this_risk
                            or total_prompts >= max_prompts
                        ):
                            stop_risk = True
                            break

                        prompt = prompt_instance.prompt
                        pcontext = prompt_instance.context
                        module_name = prompt_instance.module_name

                        # Get Prompt in Text format
                        prompt_text = prompt.get()

                        # Create Prompt Variables from template variables
                        template_variables = prompt.template_vars
                        prompt_variables = []
                        for tv in template_variables:
                            values = self._get_template_values(tv)
                            prompt_variables.append(PromptVariable(name=tv, values=values))

                        # Ensure pcontext is valid
                        if not isinstance(pcontext, ProbeContext):
                            logging.warning(
                                f"Skipping invalid pcontext for prompt {i + 1}"
                            )
                            continue

                        # Extract key attributes from ProbeContext
                        goal = pcontext.goal
                        tags = pcontext.tags
                        threat_class = pcontext.threat_class
                        threat_category = pcontext.threat_category
                        strategy = pcontext.technique  # Technique -> Strategy
                        detectors = pcontext.detectors

                        eval_mod_params = []
                        if prompt.evaluation_hint:
                            expected_next_words = (
                                prompt.evaluation_hint.expected_next_words
                                if prompt.evaluation_hint
                                else ""
                            )
                            eval_mod_params.append(
                                EvalModuleParam(param="expected_next_words", value=expected_next_words)
                            )

                        # Define Evaluation Modules
                        evaluation_method = ModuleBasedPromptEvaluation(
                            modules=detectors, params=eval_mod_params
                        )

                        # Create TestPromptWithModEval object
                        test_prompt = TestPromptWithModEval(
                            prompt=prompt_text,
                            evaluation_method=evaluation_method,
                            module_name=module_name,
                            tags=tags,
                            threat_class=threat_class,
                            threat_category=threat_category,
                            goal=goal,
                            strategy=strategy,
                            template_variables=prompt_variables,
                        )

                        logging.debug(
                            f"Generated Prompt for Risk {risk.risk}: {prompt_text[0:50]}"
                        )

                        test_prompts.append(test_prompt)
                        generated_here += 1
                        total_prompts += 1

                        if generated_here >= allowed_for_this_risk:
                            stop_risk = True
                            break

            logging.info(
                f"Generated {generated_here} prompt(s) for Risk {risk.risk} "
                f"(allowance was {allowed_for_this_risk})."
            )

            # Yield if anything was generated for this risk
            if test_prompts:
                yield TestPromptsWithModEval(risk_name=risk.risk, test_prompts=test_prompts)

            # Any unused allowance is carried forward to the next risks
            carry_over = max(0, allowed_for_this_risk - generated_here)
