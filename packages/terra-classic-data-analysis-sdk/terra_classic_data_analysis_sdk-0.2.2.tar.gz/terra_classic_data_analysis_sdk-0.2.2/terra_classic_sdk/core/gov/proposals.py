"""Gov module governance proposal types."""

from __future__ import annotations

import attr
from betterproto.lib.google.protobuf import Any as Any_pb
from terra_proto.cosmos.gov.v1beta1 import TextProposal as TextProposal_pb

from terra_classic_sdk.core import AccAddress
from terra_classic_sdk.util.json import JSONSerializable

__all__ = ["ExecLegacyContentProposal"]


@attr.s
class ExecLegacyContentProposal(JSONSerializable):
    """Generic proposal type with only title and description that does nothing if
    passed. Primarily used for assessing the community sentiment around the proposal.

    Args:
        title: proposal title
        description: proposal description
    """

    type_amino = "gov/TextProposal"
    """"""
    type_url = "/cosmos.gov.v1.MsgExecLegacyContent"
    """"""
    content:dict=attr.ib()
    authority:AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {"content":self.content,"authority":self.authority},
        }

    @classmethod
    def from_data(cls, data: dict) -> ExecLegacyContentProposal:
        return cls(content=data["content"],authority=data["authority"] if "authority" in data.keys() else "")

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "content":self.content,
            "authority":self.authority
        }

    def to_proto(self) -> TextProposal_pb:
        return TextProposal_pb(title=self.title, description=self.description)

    def pack_any(self) -> Any_pb:
        return Any_pb(type_url=self.type_url, value=bytes(self.to_proto()))

    @classmethod
    def from_proto(cls, proto: TextProposal_pb):
        return cls(
            title=proto.title,
            description=proto.description
        )
