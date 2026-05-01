"""
Quick smoke test for the data tools.

Run this BEFORE starting the agent to confirm that yfinance is working
and your symbol mappings produce sane numbers:

    python smoke_test.py

If you see prices and a portfolio table, you're good to go.
"""

import json

from tools.market_data import (
    get_quote_data,
    get_market_overview_data,
    get_sector_movers_data,
)
from tools.portfolio import get_portfolio_data, get_position_data


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def main() -> None:
    section("get_quote('Reliance')")
    print(json.dumps(get_quote_data("Reliance"), indent=2))

    section("get_quote('Nifty')")
    print(json.dumps(get_quote_data("Nifty"), indent=2))

    section("get_market_overview()")
    print(json.dumps(get_market_overview_data(), indent=2))

    section("get_sector_movers('IT')")
    print(json.dumps(get_sector_movers_data("IT"), indent=2))

    section("get_portfolio()")
    print(json.dumps(get_portfolio_data(), indent=2))

    section("get_position('TCS')")
    print(json.dumps(get_position_data("TCS"), indent=2))


if __name__ == "__main__":
    main()
