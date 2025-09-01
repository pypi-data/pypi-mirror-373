import datetime
import warnings

import pandas as pd
from rqdatac.services.stock_status import get_shares
from rqdatac.services.get_price import get_price
from rqdatac.services.calendar import is_trading_date, get_previous_trading_date
from rqdatac.services.live import current_snapshot
from rqdatac.validators import ensure_order_book_ids
from rqdatac.decorators import export_as_api


@export_as_api
def current_freefloat_turnover(order_book_ids):
    """
    股票当日累计自由流通换手率, 即当日累计成交金额/自由流通市值（盘中实时）

    :param order_book_ids: 股票代码或代码列表, 如'000001.XSHE'

    :return: pd.Series or None
    """
    today = datetime.date.today()
    if not is_trading_date(today):
        warnings.warn('today is not a trading day!')
        return None

    order_book_ids = ensure_order_book_ids(order_book_ids, type='CS')
    shares = get_shares(order_book_ids, today, today, fields='free_circulation')
    if shares is None:
        return None
    shares = shares.droplevel(1)['free_circulation']

    snapshots = current_snapshot(order_book_ids)
    if len(order_book_ids) == 1:
        snapshots = [snapshots]
    t_shares = pd.Series({(t.order_book_id, t.datetime): t.total_turnover/t.last for t in snapshots})
    t_shares.index.names = ['order_book_id', 'datetime']
    turnover = t_shares / shares
    return turnover


@export_as_api
def get_live_minute_price_change_rate(order_book_ids):
    """
    获取当日分钟累积收益率

    :param order_book_ids: 股票代码或代码列表, 如'000001.XSHE'

    :return: pd.DataFrame or None
    """
    today = datetime.date.today()
    if not is_trading_date(today):
        warnings.warn('today is not a trading day!')
        return None

    order_book_ids = ensure_order_book_ids(order_book_ids)
    close = get_price(order_book_ids, today, today, '1m', fields='close', adjust_type='none')
    if close is None:
        warnings.warn('today minute data is not ready')
        return

    close = close['close'].unstack('order_book_id')
    snapshots = current_snapshot(order_book_ids)
    if len(order_book_ids) == 1:
        snapshots = [snapshots]
    prev_close = pd.Series({t.order_book_id: t.prev_close for t in snapshots})
    minute_return = close / prev_close - 1
    return minute_return
