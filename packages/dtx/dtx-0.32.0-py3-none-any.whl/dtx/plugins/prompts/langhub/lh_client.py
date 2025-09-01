import re
from typing import Dict, List, Optional

from langchain_core.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.prompt import PromptTemplate
from langsmith import Client
from langsmith import schemas as ls_schemas
from pydantic import BaseModel, model_validator

from dtx.core import logging
from dtx_models.prompts import BaseMultiTurnConversation, RoleType, Turn
from dtx_models.template.prompts.langhub import (
    LangchainHubPrompt,
    LangchainHubPromptMetadata,
)


class LangHubPromptSearchQuery(BaseModel):
    query: Optional[str] = None  # Free text search
    filters: Optional[Dict[str, str]] = None  # Field name -> regex pattern
    full_name: Optional[str] = None
    owner: Optional[str] = None

    @model_validator(mode="before")
    def validate_and_initialize(cls, values):
        query = values.get("query")
        full_name = values.get("full_name")
        owner = values.get("owner")
        filters = values.get("filters") or {}

        # Ensure at least one field is provided
        if not any([query, full_name, owner]):
            raise ValueError(
                "At least one of 'query', 'full_name', or 'owner' must be provided."
            )

        # Set query and filters based on full_name or owner
        if full_name:
            values["query"] = full_name
            filters.setdefault("metadata.full_name", full_name)
        elif owner:
            values["query"] = owner
            filters.setdefault("metadata.owner", owner)

        values["filters"] = filters
        return values


# --- Repository Class ---


class LangHubPromptRepository:
    def __init__(self):
        self.client = Client()

    def _list_prompts(
        self, query: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[ls_schemas.Prompt]:
        prompts_response = self.client.list_prompts(
            limit=limit,
            offset=offset,
            query=query,
            is_public=True,
            sort_field=ls_schemas.PromptSortField.num_downloads,
            sort_direction="desc",
        )
        return prompts_response.repos

    def _parse_prompt_to_model(self, prompt_obj, repo_obj) -> LangchainHubPrompt:
        if not isinstance(prompt_obj, (ChatPromptTemplate, PromptTemplate)):
            raise TypeError(
                f"Unsupported prompt type: {type(prompt_obj).__name__}. Only ChatPromptTemplate and PromptTemplate are supported."
            )

        # Build metadata
        metadata = LangchainHubPromptMetadata(
            id=str(repo_obj.id),
            name=repo_obj.repo_handle,
            owner=repo_obj.owner or "unknown",
            description=repo_obj.description or "",
            readme=repo_obj.readme or "",
            tags=repo_obj.tags or [],
            created_at=repo_obj.created_at,
            updated_at=repo_obj.updated_at,
            is_public=repo_obj.is_public,
            num_likes=repo_obj.num_likes,
            num_downloads=repo_obj.num_downloads,
            num_views=repo_obj.num_views,
            last_commit_hash=repo_obj.last_commit_hash or "",
            full_name=repo_obj.full_name,
        )

        # Convert to conversation
        conversation = self._to_multi_turn_conversation(prompt_obj)
        input_variables = getattr(prompt_obj, "input_variables", [])

        return LangchainHubPrompt(
            metadata=metadata,
            conversation=conversation,
            input_variables=input_variables,
        )

    def _to_multi_turn_conversation(self, prompt_obj) -> BaseMultiTurnConversation:
        turns = []

        if isinstance(prompt_obj, ChatPromptTemplate):
            for message_template in prompt_obj.messages:
                if isinstance(message_template, HumanMessagePromptTemplate):
                    role = RoleType.USER
                elif isinstance(message_template, AIMessagePromptTemplate):
                    role = RoleType.ASSISTANT
                elif isinstance(message_template, SystemMessagePromptTemplate):
                    role = RoleType.SYSTEM
                else:
                    continue  # Skip unsupported types

                prompt_template = getattr(message_template, "prompt", None)
                if prompt_template:
                    message = prompt_template.template
                    turns.append(Turn(role=role, message=message))

        elif isinstance(prompt_obj, PromptTemplate):
            # Single turn prompt — treat as SYSTEM role
            turns.append(Turn(role=RoleType.SYSTEM, message=prompt_obj.template))

        else:
            raise TypeError(
                f"Unsupported template type for conversation conversion: {type(prompt_obj)}"
            )

        return BaseMultiTurnConversation(turns=turns)

    def _fetch_and_parse_prompts(
        self,
        search_query: Optional[LangHubPromptSearchQuery] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[LangchainHubPrompt]:
        query_str = search_query.query if search_query else None
        prompts = self._list_prompts(query=query_str, limit=limit, offset=offset)

        parsed_prompts = []
        for repo_obj in prompts:
            try:
                if not repo_obj.last_commit_hash:
                    continue
                prompt_id = f"{repo_obj.full_name}:{repo_obj.last_commit_hash}"
                prompt_obj = self.client.pull_prompt(prompt_id)
                parsed_prompt = self._parse_prompt_to_model(prompt_obj, repo_obj)

                if self._apply_filters(parsed_prompt, search_query):
                    parsed_prompts.append(parsed_prompt)

            except Exception as e:
                logging.warn(f"Error parsing prompt {repo_obj.full_name}: {e}")
                logging.exception("Error parsing prompt %s", e)

        return parsed_prompts

    def _apply_filters(
        self,
        parsed_prompt: LangchainHubPrompt,
        search_query: Optional[LangHubPromptSearchQuery],
    ) -> bool:
        if not search_query or not search_query.filters:
            return True

        for field, pattern in search_query.filters.items():
            value = self._get_field_value(parsed_prompt, field)
            if value is None or not re.search(pattern, str(value)):
                return False

        return True

    def _get_field_value(self, parsed_prompt: LangchainHubPrompt, field: str):
        parts = field.split(".")
        value = parsed_prompt
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
        return value

    def search(
        self, search_query: LangHubPromptSearchQuery, limit: int = 50, offset: int = 0
    ) -> List[LangchainHubPrompt]:
        return self._fetch_and_parse_prompts(
            search_query=search_query, limit=limit, offset=offset
        )


if __name__ == "__main__":
    repo = LangHubPromptRepository()
    search_query = LangHubPromptSearchQuery(full_name="homanp/question-answer-pair")

    parsed_prompts = repo.search(search_query, limit=5)

    for specific_prompt in parsed_prompts:
        print(specific_prompt.model_dump_json(indent=2))
