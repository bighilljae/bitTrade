from flask import Flask, render_template, json
from coinone import Coinone
from bithumb import Bithumb
from korbit import Korbit
from cpdax import Cpdax
import requests
import datetime
import os
from auth import *

app = Flask(__name__)
api_bithumb = Bithumb(BITHUMB_KEY, BITHUMB_SECRET)
api_korbit = Korbit(KORBIT_KEY, KORBIT_SECRET, KORBIT_USERNAME, KORBIT_PWD)
api_cpdax = Cpdax(CPDAX_KEY, CPDAX_SECRET)
api_coinone = Coinone(COINONE_KEY, COINONE_SECRET)

@app.route('/hello/')
def api_root():
    recent_price = {}
    recent_price['korbit'] = korbit_get(requests.get("https://api.korbit.co.kr/v1/transactions?currency_pair=btc_krw"))
    recent_price['bithumb'] = bithumb_get(requests.get("https://api.bithumb.com/public/recent_transactions/BTC"))
    recent_price['cpdax'] = cpdax_get(requests.get("https://api.cpdax.com/v1/trades/BTC-KRW?limit=20"))
    recent_price['coinone'] = coinone_get(requests.get("https://api.coinone.co.kr/trades/?currency=BTC"))
    return json.dumps(recent_price)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/exchangekrw/')
def exchange():
    # change to api_price
    exchange_krw = {}
    exchange_krw['coinone'] = get2(api_coinone)
    exchange_krw['korbit'] = get2(api_korbit)
    exchange_krw['cpdax'] = get2(api_cpdax)
    exchange_krw['bithumb'] = get2(api_bithumb)
    return json.dumps(exchange_krw)

@app.route('/bid/')
def bid():
    market = {}
    market['coinone'] = api_coinone.bid()
    market['korbit'] = api_korbit.bid()
    market['cpdax'] = api_cpdax.bid()
    market['bithumb'] = api_bithumb.bid()
    u = {}
    for cen in market:
        for cur in market[cen]:
            if cur in u:
                u[cur][cen] = market[cen][cur]
            else:
                u[cur] = {cen: market[cen][cur]}

    for cur in list(u):
        if len(u[cur].keys()) < 2:
            del u[cur]

    writedata(market)
    return json.dumps(u)

def writedata(market):
    market['ts'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    try:
        f = open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep + datetime.datetime.now().strftime('%Y-%m-%d')+'.txt', 'a')
    except:
        if not os.path.exists(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep):
            os.makedirs(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep)
        f = open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep + datetime.datetime.now().strftime('%Y-%m-%d')+'.txt', 'w')
    f.write(json.dumps(market) + '\n')
    f.close()

def min(li):
    m = 999999999
    for arg in li:
        if m > arg:
            m = arg
    return m

def max(li):
    m = 0
    for arg in li:
        if m < arg:
            m = arg
    return m


def korbit_get(r):
    if r.status_code != requests.codes.ok:
        return
    ar = []
    js = r.json()
    for i in range(20):
        ar.append({'price': js[i]['price'], 'amount': js[i]['amount']})
    return ar

def bithumb_get(r):
    if r.status_code != requests.codes.ok:
        return
    js = r.json()['data']
    ar = []
    for i in range(20):
        ar.append({'price': js[i]['price'], 'amount': js[i]['units_traded']})
    return ar

def cpdax_get(r):
    if r.status_code != requests.codes.ok:
        return
    js = r.json()
    ar = []
    for i in range(20):
        ar.append({'price': js[i]['price'], 'amount': js[i]['size']})
    return ar


def coinone_get(r):
    if r.status_code != requests.codes.ok:
        return
    js = r.json()['completeOrders']
    ar = []
    for i in range(1, 21):
        ar.append({'price': js[-i]['price'], 'amount': js[-i]['qty']})
    return ar


# TODO get2 함수들은 각 객체 안으로 이동
def get2(api):
    price = api.price
    balance = api.balance

    sum = 0
    try:
        sum = float(balance['krw'])
    except:
        pass

    for key in price:
        try:
            sum += float(price[key]) * float(balance[key])
        except:
            pass
    return sum

'''
현재 coinone을 제외한 거래소의 경우에는 해당 거래소가 취급하는 코인의 종류에 변동이 생기면 수동으로 코드를 변경해 맞춰 줘야 함.
자동화를 위해서는 해당 api dictionary에서 코인 이름을 빼내 맞춰야 할 것으로 보임.
'''


if __name__ == '__main__':
    app.run(debug=True)
