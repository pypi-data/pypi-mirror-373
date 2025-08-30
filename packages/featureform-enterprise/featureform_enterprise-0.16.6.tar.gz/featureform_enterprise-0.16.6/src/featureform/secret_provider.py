from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, TypeVar, Union


class SecretType(str, Enum):
    ENVIRONMENT = "environment"
    STATIC = "static"
    VAULT = "vault"


S = TypeVar("S", bound="Secret")


class SecretProvider(Generic[S], ABC):
    @abstractmethod
    def secret(self, key: str, **kwargs) -> S:
        """Create a secret retriever for delayed access."""
        pass


@dataclass(frozen=True)
class EnvironmentSecretProvider(SecretProvider["EnvironmentSecret"]):
    """Creates references to environment variable secrets."""

    def secret(self, key: str, **kwargs) -> EnvironmentSecret:
        """Create an environment variable secret reference."""
        return EnvironmentSecret(key)


@dataclass(frozen=True)
class VaultSecretProvider(SecretProvider["VaultSecret"]):
    """Creates references to Vault secrets."""

    default_path: str
    vault_provider_name: str

    def secret(self, key: str, **kwargs) -> VaultSecret:
        """
        Create a Vault secret reference.

        Args:
            key: Secret key
            **kwargs: Optional parameters including:
                path: Optional override for default_path
        """
        path = kwargs.get("path", self.default_path)
        return VaultSecret(key, path, self.vault_provider_name)


class Secret(ABC):
    """Abstract base class for secret values with delayed retrieval."""

    @abstractmethod
    def get(self) -> Any:
        """Retrieve the secret value."""
        pass

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Serialize the secret configuration."""
        pass

    @classmethod
    def deserialize(cls, data: Union[Dict[str, Any] | Any]) -> Secret:
        """
        Deserialize a secret from a dictionary configuration.

        Args:
            data: Dictionary containing serialized secret data

        Returns:
            Appropriate Secret implementation

        Raises:
            ValueError: If the secret type is unknown
        """
        # Handle static values (backwards compatibility)
        if "type" not in data:
            return StaticSecret(data)

        secret_map = {
            SecretType.ENVIRONMENT.name: EnvironmentSecret,
            SecretType.STATIC.name: StaticSecret,
            SecretType.VAULT.name: VaultSecret,
        }

        secret_type = data["type"]
        if secret_type.upper() not in secret_map:
            raise ValueError(f"Unknown secret type: {secret_type}")

        return secret_map[secret_type].deserialize(data)


@dataclass(frozen=True)
class StaticSecret(Secret):
    """Secret containing a static value."""

    value: Any

    def get(self) -> Any:
        return self.value

    def serialize(self) -> str:
        return self.value

    @classmethod
    def deserialize(cls, data: Dict[str, Any] | str) -> StaticSecret:
        if not isinstance(data, Dict):
            return cls(data) # Backwards compatibility
        return cls(data.get("value", data))


@dataclass(frozen=True)
class EnvironmentSecret(Secret):
    """Secret that retrieves its value from environment variables."""

    key: str

    def get(self) -> str | None:
        return os.getenv(self.key)

    def serialize(self) -> Dict[str, str]:
        return {"type": SecretType.ENVIRONMENT.name, "key": self.key}

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> EnvironmentSecret:
        if "key" not in data:
            raise ValueError("EnvironmentSecret deserialization failed: 'key' is missing.")
        return cls(data["key"])


@dataclass(frozen=True)
class VaultSecret(Secret):
    """Secret that retrieves its value from Vault."""

    key: str
    path: str
    _vault_provider_name: str

    def get(self) -> str | None:
        raise NotImplementedError("VaultSecret retrieval not implemented")

    def serialize(self) -> Dict[str, str]:
        return {
            "type": SecretType.VAULT.name,
            "key": self.key,
            "path": self.path,
            "vault_provider_name": self._vault_provider_name,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> VaultSecret:
        for field in ["key", "path", "vault_provider_name"]:
            if field not in data:
                raise ValueError(f"VaultSecret deserialization failed: '{field}' is missing.")

        return cls(
            data["key"],
            data["path"],
            data["vault_provider_name"],
        )
