"""
PromptInject detector

Looks for payloads injected from the PromptInject framework using the 
promptinject probe
"""

from .base import EvalHintBasedEvaluator

class AttackRogueString(EvalHintBasedEvaluator):
    """Detect if model emits trigger string"""

    bcp47 = "*"
    doc_uri = "https://github.com/agencyenterprise/PromptInject"

