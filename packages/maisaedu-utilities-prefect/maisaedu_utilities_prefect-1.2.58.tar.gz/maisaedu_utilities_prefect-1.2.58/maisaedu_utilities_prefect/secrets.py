from __future__ import annotations

import json
import os
import psycopg2

from dataclasses import dataclass
from abc import abstractmethod, ABC
from prefect import task
from typing import Optional

from .constants.env import PROD, DEV, LOCAL
from maisaedu_utilities_prefect.dw import get_dsn
from maisaedu_utilities_prefect.utils import read_file, write_file, build_prefect_logger


def get_secret(secret_name: str) -> str:
    with psycopg2.connect(get_dsn()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select meta.get_secret(%s)", [secret_name])
            (secret,) = cursor.fetchone()
            if secret is None:
                raise Exception("Secret does not exist or is not accessible", secret)
            else:
                return secret


def upload_secret(secret_name: str, content: str):
    with psycopg2.connect(get_dsn()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select meta.put_secret(%s, %s)", [secret_name, content])
            cursor.fetchall()


@task
def download_secret(secret_name: str, output: Optional[str] = None):
    secret = get_secret(secret_name)

    if output is not None:
        os.makedirs("/".join(output.split("/")[:-1]), exist_ok=True)
        with open(output, "w") as output_file:
            output_file.write(secret)

    return secret


class Secret(ABC):
    @classmethod
    @abstractmethod
    def parse_self(cls, definition: str) -> Optional[Secret]:
        pass

    @abstractmethod
    def load(self) -> bytes:
        pass

    @abstractmethod
    def store(self, contents: memoryview):
        pass

    @classmethod
    def parse(cls, definition: str) -> Secret:
        for subclass in cls.__subclasses__():
            parsed = subclass.parse_self(definition)
            if parsed is not None:
                return parsed

        raise Exception(f"Bad secret definition: {definition}")


@dataclass
class FileSecret(Secret):
    file_path: str

    @classmethod
    def parse_self(cls, definition: str) -> Optional[Secret]:
        if definition.startswith("file:"):
            return cls(definition.lstrip("file:"))

    def load(self) -> bytes:
        return read_file(self.file_path)

    def store(self, contents: memoryview):
        if os.path.exists(self.file_path):
            build_prefect_logger().warn(f"File already exists {self.file_path} and will be overrided")

        write_file(self.file_path, contents)


@dataclass
class EnvSecret(Secret):
    env_var: str

    @classmethod
    def parse_self(cls, definition: str) -> Optional[Secret]:
        if definition.startswith("env:"):
            return cls(definition.lstrip("env:"))

    def load(self) -> bytes:
        return os.environ[self.env_var].encode("utf8")

    def store(self, contents: memoryview):
        if self.env_var in os.environ:
            build_prefect_logger().warn(
                f"Environment variable {self.env_var} already set"
            )
            return

        os.environ[self.env_var] = bytes(contents).decode("utf8")


def task_setup_secrets(secrets_path: str = "secrets.json", **kwargs):
    fallback_path = "secrets.json"
    try:
        with open(secrets_path) as secrets_file:
            secrets = json.load(secrets_file)
    except Exception as e:
        with open(fallback_path) as secrets_file:
            secrets = json.load(secrets_file)

    with psycopg2.connect(get_dsn()) as connection, connection.cursor() as cursor:
        for secret_name, definition in secrets.items():
            cursor.execute("select meta.get_secret(%s)", [secret_name])
            (content,) = cursor.fetchone()
            if content is None:
                print("Secret does not exist or is not accessible", secret_name)
            else:
                Secret.parse(definition).store(content)


@task()
async def async_setup_secrets(secrets_path: str = "secrets.json"):
    task_setup_secrets(secrets_path)

    return True


@task()
def setup_secrets(secrets_path: str = "secrets.json"):
    task_setup_secrets(secrets_path)

    return True


def refresh_secrets(secrets_path: str = "secrets.json"):
    with open(secrets_path) as secrets_file:
        secrets = json.load(secrets_file)

        with psycopg2.connect(get_dsn()) as connection, connection.cursor() as cursor:
            for secret_name, definition in secrets.items():
                content = Secret.parse(definition).load()
                cursor.execute("select meta.put_secret(%s, %s)", [secret_name, content])
                cursor.fetchall()


def get_cipher_key(env=PROD):
    if env == PROD:
        path = "data/prod-cipher-key.text"
    elif env == DEV or env == LOCAL:
        path = "data/dev-cipher-key.text"

    try:
        with open(path) as f:
            r = f.read()
            return r
    except Exception as e:
        return None
