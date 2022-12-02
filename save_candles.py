import requests
import defs
import pandas as pd
import numpy as np

session = requests.Session()
ins_df = pd.read_pickle("instruments.pkl")
our_currencies = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'NZD', 'CAD']

def fetch_candles(pair_name, count, granularity):
    url = f"{defs.OANDA_URL}/instruments/{pair_name}/candles"
    params = dict(
        count = count,
        granularity = granularity,
        price = "MBA"
    )
    response = session.get(url, params=params, headers=defs.SECURE_HEADER)
    return response.status_code, response.json()
res = fetch_candles("EUR_USD",10,"H1")

def get_candles_df(json_response):
    prices = ['mid', 'bid', 'ask']
    ohlc = ['o', 'h', 'l', 'c']
    our_data = []
    for candle in json_response['candles']:
        if candle['complete'] == False:
            continue
        new_dict = {}
        new_dict['time'] = candle['time']
        new_dict['volume'] = candle['volume']
        for price in prices:
            for oh in ohlc:
                new_dict[f"{price}_{oh}"] = candle[price][oh]
        our_data.append(new_dict)
    return pd.DataFrame.from_dict(our_data)

def save_file(candles_df, pair, granularity):
    candles_df.to_pickle(f"his_data/{pair}_{granularity}.pkl")

def create_data(pair, granularity):
    code, json_data = fetch_candles(pair, 4000, granularity)
    if code != 200:
        print(pair, "Error")
        return
    df = get_candles_df(json_data)
    print(f"{pair} loaded {df.shape[0]} candles from {df.time.min()} to {df.time.max()}")
    save_file(df, pair, granularity)

for p1 in our_currencies:
    for p2 in our_currencies:
        pair = f"{p1}_{p2}"
        if pair in ins_df.name.unique():
            create_data(pair, "M5")