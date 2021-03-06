import base64
import simplejson as json
import hashlib
import hmac
import requests
import httplib2
import time
import math
import threading
import sys, traceback



URL = 'https://api.coinone.co.kr'

class Coinone:
    api_key = ''
    secret_key = ''
    price = {}
    balance = {}
    name = "coinone"
    def __init__(self, key, secret):
        self.api_key = key
        self.secret_key = secret
        self.run_worker()

    def get_signature(self, encoded_payload, key):
        signature = hmac.new(key, encoded_payload, hashlib.sha512)
        return signature.hexdigest()

    def get_header(self, payload):
        dumped_json = json.dumps(payload)
        encoded_payload = base64.b64encode(dumped_json.encode('utf-8'))
        encoded_secret_key = base64.b64encode(self.secret_key.upper().encode('utf-8'))

        return {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))}

    def secret_api(self, endpoint, **kwargs):
        url_path = URL + endpoint
        endpoint_item_array = {
            "access_token": self.api_key,
            'nonce': time.time()*10000
        }
        payload = dict(endpoint_item_array, **kwargs)
        res = requests.post(url_path, headers=self.get_header(payload), data=payload)
        if endpoint != '/v2/account/balance':
            print('coinone secret_api ' + endpoint + ' ' + str(res.status_code) + ' ' + res.text)
        if res.status_code != requests.codes.ok:
            print('[ERR] coinone: ' + endpoint + " : " + res.text)
        return res

    def bid(self):
        return self.price

    # Pre check doned
    def buy_coin(self, cur, amount, account):
        if round(amount/self.price[cur], 4) < account:
            qty = str(round(amount/self.price[cur], 4))
        else:
            qty = str(round(account, 4))
        try:
            if float(qty) == 0:
                raise Exception('Size Error')
            r = self.secret_api("/v2/order/limit_buy/", price=str(int(self.price[cur])), qty=qty, currency=cur)
            return {
                'units': round(amount/self.price[cur], 4),
                'price': self.price[cur]
            }
        except:
            return {
                'units': 0,
                'price': 0,
                'error': True
            }

    # Pre check doned
    def sell_coin(self, cur, amount):
        # r = self.secret_api("/trade/market_sell", {'currency': str(cur).upper(), 'units': amount}).json()
        r = self.secret_api("/v2/order/limit_sell/", price=str(int(self.price[cur])), qty=str(amount), currency=cur)
        if r.status_code != requests.codes.ok:
            return {'price': 0, 'units': 0, 'error': True}
        return r.json()


    def run_worker(self):
        p_thread = threading.Thread(target=get_coinone_price, args=(self,))
        p_thread.daemon = True
        p_thread.start()

        b_thread = threading.Thread(target=get_coinone_balance, args=(self,))
        b_thread.daemon = True
        b_thread.start()


def get_coinone_price(api):
    while True:
        currency = ['btc', 'bch', 'eth', 'etc', 'xrp', 'qtum', 'ltc', 'btg']
        res = {}
        try:
            for cur in currency:
                r = requests.get("https://api.coinone.co.kr/orderbook/?currency=%s" % cur)
                if r.status_code != requests.codes.ok:
                    continue
                res[cur] = float(r.json()['bid'][0]['price'])
            api.price = res
        except:
            traceback.print_exc(file=sys.stdout)
        time.sleep(20)

def get_coinone_balance(api):
    while True:
        r = api.secret_api("/v2/account/balance").json()
        for key in r:
            try:
                api.balance[key] = r[key]['balance']
            except:
                pass
        time.sleep(5)
