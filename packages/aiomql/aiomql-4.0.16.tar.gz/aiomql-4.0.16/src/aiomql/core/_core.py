from typing import Callable

import MetaTrader5
from MetaTrader5 import (
    Tick,
    SymbolInfo,
    AccountInfo,
    TerminalInfo,
    TradeOrder,
    TradePosition,
    TradeDeal,
    OrderCheckResult,
    OrderSendResult,
    BookInfo,
    TradeRequest,
)

from .config import Config

constants = (
    "TIMEFRAME_M1",
    "TIMEFRAME_M2",
    "TIMEFRAME_M3",
    "TIMEFRAME_M4",
    "TIMEFRAME_M5",
    "TIMEFRAME_M6",
    "TIMEFRAME_M10",
    "TIMEFRAME_M12",
    "TIMEFRAME_M15",
    "TIMEFRAME_M20",
    "TIMEFRAME_M30",
    "TIMEFRAME_H1",
    "TIMEFRAME_H2",
    "TIMEFRAME_H4",
    "TIMEFRAME_H3",
    "TIMEFRAME_H6",
    "TIMEFRAME_H8",
    "TIMEFRAME_H12",
    "TIMEFRAME_D1",
    "TIMEFRAME_W1",
    "TIMEFRAME_MN1",
    "COPY_TICKS_ALL",
    "COPY_TICKS_INFO",
    "COPY_TICKS_TRADE",
    "TICK_FLAG_BID",
    "TICK_FLAG_ASK",
    "TICK_FLAG_LAST",
    "TICK_FLAG_VOLUME",
    "TICK_FLAG_BUY",
    "TICK_FLAG_SELL",
    "POSITION_TYPE_BUY",
    "POSITION_TYPE_SELL",
    "POSITION_REASON_CLIENT",
    "POSITION_REASON_MOBILE",
    "POSITION_REASON_WEB",
    "POSITION_REASON_EXPERT",
    "ORDER_TYPE_BUY",
    "ORDER_TYPE_SELL",
    "ORDER_TYPE_BUY_LIMIT",
    "ORDER_TYPE_SELL_LIMIT",
    "ORDER_TYPE_BUY_STOP",
    "ORDER_TYPE_SELL_STOP",
    "ORDER_TYPE_BUY_STOP_LIMIT",
    "ORDER_TYPE_SELL_STOP_LIMIT",
    "ORDER_TYPE_CLOSE_BY",
    "ORDER_STATE_STARTED",
    "ORDER_STATE_PLACED",
    "ORDER_STATE_CANCELED",
    "ORDER_STATE_PARTIAL",
    "ORDER_STATE_FILLED",
    "ORDER_STATE_REJECTED",
    "ORDER_STATE_EXPIRED",
    "ORDER_STATE_REQUEST_ADD",
    "ORDER_STATE_REQUEST_MODIFY",
    "ORDER_STATE_REQUEST_CANCEL",
    "ORDER_FILLING_FOK",
    "ORDER_FILLING_IOC",
    "ORDER_FILLING_RETURN",
    "ORDER_FILLING_BOC",
    "ORDER_TIME_GTC",
    "ORDER_TIME_DAY",
    "ORDER_TIME_SPECIFIED",
    "ORDER_TIME_SPECIFIED_DAY",
    "ORDER_REASON_CLIENT",
    "ORDER_REASON_MOBILE",
    "ORDER_REASON_WEB",
    "ORDER_REASON_EXPERT",
    "ORDER_REASON_SL",
    "ORDER_REASON_TP",
    "ORDER_REASON_SO",
    "DEAL_TYPE_BUY",
    "DEAL_TYPE_SELL",
    "DEAL_TYPE_BALANCE",
    "DEAL_TYPE_CREDIT",
    "DEAL_TYPE_CHARGE",
    "DEAL_TYPE_CORRECTION",
    "DEAL_TYPE_BONUS",
    "DEAL_TYPE_COMMISSION",
    "DEAL_TYPE_COMMISSION_DAILY",
    "DEAL_TYPE_COMMISSION_MONTHLY",
    "DEAL_TYPE_COMMISSION_AGENT_DAILY",
    "DEAL_TYPE_COMMISSION_AGENT_MONTHLY",
    "DEAL_TYPE_INTEREST",
    "DEAL_TYPE_BUY_CANCELED",
    "DEAL_TYPE_SELL_CANCELED",
    "DEAL_DIVIDEND",
    "DEAL_DIVIDEND_FRANKED",
    "DEAL_TAX",
    "DEAL_ENTRY_IN",
    "DEAL_ENTRY_OUT",
    "DEAL_ENTRY_INOUT",
    "DEAL_ENTRY_OUT_BY",
    "DEAL_REASON_CLIENT",
    "DEAL_REASON_MOBILE",
    "DEAL_REASON_WEB",
    "DEAL_REASON_EXPERT",
    "DEAL_REASON_SL",
    "DEAL_REASON_TP",
    "DEAL_REASON_SO",
    "DEAL_REASON_ROLLOVER",
    "DEAL_REASON_VMARGIN",
    "DEAL_REASON_SPLIT",
    "TRADE_ACTION_DEAL",
    "TRADE_ACTION_PENDING",
    "TRADE_ACTION_SLTP",
    "TRADE_ACTION_MODIFY",
    "TRADE_ACTION_REMOVE",
    "TRADE_ACTION_CLOSE_BY",
    "SYMBOL_CHART_MODE_BID",
    "SYMBOL_CHART_MODE_LAST",
    "SYMBOL_CALC_MODE_FOREX",
    "SYMBOL_CALC_MODE_FUTURES",
    "SYMBOL_CALC_MODE_CFD",
    "SYMBOL_CALC_MODE_CFDINDEX",
    "SYMBOL_CALC_MODE_CFDLEVERAGE",
    "SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE",
    "SYMBOL_CALC_MODE_EXCH_STOCKS",
    "SYMBOL_CALC_MODE_EXCH_FUTURES",
    "SYMBOL_CALC_MODE_EXCH_OPTIONS",
    "SYMBOL_CALC_MODE_EXCH_OPTIONS_MARGIN",
    "SYMBOL_CALC_MODE_EXCH_BONDS",
    "SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX",
    "SYMBOL_CALC_MODE_EXCH_BONDS_MOEX",
    "SYMBOL_CALC_MODE_SERV_COLLATERAL",
    "SYMBOL_TRADE_MODE_DISABLED",
    "SYMBOL_TRADE_MODE_LONGONLY",
    "SYMBOL_TRADE_MODE_SHORTONLY",
    "SYMBOL_TRADE_MODE_CLOSEONLY",
    "SYMBOL_TRADE_MODE_FULL",
    "SYMBOL_TRADE_EXECUTION_REQUEST",
    "SYMBOL_TRADE_EXECUTION_INSTANT",
    "SYMBOL_TRADE_EXECUTION_MARKET",
    "SYMBOL_TRADE_EXECUTION_EXCHANGE",
    "SYMBOL_SWAP_MODE_DISABLED",
    "SYMBOL_SWAP_MODE_POINTS",
    "SYMBOL_SWAP_MODE_CURRENCY_SYMBOL",
    "SYMBOL_SWAP_MODE_CURRENCY_MARGIN",
    "SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT",
    "SYMBOL_SWAP_MODE_INTEREST_CURRENT",
    "SYMBOL_SWAP_MODE_INTEREST_OPEN",
    "SYMBOL_SWAP_MODE_REOPEN_CURRENT",
    "SYMBOL_SWAP_MODE_REOPEN_BID",
    "DAY_OF_WEEK_SUNDAY",
    "DAY_OF_WEEK_MONDAY",
    "DAY_OF_WEEK_TUESDAY",
    "DAY_OF_WEEK_WEDNESDAY",
    "DAY_OF_WEEK_THURSDAY",
    "DAY_OF_WEEK_FRIDAY",
    "DAY_OF_WEEK_SATURDAY",
    "SYMBOL_ORDERS_GTC",
    "SYMBOL_ORDERS_DAILY",
    "SYMBOL_ORDERS_DAILY_NO_STOPS",
    "SYMBOL_OPTION_RIGHT_CALL",
    "SYMBOL_OPTION_RIGHT_PUT",
    "SYMBOL_OPTION_MODE_EUROPEAN",
    "SYMBOL_OPTION_MODE_AMERICAN",
    "ACCOUNT_TRADE_MODE_DEMO",
    "ACCOUNT_TRADE_MODE_CONTEST",
    "ACCOUNT_TRADE_MODE_REAL",
    "ACCOUNT_STOPOUT_MODE_PERCENT",
    "ACCOUNT_STOPOUT_MODE_MONEY",
    "ACCOUNT_MARGIN_MODE_RETAIL_NETTING",
    "ACCOUNT_MARGIN_MODE_EXCHANGE",
    "ACCOUNT_MARGIN_MODE_RETAIL_HEDGING",
    "BOOK_TYPE_SELL",
    "BOOK_TYPE_BUY",
    "BOOK_TYPE_SELL_MARKET",
    "BOOK_TYPE_BUY_MARKET",
    "TRADE_RETCODE_REQUOTE",
    "TRADE_RETCODE_REJECT",
    "TRADE_RETCODE_CANCEL",
    "TRADE_RETCODE_PLACED",
    "TRADE_RETCODE_DONE",
    "TRADE_RETCODE_DONE_PARTIAL",
    "TRADE_RETCODE_ERROR",
    "TRADE_RETCODE_TIMEOUT",
    "TRADE_RETCODE_INVALID",
    "TRADE_RETCODE_INVALID_VOLUME",
    "TRADE_RETCODE_INVALID_PRICE",
    "TRADE_RETCODE_INVALID_STOPS",
    "TRADE_RETCODE_TRADE_DISABLED",
    "TRADE_RETCODE_MARKET_CLOSED",
    "TRADE_RETCODE_NO_MONEY",
    "TRADE_RETCODE_PRICE_CHANGED",
    "TRADE_RETCODE_PRICE_OFF",
    "TRADE_RETCODE_INVALID_EXPIRATION",
    "TRADE_RETCODE_ORDER_CHANGED",
    "TRADE_RETCODE_TOO_MANY_REQUESTS",
    "TRADE_RETCODE_NO_CHANGES",
    "TRADE_RETCODE_SERVER_DISABLES_AT",
    "TRADE_RETCODE_CLIENT_DISABLES_AT",
    "TRADE_RETCODE_LOCKED",
    "TRADE_RETCODE_FROZEN",
    "TRADE_RETCODE_INVALID_FILL",
    "TRADE_RETCODE_CONNECTION",
    "TRADE_RETCODE_ONLY_REAL",
    "TRADE_RETCODE_LIMIT_ORDERS",
    "TRADE_RETCODE_LIMIT_VOLUME",
    "TRADE_RETCODE_INVALID_ORDER",
    "TRADE_RETCODE_POSITION_CLOSED",
    "TRADE_RETCODE_INVALID_CLOSE_VOLUME",
    "TRADE_RETCODE_CLOSE_ORDER_EXIST",
    "TRADE_RETCODE_LIMIT_POSITIONS",
    "TRADE_RETCODE_REJECT_CANCEL",
    "TRADE_RETCODE_LONG_ONLY",
    "TRADE_RETCODE_SHORT_ONLY",
    "TRADE_RETCODE_CLOSE_ONLY",
    "TRADE_RETCODE_FIFO_CLOSE",
    "RES_S_OK",
    "RES_E_FAIL",
    "RES_E_INVALID_PARAMS",
    "RES_E_NO_MEMORY",
    "RES_E_NOT_FOUND",
    "RES_E_INVALID_VERSION",
    "RES_E_AUTH_FAILED",
    "RES_E_UNSUPPORTED",
    "RES_E_AUTO_TRADING_DISABLED",
    "RES_E_INTERNAL_FAIL",
    "RES_E_INTERNAL_FAIL_SEND",
    "RES_E_INTERNAL_FAIL_RECEIVE",
    "RES_E_INTERNAL_FAIL_INIT",
    "RES_E_INTERNAL_FAIL_CONNECT",
    "RES_E_INTERNAL_FAIL_TIMEOUT",
)
core_mt5_functions = (
    "initialize",
    "shutdown",
    "login",
    "version",
    "terminal_info",
    "account_info",
    "copy_ticks_from",
    "copy_ticks_range",
    "copy_rates_from",
    "copy_rates_from_pos",
    "copy_rates_range",
    "positions_total",
    "positions_get",
    "orders_total",
    "orders_get",
    "history_orders_total",
    "history_orders_get",
    "history_deals_total",
    "history_deals_get",
    "order_check",
    "order_send",
    "order_calc_margin",
    "order_calc_profit",
    "symbol_info",
    "symbol_info_tick",
    "symbol_select",
    "symbols_total",
    "symbols_get",
    "market_book_add",
    "market_book_release",
    "market_book_get",
    "last_error",
)
types = (
    "TradePosition",
    "TradeOrder",
    "TradeDeal",
    "TradeRequest",
    "OrderSendResult",
    "OrderCheckResult",
    "Tick",
    "TerminalInfo",
    "SymbolInfo",
    "AccountInfo",
    "BookInfo",
)


class BaseMeta(type):
    def __new__(mcs, cls_name, bases, cls_dict):
        defaults: dict = getattr(MetaTrader5, "__dict__", {})
        callables = {f"_{key}": value for key in core_mt5_functions if (value := defaults.get(key, None)) is not None}
        consts = {key: value for key in constants if (value := defaults.get(key, None)) is not None}
        types_ = {key: value for key in types if (value := defaults.get(key, None)) is not None}
        cls_dict |= callables
        cls_dict |= consts
        cls_dict |= types_
        return super().__new__(mcs, cls_name, bases, cls_dict)


class MetaCore(metaclass=BaseMeta):
    TIMEFRAME_M1: int
    TIMEFRAME_M2: int
    TIMEFRAME_M3: int
    TIMEFRAME_M4: int
    TIMEFRAME_M5: int
    TIMEFRAME_M6: int
    TIMEFRAME_M10: int
    TIMEFRAME_M12: int
    TIMEFRAME_M15: int
    TIMEFRAME_M20: int
    TIMEFRAME_M30: int
    TIMEFRAME_H1: int
    TIMEFRAME_H2: int
    TIMEFRAME_H4: int
    TIMEFRAME_H3: int
    TIMEFRAME_H6: int
    TIMEFRAME_H8: int
    TIMEFRAME_H12: int
    TIMEFRAME_D1: int
    TIMEFRAME_W1: int
    TIMEFRAME_MN1: int
    COPY_TICKS_ALL: int
    COPY_TICKS_INFO: int
    COPY_TICKS_TRADE: int
    TICK_FLAG_BID: int
    TICK_FLAG_ASK: int
    TICK_FLAG_LAST: int
    TICK_FLAG_VOLUME: int
    TICK_FLAG_BUY: int
    TICK_FLAG_SELL: int
    POSITION_TYPE_BUY: int
    POSITION_TYPE_SELL: int
    POSITION_REASON_CLIENT: int
    POSITION_REASON_MOBILE: int
    POSITION_REASON_WEB: int
    POSITION_REASON_EXPERT: int
    ORDER_TYPE_BUY: int
    ORDER_TYPE_SELL: int
    ORDER_TYPE_BUY_LIMIT: int
    ORDER_TYPE_SELL_LIMIT: int
    ORDER_TYPE_BUY_STOP: int
    ORDER_TYPE_SELL_STOP: int
    ORDER_TYPE_BUY_STOP_LIMIT: int
    ORDER_TYPE_SELL_STOP_LIMIT: int
    ORDER_TYPE_CLOSE_BY: int
    ORDER_STATE_STARTED: int
    ORDER_STATE_PLACED: int
    ORDER_STATE_CANCELED: int
    ORDER_STATE_PARTIAL: int
    ORDER_STATE_FILLED: int
    ORDER_STATE_REJECTED: int
    ORDER_STATE_EXPIRED: int
    ORDER_STATE_REQUEST_ADD: int
    ORDER_STATE_REQUEST_MODIFY: int
    ORDER_STATE_REQUEST_CANCEL: int
    ORDER_FILLING_FOK: int
    ORDER_FILLING_IOC: int
    ORDER_FILLING_RETURN: int
    ORDER_FILLING_BOC: int
    ORDER_TIME_GTC: int
    ORDER_TIME_DAY: int
    ORDER_TIME_SPECIFIED: int
    ORDER_TIME_SPECIFIED_DAY: int
    ORDER_REASON_CLIENT: int
    ORDER_REASON_MOBILE: int
    ORDER_REASON_WEB: int
    ORDER_REASON_EXPERT: int
    ORDER_REASON_SL: int
    ORDER_REASON_TP: int
    ORDER_REASON_SO: int
    DEAL_TYPE_BUY: int
    DEAL_TYPE_SELL: int
    DEAL_TYPE_BALANCE: int
    DEAL_TYPE_CREDIT: int
    DEAL_TYPE_CHARGE: int
    DEAL_TYPE_CORRECTION: int
    DEAL_TYPE_BONUS: int
    DEAL_TYPE_COMMISSION: int
    DEAL_TYPE_COMMISSION_DAILY: int
    DEAL_TYPE_COMMISSION_MONTHLY: int
    DEAL_TYPE_COMMISSION_AGENT_DAILY: int
    DEAL_TYPE_COMMISSION_AGENT_MONTHLY: int
    DEAL_TYPE_INTEREST: int
    DEAL_TYPE_BUY_CANCELED: int
    DEAL_TYPE_SELL_CANCELED: int
    DEAL_DIVIDEND: int
    DEAL_DIVIDEND_FRANKED: int
    DEAL_TAX: int
    DEAL_ENTRY_IN: int
    DEAL_ENTRY_OUT: int
    DEAL_ENTRY_INOUT: int
    DEAL_ENTRY_OUT_BY: int
    DEAL_REASON_CLIENT: int
    DEAL_REASON_MOBILE: int
    DEAL_REASON_WEB: int
    DEAL_REASON_EXPERT: int
    DEAL_REASON_SL: int
    DEAL_REASON_TP: int
    DEAL_REASON_SO: int
    DEAL_REASON_ROLLOVER: int
    DEAL_REASON_VMARGIN: int
    DEAL_REASON_SPLIT: int
    TRADE_ACTION_DEAL: int
    TRADE_ACTION_PENDING: int
    TRADE_ACTION_SLTP: int
    TRADE_ACTION_MODIFY: int
    TRADE_ACTION_REMOVE: int
    TRADE_ACTION_CLOSE_BY: int
    SYMBOL_CHART_MODE_BID: int
    SYMBOL_CHART_MODE_LAST: int
    SYMBOL_CALC_MODE_FOREX: int
    SYMBOL_CALC_MODE_FUTURES: int
    SYMBOL_CALC_MODE_CFD: int
    SYMBOL_CALC_MODE_CFDINDEX: int
    SYMBOL_CALC_MODE_CFDLEVERAGE: int
    SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE: int
    SYMBOL_CALC_MODE_EXCH_STOCKS: int
    SYMBOL_CALC_MODE_EXCH_FUTURES: int
    SYMBOL_CALC_MODE_EXCH_OPTIONS: int
    SYMBOL_CALC_MODE_EXCH_OPTIONS_MARGIN: int
    SYMBOL_CALC_MODE_EXCH_BONDS: int
    SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX: int
    SYMBOL_CALC_MODE_EXCH_BONDS_MOEX: int
    SYMBOL_CALC_MODE_SERV_COLLATERAL: int
    SYMBOL_TRADE_MODE_DISABLED: int
    SYMBOL_TRADE_MODE_LONGONLY: int
    SYMBOL_TRADE_MODE_SHORTONLY: int
    SYMBOL_TRADE_MODE_CLOSEONLY: int
    SYMBOL_TRADE_MODE_FULL: int
    SYMBOL_TRADE_EXECUTION_REQUEST: int
    SYMBOL_TRADE_EXECUTION_INSTANT: int
    SYMBOL_TRADE_EXECUTION_MARKET: int
    SYMBOL_TRADE_EXECUTION_EXCHANGE: int
    SYMBOL_SWAP_MODE_DISABLED: int
    SYMBOL_SWAP_MODE_POINTS: int
    SYMBOL_SWAP_MODE_CURRENCY_SYMBOL: int
    SYMBOL_SWAP_MODE_CURRENCY_MARGIN: int
    SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT: int
    SYMBOL_SWAP_MODE_INTEREST_CURRENT: int
    SYMBOL_SWAP_MODE_INTEREST_OPEN: int
    SYMBOL_SWAP_MODE_REOPEN_CURRENT: int
    SYMBOL_SWAP_MODE_REOPEN_BID: int
    DAY_OF_WEEK_SUNDAY: int
    DAY_OF_WEEK_MONDAY: int
    DAY_OF_WEEK_TUESDAY: int
    DAY_OF_WEEK_WEDNESDAY: int
    DAY_OF_WEEK_THURSDAY: int
    DAY_OF_WEEK_FRIDAY: int
    DAY_OF_WEEK_SATURDAY: int
    SYMBOL_ORDERS_GTC: int
    SYMBOL_ORDERS_DAILY: int
    SYMBOL_ORDERS_DAILY_NO_STOPS: int
    SYMBOL_OPTION_RIGHT_CALL: int
    SYMBOL_OPTION_RIGHT_PUT: int
    SYMBOL_OPTION_MODE_EUROPEAN: int
    SYMBOL_OPTION_MODE_AMERICAN: int
    ACCOUNT_TRADE_MODE_DEMO: int
    ACCOUNT_TRADE_MODE_CONTEST: int
    ACCOUNT_TRADE_MODE_REAL: int
    ACCOUNT_STOPOUT_MODE_PERCENT: int
    ACCOUNT_STOPOUT_MODE_MONEY: int
    ACCOUNT_MARGIN_MODE_RETAIL_NETTING: int
    ACCOUNT_MARGIN_MODE_EXCHANGE: int
    ACCOUNT_MARGIN_MODE_RETAIL_HEDGING: int
    BOOK_TYPE_SELL: int
    BOOK_TYPE_BUY: int
    BOOK_TYPE_SELL_MARKET: int
    BOOK_TYPE_BUY_MARKET: int
    TRADE_RETCODE_REQUOTE: int
    TRADE_RETCODE_REJECT: int
    TRADE_RETCODE_CANCEL: int
    TRADE_RETCODE_PLACED: int
    TRADE_RETCODE_DONE: int
    TRADE_RETCODE_DONE_PARTIAL: int
    TRADE_RETCODE_ERROR: int
    TRADE_RETCODE_TIMEOUT: int
    TRADE_RETCODE_INVALID: int
    TRADE_RETCODE_INVALID_VOLUME: int
    TRADE_RETCODE_INVALID_PRICE: int
    TRADE_RETCODE_INVALID_STOPS: int
    TRADE_RETCODE_TRADE_DISABLED: int
    TRADE_RETCODE_MARKET_CLOSED: int
    TRADE_RETCODE_NO_MONEY: int
    TRADE_RETCODE_PRICE_CHANGED: int
    TRADE_RETCODE_PRICE_OFF: int
    TRADE_RETCODE_INVALID_EXPIRATION: int
    TRADE_RETCODE_ORDER_CHANGED: int
    TRADE_RETCODE_TOO_MANY_REQUESTS: int
    TRADE_RETCODE_NO_CHANGES: int
    TRADE_RETCODE_SERVER_DISABLES_AT: int
    TRADE_RETCODE_CLIENT_DISABLES_AT: int
    TRADE_RETCODE_LOCKED: int
    TRADE_RETCODE_FROZEN: int
    TRADE_RETCODE_INVALID_FILL: int
    TRADE_RETCODE_CONNECTION: int
    TRADE_RETCODE_ONLY_REAL: int
    TRADE_RETCODE_LIMIT_ORDERS: int
    TRADE_RETCODE_LIMIT_VOLUME: int
    TRADE_RETCODE_INVALID_ORDER: int
    TRADE_RETCODE_POSITION_CLOSED: int
    TRADE_RETCODE_INVALID_CLOSE_VOLUME: int
    TRADE_RETCODE_CLOSE_ORDER_EXIST: int
    TRADE_RETCODE_LIMIT_POSITIONS: int
    TRADE_RETCODE_REJECT_CANCEL: int
    TRADE_RETCODE_LONG_ONLY: int
    TRADE_RETCODE_SHORT_ONLY: int
    TRADE_RETCODE_CLOSE_ONLY: int
    TRADE_RETCODE_FIFO_CLOSE: int
    RES_S_OK: int
    RES_E_FAIL: int
    RES_E_INVALID_PARAMS: int
    RES_E_NO_MEMORY: int
    RES_E_NOT_FOUND: int
    RES_E_INVALID_VERSION: int
    RES_E_AUTH_FAILED: int
    RES_E_UNSUPPORTED: int
    RES_E_AUTO_TRADING_DISABLED: int
    RES_E_INTERNAL_FAIL: int
    RES_E_INTERNAL_FAIL_SEND: int
    RES_E_INTERNAL_FAIL_RECEIVE: int
    RES_E_INTERNAL_FAIL_INIT: int
    RES_E_INTERNAL_FAIL_CONNECT: int
    RES_E_INTERNAL_FAIL_TIMEOUT: int
    _account_info: Callable
    _copy_rates_from: Callable
    _copy_rates_from_pos: Callable
    _copy_rates_range: Callable
    _copy_ticks_from: Callable
    _copy_ticks_range: Callable
    _history_deals_get: Callable
    _history_deals_total: Callable
    _history_orders_get: Callable
    _history_orders_total: Callable
    _initialize: Callable
    _last_error: Callable
    _login: Callable
    _market_book_add: Callable
    _market_book_get: Callable
    _market_book_release: Callable
    _order_calc_margin: Callable
    _order_calc_profit: Callable
    _order_check: Callable
    _order_send: Callable
    _orders_get: Callable
    _orders_total: Callable
    _positions_get: Callable
    _positions_total: Callable
    _shutdown: Callable
    _symbol_info: Callable
    _symbol_info_tick: Callable
    _symbol_select: Callable
    _symbols_get: Callable
    _symbols_total: Callable
    _terminal_info: Callable
    _version: Callable
    config: Config
    AccountInfo: AccountInfo
    TradePosition: TradePosition
    TradeOrder: TradeOrder
    TradeDeal: TradeDeal
    TradeRequest: TradeRequest
    OrderSendResult: OrderSendResult
    OrderCheckResult: OrderCheckResult
    Tick: Tick
    TerminalInfo: TerminalInfo
    SymbolInfo: SymbolInfo
    BookInfo: BookInfo
