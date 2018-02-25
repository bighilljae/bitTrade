import requests
import datetime
import threading
import time

class Korbit():
    price = {}
    balance = {}
    def __init__(self):
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
            'Authorization': self.token['token_type'] + ' ' + self.token['access_token']
        }

    def create_token(self):
        payload = {
            'client_id': API_KEY,
            'client_secret': SECRET_KEY,
            'username': USERNAME,
            'password': PWD,
            'grant_type': 'password'
        }
        res = requests.post("https://api.korbit.co.kr/v1/oauth2/access_token", data=payload)
        self.token = res.json()
        self.expire_date = datetime.datetime.now() + datetime.timedelta(hours=1)

    def refresh_token(self):
        payload = {
            'client_id': API_KEY,
            'client_secret': SECRET_KEY,
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