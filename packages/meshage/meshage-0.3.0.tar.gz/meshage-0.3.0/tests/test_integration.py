"""
Integration tests for the meshage library.
"""

import unittest
from unittest.mock import AsyncMock, patch

from meshage.config import MQTTConfig
from meshage.messages import MeshtasticNodeInfoMessage, MeshtasticTextMessage


class TestIntegration(unittest.TestCase):
    """Integration tests for the meshage library."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MQTTConfig()

    def test_text_message_workflow(self):
        """Test the complete workflow for creating and processing a text message."""
        # Create a text message
        text = "Hello, world!"
        message = MeshtasticTextMessage(text, self.config)

        # Verify message properties
        self.assertEqual(message.type, 1)  # TEXT_MESSAGE_APP
        self.assertEqual(message.payload, text.encode("utf-8"))
        self.assertIsInstance(message.message_id, int)

        # Create packet
        packet = message.packet()
        self.assertEqual(packet.id, message.message_id)
        self.assertEqual(getattr(packet, "from"), self.config.config["userid"])
        self.assertEqual(packet.to, 0xFFFFFFFF)  # BROADCAST_NUM
        self.assertFalse(packet.want_ack)
        self.assertEqual(packet.channel, self.config.encoded_channel)
        self.assertEqual(packet.hop_limit, 3)
        self.assertEqual(packet.hop_start, 3)
        self.assertIsInstance(packet.encrypted, bytes)

        # Create service envelope
        envelope = message.service_envelope(packet)
        self.assertEqual(envelope.packet, packet)
        self.assertEqual(envelope.channel_id, self.config.config["channel"])
        self.assertEqual(envelope.gateway_id, self.config.userid)

        # Convert to bytes
        bytes_result = bytes(message)
        self.assertIsInstance(bytes_result, bytes)
        self.assertGreater(len(bytes_result), 0)

    def test_node_info_message_workflow(self):
        """Test the complete workflow for creating and processing a node info message."""
        # Create a node info message
        message = MeshtasticNodeInfoMessage(self.config)

        # Verify message properties
        self.assertEqual(message.type, 4)  # NODEINFO_APP (actual value from meshtastic)
        self.assertIsInstance(message.payload, bytes)
        self.assertGreater(len(message.payload), 0)
        self.assertIsInstance(message.message_id, int)

        # Create packet
        packet = message.packet()
        self.assertEqual(packet.id, message.message_id)
        self.assertEqual(getattr(packet, "from"), self.config.config["userid"])
        self.assertEqual(packet.to, 0xFFFFFFFF)  # BROADCAST_NUM
        self.assertFalse(packet.want_ack)
        self.assertEqual(packet.channel, self.config.encoded_channel)
        self.assertEqual(packet.hop_limit, 3)
        self.assertEqual(packet.hop_start, 3)
        self.assertIsInstance(packet.encrypted, bytes)

        # Create service envelope
        envelope = message.service_envelope(packet)
        self.assertEqual(envelope.packet, packet)
        self.assertEqual(envelope.channel_id, self.config.config["channel"])
        self.assertEqual(envelope.gateway_id, self.config.userid)

        # Convert to bytes
        bytes_result = bytes(message)
        self.assertIsInstance(bytes_result, bytes)
        self.assertGreater(len(bytes_result), 0)

    def test_multiple_message_types(self):
        """Test creating multiple different types of messages."""
        # Create text message
        text_message = MeshtasticTextMessage("Test message", self.config)

        # Create node info message
        node_info_message = MeshtasticNodeInfoMessage(self.config)

        # Verify they have different types
        self.assertNotEqual(text_message.type, node_info_message.type)

        # Verify they have different message IDs
        self.assertNotEqual(text_message.message_id, node_info_message.message_id)

        # Verify they can both be converted to bytes
        text_bytes = bytes(text_message)
        node_info_bytes = bytes(node_info_message)

        self.assertIsInstance(text_bytes, bytes)
        self.assertIsInstance(node_info_bytes, bytes)
        self.assertGreater(len(text_bytes), 0)
        self.assertGreater(len(node_info_bytes), 0)

    def test_config_consistency_across_messages(self):
        """Test that configuration is consistent across different message types."""
        # Create different message types
        text_message = MeshtasticTextMessage("Test", self.config)
        node_info_message = MeshtasticNodeInfoMessage(self.config)

        # Verify they all use the same config
        self.assertEqual(text_message.config, self.config)
        self.assertEqual(node_info_message.config, self.config)

        # Verify they all generate packets with consistent config values
        text_packet = text_message.packet()
        node_info_packet = node_info_message.packet()

        self.assertEqual(getattr(text_packet, "from"), self.config.config["userid"])
        self.assertEqual(
            getattr(node_info_packet, "from"), self.config.config["userid"]
        )
        self.assertEqual(text_packet.channel, self.config.encoded_channel)
        self.assertEqual(node_info_packet.channel, self.config.encoded_channel)

    def test_message_encryption_consistency(self):
        """Test that encryption is consistent across message types."""
        # Create messages
        text_message = MeshtasticTextMessage("Test message", self.config)
        node_info_message = MeshtasticNodeInfoMessage(self.config)

        # Get packets
        text_packet = text_message.packet()
        node_info_packet = node_info_message.packet()

        # Verify encryption is applied
        self.assertIsInstance(text_packet.encrypted, bytes)
        self.assertIsInstance(node_info_packet.encrypted, bytes)
        self.assertGreater(len(text_packet.encrypted), 0)
        self.assertGreater(len(node_info_packet.encrypted), 0)

        # Verify encrypted data is different from original payload
        self.assertNotEqual(text_packet.encrypted, text_message.payload)
        self.assertNotEqual(node_info_packet.encrypted, node_info_message.payload)

    def test_service_envelope_consistency(self):
        """Test that service envelopes are consistent across message types."""
        # Create messages
        text_message = MeshtasticTextMessage("Test message", self.config)
        node_info_message = MeshtasticNodeInfoMessage(self.config)

        # Create service envelopes
        text_envelope = text_message.service_envelope(text_message.packet())
        node_info_envelope = node_info_message.service_envelope(
            node_info_message.packet()
        )

        # Verify envelope properties are consistent
        self.assertEqual(text_envelope.channel_id, self.config.config["channel"])
        self.assertEqual(node_info_envelope.channel_id, self.config.config["channel"])
        self.assertEqual(text_envelope.gateway_id, self.config.userid)
        self.assertEqual(node_info_envelope.gateway_id, self.config.userid)

        # Verify envelopes can be serialized
        text_serialized = text_envelope.SerializeToString()
        node_info_serialized = node_info_envelope.SerializeToString()

        self.assertIsInstance(text_serialized, bytes)
        self.assertIsInstance(node_info_serialized, bytes)
        self.assertGreater(len(text_serialized), 0)
        self.assertGreater(len(node_info_serialized), 0)

    @patch("aiomqtt.Client")
    def test_mqtt_publishing_simulation(self, mock_client):
        """Simulate MQTT publishing workflow."""
        # Mock the MQTT client
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Create messages
        text_message = MeshtasticTextMessage("Hello, world!", self.config)
        node_info_message = MeshtasticNodeInfoMessage(self.config)

        # Simulate publishing
        text_bytes = bytes(text_message)
        node_info_bytes = bytes(node_info_message)

        # Verify bytes are valid
        self.assertIsInstance(text_bytes, bytes)
        self.assertIsInstance(node_info_bytes, bytes)
        self.assertGreater(len(text_bytes), 0)
        self.assertGreater(len(node_info_bytes), 0)

        # Verify topic format
        expected_topic = f"{self.config.config['root_topic']}/2/e/{self.config.config['channel']}/{self.config.userid}"
        self.assertEqual(self.config.publish_topic, expected_topic)

    def test_error_handling(self):
        """Test error handling in message creation."""
        # Test with invalid config
        with self.assertRaises((TypeError, AttributeError)):
            message = MeshtasticTextMessage("test", None)
            # The error would occur when trying to use the config
            _ = message.packet()
        
        # Test with None payload for text message
        with self.assertRaises((TypeError, AttributeError)):
            MeshtasticTextMessage(None, self.config)

    def test_message_id_uniqueness_across_types(self):
        """Test that message IDs are unique across different message types."""
        # Create multiple messages of different types
        messages = []

        # Add text messages
        for i in range(5):
            messages.append(MeshtasticTextMessage(f"Message {i}", self.config))

        # Add node info messages
        for i in range(5):
            messages.append(MeshtasticNodeInfoMessage(self.config))

        # Verify all message IDs are unique
        message_ids = [msg.message_id for msg in messages]
        self.assertEqual(len(message_ids), len(set(message_ids)))


if __name__ == "__main__":
    unittest.main()
