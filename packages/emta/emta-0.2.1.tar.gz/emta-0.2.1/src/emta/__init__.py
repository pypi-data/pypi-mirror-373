"""Eastmoney Trading Library

Unofficial library for interacting with Eastmoney trading services.
"""

from .core.agent import TradingAgent
from .models.trading import Order, OrderStatus, OrderType

__all__ = ["TradingAgent", "Order", "OrderType", "OrderStatus"]
