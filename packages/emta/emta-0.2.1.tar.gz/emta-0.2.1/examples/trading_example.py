#!/usr/bin/env python3
"""Example usage of the Eastmoney Trading Library"""

from emta import OrderType, TradingAgent


def main():
    # Create a trading agent
    agent = TradingAgent("your_username", "your_password")

    # Login to Eastmoney
    if agent.login():
        print("Successfully logged in to Eastmoney")

        # Get account information
        account_info = agent.get_account_info()
        print(f"Account balance: {account_info.get('account_balance', 0)}")

        # Place a buy order
        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        if order_id:
            print(f"Order placed successfully with ID: {order_id}")

        # Get market data
        market_data = agent.get_market_data("SH600000")
        print(f"Market data for SH600000: {market_data}")

        # Logout
        agent.logout()
        print("Logged out successfully")
    else:
        print("Failed to log in to Eastmoney")


if __name__ == "__main__":
    main()
