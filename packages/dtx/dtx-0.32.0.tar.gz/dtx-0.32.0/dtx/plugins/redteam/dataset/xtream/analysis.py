from typing import List

from dtx.core import logging
from dtx_models.analysis import (
    AnalysisResult,
    AppRisks,
    RiskItem,
    ThreatLevel,
    ThreatModel,
)
from dtx_models.scope import RedTeamScope
from dtx_models.plugins.xtream.plan import HarmfulBehaviour
from dtx.plugins.redteam.dataset.base.harm_repo import HarmfulBehaviourRepo


class AppRiskAnalysis_Xtream_Jb:
    """
    Create a Threat Model of the App using XTREAM behaviors
    """

    logger = logging.getLogger(__name__)

    def __init__(self, harmb_repo: HarmfulBehaviourRepo):
        self._harm_repo = harmb_repo

    def analyze(self, scope: RedTeamScope) -> AnalysisResult:
        """
        Performs AI security risk analysis based on the given RedTeamScope.

        :param scope: The RedTeamScope object containing agent details.
        :return: `AnalysisResult` object containing structured risk analysis.
        """
        self.logger.info("Starting XTREAM analysis..")
        self.logger.info("Collecting harmful behaviors by risk class")

        risks = self._fetch_risks(scope)
        threat_model = self._generate_threat_model(scope)
        apps_threats = AppRisks(risks=risks)
        self.logger.info("Generated Threat Model based on Xtream Analysis")
        return AnalysisResult(threat_analysis=threat_model, threats=apps_threats)

    def _generate_threat_model(self, scope: RedTeamScope) -> ThreatModel:
        """
        Generate a ThreatModel summary for the XTREAM analysis
        """
        desc = "This threat model is based on observed harmful behaviors from the XTREAM harm repo."
        goals = ["Demonstrate real-world harmful behaviors mapped to the app's attack surface."]
        threat_actors = ["Malicious User", "Careless User", "Compromised Agent"]

        return ThreatModel(
            analysis=desc,
            target=scope.agent,
            threat_actors=threat_actors,
            worst_scenarios=goals,
        )

    def _fetch_risks(self, scope: RedTeamScope) -> List[RiskItem]:
        """
        Fetches risks related to all risk classes present in the HarmfulBehaviourRepo
        """
        redteam_settings = scope.redteam
        plugin_ids = redteam_settings.plugins.get_plugin_ids()
        max_goals_per_plugin = scope.redteam.max_goals_per_plugin
        risk_items = self._risk_classes_to_risk_items(plugin_ids, max_goals_per_plugin)
        return risk_items

    def _risk_classes_to_risk_items(self, plugin_ids: List[str], max_goals_per_plugin:int=5) -> List[RiskItem]:
        """
        Convert each supported risk_class to a RiskItem, using HarmfulBehaviour objects as goals.
        Summary will include the functional categories of the behaviors.
        """
        risk_items: List[RiskItem] = []

        for risk_class in plugin_ids:
            behaviours: List[HarmfulBehaviour] = self._harm_repo.get_behaviours(risk_class)
            if behaviours:
                # Use the behavior "text" (or behavior_id, or any other field) as goals
                goals = [hb.behavior for hb in behaviours][0:max_goals_per_plugin]

                # Extract unique functional categories
                categories = sorted(set(hb.semantic_category for hb in behaviours))
                _human_categories = self._snake_case_to_human_readable(categories)
                summary = f"Test {', '.join(_human_categories)} behaviors using various strategies"

                risk_item = RiskItem(
                    risk=risk_class,
                    risk_score=8,  # You can still customize this if desired
                    summary=summary,
                    threat_level=ThreatLevel.HIGH,
                    attack_strategies=goals,
                )
                risk_items.append(risk_item)

        return risk_items

    def _snake_case_to_human_readable(self, snake_case_list):
        """
        Converts a list of snake_case strings to human-readable format.
        
        Example:
        ["harmful_behaviors", "risk_class"] -> ["Harmful Behaviors", "Risk Class"]
        """
        human_readable_list = []
        for s in snake_case_list:
            # Split by underscores, capitalize each word, then join with spaces
            words = s.split('_')
            human_readable = ' '.join(word.capitalize() for word in words)
            human_readable_list.append(human_readable)
        return human_readable_list
