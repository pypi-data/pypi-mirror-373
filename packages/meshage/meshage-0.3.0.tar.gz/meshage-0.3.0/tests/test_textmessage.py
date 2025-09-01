"""
Unit tests for the MeshtasticTextMessage class.
"""

import unittest

from meshtastic.protobuf import portnums_pb2

from meshage.config import MQTTConfig
from meshage.messages import MeshtasticTextMessage


class TestMeshtasticTextMessage(unittest.TestCase):
    """Test the MeshtasticTextMessage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MQTTConfig()
        self.test_text = "Hello, world!"
        self.message = MeshtasticTextMessage(self.test_text, self.config)

    def test_init(self):
        """Test text message initialization."""
        self.assertEqual(self.message.config, self.config)
        self.assertEqual(self.message.payload, self.test_text.encode("utf-8"))
        self.assertEqual(self.message.type, portnums_pb2.TEXT_MESSAGE_APP)
        self.assertIsInstance(self.message.message_id, int)
        self.assertGreater(self.message.message_id, 0)

    def test_text_encoding(self):
        """Test that text is properly encoded as UTF-8."""
        test_cases = [
            "Simple text",
            "Text with unicode: 🚀",
            "Text with special chars: !@#$%^&*()",
            "Empty string",
            "Very long text " * 100,
        ]

        for text in test_cases:
            message = MeshtasticTextMessage(text, self.config)
            self.assertEqual(message.payload, text.encode("utf-8"))

    def test_type_assignment(self):
        """Test that the correct port number type is assigned."""
        self.assertEqual(self.message.type, portnums_pb2.TEXT_MESSAGE_APP)

    def test_inheritance(self):
        """Test that MeshtasticTextMessage properly inherits from MeshtasticMessage."""
        # Should have all the methods from the parent class
        self.assertTrue(hasattr(self.message, "generate_message_id"))
        self.assertTrue(hasattr(self.message, "encrypt_packet"))
        self.assertTrue(hasattr(self.message, "packet"))
        self.assertTrue(hasattr(self.message, "service_envelope"))
        self.assertTrue(hasattr(self.message, "__bytes__"))

    def test_message_id_uniqueness(self):
        """Test that message IDs are unique for different text messages."""
        message1 = MeshtasticTextMessage("First message", self.config)
        message2 = MeshtasticTextMessage("Second message", self.config)

        self.assertNotEqual(message1.message_id, message2.message_id)

    def test_packet_creation(self):
        """Test that text messages can create packets."""
        packet = self.message.packet()

        # Verify packet has required attributes
        self.assertEqual(packet.id, self.message.message_id)
        self.assertEqual(getattr(packet, "from"), self.config.config["userid"])
        self.assertEqual(packet.to, 0xFFFFFFFF)  # BROADCAST_NUM
        self.assertFalse(packet.want_ack)
        self.assertEqual(packet.channel, self.config.encoded_channel)
        self.assertEqual(packet.hop_limit, 3)
        self.assertEqual(packet.hop_start, 3)
        self.assertIsInstance(packet.encrypted, bytes)

    def test_service_envelope_creation(self):
        """Test that text messages can create service envelopes."""
        packet = self.message.packet()
        envelope = self.message.service_envelope(packet)

        # Verify envelope attributes
        self.assertEqual(envelope.packet, packet)
        self.assertEqual(envelope.channel_id, self.config.config["channel"])
        self.assertEqual(envelope.gateway_id, self.config.userid)

    def test_bytes_conversion(self):
        """Test that text messages can be converted to bytes."""
        bytes_result = bytes(self.message)

        # Should return serialized service envelope
        self.assertIsInstance(bytes_result, bytes)
        self.assertGreater(len(bytes_result), 0)

    def test_encryption_integration(self):
        """Test that text messages are properly encrypted."""
        packet = self.message.packet()

        # The encrypted data should be different from the original text
        original_text_bytes = self.test_text.encode("utf-8")
        self.assertNotEqual(packet.encrypted, original_text_bytes)
        self.assertGreater(len(packet.encrypted), 0)

    def test_empty_text(self):
        """Test handling of empty text."""
        empty_message = MeshtasticTextMessage("", self.config)
        self.assertEqual(empty_message.payload, b"")
        self.assertEqual(empty_message.type, portnums_pb2.TEXT_MESSAGE_APP)

    def test_unicode_text(self):
        """Test handling of unicode text."""
        unicode_text = "Hello 世界! 🚀"
        unicode_message = MeshtasticTextMessage(unicode_text, self.config)
        self.assertEqual(unicode_message.payload, unicode_text.encode("utf-8"))

    def test_special_characters(self):
        """Test handling of special characters."""
        special_text = "Text with \n\t\r special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_message = MeshtasticTextMessage(special_text, self.config)
        self.assertEqual(special_message.payload, special_text.encode("utf-8"))

    def test_long_text(self):
        """Test handling of long text."""
        long_text = "A" * 1000
        long_message = MeshtasticTextMessage(long_text, self.config)
        self.assertEqual(long_message.payload, long_text.encode("utf-8"))

    def test_multiple_instances(self):
        """Test that multiple text message instances work correctly."""
        messages = []
        for i in range(10):
            text = f"Message {i}"
            message = MeshtasticTextMessage(text, self.config)
            messages.append(message)

        # All messages should have unique IDs
        message_ids = [msg.message_id for msg in messages]
        self.assertEqual(len(message_ids), len(set(message_ids)))

        # All messages should have correct payloads
        for i, message in enumerate(messages):
            expected_text = f"Message {i}"
            self.assertEqual(message.payload, expected_text.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
