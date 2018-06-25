from flask import Flask, render_template, json, request
from coinone import Coinone
from bithumb import Bithumb
from korbit import Korbit
from cpdax import Cpdax
from gopax import Gopax
from alarm import Alarm
import threading
import requests
import datetime
import os
import time
from auth import *

app = Flask(__name__)
bot = Alarm(5)
apis = []
apis.append(Bithumb(BITHUMB_KEY, BITHUMB_SECRET))
apis.append(Korbit(KORBIT_KEY, KORBIT_SECRET, KORBIT_USERNAME, KORBIT_PWD))
apis.append(Coinone(COINONE_KEY, COINONE_SECRET))
apis.append(Gopax(GOPAX_KEY, GOPAX_SECRET))
# aps.append(Cpdax(CPDAX_KEY, CPDAX_SECRET))
trade_history = []
last_trade = None

app_settings = {
    'alarm': False,
    'trade': False,
    'label': 'btc',
    'threshold': 1.5,
    'alarm_thres': 0.6,
    'order': 100000
}


@app.route('/')
def home():
    return render_template('index.html', api_list=list(map(lambda ap: ap.name, apis)))

@app.route('/history')
def history():
    return json.dumps(trade_history)

@app.route('/exchangekrw/')
def exchange():
    # change to api_price
    exchange_krw = {}
    for api in apis:
        exchange_krw[api.name] = api.balance
        exchange_krw[api.name]['get2'] = get2(api)
    print(json.dumps(exchange_krw))
    return json.dumps(exchange_krw)

@app.route('/bid/')
def bid():
    global last_trade
    global trade_history
    market = {}
    for api in apis:
        market[api.name] = api.bid()

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
        if cur not in app_settings['label'].split(','):
            continue
        m1, c1 = max(u[cur])
        m2, c2 = min(u[cur])
        if m1 / m2 > 1+app_settings['alarm_thres']/100 and app_settings['alarm'] is True and cur in app_settings['label'].split(','):
            bot.add(cur, m1 / m2)
        if last_trade is not None and datetime.datetime.now().minute == last_trade.minute:
            continue
        if m1 / m2 > (1+app_settings['threshold']/100) and app_settings['trade'] is True :
            last_trade = datetime.datetime.now()
            trade_amount = int(app_settings['order']) / c2api(c1).price[cur]
            if float(c2api(c2).balance[cur]) < trade_amount:
                bot.add('not enough crypto currency', None)
                print('not enough crypto currency')
# bot.message()
            r = c2api(c2).buy_coin(cur, app_settings['order'], float(c2api(c1).balance[cur]))
            print(json.dumps(r))
            if float(r['units']) > 0:
                sell_res = c2api(c1).sell_coin(cur, float(r['units']))
                print(json.dumps(sell_res))
                trade_history.insert(0, {'buy': c2api(c2).name,
                                           'sell': c2api(c1).name,
                                            'cur': cur,
                                           'amount': r['units'],
                                           'time': datetime.datetime.now().strftime('%m-%d %H:%M')})
                st = 'Trade Done ' + c2api(c2).name + ' ' + c2api(c1).name
                print(st)
                bot.add(st, None)
                bot.message(True)

            if len(trade_history) > 10:
                trade_history = trade_history[:10]
           
    if app_settings['alarm'] is True:
        bot.message()


    # writedata(market)
    return json.dumps(u)

def c2api(c):
    for api in apis:
        if api.name == c:
            return api

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

    ll = request.args.get('threshold', default='', type=str)
    app_settings['threshold'] = float(ll)

    at = request.args.get('alarm_thres', default='', type=str)
    app_settings['alarm_thres'] = float(at)

    ord = request.args.get('order', default='', type=str)
    app_settings['order'] = int(ord)
    print(json.dumps(app_settings))
    return json.dumps(app_settings)


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
    c = ''
    for cen in li:
        if m > li[cen]:
            m = li[cen]
            c = cen
    return m, c

def max(li):
    m = 0
    c = ''
    for cen in li:
        if m < li[cen]:
            m = li[cen]
            c = cen
    return m, c


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
    return str(sum)


def run_bid():
    while True:
        time.sleep(5)
        if app_settings['alarm'] is True:
            try:
                bid()
            except:
                pass

def test():
    for api in apis:
        r = api.buy_coin('btc', 10000, 100000)
        if 'error' in r:
            print(api.name + ' buy error' + json.dumps(r))
            return
        r = api.sell_coin('btc', float(r['units']))
        if 'error' in r:
            print(api.name + ' sell error' + json.dumps(r))
            return


if __name__ == '__main__':
    b_thread = threading.Thread(target=run_bid)
    b_thread.daemon = True
    b_thread.start()
    app.run(host='0.0.0.0', port=8080)

