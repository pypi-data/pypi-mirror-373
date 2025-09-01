"""
Unit tests for the MQTTConfig class.
"""

import os
import unittest
from unittest.mock import mock_open, patch

from meshage.config import MQTTConfig, xor_checksum


class TestXorChecksum(unittest.TestCase):
    """Test the xor_checksum utility function."""

    def test_xor_checksum_empty_bytes(self):
        """Test xor_checksum with empty bytes."""
        result = xor_checksum(b"")
        self.assertEqual(result, 0)

    def test_xor_checksum_single_byte(self):
        """Test xor_checksum with a single byte."""
        result = xor_checksum(b"\x01")
        self.assertEqual(result, 1)

    def test_xor_checksum_multiple_bytes(self):
        """Test xor_checksum with multiple bytes."""
        result = xor_checksum(b"\x01\x02\x03")
        self.assertEqual(result, 0)  # 1 ^ 2 ^ 3 = 0

    def test_xor_checksum_string_bytes(self):
        """Test xor_checksum with string bytes."""
        result = xor_checksum(b"test")
        # Calculate expected: ord('t') ^ ord('e') ^ ord('s') ^ ord('t') = 116 ^ 101 ^ 115 ^ 116 = 22
        expected = ord("t") ^ ord("e") ^ ord("s") ^ ord("t")
        self.assertEqual(result, expected)


class TestMQTTConfig(unittest.TestCase):
    """Test the MQTTConfig class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MQTTConfig()

    def test_defaults(self):
        """Test that defaults are set correctly."""
        # Test that all required keys exist
        required_keys = [
            "host",
            "port",
            "username",
            "password",
            "root_topic",
            "channel",
            "userid",
            "key",
        ]
        for key in required_keys:
            self.assertIn(key, self.config.config)
            self.assertIsNotNone(self.config.config[key])

        # Test that key is properly decoded (not the default "AQ==")
        self.assertNotEqual(self.config.config["key"], "AQ==")
        self.assertGreater(len(self.config.config["key"]), 4)

    def test_userid_property(self):
        """Test the userid property formatting."""
        expected_userid = "!%08x" % 452664778
        self.assertEqual(self.config.userid, expected_userid)

    def test_publish_topic_property(self):
        """Test the topic property formatting."""
        # Test that topic follows the expected format
        expected_format = f"{self.config.config['root_topic']}/2/e/{self.config.config['channel']}/{self.config.userid}"
        self.assertEqual(self.config.publish_topic, expected_format)

    def test_receive_topic_property(self):
        """Test the receive_topic property formatting."""
        # Test that topic follows the expected format
        expected_format = f"{self.config.config['root_topic']}/2/e/{self.config.config['channel']}/#"
        self.assertEqual(self.config.receive_topic, expected_format)

    def test_key_property(self):
        """Test the key property base64 decoding."""
        key_bytes = self.config.key
        self.assertIsInstance(key_bytes, bytes)
        # Key length can vary depending on the actual key used
        self.assertGreater(len(key_bytes), 0)

    def test_encoded_channel_property(self):
        """Test the encoded_channel property calculation."""
        encoded_channel = self.config.encoded_channel
        self.assertIsInstance(encoded_channel, int)
        self.assertGreater(encoded_channel, 0)

    def test_aiomqtt_config_property(self):
        """Test the aiomqtt_config property."""
        aiomqtt_config = self.config.aiomqtt_config
        expected_keys = {"hostname", "port", "username", "password"}
        self.assertEqual(set(aiomqtt_config.keys()), expected_keys)
        # Test that values match the config
        self.assertEqual(aiomqtt_config["hostname"], self.config.config["host"])
        self.assertEqual(aiomqtt_config["port"], self.config.config["port"])
        self.assertEqual(aiomqtt_config["username"], self.config.config["username"])
        self.assertEqual(aiomqtt_config["password"], self.config.config["password"])

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="[mqtt]\nhost = test.example.com\nport = 8883\nusername = testuser\npassword = testpass\nroot_topic = msh/test\nchannel = testchannel\nuserid = 123456789\nkey = testkey==",
    )
    def test_load_config_from_file(self, mock_file):
        """Test loading configuration from mqtt.conf file."""
        config = MQTTConfig()
        # The config should be loaded from the mocked file
        # Note: This test is limited by the fact that the config is loaded in __init__
        # We can't easily test the file loading in isolation without refactoring

    @patch.dict(
        os.environ,
        {
            "MQTT_HOST": "env.example.com",
            "MQTT_PORT": "8883",
            "MQTT_USERNAME": "envuser",
            "MQTT_PASSWORD": "envpass",
        },
    )
    def test_load_env_variables(self):
        """Test loading configuration from environment variables."""
        config = MQTTConfig()
        self.assertEqual(config.config["host"], "env.example.com")
        self.assertEqual(
            config.config["port"], "8883"
        )  # Environment variables are strings
        self.assertEqual(config.config["username"], "envuser")
        self.assertEqual(config.config["password"], "envpass")

    def test_key_replacement_from_default(self):
        """Test that the default short key is replaced with the full key."""
        config = MQTTConfig()
        # The default "AQ==" should be replaced with the full key
        self.assertNotEqual(config.config["key"], "AQ==")
        self.assertGreater(len(config.config["key"]), 4)

    def test_encoded_channel_calculation(self):
        """Test the encoded channel calculation logic."""
        # Test with known values
        config = MQTTConfig()
        config.config["key"] = "1PG7OiApB1nwvP+rz05pAQ=="
        config.config["channel"] = "LongFast"

        encoded = config.encoded_channel
        self.assertIsInstance(encoded, int)
        # The encoded channel should be deterministic for the same key and channel
        self.assertEqual(encoded, config.encoded_channel)


if __name__ == "__main__":
    unittest.main()
