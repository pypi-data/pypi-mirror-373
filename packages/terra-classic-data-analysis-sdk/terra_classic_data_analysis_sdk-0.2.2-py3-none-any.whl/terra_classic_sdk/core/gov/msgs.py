"""Gov module message types."""

from __future__ import annotations

import json
from typing import Union

import attr
from terra_proto.cosmos.gov.v1beta1 import MsgDeposit as MsgDeposit_pb
from terra_proto.cosmos.gov.v1beta1 import MsgSubmitProposal as MsgSubmitProposal_pb
from terra_proto.cosmos.gov.v1beta1 import MsgVote as MsgVote_pb

from terra_classic_sdk.core import AccAddress, Coins
from terra_classic_sdk.core.msg import Msg

from .data import ProposalMsg, VoteOption

__all__ = ["MsgSubmitProposal", "MsgDeposit", "MsgVote"]

from ...util.converter import try_json_loads


@attr.s
class MsgSubmitProposal(Msg):
    """Submit the attached proposal with an initial deposit.

    Args:
        content (Content): type of proposal
        initial_deposit (Coins): initial deposit for proposal made by proposer
        proposer (AccAddress): proposal submitter
    """

    type_amino = "gov/MsgSubmitProposal"
    """"""
    type_url = "/cosmos.gov.v1.MsgSubmitProposal"
    """"""
    action = "submit_proposal"
    """"""
    prototype = MsgSubmitProposal_pb
    """"""

    initial_deposit: Coins = attr.ib(converter=Coins)
    proposer: AccAddress = attr.ib()
    messages:list=attr.ib()
    title:str=attr.ib()
    summary:str=attr.ib()
    metadata: Union[dict, str]=attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "initial_deposit": self.initial_deposit.to_amino(),
                "proposer": self.proposer,
                "messages": self.messages,
                "title": self.title,
                "summary": self.summary,
                "metadata": self.metadata,
            },
        }

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "initial_deposit": self.initial_deposit.to_data(),
            "proposer": self.proposer,
            "messages": self.messages,
            "title": self.title,
            "summary": self.summary,
            "metadata": self.metadata,
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgSubmitProposal:
        return cls(
            initial_deposit=Coins.from_data(data["initial_deposit"]),
            proposer=data["proposer"],
            messages=data["messages"],
            title=data["title"],
            summary=data["summary"],
            metadata=try_json_loads(data["metadata"])
        )

    def to_proto(self) -> MsgSubmitProposal_pb:
        return MsgSubmitProposal_pb(
            initial_deposit=self.initial_deposit.to_proto(),
            proposer=self.proposer
        )

    @classmethod
    def from_proto(cls, proto: MsgSubmitProposal_pb) -> MsgSubmitProposal:
        return cls(
            initial_deposit=Coins.from_proto(proto["initial_deposit"]),
            proposer=proto["proposer"],
        )

@attr.s
class MsgSubmitProposal_v1beta1(Msg):
    """Submit the attached proposal with an initial deposit.

    Args:
        content (Content): type of proposal
        initial_deposit (Coins): initial deposit for proposal made by proposer
        proposer (AccAddress): proposal submitter
    """

    type_amino = "gov/MsgSubmitProposal"
    """"""
    type_url = "/cosmos.gov.v1beta1.MsgSubmitProposal"
    """"""
    action = "submit_proposal"
    """"""
    prototype = MsgSubmitProposal_pb
    """"""

    content: dict = attr.ib()
    initial_deposit: Coins = attr.ib(converter=Coins)
    proposer: AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "content": self.content,
                "initial_deposit": self.initial_deposit.to_amino(),
                "proposer": self.proposer,
            },
        }

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "content": self.content,
            "initial_deposit": self.initial_deposit.to_data(),
            "proposer": self.proposer
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgSubmitProposal:
        return cls(
            content=data['content'],
            initial_deposit=Coins.from_data(data["initial_deposit"]),
            proposer=data["proposer"],
        )

    def to_proto(self) -> MsgSubmitProposal_pb:
        return MsgSubmitProposal_pb(
            content=self.content,
            initial_deposit=self.initial_deposit.to_proto(),
            proposer=self.proposer,
        )

    @classmethod
    def from_proto(cls, proto: MsgSubmitProposal_pb) -> MsgSubmitProposal:
        return cls(
            content=proto["content"],
            initial_deposit=Coins.from_proto(proto["initial_deposit"]),
            proposer=proto["proposer"],
        )

@attr.s
class MsgDeposit(Msg):
    """Deposit funds for an active deposit-stage proposal.

    Args:
        proposal_id (int): proposal number to deposit for
        depositor (AccAddress): account making deposit
        amount (Coins): amount to deposit
    """

    type_amino = "gov/MsgDeposit"
    """"""
    type_url = "/cosmos.gov.v1.MsgDeposit"
    """"""
    action = "deposit"
    """"""
    prototype = MsgDeposit_pb
    """"""

    proposal_id: int = attr.ib(converter=int)
    depositor: AccAddress = attr.ib()
    amount: Coins = attr.ib(converter=Coins)

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "proposal_id": str(self.proposal_id),
                "depositor": self.depositor,
                "amount": self.amount.to_amino(),
            },
        }

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "proposal_id": str(self.proposal_id),
            "depositor": self.depositor,
            "amount": self.amount.to_data(),
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgDeposit:
        return cls(
            proposal_id=data["proposal_id"],
            depositor=data["depositor"],
            amount=Coins.from_data(data["amount"]),
        )

    def to_proto(self) -> MsgDeposit_pb:
        return MsgDeposit_pb(
            proposal_id=self.proposal_id,
            depositor=self.depositor,
            amount=self.amount.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgDeposit_pb) -> MsgDeposit:
        return cls(
            proposal_id=proto["proposal_id"],
            depositor=proto["depositor"],
            amount=Coins.from_proto(proto["amount"]),
        )

@attr.s
class MsgDeposit_v1beta1(Msg):
    """Deposit funds for an active deposit-stage proposal.

    Args:
        proposal_id (int): proposal number to deposit for
        depositor (AccAddress): account making deposit
        amount (Coins): amount to deposit
    """

    type_amino = "gov/MsgDeposit"
    """"""
    type_url = "/cosmos.gov.v1beta1.MsgDeposit"
    """"""
    action = "deposit"
    """"""
    prototype = MsgDeposit_pb
    """"""

    proposal_id: int = attr.ib(converter=int)
    depositor: AccAddress = attr.ib()
    amount: Coins = attr.ib(converter=Coins)

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "proposal_id": str(self.proposal_id),
                "depositor": self.depositor,
                "amount": self.amount.to_amino(),
            },
        }

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "proposal_id": str(self.proposal_id),
            "depositor": self.depositor,
            "amount": self.amount.to_data(),
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgDeposit:
        return cls(
            proposal_id=data["proposal_id"],
            depositor=data["depositor"],
            amount=Coins.from_data(data["amount"]),
        )


    def to_proto(self) -> MsgDeposit_pb:
        return MsgDeposit_pb(
            proposal_id=self.proposal_id,
            depositor=self.depositor,
            amount=self.amount.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgDeposit_pb) -> MsgDeposit:
        return cls(
            proposal_id=proto["proposal_id"],
            depositor=proto["depositor"],
            amount=Coins.from_proto(proto["amount"]),
        )

@attr.s
class MsgVote(Msg):
    """Vote for an active voting-stage proposal.

    Args:
        proposal_id (int): proposal to vote for
        voter (AccAddress): account casting vote
        option (VoteOption): vote option (must be one of: :data:`MsgVote.ABSTAIN`, :data:`MsgVote.YES`, :data:`MsgVote.NO`, or :data:`MsgVote.NO_WITH_VETO`),
    """

    type_amino = "gov/MsgVote"
    """"""
    type_url = "/cosmos.gov.v1.MsgVote"
    """"""
    action = "vote"
    """"""
    prototype = MsgVote_pb
    """"""

    EMPTY = "Empty"
    """Encodes an empty vote option."""

    YES = "Yes"
    """"""
    ABSTAIN = "Abstain"
    """"""
    NO = "No"
    """"""
    NO_WITH_VETO = "NoWithVeto"
    """"""

    proposal_id: int = attr.ib(converter=int)
    voter: AccAddress = attr.ib()
    option: VoteOption = attr.ib()

    """
    @option.validator
    def _check_option(self, attribute, value):
        possible_options = [
            self.EMPTY,
            self.YES,
            self.ABSTAIN,
            self.NO,
            self.NO_WITH_VETO,
        ]
        if value not in possible_options:
            raise TypeError(
                f"incorrect value for option: {value}, must be one of: {possible_options}"
            )
    """

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "proposal_id": str(self.proposal_id),
                "voter": self.voter,
                "option": self.option.name,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgVote:
        return cls(
            proposal_id=data["proposal_id"],
            voter=data["voter"],
            option=data["option"],
        )

    def to_proto(self) -> MsgVote_pb:
        return MsgVote_pb(
            proposal_id=self.proposal_id, 
            voter=self.voter, 
            option=self.option
        )

    @classmethod
    def from_proto(cls, proto: MsgVote_pb) -> MsgVote:
        return cls(
            proposal_id=proto.proposal_id,
            voter=proto.voter,
            option=proto.option
        )

@attr.s
class MsgVote_v1beta1(Msg):
    """Vote for an active voting-stage proposal.

    Args:
        proposal_id (int): proposal to vote for
        voter (AccAddress): account casting vote
        option (VoteOption): vote option (must be one of: :data:`MsgVote.ABSTAIN`, :data:`MsgVote.YES`, :data:`MsgVote.NO`, or :data:`MsgVote.NO_WITH_VETO`),
    """

    type_amino = "gov/MsgVote"
    """"""
    type_url = "/cosmos.gov.v1beta1.MsgVote"
    """"""
    action = "vote"
    """"""
    prototype = MsgVote_pb
    """"""

    EMPTY = "Empty"
    """Encodes an empty vote option."""

    YES = "Yes"
    """"""
    ABSTAIN = "Abstain"
    """"""
    NO = "No"
    """"""
    NO_WITH_VETO = "NoWithVeto"
    """"""

    proposal_id: int = attr.ib(converter=int)
    voter: AccAddress = attr.ib()
    option: VoteOption = attr.ib()

    """
    @option.validator
    def _check_option(self, attribute, value):
        possible_options = [
            self.EMPTY,
            self.YES,
            self.ABSTAIN,
            self.NO,
            self.NO_WITH_VETO,
        ]
        if value not in possible_options:
            raise TypeError(
                f"incorrect value for option: {value}, must be one of: {possible_options}"
            )
    """

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "proposal_id": str(self.proposal_id),
                "voter": self.voter,
                "option": self.option.name,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgVote:
        return cls(
            proposal_id=data["proposal_id"],
            voter=data["voter"],
            option=data["option"],
        )

    def to_proto(self) -> MsgVote_pb:
        return MsgVote_pb(
            proposal_id=self.proposal_id,
            voter=self.voter,
            option=self.option
        )

    @classmethod
    def from_proto(cls, proto: MsgVote_pb) -> MsgVote:
        return cls(
            proposal_id=proto.proposal_id,
            voter=proto.voter,
            option=proto.option
        )