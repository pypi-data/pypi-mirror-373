import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2

from .config import MQTTConfig
from .messages import MeshtasticMessage, MeshtasticTextMessage


class MeshtasticMessageParser:
    def __init__(self, config: MQTTConfig):
        self.config = config

    def parse_message(self, message: bytes) -> MeshtasticMessage | None:
        if len(message) > mesh_pb2.Constants.DATA_PAYLOAD_LEN:
            logging.error(
                f"Message too long to be a Meshtastic message ({len(message)} bytes)"
            )
            return None

        try:
            service_envelope = mqtt_pb2.ServiceEnvelope()
            service_envelope.ParseFromString(message)
        except Exception:
            logging.exception(f"Failed to parse service envelope")
            return None

        if getattr(service_envelope.packet, "from") == self.config.config["userid"]:
            logging.debug(f"Ignoring message from self")
            return None

        logging.debug(
            f"Received message from {getattr(service_envelope.packet, 'from')}"
        )

        if service_envelope.packet.HasField(
            "encrypted"
        ) and not service_envelope.packet.HasField("decoded"):
            try:
                self.decrypt_packet(service_envelope.packet)
            except Exception:
                logging.exception(f"Failed to decrypt packet")
                return None

        if service_envelope.packet.decoded.portnum == portnums_pb2.TEXT_MESSAGE_APP:
            return MeshtasticTextMessage.decode(service_envelope.packet)

        logging.warning(
            f"Unknown message type: {service_envelope.packet.decoded.portnum}"
        )
        return None

    def decrypt_packet(self, packet: mesh_pb2.MeshPacket):
        nonce_packet_id = getattr(packet, "id").to_bytes(8, "little")
        nonce_from_node = getattr(packet, "from").to_bytes(8, "little")

        # Put both parts into a single byte array.
        nonce = nonce_packet_id + nonce_from_node

        cipher = Cipher(
            algorithms.AES(self.config.key), modes.CTR(nonce), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted_bytes = (
            decryptor.update(getattr(packet, "encrypted")) + decryptor.finalize()
        )

        data = mesh_pb2.Data()
        data.ParseFromString(decrypted_bytes)
        packet.decoded.CopyFrom(data)
