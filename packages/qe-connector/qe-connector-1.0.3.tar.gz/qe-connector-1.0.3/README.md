# Quantum Execute Python SDK

[![Python Version](https://img.shields.io/pypi/pyversions/qe-connector)](https://pypi.org/project/qe-connector/)
[![PyPI Version](https://img.shields.io/pypi/v/qe-connector)](https://pypi.org/project/qe-connector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是 Quantum Execute 公共 API 的官方 Python SDK，为开发者提供了一个轻量级、易于使用的接口来访问 Quantum Execute 的交易服务。

## 功能特性

- ✅ 完整的 Quantum Execute API 支持
- ✅ 交易所 API 密钥管理
- ✅ 主订单创建与管理（TWAP、VWAP、POV 等算法）
- ✅ 订单查询和成交明细
- ✅ ListenKey 创建与管理
- ✅ 安全的 HMAC-SHA256 签名认证
- ✅ 支持生产环境和测试环境
- ✅ 链式调用 API 设计
- ✅ 完整的错误处理

## 安装

```bash
pip install qe-connector
```

或者从源码安装：

```bash
git clone https://github.com/Quantum-Execute/qe-connector-python.git
cd qe-connector-python
pip install -e .
```

## 快速开始

### 初始化客户端

```python
from qe.user import User as Client
import logging

# 配置日志（可选）
logging.basicConfig(level=logging.INFO)

# 创建生产环境客户端
client = Client(
    api_key="your-api-key",
    api_secret="your-api-secret"
)

# 创建测试环境客户端
client = Client(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://testapi.quantumexecute.com"
)
```

### 使用枚举类型（推荐）

SDK 提供了枚举类型来确保类型安全和代码提示。推荐使用枚举而不是字符串：

```python
# 导入枚举类型
from qe.lib import Algorithm, Exchange, MarketType, OrderSide, StrategyType, MarginType

# 可用的枚举值
print("算法类型:", [algo.value for algo in Algorithm])           # ['TWAP', 'VWAP', 'POV']
print("交易所:", [exchange.value for exchange in Exchange])     # ['Binance']
print("市场类型:", [market.value for market in MarketType])     # ['SPOT', 'PERP']
print("订单方向:", [side.value for side in OrderSide])         # ['buy', 'sell']
print("策略类型:", [strategy.value for strategy in StrategyType]) # ['TWAP_1', 'POV']
print("保证金类型:", [margin.value for margin in MarginType])   # ['U']

# 使用枚举创建订单（推荐）
response = client.create_master_order(
    algorithm=Algorithm.TWAP,        # 而不是 "TWAP"
    exchange=Exchange.BINANCE,       # 而不是 "Binance"
    marketType=MarketType.SPOT,      # 而不是 "SPOT"
    side=OrderSide.BUY,             # 而不是 "buy"
    # ... 其他参数
)
```

## API 参考

### 交易所 API 管理

#### 查询交易所 API 列表

查询当前用户绑定的所有交易所 API 账户。

**请求参数：**

| 参数名 | 类型 | 是否必传 | 描述 |
|--------|------|----------|------|
| page | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |
| exchange | str | 否 | 交易所名称筛选 |

**响应字段：**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| items | array | API 列表 |
| ├─ id | string | API 记录的唯一标识 |
| ├─ createdAt | string | API 添加时间 |
| ├─ accountName | string | 账户名称（如：账户1、账户2） |
| ├─ exchange | string | 交易所名称（如：Binance、OKX、Bybit） |
| ├─ apiKey | string | 交易所 API Key（部分隐藏） |
| ├─ verificationMethod | string | API 验证方式（如：OAuth、API） |
| ├─ balance | float | 账户余额（美元） |
| ├─ status | string | API 状态：正常、异常（不可用） |
| ├─ isValid | bool | API 是否有效 |
| ├─ isTradingEnabled | bool | 是否开启交易权限 |
| ├─ isDefault | bool | 是否为该交易所的默认账户 |
| ├─ isPm | bool | 是否为 Pm 账户 |
| total | int | API 总数 |
| page | int | 当前页码 |
| pageSize | int | 每页显示数量 |

**示例代码：**

```python
# 获取所有交易所 API 密钥
apis = client.list_exchange_apis()
print(f"共有 {apis['total']} 个 API 密钥")

# 打印每个 API 的详细信息
for api in apis['items']:
    print(f"""
API 信息：
    账户: {api['accountName']}
    交易所: {api['exchange']}
    状态: {api['status']}
    余额: ${api['balance']:.2f}
    交易权限: {'开启' if api['isTradingEnabled'] else '关闭'}
    是否默认: {'是' if api['isDefault'] else '否'}
    是否PM账户: {'是' if api['isPm'] else '否'}
    添加时间: {api['createdAt']}
    """)

# 带分页和过滤
apis = client.list_exchange_apis(
    page=1,
    pageSize=10,
    exchange="binance"
)
```

### 交易订单管理

#### 创建主订单

创建新的主订单并提交到算法侧执行。

**请求参数：**

| 参数名 | 类型 | 是否必传 | 描述 |
|--------|------|--------|------|
| **基础参数** |
| algorithm | string/Algorithm | 是 | 交易算法，可选值：TWAP、VWAP、POV |
| exchange | string/Exchange | 是 | 交易所名称，可选值：Binance |
| symbol | string | 是 | 交易对符号（如：BTCUSDT） |
| marketType | string/MarketType | 是 | 市场类型，可选值：SPOT（现货）、PERP（合约） |
| side | string/OrderSide | 是 | 买卖方向，可选值：buy（买入）、sell（卖出） |
| apiKeyId | string | 是 | 指定使用的 API 密钥 ID |
| **数量参数（二选一）** |
| totalQuantity | string | 否* | 要交易的总数量，支持字符串表示以避免精度问题，与 orderNotional 二选一，范围：>0 |
| orderNotional | string | 否* | 按价值下单时的金额，以计价币种为单位（如ETHUSDT为USDT数量），与 totalQuantity 二选一，范围：>0 |
| **时间参数** |
| startTime | string | 否 | 开始执行时间（ISO 8601格式） |
| endTime | string | 否 | 结束执行时间（ISO 8601格式） |
| executionDuration | int | 否 | 订单的有效时间（分钟），范围：>1 |
| **策略参数** |
| strategyType | string/StrategyType | 否 | 策略类型，如：TWAP_1、POV |
| **TWAP/VWAP 算法参数** |
| mustComplete | bool | 否 | 是否一定要在duration之内执行完，选false则不会追进度，默认：true |
| makerRateLimit | string | 否 | 要求maker占比超过该值（优先级低于mustcomplete），范围：0-1，默认："0" |
| povLimit | string | 否 | 占市场成交量比例限制，优先级低于mustcomplete，范围：0-1，默认："0.8" |
| limitPrice | string | 否 | 最高/低允许交易的价格，买的话就是最高价，卖就是最低价，超出范围停止交易，填"-1"不限制，范围：>0，默认："-1" |
| upTolerance | string | 否 | 允许超出schedule的容忍度，比如0.1就是执行过程中允许比目标进度超出母单数量的10%，范围：>0且<1，默认：-1 |
| lowTolerance | string | 否 | 允许落后schedule的容忍度，范围：>0且<1，默认：-1 |
| strictUpBound | bool | 否 | 是否追求严格小于uptolerance，开启后可能会把很小的母单也拆的很细，不建议开启，默认：false |
| tailOrderProtection | bool | 否 | 尾单必须taker扫完，如果false则允许省一点，小于交易所最小发单量，默认：true |
| **POV 算法参数** |
| povMinLimit | string | 否 | 占市场成交量比例下限，范围：小于max(POVLimit-0.01,0)，默认："0" |
| **其他参数** |
| reduceOnly | bool | 否 | 合约交易时是否仅减仓，默认：false |
| marginType | string/MarginType | 否 | 合约交易保证金类型，可选值：U（U本位） |
| notes | string | 否 | 订单备注 |

*注：totalQuantity 和 orderNotional 必须传其中一个  

**响应字段：**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| masterOrderId | string | 创建成功的主订单 ID |
| success | bool | 创建是否成功 |
| message | string | 创建结果消息 |

**示例代码：**

```python
# 导入枚举类型（推荐方式）
from qe.lib import Algorithm, Exchange, MarketType, OrderSide, StrategyType, MarginType

# TWAP 订单示例 - 使用枚举创建订单（推荐）
response = client.create_master_order(
    algorithm=Algorithm.TWAP,                      # 使用算法枚举
    exchange=Exchange.BINANCE,                     # 使用交易所枚举
    symbol="BTCUSDT",
    marketType=MarketType.SPOT,                    # 使用市场类型枚举
    side=OrderSide.BUY,                           # 使用订单方向枚举
    apiKeyId="your-api-key-id",                   # 从 list_exchange_apis 获取
    orderNotional="200",                          # $200 名义价值
    strategyType=StrategyType.TWAP_1,             # 使用策略类型枚举
    startTime="2025-09-02T19:54:34+08:00",
    endTime="2025-09-03T01:44:35+08:00",
    executionDuration="5",                        # 5 秒间隔
    mustComplete=True,                            # 必须完成全部订单
    worstPrice=-1,                               # -1 表示无价格限制
    upTolerance="-1",                            # 允许超出容忍度
    lowTolerance="-1",                           # 允许落后容忍度
    tailOrderProtection=True,                    # 尾单保护
    notes="测试 TWAP 订单"                       # 订单备注
)

if response.get('success'):
    print(f"主订单创建成功，ID: {response['masterOrderId']}")
else:
    print(f"创建失败：{response.get('message')}")
```

**POV 合约订单示例：**

```python
# POV 合约订单示例 - 使用枚举
response = client.create_master_order(
    algorithm=Algorithm.POV,                       # POV 算法
    exchange=Exchange.BINANCE,
    symbol="BTCUSDT",
    marketType=MarketType.PERP,                    # 合约市场
    side=OrderSide.SELL,                          # 卖出
    apiKeyId="your-api-key-id",
    orderNotional="1000",                         # $1000 名义价值
    strategyType=StrategyType.POV,                # POV 策略
    startTime="2025-09-02T19:54:34+08:00",
    endTime="2025-09-03T01:44:35+08:00",
    povLimit=0.2,                                 # 占市场成交量 20%
    povMinLimit=0.05,                             # 最低占市场成交量 5%
    marginType=MarginType.U,                      # U本位保证金
    reduceOnly=False,
    mustComplete=True,
    notes="POV 合约订单示例"
)

if response.get('success'):
    print(f"POV 订单创建成功，ID: {response['masterOrderId']}")
```

#### 查询主订单列表

获取用户的主订单列表。

**请求参数：**

| 参数名 | 类型 | 是否必传 | 描述 |
|--------|------|----------|------|
| page | int32 | 否 | 页码 |
| pageSize | int32 | 否 | 每页数量 |
| status | string | 否 | 订单状态筛选，可选值：NEW（执行中）、COMPLETED（已完成） |
| exchange | string | 否 | 交易所名称筛选 |
| symbol | string | 否 | 交易对筛选 |
| startTime | string | 否 | 开始时间筛选 |
| endTime | string | 否 | 结束时间筛选 |

**响应字段：**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| items | array | 主订单列表 |
| ├─ masterOrderId | string | 主订单 ID |
| ├─ algorithm | string | 算法 |
| ├─ algorithmType | string | 算法类型 |
| ├─ exchange | string | 交易所 |
| ├─ symbol | string | 交易对 |
| ├─ marketType | string | 市场类型 |
| ├─ side | string | 买卖方向 |
| ├─ totalQuantity | string | 总数量 |
| ├─ filledQuantity | string | 已成交数量 |
| ├─ averagePrice | float64 | 平均成交价 |
| ├─ status | string | 状态：NEW（创建，未执行）、WAITING（等待中）、PROCESSING（执行中，且未完成）、PAUSED（已暂停）、CANCEL（取消中）、CANCELLED（已取消）、COMPLETED（已完成）、REJECTED（已拒绝）、EXPIRED（已过期）、CANCEL_REJECT（取消被拒绝） |
| ├─ executionDuration | int32 | 执行时长（分钟） |
| ├─ priceLimit | float64 | 价格限制 |
| ├─ startTime | string | 开始时间 |
| ├─ endTime | string | 结束时间 |
| ├─ createdAt | string | 创建时间 |
| ├─ updatedAt | string | 更新时间 |
| ├─ notes | string | 备注 |
| ├─ marginType | string | 保证金类型（U:U本位） |
| ├─ reduceOnly | bool | 是否仅减仓 |
| ├─ strategyType | string | 策略类型 |
| ├─ orderNotional | string | 订单金额（USDT） |
| ├─ mustComplete | bool | 是否必须完成 |
| ├─ makerRateLimit | string | 最低 Maker 率 |
| ├─ povLimit | string | 最大市场成交量占比 |
| ├─ clientId | string | 客户端 ID |
| ├─ date | string | 发单日期（格式：YYYYMMDD） |
| ├─ ticktimeInt | string | 发单时间（格式：093000000 表示 9:30:00.000） |
| ├─ limitPriceString | string | 限价（字符串） |
| ├─ upTolerance | string | 上容忍度 |
| ├─ lowTolerance | string | 下容忍度 |
| ├─ strictUpBound | bool | 严格上界 |
| ├─ ticktimeMs | int64 | 发单时间戳（epoch 毫秒） |
| ├─ category | string | 交易品种（spot 或 perp） |
| ├─ filledAmount | float64 | 成交金额 |
| ├─ totalValue | float64 | 成交总值 |
| ├─ base | string | 基础币种 |
| ├─ quote | string | 计价币种 |
| ├─ completionProgress | float64 | 完成进度（0-1） |
| ├─ reason | string | 原因（如取消原因） |
| total | int32 | 总数 |
| page | int32 | 当前页码 |
| pageSize | int32 | 每页数量 |

**示例代码：**

```python
# 查询所有主订单
orders = client.get_master_orders()

# 带过滤条件查询
orders = client.get_master_orders(
    page=1,
    pageSize=20,
    status="NEW",              # 执行中的订单
    symbol="BTCUSDT",
    startTime="2024-01-01T00:00:00Z",
    endTime="2024-01-31T23:59:59Z"
)

# 打印订单详细信息
for order in orders['items']:
    print(f"""
订单信息：
    ID: {order['masterOrderId']}
    算法: {order['algorithm']} ({order.get('strategyType', 'N/A')})
    交易对: {order['symbol']} {order['marketType']}
    方向: {order['side']}
    状态: {order['status']}
    完成度: {order['completionProgress'] * 100:.2f}%
    平均价格: ${order.get('averagePrice', 0):.2f}
    已成交: {order['filledQuantity']} / {order['totalQuantity']}
    成交金额: ${order.get('filledAmount', 0):.2f}
    创建时间: {order['createdAt']}
    发单日期: {order.get('date', 'N/A')}
    上容忍度: {order.get('upTolerance', 'N/A')}
    下容忍度: {order.get('lowTolerance', 'N/A')}
    """)
```

#### 查询成交记录

获取用户的成交记录。

**请求参数：**

| 参数名 | 类型 | 是否必传 | 描述 |
|--------|------|----------|------|
| page | int32 | 否 | 页码 |
| pageSize | int32 | 否 | 每页数量 |
| masterOrderId | string | 否 | 主订单 ID 筛选 |
| subOrderId | string | 否 | 子订单 ID 筛选 |
| symbol | string | 否 | 交易对筛选 |
| startTime | string | 否 | 开始时间筛选 |
| endTime | string | 否 | 结束时间筛选 |

**响应字段：**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| items | array | 成交记录列表 |
| ├─ id | string | 记录 ID |
| ├─ orderCreatedTime | string | 订单创建时间 |
| ├─ masterOrderId | string | 主订单 ID |
| ├─ exchange | string | 交易所 |
| ├─ category | string | 市场类型 |
| ├─ symbol | string | 交易对 |
| ├─ side | string | 方向 |
| ├─ filledValue | float64 | 成交价值 |
| ├─ filledQuantity | string | 成交数量 |
| ├─ avgPrice | float64 | 平均价格 |
| ├─ price | float64 | 成交价格 |
| ├─ fee | float64 | 手续费 |
| ├─ tradingAccount | string | 交易账户 |
| ├─ status | string | 状态 |
| ├─ rejectReason | string | 拒绝原因 |
| ├─ base | string | 基础币种 |
| ├─ quote | string | 计价币种 |
| ├─ type | string | 订单类型 |
| total | int32 | 总数 |
| page | int32 | 当前页码 |
| pageSize | int32 | 每页数量 |

**示例代码：**

```python
# 查询特定主订单的成交明细
fills = client.get_order_fills(
    masterOrderId="your-master-order-id",
    page=1,
    pageSize=50
)

# 查询所有成交
fills = client.get_order_fills(
    symbol="BTCUSDT",
    startTime="2024-01-01T00:00:00Z",
    endTime="2024-01-01T23:59:59Z"
)

# 统计成交信息
total_value = 0
total_fee = 0
for fill in fills['items']:
    print(f"""
成交详情：
    时间: {fill['orderCreatedTime']}
    交易对: {fill['symbol']}
    方向: {fill['side']}
    成交价格: ${fill['price']:.2f}
    成交数量: {fill['filledQuantity']}
    成交金额: ${fill['filledValue']:.2f}
    手续费: ${fill['fee']:.4f}
    账户: {fill['tradingAccount']}
    类型: {fill.get('type', 'N/A')}
    """)
    total_value += fill['filledValue']
    total_fee += fill['fee']

print(f"总成交额: ${total_value:.2f}, 总手续费: ${total_fee:.2f}")
```

#### 取消主订单

取消指定的主订单。

**请求参数：**

| 参数名 | 类型 | 是否必传 | 描述 |
|--------|------|----------|------|
| masterOrderId | string | 是 | 要取消的主订单 ID |
| reason | string | 否 | 取消原因 |

**响应字段：**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| success | bool | 取消是否成功 |
| message | string | 取消结果消息 |

**示例代码：**

```python
# 取消订单
response = client.cancel_master_order(
    masterOrderId="your-master-order-id",
    reason="用户手动取消"  # 可选的取消原因
)

if response.get('success'):
    print("订单取消成功")
else:
    print(f"订单取消失败: {response.get('message')}")

# 批量取消示例
def cancel_all_active_orders(client):
    """取消所有活跃订单"""
    orders = client.get_master_orders(status="ACTIVE")
    cancelled_count = 0
    
    for order in orders['items']:
        try:
            response = client.cancel_master_order(
                masterOrderId=order['masterOrderId'],
                reason="批量取消活跃订单"
            )
            if response.get('success'):
                cancelled_count += 1
                print(f"已取消订单: {order['masterOrderId']}")
            else:
                print(f"取消失败: {order['masterOrderId']} - {response.get('message')}")
        except Exception as e:
            print(f"取消异常: {order['masterOrderId']} - {str(e)}")
    
    print(f"\n总计取消 {cancelled_count} 个订单")
    return cancelled_count
```

#### 创建 ListenKey

创建一个随机的UUID作为ListenKey，绑定当前用户信息，有效期24小时。ListenKey用于WebSocket连接，可以实时接收用户相关的交易数据推送。

**请求参数：**

| 参数名 | 类型 | 是否必传 | 描述 |
|--------|------|----------|------|
| 无需参数 | - | - | - |

**响应字段：**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| listenKey | string | 生成的ListenKey |
| expireAt | string | ListenKey过期时间戳（秒） |
| success | bool | 创建是否成功 |
| message | string | 创建结果消息 |

**示例代码：**

```python
# 创建 ListenKey
result = client.create_listen_key()

if result.get('success'):
    print(f"ListenKey创建成功:")
    print(f"ListenKey: {result['listenKey']}")
    print(f"过期时间: {result['expireAt']}")
    
    # 使用 ListenKey 建立 WebSocket 连接
    # ws_url = f"wss://api.quantumexecute.com/ws/{result['listenKey']}"
else:
    print(f"ListenKey创建失败：{result.get('message')}")
```

**注意事项：**
- ListenKey 有效期为 24 小时，过期后需要重新创建
- 每个用户同时只能有一个有效的 ListenKey
- ListenKey 用于 WebSocket 连接，可以实时接收交易数据推送
- 建议在应用启动时创建 ListenKey，并在接近过期时重新创建

## 错误处理

SDK 提供了详细的错误信息，包括 API 错误和网络错误：

```python
from qe.error import ClientError, APIError

response = client.create_master_order(
    # ... 设置参数
)

if 'error' in response:
    # 检查是否为 API 错误
    error = response['error']
    if isinstance(error, dict) and 'code' in error:
        print(f"API 错误 - 代码: {error['code']}, 原因: {error.get('reason')}, 消息: {error.get('message')}")
        print(f"TraceID: {error.get('trace_id')}")
        
        # 根据错误代码处理
        if error['code'] == 400:
            print("请求参数错误")
        elif error['code'] == 401:
            print("认证失败")
        elif error['code'] == 403:
            print("权限不足")
        elif error['code'] == 429:
            print("请求过于频繁")
        else:
            print(f"其他错误: {error}")
    else:
        print(f"网络或其他错误: {error}")
```

## 高级配置

### 自定义 HTTP 客户端

```python
import requests
import time

# 创建自定义 HTTP 客户端
session = requests.Session()
session.timeout = 30  # 30 秒超时
session.headers.update({
    'User-Agent': 'QE-Python-SDK/1.0.0'
})

client = Client("your-api-key", "your-api-secret")
client.session = session
```

### 使用代理

```python
import requests

proxies = {
    'https': 'http://proxy.example.com:8080'
}

client = Client("your-api-key", "your-api-secret")
client.session.proxies.update(proxies)
```

### 时间偏移调整

如果遇到时间戳错误，可以调整客户端的时间偏移：

```python
# 设置时间偏移（毫秒）
client.time_offset = 1000  # 客户端时间比服务器快 1 秒
```

### 请求重试

```python
import time
import math

# 实现简单的重试逻辑
def retry_request(func, max_retries=3):
    """重试请求函数"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise e
            
            # 检查是否应该重试
            if hasattr(e, 'code') and 400 <= e.code < 500:
                raise e  # 不重试客户端错误
            
            # 指数退避
            wait_time = math.pow(2, i)
            print(f"请求失败，{wait_time}秒后重试...")
            time.sleep(wait_time)

# 使用重试
def create_order_with_retry():
    return client.create_master_order(
        # ... 设置参数
    )

result = retry_request(create_order_with_retry, max_retries=3)
```

## 最佳实践

### 1. API 密钥管理

```python
# 定期检查 API 密钥状态
def check_api_key_status(client):
    apis = client.list_exchange_apis()
    if not apis.get('items'):
        print("获取 API 列表失败")
        return
    
    for api in apis['items']:
        if not api['isValid']:
            print(f"警告: API {api['id']} ({api['accountName']}) 状态异常")
        if api['balance'] < 100:
            print(f"警告: 账户 {api['accountName']} 余额不足 (${api['balance']:.2f})")
```

### 2. 订单监控

```python
# 监控订单执行状态
def monitor_order(client, master_order_id):
    import time
    
    while True:
        orders = client.get_master_orders(page=1, pageSize=1)
        
        if not orders['items']:
            print("订单不存在")
            return
        
        order = orders['items'][0]
        print(f"订单进度: {order['completionProgress']*100:.2f}%, 状态: {order['status']}")
        
        if order['status'] == "COMPLETED":
            print(f"订单已结束，最终状态: {order['status']}")
            return
        
        time.sleep(10)  # 每 10 秒检查一次
```

### 3. 批量处理

```python
# 批量获取所有订单
def get_all_orders(client):
    all_orders = []
    page = 1
    page_size = 100
    
    while True:
        result = client.get_master_orders(page=page, pageSize=page_size)
        all_orders.extend(result['items'])
        
        # 检查是否还有更多数据
        if len(result['items']) < page_size:
            break
        page += 1
    
    return all_orders
```

### 4. ListenKey 管理

```python
import time
from datetime import datetime

# ListenKey 管理器
class ListenKeyManager:
    def __init__(self, client):
        self.client = client
        self.listen_key = None
        self.expire_at = None
    
    def create_listen_key(self):
        """创建或刷新 ListenKey"""
        result = self.client.create_listen_key()
        
        if not result.get('success'):
            raise Exception(f"创建 ListenKey 失败: {result.get('message')}")
        
        self.listen_key = result['listenKey']
        self.expire_at = int(result['expireAt'])
        
        print(f"ListenKey 创建成功: {self.listen_key}, 过期时间: {self.expire_at}")
        return self.listen_key
    
    def is_expired(self):
        """检查 ListenKey 是否即将过期"""
        if not self.expire_at:
            return True
        # 提前1小时刷新
        return time.time() > self.expire_at - 3600
    
    def auto_refresh(self):
        """自动刷新 ListenKey"""
        if self.is_expired():
            print("ListenKey 即将过期，开始刷新...")
            self.create_listen_key()

# 使用示例
manager = ListenKeyManager(client)
listen_key = manager.create_listen_key()

# 定期检查并刷新
while True:
    manager.auto_refresh()
    time.sleep(1800)  # 每30分钟检查一次
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 联系我们

- 官网：[https://test.quantumexecute.com](https://test.quantumexecute.com)
- 邮箱：support@quantumexecute.com
- GitHub：[https://github.com/Quantum-Execute/qe-connector-python](https://github.com/Quantum-Execute/qe-connector-python)