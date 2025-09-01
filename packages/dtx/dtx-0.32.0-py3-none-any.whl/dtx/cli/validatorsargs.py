import os
from pathlib import Path
from typing import Optional, Set, Dict, List

from .datasetargs import DatasetArgs
from .evaluatorargs import EvalMethodArgs
from dtx.sdk.datasets import DatasetAvailability  # unified source of truth
from dtx.core import logging


class EnvValidator:
    """
    Central environment‑variable validator for **datasets** and **evaluation methods**.

    ▸ Uses the *single* authority (`DatasetAvailability`) for dataset requirements.
    ▸ Falls back to each eval‑method's declared `env_vars` list.
    ▸ Raises a clear, multi‑line `EnvironmentError` when requirements are unmet.
    """
    logger = logging.getLogger("EnvValidator")


    # ------------------------------------------------------------------ #
    # 🛠  Public helpers                                                 #
    # ------------------------------------------------------------------ #

    @classmethod
    def validate(cls, dataset: Optional[str] = None, eval_name: Optional[str] = None):
        """Validate that all necessary environment variables are present.

        Parameters
        ----------
        dataset : Optional[str]
            Dataset *short‑name* or canonical name (as accepted by ``DatasetArgs``).
        eval_name : Optional[str]
            Evaluation method name (case‑insensitive, as defined in ``EvalMethodArgs``).
        """
        missing_vars: Set[str] = set()
        extra_messages: List[str] = []

        # -------------------------------------------------------------- #
        # 📦 Dataset checks
        # -------------------------------------------------------------- #
        if dataset:
            dataset_enum = cls._resolve_dataset_enum(dataset)
            # Retrieve the full requirements for pretty logging:
            reqs: Dict[str, List[str]] = DatasetAvailability._DATASET_ENV_MAP.get(  # type: ignore[attr-defined]  # noqa: E501
                dataset_enum, {"all": [], "any": []}
            )
            cls.logger.info(f"🔍 Checking env vars for dataset '{dataset_enum.value}': {reqs}")

            # Use the authoritative helper – no duplicated logic needed ✅
            if not DatasetAvailability.is_available(dataset_enum):
                # Replicate the fine‑grained feedback expected by the CLI
                missing_vars.update(cls._check_all(reqs["all"]))
                if reqs["any"] and not cls._check_any(reqs["any"]):
                    extra_messages.append(
                        f"Dataset '{dataset_enum.value}' requires at least one of: {', '.join(reqs['any'])}"
                    )

        # -------------------------------------------------------------- #
        # 📊 Evaluation‑method checks
        # -------------------------------------------------------------- #
        if eval_name:
            eval_cfg = EvalMethodArgs.EVAL_CHOICES.get(eval_name.lower())
            if eval_cfg:
                eval_envs = eval_cfg.get("env_vars", [])
                cls.logger.info(f"🔍 Checking env vars for eval '{eval_name}': {eval_envs}")
                missing_vars.update(cls._check_all(eval_envs))
            else:
                raise ValueError(f"Unknown evaluation method '{eval_name}'")

        # -------------------------------------------------------------- #
        # 🚦 Final decision
        # -------------------------------------------------------------- #
        if missing_vars or extra_messages:
            cls._raise_error(missing_vars, extra_messages)

    # ------------------------------------------------------------------ #
    # 🔒 Internal helpers                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _check_all(vars_list):
        """Return the subset of *required* vars that are missing."""
        return {var for var in vars_list if not os.getenv(var)}

    @staticmethod
    def _check_any(vars_list):
        """Return **True** iff *any* of the given vars is present."""
        return any(os.getenv(var) for var in vars_list)

    @classmethod
    def _raise_error(cls, missing_vars: Set[str], extra_messages: List[str]):
        msg_lines: List[str] = []

        if missing_vars:
            msg_lines.append(
                "🚨 Missing environment variables: " + ", ".join(sorted(missing_vars))
            )
        if extra_messages:
            msg_lines.extend(["🚨 " + m for m in extra_messages])

        env_file = cls._find_env_file()
        if env_file:
            msg_lines.append(f"\n💡 You can update your environment variables in: {env_file}")
        else:
            msg_lines.append("\n💡 Consider creating a .env file to store environment variables.")

        raise EnvironmentError("\n".join(msg_lines))

    @staticmethod
    def _find_env_file():
        """Search a few conventional locations for a *.env* file."""
        candidates = [
            Path.cwd() / ".env",
            Path.home() / ".dtx" / ".env",
            Path.cwd() / "config" / ".env",
        ]
        for path in candidates:
            if path.is_file():
                return str(path)
        return None

    # ------------------------- Dataset resolution --------------------- #
    @staticmethod
    def _resolve_dataset_enum(dataset_input: str):
        dataset_input = dataset_input.strip().lower()
        dataset_enum = DatasetArgs.ALL_DATASETS.get(dataset_input)
        if not dataset_enum:
            valid = ", ".join(sorted(DatasetArgs.ALL_DATASETS.keys()))
            raise ValueError(f"Unknown dataset '{dataset_input}'. Valid options: {valid}")
        return dataset_enum

    # ----------------------- Optional debug helper -------------------- #
    @classmethod
    def list_all_dependencies(cls):
        """Return a dict of every dataset/eval and its env‑var requirements."""
        return {
            "datasets": DatasetAvailability._DATASET_ENV_MAP,  # type: ignore[attr-defined]
            "evals": {
                name: cfg.get("env_vars", [])
                for name, cfg in EvalMethodArgs.EVAL_CHOICES.items()
            },
        }
