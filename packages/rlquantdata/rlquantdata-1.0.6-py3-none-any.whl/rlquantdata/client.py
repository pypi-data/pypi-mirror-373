import datetime
import datetime as dt
import gc
import hashlib
import json
import os
import re
import threading
import time
from io import BytesIO

import numpy as np
import pandas as pd
import requests
from pandas import Index

from rlquantdata.utilities import utils

exec('from numpy import nan')


class DayBarStore():
    """规定一些标准数据加载模块，目前数据格式同因子平台数据，columns: code, index: time"""

    def __init__(self, f, include930, key, start_time='2015-01-01', end_time=None):
        '''freq: 文件子目录'''
        t1 = time.time()
        freq, field = key.split('/')
        if start_time is None:
            start_time = '2007-01-01'
            if freq == '01min':
                start_time = '2009-01-01'
        self.start_time = start_time
        self.end_time = end_time
        self._data = utils.get_feather(f, include930, key, start_time, end_time, stocks=None, freq='price' + freq)
        self._data = self._data.sort_index(axis=1)
        if end_time is None:
            self.end_time = self._data.index[-1].strftime('%Y-%m-%d')
        print('load {}/price{} from {} to {}, consume {:.4}s'.format(f, key,
                                                                     start_time, end_time, time.time() - t1))

    def get_datas(self, trading_dates, start_time, end_time, bar_counts, codes):
        # 合并 trading_dates 和 self._data.index，防止类似于指数000001.fea数据，会提前录入
        trading_dates = pd.to_datetime(trading_dates).union(self._data.index).sort_values()
        days = utils.trade_time(trading_dates, start_time=start_time, end_time=end_time, bar_counts=bar_counts)
        if len(days) == 0:
            raise ValueError('days did not provide')
        if isinstance(days, str):
            days = pd.to_datetime(days)
        elif isinstance(days, int):
            days = pd.to_datetime(str(days))
        elif isinstance(days, list):
            days = [pd.to_datetime((day)) for day in days]
        else:
            raise ValueError('days type:{} not match.'.format(type(days)))

        if isinstance(codes, (list, np.ndarray)):
            codes = [int(code) for code in codes]
            return self._data.reindex(index=days, columns=codes)
        elif isinstance(codes, Index):
            if codes.dtype != 'int64':
                raise ValueError('not support for codes type:{}'.format(codes.dtype))
            return self._data.loc[start_time:end_time].reindex(columns=codes)
        elif isinstance(codes, str):
            codes = [int(codes)]
            return self._data.reindex(index=days, columns=codes)
        elif codes is None:
            return self._data.reindex(index=days)
        else:
            raise ValueError('not support for codes:{}'.format(codes))

    def get_range_datas(self, start_time, end_time, codes):
        if isinstance(codes, (list, np.ndarray)):
            codes = [int(code) for code in codes]
            return self._data.loc[start_time:end_time].reindex(columns=codes)
        elif isinstance(codes, Index):
            if codes.dtype != 'int64':
                raise ValueError('not support for codes type:{}'.format(codes.dtype))
            return self._data.loc[start_time:end_time].reindex(columns=codes)
        elif isinstance(codes, str):
            codes = [int(codes)]
            return self._data.loc[start_time:end_time].reindex(columns=codes)
        elif codes is None:
            return self._data.loc[start_time:end_time, :]
        else:
            raise ValueError('not support for codes:{}'.format(codes))


def get_last_not_nan(df: pd.DataFrame):
    sub_v = df.values
    ix = len(df) - 1 - (~pd.isna(sub_v))[::-1].argmax(0)
    return pd.Series(data=sub_v[ix, range(df.shape[1])], index=df.columns, dtype=object)


class BaseClient(object):
    """加载数据key格式统一：fre/field"""

    def __init__(self, path,
                 include930=True,
                 day_with_1500=False,
                 username=None,
                 password=None,
                 remote_servers='factorlib.irongliang.com',
                 https=True,
                 enable_remote=False,
                 format_column=None
                 ):
        if isinstance(path, str) or path is None:
            self.path = {'public': path}
        elif isinstance(path, dict):
            self.path = path
        else:
            raise ValueError('not support for path:{}'.format(path))
        self.include930 = include930
        self.day_with_1500 = day_with_1500
        self.format_column = format_column
        self._datas = {}
        for key, path in self.path.items():
            if path != '' and path is not None:
                if not os.path.exists(path):
                    raise RuntimeError('data path {} not exist'.format(os.path.abspath(path)))
        self.load_time = 0
        self.load_count = 0
        self.get_datas_time = 0
        self.get_datas_count = 0

        now_time = datetime.datetime.now()
        if now_time.hour < 22:
            self.validate_time = datetime.datetime.combine(now_time - datetime.timedelta(days=1),
                                                           datetime.time(10, 0, 0))
        else:
            self.validate_time = datetime.datetime.combine(now_time, datetime.time(10, 0, 0))
        # load bar

        self.enable_remote = enable_remote
        if enable_remote:
            none_num = [username, password, remote_servers].count(None)
            if 1 < none_num < 3:
                raise Exception('开启远程请求，必须提供 remove_servers、username、password 参数')
            self.username = username
            self.password = hashlib.md5(password.encode('utf-8')).hexdigest()
            self.__server_list = []
            self.__lock = threading.Lock()
            self.__valid_url_index = 0
            self.__token = None
            protocol = 'https' if https else 'http'
            for remote_server in remote_servers.split(','):
                split = remote_server.split(':')
                if len(split) != 2 and len(split) != 1:
                    raise Exception(f'错误的服务列表 {remote_server}')
                ip = split[0]
                if len(split) == 2:
                    port = split[1]
                else:
                    port = '443' if https else '80'
                if not port.isdigit():
                    raise Exception(f'错误的端口 {port}')
                self.__server_list.append(f'{protocol}://{ip}:{port}')

        close_data = self.get_data('2007-01-01', dt.datetime.today().strftime('%Y-%m-%d'), None, '01d/close', None, 1,
                                   format_column=False)
        # 按close时间戳作为交易日列表
        self.trading_dates = pd.to_datetime(close_data.index, unit='ns').values

        self.full_ticks = {}
        # # 初始化daily，分钟的后续取数时再添加
        freq = '01d'
        self.full_ticks[freq] = utils.get_full_trade_tick(self.trading_dates, freq, include930=include930)

        if format_column is not None:
            code_columns = self.get_data('2007-01-01', dt.datetime.today().strftime('%Y-%m-%d'), None,
                                         f'01d/{format_column}', None, 1, format_column=False)
            self.codes = code_columns.columns.astype(int).tolist()
        else:
            self.codes = close_data.columns.astype(int).tolist()

    def set_include930(self, include930):
        self.include930 = include930

    def check_validata_time(self):
        now_time = datetime.datetime.now()
        if (now_time - self.validate_time).total_seconds() > 24 * 3600:
            self._datas.clear()
            self.validate_time = datetime.datetime.combine(now_time, datetime.time(10, 0, 0))

    def preloading(self, start_time, end_time, subscribe_data):
        for freq, fields in subscribe_data.items():
            t1 = time.time()
            for field_in in fields:
                splite_field = field_in.split('.')
                if len(splite_field) == 2:
                    custom_key = splite_field[0]
                    field = splite_field[1]
                else:
                    custom_key = 'public'
                    field = field_in
                data_key = '{}/{}'.format(freq, field)
                bar_key = '{}/{}'.format(freq, field_in)
                self._datas[bar_key] = DayBarStore(self.path[custom_key], self.include930, data_key, start_time,
                                                   end_time)
            self.load_time += time.time() - t1
            self.load_count += 1

    def check_time_limit(self, start_time, end_time, bar_store):
        if start_time is not None:
            if pd.to_datetime(start_time) < pd.to_datetime(bar_store.start_time):
                return True
        if end_time is not None:
            if pd.to_datetime(end_time) > pd.to_datetime(bar_store.end_time):
                return True

        # if end_time is None:
        #     end_time = dt.datetime.today().strftime('%Y-%m-%d 15:00:00')
        # else:
        #     end_time = pd.to_datetime(end_time).strftime('%Y-%m-%d 15:00:00')
        # if start_time is None:
        #     start_time = '2007-01-01'
        # if pd.to_datetime(start_time) < pd.to_datetime(bar_store.start_time):
        #     return True
        # if pd.to_datetime(end_time) > pd.to_datetime(bar_store.end_time):
        #     return True
        return False

    def get_fin_data(self, start_time, end_time, field, quarter_shift=0, quarter=None, interval=1, codes=None,
                     publish_merge=None, quarter_merge=None, format_column=True, universe=None):
        if start_time is None:
            start_time = '2007-01-01'
        if field is None:
            raise ValueError('field is None')

        fields = field
        file_list = []
        fields_remote = []  # 收集需要远程获取的field

        if not isinstance(field, list):
            fields = [field]
        for field in fields:
            file_exist = False
            for _, msg_path in self.path.items():
                filepath = "{}/{}/{}.fea".format(msg_path, 'finance', field)
                if not os.path.exists(filepath):
                    try:
                        filepath = utils.search_files(msg_path, 'finance', '{}.fea'.format(field))
                        file_list.append((field, filepath))
                        file_exist = True
                        break
                    except FileNotFoundError:
                        pass
                else:
                    file_list.append((field, filepath))
                    file_exist = True
                    break
            if not file_exist:
                if self.enable_remote:
                    fields_remote.append(field)  # 本地不存在，加入远程列表
                # if self.enable_remote:
                #     for field in fields:
                #         df = self.__get_remote_fin_data(start_time, end_time, field, quarter_shift, quarter,
                #                                         interval, universe=universe)
                #         file_list.append((df, None))
                # else:
                #     raise FileNotFoundError('{}.fea'.format(field))

        # 批量处理远程请求
        if fields_remote and self.enable_remote:
            fields_remote_str = ",".join(fields_remote)
            # 直接请求整个fields_remote列表，服务端统一处理
            df_remote = self.__get_remote_fin_data(
                start_time, end_time, fields_remote_str,
                quarter_shift, quarter, interval, universe=universe,
                publish_merge=publish_merge, quarter_merge=quarter_merge
            )
            file_list.append((df_remote, None))
        elif fields_remote:
            error_msg = ''
            for field in fields_remote:
                error_msg += '{}.fea'.format(field)
            raise FileNotFoundError(error_msg)

        universe = self.__apply_universe(start_time, end_time, codes, universe)

        merge_publish_df = None
        merge_quarter_df = None
        if publish_merge is not None:
            if isinstance(publish_merge, pd.DataFrame):
                merge_publish_df = publish_merge
            else:
                merge_publish_df = self.get_data('1993-01-01', datetime.datetime.now().strftime('%Y-%m-%d'), codes=None,
                                                 field=f'01d/{publish_merge}')
            merge_publish_df.index = merge_publish_df.index.strftime('%Y-%m-%d')
        elif quarter_merge is not None:
            if isinstance(quarter_merge, pd.DataFrame):
                merge_quarter_df = quarter_merge
            else:
                merge_quarter_df = self.get_data('1993-01-31', datetime.datetime.now().strftime('%Y-%m-%d'), codes=None,
                                                 field=f'01d/{quarter_merge}')
            merge_quarter_df.index = merge_quarter_df.index.strftime('%Y-%m-%d')

        result = None
        for file_tuple in file_list:
            if file_tuple[1] is not None:
                single_df = self._get_fin_data(file_tuple[0], file_tuple[1], quarter_shift, start_time, quarter,
                                               merge_publish_df, merge_quarter_df)
            else:
                single_df = file_tuple[0]
            if result is None:
                result = single_df
            else:
                union_columns = result.columns.union(single_df.columns)
                result = result.reindex(columns=union_columns)
                single_df = single_df.reindex(columns=union_columns)
                result = single_df.fillna(result)
        result = result.ffill()
        result = result.loc[start_time:end_time, :]
        result = result.bfill()
        if interval > 1:
            result = result[::interval]

        if merge_publish_df is not None:
            merge_publish_df.index = pd.to_datetime(merge_publish_df.index)
        elif merge_quarter_df is not None:
            merge_quarter_df.index = pd.to_datetime(merge_quarter_df.index)

        if isinstance(codes, (list, np.ndarray)):
            codes = [int(code) for code in codes]
        elif isinstance(codes, Index):
            if codes.dtype != 'int64':
                raise ValueError('not support for codes type:{}'.format(codes.dtype))
            pass
        elif isinstance(codes, str):
            codes = [int(codes)]
        elif codes is None:
            # return result
            pass
        else:
            raise ValueError('not support for codes:{}'.format(codes))

        result = result.reindex(columns=codes)
        # return result.reindex(columns=codes)

        if universe is not None:
            result = result.reindex(columns=universe.columns)
            universe = universe.reindex(index=result.index)
            return result * universe
        elif format_column and self.format_column is not None and codes is None:
            # 如果需要按照统一codes进行format，在此执行
            return result.reindex(columns=self.codes)

        return result

    def _get_fin_data(self, field, filepath, quarter_shift, start_time, quarter, merge_publish_df, merge_quarter_df):
        if field in self._datas.keys():
            df = self._datas[field]
        else:
            df: pd.DataFrame = pd.read_feather(filepath, use_threads=False).set_index('trade_date')
            df.columns = df.columns.astype(int)
            df = df.sort_index(axis=1)
            df.columns.name = 'code'
            self._datas[field] = df

        values = df.tail(1).squeeze()

        quarter_map = {1: '0331', 2: '0630', 3: '0930', 4: '1231'}
        fin_date = quarter_map[quarter] if quarter in quarter_map else None

        path = self.get_path()
        if isinstance(path, str):
            trade_date_path = f'{path}/price01d/trade_date.fea'
        else:
            trade_date_path = f'{path["public"]}/price01d/trade_date.fea'
        from rlquantdata.utilities.trade_date_utils import TradeDateUtils
        tdu = TradeDateUtils(trade_date_path, self)

        def at_data(data_df, label, trade_date):
            if label not in data_df.columns:
                return np.nan
            trade_date = trade_date[:4] + "-" + trade_date[4:6] + "-" + trade_date[6:]
            if not tdu.isBizDay('china.sse', trade_date):
                trade_date = tdu.advanceDateByCalendar('china.sse', trade_date, '-1b').strftime('%Y-%m-%d')
            if trade_date in data_df.index:
                return data_df.at[trade_date, label]
            else:
                return np.nan

        def get_fin(vv, label, fin_date=None, shift=0):
            split_array = vv.split(':')
            for i in range(len(split_array), 0, -2):
                if fin_date is None:
                    idx = i - 1 - shift * 2
                    if idx < 0:
                        return np.nan
                    if merge_quarter_df is not None:
                        return at_data(merge_quarter_df, label, split_array[idx - 1])
                    return float(split_array[idx]) if split_array[idx] != '' else np.nan
                elif split_array[i - 2].endswith(fin_date):
                    idx = i - 1 - shift * 2 * 4
                    if idx < 0:
                        return np.nan
                    if merge_quarter_df is not None:
                        return at_data(merge_quarter_df, label, split_array[idx - 1])
                    return float(split_array[idx]) if split_array[idx] != '' else np.nan

        start_time = start_time.replace('-', '')
        main_dict = {}
        for label, item in values.items():
            if item is None:
                main_dict[label] = {}
                continue

            array = item.split(',')
            label_dict = {}
            for i in range(len(array), 0, -2):
                cur_date = array[i - 2]
                if merge_publish_df is not None:
                    label_dict[cur_date] = at_data(merge_publish_df, label, cur_date)
                else:
                    label_dict[cur_date] = get_fin(array[i - 1], label, fin_date, quarter_shift)
                if cur_date < start_time and not pd.isna(label_dict[cur_date]):
                    break

            main_dict[label] = label_dict

        # 生成完整的 df，可能包含节假日
        result = pd.DataFrame(main_dict)
        result.index = pd.to_datetime(result.index)
        union_index = result.index.union(df.index)
        result = result.reindex(union_index, fill_value=pd.NA)

        # 获取节假日的 index
        hol_index = result.index.difference(df.index)

        # 获取连续节假日的第一天，得到第一天的索引，由该索引获得连续节假日的第一天的上一个交易日
        start_of_continuous_segments = hol_index[
            result.index.difference(df.index).to_series().diff() > pd.Timedelta(days=1)]
        start_of_continuous_segments = pd.DatetimeIndex([hol_index[0]]).union(start_of_continuous_segments)
        position = union_index.searchsorted(start_of_continuous_segments)
        head_hol_size = 0
        # 移除连续节假日
        while True:
            if position[head_hol_size] == head_hol_size:
                head_hol_size += 1
            else:
                break
        position = position[head_hol_size:] - 1
        pre_biz_index = union_index[position]

        # 将连续节假日的数据，先 ffill，再取连续节假日的最后一天，使得后面节假日的数据优先级高于前面的节假日
        hol_df = result.loc[hol_index]
        index_diff = hol_df.index.to_series().diff().dt.days.ne(1).cumsum()
        hol_df['index_diff'] = index_diff
        hol_df = hol_df.groupby('index_diff').ffill()
        hol_df['index_diff'] = index_diff
        hol_df = hol_df.groupby('index_diff').tail(1)
        hol_df = hol_df.drop('index_diff', axis=1)

        if head_hol_size != 0:
            # 头几天为节假日，移除后再合并
            # 将合并的节假日数据，与交易日数据合并，并给与交易日的 index
            head_hol_row_df = hol_df.head(head_hol_size)
            hol_df = hol_df.drop(hol_df.index[:head_hol_size])
            hol_df = pd.DataFrame(
                np.where(pd.isna(hol_df), result.loc[pre_biz_index], hol_df),
                index=pre_biz_index,
                columns=hol_df.columns
            )
            result = pd.concat([head_hol_row_df, result.reindex(df.index)])
            result.update(hol_df)
            result.iloc[:head_hol_size + 1] = result.iloc[:head_hol_size + 1].ffill()
            result = result.drop(result.index[:head_hol_size])
            result.index.name = 'trade_date'
        else:
            hol_df = pd.DataFrame(
                np.where(pd.isna(hol_df), result.loc[pre_biz_index], hol_df),
                index=pre_biz_index,
                columns=hol_df.columns
            )
            result = result.reindex(df.index)
            result.update(hol_df)

        return result

    def get_data(self, start_time=None, end_time=None,
                 codes=None, field='01d/close', bar_counts=None, interval=1, format_column=True, universe=None):

        t1 = time.time()
        freq, fld = field.split('/', 1)
        fre = re.sub(r'[^a-zA-Z]', '', freq)
        try:
            if field not in self._datas.keys():
                print('no {} data source, now load it'.format(field))
                self.preloading(start_time, end_time, {freq: [fld]})
            elif self.check_time_limit(start_time, end_time, self._datas[field]):
                self.preloading(start_time, end_time, {freq: [fld]})
        except FileNotFoundError as e:
            if self.enable_remote:
                return self.__get_remote_data(start_time, end_time, codes, field, bar_counts, interval,
                                              universe=universe)
            raise e

        universe = self.__apply_universe(start_time, end_time, codes, universe)

        start_time, end_time = utils.format_time(start_time, end_time, fre)

        # if end_time == None:
        #     end_time = dt.datetime.today().strftime('%Y%m%d')
        if (start_time is None) or (end_time is None):
            if freq.endswith('min'):
                bars = self._datas[field].get_datas([], start_time, end_time, bar_counts, codes)
            else:
                bars = self._datas[field].get_datas(self.trading_dates, start_time, end_time, bar_counts, codes)
        else:
            if freq == '01d':
                start_time_int = pd.to_datetime(pd.to_datetime(start_time).strftime('%Y-%m-%d 00:00:00'))
                end_time_int = pd.to_datetime(pd.to_datetime(end_time).strftime('%Y-%m-%d 00:00:00'))
            else:
                start_time_int = pd.to_datetime(start_time)
                end_time_int = pd.to_datetime(end_time)
            bars = self._datas[field].get_range_datas(start_time_int, end_time_int, codes)
        self.get_datas_time += time.time() - t1
        self.get_datas_count += 1
        if bar_counts is None and interval > 1:
            bars = bars[::interval]

        if universe is not None:
            bars = bars.reindex(columns=universe.columns)
            universe = universe.reindex(index=bars.index)
            return bars * universe
        # 如果需要按照统一codes进行format，在此执行
        elif format_column and self.format_column is not None and codes is None:
            bars = bars.reindex(columns=self.codes)
        return bars

    def del_data(self, field):
        if field in self._datas.keys():
            del self._datas[field]
            gc.collect()

    def get_path(self):
        return self.path

    def get_remote_hol_dates(self, from_date=None):
        if self.enable_remote:
            return self.__get_remote_hol_dates(from_date)
        else:
            return None

    def __get_remote_hol_dates(self, from_date, relogin=False):
        token = self.__login(relogin)
        if token is None:
            return None
        if from_date is None:
            from_date = ''
        response = self.__request(f'api/factor/data/get_hol_dates/{from_date}', None, headers={'Authorization': token})
        if response is not None:
            stream_data = BytesIO()
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    stream_data.write(chunk)
            stream_data.seek(0)
            result = json.loads(stream_data.getvalue())
            if result.get('code', 0) == -1 and not relogin:
                return self.__get_remote_hol_dates(from_date, True)
            elif result.get('code', None) is None:
                return result.get('value')
            else:
                raise Exception(f'get data error, message: {result["msg"]}')
        return None

    def __get_remote_data(self, start_time, end_time, codes, field, bar_counts, interval, relogin=False, universe=None):
        token = self.__login(relogin)
        if token is None:
            return None
        t1 = time.time()
        data_json = {
            'start_time': start_time, 'end_time': end_time, 'codes': codes, 'field': field,
            'bar_counts': bar_counts, 'interval': interval,
        }
        if isinstance(universe, str):
            data_json['universe'] = universe
        response = self.__request('api/factor/data/get_data', data_json, {'Authorization': token}, True)
        if response is not None:
            with BytesIO() as stream_data:
                for chunk in response.iter_content(chunk_size=1024):
                    # 处理数据块
                    if chunk:
                        # 在这里自定义处理数据块的逻辑
                        stream_data.write(chunk)
                stream_data.seek(0)
                if stream_data.getvalue()[0] == 65:
                    data = pd.read_feather(stream_data).set_index('trade_date')
                    data.columns = data.columns.astype(int)
                    print(
                        f'get field {field} from remote, start time {start_time}, end time {end_time}, cost {time.time() - t1}')
                else:
                    result = json.loads(stream_data.getvalue())
                    if result.get('code', 0) == -1 and not relogin:
                        data = self.__get_remote_data(start_time, end_time, codes, field, bar_counts, interval, True,
                                                      universe)
                    else:
                        raise Exception(f'get data error, message: {result["msg"]}')
                if universe is not None and not isinstance(universe, str):
                    if codes is not None:
                        universe = universe.reindex(columns=codes)
                    data = data.reindex(columns=universe.columns)
                    universe = universe.reindex(index=data.index)
                    return data * universe
                return data
        return None

    def __get_remote_fin_data(self, start_time, end_time, field, quarter_shift, quarter, interval, relogin=False,
                              universe=None, publish_merge=None, quarter_merge=None):
        token = self.__login(relogin)
        if token is None:
            return None
        t1 = time.time()
        data_json = {
            'start_time': start_time, 'end_time': end_time, 'field': field, 'quarter_shift': quarter_shift,
            'quarter': quarter, 'interval': interval, 'publish_merge': publish_merge, 'quarter_merge': quarter_merge
        }
        if isinstance(universe, str):
            data_json['universe'] = universe
        response = self.__request('api/factor/data/get_fin_data', data_json, {'Authorization': token})
        if response is not None:
            with BytesIO() as stream_data:
                for chunk in response.iter_content(chunk_size=1024):
                    # 处理数据块
                    if chunk:
                        # 在这里自定义处理数据块的逻辑
                        stream_data.write(chunk)
                stream_data.seek(0)
                if stream_data.getvalue()[0] == 65:
                    data = pd.read_feather(stream_data).set_index('trade_date')
                    data.columns = data.columns.astype(int)
                    print(
                        f'get field {field} from remote, start time {start_time}, end time {end_time}, cost {time.time() - t1}')
                else:
                    result = json.loads(stream_data.getvalue())
                    if result.get('code', 0) == -1 and not relogin:
                        data = self.__get_remote_fin_data(start_time, end_time, field, quarter_shift, quarter, interval,
                                                          True, universe)
                    else:
                        raise Exception(f'get fin data error, message: {result["msg"]}')
                if universe is not None and not isinstance(universe, str):
                    data = data.reindex(columns=universe.columns)
                    universe = universe.reindex(index=data.index)
                    return data * universe
                else:
                    return data
        return None

    def __login(self, relogin=False):
        if self.__token is None or relogin:
            result = self.__request('api/user/login', {
                'username': self.username,
                'password': self.password,
            })
            if result is not None:
                result = json.loads(result.text)
                if result['success']:
                    self.__token = result['value']['token']
                    print(f'login success, role : {result["value"]["role"]}, {result["value"]["msg"]}')
                else:
                    print(f'login error, message: {result["msg"]}')

        return self.__token

    def __request(self, url_suffix, json, headers=None, stream=False):
        self.__lock.acquire()
        size = len(self.__server_list)
        firs_index = self.__valid_url_index
        resp = None
        while True:
            url_prefix = self.__server_list[self.__valid_url_index]
            try:
                resp = requests.post(f'{url_prefix}' + f'/{url_suffix}'.replace('//', '/'), json=json, headers=headers,
                                     stream=stream)
                if resp.status_code == 200:
                    return resp
                else:
                    print(f'request error, http status {resp.status_code}')
                    return None
            except Exception as e:
                print(f'{self.__server_list[self.__valid_url_index]} invalid')
                if firs_index != (self.__valid_url_index + 1) % size:
                    self.__valid_url_index = (self.__valid_url_index + 1) % size
                else:
                    break
            finally:
                self.__lock.release()
        return resp

    def __apply_universe(self, start_time, end_time, codes, universe):
        if universe is None:
            return universe
        if isinstance(universe, pd.DataFrame):
            if codes is not None:
                universe = universe.reindex(columns=codes)
            return universe
        if isinstance(universe, str):
            return self.get_data(start_time, end_time, field=universe)
