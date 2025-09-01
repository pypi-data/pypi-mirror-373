from typing import List, Dict, Type
from .dan import (
    DAN,
    AntiDAN,
    DANJailbreak,
    STAN,
    DUDE,
    DevMode,
    MarkdownLink,
)

from .continuation import Continuation

from ..domain.modelio import ModelProbe
from .base import  Evaluator
from .mitigation import MitigationBypass
from .encoding import DecodeApprox, DecodeMatch
from .prompt_injection import AttackRogueString
from .goodside import Glitch
from .replay import RepeatDiverges

class EvaluatorContext:
    """
    EvaluatorContext is a class that defines the context for an evaluator.
    """
    pass  # Define this class according to your specific requirements

class EvaluatorManager:
    """
    Evaluator is a class that maintains instances of evaluators and provides a method to evaluate a probe.
    """
    def __init__(self, context: EvaluatorContext=None):
        self.context = context or EvaluatorContext()
        self.evaluators_map: Dict[str, Type[Evaluator]] = {
            "mitigation.MitigationBypass": MitigationBypass,
            "dan.DAN": DAN,
            "dan.AntiDAN": AntiDAN,
            "dan.DANJailbreak": DANJailbreak,
            "dan.STAN": STAN,
            "dan.DUDE": DUDE,
            "dan.DevMode": DevMode,
            "dan.MarkdownLink": MarkdownLink,
            "continuation.Continuation": Continuation,
            "encoding.DecodeMatch": DecodeMatch,
            "encoding.DecodeApprox": DecodeApprox,
            "prompt_injection.AttackRogueString": AttackRogueString,
            "goodside.Glitch": Glitch,
            "replay.RepeatDiverges": RepeatDiverges,
        }
        self.evaluators_instances = {
            name: evaluator(context)
            for name, evaluator in self.evaluators_map.items()
        }

    def evaluate(self, evaluator_name: str, 
                 attempt: ModelProbe, 
                 case_sensitive=False) -> List[float]:
        """
        Evaluate the probe using the specified evaluator.
        
        Args:
            evaluator_name (str): The name of the evaluator to use.
            attempt (BaseModelProbe): The probe to evaluate.
            case_sensitive (bool): Whether the evaluation should be case sensitive.
            
        Returns:
            List[float]: The evaluation results.
        """
        if evaluator_name not in self.evaluators_instances:
            raise ValueError(f"Evaluator '{evaluator_name}' is not recognized.")
        
        evaluator = self.evaluators_instances[evaluator_name]
        return evaluator.evaluate(attempt, case_sensitive)

    def get_evaluators(self) -> List[str]:
        """
        Get the list of available evaluators.
        
        Returns:
            List[str]: A list of available evaluator names.
        """
        return list(self.evaluators_map.keys())

# # Example usage
# if __name__ == "__main__":
#     context = EvaluatorContext()  # Initialize context as per your requirements
#     wrapper = EvaluatorWrapper(context)

#     # List available evaluators
#     evaluators = wrapper.get_evaluators()
#     print("Available evaluators:", evaluators)

#     # Create a dummy BaseModelProbe instance for testing
#     attempt = BaseModelProbe()  # Define BaseModelProbe according to your specific requirements

#     # Evaluate using a specific evaluator
#     results = wrapper.evaluate("dan.DAN", attempt)
#     print("Evaluation results:", results)