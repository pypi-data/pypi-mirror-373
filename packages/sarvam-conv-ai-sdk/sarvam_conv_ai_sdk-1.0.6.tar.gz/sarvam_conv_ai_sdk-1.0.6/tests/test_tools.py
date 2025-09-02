from datetime import datetime

import pytest

from sarvam_conv_ai_sdk.tool import (
    EngagementMetadata,
    SarvamInteractionTranscript,
    SarvamInteractionTurn,
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


def create_test_engagement_metadata() -> EngagementMetadata:
    """Helper function to create a valid EngagementMetadata for testing"""
    return EngagementMetadata(
        interaction_id="test_interaction_123", app_id="test_app", app_version=1
    )


def create_test_engagement_metadata_with_campaign() -> EngagementMetadata:
    """Helper function to create a valid EngagementMetadata with campaign info for testing"""
    return EngagementMetadata(
        interaction_id="test_interaction_456",
        attempt_id="test_attempt_123",
        campaign_id="test_campaign_789",
        app_id="test_app",
        app_version=1,
    )


def create_test_engagement_metadata_with_language_and_phone(
    language: SarvamToolLanguageName = SarvamToolLanguageName.HINDI,
    phone_number: str = "911234567890",
) -> EngagementMetadata:
    """Helper function to create EngagementMetadata with interaction language and agent phone"""
    return EngagementMetadata(
        interaction_id="test_interaction_lang_phone",
        app_id="test_app",
        app_version=1,
        interaction_language=language,
        agent_phone_number=phone_number,
    )


class TestGreetingTool(SarvamTool):
    """Example tool that provides greetings in different languages"""

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        user_name = context.get_agent_variable("user_name")

        greetings = {
            SarvamToolLanguageName.ENGLISH: f"Hello {user_name}!",
            SarvamToolLanguageName.HINDI: f"नमस्ते {user_name}!",
            SarvamToolLanguageName.MARATHI: f"नमस्कार {user_name}!",
        }

        greeting = greetings.get(context.get_current_language(), f"Hello {user_name}!")

        return SarvamToolOutput(message_to_user=greeting, context=context)


class TestWeatherTool(SarvamTool):
    """Example tool that provides weather information"""

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        location = context.get_agent_variable("location")

        # Simulate weather data
        weather_info = f"The weather in {location} is sunny with a temperature of 25°C."

        return SarvamToolOutput(
            message_to_llm=f"Weather information for {location}: {weather_info}",
            message_to_user=weather_info,
            context=context,
        )


class TestLanguageChangeTool(SarvamTool):
    """Example tool that changes the conversation language"""

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        new_language = context.get_agent_variable("target_language")

        # Check if the language is a valid enum value
        try:
            if isinstance(new_language, str):
                # Try to get the enum value
                language_enum = SarvamToolLanguageName(new_language)
                context.change_language(language_enum)
                return SarvamToolOutput(
                    message_to_user=f"Language changed to {new_language}",
                    context=context,
                )
            elif new_language in SarvamToolLanguageName:
                context.change_language(new_language)
                return SarvamToolOutput(
                    message_to_user=f"Language changed to {new_language}",
                    context=context,
                )
            else:
                return SarvamToolOutput(
                    message_to_user=f"Sorry, {new_language} is not supported.",
                    context=context,
                )
        except ValueError:
            return SarvamToolOutput(
                message_to_user=f"Sorry, {new_language} is not supported.",
                context=context,
            )


class TestEndConversationTool(SarvamTool):
    """Example tool that ends the conversation"""

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        context.set_end_conversation()

        farewell_messages = {
            SarvamToolLanguageName.ENGLISH: "Goodbye! Have a great day!",
            SarvamToolLanguageName.HINDI: "अलविदा! आपका दिन शुभ हो!",
            SarvamToolLanguageName.MARATHI: "पुन्हा भेटू! तुमचा दिवस चांगला जावो!",
        }

        farewell = farewell_messages.get(
            context.get_current_language(), "Goodbye! Have a great day!"
        )

        return SarvamToolOutput(message_to_user=farewell, context=context)


class TestWelcomeOnStartTool(SarvamOnStartTool):
    """Example on-start tool that sets up initial welcome message"""

    async def run(self, context: SarvamOnStartToolContext) -> SarvamOnStartToolContext:
        user_id = context.get_user_identifier()

        # Set initial bot message based on language
        welcome_messages = {
            SarvamToolLanguageName.ENGLISH: f"Welcome {user_id}! How can I help you today?",
            SarvamToolLanguageName.HINDI: f"स्वागत है {user_id}! मैं आज आपकी कैसे मदद कर सकता हूं?",
            SarvamToolLanguageName.MARATHI: f"स्वागत आहे {user_id}! मी आज तुमची कशी मदत करू शकतो?",
        }

        welcome_message = welcome_messages.get(
            context.initial_language_name,
            f"Welcome {user_id}! How can I help you today?",
        )

        context.set_initial_bot_message(welcome_message)
        context.set_initial_state_name("main_menu")

        return context


class TestAnalyticsOnEndTool(SarvamOnEndTool):
    """Example on-end tool that processes conversation analytics"""

    async def run(self, context: SarvamOnEndToolContext) -> SarvamOnEndToolContext:
        user_id = context.get_user_identifier()
        transcript = context.get_interaction_transcript()

        if transcript:
            # Simulate analytics processing
            total_turns = len(transcript.interaction_transcript)
            user_turns = len(
                [
                    t
                    for t in transcript.interaction_transcript
                    if t.role == SarvamInteractionTurnRole.USER
                ]
            )
            agent_turns = len(
                [
                    t
                    for t in transcript.interaction_transcript
                    if t.role == SarvamInteractionTurnRole.AGENT
                ]
            )

            # Store analytics in agent variables
            context.agent_variables["analytics"] = {
                "total_turns": total_turns,
                "user_turns": user_turns,
                "agent_turns": agent_turns,
                "user_id": user_id,
            }

        return context


class TestToolImplementations:
    """Test cases for tool implementations"""

    @pytest.mark.asyncio
    async def test_greeting_tool(self):
        """Test the greeting tool functionality"""
        tool = TestGreetingTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_name": "John"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert result.message_to_user == "Hello John!"
        assert result.message_to_llm is None
        assert result.context == context

    @pytest.mark.asyncio
    async def test_greeting_tool_hindi(self):
        """Test the greeting tool in Hindi"""
        tool = TestGreetingTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.HINDI,
            allowed_languages=[SarvamToolLanguageName.HINDI],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_name": "राहुल"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert result.message_to_user == "नमस्ते राहुल!"
        assert result.message_to_llm is None
        assert result.context == context

    @pytest.mark.asyncio
    async def test_weather_tool(self):
        """Test the weather tool functionality"""
        tool = TestWeatherTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"location": "Mumbai"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "Mumbai" in result.message_to_user
        assert "sunny" in result.message_to_user
        assert "25°C" in result.message_to_user
        assert result.message_to_llm is not None
        assert "Mumbai" in result.message_to_llm

    @pytest.mark.asyncio
    async def test_language_change_tool(self):
        """Test the language change tool functionality"""
        tool = TestLanguageChangeTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"target_language": SarvamToolLanguageName.HINDI},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert result.message_to_user == "Language changed to Hindi"
        assert context.language == SarvamToolLanguageName.HINDI

    @pytest.mark.asyncio
    async def test_language_change_tool_invalid(self):
        """Test the language change tool with invalid language"""
        tool = TestLanguageChangeTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"target_language": "InvalidLanguage"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "InvalidLanguage is not supported" in result.message_to_user
        assert context.language == SarvamToolLanguageName.ENGLISH  # Should not change

    @pytest.mark.asyncio
    async def test_end_conversation_tool(self):
        """Test the end conversation tool functionality"""
        tool = TestEndConversationTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "Goodbye" in result.message_to_user
        assert context.end_conversation is True

    @pytest.mark.asyncio
    async def test_end_conversation_tool_hindi(self):
        """Test the end conversation tool in Hindi"""
        tool = TestEndConversationTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.HINDI,
            allowed_languages=[SarvamToolLanguageName.HINDI],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "अलविदा" in result.message_to_user
        assert context.end_conversation is True


class TestOnStartToolImplementations:
    """Test cases for on-start tool implementations"""

    @pytest.mark.asyncio
    async def test_welcome_on_start_tool(self):
        """Test the welcome on-start tool functionality"""
        tool = TestWelcomeOnStartTool()
        context = SarvamOnStartToolContext(
            user_identifier="user123",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "Welcome user123" in result.initial_bot_message
        assert "How can I help you today" in result.initial_bot_message
        assert result.initial_state_name == "main_menu"

    @pytest.mark.asyncio
    async def test_welcome_on_start_tool_hindi(self):
        """Test the welcome on-start tool in Hindi"""
        tool = TestWelcomeOnStartTool()
        context = SarvamOnStartToolContext(
            user_identifier="user456",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.HINDI,
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "स्वागत है user456" in result.initial_bot_message
        assert "मैं आज आपकी कैसे मदद कर सकता हूं" in result.initial_bot_message


class TestOnEndToolImplementations:
    """Test cases for on-end tool implementations"""

    @pytest.mark.asyncio
    async def test_analytics_on_end_tool(self):
        """Test the analytics on-end tool functionality"""
        tool = TestAnalyticsOnEndTool()

        # Create a sample transcript
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[
                SarvamInteractionTurn(
                    role=SarvamInteractionTurnRole.USER, en_text="Hello"
                ),
                SarvamInteractionTurn(
                    role=SarvamInteractionTurnRole.AGENT, en_text="Hi there!"
                ),
                SarvamInteractionTurn(
                    role=SarvamInteractionTurnRole.USER, en_text="How are you?"
                ),
                SarvamInteractionTurn(
                    role=SarvamInteractionTurnRole.AGENT,
                    en_text="I'm doing well, thank you!",
                ),
            ],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )

        context = SarvamOnEndToolContext(
            user_identifier="user123",
            interaction_transcript=transcript,
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        assert "analytics" in result.agent_variables
        analytics = result.agent_variables["analytics"]
        assert analytics["total_turns"] == 4
        assert analytics["user_turns"] == 2
        assert analytics["agent_turns"] == 2
        assert analytics["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_analytics_on_end_tool_no_transcript(self):
        """Test the analytics on-end tool with empty transcript"""
        tool = TestAnalyticsOnEndTool()

        # Create an empty transcript since it's required
        empty_transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )

        context = SarvamOnEndToolContext(
            user_identifier="user123",
            interaction_transcript=empty_transcript,
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)

        # Should have analytics with 0 counts when transcript is empty
        assert "analytics" in result.agent_variables
        analytics = result.agent_variables["analytics"]
        assert analytics["total_turns"] == 0
        assert analytics["user_turns"] == 0
        assert analytics["agent_turns"] == 0
        assert analytics["user_id"] == "user123"


class TestToolOutputValidation:
    """Test cases for SarvamToolOutput validation"""

    def _create_context(self, language=SarvamToolLanguageName.ENGLISH):
        """Helper method to create a context with required fields"""
        return SarvamToolContext(
            language=language,
            allowed_languages=[language],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )

    def test_tool_output_with_message_to_user(self):
        """Test tool output with message to user"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        output = SarvamToolOutput(message_to_user="Hello!", context=context)
        assert output.message_to_user == "Hello!"
        assert output.message_to_llm is None

    def test_tool_output_with_message_to_llm(self):
        """Test tool output with message to LLM"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        output = SarvamToolOutput(
            message_to_llm="Internal processing complete", context=context
        )
        assert output.message_to_llm == "Internal processing complete"
        assert output.message_to_user is None

    def test_tool_output_with_both_messages(self):
        """Test tool output with both messages"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        output = SarvamToolOutput(
            message_to_user="Hello!",
            message_to_llm="Internal processing complete",
            context=context,
        )
        assert output.message_to_user == "Hello!"
        assert output.message_to_llm == "Internal processing complete"

    def test_tool_output_with_no_messages(self):
        """Test tool output validation with no messages (should fail)"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        with pytest.raises(
            ValueError,
            match="At least one of message_to_llm or message_to_user must be set",
        ):
            SarvamToolOutput(context=context)


class TestToolIntegration:
    """Integration tests for multiple tools working together"""

    @pytest.mark.asyncio
    async def test_conversation_flow(self):
        """Test a complete conversation flow with multiple tools"""
        # Start with greeting
        greeting_tool = TestGreetingTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_name": "Alice"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await greeting_tool.run(context)
        assert "Hello Alice" in result.message_to_user

        # Change language
        language_tool = TestLanguageChangeTool()
        context.agent_variables["target_language"] = SarvamToolLanguageName.HINDI
        result = await language_tool.run(context)
        assert context.language == SarvamToolLanguageName.HINDI

        # Get weather
        weather_tool = TestWeatherTool()
        context.agent_variables["location"] = "Delhi"
        result = await weather_tool.run(context)
        assert "Delhi" in result.message_to_user

        # End conversation
        end_tool = TestEndConversationTool()
        result = await end_tool.run(context)
        assert context.end_conversation is True


class TestStateTransitionValidation:
    """Test cases for state transition validation"""

    def test_valid_state_transition(self):
        """Test valid state transition"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings", "help"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should not raise an exception
        context.change_state("weather")
        assert context.get_current_state() == "weather"

    def test_invalid_state_transition(self):
        """Test invalid state transition raises ValueError"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings", "help"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        with pytest.raises(ValueError, match="State invalid_state not valid"):
            context.change_state("invalid_state")

    def test_state_transition_with_empty_next_states(self):
        """Test state transition when no next states are allowed"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="end_conversation",
            next_valid_states=[],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        with pytest.raises(ValueError, match="State any_state not valid"):
            context.change_state("any_state")

    def test_state_transition_to_same_state(self):
        """Test state transition to the same state (should be valid)"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["main_menu", "weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should not raise an exception
        context.change_state("main_menu")
        assert context.get_current_state() == "main_menu"

    def test_get_current_state(self):
        """Test getting current state"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="settings",
            next_valid_states=["main_menu", "weather"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        assert context.get_current_state() == "settings"


class TestLanguageValidation:
    """Test cases for language validation"""

    def test_valid_language_change(self):
        """Test valid language change"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
                SarvamToolLanguageName.MARATHI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should not raise an exception
        context.change_language(SarvamToolLanguageName.HINDI)
        assert context.get_current_language() == SarvamToolLanguageName.HINDI

    def test_invalid_language_change(self):
        """Test invalid language change raises ValueError"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        with pytest.raises(ValueError, match="Language Marathi not allowed"):
            context.change_language(SarvamToolLanguageName.MARATHI)

    def test_language_change_with_empty_allowed_languages(self):
        """Test language change when no languages are allowed"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        with pytest.raises(ValueError, match="Language Hindi not allowed"):
            context.change_language(SarvamToolLanguageName.HINDI)

    def test_language_change_to_same_language(self):
        """Test language change to the same language (should be valid)"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should not raise an exception
        context.change_language(SarvamToolLanguageName.ENGLISH)
        assert context.get_current_language() == SarvamToolLanguageName.ENGLISH

    def test_get_current_language(self):
        """Test getting current language"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.HINDI,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        assert context.get_current_language() == SarvamToolLanguageName.HINDI

    def test_all_languages_allowed(self):
        """Test when all languages are allowed"""
        all_languages = [
            SarvamToolLanguageName.BENGALI,
            SarvamToolLanguageName.GUJARATI,
            SarvamToolLanguageName.KANNADA,
            SarvamToolLanguageName.MALAYALAM,
            SarvamToolLanguageName.TAMIL,
            SarvamToolLanguageName.TELUGU,
            SarvamToolLanguageName.PUNJABI,
            SarvamToolLanguageName.ODIA,
            SarvamToolLanguageName.MARATHI,
            SarvamToolLanguageName.HINDI,
            SarvamToolLanguageName.ENGLISH,
        ]

        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=all_languages,
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Test changing to each language
        for language in all_languages:
            context.change_language(language)
            assert context.get_current_language() == language


class TestStateAndLanguageIntegration:
    """Integration tests for state and language validation"""

    def test_state_and_language_changes_together(self):
        """Test state and language changes work together"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
                SarvamToolLanguageName.MARATHI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings", "help"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Change language first
        context.change_language(SarvamToolLanguageName.HINDI)
        assert context.get_current_language() == SarvamToolLanguageName.HINDI

        # Then change state
        context.change_state("weather")
        assert context.get_current_state() == "weather"

        # Change both again
        context.change_language(SarvamToolLanguageName.MARATHI)
        context.change_state("settings")
        assert context.get_current_language() == SarvamToolLanguageName.MARATHI
        assert context.get_current_state() == "settings"

    def test_context_persistence_across_changes(self):
        """Test that context persists correctly across state and language changes"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_name": "John", "location": "Mumbai"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Store initial values
        initial_language = context.get_current_language()
        initial_state = context.get_current_state()
        initial_variables = context.agent_variables.copy()

        # Make changes
        context.change_language(SarvamToolLanguageName.HINDI)
        context.change_state("weather")

        # Verify other properties remain unchanged
        assert context.agent_variables == initial_variables
        assert context.allowed_languages == [
            SarvamToolLanguageName.ENGLISH,
            SarvamToolLanguageName.HINDI,
        ]
        assert context.next_valid_states == ["weather", "settings"]

        # Verify changes were made
        assert context.get_current_language() != initial_language
        assert context.get_current_state() != initial_state


class TestStateAwareTool(SarvamTool):
    """Example tool that changes state and validates transitions"""

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        current_state = context.get_current_state()
        user_name = context.get_agent_variable("user_name")

        if current_state == "main_menu":
            # Transition to weather state
            context.change_state("weather")
            return SarvamToolOutput(
                message_to_user=f"Hello {user_name}! Let me get the weather for you.",
                context=context,
            )
        elif current_state == "weather":
            # Transition to settings state
            context.change_state("settings")
            return SarvamToolOutput(
                message_to_user="Weather information provided. Now in settings.",
                context=context,
            )
        else:
            return SarvamToolOutput(
                message_to_user="Unknown state. Returning to main menu.",
                context=context,
            )


class TestLanguageAwareTool(SarvamTool):
    """Example tool that changes language and validates allowed languages"""

    async def run(self, context: SarvamToolContext) -> SarvamToolOutput:
        target_language = context.get_agent_variable("target_language")
        user_name = context.get_agent_variable("user_name")

        try:
            context.change_language(target_language)
            greetings = {
                SarvamToolLanguageName.ENGLISH: f"Hello {user_name}!",
                SarvamToolLanguageName.HINDI: f"नमस्ते {user_name}!",
                SarvamToolLanguageName.MARATHI: f"नमस्कार {user_name}!",
            }
            greeting = greetings.get(target_language, f"Hello {user_name}!")
            return SarvamToolOutput(
                message_to_user=greeting,
                context=context,
            )
        except ValueError as e:
            return SarvamToolOutput(
                message_to_user=f"Language change failed: {str(e)}",
                context=context,
            )


class TestToolWithStateAndLanguageValidation:
    """Test tools that use state and language validation"""

    @pytest.mark.asyncio
    async def test_state_aware_tool_valid_transitions(self):
        """Test state aware tool with valid state transitions"""
        tool = TestStateAwareTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_name": "Alice"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # First transition: main_menu -> weather
        result = await tool.run(context)
        assert "Hello Alice" in result.message_to_user
        assert context.get_current_state() == "weather"

        # Second transition: weather -> settings
        result = await tool.run(context)
        assert "Weather information provided" in result.message_to_user
        assert context.get_current_state() == "settings"

    @pytest.mark.asyncio
    async def test_state_aware_tool_invalid_transition(self):
        """Test state aware tool with invalid state transition"""
        tool = TestStateAwareTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="unknown_state",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_name": "Alice"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should handle unknown state gracefully
        result = await tool.run(context)
        assert "Unknown state" in result.message_to_user

    @pytest.mark.asyncio
    async def test_language_aware_tool_valid_language(self):
        """Test language aware tool with valid language change"""
        tool = TestLanguageAwareTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.HINDI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={
                "user_name": "राहुल",
                "target_language": SarvamToolLanguageName.HINDI,
            },
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)
        assert "नमस्ते राहुल" in result.message_to_user
        assert context.get_current_language() == SarvamToolLanguageName.HINDI

    @pytest.mark.asyncio
    async def test_language_aware_tool_invalid_language(self):
        """Test language aware tool with invalid language change"""
        tool = TestLanguageAwareTool()
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={
                "user_name": "Alice",
                "target_language": SarvamToolLanguageName.HINDI,
            },
            engagement_metadata=create_test_engagement_metadata(),
        )

        result = await tool.run(context)
        assert "Language change failed" in result.message_to_user
        assert context.get_current_language() == SarvamToolLanguageName.ENGLISH


class TestContextValidation:
    """Test cases for context validation and edge cases"""

    def test_context_with_no_allowed_languages(self):
        """Test context with no allowed languages"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should not be able to change to any language
        with pytest.raises(ValueError, match="Language Hindi not allowed"):
            context.change_language(SarvamToolLanguageName.HINDI)

    def test_context_with_no_next_valid_states(self):
        """Test context with no next valid states"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="end_conversation",
            next_valid_states=[],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Should not be able to change to any state
        with pytest.raises(ValueError, match="State any_state not valid"):
            context.change_state("any_state")

    def test_context_initialization_validation(self):
        """Test context initialization with various combinations"""
        # Valid initialization
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context is not None

        # Test with current language not in allowed languages
        # Note: Current implementation doesn't validate during construction
        # This test documents the expected behavior if validation is added
        context_with_invalid_language = SarvamToolContext(
            language=SarvamToolLanguageName.HINDI,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )
        # Should fail when trying to change language
        with pytest.raises(ValueError, match="Language Hindi not allowed"):
            context_with_invalid_language.change_language(SarvamToolLanguageName.HINDI)

        # Test with current state not in next valid states
        # Note: Current implementation doesn't validate during construction
        # This test documents the expected behavior if validation is added
        context_with_invalid_state = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )
        # Should fail when trying to change state
        with pytest.raises(ValueError, match="State main_menu not valid"):
            context_with_invalid_state.change_state("main_menu")

    def test_end_conversation_setting(self):
        """Test setting end conversation flag"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={},
            engagement_metadata=create_test_engagement_metadata(),
        )

        assert context.end_conversation is False
        context.set_end_conversation()
        assert context.end_conversation is True
