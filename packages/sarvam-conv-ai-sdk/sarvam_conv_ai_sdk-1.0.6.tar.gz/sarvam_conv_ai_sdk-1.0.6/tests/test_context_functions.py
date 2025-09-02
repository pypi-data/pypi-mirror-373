from datetime import datetime

import pytest

from sarvam_conv_ai_sdk.tool import (
    EngagementMetadata,
    SarvamInteractionTranscript,
    SarvamInteractionTurn,
    SarvamInteractionTurnRole,
    SarvamOnEndToolContext,
    SarvamOnStartToolContext,
    SarvamToolBaseContext,
    SarvamToolContext,
    SarvamToolLanguageName,
    is_value_serializable,
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


def create_test_engagement_metadata_with_language(
    language: SarvamToolLanguageName = SarvamToolLanguageName.HINDI,
) -> EngagementMetadata:
    """Helper function to create EngagementMetadata with specific interaction language"""
    return EngagementMetadata(
        interaction_id="test_interaction_language",
        app_id="test_app",
        app_version=1,
        interaction_language=language,
    )


def create_test_engagement_metadata_with_phone(
    phone_number: str = "911234567890",
) -> EngagementMetadata:
    """Helper function to create EngagementMetadata with agent phone number"""
    return EngagementMetadata(
        interaction_id="test_interaction_phone",
        app_id="test_app",
        app_version=1,
        agent_phone_number=phone_number,
    )


def create_test_engagement_metadata_complete(
    interaction_language: SarvamToolLanguageName = SarvamToolLanguageName.MARATHI,
    agent_phone_number: str = "+911234567890",
) -> EngagementMetadata:
    """Helper function to create EngagementMetadata with all fields including new ones"""
    return EngagementMetadata(
        interaction_id="test_interaction_complete",
        attempt_id="test_attempt_complete",
        campaign_id="test_campaign_complete",
        interaction_language=interaction_language,
        app_id="test_app_complete",
        app_version=2,
        agent_phone_number=agent_phone_number,
    )


class TestSarvamToolBaseContext:
    """Test cases for SarvamToolBaseContext functionality"""

    def test_initialization(self):
        """Test context initialization with empty agent variables"""
        context = SarvamToolBaseContext(
            engagement_metadata=create_test_engagement_metadata()
        )
        assert context.agent_variables == {}

    def test_initialization_with_variables(self):
        """Test context initialization with predefined agent variables"""
        variables = {"user_id": "123", "session_id": "abc"}
        context = SarvamToolBaseContext(
            agent_variables=variables,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.agent_variables == variables

    def test_set_agent_variable_success(self):
        """Test setting agent variable successfully"""
        context = SarvamToolBaseContext(
            agent_variables={"user_id": "123"},
            engagement_metadata=create_test_engagement_metadata(),
        )
        context.set_agent_variable("user_id", "456")
        assert context.agent_variables["user_id"] == "456"

    def test_set_agent_variable_not_defined(self):
        """Test setting agent variable that is not defined"""
        context = SarvamToolBaseContext(
            engagement_metadata=create_test_engagement_metadata()
        )
        with pytest.raises(ValueError, match="Variable test_var not defined"):
            context.set_agent_variable("test_var", "value")

    def test_get_agent_variable_success(self):
        """Test getting agent variable successfully"""
        context = SarvamToolBaseContext(
            agent_variables={"user_id": "123"},
            engagement_metadata=create_test_engagement_metadata(),
        )
        value = context.get_agent_variable("user_id")
        assert value == "123"

    def test_get_agent_variable_not_found(self):
        """Test getting agent variable that doesn't exist"""
        context = SarvamToolBaseContext(
            engagement_metadata=create_test_engagement_metadata()
        )
        with pytest.raises(ValueError, match="Variable test_var not found"):
            context.get_agent_variable("test_var")

    def test_set_agent_variable_non_serializable(self):
        """Test setting non-serializable agent variable"""
        context = SarvamToolBaseContext(
            agent_variables={"test": "value"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Test with a function (non-serializable)
        def test_func():
            pass

        with pytest.raises(ValueError, match="Variable value is not serializable"):
            context.set_agent_variable("test", test_func)


class TestSarvamToolContext:
    """Test cases for SarvamToolContext functionality"""

    def test_initialization(self):
        """Test context initialization with default values"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.language == SarvamToolLanguageName.ENGLISH
        assert context.end_conversation is False
        assert context.agent_variables == {}

    def test_get_current_language(self):
        """Test getting current language"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.HINDI,
            allowed_languages=[SarvamToolLanguageName.HINDI],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.get_current_language() == SarvamToolLanguageName.HINDI

    def test_change_language(self):
        """Test changing language"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.MARATHI,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )
        context.change_language(SarvamToolLanguageName.MARATHI)
        assert context.language == SarvamToolLanguageName.MARATHI

    def test_set_end_conversation(self):
        """Test setting end conversation flag"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=create_test_engagement_metadata(),
        )
        context.set_end_conversation()
        assert context.end_conversation is True

    def test_inheritance_from_base_context(self):
        """Test that SarvamToolContext inherits functionality from base context"""
        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            agent_variables={"user_id": "123"},
            engagement_metadata=create_test_engagement_metadata(),
        )

        # Test inherited functionality
        assert context.get_agent_variable("user_id") == "123"
        context.set_agent_variable("user_id", "456")
        assert context.get_agent_variable("user_id") == "456"


class TestSarvamOnStartToolContext:
    """Test cases for SarvamOnStartToolContext functionality"""

    def test_initialization(self):
        """Test context initialization with required parameters"""
        context = SarvamOnStartToolContext(
            user_identifier="user123",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.user_identifier == "user123"
        assert context.initial_state_name == "welcome"
        assert context.initial_language_name == SarvamToolLanguageName.ENGLISH
        assert context.initial_bot_message is None

    def test_get_user_identifier(self):
        """Test getting user identifier"""
        context = SarvamOnStartToolContext(
            user_identifier="user456",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.get_user_identifier() == "user456"

    def test_set_initial_bot_message(self):
        """Test setting initial bot message"""
        context = SarvamOnStartToolContext(
            user_identifier="user123",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=create_test_engagement_metadata(),
        )
        context.set_initial_bot_message("Hello! Welcome to our service.")
        assert context.initial_bot_message == "Hello! Welcome to our service."

    def test_set_initial_state_name(self):
        """Test setting initial state name"""
        context = SarvamOnStartToolContext(
            user_identifier="user123",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=create_test_engagement_metadata(),
        )
        context.set_initial_state_name("main_menu")
        assert context.initial_state_name == "main_menu"

    def test_set_initial_language_name(self):
        """Test setting initial language name"""
        context = SarvamOnStartToolContext(
            user_identifier="user123",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=create_test_engagement_metadata(),
        )
        context.set_initial_language_name(SarvamToolLanguageName.HINDI)
        assert context.initial_language_name == SarvamToolLanguageName.HINDI


class TestSarvamOnEndToolContext:
    """Test cases for SarvamOnEndToolContext functionality"""

    def test_initialization(self):
        """Test context initialization with required parameters"""
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        context = SarvamOnEndToolContext(
            user_identifier="user123",
            interaction_transcript=transcript,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.user_identifier == "user123"
        assert context.interaction_transcript == transcript

    def test_initialization_with_transcript(self):
        """Test context initialization with interaction transcript"""
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[
                SarvamInteractionTurn(
                    role=SarvamInteractionTurnRole.USER, en_text="Hello"
                ),
                SarvamInteractionTurn(
                    role=SarvamInteractionTurnRole.AGENT, en_text="Hi there!"
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
        assert context.user_identifier == "user123"
        assert context.interaction_transcript == transcript

    def test_get_user_identifier(self):
        """Test getting user identifier"""
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        context = SarvamOnEndToolContext(
            user_identifier="user456",
            interaction_transcript=transcript,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.get_user_identifier() == "user456"

    def test_get_interaction_transcript(self):
        """Test getting interaction transcript"""
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        context = SarvamOnEndToolContext(
            user_identifier="user123",
            interaction_transcript=transcript,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.get_interaction_transcript() == transcript

    def test_get_interaction_transcript_none(self):
        """Test getting interaction transcript when it's empty"""
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        context = SarvamOnEndToolContext(
            user_identifier="user123",
            interaction_transcript=transcript,
            engagement_metadata=create_test_engagement_metadata(),
        )
        assert context.get_interaction_transcript() == transcript
        assert len(context.get_interaction_transcript().interaction_transcript) == 0


class TestUtilityFunctions:
    """Test cases for utility functions"""

    def test_is_value_serializable_string(self):
        """Test serialization check with string"""
        assert is_value_serializable("test") is True

    def test_is_value_serializable_dict(self):
        """Test serialization check with dictionary"""
        data = {"key": "value", "number": 123}
        assert is_value_serializable(data) is True

    def test_is_value_serializable_list(self):
        """Test serialization check with list"""
        data = [1, 2, 3, "test"]
        assert is_value_serializable(data) is True

    def test_is_value_serializable_function(self):
        """Test serialization check with function (should fail)"""

        def test_func():
            pass

        with pytest.raises(ValueError, match="Variable value is not serializable"):
            is_value_serializable(test_func)

    def test_is_value_serializable_class(self):
        """Test serialization check with class (should fail)"""

        class TestClass:
            pass

        with pytest.raises(ValueError, match="Variable value is not serializable"):
            is_value_serializable(TestClass)


class TestSarvamToolLanguageName:
    """Test cases for SarvamToolLanguageName enum"""

    def test_all_languages_present(self):
        """Test that all expected languages are present in the enum"""
        expected_languages = [
            "Bengali",
            "Gujarati",
            "Kannada",
            "Malayalam",
            "Tamil",
            "Telugu",
            "Punjabi",
            "Odia",
            "Marathi",
            "Hindi",
            "English",
        ]

        for language in expected_languages:
            assert hasattr(SarvamToolLanguageName, language.upper())
            assert getattr(SarvamToolLanguageName, language.upper()) == language

    def test_language_values(self):
        """Test specific language values"""
        assert SarvamToolLanguageName.ENGLISH == "English"
        assert SarvamToolLanguageName.HINDI == "Hindi"
        assert SarvamToolLanguageName.MARATHI == "Marathi"


class TestSarvamInteractionTranscript:
    """Test cases for SarvamInteractionTranscript"""

    def test_initialization(self):
        """Test transcript initialization"""
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        assert transcript.interaction_transcript == []

    def test_with_interaction_turns(self):
        """Test transcript with interaction turns"""
        turns = [
            SarvamInteractionTurn(role=SarvamInteractionTurnRole.USER, en_text="Hello"),
            SarvamInteractionTurn(
                role=SarvamInteractionTurnRole.AGENT, en_text="Hi there!"
            ),
        ]

        transcript = SarvamInteractionTranscript(
            interaction_transcript=turns,
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        assert len(transcript.interaction_transcript) == 2
        assert (
            transcript.interaction_transcript[0].role == SarvamInteractionTurnRole.USER
        )
        assert transcript.interaction_transcript[0].en_text == "Hello"
        assert (
            transcript.interaction_transcript[1].role == SarvamInteractionTurnRole.AGENT
        )
        assert transcript.interaction_transcript[1].en_text == "Hi there!"


class TestSarvamInteractionTurn:
    """Test cases for SarvamInteractionTurn"""

    def test_initialization(self):
        """Test interaction turn initialization"""
        turn = SarvamInteractionTurn(
            role=SarvamInteractionTurnRole.USER, en_text="Hello world"
        )
        assert turn.role == SarvamInteractionTurnRole.USER
        assert turn.en_text == "Hello world"

    def test_user_role(self):
        """Test user role interaction turn"""
        turn = SarvamInteractionTurn(
            role=SarvamInteractionTurnRole.USER, en_text="What's the weather like?"
        )
        assert turn.role == "user"
        assert turn.en_text == "What's the weather like?"

    def test_agent_role(self):
        """Test agent role interaction turn"""
        turn = SarvamInteractionTurn(
            role=SarvamInteractionTurnRole.AGENT, en_text="The weather is sunny today."
        )
        assert turn.role == "agent"
        assert turn.en_text == "The weather is sunny today."


class TestEngagementMetadata:
    """Test cases for EngagementMetadata functionality and new fields"""

    def test_basic_initialization(self):
        """Test basic EngagementMetadata initialization with required fields only"""
        metadata = EngagementMetadata(
            interaction_id="test_interaction_123", app_id="test_app", app_version=1
        )
        assert metadata.interaction_id == "test_interaction_123"
        assert metadata.app_id == "test_app"
        assert metadata.app_version == 1
        assert metadata.attempt_id is None
        assert metadata.campaign_id is None
        # Test new fields with defaults
        assert metadata.interaction_language == SarvamToolLanguageName.ENGLISH
        assert metadata.agent_phone_number is None

    def test_initialization_with_all_fields(self):
        """Test EngagementMetadata initialization with all fields"""
        metadata = EngagementMetadata(
            interaction_id="test_interaction_456",
            attempt_id="test_attempt_123",
            campaign_id="test_campaign_789",
            interaction_language=SarvamToolLanguageName.HINDI,
            app_id="test_app",
            app_version=2,
            agent_phone_number="911234567890",
        )
        assert metadata.interaction_id == "test_interaction_456"
        assert metadata.attempt_id == "test_attempt_123"
        assert metadata.campaign_id == "test_campaign_789"
        assert metadata.interaction_language == SarvamToolLanguageName.HINDI
        assert metadata.app_id == "test_app"
        assert metadata.app_version == 2
        assert metadata.agent_phone_number == "911234567890"

    def test_interaction_language_default(self):
        """Test that interaction_language defaults to English"""
        metadata = EngagementMetadata(
            interaction_id="test_interaction_123", app_id="test_app", app_version=1
        )
        assert metadata.interaction_language == SarvamToolLanguageName.ENGLISH

    def test_interaction_language_all_values(self):
        """Test interaction_language with all supported language values"""
        languages = [
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

        for language in languages:
            metadata = EngagementMetadata(
                interaction_id="test_interaction_123",
                app_id="test_app",
                app_version=1,
                interaction_language=language,
            )
            assert metadata.interaction_language == language

    def test_agent_phone_number_default(self):
        """Test that agent_phone_number defaults to None"""
        metadata = EngagementMetadata(
            interaction_id="test_interaction_123", app_id="test_app", app_version=1
        )
        assert metadata.agent_phone_number is None

    def test_agent_phone_number_valid_formats(self):
        """Test agent_phone_number with various valid phone number formats"""
        valid_phone_numbers = [
            "911234567890",
            "+911234567890",
            "1234567890",
            "+1-234-567-8900",
            "234-567-8900",
            "(234) 567-8900",
            "+91 98765 43210",
            "98765-43210",
        ]

        for phone_number in valid_phone_numbers:
            metadata = EngagementMetadata(
                interaction_id="test_interaction_123",
                app_id="test_app",
                app_version=1,
                agent_phone_number=phone_number,
            )
            assert metadata.agent_phone_number == phone_number

    def test_agent_phone_number_none(self):
        """Test agent_phone_number with explicit None value"""
        metadata = EngagementMetadata(
            interaction_id="test_interaction_123",
            app_id="test_app",
            app_version=1,
            agent_phone_number=None,
        )
        assert metadata.agent_phone_number is None

    def test_agent_phone_number_empty_string(self):
        """Test agent_phone_number with empty string"""
        metadata = EngagementMetadata(
            interaction_id="test_interaction_123",
            app_id="test_app",
            app_version=1,
            agent_phone_number="",
        )
        assert metadata.agent_phone_number == ""

    def test_combined_new_fields(self):
        """Test both new fields together with various combinations"""
        test_cases = [
            # (interaction_language, agent_phone_number)
            (SarvamToolLanguageName.ENGLISH, None),
            (SarvamToolLanguageName.HINDI, "911234567890"),
            (SarvamToolLanguageName.MARATHI, "+911234567890"),
            (SarvamToolLanguageName.TAMIL, ""),
            (SarvamToolLanguageName.BENGALI, "+1-234-567-8900"),
        ]

        for language, phone_number in test_cases:
            metadata = EngagementMetadata(
                interaction_id="test_interaction_123",
                app_id="test_app",
                app_version=1,
                interaction_language=language,
                agent_phone_number=phone_number,
            )
            assert metadata.interaction_language == language
            assert metadata.agent_phone_number == phone_number

    def test_backwards_compatibility(self):
        """Test that existing code without new fields still works"""
        # This simulates existing code that doesn't know about new fields
        metadata = EngagementMetadata(
            interaction_id="test_interaction_legacy",
            attempt_id="test_attempt_legacy",
            campaign_id="test_campaign_legacy",
            app_id="legacy_app",
            app_version=1,
        )

        # Should have default values for new fields
        assert metadata.interaction_language == SarvamToolLanguageName.ENGLISH
        assert metadata.agent_phone_number is None

        # Old fields should work as before
        assert metadata.interaction_id == "test_interaction_legacy"
        assert metadata.attempt_id == "test_attempt_legacy"
        assert metadata.campaign_id == "test_campaign_legacy"
        assert metadata.app_id == "legacy_app"
        assert metadata.app_version == 1


class TestEngagementMetadataIntegration:
    """Integration tests for EngagementMetadata with new fields in various contexts"""

    def test_sarvam_tool_context_with_new_engagement_fields(self):
        """Test SarvamToolContext with EngagementMetadata containing new fields"""
        metadata = create_test_engagement_metadata_complete(
            interaction_language=SarvamToolLanguageName.TAMIL,
            agent_phone_number="+918765432109",
        )

        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[
                SarvamToolLanguageName.ENGLISH,
                SarvamToolLanguageName.TAMIL,
            ],
            state="main_menu",
            next_valid_states=["weather", "settings"],
            engagement_metadata=metadata,
        )

        # Verify context works with new metadata fields
        retrieved_metadata = context.get_engagement_metadata()
        assert retrieved_metadata.interaction_language == SarvamToolLanguageName.TAMIL
        assert retrieved_metadata.agent_phone_number == "+918765432109"
        assert retrieved_metadata.interaction_id == "test_interaction_complete"

    def test_sarvam_tool_base_context_with_new_engagement_fields(self):
        """Test SarvamToolBaseContext with EngagementMetadata containing new fields"""
        metadata = create_test_engagement_metadata_with_language(
            language=SarvamToolLanguageName.PUNJABI
        )

        context = SarvamToolBaseContext(
            agent_variables={"test_var": "test_value"},
            engagement_metadata=metadata,
        )

        # Verify base context works with new metadata fields
        retrieved_metadata = context.get_engagement_metadata()
        assert retrieved_metadata.interaction_language == SarvamToolLanguageName.PUNJABI
        assert retrieved_metadata.agent_phone_number is None

    def test_sarvam_on_start_tool_context_with_new_engagement_fields(self):
        """Test SarvamOnStartToolContext with EngagementMetadata containing new fields"""
        metadata = create_test_engagement_metadata_with_phone(
            phone_number="919876543210"
        )

        context = SarvamOnStartToolContext(
            user_identifier="start_user_123",
            initial_state_name="welcome",
            initial_language_name=SarvamToolLanguageName.GUJARATI,
            engagement_metadata=metadata,
        )

        # Verify context works with new metadata fields
        retrieved_metadata = context.get_engagement_metadata()
        assert (
            retrieved_metadata.interaction_language == SarvamToolLanguageName.ENGLISH
        )  # default
        assert retrieved_metadata.agent_phone_number == "919876543210"
        assert context.initial_language_name == SarvamToolLanguageName.GUJARATI

    def test_sarvam_on_end_tool_context_with_new_engagement_fields(self):
        """Test SarvamOnEndToolContext with EngagementMetadata containing new fields"""
        metadata = create_test_engagement_metadata_complete(
            interaction_language=SarvamToolLanguageName.KANNADA,
            agent_phone_number="+917654321098",
        )

        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )

        context = SarvamOnEndToolContext(
            user_identifier="end_user_456",
            interaction_transcript=transcript,
            engagement_metadata=metadata,
        )

        # Verify context works with new metadata fields
        retrieved_metadata = context.get_engagement_metadata()
        assert retrieved_metadata.interaction_language == SarvamToolLanguageName.KANNADA
        assert retrieved_metadata.agent_phone_number == "+917654321098"
        assert context.user_identifier == "end_user_456"

    def test_metadata_field_consistency_across_contexts(self):
        """Test that metadata with new fields remains consistent across different contexts"""
        # Create metadata with specific values
        original_metadata = EngagementMetadata(
            interaction_id="consistency_test_123",
            attempt_id="consistency_attempt",
            campaign_id="consistency_campaign",
            interaction_language=SarvamToolLanguageName.MALAYALAM,
            app_id="consistency_app",
            app_version=3,
            agent_phone_number="+916543210987",
        )

        # Test with SarvamToolContext
        tool_context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="test_state",
            next_valid_states=["next_state"],
            engagement_metadata=original_metadata,
        )

        # Test with SarvamOnStartToolContext
        start_context = SarvamOnStartToolContext(
            user_identifier="consistency_user",
            initial_state_name="start_state",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=original_metadata,
        )

        # Test with SarvamOnEndToolContext
        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        end_context = SarvamOnEndToolContext(
            user_identifier="consistency_user",
            interaction_transcript=transcript,
            engagement_metadata=original_metadata,
        )

        # Verify all contexts have same metadata values
        contexts = [tool_context, start_context, end_context]
        for context in contexts:
            metadata = context.get_engagement_metadata()
            assert metadata.interaction_id == "consistency_test_123"
            assert metadata.attempt_id == "consistency_attempt"
            assert metadata.campaign_id == "consistency_campaign"
            assert metadata.interaction_language == SarvamToolLanguageName.MALAYALAM
            assert metadata.app_id == "consistency_app"
            assert metadata.app_version == 3
            assert metadata.agent_phone_number == "+916543210987"

    def test_helper_functions_compatibility(self):
        """Test that new helper functions work with all context types"""
        # Test create_test_engagement_metadata_with_language
        language_metadata = create_test_engagement_metadata_with_language(
            SarvamToolLanguageName.ODIA
        )

        context = SarvamToolContext(
            language=SarvamToolLanguageName.ENGLISH,
            allowed_languages=[SarvamToolLanguageName.ENGLISH],
            state="test",
            next_valid_states=["test"],
            engagement_metadata=language_metadata,
        )
        assert (
            context.get_engagement_metadata().interaction_language
            == SarvamToolLanguageName.ODIA
        )

        # Test create_test_engagement_metadata_with_phone
        phone_metadata = create_test_engagement_metadata_with_phone(
            phone_number="918888888888"
        )

        start_context = SarvamOnStartToolContext(
            user_identifier="test_user",
            initial_state_name="test",
            initial_language_name=SarvamToolLanguageName.ENGLISH,
            engagement_metadata=phone_metadata,
        )
        assert (
            start_context.get_engagement_metadata().agent_phone_number == "918888888888"
        )

        # Test create_test_engagement_metadata_complete
        complete_metadata = create_test_engagement_metadata_complete(
            interaction_language=SarvamToolLanguageName.TELUGU,
            agent_phone_number="+919999999999",
        )

        transcript = SarvamInteractionTranscript(
            interaction_transcript=[],
            interaction_start_time=datetime.now(),
            interaction_end_time=datetime.now(),
        )
        end_context = SarvamOnEndToolContext(
            user_identifier="test_user",
            interaction_transcript=transcript,
            engagement_metadata=complete_metadata,
        )

        metadata = end_context.get_engagement_metadata()
        assert metadata.interaction_language == SarvamToolLanguageName.TELUGU
        assert metadata.agent_phone_number == "+919999999999"
