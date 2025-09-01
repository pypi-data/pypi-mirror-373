import yaml
from pathlib import Path
from dtx_models.plugins.xtream.config import AttackerConfig

class XtreamGlobalConfig:
    """Global configuration for important file paths."""

    # Base directory is 'config'
    CONFIG_DIR = Path(__file__).resolve().parent 
    PROMPTS_DIR = CONFIG_DIR / "prompts"

    def __init__(self):
        self._config = self.get_default_config()

    def get_attacker_agent_prompts_path(cls) -> Path:
        """Return path to 'config/prompts/attacker_agent_prompts.yaml'."""
        return cls.PROMPTS_DIR / "attacker_agent_prompts.yaml"

    def get_attack_planner_prompts_path(cls) -> Path:
        """Return path to 'config/prompts/attack_planner_prompts.yml'."""
        return cls.PROMPTS_DIR / "attack_planner_prompts.yml"

    def get_default_config_path(cls) -> Path:
        """Return path to 'config/config.yml'."""
        return cls.CONFIG_DIR / "config.yml"

    def get_default_config(cls) -> dict:
        """ Return the config"""
        with open(cls.get_default_config_path(), "r") as f:
            config_data = yaml.safe_load(f)
            return config_data

    def get_attacker_config(self) -> AttackerConfig:
        return AttackerConfig(**self._config)

    def resolve_relative_to_config(cls, relative_path: str) -> Path:
        """Resolve an arbitrary path relative to 'config' directory."""
        return cls.CONFIG_DIR / relative_path
