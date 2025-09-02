"""交易相关枚举定义
"""
from enum import Enum


class MasterOrderStatus(str, Enum):
    """母单状态枚举"""
    NEW = "NEW"                # 执行中
    COMPLETED = "COMPLETED"    # 已完成


class Algorithm(str, Enum):
    """算法枚举"""
    TWAP = "TWAP"  # TWAP算法
    VWAP = "VWAP"  # VWAP算法
    POV = "POV"    # POV算法


class StrategyType(str, Enum):
    """策略类型枚举"""
    TWAP_1 = "TWAP-1"  # TWAP策略版本1
    TWAP_2 = "TWAP-2"  # TWAP策略版本2
    POV = "POV"        # POV策略


class MarketType(str, Enum):
    """市场类型枚举"""
    SPOT = "SPOT"  # 现货市场
    PERP = "PERP"  # 合约市场


class OrderSide(str, Enum):
    """订单方向枚举"""
    BUY = "buy"    # 买入
    SELL = "sell"  # 卖出


class MarginType(str, Enum):
    """保证金类型枚举"""
    U = "U"  # U本位
    # C = "C"  # 币本位


class Exchange(str, Enum):
    """交易所枚举"""
    BINANCE = "Binance"  # 币安


class Category(str, Enum):
    """币对品种枚举（与市场类型对应）"""
    SPOT = "spot"  # 现货品种
    PERP = "perp"  # 合约品种
