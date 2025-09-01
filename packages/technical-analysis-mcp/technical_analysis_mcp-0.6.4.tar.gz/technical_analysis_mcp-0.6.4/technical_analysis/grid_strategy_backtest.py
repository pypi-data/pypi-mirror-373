import logging
import akshare as ak
import backtrader as bt
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta, date
from .backtest_data import BacktestData
from .grid_loader import GridLoader

initial_cash = 100000

class Params:
    def __init__(self):
        self.initial_cash = 100000  # 初始资金
        self.rsi_period = 10    # RSI 周期
        self.start_date = None    # 回测开始日期
        self.end_date = None      # 回测结束日期
        self.asset = None
        self.max_price = None
        self.min_price = None
        self.buy_rsi_threshold = 70
        self.sell_rsi_threshold = 30
        self.position_size = 0.1     

class GridStrategy(bt.Strategy):
    """
    网格交易策略实现
    """
    

    def __init__(self, config):
        # 初始化参数
        self.params = Params()  # 初始化参数
        self.params.initial_cash = 100000
        self.params.rsi_period = 10  # 初始化RSI指标周期
        self.grid_levels = []  # 网格价格水平
        self.current_level = 0  # 当前网格层级
        self.peak = -float('inf')  # 资产峰值
        self.max_drawdown = 0  # 最大回撤
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)  # 初始化RSI指标
        self.trade_log = []  # 交易日志
        self.test_case = None  # 测试案例配置
        self.params.start_date = None  # 初始化时间参数
        self.params.end_date = None  # 初始化时间参数
        self.params.asset = None  # 初始化资产参数
        self.base_price = None  # 基准价格
        self.base_position = 0.1  # 初始仓位
        self.position_triggered=False
        self._initialize_grid(config)  # 初始化网格

    def _initialize_grid(self, config):
        """初始化网格价格水平"""
        # 从grid_parameters中提取参数
        grid_params = config.get('grid_parameters', {})
        self.params.min_price = config.get('price_range', {}).get('min', 3.8)
        self.params.max_price = config.get('price_range', {}).get('max', 4.2)
        
        # 从买卖区域提取RSI阈值
        self.params.buy_rsi_threshold = int(grid_params.get('buy_rsi_threshold', 70))
        self.params.sell_rsi_threshold = int(grid_params.get('sell_rsi_threshold', 30))
        
        # 设置资产和时间范围参数
        self.params.asset = config.get('metadata', {}).get('asset', '')
        self.params.start_date = config.get('start_date')
        self.params.end_date = config.get('end_date')
        
        self.grid_levels=config.get('grid_levels', [])

        
        self.current_level = len(self.grid_levels) // 2  # 中间层级
        
        # 检查当前价格是否接近base_price，如果是则执行首次交易
        self.base_price = config.get('trigger_conditions', {}).get('base_price', None)
        self.trigger_order_type = config.get('trigger_conditions', {}).get('order_type', 'limit')
        self.base_position = config.get('trigger_conditions', {}).get('position_size', 0.1)
        if self.base_price is not None:
            for i, level in enumerate(self.grid_levels):
                if level['price'] == self.base_price:
                    self.current_level = i
                    break
            else:
                # If base_price not found in grid_levels, find closest level
                closest_level = min(self.grid_levels, key=lambda x: abs(x['price'] - self.base_price))
                self.current_level = self.grid_levels.index(closest_level)

        
        logging.info(f"触发价格 {self.base_price} 网格层级: {self.grid_levels} 初始层级: {self.current_level}")
        
    def next(self):
        # 更新回撤数据
        current_value = self.broker.getvalue()
        if current_value > self.peak:
            self.peak = current_value
        drawdown = (self.peak - current_value) / self.peak
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

        # 检查当前日期是否在配置的时间范围内
        current_date = self.data.datetime.date()
        if current_date < self.params.start_date:
            return
        if current_date > self.params.end_date:
            # 以最新的开盘价卖出全部持仓
            position = self.broker.getposition(self.data)
            if position.size > 0:
                self.close()
                logging.info(f'已到达结束日期{self.params.end_date}, 以{current_date} 收盘价 {self.data.close[0]} 卖出全部持仓{position.size}')
            return
        
        # 只在有效日期范围内检查触发条件和网格交易
        if not self.position_triggered:  # 无持仓时建立初始网格
            self._check_trigger_conditions()
        else:
            self._check_grid()

    def _check_trigger_conditions(self):
        """检查是否满足交易条件"""
        current_date = self.data.datetime.date()
        size = int(self.params.initial_cash / self.base_price * self.base_position)
        
        # 添加详细的交易参数日志
        logging.info(f'准备触发交易: 日期={current_date}, 基准价格={self.base_price:.3f}, '
                    f'仓位比例={self.base_position:.2%}, 计算数量={size}, '
                    f'可用资金={self.broker.getcash():.2f}')
        
        if self.trigger_order_type == 'market':
            if size > 0 and self.broker.getcash() >= (size * self.data.close[0]):
                self.buy(size=size, data=self.data, exectype=bt.Order.Market)
                logging.info(f'触发交易条件: {current_date} 以当前市价 建立{self.base_position:.2%}底仓')
                self.position_triggered = True
            else:
                logging.warning(f'市价单交易条件不满足: 数量={size}, 所需资金={size * self.data.close[0]:.2f}, '
                              f'可用资金={self.broker.getcash():.2f}')
        else:
            trade_price = self.pre_calculate_trade_price(self.base_price)
            
            if trade_price and size > 0 and self.broker.getcash() >= (size * trade_price):
                self.buy(size=size, price=trade_price, data=self.data, exectype=bt.Order.Limit)
                logging.info(f'触发交易条件: {current_date} 价格{trade_price} 在网格范围内 建立{self.base_position:.2%}底仓')
                self.position_triggered = True
            else:
                logging.warning(f'限价单交易条件不满足: 价格={trade_price}, 数量={size}, '
                              f'所需资金={size * (trade_price or 0):.2f}, 可用资金={self.broker.getcash():.2f}')
    
    def pre_calculate_trade_price(self, grid_price, buy=True):
        """计算网格交易价格，允许在交易时间段内成交而不仅限于收盘价。使用当前K线的实时价格（high/low）作为交易触发条件"""
        # 获取当前K线的最高价和最低价
        #logging.debug(f"最高价: {self.data.high[0]}, 最低价: {self.data.low[0]}, 检查网格价格: {grid_price}")
        high_price = self.data.high[0]
        low_price = self.data.low[0]
        
        # 如果网格价格在当前K线的高低区间内，则直接使用网格价格
        if buy:
            if low_price <= grid_price:
                return grid_price
        else:
            if high_price >= grid_price:
                return grid_price
            
        # 如果网格价格不在当前K线的高低区间内，则不满足交易条件
        logging.warning(f'价格不在网格范围内: 最高价={high_price}, 最低价={low_price}, 网格价格={grid_price}')
        return None
        
    def _check_grid(self):
        """检查是否需要调整网格"""
        # 检查网格层级索引是否有效
        if self.current_level + 1 >= len(self.grid_levels) or self.current_level - 1 < 0:
            return
            
        # 价格(high)突破上层网格且RSI>sell_rsi_threshold 执行卖出
        upper_level = self.grid_levels[self.current_level + 1]
        if self.data.high[0] > upper_level['price'] and self.rsi[0] > self.params.sell_rsi_threshold:
            trade_price = upper_level['price']
            size=int(self.params.initial_cash / trade_price * upper_level['size'])
            position = self.broker.getposition(self.data).size
            self.sell(size=min(position, size), price=trade_price, exectype=bt.Order.Limit)
            self.current_level += 1
            
        # 价格(low)跌破下层网格且RSI<buy_rsi_threshold 执行买入
        lower_level = self.grid_levels[self.current_level - 1]
        if self.data.low[0] < lower_level['price'] and self.rsi[0] < self.params.buy_rsi_threshold:
            trade_price = lower_level['price']
            size=int(self.params.initial_cash / trade_price * lower_level['size'])
            cost = size * trade_price
            if self.broker.getcash() >= cost:
                self.buy(size=size, price=trade_price, exectype=bt.Order.Limit)
                self.current_level -= 1
            else:
                size = int(self.broker.getcash() / trade_price)
                self.buy(size=size, price=trade_price, exectype=bt.Order.Limit)
                self.current_level -= 1

    def calculate_utilization(self):
        """
        计算当前资金利用率
        公式: 持仓价值 / 总资金
        """
        position_value = self.broker.getvalue() - self.broker.getcash()
        total_value = self.broker.getvalue()
        return position_value / total_value if total_value > 0 else 0

    def notify_order(self, order):
        """
        订单状态变化回调
        :param order: 订单对象
        """
        # 记录所有订单状态变化
        order_status = order.getstatusname()
        logging.debug(f'订单状态变化: {order_status} - {order.ref}')
        
        if order.status in [order.Completed]:
            # 订单完成
            self.trade_log.append({
                'date': order.data.datetime.date(),
                'status': order.getstatusname(),
                'size': order.executed.size,
                'rsi': self.rsi[0],
                'price': order.executed.price,
                'current_level': self.current_level,
                'value': self.broker.getvalue(),
                'action': 'buy' if order.isbuy() else 'sell',
                'utilization': self.calculate_utilization()
            })
            logging.info(f'订单完成: {order_status} - 操作: {"买入" if order.isbuy() else "卖出"}, '
                        f'数量: {order.executed.size}, 价格: {order.executed.price:.3f}')
        elif order.status in [order.Rejected, order.Margin, order.Cancelled]:
            # 订单被拒绝、资金不足或被取消
            logging.warning(f'订单未完成: {order_status} - 操作: {"买入" if order.isbuy() else "卖出"}, '
                          f'原因: {order_status}')
        elif order.status in [order.Submitted, order.Accepted]:
            # 订单已提交或已接受
            logging.debug(f'订单已提交: {order_status} - 操作: {"买入" if order.isbuy() else "卖出"}')
            
def calculate_reward(strat, benchmark_return = None)->tuple[float, float]:
    # 获取最大回撤
    logging.info(f"最大回撤分析: {strat.max_drawdown} peak {strat.peak}")
    
    # 获取收益率
    if hasattr(strat.analyzers, 'returns'):
        logging.info(f"收益率分析: {strat.analyzers.returns.get_analysis()}")
        returns = strat.analyzers.returns.get_analysis()
        total_return = returns['rtot']  # 总收益率
        annual_return = returns['rnorm'] # 年化收益率
    else:
        total_return = 0
        annual_return = 0
    
    # 综合计算奖励值(综合考虑收益率、回撤和交易质量)
    reward = (1 - strat.max_drawdown * 2) * (1 + total_return*20) * (1 + annual_return*2)

    # 如果提供了基准收益率，则计算超额收益
    if benchmark_return is not None:
        excess_return = total_return - benchmark_return
        reward *= (1 + np.tanh(excess_return * 10) )
    else:
        excess_return = 0
    
    return reward, excess_return
        
# 获取当前日期和90天前日期
today = datetime.now().strftime('%Y%m%d')
days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')

def standardize_data(df, source_type):
    """
    标准化不同API返回的数据结构
    :param df: 原始DataFrame
    :param source_type: 数据源类型('stock'/'etf'/'daily')
    :return: 标准化后的DataFrame
    """
    if df is None:
        return None
        
    # 统一列名映射
    column_mapping = {
        'stock': {'日期': 'date', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount', '换手率': 'turnover_ratio', '涨跌幅': 'change_ratio'},
        'etf': {'日期': 'date', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount', '换手率': 'turnover_ratio', '涨跌幅': 'change_ratio'}
    }
    
    # 重命名列
    df = df.rename(columns=column_mapping.get(source_type, {}))
    
    # 确保包含所有必要列
    required_cols = ['date', 'open', 'close', 'high', 'low', 'volume']
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    # 标准化日期格式
    if 'date' in df.columns:
        df['date_original'] = df['date'].copy()  # 复制date列
        df['date_original'] = pd.to_datetime(df['date_original'])
        df.set_index('date_original', inplace=True)
        df.sort_index(inplace=True)
        
    return df

def get_etf_data(etf_code='510300', start_date=None, end_date=None):
    """
    获取ETF历史数据
    :param etf_code: ETF代码
    :param start_date: 开始日期(YYYYMMDD)
    :param end_date: 结束日期(YYYYMMDD)
    :return: DataFrame
        包含以下列:
        - date: 日期
        - open: 开盘价
        - close: 收盘价
        - high: 最高价
        - low: 最低价
        - volume: 成交量(单位:份)
    """
    logging.info(f"开始获取ETF数据，参数: etf_code={etf_code}, start_date={start_date}, end_date={end_date}")
    
    if not start_date:
        start_date = days_ago
    if not end_date:
        end_date = today
        
    try:
        logging.debug("正在请求akshare fund_etf_hist_em API...")
        df = ak.fund_etf_hist_em(symbol=etf_code, start_date=start_date, end_date=end_date, adjust="hfq")
        
        if df.empty:
            logging.warning("返回的ETF数据集为空，请检查参数和网络连接")
            return None
            
        logging.info(f"成功获取ETF数据，共{len(df)}条记录")
        
        return standardize_data(df, 'etf')
    except Exception as e:
        logging.error(f"获取ETF数据失败: {e}")
        return None

def load_grid_params_from_jsonl(jsonl_path):
    """从JSONL文件加载网格参数"""
    params_list = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'output' in data:
                    # 如果output是字符串则尝试解析为JSON，否则直接使用
                    if isinstance(data['output'], str):
                        try:
                            params_list.append(json.loads(data['output']))
                        except json.JSONDecodeError:
                            params_list.append(data['output'])
                    else:
                        params_list.append(data['output'])
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析错误: {e}, 行内容: {line}")
                continue
    return params_list

def run_backtest(config)->BacktestData:
    # 2. 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 1. 使用akshare获取数据
    asset = config.get('metadata', {}).get('asset', None)
    if not asset:
        raise ValueError("配置文件中未找到有效的asset字段")
    # 在开始和结束日期前后各添加一周缓冲
    buffer_days = timedelta(days=7)
    date_start=config['start_date']
    date_end=config['end_date']
    
    date_start_str = (date_start - buffer_days * 2).strftime('%Y%m%d')
    date_end_str = (date_end + buffer_days).strftime('%Y%m%d')
    logging.debug(f"获取{asset}数据的日期范围: {date_start_str} 到 {date_end_str}")
    stock_data = get_etf_data(asset, date_start_str, date_end_str)
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data.set_index('date', inplace=True)
    
    # 添加策略
    strategy = cerebro.addstrategy(GridStrategy, config=config)
    
    # 3. 加载数据
    data = bt.feeds.PandasData(dataname=stock_data)
    cerebro.adddata(data)
    
    # 4. 设置初始资金
    cerebro.broker.setcash(initial_cash)
    
    # 5. 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
    
    try:
        # 6. 运行回测
        logging.info(f'初始资金: {cerebro.broker.getvalue():.2f}')
        results = cerebro.run()
        logging.info(f'最终资金: {cerebro.broker.getvalue():.2f}')
        #打印最终价格
        logging.info(f'最终价格: {stock_data["close"].iloc[-1]:.3f}')

        # 计算基准收益率
        benchmark_return = (stock_data['close'].iloc[-1] - stock_data['close'].iloc[0]) / stock_data['close'].iloc[0]
        logging.info(f'基准收益率: {benchmark_return:.2%}')

        # 计算策略收益率
        strategy_return = (cerebro.broker.getvalue() / initial_cash ) - 1
        logging.info(f'策略收益率: {strategy_return:.2%}')
    except Exception as e:
        logging.error(f'回测失败: {e}')
        raise ValueError(f'回测失败: {e}') from e
    
    # 7. 输出性能指标
    strat = results[0]
    trade_count = len(strat.trade_log)
    logging.info(f'交易次数: {trade_count}')
    
    # 8. 打印交易日志
    logging.info('\n=== 交易日志 ===')
    for i, trade in enumerate(strat.trade_log, 1):
        logging.info(f'{i}. 日期: {trade["date"]}, 价格: {trade["price"]:.3f}, RSI:{trade["rsi"]}, 操作: {trade["action"]}, '
        f'数量: {trade["size"]}, current_level: {trade["current_level"]}, 资产价值: {trade["value"]:.2f}, 资金利用率: {trade["utilization"]:.2f}')
    reward, excess_return = calculate_reward(strat, benchmark_return)
    logging.info(f'reward:{reward}')
    # 9. 可视化结果
    
    # 返回BacktestData对象
    return BacktestData(
        strategy_name=config.get('metadata', {}).get('strategy_name', '网格交易策略'),
        asset=config.get('metadata', {}).get('asset', ''),
        start_date=date_start,
        end_date=date_end,
        benchmark_return=benchmark_return,
        strategy_return=strategy_return,
        excess_return=excess_return,
        reward=reward,
        trade_count=trade_count,
        max_drawdown=strat.max_drawdown,
        trade_log=strat.trade_log
    )

if __name__ == '__main__':
    # 从JSONL文件加载网格参数
    jsonl_path = 'e:/工作/文档/aigc_projects/网格/data/515030.jsonl'
    grid_params_list = load_grid_params_from_jsonl(jsonl_path)
    
    # 对每个网格参数配置运行回测
    results = []
    for params in grid_params_list:
        # 使用GridLoader加载配置
        config = GridLoader.load_from_dict(params)
        backtest_data = run_backtest(config)
        
        # 获取reward并保存结果
        results.append({
            'reward': backtest_data.reward
        })
    
    # 保存结果到新的JSONL文件
    output_path = 'e:/工作/文档/aigc_projects/网格/data/backtest_results.jsonl'
    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
