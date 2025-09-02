# MEXC Trading SDK

> The unofficial, fully-typed async Python SDK for MEXC, by Tribulnation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> [Read the docs](https://mexc.tribulnation.com)

## Quick Start

```bash
pip install mexc-trading-sdk
```

```python
from mexc import MEXC

async with MEXC.new(API_KEY, API_SECRET) as client:
  r = await client.spot.place_order('BTCUSDT', {
    'price': '50000',
    'quantity': '0.001',
    'type': 'LIMIT',
    'side': 'BUY',
  })
```

## Why MEXC SDK?

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

> Get your API keys from the [MEXC dashboard](https://www.mexc.com/user/openapi).

Or, you can use public methods:

```python
from mexc.spot import MarketData

async with MarketData() as client:
  candles = await client.candles('BTCUSDT', interval='15m')
```

## Supported APIs

The SDK covers the following MEXC endpoints:

### Spot

#### Trading
- [`place_order`](mexc/src/mexc/spot/trading/place_order.py)
- [`cancel_order`](mexc/src/mexc/spot/trading/cancel_order.py)
- [`cancel_all_orders`](mexc/src/mexc/spot/trading/cancel_all_orders.py)

#### User Data
- [`account`](mexc/src/mexc/spot/user_data/account.py) (balances)
- [`my_trades`](mexc/src/mexc/spot/user_data/my_trades.py) (trade history)
- [`query_order`](mexc/src/mexc/spot/user_data/query_order.py)
- [`open_orders`](mexc/src/mexc/spot/user_data/open_orders.py)
- [`my_orders`](mexc/src/mexc/spot/user_data/my_orders.py) (order history)

#### Market Data
- [`time`](mexc/src/mexc/spot/market_data/time.py) (server time)
- [`depth`](mexc/src/mexc/spot/market_data/depth.py) (order book)
- [`candles`](mexc/src/mexc/spot/market_data/candles.py) (klines)
- [`trades`](mexc/src/mexc/spot/market_data/trades.py) (recent trades)
- [`agg_trades`](mexc/src/mexc/spot/market_data/agg_trades.py)
- [`exchange_info`](mexc/src/mexc/spot/market_data/exchange_info.py)

#### Wallet
- [`currency_info`](mexc/src/mexc/wallet/currency_info.py) (withdrawal methods)
- [`deposit_addresses`](mexc/src/mexc/wallet/deposit_addresses.py) (deposit methods)
- [`withdraw`](mexc/src/mexc/wallet/withdraw.py)
- [`cancel_withdraw`](mexc/src/mexc/wallet/cancel_withdraw.py)
- [`deposit_history`](mexc/src/mexc/wallet/deposit_history.py)
- [`withdrawal_history`](mexc/src/mexc/wallet/withdrawal_history.py)

#### Public Streams
- [`candles`](mexc/src/mexc/spot/streams/market/candles.py)
- [`trades`](mexc/src/mexc/spot/streams/market/trades.py)

#### User Streams
- [`my_trades`](mexc/src/mexc/spot/streams/user/my_trades.py) (trade history)

### Futures

#### Trading

Has been "under maintenance" (see the [docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#order-under-maintenance)) for years. I.e., they don't want you to trade futures via the API, sorry.

#### Market Data
- [`candles`](mexc/src/mexc/futures/market_data/candles.py)
- [`funding_rate`](mexc/src/mexc/futures/market_data/funding_rate.py)
- [`contract_info`](mexc/src/mexc/futures/market_data/contract_info.py)

#### User Data
- [`my_trades`](mexc/src/mexc/futures/user_data/my_trades.py)
- [`funding_rate_history`](mexc/src/mexc/futures/user_data/funding_rate_history.py)

#### User Streams
- [`my_trades`](mexc/src/mexc/futures/streams/user/my_trades.py)