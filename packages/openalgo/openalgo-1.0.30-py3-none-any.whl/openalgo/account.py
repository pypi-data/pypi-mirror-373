# -*- coding: utf-8 -*-
"""
OpenAlgo REST API Documentation - Account Methods
    https://docs.openalgo.in
"""

import httpx
from .base import BaseAPI

class AccountAPI(BaseAPI):
    """
    Account management API methods for OpenAlgo.
    Inherits from the BaseAPI class.
    """

    def _make_request(self, endpoint, payload):
        """Make HTTP request with proper error handling"""
        url = self.base_url + endpoint
        try:
            response = httpx.post(url, json=payload, headers=self.headers)
            return self._handle_response(response)
        except httpx.TimeoutException:
            return {
                'status': 'error',
                'message': 'Request timed out. The server took too long to respond.',
                'error_type': 'timeout_error'
            }
        except httpx.ConnectError:
            return {
                'status': 'error',
                'message': 'Failed to connect to the server. Please check if the server is running.',
                'error_type': 'connection_error'
            }
        except httpx.HTTPError as e:
            return {
                'status': 'error',
                'message': f'HTTP error occurred: {str(e)}',
                'error_type': 'http_error'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}',
                'error_type': 'unknown_error'
            }
    
    def _handle_response(self, response):
        """Helper method to handle API responses"""
        try:
            if response.status_code != 200:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}: {response.text}',
                    'code': response.status_code,
                    'error_type': 'http_error'
                }
            
            data = response.json()
            if data.get('status') == 'error':
                return {
                    'status': 'error',
                    'message': data.get('message', 'Unknown error'),
                    'code': response.status_code,
                    'error_type': 'api_error'
                }
            return data
            
        except ValueError:
            return {
                'status': 'error',
                'message': 'Invalid JSON response from server',
                'raw_response': response.text,
                'error_type': 'json_error'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'error_type': 'unknown_error'
            }

    def funds(self):
        """
        Get funds and margin details of the connected trading account.

        Returns:
        dict: JSON response containing funds data with format:
            {
                "data": {
                    "availablecash": "amount",
                    "collateral": "amount",
                    "m2mrealized": "amount",
                    "m2munrealized": "amount",
                    "utiliseddebits": "amount"
                },
                "status": "success"
            }
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("funds", payload)

    def orderbook(self):
        """
        Get orderbook details from the broker with basic orderbook statistics.

        Returns:
        dict: JSON response containing orders data with format:
            {
                "data": {
                    "orders": [
                        {
                            "action": "BUY/SELL",
                            "exchange": "exchange_code",
                            "order_status": "status",
                            "orderid": "id",
                            "price": price_value,
                            "pricetype": "type",
                            "product": "product_type",
                            "quantity": quantity_value,
                            "symbol": "symbol_name",
                            "timestamp": "DD-MMM-YYYY HH:MM:SS",
                            "trigger_price": trigger_price_value
                        },
                        ...
                    ],
                    "statistics": {
                        "total_buy_orders": count,
                        "total_completed_orders": count,
                        "total_open_orders": count,
                        "total_rejected_orders": count,
                        "total_sell_orders": count
                    }
                },
                "status": "success"
            }
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("orderbook", payload)

    def tradebook(self):
        """
        Get tradebook details from the broker.

        Returns:
        dict: JSON response containing trades data with format:
            {
                "data": [
                    {
                        "action": "BUY/SELL",
                        "average_price": price_value,
                        "exchange": "exchange_code",
                        "orderid": "id",
                        "product": "product_type",
                        "quantity": quantity_value,
                        "symbol": "symbol_name",
                        "timestamp": "DD-MMM-YYYY HH:MM:SS",
                        "trade_value": value
                    },
                    ...
                ],
                "status": "success"
            }
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("tradebook", payload)

    def positionbook(self):
        """
        Get positionbook details from the broker.

        Returns:
        dict: JSON response containing positions data with format:
            {
                "data": [
                    {
                        "average_price": "price_value",
                        "exchange": "exchange_code",
                        "product": "product_type",
                        "quantity": quantity_value,
                        "symbol": "symbol_name"
                    },
                    ...
                ],
                "status": "success"
            }
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("positionbook", payload)

    def holdings(self):
        """
        Get stock holdings details from the broker.

        Returns:
        dict: JSON response containing holdings data with format:
            {
                "data": {
                    "holdings": [
                        {
                            "exchange": "exchange_code",
                            "pnl": pnl_value,
                            "pnlpercent": percentage_value,
                            "product": "product_type",
                            "quantity": quantity_value,
                            "symbol": "symbol_name"
                        },
                        ...
                    ],
                    "statistics": {
                        "totalholdingvalue": value,
                        "totalinvvalue": value,
                        "totalpnlpercentage": percentage,
                        "totalprofitandloss": value
                    }
                },
                "status": "success"
            }
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("holdings", payload)

    def analyzerstatus(self):
        """
        Get analyzer status information.

        Returns:
        dict: JSON response containing analyzer status with format:
            {
                "data": {
                    "analyze_mode": false,
                    "mode": "live",
                    "total_logs": 2
                },
                "status": "success"
            }
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("analyzer", payload)

    def analyzertoggle(self, mode):
        """
        Toggle analyzer mode between analyze and live modes.

        Args:
            mode (bool): True for analyze mode (simulated), False for live mode

        Returns:
        dict: JSON response containing analyzer toggle result with format:
            {
                "status": "success",
                "data": {
                    "mode": "live/analyze",
                    "analyze_mode": true/false,
                    "total_logs": 2,
                    "message": "Analyzer mode switched to live"
                }
            }
        """
        payload = {
            "apikey": self.api_key,
            "mode": mode
        }
        return self._make_request("analyzer/toggle", payload)
