# -*- coding: utf-8 -*-
import warnings
from collections import OrderedDict
import math

import pandas as pd

from rqdatac.services.calendar import get_previous_trading_date
from rqdatac.services.get_price import get_price
from rqdatac.services.basic import instruments
from rqdatac.validators import (
    ensure_date_or_today_int,
    check_quarter,
    quarter_string_to_date,
    ensure_list_of_string,
    ensure_order,
    check_items_in_container,
    ensure_date_range,
    ensure_date_int,
    ensure_order_book_ids,
    raise_for_no_panel,
)
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api, compatible_with_parm, may_trim_bjse
from rqdatac.hk_decorators import support_hk_order_book_id
from rqdatac.utils import pf_fill_nan, is_panel_removed, int8_to_datetime_v


@export_as_api
@support_hk_order_book_id
@compatible_with_parm(name="country", value="cn", replace="market")
def get_split(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取拆分信息

    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_date: 开始日期；默认为上市首日
    :param end_date: 结束日期；默认为今天
    :param market:  (Default value = "cn")

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    data = get_client().execute("get_split", order_book_ids, start_date, end_date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)
    df.sort_values("ex_dividend_date", inplace=True)
    # cumprod [1, 2, 4] -> [1, 1*2, 1*2*4]
    df["cum_factor"] = df["split_coefficient_to"] / df["split_coefficient_from"]
    df["cum_factor"] = df.groupby("order_book_id")["cum_factor"].cumprod()
    if len(order_book_ids) == 1:
        df.set_index("ex_dividend_date", inplace=True)
    else:
        df.set_index(["order_book_id", "ex_dividend_date"], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api
@support_hk_order_book_id
@compatible_with_parm(name="country", value="cn", replace="market")
def get_dividend(order_book_ids, start_date=None, end_date=None, adjusted=False, expect_df=False, market="cn"):
    """获取分红信息

    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_date: 开始日期，默认为股票上市日期
    :param end_date: 结束日期，默认为今天
    :param adjusted: deprecated
    :param market:  (Default value = "cn")

    """
    if adjusted:
        warnings.warn(
            "get_dividend adjusted = `True` is not supported yet. "
            "The default value is `False` now."
        )
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    data = get_client().execute("get_dividend", order_book_ids, start_date, end_date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)
    if len(order_book_ids) == 1 and not expect_df:
        df.set_index("declaration_announcement_date", inplace=True)
    else:
        df.set_index(["order_book_id", "declaration_announcement_date"], inplace=True)
    return df.sort_index()


@export_as_api
@support_hk_order_book_id
def get_dividend_info(order_book_ids, start_date=None, end_date=None, market="cn"):
    """对应时间段是否发生分红

    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_date: 开始日期，默认为空
    :param end_date: 结束日期，默认为空
    :param market:  (Default value = "cn")

    """
    order_book_ids = ensure_order_book_ids(order_book_ids)
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    if start_date and end_date:
        if start_date > end_date:
            raise ValueError("invalid date range: [{!r}, {!r}]".format(start_date, end_date))

    data = get_client().execute("get_dividend_info_v2", order_book_ids, start_date, end_date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)
    if "rice_create_tm" in df.columns:
        df["rice_create_tm"] = pd.to_datetime(df["rice_create_tm"] + 3600 * 8, unit="s")
    if len(order_book_ids) == 1:
        df.set_index("effective_date", inplace=True)
    else:
        df.set_index(["order_book_id", "effective_date"], inplace=True)
    return df.sort_index()


@export_as_api
@support_hk_order_book_id
def get_dividend_amount(order_book_ids, start_quarter=None, end_quarter=None, date=None, market="cn"):
    """获取股票历年分红总额

    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_quarter: 开始季度，默认为空
    :param end_quarter: 结束季度，默认为空
    :param date: 公告发布日期，默认为当前日期, 如 '2020-01-01' | '20200101'
    :param market:  (Default value = "cn")

    """
    order_book_ids = ensure_order_book_ids(order_book_ids)
    if start_quarter is not None:
        check_quarter(start_quarter, 'start_quarter')
        start_quarter = ensure_date_int(quarter_string_to_date(start_quarter))
    if end_quarter is not None:
        check_quarter(end_quarter, 'end_quarter')
        end_quarter = ensure_date_int(quarter_string_to_date(end_quarter))

    if start_quarter and end_quarter and start_quarter > end_quarter:
        raise ValueError("invalid quarter range: [{!r}, {!r}]".format(start_quarter, end_quarter))
    date = ensure_date_or_today_int(date)

    data = get_client().execute("get_dividend_amount_v2", order_book_ids, start_quarter, end_quarter, date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)
    if "rice_create_tm" in df.columns:
        df["rice_create_tm"] = pd.to_datetime(df["rice_create_tm"] + 3600 * 8, unit="s")
    # 可能在不同的info_date下, 存在相同 end_date的数据, 这时候取info_date最新的那条
    df.sort_values(["order_book_id", "info_date", "end_date"], inplace=True)
    df.drop_duplicates(subset=["order_book_id", "end_date", "event_procedure"], keep="last", inplace=True)
    df["quarter"] = df["end_date"].apply(
        lambda d: "{}q{}".format(d.year, math.ceil(d.month / 3))
    )
    agg_dict = {
        "info_date": "last",
        "amount": "sum"
    }
    if "rice_create_tm" in df.columns:
        agg_dict["rice_create_tm"] = "last"
    df = df.groupby(["order_book_id", "quarter", "event_procedure"], as_index=False).agg(agg_dict)
    df.sort_values(["order_book_id", "quarter", "info_date"], inplace=True)
    df.set_index(["order_book_id", "quarter"], inplace=True)
    return df


@export_as_api
@support_hk_order_book_id
@compatible_with_parm(name="country", value="cn", replace="market")
def get_ex_factor(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取复权因子

    :param order_book_ids: 如'000001.XSHE'
    :param market: 国家代码, 如 'cn' (Default value = "cn")
    :param start_date: 开始日期，默认为股票上市日期
    :param end_date: 结束日期，默认为今天
    :returns: 如果有数据，返回一个DataFrame, 否则返回None

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    data = get_client().execute("get_ex_factor", order_book_ids, start_date, end_date, market=market)
    if not data:
        return None
    df = pd.DataFrame(data)
    df.sort_values(["order_book_id", "ex_date"], inplace=True)
    df.set_index("ex_date", inplace=True)
    return df


TURNOVER_FIELDS_MAP = OrderedDict()
TURNOVER_FIELDS_MAP["today"] = "turnover_rate"
TURNOVER_FIELDS_MAP["week"] = "week_turnover_rate"
TURNOVER_FIELDS_MAP["month"] = "month_turnover_rate"
TURNOVER_FIELDS_MAP["year"] = "year_turnover_rate"
TURNOVER_FIELDS_MAP["current_year"] = "year_sofar_turnover_rate"


def _get_maped_fields(fields):
    fields = ensure_list_of_string(fields, "fields")
    check_items_in_container(fields, TURNOVER_FIELDS_MAP, "fields")
    fields = ensure_order(fields, TURNOVER_FIELDS_MAP.keys())
    return fields, [TURNOVER_FIELDS_MAP[field] for field in fields]


@export_as_api
@support_hk_order_book_id
def get_turnover_rate(order_book_ids, start_date=None, end_date=None, fields=None, expect_df=True, market="cn"):
    """获取股票换手率数据

    :param order_book_ids: 股票代码或股票代码列表
    :param start_date: 开始时间
    :param end_date: 结束时间；在 start_date 和 end_date 都不指定的情况下，默认为最近3个月
    :param fields: str或list类型. 默认为None, 返回所有fields.
                   field 包括： 'today', 'week', 'month', 'year', 'current_year'
                   (Default value = None)
    :param expect_df: 返回 MultiIndex DataFrame (Default value = True)
    :param market: 地区代码, 如: 'cn' (Default value = "cn")
    :returns: 如果order_book_ids或fields为单个值 返回pandas.DataFrame, 否则返回pandas.Panel

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    start_date, end_date = ensure_date_range(start_date, end_date)
    if fields is not None:
        fields, mapped_fields = _get_maped_fields(fields)
    else:
        fields, mapped_fields = list(TURNOVER_FIELDS_MAP.keys()), list(TURNOVER_FIELDS_MAP.values())
    df = get_client().execute(
        "get_turnover_rate", order_book_ids, start_date, end_date, mapped_fields, market=market
    )
    if not df:
        return
    df = pd.DataFrame(df, columns=["tradedate", "order_book_id"] + mapped_fields)
    df.rename(columns={v: k for k, v in TURNOVER_FIELDS_MAP.items()}, inplace=True)

    if not expect_df and not is_panel_removed:
        df.set_index(["tradedate", "order_book_id"], inplace=True)
        df.sort_index(inplace=True)
        df = df.to_panel()
        df = pf_fill_nan(df, order_book_ids)
        if len(order_book_ids) == 1:
            df = df.minor_xs(*order_book_ids)
            if fields and len(fields) == 1:
                return df[fields[0]]
            return df
        if fields and len(fields) == 1:
            return df[fields[0]]
        warnings.warn("Panel is removed after pandas version 0.25.0."
                      " the default value of 'expect_df' will change to True in the future.")
        return df
    else:
        df.sort_values(["order_book_id", "tradedate"], inplace=True)
        df.set_index(["order_book_id", "tradedate"], inplace=True)
        if expect_df:
            return df

        if len(order_book_ids) != 1 and len(fields) != 1:
            raise_for_no_panel()

        if len(order_book_ids) == 1:
            df.reset_index(level=0, drop=True, inplace=True)
            if len(fields) == 1:
                df = df[fields[0]]
            return df
        else:
            df = df.unstack(0)[fields[0]]
            df.index.name = None
            df.columns.name = None
            return df


@export_as_api
@support_hk_order_book_id
def get_price_change_rate(order_book_ids, start_date=None, end_date=None, expect_df=True, market="cn"):
    """获取价格变化信息

    :param order_book_ids: 股票列表
    :param start_date: 开始日期: 如'2013-01-04'
    :param end_date: 结束日期: 如'2014-01-04'；在 start_date 和 end_date 都不指定的情况下，默认为最近3个月
    :param expect_df: 是否返回 MultiIndex DataFrame (Default value = True)
    :param market: 地区代码
    :returns: 如果输入一只股票, 则返回pandas.Series, 否则返回pandas.DataFrame

    """
    start_date, end_date = ensure_date_range(start_date, end_date)
    order_book_ids = ensure_order_book_ids(order_book_ids)
    all_instruments = instruments(order_book_ids)
    convertibles = []
    not_convertibles = []
    for i in all_instruments:
        if i.type == 'Convertible':
            convertibles.append(i.order_book_id)
        else:
            not_convertibles.append(i.order_book_id)
    df = None
    df_convertible = None

    if not_convertibles:
        # 向前多取一天，防止start_date的收益率缺失
        start_date_prev = get_previous_trading_date(start_date)
        df = get_price(
            order_book_ids=not_convertibles,
            start_date=start_date_prev, end_date=end_date,
            adjust_type='post', fields='close', expect_df=True
        )

        if df is not None:
            df = df['close']
            df = df.groupby(level='order_book_id').pct_change().dropna()

    # 因为可转债可能会派息，所以用 close 去算不准，需要用当天不复权的 close 和 prev_close 去算
    if convertibles:
        df_convertible = get_price(
            order_book_ids=convertibles,
            start_date=start_date, end_date=end_date,
            adjust_type='none', fields=['close', 'prev_close'], expect_df=True
        )

        if df_convertible is not None:
            df_convertible = df_convertible['close'] / df_convertible['prev_close'] - 1

    if df is None and df_convertible is None:
        return None
    df = pd.concat([df, df_convertible])
    if df.empty:
        return None
    df = df.unstack('order_book_id')

    if len(order_book_ids) == 1 and not expect_df:
        series = df[order_book_ids[0]]
        return series

    return df


@export_as_api
@compatible_with_parm(name="country", value="cn", replace="market")
def get_yield_curve(start_date=None, end_date=None, tenor=None, market="cn"):
    """获取国债收益率曲线

    :param market: 地区代码, 如'cn', 'us' (Default value = "cn")
    :param start_date: 开始日期 (Default value = "2013-01-04")
    :param end_date: 结束日期 (Default value = "2014-01-04")
    :param tenor: 类别, 如 OS, 1M, 3M, 1Y (Default value = None)

    """
    start_date, end_date = ensure_date_range(start_date, end_date)
    all_tenor = (
        "0S",
        "1M",
        "2M",
        "3M",
        "6M",
        "9M",
        "1Y",
        "2Y",
        "3Y",
        "4Y",
        "5Y",
        "6Y",
        "7Y",
        "8Y",
        "9Y",
        "10Y",
        "15Y",
        "20Y",
        "30Y",
        "40Y",
        "50Y",
    )
    if tenor:
        tenor = ensure_list_of_string(tenor, "tenor")
        check_items_in_container(tenor, all_tenor, "tenor")
        tenor = ensure_order(tenor, all_tenor)
    df = get_client().execute("get_yield_curve", start_date, end_date, tenor, market=market)
    if not df:
        return
    columns = ["trading_date"]
    columns.extend(tenor or all_tenor)
    df = pd.DataFrame(df, columns=columns)
    df.set_index("trading_date", inplace=True)
    return df.sort_index()


@export_as_api
@support_hk_order_book_id
def get_block_trade(order_book_ids, start_date=None, end_date=None, market='cn'):
    """获取大宗交易信息
    :param order_book_ids: 股票代码
    :param start_date: 起始日期，默认为前三个月
    :param end_date: 截止日期，默认为今天
    :param market: (default value = 'cn')
    :return: pd.DataFrame or None
    """

    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)

    data = get_client().execute('get_block_trade', order_book_ids, start_date, end_date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)[['order_book_id', 'trade_date', 'price', 'volume', 'total_turnover', 'buyer', 'seller']]
    df.set_index(["order_book_id", "trade_date"], inplace=True)
    df.sort_index(inplace=True)
    return df


EXCHANGE_DATE_FIELDS = [
    "currency_pair",
    "bid_referrence_rate",
    "ask_referrence_rate",
    "middle_referrence_rate",
    "bid_settlement_rate_sh",
    "ask_settlement_rate_sh",
    "bid_settlement_rate_sz",
    "ask_settlement_rate_sz",
]


@export_as_api
def get_exchange_rate(start_date=None, end_date=None, fields=None):
    """获取汇率信息

    :param start_date: 开始日期, 如 '2013-01-04' (Default value = None)
    :param end_date: 结束日期, 如 '2014-01-04' (Default value = None)
    :param fields: str or list 返回 字段名称:currency_pair、bid_referrence_rate、ask_referrence_rate、middle_referrence_rate
        bid_settlement_rate_sh、ask_settlement_rate_sh、bid_settlement_rate_sz、ask_settlement_rate_sz

    """
    start_date, end_date = ensure_date_range(start_date, end_date)
    if fields:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, EXCHANGE_DATE_FIELDS, "fields")
    else:
        fields = EXCHANGE_DATE_FIELDS

    data = get_client().execute("get_exchange_rate", start_date, end_date, fields)
    if not data:
        return None
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    df = df[fields]
    return df


TEMPORARY_CODE_FIELDS = [
    "symbol",
    "temporary_trade_code",
    "temporary_symbol",
    "temporary_round_lot",
    "temporary_effective_date",
    "parallel_effective_date",
    "parallel_cancel_date"
]


@export_as_api
@support_hk_order_book_id
def get_temporary_code(order_book_ids, market="cn"):
    """临时交易代码查询

    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param market:  (Default value = "cn")
    """
    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)

    data = get_client().execute("get_temporary_code", order_book_ids, market)
    if not data:
        return None
    df = pd.DataFrame(data)
    df.set_index("order_book_id", inplace=True)
    df = df[TEMPORARY_CODE_FIELDS]
    return df


INTERBANK_OFFERED_RATE_FIELDS = ['ON', '1W', '2W', '1M', '3M', '6M', '9M', '1Y']


@export_as_api
def get_interbank_offered_rate(start_date=None, end_date=None, fields=None, source='Shibor'):
    """ 获取银行间同业拆放利率

    :param start_date: 开始日期, 如 '2013-01-04' (Default value = None)
    :param end_date: 结束日期, 如 '2014-01-04' (Default value = None)
    :param fields: str or list:
        ON	隔夜
        1W	1周
        2W	2周
        1M	1个月
        3M	3个月
        6M	6个月
        9M	9个月
        1Y	1年
    :param source: str, 默认Shibor 上海银行间同业拆放利率

    :returns DataFrame
    """

    start_date, end_date = ensure_date_range(start_date, end_date)
    if fields:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, INTERBANK_OFFERED_RATE_FIELDS, "fields")
    else:
        fields = INTERBANK_OFFERED_RATE_FIELDS

    data = get_client().execute("get_interbank_offered_rate", start_date, end_date, fields, source)
    if not data:
        return None
    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)
    return df


@export_as_api
@may_trim_bjse
def get_abnormal_stocks(start_date=None, end_date=None, types=None, market="cn"):
    """获取龙虎榜每日明细

    :param start_date: 开始日期
    :param end_date: 结束日期
    :param types: 异动类型代码

    :returns DataFrame"""
    start_date, end_date = ensure_date_range(start_date, end_date)
    if types:
        types = ensure_list_of_string(types, "types")
    data = get_client().execute("get_abnormal_stocks", start_date, end_date, types, market)
    if not data:
        return None
    df = pd.DataFrame.from_records(data)
    df["abnormal_e_date"] = df["date"]
    df.set_index(["order_book_id", "date"], inplace=True)
    # 固定返回的列, 确保其包括 change_rate, turnover_rate, amplitude, deviation
    columns = [
        "type", "abnormal_s_date", "abnormal_e_date", "volume",
        "total_turnover", "change_rate", "turnover_rate", "amplitude",
        "deviation", "reason"
    ]
    df = df.reindex(columns=columns)
    return df


@export_as_api
def get_abnormal_stocks_detail(order_book_ids, start_date=None, end_date=None, sides=None, types=None, market="cn"):
    """获取龙虎榜机构交易明细

    :param order_book_ids: 证券id
    :param start_date: 开始时间
    :param end_date: 结束时间
    :param sides: 交易方向, 可选值包括buy, sell, cum
    :param types: 异动类型代码

    :returns DataFrame
    """
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)
    if types:
        types = ensure_list_of_string(types, "types")
    if sides:
        sides = ensure_list_of_string(sides, "side")
        check_items_in_container(sides, ["buy", "sell", "cum"], "side")
    data = get_client().execute("get_abnormal_stocks_detail", order_book_ids, start_date, end_date, sides, types)
    if not data:
        return None
    df = pd.DataFrame.from_records(data)
    df.sort_values(["order_book_id", "date", "side", "rank"], inplace=True)
    df.set_index(["order_book_id", "date"], inplace=True)
    return df


BUY_BACK_FIELDS = [
    'seller',
    'procedure',
    'share_type',
    'announcement_dt',
    'buy_back_start_date',
    'buy_back_end_date',
    'write_off_date',
    'maturity_desc',
    'buy_back_volume',
    'volume_ceiling',
    'volume_floor',
    'buy_back_value',
    'buy_back_price',
    'price_ceiling',
    'price_floor',
    'currency',
    'purpose',
    'buy_back_percent',
    'value_floor',
    'value_ceiling',
    'buy_back_mode'
]


@export_as_api
@support_hk_order_book_id
def get_buy_back(
        order_book_ids,
        start_date=None,
        end_date=None,
        fields=None,
        market='cn'
):
    """ 获取股票回购数据

    :param order_book_ids: str/list, 证券id列表
    :param start_date: 开始时间
    :param end_date: 结束时间
    :param fields: str/list, 字段
    :param market: str, default 'cn'

    :return: pandas.DataFrame
    返回相关字段列表
        seller	股份被回购方
        procedure	事件进程
        share_type	股份类别
        announcement_dt	公告发布当天的日期时间戳
        buy_back_start_date	回购期限起始日
        buy_back_end_date	回购期限截至日
        write_off_date	回购注销公告日（该字段为空的时候代表这行记录尚未完成注销，有日期的时候代表已完成注销）
        maturity_desc	股份回购期限说明
        buy_back_volume	回购股数(股)(份)
        volume_ceiling	回购数量上限(股)(份)
        volume_floor	回购数量下限(股)(份)
        buy_back_value	回购总金额(元)
        buy_back_price	回购价格(元/股)(元/份)
        price_ceiling	回购价格上限(元)
        price_floor	回购价格下限(元)
        currency	货币单位
        purpose	回购目的
        buy_back_percent	占总股本比例
        value_floor	拟回购资金总额下限(元)
        value_ceiling	拟回购资金总额上限(元)
        buy_back_mode	股份回购方式
    """

    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)
    if fields is not None:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, BUY_BACK_FIELDS, 'buy_back')
    else:
        fields = BUY_BACK_FIELDS
    data = get_client().execute(
        "get_buy_back", order_book_ids, start_date, end_date, fields, return_create_tm=True, market=market
    )
    if not data:
        return None
    df = pd.DataFrame.from_records(data)
    df["rice_create_tm"] = pd.to_datetime(df["rice_create_tm"] + 3600 * 8, unit="s")
    df.set_index(["order_book_id", "date"], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api
@may_trim_bjse
def get_forecast_report_date(order_book_ids, start_quarter, end_quarter, market='cn'):
    """ 获取股票定期报告预约披露日数据

    :param order_book_ids: str/list, 证券id列表
    :param start_quarter: 开始季度
    :param end_quarter: 结束季度
    :param market:  (Default value = "cn")

    :return pandas.DataFrame
    MultiIndex of (order_book_id, quarter)
    其他字段:
        order_book_id           股票代码 (INDEX1)
        quarter                 季度 (INDEX2)
        info_date               公告日期
        first_forecast_date     首次预约日
        first_change_date       首次变更日
        second_change_date      二次变更日
        third_change_date       三次变更日
        actual_info_date        实际披露日
        rice_create_tm          米筐入库时间
    """
    order_book_ids = ensure_order_book_ids(order_book_ids)
    if start_quarter is not None:
        check_quarter(start_quarter, 'start_quarter')
        start_quarter = ensure_date_int(quarter_string_to_date(start_quarter))
    if end_quarter is not None:
        check_quarter(end_quarter, 'end_quarter')
        end_quarter = ensure_date_int(quarter_string_to_date(end_quarter))

    order_book_ids = ensure_order_book_ids(order_book_ids)

    data = get_client().execute(
        "get_forecast_report_date", order_book_ids, start_quarter, end_quarter, market=market
    )
    if not data:
        return None
    df = pd.DataFrame(data)
    df["rice_create_tm"] = pd.to_datetime(df["rice_create_tm"] + 3600 * 8, unit="s")
    df['info_date'] = int8_to_datetime_v(df['info_date'])
    df.set_index(['order_book_id', 'quarter'], inplace=True)
    df.sort_index(inplace=True)
    # keep special order
    df = df[['info_date', 'first_forecast_date', 'first_change_date', 'second_change_date', 'third_change_date', 'actual_info_date', 'rice_create_tm']]
    return df


@export_as_api
@may_trim_bjse
def get_leader_shares_change(
        order_book_ids,
        start_date=None,
        end_date=None,
        market='cn'
):
    """
    获取高管持股变动数据

    :param order_book_ids: str/list, 证券id列表
    :param start_date: 开始时间
    :param end_date: 结束时间
    :param market: str, default 'cn'

    :return pandas.DataFrame MultiIndex
    Index: ['order_book_id', 'change_date']
    返回字段:
        order_book_id   证劵代码 (INDEX1)
        change_date     变动日期 (INDEX2)
        leader_name     姓名
        position        职务
        shares_change   变动数(股)
        current_shares  变动后持股数(股)
        ratio_change    变动比例(%)
        price_change    变动价格
        change_reason   变动原因
        rice_create_tm  米筐入库时间
    """
    order_book_ids = ensure_order_book_ids(order_book_ids)
    start_date, end_date = ensure_date_range(start_date, end_date)
    data = get_client().execute(
        "get_leader_shares_change", order_book_ids, start_date, end_date, market=market
    )
    if not data:
        return None
    df = pd.DataFrame.from_records(data)
    df["rice_create_tm"] = pd.to_datetime(df["rice_create_tm"] + 3600 * 8, unit="s")
    df['change_date'] = int8_to_datetime_v(df['change_date'])
    df.set_index(['order_book_id', 'change_date'], inplace=True)
    df.sort_index(inplace=True)
    # keep special order
    df = df[['leader_name', 'position', 'shares_change', 'current_shares', 'ratio_change', 'price_change', 'change_reason', 'rice_create_tm']]
    return df
