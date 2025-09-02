# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# All rights reserved.
# https://github.com/btschwertfeger
#

from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING, Self

import requests

if TYPE_CHECKING:

    from kraken_infinity_grid.gridbot import KrakenInfinityGridBot

LOG = getLogger(__name__)


class Telegram:
    """Telegram class to send messages to a Telegram chat."""

    def __init__(
        self: Self,
        strategy: "KrakenInfinityGridBot",
        telegram_token: str,
        telegram_chat_id: str,
        exception_token: str,
        exception_chat_id: str,
    ) -> None:
        self.__s = strategy
        self.__telegram_token = telegram_token
        self.__telegram_chat_id = telegram_chat_id
        self.__exception_token = exception_token
        self.__exception_chat_id = exception_chat_id

    def send_to_telegram(
        self: Self,
        message: str,
        exception: bool | None = False,
        log: bool = True,
    ) -> None:
        """Send a message to a Telegram chat"""
        if exception:
            if log:
                LOG.error(message)
            if not (self.__exception_token and self.__exception_chat_id):
                return
            response = requests.post(
                url=f"https://api.telegram.org/bot{self.__exception_token}/sendMessage",
                params={
                    "chat_id": self.__exception_chat_id,
                    "text": f"```\n{message}\n```",
                    "parse_mode": "markdown",
                },
                timeout=10,
            )
        else:
            if log:
                LOG.info(message)
            if not (self.__telegram_token and self.__telegram_chat_id):
                return
            response = requests.post(
                url=f"https://api.telegram.org/bot{self.__telegram_token}/sendMessage",
                params={
                    "chat_id": self.__telegram_chat_id,
                    "text": message,
                    "parse_mode": "markdown",
                },
                timeout=10,
            )

        if response.status_code != 200:
            # Its not that important to send telegram messages... so we just log
            # this here. The user will know that something is wrong when not
            # receiving regular status updates.
            LOG.error(
                "Failed to send message to Telegram. Status code: %d, message: \n%s",
                response.status_code,
                message,
            )

    def send_telegram_update(self: Self) -> None:
        """Send a message to the Telegram chat with the current status."""
        balances = self.__s.get_balances()

        message = f"👑 {self.__s.symbol}\n"
        message += f"└ Price » {self.__s.ticker.last} {self.__s.quote_currency}\n\n"

        message += "⚜️ Account\n"
        message += f"├ Total {self.__s.base_currency} » {balances['base_balance']}\n"
        message += f"├ Total {self.__s.quote_currency} » {balances['quote_balance']}\n"
        message += (
            f"├ Available {self.__s.quote_currency} » {balances['quote_available']}\n"
        )
        message += f"├ Available {self.__s.base_currency} » {balances['base_available'] - float(self.__s.configuration.get()['vol_of_unfilled_remaining'])}\n"  # noqa: E501
        message += f"├ Unfilled surplus of {self.__s.base_currency} » {self.__s.configuration.get()['vol_of_unfilled_remaining']}\n"  # noqa: E501
        message += f"├ Wealth » {round(balances['base_balance'] * self.__s.ticker.last + balances['quote_balance'], self.__s.cost_decimals)} {self.__s.quote_currency}\n"  # noqa: E501
        message += f"└ Investment » {round(self.__s.investment, self.__s.cost_decimals)} / {self.__s.max_investment} {self.__s.quote_currency}\n\n"  # noqa: E501

        message += "💠 Orders\n"
        message += f"├ Amount per Grid » {self.__s.amount_per_grid} {self.__s.quote_currency}\n"
        message += f"└ Open orders » {self.__s.orderbook.count()}\n"

        message += "\n```\n"
        message += f" 🏷️ Price in {self.__s.quote_currency}\n"
        max_orders_to_list: int = 5

        next_sells = [
            order["price"]
            for order in self.__s.orderbook.get_orders(
                filters={"side": "sell"},
                order_by=("price", "ASC"),
                limit=max_orders_to_list,
            )
        ]
        next_sells.reverse()

        if (n_sells := len(next_sells)) == 0:
            message += f"└───┬> {self.__s.ticker.last}\n"
        else:
            for index, sell_price in enumerate(next_sells):
                change = (sell_price / self.__s.ticker.last - 1) * 100
                if index == 0:
                    message += f" │  ┌[ {sell_price} (+{change:.2f}%)\n"
                elif index <= n_sells - 1 and index != max_orders_to_list:
                    message += f" │  ├[ {sell_price} (+{change:.2f}%)\n"
            message += f" └──┼> {self.__s.ticker.last}\n"

        next_buys = [
            order["price"]
            for order in self.__s.orderbook.get_orders(
                filters={"side": "buy"},
                order_by=("price", "DESC"),
                limit=max_orders_to_list,
            )
        ]
        if (n_buys := len(next_buys)) != 0:
            for index, buy_price in enumerate(next_buys):
                change = (buy_price / self.__s.ticker.last - 1) * 100
                if index < n_buys - 1 and index != max_orders_to_list:
                    message += f"    ├[ {buy_price} ({change:.2f}%)\n"
                else:
                    message += f"    └[ {buy_price} ({change:.2f}%)"
        message += "\n```"

        self.send_to_telegram(message)
        self.__s.configuration.update({"last_telegram_update": datetime.now()})
