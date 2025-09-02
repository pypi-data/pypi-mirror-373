"""API client for Eastmoney trading operations."""

from typing import Any

import httpx
from loguru import logger

from emta.models.trading import OrderType

from ..models.exceptions import TradingError, ValidateKeyError

# Base headers for API requests
BASE_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://jywg.18.cn",
    "Host": "jywg.18.cn",
}


class APIClient:
    """Handles API requests to Eastmoney trading services"""

    def __init__(self, session: httpx.Client, validate_key: str | None):
        """Initialize the API client.

        Args:
            session: HTTP client session
        """
        self.session = session
        self.logger = logger
        if not validate_key:
            raise ValidateKeyError("Validate key is not validate or You not login")
        self.validate_key = validate_key

    def _check_response(self, resp: httpx.Response) -> None:
        """Check if response is successful.

        Args:
            resp: HTTP response to check

        Raises:
            TradingError: If response status is not 200
        """
        if resp.status_code != 200:
            self.logger.error(
                f"Request {resp.url} failed, code={resp.status_code}, response={resp.text}"
            )
            raise TradingError(f"API request failed with status {resp.status_code}")

    def query_something(
        self, url: str, req_data: dict[str, Any] | None = None
    ) -> httpx.Response:
        """通用查询函数

        :param url: 请求url
        :param req_data: 请求提交数据,可选
        :return: HTTP响应
        """
        full_url = f"{url}{self.validate_key}"
        if req_data is None:
            req_data = {
                "qqhs": 100,
                "dwc": "",
            }
        headers = BASE_HEADERS.copy()
        headers["X-Requested-With"] = "XMLHttpRequest"
        self.logger.debug(f"(url={full_url}), (data={req_data})")
        resp = self.session.post(full_url, headers=headers, data=req_data)
        self._check_response(resp)
        return resp

    def query_asset_and_position_v1(self) -> dict[str, Any]:
        """Get asset and position information.

        Args:
            validate_key: Validation key for the session

        Returns:
            Dictionary containing asset and position data
        """
        url = "https://jywg.18.cn/Com/queryAssetAndPositionV1?validatekey="
        resp = self.query_something(url)
        self._check_response(resp)
        return resp.json()  # type: ignore[no-any-return]

    def submit_trade_v2(
        self,
        stock_code: str,
        trade_type: OrderType,
        market: str,
        price: float,
        amount: int,
    ) -> dict[str, Any]:
        """交易接口, 买入或卖出.

        :param str stock_code: 股票代码
        :param str trade_type: 交易方向,B for buy, S for sell
        :param str market: 股票市场,HA 上海, SA
        :param float price: 股票价格
        :param int amount: 买入/卖出数量
        """
        req_data = {
            "stockCode": stock_code,
            "tradeType": trade_type.value,
            "zqmc": "",
            "market": market,
            "price": price,
            "amount": amount,
        }
        self.logger.info(req_data)
        url = "https://jywg.18.cn/Trade/SubmitTradeV2?validatekey="
        resp = self.query_something(url, req_data=req_data)
        self._check_response(resp)
        return resp.json()  # type: ignore[no-any-return]

    def revoke_orders(self, order_str: str) -> str | Any:
        """取消交易接口.

        :param str order_str: 订单字符串, 由成交日期+成交编号组成. 在create_order和query_order接口, Wtrq的值是成交日期, Wtbh的值是成交编号, 格式为: 20240520_130662
        """
        data = {"revokes": order_str.strip()}
        url = "https://jywg.18.cn/Trade/RevokeOrders?validatekey="
        resp = self.query_something(url, req_data=data)
        self._check_response(resp)
        return resp.text.strip()

    def get_order_data(self) -> dict[str, Any]:
        """查询交易接口."""
        url = "https://jywg.18.cn/Search/GetOrdersData?validatekey="
        resp = self.query_something(url)
        self._check_response(resp)
        return resp.json()  # type: ignore[no-any-return]
