# -*- coding: utf-8 -*-
"""
ETF异动筛选器
基于ATR10/MA10和RSI10指标筛选出现行情异动的ETF
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .stock_data import get_etf_data, calculate_rsi, calculate_atr, calculate_moving_averages

logging.basicConfig(level=logging.INFO)

# 主要ETF代码列表
MAIN_ETF_CODES = [
    '510300',  # 沪深300ETF
    '510500',  # 中证500ETF
    '510050',  # 上证50ETF
    '159915',  # 创业板ETF
    '512000',  # 券商ETF
    '512880',  # 证券ETF
    '515030',  # 新能源车ETF
    '512690',  # 酒ETF
    '512170',  # 医疗ETF
    '512010',  # 医药ETF
    '515790',  # 光伏ETF
    '512480',  # 半导体ETF
    '512720',  # 计算机ETF
    '512760',  # 芯片ETF
    '159928',  # 消费ETF
    '510900',  # H股ETF
    '513050',  # 中概互联网ETF
    '512980',  # 传媒ETF
    '512660',  # 军工ETF
    '159949',  # 创业板50ETF
]

def calculate_atr_ma_ratio(data, atr_window=10, ma_window=10):
    """
    计算ATR与MA的比率，用于衡量波动率相对于价格的异动程度
    :param data: 包含价格数据的DataFrame
    :param atr_window: ATR计算窗口
    :param ma_window: MA计算窗口
    :return: ATR/MA比率
    """
    if len(data) < max(atr_window, ma_window):
        return None
    
    # 计算ATR和MA
    data = calculate_atr(data, window=atr_window)
    data = calculate_moving_averages(data, windows=[ma_window])
    
    atr_col = f'atr'
    ma_col = f'ma_{ma_window}'
    
    # 计算ATR/MA比率
    atr_ma_ratio = data[atr_col] / data[ma_col]
    return atr_ma_ratio

from functools import lru_cache
import pickle

def cache_key(*args, **kwargs):
    """生成缓存键，处理datetime对象"""
    key_args = []
    for arg in args:
        if isinstance(arg, datetime):
            key_args.append(arg.strftime('%Y%m%d%H%M%S'))
        else:
            key_args.append(arg)
    key_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, datetime):
            key_kwargs[k] = v.strftime('%Y%m%d%H%M%S')
        else:
            key_kwargs[k] = v
    return pickle.dumps((key_args, key_kwargs))

@lru_cache(maxsize=32)
def screen_etf_anomaly_cached(*args, **kwargs):
    """带缓存的screen_etf_anomaly包装函数"""
    return screen_etf_anomaly(*args, **kwargs)

def screen_etf_anomaly(etf_codes:tuple=None, end_date = datetime.now(), lookback_days=60, 
                      atr_ma_threshold=0.02, rsi_threshold_low=30, 
                      rsi_threshold_high=70, min_volume_ratio=1.5):
    """
    基于ATR10/MA10和RSI10筛选行情异动的ETF
    
    :param etf_codes: ETF代码列表，如果为None则使用默认列表
    :param lookback_days: 回看天数
    :param atr_ma_threshold: ATR/MA比率阈值，超过此值认为波动率异动
    :param rsi_threshold_low: RSI超卖阈值
    :param rsi_threshold_high: RSI超买阈值
    :param min_volume_ratio: 最小成交量比率阈值（相对于20日均量）
    :return: DataFrame包含筛选结果和异动指标
    """
    if etf_codes is None:
        etf_codes = tuple(MAIN_ETF_CODES)
    
    results = []
    
    for etf_code in etf_codes:
        try:
            # 获取ETF数据
            start_date = end_date - timedelta(days=lookback_days + 30)  # 多取一些数据用于计算指标
            df = get_etf_data(etf_code, 
                            start_date=start_date.strftime('%Y%m%d'), 
                            end_date=end_date.strftime('%Y%m%d'))
            
            if df is None or len(df) < lookback_days:
                continue
            
            # 计算技术指标
            df = calculate_rsi(df, window=10)
            df = calculate_moving_averages(df, windows=[10, 20])
            df['atr'] = calculate_atr(df, window=10)
            
            # 计算ATR/MA比率
            df['atr_ma_ratio'] = (df['atr'] / df['ma_10']).astype(np.float16)
            
            # 计算成交量比率
            df['volume_ma20'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = (df['volume'] / df['volume_ma20']).astype(np.float16)
            
            
            # 遍历lookback_days中的每一天
            for day_offset in range(lookback_days):
                #logging.info(day_offset)
                if day_offset >= len(df):
                    continue
                    
                # 获取当前日期的数据
                current_idx = -day_offset - 1
                if current_idx < -len(df):
                    continue
                    
                current_data = df.iloc[current_idx]
                current_date = df.index[current_idx]
                
                # 获取回看窗口数据（当前日期往前看20天）
                lookback_start = max(0, len(df) - day_offset - 20)
                lookback_end = len(df) - day_offset
                recent_data = df.iloc[lookback_start:lookback_end]
                
                if len(recent_data) < 10:  # 确保有足够的数据
                    continue
                
                # 检查异动条件
                anomaly_score = 0
                anomaly_reasons = []
                #logging.info(f"扫描日期 {current_date}")
                
                # 1. ATR/MA比率异动
                current_atr_ma = current_data['atr_ma_ratio']
                avg_atr_ma = recent_data['atr_ma_ratio'].mean()
                if current_atr_ma > avg_atr_ma * 1.2 and current_atr_ma > atr_ma_threshold:
                    anomaly_score += 2
                    anomaly_reasons.append(f"波动率异动(ATR/MA={current_atr_ma:.3f})")
                
                # 2. RSI极端值
                current_rsi = current_data['rsi_10']
                if current_rsi <= rsi_threshold_low:
                    anomaly_score += 2
                    anomaly_reasons.append(f"超卖信号(RSI={current_rsi:.1f})")
                elif current_rsi >= rsi_threshold_high:
                    anomaly_score += 2
                    anomaly_reasons.append(f"超买信号(RSI={current_rsi:.1f})")
                
                # 3. 成交量异动
                current_volume_ratio = current_data['volume_ratio']
                if current_volume_ratio >= min_volume_ratio:
                    anomaly_score += 1
                    anomaly_reasons.append(f"成交量放大({current_volume_ratio:.1f}倍)")
                
                # 4. 价格突破
                current_price = current_data['close']
                ma10 = current_data['ma_10']
                ma20 = current_data['ma_20']
                
                # 计算价格变化（相对于5天前和10天前）
                price_change_5d = 0
                price_change_10d = 0
                
                if day_offset + 5 < len(df):
                    price_5d_ago = df.iloc[-(day_offset + 5)]['close']
                    price_change_5d = (current_price / price_5d_ago - 1) * 100
                    
                if day_offset + 10 < len(df):
                    price_10d_ago = df.iloc[-(day_offset + 10)]['close']
                    price_change_10d = (current_price / price_10d_ago - 1) * 100
                
                if abs(price_change_5d) > 3:
                    anomaly_score += 1
                anomaly_reasons.append(f"5日涨跌幅{price_change_5d:+.1f}%")
                
                # 5. 价格偏离均线
                price_ma10_dev = (current_price / ma10 - 1) * 100
                if abs(price_ma10_dev) > 2:
                    anomaly_score += 1
                    anomaly_reasons.append(f"价格偏离MA10({price_ma10_dev:+.1f}%)")
                
                # 如果有异动，添加到结果
                if anomaly_score >= 3:  # 至少满足2个条件
                    result = {
                        'etf_code': etf_code,
                        'etf_name': get_etf_name(etf_code),
                        'current_price': current_price,
                        'price_change_5d': price_change_5d,
                        'price_change_10d': price_change_10d,
                        'rsi_10': current_rsi,
                        'atr_ma_ratio': current_atr_ma,
                        'volume_ratio': current_volume_ratio,
                        'anomaly_score': anomaly_score,
                        'anomaly_reasons': '; '.join(anomaly_reasons),
                        'last_date': current_date.strftime('%Y-%m-%d')
                    }
                    results.append(result)
                
        except Exception as e:
            print(f"处理ETF {etf_code} 时出错: {e}")
            continue
    
    # 转换为DataFrame并排序
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('anomaly_score', ascending=False)
        return results_df
    else:
        return pd.DataFrame()

def get_etf_name(etf_code):
    """获取ETF名称"""
    etf_names = {
        '510300': '沪深300ETF',
        '510500': '中证500ETF',
        '510050': '上证50ETF',
        '159915': '创业板ETF',
        '512000': '券商ETF',
        '512880': '证券ETF',
        '515030': '新能源车ETF',
        '512690': '酒ETF',
        '512170': '医疗ETF',
        '512010': '医药ETF',
        '515790': '光伏ETF',
        '512480': '半导体ETF',
        '512720': '计算机ETF',
        '512760': '芯片ETF',
        '159928': '消费ETF',
        '510900': 'H股ETF',
        '513050': '中概互联网ETF',
        '512980': '传媒ETF',
        '512660': '军工ETF',
        '159949': '创业板50ETF',
    }
    return etf_names.get(etf_code, f'ETF{etf_code}')

def get_top_anomaly_etfs(top_n=10, **kwargs):
    """
    获取异动最明显的top N ETF
    :param top_n: 返回前N个ETF
    :param kwargs: 传递给screen_etf_anomaly的其他参数
    :return: DataFrame
    """
    results = screen_etf_anomaly_cached(**kwargs)
    if not results.empty:
        return results.head(top_n)
    return results

def format_anomaly_results(results_df):
    """
    格式化异动筛选结果
    :param results_df: 筛选结果DataFrame
    :return: 格式化的字符串
    """
    if results_df.empty:
        return "未找到符合条件的异动ETF"
    
    output = []
    output.append("=== ETF行情异动筛选结果 ===")
    output.append(f"筛选时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    for _, row in results_df.iterrows():
        output.append(f"【{row['etf_name']}({row['etf_code']})】")
        output.append(f"当前价格: ¥{row['current_price']:.3f}")
        output.append(f"5日涨跌: {row['price_change_5d']:+.1f}%")
        output.append(f"10日涨跌: {row['price_change_10d']:+.1f}%")
        output.append(f"RSI(10): {row['rsi_10']:.1f}")
        output.append(f"波动率: {row['atr_ma_ratio']:.3f}")
        output.append(f"成交量: {row['volume_ratio']:.1f}倍")
        output.append(f"异动评分: {row['anomaly_score']}")
        output.append(f"异动原因: {row['anomaly_reasons']}")
        output.append(f"最后更新: {row['last_date']}")
        output.append("-" * 50)
    
    return "\n".join(output)


def main():
    logging.info(format_anomaly_results(get_top_anomaly_etfs()))


if __name__ == "__main__":
    main()
