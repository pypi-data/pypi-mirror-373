import re
import calendar
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from mdbq.other import ua_sj
import requests
from collections.abc import Mapping


def safe_get(d, keys, default=None):
    """
    安全获取嵌套字典值
    data = {"user": {"profile": {"name": "Alice"}}}
    result = safe_get(data, ["user", "profile", "name"], "Unknown")
    print(result)  # 输出: "Alice"
    """
    if not keys:
        return default
    if not isinstance(d, Mapping):
        return default
    for key in keys:
        d = d.get(key, default)
        if not isinstance(d, Mapping):
            break
    return d if d is not None else default


def get_public_ip():
    services = [
        'https://checkip.amazonaws.com',
        'https://ipinfo.io/ip',
        'https://icanhazip.com',
        'https://ifconfig.me/ip',
        'https://ipecho.net/plain',
        'https://myexternalip.com/raw',
        'https://ipapi.co/ip'
    ]
    for url in services:
        try:
            response = requests.get(url, timeout=5, headers={'User-Agent': ua_sj.get_ua()})
            if response.status_code == 200:
                response = re.findall(r'\d+\.\d+\.\d+\.\d+', response.text.strip())
                if response:
                    return response[0]
        except:
            continue
    print("无法获取外网 IP")
    return '120.236.0.0/8'


def first_and_last_day(date):
    """
    返回指定日期当月的第一天和最后一天
    """
    date = pd.to_datetime(date)  # n 月以前的今天
    _, _lastDay = calendar.monthrange(date.year, date.month)  # 返回月的第一天的星期和当月总天数
    _firstDay = datetime.date(date.year, date.month, day=1)
    _lastDay = datetime.date(date.year, date.month, day=_lastDay)
    return _firstDay, _lastDay


def get_day_of_month(num: int, fm=None):
    """
    num: 获取n月以前的第一天和最后一天, num=0时, 返回当月第一天和最后一天
    fm: 日期输出格式
    """
    if not fm:
        fm ='%Y%m%d'
    _today = datetime.date.today()
    months_ago = _today - relativedelta(months=num)  # n 月以前的今天
    _, _lastDay = calendar.monthrange(months_ago.year, months_ago.month)  # 返回月的第一天的星期和当月总天数
    _firstDay = datetime.date(months_ago.year, months_ago.month, day=1).strftime(fm)
    _lastDay = datetime.date(months_ago.year, months_ago.month, day=_lastDay).strftime(fm)
    return _firstDay, _lastDay


def dates_between(start_date, end_date, fm=None) -> list:
    """
    获取两个日期之间的所有日期， 返回 list
    fm: 日期输出格式
    """
    if not fm:
        fm ='%Y-%m-%d'
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime(fm))
        current_date += datetime.timedelta(days=1)
    return dates


def cover_df(df):
    df.replace([np.inf, -np.inf], '0', inplace=True)  # 清理一些非法值
    df.replace(to_replace=['\\N', '-', '--', '', 'nan', 'NAN'], value='0', regex=False, inplace=True)  # 替换掉特殊字符
    df.replace(to_replace=[','], value='', regex=True, inplace=True)
    df.replace(to_replace=['="'], value='', regex=True, inplace=True)  # ="和"不可以放在一起清洗, 因为有: id=86785565
    df.replace(to_replace=['"'], value='', regex=True, inplace=True)
    cols = df.columns.tolist()
    for col in cols:
        if col == 'id':
            df.pop('id')
            continue
        # df[col] = df[col].apply(
        #     lambda x: float(float((str(x).rstrip("%"))) / 100) if re.findall(r'^\d+\.?\d*%$', str(x)) else x)
        # df[col] = df[col].apply(lambda x:
        #                         float(re.sub(r'%$', '', str(x))) / 100
        #                         if (str(x) != '' and str(x).endswith('%')) and not re.findall(
        #     '[\\u4e00-\\u9fa5]', str(x)) else '0.0' if str(x) == '0%' else x)
        df[col] = df[col].apply(
            lambda x: float(str(x).rstrip("%")) / 100
            if (
                    re.fullmatch(r'^\d+\.?\d*%$', str(x))  # 匹配数字加%格式
                    and not re.search(r'[\u4e00-\u9fa5]', str(x))  # 排除含中文的情况
            )
            else (
                '0.0' if str(x) == '0%' else x  # 处理 "0%"
            )
        )

        try:
            # 不能直接使用 int() ，对于大数，可能转为uint64，导致数据库入库可能异常
            df[col] = df[col].apply(
                lambda x: np.int64(str(x)) if '_' not in str(x) and '.' not in str(x) else x)  # 不含小数点尝试转整数
        except:
            pass
        try:
            if df[col].dtype == 'object':  # 有些列没有被 pandas 识别数据类型，会没有 dtype 属性
                df[col] = df[col].apply(lambda x: float(x) if '.' in str(x) and '_' not in str(x) else x)
        except:
            pass
        new_col = col.lower()
        new_col = re.sub(r'[()\-，,&~^、 （）\"\'“”=·/。》《><！!`]', '_', new_col, re.IGNORECASE)
        new_col = new_col.replace('）', '')
        new_col = re.sub(r'_{2,}', '_', new_col)
        new_col = re.sub(r'_+$', '', new_col)
        df.rename(columns={col: new_col}, inplace=True)
    df.fillna(0, inplace=True)
    return df


def translate_keys(original_dict:dict, translation_dict:dict) -> dict:
    """
    original_dict键名翻译, 若键存在则返回翻译值，否则返回原键
    """
    return {translation_dict.get(k, k): v for k, v in original_dict.items()}


def is_valid_date(date_string):
    """
    mysql调用
    判断是否是日期格式, 且允许没有前导零, 且允许带时间
    纯日期格式： 返回 1
    日期+时间： 返回 2
    """
    date_pattern = r"^(\d{4})-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])$"
    match = re.match(date_pattern, str(date_string))  # 判断纯日期格式：2024-11-09
    if match is None:
        date_pattern = r".*\d+:\d+:\d+$"
        match = re.match(date_pattern, date_string)  # 判断日期+时间：2024-11-09 00:36:45
        if match is not None:
            return 2
    else:
        return 1


def is_integer(int_str):
    """
    mysql调用
    判断是否整数, 允许包含千分位分隔符, 允许科学计数法
    """
    # 如果是科学计数法
    match = re.findall(r'^[-+]?(\d+)\.(\d+)[eE][-+]?(\d+)$', str(int_str))
    if match:
        if len(match[0]) == 3:
            if int(match[0][0]) == 0:  # 0 开头
                if int(match[0][2]) > 10:  # 转换后整数长度超过 10 位
                    return False
            else:  # 不是 0 开头
                if len(match[0][0]) + int(match[0][2]) > 10:  # 转换后整数长度超过 10 位
                    return False
            if int(match[0][2]) >= len(match[0][1]):
                return True
            else:
                return False
    # 如果是普通数字, 且允许千分符
    __pattern = r'^[-+]?\d{1,3}(,\d{3}){0,3}$|^[-+]?\d{1,9}$'
    return re.match(__pattern, str(int_str)) is not None


if __name__ == '__main__':
    pass
