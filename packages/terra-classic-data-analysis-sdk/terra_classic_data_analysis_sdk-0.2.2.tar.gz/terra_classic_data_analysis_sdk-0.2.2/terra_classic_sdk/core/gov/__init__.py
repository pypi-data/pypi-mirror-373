from terra_proto.cosmos.gov.v1beta1 import ProposalStatus

from .data import ProposalMsg, Proposal, VoteOption, WeightedVoteOption
from .msgs import MsgDeposit, MsgSubmitProposal, MsgVote,MsgVote_v1beta1,MsgDeposit_v1beta1
from .proposals import ExecLegacyContentProposal

__all__ = [
    "ProposalMsg",
    "MsgDeposit",
    "MsgDeposit_v1beta1",
    "MsgSubmitProposal",
    "MsgVote",
    "MsgVote_v1beta1",
    "Proposal",
    "ExecLegacyContentProposal",
    "ProposalStatus",
    "VoteOption",
    "WeightedVoteOption",
]
