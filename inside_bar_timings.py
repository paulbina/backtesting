import pandas as pd
import utils
import datetime as dt
from dateutil.parser import *

df_trades = pd.read_pickle("USD_JPY_H4_trades.pkl")
pair = "USD_JPY"
df_raw = pd.read_pickle(utils.get_his_data_filename(pair, "M5"))


non_cols = ['time', 'volume']
mod_cols = [x for x in df_raw.columns if x not in non_cols]
df_raw[mod_cols] = df_raw[mod_cols].apply(pd.to_numeric)
#from string to dt
df_trades["time"] = [parse(x) for x in df_trades.time]
df_raw["time"] = [parse(x) for x in df_raw.time]
#end
df_trades["next"] = df_trades["time"].shift(-1)
df_trades['trade_end'] = df_trades.next + dt.timedelta(hours=3, minutes=55)
df_trades['trade_start'] = df_trades.time + dt.timedelta(hours=4)
print(df_trades[['time', 'next', 'trade_end', 'trade_start']].head())

df_trades.dropna(inplace=True)
df_trades.reset_index(drop=True, inplace=True)

def signal_text(signal):
    if signal == 1:
        return 'BUY'
    elif signal == -1:
        return 'SELL'
    return 'NONE'

def triggered(direction, current_price, signal_price):
    if direction == 1 and current_price > signal_price:
        return True
    elif direction == -1 and current_price < signal_price:
        return True


def end_hit_calc(direction, SL, price, start_price):
    delta = price - start_price
    full_delta = start_price - SL
    fraction = abs(delta / full_delta)

    if direction == 1 and price >= start_price:
        return fraction
    elif direction == 1 and price < start_price:
        return -fraction
    elif direction == -1 and price <= start_price:
        return fraction
    elif direction == -1 and price > start_price:
        return -fraction

def process_buy(TP, SL, ask_prices, bid_prices, entry_price):
    for index, price in enumerate(ask_prices):
        if triggered(1, price, entry_price) == True:
            for live_price in bid_prices[index:]:
                if live_price >= TP:
                    return 2.0
                elif live_price <= SL:
                    return -1.0
            return end_hit_calc(1, SL, live_price, entry_price)
    return 0.0

def process_sell(TP, SL, ask_prices, bid_prices, entry_price):
    for index, price in enumerate(bid_prices):
        if triggered(-1, price, entry_price) == True:
            for live_price in ask_prices[index:]:
                if live_price <= TP:
                    return 2.0
                elif live_price >= SL:
                    return -1.0
            return end_hit_calc(-1, SL, live_price, entry_price)
    return 0.0

def process_trade(start_index, direction, TP, SL, prices, start_price):
    if direction == 1:
        return process_buy(start_index, TP, SL, prices, start_price)
    else:
        return process_sell(start_index, TP, SL, prices, start_price)


def process_m5(m5_df, row):
    result = 0.0
    for index, price in enumerate(m5_df.mid_c.values):
        #[23,35,54,484,54,84,]
        #first index is 0
        if triggered(row.SIGNAL, price, row.ENTRY) == True:
            #print(f"Signal at {index} {price:.2f} {row.ENTRY:.2f} {row.SIGNAL:.2f}")
            result = process_trade(index, row.SIGNAL, row.TAKEPROFIT, row.STOPLOSS, m5_df.mid_c.values, row.ENTRY)
            break
    return result

total = 0
for index, row in df_trades.iterrows():
    m5_data = df_raw[(df_raw.time >= row.trade_start) & (df_raw.time <= row.trade_end)]
    if row.SIGNAL == 1:
        r = process_buy(row.TAKEPROFIT, row.STOPLOSS, m5_data.ask_c.values, m5_data.bid_c.values, row.ENTRY)
        total += r
    else:
        r = process_sell(row.TAKEPROFIT, row.STOPLOSS, m5_data.ask_c.values, m5_data.bid_c.values, row.ENTRY)
        total += r
print(total)






