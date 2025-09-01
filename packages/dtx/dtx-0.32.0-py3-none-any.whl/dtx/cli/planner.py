from dtx.core import logging

from typing import Optional

import yaml
from pydantic import BaseModel

from dtx_models.analysis import PromptDataset, RedTeamPlan, TestSuitePrompts
from dtx_models.scope import RedTeamScope
from dtx.plugins.redteam.dataset.xtream.analysis import AppRiskAnalysis_Xtream_Jb
from dtx.plugins.redteam.dataset.xtream.generator import PromptsGenerator_Xteamjb
from dtx.plugins.redteam.dataset.hf.analysis import AppRiskAnalysis_HF
from dtx.plugins.redteam.dataset.hf.generator import HFDataset_PromptsGenerator
from dtx.plugins.redteam.dataset.stargazer.generator import (
    Stargazer_PromptsGenerator,
)
from dtx.plugins.redteam.dataset.stingray.generator import (
    Stringray_PromptsGenerator,
)
from dtx.threat_model.analysis import AppRiskAnalysis, AppRiskAnalysisModelChain
from dtx.threat_model.analysis_sr import (
    AppRiskAnalysis_SR,
)


class PlanInput(BaseModel):
    dataset: PromptDataset


class RedTeamPlanGenerator:

    logger = logging.getLogger(__name__)

    def __init__(self, scope: RedTeamScope, config: PlanInput):
        self.scope = scope
        self.config = config
        self.plan: Optional[RedTeamPlan] = None

    def run(self) -> RedTeamPlan:

        self.logger.info(f"Starting RedTeamPlan generation for dataset={self.config.dataset}...")
        if self.config.dataset == PromptDataset.STINGRAY:
            self.plan = self._generate_with_stingray()
        elif self.config.dataset == PromptDataset.STARGAZER:
            self.plan = self._generate_with_stargazer()
        elif self.config.dataset == PromptDataset.XTREAM_JB:
            self.plan = self._generate_with_xtream_jb()
        elif self.config.dataset.derived_from_hf():
            self.plan = self._generate_with_hf()
        else:
            raise ValueError(f"Unsupported dataset type: {self.config.dataset}")
        self.logger.info("Finished RedTeamPlan generation.")
        return self.plan

    def save_yaml(self, path: str):
        if not self.plan:
            raise ValueError("No plan is provided to save")
        self.logger.info(f"Saving RedTeamPlan to {path}...")
        yaml_data = yaml.dump(self.plan.model_dump(), default_flow_style=False)
        with open(path, "w") as file:
            file.write(yaml_data)
        self.logger.info("RedTeamPlan saved successfully.")

    @classmethod
    def load_yaml(cls, path: str) -> RedTeamPlan:
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        cls.logger.info("RedTeamPlan loaded successfully.")
        return RedTeamPlan(**data)

    def _generate_with_stargazer(self) -> RedTeamPlan:
        self.logger.info("Running Stargazer analysis...")
        analyzer = AppRiskAnalysis(
            llm=AppRiskAnalysisModelChain(model_name="gpt-4o", temperature=0.5)
        )
        analysis_result = analyzer.analyze(self.scope)
        self.logger.info("Completed Stargazer analysis.")

        self.logger.info("Generating Stargazer test prompts...")
        generator = Stargazer_PromptsGenerator(model="gpt-4o", temperature=0.7)
        test_suite = self._build_test_suite(
            generator, analysis_result, PromptDataset.STARGAZER
        )
        return RedTeamPlan(
            scope=self.scope, threat_model=analysis_result, test_suites=[test_suite]
        )

    def _generate_with_stingray(self) -> RedTeamPlan:
        self.logger.info("Running Stringray analysis...")
        analyzer = AppRiskAnalysis_SR()
        analysis_result = analyzer.analyze(self.scope)
        self.logger.info("Completed Stringray analysis.")

        self.logger.info("Generating Stringray test prompts...")
        generator = Stringray_PromptsGenerator()
        test_suite = self._build_test_suite(
            generator, analysis_result, PromptDataset.STINGRAY
        )
        return RedTeamPlan(
            scope=self.scope, threat_model=analysis_result, test_suites=[test_suite]
        )

    def _generate_with_xtream_jb(self) -> RedTeamPlan:

        self.logger.info("Running XTREAM_JB analysis...")
        from dtx.config import globals
        harmb_repo = globals.get_harmb_repo()
        analyzer = AppRiskAnalysis_Xtream_Jb(harmb_repo=harmb_repo)
        analysis_result = analyzer.analyze(self.scope)
        self.logger.info("Completed XTREAM_JB analysis.")

        self.logger.info("Generating XTREAM_JB test prompts...")
        harmb_repo = globals.get_harmb_repo()
        generator = PromptsGenerator_Xteamjb(harm_repo=harmb_repo)
        test_suite = self._build_test_suite(
            generator, analysis_result, PromptDataset.XTREAM_JB
        )
        self.logger.info("Done Generating XTREAM_JB test prompts...")
        return RedTeamPlan(
            scope=self.scope, threat_model=analysis_result, test_suites=[test_suite]
        )

    def _generate_with_hf(self) -> RedTeamPlan:
        from dtx.config import globals
        
        self.logger.info("Running HF-based analysis...")
        hf_prompt_gen = globals.get_deps_factory().hf_prompt_generator
        analyzer = AppRiskAnalysis_HF(hf_prompts_gen=hf_prompt_gen)
        analysis_result = analyzer.analyze(self.scope, dataset=self.config.dataset)
        self.logger.info("Completed HF-based analysis.")

        self.logger.info("Generating HF test prompts...")
        generator = HFDataset_PromptsGenerator(hf_prompts_gen=hf_prompt_gen)
        test_suite = TestSuitePrompts(dataset=self.config.dataset)
        for prompts in generator.generate(
            dataset=self.config.dataset,
            app_name=analysis_result.threat_analysis.target.name,
            threat_desc=analysis_result.threat_analysis.analysis,
            risks=analysis_result.threats.risks,
            max_prompts=self.scope.redteam.max_prompts,
            max_prompts_per_plugin=self.scope.redteam.max_prompts_per_plugin,
        ):
            self.logger.debug(
                f"Appending prompts for risk: {prompts.risk_name} with {len(prompts.test_prompts)} test prompts."
            )
            test_suite.risk_prompts.append(prompts)

        return RedTeamPlan(
            scope=self.scope, threat_model=analysis_result, test_suites=[test_suite]
        )

    def _build_test_suite(
        self, generator, analysis_result, dataset
    ) -> TestSuitePrompts:
        self.logger.info(
            f"Building test suite for dataset={dataset} with max_prompts={self.scope.redteam.max_prompts}, max_prompts_per_plugin={self.scope.redteam.max_prompts_per_plugin}."
        )
        test_suite = TestSuitePrompts(dataset=dataset)
        for prompts in generator.generate(
            app_name=analysis_result.threat_analysis.target.name,
            threat_desc=analysis_result.threat_analysis.analysis,
            risks=analysis_result.threats.risks,
            max_prompts=self.scope.redteam.max_prompts,
            max_prompts_per_plugin=self.scope.redteam.max_prompts_per_plugin,
            max_goals_per_plugin=self.scope.redteam.max_goals_per_plugin,
        ):
            test_suite.risk_prompts.append(prompts)
        self.logger.info(f"Finished building test suite for dataset={dataset}.")
        return test_suite
