from typing import List, Optional

# Importing LangChain components for AI-driven prompt analysis
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from dtx.core import logging

# ------------------ BASE CLASSES ------------------


class BasePromptStructure(BaseModel):
    """
    Base class for structured prompt analysis.
    This class acts as a foundation for defining structured analysis results.
    """

    pass


class PromptSubparts(BaseModel):
    """
    Pydantic model to structure the extracted components of a given prompt.
    This model ensures the AI's output follows a structured format.
    """

    adversarial_prefix: Optional[List[str]] = Field(
        None,
        description="List of words or sentences acting as noise in the prompt prefix to confuse LLMs.",
    )
    adversarial_suffix: Optional[List[str]] = Field(
        None,
        description="List of words or sentences acting as noise in the prompt suffix to confuse LLMs.",
    )
    jailbreak: Optional[List[str]] = Field(
        None,
        description="List of sentences specifically used to bypass AI safeguards and jailbreak the model.",
    )
    goal: Optional[str] = Field(
        None, description="The inferred intent or objective behind the prompt."
    )
    harmful_words: Optional[List[str]] = Field(
        None, description="List of harmful words detected in the prompt."
    )
    harmful_sentences: Optional[List[str]] = Field(
        None, description="List of sentences containing harmful or unethical intent."
    )

    def __init__(self, **data):
        """
        Ensures harmful_words and harmful_sentences default to empty lists instead of None.
        """
        data.setdefault("harmful_words", [])
        data.setdefault("harmful_sentences", [])
        super().__init__(**data)


# ------------------ AI MODEL CHAIN ------------------


class PromptClassificationModelChain:
    """
    A class that builds a LangChain-powered AI model pipeline for analyzing adversarial prompts.

    The model uses OpenAI's ChatGPT (or any LLM) to:
    - Detect adversarial noise in prompt prefixes/suffixes
    - Identify jailbreak patterns
    - Extract harmful words and sentences
    - Infer the underlying intent (goal) of the prompt

    The model outputs structured data in the form of a Pydantic `PromptSubparts` object.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initializes the AI model with OpenAI's ChatGPT API.

        :param model_name: Name of the LLM model to use (e.g., "gpt-4o-mini").
        :param temperature: Controls response randomness (lower values = more deterministic).
        """
        self.model = ChatOpenAI(model=model_name, temperature=temperature)

        # Creates a JSON parser to ensure structured output matching the `PromptSubparts` schema
        self.parser = JsonOutputParser(pydantic_object=PromptSubparts)

        # Defines the system's prompt template with specific instructions
        self.prompt = PromptTemplate(
            template="""
You are a prompt moderation engine that provides detailed analysis of adversarial prompts. 
Your response must follow the provided structured format.

- **adversarial_prefix**: Any words or sentences acting as noise in the prefix to confuse LLMs.
- **adversarial_suffix**: Any words or sentences acting as noise in the suffix to confuse LLMs.
- **jailbreak**: Sentences used to bypass model restrictions.
- **harmful_words**: Explicitly harmful or unethical words in the prompt.
- **harmful_sentences**: Specific sentences that contain harmful or unethical intent.
- **goal**: The inferred intent of the prompt. Intent should have harmful words to make it more specific formatted as: "Intent is ..."

Algorithm
1. First identify if there are jailbreak techniques used. Identify jailbreak para, sentences
2. Identify the real intent or goal
2. identify harmful words and sentences
3. finally identify adversarial prefix and suffix. 

Whole prompt about the divided into the subparts

The prompt to analyze is enclosed within **<<prompt>>** tags.

<<prompt>>
{prompt}
<</prompt>>

""",
            input_variables=["prompt"],
        )

    def get_chain(self, schema: BasePromptStructure):
        """
        Constructs a LangChain pipeline to process prompts and return structured analysis.

        :param schema: A Pydantic model schema to enforce structured AI output.
        :return: A LangChain pipeline that combines the AI model with the prompt template.
        """
        # Enforces structured output format based on the provided schema (PromptSubparts)
        structured_llm = self.model.with_structured_output(schema=schema)

        # Combines the system prompt with the AI model to form an analysis chain
        chain = self.prompt | structured_llm
        return chain


# ------------------ PROMPT ANALYSIS CLASS ------------------


class PromptStructureAnalysis:
    """
    This class orchestrates the prompt analysis using LangChain and OpenAI.

    - It leverages the `PromptClassificationModelChain` to process adversarial prompts.
    - Returns a structured `PromptSubparts` object containing analyzed features.
    """

    logger = logging.getLogger(
        __name__
    )  # Logger for debugging and tracking analysis tasks

    def __init__(self, llm: PromptClassificationModelChain):
        """
        Initializes the PromptStructureAnalysis engine.

        :param llm: An instance of `PromptClassificationModelChain` for structured AI analysis.
        """
        # Creates an AI pipeline for detecting adversarial patterns in prompts
        self.analysis_chain = llm.get_chain(schema=PromptSubparts)

    def analyze(self, prompt_text: str) -> PromptSubparts:
        """
        Analyzes a given prompt to detect adversarial noise, jailbreak attempts, harmful content, and intent.

        :param prompt_text: The input prompt to be analyzed.
        :return: A structured `PromptSubparts` object containing extracted features.
        """
        # Logs the start of threat analysis
        self.logger.info("Performing prompt analysis...")

        # Passes the prompt to the AI model chain and receives structured analysis
        threat_analysis = self.analysis_chain.invoke(
            {
                "prompt": prompt_text,
            }
        )

        # Logs the batch processing of prompt analysis
        self.logger.info("Generating structured analysis output...")

        return threat_analysis
