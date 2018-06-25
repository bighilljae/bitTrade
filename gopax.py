import requests
import datetime
import threading
import time
import os
import sys
import hmac
import base64
import hashlib


class Gopax():
    api_key = ''
    secret_key = ''
    price = {}
    balance = {}
    name = "gopax"
    def __init__(self, key, secret):
        self.api_key = key
        self.secret_key = secret
        self.run_worker()

    def headers(self, method, endpoint):
        nonce = str(time.time())

        what = nonce + method + endpoint
        key = base64.b64decode(self.secret_key)
        signature = hmac.new(key, str(what).encode('utf-8'), hashlib.sha512)
        signature_b64 = base64.b64encode(signature.digest())

        return {
            'API-Key': self.api_key,
            'Signature': signature_b64,
            'Nonce': nonce,
            'Content-Type': 'application/json'
        }

    def bid(self):
        return self.price

    def run_worker(self):
        p_thread = threading.Thread(target=get_gopax_price, args=(self,))
        p_thread.daemon = True
        p_thread.start()

        b_thread = threading.Thread(target=get_gopax_balance, args=(self,))
        b_thread.daemon = True
        b_thread.start()



    def buy_coin(self, cur, amount, account):
        if round(amount / self.price[cur], 4) < account:
            size = str(round(amount / self.price[cur], 4))
        else:
            size = str(round(account, 4))
        payload = {
            "amount": size,
            "type": 'market',
            "side": 'buy',
            "tradingPairName": str(cur).upper()+"-KRW"
        }
        try:
            if float(size) == 0 :
                raise Exception('Size error')
            print('gopax buy %f' % amount)
            r = requests.post("https://api.gopax.co.kr/orders", headers=self.headers('POST', '/orders'), data=payload)
            r = r.json()
            return {
                'units': size,
                'price': str(int(self.price[cur]))
            }
        except:
            return {
                'units': 0,
                'price': 0,
                'error': True
            }

        # Pre check doned

    def sell_coin(self, cur, amount):
        print('gopax sell %f' % amount)
        r = requests.post("https://api.gopax.co.kr/orders", headers=self.headers('POST', '/orders'),
                          data={'type': 'market',
                                'tradingPairName': str(cur)+"-KRW",
                                'amount': amount,
                                'side': 'sell'})
        if r.status_code != requests.codes.ok:
            return {'units': 0, 'price': 0, 'error': True}
        return r.json()

def get_gopax_balance(api):
    while True:
        r = requests.get('https://api.gopax.co.kr/balances', headers=api.headers('GET', '/balances')).json()
        for p in r:
            api.balance[str.lower(r[p]['asset'])] = r[p]['avail']
        time.sleep(5)

def get_gopax_price(api):
    while True:
        r = requests.get("https://api.gopax.co.kr/trading-pairs/stats")
        res = {}
        for p in r.json():
            if p['name'].endswith('KRW'):
                res[p['name'][0:3].lower()] = p['close']
        api.price = res

        time.sleep(5)
