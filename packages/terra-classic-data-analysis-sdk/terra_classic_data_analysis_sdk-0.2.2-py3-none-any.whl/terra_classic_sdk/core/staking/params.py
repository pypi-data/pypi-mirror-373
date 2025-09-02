from __future__ import annotations

import attr
from terra_proto.cosmos.distribution.v1beta1 import Params as Params_pb
from terra_classic_sdk.util.json import JSONSerializable

@attr.s
class Params(JSONSerializable):
    unbonding_time: str = attr.ib()
    max_validators: int = attr.ib(converter=int)
    max_entries: int = attr.ib(converter=int)
    historical_entries: int = attr.ib(converter=int)
    bond_denom:str=attr.ib()
    min_commission_rate:str=attr.ib()


    @classmethod
    def from_data(cls, data: dict) -> Params:
        return cls(
            unbonding_time=data["unbonding_time"],
            max_validators=data["max_validators"],
            max_entries=data["max_entries"],
            historical_entries=data["historical_entries"],
            bond_denom=data["bond_denom"],
            min_commission_rate=data["min_commission_rate"]
        )


    def to_data(self) -> dict:
        return {
            "unbonding_time": self.unbonding_time,
            "max_validators": self.max_validators,
            "max_entries": self.max_entries,
            "historical_entries": self.historical_entries,
            "bond_denom": self.bond_denom,
            "min_commission_rate": self.min_commission_rate
        }


    def to_proto(self) -> Params_pb:
        return Params_pb(
            unbonding_time=self.unbonding_time,
            max_validators=self.max_validators,
            max_entries=self.max_entries,
            historical_entries=self.historical_entries,
            bond_denom=self.bond_denom,
            min_commission_rate=self.min_commission_rate
        )


    @classmethod
    def from_proto(cls, proto: Params_pb) -> Params:
        return cls(
            unbonding_time=proto.unbonding_time,
            max_validators=proto.max_validators,
            max_entries=proto.max_entries,
            historical_entries=proto.historical_entries,
            bond_denom=proto.bond_denom,
            min_commission_rate=proto.min_commission_rate
        )

