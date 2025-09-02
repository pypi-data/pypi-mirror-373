# Sarvam Conv AI SDK

The **Sarvam Conversational AI SDK** is a Python package that helps developers build and extend conversational agents. It provides core components to manage conversation flow, language preferences, and messaging, making it easier to develop interactive and context-aware AI experiences.

---

## Overview

The Sarvam Conv AI SDK enables developers to create tools that can:

* Facilitate agentic capabilities like API calling in the middle of a conversation.
* Manage agent-specific variables
* Control and modify the language used during conversations
* Send dynamic messages to both the user and the underlying language model (LLM)

---

## Installation

Install the SDK via pip:

```bash
pip install sarvam-conv-ai-sdk
```

---

## Example Usage

```python
import httpx
from pydantic import Field

from sarvam_conv_ai_sdk import (
    SarvamInteractionTurnRole,
    SarvamOnEndTool,
    SarvamOnEndToolContext,
    SarvamOnStartTool,
    SarvamOnStartToolContext,
    SarvamTool,
    SarvamToolContext,
    SarvamToolLanguageName,
    SarvamToolOutput,
)

class OnStart(SarvamOnStartTool): #Name of the class has to be OnStart
    async def run(self, context: SarvamOnStartToolContext):
        user_id = context.get_user_identifier()
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://sarvam-flights.com/users/{user_id}")
            response.raise_for_status()
            user_data = response.json()

        source_destination = user_data.get("home_city")
        context.set_agent_variable("source_destination", source_destination)
        context.set_agent_variable("passenger_name", user_data.get("name"))
        context.set_initial_language_name(SarvamToolLanguageName.ENGLISH)
        context.set_initial_bot_message(
            f"Hello! Would you like to book a flight from {source_destination}? Where would you like to go?",
        )
        return context


class BookFlight(SarvamTool):
    """Book a flight based on the user's travel preferences."""

    destination: str = Field(description="City of destination")
    travel_date: str = Field(description="Date of travel (YYYY-MM-DD)")

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        source_destination = context.get_agent_variable("source_destination")
        booking_data = {
            "source": source_destination,
            "destination": self.destination,
            "travel_date": self.travel_date,
            "passenger_name": context.get_agent_variable("passenger_name"),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://sarvam-flights.com/book", json=booking_data
            )
            response.raise_for_status()
            booking_result = response.json()

        if booking_result.get("status") == "confirmed":
            context.set_agent_variable("booking_id", booking_result.get("booking_id"))
            context.set_end_conversation()
            return SarvamToolOutput(
                message_to_user=f"Flight booked successfully to {self.destination}!",
                context=context,
            )
        else:
            context.change_state("recommend_destinations")
            return SarvamToolOutput(
                message_to_llm="Booking failed. Please suggest similar destinations.",
                context=context,
            )


class OnEnd(SarvamOnEndTool):  #Name of the class has to be OnEnd
    async def run(self, context: SarvamOnEndToolContext):
        feedback = context.get_agent_variable("feedback")
        negative_words = ["bad", "poor", "disappointed", "unhappy", "problem"]
        interaction_transcript = context.get_interaction_transcript()
        if interaction_transcript.interaction_transcript:
            for turn in interaction_transcript.interaction_transcript:
                if turn.role == SarvamInteractionTurnRole.USER:
                    is_negative = any(word in feedback.lower() for word in negative_words)
            context.set_agent_variable("feedback_sentiment", is_negative)

        return context

```

---

## Base Classes

The SDK exposes three base classes for tool development:

### 1. `SarvamTool`

Primary base class for all operational tools invoked during conversation flow.

**Example:**

```python
class MyCustomTool(SarvamTool):
    """Brief description of the tool's purpose."""

    tool_variable: type = Field(description="Description of this input parameter")

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        # Custom tool logic
        return SarvamToolOutput(
            message_to_user="Response to user",
            message_to_llm="Context for LLM",
            context=context
        )
```

### 2. `SarvamOnStartTool`

Executed at the beginning of a conversation, typically for initialization. The class **must** be named `OnStart`.

### 3. `SarvamOnEndTool`

Executed at the end of a conversation, typically for cleanup or post-processing. The class **must** be named `OnEnd`.

---

## Context Classes and Methods

### `SarvamToolContext`

The context object passed to `SarvamTool.run()` methods.

#### Variable Management

* `get_agent_variable(variable_name: str) -> Any`
  Retrieve the value of a variable.

* `set_agent_variable(variable_name: str, value: Any) -> None`
  Update a variable's value.

#### Language Control

* `get_current_language() -> SarvamToolLanguageName`
  Returns the current language of the agent.

* `change_language(language: SarvamToolLanguageName) -> None`
  Update the language preference.

#### Conversation Flow

* `set_end_conversation() -> None`
  Explicitly end the conversation.

#### State Management

* `get_current_state() -> str`
  Returns the current state of the conversation.

* `change_state(state: str) -> None`
  Transition to a new state. **Note:** The new state must be one of the next valid states defined in the agent configuration.

#### Engagement Metadata

* `get_engagement_metadata() -> EngagementMetadata`
  Retrieve the engagement metadata containing information about the current interaction. 

---

### `SarvamOnStartToolContext`

The context object passed to `SarvamOnStartTool.run()` methods.

#### Variable Management

* `get_agent_variable(variable_name: str) -> Any`
  Retrieve the value of a variable.

* `set_agent_variable(variable_name: str, value: Any) -> None`
  Update a variable's value.

#### User Information

* `get_user_identifier() -> str`
  Get the user identifier.

#### Initialization Methods

* `set_initial_bot_message(message: str) -> None`
  Set the first message sent by the agent when the conversation starts.

* `set_initial_state_name(state_name: str) -> None`
  Set the initial state from which the agent should start.

* `set_initial_language_name(language: SarvamToolLanguageName) -> None`
  Define the initial language preference for the user.

#### Engagement Metadata

* `get_engagement_metadata() -> EngagementMetadata`
  Retrieve the engagement metadata containing information about the current interaction.

---

### `SarvamOnEndToolContext`

The context object passed to `SarvamOnEndTool.run()` methods.

#### Variable Management

* `get_agent_variable(variable_name: str) -> Any`
  Retrieve the value of a variable.

* `set_agent_variable(variable_name: str, value: Any) -> None`
  Update a variable's value.

#### User Information

* `get_user_identifier() -> str`
  Get the user identifier.

#### Engagement Metadata

* `get_engagement_metadata() -> EngagementMetadata`
  Retrieve the engagement metadata containing information about the current interaction.


### Interaction Reattempt
* `set_retry_interaction`
  The user will be reattempted with the same agent. Useful when any business goal has not been met. 

#### Interaction Transcript

* `get_interaction_transcript() -> SarvamInteractionTranscript`
  Retrieve the conversation history containing user and agent messages in English and
 the timestamp when the conversation began and ended. Format: `yyyy-mm-dd hh:mm:ss`

**Example transcript:**
```python
[
    SarvamInteractionTurn(role=<SarvamInteractionTurnRole.AGENT: 'agent'>, en_text='Hello! How can I help you today?'),
    SarvamInteractionTurn(role=<SarvamInteractionTurnRole.USER: 'user'>, en_text='I need to book a flight'),
    SarvamInteractionTurn(role=<SarvamInteractionTurnRole.AGENT: 'agent'>, en_text='I can help you with that. Where would you like to go?'),
    SarvamInteractionTurn(role=<SarvamInteractionTurnRole.USER: 'user'>, en_text='I want to go to Mumbai'),
    SarvamInteractionTurn(role=<SarvamInteractionTurnRole.AGENT: 'agent'>, en_text='Great! When would you like to travel?')
]
```

---

## Return Types

### `SarvamToolOutput`

The return type for `SarvamTool.run()` methods. Contains:

* `message_to_user: Optional[str]` - Message that is sent directly to the user
* `message_to_llm: Optional[str]` - Message that is sent to the LLM, which then responds
* `context: SarvamToolContext` - The updated context object

**Note:** At least one of `message_to_llm` or `message_to_user` must be set.

**Important:** When both `message_to_user` and `message_to_llm` are set, only the `message_to_user` is actually sent to the user, but the `message_to_llm` overrides the `message_to_user` when adding to the chat thread for the LLM's context.

### `EngagementMetadata`

The engagement metadata object that can be retrieved from context objects using `get_engagement_metadata()`. Contains:

* `interaction_id: str` - Unique identifier for each conversation between user & agent.
* `attempt_id: Optional[str]` - Unique identifier for each attempt created on the platform
* `campaign_id: Optional[str]` - Campaign ID for the interaction
* `interaction_language: SarvamToolLanguageName` - The language used for the interaction (defaults to English)
* `app_id: str` - Application identifier of the agent for the interaction
* `app_version: int` - Version number of the agent
* `agent_phone_number: Optional[str]` - Phone number associated with the conversational agent application

---

## Supported Languages

The SDK supports multilingual conversations using the `SarvamToolLanguageName` enum. Available languages include:

* Bengali
* Gujarati
* Kannada
* Malayalam
* Tamil
* Telugu
* Punjabi
* Odia
* Marathi
* Hindi
* English

**Note:** The allowed languages are actually a subset that is preselected while defining the agent configurations.

---

## Best Practices

1. **Always implement `run()`**: The `run()` method is the entry point for tool execution logic.
2. **Use `Field()` for parameters**: Ensures type safety and adds descriptive metadata necessary for LLM to use in the prompt.
3. **Gracefully handle errors**: Avoid accessing unset variables or using invalid types.
4. **Return the appropriate type**: `SarvamTool.run()` must return `SarvamToolOutput`, while `SarvamOnStartTool.run()` and `SarvamOnEndTool.run()` return their respective context objects.
5. **Write meaningful docstrings**: Clearly describe what each tool is intended to do as this directly impacts the performance of tool calling capabilities of the agent.
6. **Use async operations for I/O**: For the best performance, use `async/await` for external API calls to avoid blocking.
7. **Use context methods**: Use the provided context methods for variable management, language control, and messaging instead of directly accessing context attributes.

---

## Error Handling

The SDK includes built-in error handling for common scenarios:

* **Variable not found**: Raises ValueError when accessing undefined variables
* **Variable not defined**: Raises ValueError when setting variables that haven't been initialized
* **Non-serializable values**: Raises ValueError when variable values cannot be JSON serialized
* **Invalid output**: Raises ValueError when `SarvamToolOutput` is created without at least one message

---

## Testing Your Tools

After creating a tool, you can test it locally to ensure it works as expected. Here's how to test your tools:

### Testing Steps

1. **Create the ToolContext**: Initialize the appropriate context object with test data
2. **Instantiate the tool class**: Use `tool.model_validate(tool_args)` to create a tool instance
3. **Run the tool**: Call the tool's `run()` method with the context
4. **Observe the returned object**: Check if the necessary changes have been made to the context

### Example Test: SarvamTool

```python
# Test the BookFlight tool
async def test_book_flight():
    # 1. Create the ToolContext
    context = SarvamToolContext(
        language=SarvamToolLanguageName.ENGLISH,
        allowed_languages=[SarvamToolLanguageName.ENGLISH],
        state="booking",
        next_valid_states=["recommend_destinations", "end"],
        agent_variables={
            "source_destination": "Mumbai",
            "passenger_name": "John Doe",
            "booking_id": "123"
        },
        engagement_metadata=EngagementMetadata(
            interaction_id="123",
            attempt_id="456",
            campaign_id="789",
            interaction_language=SarvamToolLanguageName.ENGLISH,
            app_id="101",
            app_version=1,
            agent_phone_number="+1234567890",
        ),
    )
    
    # 2. Instantiate the tool class
    tool_args = {
        "destination": "Delhi",
        "travel_date": "2024-03-15"
    }
    tool_instance = BookFlight.model_validate(tool_args)
    
    # 3. Run the tool
    result = await tool_instance.run(context)
    
    # 4. Observe the returned object
    print(f"Message to user: {result.message_to_user}")
    print(f"Message to LLM: {result.message_to_llm}")
    print(f"End conversation: {result.context.end_conversation}")
    print(f"Current state: {result.context.get_current_state()}")
    print(f"Agent variables: {result.context.agent_variables}")
    print(f"Current Language: {result.context.get_current_language()}")

# Run the test
asyncio.run(test_book_flight())
```

### Example Test: OnStart Tool

For `SarvamOnStartTool`, the testing approach is similar but it returns the context object directly:

```python
# Testing OnStart tool
async def test_on_start():
    context = SarvamOnStartToolContext(
        user_identifier="user123",
        agent_variables={"source_destination": "Mumbai", "passenger_name": "John Doe"},
        engagement_metadata=EngagementMetadata(
            interaction_id="123",
            attempt_id="456",
            campaign_id="789",
            interaction_language=SarvamToolLanguageName.ENGLISH,
            app_id="101",
            app_version=1,
            agent_phone_number="+1234567890",
        ),
        initial_bot_message=None,
        initial_state_name="start",
        initial_language_name=SarvamToolLanguageName.ENGLISH,
    )
    
    tool_instance = OnStart()
    result = await tool_instance.run(context)
    
    print(f"Initial bot message: {result.initial_bot_message}")
    print(f"Initial state: {result.initial_state_name}")
    print(f"Initial Language Name: {result.initial_language_name}")
    print(f"Agent variables: {result.agent_variables}")

# Run the test
asyncio.run(test_on_start())
```

### Example Test: OnEnd Tool

```python
# Testing OnEnd tool
async def test_on_end():
    context = SarvamOnEndToolContext(
        user_identifier="user123",
        agent_variables={"feedback": "I had a bad experience", "feedback_sentiment": False},
        engagement_metadata=EngagementMetadata(
            interaction_id="123",
            attempt_id="456",
            campaign_id="789",
            interaction_language=SarvamToolLanguageName.ENGLISH,
            app_id="101",
            app_version=1,
            agent_phone_number="+1234567890",
        ),
        interaction_transcript=SarvamInteractionTranscript(
            interaction_transcript=[
                SarvamInteractionTurn(role=SarvamInteractionTurnRole.AGENT, en_text='Hello! How can I help you today?'),
                SarvamInteractionTurn(role=SarvamInteractionTurnRole.USER, en_text='I need to book a flight'),
                SarvamInteractionTurn(role=SarvamInteractionTurnRole.AGENT, en_text='I can help you with that. Where would you like to go?'),
                SarvamInteractionTurn(role=SarvamInteractionTurnRole.USER, en_text='I want to go to Mumbai'),
                SarvamInteractionTurn(role=SarvamInteractionTurnRole.AGENT, en_text='Great! When would you like to travel?')
            ],
            interaction_start_time=datetime.now() - timedelta(minutes=2),
            interaction_end_time=datetime.now(),
        ),
        retry_interaction=False,
    )
    
    tool_instance = OnEnd()
    result = await tool_instance.run(context)
    
    print(f"Agent variables: {result.agent_variables}")
    print(f"Interaction Retry: {result.retry_interaction}")

# Run the test
asyncio.run(test_on_end())
```
