import yaml
from jinja2 import Template
from pathlib import Path
from typing import Optional, Dict, List, Any

from dtx.core import logging
from dtx_models.results import EvalReport
from dtx_models.repo.plugin import PluginRepo
from dtx_models.repo.ai_frameworks import AIFrameworkRepo
from dtx_models.repo.plugin2frameworks import Plugin2FrameworkMapper
from dtx.core.reports.html.builder import AssessmentReportBuilder, AIRiskAssessmentReport


# Initialize module-level logger
logger = logging.getLogger(__name__)

plugin_repo = PluginRepo()
aif_repo = AIFrameworkRepo()
plugin2framework_mapper = Plugin2FrameworkMapper(
    plugin_repo=plugin_repo,
    framework_repo=aif_repo,
)


class ReportGenerator:
    """
    Generates an HTML evaluation report using EvalReport or AIRiskAssessmentReport.
    """
    def __init__(self, template_path: Optional[Path] = None):
        if template_path is None:
            base = Path(__file__).parent
            template_path = base / '../templates' / 'html_report_template.html'
        self.template_path = Path(template_path)
        logger.info(f"Initializing ReportGenerator with template: {self.template_path}")
        if not self.template_path.exists():
            logger.error(f"Template not found: {self.template_path}")
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        self.plugin2framework_mapper = plugin2framework_mapper

    def _load_yaml(self, yaml_file_path: str) -> EvalReport:
        path = Path(yaml_file_path)
        logger.debug(f"Loading YAML data from: {path}")
        if not path.exists():
            logger.error(f"YAML file not found: {path}")
            raise FileNotFoundError(f"YAML file not found: {path}")
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        report = EvalReport(**data)
        logger.info(f"Loaded EvalReport with {len(report.eval_results)} results")
        return report

    def _render(self, context: Dict[str, Any]) -> str:
        template_str = self.template_path.read_text(encoding='utf-8')
        template = Template(template_str)
        logger.info("Rendering template with context keys: %s", list(context.keys()))
        return template.render(**context)
    def generate(
        self,
        assessment: Optional[AIRiskAssessmentReport] = None,
        report: Optional[EvalReport] = None,
        yaml_file_path: Optional[str] = None
    ) -> str:
        """
        Generate HTML from either:
        - an existing AIRiskAssessmentReport + raw EvalReport
        - just an EvalReport
        - or a YAML file path
        """
        # 1) Load the EvalReport if needed, then build the AIRiskAssessmentReport
        if assessment is None:
            if report is None:
                if yaml_file_path is None:
                    logger.error("No assessment, report, or YAML path provided.")
                    raise ValueError("Provide one of: assessment, report, or yaml_file_path")
                report = self._load_yaml(yaml_file_path)
            builder = AssessmentReportBuilder(eval_report=report, 
                                              plugin2framework_mapper=self.plugin2framework_mapper)
            assessment = builder.build()
        
        # Add user/assistant conversation fields to each eval_result
        for res in report.eval_results:
            turns = []
            # Try to get turns from responses[0].response.turns if available
            if (res.responses and 
                hasattr(res.responses[0], "response") and
                res.responses[0].response and
                hasattr(res.responses[0].response, "turns")):
                turns = res.responses[0].response.turns
            # Else fallback to prompt.turns
            elif hasattr(res.prompt, "turns"):
                turns = res.prompt.turns
            user_turns = [t.message for t in turns if getattr(t, "role", None) == "USER"]
            assistant_turns = [t.message for t in turns if getattr(t, "role", None) == "ASSISTANT"]

            res._user_message = user_turns[-1] if user_turns else ''
            res._assistant_response = assistant_turns[-1] if assistant_turns else ''

        # 2) Executive summary
        exec_overall = assessment.overall_stats.overall
        sev = assessment.overall_stats.severity
        executive_summary = {
            'total_findings': exec_overall['total'],
            'passed':          exec_overall['passed'],
            'failed':          exec_overall['failed'],
            'critical':        sev.critical,
            'high':            sev.high,
            'medium':          sev.medium,
            'low':             sev.low,
            'jailbreaks':      sev.jailbreaks,
        }

        # 3) Findings list (for the nav list at top)
        findings_list: List[Dict[str, Any]] = []
        for sec in assessment.risk_sections:
            findings_list.append({
                'id':      sec.id,
                'title':   sec.title,
                'percent': sec.percent,
                'passed':  sec.passed,
                'failed':  sec.failed,
                'total':   sec.total,
            })

        # 4) Findings details (for the big "Findings Details" tables)
        findings_details: Dict[str, List[Dict[str, Any]]] = {}
        for sec in assessment.risk_sections:
            checks = []
            for chk in sec.risks:
                checks.append({
                    'id':          chk.id,
                    'name':        chk.name,
                    'status':      chk.status.value,
                    'severity':    chk.severity.value if chk.severity else None,
                    'description': chk.description or '-',
                })
            findings_details[sec.id] = checks

        # 5) Regulatory readiness (framework scores)
        regulatory_readiness = {
            fw.title: fw.score
            for fw in assessment.frameworks
        }

        # 6) Findings summary (you used the same keys as exec summary)
        findings_summary = executive_summary

        # 7) Overall safety % for the doughnut
        total = executive_summary['total_findings']
        overall_safety_score = int((executive_summary['passed'] / total) * 100) if total else 0

        # 8) Risk metrics for the horizontal bar
        risk_metrics = {
            'critical': sev.critical,
            'high':     sev.high,
            'medium':   sev.medium,
            'low':      sev.low,
        }
        risk_max = max(risk_metrics.values()) if risk_metrics else 0

        # 9) Attack techniques (pie chart): count total checks per category
        attack_techniques = {
            sec.title: sec.total
            for sec in assessment.risk_sections
        }

        safety_categories = [
            {
                'id':    cat.id,
                'title': cat.title,
                'score': cat.score,
                'passed': cat.passed,
                'failed': cat.failed,
                'total': cat.total
            }
            for cat in assessment.overall_stats.safety_categories ]

        # 10) Build context and render
        context = {
            'executive_summary':    executive_summary,
            'findings_list':        findings_list,
            'findings_details':     findings_details,
            'assessment':           assessment,
            'report':               report,
            'regulatory_readiness': regulatory_readiness,
            'findings_summary':     findings_summary,
            'overall_safety_score': overall_safety_score,
            'risk_metrics':         risk_metrics,
            'risk_max':             risk_max,
            'attack_techniques':    attack_techniques,
            'safety_categories': safety_categories,
        }
        return self._render(context)


    def save(self, html: str, output_path: str) -> None:
        out_path = Path(output_path)
        logger.info(f"Saving report to: {out_path}")
        out_path.write_text(html, encoding='utf-8')

    def generate_to_file(
        self,
        yaml_file_path: str,
        output_path: str
    ) -> None:
        html = self.generate(None, None, yaml_file_path)
        self.save(html, output_path)
        logger.info(f"HTML report generated at: {output_path}")

if __name__ == '__main__':
    generator = ReportGenerator(template_path="html_report_templates.html")
    generator.generate_to_file('report.yml', 'index.html')
