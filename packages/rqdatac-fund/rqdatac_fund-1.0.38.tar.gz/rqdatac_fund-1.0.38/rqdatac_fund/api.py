# -*- coding: utf-8 -*-
import datetime
import warnings
from collections import defaultdict
from functools import reduce

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api, ttl_cache
from rqdatac.services.basic import Instrument
from rqdatac.services.calendar import get_trading_dates_in_type
from rqdatac.utils import to_date, to_datetime, pd_version, is_panel_removed
from rqdatac.validators import (
    ensure_date_str,
    ensure_date_int,
    ensure_list_of_string,
    ensure_string_in,
    check_items_in_container,
    ensure_trading_date,
    ensure_date_range,
    raise_for_no_panel,
    check_type
)
from rqdatac.rqdatah_helper import rqdatah_serialize, http_conv_instruments


def _get_instrument(order_book_id, market="cn"):
    d = _all_instruments_dict(market)
    return d.get(order_book_id)


@ttl_cache(3 * 3600)
def _all_instruments_list(market):
    il = [Instrument(i) for i in get_client().execute("fund.all_instruments", market)]
    il.sort(key=lambda i: i.order_book_id)
    return il


@ttl_cache(3 * 3600)
def _all_instruments_dict(market):
    all_list = _all_instruments_list(market)
    d = {}
    for i in all_list:
        d[i.order_book_id] = i
        d[i.symbol] = i

    return d


def ensure_fund(ob, market="cn"):
    try:
        return _all_instruments_dict(market)[ob].order_book_id
    except KeyError:
        warnings.warn("invalid order_book_id: {}".format(ob))
        return None

def ensure_obs(order_book_ids, market="cn"):
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    order_book_ids = list(set(order_book_ids))
    validated_order_book_ids = []
    for oid in order_book_ids:
        validated_oid = ensure_fund(oid, market)
        if validated_oid is not None:
            validated_order_book_ids.append(validated_oid)
    if not validated_order_book_ids:
        raise ValueError("No valid fund order book ids provided")
    return validated_order_book_ids


class MainCodeMap:
    DATE_MIN = 20010101
    relation_dict = {
        "multi_currency": 0,
        "multi_share": 1,
        "parent_and_child": 2,
    }

    def __init__(self):
        self.relations = defaultdict(list)
        self.main_code_map = {}
        self.DATE_MAX = ensure_date_int(datetime.date.today())


    def add_relation(self, order_book_id, related_ob, start_date, end_date, relation_type):
        start_date = ensure_date_int(start_date) if start_date else self.DATE_MIN
        end_date = ensure_date_int(end_date) if end_date else self.DATE_MAX
        relation_type = self.relation_dict.get(relation_type, -1)
        self.relations[order_book_id].append((related_ob, start_date, end_date, relation_type))
    

    def gen_map(self):
        for order_book_id, relations in self.relations.items():
            relations = sorted(relations, key=lambda x: x[3])
            indexs = sorted(list(set(
                # 取 relations 中的所有端点值生成 indexs
                # 这里多加了个 end+1 是因为需要考虑 ob 在转型后自己作为 main_code 的情况，需要用 fillna 填充自己的 ob
                reduce(lambda x, y: x + y, [[x[1] + 1, x[2], x[2] + 1] for x in relations])
            )))
            series = pd.Series(index=indexs)
            for related_ob, start, end, _ in relations:
                # ob 在 end 这一天还可能有数据，所以这里取到 end
                # 用 start+1 的原因是 start 可能会和其他 relation 的 end 相等
                series.loc[start + 1:end] = related_ob
            series = series.fillna(order_book_id)
            series.drop_duplicates(inplace=True, keep='first')
            self.main_code_map[order_book_id] = series
    

    def get_main_code(self, order_book_id, start_date=None, end_date=None):
        if order_book_id not in self.main_code_map:
            return [order_book_id]
        if start_date is None and end_date is None:
            return self.main_code_map[order_book_id].tolist()
        start_date = ensure_date_int(start_date)
        end_date = ensure_date_int(end_date)
        result = []
        series = self.main_code_map[order_book_id]
        # 从后往前，如果 date <= start_date，则后面无需再判断
        for date in reversed(series.index):
            if date <= start_date:
                result.append(series.loc[date])
                break
            if date <= end_date:
                result.append(series.loc[date])
        return result


@ttl_cache(3 * 3600)
def _all_main_code_map(market):
    relation_documents = get_client().execute("fund.get_related_code", None,
                                              relation_types=["multi_share", "parent_and_child", "multi_currency"],
                                              market=market)
    if not relation_documents:
        return {}
    
    map = MainCodeMap()
    for doc in relation_documents:
        map.add_relation(doc["related_id"], doc["order_book_id"], doc["effective_date"], doc["cancel_date"], doc["type"])
    map.gen_map()
    return map


def to_main_code(order_book_ids, start_date=None, end_date=None, market='cn'):
    """获取基金的主基金

    :param order_book_ids: 基金代码或者基金代码列表
    :param start_date: 开始日期，如果不指定，则返回所有时间段的主基金
    :param end_date: 结束日期，如果不指定，则返回所有时间段的主基金
    :param market:  (Default value = 'cn')
    :returns: DataFrame

    """ 
    main_code_map = _all_main_code_map(market)
    # 单天查询，需要回溯最近的有数据的一天，无法确定最近的一天在哪个区间，因此在该天之前的区间 main_code 都要返回
    if start_date == end_date and start_date is not None:
        start_date = main_code_map.DATE_MIN
    return {
        ob: main_code_map.get_main_code(ob, start_date, end_date)
        for ob in order_book_ids
    }


def main_code_flattern(main_codes):
    """把 main_code 列表平铺并去重"""
    return list(set(code for codes in main_codes.values() for code in codes))


def with_secondary_fund(main_codes, data, date_type='range'):
    """将主基金与次级基金关联的函数

    :param main_codes: 主基金代码列表
    :param data: 获取并处理好的数据，DataFrame
    :param date_type:  数据的区间类型，'range': 返回一个区间内数据，'date': 返回离某一天最近的数据
                       对于'date'类型，需要做额外处理，因为 main_codes 可能有多个，需要取返回数据中最近的那个
                       (Default value = 'range')
    :returns: DataFrame
    
    """
    if not main_codes or data is None or data.empty:
        return data
    # 把所有 main_code 都不在 data 中的 ob 过滤掉
    main_codes = {
        k: v for k,v in main_codes.items()
        if set(v) & set(data.index.levels[0])
    }
    order_book_ids = main_codes.keys()
    main_codes = main_codes.values()
    if date_type == 'date':
        main_codes = [
            # 遍历每个 ob 的 main_codes，拿到对应数据的日期，取最近的那个
            sorted(
                (data.loc[id].index.values[-1], id) for id in codes if id in data.index.levels[0]
            )[-1][1]
            for codes in main_codes 
        ]
    index_names = list(data.index.names)
    related_oid_establishment_df = pd.DataFrame({
        '_oids': order_book_ids,
        index_names[0]: main_codes,
        '_establishment_date': [ _get_instrument(oid).establishment_date for oid in order_book_ids]
    })
    related_oid_establishment_df = related_oid_establishment_df.explode(index_names[0])
    related_oid_establishment_df['_establishment_date'] = pd.to_datetime(related_oid_establishment_df['_establishment_date'], format='%Y-%m-%d')
    data.reset_index(inplace=True)
    data = data.merge(related_oid_establishment_df, how='inner', on=index_names[0])
    data = data[data[index_names[1]] >= data['_establishment_date']]
    # 对于主次基金上架日期不一致修正后，会出现空值情况，对此统一返回 None
    if data.empty:
        return
    data.drop([index_names[0], '_establishment_date'], axis=1, inplace=True)
    data.rename(columns={'_oids': index_names[0]}, inplace=True)
    data.set_index(index_names, inplace=True)
    data.sort_index(inplace=True)
    return data


@export_as_api(namespace="fund")
def all_instruments(date=None, market="cn"):
    """获取全部基金信息

    :param date: 该参数表示过滤掉 listed_date 晚于当日的基金，默认为 None，表示获取全部基金信息，不进行过滤。 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    a = _all_instruments_list(market)
    if date is not None:
        date = ensure_date_str(date)
        a = [i for i in a if i.listed_date < date]

    df = pd.DataFrame(
        [
            [
                v.order_book_id,
                v.establishment_date,
                v.listed_date,
                v.transition_time,
                v.amc,
                v.symbol,
                v.fund_type,
                v.fund_manager,
                v.latest_size,
                v.benchmark,
                v.accrued_daily,
                v.de_listed_date,
                v.stop_date,
                v.exchange,
                v.round_lot,
            ]
            for v in a
        ],
        columns=[
            "order_book_id",
            "establishment_date",
            "listed_date",
            "transition_time",
            "amc",
            "symbol",
            "fund_type",
            "fund_manager",
            "latest_size",
            "benchmark",
            "accrued_daily",
            "de_listed_date",
            "stop_date",
            "exchange",
            "round_lot",
        ],
    )
    df = df[6 == df["order_book_id"].str.len()]
    df = df.drop_duplicates().sort_values(['order_book_id', 'listed_date'])
    return df.reset_index(drop=True)


@export_as_api(namespace="fund")
@rqdatah_serialize(converter=http_conv_instruments)
def instruments(order_book_ids, market="cn"):
    """获取基金详细信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param market:  (Default value = "cn")
    :returns: Instrument object or list of Instrument object
            取决于参数是一个 order_book_id 还是多个 order_book_id

    """
    order_book_ids = ensure_list_of_string(order_book_ids)
    if len(order_book_ids) == 1:
        return _get_instrument(order_book_ids[0])
    d = _all_instruments_dict(market)
    return [d[i] for i in order_book_ids if i in d]


NAV_FIELDS = (
    "acc_net_value",
    "unit_net_value",
    "change_rate",
    "adjusted_net_value",
    "daily_profit",
    "weekly_yield",
)


@export_as_api(namespace="fund")
def get_nav(order_book_ids, start_date=None, end_date=None, fields=None, expect_df=False, market="cn"):
    """获取基金净值数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param fields: str or list of str，例如：'acc_net_value', 'unit_net_value',
                    'subscribe_status', 'redeem_status', 'change_rate' (Default value = None)
    :param expect_df: 返回 MultiIndex DataFrame (Default value = False)
    :param market:  (Default value = "cn")
    :returns: DataFrame or Series or Panel

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields)
        for f in fields:
            if f not in NAV_FIELDS:
                raise ValueError("invalid field: {}".format(f))
    else:
        fields = NAV_FIELDS

    result = get_client().execute(
        "fund.get_nav", order_book_ids, start_date, end_date, fields, market=market
    )
    if not result:
        return
    result = pd.DataFrame(result)
    result = result.fillna(np.nan)

    if not is_panel_removed and not expect_df:
        result = result.set_index(["datetime", "order_book_id"])
        result.reindex(columns=fields)
        result = result.to_panel()
        if len(order_book_ids) == 1:
            result = result.minor_xs(order_book_ids[0])
        if len(fields) == 1:
            return result[fields[0]]
        if len(order_book_ids) != 1 and len(fields) != 1:
            warnings.warn("Panel is removed after pandas version 0.25.0."
                          " the default value of 'expect_df' will change to True in the future.")
        return result
    else:
        result.sort_values(["order_book_id", "datetime"], inplace=True)
        result.set_index(["order_book_id", "datetime"], inplace=True)
        result.reindex(columns=fields)
        if expect_df:
            return result

        if len(order_book_ids) != 1 and len(fields) != 1:
            raise_for_no_panel()

        if len(order_book_ids) == 1:
            result.reset_index(level=0, inplace=True, drop=True)
            if len(fields) == 1:
                result = result[fields[0]]
        else:
            field = result.columns[0]
            result = result.unstack(0)[field]

        return result


@export_as_api(namespace="fund")
def get_holdings(order_book_ids, date=None, market="cn", **kwargs):
    """获取距离指定日期最近发布的基金持仓信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 日期，为空则返回所有持仓 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    def _remove_old_secucode(df):
        # df 包括了单个id当天的所有记录.
        # 由于基金可能发生转型, 导致 df 中 fund_id 相同, 但是 secu_code 不同的情况
        # 当出现这种情况时, 只需要保留纯数字的 secu_code
        if len(set(df["secu_code"])) > 1:
            return df[df["secu_code"].str.isdigit()]
        return df

    order_book_ids = ensure_obs(order_book_ids, market)

    if date is not None:
        date = ensure_date_int(date)
        start_date = end_date = None
        main_codes = to_main_code(order_book_ids, date, date, market)
        date_type = 'date'
    else:
        if "start_date" in kwargs and "end_date" in kwargs:
            start_date = ensure_date_int(kwargs.pop("start_date"))
            end_date = ensure_date_int(kwargs.pop("end_date"))
        elif "start_date" in kwargs or "end_date" in kwargs:
            raise ValueError('please ensure start_date and end_date exist')
        else:
            start_date = end_date = None
        main_codes = to_main_code(order_book_ids, start_date, end_date, market)
        date_type = 'range'
    main_obs = main_code_flattern(main_codes)
    if kwargs:
        raise ValueError('unknown kwargs: {}'.format(kwargs))

    df = get_client().execute("fund.get_holdings_v4", main_obs, date, start_date, end_date, market=market)
    if not df:
        return

    df = pd.DataFrame(data=df)
    fields = ["type", "weight", "shares", "market_value", "symbol"]
    if "category" in df.columns:
        fields += ["category"]
    if "region" in df.columns:
        fields += ["region"]

    df.sort_values(["fund_id", "date", "type", "order_book_id"], inplace=True)
    df.set_index(["fund_id", "date"], inplace=True)
    # backward compatibility
    if "secu_code" in df.columns:
        df = df.groupby(["fund_id", "date"], group_keys=False).apply(_remove_old_secucode)
        df.drop(columns=["secu_code"], inplace=True)
    return with_secondary_fund(main_codes, df.sort_index(), date_type=date_type)


@export_as_api(namespace="fund")
def get_split(order_book_ids, market="cn"):
    """获取基金拆分信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param market:  (Default value = "cn")
    :returns: DataFrame
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    data = get_client().execute("fund.get_split", order_book_ids, market=market)
    if not data:
        return
    df = pd.DataFrame(data, columns=["order_book_id", "split_ratio", "ex_dividend_date"])
    return df.set_index(["order_book_id", "ex_dividend_date"]).sort_index()


@export_as_api(namespace="fund")
def get_dividend(order_book_ids, market="cn"):
    """获取基金分红信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    data = get_client().execute("fund.get_dividend", order_book_ids, market=market)
    if not data:
        return

    df = pd.DataFrame(
        data,
        columns=["order_book_id", "book_closure_date", "payable_date", "dividend_before_tax", "ex_dividend_date"],
    )
    return df.set_index(["order_book_id", "ex_dividend_date"]).sort_index()


@export_as_api(namespace="fund")
def get_manager(order_book_ids, expect_df=True, market="cn"):
    """获取基金经理信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param market:  (Default value = "cn")
    :param expect_df: 返回 MultiIndex DataFrame (Default value = True)
    :returns: DataFrame or Panel

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    docs = get_client().execute("fund.get_manager", order_book_ids, market=market)
    if not docs:
        return

    if not expect_df and not is_panel_removed:
        data = {}
        fields = []
        for doc in docs:
            data.setdefault(doc["order_book_id"], []).append(doc)
            doc.pop('order_book_id')
            if len(fields) < len(doc.keys()):
                fields = list(doc.keys())
        array = np.full((len(fields), max([len(v) for v in data.values()]), len(order_book_ids)), None)
        for i in range(max([len(v) for v in data.values()])):
            for j, order_book_id in enumerate(order_book_ids):
                try:
                    doc = data.setdefault(order_book_id, [])[i]
                except IndexError:
                    doc = None

                for k, f in enumerate(fields):
                    v = None if doc is None else doc[f]
                    array[k, i, j] = v
        result = pd.Panel(data=array, items=fields, minor_axis=order_book_ids)
        if len(order_book_ids) == 1:
            return result.minor_xs(order_book_ids[0])
        warnings.warn("Panel is removed after pandas version 0.25.0."
                      " the default value of 'expect_df' will change to True in the future.")
        return result
    else:
        df = pd.DataFrame(docs)
        df.sort_values(["order_book_id", "start_date"], inplace=True)
        df.set_index(["order_book_id", "id"], inplace=True)
        if expect_df:
            return df
        if len(order_book_ids) == 1:
            return df.reset_index(level=0, drop=True)

        raise_for_no_panel()


@export_as_api(namespace="fund")
def get_manager_info(manager_id, fields=None, market="cn"):
    """获取基金经理个人信息

    :param manager: 可以使用人员编码（如'101000002'）或姓名（如'江辉'），str 或 list of str
    :param fields: str or list of str，例如："gender", "region", (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    manager_id = ensure_list_of_string(manager_id)
    # 检查manager中是否同时有人员编码或姓名
    if len(set(map(lambda x: x.isdigit(), manager_id))) > 1:
        raise ValueError("couldn't get manager_id and name at the same time")

    manager_fields = ["gender", "region", "birthdate", "education", "practice_date", "experience_time", "background"]
    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, manager_fields, "fields")
    else:
        fields = manager_fields
    result = get_client().execute("fund.get_manager_info", manager_id, fields, market=market)
    if not result:
        warnings.warn("manager_id/manager_name does not exist")
        return

    df = pd.DataFrame(result).set_index("id")
    fields.insert(0, "chinesename")
    df.sort_index(inplace=True)
    return df[fields]


@export_as_api(namespace="fund")
def get_asset_allocation(order_book_ids, date=None, market="cn"):
    """获取指定日期最近发布的基金资产配置信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 日期，为空则返回所有时间段的数据 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date is not None:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    df = get_client().execute("fund.get_asset_allocation_v2", main_obs, date, market=market)
    if not df:
        return

    columns = [
        "order_book_id", "datetime", "info_date",
        "stock", "bond", "fund", "cash", "other", "nav", "net_asset", "total_asset"
    ]
    df = pd.DataFrame(df, columns=columns)
    df["datetime"] = pd.to_datetime(df["datetime"])
    warnings.warn("'nav' is deprecated. Please use 'net_asset' instead")
    df = df.set_index(["order_book_id", "datetime"]).sort_index()
    return with_secondary_fund(main_codes, df, date_type=date_type)


@export_as_api(namespace="fund")
def get_ratings(order_book_ids, date=None, market="cn"):
    """获取距离指定日期最近发布的基金评级信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 日期，为空则返回所有时间段的数据 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if date is not None:
        date = ensure_date_int(date)

    df = get_client().execute("fund.get_ratings_v2", order_book_ids, date, market=market)
    if not df:
        return

    df = pd.DataFrame(df, columns=["order_book_id", "datetime", "zs", "sh3", "sh5", "jajx"])
    df.sort_values(["order_book_id", "datetime"], inplace=True)
    if date is not None:
        df.drop_duplicates(subset=['order_book_id'], keep='last', inplace=True)
    df.set_index(["order_book_id", "datetime"], inplace=True)
    df.fillna(np.nan, inplace=True)
    return df.sort_index()


@export_as_api(namespace="fund")
def get_units_change(order_book_ids, date=None, market="cn"):
    """获取距离指定日期最近发布的基金认购赎回信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 日期，为空则返回所有时间段的数据 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if date is not None:
        date = ensure_date_int(date)

    df = get_client().execute("fund.get_units_change_v2", order_book_ids, date, market=market)
    if not df:
        return

    df = pd.DataFrame(df)
    return df.set_index(["order_book_id", "datetime"]).sort_index()
    

@export_as_api(namespace="fund")
def get_daily_units(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取距离指定日期最近发布的基金认购赎回信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始时间, 如果为空, 则不限制
    :param end_date: 结束时间, 如果为空, 则不限制
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if start_date and end_date and end_date < start_date:
        raise ValueError()

    df = get_client().execute(
        "fund.get_daily_units", order_book_ids, start_date, end_date, market=market
    )
    if not df:
        return

    df = pd.DataFrame(df)
    return df.set_index(["order_book_id", "datetime"]).sort_index()


@export_as_api(namespace="fund")
def get_ex_factor(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取公募基金复权因子

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 如 '2013-01-04' (Default value = None)
    :param end_date: 如 '2014-01-04' (Default value = None)
    :param market:  (Default value = "cn")
    :returns: 如果有数据，返回一个DataFrame, 否则返回None

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if start_date and end_date and end_date < start_date:
        raise ValueError()
    data = get_client().execute("fund.get_ex_factor", order_book_ids, start_date, end_date, market=market)
    if not data:
        return

    df = pd.DataFrame(
        data,
        columns=["order_book_id", "ex_factor", "ex_cum_factor", "ex_end_date", "ex_date"]
    )
    return df.set_index(["order_book_id", "ex_date"]).sort_index()


@export_as_api(namespace="fund")
def get_industry_allocation(order_book_ids, date=None, market="cn"):
    """获取指定日期最近发布的基金行业配置信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 日期，为空则返回所有时间段的数据 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date is not None:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    df = get_client().execute("fund.get_industry_allocation_v2", main_obs, date, market=market)
    if not df:
        return
    # 指定字段排序
    df = pd.DataFrame(df, columns=["standard", "industry", "weight", "market_value", "order_book_id", "datetime"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index(["order_book_id", "datetime"]).sort_index()
    return with_secondary_fund(main_codes, df, date_type=date_type)


@export_as_api(namespace="fund")
def get_indicators(order_book_ids, start_date=None, end_date=None, fields=None, rule="ricequant",
                   indicator_type="value", market="cn"):
    """获取基金衍生数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param fields: str or list of str (Default value = None)
    :param rule:  str, 可选：["ricequant"] (Default value = "ricequant")
    :param indicator_type: str, 可选：["value", "rank"] (Default value = "value")
    :param market:  (Default value = "cn")
    :returns: DataFrame or Series

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    check_items_in_container(rule, ["ricequant"], "rule")
    check_items_in_container(indicator_type, ["rank", "value"], "indicator_type")

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
    result = get_client().execute("fund.get_indicators", order_book_ids, start_date, end_date, fields, rule=rule,
                                  indicator_type=indicator_type, market=market)
    if not result:
        return

    df = pd.DataFrame(result).set_index(keys=["order_book_id", "datetime"])
    df.sort_index(inplace=True)

    if "update_time" in df.columns:
        df.drop(columns="update_time", inplace=True)

    if fields is not None:
        return df[fields]

    # benckmark列挪到第一位
    if 'benchmark' in df.columns:
        cols = list(df.columns.values)
        cols.remove('benchmark')
        df.reindex(columns=['benchmark'] + cols)

    return df


@export_as_api(namespace="fund")
def get_snapshot(order_book_ids, fields=None, rule="ricequant", indicator_type="value", market="cn"):
    """获取基金的最新数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param fields: str or list of str，例如："last_week_return", "subscribe_status", (Default value = None)
    :param rule:  str, 可选：["ricequant"] (Default value = "ricequant")
    :param indicator_type: str, 可选：["value", "rank"] (Default value = "value")
    :param market:  (Default value = "cn")
    :returns: DataFrame or Series

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    check_items_in_container(rule, ["ricequant"], "rule")
    check_items_in_container(indicator_type, ["value", "rank"], "indicator_type")

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")

    if indicator_type == "value":
        result = get_client().execute("fund.get_snapshot", order_book_ids, fields, rule=rule, market=market)
    elif indicator_type == "rank":
        result = get_client().execute("fund.get_snapshot_rank", order_book_ids, fields, rule=rule, market=market)
    if not result:
        return

    if rule == "ricequant":
        df = pd.DataFrame(result)
        df.rename(columns={'latest_date': 'datetime'}, inplace=True)
        df.set_index(["order_book_id", "datetime"], inplace=True)
    else:
        df = pd.DataFrame(result).set_index("order_book_id")
    df.sort_index(inplace=True)
    if fields is not None:
        return df[fields]

    # update_time是清洗生成的时间 不需要返回
    if "update_time" in df.columns:
        df.drop(columns="update_time", inplace=True)

    # benckmark列挪到第一位
    if 'benchmark' in df.columns:
        cols = list(df.columns.values)
        cols.remove('benchmark')
        df.reindex(columns=['benchmark'] + cols)

    return df


@export_as_api(namespace="fund")
def get_manager_indicators(manager_ids, start_date=None, end_date=None, fields=None,
                           asset_type="stock", manage_type="all", rule="ricequant", market="cn"):
    """获取基金衍生数据

    :param manager_ids: 基金经理代码，str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param fields: str or list of str (Default value = None)
    :param asset_type: 	资产种类, 股票型-stock, 债券型-bond，默认返回stock
    :param manage_type: 管理方式, 全产品-all， 独管-independent，默认返回all
    :param rule:  str, 可选：["ricequant"] (Default value = "ricequant")
    :param market:  (Default value = "cn")
    :returns: DataFrame or Series

    """
    manager_ids = ensure_list_of_string(manager_ids)
    check_items_in_container(rule, ["ricequant"], "rule")
    check_items_in_container(asset_type, ["stock", "bond"], "asset_type")
    check_items_in_container(manage_type, ["all", "independent"], "manage_type")

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
    result = get_client().execute("fund.get_manager_indicators", manager_ids, start_date, end_date, fields,
                                  asset_type=asset_type, manage_type=manage_type, rule=rule, market=market)
    if not result:
        return

    df = pd.DataFrame(result).set_index(keys=["manager_id", "datetime"])
    df.sort_index(inplace=True)
    if fields is not None:
        return df[fields]
    return df


@export_as_api(namespace="fund")
def get_related_code(order_book_ids, market="cn"):
    """get_related_code

    :param order_book_ids: 基金代码，str 或 list of str
    :param market:  (Default value = "cn")
    :returns: DataFrame or Series

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    result = get_client().execute("fund.get_related_code", order_book_ids, market=market)
    if not result:
        return
    df = pd.DataFrame(result, columns=["order_book_id", "related_id", "type", "effective_date", "cancel_date"])
    df.rename(columns={"order_book_id": "main_code", "related_id": "related_code"}, inplace=True)
    return df


@export_as_api(namespace="fund")
def get_etf_components(order_book_ids, trading_date=None, market="cn"):
    """获取etf基金份额数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param trading_date: 交易日期，默认为当天
    :param market: (Default value = "cn")
    :return: DataFrame

    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    ids_with_suffix = []
    for order_book_id in order_book_ids:
        if order_book_id.endswith(".XSHG") or order_book_id.endswith(".XSHE"):
            ids_with_suffix.append(order_book_id)
        elif order_book_id.startswith("1"):
            ids_with_suffix.append(order_book_id + ".XSHE")
        elif order_book_id.startswith("5"):
            ids_with_suffix.append(order_book_id + ".XSHG")
    if not ids_with_suffix:
        return

    if trading_date is not None:
        trading_date = to_date(trading_date)
        if trading_date > datetime.date.today():
            return
    else:
        trading_date = datetime.date.today()
    trading_date = ensure_date_int(ensure_trading_date(trading_date))

    result = get_client().execute("fund.get_etf_components_v2", ids_with_suffix, trading_date, market=market)
    if not result:
        return

    columns = ["trading_date", "order_book_id", "stock_code", "stock_amount", "cash_substitute",
               "cash_substitute_proportion", "fixed_cash_substitute", "redeem_cash_substitute"]
    df = pd.DataFrame(result, columns=columns)
    df.sort_values(by=["order_book_id", "trading_date", "stock_code"], inplace=True)
    df.set_index(["order_book_id", "trading_date"], inplace=True)
    return df.sort_index()


@export_as_api(namespace="fund")
def get_stock_change(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金报告期内重大股票持仓变动情况

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)
    main_codes = to_main_code(order_book_ids, start_date, end_date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_stock_change_v2", main_obs, start_date, end_date, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df = df.set_index(["fund_id", "date"]).sort_index()
    df = df[['order_book_id', 'market_value', 'weight', 'change_type']]
    return with_secondary_fund(main_codes, df)


@export_as_api(namespace="fund")
def get_term_to_maturity(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取货币型基金的持仓剩余期限

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)
    main_codes = to_main_code(order_book_ids, start_date, end_date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_term_to_maturity", main_obs, start_date, end_date, market=market)
    if result:
        result = [i for i in result if i is not None]
    if not result:
        return
    df = pd.DataFrame(result)
    df = df[['order_book_id', 'date', '0_30', '30_60', '60_90', '90_120', '120_397', '90_180', '>180']]
    df.set_index(['order_book_id', 'date'], inplace=True)
    df = df.stack().reset_index()
    if pd_version >= "0.21":
        df = df.set_axis(['order_book_id', 'date', 'term', 'weight'], axis=1, copy=False)
    else:
        df.set_axis(1, ['order_book_id', 'date', 'term', 'weight'])
    df = df.set_index(['order_book_id', 'date']).sort_index()
    df.dropna(inplace=True)
    return with_secondary_fund(main_codes, df)


@export_as_api(namespace="fund")
def get_bond_stru(order_book_ids, date=None, market="cn"):
    """获取指定日期公募基金债券持仓券种明细信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 日期，为空则返回所有时间段的数据 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date is not None:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    data = get_client().execute("fund.get_bond_stru_v2", main_obs, date, market=market)
    if not data:
        return
    df = pd.DataFrame(data)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    df = df[['bond_type', 'weight_nv', 'weight_bond_mv', 'market_value']]
    return with_secondary_fund(main_codes, df, date_type=date_type)


export_as_api(get_bond_stru, namespace='fund', name='get_bond_structure')

AMC_FIELDS = ["amc_id", "amc", "establishment_date", "reg_capital"]


@export_as_api(namespace="fund")
def get_amc(amc_ids=None, fields=None, market="cn"):
    """获取基金公司详情信息

    :param amc_ids: 基金公司id或简称，默认为 None
    :param fields: 可选参数。默认为所有字段。 (Default value = None)
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    if fields is None:
        fields = AMC_FIELDS
    else:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, AMC_FIELDS, "fields")

    result = get_client().execute("fund.get_amc", market=market)
    if amc_ids:
        amc_ids = ensure_list_of_string(amc_ids)
        amcs = tuple(amc_ids)
        result = [i for i in result if i["amc_id"] in amc_ids or i["amc"].startswith(amcs)]

    if not result:
        return
    return pd.DataFrame(result)[fields]


@export_as_api(namespace="fund")
def get_credit_quality(order_book_ids, date=None, market="cn"):
    """获取基金信用风险数据信息

    :param order_book_ids: 基金代码，str 或 list of str
    :param date: 交易日期，默认返回所有
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    date_type = 'range'
    if date:
        date = ensure_date_int(date)
        date_type = 'date'
    main_codes = to_main_code(order_book_ids, date, date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_credit_quality", main_obs, date, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df.rename(columns={"t_type": "bond_sector_rating_type"}, inplace=True)
    df.sort_values(["order_book_id", "date", "bond_sector_rating_type", "credit_rating"], inplace=True)
    df.set_index(["order_book_id", "date"], inplace=True)
    return with_secondary_fund(main_codes, df.sort_index(), date_type=date_type)


@export_as_api(namespace="fund")
def get_irr_sensitivity(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金利率风险敏感性分析数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期, 如'2013-01-04'
    :param end_date: 结束日期, 如'2014-01-04'；在 start_date 和 end_date 都不指定的情况下，默认为最近6个月
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    start_date, end_date = ensure_date_range(start_date, end_date, delta=relativedelta(months=6))
    result = get_client().execute("fund.get_irr_sensitivity_v2", order_book_ids, start_date, end_date, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    return df


@export_as_api(namespace="fund")
def get_etf_cash_components(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取现金差额数据

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期, 如'2013-01-04', 如果不传入, 则默认不限制开始日期
    :param end_date: 结束日期, 如'2014-01-04', 如果不传入, 则默认为今天
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)

    # 用户可能传入不带后缀的id, 这里统一处理成带后缀的id.
    for indx in range(len(order_book_ids)):
        if order_book_ids[indx].endswith(".XSHG") or order_book_ids[indx].endswith(".XSHE"):
            pass
        elif order_book_ids[indx].startswith("1"):
            order_book_ids[indx] = order_book_ids[indx] + ".XSHE"
        elif order_book_ids[indx].startswith("5"):
            order_book_ids[indx] = order_book_ids[indx] + ".XSHG"
        else:
            pass

    if end_date is None:
        end_date = datetime.date.today()
    end_date = ensure_date_int(end_date)

    if start_date is not None:
        start_date = ensure_date_int(start_date)

    result = get_client().execute(
        "fund.get_etf_cash_components", order_book_ids, start_date, end_date, market=market
    )
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "date"])
    df.sort_index(inplace=True)
    return df


AMC_TYPES = ['total', 'equity', 'hybrid', 'bond', 'monetary', 'shortbond', 'qdii']


@export_as_api(namespace="fund")
def get_amc_rank(amc_ids, date=None, type=None, market="cn"):
    """获取基金公司排名

    :param amc_ids: 基金公司代码，str or list
    :param date: 规模截止时间
    :param type: 基金类型，str or list
    :param market: (Default value = "cn")
    :return: DataFrame
    """
    amc_ids = ensure_list_of_string(amc_ids)
    if date:
        date = ensure_date_int(date)
    if type is not None:
        type = ensure_list_of_string(type)
        check_items_in_container(type, AMC_TYPES, "type")

    result = get_client().execute("fund.get_amc_rank", amc_ids, date, type, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df = df.set_index(keys=['amc_id', 'type'])
    df.sort_values('date', inplace=True)
    return df


@export_as_api(namespace="fund")
def get_holder_structure(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取基金持有人结构

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期, 如'2013-01-04', 如果不传入, 则默认不限制开始日期
    :param end_date: 结束日期, 如'2014-01-04', 如果不传入, 则默认为今天
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    if end_date is not None:
        end_date = ensure_date_int(end_date)

    if start_date is not None:
        start_date = ensure_date_int(start_date)

    result = get_client().execute(
        "fund.get_holder_structure", order_book_ids, start_date, end_date, market=market)
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "date"])
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace="fund")
def get_qdii_scope(order_book_ids, start_date=None, end_date=None, market="cn"):
    """获取QDII地区配置

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期, 如'2013-01-04', 如果不传入, 则默认不限制开始日期
    :param end_date: 结束日期, 如'2014-01-04', 如果不传入, 则默认为今天
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    main_codes = to_main_code(order_book_ids, start_date, end_date, market)
    main_obs = main_code_flattern(main_codes)

    result = get_client().execute("fund.get_qdii_scope", main_obs, start_date, end_date, market=market)
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "date"])
    df.sort_index(inplace=True)
    return with_secondary_fund(main_codes, df)


@export_as_api(namespace="fund")
def get_benchmark(order_book_ids, market="cn"):
    """获取基金基准

    :param order_book_ids: 基金代码，str 或 list of str
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    result = get_client().execute(
        "fund.get_benchmark", order_book_ids, market=market)
    if not result:
        return None
    df = pd.DataFrame.from_records(result, index=["order_book_id", "start_date"])
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace='fund')
def get_instrument_category(order_book_ids, date=None, category_type=None, source='gildata', market="cn"):
    """获取合约所属风格分类

    :param order_book_ids: 单个合约字符串或合约列表，如 '000001' 或 ['000001', '000003']
    :param date: 日期字符串，格式如 '2015-01-07' 或 '20150107'，若不指定，则为当天
    :param category_type: 可传入list，不指定则返回全部。可选：价值风格-value，规模风格-size，操作风格-operating_style，
                          久期分布-duration，券种配置-bond_type, 基金行业板块-industry_citics, 基金概念板块-concept,
                          基金投资风格-investment_style, 基金属性-universe, 分级基金标签-structured_fund, 基金分类-fund_type
    :param source: 分类来源。gildata: 聚源
    :param market:  (Default value = "cn")
    :returns: DataFrame
        返回合约指定的日期中所属风格分类
    """

    order_book_ids = ensure_obs(order_book_ids, market)

    if date:
        date = ensure_date_int(date)

    category_types = {
        'value', 'size', 'operating_style', 'duration', 'bond_type',
        'industry_citics', 'concept', 'investment_style', 'universe', 'structured_fund'
    }

    base_category_types = category_types.copy()
    base_category_types.add("fund_type")

    if category_type is None:
        category_type = category_types
    category_type = ensure_list_of_string(category_type)

    if 1 < len(category_type) and "fund_type" in category_type:
        raise ValueError("'fund_type' can only be searched independently.")

    check_items_in_container(category_type, base_category_types, 'category_type')

    source = ensure_string_in(source, {'gildata'}, 'source')

    result = get_client().execute('fund.get_instrument_category', order_book_ids, date, category_type, source,
                                  market=market)

    if not result:
        return

    if "fund_type" in category_type:
        c = [
            "order_book_id", "category_type", "first_type_code", "first_type", "second_type_code", "second_type",
            "third_type_code", "third_type"
        ]
        df = pd.DataFrame.from_records(result, index=['order_book_id', 'category_type'], columns=c)
    else:
        df = pd.DataFrame.from_records(result, index=['order_book_id', 'category_type'])
    return df


@export_as_api(namespace='fund')
def get_category(category, date=None, source='gildata', market='cn'):
    """获取指定分类下所属基金列表

    :param category: 风格类型映射, 如{"concept": ["食品饮料", "国防军工"], "investment_style": "沪港深混合型"}
    :param date: 如 '2015-01-07' 或 '20150107' (Default value = None)
    :param source: 分类来源。gildata: 聚源
    :param market:  (Default value = "cn")
    :returns: DataFrame
    """
    category_keys = {
        'value', 'size', 'operating_style', 'duration', 'bond_type', 'fund_type',
        'industry_citics', 'concept', 'investment_style', 'universe', 'structured_fund'
    }

    if date:
        date = ensure_date_int(date)

    check_type(category, dict, "category")
    source = ensure_string_in(source, {'gildata'}, 'source')

    check_items_in_container(category, category_keys, 'category')
    for k in category:
        category[k] = ensure_list_of_string(category[k])

    category_types_map = defaultdict(list)

    category_type_copy = list(category.keys())
    if "fund_type" in category_type_copy:
        fund_type_df = get_category_mapping(category_type="fund_type")
        category_types_map["fund_type"].extend(fund_type_df.values.flatten().tolist())
        category_type_copy.remove("fund_type")

    if category_type_copy:
        df = get_category_mapping(category_type=category_type_copy)
        unique_index = df.index.unique()
        for idx in unique_index:
            category_types_map[idx].extend([_ for _ in df.loc[idx].values.flatten() if _ is not None])

    for c in category:
        if not set(category[c]).issubset(set(category_types_map[c])):
            raise ValueError("Unexpected category.")
    return get_client().execute('fund.get_category_v2', category, date, source, market=market)


@export_as_api(namespace='fund')
def get_category_mapping(source='gildata', category_type=None, market="cn"):
    """获取风格分类列表概览

    :param source: 分类来源。gildata: 聚源
    :param category_type: 风格类型, (Default value = ['value', 'size', 'universe', 'bond_type', 'concept', 'duration', 'structured_fund', 'operating_style', 'industry_citics', 'investment_style'])
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """

    source = ensure_string_in(source, {'gildata'}, 'source')

    # 参数category_type为None时默认取除fund_type以外的风格, 因为fund_type不能和其他风格共存
    category_types = {
        'value', 'size', 'operating_style', 'duration', 'bond_type',
        'industry_citics', 'concept', 'investment_style', 'universe', 'structured_fund'
    }

    if category_type is None:
        category_type = category_types
    category_type = ensure_list_of_string(category_type)

    if "fund_type" in category_type:
        assert len(category_type) == 1, "'fund_type' can only be searched independently."
    else:
        check_items_in_container(category_type, category_types, 'category_type')

    result = get_client().execute("fund.get_category_mapping", source, market=market)
    if not result:
        return
    if "fund_type" in category_type:
        columns = [
            "first_type_code", "first_type", "second_type_code", "second_type", "third_type_code", "third_type",
            "category_type"
        ]
        df = pd.DataFrame(result, columns=columns)
        df = df["fund_type" == df["category_type"]]
    else:
        columns = ["category", "category_index", "category_type"]
        df = pd.DataFrame(result, columns=columns)
        df = df[df["category_type"].isin(category_type)]

    df.set_index(keys=["category_type"], inplace=True)
    return df


@export_as_api(namespace="fund")
def get_benchmark_price(order_book_ids, start_date=None, end_date=None, market="cn"):
    """
    获取基金 benchmark 价格

    :param order_book_ids: 基金order_book_id, str or list
    :param start_date: 开始日期，不指定则不限制开始日期
    :param end_date: 结束日期，不指定则不限制结束日期
    :param market: (Default value = "cn")
    :return: DataFrame
    """
    order_book_ids = ensure_list_of_string(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    result = get_client().execute(
        "fund.get_benchmark_price", order_book_ids, start_date, end_date, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    return df


FINANCIALS_FIELDS = [
    'accts_payable',
    'accts_receivable',
    'cash_equivalent',
    'deferred_expense',
    'deferred_income_tax_assets',
    'deferred_income_tax_liabilities',
    'dividend_receivable',
    'financial_asset_held_for_trading',
    'financial_liabilities',
    'interest_payable',
    'interest_receivable',
    'leverage',
    'management_fee_payable',
    'other_accts_payable',
    'other_accts_receivable',
    'other_assets',
    'other_equity',
    'other_liabilities',
    'paid_in_capital',
    'profit_payable',
    'redemption_fee_payable',
    'redemption_money_payable',
    'sales_fee_payable',
    'stock_cost',
    'stock_income',
    'tax_payable',
    'total_asset',
    'total_equity',
    'total_equity_and_liabilities',
    'total_liabilities',
    'transaction_fee_payable',
    'trust_fee_payable',
    'undistributed_profit',
    'info_date'
]


@export_as_api(namespace="fund")
def get_financials(order_book_ids, start_date=None, end_date=None, fields=None, market="cn"):
    """
    获取基金财务数据

    :param order_book_ids: 基金order_book_id, str or list
    :param start_date: 开始日期，默认为 None
    :param end_date: 结束日期，默认为 None
    :param fields: 字段, 默认为None
    :param market: (Default value = "cn")
    :return: DataFrame
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)

    if fields is None:
        fields = FINANCIALS_FIELDS
    else:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, FINANCIALS_FIELDS, "fields")
    result = get_client().execute(
        "fund.get_financials", order_book_ids, start_date, end_date, fields, market=market)
    if not result:
        return

    df = pd.DataFrame(result)
    df = df.set_index(["order_book_id", "date"]).sort_index()
    return df


FEE_FIELDS = [
    "purchase_fee",
    "subscription_fee",
    "redemption_fee",
    "management_fee",
    "custodian_fee",
    "sales_service_fee",
]


@export_as_api(namespace="fund")
def get_fee(order_book_ids, fee_type=None, charge_type="front", date=None, market_type="otc", market="cn"):
    """
    获取基金费率信息

    :param order_book_ids: 基金order_book_id, str or list
    :param charge_type: 前后端费率(front, back), default=front
    :param fee_type: 费率类型，默认返回所有
    :param date: 日期, 默认为None
    :param market_type: 场内/场外费率(exchange, otc), 默认为otc
    :param market:  (Default value = "cn")
    :return: DataFrame
    """
    order_book_ids = ensure_obs(order_book_ids, market)
    if date:
        date = ensure_date_int(date)
    if fee_type is None:
        fee_type = FEE_FIELDS
    else:
        fee_type = ensure_list_of_string(fee_type)
        check_items_in_container(fee_type, FEE_FIELDS, "fields")

    check_items_in_container(charge_type, ["front", "back"], "charge_type")
    market_type = market_type.lower()
    check_items_in_container(market_type, ['otc', 'exchange'], 'market_type')
    result = get_client().execute("fund.get_fee_v2", order_book_ids, fee_type, charge_type, date, market_type,
                                  market=market)
    if not result:
        return
    columns = [
        'order_book_id', 'fee_type', 'fee_ratio', 'fee_value',
        'inv_floor', 'inv_cap', 'share_floor', 'share_cap',
        'holding_period_floor', 'holding_period_cap',
        'return_floor', 'return_cap'
    ]
    df = pd.DataFrame(result, columns=columns)
    df.drop_duplicates(df.columns, inplace=True)
    df.set_index(["order_book_id", "fee_type"], inplace=True)
    df.sort_index(inplace=True)
    return df


@export_as_api(namespace="fund")
def get_transition_info(order_book_ids, market="cn"):
    """
    获取基金转型信息

    :param order_book_ids: 基金order_book_id, str or list
    :param market:  (Default value = "cn")
    :return: DataFrame
    """

    def _handler(group):
        if 1 < len(group):
            group.sort_values("transition_time", inplace=True)
            group.drop_duplicates(subset=["order_book_id"], inplace=True)
            return group
        return group

    order_book_ids = ensure_obs(order_book_ids, market)
    result = get_client().execute("fund.get_transition_info", order_book_ids, market=market)
    if not result:
        return
    df = pd.DataFrame(result)
    df["order_book_id"] = df["order_book_id"].apply(lambda x: x[0:6])
    df = df.groupby(["order_book_id", "establishment_date"], as_index=False, group_keys=False).apply(_handler)
    # 未曾转型的基金不需要返回
    df = df.groupby(["order_book_id"], as_index=False, group_keys=False).apply(
        lambda g: g if 1 < len(g) else pd.DataFrame())
    df.dropna(inplace=True)
    if 0 == len(df):
        return
    df["transition_time"] = df["transition_time"].astype(int)
    df.set_index(["order_book_id", "transition_time"], inplace=True)
    return df.sort_index()


TRANSACTION_STATUS_FIELDS = [
    "subscribe_status",
    "redeem_status",
    "issue_status",
    "subscribe_upper_limit",
    "subscribe_lower_limit",
    "redeem_lower_limit",
    "redeem_upper_limit",
]


@export_as_api(namespace="fund")
def get_transaction_status(order_book_ids, start_date=None, end_date=None, fields=None, investor="institution",
                           market="cn"):
    """获取基金申赎状态

    :param order_book_ids: 基金代码，str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param fields: str or list of str，例如：'subscribe_status', 'redeem_status',
                    'subscribe_upper_limit', 'subscribe_lower_limit', 'redeem_lower_limit' (Default value = None)
                    'redeem_upper_limit',
    :param investor: 投资者身份(Default value = institution) institution/retail
    :param market:  (Default value = "cn")
    :returns: DataFrame

    """
    order_book_ids = ensure_obs(order_book_ids, market)

    if start_date:
        start_date = to_date(start_date)
    if end_date:
        end_date = to_date(end_date)

    if fields is not None:
        fields = ensure_list_of_string(fields)
        check_items_in_container(fields, TRANSACTION_STATUS_FIELDS, 'fields')
    else:
        fields = TRANSACTION_STATUS_FIELDS

    check_items_in_container(investor, ['institution', 'retail'], 'investor')

    result = get_client().execute(
        "fund.get_transaction_status_v2", order_book_ids, fields, investor, market=market
    )
    if not result:
        return

    def _oid_process(x):
        x.set_index('datetime', inplace=True)
        x.sort_index(inplace=True)

        dates = pd.date_range(x.index.values[0], x.index.values[-1], freq='D')
        x = x.reindex(dates, method='ffill')
        x.index.names = ['datetime']

        x = x.where(x.notnull(), None)

        return x

    result = pd.DataFrame(result)

    result = result.groupby(['order_book_id']).apply(_oid_process)
    result.drop('order_book_id', axis=1, inplace=True)
    result.reset_index(inplace=True)

    result['datetime'] = result['datetime'].apply(to_date)

    if start_date:
        result = result[result['datetime'] >= start_date]
    if end_date:
        result = result[result['datetime'] <= end_date]

    result.set_index(['order_book_id', 'datetime'], inplace=True)

    result = result.reindex(columns=fields)
    return result


@export_as_api(namespace="fund")
def get_manager_weight_info(managers, start_date=None, end_date=None, asset_type="stock", manage_type="all", market="cn"):
    """获取基金经理在管权重信息

    :param managers: 可以使用人员编码（如'101000002'）或姓名（如'江辉'），str 或 list of str
    :param start_date: 开始日期 (Default value = None)
    :param end_date: 结束日期 (Default value = None)
    :param asset_type: 	资产种类, 股票型-stock, 债券型-bond，默认stock
    :param manage_type: 管理方式, 全产品-all， 独管-independent，默认all
    :returns: DataFrame

    """
    managers = ensure_list_of_string(managers)
    # 检查manager中是否同时有人员编码或姓名
    if len(set(x.isdigit() for x in managers)) > 1:
        raise ValueError("couldn't get manager_id and name at the same time")

    if start_date:
        start_date = ensure_date_int(start_date)
    if end_date:
        end_date = ensure_date_int(end_date)
    result = get_client().execute("fund.get_manager_weight_info", managers, start_date, end_date, asset_type, manage_type, market)

    if not result:
        return

    df = pd.DataFrame(result)
    df.set_index(keys=["manager_id", "datetime"], inplace=True)
    return df.sort_index()
