# Deribit Trading SDK

> The unofficial, fully-typed async Python SDK for Deribit, by Tribulnation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> [Read the docs](https://deribit.tribulnation.com)

## Quick Start

```bash
pip install deribit-trading-sdk
```

```python
from deribit import Deribit

async with Deribit.new(API_KEY, API_SECRET) as client:
  candles = await client.buy('BTC_USDT', {
    'price': '50000',
    'quantity': '0.001',
    'type': 'LIMIT',
    'side': 'BUY',
  })
```

## Why Deribit SDK?

- **🚀 Fully Async** - Built with `httpx` for high-performance async operations
- **🔒 Type Safe** - Complete type annotations with `TypedDict` and `pydantic` validation
- **⚡ Easy to Use** - Simple context-managed API with `async with`
- **📊 Comprehensive** - Spot trading, market data, wallet, and WebSocket streams
- **🎯 No Setup Required** - Start exploring markets immediately

## What's Included

- **Market Data** - Real-time prices, order books, and historical data
- **Spot Trading** - Place, cancel, and query orders
- **User Data** - Account balances, trade history, and order status
- **Wallet Operations** - Deposits, withdrawals, and address management
- **WebSocket Streams** - Live market data and user notifications

## Authentication

> Get your API keys from the [Deribit dashboard](https://www.deribit.com/account/BTC/api).

Or, you can use public methods:

```python
from deribit import MarketData

async with MarketData.new() as client:
  r = await client.get_order_book('BTC_USDC')
```

## Supported APIs

The SDK covers the following Deribit endpoints:

### Account

- [`get_account_summary`](deribit/src/deribit/account/get_account_summary.py)
- [`get_account_summaries`](deribit/src/deribit/account/get_account_summaries.py)

### Market Data

- [`get_contract_size`](deribit/src/deribit/market_data/get_contract_size.py)
- [`get_index_price`](deribit/src/deribit/market_data/get_index_price.py)
- [`get_instrument`](deribit/src/deribit/market_data/get_instrument.py)
- [`get_instruments`](deribit/src/deribit/market_data/get_instruments.py)
- [`get_last_trades_by_instrument`](deribit/src/deribit/market_data/get_last_trades_by_instrument.py)
- [`get_order_book`](deribit/src/deribit/market_data/get_order_book.py)

### Private Subscriptions

- [`user_orders`](deribit/src/deribit/subscriptions/private/user_orders.py)
- [`user_trades`](deribit/src/deribit/subscriptions/private/user_trades.py)

### Public Subscriptions

- [`depth_updates`](deribit/src/deribit/subscriptions/public/depth_updates.py)
- [`depth`](deribit/src/deribit/subscriptions/public/depth.py)
- [`trades`](deribit/src/deribit/subscriptions/public/trades.py)

### Trading

- [`buy`](deribit/src/deribit/trading/buy.py)
- [`cancel`](deribit/src/deribit/trading/cancel.py)
- [`cancel_all_by_currency_pair`](deribit/src/deribit/trading/cancel_all_by_currency_pair.py)
- [`cancel_all_by_currency`](deribit/src/deribit/trading/cancel_all_by_currency.py)
- [`cancel_all_by_instrument`](deribit/src/deribit/trading/cancel_all_by_instrument.py)
- [`cancel_all_by_kind_or_type`](deribit/src/deribit/trading/cancel_all_by_kind_or_type.py)
- [`cancel_all`](deribit/src/deribit/trading/cancel_all.py)
- [`cancel_by_label`](deribit/src/deribit/trading/cancel_by_label.py)
- [`edit`](deribit/src/deribit/trading/edit.py)
- [`edit_by_label`](deribit/src/deribit/trading/edit_by_label.py)
- [`get_open_orders`](deribit/src/deribit/trading/get_open_orders.py)
- [`get_open_orders_by_currency`](deribit/src/deribit/trading/get_open_orders_by_currency.py)
- [`get_open_orders_by_instrument`](deribit/src/deribit/trading/get_open_orders_by_instrument.py)
- [`get_open_orders_by_label`](deribit/src/deribit/trading/get_open_orders_by_label.py)
- [`get_order_state`](deribit/src/deribit/trading/get_order_state.py)
- [`get_order_state_by_label`](deribit/src/deribit/trading/get_order_state_by_label.py)
- [`get_user_trades_by_currency`](deribit/src/deribit/trading/get_user_trades_by_currency.py)
- [`get_user_trades_by_instrument`](deribit/src/deribit/trading/get_user_trades_by_instrument.py)

### Wallet

- [`get_current_deposit_address`](deribit/src/deribit/wallet/get_current_deposit_address.py)
- [`get_deposits`](deribit/src/deribit/wallet/get_deposits.py)
- [`get_withdrawals`](deribit/src/deribit/wallet/get_withdrawals.py)
- [`withdraw`](deribit/src/deribit/wallet/withdraw.py)