# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from functools import lru_cache
import json

from . import market_sentiment
from .trading_strategy import generate_trading_strategy, trading_strategy_backtest

from .grid_loader import GridLoader
from .stock_data import get_etf_data, get_stock_hist_data, calculate_rsi, calculate_atr, calculate_bollinger_bands, calculate_moving_averages, classify_market_style
from .etf_screener import screen_etf_anomaly, screen_etf_anomaly_cached
from .grid_strategy_backtest import run_backtest
from .vector_db import VectorDB
from mcp.server.fastmcp import FastMCP
import pandas as pd
import asyncio

import logging

import sys
sys.stdout.reconfigure(encoding='utf-8')

mcp = FastMCP(host="0.0.0.0", port=8000)

NEWS_TOKEN = "token-7d02g64d2e187fd83b0i2hh4bd8j"

knowledge_base = VectorDB("events", "event")

#@mcp.resource("data://etf/{etf_code}/indicators.md?with_market_style={with_market_style}&base_date={base_date}")
@mcp.tool(name="analyze_etf_technical")
def analyze_etf_technical(etf_code='510300', with_market_style: bool=True, base_date: str=None, return_days: int=5, return_format: str='markdown'):
    """
    ETF技术指标分析工具，获取包括价格、RSI(10日)、布林带等关键指标
    :param etf_code: ETF代码 (例如'510300') 不要使用LOF代码
    :param with_market_style: 是否对市场风格进行分类 (True/False)
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param return_days: 返回最后几条数据 (默认为5条)
    :param return_format: 返回数据格式 (默认为markdown，可选为json)
    :return: 包含技术指标的DataFrame (Markdown格式)
    
    返回数据示例:
    | date       | close | rsi_10 | boll_upper | boll_middle | boll_lower | ma_5 | ma_10 | ma_20 | volume |
    |------------|-------|--------|------------|-------------|------------|------|-------|-------|--------|
    | 2023-01-01 | 4.12  | 65.32  | 4.25       | 4.10        | 3.95       | 4.08 | 4.05  | 4.02  | 120000 |
    
    字段说明:
    - date: 交易日期
    - close: 收盘价
    - rsi_10: 10日相对强弱指数(30-70为正常区间)
    - boll_upper: 布林带上轨(20日平均+2倍标准差)
    - boll_middle: 布林带中轨(20日移动平均)
    - boll_lower: 布林带下轨(20日平均-2倍标准差)
    - ma_5: 5日移动平均
    - ma_10: 10日移动平均
    - ma_20: 20日移动平均
    - atr: 平均真实波幅(10日)，衡量价格波动性的指标
    - mkt_style: 市场风格分类结果
    - volume: 成交量(单位:份)，反映市场活跃度，高成交量通常伴随价格趋势确认
    """
    # 判断base_date是否为None
    df = get_etf_data(etf_code=etf_code, end_date=base_date, duration=90+return_days)
    
    if df is not None:
        # 计算技术指标
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        df['atr'] = calculate_atr(df)
        
        # 如果需要进行市场风格分类
        if with_market_style:
            df = pd.concat([df, classify_market_style(df)], axis=1)
        df.index.name = 'date'
        # 返回最后return_days条数据
        if return_format == 'markdown':
            return df.tail(return_days).to_markdown()
        else:
            return df.tail(return_days).to_dict(orient='records')
    else:
        raise Exception(f"无法获取数据，请检查输入参数{etf_code}是否正确。 ")


#@mcp.resource("data://stock/{stock_code}/indicators.md?with_market_style={with_market_style}&base_date={base_date}")
@mcp.tool(name="analyze_stock_hist_technical")
def analyze_stock_hist_technical(stock_code='000001', with_market_style: bool=True, base_date: str=None, return_days: int=5, return_format: str='markdown'):
    """
    股票历史数据技术指标分析工具，获取包括价格、RSI(10日)、布林带等关键指标
    :param stock_code: 股票代码 (例如'000001')
    :param with_market_style: 是否对市场风格进行分类 (True/False)
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param return_days: 返回最后几条数据 (默认为5条)
    :param return_format: 返回数据格式 (默认为markdown，可选为json)
    :return: 包含技术指标的DataFrame (Markdown格式)
    
    返回数据示例:
    | date       | close | rsi_10 | boll_upper | boll_middle | boll_lower | ma_5 | ma_10 | ma_20 | volume |
    |------------|-------|--------|------------|-------------|------------|------|-------|-------|--------|
    | 2023-01-01 | 12.45 | 58.76  | 12.80      | 12.40       | 12.00      | 12.38| 12.35 | 12.30 | 45000  |
    
    字段说明:
    - date: 交易日期
    - close: 收盘价
    - rsi_10: 10日相对强弱指数(30-70为正常区间)
    - boll_upper: 布林带上轨(20日平均+2倍标准差)
    - boll_middle: 布林带中轨(20日移动平均)
    - boll_lower: 布林带下轨(20日平均-2倍标准差)
    - ma_5: 5日移动平均
    - ma_10: 10日移动平均
    - ma_20: 20日移动平均
    - atr: 平均真实波幅(10日)，衡量价格波动性的指标
    - mkt_style: 市场风格分类结果
    - volume: 成交量(单位:手，1手=100股)，反映市场活跃度，高成交量通常伴随价格趋势确认
    """
    # 获取数据
    df = get_stock_hist_data(stock_code=stock_code, end_date=base_date, duration=90+return_days)
    
    if df is not None:
        # 计算技术指标
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        df['atr'] = calculate_atr(df)
        
        # 如果需要进行市场风格分类
        if with_market_style:
            df = pd.concat([df, classify_market_style(df)], axis=1)
        df.index.name = 'date'
        # 返回最后return_days条数据
        if return_format == 'markdown':
            return df.tail(return_days).to_markdown()
        else:
            return df.tail(return_days).to_dict(orient='records')
    else:
        raise Exception(f"无法获取数据，请检查输入参数{stock_code}是否正确。")

@mcp.tool(name="screen_etf_anomaly_in_tech")
def screen_etf_anomaly_in_tech(etf_codes=("513050"), base_date: str = None,
                                    lookback_days: int = 60, top_k: int=10):
    """
    筛选ETF异动行情，基于技术指标分析找出近期表现异常的ETF
    
    :param etf_codes: 要筛选的ETF代码列表，默认为("513050")，多个代码用逗号分隔
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param lookback_days: 回溯天数，用于计算技术指标(默认60天)
    :param top_k: 返回排名前几的ETF(默认10个)
    :return: 包含异动ETF信息的Markdown表格，包括ETF代码、名称、异常指标和得分
    
    返回数据示例:
    | etf_code | etf_name | anomaly_score | rsi | boll_band_width | volume_change |
    |----------|----------|---------------|-----|-----------------|---------------|
    | 513050   | 中概互联 | 0.85          | 72  | 0.12            | 1.5           |
    
    字段说明:
    - etf_code: ETF代码
    - etf_name: ETF名称
    - anomaly_score: 异常得分(0-7)，越高表示异常程度越大
    - volume_change: 成交量变化率(最近5日平均/60日平均)
    """
    # 处理日期参数
    end_date = datetime.strptime(base_date, '%Y%m%d') if base_date and len(base_date)>=8  else datetime.now()
    
    # 处理ETF代码参数
    etf_list = tuple(etf_codes.split(',')) if etf_codes else None
    return screen_etf_anomaly_cached(etf_list, end_date=end_date,  lookback_days=lookback_days)[0:top_k].to_markdown()

@mcp.tool(name="get_stock_news")
@lru_cache(maxsize=50)
def get_stock_news(news_count: int = 3, publish_before: str = None):
    """
    以时间线方式获取股票市场最新事件，包括政策、行业动态和市场行情
    :param news_count: 返回新闻数量 (默认3条)
    :param publish_before: 发布日期上限 (格式YYYY-MM-DD)
    :return: 新闻列表 (JSON格式)
    """
    import requests
    url = "https://fin-news-http-stock-mapiokjbpk.cn-hangzhou.fcapp.run/daily_news"
    
    if publish_before:
        params = {
            'news_count': news_count,
            'publish_before': publish_before
        }
    else:
        params = {
            'news_count': news_count
        }
    
    headers = {
        'Authorization': f'Bearer {NEWS_TOKEN}'
    }
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"请求失败，状态码: {response.status_code}")

@mcp.tool()
def test_trading_strategy(etf_code: str, trading_plan: str, base_date: date = datetime.now() - timedelta(days=30)):
    """
    测试多条件交易策略的执行情况。
    
    Args:
        etf_code (str): ETF代码，用于指定测试的标的。
        trading_plan (str): 指定使用的交易策略 包括： 1. 趋势判断和交易方向（买入/卖出/波段） 2. 进入时机和初始仓位比例(0-1之间的数值), 市价开仓还是限价开仓 3. 退出时机和两周内波段交易计划, 假设两周后不管是否盈利都需要平仓
        base_date (date, optional): 基准日期，用于回测的起始日期。默认为一月前的日期。
    
    Returns:
        返回回测结果或策略表现数据。
    
    """
    trading_strategy = generate_trading_strategy(etf_code, trading_plan, base_date)
    return trading_strategy_backtest(trading_strategy)

@mcp.tool(name="trading_strategy_backtest")
def trading_strategy_backtest_mcp(trading_strategy:dict):
    """
    对交易策略进行回测，返回回测结果
    :param trading_strategy: 交易策略配置 (JSON格式)
    :return: 回测结果 (JSON格式)
    """
    return trading_strategy_backtest(trading_strategy)



@mcp.tool()
def search_related_news_in_knowledge_base(query):
    """从知识库中检索与查询相关的事件及其对ETF的影响。

    :param query: 查询字符串，用于在知识库中检索相关新闻
    :return: 包含匹配新闻的列表，每个新闻包含字段：event, etf, market, event_date, factors, confidence, logic
    """

    # 先从知识库中检索
    results = knowledge_base.retrieve(query, output_fields=["event", "etf", "market", "event_date", "factors", "confidence", "logic", "market_sentiment"])

    return results

@mcp.tool(name="get_sentiment_by_date")
def get_sentiment_by_date(date: str):
    """
    获取指定日期的市场情绪
    :param date: 指定日期，格式YYYY-MM-DD
    :return: 市场情绪，包含字段：date, adjusted_sentiment_score, sentiment_level
    """
    return market_sentiment.get_sentiment_by_date(date)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='ETF技术指标分析工具')
    parser.add_argument('--transport', type=str, default='stdio', help='指定传输方式，默认为stdio')
    args = parser.parse_args()
    mcp.run(transport=args.transport)

if __name__ == "__main__":
    main()
