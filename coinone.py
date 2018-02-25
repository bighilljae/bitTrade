import base64
import simplejson as json
import hashlib
import hmac
import requests
import httplib2
import time
import math
import threading



URL = 'https://api.coinone.co.kr'

class Coinone:
    price = {}
    balance = {}
    def __init__(self):
        self.api_key = API_KEY
        self.secret_key = SECRET_KEY
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
        if res.status_code != requests.codes.ok:
            print('[ERR] coinone: ' + endpoint + " : " + res.text)
        return res

    def bid(self):
        return self.price

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
        for cur in currency:
            r = requests.get("https://api.coinone.co.kr/orderbook/?currency=%s" % cur)
            if r.status_code != requests.codes.ok:
                continue
            res[cur] = float(r.json()['bid'][0]['price'])
        api.price = res
        time.sleep(10)

def get_coinone_balance(api):
    while True:
        r = api.secret_api("/v2/account/balance").json()
        for key in r:
            try:
                api.balance[key] = r[key]['balance']
            except:
                pass
        time.sleep(5)
