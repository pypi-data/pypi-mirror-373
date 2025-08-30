from datetime import datetime
from enum import StrEnum, auto
from uuid import UUID

from pydantic import BaseModel, ConfigDict, JsonValue


class FinalEnvironmentRequest(BaseModel):
    status: str


class StoreAgentStatePostRequest(BaseModel):
    agent_id: str
    step: str
    state: JsonValue
    trajectory_timestep: int


class StoreEnvironmentFrameRequest(BaseModel):
    agent_state_point_in_time: str
    current_agent_step: str
    state: JsonValue
    trajectory_timestep: int


class TrajectoryPatchRequest(BaseModel):
    public: bool | None = None
    shared_with: list[int] | None = None
    notification_enabled: bool | None = None
    notification_type: str | None = None
    min_estimated_time: float | None = None
    max_estimated_time: float | None = None


class ExecutionStatus(StrEnum):
    QUEUED = auto()
    IN_PROGRESS = "in progress"
    FAIL = auto()
    SUCCESS = auto()
    CANCELLED = auto()

    def is_terminal_state(self) -> bool:
        return self in self.terminal_states()

    @classmethod
    def terminal_states(cls) -> set["ExecutionStatus"]:
        return {cls.SUCCESS, cls.FAIL, cls.CANCELLED}


class WorldModel(BaseModel):
    """
    Payload for creating a new world model snapshot.

    This model is sent to the API.
    """

    content: str
    prior: UUID | str | None = None
    name: str | None = None
    description: str | None = None
    trajectory_id: UUID | str | None = None
    model_metadata: JsonValue | None = None
    project_id: UUID | str | None = None


class SearchOperator(StrEnum):
    """Operators for structured search criteria."""

    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"


class SearchCriterion(BaseModel):
    """A single search criterion with field, operator, and value."""

    field: str
    operator: SearchOperator
    value: str | list[str] | bool


class WorldModelSearchPayload(BaseModel):
    """Payload for structured world model search."""

    criteria: list[SearchCriterion]
    size: int = 10
    project_id: UUID | str | None = None
    search_all_versions: bool = False


class WorldModelResponse(WorldModel):
    """
    Response model for a world model snapshot.

    This model is received from the API.
    """

    id: UUID | str
    name: str  # type: ignore[mutable-override]  # The API always returns a non-optional name, overriding the base model's optional field.
    email: str | None
    enabled: bool
    created_at: datetime


class UserAgentRequestStatus(StrEnum):
    """Enum for the status of a user agent request."""

    PENDING = auto()
    RESPONDED = auto()
    EXPIRED = auto()
    CANCELLED = auto()


class UserAgentRequest(BaseModel):
    """Sister model for UserAgentRequestsDB."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    trajectory_id: UUID
    response_trajectory_id: UUID | None = None
    request: JsonValue
    response: JsonValue | None = None
    request_world_model_edit_id: UUID | None = None
    response_world_model_edit_id: UUID | None = None
    expires_at: datetime | None = None
    user_response_task: JsonValue | None = None
    status: UserAgentRequestStatus
    created_at: datetime | None = None
    modified_at: datetime | None = None


class UserAgentRequestPostPayload(BaseModel):
    """Payload to create a new user agent request."""

    trajectory_id: UUID
    request: JsonValue
    request_world_model_edit_id: UUID | None = None
    status: UserAgentRequestStatus = UserAgentRequestStatus.PENDING
    expires_in_seconds: int | None = None
    user_response_task: JsonValue | None = None
    notify_user: JsonValue = {"email": True, "sms": False}


class UserAgentResponsePayload(BaseModel):
    """Payload for a user to submit a response to a request."""

    response: JsonValue
    response_world_model_edit_id: UUID | None = None


class DiscoveryResponse(BaseModel):
    """Response model for a discovery request. This model is received from the API."""

    discovery_id: UUID | str
    project_id: UUID | str
    world_model_id: UUID | str
    dataset_id: UUID | str
    description: str
    associated_trajectories: list[UUID | str]
    validation_level: int
    created_at: datetime


class DataStorageSearchPayload(BaseModel):
    """Payload for structured data storage search."""

    criteria: list[SearchCriterion]
    size: int = 10
