import requests
import defs
import pandas as pd
import numpy as np
# data la el in video = rjson la mine


def desired_numbered_of_collumns():#display the desired number of collumns
    desired_width=150
    pd.set_option('display.width',desired_width)
    np.set_printoptions(linewidth=desired_width)
    pd.set_option('display.max_columns',15)
desired_numbered_of_collumns()


session = requests.Session()
instrument = "EUR_USD"
count = 10
granularity = "M5"
url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/instruments"
url = f"{defs.OANDA_URL}/instruments/{instrument}/candles"
print(url),print()
print(url),print()


params = dict( #parametrii pt candle
    count=count,
    granularity = granularity,
    price = "MBA"
)
#print(params)


response = session.get(url,params=params,headers=defs.SECURE_HEADER)
rsc = response.status_code
rjson = response.json()
#print(rsc),print()
#print(rjson),print()
#print(rjson.keys()),print()
#print(rsc2),print()
#print(rjson2),print()
#print(rjson2.keys()),print()




instruments = rjson['instruments']
#print(instruments)
#print(len(instruments)),print()
instKeys = instruments[0].keys()
##print(instKeys),print()
instrument_data = []
for item in instruments:
    new_ob = dict(
        name = item['name'],
        type = item['type'],
        displayName = item['displayName'],
        pipLocation = item['pipLocation'],
        marginRate = item['marginRate']
        )
    instrument_data.append(new_ob)
#for item in instrument_data[0:3]:
#    print(item)
#print()

instrument_df = pd.DataFrame.from_dict(instrument_data)
#print(instrument_df),print()
#instrument_df.to_pickle("instruments.pkl") #creaza un fel de excel in care retine valori
new_table = pd.read_pickle("instruments.pkl") #citeste acel file cu valori




prices = ['mid', 'bid', 'ask']
ohlc = ['o','h','l','c']

# for price in prices:
#     for oh in ohlc:
#         print(f"{price}_{oh}")


#print(rjson2['candles'][0]),print(rjson2['candles'][0]['bid']['o']),print()

our_data = []
#print(len(rjson2['candles'])),print()
for candle in rjson2['candles']:
    if candle['complete'] == False:
        continue
    new_dict = {}
    new_dict['time'] = candle['time']
    new_dict['volume'] = candle['volume']
    for price in prices:
        for oh in ohlc:
            new_dict[f"{price}_{oh}"] = candle[price][oh]
    our_data.append(new_dict)

candles_dt = pd.DataFrame.from_dict(our_data)
print(candles_dt)
candles_dt.to_pickle("EUR_USD_HR.pkl")

