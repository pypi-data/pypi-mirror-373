# -*- coding: utf-8 -*-
"""
OpenAlgo REST API Documentation - Data Methods
    https://docs.openalgo.in
"""

import httpx
import pandas as pd
from datetime import datetime
import time
from .base import BaseAPI

class DataAPI(BaseAPI):
    """
    Data API methods for OpenAlgo.
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

    def quotes(self, *, symbol, exchange):
        """
        Get real-time quotes for a symbol.

        Parameters:
        - symbol (str): Trading symbol. Required.
        - exchange (str): Exchange code. Required.

        Returns:
        dict: JSON response containing quote data including bid, ask, ltp, volume etc.
        """
        payload = {
            "apikey": self.api_key,
            "symbol": symbol,
            "exchange": exchange
        }
        return self._make_request("quotes", payload)

    def depth(self, *, symbol, exchange):
        """
        Get market depth (order book) for a symbol.

        Parameters:
        - symbol (str): Trading symbol. Required.
        - exchange (str): Exchange code. Required.

        Returns:
        dict: JSON response containing market depth data including top 5 bids/asks.
        """
        payload = {
            "apikey": self.api_key,
            "symbol": symbol,
            "exchange": exchange
        }
        return self._make_request("depth", payload)

    def symbol(self, *, symbol, exchange):
        """
        Get symbol details from the API.

        Parameters:
        - symbol (str): Trading symbol. Required.
        - exchange (str): Exchange code. Required.

        Returns:
        dict: JSON response containing symbol details like token, lot size, tick size, etc.
        """
        payload = {
            "apikey": self.api_key,
            "symbol": symbol,
            "exchange": exchange
        }
        return self._make_request("symbol", payload)
        
    def search(self, *, query, exchange=None):
        """
        Search for symbols across exchanges.
        
        Parameters:
        - query (str): Search query for symbol. Required.
        - exchange (str): Exchange filter. Optional.
            Supported exchanges: NSE, NFO, BSE, BFO, MCX, CDS, BCD, NCDEX, NSE_INDEX, BSE_INDEX, MCX_INDEX
        
        Returns:
        dict: JSON response containing matching symbols with details like:
            - symbol: Trading symbol
            - name: Company/instrument name  
            - exchange: Exchange code
            - token: Unique instrument token
            - instrumenttype: Type of instrument
            - lotsize: Lot size
            - strike: Strike price (for options)
            - expiry: Expiry date (for derivatives)
        """
        payload = {
            "apikey": self.api_key,
            "query": query
        }
        if exchange:
            payload["exchange"] = exchange
            
        return self._make_request("search", payload)
        
    def history(self, *, symbol, exchange, interval, start_date, end_date):
        """
        Get historical data for a symbol in pandas DataFrame format.

        Parameters:
        - symbol (str): Trading symbol. Required.
        - exchange (str): Exchange code. Required.
        - interval (str): Time interval for the data. Required.
                       Use interval() method to get supported intervals.
        - start_date (str): Start date in format 'YYYY-MM-DD'. Required.
        - end_date (str): End date in format 'YYYY-MM-DD'. Required.

        Returns:
        pandas.DataFrame or dict: DataFrame with historical data if successful,
                                error dict if failed. DataFrame has timestamp as index.
                                For intraday data (non-daily timeframes), timestamps
                                are converted to IST. Daily data is already in IST.
        """
        payload = {
            "apikey": self.api_key,
            "symbol": symbol,
            "exchange": exchange,
            "interval": interval,
            "start_date": start_date,
            "end_date": end_date
        }

        result = self._make_request("history", payload)
        
        if result.get('status') == 'success' and 'data' in result:
            try:
                df = pd.DataFrame(result['data'])
                if df.empty:
                    return {
                        'status': 'error',
                        'message': 'No data available for the specified period',
                        'error_type': 'no_data'
                    }
                
                # Convert timestamp to datetime
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                
                # Convert to IST for intraday timeframes
                if interval not in ['D', 'W', 'M']:  # Not daily/weekly/monthly
                    df["timestamp"] = df["timestamp"].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                
                # Set timestamp as index
                df.set_index('timestamp', inplace=True)
                
                # Sort index and remove duplicates
                df = df.sort_index()
                df = df[~df.index.duplicated(keep='first')]
                
                return df
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Failed to process historical data: {str(e)}',
                    'error_type': 'processing_error',
                    'raw_data': result['data']
                }
        return result

    def intervals(self):
        """
        Get supported time intervals for historical data from the API.

        Returns:
        dict: JSON response containing supported intervals categorized by type
              (seconds, minutes, hours, days, weeks, months)
        """
        payload = {
            "apikey": self.api_key
        }
        return self._make_request("intervals", payload)
        
    def interval(self):
        """
        Legacy method. Use intervals() instead.
        Get supported time intervals for historical data.

        Returns:
        dict: JSON response containing supported intervals
        """
        return self.intervals()

    def expiry(self, *, symbol, exchange, instrumenttype):
        """
        Get expiry dates for a symbol.

        Parameters:
        - symbol (str): Trading symbol. Required.
        - exchange (str): Exchange code. Required.
        - instrumenttype (str): Instrument type (futures/options). Required.

        Returns:
        dict: JSON response containing expiry dates for the symbol
        """
        payload = {
            "apikey": self.api_key,
            "symbol": symbol,
            "exchange": exchange,
            "instrumenttype": instrumenttype
        }
        return self._make_request("expiry", payload)
