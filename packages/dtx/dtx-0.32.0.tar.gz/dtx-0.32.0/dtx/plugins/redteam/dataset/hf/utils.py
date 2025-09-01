import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Dict

from dtx.core import logging
from dtx_models.analysis import PromptDataset

from .adapters.base import BaseRiskPromptGenerator

CLASS_NAME = "RiskPromptGenerator"
ATTRIBUTE_NAME = "REGISTERED_DATASET_NAME"


def load_classes_from_directory(
    relative_dir: str,
) -> Dict[PromptDataset, BaseRiskPromptGenerator]:
    script_dir = Path(__file__).parent.resolve()
    abs_dir = script_dir / relative_dir
    dataset_class_map = {}

    if not abs_dir.exists() or not abs_dir.is_dir():
        raise ValueError(f"Directory {abs_dir} does not exist.")

    # Convert relative_dir to package-style notation
    package_name = ".".join(relative_dir.split(os.sep))  # Ensures correct format

    # Ensure the base directory is in sys.path for module resolution
    package_root = script_dir.parent.parent  # Adjust based on project structure
    sys.path.append(str(package_root))

    for file in abs_dir.glob("*.py"):
        if file.stem == "__init__":  # Skip __init__.py
            continue

        module_name = f"{package_name}.{file.stem}"  # Correctly formatted module name

        try:
            module = importlib.import_module(
                module_name, package=package_name
            )  # Ensure package context

            # Iterate over all classes in the module
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__name__ == CLASS_NAME and hasattr(obj, ATTRIBUTE_NAME):
                    dataset_name = getattr(obj, ATTRIBUTE_NAME)
                    if isinstance(dataset_name, str):
                        dataset_class_map[dataset_name] = obj

        except ImportError as e:
            logging.error(f"{file.stem} due to import error: {e}")
            raise e

    return dataset_class_map


# Map of Modules by registered names
HF_DATASET_MAP: Dict[PromptDataset, BaseRiskPromptGenerator] = (
    load_classes_from_directory("adapters")
)

# Example Usage
if __name__ == "__main__":
    dataset_map = HF_DATASET_MAP
    print(dataset_map)
