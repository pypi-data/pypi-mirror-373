"""Distribution module governance proposal types."""

from __future__ import annotations

import attr
from betterproto.lib.google.protobuf import Any as Any_pb
from terra_proto.cosmos.distribution.v1beta1 import (
    MsgUpdateParams as MsgUpdateParams_pb
)

from terra_classic_sdk.core import AccAddress, Coins
from terra_classic_sdk.util.json import JSONSerializable
from .params import Params

__all__ = ["MsgUpdateParams"]


@attr.s
class MsgUpdateParams(JSONSerializable):
    """Proposal for tax params updating.  user defind module: tax

    Args:
        authority: the address that controls the module
        params: defines the x/staking parameters to update
    """

    type_amino = "tax/MsgUpdateParams"
    """"""
    type_url = "/terra.tax.v1beta1.MsgUpdateParams"
    """"""
    prototype = MsgUpdateParams_pb
    """"""
    authority: AccAddress = attr.ib()
    """
    authority is the address that controls the module (defaults to x/gov unless
    overwritten).
    """
    params: Params = attr.ib()
    """
    params defines the x/distribution parameters to update. NOTE: All
    parameters must be supplied.
    """


    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "authority":self.authority,
                "params": self.params.to_data(),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgUpdateParams_pb:
        return cls(
            authority=data["authority"],
            params=Params.from_data(data["params"]),
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "authority":self.authority,
            "params": self.params.to_data(),
        }

    # def to_proto(self) -> MsgUpdateParams_pb:
    #     return MsgUpdateParams_pb(
    #         authority=self.authority,
    #         params=self.params.to_proto(),
    #     )
    #
    # @classmethod
    # def from_proto(cls, proto: MsgUpdateParams_pb) -> MsgUpdateParams_pb:
    #     return cls(
    #         authority=proto.authority,
    #         params=Params.from_proto(proto.params),
    #     )

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))