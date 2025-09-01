"""
Test to verify that the abstract MeshtasticMessage class cannot be instantiated.
"""

import os
import sys
import unittest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from meshage.config import MQTTConfig


class TestAbstractClassBehavior(unittest.TestCase):
    """Test that the abstract MeshtasticMessage class cannot be instantiated."""

    def test_abstract_class_instantiation_fails(self):
        """Test that trying to create an instance of MeshtasticMessage fails."""
        config = MQTTConfig()
        
        from meshage.messages import MeshtasticMessage
        
        with self.assertRaises(TypeError):
            # Attempting to instantiate the abstract base class should raise TypeError
            MeshtasticMessage(b"test payload", config)

    def test_abstract_class_has_abstract_methods(self):
        """Test that the abstract class has the expected abstract methods."""
        from meshage.messages import MeshtasticMessage

        # Check that the class is abstract
        self.assertTrue(hasattr(MeshtasticMessage, "__abstractmethods__"))

        # Check that it has the expected abstract methods
        abstract_methods = MeshtasticMessage.__abstractmethods__
        self.assertIn("__init__", abstract_methods)

    def test_concrete_subclasses_can_be_instantiated(self):
        """Test that concrete subclasses can be instantiated."""
        config = MQTTConfig()

        from meshage.messages import MeshtasticNodeInfoMessage, MeshtasticTextMessage

        # These should work without raising TypeError
        text_message = MeshtasticTextMessage("test", config)
        self.assertIsNotNone(text_message)

        node_info_message = MeshtasticNodeInfoMessage(config)
        self.assertIsNotNone(node_info_message)


if __name__ == "__main__":
    unittest.main()
