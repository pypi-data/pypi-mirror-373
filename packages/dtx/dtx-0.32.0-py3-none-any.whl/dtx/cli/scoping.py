from typing import Optional, List

import yaml
from pydantic import BaseModel

from dtx.core.builders.redteam import RedTeamScopeBuilder
from dtx_models.scope import AgentInfo, RedTeamScope


class ScopeInput(BaseModel):
    description: str
    plugins: Optional[List[str]] = None  # Optional plugin IDs or expressions
    frameworks: Optional[List[str]] = None

class RedTeamScopeCreator:
    def __init__(self, config: ScopeInput):
        self.config = config
        self.scope: Optional[RedTeamScope] = None

    def run(self) -> RedTeamScope:
        agent_data = AgentInfo(description=self.config.description)
        builder = RedTeamScopeBuilder().set_agent(agent_data)

        if self.config.frameworks:
            builder.add_plugins_by_framework(self.config.frameworks)

        if self.config.plugins:
            builder.add_plugins_by_expression(self.config.plugins)
        
        if not self.config.frameworks and not self.config.plugins:
            # fallback to all plugins only if nothing else is specified
            builder.add_plugins_from_repo()

        self.scope = builder.build()
        return self.scope


    def save_yaml(self, path: str):
        if not self.scope:
            raise ValueError("Run must be called before saving.")
        yaml_data = yaml.dump(self.scope.model_dump(), default_flow_style=False)
        with open(path, "w") as file:
            file.write(yaml_data)

    @staticmethod
    def load_yaml(path: str) -> RedTeamScope:
        """Load and return a RedTeamScope object from a YAML file."""
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return RedTeamScope(**data)
