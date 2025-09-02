from __future__ import annotations

import attr
from terra_proto.cosmos.distribution.v1beta1 import Params as Params_pb
from terra_classic_sdk.util.json import JSONSerializable
from terra_classic_sdk.core import Dec

@attr.s
class Params(JSONSerializable):
    community_tax: Dec = attr.ib(converter=Dec)
    base_proposer_reward: Dec = attr.ib(converter=Dec)
    bonus_proposer_reward: Dec = attr.ib(converter=Dec)
    withdraw_addr_enabled: bool = attr.ib()

    @classmethod
    def from_data(cls, data: dict) -> Params:
        return cls(
            community_tax=data["community_tax"],
            base_proposer_reward=data["base_proposer_reward"],
            bonus_proposer_reward=data["bonus_proposer_reward"],
            withdraw_addr_enabled=data["withdraw_addr_enabled"]
        )

    def to_data(self) -> dict:
        return {
            "community_tax": str(self.community_tax),
            "base_proposer_reward": str(self.base_proposer_reward),
            "bonus_proposer_reward": str(self.bonus_proposer_reward),
            "withdraw_addr_enabled": self.withdraw_addr_enabled
        }

    def to_proto(self) -> Params_pb:
        return Params_pb(
            community_tax=str(self.community_tax),
            base_proposer_reward=str(self.base_proposer_reward),
            bonus_proposer_reward=str(self.bonus_proposer_reward),
            withdraw_addr_enabled=self.withdraw_addr_enabled
        )

    @classmethod
    def from_proto(cls, proto: Params_pb) -> Params:
        return cls(
            community_tax=proto.community_tax,
            base_proposer_reward=proto.base_proposer_reward,
            bonus_proposer_reward=proto.bonus_proposer_reward,
            withdraw_addr_enabled=proto.withdraw_addr_enabled
        )
