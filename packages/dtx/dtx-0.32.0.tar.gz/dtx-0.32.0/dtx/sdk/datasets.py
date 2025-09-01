import os
from typing import Dict, List, Literal

from dtx_models.analysis import PromptDataset


class DatasetAvailabilityError(RuntimeError):
    """Raised when a dataset cannot be used due to missing env-vars.
        Utility helpers for **runtime** dataset validation.

        Some prompt datasets require API keys or other secrets in order to download
        and cache the examples.  This module lets you:

        1. **Check** whether a single dataset is usable on the current machine.
        2. **List** every dataset that is currently available (all env-vars present).

        Typical usage
        -------------
        from dtx.sdk.dataset_availability import DatasetAvailability
        from dtx_models.analysis import PromptDataset

        # Single-dataset check -------------------------------------------------------
        DatasetAvailability.assert_available(PromptDataset.HF_LMSYS)   # raises if missing

        # Discover everything you can run -------------------------------------------
        print("Datasets ready on this box:")
        for ds in DatasetAvailability.available_datasets():
            print(" •", ds.value)
    
    """


class DatasetAvailability:
    """
    Static helpers that know *which* environment variables each dataset needs.

    Core API
    --------
    ✓ `assert_available(dataset)`   – raise if requirements are unmet  
    ✓ `is_available(dataset)`       – bool  
    ✓ `available_datasets()`        – list of PromptDataset enums
    """

    # --------------------------------------------------------------------- #
    # 1. Static permission matrix (adapted from CLI code)                    #
    # --------------------------------------------------------------------- #

    _DATASET_ENV_MAP: Dict[PromptDataset, Dict[Literal["all", "any"], List[str]]] = {
        PromptDataset.STINGRAY: {"all": [], "any": []},
        PromptDataset.STARGAZER: {"all": [], "any": ["OPENAI_API_KEY", "DETOXIO_API_KEY"]},
        PromptDataset.HF_BEAVERTAILS: {"all": [], "any": []},
        PromptDataset.HF_HACKAPROMPT: {"all": [], "any": []},
        PromptDataset.HF_JAILBREAKBENCH: {"all": [], "any": []},
        PromptDataset.HF_SAFEMTDATA: {"all": [], "any": []},
        PromptDataset.HF_FLIPGUARDDATA: {"all": [], "any": []},
        PromptDataset.HF_JAILBREAKV: {"all": [], "any": []},
        PromptDataset.HF_LMSYS: {"all": ["HF_TOKEN"], "any": []},
        PromptDataset.HF_AISAFETY: {"all": [], "any": []},
        PromptDataset.HF_AIRBENCH: {"all": [], "any": []},
        PromptDataset.HF_RENELLM: {"all": ["HF_TOKEN"], "any": []},
        PromptDataset.HF_XTREAM: {"all": [], "any": []},
        PromptDataset.XTREAM_JB: {"all": [], "any": ["OPENAI_API_KEY", "DETOXIO_API_KEY"]},
    }

    # --------------------------------------------------------------------- #
    # 2. Public helpers                                                     #
    # --------------------------------------------------------------------- #

    @classmethod
    def is_available(cls, dataset: PromptDataset) -> bool:
        """
        Return **True** if all *mandatory* and at least one of the *optional* env
        variables are present for the given dataset.  False otherwise.
        """
        reqs = cls._DATASET_ENV_MAP.get(dataset, {"all": [], "any": []})

        # All "all" vars must exist
        if any(os.getenv(var) is None for var in reqs["all"]):
            return False

        # At least one of "any" vars must exist (if list not empty)
        if reqs["any"] and not any(os.getenv(var) for var in reqs["any"]):
            return False

        return True

    @classmethod
    def assert_available(cls, dataset: PromptDataset) -> None:
        """
        Raise `DatasetAvailabilityError` if the dataset cannot be used.

        Returns
        -------
        None
            Pure side-effect method; success implies the dataset is usable.
        """
        if cls.is_available(dataset):
            return

        reqs = cls._DATASET_ENV_MAP.get(dataset, {"all": [], "any": []})
        missing_all = [v for v in reqs["all"] if os.getenv(v) is None]
        missing_any_group = reqs["any"] if reqs["any"] and not any(os.getenv(v) for v in reqs["any"]) else []

        missing_vars = ", ".join(missing_all + missing_any_group)
        raise DatasetAvailabilityError(
            f"Dataset '{dataset.value}' is unavailable. "
            f"Missing environment variables: {missing_vars or '<unspecified>'}"
        )

    @classmethod
    def available_datasets(cls) -> List[PromptDataset]:
        """
        Return a **list of datasets** that meet their environment requirements.
        The list is sorted by the enum value for determinism.
        """
        return sorted(
            [ds for ds in PromptDataset if cls.is_available(ds)],
            key=lambda d: d.value.lower(),
        )
