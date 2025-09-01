"""
A large portion of this code is adapted from MQTT Connect for Meshtastic, version 0.8.7
https://github.com/pdxlocations/connect/blob/869be93a3c32d9550cbd63c1ae0ccb61686eca60/mqtt-connect.py
A number of functions have been broken up and reorganized to make it more usable as a library.
"""

import base64
import os
from configparser import ConfigParser, NoSectionError
from contextlib import suppress
from typing import Any, Dict, TypedDict


def xor_checksum(data: bytes) -> int:
    checksum: int = 0
    for char in data:
        checksum ^= char
    return checksum


class ConfigSet(TypedDict):
    host: str
    port: int
    username: str
    password: str
    root_topic: str
    channel: str
    userid: int
    key: str


class MQTTConfig:
    def __init__(self):
        self.defaults()
        self.load_config()
        self.load_env()

        # Replace the default shortened key with the full key
        if self.config["key"] == "AQ==":
            self.config["key"] = "1PG7OiApB1nwvP+rz05pAQ=="

    def defaults(self):
        self.config: ConfigSet = {
            "host": "mqtt.meshtastic.org",
            "port": 1883,
            "username": "meshdev",
            "password": "large4cats",
            "root_topic": "msh/US",
            "channel": "LongFast",
            "userid": 452664778,
            "key": "AQ==",
        }

    def load_config(self):
        config = ConfigParser()
        with suppress(FileNotFoundError, NoSectionError):
            config.read("mqtt.conf")
            for key in self.config:
                value = config.get("mqtt", key)
                if isinstance(self.config[key], int):
                    value = int(value)
                if value:
                    self.config[key] = value

    def load_env(self):
        for key in self.config:
            value = os.getenv(f"MQTT_{key.upper()}")
            if value:
                self.config[key] = value

    @property
    def userid(self) -> str:
        return "!%08x" % self.config["userid"]

    @property
    def publish_topic(self) -> str:
        return f"{self.config['root_topic']}/2/e/{self.config['channel']}/{self.userid}"

    @property
    def receive_topic(self) -> str:
        return f"{self.config['root_topic']}/2/e/{self.config['channel']}/#"

    @property
    def key(self) -> bytes:
        return base64.b64decode(self.config["key"].encode("ascii"))

    @property
    def encoded_channel(self) -> int:
        key = self.config["key"].replace("-", "+").replace("_", "/")
        key_bytes = base64.b64decode(key.encode("utf-8"))
        h_key = xor_checksum(key_bytes)
        h_name = xor_checksum(self.config["channel"].encode("utf-8"))
        return h_name ^ h_key

    @property
    def aiomqtt_config(self) -> Dict[str, str | int]:
        return {
            "hostname": self.config["host"],
            "port": self.config["port"],
            "username": self.config["username"],
            "password": self.config["password"],
        }
