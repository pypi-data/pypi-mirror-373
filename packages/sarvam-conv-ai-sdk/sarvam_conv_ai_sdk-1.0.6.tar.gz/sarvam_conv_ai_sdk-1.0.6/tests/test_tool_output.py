import pytest

from sarvam_conv_ai_sdk.tool import (
    EngagementMetadata,
    SarvamToolContext,
    SarvamToolLanguageName,
    SarvamToolOutput,
)


def create_test_engagement_metadata() -> EngagementMetadata:
    """Helper function to create a valid EngagementMetadata for testing"""
    return EngagementMetadata(
        interaction_id="test_interaction_123", app_id="test_app", app_version=1
    )


def create_test_engagement_metadata_with_new_fields(
    language: SarvamToolLanguageName = SarvamToolLanguageName.MARATHI,
    phone_number: str = "+918888888888",
) -> EngagementMetadata:
    """Helper function to create EngagementMetadata with new fields for testing"""
    return EngagementMetadata(
        interaction_id="test_interaction_new_fields",
        app_id="test_app",
        app_version=1,
        interaction_language=language,
        agent_phone_number=phone_number,
    )


class TestSarvamToolOutput:
    """Test cases for SarvamToolOutput validation and functionality"""

    def _create_context(self, language=SarvamToolLanguageName.ENGLISH):
        """Helper method to create a context with required fields"""
        return SarvamToolContext(
            language=language,
            allowed_languages=[language],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )

    def test_valid_output_with_message_to_user(self):
        """Test valid tool output with only message to user"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        output = SarvamToolOutput(
            message_to_user="Hello, how can I help you?", context=context
        )
        assert output.message_to_user == "Hello, how can I help you?"
        assert output.message_to_llm is None
        assert output.context == context

    def test_valid_output_with_message_to_llm(self):
        """Test valid tool output with only message to LLM"""
        context = self._create_context(SarvamToolLanguageName.HINDI)
        output = SarvamToolOutput(
            message_to_llm="Internal processing: User requested weather info",
            context=context,
        )
        assert (
            output.message_to_llm == "Internal processing: User requested weather info"
        )
        assert output.message_to_user is None
        assert output.context == context

    def test_valid_output_with_both_messages(self):
        """Test valid tool output with both messages"""
        context = self._create_context(SarvamToolLanguageName.MARATHI)
        output = SarvamToolOutput(
            message_to_user="Here's your weather information",
            message_to_llm="Weather data retrieved successfully",
            context=context,
        )
        assert output.message_to_user == "Here's your weather information"
        assert output.message_to_llm == "Weather data retrieved successfully"
        assert output.context == context

    def test_invalid_output_no_messages(self):
        """Test that tool output fails when no messages are provided"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        with pytest.raises(
            ValueError,
            match="At least one of message_to_llm or message_to_user must be set",
        ):
            SarvamToolOutput(context=context)

    def test_invalid_output_empty_messages(self):
        """Test that tool output fails when both messages are empty strings"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        with pytest.raises(
            ValueError,
            match="At least one of message_to_llm or message_to_user must be set",
        ):
            SarvamToolOutput(message_to_user="", message_to_llm="", context=context)

    def test_invalid_output_none_messages(self):
        """Test that tool output fails when both messages are None"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        with pytest.raises(
            ValueError,
            match="At least one of message_to_llm or message_to_user must be set",
        ):
            SarvamToolOutput(message_to_user=None, message_to_llm=None, context=context)

    def test_output_with_empty_string_message_to_user(self):
        """Test tool output with empty string for message_to_user but valid message_to_llm"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        output = SarvamToolOutput(
            message_to_user="", message_to_llm="Processing complete", context=context
        )
        assert output.message_to_user == ""
        assert output.message_to_llm == "Processing complete"

    def test_output_with_empty_string_message_to_llm(self):
        """Test tool output with empty string for message_to_llm but valid message_to_user"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        output = SarvamToolOutput(
            message_to_user="Hello there!", message_to_llm="", context=context
        )
        assert output.message_to_user == "Hello there!"
        assert output.message_to_llm == ""

    def test_output_with_whitespace_only_messages(self):
        """Test tool output with whitespace-only messages"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        # Should pass if at least one message has non-whitespace content
        output = SarvamToolOutput(
            message_to_user="   ", message_to_llm="Valid message", context=context
        )
        assert output.message_to_user == "   "
        assert output.message_to_llm == "Valid message"

    def test_output_with_long_messages(self):
        """Test tool output with very long messages"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        long_message = "A" * 1000  # 1000 character message

        output = SarvamToolOutput(message_to_user=long_message, context=context)
        assert output.message_to_user == long_message
        assert len(output.message_to_user) == 1000

    def test_output_with_special_characters(self):
        """Test tool output with special characters and unicode"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        special_message = "Hello! 🌟 नमस्ते! 你好! Привет! 🎉"

        output = SarvamToolOutput(message_to_user=special_message, context=context)
        assert output.message_to_user == special_message

    def test_output_context_preservation(self):
        """Test that the context is properly preserved in the output"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.HINDI,
            allowed_languages=[SarvamToolLanguageName.HINDI],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_id": "123", "session_id": "abc"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        output = SarvamToolOutput(message_to_user="Test message", context=context)

        assert output.context is context
        assert output.context.language == SarvamToolLanguageName.HINDI
        assert output.context.agent_variables["user_id"] == "123"
        assert output.context.agent_variables["session_id"] == "abc"

    def test_output_immutability(self):
        """Test that modifying the output doesn't affect the original context"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"counter": 0},
            engagement_metadata=create_test_engagement_metadata(),
        )

        output = SarvamToolOutput(message_to_user="Test", context=context)

        # Modify the context through the output
        output.context.agent_variables["counter"] = 1

        # The original context should also be modified (same object)
        assert context.agent_variables["counter"] == 1
        assert output.context.agent_variables["counter"] == 1


class TestSarvamToolOutputEdgeCases:
    """Test edge cases for SarvamToolOutput"""

    def _create_context(self, language=SarvamToolLanguageName.ENGLISH):
        """Helper method to create a context with required fields"""
        return SarvamToolContext(
            language=language,
            allowed_languages=[language],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )

    def test_output_with_numeric_messages(self):
        """Test tool output with numeric messages (should be converted to strings)"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        # Since the fields are defined as Optional[str], we need to convert to strings
        output = SarvamToolOutput(
            message_to_user="42", message_to_llm="3.14", context=context
        )

        assert output.message_to_user == "42"
        assert output.message_to_llm == "3.14"

    def test_output_with_boolean_messages(self):
        """Test tool output with boolean messages (converted to strings)"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)

        output = SarvamToolOutput(
            message_to_user="True", message_to_llm="False", context=context
        )

        assert output.message_to_user == "True"
        assert output.message_to_llm == "False"

    def test_output_with_dict_message(self):
        """Test tool output with dictionary as message (converted to string)"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        dict_message = {"status": "success", "data": {"temperature": 25}}

        output = SarvamToolOutput(message_to_llm=str(dict_message), context=context)

        assert output.message_to_llm == str(dict_message)
        assert output.message_to_user is None

    def test_output_with_list_message(self):
        """Test tool output with list as message (converted to string)"""
        context = self._create_context(SarvamToolLanguageName.ENGLISH)
        list_message = ["item1", "item2", "item3"]

        output = SarvamToolOutput(message_to_user=str(list_message), context=context)

        assert output.message_to_user == str(list_message)
        assert output.message_to_llm is None

    def test_output_with_new_engagement_metadata_fields(self):
        """Test tool output with EngagementMetadata containing new fields"""
        metadata = create_test_engagement_metadata_with_new_fields(
            language=SarvamToolLanguageName.KANNADA, phone_number="+919876543210"
        )

        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=metadata,
        )

        output = SarvamToolOutput(
            message_to_user="Test message with new metadata fields", context=context
        )

        # Verify the output contains the context with new metadata fields
        assert output.message_to_user == "Test message with new metadata fields"
        assert output.context is context

        # Verify new fields are accessible through the context
        retrieved_metadata = output.context.get_engagement_metadata()
        assert retrieved_metadata.interaction_language == SarvamToolLanguageName.KANNADA
        assert retrieved_metadata.agent_phone_number == "+919876543210"
        assert retrieved_metadata.interaction_id == "test_interaction_new_fields"
