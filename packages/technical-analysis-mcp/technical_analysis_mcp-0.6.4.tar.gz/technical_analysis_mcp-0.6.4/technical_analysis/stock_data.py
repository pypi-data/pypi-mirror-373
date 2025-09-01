import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


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
        'etf': {'日期': 'date', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount', '换手率': 'turnover_ratio', '涨跌幅': 'change_ratio'},
        'daily': {'date': 'date', 'open': 'open', 'close': 'close', 'high': 'high', 'low': 'low', 'volume': 'volume'}
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
        df['date'] = pd.to_datetime(df['date_original'])
        #把date列设置为索引,
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        # 删除原始的 'date_original' 列
        df.drop('date_original', axis=1, inplace=True)
    return df



def get_daily_data(ts_code='160630.SZ', start_date=None, end_date=None):
    """
    获取日线数据
    :param ts_code: 股票代码
    :param start_date: 开始日期(YYYYMMDD)
    :param end_date: 结束日期(YYYYMMDD)
    :return: DataFrame
        包含以下列:
        - date: 日期
        - open: 开盘价
        - close: 收盘价
        - high: 最高价
        - low: 最低价
        - volume: 成交量(单位:手，1手=100股)
    """
    print(f"[DEBUG] 开始获取数据，参数: ts_code={ts_code}, start_date={start_date}, end_date={end_date}")
    
    
    if not end_date:
        base_date = datetime.now()
        end_date = base_date.strftime('%Y%m%d')
    else:
        base_date = datetime.strptime(end_date, '%Y%m%d')

    if not start_date:
        start_date = (base_date-timedelta(days=90)).strftime('%Y%m%d')
        
    try:
        print(f"[DEBUG] 正在请求akshare API...")
        df = ak.stock_zh_a_daily(symbol=ts_code.split('.')[0], start_date=start_date, end_date=end_date)
        
        if df.empty:
            print("[WARNING] 返回的数据集为空，请检查参数和网络连接")
            return None
            
        print(f"[DEBUG] 成功获取数据，共{len(df)}条记录")
        
        return standardize_data(df, 'daily')
    except Exception as e:
        print(f"[ERROR] 获取数据失败: {e}")
        return None
        
def get_etf_data(etf_code='510300', start_date=None, end_date=None, duration=90):
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
    print(f"[DEBUG] 开始获取ETF数据，参数: etf_code={etf_code}, start_date={start_date}, end_date={end_date}")
    
    if not end_date:
        base_date = datetime.now()
        end_date = base_date.strftime('%Y%m%d')
    else:
        if len(end_date) == 8:
            base_date = datetime.strptime(end_date, '%Y%m%d')
        else:
            base_date = datetime.strptime(end_date, '%Y-%m-%d')

    if not start_date:
        start_date = (base_date-timedelta(days=min(360*3, duration))).strftime('%Y%m%d')
        
    try:
        print(f"[DEBUG] 正在请求akshare fund_etf_hist_em API...")
        df = ak.fund_etf_hist_em(symbol=etf_code, start_date=start_date, end_date=end_date, adjust="hfq")
        df["symbol"]=etf_code
        
        if df.empty:
            print("[WARNING] 返回的ETF数据集为空，请检查参数和网络连接")
            return None
            
        print(f"[DEBUG] 成功获取ETF数据，共{len(df)}条记录")
        
        return standardize_data(df, 'etf')
    except Exception as e:
        print(f"[ERROR] 获取ETF数据失败: {e}")
        return None
        
def get_stock_hist_data(stock_code='000001', start_date=None, end_date=None, duration=90):
    """
    获取股票历史数据
    :param stock_code: 股票代码
    :param start_date: 开始日期(YYYYMMDD)
    :param end_date: 结束日期(YYYYMMDD)
    :return: DataFrame
        包含以下列:
        - date: 日期
        - open: 开盘价
        - close: 收盘价
        - high: 最高价
        - low: 最低价
        - volume: 成交量(单位:手，1手=100股)
    """
    print(f"[DEBUG] 开始获取股票历史数据，参数: stock_code={stock_code}, start_date={start_date}, end_date={end_date}")
    
    if not end_date:
        base_date = datetime.now()
        end_date = base_date.strftime('%Y%m%d')
    else:
        if len(end_date) == 8:
            base_date = datetime.strptime(end_date, '%Y%m%d')
        else:
            base_date = datetime.strptime(end_date, '%Y-%m-%d')

    if not start_date:
        start_date = (base_date-timedelta(days=min(120,duration))).strftime('%Y%m%d')
        
    try:
        print(f"[DEBUG] 正在请求akshare stock_zh_a_hist API...")
        df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="hfq")
        df["symbol"]=stock_code
        
        if df.empty:
            print("[WARNING] 返回的股票历史数据集为空，请检查参数和网络连接")
            return None
            
        print(f"[DEBUG] 成功获取股票历史数据，共{len(df)}条记录")
        
        return standardize_data(df, 'stock')
    except Exception as e:
        print(f"[ERROR] 获取股票历史数据失败: {e}")
        return None

def calculate_atr(data, window=10):
    """
    计算真实波动幅度ATR
    :param data: 包含最高价、最低价和收盘价的数据
    :param window: 计算ATR的窗口 (默认10)
    :return: 包含ATR的数据
    """
    high_low = data['high'] - data['low']
    high_close = abs(data['high'] - data['close'].shift())  
    low_close = abs(data['low'] - data['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=window).mean().astype(np.float16)
    return atr

def calculate_rsi(data, window=10):
    """
    计算RSI指标
    :param data: 包含收盘价的数据
    :param window: RSI计算窗口(默认10)
    :return: 包含RSI的数据
    """
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data[f'rsi_{window}'] = rsi.astype(np.float16)
    return data

def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    计算布林带指标
    :param data: 包含收盘价的数据
    :param window: 移动平均窗口
    :param num_std: 标准差倍数
    :return: 包含布林带的数据
    """
    rolling_mean = data['close'].rolling(window=window).mean().astype(np.float16)
    rolling_std = data['close'].rolling(window=window).std().astype(np.float16)
    
    data['boll_middle'] = rolling_mean
    data['boll_upper'] = rolling_mean + (rolling_std * num_std)
    data['boll_lower'] = rolling_mean - (rolling_std * num_std)
    return data

def calculate_moving_averages(data, windows=[5, 10, 20, 60]):
    """
    计算移动平均线
    :param data: 包含收盘价的数据
    :param windows: 移动平均窗口列表
    :return: 包含移动平均线的数据
    """
    for window in windows:
        data[f'ma_{window}'] = data['close'].rolling(window=window, min_periods=max(1,window-10)).mean().astype(np.float16)
    return data

def analyze_stock_technical(ts_code='000001'):
    """
    股票技术指标分析工具，获取包括价格、RSI、布林带等关键指标
    :param ts_code: 股票代码 (例如'000001')
    :return: 包含技术指标的DataFrame
    """
    # 获取数据
    df = get_daily_data(ts_code=ts_code)
    
    if df is not None:
        # 计算技术指标
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        
        # 返回最后5条数据
        return df.tail(5).to_markdown()
    else:
        raise Exception("无法获取数据，请检查tushare token和网络连接。")


def classify_market_style(
        df: pd.DataFrame,
        close: str = 'close',
        ma_5: str = 'ma_5',
        ma_20: str = 'ma_20',
        rsi_10: str = 'rsi_10',
        boll_upper: str = 'boll_upper',
        boll_middle: str = 'boll_middle',
        boll_lower: str = 'boll_lower',
        volume: str = 'volume',
        atr: str = 'atr',
        output_name:str = 'mkt_style',
        mkt_base_style: float = 1.0
) -> pd.DataFrame:
    """
    根据预计算的指标列，判断市场风格，并返回描述性字符串。
    返回一个新的DataFrame，仅包含 `mkt_style` 字段。
    
    mkt_style字段可能的取值和含义：
    - "上升趋势": 市场处于强劲上涨趋势
    - "下降趋势": 市场处于明显下跌趋势
    - "向上反转": 市场从下跌转为上涨
    - "向下反转": 市场从上涨转为下跌
    - "震荡行情": 市场处于横盘震荡状态
    - "震荡上行": 震荡行情但偏向上行
    - "震荡下行": 震荡行情但偏向下行
    
    示例:
    >>> df = classify_market_style(data)
    >>> df.head()
                    mkt_style
    date                    
    2023-01-01      上升趋势
    2023-01-02      上升趋势
    2023-01-03      震荡行情
    2023-01-04      向下反转
    2023-01-05      下降趋势
    """
    # 风格定义
    trend_up_threshold: str = "上升趋势"  # 趋势向上
    reversal_up_threshold: str = "向上反转"  # 反转向上
    range_threshold: str = "横盘震荡"  # 震荡
    reversal_down_threshold: str = "向下反转"  # 反转向下
    trend_down_threshold: str = "下降趋势"  # 趋势向下
    trend_range_down: str = "震荡下行"
    trend_range_up: str = "震荡上行"

    # 初始化一个新的DataFrame，复制原DataFrame结构但内容为空
    mkt_style_df = pd.DataFrame(index=df.index, columns=[output_name], dtype=str)
    mkt_style_df[output_name] = ''  # 初始化为空字符串

    

    # 计算辅助指标（如斜率）
    ma20_slope = df[ma_20].diff(3) / 3  # 3周期斜率

    # 计算布林带宽度
    band_width = df[boll_upper] - df[boll_lower]
    
    # 计算ATR相对波动率
    atr_ratio = df[atr] / df[close].rolling(20).mean()
    
    # 波动率动态调整参数
    atr_median = (df[boll_upper] - df[boll_lower]).rolling(20, min_periods=1).median().ffill()
    dynamic_spread_factor = 0.3 * mkt_base_style  # 动态调整均线间距阈值

    for i in range(0, len(df)):
        # 获取当前行索引
        idx = df.index[i]

        # --- 1. 趋势向上 ---
        if (
                df[ma_5].iloc[i] > df[ma_20].iloc[i] and
                ma20_slope.iloc[i] > 0 and
                df[rsi_10].iloc[i] > 60 and
                band_width.iloc[i] > band_width.rolling(50, min_periods=1).mean().iloc[i] * 0.7  and # 布林带宽度较宽
                atr_ratio.iloc[i] > 0.02  # ATR波动率较高
        ):
            mkt_style_df.at[idx, output_name] = trend_up_threshold

        # --- 2. 趋势向下 ---
        elif (
                df[ma_5].iloc[i] < df[ma_20].iloc[i] and
                ma20_slope.iloc[i] < 0 and
                df[rsi_10].iloc[i] < 60 and
                band_width.iloc[i] > band_width.rolling(50, min_periods=1).mean().iloc[i] * 0.7  and # 布林带宽度较宽
                atr_ratio.iloc[i] > 0.02  # ATR波动率较高
        ):
            mkt_style_df.at[idx, output_name] = trend_down_threshold

        # --- 3. 震荡（条件放宽）---
        elif (
                # 布林带宽度条件
                band_width.iloc[i] < band_width.rolling(50, min_periods=1).mean().iloc[i] * 1.2 and
                # RSI范围
                30 < df[rsi_10].iloc[i] < 70 and
                # 成交量条件
                df[volume].iloc[i] < df[volume].rolling(10, min_periods=1).mean().iloc[i] * 1.1 and
                # ATR波动率条件
                atr_ratio.iloc[i] < 0.04  # ATR波动率较低
        ):
            mkt_style_df.at[idx, output_name] = range_threshold

        # --- 4. 反转向上（放宽前置条件）---
        elif i > 0 and (
                # mkt_style_df['mkt_style'].iloc[i - 1] in [trend_down_threshold, range_threshold, trend_unknown] and
                df[close].iloc[i] > df[ma_5].iloc[i] and
                df[rsi_10].iloc[i] > 45 and
                df[rsi_10].iloc[i - 3] < 40 and
                df[volume].iloc[i] > df[volume].rolling(10, min_periods=1).mean().iloc[i] * 1.1
        ):
            mkt_style_df.at[idx, output_name] = reversal_up_threshold

        # --- 5. 反转向下（放宽前置条件）---
        elif i > 0 and (
                # mkt_style_df['mkt_style'].iloc[i - 1] in [trend_up_threshold, range_threshold, trend_unknown] and
                df[close].iloc[i] < df[ma_5].iloc[i] and
                df[rsi_10].iloc[i] < 55 and
                df[rsi_10].iloc[i - 3] > 60 and
                df[volume].iloc[i] > df[volume].rolling(10, min_periods=1).mean().iloc[i] * 1.1
        ):
            mkt_style_df.at[idx, output_name] = reversal_down_threshold

        # 其他情况视为趋势未知
        else:
            if df[ma_5].iloc[i] > df[ma_20].iloc[i]:
                mkt_style_df.at[idx, output_name] = str(trend_range_up)
            else:
                mkt_style_df.at[idx, output_name] = str(trend_range_down)

    return mkt_style_df