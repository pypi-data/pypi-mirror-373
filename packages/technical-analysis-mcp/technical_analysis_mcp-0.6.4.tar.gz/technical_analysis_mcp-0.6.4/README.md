# 技术指标分析工具
该工具提供mcp服务器用于分析ETF和股票的技术指标。它使用`akshare`库获取历史数据，并计算RSI、布林带和移动平均线等技术指标。该工具支持ETF和股票历史数据分析。


## API文档

mcp服务器提供的接口:

### analyze_etf_technical

```python
@mcp.tool()
def analyze_etf_technical(etf_code='510300', with_market_style=False):
    """
    ETF技术指标分析工具
    :param etf_code: ETF代码 (例如'510300')
    :param with_market_style: 是否包含市场风格分类 (True/False)
    :param base_date: 基准日期，格式为YYYYMMDD (可选)
    :return: 包含技术指标的Markdown表格(最后5条记录)
    """
```

**新增字段说明**:


**参数**:
- `etf_code`: ETF代码，默认为'510300'(沪深300ETF)

**返回值**:
- 包含以下技术指标的Markdown表格:
  - 价格数据
  - RSI指标
  - 布林带
  - 移动平均线
  - `atr`: 平均真实波幅(10日)，衡量价格波动性的指标，数值越大表示波动越大
  - `mkt_style`: 市场风格分类结果

**示例**:
```python
result = analyze_etf_technical('510300')
print(result)
```

### analyze_stock_hist_technical

```python
@mcp.tool()
def analyze_stock_hist_technical(stock_code='000001'):
    """
    股票历史数据技术指标分析工具
    :param stock_code: 股票代码 (例如'000001')
    :param base_date: 基准日期，格式为YYYYMMDD (可选)
    :return: 包含技术指标的Markdown表格(最后5条记录)
    """
```

**参数**:
- `stock_code`: 股票代码，默认为'000001'(平安银行)

**返回值**:
- 包含以下技术指标的Markdown表格:
  - 价格数据
  - RSI指标
  - 布林带
  - 移动平均线
  - `atr`: 平均真实波幅(10日)，衡量价格波动性的指标，数值越大表示波动越大
  - `mkt_style`: 市场风格分类结果

**示例**:
```python
result = analyze_stock_hist_technical('000001')
print(result)
```

### get_stock_news

```python
@mcp.tool()
def get_stock_news(news_count=3, publish_before=None):
    """
    以时间线方式获取股票市场最新事件，包括政策、行业动态和市场行情
    :param news_count: 返回新闻数量 (默认3条)
    :param publish_before: 发布日期上限 (格式YYYY-MM-DD)
    :return: 新闻列表 (JSON格式)
    """
```

**参数**:
- `news_count`: 返回新闻数量，默认为3条
- `publish_before`: 发布日期上限，格式为YYYY-MM-DD

**返回值**:
- 新闻列表 (JSON格式)

**示例**:
```python
result = get_stock_news(news_count=5)
print(result)
```

### screen_etf_anomaly_in_tech

```python
@mcp.tool()
def screen_etf_anomaly_in_tech(etf_codes="513050", base_date=None, lookback_days=60, top_k=10):
    """
    筛选ETF异动行情，基于技术指标分析找出近期表现异常的ETF
    :param etf_codes: 要筛选的ETF代码列表，默认为"513050"，多个代码用逗号分隔
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param lookback_days: 回溯天数，用于计算技术指标(默认60天)
    :param top_k: 返回排名前几的ETF(默认10个)
    :return: 包含异动ETF信息的Markdown表格，包括ETF代码、名称、异常指标和得分
    """
```

**参数**:
- `etf_codes`: ETF代码列表，默认为"513050"
- `base_date`: 基准日期，格式为YYYYMMDD
- `lookback_days`: 回溯天数，默认为60天
- `top_k`: 返回排名前几的ETF，默认为10个

**返回值**:
- 包含异动ETF信息的Markdown表格

**示例**:
```python
result = screen_etf_anomaly_in_tech(etf_codes="513050,510300")
print(result)
```

## 安装与配置

### 安装
```bash
pip install technical-analysis-mcp
```

### 配置
1. 确保已安装Python 3.8+版本
2. 需要配置akshare数据源(可选)
3. 运行MCP服务器:
```bash
technical-analysis-mcp
```

### 市场风格分类示例
```python
# 获取带市场风格分类的ETF技术指标
result = analyze_etf_technical('510300', with_market_style=True)
print(result)

# 获取带市场风格分类的股票技术指标
result = analyze_stock_hist_technical('000001', with_market_style=True)
print(result)
```

## MCP配置示例
```json
{
  "mcpServers": {
    "technical-analysis-mcp": {
      "command": "uvx",
      "args": ["technical-analysis-mcp"]
    }
  }
}
```
## Restful API

使用uvicorn启动FastAPI应用：
```bash
uvicorn technical_analysis.http:app --reload --port 8000
```

应用启动后，可以通过以下地址访问API文档：
http://localhost:8000/docs