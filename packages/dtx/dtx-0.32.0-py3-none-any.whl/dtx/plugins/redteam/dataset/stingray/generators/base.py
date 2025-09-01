import os
import random
from ..domain.modelio import ProbeContext, Prompt, EvaluationHint

# class ModelConfig:
#     """
#     ModelConfig is a class that holds the configuration for a model.
    
#     Attributes:
#         name (str): The name of the model that can be used to address the model in prompts such as ChatGPT.
#     """
#     def __init__(self, name: str):
#         self.name = name # Name of the model

class ThreatClass:
    TOXICITY = "TOXICITY"
    MISINFORMATION = "MISINFORMATION"
    INFORMATION_HAZARD = "INFORMATION_HAZARD"
    MALICIOUS_USE = "MALICIOUS_USE"
    HUMAN_COMPUTER_INTERACTION = "HUMAN_COMPUTER_INTERACTION"
    AUTOMATION_ACCESS_ENVIRONMENTAL = "AUTOMATION_ACCESS_ENVIRONMENTAL"
    DEFENSE_BYPASS = "DEFENSE_BYPASS"
    UNKNOWN=""

class ThreatCategory:
    ABUSIVE_LANGUAGE = "ABUSIVE_LANGUAGE"
    HATE_SPEECH = "HATE_SPEECH"
    HARASSMENT = "HARASSMENT"
    BULLYING = "BULLYING"
    SEXUAL_ASSAULT = "SEXUAL_ASSAULT"
    PROFANITY = "PROFANITY"
    FALSE_INFORMATION = "FALSE_INFORMATION"
    MISLEADING_INFORMATION = "MISLEADING_INFORMATION"
    PERSONAL_INFORMATION_LEAKAGE = "PERSONAL_INFORMATION_LEAKAGE"
    SENSITIVE_INFORMATION_LEAKAGE = "SENSITIVE_INFORMATION_LEAKAGE"
    MALWARE_GENERATION = "MALWARE_GENERATION"
    WEAPONIZATION = "WEAPONIZATION"
    FRAUD = "FRAUD"
    PHISHING = "PHISHING"
    THEFT = "THEFT"
    VIOLENCE = "VIOLENCE"
    CRIME = "CRIME"
    CBRN = "CBRN"  # Chemical, Biological, Radiological, and Nuclear threats
    JAILBREAK = "JAILBREAK"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    HACKING = "HACKING"
    UNKNOWN=""



class GeneratorConfig:
    """
    GeneratorConfig is a class that holds the configuration for a generator.
    
    Attributes:
        resource_path (str): The path to the resources directory.
    """
    def __init__(self, resource_path=None):
        default_rp = os.path.join(os.path.dirname(__file__), "../resources/")
        self.resource_path = resource_path or default_rp
        self.seed = random.random()
        self.generators = { "techniques": {
                "indirect-prompt-injection-encoding": {"payload_classes": ["default"]}
            }
        }

class BaseGenerator:
    """
    BaseGenerator is a base class for generators.
    
    Attributes:
        config (GeneratorConfig): The configuration for the generator.
    """
    prompts = []
    def __init__(self, config:GeneratorConfig=None):
        self.config = config or GeneratorConfig()
    
    def generate(self):
        """
        Generate prompts.
        
        Yields:
            Prompt: The next prompt.
        """
        for prompt in self.prompts:
            yield prompt

class BaseTemplatizedPromptGenerator(BaseGenerator):
    """
    BaseTemplatizedPromptGenerator is a base class for templatized prompt generators.
    
    Attributes:
        active (bool): Whether the generator is active.
        recommended_detector (list): A list of recommended detectors.
        doc_uri (str): The URI of the document.
        goal (str): The goal of the generator.
        tags (list): A list of tags associated with the generator.
        template_vars (list): A list of template variables associated with the generator.
    """
    active = True
    recommended_detector = []
    doc_uri = ""
    goal = ""
    tags = []
    template_vars = []
    prompts = []
    # 10 Fast, 6 Medium , 3 Slow (Generally need a model)
    speed = 10 
    technique = ""
    threat_class=ThreatClass.UNKNOWN
    threat_category=ThreatCategory.UNKNOWN
    
    def __init__(self, config:GeneratorConfig=None):
        super().__init__(config)
        
    def create_probe_context(self):
        return ProbeContext(goal=self.goal, 
                        references=[self.doc_uri], 
                        detectors=self.recommended_detector, 
                        tags=self.tags,
                        threat_class=self.threat_class,
                        threat_category=self.threat_category,
                        technique=self.technique)
        
    def generate(self):
        """
        Generate prompts with the template values applied.
        
        Yields:
            Prompt: The next prompt with the template values applied.
        """
        for prompt in self.prompts:
            yield Prompt(prompt, 
                        template_vars=self.template_vars)
    

class BasePromptWithEvalHintGenerator(BaseTemplatizedPromptGenerator):
    """
    BaseTemplatizedPromptGenerator is a base class for templatized prompt generators.
    
    """
    
    # Evaluation hints to faciliate evaluation
    eval_hints:EvaluationHint = []
    
    def __init__(self, config:GeneratorConfig=None):
        super().__init__(config)
        
    def create_probe_context(self):
        return ProbeContext(goal=self.goal, 
                        references=[self.doc_uri], 
                        detectors=self.recommended_detector, 
                        tags=self.tags, 
                    threat_class=self.threat_class,
                        threat_category=self.threat_category,
                        technique=self.technique)
        
    def generate(self):
        """
        Generate prompts with the template values applied.
        
        Yields:
            Prompt: The next prompt with the template values applied.
        """
        for prompt, eval_hint in zip(self.prompts, self.eval_hints):
            yield Prompt(prompt, 
                         template_vars=self.template_vars, 
                         evaluation_hint=eval_hint)