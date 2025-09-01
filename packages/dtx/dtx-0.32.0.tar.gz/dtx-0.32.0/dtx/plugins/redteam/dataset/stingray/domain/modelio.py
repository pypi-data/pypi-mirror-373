from typing import List

class BasePrompt:
    """
    BasePrompt is a base class for prompts.
    
    This class doesn't contain any attributes or methods, but serves as a base for other prompt-related classes.
    """
    def __init__(self):
        pass
    
class EvaluationHint(object):
     
    def __init__(self, expected_next_words:str|List[str]=None):
        self.expected_next_words=expected_next_words or ""

class Prompt(BasePrompt):
    """
    Prompt is a class that represents a prompt with a goal and various optional attributes.
    
    Attributes:
        template (str): The prompt template.
        template_vars (list): A list of template variables associated with the prompt.
    """
    def __init__(self, prompt, 
                 template_vars: List = None, 
                 evaluation_hint:EvaluationHint=None):
        self.template = prompt
        self.template_vars = template_vars or []
        self.evaluation_hint = evaluation_hint

    def get(self, template_values: dict = None):
        """
        Get the prompt with the given template values applied.
        
        Args:
            template_values (dict): A dictionary of values to apply to the template.
            
        Returns:
            str: The prompt with the template values applied.
        """
        template_values = template_values or {}
        if template_values and self.template_vars:
            return self.template.format(**template_values)
        else:
            return self.template

    def is_a_template(self):
        """
        Check if the prompt is a template.
        
        Returns:
            bool: True if the prompt is a template, False otherwise.
        """
        return len(self.template_vars) > 0
    

class ProbeContext:
    """
    ProbeContext is a class used to define the context in which a model probe operates.
    
    Attributes:
        goal (str): The goal of the probe.
        tags (list): A list of tags associated with the probe.
        detectors (list): A list of detectors associated with the probe.
        references (list): A list of references associated with the probe.
    """
    def __init__(self, goal, tags: List = None, 
                    detectors: List = None, 
                    references: List = None,
                    threat_class:str=None, threat_category:str=None, 
                    technique:str=None):
        self.goal = goal or ''
        self.tags = tags or []
        self.detectors = detectors or []
        self.references = references or []
        self.threat_class = threat_class or ""
        self.threat_category = threat_category or ""
        self.technique = technique or ""

class BaseModelProbe(object):
    """
    BaseModelProbe is a base class for model probes.
    
    This class doesn't contain any attributes or methods, but serves as a base for other probe-related classes.
    """
    def __init__(self):
        pass
    
    def all_responses(self):
        """
        Method to retrieve all responses from the probe.
        
        Raises:
            Exception: If the method is not implemented in the subclass.
        """
        raise Exception("Method not implemented - all_responses")

class ModelProbe(BaseModelProbe):
    """
    ModelProbe is a class that represents a single-turn model probe.
    
    Attributes:
        prompt (Prompt): The prompt used in the probe.
        response (str): The response received from the model.
    """
    def __init__(self, prompt: Prompt, response: str=None, responses=None):
        self.prompt = prompt
        self._responses = []
        if responses:
            self._responses = responses
        else:
            self._responses.append(response)

    def all_responses(self) -> List[str]:
        """
        Retrieve all responses from the probe.
        
        Returns:
            list: A list containing the single response from the probe.
        """
        return self._responses


#
# TODO following should handle EvaluationHint

# class ModelMultiTurnProbe(BaseModelProbe):
#     """
#     ModelMultiTurnProbe is a class that represents a multi-turn model probe.
    
#     Attributes:
#         turns (list): A list of ModelProbe objects representing each turn in the conversation.
#     """
#     def __init__(self):
#         self.turns = []
    
#     def add(self, probe: ModelProbe):
#         """
#         Add a single-turn probe to the multi-turn probe.
        
#         Args:
#             probe (ModelProbe): The single-turn probe to add.
#         """
#         self.turns.append(probe)

#     def all_responses(self) -> List[str]:
#         """
#         Retrieve all responses from the multi-turn probe.
        
#         Returns:
#             list: A list containing all responses from each turn in the conversation.
#         """
#         return [probe.response for probe in self.turns]
