import torch

from typing import Any, Dict, Union
from transformers import pipeline
from dtx_models.providers.hf import DType, HuggingFaceProviderConfig


class HFPipelineError(Exception):
    """Custom exception for HuggingFacePipeline errors."""

    def __init__(self, message: str):
        super().__init__(f"HFPipelineError: {message}")


class HuggingFacePipeline:
    def __init__(self, provider: HuggingFaceProviderConfig):
        self.provider = provider
        self._task, model_name = provider.task, provider.model
        try:
            torch_dtype = (
                self._to_torch_dtype(provider.params.dtype)
                if provider.params and provider.params.dtype
                else None
            )
            self.pipeline = pipeline(
                self._task, model=model_name, torch_dtype=torch_dtype
            )

        except OSError as e:
            raise HFPipelineError(f"Model '{model_name}' not found or corrupted: {e}")
        except Exception as e:
            raise HFPipelineError(
                f"Failed to initialize pipeline for model '{model_name}': {e}"
            )

    def run_pipeline(self, input_text: Union[str, Dict]) -> Any:
        """
        Runs the pipeline with input_text, ensuring truncation based on max_token_length.
        Handles errors and raises HFPipelineError when necessary.
        """
        try:
            tokenizer = self.pipeline.tokenizer

            # Get max_token_length from config or fallback to model_max_length
            max_length = getattr(self.provider.params, "max_token_length", None)
            if max_length is None or max_length <= 0:
                max_length = getattr(
                    tokenizer, "model_max_length", 512
                )  # Default fallback

            # Avoid unreasonably large values (some models report huge max lengths)
            if max_length > 4096:
                max_length = 512  # Set a reasonable limit to prevent tensor mismatches

            # print(f"Using max_length: {max_length}")  # Debugging log

            # If input is a string, truncate it before passing to the model
            if isinstance(input_text, str):
                tokenized = tokenizer(
                    input_text,
                    truncation=True,
                    max_length=max_length,
                    return_tensors="pt",
                )
                input_text = tokenizer.decode(
                    tokenized["input_ids"][0], skip_special_tokens=True
                )

            config_params: Dict[str, Any] = {}

            if self.provider.params:
                task_specific_params = self._get_task_specific_params(
                    self.provider.params.model_dump(exclude_none=True), self._task
                )
                config_params.update(task_specific_params)
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
        self, params: Dict[str, Any], task: str
    ) -> Dict[str, Any]:
        supported_params = {
            "text-generation": {
                "temperature",
                "top_k",
                "top_p",
                "repetition_penalty",
                "max_new_tokens",
                "do_sample",
            },
            "text-classification": set(),
            "token-classification": set(),
            "feature-extraction": set(),
            "sentence-similarity": set(),
            "fill-mask": set(),
        }
        return {
            key: value
            for key, value in params.items()
            if key in supported_params.get(task, set())
        }
