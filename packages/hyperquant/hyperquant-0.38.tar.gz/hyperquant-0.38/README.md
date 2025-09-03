# minquant

minquant is a minimalistic framework for quantitative trading strategies. It allows users to quickly validate their strategy ideas with ease and efficiency.

## Core APIs

### `core.py`
主要功能包括：
- `ExchangeBase` 和 `Exchange` 类：实现基础的交易功能
  - 资产管理（初始资金、已实现/未实现盈亏等）
  - 下单交易（买入、卖出、平仓等）
  - 仓位管理和风控
  - 账户状态更新和记录
- `gen_back_time` 函数：回测时间周期管理，支持训练和测试时间区间的生成

### `draw.py`
主要功能包括：
- 支持多种图表类型：K线、曲线、柱状图等
- 提供丰富的交互功能：
  - 时间轴缩放和跳转
  - 自动播放功能
  - 多图表联动显示
  - 指标叠加功能
- 提供详细的数据标注：
  - 交易信号标记
  - 数据显示和提示
  - 自定义颜色和样式

### `logkit.py`
主要功能包括：
- 自定义日志级别和格式化：
  - DEBUG: 调试信息
  - INFO: 普通信息（蓝色）
  - OK: 成功信息（绿色）
  - WARNING: 警告信息（黄色）
  - ERROR: 错误信息（红色）
  - CRITICAL: 严重错误（深红色）
- 支持多种日志输出：
  - 控制台彩色输出
  - 文件日志记录
- 提供便捷的日志分割线和时间戳功能
- 支持异常信息的格式化输出
- 可配置时区和时间显示

## 使用方法

### 1. 初始化交易环境
```python
from core import Exchange
# 创建交易实例，设置初始资金和交易品种
exchange = Exchange(
    trade_symbols=['BTCUSDT'],  # 交易品种
    initial_balance=10000,      # 初始资金
    fee=0.0002,                # 手续费率
    recorded=True              # 是否记录交易历史
)
```

### 2. 执行交易操作
```python
# 买入操作
exchange.Buy('BTCUSDT', price=30000, amount=0.1, time='2024-01-01')

# 卖出操作
exchange.Sell('BTCUSDT', price=31000, amount=0.1, time='2024-01-02')

# 获取账户状态
print(exchange.stats)
```

### 3. 绘制分析图表
```python
from draw import draw
import pandas as pd

# 准备数据
data_df = pd.DataFrame({
    'date': [...],      # 时间列
    'open': [...],      # 开盘价
    'close': [...],     # 收盘价
    'high': [...],      # 最高价
    'low': [...],       # 最低价
    'volume': [...]     # 成交量
})

# 配置图表
data_dict = [
    {
        'series_name': 'K线图',
        'draw_type': 'Kline',
        'height': 60,
        'col': ['open', 'close', 'low', 'high']
    },
    {
        'series_name': '成交量',
        'draw_type': 'Bar',
        'height': 20,
        'col': 'volume'
    }
]

# 绘制图表
draw(
    df=data_df,
    data_dict=data_dict,
    date_col='date',
    title='BTC/USDT'
)
```

### 4. 日志记录
```python
from logkit import get_logger

# 创建日志实例
logger = get_logger(
    name='strategy',                  # 日志名称
    file_path='logs/strategy.log',    # 日志文件路径
    show_time=True,                   # 显示时间戳
    use_color=True                    # 使用彩色输出
)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("普通信息")
logger.ok("成功信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 使用分割线
logger.divider("回测开始", sep='=', display_time=True)
```
