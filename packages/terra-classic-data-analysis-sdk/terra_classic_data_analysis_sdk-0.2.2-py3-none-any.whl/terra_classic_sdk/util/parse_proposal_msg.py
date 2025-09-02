from typing import Union

from terra_classic_sdk.core.distribution.proposals import MsgCommunityPoolSpend,MsgUpdateParams as MsgUpdateParams_distribution
from terra_classic_sdk.core.staking.proposals import MsgUpdateParams as MsgUpdateParams_staking
from terra_classic_sdk.core.tax.proposals import MsgUpdateParams as MsgUpdateParams_tax
from terra_classic_sdk.core.slashing.proposals import MsgUpdateParams as MsgUpdateParams_slashing
from terra_classic_sdk.core.gov.proposals import ExecLegacyContentProposal
from terra_classic_sdk.core.params.proposals import ParameterChangeProposal
from terra_classic_sdk.core.ibc.proposals import ClientUpdateProposal
from terra_classic_sdk.core.wasm.proposals import MigrateContractProposal
from terra_classic_sdk.core.treasury.proposals import AddBurnTaxExemptionAddressProposal

from terra_classic_sdk.core.upgrade import (
    CancelSoftwareUpgradeProposal,
    SoftwareUpgradeProposal,
)
from terra_classic_sdk.core.wasm.proposals import UpdateAdminProposal

from terra_proto.cosmos.distribution.v1beta1 import MsgCommunityPoolSpend as MsgCommunityPoolSpend_pb
from terra_proto.cosmos.gov.v1beta1 import TextProposal as TextProposal_pb
from terra_proto.cosmos.params.v1beta1 import ParameterChangeProposal as ParameterChangeProposal_pb
from terra_proto.cosmos.upgrade.v1beta1 import (
    CancelSoftwareUpgradeProposal as CancelSoftwareUpgradeProposal_pb,
    SoftwareUpgradeProposal as SoftwareUpgradeProposal_pb
)
from terra_proto.ibc.core.client.v1 import ClientUpdateProposal as ClientUpdateProposal_pb

from .base import create_demux, create_demux_proto

ProposalMsg = Union[
    ExecLegacyContentProposal,
    MsgCommunityPoolSpend,
    MsgUpdateParams_distribution,
    MsgUpdateParams_staking,
    MsgUpdateParams_tax,
    MsgUpdateParams_slashing,
    ParameterChangeProposal,
    SoftwareUpgradeProposal,
    CancelSoftwareUpgradeProposal,
    ClientUpdateProposal,
    UpdateAdminProposal,
    MigrateContractProposal,
    AddBurnTaxExemptionAddressProposal,
]

parse_proposal_msg = create_demux(
    [
        MsgCommunityPoolSpend,
        ExecLegacyContentProposal,
        MsgUpdateParams_distribution,
        MsgUpdateParams_staking,
        MsgUpdateParams_tax,
        MsgUpdateParams_slashing,
        ParameterChangeProposal,
        SoftwareUpgradeProposal,
        CancelSoftwareUpgradeProposal,
        ClientUpdateProposal,
        UpdateAdminProposal,
        MigrateContractProposal,
        AddBurnTaxExemptionAddressProposal,
    ]
)

parse_proposal_msg_proto = create_demux_proto(
    [
        MsgCommunityPoolSpend,
        ExecLegacyContentProposal,
        MsgUpdateParams_distribution,
        MsgUpdateParams_staking,
        MsgUpdateParams_slashing,
        ParameterChangeProposal,
        SoftwareUpgradeProposal,
        CancelSoftwareUpgradeProposal,
        ClientUpdateProposal,
        UpdateAdminProposal,
        MigrateContractProposal,
        AddBurnTaxExemptionAddressProposal
    ]
)
"""
parse_content_proto = create_demux_proto(
    [
        [MsgCommunityPoolSpend.type_url, MsgCommunityPoolSpend_pb],
        [TextProposal.type_url, TextProposal_pb],
        [ParameterChangeProposal.type_url, ParameterChangeProposal_pb],
        [SoftwareUpgradeProposal.type_url, SoftwareUpgradeProposal_pb],
        [CancelSoftwareUpgradeProposal.type_url, CancelSoftwareUpgradeProposal_pb],
        [ClientUpdateProposal.type_url, ClientUpdateProposal_pb]
    ]
)
"""