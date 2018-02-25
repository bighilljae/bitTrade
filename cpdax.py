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

    def __init__(self):
        self.run_worker()

    @property
    def headers(self):
        t = str(int(time.time()))
        msg = API_KEY + t + 'GET' + '/v1/balance'
        h = hmac.new(SECRET_KEY.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
        h64 = h
        return {
            'CP-ACCESS-KEY': API_KEY,
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