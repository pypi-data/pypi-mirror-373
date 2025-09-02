# terra_classic_sdk/client/lcd/api/bank.py
from typing import Optional, List

from terra_classic_sdk.core import AccAddress, Coins
from terra_classic_sdk.core.bank.data import Metadata

from ..params import APIParams
from ._base import BaseAsyncAPI, sync_bind

__all__ = ["AsyncBankAPI", "BankAPI"]


class AsyncBankAPI(BaseAsyncAPI):
    async def balance(
        self, address: AccAddress, params: Optional[APIParams] = None
    ) -> (Coins, dict):
        """Fetches an account's current balance.

        Args:
            address (AccAddress): account address
            params (APIParams, optional): additional params for the API like pagination

        Returns:
            Coins: balance
            Pagination: pagination info
        """
        res = await self._c._get(f"/cosmos/bank/v1beta1/balances/{address}", params)
        return Coins.from_data(res["balances"]), res.get("pagination")

    async def total(self, params: Optional[APIParams] = None) -> (Coins, dict):
        """Fetches the current total supply of all tokens.

        Returns:
            Coins: total supply
            params (APIParams, optional): additional params for the API like pagination
        """
        res = await self._c._get("/cosmos/bank/v1beta1/supply", params)
        return Coins.from_data(res.get("supply")), res.get("pagination")

    async def denoms_metadata(self, params: Optional[APIParams] = None) -> (List[Metadata], dict):
        """Fetches the denominations metadata.

        Args:
            params (APIParams, optional): additional params for the API like pagination

        Returns:
            List[Metadata]: list of denominations metadata
            dict: pagination info
        """
        res = await self._c._get("/cosmos/bank/v1beta1/denoms_metadata", params)
        metadatas = [Metadata.from_data(metadata) for metadata in res.get("metadatas", [])]
        return metadatas, res.get("pagination", {})


class BankAPI(AsyncBankAPI):
    @sync_bind(AsyncBankAPI.balance)
    def balance(
        self, address: AccAddress, params: Optional[APIParams] = None
    ) -> (Coins, dict):
        pass

    balance.__doc__ = AsyncBankAPI.balance.__doc__

    @sync_bind(AsyncBankAPI.total)
    def total(self, params: Optional[APIParams] = None) -> (Coins, dict):
        pass

    total.__doc__ = AsyncBankAPI.total.__doc__

    @sync_bind(AsyncBankAPI.denoms_metadata)
    def denoms_metadata(self, params: Optional[APIParams] = None) -> (List[Metadata], dict):
        pass

    denoms_metadata.__doc__ = AsyncBankAPI.denoms_metadata.__doc__
