"""
Module: ai_risk_assessment
Description: Builds a structured AI risk assessment report from raw EvalReport data,
             mapping plugin results into safety categories, frameworks, and overall stats.
"""

from dtx.core import logging
from typing import Optional, Dict, List
from uuid import UUID
from collections import defaultdict
from enum import Enum

from pydantic import BaseModel, Field

from dtx_models.results import EvalReport, EvalResult
from dtx_models.repo.plugin2frameworks import Plugin2FrameworkMapper
from dtx_models.repo.plugin import PluginRepo


# Initialize module-level logger
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Enums: define severity and pass/fail status values
# ----------------------------------------------------------------------

class AIRiskSeverity(str, Enum):
    """
    Enumeration of severity levels for AI risk findings.
    """
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class AIEvalStatus(str, Enum):
    """
    Enumeration of evaluation status: pass or fail.
    """
    passed = "pass"
    failed = "fail"


# ----------------------------------------------------------------------
# Risk Check and Category Section Models
# ----------------------------------------------------------------------

class AIRiskCheck(BaseModel):
    """
    Represents an individual risk check (one EvalResult).
    """
    id: str                                # Unique run ID
    name: str                              # Human-readable name of the check
    status: AIEvalStatus                   # Whether the check passed or failed
    severity: Optional[AIRiskSeverity] = None  # Severity level of the finding
    description: Optional[str] = None      # Optional detailed description


class AIRiskCategorySection(BaseModel):
    """
    Aggregates multiple AIRiskCheck items under a common category (plugin-based).
    """
    id: str                                # Internal category ID (e.g. plugin prefix)
    name: str                              # Human-readable name
    title: str                             # Display title
    description: Optional[str] = None      # Optional longer description
    percent: int = Field(..., ge=0, le=100)  # Percent passed in this category
    passed: int                            # Number of passed checks
    failed: int                            # Number of failed checks
    total: int                             # Total number of checks
    risks: List[AIRiskCheck]               # List of individual risk checks


# ----------------------------------------------------------------------
# Framework Breakdown Models
# ----------------------------------------------------------------------

class AIRiskFramework(BaseModel):
    """
    Summarizes compliance controls under a specific framework (e.g., NIST, ISO).
    """
    id: str                                # Framework identifier
    name: str                              # Human-readable name
    title: str                             # Display title
    description: Optional[str] = None      # Optional framework description
    score: int = Field(..., ge=0, le=100)  # Percentage of controls passed
    passed: int                            # Number of passed controls
    failed: int                            # Number of failed controls
    total: int                             # Total number of controls
    controls: List[Dict] = []              # Detailed control data (if available)


# ----------------------------------------------------------------------
# Safety Category Stats (to mirror UI risk categories chart)
# ----------------------------------------------------------------------

class SafetyCategoryStats(BaseModel):
    """
    Holds aggregate stats for a top‐level safety category (e.g. 'Hallucination').
    """
    id: str                                # Category slug (e.g. 'hallucination')
    name: str                              # Human-readable name
    title: str                             # Display title
    score: int = Field(..., ge=0, le=100)  # Percent of checks passed in this category
    passed: int                            # Number of passed checks
    failed: int                            # Number of failed checks
    total: int                             # Total checks in this category


# ----------------------------------------------------------------------
# Summary / Stats Models
# ----------------------------------------------------------------------

class AIRiskOverallSeverityCounts(BaseModel):
    """
    Counts of findings by severity level, plus pass/fail/jailbreak totals.
    """
    total: int
    passed: int
    failed: int
    critical: int
    high: int
    medium: int
    low: int
    jailbreaks: int


class AIRiskFrameworkOverview(BaseModel):
    """
    Lightweight overview of a framework for the summary section.
    """
    id: str
    name: str
    title: str
    score: int = Field(..., ge=0, le=100)
    passed: int
    failed: int
    total: int


class AIRiskSectionStats(BaseModel):
    """
    Lightweight overview of a category section for the summary section.
    """
    id: str
    name: str
    title: str
    description: Optional[str] = None
    score: int = Field(..., ge=0, le=100)
    passed: int
    failed: int
    total: int


class AIRiskOverallStats(BaseModel):
    """
    Top-level container for overall assessment metrics.
    """
    overall: Dict[str, int]                    # { total, passed, failed }
    safety_categories: List[SafetyCategoryStats]  # Stats for each UI safety category
    severity: AIRiskOverallSeverityCounts      # Breakdown by severity
    frameworks: List[AIRiskFrameworkOverview]  # Framework overviews
    sections: List[AIRiskSectionStats]         # Category section overviews


class AIRiskProviderReport(BaseModel):
    """
    Stubmodel for per-provider breakdown if needed in the future.
    """
    provider_id: Optional[UUID]
    provider_name: Optional[str]
    provider_type: Optional[str]
    risk_sections: List[AIRiskCategorySection] = []


class AIRiskAssessmentReport(BaseModel):
    """
    Full assessment report combining all stats, frameworks, sections, and providers.
    """
    overall_stats: AIRiskOverallStats
    frameworks: List[AIRiskFramework]
    risk_sections: List[AIRiskCategorySection]
    providers: List[AIRiskProviderReport]


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def _to_severity_enum(value: str) -> Optional[AIRiskSeverity]:
    """
    Convert a severity string to the AIRiskSeverity enum.
    """
    val = value.lower()
    if 'critical' in val:
        return AIRiskSeverity.critical
    if 'high' in val:
        return AIRiskSeverity.high
    if 'medium' in val:
        return AIRiskSeverity.medium
    return AIRiskSeverity.low


def _humanize_slug(slug: str) -> str:
    """
    Turn a machine slug like 'data_leaks' into 'Data Leaks'.
    """
    if not slug:
        return ''
    return slug.replace('_', ' ').replace('-', ' ').title()


# ----------------------------------------------------------------------
# Builder: constructs the full AIRiskAssessmentReport
# ----------------------------------------------------------------------

class AssessmentReportBuilder:
    """
    Takes an EvalReport and a Plugin→Framework mapper,
    and produces a structured AIRiskAssessmentReport.
    """

    def __init__(
        self,
        eval_report: EvalReport,
        plugin2framework_mapper: Plugin2FrameworkMapper
    ):
        self.report = eval_report
        self.results: List[EvalResult] = eval_report.eval_results
        self.plugin2framework_mapper = plugin2framework_mapper
        self.plugin_repo = PluginRepo()

    def build(self) -> AIRiskAssessmentReport:
        """
        Main entry: compute overall stats, frameworks, sections,
        and also safety‐categories based on plugin tags.
        """
        overall = self._compute_overall_stats()
        frameworks = self._build_frameworks()
        sections = self._build_sections()

        # fill in summaries
        overall.frameworks = [self._to_framework_overview(fw) for fw in frameworks]
        overall.sections   = [self._to_section_stats(sec)    for sec in sections]

        # compute safety_categories
        overall.safety_categories = self._build_safety_category_stats()

        providers = []  # (unchanged)
        return AIRiskAssessmentReport(
            overall_stats=overall,
            frameworks=frameworks,
            risk_sections=sections,
            providers=providers,
        )

    def _compute_overall_stats(self) -> AIRiskOverallStats:
        """
        Count total/passed/failed checks, tally jailbreaks, and bucket by severity.
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.responses and r.responses[0].success)
        failed = total - passed
        jailbreaks = sum(1 for r in self.results if r.responses and r.responses[0].jailbreak_achieved)

        # Initialize severity buckets
        buckets = dict(critical=0, high=0, medium=0, low=0)
        for r in self.results:
            sev = r.risk_score.overall.overall_score.severity.value.lower()
            if 'critical' in sev:
                buckets['critical'] += 1
            elif 'high' in sev:
                buckets['high'] += 1
            elif 'medium' in sev:
                buckets['medium'] += 1
            else:
                buckets['low'] += 1

        return AIRiskOverallStats(
            overall=dict(total=total, passed=passed, failed=failed),
            safety_categories=[],  # to be populated if desired
            severity=AIRiskOverallSeverityCounts(
                total=total,
                passed=passed,
                failed=failed,
                critical=buckets['critical'],
                high=buckets['high'],
                medium=buckets['medium'],
                low=buckets['low'],
                jailbreaks=jailbreaks,
            ),
            frameworks=[],
            sections=[],
        )

    def _build_frameworks(self) -> List[AIRiskFramework]:
        """
        Group checks by their compliance frameworks and compute pass rates.
        """
        framework_data = defaultdict(lambda: {
            "passed": 0, "failed": 0, "total": 0,
            "framework_title": None, "framework_description": None,
        })

        for r in self.results:
            plugin_id = r.plugin_id
            if not plugin_id:
                continue

            plugin_dto = self.plugin2framework_mapper.get_plugin_with_frameworks(plugin_id)
            if not plugin_dto:
                continue

            is_pass = r.responses and r.responses[0].success

            # Tally each control under its framework
            for ctrl in plugin_dto.compliance_controls:
                f_id = ctrl.framework_id
                framework_data[f_id]["total"] += 1
                if is_pass:
                    framework_data[f_id]["passed"] += 1
                else:
                    framework_data[f_id]["failed"] += 1

                # capture title/description once
                framework_data[f_id]["framework_title"] = framework_data[f_id]["framework_title"] or ctrl.framework_title
                framework_data[f_id]["framework_description"] = framework_data[f_id]["framework_description"] or ctrl.framework_description

        # Build Pydantic models from aggregated data
        frameworks: List[AIRiskFramework] = []
        for fid, data in framework_data.items():
            total = data["total"]
            passed = data["passed"]
            failed = data["failed"]
            score = int((passed / total) * 100) if total else 0

            frameworks.append(
                AIRiskFramework(
                    id=fid,
                    name=_humanize_slug(fid),
                    title=data["framework_title"] or fid,
                    description=data["framework_description"],
                    score=score,
                    passed=passed,
                    failed=failed,
                    total=total,
                    controls=[],
                )
            )
        return frameworks

    def _build_sections(self) -> List[AIRiskCategorySection]:
        """
        Group checks by plugin-category prefix and compute category‐level stats.
        """
        tree: Dict[str, List[EvalResult]] = defaultdict(list)
        for r in self.results:
            cat = r.plugin_id.split(':')[0] if r.plugin_id else 'Unknown'
            tree[cat].append(r)

        sections: List[AIRiskCategorySection] = []
        for cat, items in tree.items():
            passed = sum(1 for r in items if r.responses and r.responses[0].success)
            failed = len(items) - passed
            total = len(items)
            percent = int((passed / total) * 100) if total else 0

            # Build individual check entries
            checks: List[AIRiskCheck] = []
            for r in items:
                sev_value = r.risk_score.overall.overall_score.severity.value
                checks.append(
                    AIRiskCheck(
                        id=r.run_id,
                        name=_humanize_slug(r.plugin_id),
                        status=AIEvalStatus.passed if r.responses and r.responses[0].success else AIEvalStatus.failed,
                        severity=_to_severity_enum(sev_value),
                    )
                )

            sections.append(
                AIRiskCategorySection(
                    id=cat,
                    name=_humanize_slug(cat),
                    title=_humanize_slug(cat),
                    percent=percent,
                    passed=passed,
                    failed=failed,
                    total=total,
                    risks=checks,
                )
            )

        return sections

    def _to_framework_overview(self, fw: AIRiskFramework) -> AIRiskFrameworkOverview:
        """
        Convert detailed framework model to a lightweight overview.
        """
        return AIRiskFrameworkOverview(
            id=fw.id,
            name=fw.name,
            title=fw.title,
            score=fw.score,
            passed=fw.passed,
            failed=fw.failed,
            total=fw.total,
        )

    def _build_safety_category_stats(self) -> List[SafetyCategoryStats]:
        """
        For each unique tag in the plugin repo, find all plugins
        with that tag, then count how many EvalResults came from
        those plugins (passed/failed/total), and compute a pass%
        """
        stats: List[SafetyCategoryStats] = []
        tags = self.plugin_repo.get_unique_tags()  # e.g. ['bias','hallucination','security',…]
        for tag in tags:
            # get all plugin‐IDs carrying this tag
            plugins_for_tag = self.plugin_repo.get_plugins_by_tag(tag)
            plugin_ids = {p.id for p in plugins_for_tag}

            # filter eval results by plugin_id membership
            matching = [r for r in self.results if r.plugin_id in plugin_ids]
            total = len(matching)
            if total == 0:
                # skip tags with no checks
                continue

            passed = sum(1 for r in matching if r.responses and r.responses[0].success)
            failed = total - passed
            score = int((passed / total) * 100)

            stats.append(SafetyCategoryStats(
                id=tag,
                name=_humanize_slug(tag),
                title=_humanize_slug(tag),
                score=score,
                passed=passed,
                failed=failed,
                total=total
            ))

        return stats

    def _to_section_stats(self, sec: AIRiskCategorySection) -> AIRiskSectionStats:
        """
        Convert detailed category model to a lightweight overview.
        """
        return AIRiskSectionStats(
            id=sec.id,
            name=sec.name,
            title=sec.title,
            description=sec.description,
            score=sec.percent,
            passed=sec.passed,
            failed=sec.failed,
            total=sec.total,
        )
