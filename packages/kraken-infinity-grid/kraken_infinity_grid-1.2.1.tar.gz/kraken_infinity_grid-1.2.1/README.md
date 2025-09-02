<h1>
⚠️ This project will be archived soon, please migrate to https://github.com/btschwertfeger/infinity-grid
</h1>

<h1 align="center">Infinity Grid Trading Algorithm for the Kraken Exchange</h1>

<div align="center">

[![GitHub](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/btschwertfeger/kraken-infinity-grid)
[![Generic badge](https://img.shields.io/badge/python-3.11+-blue.svg)](https://shields.io/)
[![Downloads](https://static.pepy.tech/personalized-badge/kraken-infinity-grid?period=total&units=abbreviation&left_color=grey&right_color=orange&left_text=downloads)](https://pepy.tech/project/kraken-infinity-grid)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Typing](https://img.shields.io/badge/typing-mypy-informational)](https://mypy-lang.org/)
[![CI/CD](https://github.com/btschwertfeger/kraken-infinity-grid/actions/workflows/cicd.yaml/badge.svg?branch=master)](https://github.com/btschwertfeger/kraken-infinity-grid/actions/workflows/cicd.yaml)
[![codecov](https://codecov.io/gh/btschwertfeger/kraken-infinity-grid/branch/master/badge.svg)](https://app.codecov.io/gh/btschwertfeger/kraken-infinity-grid)

[![OpenSSF ScoreCard](https://img.shields.io/ossf-scorecard/github.com/btschwertfeger/kraken-infinity-grid?label=openssf%20scorecard&style=flat)](https://securityscorecards.dev/viewer/?uri=github.com/btschwertfeger/kraken-infinity-grid)
[![OpenSSF Best
Practices](https://www.bestpractices.dev/projects/9956/badge)](https://www.bestpractices.dev/projects/9956)

[![release](https://shields.io/github/release-date/btschwertfeger/kraken-infinity-grid)](https://github.com/btschwertfeger/kraken-infinity-grid/releases)
[![release](https://img.shields.io/pypi/v/kraken-infinity-grid)](https://pypi.org/project/kraken-infinity-grid/)
[![Documentation Status Stable](https://readthedocs.org/projects/kraken-infinity-grid/badge/?version=stable)](https://kraken-infinity-grid.readthedocs.io/en/stable)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14735203.svg)](https://doi.org/10.5281/zenodo.14735203)

</div>

> ⚠️ **Disclaimer**: This software was initially designed for private use only.
> Please note that this project is independent and not endorsed by Kraken or
> Payward Ltd. Users should be aware that they are using third-party software,
> and the authors of this project are not responsible for any issues, losses, or
> risks associated with its usage. **Payward Ltd. and Kraken are in no way
> associated with the authors of this package and documentation.**
>
> There is no guarantee that this software will work flawlessly at this or later
> times. Of course, no responsibility is taken for possible profits or losses.
> This software probably has some errors in it, so use it at your own risk. Also
> no one should be motivated or tempted to invest assets in speculative forms of
> investment. By using this software you release the author(s) from any
> liability regarding the use of this software.

The kraken-infinity-grid is a trading algorithm that uses grid trading
strategies that places buy and sell orders in a grid-like manner, while
following the principle of buying low and selling high. It is designed for
trading cryptocurrencies on the [Kraken](https://pro.kraken.com) Spot exchange,
is written in Python and uses the
[python-kraken-sdk](https://github.com/btschwertfeger/python-kraken-sdk) library
to interact with the Kraken API.

The algorithm requires a PostgreSQL or SQLite database and can be run either
locally or in a Docker container (recommended). The algorithm can be configured
to use different trading strategies, such as GridHODL, GridSell, SWING, and
cDCA.

While the verbosity levels of logging provide useful insights into the
algorithms's behavior, the Telegram notifications can be used to receive updates
on the algorithms's activity and exceptions. For this the algorithm requires two
different Telegram bot tokens and chat IDs, one for regular notifications and
one for exception notifications (see [Setup](#Setup) for more information).

Documentation:

- https://kraken-infinity-grid.readthedocs.io/en/latest/
- https://kraken-infinity-grid.readthedocs.io/en/stable/

PnL Calculator (for tax purposes):

- https://github.com/btschwertfeger/kraken-pnl-calculator

## 📚 Fundamental concepts

`kraken-infinity-grid` is a sophisticated trading algorithm designed for
automated cryptocurrency trading using a grid strategy. This approach is
particularly effective in volatile markets, where frequent price fluctuations
allow for consistent profit opportunities through structured buying and selling
patterns.

### 📈 The core idea: Grid trading

At its essence, grid trading aims to capitalize on market volatility by setting
a series of buy and sell orders at predefined intervals. The algorithm operates
within a "grid" of prices, purchasing assets when prices dip and selling them as
prices rise. This systematic approach helps in capturing small gains repeatedly,
leveraging the natural oscillations in market prices.

<div align="center">
  <figure>
    <img
    src="doc/_static/images/blsh.png?raw=true"
    alt="Buying low and selling high in high-volatile markets"
    style="background-color: white; border-radius: 7px">
    <figcaption>Figure 1: Buying low and selling high in high-volatile markets</figcaption>
  </figure>
</div>

_All currency pairs mentioned here are for illustrative purposes only._

### 📊 Key Elements of Grid Trading

1. **Intervals**: Unlike fully static systems, `kraken-infinity-grid` uses
   fixed intervals that shift up or down based on price movements, ensuring
   continuous trading and avoids manual interactions. This flexibility is
   crucial for maintaining profitability in diverse market environments.

2. **Volatility Advantage**: High volatility is a friend to grid traders. The
   more the price oscillates, the more opportunities arise to buy low and sell
   high. The algorithm thrives in such conditions, with each price movement
   potentially triggering a profitable trade.

3. **Consistent Position Sizing**: Each trade involves a consistent volume in
   terms of the quote currency (e.g., $100 per trade). This uniformity
   simplifies the management of trades and helps in maintaining a balanced
   portfolio.

### 📉 Risk Management and Reinvestment

1. **Risk Mitigation**: The algorithm inherently incorporates risk management by
   spreading investments across multiple price levels and maintaining almost
   consistent trade sizes. This diversification reduces the impact of adverse
   market movements on the overall portfolio.

2. **Reinvestment Mechanism**: Accumulated profits can be reinvested, enhancing
   the trading capital and potential returns. The algorithm automatically
   adjusts buy and and places sell orders to reflect the increased capital, thus
   compounding growth over time.

## 📊 Available strategies

Each of the following strategies is designed to leverage different aspects of
market behavior, providing flexibility and adaptability to traders depending on
their risk tolerance, market outlook, and investment goals.

### `GridHODL`

The _GridHODL_ strategy operates on a predefined grid system where buy and sell
orders are placed at fixed intervals below and above the current market price,
respectively. This strategy is designed to capitalize on market fluctuations by
buying low and selling high, ensuring gradual accumulation of the base currency
over time.

Technical Breakdown:

- **Order Placement**: The algorithm dynamically adjusts $n$ buy orders
  below the current market price. For example, with a 4% interval, if the
  current BTC price is $50,000, the first buy order is set at $48,000, the
  second at $46,080, and so on.
- **Execution**: Upon execution of a buy order, a corresponding sell order is
  immediately placed at 4% above the purchase price respecting a fixed quote
  volume. This creates a cycle of continuous buying and selling, with each cycle
  aiming to yield a small portion in the base currency.
- **Accumulation**: Unlike traditional trading strategies, GridHODL is designed
  to accumulate the base currency gradually. Each buy order slightly increases
  the holdings, while the fixed order size in terms of quote currency (e.g.,
  $100) ensures consistent exposure.

This strategy is particularly effective in sideways, slightly, and high volatile
markets, where frequent price oscillations allow for regular execution of the
grid orders. Accumulating the base currency over time can lead to significant
gains, especially when prices rise after a long accumulation phase.

### `GridSell`

The _GridSell_ is a complementary approach to `GridHODL`, focusing on
liquidating the purchased base currency in each trade cycle to realize immediate
profits. The key distinction is that each sell order matches the total quantity
bought in the preceding buy order.

Technical Breakdown:

- **Order Logic**: For every buy order executed (e.g., purchasing $100 worth of
  BTC at $48,000), a sell order is placed for the entire amount of BTC acquired
  at a 4% higher price. This ensures that each trade cycle results in a complete
  turnover of the base currency.
- **Profit Realization**: The strategy ensures that profits are locked in at
  each cycle, reducing the need for long-term accumulation or holding. It is
  particularly suitable for traders who prioritize short-term gains over base
  currency accumulation.
- **Risk Mitigation**: By liquidating the entire bought amount, the GridSell
  strategy minimizes exposure to prolonged market downturns, ensuring that the
  trader consistently realizes profits without holding onto assets for extended
  periods.

### `SWING`

The _SWING_ strategy builds upon `GridHODL` but introduces a mechanism to
capitalize on significant upward price movements by selling accumulated base
currency at higher levels.

Technical Breakdown:

- **Market Adaptation**: This strategy tracks the highest buy price within a
  defined range (e.g., $40,000 to $80,000). If the market price exceeds this
  range (e.g., rises to $83,200), the algorithm initiates sell orders at
  predefined intervals (e.g., 4% above the highest buy price).
- **Sell Execution**: Unlike `GridHODL`, which focuses on buying and selling in
  cycles, SWING starts selling accumulated base currency once the price
  surpasses the highest recorded buy price. This ensures that profits are
  captured during bullish market trends.
- **Continuous Accumulation**: Even as it initiates sell orders above the
  highest buy price, the algorithm continues to place buy orders below it,
  ensuring that base currency accumulation continues during market dips.
- **Profit Maximization**: This dual approach allows traders to benefit from
  both upward trends (through sell orders) and downward corrections (through
  continued accumulation).

> ⚠️ It also starts selling the already existing base currency above the
> current price. This should be kept in mind when choosing this
> strategy.

### `cDCA`

The _cDCA_ (Custom Dollar-Cost Averaging) strategy diverges from traditional DCA
by incorporating dynamic interval adjustments to optimize long-term accumulation
of the base currency.

Technical Breakdown:

- **Fixed Interval Purchases**: Unlike time-based DCA, cDCA places buy orders at
  fixed percentage intervals (e.g., every 4% price movement) rather than at
  regular time intervals. This ensures that purchases are made in response to
  market movements rather than arbitrary time frames.
- **No Sell Orders**: cDCA focuses purely on accumulation. It consistently buys
  the base currency (e.g., $100 worth of BTC) at each interval without placing
  corresponding sell orders, banking on long-term price appreciation.
- **Adaptive Buy Orders**: The algorithm adapts to rising prices by shifting buy
  orders upward rather than letting them fall out of scope. For instance, if the
  price exceeds $60,000, new buy orders are placed at 4% intervals below this
  new level, maintaining relevance in the current market context.
- **Long-Term Growth**: This strategy is ideal for traders with a long-term
  investment horizon, aiming to build a significant position in the base
  currency over time, with the expectation of future price increases.

<a name="setup"></a>

## 🚀 Setup

<a name="preparation"></a>

### Preparation

Before installing and running the `kraken-infinity-grid`, you need to make sure
to clearly understand the available trading strategies and their configuration.
Avoid running the algorithm with real money before you are confident in the
algorithm's behavior and performance!

1. In order to trade at the [Kraken Cryptocurrency
   Exchange](https://pro.kraken.com), you need to generate API keys for the
   Kraken exchange (see [How to create an API
   key](https://support.kraken.com/hc/en-us/articles/360000919966-How-to-create-an-API-key)).
   Make sure to generate keys with the required permissions for trading and
   querying orders:

<div align="center">
  <figure>
    <img
    src="doc/_static/images/kraken_api_key_permissions.png?raw=true"
    alt="Required API key permissions"
    style="background-color: white; border-radius: 7px">
    <figcaption>Figure 2: Required API key permissions</figcaption>
  </figure>
</div>

2. [optional] The algorithm leverages Telegram Bots to send notifications about
   the current state of the algorithm. We need two, one for the notifications
   about the algorithm's state and trades and one for notifications about
   errors.

   - Create two bots, name as you wish via: https://telegram.me/BotFather.
   - Start the chat with both new Telegram bots and write any message to ensure
     that the chat ID is available in the next step.
   - Get the bot token from the BotFather and access
     `https://api.telegram.org/bot<your bot token here>/getUpdates` to receive
     your chat ID.
   - Save the chat IDs as well as the bot tokens for both of them, we'll need
     them later.

This repository contains a `docker-compose.yaml` file that can be used to run
the algorithm using docker compose. The `docker-compose.yaml` also provides a
default configuration for the PostgreSQL database. To run the algorithm, follow
these steps:

### Running the algorithm

**Pure Python process**

To run the algorithm as a pure Python process, follow these steps:

1. Install the package via pip:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install kraken-infinity-grid
   ```

2. The algorithm can be started via the command-line interface. For using a
   local SQLite database, you can specify the path to the SQLite database file
   via the `--sqlite-file` option. The SQLite database is created
   automatically if it does not exist, otherwise the existing database is used.
   See more configuration options within the configuration section.

   ```bash
   kraken-infinity-grid \
       --api-key <your-api-key> \
       --secret-key <your-api-secret> \
       run \
       --strategy "GridHODL" \
       ...
       --sqlite-file=/path/to/sqlite.db
   ```

**Docker Compose**

The repository of the
[`kraken-infinity-grid`](https://github.com/btschwertfeger/kraken-infinity-grid)
contains a `docker-compose.yaml` file that can be used to run the algorithm
using Docker Compose. This file also provides a default configuration for the
PostgreSQL database. To run the algorithm, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/btschwertfeger/kraken-infinity-grid.git
   ```

2. Build the Docker images:

   ```bash
   docker system prune -a
   docker compose build --no-cache
   ```

3. Configure the algorithm either by ensuring the environment variables
   documented further down are set or by setting them directly within the
   `docker-compose.yaml`..

4. Run the algorithm:

   ```bash
   docker compose up # -d
   ```

5. Check the logs of the container and the Telegram chat for updates.

## 🛠 Configuration

| Variable                       | Type               | Description                                                                                                                                                                                                                                                                                                    |
| ------------------------------ | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `KRAKEN_API_KEY`               | `str`              | Your Kraken API key.                                                                                                                                                                                                                                                                                           |
| `KRAKEN_SECRET_KEY`            | `str`              | Your Kraken secret key.                                                                                                                                                                                                                                                                                        |
| `KRAKEN_RUN_NAME`              | `str`              | The name of the instance. Can be any name that is used to differentiate between instances of the kraken-infinity-grid.                                                                                                                                                                                         |
| `KRAKEN_RUN_USERREF`           | `int`              | A reference number to identify the algorithms's orders. This can be a timestamp or any integer number. **Use different userref's for different algorithms!**                                                                                                                                                   |
| `KRAKEN_BOT_VERBOSE`           | `int`/(`-v`,`-vv`) | Enable verbose logging.                                                                                                                                                                                                                                                                                        |
| `KRAKEN_DRY_RUN`               | `bool`             | Enable dry-run mode (no actual trades).                                                                                                                                                                                                                                                                        |
| `KRAKEN_RUN_BASE_CURRENCY`     | `str`              | The base currency e.g., `BTC`.                                                                                                                                                                                                                                                                                 |
| `KRAKEN_RUN_QUOTE_CURRENCY`    | `str`              | The quote currency e.g., `USD`.                                                                                                                                                                                                                                                                                |
| `KRAKEN_RUN_AMOUNT_PER_GRID`   | `float`            | The amount to use per grid interval e.g., `100` (USD).                                                                                                                                                                                                                                                         |
| `KRAKEN_RUN_INTERVAL`          | `float`            | The interval between orders e.g., `0.04` to have 4 % intervals.                                                                                                                                                                                                                                                |
| `KRAKEN_RUN_N_OPEN_BUY_ORDERS` | `int`              | The number of concurrent open buy orders e.g., `5`. The number of always open buy positions specifies how many buy positions should be open at the same time. If the interval is defined to 2%, a number of 5 open buy positions ensures that a rapid price drop of almost 10% that can be caught immediately. |
| `KRAKEN_RUN_MAX_INVESTMENT`    | `str`              | The maximum investment amount, e.g. `1000` USD.                                                                                                                                                                                                                                                                |
| `KRAKEN_RUN_FEE`               | `float`            | A custom fee percentage, e.g. `0.0026` for 0.26 % fee.                                                                                                                                                                                                                                                         |
| `KRAKEN_RUN_STRATEGY`          | `str`              | The trading strategy (e.g., `GridHODL`, `GridSell`, `SWING`, or `cDCA`).                                                                                                                                                                                                                                       |
| `KRAKEN_RUN_TELEGRAM_TOKEN`    | `str`              | The Telegram bot token for notifications.                                                                                                                                                                                                                                                                      |
| `KRAKEN_RUN_TELEGRAM_CHAT_ID`  | `str`              | The Telegram chat ID for notifications.                                                                                                                                                                                                                                                                        |
| `KRAKEN_RUN_EXCEPTION_TOKEN`   | `str`              | The Telegram bot token for exception notifications.                                                                                                                                                                                                                                                            |
| `KRAKEN_RUN_EXCEPTION_CHAT_ID` | `str`              | The Telegram chat ID for exception notifications.                                                                                                                                                                                                                                                              |
| `KRAKEN_RUN_DB_USER`           | `str`              | The PostgreSQL database user.                                                                                                                                                                                                                                                                                  |
| `KRAKEN_RUN_DB_NAME`           | `str`              | The PostgreSQL database name.                                                                                                                                                                                                                                                                                  |
| `KRAKEN_RUN_DB_PASSWORD`       | `str`              | The PostgreSQL database password.                                                                                                                                                                                                                                                                              |
| `KRAKEN_RUN_DB_HOST`           | `str`              | The PostgreSQL database host.                                                                                                                                                                                                                                                                                  |
| `KRAKEN_RUN_DB_PORT`           | `int`              | The PostgreSQL database port.                                                                                                                                                                                                                                                                                  |
| `KRAKEN_RUN_SQLITE_FILE`       | `str`              | The path to a local SQLite database file, e.g., `/path/to/sqlite.db`, will be created if it does not exist. If a SQLite database is used, the PostgreSQL database configuration is ignored.                                                                                                                    |

<a name="monitoring"></a>

## 📡 Monitoring

Trades as well as open positions can be monitored at
[Kraken](https://pro.kraken.com).

<div align="center">
  <figure>
    <img
    src="doc/_static/images/kraken_dashboard.png?raw=true"
    alt="Required API key permissions"
    style="background-color: white; border-radius: 7px">
    <figcaption>Figure 3: Monitoring orders via Kraken's web UI</figcaption>
  </figure>
</div>

Additionally, the algorithm can be configured to send notifications about the
current state of the algorithm via Telegram Bots (see
[Preparation](#preparation)).

<div align="center">
  <figure>
    <img
    src="doc/_static/images/telegram_update.png?raw=true"
    alt="Required API key permissions"
    style="background-color: white; border-radius: 7px; height: 500px">
    <figcaption>Figure 4: Monitoring orders and trades via Telegram</figcaption>
  </figure>
</div>

## 🚨 Troubleshooting

- Only use release versions of the `kraken-infinity-grid`. The `master` branch
  might contain unstable code! Also pin the the dependencies used in order to
  avoid unexpected behavior.
- Check the **permissions of your API keys** and the required permissions on the
  respective endpoints.
- If you get some Cloudflare or **rate limit errors**, please check your Kraken
  Tier level and maybe apply for a higher rank if required.
- **Use different API keys for different algorithms**, because the nonce
  calculation is based on timestamps and a sent nonce must always be the highest
  nonce ever sent of that API key. Having multiple algorithms using the same
  keys will result in invalid nonce errors.
- Kraken often has **maintenance windows**. Please check the status page at
  https://status.kraken.com/ for more information.
- When encountering errors like "Could not find order '...'. Retry 3/3 ...",
  this might be due to the **Kraken API being slow**. The algorithm will retry
  the request up to three times before raising an exception. If the order is
  still not available, just restart the algorithm - or let this be handled by
  Docker compose to restart the container automatically. Then the order will
  most probably be found.

## Backtesting

- The `tools/` directory contains some backtesting tries, but this is still to
  be developed and not ready yet for actual backtesting activities.

---

<a name="notes"></a>

## 📝 Notes

This project follows semantic versioning (`v<Major>.<Minor>.<Patch>`). Here's
what each part signifies:

- **Major**: This denotes significant changes that may introduce new features or
  modify existing ones. It's possible for these changes to be breaking, meaning
  backward compatibility is not guaranteed. To avoid unexpected behavior, it's
  advisable to specify at least the major version when pinning dependencies.
- **Minor**: This level indicates additions of new features or extensions to
  existing ones. Typically, these changes do not break existing implementations.
- **Patch**: Here, you'll find bug fixes, documentation updates, and changes
  related to continuous integration (CI). These updates are intended to enhance
  stability and reliability without altering existing functionality.

<a name="references"></a>

## 🔭 References

- https://github.com/btschwertfegr/python-kraken-sdk
