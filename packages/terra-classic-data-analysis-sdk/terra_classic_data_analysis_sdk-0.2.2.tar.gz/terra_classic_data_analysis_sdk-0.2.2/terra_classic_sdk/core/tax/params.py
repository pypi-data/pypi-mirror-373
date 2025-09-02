from __future__ import annotations

import attr
from terra_classic_sdk.core import  Coin
from terra_classic_sdk.util.json import JSONSerializable

@attr.s
class Params(JSONSerializable):
    gas_prices:[Coin] = attr.ib()
    burn_tax_rate: str = attr.ib()

    @classmethod
    def from_data(cls, data: dict) -> Params:
        return cls(
            gas_prices=[Coin.from_data(x) for x in data["gas_prices"]] if data["gas_prices"] else [],
            burn_tax_rate=data["burn_tax_rate"]
        )


    def to_data(self) -> dict:
        return {
            "gas_prices": [x.to_data() for x in self.gas_prices] if self.gas_prices else [],
            "burn_tax_rate": self.burn_tax_rate
        }



