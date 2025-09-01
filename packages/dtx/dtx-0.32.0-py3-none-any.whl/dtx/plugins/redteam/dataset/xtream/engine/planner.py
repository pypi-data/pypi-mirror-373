import concurrent.futures
import random
from dtx.core import logging

from typing import Dict, List, Optional

from tenacity import retry, stop_after_attempt, wait_fixed

from ..core.agents.planner import AttackPlannerAgent
from dtx_models.plugins.xtream.plan import (
    XtreamAttackPlan,
    AttackPlannerPrompts,
    XtreamAttackPlans,
    AttackStrategy,
    BaseHarmfulBehaviour,
    ConversationPlan,
)


class AttackPlanGenerator:
    def __init__(
        self,
        agent: AttackPlannerAgent,
        prompts: AttackPlannerPrompts,
        behaviors: List[BaseHarmfulBehaviour],
        risk_name: str
    ):
        self.agent = agent
        self.prompts = prompts
        self.behaviors = behaviors
        self.risk_name = risk_name
        self._logger = logging.getLogger(__name__)

    def _format_prompts(
        self,
        behavior_text: str,
        set_number: int,
        previous_responses: Optional[Dict] = None,
        num_strategies:int = 10,
    ) -> List[Dict]:
        """Format system and user prompts."""
        system_prompt = self.prompts.prompts.system.messages[0].content

        if set_number == 1:
            user_prompt_template = (
                self.prompts.prompts.user_messages[0].messages[0].content
            )
            formatted_user_prompt = user_prompt_template.replace(
                "{target_behavior}", behavior_text
            )
            formatted_user_prompt = formatted_user_prompt.replace(
                "{num_strategies}", str(num_strategies)
            )
        else:
            user_prompt_template = (
                self.prompts.prompts.user_messages[1].messages[0].content
            )
            formatted_user_prompt = user_prompt_template.replace(
                "{target_behavior}", behavior_text
            )
            formatted_user_prompt = formatted_user_prompt.replace(
                "{num_strategies}", str(num_strategies)
            )

            strategies_text = ""
            if previous_responses:
                for set_name, response in previous_responses.items():
                    strategies_text += f"\n{set_name}:\n{response}\n"
            formatted_user_prompt = formatted_user_prompt.replace(
                "{previously_generated_strategies}", strategies_text
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": formatted_user_prompt},
        ]

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
    def _generate_raw_strategies(self, messages: List[Dict], set_num: int) -> Dict:
        """Call the model API to generate raw JSON strategies."""
        self._logger.debug(f"Calling model API for set {set_num}...")
        response = self.agent.call_api(
            messages=messages,
            response_format={"type": "json_object"},
        )
        import json

        parsed_response = json.loads(response)
        assert isinstance(parsed_response, dict), "Response must be a dictionary"
        self._logger.debug(f"Received API response for set {set_num}.")
        return parsed_response

    def _process_single_behavior(
        self,
        behavior_number: int,
        behavior: BaseHarmfulBehaviour,
        num_sets: int,
        num_strategies: int=10,
    ) -> XtreamAttackPlan:
        """Process one behavior into an XtreamAttackPlan."""
        self._logger.info(
            f"[Behavior {behavior_number}] Starting processing for behavior='{behavior.behavior}'"
        )

        full_attack_strategies: Dict[str, Dict[str, AttackStrategy]] = {}
        previous_responses: Dict[str, Dict] = {}

        for set_num in range(1, num_sets + 1):
            self._logger.debug(f"[Behavior {behavior_number}] Generating set {set_num}...")

            messages = self._format_prompts(
                behavior_text=behavior.behavior,
                set_number=set_num,
                previous_responses=previous_responses,
                num_strategies=num_strategies
            )

            raw_strategies = self._generate_raw_strategies(messages, set_num)

            # Now we parse raw strategies into properly typed AttackStrategy objects
            set_strategies = {}
            for strategy_name, strategy_info in raw_strategies.items():
                conversation_plan_data = strategy_info.pop("conversation_plan")
                conversation_plan = ConversationPlan(
                    turns=conversation_plan_data.get("turns", []),
                    final_turn=conversation_plan_data.get("final_turn", ""),
                )

                strategy = AttackStrategy(
                    conversation_plan=conversation_plan, **strategy_info
                )
                set_strategies[strategy_name] = strategy

                self._logger.debug(
                    f"[Behavior {behavior_number}] Parsed strategy '{strategy_name}' for set {set_num}."
                )

            full_attack_strategies[f"Set_{set_num}"] = set_strategies
            previous_responses[f"Set_{set_num}"] = (
                raw_strategies  # Keep raw for formatting next user prompt
            )

        attack_plan = XtreamAttackPlan(
            risk_name=self.risk_name,
            behavior_number=behavior_number,
            behavior_details=behavior,
            attack_strategies=full_attack_strategies,
        )

        self._logger.info(
            f"[Behavior {behavior_number}] Finished processing {num_sets} sets for behavior_id='{behavior.behavior_id}'."
        )

        return attack_plan

    def generate_attack_plans(
        self,
        num_behaviors: int = 15,
        num_sets: int = 5,
        num_strategies: int=10,
    ) -> XtreamAttackPlans:
        """Generate XtreamAttackPlans."""
        self._logger.info(
            f"Starting generation of attack plans (num_behaviors={num_behaviors}, num_sets={num_sets})..."
        )

        selected_behaviors = self.behaviors
        if len(selected_behaviors) > num_behaviors:
            random.seed(42)
            selected_behaviors = random.sample(selected_behaviors, num_behaviors)
            self._logger.info(
                f"Randomly selected {num_behaviors} behaviors out of {len(self.behaviors)} total behaviors."
            )

        plans = []
        for idx, behavior in enumerate(selected_behaviors, start=1):
            plan = self._process_single_behavior(
                behavior_number=idx, behavior=behavior, 
                num_sets=num_sets,
                num_strategie=num_strategies
            )
            plans.append(plan)

        self._logger.info(
            f"Completed generation of {len(plans)} attack plans."
        )
        return XtreamAttackPlans(plans=plans)


class ConcurrentAttackPlanGenerator(AttackPlanGenerator):
    def generate_attack_plans(
        self,
        num_behaviors: int = 15,
        num_sets: int = 5,
        num_strategies: int=10,
    ) -> XtreamAttackPlans:
        """Generate XtreamAttackPlans concurrently."""
        self._logger.info(
            f"Starting *concurrent* generation of attack plans (num_behaviors={num_behaviors}, num_sets={num_sets})..."
        )

        selected_behaviors = self.behaviors
        if len(selected_behaviors) > num_behaviors:
            random.seed(42)
            selected_behaviors = random.sample(selected_behaviors, num_behaviors)
            self._logger.info(
                f"Randomly selected {num_behaviors} behaviors out of {len(self.behaviors)} total behaviors."
            )

        plans = []
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for idx, behavior in enumerate(selected_behaviors, start=1):
                self._logger.info(
                    f"[Behavior {idx}] Submitting task for behavior_id='{idx}', category='{behavior.behavior}'."
                )
                tasks.append(
                    executor.submit(
                        self._process_single_behavior,
                        behavior_number=idx,
                        behavior=behavior,
                        num_sets=num_sets,
                        num_strategies=num_strategies
                    )
                )

            for future in concurrent.futures.as_completed(tasks):
                plan = future.result()
                plans.append(plan)
                self._logger.info(
                    f"[Behavior {plan.behavior_number}] Completed concurrent processing."
                )

        self._logger.info(
            f"Completed concurrent generation of {len(plans)} attack plans."
        )
        return XtreamAttackPlans(plans=plans)
