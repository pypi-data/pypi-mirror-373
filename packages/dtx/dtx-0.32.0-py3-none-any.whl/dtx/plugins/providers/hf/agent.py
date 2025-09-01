# The `HFAgent` class is a Python class that utilizes the Hugging Face pipeline for text generation
# and classification tasks within multi-turn conversations.
from typing import Dict, List, Optional, Union

from dtx.core import logging
from dtx_models.evaluator import EvaluatorInScope
from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    BaseMultiTurnResponseBuilder,
    RoleType,
    Turn,
)
from dtx_models.providers.hf import (
    HuggingFaceProviderConfig,
    HuggingFaceTask,
    SupportedFormat,
    ClassificationModelScope
)

from dtx.plugins.providers.hf.base.pipeline import HuggingFacePipeline


from ..base.agent import BaseAgent


class HFAgent(BaseAgent):
    logger = logging.getLogger(__name__)

    def __init__(self, provider: HuggingFaceProviderConfig):
        self._provider = provider
        self._pipeline = None
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initialize the Hugging Face pipeline if not already initialized."""
        if not self._pipeline:
            self._pipeline = HuggingFacePipeline(provider=self._provider)

    def get_preferred_evaluator(self) -> Optional[EvaluatorInScope]:
        """
        Return Preferred Evaluator if exists
        """
        return self._provider.preferred_evaluator

    def generate(
        self, prompt: str, system_prompt: str = None
    ) -> Union[str, Dict[str, float], List[Dict[str, Union[str, float]]]]:
        """
        Generates a response using the Hugging Face pipeline for single-turn text generation or classification.
        """
        formatted_prompt = (
            BaseMultiTurnResponseBuilder()
            .add_prompt(prompt, system_prompt)
            .build()
            .to_format(
                supported_format=self._provider.supported_input_format, multi_turn=False
            )
        )

        pipeline_output = self._pipeline.run_pipeline(formatted_prompt)
        return self._extract_response(pipeline_output)

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        """
        Handles multi-turn conversations based on the task type and format.
        Returns:
            - `BaseMultiTurnResponse` for text-generation tasks.
            - `BaseMultiTurnAgentResponse` for classification tasks.
        """
        if self._provider.task == HuggingFaceTask.TEXT_CLASSIFICATION:
            return self._handle_classification_conversation(prompt)
        else:
            return self._handle_generation_conversation(prompt)

    # ===================================================
    # HANDLING TEXT GENERATION TASKS
    # ===================================================

    def _handle_generation_conversation(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        """
        Processes a multi-turn conversation for text generation.
        """
        builder = BaseMultiTurnResponseBuilder()
        builder.add_prompt_attributes(prompt)

        if self._provider.support_multi_turn:
            return self._process_multi_turn_generation(prompt, builder)
        else:
            return self._process_single_turn_generation(prompt, builder)

    def _process_multi_turn_generation(
        self, prompt: BaseMultiTurnConversation, builder: BaseMultiTurnResponseBuilder
    ) -> BaseMultiTurnAgentResponse:
        """
        Handles multi-turn generation where user and assistant alternate turns.
        """
        if prompt.has_system_turn():
            builder.add_turn(prompt.get_system_turn())

        for turn in prompt.get_user_turns():
            builder.add_turn(turn)
            formatted_prompt = builder.build().to_format(
                supported_format=self._provider.supported_input_format,
                multi_turn=True,
            )

            pipeline_output = self._pipeline.run_pipeline(formatted_prompt)
            assistant_response = self._extract_response(pipeline_output) or "Empty Response"

            builder.add_turn(Turn(role=RoleType.ASSISTANT, message=assistant_response))
        return builder.build()

    def _process_single_turn_generation(
        self, prompt: BaseMultiTurnConversation, builder: BaseMultiTurnResponseBuilder
    ) -> BaseMultiTurnAgentResponse:
        """
        Handles a single-turn conversation for text generation.
        """
        if prompt.has_system_turn():
            builder.add_turn(prompt.get_system_turn())

        for turn in prompt.get_user_turns():
            builder.add_turn(turn)
            break  # Process only the first user turn

        formatted_prompt = builder.build().to_format(
            supported_format=self._provider.supported_input_format,
            multi_turn=False,
        )

        pipeline_output = self._pipeline.run_pipeline(formatted_prompt)
        assistant_response = self._extract_response(pipeline_output) or "Empty Response"

        builder.add_turn(Turn(role=RoleType.ASSISTANT, message=assistant_response))
        return builder.build()

    # ===================================================
    # HANDLING CLASSIFICATION TASKS
    # ===================================================

    def _handle_classification_conversation(
        self, prompt: BaseMultiTurnConversation
    ) -> BaseMultiTurnAgentResponse:
        """
        Run a classification pipeline over the conversation according to
        `classification_model_scope` and return a `BaseMultiTurnAgentResponse`
        whose `scores` field is a fully-formed `ClassificationScores`.
        """
        scope = self._provider.classification_model_scope
        input_format = self._provider.supported_input_format

        # --- Builder initialised with turns + prompt meta -----------------
        builder = (
            BaseMultiTurnResponseBuilder()
            .add_turns(prompt.turns)
            .add_prompt_attributes(prompt)
        )

        # Helper: run HF pipeline on some text & record scores in builder
        def _classify(text: str):
            response = self._extract_response(self._pipeline.run_pipeline(text))
            # `response` is expected to be {label: score, ...}
            builder.add_label_scores(response)

        # --------- Collect raw scores based on scope ----------------------
        if scope == ClassificationModelScope.PROMPT:
            for turn in prompt.get_user_turns():
                _classify(turn.message)

        elif scope == ClassificationModelScope.RESPONSE:
            for turn in prompt.turns:
                if turn.role == RoleType.ASSISTANT:
                    _classify(turn.message)

        elif scope == ClassificationModelScope.CONVERSATION:
            formatted = prompt.to_format(input_format, multi_turn=False)
            _classify(formatted)

        else:
            raise ValueError(f"Unsupported classification scope: {scope}")

        # --------- Build & return final agent response --------------------
        return builder.build()


    # ===================================================
    # RESPONSE EXTRACTION
    # ===================================================

    def _extract_response(
        self, pipeline_output
    ) -> Union[str, Dict[str, float], List[Dict[str, Union[str, float]]]]:
        """
        Extracts the appropriate response from the pipeline output based on the task type and format.
        """

        task = self._provider.task
        input_format = self._provider.supported_input_format  # OpenAI, Alpaca, etc.

        if task in {
            HuggingFaceTask.TEXT_GENERATION,
            HuggingFaceTask.TEXT2TEXT_GENERATION,
        }:
            # If the model expects OpenAI format, extract response differently
            if input_format == SupportedFormat.OPENAI:
                return pipeline_output[0]["generated_text"][-1][
                    "content"
                ]  # OpenAI-like output
            else:
                return pipeline_output[0]["generated_text"]  # Default HF output

        elif task == HuggingFaceTask.TEXT_CLASSIFICATION:
            return {result["label"]: result["score"] for result in pipeline_output}

        elif task == HuggingFaceTask.TOKEN_CLASSIFICATION:
            return [
                {
                    "word": entity["word"],
                    "entity": entity["entity"],
                    "score": entity["score"],
                }
                for entity in pipeline_output
            ]

        elif task == HuggingFaceTask.FILL_MASK:
            return [result["sequence"] for result in pipeline_output]

        else:
            raise ValueError(f"Unsupported HuggingFaceTask: {task}")
