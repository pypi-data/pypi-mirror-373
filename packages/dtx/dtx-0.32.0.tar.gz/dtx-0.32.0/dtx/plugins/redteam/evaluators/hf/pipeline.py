from enum import Enum
from typing import Any, Dict, Union

from transformers import AutoTokenizer, pipeline

try:
    import torch
except ModuleNotFoundErrorError:
    print(
        "[WARN] torch is not found. dtx will be limited in its functionality. If required, run pip install dtx[torch] to install full version of dtx."
    )


class HFPipelineError(Exception):
    """Custom exception for HuggingFacePipeline errors."""

    def __init__(self, message: str):
        super().__init__(f"HFPipelineError: {message}")


class HuggingFaceTask(str, Enum):
    TEXT_GENERATION = "text-generation"
    TEXT2TEXT_GENERATION = "text2text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    TOKEN_CLASSIFICATION = "token-classification"
    FEATURE_EXTRACTION = "feature-extraction"
    SENTENCE_SIMILARITY = "sentence-similarity"
    FILL_MASK = "fill-mask"


class DType(str, Enum):
    FLOAT16 = "float16"
    BFLOAT16 = "bfloat16"
    FLOAT32 = "float32"


class HuggingFacePipeline:
    def __init__(
        self, task: HuggingFaceTask, model_name: str, config: Dict[str, Any] = None
    ):
        self.task = task
        self.model_name = model_name
        self.config = config or {}

        try:
            torch_dtype = self._to_torch_dtype(self.config.get("dtype"))
            self.pipeline = pipeline(
                self.task, model=self.model_name, torch_dtype=torch_dtype
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        except OSError as e:
            raise HFPipelineError(
                f"Model '{self.model_name}' not found or corrupted: {e}"
            )
        except Exception as e:
            raise HFPipelineError(
                f"Failed to initialize pipeline for model '{self.model_name}': {e}"
            )

    def run_pipeline(self, input_text: Union[str, Dict]) -> Any:
        """
        Runs the pipeline with input_text, ensuring truncation based on max_token_length.
        Handles errors and raises HFPipelineError when necessary.
        """
        try:
            # Get max_token_length from config or fallback to model_max_length
            max_length = self.config.get(
                "max_token_length", self.tokenizer.model_max_length
            )

            # Avoid unreasonably large values
            if max_length > 4096:
                max_length = 512  # Set a reasonable limit

            # If input is a string, truncate it before passing to the model
            if isinstance(input_text, str):
                tokenized = self.tokenizer(
                    input_text,
                    truncation=True,
                    max_length=max_length,
                    return_tensors="pt",
                )
                input_text = self.tokenizer.decode(
                    tokenized["input_ids"][0], skip_special_tokens=True
                )

            config_params = self._get_task_specific_params(self.config, self.task)

            return self.pipeline(input_text, **config_params)

        except RuntimeError as e:
            raise HFPipelineError(
                f"Pipeline execution failed due to tensor mismatch: {e}"
            )
        except ValueError as e:
            raise HFPipelineError(f"Invalid input to the pipeline: {e}")
        except Exception as e:
            raise HFPipelineError(f"Unexpected error during pipeline execution: {e}")

    def _to_torch_dtype(self, dtype: DType) -> torch.dtype:
        dtype_mapping = {
            DType.BFLOAT16: torch.bfloat16,
            DType.FLOAT16: torch.float16,
            DType.FLOAT32: torch.float32,
        }
        return dtype_mapping.get(dtype, torch.float32)

    def _get_task_specific_params(
        self, params: Dict[str, Any], task: HuggingFaceTask
    ) -> Dict[str, Any]:
        supported_params = {
            HuggingFaceTask.TEXT_GENERATION: {
                "temperature",
                "top_k",
                "top_p",
                "repetition_penalty",
                "max_new_tokens",
                "do_sample",
            },
            HuggingFaceTask.TEXT_CLASSIFICATION: set(),
            HuggingFaceTask.TOKEN_CLASSIFICATION: set(),
            HuggingFaceTask.FEATURE_EXTRACTION: set(),
            HuggingFaceTask.SENTENCE_SIMILARITY: set(),
            HuggingFaceTask.FILL_MASK: set(),
        }
        return {
            key: value
            for key, value in params.items()
            if key in supported_params.get(task, set())
        }
