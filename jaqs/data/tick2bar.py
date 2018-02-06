# encoding: UTF-8
'''
This module is used to load the ticks from csv files and transfer them to bar
type.


Created on Feb 5, 2018

@author: bob
'''

import datetime
import pandas as pd
import numpy as np

from pandas.core.indexes.range import RangeIndex

def load_and_merge_ticks(file_path, freq='3s'):
    '''
    transfer the tick data to bar data
    '''
    
    # load csv file
    data = pd.read_csv(file_path, dtype={'code': 'str', 'date': 'str', 'time': 'str'})
    
    # reindex the data with date time 
    mtime = data['time'].apply(lambda x: x[:2] + ':' + x[2:4] + ':' + x[4:6] + '.' + x[6:])
    data.index = data['date'].str.cat(mtime.tolist(), sep=' ')
    data.index = pd.DatetimeIndex(data.index)
    
    # resample the data
    data = data.resample(freq, closed='left', label='left').last()
    data = data[(data.index.time <= datetime.time(11, 30)) | (data.index.time > datetime.time(13, 0))]
    
    # deal with the data before open
    data_before_open = data[data.index.time <= datetime.time(9, 30)]
    data_before_open = data_before_open.dropna()
    data = data[data.index.time > datetime.time(9, 30)].fillna(method='pad')
    data = pd.concat([data_before_open, data])
    
    #reset the time columns according the latest index
    data['time'] = data.index.to_series().apply(lambda x: int("%02d%02d%02d000" % (x.hour, x.minute, x.second)))
    data['date'] = data['date'].apply(lambda x : int(x))
    
    data.index = RangeIndex(start=0, stop=len(data))
    
    return data

def ticks2bar(tk_data, freq='3s'):
    '''
    '''
    tk_data['freq'] = freq
    tk_data['settle'] = np.nan
    tk_data['open'] = np.nan
    tk_data = pd.DataFrame(tk_data[tk_data['time'] >= 93000000])
    tk_data.reset_index(inplace=True)
    
    volume_diff = tk_data['volume'].diff(periods=1)
    volume_diff[0] = tk_data['volume'][0]
    tk_data['volume'] = volume_diff
    
    turnover_diff = tk_data['turnover'].diff(periods=1)
    turnover_diff[0] = tk_data['turnover'][0]
    tk_data['turnover'] = turnover_diff
    
    tk_data['vwap'] = tk_data['turnover'] / tk_data['volume']
    
        
#     print(pd_stock[['volume', 'turnover', 'vwap', 'open', 'last']])
    
    tk_data = tk_data[['last', 'code', 'date', 'freq', 'high', 'low', 
                                   'iopv', 'open', 'settle', 'symbol', 'time', 
                                   'turnover', 'volume', 'vwap']]
    tk_data.columns = ['close', 'code', 'date', 'freq', 'high', 'low', 
                                  'io', 'open', 'settle', 'symbol', 'time',
                                  'turnover', 'volume', 'vwap']    
    
    return tk_data

def get_tick_bar(symbol, start_time, end_time, trade_date, freq='3s'):
    '''
    load raw data from csv file and 
    '''
    universe, market = symbol.split('.')
    if market == 'SH':
        file_name = "%s%s%d.csv" % ('sh', universe, trade_date)
    else:
        file_name = "%s%s%d.csv" % ('sh', universe, trade_date)
        
    file_path = '../../data/' + file_name
    
    return ticks2bar(load_and_merge_ticks(file_path, freq), freq)
    
    

if __name__ == '__main__':
#     tk_data = load_and_merge_ticks('../../data/sh60051920171130.csv')
#     print(ticks2bar(tk_data))
    bar_data = get_tick_bar(symbol="600519.SH", start_time=200000, end_time=160000, trade_date=20171130, freq='3s')
    print(bar_data)
    