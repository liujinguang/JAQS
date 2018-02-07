# encoding: UTF-8
'''
Created on Feb 7, 2018

@author: bob
'''

from __future__ import print_function, division, unicode_literals, absolute_import

import time
import numpy as np

import jaqs.util as jutil

from config_path import DATA_CONFIG_PATH, TRADE_CONFIG_PATH
from trade.strategy import EventDrivenStrategy

data_config = jutil.read_json(DATA_CONFIG_PATH)
trade_config = jutil.read_json(TRADE_CONFIG_PATH)

result_dir_path = '../../output/day_trading'


class DayTrading(EventDrivenStrategy):
    '''
    High-frequency trading
    '''
    
    def __init__(self):
        super(DayTrading, self).__init__()
        
        self.symbol = ''
        
    def init_from_config(self, props):
        '''        
        '''
        super(DayTrading, self).init_from_config(props)
        

if __name__ == '__main__':
    pass