import json
from abc import abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator


class SarvamToolLanguageName(StrEnum):
    BENGALI = "Bengali"
    GUJARATI = "Gujarati"
    KANNADA = "Kannada"
    MALAYALAM = "Malayalam"
    TAMIL = "Tamil"
    TELUGU = "Telugu"
    PUNJABI = "Punjabi"
    ODIA = "Odia"
    MARATHI = "Marathi"
    HINDI = "Hindi"
    ENGLISH = "English"


def is_value_serializable(value: Any) -> bool:
    try:
        json.dumps(value)
        return True
    except TypeError:
        raise ValueError(f"Variable value is not serializable: {value}")


class EngagementMetadata(BaseModel):
    interaction_id: str = Field(description="Interaction ID")
    attempt_id: Optional[str] = Field(description="Attempt ID", default=None)
    campaign_id: Optional[str] = Field(description="Campaign ID", default=None)
    interaction_language: SarvamToolLanguageName = Field(
        description="Interaction language", default=SarvamToolLanguageName.ENGLISH
    )
    app_id: str = Field(description="App ID")
    app_version: int = Field(description="App version")
    agent_phone_number: Optional[str] = Field(
        description="Agent phone number (ex: 911234567890)", default=None
    )


class SarvamToolBaseContext(BaseModel):
    agent_variables: Dict[str, Any] = {}
    engagement_metadata: EngagementMetadata = Field(description="Engagement metadata")

    def get_agent_variable(self, variable_name: str) -> Any:
        if variable_name in self.agent_variables:
            return self.agent_variables[variable_name]
        raise ValueError(f"Variable {variable_name} not found")

    def set_agent_variable(self, variable_name: str, value: Any) -> None:
        if variable_name not in self.agent_variables:
            raise ValueError(f"Variable {variable_name} not defined")
        is_value_serializable(value)
        self.agent_variables[variable_name] = value

    def get_engagement_metadata(self) -> EngagementMetadata:
        return self.engagement_metadata


class SarvamToolContext(SarvamToolBaseContext):
    language: SarvamToolLanguageName
    allowed_languages: list[SarvamToolLanguageName]
    end_conversation: bool = False
    state: str
    next_valid_states: list[str]

    def get_current_language(self) -> SarvamToolLanguageName:
        return self.language

    def change_language(self, language: SarvamToolLanguageName) -> None:
        if language not in self.allowed_languages:
            raise ValueError(f"Language {language} not allowed")
        self.language = language

    def get_current_state(self) -> str:
        return self.state

    def change_state(self, state: str) -> None:
        if state not in self.next_valid_states:
            raise ValueError(f"State {state} not valid")
        self.state = state

    def set_end_conversation(self) -> None:
        self.end_conversation = True


class SarvamToolOutput(BaseModel):
    message_to_llm: Optional[str] = None
    message_to_user: Optional[str] = None
    context: SarvamToolContext

    @model_validator(mode="after")
    def validate_messages(self) -> "SarvamToolOutput":
        if not self.message_to_llm and not self.message_to_user:
            raise ValueError(
                "At least one of message_to_llm or message_to_user must be set"
            )
        return self


class SarvamOnStartToolContext(SarvamToolBaseContext):
    user_identifier: str
    initial_bot_message: Optional[str] = None
    initial_state_name: str
    initial_language_name: SarvamToolLanguageName

    def get_user_identifier(self) -> str:
        return self.user_identifier

    def set_initial_bot_message(self, message: str) -> None:
        self.initial_bot_message = message

    def set_initial_state_name(self, state_name: str) -> None:
        self.initial_state_name = state_name

    def set_initial_language_name(self, language_name: SarvamToolLanguageName) -> None:
        self.initial_language_name = language_name


class SarvamInteractionTurnRole(StrEnum):
    USER = "user"
    AGENT = "agent"


class SarvamInteractionTurn(BaseModel):
    role: SarvamInteractionTurnRole = Field(description="Role of the speaker")
    en_text: str = Field(description="English text uttered by the speaker")


class SarvamInteractionTranscript(BaseModel):
    interaction_transcript: Optional[list[SarvamInteractionTurn]] = Field(
        description="Interaction transcript", default=None
    )
    interaction_start_time: datetime = Field(description="Interaction start time")
    interaction_end_time: datetime = Field(description="Interaction end time")


class SarvamOnEndToolContext(SarvamToolBaseContext):
    user_identifier: str
    interaction_transcript: SarvamInteractionTranscript = Field(
        description="Interaction transcript"
    )
    retry_interaction: bool = Field(description="Retry interaction", default=False)

    def get_user_identifier(self) -> str:
        return self.user_identifier

    def get_interaction_transcript(self) -> SarvamInteractionTranscript:
        return self.interaction_transcript

    def set_retry_interaction(self) -> None:
        self.retry_interaction = True


class SarvamTool(BaseModel):
    @abstractmethod
    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        raise NotImplementedError("Subclasses must implement this method")


class SarvamOnStartTool(BaseModel):
    @abstractmethod
    async def run(self, context: SarvamOnStartToolContext) -> SarvamOnStartToolContext:
        raise NotImplementedError("Subclasses must implement this method")


class SarvamOnEndTool(BaseModel):
    @abstractmethod
    async def run(self, context: SarvamOnEndToolContext) -> SarvamOnEndToolContext:
        raise NotImplementedError("Subclasses must implement this method")
