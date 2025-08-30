from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid


class Population(BaseModel):
    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class PopulationInfo(BaseModel):
    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    agent_count: int
    metadata: Optional[Dict[str, Any]] = None


class DataItem(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    data_type: str
    content: Any
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class Agent(BaseModel):
    agent_id: uuid.UUID
    name: str
    population_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    data_items: List[DataItem] = Field(default_factory=list)
    source: Optional[str] = None
    source_id: Optional[str] = None


class CreatePopulationPayload(BaseModel):
    name: str
    description: Optional[str] = None


class UpdatePopulationMetadataPayload(BaseModel):
    metadata: Dict[str, Any]
    mode: Optional[Literal["merge", "replace"]] = "merge"


class InitialDataItemPayload(BaseModel):
    data_type: str
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class CreateAgentPayload(BaseModel):
    name: str
    source: Optional[str] = None
    source_id: Optional[str] = None
    population_id: Optional[uuid.UUID] = None
    agent_data: Optional[List[InitialDataItemPayload]] = None


class CreateDataItemPayload(BaseModel):
    data_type: str
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class UpdateDataItemPayload(BaseModel):
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class DeletionResponse(BaseModel):
    message: str


# --- Generation Operation Models ---
class OpenGenerationRequest(BaseModel):
    question: str
    data_types: Optional[List[str]] = None
    exclude_data_types: Optional[List[str]] = None
    images: Optional[Dict[str, str]] = (
        None  # Dict of {description: url} for multiple images
    )
    reasoning: bool = False
    evidence: bool = False
    confidence: bool = False
    memory_stream: Optional["MemoryStream"] = None


class OpenGenerationResponse(BaseModel):
    question: str
    answer: str
    reasoning: Optional[str] = ""
    evidence: Optional[str] = ""
    confidence: Optional[float] = None


class ClosedGenerationRequest(BaseModel):
    question: str
    options: List[str]
    data_types: Optional[List[str]] = None
    exclude_data_types: Optional[List[str]] = None
    images: Optional[Dict[str, str]] = None
    reasoning: bool = False
    evidence: bool = False
    confidence: bool = False
    memory_stream: Optional["MemoryStream"] = None


class ClosedGenerationResponse(BaseModel):
    question: str
    options: List[str]
    response: str
    reasoning: Optional[str] = ""
    evidence: Optional[str] = ""
    confidence: Optional[float] = None


class AddContextRequest(BaseModel):
    context: str


class AddContextResponse(BaseModel):
    message: str
    session_id: uuid.UUID


# --- Survey Session Models ---
class TurnType(str, Enum):
    """Enum for different types of conversation turns."""

    CONTEXT = "context"
    IMAGE = "image"
    OPEN_QUESTION = "open_question"
    CLOSED_QUESTION = "closed_question"


class BaseTurn(BaseModel):
    """Base model for all conversation turns."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    type: TurnType

    class Config:
        use_enum_values = True


class ContextTurn(BaseTurn):
    """A context turn that provides background information."""

    type: Literal[TurnType.CONTEXT] = TurnType.CONTEXT
    user_context: str


class ImageTurn(BaseTurn):
    """A standalone image turn (e.g., for context or reference)."""

    type: Literal[TurnType.IMAGE] = TurnType.IMAGE
    images: Dict[str, str]
    caption: Optional[str] = None


class OpenQuestionTurn(BaseTurn):
    """An open question-answer turn."""

    type: Literal[TurnType.OPEN_QUESTION] = TurnType.OPEN_QUESTION
    user_question: str
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None


class ClosedQuestionTurn(BaseTurn):
    """A closed question-answer turn."""

    type: Literal[TurnType.CLOSED_QUESTION] = TurnType.CLOSED_QUESTION
    user_question: str
    user_options: List[str]
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None

    @validator("user_options")
    def validate_options(cls, v):
        if not v:
            raise ValueError("Closed questions must have at least one option")
        if len(v) < 2:
            raise ValueError("Closed questions should have at least two options")
        return v

    @validator("llm_response")
    def validate_response(cls, v, values):
        if (
            v is not None
            and "user_options" in values
            and v not in values["user_options"]
        ):
            raise ValueError(f"Response '{v}' must be one of the provided options")
        return v


# Union type for all possible turn types
SurveySessionTurn = Union[ContextTurn, ImageTurn, OpenQuestionTurn, ClosedQuestionTurn]


class SurveySessionCreateResponse(BaseModel):
    id: uuid.UUID  # Session ID
    agent_id: uuid.UUID
    created_at: datetime
    status: str


class SurveySessionDetailResponse(BaseModel):
    """Detailed survey session response with typed conversation turns."""

    id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    conversation_history: List[SurveySessionTurn] = Field(default_factory=list)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SurveySessionListItemResponse(BaseModel):
    """Summary response for listing survey sessions."""

    id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    turn_count: int = Field(description="Number of turns in conversation history")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SurveySessionCloseResponse(BaseModel):
    id: uuid.UUID  # Session ID
    status: str
    updated_at: datetime
    message: Optional[str] = None


# --- Memory Stream Models (to replace Survey Sessions) ---
class MemoryTurnType(str, Enum):
    """Enum for different types of memory turns."""

    CONTEXT = "context"
    IMAGE = "image"
    OPEN_QUESTION = "open_question"
    CLOSED_QUESTION = "closed_question"


class BaseMemoryTurn(BaseModel):
    """Base model for all memory turns."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    type: MemoryTurnType

    class Config:
        use_enum_values = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = self.model_dump()
        # Remove timestamp - let API handle it
        data.pop("timestamp", None)
        # Ensure enum is serialized as string
        if "type" in data:
            if hasattr(data["type"], "value"):
                data["type"] = data["type"].value
        return data


class ContextMemoryTurn(BaseMemoryTurn):
    """A context turn that provides background information."""

    type: MemoryTurnType = Field(default=MemoryTurnType.CONTEXT)
    user_context: str


class ImageMemoryTurn(BaseMemoryTurn):
    """A standalone image turn (e.g., for context or reference)."""

    type: MemoryTurnType = Field(default=MemoryTurnType.IMAGE)
    images: Dict[str, str]
    caption: Optional[str] = None


class OpenQuestionMemoryTurn(BaseMemoryTurn):
    """An open question-answer turn."""

    type: MemoryTurnType = Field(default=MemoryTurnType.OPEN_QUESTION)
    user_question: str
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None
    llm_reasoning: Optional[str] = None


class ClosedQuestionMemoryTurn(BaseMemoryTurn):
    """A closed question-answer turn."""

    type: MemoryTurnType = Field(default=MemoryTurnType.CLOSED_QUESTION)
    user_question: str
    user_options: List[str]
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None
    llm_reasoning: Optional[str] = None


# Discriminated union of all memory turn types
MemoryTurn = Union[
    ContextMemoryTurn, ImageMemoryTurn, OpenQuestionMemoryTurn, ClosedQuestionMemoryTurn
]


class MemoryStream(BaseModel):
    """
    A flexible memory stream that can be passed to generation functions.
    This replaces the session-based approach with a more flexible paradigm.
    """

    turns: List[MemoryTurn] = Field(default_factory=list)

    def add_turn(self, turn: MemoryTurn) -> None:
        """Add a turn to the memory stream."""
        self.turns.append(turn)

    def remove_turn(self, index: int) -> Optional[MemoryTurn]:
        """Remove a turn at the specified index."""
        if 0 <= index < len(self.turns):
            return self.turns.pop(index)
        return None

    def get_turns_by_type(self, turn_type: MemoryTurnType) -> List[MemoryTurn]:
        """Get all turns of a specific type."""
        return [turn for turn in self.turns if turn.type == turn_type]

    def get_last_turn(self) -> Optional[MemoryTurn]:
        """Get the most recent turn."""
        return self.turns[-1] if self.turns else None

    def clear(self) -> None:
        """Clear all turns from the memory stream."""
        self.turns = []

    def __len__(self) -> int:
        """Return the number of turns in the memory stream."""
        return len(self.turns)

    def __bool__(self) -> bool:
        """Return True if the memory stream has any turns."""
        return bool(self.turns)

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory stream to a dictionary for serialization."""
        return {"turns": [turn.to_dict() for turn in self.turns]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryStream":
        """Create a MemoryStream from a dictionary."""
        memory = cls()
        for turn_data in data.get("turns", []):
            turn_type = turn_data.get("type")
            if turn_type == MemoryTurnType.CONTEXT:
                memory.add_turn(ContextMemoryTurn(**turn_data))
            elif turn_type == MemoryTurnType.IMAGE:
                memory.add_turn(ImageMemoryTurn(**turn_data))
            elif turn_type == MemoryTurnType.OPEN_QUESTION:
                memory.add_turn(OpenQuestionMemoryTurn(**turn_data))
            elif turn_type == MemoryTurnType.CLOSED_QUESTION:
                memory.add_turn(ClosedQuestionMemoryTurn(**turn_data))
        return memory

    def fork(self, up_to_index: Optional[int] = None) -> "MemoryStream":
        """Create a copy of this memory stream, optionally up to a specific index."""
        new_memory = MemoryStream()
        turns_to_copy = (
            self.turns[:up_to_index] if up_to_index is not None else self.turns
        )
        for turn in turns_to_copy:
            new_memory.add_turn(turn.model_copy())
        return new_memory

    def filter_by_type(self, turn_type: MemoryTurnType) -> "MemoryStream":
        """Create a new memory stream with only turns of a specific type."""
        new_memory = MemoryStream()
        for turn in self.get_turns_by_type(turn_type):
            new_memory.add_turn(turn.model_copy())
        return new_memory

    def get_question_answer_pairs(self) -> List[tuple]:
        """Extract question-answer pairs from the memory."""
        pairs = []
        for turn in self.turns:
            if isinstance(turn, (OpenQuestionMemoryTurn, ClosedQuestionMemoryTurn)):
                if turn.llm_response:
                    pairs.append((turn.user_question, turn.llm_response))
        return pairs

    def truncate(self, max_turns: int) -> None:
        """Keep only the most recent N turns."""
        if len(self.turns) > max_turns:
            self.turns = self.turns[-max_turns:]

    def insert_turn(self, index: int, turn: MemoryTurn) -> None:
        """Insert a turn at a specific position."""
        self.turns.insert(index, turn)
