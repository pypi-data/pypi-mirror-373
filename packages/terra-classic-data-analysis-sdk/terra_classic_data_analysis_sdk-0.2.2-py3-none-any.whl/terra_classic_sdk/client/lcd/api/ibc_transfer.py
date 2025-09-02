from terra_classic_sdk.core.ibc_transfer import DenomTrace

from ._base import BaseAsyncAPI, sync_bind

__all__ = ["AsyncIbcTransferAPI", "IbcTransferAPI"]


class AsyncIbcTransferAPI(BaseAsyncAPI):
    async def parameters(self) -> dict:
        """Fetches the IbcTransfer module's parameters.

        Returns:
            dict: IbcTransfer module parameters
        """
        res = await self._c._get("/ibc/apps/transfer/v1/params")
        params = res["params"]
        return {
            "send_enabled": bool(params["send_enabled"]),
            "receive_enabled": bool(params["receive_enabled"]),
        }
    async def denom_traces(self, params: dict = {}) -> (list, dict):
        """
        Fetches all denomination traces.

        Args:
            params (dict): optional pagination or query parameters

        Returns:
            list: A list of DenomTrace objects.
            dict: Pagination info
        """
        res = await self._c._get("/ibc/apps/transfer/v1/denom_traces", params)
        denom_traces = [DenomTrace.from_data(d) for d in res.get("denom_traces", [])]
        pagination = res.get("pagination")
        return denom_traces, pagination


class IbcTransferAPI(AsyncIbcTransferAPI):
    @sync_bind(AsyncIbcTransferAPI.parameters)
    def parameters(self) -> dict:
        pass

    parameters.__doc__ = AsyncIbcTransferAPI.parameters.__doc__

    @sync_bind(AsyncIbcTransferAPI.denom_traces)
    def denom_traces(self, params: dict = {}) -> (list, dict):
        pass

    denom_traces.__doc__ = AsyncIbcTransferAPI.denom_traces.__doc__