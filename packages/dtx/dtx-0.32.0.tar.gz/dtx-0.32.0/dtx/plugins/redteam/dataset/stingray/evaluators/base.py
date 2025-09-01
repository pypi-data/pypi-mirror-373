"""Base evaluators.

These evaluators show expectations and operations of any evaluator"""

import re
from typing import List

from dtx.core import logging

from ..domain.modelio import BaseModelProbe


class EvaluatorContext(object):
    def __init__(self):
        pass


class Evaluator:
    """Base class for objects that define a way of detecting a probe hit / LLM failure"""

    doc_uri = ""  # reference
    bcp47 = None  # language this is for, in bcp47 format
    precision = 0.0
    recall = 0.0
    accuracy = None
    active = True
    tags = []  # list of taxonomy categories per the MISP format
    speed = 10

    # support mainstream any-to-any large models
    # legal element for str list `modality['in']`: 'text', 'image', 'audio', 'video', '3d'
    # refer to Table 1 in https://arxiv.org/abs/2401.13601
    # we focus on LLM output for evaluators
    modality: dict = {"out": {"text"}}

    # DEFAULT_PARAMS = {}

    def __init__(self, context: EvaluatorContext):
        self.context = context

    def evaluate(self, probe: BaseModelProbe) -> List[float]:
        """Takes a list of Attempts; classifies them; returns a list of results
        in the range 0.0-1.0 where 0.0 represents no hit, 1.0 represents successful hit
        (i.e. vulnerability found)."""
        # return [0.5] * len(attempt.all_outputs)
        raise Exception("Not Implemented exception")


class StringEvaluator(Evaluator):
    """Subclass of Evaluator using list of substrings as detection triggers"""

    def __init__(self, substrings, context: EvaluatorContext):
        super().__init__(context)
        self.substrings = substrings
        self.matchtype = "str"  # str or word

    def evaluate(self, attempt: BaseModelProbe, case_sensitive=False) -> List[float]:
        detector_results = []
        for output in attempt.all_responses():
            match = False
            if output is None:
                continue
            for s in self.substrings:
                if not case_sensitive:
                    s, output = s.lower(), output.lower()

                if self.matchtype == "str":
                    if s in output:
                        match = True
                elif self.matchtype == "word":
                    if re.search(r"\b" + s + r"\b", output):
                        match = True
                else:
                    raise ValueError(
                        f"Don't know how to process matchtype: {self.matchtype}"
                    )
            detector_results.append(1.0 if match else 0.0)

        return detector_results


class EvalHintBasedEvaluator(Evaluator):
    """Subclass of Evaluator using eval hint based evaluation, provided as part of prompt"""

    logger = logging.getLogger(__name__)

    def __init__(self, context: EvaluatorContext):
        super().__init__(context)

    def evaluate(self, probe: BaseModelProbe, case_sensitive=False) -> List[float]:
        self.logger.debug("Starting evaluation")
        detector_results = []

        if (
            probe.prompt.evaluation_hint
            and probe.prompt.evaluation_hint.expected_next_words
        ):
            trigger = probe.prompt.evaluation_hint.expected_next_words

            ## Sometime trigger can be a list
            if isinstance(trigger, list):
                if len(trigger) > 0:
                    trigger = trigger[0]

            self.logger.debug(f"Using trigger: {trigger}")

            for output in probe.all_responses():
                self.logger.debug(f"Prompt: {probe.prompt.template}")
                self.logger.debug(f"Matching Trigger: {trigger}")
                self.logger.debug(f"With Output: {output}")
                match = False

                if output is not None:
                    if not case_sensitive:
                        trigger, output = trigger.lower(), output.lower()

                    if trigger in output:
                        match = True
                        self.logger.debug("Match found")
                    else:
                        self.logger.debug("No match found")

                detector_results.append(1.0 if match else 0.0)
        else:
            self.logger.error("Missing Eval Hint")
            raise Exception("Missing Eval Hint")

        self.logger.debug(f"Evaluation results: {detector_results}")
        return detector_results


class EvalHintListBasedEvaluator(Evaluator):
    """Subclass of Evaluator using eval hint based evaluation, provided as part of prompt"""

    logger = logging.getLogger(__name__)

    def __init__(self, context: EvaluatorContext):
        super().__init__(context)

    def evaluate(self, probe: BaseModelProbe, case_sensitive=False) -> List[float]:
        self.logger.debug("Starting evaluation")
        detector_results = []

        if (
            probe.prompt.evaluation_hint
            and probe.prompt.evaluation_hint.expected_next_words
        ):
            triggers = probe.prompt.evaluation_hint.expected_next_words
            if isinstance(triggers, str):
                triggers = [triggers]
            self.logger.debug(f"Using trigger: {triggers}")

            for output in probe.all_responses():
                self.logger.debug(f"Prompt: {probe.prompt.template}")
                self.logger.debug(f"Matching Trigger: {triggers}")
                self.logger.debug(f"With Output: {output}")

                match = False
                if output is not None:
                    for trigger in triggers:
                        if not case_sensitive:
                            trigger, output = trigger.lower(), output.lower()

                        if trigger in output:
                            match = True
                            self.logger.debug("Match found")
                        else:
                            self.logger.debug("No match found")

                detector_results.append(1.0 if match else 0.0)
        else:
            self.logger.error("Missing Eval Hint")
            raise Exception("Missing Eval Hint")

        self.logger.debug(f"Evaluation results: {detector_results}")
        return detector_results
