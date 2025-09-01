import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, Iterator, List

from dtx.core import logging
from dtx_models.analysis import PromptDataset
from dtx.plugins.redteam.dataset.hf.adapters.base import (
    BaseRiskPromptGenerator,
    MultiTurnConversation,
)


class RiskPromptWrapper:
    """
    A wrapper class that encapsulates the risk prompt generator to prevent direct corruption.
    """

    def __init__(self, generator: BaseRiskPromptGenerator):
        """
        Initializes the wrapper with a specific risk prompt generator.

        :param generator: An instance of BaseRiskPromptGenerator.
        """
        self._generator = generator

    def support_risk_class(self, risk_class: str) -> bool:
        return self._generator.support_risk_class(risk_class)

    def get_supported_risk_classes(self) -> List[str]:
        return self._generator.get_supported_risk_classes()

    def generate(self, risk_name: str) -> Iterator[MultiTurnConversation]:
        """
        Calls the wrapped generator's `generate` method.

        :param risk_name: The risk name to generate conversations for.
        :return: An iterator over MultiTurnConversation objects.
        """
        return self._generator.generate(risk_name)

    def is_available(self) -> bool:
        return self._generator.is_available()

    def get_description(self) -> str:
        return self._generator.get_description()

    def get_goals(self, risk_class):
        """Retrieve goals for a given risk class"""
        return self._generator.get_goals(risk_class=risk_class)

    def get_labels(self, risk_class: str) -> List[str]:
        """
        Retrieves labels related to the risk_class
        """
        category_labels = self._generator.get_labels(risk_class)
        return category_labels

    def get_risk_summary(self, risk_class: str) -> str:
        """
        Create and return risk summary based on the dataset context
        """
        labels = self.get_labels(risk_class)
        return f"Generate various prompts related to categories {labels}"

    def get_all_goals(self) -> List[str]:
        return self._generator.get_all_goals()


class HFPromptsGenerator:
    """
    A class that dynamically loads risk prompt generators and provides a method to retrieve
    a wrapped generator instance for a dataset.
    """

    CLASS_NAME = "RiskPromptGenerator"
    ATTRIBUTE_NAME = "REGISTERED_DATASET_NAME"

    def __init__(self):
        """
        Initializes the HFPromptsGenerator by loading all available adapters.
        """
        self.dataset_map: Dict[PromptDataset, BaseRiskPromptGenerator] = (
            self._load_classes_from_directory("adapters")
        )
        logging.info(f"Loaded {len(self.dataset_map)} risk prompt generators.")

    def _load_classes_from_directory(
        self, relative_dir: str
    ) -> Dict[PromptDataset, BaseRiskPromptGenerator]:
        """
        Private method to load all RiskPromptGenerator classes from a given directory.

        :param relative_dir: Relative directory containing risk prompt generator modules.
        :return: A dictionary mapping dataset names to their corresponding generator classes.
        """
        script_dir = Path(__file__).parent.resolve()
        abs_dir = script_dir / relative_dir
        dataset_class_map = {}

        if not abs_dir.exists() or not abs_dir.is_dir():
            raise ValueError(f"Directory {abs_dir} does not exist.")

        # Convert relative_dir to package-style notation
        package_name = ".".join(relative_dir.split(os.sep))  # Ensures correct format

        # Ensure the base directory is in sys.path for module resolution
        package_root = script_dir  # Adjust based on project structure
        sys.path.append(str(package_root))

        for file in abs_dir.glob("*.py"):
            if file.stem == "__init__":  # Skip __init__.py
                continue

            module_name = (
                f"{package_name}.{file.stem}"  # Correctly formatted module name
            )

            try:
                module = importlib.import_module(
                    module_name, package=package_name
                )  # Ensure package context

                # Iterate over all classes in the module
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__name__ == self.CLASS_NAME and hasattr(
                        obj, self.ATTRIBUTE_NAME
                    ):
                        dataset_name = getattr(obj, self.ATTRIBUTE_NAME)
                        if isinstance(dataset_name, str):
                            dataset_class_map[dataset_name] = obj

            except ImportError as e:
                logging.error(f"{file.stem} due to import error: {e}")
                raise e

        return dataset_class_map

    def get_generator(self, dataset: str) -> RiskPromptWrapper:
        """
        Retrieves a wrapped risk prompt generator for the given dataset.

        :param dataset: The dataset name.
        :return: An instance of RiskPromptWrapper that encapsulates BaseRiskPromptGenerator.
        :raises ValueError: If the dataset name is not registered.
        """
        if dataset not in self.dataset_map:
            raise ValueError(f"No registered generator for dataset: {dataset}")

        # Wrap the generator to prevent corruption
        return RiskPromptWrapper(self.dataset_map[dataset]())


# Example Usage
if __name__ == "__main__":
    generator = HFPromptsGenerator()

    # Example dataset name
    dataset_name = "some_dataset_name"

    try:
        risk_generator = generator.get_generator(dataset_name)
        for conversation in risk_generator.generate("example_risk_name"):
            print(conversation)
    except ValueError as e:
        logging.error(e)
