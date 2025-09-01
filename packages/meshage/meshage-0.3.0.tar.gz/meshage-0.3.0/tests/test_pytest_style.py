"""
Pytest-style tests for the meshage library.
"""

from unittest.mock import AsyncMock, patch

import pytest
from meshtastic.protobuf import mesh_pb2, portnums_pb2

from meshage.config import xor_checksum
from meshage.messages import MeshtasticMessage, MeshtasticNodeInfoMessage, MeshtasticTextMessage


class TestConfigPytest:
    """Pytest-style tests for the MQTTConfig class."""

    def test_xor_checksum_empty(self):
        """Test xor_checksum with empty bytes."""
        assert xor_checksum(b"") == 0

    def test_xor_checksum_single_byte(self):
        """Test xor_checksum with a single byte."""
        assert xor_checksum(b"\x01") == 1

    def test_xor_checksum_multiple_bytes(self):
        """Test xor_checksum with multiple bytes."""
        assert xor_checksum(b"\x01\x02\x03") == 0  # 1 ^ 2 ^ 3 = 0

    def test_config_defaults(self, config):
        """Test that config defaults are set correctly."""
        # Test that all required keys exist and have valid values
        required_keys = ["host", "port", "username", "password", "root_topic", "channel", "userid", "key"]
        for key in required_keys:
            assert key in config.config
            assert config.config[key] is not None
        
        # Test that key is properly decoded (not the default "AQ==")
        assert config.config["key"] != "AQ=="
        assert len(config.config["key"]) > 4

    def test_userid_property(self, config):
        """Test the userid property formatting."""
        expected_userid = "!%08x" % 452664778
        assert config.userid == expected_userid

    def test_publish_topic_property(self, config):
        """Test the publish_topic property formatting."""
        # Test that topic follows the expected format
        expected_format = f"{config.config['root_topic']}/2/e/{config.config['channel']}/{config.userid}"
        assert config.publish_topic == expected_format

    def test_receive_topic_property(self, config):
        """Test the receive_topic property formatting."""
        # Test that topic follows the expected format
        expected_format = f"{config.config['root_topic']}/2/e/{config.config['channel']}/#"
        assert config.receive_topic == expected_format

    def test_key_property(self, config):
        """Test the key property base64 decoding."""
        key_bytes = config.key
        assert isinstance(key_bytes, bytes)
        # Key length can vary depending on the actual key used
        assert len(key_bytes) > 0

    def test_encoded_channel_property(self, config):
        """Test the encoded_channel property calculation."""
        encoded_channel = config.encoded_channel
        assert isinstance(encoded_channel, int)
        assert encoded_channel > 0

    def test_aiomqtt_config_property(self, config):
        """Test the aiomqtt_config property."""
        aiomqtt_config = config.aiomqtt_config
        expected_keys = {"hostname", "port", "username", "password"}
        assert set(aiomqtt_config.keys()) == expected_keys
        # Test that values match the config
        assert aiomqtt_config["hostname"] == config.config["host"]
        assert aiomqtt_config["port"] == config.config["port"]
        assert aiomqtt_config["username"] == config.config["username"]
        assert aiomqtt_config["password"] == config.config["password"]


class TestTextMessagePytest:
    """Pytest-style tests for the MeshtasticTextMessage class."""

    def test_text_message_init(self, config, sample_text):
        """Test text message initialization."""
        message = MeshtasticTextMessage(sample_text, config)

        assert message.config == config
        assert message.payload == sample_text.encode("utf-8")
        assert message.type == portnums_pb2.TEXT_MESSAGE_APP
        assert isinstance(message.message_id, int)
        assert message.message_id > 0

    def test_text_encoding_variations(self, config):
        """Test text encoding with various inputs."""
        test_cases = [
            "Simple text",
            "Text with unicode: 🚀",
            "Text with special chars: !@#$%^&*()",
            "",
            "Very long text " * 100,
        ]

        for text in test_cases:
            message = MeshtasticTextMessage(text, config)
            assert message.payload == text.encode("utf-8")

    def test_message_id_uniqueness(self, config):
        """Test that message IDs are unique."""
        message1 = MeshtasticTextMessage("First message", config)
        message2 = MeshtasticTextMessage("Second message", config)

        assert message1.message_id != message2.message_id

    def test_packet_creation(self, config, sample_text):
        """Test packet creation for text messages."""
        message = MeshtasticTextMessage(sample_text, config)
        packet = message.packet()

        assert packet.id == message.message_id
        assert getattr(packet, "from") == config.config["userid"]
        assert packet.to == 0xFFFFFFFF  # BROADCAST_NUM
        assert packet.want_ack is False
        assert packet.channel == config.encoded_channel
        assert packet.hop_limit == 3
        assert packet.hop_start == 3
        assert isinstance(packet.encrypted, bytes)

    def test_bytes_conversion(self, config, sample_text):
        """Test conversion to bytes."""
        message = MeshtasticTextMessage(sample_text, config)
        bytes_result = bytes(message)

        assert isinstance(bytes_result, bytes)
        assert len(bytes_result) > 0

    def test_encryption_integration(self, config, sample_text):
        """Test that text messages are properly encrypted."""
        packet = MeshtasticTextMessage(sample_text, config).packet()

        original_text_bytes = sample_text.encode("utf-8")
        assert packet.encrypted != original_text_bytes
        assert len(packet.encrypted) > 0


class TestNodeInfoMessagePytest:
    """Pytest-style tests for the MeshtasticNodeInfoMessage class."""

    def test_node_info_init(self, config):
        """Test node info message initialization."""
        message = MeshtasticNodeInfoMessage(config)

        assert message.config == config
        assert message.type == portnums_pb2.NODEINFO_APP
        assert isinstance(message.message_id, int)
        assert message.message_id > 0
        assert isinstance(message.payload, bytes)
        assert len(message.payload) > 0

    def test_payload_creation(self, config):
        """Test that the payload is properly created from User protobuf."""
        message = MeshtasticNodeInfoMessage(config)

        user = mesh_pb2.User()
        user.ParseFromString(message.payload)

        assert user.id == config.userid
        assert user.short_name == "MQTT"
        assert user.long_name == f"Meshage {config.userid}"
        assert user.hw_model == mesh_pb2.HardwareModel.PRIVATE_HW
        assert user.is_unmessagable is True

    def test_message_id_uniqueness(self, config):
        """Test that message IDs are unique."""
        message1 = MeshtasticNodeInfoMessage(config)
        message2 = MeshtasticNodeInfoMessage(config)

        assert message1.message_id != message2.message_id

    def test_packet_creation(self, config):
        """Test packet creation for node info messages."""
        message = MeshtasticNodeInfoMessage(config)
        packet = message.packet()

        assert packet.id == message.message_id
        assert getattr(packet, "from") == config.config["userid"]
        assert packet.to == 0xFFFFFFFF  # BROADCAST_NUM
        assert packet.want_ack is False
        assert packet.channel == config.encoded_channel
        assert packet.hop_limit == 3
        assert packet.hop_start == 3
        assert isinstance(packet.encrypted, bytes)

    def test_bytes_conversion(self, config):
        """Test conversion to bytes."""
        message = MeshtasticNodeInfoMessage(config)
        bytes_result = bytes(message)

        assert isinstance(bytes_result, bytes)
        assert len(bytes_result) > 0

    def test_encryption_integration(self, config):
        """Test that node info messages are properly encrypted."""
        message = MeshtasticNodeInfoMessage(config)
        packet = message.packet()

        assert packet.encrypted != message.payload
        assert len(packet.encrypted) > 0


class TestIntegrationPytest:
    """Pytest-style integration tests."""

    def test_multiple_message_types(self, config):
        """Test creating multiple different types of messages."""
        text_message = MeshtasticTextMessage("Test message", config)
        node_info_message = MeshtasticNodeInfoMessage(config)

        assert text_message.type != node_info_message.type
        assert text_message.message_id != node_info_message.message_id

        text_bytes = bytes(text_message)
        node_info_bytes = bytes(node_info_message)

        assert isinstance(text_bytes, bytes)
        assert isinstance(node_info_bytes, bytes)
        assert len(text_bytes) > 0
        assert len(node_info_bytes) > 0

    def test_config_consistency(self, config):
        """Test that configuration is consistent across message types."""
        text_message = MeshtasticTextMessage("Test", config)
        node_info_message = MeshtasticNodeInfoMessage(config)

        assert text_message.config == config
        assert node_info_message.config == config

        text_packet = text_message.packet()
        node_info_packet = node_info_message.packet()

        assert getattr(text_packet, "from") == config.config["userid"]
        assert getattr(node_info_packet, "from") == config.config["userid"]
        assert text_packet.channel == config.encoded_channel
        assert node_info_packet.channel == config.encoded_channel

    def test_message_id_uniqueness_across_types(self, config):
        """Test that message IDs are unique across different message types."""
        messages = []

        for i in range(5):
            messages.append(MeshtasticTextMessage(f"Message {i}", config))

        for i in range(5):
            messages.append(MeshtasticNodeInfoMessage(config))

        message_ids = [msg.message_id for msg in messages]
        assert len(message_ids) == len(set(message_ids))

    @pytest.mark.asyncio
    async def test_mqtt_publishing_simulation(self, config):
        """Simulate MQTT publishing workflow."""
        with patch("aiomqtt.Client") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            text_message = MeshtasticTextMessage("Hello, world!", config)
            node_info_message = MeshtasticNodeInfoMessage(config)

            text_bytes = bytes(text_message)
            node_info_bytes = bytes(node_info_message)

            assert isinstance(text_bytes, bytes)
            assert isinstance(node_info_bytes, bytes)
            assert len(text_bytes) > 0
            assert len(node_info_bytes) > 0

            expected_topic = f"{config.config['root_topic']}/2/e/{config.config['channel']}/{config.userid}"
            assert config.publish_topic == expected_topic


class TestErrorHandlingPytest:
    """Pytest-style error handling tests."""

    def test_invalid_config_for_text_message(self):
        """Test error handling with invalid config for text message."""
        with pytest.raises((TypeError, AttributeError)):
            message = MeshtasticTextMessage("test", None)
            # The error would occur when trying to use the config
            # Try to access a property that uses the config
            _ = message.packet()

    def test_none_payload_for_text_message(self, config):
        """Test error handling with None payload for text message."""
        with pytest.raises(AttributeError):
            MeshtasticTextMessage(None, config)

    def test_abstract_class_instantiation_fails(self, config):
        """Test that trying to create an instance of MeshtasticMessage fails."""
        with pytest.raises(TypeError):
            # Attempting to instantiate the abstract base class should raise TypeError
            MeshtasticMessage(b"test payload", config)
