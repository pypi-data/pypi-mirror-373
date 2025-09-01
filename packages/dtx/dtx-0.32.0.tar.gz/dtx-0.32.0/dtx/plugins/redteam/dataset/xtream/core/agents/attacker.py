"""
AttackerAgent Class

Purpose:
---------
Simulate a red-team attacker executing a pre-generated multi-turn jailbreak strategy
against a target model.

Algorithm Overview:
--------------------
1. Initialize agent with a Behavior and Attack Strategy.
2. At each phase (turn), generate next attacker message:
    a. First Turn → Use first_turn_template
    b. Middle Turns → Use nth_turn_template
    c. Final Turn → Use final_turn_template
3. Send attack messages to target model.
4. Evaluate target model's response with a judge model.
5. Pick the best attempt and commit it.
6. If needed, revise the plan dynamically using LLM.
7. Track and log conversation history and scores.

Models used:
------------
- Behavior (BaseHarmfulBehaviour)
- Attack Strategy (AttackStrategy with ConversationPlan)
- Target Model (victim)
- Evaluation Model (judge)
"""

from typing import Optional

import tiktoken
import yaml


# from tenacity import retry, stop_after_attempt, wait_fixed
from .base import BaseAgent
from ...config.globals import XtreamGlobalConfig
from dtx_models.plugins.xtream.config import AttackerAgentConfig
from dtx_models.plugins.xtream.plan import AttackStrategy, BaseHarmfulBehaviour


class LLMRefusalError(Exception):
    """Raised when the attacker LLM refuses to generate a response."""

    pass


class AttackerAgent(BaseAgent):
    """Agent that executes multi-turn attack strategies based on pre-generated plans."""

    DEFAULT_CONFIG = XtreamGlobalConfig()
    def __init__(
        self,
        config: AttackerAgentConfig,
        behavior: BaseHarmfulBehaviour,
        strategy: AttackStrategy,
    ):
        """
        Initialize the attacker agent.

        Args:
            config: Model config (AttackerAgentConfig)
            behavior: The behavior we want the model to perform (BaseHarmfulBehaviour)
            strategy: The planned attack strategy (AttackStrategy)
        """
        super().__init__(config.model_dump())
        self.model_config = config  # Save typed config
        self.messages = []
        self.behavior = behavior
        self.strategy = strategy
        self.plan_phase = 1
        self.num_phases = (
            len(self.strategy.conversation_plan.turns) + 1
        )  # Turns + final turn
        self.plan_score_history = []
        self.next_message_candidates = []
        self._load_prompt_templates()

    def _load_prompt_templates(self) -> dict:
        """Load the attack agent's system and user templates from YAML (safely from package resources)."""
        
        prompt_file = self.DEFAULT_CONFIG.get_attacker_agent_prompts_path()

        with prompt_file.open("r", encoding="utf-8") as f:
            prompts = yaml.safe_load(f)["prompts"]

        self.system_prompt = prompts["system"]["messages"][0]["content"]
        self.first_turn_template = prompts["first_turn_messages"]["messages"][0][
            "content"
        ]
        self.nth_turn_template = prompts["nth_turn_messages"]["messages"][0]["content"]
        self.final_turn_template = prompts["final_turn_messages"]["messages"][0][
            "content"
        ]
        self.revise_plan_template = prompts["revise_plan_messages"]["messages"][0][
            "content"
        ]

        return prompts

    def commit(self):
        """Commit the best candidate from the current attack phase to the conversation history."""
        if not self.next_message_candidates:
            raise ValueError("No generated candidates to commit.")

        best_candidate = max(self.next_message_candidates, key=lambda x: x["score"])

        if self.plan_phase < self.num_phases:
            self.messages += best_candidate["messages"]
            self.plan_phase += 1
            self.plan_score_history.append(best_candidate["score"])
            self.next_message_candidates.clear()
        else:
            # Replace final turn
            self.messages[-2:] = best_candidate["messages"]
            self.plan_score_history[-1] = best_candidate["score"]

    # @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    def generate_response(self, conversation_history: Optional[str] = None) -> str:
        """Generate attacker message for current plan phase."""
        if self.plan_phase == 1:
            return self._generate_first_turn()
        elif self.plan_phase == self.num_phases:
            return self._generate_final_turn(conversation_history)
        else:
            return self._generate_nth_turn(conversation_history)

    def generate_and_evaluate_candidate(
        self, target, evaluator, conversation_history: Optional[str] = None
    ) -> dict:
        """
        Generate attack message, send to target, evaluate target's response.

        Args:
            target: Target model
            evaluator: Evaluation model
            conversation_history: Prior conversation history

        Returns:
            Dictionary containing evaluation results.
        """
        attack_generation = self.generate_response(conversation_history)
        target_response = target.generate_response(attack_generation)
        truncated_response = self._truncate_response(target_response)

        score, reason = evaluator.infer_single(
            self.behavior.behavior, truncated_response
        )

        self.next_message_candidates[-1]["score"] = score

        return {
            "phase": self.plan_phase,
            "attacker": attack_generation,
            "target": target_response,
            "target_truncated": truncated_response,
            "evaluation_score": score,
            "evaluation_reason": reason,
        }

    def _generate_first_turn(self) -> str:
        """Generate first conversation turn."""
        first_turn_flow = self.strategy.conversation_plan.turns[0]

        formatted_system_prompt = self.system_prompt.format(
            target_behavior=self.behavior.behavior,
            strategy=self._format_strategy(),
            max_turns=self.num_phases,
        )

        formatted_user_prompt = self.first_turn_template.format(
            turn_1_conversation_flow=first_turn_flow,
        )

        next_messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": formatted_user_prompt},
        ]

        response = self.call_api(
            messages=next_messages, temperature=self.model_config.temperature
        )
        next_messages.append({"role": "assistant", "content": response})
        self.next_message_candidates.append({"score": 0, "messages": next_messages})

        return self._extract_conversation(response)

    def _generate_nth_turn(self, conversation_history: str) -> str:
        """Generate intermediate conversation turns."""
        turn_text = self.strategy.conversation_plan.turns[self.plan_phase - 1]

        formatted_prompt = self.nth_turn_template.format(
            turn_number=self.plan_phase,
            conversation_history=conversation_history,
            turn_number_conversation_flow=turn_text,
            previous_turn_number=self.plan_phase - 1,
        )

        formatted_system_prompt = self.system_prompt.format(
            target_behavior=self.behavior.behavior,
            strategy=self._format_strategy(),
            max_turns=self.num_phases,
        )

        next_messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": formatted_prompt},
        ]

        response = self.call_api(
            messages=next_messages, temperature=self.model_config.temperature
        )
        next_messages.append({"role": "assistant", "content": response})
        self.next_message_candidates.append({"score": 0, "messages": next_messages})

        return self._extract_conversation(response)

    def _generate_final_turn(self, conversation_history: str) -> str:
        """Generate final conversation turn."""
        final_turn_flow = self.strategy.conversation_plan.final_turn

        formatted_prompt = self.final_turn_template.format(
            conversation_history=conversation_history,
            final_turn_conversation_flow=final_turn_flow,
        )

        formatted_system_prompt = self.system_prompt.format(
            target_behavior=self.behavior.behavior,
            strategy=self._format_strategy(),
            max_turns=self.num_phases,
        )

        next_messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": formatted_prompt},
        ]

        response = self.call_api(
            messages=next_messages, temperature=self.model_config.temperature
        )
        next_messages.append({"role": "assistant", "content": response})
        self.next_message_candidates.append({"score": 0, "messages": next_messages})

        return self._extract_conversation(response)

    # @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    def revise_plan(self, conversation_history: str = ""):
        """Revise attack strategy if plan fails."""
        formatted_system_prompt = self.system_prompt.format(
            target_behavior=self.behavior.behavior,
            strategy=self._format_strategy(),
            max_turns="as many turns as necessary",
        )

        formatted_prompt = (
            self.revise_plan_template.replace(
                "{target_behavior}", self.behavior.behavior
            )
            .replace("{turn_number}", str(self.plan_phase))
            .replace("{conversation_history}", conversation_history)
            .replace("{old_plan}", self.strategy.model_dump_json(indent=2))
            .replace("{previous_turn_number}", str(self.plan_phase - 1))
        )

        response = self.call_api(
            [
                {"role": "system", "content": formatted_system_prompt},
                {"role": "user", "content": formatted_prompt},
            ],
            temperature=self.model_config.temperature,
        )

        try:
            response_slice = response[response.find("{") : response.rfind("}") + 1]
            new_strategy = AttackStrategy.model_validate_json(response_slice)
            self.strategy = new_strategy
            self.num_phases = len(new_strategy.conversation_plan.turns) + 1
            return new_strategy
        except Exception as e:
            raise ValueError(f"Failed to parse revised plan: {e}\nResponse: {response}")

    def _truncate_response(self, response_text: str, max_tokens: int = 512) -> str:
        """Truncate long model responses to avoid overflow."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-4o-2024-08-06")
            tokens = encoding.encode(response_text)
            if len(tokens) <= max_tokens:
                return response_text
            return encoding.decode(tokens[:max_tokens])
        except Exception as e:
            print(f"Warning: Error in token counting: {e}")
            return response_text

    def _extract_conversation(self, response: str) -> str:
        """Extract text between <conversation>...</conversation>."""
        start = response.find("<conversation>") + len("<conversation>")
        end = response.find("</conversation>")
        return response[start:end].strip()

    def _format_strategy(self) -> str:
        """Format attack strategy nicely for prompts."""
        return "\n".join(
            [
                f"Persona: {self.strategy.persona}",
                f"Context: {self.strategy.context}",
                f"Approach: {self.strategy.approach}",
                f"Conversation Plan: {self.strategy.conversation_plan.model_dump_json(indent=2)}",
            ]
        )
