# encoding: utf-8

"""
A very first example of AlphaStrategy back-test:
    Market value weight among UNIVERSE.
    Benchmark is HS300.
    
"""
from __future__ import print_function, unicode_literals, division, absolute_import

from jaqs.data import RemoteDataService, DataView

import jaqs.util as jutil

from jaqs.trade import model
from jaqs.trade import (AlphaStrategy, AlphaBacktestInstance, AlphaTradeApi,
                        PortfolioManager, AlphaLiveTradeInstance, RealTimeTradeApi)
import jaqs.trade.analyze as ana

from config_path import DATA_CONFIG_PATH, TRADE_CONFIG_PATH

# data_config = {
#     "remote.data.address": "tcp://data.tushare.org:8910",
#     "remote.data.username": "YourTelephoneNumber",
#     "remote.data.password": "YourToken"
# }
# trade_config = {
#     "remote.trade.address": "tcp://gw.quantos.org:8901",
#     "remote.trade.username": "YourTelephoneNumber",
#     "remote.trade.password": "YourToken"
# }

data_config = jutil.read_json(DATA_CONFIG_PATH)
trade_config = jutil.read_json(TRADE_CONFIG_PATH)

# Data files are stored in this folder:
dataview_store_folder = '../../output/simplest/dataview'

# Back-test and analysis results are stored here
backtest_result_folder = '../../output/simplest'

UNIVERSE = '000807.SH'   #投资范围(universe)：中证申万食品饮料指数 000807.SH的所有成份股


def save_data():
    """
    This function fetches data from remote server and stores them locally.
    Then we can use local data to do back-test.

    """
    dataview_props = {# Start and end date of back-test
                      'start_date': 20170101, 'end_date': 20171231,
                      # Investment universe and performance benchmark
                      'universe': UNIVERSE, 'benchmark': '000300.SH',   #业绩比较基准(benchmark)：沪深300指数 000300.SH
                      # Data fields that we need
                      'fields': 'total_mv,turnover',
                      # freq = 1 means we use daily data. Please do not change this.
                      'freq': 1}

    # RemoteDataService communicates with a remote server to fetch data
    ds = RemoteDataService()
    # Use username and password in data_config to login
    ds.init_from_config(data_config)
    
    # DataView utilizes RemoteDataService to get various data and store them
    dv = DataView()
    dv.init_from_config(dataview_props, ds)
    dv.prepare_data()
    dv.save_dataview(folder_path=dataview_store_folder)


def do_backtest():
    # Load local data file that we just stored.
    dv = DataView()
    dv.load_dataview(folder_path=dataview_store_folder)
    
    backtest_props = {# start and end date of back-test
                      "start_date": dv.start_date,
                      "end_date": dv.end_date,
                      # re-balance period length
                      "period": "month",
                      # benchmark and universe
                      "benchmark": dv.benchmark,
                      "universe": dv.universe,
                      # Amount of money at the start of back-test
                      "init_balance": 1e8,
                      # Amount of money at the start of back-test
                      "position_ratio": 1.0,
                      }
    backtest_props.update(data_config)
    backtest_props.update(trade_config)

    # We use trade_api to send orders
    trade_api = AlphaTradeApi()
    # This is our strategy
    strategy = AlphaStrategy(pc_method='market_value_weight')
    # PortfolioManager helps us to manage tasks, orders and calculate positions
    pm = PortfolioManager()
    # BacktestInstance is in charge of running the back-test
    bt = AlphaBacktestInstance()

    # Public variables are stored in context. We can also store anything in it
    context = model.Context(dataview=dv, instance=bt, strategy=strategy, trade_api=trade_api, pm=pm)

    bt.init_from_config(backtest_props)
    bt.run_alpha()

    # After finishing back-test, we save trade results into a folder
    bt.save_results(folder_path=backtest_result_folder)


def do_livetrade():
    dv = DataView()
    dv.load_dataview(folder_path=dataview_store_folder)
    
    props = {"period": "day",
             "strategy_no": 1044,
             "init_balance": 1e6}
    props.update(data_config)
    props.update(trade_config)
    
    strategy = AlphaStrategy(pc_method='market_value_weight')
    pm = PortfolioManager()
    
    bt = AlphaLiveTradeInstance()
    trade_api = RealTimeTradeApi(props)
    ds = RemoteDataService()
    
    context = model.Context(dataview=dv, instance=bt, strategy=strategy, trade_api=trade_api, pm=pm, data_api=ds)
    
    bt.init_from_config(props)
    bt.run_alpha()
    
    goal_positions = strategy.goal_positions
    print("Length of goal positions:", len(goal_positions))
    task_id, msg = trade_api.goal_portfolio(goal_positions)
    print(task_id, msg)


def analyze_backtest_results():
    # Analyzer help us calculate various trade statistics according to trade results.
    # All the calculation results will be stored as its members.
    ta = ana.AlphaAnalyzer()
    dv = DataView()
    dv.load_dataview(folder_path=dataview_store_folder)
    
    ta.initialize(dataview=dv, file_folder=backtest_result_folder)

    ta.do_analyze(result_dir=backtest_result_folder,
                  selected_sec=list(ta.universe)[:3])


if __name__ == "__main__":
    is_backtest = True
    
    if is_backtest:
        save_data()
        do_backtest()
        analyze_backtest_results()
    else:
        save_data()
        do_livetrade()
