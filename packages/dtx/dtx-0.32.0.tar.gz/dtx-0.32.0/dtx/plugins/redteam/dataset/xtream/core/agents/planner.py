from .base import BaseAgent
from dtx_models.plugins.xtream.config import AttackPlanGeneratorConfig


class AttackPlannerAgent(BaseAgent):
    """Agent that accepts a typed AttackPlanGeneratorConfig instead of a dict."""

    def __init__(self, config: AttackPlanGeneratorConfig):
        # Use .dict() to convert Pydantic model to plain dict for BaseAgent
        super().__init__(config=config.model_dump())
