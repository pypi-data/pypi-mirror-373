from __future__ import annotations
import attr
from terra_proto.terra.treasury.v1beta1 import AddBurnTaxExemptionAddressProposal as AddBurnTaxExemptionAddressProposal_pb
from terra_classic_sdk.core import AccAddress
from terra_classic_sdk.util.json import JSONSerializable


@attr.s
class AddBurnTaxExemptionAddressProposal(JSONSerializable):
    """A governance proposal to add an address to the burn tax exemption list."""
    type_amino = "treasury/AddBurnTaxExemptionAddressProposal"
    """"""
    type_url = "/terra.treasury.v1beta1.AddBurnTaxExemptionAddressProposal"
    """"""
    action = "submit_proposal"
    """"""
    prototype = AddBurnTaxExemptionAddressProposal_pb
    """"""

    title: str = attr.ib()
    description: str = attr.ib()
    addresses: AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "addresses": self.addresses,
        }

    @classmethod
    def from_data(cls, data: dict) -> AddBurnTaxExemptionAddressProposal:
        return cls(
            title=data["title"],
            description=data["description"],
            addresses=data["addresses"],
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "title": self.title,
            "description": self.description,
            "addresses": self.addresses,
        }

    @classmethod
    def from_proto(cls, proto: AddBurnTaxExemptionAddressProposal_pb) -> AddBurnTaxExemptionAddressProposal:
        return cls(
            title=proto.title,
            description=proto.description,
            addresses=proto.addresses
        )

    def to_proto(self) -> AddBurnTaxExemptionAddressProposal_pb:
        return AddBurnTaxExemptionAddressProposal_pb(
            title=self.title,
            description=self.description,
            addresses=self.addresses,
        )
