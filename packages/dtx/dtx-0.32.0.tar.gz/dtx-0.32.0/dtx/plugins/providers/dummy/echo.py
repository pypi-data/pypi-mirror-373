from dtx_models.prompts import (
    BaseMultiTurnAgentResponse,
    BaseMultiTurnConversation,
    RoleType,
    Turn,
)

from ..base.agent import BaseAgent


class EchoAgent(BaseAgent):
    def generate(self, prompt: str) -> str:
        raise prompt

    def converse(self, prompt: BaseMultiTurnConversation) -> BaseMultiTurnAgentResponse:
        """
        Perform a multi-turn conversation with the agent.
        Ensures a USER -> ASSISTANT -> USER -> ASSISTANT sequence.
        If an ASSISTANT turn is missing, it is inserted by copying the preceding USER turn.
        """
        turns = prompt.turns
        structured_turns = []
        i = 0  # Index for iterating over turns

        while i < len(turns):
            structured_turns.append(turns[i])

            j = i + 1  # Next index

            # If current turn is USER and next turn is missing or not ASSISTANT, insert one
            if turns[i].role == RoleType.USER and (
                j >= len(turns) or turns[j].role != RoleType.ASSISTANT
            ):
                assistant_turn = Turn(role=RoleType.ASSISTANT, message=turns[i].message)
                structured_turns.append(assistant_turn)

            i += 1  # Move to the next turn

        return BaseMultiTurnAgentResponse(turns=structured_turns)
