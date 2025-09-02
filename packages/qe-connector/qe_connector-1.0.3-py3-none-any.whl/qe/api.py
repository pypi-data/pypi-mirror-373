import json
from json import JSONDecodeError
import logging
import requests
from .__version__ import __version__
from qe.error import ClientError, ServerError
from qe.lib.utils import get_timestamp
from qe.lib.utils import cleanNoneValue
from qe.lib.utils import encoded_string
from qe.lib.utils import check_required_parameter
from qe.lib.authentication import hmac_hashing, rsa_signature, ed25519_signature


class API(object):
    """API base class

    Keyword Args:
        base_url (str, optional): the API base url, useful to switch to testnet, etc. By default it's https://api.binance.com
        timeout (int, optional): the time waiting for server response, number of seconds. https://docs.python-requests.org/en/master/user/advanced/#timeouts
        proxies (obj, optional): Dictionary mapping protocol to the URL of the proxy. e.g. {'https': 'http://1.2.3.4:8080'}
        show_limit_usage (bool, optional): whether return limit usage(requests and/or orders). By default, it's False
        show_header (bool, optional): whether return the whole response header. By default, it's False
        time_unit (str, optional): select a time unit. By default, it's None.
        private_key (str, optional): RSA private key for RSA authentication
        private_key_pass(str, optional): Password for PSA private key
    """

    def __init__(
        self,
        api_key=None,
        api_secret=None,
        base_url=None,
        timeout=None,
        proxies=None,
        show_limit_usage=False,
        show_header=False,
        time_unit=None,
        private_key=None,
        private_key_pass=None,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = timeout
        self.proxies = None
        self.show_limit_usage = False
        self.show_header = False
        self.private_key = private_key
        self.private_key_pass = private_key_pass
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json;charset=utf-8",
                "User-Agent": "qe-connector-python/" + __version__,
                "X-MBX-APIKEY": api_key,
            }
        )

        if (
            time_unit == "microsecond"
            or time_unit == "millisecond"
            or time_unit == "MILLISECOND"
            or time_unit == "MICROSECOND"
        ):
            self.session.headers.update({"X-MBX-TIME-UNIT": time_unit})

        if show_limit_usage is True:
            self.show_limit_usage = True

        if show_header is True:
            self.show_header = True

        if type(proxies) is dict:
            self.proxies = proxies

        self._logger = logging.getLogger(__name__)
        return

    def query(self, url_path, payload=None):
        return self.send_request("GET", url_path, payload=payload)

    def limit_request(self, http_method, url_path, payload=None):
        """limit request is for those endpoints require API key in the header"""

        check_required_parameter(self.api_key, "api_key")
        return self.send_request(http_method, url_path, payload=payload)

    def sign_request(self, http_method, url_path, payload=None):
        if payload is None:
            payload = {}
        payload["timestamp"] = get_timestamp()
        query_string = self._prepare_params(payload)
        payload["signature"] = self._get_sign(query_string)
        return self.send_request(http_method, url_path, payload)

    def limited_encoded_sign_request(self, http_method, url_path, payload=None):
        """This is used for some endpoints has special symbol in the url.
        In some endpoints these symbols should not encoded
        - @
        - [
        - ]

        so we have to append those parameters in the url
        """
        if payload is None:
            payload = {}
        payload["timestamp"] = get_timestamp()
        query_string = self._prepare_params(payload)
        url_path = (
            url_path + "?" + query_string + "&signature=" + self._get_sign(query_string)
        )
        return self.send_request(http_method, url_path)

    def send_request(self, http_method, url_path, payload=None):
        if payload is None:
            payload = {}
        url = self.base_url + url_path
        self._logger.debug("url: " + url)
        params = cleanNoneValue(
            {
                "url": url,
                "params": self._prepare_params(payload),
                "timeout": self.timeout,
                "proxies": self.proxies,
            }
        )
        response = self._dispatch_request(http_method)(**params)
        self._logger.debug("raw response from server:" + response.text)
        
        # Handle HTTP errors (4xx, 5xx)
        if response.status_code >= 400:
            self._handle_exception(response)
        
        # Parse response
        try:
            data = response.json()
        except ValueError:
            # If not JSON, return as text
            data = response.text
            return data
        
        # Check API response code (matching Go's logic)
        if isinstance(data, dict) and 'code' in data:
            if data.get('code') != 200:
                # Raise APIError if code is not 200
                from qe.error import APIError
                raise APIError(
                    code=data.get('code'),
                    reason=data.get('reason', ''),
                    message=data.get('message', ''),
                    trace_id=data.get('traceId'),
                    server_time=data.get('serverTime')
                )
            # Return message field if code is 200 (matching Go's behavior)
            return data.get('message', data)
        
        # For responses without code field, return as is
        result = {}
        if self.show_limit_usage:
            limit_usage = {}
            for key in response.headers.keys():
                key = key.lower()
                if (
                    key.startswith("x-mbx-used-weight")
                    or key.startswith("x-mbx-order-count")
                    or key.startswith("x-sapi-used")
                ):
                    limit_usage[key] = response.headers[key]
            result["limit_usage"] = limit_usage

        if self.show_header:
            result["header"] = response.headers

        if len(result) != 0:
            result["data"] = data
            return result

        return data

    def _prepare_params(self, params):
        return encoded_string(cleanNoneValue(params))

    def _get_sign(self, payload):
        if self.private_key is not None:
            try:
                return ed25519_signature(
                    self.private_key, payload, self.private_key_pass
                )
            except ValueError:
                return rsa_signature(self.private_key, payload, self.private_key_pass)
        else:
            return hmac_hashing(self.api_secret, payload)

    def _dispatch_request(self, http_method):
        return {
            "GET": self.session.get,
            "DELETE": self.session.delete,
            "PUT": self.session.put,
            "POST": self.session.post,
        }.get(http_method, "GET")

    def _handle_exception(self, response):
        """Handle HTTP errors (4xx, 5xx) matching Go's error handling"""
        status_code = response.status_code
        if status_code < 400:
            return
            
        # Try to parse error response as JSON
        try:
            err = json.loads(response.text)
        except JSONDecodeError:
            # If not JSON, raise generic server error
            raise ServerError(status_code, response.text)
        
        # Check if response matches APIError structure
        if all(key in err for key in ['code', 'reason', 'message']):
            from qe.error import APIError
            raise APIError(
                code=err.get('code'),
                reason=err.get('reason', ''),
                message=err.get('message', ''),
                trace_id=err.get('traceId'),
                server_time=err.get('serverTime')
            )
        
        # Fall back to original error handling for other formats
        if 400 <= status_code < 500:
            error_data = err.get('data')
            raise ClientError(
                status_code, 
                err.get('code'), 
                err.get('msg', err.get('message', response.text)), 
                response.headers, 
                error_data
            )
        raise ServerError(status_code, response.text)
