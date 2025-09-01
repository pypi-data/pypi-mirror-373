from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from technical_analysis.etf_screener import screen_etf_anomaly_cached
from .stock_data import get_etf_data, get_stock_hist_data, calculate_rsi, calculate_bollinger_bands, calculate_moving_averages, calculate_atr, classify_market_style
import pandas as pd

app = FastAPI(
    title="Technical Analysis API",
    description="金融技术指标分析API",
    version="0.3.4",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

@app.get("/api/etf/{etf_code}", summary="ETF技术指标分析")
async def analyze_etf_technical(etf_code: str = '510300', with_market_style: bool = True, base_date: str = None, return_days: int = 5) ->dict:
    """
    获取ETF技术指标数据
    - **etf_code**: ETF代码 (例如'510300') 不要使用LOF代码
    - **with_market_style**: 是否对市场风格进行分类 (True/False)
    - **base_date**: 基准日期(格式YYYYMMDD)，默认为当前日期
    - **return_days**: 返回最后几条数据 (默认为5条)
    
    返回格式示例:
    {
        "date": "2023-01-01",
        "close": 4.12,
        "rsi_10": 65.32,
        "boll_upper": 4.25,
        "boll_middle": 4.10,
        "boll_lower": 3.95,
        "ma_5": 4.08,
        "ma_10": 4.05,
        "ma_20": 4.02,
        "atr": 0.15,
        "mkt_style": "震荡市",
        "volume": 120000
    }
    
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
    df = get_etf_data(etf_code=etf_code, end_date=base_date, duration=90+return_days)
    if df is not None:
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        df['atr'] = calculate_atr(df)
        if with_market_style:
            df = pd.concat([df, classify_market_style(df)], axis=1)
        df.index.name = 'date'
        return {"results": df.tail(return_days).reset_index().to_dict(orient="records"), "v":app.version}
    else:
        return {"error": "无法获取数据"}

@app.get("/api/stock/{stock_code}", summary="股票技术指标分析")
async def analyze_stock_hist_technical(stock_code: str = '000001', with_market_style: bool = True, base_date: str = None, return_days: int = 5) ->dict:
    """
    获取股票技术指标数据
    - **stock_code**: 股票代码 (例如'000001')
    - **with_market_style**: 是否对市场风格进行分类 (True/False)
    - **base_date**: 基准日期(格式YYYYMMDD)，默认为当前日期
    - **return_days**: 返回最后几条数据 (默认为5条)
    
    返回格式示例:
    {
        "date": "2023-01-01",
        "close": 12.45,
        "open": 12.30,
        "high": 12.60,
        "low": 12.20,
        "volume": 12345678,
        "rsi_10": 58.75,
        "boll_upper": 12.80,
        "boll_middle": 12.45,
        "boll_lower": 12.10,
        "ma_5": 12.40,
        "ma_10": 12.38,
        "ma_20": 12.35,
        "atr": 0.45,
        "mkt_style": "上涨趋势"
    }
    
    字段说明:
    - date: 交易日期
    - close: 收盘价
    - open: 开盘价
    - high: 最高价
    - low: 最低价
    - volume: 成交量(股)
    - rsi_10: 10日相对强弱指数(30-70为正常区间)
    - boll_upper: 布林带上轨(20日平均+2倍标准差)
    - boll_middle: 布林带中轨(20日移动平均)
    - boll_lower: 布林带下轨(20日平均-2倍标准差)
    - ma_5: 5日移动平均
    - ma_10: 10日移动平均
    - ma_20: 20日移动平均
    - atr: 平均真实波幅(10日)，衡量价格波动性的指标
    - mkt_style: 市场风格分类结果
    """
    df = get_stock_hist_data(stock_code=stock_code, end_date=base_date, duration=90+return_days)
    if df is not None:
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        df['atr'] = calculate_atr(df)
        if with_market_style:
            df = pd.concat([df, classify_market_style(df)], axis=1)
        df.index.name = 'date'
        return {"results": df.tail(return_days).reset_index().to_dict(orient="records"), "v":app.version}
    else:
        return {"error": "无法获取数据"}

@app.get("/api/anomaly/etf", summary="ETF行情异动检测")
async def detect_etf_anomaly_advanced(etf_codes: str = None, 
                                    atr_ma_threshold: float = 0.02, 
                                    rsi_threshold_low: int = 30, 
                                    rsi_threshold_high: int = 70, 
                                    min_volume_ratio: float = 1.5,
                                    base_date: str = None,
                                    lookback_days: int = 30, top_k:int =10) -> dict:
    """
    ETF异动检测
    - **etf_codes**: ETF代码列表(逗号分隔)，如果为None则使用默认列表
    - **atr_ma_threshold**: ATR/MA比率阈值，超过此值认为波动率异动
    - **rsi_threshold_low**: RSI超卖阈值
    - **rsi_threshold_high**: RSI超买阈值
    - **min_volume_ratio**: 最小成交量比率阈值(相对于20日均量)
    - **base_date**: 基准日期(格式YYYYMMDD)，默认为当前日期
    - **lookback_days**: 回溯天数(默认为30天)
    
    返回格式示例:
    {
        "results": [
            {
                "etf_code": "510300",
                "etf_name": "沪深300ETF",
                "current_price": 4.12,
                "price_change_5d": 2.5,
                "price_change_10d": 5.2,
                "rsi_10": 72.5,
                "atr_ma_ratio": 0.025,
                "volume_ratio": 1.8,
                "anomaly_score": 4,
                "anomaly_reasons": "超买信号(RSI=72.5); 成交量放大(1.8倍)",
                "last_date": "2023-01-01"
            }
        ],
        "v": "0.3.4"
    }
    """
    from datetime import datetime
    
    # 处理日期参数
    end_date = datetime.strptime(base_date, '%Y%m%d') if base_date else datetime.now()
    
    # 处理ETF代码参数
    etf_list = tuple(etf_codes.split(',')) if etf_codes else None
    
    # 调用etf_screener模块
    results = screen_etf_anomaly_cached(
        etf_codes=etf_list,
        end_date=end_date,
        lookback_days=lookback_days,
        atr_ma_threshold=atr_ma_threshold,
        rsi_threshold_low=rsi_threshold_low,
        rsi_threshold_high=rsi_threshold_high,
        min_volume_ratio=min_volume_ratio
    )
    
    return {"results": results[0:top_k].reset_index().to_dict(orient="records"), "v": app.version}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Technical Analysis API",
        version="0.1.0",
        description="金融技术指标分析API",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi