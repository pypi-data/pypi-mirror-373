from __future__ import annotations

from typing import List, Optional

import attr
from terra_proto.cosmos.auth.v1beta1 import ModuleAccount as ModuleAccount_pb

from terra_classic_sdk.core.auth.data.base_account import BaseAccount
from terra_classic_sdk.util.json import JSONSerializable

__all__ = ["ModuleAccount"]

@attr.s
class ModuleAccount(JSONSerializable):
    """
    Stores information about a module account.
    """

    type_amino = "core/ModuleAccount"
    """Amino type identifier."""
    type_url = "/cosmos.auth.v1beta1.ModuleAccount"
    """URL-based type identifier."""

    base_account: BaseAccount = attr.ib()
    """Base account details associated with the module account."""
    name: str = attr.ib()
    """Name of the module account."""
    permissions: List[str] = attr.ib(factory=list)
    """List of permissions assigned to the module account."""

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "base_account": self.base_account.to_amino(),
                "name": self.name,
                "permissions": self.permissions,
            },
        }

    @classmethod
    def from_amino(cls, amino: dict) -> ModuleAccount:
        value = amino["value"]
        return cls(
            base_account=BaseAccount.from_amino(value["base_account"]),
            name=value["name"],
            permissions=value.get("permissions", []),
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "base_account": self.base_account.to_data(),
            "name": self.name,
            "permissions": self.permissions,
        }

    @classmethod
    def from_data(cls, data: dict) -> ModuleAccount:
        return cls(
            base_account=BaseAccount.from_data(data["base_account"]),
            name=data["name"],
            permissions=data.get("permissions", []),
        )

    def to_proto(self) -> ModuleAccount_pb:
        proto = ModuleAccount_pb()
        proto.base_account = self.base_account.to_proto()
        proto.name = self.name
        proto.permissions.extend(self.permissions)
        return proto

    @classmethod
    def from_proto(cls, proto: ModuleAccount_pb) -> ModuleAccount:
        return cls(
            base_account=BaseAccount.from_proto(proto.base_account),
            name=proto.name,
            permissions=list(proto.permissions),
        )
