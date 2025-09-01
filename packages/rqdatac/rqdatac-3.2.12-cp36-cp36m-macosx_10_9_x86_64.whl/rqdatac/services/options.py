# -*- coding: utf-8 -*-
import warnings
import datetime

import numpy as np
import pandas as pd

from rqdatac.validators import (
    check_items_in_container,
    ensure_date_int,
    ensure_order_book_ids,
    ensure_string,
    ensure_string_in,
    ensure_date_range,
    ensure_list_of_string
)

from rqdatac.client import get_client
from rqdatac.decorators import export_as_api
from rqdatac.services.calendar import current_trading_date, get_trading_dates
from rqdatac.services.basic import all_instruments, instruments
from rqdatac.services.get_price import get_price
from rqdatac.utils import is_panel_removed, convert_bar_to_multi_df, int14_to_datetime_v, date_to_int8, int8_to_datetime
from rqdatac.rqdatah_helper import rqdatah_serialize, http_conv_list_to_csv
from rqdatac.share.errors import PermissionDenied, MarketNotSupportError, NoSuchService


VALID_GREEKS_FIELDS = ['iv', 'delta', 'gamma', 'vega', 'theta', 'rho']


def get_greeks_min(order_book_ids, start_date, end_date, fields, model, market):
    live_date = current_trading_date()
    if start_date > live_date:
        return None

    data = get_client().execute('options.get_greeks_min', order_book_ids, start_date, end_date, fields, model,
                                market=market)
    data = [(obid, {k: np.frombuffer(*v) for k, v in d.items()}) for obid, d in data]
    df = convert_bar_to_multi_df(data, 'datetime', fields, int14_to_datetime_v)

    if end_date < live_date:
        return df

    live_date_str = '%d-%02d-%02d' % (live_date // 10000, live_date % 10000 // 100, live_date % 100)
    live_obs = set(
        ins.order_book_id for ins in instruments(order_book_ids)
        if ins.de_listed_date == '0000-00-00' or ins.de_listed_date >= live_date_str
    )
    if df is not None:
        idx = df.index
        for ob in idx.levels[0]:
            if ob not in live_obs:
                continue
            loc = idx.get_loc(ob)
            if date_to_int8(idx[loc.stop - 1][-1]) == live_date:
                live_obs.remove(ob)
    if not live_obs:
        return df

    live_df = None
    if end_date >= live_date:
        try:
            live_data = get_client().execute('options.get_live_greeks_min', list(live_obs), model, market)
            live_dfs = [pd.DataFrame(d) for d in live_data if d]
            if live_dfs:
                live_df = pd.concat(live_dfs)
                live_df['datetime'] = int14_to_datetime_v(live_df['datetime'])
                live_df.set_index(['order_book_id', 'datetime'], inplace=True)
            if live_df is None:
                return df
        except (PermissionDenied, MarketNotSupportError, NoSuchService) as e:
            warnings.warn("Error when get realtime minbar option greeks: {}".format(e))
    if df is None:
        return live_df
    df = pd.concat([df, live_df])
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace='options')
def get_greeks(order_book_ids, start_date=None, end_date=None, fields=None, model='implied_forward', price_type='close',
               frequency='1d', market="cn"):
    """获取指定股票期权的隐含波动率iv， 以及5个希腊字母数值(delta, gamma, bega, theta, rho)
    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_date: 开始日期, 必要参数
    :param end_date: 结束日期；默认为今天
    :param fields: str或list类型. 默认为None, 返回所有fields.
    :param model: str类型， last: 代表用每日close价格， implied_forward 代表用隐含风险收益率计算
    :param price_type: 'close' or 'settlement'
    :param frequency: '1d' or '1m', 如果为'1m'，则price_type必须为'close'
    :param market: 默认值为"cn"
    """

    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    check_items_in_container(model, ['implied_forward', 'last'], 'model')
    ensure_string_in(price_type, ('close', 'settlement'), 'price_type')
    ensure_string_in(frequency, ('1d', '1m'), 'frequency')
    if frequency == '1m' and price_type != 'close':
        raise ValueError('1m frequency only support price_type=close!')
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    else:
        raise ValueError('start_date is expected')
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    else:
        end_date = ensure_date_int(datetime.datetime.now().date())
    if end_date < start_date:
        raise ValueError("invalid date range: [{!r}, {!r}]".format(start_date, end_date))

    if fields is None:
        fields = VALID_GREEKS_FIELDS
    else:
        fields = ensure_list_of_string(fields, 'fields')
        check_items_in_container(fields, VALID_GREEKS_FIELDS, 'Greeks')

    if frequency == '1m':
        return get_greeks_min(order_book_ids, start_date, end_date, fields, model, market)

    data = get_client().execute("options.get_greeks", order_book_ids, start_date, end_date, fields, model, price_type,
                                market=market)
    if not data:
        return None

    df = pd.DataFrame(data)
    date_field = 'trading_date'
    df.set_index(["order_book_id", date_field], inplace=True)
    df.sort_index(inplace=True)
    return df[fields]


SPECIAL_UNDERLYING_SYMBOL = ("510050.XSHG", "510300.XSHG", "159919.XSHE")


@export_as_api(namespace='options')
@rqdatah_serialize(converter=http_conv_list_to_csv, name='order_book_id')
def get_contracts(
        underlying,
        option_type=None,
        maturity=None,
        strike=None,
        trading_date=None
):
    """返回符合条件的期权

    :param underlying: 标的合约, 可以填写'M'代表期货品种的字母；也可填写'M1901'这种具体 order_book_id
    :param option_type: 期权类型, 'C'代表认购期权, 'P'代表认沽期权合约, 默认返回全部
    :param maturity: 到期月份, 如'1811'代表期权18年11月到期, 默认返回全部到期月份
    :param strike: 行权价, 向左靠档, 默认返回全部行权价
    :param trading_date: 查询日期, 默认返回当前全部

    :returns
        返回order_book_id list；如果无符合条件期权则返回空list[]
    """
    underlying = ensure_string(underlying, "underlying").upper()
    instruments_df = all_instruments(type='Option')
    underlying_symbols = instruments_df.underlying_symbol.unique()
    underlying_order_book_ids = instruments_df.underlying_order_book_id.unique()
    instruments_df = all_instruments(type='Option', date=trading_date)
    if underlying in underlying_symbols:
        instruments_df = instruments_df[instruments_df.underlying_symbol == underlying]
    elif underlying in underlying_order_book_ids:
        instruments_df = instruments_df[instruments_df.underlying_order_book_id == underlying]
    else:
        raise ValueError("Unknown underlying")
    if instruments_df.empty:
        return []

    if option_type is not None:
        option_type = ensure_string(option_type, "option_type").upper()
        ensure_string_in(option_type, {'P', 'C'}, "option_type")
        instruments_df = instruments_df[instruments_df.option_type == option_type]

    if maturity is not None:
        maturity = int(maturity)
        month = maturity % 100
        if month not in range(1, 13):
            raise ValueError("Unknown month")
        year = maturity // 100 + 2000
        str_month = str(month)
        if len(str_month) == 1:
            str_month = '0' + str_month
        date_str = str(year) + '-' + str_month
        instruments_df = instruments_df[instruments_df.maturity_date.str.startswith(date_str)]
        if instruments_df.empty:
            return []

    if strike:
        if underlying in SPECIAL_UNDERLYING_SYMBOL and trading_date:
            order_book_ids = instruments_df.order_book_id.tolist()

            strikes = get_price(order_book_ids, start_date=trading_date, end_date=trading_date, fields='strike_price',
                                expect_df=is_panel_removed)
            if strikes is None:
                return []
            if is_panel_removed:
                strikes.reset_index(level=1, inplace=True, drop=True)
            else:
                strikes = strikes.T

            instruments_df.set_index(instruments_df.order_book_id, inplace=True)
            instruments_df['strike_price'] = strikes[strikes.columns[0]]
            instruments_df = instruments_df[instruments_df.strike_price.notnull()]
            if instruments_df.empty:
                return []

        l = []
        for date in instruments_df.maturity_date.unique():
            df = instruments_df[instruments_df.maturity_date == date]
            df = df[df.strike_price <= strike]
            if df.empty:
                continue
            df = df[df.strike_price.rank(method='min', ascending=False) == 1]
            l += df.order_book_id.tolist()
        return l

    return instruments_df.order_book_id.tolist()


VALID_CONTRACT_PROPERTY_FIELDS = ['product_name', 'symbol', 'contract_multiplier', 'strike_price']


def _get_multi_index(oids, end_date, listed, de_listed):
    mult = []
    tds = get_trading_dates('20150101', datetime.date.today())
    index = pd.to_datetime(tds)
    for oid in oids:
        if oid not in listed:
            continue
        s = str(listed[oid])
        e = str(min(end_date, de_listed[oid]))
        _start, _end = pd.Timestamp(s), pd.Timestamp(e)
        start_pos, end_pos = index.searchsorted(_start), index.searchsorted(_end)
        _index = index[start_pos:end_pos + 1]
        mult.extend([(oid, i) for i in _index])
    return pd.MultiIndex.from_tuples(mult, names=['order_book_id', 'trading_date'])


@export_as_api(namespace='options')
def get_contract_property(
        order_book_ids,
        start_date=None,
        end_date=None,
        fields=None,
        market='cn'
):
    """获取期权合约属性
    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_date: 开始日期, 必要参数
    :param end_date: 结束日期；默认为今天
    :param fields: str或list类型. 默认为None, 返回所有fields.
    :param market: 默认值为"cn", 可选：cn

    :returns
        返回DataFrame, 索引为 MultiIndex([order_book_id, trading_date])
    """
    order_book_ids = ensure_order_book_ids(order_book_ids, type='Option', market=market)
    listed_dates = {}
    de_listed_dates = {}
    _order_book_ids = []
    for oid in order_book_ids:
        i = instruments(oid)
        # 过滤order_book_ids，只取ETF期权
        # etf 期权的underlying_symbol都是有交易所后缀的
        if not i.underlying_symbol.endswith(("XSHE", "XSHG")):
            continue
        _order_book_ids.append(oid)
        listed_dates[oid] = int(i.listed_date.replace('-', ''))
        de_listed_dates[oid] = int(i.de_listed_date.replace('-', ''))
    order_book_ids = _order_book_ids

    end_date = datetime.date.today() if not end_date else end_date
    end_date = ensure_date_int(end_date)
    if start_date:
        start_date, end_date = ensure_date_range(start_date, end_date)
        # 如果指定start_date, 将退市的order_book_id过滤掉
        order_book_ids = [oid for oid in order_book_ids if start_date <= de_listed_dates[oid]]

    if fields is None:
        fields = VALID_CONTRACT_PROPERTY_FIELDS[:]
    else:
        if not isinstance(fields, list):
            fields = [fields]
        check_items_in_container(fields, VALID_CONTRACT_PROPERTY_FIELDS, 'Contract Property')
    # get data from server
    data = get_client().execute('options.get_contract_property', order_book_ids, fields)
    if not data:
        return
    df = pd.DataFrame(data)

    index = _get_multi_index(order_book_ids, end_date, listed_dates, de_listed_dates)
    df = df.set_index(['order_book_id', 'trading_date'])
    df = df.reindex(index).groupby("order_book_id").ffill()
    if start_date:
        msk = df.index.get_level_values('trading_date') >= pd.Timestamp(str(start_date))
        df = df[msk]
    return df.sort_index()


@export_as_api(namespace='options')
def get_dominant_month(
        underlying_symbol,
        start_date=None,
        end_date=None,
        rule=0,
        rank=1,
        market='cn'
):
    """获取期权主力月份
    :param underlying_symbol: str, 期权标的代码
    :param start_date: 开始日期, 默认为期权合约最早上市日期的后一交易日
    :param end_date: 结束日期；默认为今天
    :param rule: int, 选取主力月份的规则，默认为 0，主力月份不会切换为已做过主力的月份，可选：0, 1: 只考虑主力月份的选取规则
    :param rank: int, 选取主力合约或次主力合约，默认为 1，可选：1：主力月份, 2：次主力月份,
    :param market: 默认值为"cn", 可选：cn

    :returns
        返回 Series, Index 为日期, value 为主力月份
    """
    check_items_in_container(rule, [0, 1], 'rule')
    underlying_symbol = ensure_string(underlying_symbol, "underlying_symbol").upper()
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    else:
        contracts = get_contracts(underlying_symbol)
        ins = instruments(contracts)
        start_date = ensure_date_int(min([i.listed_date for i in ins]))
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    else:
        end_date = ensure_date_int(datetime.date.today())
    if end_date < start_date:
        raise ValueError("invalid date range: [{!r}, {!r}]".format(start_date, end_date))
    
    function_name = 'get_dominant_month' if rank == 1 else 'get_dominant_month_rank2'
    result = get_client().execute(f'options.{function_name}', underlying_symbol, start_date, end_date, rule, market=market)

    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index('date')
    return df.sort_index()['dominant']


@export_as_api(namespace='options')
def get_commission(underlying_symbols, market='cn'):
    """获取期权交易费用信息
    :param underlying_symbol: str, 期权标的代码
    :param market: 默认值为"cn", 可选：cn

    :returns
        返回 DataFrame, Index 为 underlying_symbol
    """
    underlying_symbol = ensure_list_of_string(underlying_symbols, "underlying_symbols")
    result = get_client().execute('options.get_commission', underlying_symbol, market=market)

    if not result:
        return

    return pd.DataFrame.from_records(result, index=["underlying_symbol"])


@export_as_api(namespace='options')
def get_atm_option(underlying_symbol, option_type='C', start_date=None, end_date=None):
    """
    获取日度的连续平值期权合约代码

    :param underlying_symbol: 标的合约, 例:'CU'
    :param option_type: 期权类型, 'C'代表认购期权, 'P'代表认沽期权合约, 默认C
    :param start_date: 开始日期, 默认为近三月
    :param end_date: 结束日期；默认为近三月
    :returns Series, Index 为日期, value 平值期权合约代码
    """
    underlying_symbol = ensure_string(underlying_symbol, "underlying_symbol").upper()
    option_type = ensure_string(option_type, "option_type").upper()
    ensure_string_in(option_type, {'P', 'C'}, "option_type")
    start_date, end_date = ensure_date_range(start_date, end_date)
    fields = ['underlying_symbol', 'listed_date', 'order_book_id', 'maturity_date', 'option_type',
              'underlying_order_book_id']

    instruments_df = all_instruments('Option')
    instruments_df = instruments_df[fields]
    instruments_df = instruments_df[(instruments_df.underlying_symbol == underlying_symbol) & (instruments_df.option_type == option_type)]
    instruments_df['maturity_date'] = pd.to_datetime(instruments_df['maturity_date'])
    instruments_df['listed_date'] = pd.to_datetime(instruments_df['listed_date'])

    dates = get_trading_dates(start_date, end_date)
    result = {}
    condidate_ids = {}
    underlying_ids_dict = {}
    for d in dates:
        d = pd.to_datetime(d)
        df = instruments_df.loc[(instruments_df['maturity_date'] > d) & (instruments_df['listed_date'] <= d)]
        if df.empty:
            continue
        min_diff = min(df['maturity_date'] - d)
        df = df.loc[df['maturity_date'] - d == min_diff]
        condidate_ids[d] = df['order_book_id'].tolist()
        underlying_ids_dict[d] = df['underlying_order_book_id'].tolist()

    ids = [order_book_id for order_book_ids in condidate_ids.values() for order_book_id in order_book_ids]
    ids = list(set(ids))
    underlying_ids = [underlying_id for underlying_ids in underlying_ids_dict.values() for underlying_id in underlying_ids]
    underlying_ids = list(set(underlying_ids))

    strike_px = get_price(ids, start_date, end_date, adjust_type='none', fields=['strike_price'])
    close_px = get_price(underlying_ids, start_date, end_date, adjust_type='none', fields=['close'])
    strike_px.reset_index(inplace=True)
    close_px.reset_index(inplace=True)

    instruments_df = instruments_df[instruments_df['order_book_id'].isin(ids)]

    merge_df = pd.merge(instruments_df, strike_px, on='order_book_id', suffixes=('', '_u'))
    merge_df = pd.merge(merge_df, close_px, left_on=('underlying_order_book_id', 'date'), right_on=('order_book_id', 'date'), suffixes=('', '_u'))

    merge_df.set_index(['order_book_id', 'date'], inplace=True)
    atm_option_df = abs(merge_df["close"] - merge_df["strike_price"])
    for d in dates:
        d = pd.to_datetime(d)
        if d not in condidate_ids or d not in atm_option_df.index.levels[1]:
            continue
        min_diff_index = atm_option_df.loc[(condidate_ids[d], d)].idxmin()
        result[d] = min_diff_index[0]
    return pd.Series(result)


OPTION_INDICATORS = ['VL_PCR', 'OI_PCR', 'AM_PCR', "skew"]


@export_as_api(namespace='options')
def get_indicators(underlying_symbols, maturity, start_date=None, end_date=None, fields=None, market='cn'):
    """
    获取期权指标
    :param underlying_symbol: 标的品种, 例: 'CU' 或 ['CU', 'AL']
    :param maturity: 期权合约到期月份, 例: '2503'
    :param start_date: 开始日期, 默认为近三月
    :param end_date: 结束日期；默认为近三月
    :param fields: 类型, 默认为None, 可选：'VL_PCR', 'OI_PCR', 'AM_PCR', 'skew'
    :returns Series
    """
    underlying_symbols = ensure_list_of_string(underlying_symbols, "underlying_symbols")
    if isinstance(maturity, int):
        maturity = str(maturity)
    maturity = ensure_string(maturity, "maturity")
    start_date, end_date = ensure_date_range(start_date, end_date)
    fields = ensure_list_of_string(fields) if fields is not None else OPTION_INDICATORS
    check_items_in_container(fields, OPTION_INDICATORS, "fields")
    result = get_client().execute('options.get_indicators', underlying_symbols, maturity, start_date, end_date, fields, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df['date'] = df['date'].map(int8_to_datetime)
    df.set_index(["underlying_symbol", "date"], inplace=True)
    df.sort_index(inplace=True)
    return df
