# -*- coding: utf-8 -*-
import six
import datetime
import warnings
import bisect

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from rqdatac.validators import (
    ensure_string,
    ensure_string_in,
    ensure_list_of_string,
    ensure_date_int,
    ensure_date_or_today_int,
    ensure_date_range,
    check_items_in_container,
    ensure_order_book_ids,
    ensure_instruments,
)
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api, ttl_cache
from rqdatac.utils import (
    int8_to_datetime,
    to_datetime,
    date_to_int8,
    to_date,
    int17_to_datetime_v,
    int14_to_datetime_v,
    int8_to_datetime_v,
    convert_bar_to_multi_df,
)
from rqdatac.services.calendar import current_trading_date, is_trading_date, get_next_trading_date, get_trading_dates, \
    get_previous_trading_date
from rqdatac.services.basic import instruments
from rqdatac.services import get_price


@export_as_api
def get_dominant_future(underlying_symbol, start_date=None, end_date=None, rule=0, rank=1, market="cn"):
    import warnings

    msg = "'get_dominant_future' is deprecated, please use 'futures.get_dominant' instead"
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return get_dominant(underlying_symbol, start_date, end_date, rule, rank, market)


@export_as_api(namespace='futures')
def get_dominant(underlying_symbol, start_date=None, end_date=None, rule=0, rank=1, market="cn"):
    """获取指定期货品种当日对应的主力合约

    :param underlying_symbol: 如'IF' 'IC'
    :param start_date: 如 '2015-01-07' (Default value = None)
    :param end_date: 如 '2015-01-08' (Default value = None)
    :param market:  (Default value = "cn")
    :param rule:  主力合约规则 (Default value = 0)
        0：在rule=1的规则上，增加约束(曾做过主力合约的合约，一旦被换下来后，不会再被选上)
        1：合约首次上市时，以当日收盘同品种持仓量最大者作为从第二个交易日开始的主力合约，当同品种其他合约持仓量在收盘后
           超过当前主力合约1.1倍时，从第二个交易日开始进行主力合约的切换。日内不会进行主力合约的切换
        2: 前一交易日持仓量与成交量均为最大的合约
    :param rank:  (Default value = 1):
        1: 主力合约
        2: 次主力合约
        3：次次主力合约
    :returns: pandas.Series
        返回参数指定的具体主力合约名称

    """
    if not isinstance(underlying_symbol, six.string_types):
        raise ValueError("invalid underlying_symbol: {}".format(underlying_symbol))

    check_items_in_container(rule, [0, 1, 2, 3], 'rule')
    check_items_in_container(rank, [1, 2, 3], 'order')

    underlying_symbol = underlying_symbol.upper()

    if start_date:
        start_date = ensure_date_int(start_date)

    if end_date:
        end_date = ensure_date_int(end_date)
    elif start_date:
        end_date = start_date

    result = get_client().execute(
        "futures.get_dominant_v2", underlying_symbol, start_date, end_date, rule, rank, market=market)

    if not result:
        return
    df = pd.DataFrame(result)
    df["date"] = df["date"].apply(int8_to_datetime)
    return df.set_index("date").sort_index()["dominant"]


@ttl_cache(3600)
def current_real_contract(ob, market):
    """获取指定期货品种当日对应的真实合约"""
    date = current_trading_date(market)
    r = get_dominant(ob, date, date, market=market)
    if isinstance(r, pd.Series) and r.size == 1:
        return r[0]
    return None


_FIELDS = [
    "margin_type",
    "long_margin_ratio",
    "short_margin_ratio",
    "commission_type",
    "open_commission_ratio",
    "close_commission_ratio",
    "close_commission_today_ratio",
]


@export_as_api
def future_commission_margin(order_book_ids=None, fields=None, hedge_flag="speculation"):
    import warnings

    msg = "'future_commission_margin' is deprecated, please use 'futures.get_commission_margin' instead"
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return get_commission_margin(order_book_ids, fields, hedge_flag)


@export_as_api(namespace='futures')
def get_commission_margin(order_book_ids=None, fields=None, hedge_flag="speculation"):
    """获取期货保证金和手续费数据

    :param order_book_ids: 期货合约, 支持 order_book_id 或 order_book_id list,
        若不指定则默认获取所有合约 (Default value = None)
    :param fields: str 或 list, 可选字段有： 'margin_type', 'long_margin_ratio', 'short_margin_ratio',
            'commission_type', 'open_commission_ratio', 'close_commission_ratio',
            'close_commission_today_ratio', 若不指定则默认获取所有字段 (Default value = None)
    :param hedge_flag: str, 账户对冲类型, 可选字段为: 'speculation', 'hedge',
            'arbitrage', 默认为'speculation', 目前仅支持'speculation' (Default value = "speculation")
    :returns: pandas.DataFrame

    """
    if order_book_ids:
        order_book_ids = ensure_list_of_string(order_book_ids)

    if fields is None:
        fields = _FIELDS
    else:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, _FIELDS, "fields")

    hedge_flag = ensure_string(hedge_flag, "hedge_flag")
    if hedge_flag not in ["speculation", "hedge", "arbitrage"]:
        raise ValueError("invalid hedge_flag: {}".format(hedge_flag))

    ret = get_client().execute("futures.get_commission_margin", order_book_ids, fields, hedge_flag)
    return pd.DataFrame(ret)


@export_as_api
def get_future_member_rank(order_book_id, trading_date=None, info_type='volume'):
    import warnings

    msg = "'get_future_member_rank' is deprecated, please use 'futures.get_member_rank' instead"
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
    return get_member_rank(order_book_id, trading_date, info_type)


@export_as_api(namespace='futures')
def get_member_rank(obj, trading_date=None, rank_by='volume', **kwargs):
    """获取指定日期最近的期货会员排名数据
    :param obj： 期货合约或品种代码
    :param trading_date: 日期
    :param rank_by: 排名依据字段
    :keyword start_date
    :keyword end_date
    :returns pandas.DataFrame or None
    """
    if not kwargs:
        trading_date = ensure_date_or_today_int(trading_date)
        ret = get_client().execute("futures.get_member_rank", obj, trading_date, rank_by)
    else:
        start_date = kwargs.pop("start_date", None)
        end_date = kwargs.pop("end_date", None)
        if kwargs:
            raise ValueError('unknown kwargs: {}'.format(kwargs))
        elif start_date and end_date:
            start_date, end_date = ensure_date_int(start_date), ensure_date_int(end_date)
            ret = get_client().execute("futures.get_member_rank_v2", obj, start_date, end_date, rank_by)
        else:
            raise ValueError('please ensure start_date and end_date exist')

    if not ret:
        return

    df = pd.DataFrame(ret).sort_values(by=['trading_date', 'rank'])
    df.set_index('trading_date', inplace=True)
    return df


@export_as_api(namespace="futures")
def get_warehouse_stocks(underlying_symbols, start_date=None, end_date=None, market="cn"):
    """获取时间区间内期货的注册仓单

    :param underlying_symbols: 期货品种, 支持列表查询
    :param start_date: 如'2015-01-01', 如果不填写则为去年的当日日期
    :param end_date: 如'2015-01-01', 如果不填写则为当日日期
    :param market: 市场, 默认为"cn"
    :return: pd.DataFrame

    """
    underlying_symbols = ensure_list_of_string(underlying_symbols, name="underlying_symbols")
    start_date, end_date = ensure_date_range(start_date, end_date, delta=relativedelta(years=1))

    # 有新老两种 symbol 时对传入的 underlying_symbols 需要对应成新的 symbol, 并对并行期结束后仍使用老的 symbol 予以警告
    multi_symbol_map = {'RO': 'OI', 'WS': 'WH', 'ER': 'RI', 'TC': 'ZC', 'ME': 'MA'}
    symbol_date_map = {'RO': 20130515, 'WS': 20130523, 'ER': 20130523, 'TC': 20160408, 'ME': 20150515}
    for symbol in set(underlying_symbols) & set(multi_symbol_map):
        date_line = symbol_date_map[symbol]
        if end_date > date_line:
            import warnings
            msg = 'You are using the old symbol: {}, however the new symbol: {} is available after {}.'.format(symbol,
                                                                                                               multi_symbol_map[
                                                                                                                   symbol],
                                                                                                               date_line)
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)

    # 对传入的 underlying_symbols 依照 multi_symbol_map 生成一个对照 DataFrame
    symbol_map_df = pd.DataFrame([(symbol, multi_symbol_map.get(symbol, symbol)) for symbol in set(underlying_symbols)],
                                 columns=['origin', 'new'])
    # 将 underlying_symbols 中 所有老的 symbol 对应为新的再去 mongo 查询
    underlying_symbols = list(symbol_map_df.new.unique())
    ret = get_client().execute("futures.get_warehouse_stocks", underlying_symbols, start_date, end_date, market=market)
    if not ret:
        return
    columns = ["date", "underlying_symbol", "on_warrant", "exchange", 'effective_forecast', 'warrant_units',
               'contract_multiplier', 'deliverable']
    df = pd.DataFrame(ret, columns=columns)

    df = df.merge(symbol_map_df, left_on='underlying_symbol', right_on='new')
    df.drop(['underlying_symbol', 'new'], axis=1, inplace=True)
    df.rename(columns={'origin': 'underlying_symbol'}, inplace=True)
    df.set_index(['date', 'underlying_symbol'], inplace=True)
    return df.sort_index()


@export_as_api(namespace="futures")
def get_contract_multiplier(underlying_symbols, start_date=None, end_date=None, market="cn"):
    """获取时间区间内期货的合约乘数

    :param underlying_symbols: 期货品种, 支持列表查询
    :param start_date: 开始日期, 如'2015-01-01', 如果不填写则取underlying_symbols对应实际数据最早范围
    :param end_date: 结束日期, 如'2015-01-01', 如果不填写则为当日前一天
    :param market: 市场, 默认为"cn", 当前仅支持中国市场
    :return: pd.DataFrame

    """
    underlying_symbols = ensure_list_of_string(underlying_symbols, name="underlying_symbols")
    ret = get_client().execute("futures.get_contract_multiplier", underlying_symbols)
    if not ret:
        return

    # 因 mongo 数据为时间范围，要返回每一天的数据，需复制合约乘数数据至至范围内所有 trading_date
    if start_date:
        start_date = to_datetime(start_date)
    if not end_date:
        end_date = datetime.datetime.today() - datetime.timedelta(days=1)
    end_date = to_datetime(end_date)

    def fill(group_df):
        # 根据当前合约日期范围及给定范围内获取所有 trading_date
        date_min, date_max = group_df['effective_date'].min(), group_df['cancel_date'].max()
        if start_date is not None:
            date_min = max(start_date, date_min)
        date_max = min(date_max, end_date)
        trading_dates = pd.to_datetime(
            get_trading_dates(date_min, date_max) + group_df['effective_date'].to_list()).unique()

        # 使用 trading_dates 作为 index 插入并填充数据
        everyday_df = group_df.set_index(['effective_date']).reindex(
            trading_dates).sort_index().ffill().reset_index().rename(columns={'index': 'date'})
        everyday_df = everyday_df[(everyday_df['date'] >= date_min) & (everyday_df['date'] <= date_max)]

        return everyday_df

    df = pd.DataFrame(ret).groupby(by=['underlying_symbol']).apply(fill)

    df = df[['date', 'underlying_symbol', 'exchange', 'contract_multiplier']]
    df.set_index(['underlying_symbol', 'date'], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace='futures')
def get_current_basis(order_book_ids, market='cn'):
    """获取股指期货的实时基差指标

    :param order_book_ids: str or str list	合约代码
    :param market: str	默认是中国内地市场('cn') 。可选'cn' - 中国内地市场；
    :return: DataFrame with below fields:
        字段	类型	说明
        order_book_id	str	合约代码
        datetime	datetime	时间戳
        index	str	指数合约
        index_px	float	指数最新价格
        future_px	float	期货最新价格
        basis	 float	升贴水， 等于期货合约收盘价- 对应指数收盘价
        basis_rate	float	升贴水率(%)，（期货合约收盘价- 对应指数收盘价）/对应指数收盘价*100
        basis_annual_rate	float	年化升贴水率（%), basis_rate *(250/合约到期剩余交易日）
    """
    ins_list = ensure_instruments(order_book_ids, 'Future')
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    underlying_id_map = {}
    remaining_days_map = {}

    for ins in ins_list:
        if ins.industry_name != '股指':
            warnings.warn(
                'expect 股指期货, got {}({})!'.format(ins.industry_name, ins.order_book_id),
                stacklevel=0
            )
            continue
        if ins.listed_date == '0000-00-00' or (ins.listed_date > today_str) or (
                ins.de_listed_date != '0000-00-00' and ins.de_listed_date < today_str):
            warnings.warn('inactive order_book_id: {}'.format(ins.order_book_id), stacklevel=0)
            continue
        underlying_id_map[ins.order_book_id] = ins.underlying_order_book_id
        remaining_days_map[ins.order_book_id] = len(get_trading_dates(today_str, ins.de_listed_date)) - 1
    if not underlying_id_map:
        return None
    futures = list(underlying_id_map.keys())
    indexes = list(set(underlying_id_map.values()))

    data = {future: {'order_book_id': future, 'index': index} for future, index in underlying_id_map.items()}
    from ..services.live import current_snapshot
    source = {sn.order_book_id: sn for sn in current_snapshot(futures + indexes, market=market)}
    if not source:
        return None

    for future, index in underlying_id_map.items():
        d = data[future]
        f = source[future]
        i = source[index]
        d['datetime'] = f['datetime']
        d['index_px'] = i['last']
        d['future_px'] = f['settlement'] if f['settlement'] == f['settlement'] else f['last']
        d['basis'] = d['future_px'] - d['index_px']
        d['basis_rate'] = d['basis'] / d['index_px'] * 100
        n = remaining_days_map[future]
        if n <= 0:
            d['basis_annual_rate'] = float('nan')
        else:
            d['basis_annual_rate'] = d['basis_rate'] * (250 / n)

    df = pd.DataFrame(list(data.values())).set_index('order_book_id')
    return df


VALID_FIELDS_MAP = {
    '1d': [
        "open", "high", "low", "close", "index", "close_index",
        "basis", "basis_rate", "basis_annual_rate",
        "settlement", "settle_basis", "settle_basis_rate", "settle_basis_annual_rate"
    ],
    '1m': [
        "open", "high", "low", "close", "index", "close_index",
        "basis", "basis_rate", "basis_annual_rate"
    ],
    'tick': [
        "index", "future_px", "index_px",
        "basis", "basis_rate", "basis_annual_rate",
    ]
}

FUTURE_PRICE_FIELDS_MAP = {
    '1d': ['close', 'open', 'high', 'low', 'settlement'],
    '1m': ['close', 'open', 'high', 'low'],
    'tick': ['last']
}


@export_as_api(namespace="futures")
def get_basis(order_book_ids, start_date=None, end_date=None, fields=None, frequency='1d', market="cn"):
    """ 获取股指期货升贴水信息.

    :param order_book_ids: 期货合约, 支持 order_book_id 或 order_book_id list.
    :param start_date: 开始时间, 若不传, 为 end_date 前3个月.
    :param end_date: 结束时间, 若不传, 为 start_date 后3个月, 如果 start_date 也不传, 则默认为最近3个月.
    :param fields: 需要返回的字段, 若不传则返回所有字段, 支持返回的字段包括
        open, high, low, close, index, close_index, basis, basis_rate, basis_annual_rate.
    :param frequency: 数据频率, 默认 '1d', 其他可选 {'1m', 'tick'}
        frequency=tick时, fields为index, future_px, index_px, basis, basis_rate, basis_annual_rate
    :param market: 市场, 默认'cn'
    :return: MultiIndex DataFrame.
    """
    start_date, end_date = ensure_date_range(start_date, end_date)
    ensure_string_in(frequency, ('1d', '1m', 'tick'), 'frequency')

    insts = instruments(order_book_ids)
    if insts is None:
        return None
    if not isinstance(order_book_ids, list):
        insts = [insts]
    insts = [
        x for x in insts
        if x.type == "Future" and x.listed_date != "0000-00-00" and x.industry_name == "股指"
    ]
    if not insts:
        return None

    underlying_id_map = {x.order_book_id: x.underlying_order_book_id for x in insts}
    delisted_map = {x.order_book_id: to_date(x.de_listed_date) for x in insts}
    close_field = 'close' if frequency != 'tick' else 'last'

    if fields is None:
        fields = VALID_FIELDS_MAP[frequency]
        need_basis, need_settlement_basis, need_index_price = True, (frequency == '1d'), True
        future_price_fields = FUTURE_PRICE_FIELDS_MAP[frequency]
    else:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, VALID_FIELDS_MAP[frequency], 'fields')
        need_basis, need_settlement_basis = False, False
        FUTURE_PRICE_FIELDS = FUTURE_PRICE_FIELDS_MAP[frequency]
        future_price_fields = set()
        need_index_price = False
        for f in fields:
            if f.startswith('basis') or f == 'future_px':
                future_price_fields.add(close_field)
                need_basis, need_index_price = True, f.startswith('basis')
            elif f == 'index_px' or f == 'close_index':
                need_index_price = True
            elif f.startswith('settle'):
                future_price_fields.add('settlement')
                need_settlement_basis, need_index_price = True, True
            elif f in FUTURE_PRICE_FIELDS:
                future_price_fields.add(f)
        future_price_fields = list(future_price_fields)

    order_book_ids = [x.order_book_id for x in insts]
    future_price = get_price.get_price(
        order_book_ids, start_date, end_date, frequency=frequency, fields=future_price_fields,
        expect_df=True, market=market
    )
    if future_price is None:
        return None

    future_price["index"] = future_price.index.get_level_values("order_book_id").map(underlying_id_map)

    _all_trading_dates = get_trading_dates(start_date, max(delisted_map.values()))
    _dates_remain_cache = {
        (s, e): (bisect.bisect_left(_all_trading_dates, e) - bisect.bisect_left(_all_trading_dates, s))
        for s in get_trading_dates(start_date, end_date)
        for e in delisted_map.values()
    }

    def _calc_annual_rate(row, rate_field):
        # row.name[1] is current date.
        order_book_id, current_date = row.name
        dates_remain = _dates_remain_cache[(current_date.date(), delisted_map[order_book_id])]
        if dates_remain == 0:
            # 在到期的时候, basis_annual_rate 的值本身也没有什么意义, 所以直接赋值为 nan.
            return float("nan")
        else:
            return row[rate_field] * 250 / dates_remain

    if need_index_price:
        underlying_ids = list({x.underlying_order_book_id for x in insts})
        if frequency == '1d':
            from rqdatac.services.detail import get_price_df
            index_close = get_price_df.get_future_indx_daybar(underlying_ids, start_date, end_date, fields=["close"])
            date_field = 'date'
        else:
            index_close = get_price.get_price(underlying_ids, start_date, end_date, frequency=frequency,
                                              fields=close_field, expect_df=True)
            date_field = 'datetime'
        if index_close is None:
            return None
        index_close.columns = ['close_index']
        future_price = pd.merge_asof(
            future_price.reset_index().sort_values(date_field),
            index_close.reset_index().rename(
                columns={'order_book_id': 'index'}
            ).sort_values(date_field),
            on=date_field,
            by='index',
            direction='backward'
        )
        future_price.set_index(['order_book_id', date_field], inplace=True)
        future_price.sort_index(inplace=True)
        future_price.bfill(axis=0, inplace=True)

    if need_basis:
        future_price["basis"] = future_price[close_field] - future_price["close_index"]
        future_price["basis_rate"] = future_price["basis"] / future_price["close_index"] * 100
        future_price["basis_annual_rate"] = future_price.apply(lambda x: _calc_annual_rate(x, "basis_rate"), axis=1)

    if need_settlement_basis:
        future_price["settle_basis"] = future_price["settlement"] - future_price["close_index"]
        future_price["settle_basis_rate"] = future_price["settle_basis"] / future_price["close_index"] * 100
        future_price["settle_basis_annual_rate"] = future_price.apply(
            lambda x: _calc_annual_rate(x, "settle_basis_rate"), axis=1
        )

    if frequency == 'tick':
        future_price.rename(columns={'close_index': 'index_px', close_field: 'future_px'}, inplace=True)

    res = future_price[fields]
    return res


VALID_ADJUST_METHODS = ['prev_close_spread', 'open_spread', 'prev_close_ratio', 'open_ratio']


@ttl_cache(1800)
def _get_future_factors_df(rule=0, rank=1, market='cn'):
    """ 获取所有复权因子表 """
    data = get_client().execute('futures.__internal__get_future_factors_v2', rule, rank, market=market)
    df = pd.DataFrame(data)
    df['ex_date'] = df['ex_date'].apply(int8_to_datetime)
    df.set_index(['underlying_symbol', 'ex_date'], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace='futures')
def get_ex_factor(underlying_symbols, start_date=None, end_date=None, adjust_method='prev_close_spread', rule=0, rank=1,
                  market='cn'):
    """ 获取期货复权因子

    :param underlying_symbols: 期货合约品种，str or list
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param adjust_method: 复权方法，prev_close_spread, prev_close_ratio, open_spread, open_ratio,
    默认为‘prev_close_spread'
    :param rule: 主力合约规则
    :param market: 默认是中国内地市场('cn') 。可选'cn' - 中国内地市场
    :return: DataFrame
    """
    df = _get_future_factors_df(rule, rank, market)
    valid_underlying_symbols = df.index.get_level_values('underlying_symbol').unique().tolist()
    underlying_symbols = ensure_list_of_string(underlying_symbols, 'underlying_symbols')
    check_items_in_container(adjust_method, VALID_ADJUST_METHODS, 'adjust_method')
    check_items_in_container(underlying_symbols, valid_underlying_symbols, 'underlying_symbols')

    factor = df.loc[underlying_symbols, adjust_method]
    factor.name = 'ex_factor'
    factor = factor.reset_index()

    spread = adjust_method.endswith('spread')
    factor.sort_values('ex_date', inplace=True)
    factor['ex_end_date'] = factor['ex_date'].apply(
        lambda r: pd.Timestamp(get_previous_trading_date(r))
    )

    def _process(x):
        x['ex_end_date'] = x['ex_end_date'].shift(-1)
        if spread:
            x['ex_cum_factor'] = x['ex_factor'].cumsum()
        else:
            x['ex_cum_factor'] = x['ex_factor'].cumprod()
        return x

    factor = factor.groupby('underlying_symbol', as_index=False).apply(_process)
    if start_date and end_date:
        start_date, end_date = to_datetime(start_date), to_datetime(end_date)
        factor = factor[(start_date <= factor['ex_date']) & (factor['ex_date'] <= end_date)]
    # _get_future_factors_df 已经排序过了，此处无需再次排序
    return factor.set_index('ex_date')


def __internal_get_ex_factor(underlying_symbols, adjust_type, adjust_method, rule=0, rank=1):
    """ 内部使用，获取复权因子，提供给get_dominant_price进行复权计算用
    :return: pd.Series
    """
    df = _get_future_factors_df(rule, rank)
    df = df.loc[underlying_symbols]

    factor = df[adjust_method]
    factor.name = 'ex_factor'
    factor = factor.reset_index()
    pre = adjust_type == 'pre'
    ratio = adjust_method.endswith('ratio')

    def _process(x):
        if ratio:
            x['ex_cum_factor'] = x['ex_factor'].cumprod()
            if pre:
                x['ex_cum_factor'] = x['ex_cum_factor'] / x['ex_cum_factor'].iloc[-1]
        else:
            x['ex_cum_factor'] = x['ex_factor'].cumsum()
            if pre:
                x['ex_cum_factor'] = x['ex_cum_factor'] - x['ex_cum_factor'].iloc[-1]

        # tds 是从小到大排列的， 因此reindex后无需再sort
        return x.set_index('ex_date')

    factor = factor.groupby('underlying_symbol', as_index=True).apply(_process)
    return factor['ex_cum_factor']


DOMINANT_PRICE_ADJUST_FIELDS = [
    'open', 'high', 'low', 'close', 'last', 'limit_up', 'limit_down', 'settlement', 'prev_settlement', 'prev_close',
    'a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3', 'b4', 'b5'
]

DOMINANT_PRICE_FIELDS = {
    'tick': [
        "trading_date", "open", "last", "high", "low",
        "prev_close", "volume", "total_turnover", "limit_up", "limit_down",
        "a1", "a2", "a3", "a4", "a5", "b1", "b2", "b3", "b4", "b5", "a1_v", "a2_v", "a3_v",
        "a4_v", "a5_v", "b1_v", "b2_v", "b3_v", "b4_v", "b5_v", "change_rate",
        "open_interest", "prev_settlement",
    ],
    'd': [
        "open", "close", "high", "low", "total_turnover", "volume", "prev_close",
        "settlement", "prev_settlement", "open_interest", "limit_up", "limit_down",
        "day_session_open",
    ],
    'm': [
        "trading_date", "open", "close", "high", "low", "total_turnover", "volume", "open_interest"
    ],
}


def _slice_dominant_data(data):
    s = None
    uids = set()
    for i, (obid, _) in enumerate(data):
        if obid in uids:
            uids.clear()
            yield slice(s, i)
            s = i
        uids.add(obid)
    yield slice(s, None)


@export_as_api(namespace='futures')
def get_dominant_price(
        underlying_symbols, start_date=None, end_date=None,
        frequency='1d', fields=None, adjust_type='pre', adjust_method='prev_close_spread',
        rule=0, rank=1
):
    """ 获取主力合约行情数据

    :param underlying_symbols: 期货合约品种，可传入 underlying_symbol, underlying_symbol list
    :param start_date: 开始日期, 最小日期为 20210104
    :param end_date: 结束日期
    :param frequency: 历史数据的频率。 支持/日/分钟/tick 级别的历史数据，默认为'1d'。
        1m- 分钟线，1d-日线，分钟可选取不同频率，例如'5m'代表 5 分钟线
    :param fields: 字段名称列表
    :param adjust_type: 复权方式，不复权 - none，前复权 - pre，后复权 - post
    :param adjust_method: 复权方法 ，prev_close_spread/open_spread:基于价差复权因子进行复权，
        prev_close_ratio/open_ratio:基于比例复权因子进行复权，
        默认为‘prev_close_spread',adjust_type为None 时，adjust_method 复权方法设置无效
    :param rule: 主力合约规则，参考get_dominant
    :return: MultiIndex DataFrame
    """
    assert isinstance(frequency, str) and (frequency == 'tick' or frequency.endswith(('d', 'm'))), 'invalid frequency!'
    if not isinstance(underlying_symbols, list):
        underlying_symbols = [underlying_symbols]
    if fields is None:
        if frequency == 'tick':
            fields = DOMINANT_PRICE_FIELDS['tick']
        elif frequency[-1] == 'm':
            fields = DOMINANT_PRICE_FIELDS['m']
        else:
            fields = DOMINANT_PRICE_FIELDS['d']
    else:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, DOMINANT_PRICE_FIELDS[frequency[-1] if frequency != 'tick' else frequency],
                                 frequency)

    trading_date_missing = False
    if frequency[-1] != 'd' and 'trading_date' not in fields:
        fields.append('trading_date')
        trading_date_missing = True

    gtw_fields = set(fields)
    if frequency == 'tick':
        gtw_fields |= {'date', 'time'}

    start_date, end_date = ensure_date_range(start_date, end_date)
    if start_date < 20100104:
        raise ValueError('expect start_date >= 20100104, get {}'.format(start_date))
    # ensure adjust_type and adjust_method
    check_items_in_container(adjust_type, ['none', 'pre', 'post'], 'adjust_type')
    check_items_in_container(adjust_method, VALID_ADJUST_METHODS, 'adjust_method')

    _date_key = 'date' if frequency == '1d' else 'trading_date'

    if frequency == 'tick':
        if set(fields) & {"open", "prev_settlement", "prev_close", "limit_up", "limit_down", "change_rate"}:
            gtw_fields.update({'volume', 'last'})
    gtw_fields = list(gtw_fields)

    data = get_client().execute('futures.get_dominant_price', underlying_symbols, start_date, end_date, frequency,
                                gtw_fields, rule, rank)
    data = [(obid, {k: np.frombuffer(*v) for k, v in d.items()}) for obid, d in data]
    df = None
    if frequency == 'tick':
        from .get_price import convert_history_tick_to_multi_df
        dfs = []
        for slice_ in _slice_dominant_data(data):
            df_ = convert_history_tick_to_multi_df(data[slice_], 'datetime', fields, int17_to_datetime_v)
            if df_ is not None:
                dfs.append(df_)
        if dfs:
            df = pd.concat(dfs)
    elif frequency[-1] == 'm':
        dfs = []
        for slice_ in _slice_dominant_data(data):
            df_ = convert_bar_to_multi_df(data[slice_], 'datetime', fields, int14_to_datetime_v)
            if df_ is not None:
                dfs.append(df_)
        if dfs:
            df = pd.concat(dfs)
            df[_date_key] = int8_to_datetime_v(df[_date_key].astype(int))
    else:
        dfs = []
        for slice_ in _slice_dominant_data(data):
            df_ = convert_bar_to_multi_df(data[slice_], 'date', fields, int8_to_datetime_v)
            if df_ is not None:
                dfs.append(df_)
        if dfs:
            df = pd.concat(dfs)

    live_date = current_trading_date()
    live_df = None
    live_obs = []
    if end_date >= live_date and frequency[-1] != 'd':
        def _to_trading_date(dt):
            if 7 <= dt.hour < 18:
                return date_to_int8(dt)
            return date_to_int8(get_next_trading_date(dt - datetime.timedelta(hours=4)))

        for ud in underlying_symbols:
            dominant = get_dominant(ud, live_date, live_date, rule=rule, rank=rank)
            if dominant is None:
                continue
            dominant_id = dominant.iloc[0]
            try:
                if df is None or _to_trading_date(df.loc[dominant_id].index.max()) != live_date:
                    live_obs.append(dominant_id)
            except KeyError:
                live_obs.append(dominant_id)

    if live_obs:
        if frequency[-1] == 'm':
            from ..services.detail.get_price_df import get_today_minbar
            live_df, _ = get_today_minbar(live_obs, fields, int(frequency[:-1]))
            if live_df is not None:
                live_df[_date_key] = int8_to_datetime(live_date)
        else:
            from ..services.live import get_ticks
            live_dfs = []
            for live_ob in live_obs:
                try:
                    live_df = get_ticks(live_ob, live_date, live_date, expect_df=True)
                    if live_df is None:
                        continue
                    live_df["trading_date"] = int8_to_datetime(live_date)
                    if 'change_rate' in fields:
                        live_df["change_rate"] = live_df["last"] / live_df["prev_settlement"] - 1
                    live_df = live_df.reindex(columns=fields)
                    live_dfs.append(live_df)
                except:
                    pass
            if live_dfs:
                live_df = pd.concat(live_dfs)

    if df is None and live_df is None:
        return None
    df = pd.concat([df, live_df])
    df.reset_index(inplace=True)
    ud_map = {ins.order_book_id: ins.underlying_symbol for ins in instruments(df['order_book_id'].unique())}
    df['underlying_symbol'] = df['order_book_id'].map(ud_map)
    df.set_index(['underlying_symbol', _date_key], inplace=True)
    df.sort_index(inplace=True)

    if adjust_type != 'none':
        # 复权调整
        factor = __internal_get_ex_factor(df.index.levels[0].tolist(), adjust_type, adjust_method, rule, rank)
        factor = factor.reindex(factor.index.union(df.index.unique()))
        factor = factor.groupby(level=0).ffill()
        values = factor.loc[df.index].values
        _fields = fields if fields else df.columns.tolist()
        adjust_fields = [f for f in DOMINANT_PRICE_ADJUST_FIELDS if f in _fields]
        if adjust_method.endswith('spread'):
            for field in adjust_fields:
                df[field] += values
        elif adjust_method.endswith('ratio'):
            for field in adjust_fields:
                df[field] *= values
        if 'total_turnover' in df.columns:
            df['total_turnover'] = 0

    if frequency[-1] != 'd':
        df = df.reset_index().set_index(['underlying_symbol', 'datetime'])
    df.rename(columns={'order_book_id': 'dominant_id'}, inplace=True)
    df.sort_index(inplace=True)
    if trading_date_missing:
        df.drop(columns='trading_date', inplace=True)
    return df


def get_ob_datetime_multi_index(
        order_book_ids,
        start_date,
        end_date,
        names=['order_book_id', 'trading_date']
):
    start_date = to_datetime(start_date).strftime("%Y-%m-%d")
    end_date = to_datetime(end_date).strftime("%Y-%m-%d")
    insts = instruments(order_book_ids)
    indexs = []
    dates = get_trading_dates(start_date, end_date)
    index = pd.to_datetime(dates)
    for i in insts:
        oid = i.order_book_id
        listed_date = i.listed_date
        de_listed_date = i.de_listed_date if i.de_listed_date != '0000-00-00' else '9999-99-99'
        start = pd.Timestamp(max(start_date, listed_date))
        end = pd.Timestamp(min(end_date, de_listed_date))
        start_pos, end_pos = index.searchsorted(start), index.searchsorted(end)
        _index = index[start_pos:end_pos + 1]
        indexs.extend([(oid, i) for i in _index])

    return pd.MultiIndex.from_tuples(indexs, names=names)


TRADING_PARAMETERS_FIELDS = [
    'long_margin_ratio',
    'short_margin_ratio',
    'commission_type',
    'open_commission',
    'close_commission',
    'discount_rate',
    'close_commission_today',
    'non_member_limit_rate',
    'client_limit_rate',
    'non_member_limit',
    'client_limit',
    'min_order_quantity',
    'max_order_quantity',
    'min_margin_ratio',
]


@export_as_api(namespace='futures')
def get_trading_parameters(order_book_ids, start_date=None, end_date=None, fields=None, market='cn'):
    """ 获取期货交易参数信息

    :param order_book_ids: 期货合约代码或代码列表
    :param start_date: 开始日期，如 '2019-01-01'，若不指定，默认为当前交易日
                       未指定时，若查询时间在 T 日 8.40pm 前，返回 T 日数据，否则返回 T+1 日数据
    :param end_date: 结束日期，如 '2023-01-01'，若不指定，默认为当前交易日
                     开始日期和结束日期需同时传入或同时不传入
    :param fields: 所需字段或字段列表，不指定则返回全部字段，可选:
        [ 'long_margin_ratio', 'short_margin_ratio', 'commission_type', 'open_commission', 
          'close_commission', 'discount_rate, 'close_commission_today',
          'non_member_limit_rate', 'client_limit_rate', 'non_member_limit', 'client_limit',
          'min_order_quantity', 'max_order_quantity', 'min_margin_ratio',
        ]
        min_margin_ratio: 最低保证金
    :param market: 目前只支持中国市场，默认为 'cn'

    :return: DataFrame(MultiIndex(order_book_id, trading_date)) or None
    """
    order_book_ids = ensure_order_book_ids(order_book_ids, type='Future', market=market)
    # 只存了真实合约信息
    order_book_ids = list(
        filter(
            lambda x: not x.endswith(('88', '99', '888', '889', '88A2', '88A3')),
            order_book_ids
        )
    )
    if fields is None:
        fields = TRADING_PARAMETERS_FIELDS
    else:
        fields = ensure_list_of_string(fields, 'fields')
        check_items_in_container(fields, TRADING_PARAMETERS_FIELDS, 'fields')
    now = datetime.datetime.now()
    if is_trading_date(now):
        # dps 任务在 18:00 第一次更新夜盘信息
        if now.hour >= 18:
            day = get_next_trading_date(now)
        else:
            day = now.date()
    else:
        day = get_next_trading_date(now)
    day = date_to_int8(day)
    if start_date is None and end_date is None:
        start_date = end_date = day
    elif start_date and end_date:
        start_date, end_date = ensure_date_range(start_date, end_date)
        # 数据是不连续向后填补的，因此不能返回还未有记录的日期
        end_date = min(end_date, day)
        if end_date < start_date:
            return None
    else:
        raise ValueError('start_date and end_date should be used together or not at the same time')

    insts = instruments(order_book_ids)
    _oids = []
    # 筛选位于 start_date 与 end_date 间的 ob
    for i in insts:
        listed_date = int(i.listed_date.replace('-', ''))
        de_listed_date = i.de_listed_date if i.de_listed_date != '0000-00-00' else '9999-99-99'
        de_listed_date = int(de_listed_date.replace('-', ''))
        if start_date <= de_listed_date and end_date >= listed_date:
            _oids.append(i.order_book_id)
    order_book_ids = _oids

    # 交易参数数据已去重所以不连续，获取全部数据
    data = get_client().execute('futures.get_trading_parameters', order_book_ids, fields, market)
    if not data:
        return

    indexes = get_ob_datetime_multi_index(order_book_ids, start_date, end_date)
    indexes = indexes.to_frame(index=False)
    indexes.sort_values(["trading_date", "order_book_id"], inplace=True)
    df = pd.DataFrame(data)
    df.sort_values(["trading_date", "order_book_id"], inplace=True)
    df = pd.merge_asof(indexes, df, on="trading_date", by="order_book_id")
    if df.empty:
        return None
    df.set_index(["order_book_id", "trading_date"], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace='futures')
def get_exchange_daily(order_book_ids, start_date=None, end_date=None, fields=None, market='cn'):
    """获取交易所日线数据

    :param order_book_ids: 期货合约代码或代码列表
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param fields: 所需字段或字段列表，不指定则返回全部字段，可选:
        [
            "open", "close", "high", "low", "total_turnover",
            "volume", "settlement", "prev_settlement", "open_interest"
        ]
    :param market: 目前只支持中国市场，默认为 'cn'
    :return: DataFrame(MultiIndex(order_book_id, trading_date)) or None
    """
    all_fields = [
        "open", "close", "high", "low", "total_turnover",
        "volume", "settlement", "prev_settlement", "open_interest"
    ]
    if fields is None:
        fields = all_fields
    else:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, all_fields, "fields")
        fields = list(set(fields))
    order_book_ids = ensure_order_book_ids(order_book_ids, type='Future', market=market)
    start_date, end_date = ensure_date_range(start_date, end_date)
    data = get_client().execute(
        'futures.get_futures_exchange_daybar_v', order_book_ids, start_date, end_date, fields, market
    )
    data = [(obid, {k: np.frombuffer(*v) for k, v in d.items()}) for obid, d in data]
    return convert_bar_to_multi_df(data, 'date', fields, int8_to_datetime_v)


@export_as_api(namespace='futures')
def get_continuous_contracts(underlying_symbol, start_date, end_date, type='front_month', market='cn'):
    """
    获取期货当月/次月/季月/远季合约，目前只支持股指期货

    :param underlying_symbol: 期货品种代码
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param type: 合约类型，可选：front_month, next_month, quarter_month, far_month
    :param market: 目前只支持中国市场，默认为 'cn'
    :return: Series[date, order_book_id]
    """
    start_date, end_date = ensure_date_range(start_date, end_date)
    check_items_in_container(type, ['front_month', 'next_month', 'current_quarter', 'next_quarter'], 'type')
    data = get_client().execute(
        'futures.get_continuous_contracts', underlying_symbol, start_date, end_date, type, market=market
    )
    return pd.Series({d['date']: d['contract'] for d in data})
