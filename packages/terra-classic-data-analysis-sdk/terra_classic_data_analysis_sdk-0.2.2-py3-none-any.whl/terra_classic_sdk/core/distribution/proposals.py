"""Distribution module governance proposal types."""

from __future__ import annotations

import attr
from betterproto.lib.google.protobuf import Any as Any_pb
from terra_proto.cosmos.distribution.v1beta1 import (
    MsgCommunityPoolSpend as MsgCommunityPoolSpend_pb,
    MsgUpdateParams as MsgUpdateParams_pb
)

from terra_classic_sdk.core import AccAddress, Coins
from terra_classic_sdk.util.json import JSONSerializable
from terra_classic_sdk.core.distribution.params import Params

__all__ = ["MsgCommunityPoolSpend","MsgUpdateParams"]


@attr.s
class MsgCommunityPoolSpend(JSONSerializable):
    """Proposal for allocating funds from the community pool to an address.

    Args:
        title: proposal title
        description: proposal description
        recipient: designated recipient of funds if proposal passes
        amount (Coins): amount to spend from community pool
    """

    type_amino = "distribution/MsgCommunityPoolSpend"
    """"""
    type_url = "/cosmos.distribution.v1beta1.MsgCommunityPoolSpend"
    """"""
    prototype = MsgCommunityPoolSpend_pb
    """"""
    authority: AccAddress = attr.ib()
    recipient: AccAddress = attr.ib()
    amount: Coins = attr.ib(converter=Coins)


    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "title": self.title,
                "description": self.description,
                "recipient": self.recipient,
                "amount": self.amount.to_amino(),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgCommunityPoolSpend:
        return cls(
            authority=data["authority"],
            recipient=data["recipient"],
            amount=Coins.from_data(data["amount"]),
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "authority":self.authority,
            "recipient": self.recipient,
            "amount": self.amount.to_data(),
        }

    def to_proto(self) -> MsgCommunityPoolSpend_pb:
        return MsgCommunityPoolSpend_pb(
            authority=self.authority,
            recipient=self.recipient,
            amount=self.amount.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgCommunityPoolSpend_pb) -> MsgCommunityPoolSpend:
        return cls(
            authority=proto.authority,
            recipient=proto.recipient,
            amount=Coins.from_proto(proto.amount),
        )

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))

@attr.s
class MsgUpdateParams(JSONSerializable):
    """Proposal for allocating funds from the community pool to an address.

    Args:
        authority: the address that controls the module
        params: defines the x/distribution parameters to update
    """

    type_amino = "distribution/MsgUpdateParams"
    """"""
    type_url = "/cosmos.distribution.v1beta1.MsgUpdateParams"
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
    def from_data(cls, data: dict) -> MsgCommunityPoolSpend:
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

    def to_proto(self) -> MsgUpdateParams_pb:
        return MsgCommunityPoolSpend_pb(
            authority=self.authority,
            params=self.params.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgUpdateParams_pb) -> MsgUpdateParams_pb:
        return cls(
            authority=proto.authority,
            params=Params.from_proto(proto.params),
        )

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))