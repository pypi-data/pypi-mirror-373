import os
import datetime as dt
import glob
import pandas as pd
import numpy as np


def search_files(parent_dir, freq, file_name):
    pattern = '{}/{}/[{}]'.format(parent_dir, freq,
                                  ']['.join([s.lower() + s.upper() for s in file_name]))
    files = glob.glob(pattern)
    if len(files) > 1:
        raise ValueError('too many candidate file for key:{}'.format(file_name))
    if len(files) == 0:
        raise FileNotFoundError('no file for key:{}'.format(file_name))
    return files[0]


def get_split_field_names(start_time, end_time, field):
    if end_time is None:
        end_time = dt.datetime.today().strftime('%Y-%m-%d 15:00:00')
    else:
        end_time = pd.to_datetime(end_time).strftime('%Y-%m-%d 15:00:00')
    freq, key = field.split('/')
    # 日频数据一个字段一个feather文件，一分钟的按月切割，其他的按年切割
    if freq == '01d':
        field_names = [key]
    elif freq in ['01min']:
        months = pd.date_range(start_time, end_time, freq="M")
        months = [ia.strftime('%Y%m') for ia in months]
        months.append(pd.to_datetime(end_time).strftime('%Y%m'))
        months = np.unique(months)
        field_names = [key + '_' + _m for _m in months]
    else:
        years = pd.date_range(start_time, end_time, freq="Y")
        years = [ia.strftime('%Y') for ia in years]
        end_t = pd.to_datetime(end_time)
        years.append(str(end_t.year))
        years = np.unique(years)
        field_names = [key + '_' + _m for _m in years]
    return field_names


def get_feather(msg_path, include930, key, start_time, end_time, stocks=None, freq='price01d'):
    """获取basic_data price 各频率数据"""
    if stocks is None:
        cols = None
    else:
        stocks = [str(ia) for ia in stocks]
        cols = ['trade_date'] + stocks

    start_time = pd.to_datetime(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_time = None if end_time is None else pd.to_datetime(end_time).strftime('%Y-%m-%d 15:00:00')
    field_names = get_split_field_names(start_time, end_time, key)
    files_len = len(field_names)
    df_list = []
    for idx, field_name in enumerate(field_names):
        filename = "{}/{}/{}.fea".format(msg_path, freq, field_name)
        if not os.path.exists(filename):
            filename = search_files(msg_path, freq, '{}.fea'.format(field_name))
        # with open(filename, 'rb') as f:
        #     with mmap.mmap(f.fileno(), 0, access=1) as mf:
        #         tmp = pd.read_feather(mf, cols, use_threads=False)
        tmp = pd.read_feather(filename, cols, use_threads=False).set_index('trade_date')
        tmp.index = pd.to_datetime(tmp.index)
        if freq.endswith('min') and not include930:
            tmp = tmp[tmp.index.time != pd.to_datetime('09:30:00').time()]
        if idx == 0:
            tmp = tmp.loc[start_time:]
        if idx == files_len - 1 and end_time is not None:
            tmp = tmp.loc[:end_time]
        # tmp = tmp.loc[start_time:end_time]
        df_list.append(tmp)
    df = pd.concat(df_list, join='outer', sort=False)

    if stocks is not None:
        stock_not_in = np.setdiff1d(stocks, df.columns)
        if len(stock_not_in) > 0:
            df[stock_not_in] = np.nan
    df.columns = df.columns.astype(int)
    df = df.sort_index().sort_index(axis=1)
    df.columns.name = 'code'
    df.index.name = 'trade_date'
    return df


def trade_time(full_tick, start_time=None, end_time=None, bar_counts=None):
    """
    从full tick中获取相应的交易时间戳，根据不同频率传入不同的full_tick
    full_tick: 相应频率的所有时间戳
    start_time: pd.timestamp
    end_time: pd.timestamp
    bar_counts: 从end time/start time 推多少个时刻，优先 bar_counts + end_time

    """
    # 交易时间段
    if start_time is None and (end_time is not None) and (bar_counts is not None):
        # 从endtime往前取n bars
        idx = np.where(full_tick <= end_time)[0][-1]
        days = full_tick[max(0, idx - bar_counts + 1): idx + 1]
        return pd.to_datetime(days).tolist()

    elif start_time is None and (end_time is not None) and (bar_counts is None):
        # 从endtime往前取n bars
        idx = np.where(full_tick <= end_time)[0][-1]
        days = full_tick[: idx+1]
        return pd.to_datetime(days).tolist()

    elif (start_time is not None) and (bar_counts is not None):
        # 从startime往后取n bars
        idx = np.where(full_tick >= start_time)[0][0]
        days = full_tick[idx: idx + bar_counts]
        return pd.to_datetime(days).tolist()

    elif (start_time is not None) and (end_time is not None):
        idx_st = np.where(full_tick >= start_time)[0][0]
        idx_et = np.where(full_tick <= end_time)[0][-1]
        if idx_st > idx_et:
            raise ValueError('no trading between {}~{}'.format(start_time, end_time))
        days = full_tick[idx_st: idx_et + 1]
        return pd.to_datetime(days).tolist()
    elif (start_time is not None) and (end_time is None) and (bar_counts is None):
        end_time = pd.to_datetime(dt.datetime.now().strftime('%Y-%m-%d 15:00:00'))
        idx_st = np.where(full_tick >= start_time)[0][0]
        idx_et = np.where(full_tick <= end_time)[0][-1]
        if idx_st > idx_et:
            raise ValueError('no trading between {}~{}'.format(start_time, end_time))
        days = full_tick[idx_st: idx_et + 1]
        return pd.to_datetime(days).tolist()
    else:
        raise ValueError('not support for start time:{}, end_time:{}, bar_counts:{}'.format(start_time, end_time,
                                                                                            bar_counts))


def construct_day_tradings(day, freq, include930):
    """
    construct_day_tradings
    """
    day = pd.to_datetime(day).strftime("%Y%m%d")

    time_0930 = "{} 093000".format(day)
    time_1130 = pd.to_datetime('{} 113000'.format(day), format='%Y-%m-%d %H:%M:%S')
    time_1330 = "{} 133000".format(day)

    tradings = pd.date_range(time_0930, time_1330, freq=freq)
    tradings = pd.Series(tradings)  # 索引对象不可变，转换为Series对象
    idxs = tradings > time_1130
    tradings[idxs] = tradings[idxs] + dt.timedelta(minutes=90)
    if not include930:
        tradings = tradings[1:]
    return tradings


def get_full_trade_tick(tradings, freq, include930=False):
    """
    根据频率生产出完成的交易日及日内时间戳
    :param include930:
    :param start_time:
    :param end_time:
    :param freq:
    :return: array / list of datetime
    """
    # tradings = pd.to_datetime(get_tradings(db_service, start_time, end_time))
    tradings = np.unique(tradings)

    if freq != "01d":
        all_tradings = []
        for day in tradings:
            # 获取每日的交易时间
            day_tradings = construct_day_tradings(day, freq, include930)
            all_tradings.extend(day_tradings.tolist())

        tradings = pd.to_datetime(all_tradings)

    return tradings


def format_time(start_time=None, end_time=None, freq='d'):
    if freq in ['d', 'D']:
        if end_time is not None:
            end_time = pd.to_datetime(pd.to_datetime(end_time).date())
        if start_time is not None:
            start_time = pd.to_datetime(pd.to_datetime(start_time).date())
    elif freq in ['min', 'T']:
        if end_time is not None:
            if len(str(end_time)) > 10:
                end_time = pd.to_datetime(end_time)
            else:
                end_time = pd.to_datetime(pd.to_datetime(end_time).strftime("%Y-%m-%d 15:00:00"))
        if start_time is not None:
            if len(str(start_time)) > 10:
                start_time = pd.to_datetime(start_time)
            else:
                start_time = pd.to_datetime(pd.to_datetime(start_time).strftime("%Y-%m-%d 00:00:00"))
    else:
        raise ValueError('not support for freq:{}'.format(freq))
    return start_time, end_time
