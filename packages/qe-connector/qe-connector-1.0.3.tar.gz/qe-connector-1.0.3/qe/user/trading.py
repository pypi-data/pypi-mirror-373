from typing import Union, Optional
from qe.lib.utils import check_required_parameters
from qe.lib.trading_enums import Algorithm, Exchange, MarketType, OrderSide, StrategyType, MarginType


def get_master_orders(self, **kwargs):
    """Get master orders (USER_DATA)
    
    Query master orders list
    
    GET /user/trading/master-orders
    
    Keyword Args:
        page (int, optional): Page number
        pageSize (int, optional): Page size
        status (str, optional): Order status filter
        exchange (str, optional): Exchange name filter
        symbol (str, optional): Trading symbol filter
        startTime (str, optional): Start time filter
        endTime (str, optional): End time filter
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    url_path = "/user/trading/master-orders"
    return self.sign_request("GET", url_path, {**kwargs})


def get_order_fills(self, **kwargs):
    """Get order fills (USER_DATA)
    
    Query order fills/trades list
    
    GET /user/trading/order-fills
    
    Keyword Args:
        page (int, optional): Page number
        pageSize (int, optional): Page size
        masterOrderId (str, optional): Master order ID filter
        subOrderId (str, optional): Sub order ID filter
        symbol (str, optional): Trading symbol filter
        startTime (str, optional): Start time filter
        endTime (str, optional): End time filter
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    url_path = "/user/trading/order-fills"
    return self.sign_request("GET", url_path, {**kwargs})


def create_master_order(self, 
                       algorithm: Union[Algorithm, str],
                       exchange: Union[Exchange, str],
                       symbol: str,
                       marketType: Union[MarketType, str],
                       side: Union[OrderSide, str],
                       apiKeyId: str,
                       **kwargs):
    """Create master order (USER_DATA)
    
    Create a new master order
    
    POST /user/trading/master-orders
    
    Args:
        algorithm (Algorithm | str): Algorithm name (e.g., Algorithm.TWAP, Algorithm.VWAP, Algorithm.POV)
        exchange (Exchange | str): Exchange name (e.g., Exchange.BINANCE)
        symbol (str): Trading symbol
        marketType (MarketType | str): Market type (e.g., MarketType.SPOT, MarketType.PERP)
        side (OrderSide | str): Order side (e.g., OrderSide.BUY, OrderSide.SELL)
        apiKeyId (str): API key ID to use
    Keyword Args:
        totalQuantity (float, optional): Total quantity to trade
        orderNotional (float, optional): Order notional value
        strategyType (StrategyType | str, optional): Strategy type (e.g., StrategyType.TWAP_1, StrategyType.TWAP_2, StrategyType.POV)
        startTime (str, optional): Start time
        executionDuration (str, optional): Execution duration
        endTime (str, optional): End time
        limitPrice (float, optional): Limit price
        mustComplete (bool, optional): Must complete flag
        makerRateLimit (float, optional): Maker rate limit
        povLimit (float, optional): POV limit
        povMinLimit (float, optional): POV minimum limit
        marginType (MarginType | str, optional): Margin type (e.g., MarginType.U, MarginType.C)
        reduceOnly (bool, optional): Reduce only flag
        notes (str, optional): Order notes
        clientId (str, optional): Client order ID
        worstPrice (float, optional): Worst acceptable price
        limitPriceString (str, optional): Limit price as string
        upTolerance (str, optional): Up tolerance
        lowTolerance (str, optional): Low tolerance
        strictUpBound (bool, optional): Strict upper bound flag
        tailOrderProtection (bool, optional): Tail order protection flag (defaults to True)
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    # 转换枚举为字符串值
    if isinstance(algorithm, Algorithm):
        algorithm = algorithm.value
    if isinstance(exchange, Exchange):
        exchange = exchange.value
    if isinstance(marketType, MarketType):
        marketType = marketType.value
    if isinstance(side, OrderSide):
        side = side.value
    
    # 处理可选参数中的枚举
    if 'strategyType' in kwargs and isinstance(kwargs['strategyType'], StrategyType):
        kwargs['strategyType'] = kwargs['strategyType'].value
    if 'marginType' in kwargs and isinstance(kwargs['marginType'], MarginType):
        kwargs['marginType'] = kwargs['marginType'].value
    
    check_required_parameters([
        [algorithm, "algorithm"],
        [exchange, "exchange"],
        [symbol, "symbol"],
        [marketType, "marketType"],
        [side, "side"],
        [apiKeyId, "apiKeyId"]
    ])
    
    params = {
        "algorithm": algorithm,
        "algorithmType": "TWAP",  # 固定值，与 Go 版本保持一致
        "exchange": exchange,
        "symbol": symbol,
        "marketType": marketType,
        "side": side,
        "apiKeyId": apiKeyId,
    }
    
    # 添加可选参数
    for key in ['totalQuantity', 'orderNotional', 'strategyType', 'startTime', 
                'executionDuration', 'endTime', 'limitPrice', 'mustComplete',
                'makerRateLimit', 'povLimit', 'povMinLimit', 'marginType', 
                'reduceOnly', 'notes', 'clientId', 'worstPrice', 'limitPriceString',
                'upTolerance', 'lowTolerance', 'strictUpBound', 'recvWindow']:
        if key in kwargs:
            params[key] = kwargs[key]
    
    # 设置 tailOrderProtection 默认值（与 Go 版本保持一致）
    if 'tailOrderProtection' in kwargs:
        params['tailOrderProtection'] = kwargs['tailOrderProtection']
    else:
        params['tailOrderProtection'] = True
    
    url_path = "/user/trading/master-orders"
    return self.sign_request("POST", url_path, params)


def cancel_master_order(self, masterOrderId: str, **kwargs):
    """Cancel master order (USER_DATA)
    
    Cancel an existing master order
    
    PUT /user/trading/master-orders/{masterOrderId}/cancel
    
    Args:
        masterOrderId (str): Master order ID to cancel
    Keyword Args:
        reason (str, optional): Cancellation reason
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameters([[masterOrderId, "masterOrderId"]])
    
    params = {"masterOrderId": masterOrderId, **kwargs}
    url_path = f"/user/trading/master-orders/{masterOrderId}/cancel"
    return self.sign_request("PUT", url_path, params)


def create_listen_key(self, **kwargs):
    """Create listen key (USER_DATA)
    
    Create a new listen key for WebSocket user data stream
    
    POST /user/trading/listen-key
    
    Keyword Args:
        recvWindow (int, optional): The value cannot be greater than 60000
    
    Returns:
        dict: Response containing listenKey, expireAt, success, and message
    """
    url_path = "/user/trading/listen-key"
    return self.sign_request("POST", url_path, {**kwargs})