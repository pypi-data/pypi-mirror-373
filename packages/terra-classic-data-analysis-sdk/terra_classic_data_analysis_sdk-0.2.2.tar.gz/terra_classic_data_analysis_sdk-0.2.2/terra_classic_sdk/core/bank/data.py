# terra_classic_sdk/core/bank/data.py
"""
Bank module data objects.
"""

from __future__ import annotations

import attr
from typing import List, Optional
from terra_classic_sdk.util.json import JSONSerializable

@attr.s
class DenomUnit(JSONSerializable):
    """Denomination unit of a token."""

    denom: str = attr.ib()
    exponent: int = attr.ib()
    aliases: List[str] = attr.ib(factory=list)

    def to_data(self) -> dict:
        return {
            "denom": self.denom,
            "exponent": self.exponent,
            "aliases": self.aliases,
        }

    @classmethod
    def from_data(cls, data: dict) -> DenomUnit:
        return cls(
            denom=data["denom"],
            exponent=data["exponent"],
            aliases=data.get("aliases", []),
        )

@attr.s
class Metadata(JSONSerializable):
    """Metadata for a token."""

    description: str = attr.ib()
    denom_units: List[DenomUnit] = attr.ib()
    base: str = attr.ib()
    display: str = attr.ib()
    name: str = attr.ib()
    symbol: str = attr.ib()
    uri: Optional[str] = attr.ib(default=None)
    uri_hash: Optional[str] = attr.ib(default=None)

    def to_data(self) -> dict:
        data = {
            "description": self.description,
            "denom_units": [unit.to_data() for unit in self.denom_units],
            "base": self.base,
            "display": self.display,
            "name": self.name,
            "symbol": self.symbol,
        }
        if self.uri is not None:
            data["uri"] = self.uri
        if self.uri_hash is not None:
            data["uri_hash"] = self.uri_hash
        return data

    @classmethod
    def from_data(cls, data: dict) -> Metadata:
        return cls(
            description=data["description"],
            denom_units=[DenomUnit.from_data(unit) for unit in data["denom_units"]],
            base=data["base"],
            display=data["display"],
            name=data["name"],
            symbol=data["symbol"],
            uri=data.get("uri"),
            uri_hash=data.get("uri_hash"),
        )
