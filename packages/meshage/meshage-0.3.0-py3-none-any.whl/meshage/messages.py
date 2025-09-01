"""
An object oriented interface for sending and receiving Meshtastic messages via MQTT.

A large portion of this code is adapted from MQTT Connect for Meshtastic, version 0.8.7
https://github.com/pdxlocations/connect/blob/869be93a3c32d9550cbd63c1ae0ccb61686eca60/mqtt-connect.py
A number of functions have been broken up and reorganized to make it more usable as a library.
"""

import random
from abc import ABC, abstractmethod

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from meshtastic import BROADCAST_NUM
from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2

from .config import MQTTConfig


class MeshtasticMessage(ABC):
    type: portnums_pb2.PortNum.ValueType

    @abstractmethod
    def __init__(self, payload: bytes, config: MQTTConfig):
        self.config = config
        self.message_id = self.generate_message_id()
        self.payload = payload

    def generate_message_id(self) -> int:
        return random.getrandbits(32)

    def encrypt_packet(self, packet: mesh_pb2.MeshPacket) -> bytes:
        # Wrap payload in Data protobuf message
        data_msg = mesh_pb2.Data()
        data_msg.portnum = self.type
        data_msg.payload = self.payload
        data_msg.bitfield = 1

        nonce_packet_id = packet.id.to_bytes(8, "little")
        nonce_from_node = getattr(packet, "from").to_bytes(8, "little")
        nonce = nonce_packet_id + nonce_from_node
        encryptor = Cipher(
            algorithms.AES(self.config.key), modes.CTR(nonce), backend=default_backend()
        ).encryptor()
        return encryptor.update(data_msg.SerializeToString()) + encryptor.finalize()

    def packet(self) -> mesh_pb2.MeshPacket:
        packet = mesh_pb2.MeshPacket()
        packet.id = self.message_id
        setattr(
            packet, "from", self.config.config["userid"]
        )  # from is a reserved keyword
        packet.to = BROADCAST_NUM
        packet.want_ack = False
        packet.channel = self.config.encoded_channel
        packet.hop_limit = 3
        packet.hop_start = 3
        packet.encrypted = self.encrypt_packet(packet)
        return packet

    def service_envelope(self, packet: mesh_pb2.MeshPacket) -> mqtt_pb2.ServiceEnvelope:
        envelope = mqtt_pb2.ServiceEnvelope()
        envelope.packet.CopyFrom(packet)
        envelope.channel_id = self.config.config["channel"]
        envelope.gateway_id = self.config.userid
        return envelope

    def __bytes__(self) -> bytes:
        return self.service_envelope(self.packet()).SerializeToString()


class MeshtasticNodeInfoMessage(MeshtasticMessage):
    def __init__(self, config: MQTTConfig):
        self.type = portnums_pb2.NODEINFO_APP
        payload = mesh_pb2.User()
        payload.id = config.userid
        payload.short_name = "MQTT"
        payload.long_name = f"Meshage {config.userid}"
        payload.hw_model = mesh_pb2.HardwareModel.PRIVATE_HW
        payload.is_unmessagable = True

        super().__init__(payload.SerializeToString(), config)


class MeshtasticTextMessage(MeshtasticMessage):
    def __init__(self, payload: str, config: MQTTConfig):
        self.type = portnums_pb2.TEXT_MESSAGE_APP
        super().__init__(payload.encode("utf-8"), config)
