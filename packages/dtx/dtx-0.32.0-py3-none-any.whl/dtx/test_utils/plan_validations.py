import pathlib
from typing import Union

from dtx.cli.planner import RedTeamPlanGenerator
from dtx_models.analysis import RedTeamPlan


def validate_plan_file(plan_file: Union[str, pathlib.Path]) -> None:
    """
    Validate the generated Red Team plan YAML file.

    Args:
        plan_file (Union[str, pathlib.Path]): Path to the YAML plan file.

    Raises:
        ValueError: If the plan is invalid.
    """
    plan_file = pathlib.Path(plan_file)

    if not plan_file.exists():
        raise FileNotFoundError(f"Plan file does not exist: {plan_file}")

    print(f"🔍 Validating plan file: {plan_file}")

    # Load the YAML into the plan model
    try:
        plan: RedTeamPlan = RedTeamPlanGenerator.load_yaml(str(plan_file))
    except Exception as e:
        raise ValueError(f"Failed to load YAML plan: {e}")

    # Validate threat_model
    if plan.threat_model is None:
        raise ValueError(f"❌ Validation failed: 'threat_model' is None in {plan_file}")

    # Validate test_suites
    if not plan.test_suites:
        raise ValueError(f"❌ Validation failed: 'test_suites' is empty in {plan_file}")

    print(f"✅ Plan file '{plan_file.name}' is valid!\n")
