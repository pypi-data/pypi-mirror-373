"Wasm module messages."

from __future__ import annotations

import base64
import json
from cProfile import label
from typing import Optional, Union

import attr
from betterproto.lib.google.protobuf import Any as Any_pb
from terra_proto.cosmwasm.wasm.v1 import MsgClearAdmin as MsgClearAdmin_pb, MsgInstantiateContract2 as MsgInstantiateContract2_pb
from terra_proto.cosmwasm.wasm.v1 import MsgExecuteContract as MsgExecuteContract_pb
from terra_proto.cosmwasm.wasm.v1 import (
    MsgInstantiateContract as MsgInstantiateContract_pb,
)
from terra_proto.cosmwasm.wasm.v1 import MsgMigrateContract as MsgMigrateContract_pb
from terra_proto.cosmwasm.wasm.v1 import MsgStoreCode as MsgStoreCode_pb
from terra_proto.cosmwasm.wasm.v1 import MsgUpdateAdmin as MsgUpdateAdmin_pb

from terra_classic_sdk.core import AccAddress, Coins
from terra_classic_sdk.core.msg import Msg
from terra_classic_sdk.core.wasm.data import AccessConfig, AccessTypeParam
from terra_classic_sdk.util.remove_none import remove_none

__all__ = [
    "MsgStoreCode",
    "MsgStoreCode_vbeta1",
    "MsgInstantiateContract",
    "MsgExecuteContract",
    "MsgExecuteContract_vbeta1",
    "MsgMigrateContract",
    "MsgUpdateAdmin",
    "MsgClearAdmin",
]


def parse_msg(msg: Union[dict,list,str, bytes]) -> dict:
    if type(msg) is dict or type(msg) is list:
        return msg
    elif type(msg) is int:
        return {"code_id":msg}
    return json.loads(msg)


@attr.s
class MsgStoreCode(Msg):
    """Upload a new smart contract WASM binary to the blockchain.

    Args:
        sender: address of sender
        wasm_byte_code: base64-encoded string containing bytecode
        instantiate_permission: access control to apply on contract creation, optional
    """

    type_amino = "wasm/MsgStoreCode"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgStoreCode"
    """"""
    prototype = MsgStoreCode_pb
    """"""

    sender: AccAddress = attr.ib()
    wasm_byte_code: str = attr.ib()
    instantiate_permission: AccessConfig = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "wasm_byte_code": self.wasm_byte_code,
                "instantiate_permission": self.instantiate_permission.to_amino(),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgStoreCode:
        return cls(
            sender=data["sender"],
            wasm_byte_code=data["wasm_byte_code"],
            instantiate_permission=AccessConfig.from_data(
                data["instantiate_permission"]
            ),
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "sender": self.sender,
            "wasm_byte_code": self.wasm_byte_code,
            "instantiate_permission": self.instantiate_permission.to_data() if self.instantiate_permission else None,
        }

    def to_proto(self) -> MsgStoreCode_pb:
        return MsgStoreCode_pb(
            sender=self.sender,
            wasm_byte_code=base64.b64decode(self.wasm_byte_code),
            instantiate_permission=self.instantiate_permission.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgStoreCode_pb) -> MsgStoreCode:
        return cls(
            sender=proto.sender,
            wasm_byte_code=base64.b64encode(proto.wasm_byte_code).decode(),
            instantiate_permission=AccessConfig.from_proto(
                proto.instantiate_permission
            ),
        )

from terra_proto.terra.wasm.v1beta1 import MsgStoreCode as MsgStoreCode_v1beta1_pb

@attr.s
class MsgStoreCode_vbeta1(Msg):
    """Upload a new smart contract WASM binary to the blockchain (v1beta1 version).

    Args:
        sender: address of sender
        wasm_byte_code: base64-encoded string containing bytecode
    """

    type_amino = "wasm/MsgStoreCode"
    type_url = "/terra.wasm.v1beta1.MsgStoreCode"
    prototype = MsgStoreCode_v1beta1_pb

    sender: AccAddress = attr.ib()
    wasm_byte_code: str = attr.ib()

    @classmethod
    def from_data(cls, data: dict) -> "MsgStoreCode_vbeta1":
        wasm_byte_code = data["wasm_byte_code"]
        # # 确保 wasm_byte_code 是字符串类型（base64 编码）
        # if isinstance(wasm_byte_code, bytes):
        #     wasm_byte_code = base64.b64encode(wasm_byte_code).decode()
        return cls(
            sender=data["sender"],
            wasm_byte_code=wasm_byte_code,
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "sender": self.sender,
            "wasm_byte_code": self.wasm_byte_code,
        }

    def to_proto(self) -> MsgStoreCode_v1beta1_pb:
        return MsgStoreCode_v1beta1_pb(
            sender=self.sender,
            wasm_byte_code=base64.b64decode(self.wasm_byte_code),
        )

    @classmethod
    def from_proto(cls, proto: MsgStoreCode_v1beta1_pb) -> "MsgStoreCode_vbeta1":
        return cls(
            sender=proto.sender,
            wasm_byte_code=base64.b64encode(proto.wasm_byte_code).decode(),
        )


@attr.s
class MsgInstantiateContract(Msg):
    """Creates a new instance of a smart contract from existing code on the blockchain.

    Args:
        sender: address of sender
        admin: address of contract admin
        code_id (int): code ID to use for instantiation
        label (str): label for the contract.
        msg (dict|str): InitMsg to initialize contract
        funds (Coins): initial amount of coins to be sent to contract
    """

    type_amino = "wasm/MsgInstantiateContract"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgInstantiateContract"
    """"""
    prototype = MsgInstantiateContract_pb
    """"""

    sender: AccAddress = attr.ib()
    admin: Optional[AccAddress] = attr.ib()
    code_id: int = attr.ib(converter=int)
    label: str = attr.ib(converter=str)
    msg: Union[dict, str] = attr.ib()
    funds: Coins = attr.ib(converter=Coins, factory=Coins)

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "admin": self.admin,
                "code_id": str(self.code_id),
                "label": self.label,
                "msg": remove_none(self.msg),
                "funds": self.funds.to_amino(),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgInstantiateContract:
        return cls(
            sender=data.get("sender"),
            admin=data.get("admin"),
            code_id=data["code_id"],
            label=data["label"],
            msg=parse_msg(data["msg"]),
            funds=Coins.from_data(data["funds"]),
        )

    def to_proto(self) -> MsgInstantiateContract_pb:
        return MsgInstantiateContract_pb(
            sender=self.sender,
            admin=self.admin,
            code_id=self.code_id,
            label=self.label,
            msg=bytes(json.dumps(self.msg), "utf-8"),
            funds=self.funds.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgInstantiateContract_pb) -> MsgInstantiateContract:
        return cls(
            sender=proto.sender,
            admin=proto.admin,
            code_id=proto.code_id,
            label=proto.label,
            msg=parse_msg(proto.msg),
            funds=Coins.from_proto(proto.funds),
        )

@attr.s
class MsgInstantiateContract2(Msg):
    """
    Creates a new instance of a smart contract from existing code on the blockchain with predictable address.

    Args:
        sender: address of sender
        admin: address of contract admin (optional)
        code_id (int): code ID to use for instantiation
        label (str): label for the contract.
        msg (dict|str): InitMsg to initialize contract
        funds (Coins): initial amount of coins to be sent to contract
        salt (bytes): arbitrary value used in computing predictable address
        fix_msg (bool): whether to include msg in address derivation
    """

    type_amino = "wasm/MsgInstantiateContract2"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgInstantiateContract2"
    """"""
    prototype = MsgInstantiateContract2_pb
    """"""
    salt: bytes = attr.ib()
    sender: AccAddress = attr.ib()
    admin: Optional[AccAddress] = attr.ib()
    code_id: int = attr.ib(converter=int)
    label: str = attr.ib(converter=str)
    msg: Union[dict, str] = attr.ib()
    funds: Coins = attr.ib(converter=Coins, factory=Coins)
    fix_msg: bool = attr.ib(default=False)

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "admin": self.admin,
                "code_id": str(self.code_id),
                "label": self.label,
                "msg": remove_none(self.msg),
                "funds": self.funds.to_amino(),
                "salt": base64.b64encode(self.salt).decode() if self.salt else "",
                "fix_msg": self.fix_msg,
            },
        }
    def to_json(self) -> str:
        data = self.to_data()
        # 对 salt 字段做 base64 编码（如果存在且是 bytes）
        if "salt" in data and isinstance(data["salt"], bytes):
            data["salt"] = base64.b64encode(data["salt"]).decode("utf-8")
        return json.dumps(data)

    @classmethod
    def from_data(cls, data: dict) -> "MsgInstantiateContract2":
        return cls(
            sender=data.get("sender"),
            admin=data.get("admin"),
            code_id=data["code_id"],
            label=data["label"],
            msg=parse_msg(data["msg"]),
            funds=Coins.from_data(data.get("funds", [])),
            salt=base64.b64decode(data["salt"]) if data.get("salt") else b"",
            fix_msg=data.get("fix_msg", False),
        )

    def to_proto(self) -> MsgInstantiateContract2_pb:
        return MsgInstantiateContract2_pb(
            sender=self.sender,
            admin=self.admin,
            code_id=self.code_id,
            label=self.label,
            msg=bytes(json.dumps(self.msg), "utf-8"),
            funds=[coin.to_proto() for coin in self.funds],
            salt=self.salt,
            fix_msg=self.fix_msg,
        )

    @classmethod
    def from_proto(cls, proto: MsgInstantiateContract2_pb) -> "MsgInstantiateContract2":
        return cls(
            sender=proto.sender,
            admin=proto.admin,
            code_id=proto.code_id,
            label=proto.label,
            msg=parse_msg(proto.msg),
            funds=Coins.from_proto(proto.funds),
            salt=proto.salt,
            fix_msg=proto.fix_msg,
        )



@attr.s
class MsgExecuteContract(Msg):
    """Execute a state-mutating function on a smart contract.

    Args:
        sender: address of sender
        contract: address of contract to execute function on
        msg (dict|str): ExecuteMsg to pass
        coins: coins to be sent, if needed by contract to execute.
            Defaults to empty ``Coins()``
    """

    type_amino = "wasm/MsgExecuteContract"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgExecuteContract"
    """"""
    prototype = MsgExecuteContract_pb
    """"""

    sender: AccAddress = attr.ib()
    contract: AccAddress = attr.ib()
    msg: Union[dict, str] = attr.ib()
    coins: Coins = attr.ib(converter=Coins, factory=Coins)

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "contract": self.contract,
                "msg": remove_none(self.msg),
                "coins": self.coins.to_amino(),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgExecuteContract:
        return cls(
            sender=data["sender"],
            contract=data["contract"],
            msg=parse_msg(data["msg"]),
            coins=Coins.from_data(data["funds"]),
        )

    def to_proto(self) -> MsgExecuteContract_pb:
        return MsgExecuteContract_pb(
            sender=self.sender,
            contract=self.contract,
            msg=bytes(json.dumps(self.msg), "utf-8"),
            funds=self.coins.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgExecuteContract_pb) -> MsgExecuteContract:
        return cls(
            sender=proto.sender,
            contract=proto.contract,
            msg=parse_msg(proto.msg),
            coins=(proto.funds),
        )

@attr.s
class MsgExecuteContract_vbeta1(Msg):
    """Execute a state-mutating function on a smart contract.

    Args:
        sender: address of sender
        contract: address of contract to execute function on
        msg (dict|str): ExecuteMsg to pass
        coins: coins to be sent, if needed by contract to execute.
            Defaults to empty ``Coins()``
    """

    type_amino = "wasm/MsgExecuteContract"
    """"""
    type_url = "/terra.wasm.v1beta1.MsgExecuteContract"
    """"""
    prototype = MsgExecuteContract_pb
    """"""

    sender: AccAddress = attr.ib()
    contract: AccAddress = attr.ib()
    execute_msg: Union[dict, str] = attr.ib()
    coins: Coins = attr.ib(converter=Coins, factory=Coins)

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "contract": self.contract,
                "execute_msg": remove_none(self.msg),
                "coins": self.coins.to_amino(),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgExecuteContract:
        return cls(
            sender=data["sender"],
            contract=data["contract"],
            execute_msg=parse_msg(data["execute_msg"]),
            coins=Coins.from_data(data["coins"]),
        )
    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "sender": self.sender,
            "contract": self.contract,
            "execute_msg": self.execute_msg,
            "coins": self.coins.to_data(),
        }

    def to_proto(self) -> MsgExecuteContract_pb:
        return MsgExecuteContract_pb(
            sender=self.sender,
            contract=self.contract,
            execute_msg=bytes(json.dumps(self.execute_msg), "utf-8"),
            funds=self.coins.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: MsgExecuteContract_pb) -> MsgExecuteContract:
        return cls(
            sender=proto.sender,
            contract=proto.contract,
            execute_msg=parse_msg(proto.execute_msg),
            coins=(proto.funds),
        )

@attr.s
class MsgMigrateContract(Msg):
    """Migrate the contract to a different code ID.

    Args:
        sender: address of contract admin
        contract: address of contract to migrate
        code_id (int): new code ID to migrate to
        msg (dict|str): MigrateMsg to execute
    """

    type_amino = "wasm/MsgMigrateContract"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgMigrateContract"
    """"""
    prototype = MsgMigrateContract_pb
    """"""

    sender: AccAddress = attr.ib()
    contract: AccAddress = attr.ib()
    code_id: int = attr.ib(converter=int)
    msg: Union[dict, str] = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "contract": self.contract,
                "code_id": str(self.code_id),
                "msg": remove_none(self.msg),
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgMigrateContract:
        return cls(
            sender=data["sender"],
            contract=data["contract"],
            code_id=data["code_id"],
            msg=parse_msg(data["msg"]),
        )

    def to_proto(self) -> MsgMigrateContract_pb:
        return MsgMigrateContract_pb(
            sender=self.sender,
            contract=self.contract,
            code_id=self.code_id,
            msg=bytes(json.dumps(self.msg), "utf-8"),
        )

    @classmethod
    def from_proto(cls, proto: MsgMigrateContract_pb) -> MsgMigrateContract:
        return cls(
            sender=proto.sender,
            contract=proto.contract,
            code_id=proto.code_id,
            msg=parse_msg(proto.msg),
        )


@attr.s
class MsgUpdateAdmin(Msg):
    """Update a smart contract's admin.

    Args:
        sender: address of current admin (sender)
        new_admin: address of new admin
        contract: address of contract to change
    """

    type_amino = "wasm/MsgUpdateAdmin"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgUpdateAdmin"
    """"""
    prototype = MsgUpdateAdmin_pb
    """"""

    sender: AccAddress = attr.ib()
    new_admin: AccAddress = attr.ib()
    contract: AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "sender": self.sender,
                "new_admin": self.new_admin,
                "contract": self.contract,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgUpdateAdmin:
        return cls(
            sender=data["sender"],
            new_admin=data["new_admin"],
            contract=data["contract"],
        )

    def to_proto(self) -> MsgUpdateAdmin_pb:
        return MsgUpdateAdmin_pb(
            sender=self.sender, new_admin=self.new_admin, contract=self.contract
        )

    @classmethod
    def from_proto(cls, proto: MsgUpdateAdmin_pb) -> MsgUpdateAdmin:
        return cls(
            sender=proto.sender,
            new_admin=proto.new_admin,
            contract=proto.contract,
        )


@attr.s
class MsgClearAdmin(Msg):
    """Clears the contract's admin field.

    Args:
        admin: address of current admin (sender)
        contract: address of contract to change
    """

    type_amino = "wasm/MsgClearAdmin"
    """"""
    type_url = "/cosmwasm.wasm.v1.MsgClearAdmin"
    """"""
    prototype = MsgClearAdmin_pb
    """"""

    sender: AccAddress = attr.ib()
    contract: AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {"sender": self.sender, "contract": self.contract},
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgClearAdmin:
        return cls(
            sender=data["sender"],
            contract=data["contract"],
        )

    def to_proto(self) -> MsgClearAdmin_pb:
        return MsgClearAdmin_pb(sender=self.sender, contract=self.contract)

    @classmethod
    def from_proto(cls, proto: MsgClearAdmin_pb) -> MsgClearAdmin:
        return cls(
            sender=proto.sender,
            contract=proto.contract,
        )

from terra_proto.terra.wasm.v1beta1 import MsgUpdateContractAdmin as MsgUpdateContractAdmin_pb
@attr.s
class MsgUpdateContractAdmin(Msg):
    """
    Update a smart contract's admin in the v1beta1 module.

    Args:
        admin: address of current admin (sender)
        new_admin: address of new admin
        contract: address of contract to change
    """

    type_amino = "wasm/MsgUpdateContractAdmin"
    type_url = "/terra.wasm.v1beta1.MsgUpdateContractAdmin"
    prototype = MsgUpdateContractAdmin_pb

    admin: AccAddress = attr.ib()
    new_admin: AccAddress = attr.ib()
    contract: AccAddress = attr.ib()

    def to_amino(self) -> dict:
        return {
            "type": self.type_amino,
            "value": {
                "admin": self.admin,
                "new_admin": self.new_admin,
                "contract": self.contract,
            },
        }

    @classmethod
    def from_data(cls, data: dict) -> MsgUpdateContractAdmin:
        return cls(
            admin=data["admin"],
            new_admin=data["new_admin"],
            contract=data["contract"],
        )

    def to_data(self) -> dict:
        return {
            "@type": self.type_url,
            "admin": self.admin,
            "new_admin": self.new_admin,
            "contract": self.contract,
        }

    def to_proto(self) -> MsgUpdateContractAdmin_pb:
        return MsgUpdateContractAdmin_pb(
            admin=self.admin, new_admin=self.new_admin, contract=self.contract
        )

    @classmethod
    def from_proto(cls, proto: MsgUpdateContractAdmin_pb) -> MsgUpdateContractAdmin:
        return cls(
            admin=proto.admin,
            new_admin=proto.new_admin,
            contract=proto.contract,
        )
