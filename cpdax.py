import time
import requests
import hmac
import hashlib
import json
import threading
import traceback
import urllib

class Cpdax():
    price = {}
    balance = {}
    api_key = ''
    secret_key = ''
    def __init__(self, key, secret):
        self.api_key = key
        self.secret_key = secret
        self.run_worker()

    def headers(self, method, endpoint, body):
        t = str(int(time.time()))
        msg = self.api_key + "" + t + "" + method + "" + endpoint + body
        h = hmac.new(str.encode(self.secret_key), str.encode(msg), hashlib.sha256).hexdigest()
        return {
            'CP-ACCESS-KEY': self.api_key,
            'CP-ACCESS-TIMESTAMP': t,
            'CP-ACCESS-DIGEST': h,
            'Content-Type': 'application/json'}

    def bid(self):
        return self.price

    def run_worker(self):
        r = requests.get("https://api.cpdax.com/v1/tickers/detailed")
        if r.status_code != requests.codes.ok:
            return
        # TODO cpdax API 확인
        li = r.json()
        res = {}
        for i in range(0, len(li)):
            if li[i]['currency_pair'].endswith('KRW'):
                cur = str.lower(li[i]['currency_pair'][0:3])
                res[cur] = float(li[i]['last'])

        self.price = res

        p_thread = threading.Thread(target=get_cpdax_price, args=(self,))
        p_thread.daemon = True
        p_thread.start()

        b_thread = threading.Thread(target=get_cpdax_balance, args=(self,))
        b_thread.daemon = True
        b_thread.start()

        # Pre check doned

    def buy_coin(self, cur, amount, account):
        try:
            if round(amount / self.price[cur], 4) < account:
                size = str(round(amount / self.price[cur], 4))
            else:
                size = str(round(account, 4))
            print('cpdax buy_coin %f' % round(amount / self.price[cur], 4))

            body = {'type': 'limit', 'side': 'buy',
                                    'product_id': str(cur).upper()+"-KRW",
                                    'size': size, 'price': str(int(self.price[cur]))}
            bdt = json.dumps(body).replace(" ", "")
            #r = requests.post("https://api.cpdax.com/v1/orders",
            #                  headers=self.headers('POST', '/v1/orders/', bdt),
            #                  data=bdt)
            #ret = urllib.request.urlopen(urllib.request.Request("https://api.cpdax.com/v1/orders",
            #                                                    str.encode(json.dumps(body)),
            #                                                    self.headers('POST', '/v1/orders/', bdt)))

            cp_access_timestamp = str(int(time.time()))
            digest_string = self.api_key + "" + str(cp_access_timestamp) + "POST" + "/v1/orders"
            digest_string = digest_string + json.dumps(body).replace(" ", "")
            cp_access_digest = hmac.new(str.encode(self.secret_key), str.encode(digest_string), hashlib.sha256).hexdigest()
            headers = {
                'CP-ACCESS-KEY': self.api_key,
                'CP-ACCESS-TIMESTAMP': cp_access_timestamp,
                'CP-ACCESS-DIGEST': cp_access_digest,
                'Content-Type': 'application/json'
            }
            ret = urllib.request.urlopen(urllib.request.Request("https://api.cpdax.com/v1/orders", str.encode(json.dumps(body)), headers))

            r = json.loads(ret.read().decode())
            print(bdt)
            print(json.dumps(r))
            return {
                'units': r['filled_size'],
                'price': r['price']
            }
        except:
            traceback.print_exc()
            return {
                'units': 0,
                'price': 0,
                'error': True
            }

        # Pre check doned

    def sell_coin(self, cur, amount):
        print('cpdax sell_coin %f' % amount)
        body={'type': 'market', 'side': 'sell', 'product_id': str(cur).upper() + "-KRW", 'size': str(amount)}
        r = requests.post("https://api.cpdax.com/v1/orders", headers=self.headers('POST', '/v1/orders',json.dumps(body)),data=json.dumps(body))
        if r.status_code != requests.codes.of:
            return {'error': True}
        return r.json()

def get_cpdax_price(api):
    while True:
        r = requests.get("https://api.cpdax.com/v1/tickers/detailed")
        if r.status_code != requests.codes.ok:
            return
        # TODO cpdax API 확인
        li = r.json()
        res = {}
        for i in range(0, len(li)):
            if li[i]['currency_pair'].endswith('KRW'):
                cur = str.lower(li[i]['currency_pair'][0:3])
                res[cur] = float(li[i]['last'])

        api.price = res
        time.sleep(5)

def get_cpdax_balance(api):
    while True:
        r = requests.get('https://api.cpdax.com/v1/balance', headers=api.headers('GET', '/v1/balance','')).json()
        for item in r:
            api.balance[str.lower(item['currency'])] = item['total']
        time.sleep(5)

