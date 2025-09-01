from typing import List, Iterator

from .base import BaseTemplatizedPromptGenerator, GeneratorConfig
from .dan import (
    Dan_11_0,
    Dan_10_0,
    Dan_9_0,
    Dan_8_0,
    Dan_7_0,
    Dan_6_2,
    Dan_6_0,
    DUDE,
    STAN,
    DAN_Jailbreak,
    AntiDAN,
    ChatGPT_Developer_Mode_v2,
    ChatGPT_Developer_Mode_RANTI,
    ChatGPT_Image_Markdown,
    Ablation_Dan_11_0,
    DanInTheWild,
    DanInTheWildMini,
)
from .continuation import ContinueSlursReclaimedSlurs80
from .suffix import GCGCached
from .donotanswer import (
    DNA_DiscriminationExclusionToxicityHatefulOffensive, 
    DNA_HumanChatbox, 
    DNA_InformationHazard, 
    DNA_MaliciousUses, 
    DNA_MisinformationHarms)
from ..generators.encoding import (
    InjectBase64, InjectBase16, InjectBase32, 
    InjectAscii85, InjectHex, InjectQP, InjectUU,
    InjectMime, InjectROT13, InjectBase2048, 
    InjectBraille, InjectMorse, InjectNato, 
    InjectEcoji, InjectZalgo)

from ..generators.prompt_injection import (
    HijackHateHumans,
    HijackHateHumansMini,
    HijackKillHumans,
    HijackKillHumansMini,
    HijackLongPrompt,
    HijackLongPromptMini
)

from ..generators.glitch import (
    Glitch,
    Glitch100
)

from ..generators.replay import (
    Repeat,
    RepeatExtended
)

from ..domain.modelio import Prompt, ProbeContext

class PromptsGeneratorFilter(object):
    
    def __init__(self, active=True, speed:int=5, 
                tags:List[str]=None, 
                technique:str=None,
                threat_class:str=None, 
                threat_category:str=None):
        self.tags = tags
        self.speed = speed
        self.active = active
        # dan, continuation, suffix-adversarial, donotanswer-dataset, 
        # indirect-prompt-injection-encoding, prompt-injection,
        # glitch-tokens, replay-poem-like-attack
        self.technique = technique
        self.threat_class = threat_class
        self.threat_category = threat_category
        

class PromptsGeneratorContext(object):
    def __init__(self, filter:PromptsGeneratorFilter=None, generator_config=None):
        self.filter = filter or PromptsGeneratorFilter()
        self.generator_config = generator_config or GeneratorConfig()
        

class StringrayPromptInstance:
    
    def __init__(self, prompt:Prompt, context:ProbeContext, module_name:str):
        self.prompt = prompt
        self.context = context
        self.module_name = module_name
        
class StingrayPromptsGenerator:
    """
    StingrayPromptsGenerator is a class that maintains instances of all DAN prompt generators
    and provides a method to generate (Prompt, ProbeContext) tuples.
    """
    DEFAULT_GENERATORS = {
        "Dan_11_0": Dan_11_0,
        "Dan_10_0": Dan_10_0,
        "Dan_9_0": Dan_9_0,
        "Dan_8_0": Dan_8_0,
        "Dan_7_0": Dan_7_0,
        "Dan_6_2": Dan_6_2,
        "Dan_6_0": Dan_6_0,
        "DUDE": DUDE,
        "STAN": STAN,
        "DAN_Jailbreak": DAN_Jailbreak,
        "AntiDAN": AntiDAN,
        "ChatGPT_Developer_Mode_v2": ChatGPT_Developer_Mode_v2,
        "ChatGPT_Developer_Mode_RANTI": ChatGPT_Developer_Mode_RANTI,
        "ChatGPT_Image_Markdown": ChatGPT_Image_Markdown,
        "Ablation_Dan_11_0": Ablation_Dan_11_0,
        "DanInTheWild": DanInTheWild,
        "DanInTheWildMini": DanInTheWildMini,
        "ContinueSlursReclaimedSlurs80": ContinueSlursReclaimedSlurs80,
        "GCGCached": GCGCached,
        "DNA_DiscriminationExclusionToxicityHatefulOffensive": DNA_DiscriminationExclusionToxicityHatefulOffensive,
        "DNA_HumanChatbox": DNA_HumanChatbox,
        "DNA_InformationHazard": DNA_InformationHazard,
        "DNA_MaliciousUses": DNA_MaliciousUses,
        "DNA_MisinformationHarms": DNA_MisinformationHarms,
        "InjectBase64": InjectBase64,
        "InjectBase16": InjectBase16,
        "InjectBase32": InjectBase32,
        "InjectAscii85": InjectAscii85,
        "InjectHex": InjectHex,
        "InjectQP": InjectQP,
        "InjectUU": InjectUU,
        "InjectMime": InjectMime,
        "InjectROT13": InjectROT13,
        "InjectBase2048": InjectBase2048,
        "InjectBraille": InjectBraille,
        "InjectMorse": InjectMorse,
        "InjectNato": InjectNato,
        "InjectEcoji": InjectEcoji,
        "InjectZalgo": InjectZalgo,
        "HijackHateHumans": HijackHateHumans,
        "HijackHateHumansMini": HijackHateHumansMini,
        "HijackKillHumans": HijackKillHumans,
        "HijackKillHumansMini": HijackKillHumansMini,
        "HijackLongPrompt": HijackLongPrompt,
        "HijackLongPromptMini": HijackLongPromptMini,
        "Glitch": Glitch,
        "Glitch100": Glitch100,
        "Repeat": Repeat,
        "RepeatExtended": RepeatExtended,
        
    }

    def __init__(self, context: PromptsGeneratorContext = None):
        self.context = context or PromptsGeneratorContext()
        self.generators = self._apply_filter(self.context)
        self.context_map = {name: generator.create_probe_context() for name, generator in self.generators.items()}

    def _apply_filter(self, context: PromptsGeneratorContext):
        filtered_generators = {}
        for name, generator_cls in self.DEFAULT_GENERATORS.items():
            # generator = generator_cls(context.generator_config)
            # First apply filter on the classes and then instantiate to prevent slower generators
            if self._matches_filter(name, generator_cls, context.filter):
                # print("Instantiating class: ", generator_cls)
                filtered_generators[name] = generator_cls(context.generator_config)
        return filtered_generators

    def _matches_filter(self, mod_name:str, generator:BaseTemplatizedPromptGenerator, 
                        filter: PromptsGeneratorFilter):
        if generator.speed < filter.speed:
            return False
        if filter.tags:
            tags = [tag.lower() for tag in generator.tags]
            if not any(tag in tags for tag in filter.tags):
                return False
        if filter.technique:
            if filter.technique.lower() != mod_name.lower():
                return False
        if filter.threat_class:
            if filter.threat_class.lower() not in generator.threat_class.lower():
                return False
        if filter.threat_category:
            if filter.threat_category.lower() not in generator.threat_category.lower():
                return False
        if generator.active != filter.active:
            return False
        return True

    def get_generators(self):
        for mod_name, gen in self.generators.items():
            yield mod_name, gen

    def generate(self, technique: str = None) -> Iterator[StringrayPromptInstance]:
        """
        Generate (Prompt, ProbeContext) tuples.
        
        Args:
            technique (str): The specific DAN technique to use. If None, all techniques are used.
        
        Yields:
            (Prompt, ProbeContext): The next prompt and its associated probe context.
        """
        if technique:
            if technique in self.generators:
                generator = self.generators[technique]
                context = self.context_map[technique]
                for prompt in generator.generate():
                    yield StringrayPromptInstance(prompt, context, technique)
            else:
                raise ValueError(f"Technique '{technique}' is not recognized.")
        else:
            for name, generator in self.generators.items():
                context = self.context_map[name]
                for prompt in generator.generate():
                    yield StringrayPromptInstance(prompt, context, name)

    @classmethod
    def get_all_module_names(cls):
        """
        Get the list of available DAN techniques.
        
        Returns:
            list: A list of available DAN technique names.
        """
        return list(cls.DEFAULT_GENERATORS.keys())

    def get_module_names(self):
        """
        Get the list of filtered DAN techniques.
        
        Returns:
            list: A list of available DAN technique names.
        """
        return list(self.generators.keys())
