

from datetime import date
import json
import logging
import os

from technical_analysis.grid_loader import GridLoader
from technical_analysis.grid_strategy_backtest import run_backtest
from openai import OpenAI, APITimeoutError, APIConnectionError, InternalServerError, NotFoundError
import requests

api_key = os.getenv("OPENAI_API_KEY", "default_api_key")

openai_client = OpenAI(
                api_key=api_key,
                base_url="https://api.siliconflow.cn/v1"
            )

def generate_trading_strategy(etf_code: str, trading_plan: str, base_date: date = None, enable_thinking=False):
    try:
        # 构建提示词
        think_str = "" if enable_thinking else "/no_think"
        json_sample = """{
"metadata": {
"asset": "159919",
"start_date": "2025-01-01",//策略开始日期
"end_date": "2025-01-15"
},
"trigger_conditions": {
"base_price": 4.003,
"order_type": "limit", //limit or market
"position_size": 0.10,
"calculation_basis": "推算过程..."
},
"price_range": {
"min": 3.800,
"max": 4.200
},
"grid_parameters": {
"buy_rsi_threshold": 70,
"sell_rsi_threshold": 30,
"zones": [
{
    "price_level": 3.840,
    "position_size_change": 0.50
},
...
]
},
"risk_management": {
"max_drawdown": 0.20,
"stop_loss": 3.600
},
"reason":"参数推算过程...",
"market_style_prediction":"根据近期价格走势及成交量判断，未来一段时间为...",
"pause_condition": "下跌趋势形成...",
"trend_strength":0.2
}"""

        if etf_code and base_date:
            prompt = f"""作为专业的量化交易策略工程师，请根据以下交易计划为ETF {etf_code} 生成一个可执行的JSON交易策略：

交易计划：
{json.dumps(trading_plan, ensure_ascii=False, indent=2)}

开始日期：{base_date.strftime("%Y%m%d")}

完整交易策略：
- 严格按照以下样例的格式输出JSON，不要附带其他无关的内容。
{json_sample}

{think_str}
"""
        else:
            prompt = f"""作为专业的量化交易策略工程师，请根据以下交易计划生成一个可执行的JSON交易策略：
{json.dumps(trading_plan, ensure_ascii=False, indent=2)}

完整交易策略：
- 严格按照以下样例的格式输出JSON，不要附带其他无关的内容。
{json_sample}

{think_str}
"""
        # 调用OpenAI API生成交易计划
        response = openai_client.chat.completions.create(
            model="Qwen/Qwen3-8B",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        # 解析响应
        content = response.choices[0].message.content
        
        # 尝试提取JSON内容
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = content[json_start:json_end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logging.exception(f"无法解析JSON: {json_str}")
                return {}
            
    except Exception as e:
        return {}


def trading_strategy_backtest(trading_strategy:dict):
    """
    对交易策略进行回测，返回回测结果
    :param trading_strategy: 交易策略配置 (JSON格式)
    :return: 回测结果 (JSON格式)
    """
    config = GridLoader.load_from_dict(trading_strategy)
    return run_backtest(config)