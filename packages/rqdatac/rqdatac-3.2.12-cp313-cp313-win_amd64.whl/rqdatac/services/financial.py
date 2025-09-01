# -*- coding: utf-8 -*-
import datetime

import pandas as pd
import math

from rqdatac.client import get_client

from rqdatac.services.orm.pit_financials_ex import FIELDS_LIST_EX
from rqdatac.services.orm.hk_pit_financials_ex import HK_FIELDS_LIST_EX
from rqdatac.hk_decorators import support_hk_order_book_id
from rqdatac.validators import (
    ensure_list_of_string,
    ensure_string,
    check_items_in_container,
    ensure_date_int,
    ensure_order_book_id,
    check_quarter,
    ensure_date_or_today_int,
    quarter_string_to_date,
    ensure_order_book_ids,
)
from rqdatac.decorators import export_as_api

ENTERPRISE_TYPE_MAP = {
    13: "business_bank",
    31: "securities_firms",
    33: "trust",
    35: "insurance_company",
    39: "other_financial_institution",
    99: "general_enterprise",
}

INFO_TYPE_MAP = {
    10: "发行上市书",
    20: "定期报告",
    30: "业绩快报",
    50: "章程制度",
    70: "临时公告",
    90: "交易所通报",
    91: "交易所临时停(复)牌公告",
    99: "其他",
    110101: "定期报告:年度报告",
    110102: "定期报告:半年度报告",
    110103: "定期报告:第一季报",
    110104: "定期报告:第三季报",
    110105: "定期报告:审计报告",
    110106: "定期报告:第二季报",
    110107: "定期报告:第四季报",
    110108: "定期报告:第五季报",
    110109: "定期报告:第二季报（更正后）",
    110110: "定期报告:第四季报（更正后）",
    110111: "定期报告:第五季报（更正后）",
    110201: "定期报告:年度报告(关联方)",
    110202: "定期报告:半年度报告(关联方)",
    110203: "定期报告:第一季报(关联方)",
    110204: "定期报告:第三季报(关联方)",
    120101: "临时公告:审计报告(更正后)",
    120102: "临时公告:年度报告(更正后)",
    120103: "临时公告:半年度报告(更正后)",
    120104: "临时公告:第一季报(更正后)",
    120105: "临时公告:第三季报(更正后)",
    120106: "临时公告:公开转让说明书(更正后)",
    120107: "临时公告:业绩快报",
    120108: "临时公告:业绩快报(更正后)",
    120201: "临时公告:跟踪评级报告",
    120202: "临时公告:同业存单发行计划",
    120203: "临时公告:比较式财务报表",
    120204: "临时公告:关联方",
    120205: "临时公告:其他",
    120206: "临时公告:前期差错更正",
    120207: "临时公告:第一季度报告",
    120208: "临时公告:第二季度报告",
    120209: "临时公告:第三季度报告",
    120210: "临时公告:第四季度报告",
    120211: "临时公告：年度报告",
    130101: "发行上市书:募集说明书",
    130102: "发行上市书:招股说明书(申报稿)",
    130103: "发行上市书:招股意向书",
    130104: "发行上市书:上市公告书",
    130105: "发行上市书:审阅报告",
    130106: "发行上市书:招股说明书",
    130107: "发行上市书:公开转让说明书",
    130108: "发行上市书:发行公告",
    130109: "发行上市书:审计报告",
    130110: "发行上市书:关联方",
    130111: "发行上市书:其他",
    140101: "发行披露文件:第一季报",
    140102: "发行披露文件:半年度报告",
    140103: "发行披露文件：第三季报",
    140104: "发行披露文件：审计报告",
    140105: "发行披露文件：募集说明书",
    140106: "发行披露文件：跟踪评级报告"
}


@export_as_api
@support_hk_order_book_id
def get_pit_financials_ex(order_book_ids, fields, start_quarter, end_quarter,
                          date=None, statements='latest', market='cn'):
    """
        获取股票财务数据(Point In Time)
    :param order_book_ids: 股票合约代码列表
    :param fields: 指定返回财报字段
    :param start_quarter: 财报季度 - 起始，如 2020q1
    :param end_quarter: 财报季度 - 截止
    :param date: 财报发布日期，默认为当前日期, 如 '2020-01-01' | '20200101'
    :param statements: 可选 latest/all, 默认为 latest
            latest: 仅返回在date时点所能观察到的最新数据；
            all：返回在date时点所能观察到的所有版本，从第一次发布直到观察时点的所有修改。
    :param market: 股票市场范围
    :return:
    """
    fields = ensure_list_of_string(fields, 'fields')
    if market == "hk":
        check_items_in_container(fields, HK_FIELDS_LIST_EX, "fields")
        fields.extend(["fiscal_year", "standard"])
    else:
        check_items_in_container(fields, FIELDS_LIST_EX, "fields")
    fields.extend(['order_book_id', 'info_date', 'end_date', 'if_adjusted', 'rice_create_tm'])
    fields = list(set(fields))
    fields[fields.index("info_date")], fields[0] = fields[0], fields[fields.index("info_date")]

    check_quarter(start_quarter, 'start_quarter')
    start_quarter_int = ensure_date_int(quarter_string_to_date(start_quarter))

    check_quarter(end_quarter, 'end_quarter')
    end_quarter_int = ensure_date_int(quarter_string_to_date(end_quarter))

    if start_quarter > end_quarter:
        raise ValueError(
            'invalid quarter range: [{!r}, {!r}]'.format(
                start_quarter, end_quarter))

    date = ensure_date_or_today_int(date)

    order_book_ids = ensure_list_of_string(order_book_ids, 'order_book_ids')

    if statements not in ['all', 'latest']:
        raise ValueError("invalid statements , got {!r}".format(statements))

    pit_financial_df = pd.DataFrame(
        get_client().execute("get_pit_financials_ex", order_book_ids, fields, start_quarter_int, end_quarter_int, date,
                             statements, market))
    if pit_financial_df.empty:
        return
    # convert rice_create_tm to datetime
    pit_financial_df['rice_create_tm'] = pd.to_datetime(pit_financial_df['rice_create_tm'] + 3600 * 8, unit='s')
    pit_financial_df = pit_financial_df.reindex(columns=fields)
    pit_financial_df.sort_values(['order_book_id', 'end_date', 'info_date'])
    pit_financial_df["end_date"] = pit_financial_df["end_date"].apply(
        lambda d: "{}q{}".format(d.year, math.ceil(d.month / 3)))
    pit_financial_df.rename(columns={"end_date": "quarter"}, inplace=True)
    pit_financial_df.set_index(['order_book_id', 'quarter'], inplace=True)
    pit_financial_df['if_adjusted'] = pit_financial_df['if_adjusted'].map(lambda x: 1 if x == 1 else 0).astype(int)
    pit_financial_df.sort_index(inplace=True)
    return pit_financial_df


@export_as_api
@support_hk_order_book_id
def current_performance(
        order_book_ids, info_date=None, quarter=None, interval="1q", fields=None, market="cn"
):
    """获取A股快报

    :param order_book_ids: 股票合约代码列表
    :param info_date: 发布日期, 如'20180501', 默认为最近的交易日 (Default value = None)
    :param quarter: 发布季度, 如'2018q1' (Default value = None)
    :param interval: 数据区间， 发布日期, 如'2y', '4q' (Default value = "1q")
    :param fields: str 或 list 类型. 默认为 None, 返回所有字段 (Default value = None)
    :param market: 地区代码, 如'cn' (Default value = "cn")
    :returns: pd.DataFrame

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, 'CS', market=market)

    end_date = None
    if info_date:
        info_date = ensure_date_int(info_date)
    elif quarter:
        splited = quarter.lower().split("q")
        if len(quarter) != 6 or len(splited) != 2:
            raise ValueError(
                "invalid argument {}: {}, valid parameter: {}".format(
                    "quarter", quarter, "string format like '2016q1'"
                )
            )

        year, quarter = int(splited[0]), int(splited[1])
        if not 1 <= quarter <= 4:
            raise ValueError(
                "invalid argument {}: {}, valid parameter: {}".format(
                    "quarter", quarter, "quarter should be in [1, 4]"
                )
            )
        month, day = QUARTER_DATE_MAP[quarter]
        end_date = ensure_date_int(datetime.datetime(year, month, day))
    else:
        info_date = ensure_date_int(datetime.date.today())
    ensure_string(interval, "interval")
    if interval[-1] not in ("y", "q", "Y", "Q"):
        raise ValueError(
            "invalid argument {}: {}, valid parameter: {}".format(
                "interval", interval, "interval unit should be q(quarter) or y(year)"
            )
        )

    try:
        int(interval[:-1])
    except ValueError:
        raise ValueError(
            "invalid argument {}: {}, valid parameter: {}".format(
                "interval", interval, "string like 4q, 2y"
            )
        )
    interval = interval.lower()

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, PERFORMANCE_FIELDS, "fields")
    else:
        fields = PERFORMANCE_FIELDS

    data = get_client().execute(
        "current_performance_v2", order_book_ids, info_date, end_date, fields, market=market
    )
    if not data:
        return
    df = pd.DataFrame(data)
    df.sort_values(by=["order_book_id", "end_date", "info_date", "mark"], ascending=[True, False, False, True], inplace=True)
    df.drop_duplicates(subset=['order_book_id', "end_date"], keep="first", inplace=True)
    num = int(interval[:-1])
    unit = interval[-1]
    if unit == "y":
        latest_month = df.iloc[0]["end_date"].month
        df["month"] = df.end_date.apply(lambda x: x.month)
        df = df[df.month == latest_month]
    df.reset_index(drop=True, inplace=True)
    df = df.groupby('order_book_id').head(num)
    df.set_index(['order_book_id', 'end_date'], inplace=True)
    return df[['info_date'] + fields]


PERFORMANCE_FORECAST_FIELDS = [
    "forecast_type",
    "forecast_description",
    "forecast_growth_rate_floor",
    "forecast_growth_rate_ceiling",
    "forecast_earning_floor",
    "forecast_earning_ceiling",
    "forecast_np_floor",
    "forecast_np_ceiling",
    "forecast_eps_floor",
    "forecast_eps_ceiling",
    "net_profit_yoy_const_forecast",
    "forecast_ne_floor",
    "forecast_ne_ceiling",
]


@export_as_api
@support_hk_order_book_id
def performance_forecast(order_book_ids, info_date=None, end_date=None, fields=None, market="cn"):
    """获取业绩预报

    :param order_book_ids: 股票代码，如['000001.XSHE', '000002.XSHE']
    :param info_date: 信息发布日期，如'20180501'，默认为最近的交易日 (Default value = None)
    :param end_date: 业绩预计报告期，如'20180501'，默认为最近的交易日 (Default value = None)
    :param fields: str或list类型. 默认为None，返回所有字段 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: pd.DataFrame

    """
    order_book_ids = ensure_order_book_ids(order_book_ids, type='CS')
    if info_date:
        info_date = ensure_date_int(info_date)
    elif end_date:
        end_date = ensure_date_int(end_date)
    else:
        info_date = ensure_date_int(datetime.datetime.today())

    if fields:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, PERFORMANCE_FORECAST_FIELDS, "fields")
    else:
        fields = PERFORMANCE_FORECAST_FIELDS

    data = get_client().execute(
        "performance_forecast_v2", order_book_ids, info_date, end_date, fields, market=market
    )
    if not data:
        return

    have_rice_create_tm = "rice_create_tm" in data[0]
    if len(order_book_ids) > 1:
        columns = ["order_book_id", "info_date", "end_date"] + fields
    else:
        columns = ["info_date", "end_date"] + fields
    if have_rice_create_tm:
        columns.append("rice_create_tm")

    df = pd.DataFrame(data, columns=columns)

    if len(order_book_ids) > 1:
        df.set_index("order_book_id", inplace=True)
    if have_rice_create_tm:
        df['rice_create_tm'] = pd.to_datetime(df['rice_create_tm'] + 3600 * 8, unit='s')
    return df


PERFORMANCE_FIELDS = [
    "operating_revenue",
    "gross_profit",
    "operating_profit",
    "total_profit",
    "np_parent_owners",
    "net_profit_cut",
    "net_operate_cashflow",
    "total_assets",
    "se_parent_owners",
    "se_without_minority",
    "total_shares",
    "basic_eps",
    "eps_weighted",
    "eps_cut_epscut",
    "eps_cut_weighted",
    "roe",
    "roe_weighted",
    "roe_cut",
    "roe_cut_weighted",
    "net_operate_cashflow_per_share",
    "equity_per_share",
    "operating_revenue_yoy",
    "gross_profit_yoy",
    "operating_profit_yoy",
    "total_profit_yoy",
    "np_parent_minority_pany_yoy",
    "ne_t_minority_ty_yoy",
    "net_operate_cash_flow_yoy",
    "total_assets_to_opening",
    "se_without_minority_to_opening",
    "basic_eps_yoy",
    "eps_weighted_yoy",
    "eps_cut_yoy",
    "eps_cut_weighted_yoy",
    "roe_yoy",
    "roe_weighted_yoy",
    "roe_cut_yoy",
    "roe_cut_weighted_yoy",
    "net_operate_cash_flow_per_share_yoy",
    "net_asset_psto_opening",
]

QUARTER_DATE_MAP = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
