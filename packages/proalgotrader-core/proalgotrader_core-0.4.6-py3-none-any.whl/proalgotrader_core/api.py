from logzero import logger
import requests
import asyncio

from typing import Any, Dict, List
from requests import Response
from proalgotrader_core.args_manager import ArgsManager


class Api:
    def __init__(self, args_manager: ArgsManager) -> None:
        self.args_manager = args_manager

        self.algo_session_key = self.args_manager.algo_session_key
        self.algo_session_secret = self.args_manager.algo_session_secret
        self.api_url = self.args_manager.api_url

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.token = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        data: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        url = f"{self.api_url}{endpoint}"
        logger.info(f"[{method.upper()}] {url} payload={json or data}")

        try:
            response: Response = await asyncio.to_thread(
                requests.request,
                method,
                url,
                data=data,
                json=json,
                headers=self.headers,
            )
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise Exception(e)

        try:
            result = response.json()
        except Exception:
            result = {}

        if not response.ok:
            logger.error(f"[{response.status_code}] {url} -> {result}")
            raise Exception(result)

        return result

    async def get_algo_session_info(self) -> Dict[str, Any]:
        try:
            result = await self._request(
                "post",
                "/api/algo-sessions/info",
                json={
                    "algo_session_key": self.algo_session_key,
                    "algo_session_secret": self.algo_session_secret,
                },
            )

            self.token = result["token"]
            self.headers["Authorization"] = f"Bearer {self.token}"

            return result
        except Exception as e:
            logger.error(f"get_algo_session_info failed: {e}")
            raise Exception(e)

    async def get_github_access_token(self, github_account_id: int) -> Dict[str, Any]:
        try:
            result = await self._request(
                "get",
                f"/api/github/accounts/{github_account_id}/access-token",
            )

            return result["access_token"]
        except Exception as e:
            logger.error(f"get_github_access_token failed: {e}")
            raise Exception(e)

    async def get_trading_days(self) -> List[Dict[str, Any]]:
        try:
            result = await self._request("get", "/api/trading-days/list")

            return result["trading_days"]
        except Exception as e:
            logger.error(f"get_trading_days failed: {e}")
            raise Exception(e)

    async def get_portfolio(self) -> Dict[str, Any]:
        try:
            result = await self._request(
                "get", f"/api/algo-sessions/{self.algo_session_key}/portfolio/list"
            )

            return result["portfolio"]
        except Exception as e:
            logger.error(f"get_portfolio failed: {e}")
            raise Exception(e)

    async def get_orders(self) -> Dict[str, Any]:
        try:
            result = await self._request(
                "get", f"/api/algo-sessions/{self.algo_session_key}/orders/list"
            )

            return result["orders"]
        except Exception as e:
            logger.error(f"get_orders failed: {e}")
            raise Exception(e)

    async def get_positions(self) -> Dict[str, Any]:
        try:
            result = await self._request(
                "get",
                f"/api/algo-sessions/{self.algo_session_key}/positions/list",
            )

            return result["positions"]
        except Exception as e:
            logger.error(f"get_positions failed: {e}")
            raise Exception(e)

    async def get_base_symbols(self) -> Dict[str, Any]:
        try:
            result = await self._request("get", "/api/base-symbols/list")

            return result["base_symbols"]
        except Exception as e:
            logger.error(f"get_base_symbols failed: {e}")
            raise Exception(e)

    async def get_broker_symbols(
        self, broker_title: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            result = await self._request(
                "get",
                f"/api/broker-symbols/{broker_title}/catalog",
                json=payload,
            )

            return result["broker_symbol"]
        except Exception as e:
            logger.error(f"get_broker_symbols failed: {e}")
            raise Exception(e)

    async def get_fno_expiry(self, payload: Dict[str, Any]) -> str | None:
        try:
            result = await self._request(
                "get",
                "/api/broker-symbols/fno/expiry",
                json=payload,
            )

            return result["expiry_date"]
        except Exception as e:
            logger.error(f"get_broker_symbols failed: {e}")
            raise Exception(e)

    async def enter_position(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self._request(
                "post",
                f"/api/algo-sessions/{self.algo_session_key}/positions/enter",
                json=payload,
            )

            return result["data"]
        except Exception as e:
            logger.error(f"enter_position failed: {e}")
            raise Exception(e)

    async def exit_position(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self._request(
                "post",
                f"/api/algo-sessions/{self.algo_session_key}/positions/exit",
                json=payload,
            )

            return result["data"]
        except Exception as e:
            logger.error(f"exit_position failed: {e}")
            raise Exception(e)

    async def exit_all_positions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await self._request(
                "post",
                f"/api/algo-sessions/{self.algo_session_key}/positions/exit/all",
                json=payload,
            )

            return result["data"]
        except Exception as e:
            logger.error(f"exit_position failed: {e}")
            raise Exception(e)

    async def get_risk_reward(
        self, position_id: str, payload: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        try:
            if not position_id:
                raise Exception("Position Id is required to get risk reward")

            result = await self._request(
                "get",
                f"/api/algo-sessions/{self.algo_session_key}/risk-rewards/{position_id}/info",
                json=payload or {},
            )

            return result["risk_reward"]
        except Exception as e:
            logger.error(f"get_risk_reward failed: {e}")
            raise Exception(e)

    async def create_risk_reward(
        self, position_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            if not position_id:
                raise Exception("Position Id is required to create risk reward")

            result = await self._request(
                "post",
                f"/api/algo-sessions/{self.algo_session_key}/risk-rewards/{position_id}/create",
                json=payload,
            )

            return result["risk_reward"]
        except Exception as e:
            logger.error(f"create_risk_reward failed: {e}")
            raise Exception(e)
