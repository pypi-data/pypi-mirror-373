from qe.lib.utils import check_required_parameters


def list_exchange_apis(self, **kwargs):
    """List exchange APIs (USER_DATA)
    
    Get user's exchange API keys list
    
    GET /user/exchange-apis
    
    Keyword Args:
        page (int, optional): Page number
        pageSize (int, optional): Page size
        exchange (str, optional): Exchange name filter
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    url_path = "/user/exchange-apis"
    return self.sign_request("GET", url_path, {**kwargs})


def add_exchange_api(self, accountName: str, exchange: str, apiKey: str, apiSecret: str, **kwargs):
    """Add exchange API (USER_DATA)
    
    Add a new exchange API key
    
    POST /user/exchange-apis
    
    Args:
        accountName (str): Account name
        exchange (str): Exchange name
        apiKey (str): API key
        apiSecret (str): API secret
    Keyword Args:
        passphrase (str, optional): Passphrase for certain exchanges
        verificationMethod (str, optional): Verification method
        enableTrading (bool, optional): Enable trading permission
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameters([
        [accountName, "accountName"],
        [exchange, "exchange"],
        [apiKey, "apiKey"],
        [apiSecret, "apiSecret"]
    ])
    
    params = {
        "accountName": accountName,
        "exchange": exchange,
        "apiKey": apiKey,
        "apiSecret": apiSecret,
        **kwargs
    }
    url_path = "/user/exchange-apis"
    return self.sign_request("POST", url_path, params)
