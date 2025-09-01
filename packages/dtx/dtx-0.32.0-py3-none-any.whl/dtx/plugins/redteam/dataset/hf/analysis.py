from typing import List

from dtx.core import logging
from dtx_models.analysis import (
    AnalysisResult,
    AppRisks,
    PromptDataset,
    RiskItem,
    ThreatLevel,
    ThreatModel,
)
from dtx_models.scope import RedTeamScope
from dtx.plugins.redteam.dataset.hf.hf_prompts_repo import HFPromptsGenerator

#
# Restructure the models to perform batch processing
#


class AppRiskAnalysis_HF:
    """
    Create a Threat Model of the App
    """

    logger = logging.getLogger(__name__)

    def __init__(self, hf_prompts_gen: HFPromptsGenerator):
        """ """
        self._generator = hf_prompts_gen

    def analyze(self, scope: RedTeamScope, dataset: PromptDataset) -> AnalysisResult:
        """
        Performs AI security risk analysis based on the given RedTeamScope.

        :param scope: The RedTeamScope object containing agent details.
        :return: `AnalysisResult` object containing structured risk analysis.
        """
        self.logger.info("Starting analysis..")
        self.logger.info("Collecting the attack strategies in batches")
        risks = self._fetch_risks_in_batches(scope, dataset)
        threat_model = self._generate_threat_model(scope=scope, dataset=dataset)
        apps_threats = AppRisks(risks=risks)
        return AnalysisResult(threat_analysis=threat_model, threats=apps_threats)

    def _generate_threat_model(self, scope: RedTeamScope, dataset: str):
        risk_generator = self._generator.get_generator(dataset)
        desc = risk_generator.get_description()
        goals = risk_generator.get_all_goals()
        # labels = risk_generator.get_labels()
        threat_actors = ["Malicious User"]

        return ThreatModel(
            analysis=desc,
            target=scope.agent,
            threat_actors=threat_actors,
            worst_scenarios=goals,
        )

    def _fetch_risks_in_batches(
        self, scope: RedTeamScope, dataset: PromptDataset
    ) -> List[RiskItem]:
        """
        Fetches risks related to the dataset
        """
        redteam_settings = scope.redteam
        plugin_ids = redteam_settings.plugins.get_plugin_ids()
        risks = self._dataset_to_risk_items(dataset=dataset, plugin_ids=plugin_ids)
        return risks

    def _dataset_to_risk_items(
        self, dataset: str, plugin_ids: List[str]
    ) -> List[RiskItem]:
        """
        Convert Multi Turn Conversation to List of Risks
        """
        risk_items: List[RiskItem] = []
        risk_generator = self._generator.get_generator(dataset)
        for plugin_id in plugin_ids:
            if risk_generator.support_risk_class(plugin_id):
                goals = risk_generator.get_goals(plugin_id)
                risk_item = RiskItem(
                    risk=plugin_id,
                    risk_score=8,
                    summary=risk_generator.get_risk_summary(plugin_id),
                    threat_level=ThreatLevel.HIGH,
                    attack_strategies=goals,
                )
                risk_items.append(risk_item)
        return risk_items
