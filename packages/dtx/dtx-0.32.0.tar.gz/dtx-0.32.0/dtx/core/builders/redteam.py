import warnings
from typing import List, Optional, Union

from dtx_models.evaluator import EvaluatorInScope
from dtx_models.providers.gradio import GradioProvider
from dtx_models.providers.hf import HFProvider
from dtx_models.providers.http import HttpProvider
from dtx_models.providers.litellm import LitellmProvider
from dtx_models.providers.ollama import OllamaProvider
from dtx_models.providers.openai import OpenaiProvider
from dtx_models.scope import (
    AgentInfo,
    PluginInScopeConfig,
    PluginsInScope,
    ProviderVars,
    RedTeamScope,
    RedTeamSettings,
)
from dtx_models.tactic import PromptMutationTactic
from dtx_models.template.prompts.langhub import LangHubPromptTemplate
from dtx_models.repo.plugin import Plugin, PluginRepo
from dtx_models.repo.ai_frameworks import AIFrameworkRepo


class RedTeamScopeBuilder:
    """Builder class for :class:`~dtx_models.scope.RedTeamScope` with a fluent API.

    **New in 2025‑07**
    ------------------
    * Added explicit *limit* attributes: ``max_prompts``, ``max_plugins``,
      ``max_prompts_per_plugin``, ``max_goals_per_plugin`` and
      ``max_prompts_per_tactic``.
    * ``num_tests`` remains for backward‑compatibility but automatically
      synchronises all of the limit parameters so callers that previously set a
      single number still get sensible behaviour.
    * Convenience ``set_prompt`` method for the common case of working with a
      single prompt template.
    """

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __init__(self):
        # Core components --------------------------------------------------
        self.agent: Optional[AgentInfo] = None

        # Limit / sizing parameters ---------------------------------------
        self.max_prompts: int = 15
        self.max_plugins: int = 100000
        self.max_prompts_per_plugin: int = 5
        self.max_goals_per_plugin: int = 1
        self.max_prompts_per_tactic: int = 5

        # Deprecated alias (kept for backward‑compatibility) --------------
        self.num_tests: int = self.max_prompts

        # Extended configuration objects ----------------------------------
        self.plugins: PluginsInScope = PluginsInScope(plugins=[])
        self.providers: List[
            Union[
                HttpProvider,
                HFProvider,
                GradioProvider,
                OllamaProvider,
                OpenaiProvider,
                LitellmProvider,
            ]
        ] = []
        self.prompts: List[LangHubPromptTemplate] = []
        self.environments: List[ProviderVars] = []
        self.tactics: List[PromptMutationTactic] = []
        self.global_evaluator: Optional[EvaluatorInScope] = None
        self._ai_framework_repo = AIFrameworkRepo()

    # ------------------------------------------------------------------
    # Fluent setters / convenience methods
    # ------------------------------------------------------------------
    def set_agent(self, agent: AgentInfo):
        self.agent = agent
        return self

    # ------------------------------------------------------------------
    # Backwards‑compatibility shim: ``num_tests`` now updates ALL limits.
    # ------------------------------------------------------------------
    def set_num_tests(self, num_tests: int):
        """Set *num_tests* and propagate to all other size limits.

        Historically the builder accepted just a *num_tests* value.  In the new
        API this automatically populates *max_prompts* (global),
        *max_prompts_per_plugin*, *max_prompts_per_tactic*, and even
        *max_plugins* so that the red‑team run remains bounded by the same
        single scalar constraint.
        """
        self.num_tests = num_tests
        # Keep every limit in sync with the single controlling scalar
        self.max_prompts = num_tests
        self.max_prompts_per_plugin = num_tests
        self.max_prompts_per_tactic = num_tests
        self.max_plugins = num_tests
        # We keep *max_goals_per_plugin* at its default (1) because goals tend
        # to be qualitative rather than quantitative, but you can always change
        # it explicitly via *set_limits* if desired.
        return self

    # Preferred modern API -------------------------------------------------
    def set_limits(
        self,
        *,
        max_prompts: Optional[int] = None,
        max_plugins: Optional[int] = None,
        max_prompts_per_plugin: Optional[int] = None,
        max_goals_per_plugin: Optional[int] = None,
        max_prompts_per_tactic: Optional[int] = None,
    ):
        """Set one or more red‑team size limits in a single call."""
        if max_prompts is not None:
            self.max_prompts = max_prompts
            self.num_tests = max_prompts  # keep alias in sync
        if max_plugins is not None:
            self.max_plugins = max_plugins
        if max_prompts_per_plugin is not None:
            self.max_prompts_per_plugin = max_prompts_per_plugin
        if max_goals_per_plugin is not None:
            self.max_goals_per_plugin = max_goals_per_plugin
        if max_prompts_per_tactic is not None:
            self.max_prompts_per_tactic = max_prompts_per_tactic
        return self

    # ------------------------------------------------------------------
    # Prompt helpers ----------------------------------------------------
    # ------------------------------------------------------------------
    def set_prompt(self, prompt: LangHubPromptTemplate):
        """Replace any existing prompt list with a single *prompt*."""
        self.prompts = [prompt]
        return self

    def add_prompt(self, prompt: LangHubPromptTemplate):
        self.prompts.append(prompt)
        return self

    def set_prompts(self, prompts: List[LangHubPromptTemplate]):
        self.prompts = prompts
        return self

    # ------------------------------------------------------------------
    # Plugin helpers -----------------------------------------------------
    # ------------------------------------------------------------------
    def add_plugin(self, plugin: Union[str, PluginInScopeConfig]):
        self.plugins.plugins.append(
            plugin if isinstance(plugin, (str, PluginInScopeConfig)) else plugin.id
        )
        return self

    def set_plugins(self, plugins: List[Union[str, PluginInScopeConfig]]):
        self.plugins.plugins = plugins
        return self

    def add_plugins_by_expression(self, expressions: List[str]=None):
        """
        Add plugins to the scope based on regex or keyword expressions.
        Matches against plugin ID and tags using PluginRepo.search().
        """
        expressions = expressions or [".*"]
        matched_plugins = PluginRepo.search(expressions)
        for plugin in matched_plugins:
            self.add_plugin(plugin)
        return self

    def add_plugins_by_framework(self, framework_patterns: List[str]):
        """
        Add plugins by matching AI Framework names/titles using search patterns (regex or keywords).

        Uses AIFrameworkRepo.search_plugins() to gather plugin IDs.

        Example:
            builder.add_plugins_by_framework(["NIST", "Fairness"])
        """
        plugins = set()
        for pattern in framework_patterns:
            plugins.update(self._ai_framework_repo.search_plugins(pattern=pattern))
        for plugin_id in plugins:
            self.add_plugin(plugin_id)
        return self

    def add_plugins_from_repo(self, keywords: Optional[List[str]] = None):
        """
        ⚠️ Deprecated: Use `add_plugins_by_expression()` instead.

        Adds plugins from the PluginRepo that match any of the provided keywords.
        If no keywords are given, adds all available plugins.
        """
        warnings.warn(
            "`add_plugins_from_repo` is deprecated and will be removed in a future release. "
            "Please use `add_plugins_by_expression()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        all_plugins: List[Plugin] = PluginRepo.get_all_plugins()
        if keywords:
            keywords_lower = [kw.lower() for kw in keywords]
            matched_plugins = [
                plugin
                for plugin in all_plugins
                if any(kw in plugin.lower() for kw in keywords_lower)
            ]
        else:
            matched_plugins = all_plugins
        for plugin in matched_plugins:
            self.add_plugin(plugin)
        return self

    # ------------------------------------------------------------------
    # Provider / environment / tactic helpers ---------------------------
    # ------------------------------------------------------------------
    def add_provider(
        self,
        provider: Union[
            HttpProvider,
            HFProvider,
            GradioProvider,
            OllamaProvider,
            OpenaiProvider,
            LitellmProvider,
        ],
    ):
        self.providers.append(provider)
        return self

    def set_providers(
        self,
        providers: List[
            Union[
                HttpProvider,
                HFProvider,
                GradioProvider,
                OllamaProvider,
                OpenaiProvider,
                LitellmProvider,
            ]
        ],
    ):
        self.providers = providers
        return self

    def add_environment(self, environment: ProviderVars):
        self.environments.append(environment)
        return self

    def set_environments(self, environments: List[ProviderVars]):
        self.environments = environments
        return self

    def set_tactics(self, tactics: List[PromptMutationTactic]):
        self.tactics = tactics
        return self

    def set_global_evaluator(self, evaluator: EvaluatorInScope):
        self.global_evaluator = evaluator
        return self

    # ------------------------------------------------------------------
    # Finalise and build -------------------------------------------------
    # ------------------------------------------------------------------
    def build(self) -> RedTeamScope:
        if not self.agent:
            raise ValueError("Agent must be set before building RedTeamScope.")

        redteam_settings = RedTeamSettings(
            max_prompts=self.max_prompts,
            max_plugins=self.max_plugins,
            max_prompts_per_plugin=self.max_prompts_per_plugin,
            max_goals_per_plugin=self.max_goals_per_plugin,
            max_prompts_per_tactic=self.max_prompts_per_tactic,
            plugins=self.plugins,
            tactics=self.tactics,
            global_evaluator=self.global_evaluator,
        )

        return RedTeamScope(
            agent=self.agent,
            providers=self.providers,
            prompts=self.prompts,
            environments=self.environments,
            redteam=redteam_settings,
        )
