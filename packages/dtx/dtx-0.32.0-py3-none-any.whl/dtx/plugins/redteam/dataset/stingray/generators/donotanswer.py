import os
from .base import (
    BaseTemplatizedPromptGenerator,
    ThreatClass,
    ThreatCategory
)

# Based on the Do-Not-Answer: A Dataset for Evaluating Safeguards in LLMs

class BaseDoNotAnswer(BaseTemplatizedPromptGenerator):
    """Base class for Do Not Answer probes."""

    bcp47 = "en"
    recommended_detector = ["mitigation.MitigationBypass"]
    technique = "donotanswer-dataset"
    doc_uri = "https://arxiv.org/abs/2308.13387"
    threat_class=ThreatClass.TOXICITY
    threat_category=ThreatCategory.PROFANITY

    def __init__(self, dna_category, tags, goal, config=None):
        super().__init__(config)
        self.dna_category = dna_category
        self.tags = tags or []
        self.goal = goal or ""
        self.prompts = self.load_prompts()

    def load_prompts(self):
        prompts_path = os.path.join(self.config.resource_path, 
                                    "donotanswer", 
                                    f"{self.dna_category}.txt")
        with open(prompts_path, encoding="utf-8") as f:
            return f.read().strip().split("\n")

class DNA_DiscriminationExclusionToxicityHatefulOffensive(BaseDoNotAnswer):
    """Probe for discrimination, exclusion, toxicity, hateful, and offensive content."""

    threat_class=ThreatClass.TOXICITY
    threat_category=ThreatCategory.PROFANITY
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dna_category="discrimination_exclusion_toxicity_hateful_offensive",
            tags=[
                "avid-effect:ethics:E0301",
                "quality:Behavioral:ContentSafety:Toxicity",
                "quality:Behavioral:ContentSafety:HateHarassment",
                "quality:Behavioral:ContentSafety:Violence",
                "quality:Behavioral:ContentSafety:Profanity",
            ],
            goal="get model to respond as discrimination exclusion toxicity hateful offensive"
        )

class DNA_HumanChatbox(BaseDoNotAnswer):
    """Probe for human chatbox content."""
    threat_class=ThreatClass.TOXICITY
    threat_category=ThreatCategory.PROFANITY
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dna_category="human_chatbox",
            tags=[
                "avid-effect:security:S0301",
                "quality:Behavioral:ContentSafety:Unauthorized",
            ],
            goal="get model to respond as human chatbox"
        )

class DNA_InformationHazard(BaseDoNotAnswer):
    """Probe for information hazard content."""

    threat_class=ThreatClass.INFORMATION_HAZARD
    threat_category=ThreatCategory.SENSITIVE_INFORMATION_LEAKAGE
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dna_category="information_hazard",
            tags=[
                "owasp:llm06",
                "avid-effect:security:S0301",
                "quality:Security:Confidentiality",
            ],
            goal="get model to respond as information hazard"
        )

class DNA_MaliciousUses(BaseDoNotAnswer):
    """Probe for malicious uses content."""

    threat_class=ThreatClass.MALICIOUS_USE
    threat_category=ThreatCategory.FRAUD
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dna_category="malicious_uses",
            tags=[
                "quality:Behavioral:ContentSafety:LegalGoodsServices",
            ],
            goal="get model to respond as malicious uses"
        )

class DNA_MisinformationHarms(BaseDoNotAnswer):
    """Probe for misinformation harms content."""

    threat_class=ThreatClass.MISINFORMATION
    threat_category=ThreatCategory.MISLEADING_INFORMATION
    def __init__(self, config=None):
        super().__init__(
            config=config,
            dna_category="misinformation_harms",
            tags=[
                "quality:Robustness:GenerativeMisinformation",
                "avid-effect:ethics:E0402",
                "owasp:llm09",
            ],
            goal="get model to respond as misinformation harms"
        )
