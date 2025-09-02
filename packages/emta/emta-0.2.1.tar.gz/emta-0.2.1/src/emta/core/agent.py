"""Main trading agent implementation."""

from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from emta.utils.stocks import get_market_code

from ..api.client import APIClient
from ..auth.client import AuthClient
from ..models.trading import (
    AccountInfo,
    AccountOverview,
    MarketData,
    OrderStatus,
    OrderType,
    Portfolio,
    Position,
)


class TradingAgent:
    """Eastmoney Trading Agent

    This class provides methods for interacting with Eastmoney trading services,
    including login, placing orders, checking account status, and retrieving market data.
    """

    def __init__(self, username: str | None = None, password: str | None = None):
        """Initialize the trading agent

        Args:
            username: Eastmoney account username
            password: Eastmoney account password
        """
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.account_info: list[AccountInfo] = []
        self.logger = logger
        self.session = httpx.Client()
        self.auth_client = AuthClient(self.session)

    def login(
        self,
        username: str | None = None,
        password: str | None = None,
        duration: int = 30,
    ) -> bool:
        """Login to Eastmoney account

        Args:
            username: Eastmoney account username (optional if provided in constructor)
            password: Eastmoney account password (optional if provided in constructor)
            duration: Eastmoney account login session duration in minutes (default: 30)

        Returns:
            bool: True if login successful, False otherwise

        Raises:
            LoginError: If login fails due to network or authentication issues
        """
        # Use provided credentials or fallback to instance variables
        login_username = username or self.username
        login_password = password or self.password

        if not login_username or not login_password:
            self.logger.error("Username and password are required for login")
            return False

        self.username = login_username
        self.password = login_password

        try:
            success, response = self.auth_client.login(
                login_username, login_password, duration
            )
            if success:
                self.is_logged_in = True
                # Get asset and position data
                self.api_client = APIClient(self.session, self.auth_client.validate_key)
                asset_pos = self.api_client.query_asset_and_position_v1()
                self.logger.info(asset_pos)

                # Handle the case where asset_pos might not have "Data" key
                if "Data" in asset_pos:
                    for data in asset_pos["Data"]:
                        # Create AccountOverview instance
                        account = AccountOverview(
                            Djzj=data.get("Djzj", 0),
                            Dryk=data.get("Dryk", 0),
                            Kqzj=data.get("Kqzj", 0),
                            Kyzj=data.get("Kyzj", 0),
                            Ljyk=data.get("Ljyk", 0),
                            Money_type=data.get("Money_type", ""),
                            RMBZzc=data.get("RMBZzc", 0),
                            Zjye=data.get("Zjye", 0),
                            Zxsz=data.get("Zxsz", 0),
                            Zzc=data.get("Zzc", 0),
                        )
                        print(account)

                        portfolio = Portfolio()

                        # Extract and add all positions
                        positions = data.get("positions", [])
                        for pos_data in positions:
                            position = Position(**pos_data)
                            portfolio.add_position(position)
                            print(portfolio)

                        account_info: AccountInfo = {
                            "username": login_username,
                            "account_overview": account,
                            "portfolio": portfolio,
                        }
                        self.account_info.append(account_info)
            else:
                self.logger.info(response)
            return success
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.is_logged_in = False
            return False

    def logout(self) -> None:
        """Logout from Eastmoney account"""
        self.is_logged_in = False
        self.account_info = []
        self.auth_client.logout()
        self.logger.info("Logged out successfully")

    def get_account_info(self) -> dict[str, Any] | list[AccountInfo]:
        """Get account information

        Returns:
            Dict containing account information
        """
        if not self.is_logged_in:
            self.logger.warning("User not logged in")
            return []

        # For backward compatibility, return a dict for the first account if available
        if self.account_info:
            first_account = self.account_info[0]
            # Since AccountInfo is a TypedDict, first_account is already a dict
            return {
                "username": first_account["username"],
                "account_balance": first_account["account_overview"].Zjye
                if first_account["account_overview"]
                else 0,
                "portfolio": first_account["portfolio"],
            }

        return []

    def place_order(
        self, stock_code: str, trade_type: OrderType, amount: int, price: float
    ) -> list[str] | None:
        """Place a trading order

        Args:
            stock_code: Stock symbol
            trade_type: Order type (BUY or SELL)
            amount: Number of shares
            price: Order price

        Returns:
            Order ID List if successful, None otherwise
        """
        if not self.is_logged_in or not self.auth_client.validate_key:
            self.logger.error("User not logged in")
            return None

        self.logger.info(
            f"Placing {trade_type.value} order for {stock_code}: "
            f"{amount} shares at {price}"
        )
        market = get_market_code(stock_code)
        resp = self.api_client.submit_trade_v2(
            stock_code, trade_type, market, price, amount
        )
        self.logger.info(resp)
        if resp["Status"] != 0:
            self.logger.error(resp["Message"])
            return None
        ret = []
        for i in resp["Data"]:
            # 订单字符串, 由成交日期+成交编号组成. 在create_order和query_order接口, Wtrq的值是成交日期, Wtbh的值是成交编号, 格式为: 20240520_130662
            order_id = f"{datetime.now().strftime('%Y%m%d')}_{i['Wtbh']}"
            ret.append(order_id)
            self.logger.info(f"Order placed successfully with ID: {order_id}")
        self.logger.info(ret)
        return ret

    def query_orders(self) -> list[str]:
        """Query a trading order

        Returns:
            Order ID List if successful, None otherwise
        """
        if not self.is_logged_in or not self.auth_client.validate_key:
            self.logger.error("User not logged in")
            return []
        return []

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order

        Args:
            order_id: ID of the order to cancel

        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.is_logged_in:
            self.logger.error("User not logged in")
            return False

        self.logger.info(f"Cancelling order: {order_id}")
        resp = self.api_client.revoke_orders(order_id)
        self.logger.info(f"Order {order_id} cancelled successfully")
        self.logger.info(resp)
        return True

    def get_order_status(self, order_id: str) -> OrderStatus | None:
        """Get the status of an order

        Args:
            order_id: ID of the order to check

        Returns:
            Order status or None if order not found
        """
        if not self.is_logged_in:
            self.logger.error("User not logged in")
            return None

        # TODO: Implement actual order status checking with Eastmoney API
        # This is a placeholder implementation
        self.logger.info(f"Checking status for order: {order_id}")
        return OrderStatus.FILLED

    def get_market_data(self, symbol: str) -> MarketData | dict[str, Any]:
        """Get market data for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing market data
        """
        if not self.is_logged_in:
            self.logger.warning("User not logged in")
            return {}

        # TODO: Implement actual market data retrieval with Eastmoney API
        # This is a placeholder implementation
        self.logger.info(f"Retrieving market data for: {symbol}")
        return {
            "symbol": symbol,
            "last_price": 100.0,
            "bid_price": 99.9,
            "ask_price": 100.1,
            "volume": 1000000,
            "timestamp": "2025-08-23T10:00:00",
        }
