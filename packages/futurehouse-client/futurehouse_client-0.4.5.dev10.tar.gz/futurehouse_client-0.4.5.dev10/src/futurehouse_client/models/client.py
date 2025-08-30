from typing import Any, Generic, TypeAlias, TypeVar

from aviary.message import Message
from aviary.tools.base import Tool
from ldp.data_structures import Transition
from ldp.graph.ops import OpResult
from pydantic import BaseModel, ConfigDict, Field, field_serializer

T = TypeVar("T")


# TODO: revisit this
# unsure what crow states will return
# need to revisit after we get more crows deployed
class BaseState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")


class BeforeTransitionState(BaseState):
    current_state: Any = Field()
    observations: list[Message] = Field()


class InitialState(BaseState):
    initial_state: Any = Field()


class ASVState(BaseState, Generic[T]):
    action: OpResult[T] = Field()
    next_state: Any = Field()
    value: float = Field()

    @field_serializer("action")
    def serialize_action(self, action: OpResult[T]) -> dict:
        return action.to_dict()

class EnvResetState(BaseState):
    observations: list[Message] = Field()
    tools: list[Tool] = Field()


class EnvStepState(BaseState):
    observations: list[Message] = Field()
    reward: float = Field()
    done: bool = Field()
    trunc: bool = Field()


class TransitionState(BaseState):
    transition: Transition = Field()

    @field_serializer("transition")
    def serialize_transition(self, transition: Transition) -> dict:
        transition_data = transition.model_dump()
        return transition_data | {
            "action": transition.action.to_dict() if transition.action else None,
        }


StateType: TypeAlias = (
    BeforeTransitionState
    | InitialState
    | ASVState
    | EnvResetState
    | EnvStepState
    | TransitionState
)
