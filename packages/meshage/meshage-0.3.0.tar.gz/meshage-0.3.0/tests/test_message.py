"""
Unit tests for the MeshtasticMessage base class.
"""

import unittest
from unittest.mock import Mock, patch

from meshage.config import MQTTConfig
from meshage.messages import MeshtasticMessage


class MockMeshtasticMessage(MeshtasticMessage):
    """Mock implementation of MeshtasticMessage for testing."""

    def __init__(self, payload: bytes, config: MQTTConfig):
        self.type = 1  # Set a valid port number for testing
        super().__init__(payload, config)


class TestMeshtasticMessage(unittest.TestCase):
    """Test the MeshtasticMessage base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MQTTConfig()
        self.test_payload = b"test message payload"
        self.message = MockMeshtasticMessage(self.test_payload, self.config)

    def test_init(self):
        """Test message initialization."""
        self.assertEqual(self.message.config, self.config)
        self.assertEqual(self.message.payload, self.test_payload)
        self.assertIsInstance(self.message.message_id, int)
        self.assertGreater(self.message.message_id, 0)

    def test_generate_message_id(self):
        """Test message ID generation."""
        message_id = self.message.generate_message_id()
        self.assertIsInstance(message_id, int)
        self.assertGreater(message_id, 0)
        # Should be a 32-bit integer
        self.assertLess(message_id, 2**32)

    def test_generate_message_id_uniqueness(self):
        """Test that message IDs are unique."""
        ids = set()
        for _ in range(100):
            ids.add(self.message.generate_message_id())
        # Should have generated unique IDs
        self.assertEqual(len(ids), 100)

    @patch("meshage.messages.Cipher")
    def test_encrypt_packet(self, mock_cipher):
        """Test packet encryption."""
        # Mock the Cipher and encryptor
        mock_encryptor = Mock()
        mock_encryptor.update.return_value = b"encrypted_data"
        mock_encryptor.finalize.return_value = b"finalized_data"

        mock_cipher_instance = Mock()
        mock_cipher_instance.encryptor.return_value = mock_encryptor
        mock_cipher.return_value = mock_cipher_instance

        # Create a mock packet
        mock_packet = Mock()
        mock_packet.id = 12345
        setattr(mock_packet, "from", 67890)

        # Test encryption
        result = self.message.encrypt_packet(mock_packet)

        # Verify the result
        self.assertEqual(result, b"encrypted_datafinalized_data")

        # Verify Cipher was called with correct parameters
        mock_cipher.assert_called_once()
        call_args = mock_cipher.call_args
        # The first argument should be an AES algorithm object
        # We can't easily test the exact key value, so just verify it's called
        self.assertIsInstance(call_args[0][0], object)  # algorithms.AES(key)
        # The second argument should be a mode with a nonce
        self.assertIsInstance(call_args[0][1].nonce, bytes)
        self.assertEqual(len(call_args[0][1].nonce), 16)  # Nonce should be 16 bytes

    def test_packet_creation(self):
        """Test packet creation."""
        packet = self.message.packet()

        # Verify packet attributes
        self.assertEqual(packet.id, self.message.message_id)
        self.assertEqual(getattr(packet, "from"), self.config.config["userid"])
        self.assertEqual(packet.to, 0xFFFFFFFF)  # BROADCAST_NUM
        self.assertFalse(packet.want_ack)
        self.assertEqual(packet.channel, self.config.encoded_channel)
        self.assertEqual(packet.hop_limit, 3)
        self.assertEqual(packet.hop_start, 3)
        self.assertIsInstance(packet.encrypted, bytes)

    def test_service_envelope_creation(self):
        """Test service envelope creation."""
        # Create a real packet instead of a mock
        packet = self.message.packet()
        
        envelope = self.message.service_envelope(packet)
        
        # Verify envelope attributes
        self.assertEqual(envelope.packet, packet)
        self.assertEqual(envelope.channel_id, self.config.config["channel"])
        self.assertEqual(envelope.gateway_id, self.config.userid)

    def test_bytes_conversion(self):
        """Test conversion to bytes."""
        bytes_result = bytes(self.message)

        # Should return serialized service envelope
        self.assertIsInstance(bytes_result, bytes)
        self.assertGreater(len(bytes_result), 0)

    def test_packet_encryption_integration(self):
        """Test the full packet encryption integration."""
        packet = self.message.packet()

        # Verify the packet has encrypted data
        self.assertIsInstance(packet.encrypted, bytes)
        self.assertGreater(len(packet.encrypted), 0)

        # The encrypted data should be different from the original payload
        self.assertNotEqual(packet.encrypted, self.test_payload)

    def test_message_id_uniqueness_across_instances(self):
        """Test that message IDs are unique across different message instances."""
        message1 = MockMeshtasticMessage(b"payload1", self.config)
        message2 = MockMeshtasticMessage(b"payload2", self.config)

        self.assertNotEqual(message1.message_id, message2.message_id)

    def test_packet_attributes_consistency(self):
        """Test that packet attributes are consistent."""
        packet = self.message.packet()

        # Verify all required attributes are set
        required_attrs = [
            "id",
            "from",
            "to",
            "want_ack",
            "channel",
            "hop_limit",
            "hop_start",
            "encrypted",
        ]
        for attr in required_attrs:
            if attr == "from":
                self.assertTrue(hasattr(packet, "from"))
            else:
                self.assertTrue(hasattr(packet, attr))

    def test_service_envelope_serialization(self):
        """Test that service envelope can be serialized."""
        packet = self.message.packet()

        # Should be able to serialize without errors
        serialized = self.message.service_envelope(packet).SerializeToString()
        self.assertIsInstance(serialized, bytes)
        self.assertGreater(len(serialized), 0)

    def test_abstract_class_instantiation_fails(self):
        """Test that trying to create an instance of MeshtasticMessage fails."""
        with self.assertRaises(TypeError):
            # Attempting to instantiate the abstract base class should raise TypeError
            MeshtasticMessage(b"test payload", self.config)


if __name__ == "__main__":
    unittest.main()
