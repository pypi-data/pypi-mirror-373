from datetime import datetime
import logging
import time
import pandas as pd
import numpy as np
from scipy.stats import yeojohnson, zscore
import sys
import os


output_file='/data/情绪指标_完整版_2021-2025.csv'

from .stock_data import get_etf_data

def calculate_market_sentiment():
    """ 计算沪深300（510300）和创业板 (159915)加权复合后的市场情绪指标 """
    logging.info(f"正在计算市场情绪指标")
    df = calculate_market_sentiment_score(etf_code='510300')
        # 计算创业板 (159915) 的市场情绪指标
    df_gem = calculate_market_sentiment_score(etf_code='159915')
    if df_gem is not None:
        # 加权复合沪深300和创业板的情绪分数 (权重: 沪深300 70%, 创业板 30%)
        df['复合情绪分数'] = df['缩量调整后情绪分数_EMA5'] * 0.7 + df_gem['缩量调整后情绪分数_EMA5'] * 0.3


    # 动态分级阈值调整（基于10%/40%/60%/90%分位数，标签改为悲观-乐观）
    score_col = '复合情绪分数'
    if score_col in df.columns:
        # 移除NaN值用于分位数计算
        valid_data = df[score_col].dropna()
        if len(valid_data) > 0:
            try:
                df['情绪分级(悲观-乐观)'] = pd.qcut(
                    df[score_col],
                    q=[0, 0.1, 0.3, 0.7, 0.9, 1.0],
                    labels=['极度悲观', '悲观', '中性', '乐观', '极度乐观'],
                    duplicates='drop'
                )
            except Exception as e:
                print(f"情绪分级失败: {str(e)}")
                df['情绪分级(悲观-乐观)'] = '未知'
        else:
            df['情绪分级(悲观-乐观)'] = '未知'
    else:
        df['情绪分级(悲观-乐观)'] = '未知'

    # 保存最终结果
    try:
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.abspath(os.path.dirname(output_file)))
        df.to_csv(output_file, encoding='utf-8-sig')
        print(f"最终完整版CSV文件生成成功：{output_file}")
    except Exception as e:
        print(f"保存文件失败：{str(e)}")
    if df.index.name != 'date':
        df.index = df['date']
    return df

def calculate_market_sentiment_score(etf_code='510300'):
    """
    计算市场情绪指标
    
    Parameters:
    etf_code (str): ETF代码，默认为'510300'(沪深300ETF)
    output_file (str): 输出的情绪指标文件路径
    
    Returns:
    pandas.DataFrame: 包含情绪指标的DataFrame
    """
    
    # 读取原始数据
    try:
        print(f"正在获取ETF数据，代码: {etf_code}")
        df = get_etf_data(etf_code=etf_code, duration=900)
        
        if df is None or df.empty:
            print(f"获取ETF数据失败: {etf_code}")
            return None
            
        print(f"成功获取ETF数据，共{len(df)}条记录")
        
        # 重命名列以匹配原有逻辑
        df = df.rename(columns={
            'open': '开盘价',
            'high': '最高价', 
            'low': '最低价',
            'close': '收盘价',
            'volume': '成交量',
            'amount': '成交额'
        })
        
    except Exception as e:
        print(f"读取ETF数据失败：{str(e)}")
        return None

    # 确保必要的列存在
    required_columns = ['收盘价', '成交量']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"缺少必要的列: {missing_columns}")
        return None

    # 计算涨跌幅和成交量变化率
    df['涨跌幅'] = df['收盘价'].pct_change()
    df['成交量变化率'] = df['成交量'].pct_change()

    # 计算原始情绪分数
    df['原始情绪分数'] = df['涨跌幅'] * df['成交量变化率']

    # 缩量调整
    # 缩量上涨：涨跌幅>0且成交量变化率<0
    cond_up = (df['涨跌幅'] > 0) & (df['成交量变化率'] < 0)
    df.loc[cond_up, '缩量调整后情绪分数'] = df.loc[cond_up, '原始情绪分数'] * (1 + df.loc[cond_up, '成交量变化率'])

    # 缩量下跌：涨跌幅<0且成交量变化率<0
    cond_down = (df['涨跌幅'] < 0) & (df['成交量变化率'] < 0)
    df.loc[cond_down, '缩量调整后情绪分数'] = df.loc[cond_down, '原始情绪分数'] * (1 - df.loc[cond_down, '成交量变化率'])

    # 非缩量情况直接使用原始分数
    if '缩量调整后情绪分数' not in df.columns:
        df['缩量调整后情绪分数'] = df['原始情绪分数']
    else:
        df['缩量调整后情绪分数'].fillna(df['原始情绪分数'], inplace=True)

    # Min-Max标准化至[-1,1]
    min_max_cols = ['原始情绪分数', '缩量调整后情绪分数']
    for col in min_max_cols:
        if col in df.columns:
            col_min = df[col].min()
            col_max = df[col].max()
            if col_max > col_min:
                df[f'{col}_MinMax标准化'] = (df[col] - col_min) / (col_max - col_min) * 2 - 1
            else:
                df[f'{col}_MinMax标准化'] = 0  # 避免除以零

    # Yeo-Johnson变换（自动选择最优lambda）+ Z-score标准化
    for col in min_max_cols:
        if col in df.columns:
            data = df[col].copy()
            data_filled = data.fillna(data.mean())  # 填充NaN值
            try:
                transformed_data, lambda_opt = yeojohnson(data_filled)  # 获取最优lambda
                df[f'{col}_YeoJohnson变换'] = transformed_data
                df[f'{col}_正态标准化'] = zscore(transformed_data)
                df[f'{col}_EMA5'] = df[f'{col}_正态标准化'].ewm(span=5, adjust=False).mean()

                print(f"{col} Yeo-Johnson最优lambda: {lambda_opt:.4f}")
            except Exception as e:
                print(f"{col} 变换失败: {str(e)}")
                df[f'{col}_YeoJohnson变换'] = data_filled
                df[f'{col}_正态标准化'] = zscore(data_filled)
                df[f'{col}_EMA5'] = df[f'{col}_正态标准化'].ewm(span=5, adjust=False).mean()

    

    return df


def load_exists_data_file():
    logging.info(f"正在加载文件 {output_file}")
    df = pd.read_csv(output_file, index_col='date')
    file_mod_time = os.path.getmtime(output_file)
    return (df, file_mod_time)
    
cached_data = load_exists_data_file()

def get_sentiment_by_date(trade_date):
    """
    获取最新的市场情绪状态
    
    Parameters:
    df (pandas.DataFrame): 包含情绪指标的DataFrame
    
    Returns:
    dict: 当前情绪状态信息
    """
    # 检查文件最后更新时间，如果超过一天则重新生成
    if os.path.exists(output_file):
        _, file_mod_time = cached_data
        current_time = time.time()
        if (current_time - file_mod_time) > 86400:  # 86400秒 = 1天
            logging.info(f"文件 {output_file} 已更新，重新生成, current_time: {current_time}, file_mod_time: {file_mod_time}")
            df = calculate_market_sentiment()
            if df is not None:
                df.to_csv(output_file)
        else:
            logging.info(f"文件 {output_file} 未更新，使用缓存数据")
            df, _ = cached_data
    else:
        df = calculate_market_sentiment()
        if df is not None:
            df.to_csv(output_file)

    

    # 如果 date 是索引列，直接通过索引检索
    if trade_date in df.index:
        df = df.loc[[trade_date]]
    else:
        print(f"未找到 trade_date 为 {trade_date} 的记录")
        return None


    if df is None or len(df) == 0:
        return None
    
    latest_row = df.iloc[-1]
    sentiment_info = {
        'date': latest_row.name.strftime('%Y-%m-%d') if hasattr(latest_row.name, 'strftime') else str(latest_row.name),
        'close_price': latest_row.get('收盘价', 'N/A'),
        'price_change': latest_row.get('涨跌幅', 'N/A'),
        'volume_change': latest_row.get('成交量变化率', 'N/A'),
        'adjusted_sentiment_score': latest_row.get('复合情绪分数', 'N/A'),
        'sentiment_level': latest_row.get('情绪分级(悲观-乐观)', '未知')
    }
    
    return sentiment_info

if __name__ == "__main__":
    
    current_sentiment = get_sentiment_by_date(datetime.now().strftime('%Y-%m-%d'))
    if current_sentiment:
        print("\n=== 最新市场情绪状态 ===")
        for key, value in current_sentiment.items():
            print(f"{key}: {value}")
