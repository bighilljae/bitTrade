import time
import requests
import hmac
import hashlib
import base64
import json
import threading

class Cpdax():
    price = {}
    balance = {}
    api_key = ''
    secret_key = ''
    def __init__(self, key, secret):
        self.api_key = key
        self.secret_key = secret
        self.run_worker()

    @property
    def headers(self):
        t = str(int(time.time()))
        msg = self.api_key + t + 'GET' + '/v1/balance'
        h = hmac.new(self.secret_key.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
        h64 = h
        return {
            'CP-ACCESS-KEY': self.api_key,
            'CP-ACCESS-TIMESTAMP': t,
            'CP-ACCESS-DIGEST': str(h64)}

    def bid(self):
        return self.price

    def run_worker(self):
        p_thread = threading.Thread(target=get_cpdax_price, args=(self,))
        p_thread.daemon = True
        p_thread.start()

        b_thread = threading.Thread(target=get_cpdax_balance, args=(self,))
        b_thread.daemon = True
        b_thread.start()

        # Pre check doned

    def buy_coin(self, cur, amount):
        r = requests.post("https://api.cpdax.com/v1/orders", headers=self.headers, data={'type': 'limit', 'side': 'buy', 'product_id': str(cur).upper()+"-KRW",
                                           'size': 100000/self.price[cur], 'price': self.price[cur]}).json()
        return {
            'units': r['filled_size'],
            'price': r['price']
        }

        # Pre check doned

    def sell_coin(self, cur, amount):
        r = requests.post("https://api.cpdax.com/v1/orders", headers=self.headers,
                          data={'type': 'market', 'side': 'sell', 'product_id': str(cur).upper() + "-KRW",'size': amount}).json()

def get_cpdax_price(api):
    while True:
        r = requests.get("https://api.cpdax.com/v1/tickers/detailed")
        if r.status_code != requests.codes.ok:
            return
        # TODO cpdax API 확인
        order = {'btc': 2, 'bch': 1, 'eth': 8, 'etc': 6, 'ltc': 14, 'eos': 4}

        res = {}
        for cur in order:
            res[cur] = float(r.json()[order[cur]]['bid'])
        api.price = res
        time.sleep(5)

def get_cpdax_balance(api):
    while True:
        r = requests.get('https://api.cpdax.com/v1/balance', headers=api.headers).json()
        for item in r:
            api.balance[str.lower(item['currency'])] = item['total']
        time.sleep(5)
