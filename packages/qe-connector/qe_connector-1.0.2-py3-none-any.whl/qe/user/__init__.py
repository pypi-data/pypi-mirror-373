from qe.api import API


class User(API):
    def __init__(self, api_key=None, api_secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = "https://testapi.quantumexecute.com"
        super().__init__(api_key, api_secret, **kwargs)

    # CONVERT
    from qe.user.exchange import list_exchange_apis
    from qe.user.exchange import add_exchange_api
    from qe.user.trading import get_master_orders
    from qe.user.trading import get_order_fills
    from qe.user.trading import create_master_order
    from qe.user.trading import cancel_master_order
    from qe.user.trading import create_listen_key
