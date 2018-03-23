from flask import Flask, render_template, json, request
from coinone import Coinone
from bithumb import Bithumb
from korbit import Korbit
from cpdax import Cpdax
from alarm import Alarm
import requests
import datetime
import os
from auth import *

app = Flask(__name__)
bot = Alarm(5)
api_bithumb = Bithumb(BITHUMB_KEY, BITHUMB_SECRET)
api_korbit = Korbit(KORBIT_KEY, KORBIT_SECRET, KORBIT_USERNAME, KORBIT_PWD)
api_cpdax = Cpdax(CPDAX_KEY, CPDAX_SECRET)
api_coinone = Coinone(COINONE_KEY, COINONE_SECRET)

app_settings = {
    'alarm': True,
    'trade': False,
    'label': ''
}

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
            continue
        if max(u[cur]) / min(u[cur]) > 1.006 and app_settings['alarm'] is True and not cur in app_settings['label'].split(','):
            bot.add(cur, max(u[cur]) / min(u[cur]))
    bot.message()


    writedata(market)
    return json.dumps(u)


@app.route('/save')
def saveSetting():
    alrm = request.args.get('alarm', default=False, type=str)
    if alrm == 'true':
        app_settings['alarm'] = True
    else:
        app_settings['alarm'] = False
    trade = request.args.get('trade', default=False, type=str)
    if trade == 'true':
        app_settings['trade'] = True
    else:
        app_settings['trade'] = False
    label = request.args.get('label', default='', type=str)
    app_settings['label'] = label
    return alrm + ' ' + trade + ' ' + label


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
    for cen in li:
        if m > li[cen]:
            m = li[cen]
    return m

def max(li):
    m = 0
    for cen in li:
        if m < li[cen]:
            m = li[cen]
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
