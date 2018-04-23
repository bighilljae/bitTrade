#
# XCoin API-call related functions
#
# @author	btckorea
# @date	2017-04-12
#
# Compatible with python3 version.

import time
import base64
import hmac, hashlib
import urllib.parse
import requests
import json
import threading


class Bithumb:
    api_url = "https://api.bithumb.com"
    api_key = ""
    api_secret = ""
    price = {}
    balance = {}

    def __init__(self, key, secret):
        self.api_key = key
        self.api_secret = secret
        self.run_worker()

    def get_header(self, endpoint, str_data):
        nonce = str(int(time.time()*1000))
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        signature = hmac.new(self.api_secret.encode(), data.encode(), hashlib.sha512).hexdigest()
        signature64 = base64.b64encode(signature.encode()).decode()
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Api-Key': self.api_key,
            'Api-Sign': str(signature64),
            'Api-Nonce': nonce,
        }

    def secret_api(self, endpoint, **kwargs):
        endpoint_item_array = {
            "endpoint": endpoint
        }
        uri_array = dict(endpoint_item_array, **kwargs)  # Concatenate the two arrays.
        json_data = json.dumps(uri_array)
        str_data = urllib.parse.urlencode(uri_array)

        session = requests.Session()
        session.cookies.clear()
        resp = session.request('POST', self.api_url+endpoint, data=str_data, headers=self.get_header(endpoint, str_data))
        if endpoint != '/info/balance':
            print('bithumb secert_api ' + endpoint + ' ' + str(resp.status_code) + ' ' + resp.text)
        return resp

    def bid(self):
        return self.price

    def run_worker(self):
        p_thread = threading.Thread(target=get_bithumb_price, args=(self,))
        p_thread.daemon = True
        p_thread.start()

        b_thread = threading.Thread(target=get_bithumb_balance, args=(self,))
        b_thread.daemon = True
        b_thread.start()

    # Pre check doned
    def buy_coin(self, cur, amount=100000):
        units = str(round(amount / self.price[cur], 4))
        r = self.secret_api("/trade/place", order_currency=str(cur).upper(), units=units, price=str(self.price[cur]), type='bid').json()
        return {
            'units': r['units'],
            'price': r['price']
        }

    # Pre check doned
    def sell_coin(self, cur, amount):
        r = self.secret_api("/trade/market_sell",  currency=str(cur).upper(), units=str(amount)).json()

def get_bithumb_balance(api):
    while True:
        r = api.secret_api("/info/balance", currency='ALL')
        if r.status_code != requests.codes.ok:
            continue
        r = r.json()
        for k in r['data']:
            if str.startswith(k, 'total'):
                api.balance[k[6:]] = r['data'][k]
        time.sleep(5)


def get_bithumb_price(api):
    while True:
        result = {}
        r = requests.get("https://api.bithumb.com/public/orderbook/all")
        r = r.json()
        for cur in r['data'].keys():
            try:
                result[str.lower(cur)] = float(r['data'][cur]['bids'][0]['price'])
            except:
                pass
        api.price = result
        time.sleep(5)

