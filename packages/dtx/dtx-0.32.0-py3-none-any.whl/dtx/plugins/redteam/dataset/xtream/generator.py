from dtx.core import logging

from typing import Iterator, List

from dtx_models.analysis import RiskItem
from dtx_models.plugins.xtream.config import AttackPlanGeneratorConfig
from dtx_models.plugins.xtream.plan import HarmfulBehaviour, AttackPlannerPromptsReader, XtreamAttackPlan
from dtx.plugins.redteam.dataset.base.harm_repo import HarmfulBehaviourRepo
from .engine.planner import ConcurrentAttackPlanGenerator
from .engine.planner import AttackPlannerAgent
from .config.globals import XtreamGlobalConfig

class PromptsGenerator_Xteamjb:
    """
    Generates test prompts and evaluation criteria for each attack strategy from XTREAM Harmful behaviors.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, harm_repo: HarmfulBehaviourRepo):
        """
        Initializes with the HarmfulBehaviourRepo.
        """
        self._harm_repo = harm_repo
        self._default_config = XtreamGlobalConfig()

    def generate(
        self,
        app_name: str,
        threat_desc: str,
        risks: List[RiskItem],
        max_prompts: int = 10,
        max_prompts_per_plugin: int = 5,
        max_goals_per_plugin: int = 5
    ) -> Iterator[XtreamAttackPlan]:
        """
        Generates test prompts and evaluation criteria for each RiskItem.
        Uses HarmfulBehaviour objects as the source of goals.

        :param app_name: Name of the AI application
        :param threat_desc: Summary of security risks/threats related to the app
        :param risks: List of RiskItem objects
        :param max_prompts: Maximum number of test prompts to generate
        :param max_prompts_per_plugin: Maximum number of test prompts to generate per risk
        :return: Iterator of XtreamAttackPlan objects
        """
        total_prompts = 0
        _attack_planner_config_dict = self._default_config.get_default_config()["attack_plan_generator"]
        attack_planner_config = AttackPlanGeneratorConfig(**_attack_planner_config_dict)
        planner_agent = AttackPlannerAgent(attack_planner_config)

        self._logger.info("Loading attack planner prompts...")
        prompt_file_path = self._default_config.get_attack_planner_prompts_path()
        planner_prompts = AttackPlannerPromptsReader.from_yaml_file(prompt_file_path)

        self._logger.info(
            f"Starting XTREAM attack plan generation for app='{app_name}' with max_prompts={max_prompts}, max_prompts_per_plugin={max_prompts_per_plugin}."
        )

        ## Global Number the behaviour numbers
        behavior_idx = 1

        for risk in risks:
            total_prompts_per_risk = 0
            self._logger.info(f"Processing risk class: '{risk.risk}'")

            # Get HarmfulBehaviour objects for this risk class
            behaviors: List[HarmfulBehaviour] = self._harm_repo.get_behaviours(risk.risk)

            if not behaviors:
                self._logger.warning(f"No behaviors found for risk class '{risk.risk}' — skipping.")
                continue


            behaviors = behaviors[0:max_goals_per_plugin]
            self._logger.info(f"Found {len(behaviors)} behaviors for risk class '{risk.risk}'.")

            num_behaviors_in_risk = len(behaviors)
            num_sets, num_strategies = self._compute_num_sets_and_strategies(
                num_behaviors=num_behaviors_in_risk,
                max_prompts_per_plugin=max_prompts_per_plugin
            )

            for behaviour in behaviors:
                self._logger.info(
                    f"Generating attack plan for behavior_id='{behaviour.behavior_id}', category='{behaviour.semantic_category}'"
                )

                generator = ConcurrentAttackPlanGenerator(agent=planner_agent, 
                                                          prompts=planner_prompts, 
                                                          behaviors=[behaviour], risk_name=risk.risk)

                attack_plans = generator.generate_attack_plans(
                    num_behaviors=1,
                    num_sets=num_sets,
                    num_strategies=num_strategies
                )

                for attack_plan in attack_plans.plans:
                    attack_plan.behavior_number = behavior_idx
                    behavior_idx += 1
                    
                    yield attack_plan
                    total_prompts_per_risk += 1
                    self._logger.debug(f"Yielded attack plan for behavior_id='{behaviour.behavior_id}'.")

                    if total_prompts_per_risk >= max_prompts_per_plugin:
                        self._logger.info(
                            f"Reached max_prompts_per_plugin={max_prompts_per_plugin} for risk class '{risk.risk}'. Moving to next risk."
                        )
                        break


                if total_prompts_per_risk >= max_prompts_per_plugin:
                    break

            total_prompts += total_prompts_per_risk

            self._logger.info(
                f"Generated {total_prompts_per_risk} attack plans for risk class '{risk.risk}'. Total so far: {total_prompts}."
            )

            if total_prompts >= max_prompts:
                self._logger.info(
                    f"Reached global max_prompts={max_prompts}. Stopping generation."
                )
                break

    def _compute_num_sets_and_strategies(
        self,
        num_behaviors: int,
        max_prompts_per_plugin: int
    ) -> tuple[int, int]:
        """
        Computes the number of sets and number of strategies to use given
        the number of behaviors and max_prompts_per_plugin limit.

        - Favors more sets than strategies
        - Minimum num_sets = 2 (unless impossible)
        - Ensures:
            total_prompts_per_risk = num_behaviors * num_sets * num_strategies <= max_prompts_per_plugin

        Returns:
            (num_sets, num_strategies)
        """

        # First compute max possible prompts per behavior
        max_prompts_per_behavior = max(max_prompts_per_plugin // num_behaviors, 1)

        # Start with sets = min(max_prompts_per_behavior, desired_min_sets)
        min_desired_sets = 2

        # Initial guess: start with more sets, fewer strategies
        num_sets = min(max_prompts_per_behavior, max(min_desired_sets, 1))
        num_strategies = max(1, max_prompts_per_behavior // num_sets)

        # Now adjust to ensure total fits in max_prompts_per_plugin
        while num_behaviors * num_sets * num_strategies > max_prompts_per_plugin:
            # Try reducing strategies first
            if num_strategies > 1:
                num_strategies -= 1
            # Then reduce sets if necessary, but don't go below 2 if possible
            elif num_sets > min_desired_sets:
                num_sets -= 1
            elif num_sets > 1:
                # If we must go below 2 to fit, allow it
                num_sets -= 1
            else:
                # Cannot reduce further
                break

        self._logger.info(
            f"Computed settings for risk: num_behaviors={num_behaviors}, max_prompts_per_plugin={max_prompts_per_plugin} => num_sets={num_sets}, num_strategies={num_strategies}"
        )

        return num_sets, num_strategies
