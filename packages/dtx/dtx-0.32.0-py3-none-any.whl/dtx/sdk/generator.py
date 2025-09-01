from __future__ import annotations

from typing import Callable, Optional, Generator, List

from dtx_models.analysis import PromptDataset
from dtx_models.prompts import BaseMultiTurnConversation
from dtx_models.tactic import PromptMutationTactic
from dtx_models.evaluator import EvaluatorInScope, AnyKeywordBasedPromptEvaluation

from dtx.sdk.runner import (
    DtxRunnerConfigBuilder,
)
from dtx.plugins.providers.dummy.echo import EchoAgent
from dtx.sdk.datasets import DatasetAvailability

from dtx.sdk.runner import (
    DtxRunner,
)

class YieldingEchoAgent(EchoAgent):
    """
    EchoAgent that invokes a user-supplied hook every time it receives
    a conversation.  No custom iterator, no blocking.
    """

    def __init__(
        self,
        on_conversation: Optional[
            Callable[[BaseMultiTurnConversation], None]
        ] = None,
    ) -> None:
        super().__init__()
        self._hook = on_conversation

    # --- single-turn “generate” (unused but kept for interface completeness) ---
    def generate(self, prompt: str) -> str:  # type: ignore[override]
        return super().generate(prompt)

    # --- multi-turn conversation ---------------------------------------------
    def converse(self, prompt: BaseMultiTurnConversation):
        if self._hook:
            self._hook(prompt)          # hand the conv to the callback
        return super().converse(prompt)  # standard echo behaviour

# --------------------------------------------------------------------------- #
#  Dummy evaluator                                                            #
# --------------------------------------------------------------------------- #

def get_dummy_evaluator() -> EvaluatorInScope:
    return EvaluatorInScope(
        evaluation_method=AnyKeywordBasedPromptEvaluation(
            keywords=["example", "test", "dummy"]
        )
    )


# --------------------------------------------------------------------------- #
#  DtxPromptGenerator                                                         #
# --------------------------------------------------------------------------- #

class DtxPromptGenerator:
    """
    Runs the red-team pipeline and captures each generated prompt
    through a simple callback on YieldingEchoAgent.
    """

    def __init__(
        self,
        dataset: PromptDataset = PromptDataset.HF_JAILBREAKV,
        max_prompts: int = 10,
        max_prompts_per_plugin: int = 5,
        max_goals_per_plugin: int = 2,
        tactics: Optional[List[PromptMutationTactic]] = None,
    ) -> None:
        self.dataset = dataset
        self.max_prompts = max_prompts
        self.max_prompts_per_plugin = max_prompts_per_plugin
        self.max_goals_per_plugin = max_goals_per_plugin
        self.tactics = tactics or []

        # Storage for captured conversations
        self._captured: List[BaseMultiTurnConversation] = []

        # Create agent with hook
        self.agent = YieldingEchoAgent(on_conversation=self._captured.append)

    # ------------------------------------------------------------------ #
    #  Public generator                                                  #
    # ------------------------------------------------------------------ #

    def generate(self) -> Generator[BaseMultiTurnConversation, None, None]:
        """
        Run the red-team pipeline and yield prompts (as structured conversations).
        A DatasetAvailabilityError is raised immediately if the chosen dataset
        is unusable on the current machine (missing API keys, etc.).
        """
        # 1. Guard-rail — bail out early if dataset can’t run here
        DatasetAvailability.assert_available(self.dataset)

        # 2. Everything below is unchanged
        evaluator = get_dummy_evaluator()

        cfg = (
            DtxRunnerConfigBuilder()
            .agent(self.agent)
            .dataset(self.dataset)
            .max_prompts(self.max_prompts)
            .max_prompts_per_plugin(self.max_prompts_per_plugin)
            .max_goals_per_plugin(self.max_goals_per_plugin)
            .evaluator(evaluator)
            .tactics(self.tactics)
            .build()
        )

        # Execute the run (blocking).  Echo agent collects prompts via the hook.
        DtxRunner(cfg).run()

        # Now simply yield what we captured.
        for convo in self._captured:
            yield convo