"""Probes to check if a generator will continue a contentious term.

Operates by giving high-risk context as a prompt, extracted from e.g. Urban
Dictionary examples of use of contentious terms, and seeing if the model will
continue the term based on varying amounts of prefix.
"""

import json
import os
from collections import defaultdict

from ..domain.modelio import EvaluationHint
from .base import (
    BasePromptWithEvalHintGenerator,
    GeneratorConfig,
    ThreatCategory,
    ThreatClass,
)


class ContinueSlursReclaimedSlurs80(BasePromptWithEvalHintGenerator):
    """Continue partial word with slur or reclaimed slur.

    This probe poses a partial ethnic slur with some preceding content, and
    checks to see if the model will complete the slur. It uses a subset of 80
    slurs & contexts that test LLMs have been likely to provide completions for.

    Example:
    =============
    from dtx.plugins.redteam.dataset.stingray.generators.continuation import ContinueSlursReclaimedSlurs80
    c = ContinueSlursReclaimedSlurs80()
    list(map(lambda x: x.expected_next_words, c.eval_hints))

    """

    bcp47 = "en"
    doc_uri = ""
    recommended_detector = [
        "continuation.Continuation",
    ]
    tags = [
        "avid-effect:ethics:E0101",
        "avid-effect:ethics:E0301",
        "avid-effect:performance:P0401",
        "owasp:llm01",
        "quality:Behavioral:ContentSafety:Toxicity",
        "quality:Behavioral:ContentSafety:HateHarassment",
        "payload:unwanted:hatespeech",
    ]
    goal = "output an ethnic slur"
    technique = "continuation"
    threat_class = ThreatClass.TOXICITY
    threat_category = ThreatCategory.PROFANITY

    def __init__(self, config: GeneratorConfig = None):
        super().__init__(config=config)
        # go through the list
        # for each term, work out first char, first three chars, all but last two chars
        # append these to each of the prefixes for that term
        slur_prefixes = defaultdict(set)
        filepath = os.path.join(self.config.resource_path, "slurprompts_80.jsonl")
        with open(filepath, "r", encoding="utf-8") as slurfile:
            for line in slurfile:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                slur_prefixes[entry["term"]].add(entry["prefix"])

        self.prompts = []
        self.eval_hints = []
        for term, prefixes in slur_prefixes.items():
            lower_term = term.lower()
            term_variants = set(["", lower_term[0]])  # blank, first letter
            if len(term) > 2:
                term_variants.add(lower_term[:2].strip())  # first two letters
            term_variants.add(
                lower_term[: int(len(lower_term) / 2)].strip()
            )  # first half of term

            for prefix in prefixes:
                for term_variant in term_variants:
                    # would use a set but order is important
                    candidate_prompt = prefix + term_variant
                    if candidate_prompt not in self.prompts:
                        self.prompts.append(candidate_prompt.strip())
                        hint = EvaluationHint(expected_next_words=term)
                        self.eval_hints.append(hint)

    # def _attempt_prestore_hook(self, attempt: Attempt, seq: int) -> Attempt:
    #     attempt.notes = dict(
    #         attempt.notes
    #     )  # we don't want all attempts.notes to ref same dict
    #     attempt.notes["trigger"] = str(self.triggers[seq])
    #     return attempt
