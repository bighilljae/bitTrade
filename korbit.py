import requests
import datetime
import threading
import time
import os
import sys

class Korbit():
    api_key = ''
    secret_key = ''
    username = ''
    password = ''
    price = {}
    balance = {}
    name = "korbit"
    def __init__(self, key, secret, name, pwd):
        self.api_key = key
        self.secret_key = secret
        self.username = name
        self.password = pwd
        self.token = {}
        self.expire_date = None
        self.create_token()
        self.run_worker()

    @property
    def headers(self):
        if self.expire_date < datetime.datetime.now():
            self.refresh_token()
        return {
            'Accept': 'application/json',
            'Authorization': "{} {}".format(self.token['token_type'],self.token['access_token'])
        }

    def create_token(self):
        payload = {
            'client_id': self.api_key,
            'client_secret': self.secret_key,
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
        }
        try:
            f = open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep + 'korbit_token.txt', 'r')
            list = f.readlines()
            #res = f.readline().json.loads()
            res = list[0].json.loads()
            expire_date_from_korbit_token = list[1]
            f.close()
        except:
            if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep):
                os.makedirs(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep)
            f = open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep +  'korbit_token.txt', 'w')
            res = requests.post("https://api.korbit.co.kr/v1/oauth2/access_token", data=payload).json()
            f.write(str(res)+'\n')
            f.write(str(datetime.datetime.now() + datetime.timedelta(hours=1)))
            expire_date_from_korbit_token = datetime.datetime.now() + datetime.timedelta(hours=1)
            f.close()
        self.token = res
        self.expire_date = expire_date_from_korbit_token

    def refresh_token(self):
        payload = {
            'client_id': self.api_key,
            'client_secret': self.secret_key,
            'refresh_token': self.token['refresh_token'],
            'grant_type': 'refresh_token'
        }
        self.token = requests.post("https://api.korbit.co.kr/v1/oatuh2/access_token", data=payload).json()
        self.expire_date = datetime.datetime.now() + datetime.timedelta(hours=1)

    def bid(self):
        return self.price

    def run_worker(self):
        p_thread = threading.Thread(target=get_korbit_price, args=(self,))
        p_thread.daemon = True
        p_thread.start()

        b_thread = threading.Thread(target=get_korbit_balance, args=(self,))
        b_thread.daemon = True
        b_thread.start()



    def buy_coin(self, cur, amount, account):
        if round(amount / self.price[cur], 4) < account:
            size = str(round(amount / self.price[cur], 4))
        else:
            size = str(round(account, 4))
        payload = {
            'type': 'limit',
            'currency_pair': str(cur)+"_krw",
            'price': str(int(self.price[cur])),
            'coin_amount': size,
            'fiat_amount': None,
            'nonce': str(int(time.time()*1000)) 
        }
        try:
            if float(size) == 0 :
                raise Exception('Size error')
            print('korbit buy %f' % amount)
            r = requests.post("https://api.korbit.co.kr/v1/user/orders/buy", headers=self.headers, data=payload)

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
        print('korbit sell %f' % amount)
        r = requests.post("https://api.korbit.co.kr/v1/user/orders/sell", headers=self.headers,
                          data={'type': 'market', 'currency_pair': str(cur)+"_krw", 'coin_amount': amount, 'nonce': str(int(time.time()*1000))})
        if r.status_code != requests.codes.ok:
            return {'units': 0, 'price': 0, 'error': True}
        return r.json()

def get_korbit_balance(api):
    while True:
        r = requests.get('https://api.korbit.co.kr/v1/user/balances', headers=api.headers).json()
        for cur in r:
            api.balance[str.lower(cur)] = r[cur]['available']
        time.sleep(5)

def get_korbit_price(api):
    while True:
        currency = ['btc', 'bch', 'eth', 'etc', 'xrp']
        res = {}
        for cur in currency:
            r = requests.get("https://api.korbit.co.kr/v1/ticker/detailed?currency_pair=%s_krw" % cur)
            if r.status_code != requests.codes.ok:
                continue
            res[cur] = float(r.json()['bid'])
        api.price = res

        time.sleep(10)
