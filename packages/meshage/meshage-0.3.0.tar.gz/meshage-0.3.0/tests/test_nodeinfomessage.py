"""
Unit tests for the MeshtasticNodeInfoMessage class.
"""

import unittest

from meshtastic.protobuf import mesh_pb2, portnums_pb2

from meshage.config import MQTTConfig
from meshage.messages import MeshtasticNodeInfoMessage


class TestMeshtasticNodeInfoMessage(unittest.TestCase):
    """Test the MeshtasticNodeInfoMessage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MQTTConfig()
        self.message = MeshtasticNodeInfoMessage(self.config)

    def test_init(self):
        """Test node info message initialization."""
        self.assertEqual(self.message.config, self.config)
        self.assertEqual(self.message.type, portnums_pb2.NODEINFO_APP)
        self.assertIsInstance(self.message.message_id, int)
        self.assertGreater(self.message.message_id, 0)
        self.assertIsInstance(self.message.payload, bytes)
        self.assertGreater(len(self.message.payload), 0)

    def test_type_assignment(self):
        """Test that the correct port number type is assigned."""
        self.assertEqual(self.message.type, portnums_pb2.NODEINFO_APP)

    def test_inheritance(self):
        """Test that MeshtasticNodeInfoMessage properly inherits from MeshtasticMessage."""
        # Should have all the methods from the parent class
        self.assertTrue(hasattr(self.message, "generate_message_id"))
        self.assertTrue(hasattr(self.message, "encrypt_packet"))
        self.assertTrue(hasattr(self.message, "packet"))
        self.assertTrue(hasattr(self.message, "service_envelope"))
        self.assertTrue(hasattr(self.message, "__bytes__"))

    def test_payload_creation(self):
        """Test that the payload is properly created from User protobuf."""
        # The payload should be a serialized User protobuf message
        user = mesh_pb2.User()
        user.ParseFromString(self.message.payload)

        # Verify User message fields
        self.assertEqual(user.id, self.config.userid)
        self.assertEqual(user.short_name, "MQTT")
        self.assertEqual(user.long_name, f"Meshage {self.config.userid}")
        self.assertEqual(user.hw_model, mesh_pb2.HardwareModel.PRIVATE_HW)
        self.assertTrue(user.is_unmessagable)

    def test_user_message_fields(self):
        """Test that the User message has the correct fields."""
        user = mesh_pb2.User()
        user.ParseFromString(self.message.payload)

        # Test individual fields
        self.assertEqual(user.id, self.config.userid)
        self.assertEqual(user.short_name, "MQTT")
        self.assertEqual(user.long_name, f"Meshage {self.config.userid}")
        self.assertEqual(user.hw_model, mesh_pb2.HardwareModel.PRIVATE_HW)
        self.assertTrue(user.is_unmessagable)

    def test_message_id_uniqueness(self):
        """Test that message IDs are unique for different node info messages."""
        message1 = MeshtasticNodeInfoMessage(self.config)
        message2 = MeshtasticNodeInfoMessage(self.config)

        self.assertNotEqual(message1.message_id, message2.message_id)

    def test_packet_creation(self):
        """Test that node info messages can create packets."""
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
        """Test that node info messages can create service envelopes."""
        packet = self.message.packet()
        envelope = self.message.service_envelope(packet)

        # Verify envelope attributes
        self.assertEqual(envelope.packet, packet)
        self.assertEqual(envelope.channel_id, self.config.config["channel"])
        self.assertEqual(envelope.gateway_id, self.config.userid)

    def test_bytes_conversion(self):
        """Test that node info messages can be converted to bytes."""
        bytes_result = bytes(self.message)

        # Should return serialized service envelope
        self.assertIsInstance(bytes_result, bytes)
        self.assertGreater(len(bytes_result), 0)

    def test_encryption_integration(self):
        """Test that node info messages are properly encrypted."""
        packet = self.message.packet()

        # The encrypted data should be different from the original payload
        self.assertNotEqual(packet.encrypted, self.message.payload)
        self.assertGreater(len(packet.encrypted), 0)

    def test_userid_consistency(self):
        """Test that the userid is consistent across the message."""
        user = mesh_pb2.User()
        user.ParseFromString(self.message.payload)

        # The userid in the User message should match the config userid
        self.assertEqual(user.id, self.config.userid)

    def test_hardware_model(self):
        """Test that the hardware model is set correctly."""
        user = mesh_pb2.User()
        user.ParseFromString(self.message.payload)

        # Should be set to PRIVATE_HW
        self.assertEqual(user.hw_model, mesh_pb2.HardwareModel.PRIVATE_HW)

    def test_is_unmessagable_flag(self):
        """Test that the is_unmessagable flag is set correctly."""
        user = mesh_pb2.User()
        user.ParseFromString(self.message.payload)

        # Should be set to True
        self.assertTrue(user.is_unmessagable)

    def test_short_name_and_long_name(self):
        """Test that short_name and long_name are set correctly."""
        user = mesh_pb2.User()
        user.ParseFromString(self.message.payload)

        # Short name should be "MQTT"
        self.assertEqual(user.short_name, "MQTT")

        # Long name should include the userid
        self.assertEqual(user.long_name, f"Meshage {self.config.userid}")

    def test_payload_serialization(self):
        """Test that the payload can be properly serialized and deserialized."""
        # Create a new message
        message = MeshtasticNodeInfoMessage(self.config)

        # Serialize the payload
        serialized = message.payload

        # Deserialize it back
        user = mesh_pb2.User()
        user.ParseFromString(serialized)

        # Verify the deserialized data matches expected values
        self.assertEqual(user.id, self.config.userid)
        self.assertEqual(user.short_name, "MQTT")
        self.assertEqual(user.long_name, f"Meshage {self.config.userid}")
        self.assertEqual(user.hw_model, mesh_pb2.HardwareModel.PRIVATE_HW)
        self.assertTrue(user.is_unmessagable)

    def test_multiple_instances(self):
        """Test that multiple node info message instances work correctly."""
        messages = []
        for _ in range(5):
            message = MeshtasticNodeInfoMessage(self.config)
            messages.append(message)

        # All messages should have unique IDs
        message_ids = [msg.message_id for msg in messages]
        self.assertEqual(len(message_ids), len(set(message_ids)))

        # All messages should have the same payload structure but different IDs
        for message in messages:
            user = mesh_pb2.User()
            user.ParseFromString(message.payload)

            # Verify the User message structure is consistent
            self.assertEqual(user.id, self.config.userid)
            self.assertEqual(user.short_name, "MQTT")
            self.assertEqual(user.long_name, f"Meshage {self.config.userid}")
            self.assertEqual(user.hw_model, mesh_pb2.HardwareModel.PRIVATE_HW)
            self.assertTrue(user.is_unmessagable)


if __name__ == "__main__":
    unittest.main()
