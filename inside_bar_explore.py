import webbrowser

import pandas as pd
import plotly.graph_objects as go
import utils


plot_cols = ['ENTRY', 'STOPLOSS', 'TAKEPROFIT']
plot_colours = ['#043ef9', '#eb5334', '#34eb37']
def plot_candles(df_plot):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df_plot.time, open=df_plot.mid_o, high=df_plot.mid_h, low=df_plot.mid_l, close=df_plot.mid_c,
        line=dict(width=1), opacity=1,
        increasing_fillcolor='#24A06B',
        decreasing_fillcolor="#CC2E3C",
        increasing_line_color='#2EC886',
        decreasing_line_color='#FF3A4C'
    ))

    for i in range(0, 3):
        fig.add_trace(go.Scatter(
            x=df_buys.time,
            y=df_buys[plot_cols[i]],
            mode='markers',
            marker=dict(color=plot_colours[i], size=12)
        ))
    for i in range(0, 3):
        fig.add_trace(go.Scatter(
            x=df_sells.time,
            y=df_sells[plot_cols[i]],
            mode='markers',
            marker=dict(color=plot_colours[i], size=12)
        ))
    fig.update_layout(width=1000, height=400,
                      margin=dict(l=10, r=10, b=10, t=10),
                      font=dict(size=10, color="#e1e1e1"),
                      paper_bgcolor="#1e1e1e",
                      plot_bgcolor="#1e1e1e")
    fig.update_xaxes(
        gridcolor="#1f292f",
        showgrid=True, fixedrange=True, rangeslider=dict(visible=False),
        rangebreaks=[
            dict(bounds=["sat", "mon"])
        ]
    )
    fig.update_yaxes(
        gridcolor="#1f292f",
        showgrid=True
    )
    fig.show()


pair = "USD_JPY"
granularity = "H4"
df_raw = pd.read_pickle(utils.get_his_data_filename(pair, granularity))

non_cols = ['time', 'volume']
mod_cols = [x for x in df_raw.columns if x not in non_cols]
df_raw[mod_cols] = df_raw[mod_cols].apply(pd.to_numeric)



SLOSS = 0.4
TPROFIT = 0.8
ENTRY_PRC = 0.1

def direction(row):
    if row.mid_c > row.mid_o:
        return 1
    return -1

def get_signal(row):
    if row.mid_h_prev > row.mid_h and row.mid_l_prev < row.mid_l:
        return row.DIRECTION_prev
    return 0

def get_entry_stop(row):
    if row.SIGNAL == 1:
        return (row.RANGE_prev * ENTRY_PRC) + row.mid_h_prev
    elif row.SIGNAL == -1:
        return row.mid_l_prev - (row.RANGE_prev * ENTRY_PRC)
    else:
        return 0

def get_stop_loss(row):
    if row.SIGNAL == 1:
        return row.ENTRY - (row.RANGE_prev * SLOSS)
    elif row.SIGNAL == -1:
        return row.ENTRY + (row.RANGE_prev * SLOSS)
    else:
        return 0

def get_take_profit(row):
    if row.SIGNAL == 1:
        return row.ENTRY + (row.RANGE_prev * TPROFIT)
    elif row.SIGNAL == -1:
        return row.ENTRY - (row.RANGE_prev * TPROFIT)
    else:
        return 0


df = df_raw[['time','mid_o', 'mid_h', 'mid_l', 'mid_c', 'bid_c', 'ask_c']].copy()
df['RANGE'] = df.mid_h - df.mid_l
df['mid_h_prev'] = df.mid_h.shift(1)
df['mid_l_prev'] = df.mid_l.shift(1)
df['RANGE_prev'] = df.RANGE.shift(1)
df['DIRECTION'] = df.apply(direction, axis=1)
df['DIRECTION_prev'] = df.DIRECTION.shift(1).fillna(0).astype(int)
df.dropna(inplace=True)
df['SIGNAL'] = df.apply(get_signal, axis=1)
df.reset_index(drop=True, inplace=True)

df['ENTRY'] = df.apply(get_entry_stop, axis=1)
df['STOPLOSS'] = df.apply(get_stop_loss, axis=1)
df['TAKEPROFIT'] = df.apply(get_take_profit, axis=1)

df_plot  = df.iloc[0:60]
df_buys = df_plot[df_plot.SIGNAL == 1]
df_sells = df_plot[df_plot.SIGNAL == -1]

df[df.SIGNAL!=0].to_pickle("his_data/USD_JPY_H4_trades.pkl")

class Trade():
    def __init__(self, row):
        self.candle_date = row.time
        self.direction = row.SIGNAL
        self.entry = row.TAKEPROFIT
        self.TP = row.TAKEPROFIT
        self.SL = row.STOPLOSS
        self.running = False
        self.result = None
        self.stopped = None

    def update(self, row):
        if self.running == True:
            self.update_result(row)
        else:
            self.check_entry(row)

    def check_entry(self,row):
        if self.direction == 1 and row.mid_c >= self.entry or self.direction == -1 and row.mid_c <= self.entry:
            self.index = row.name
            self.opened = row.time
            self.running = True

    def update_result(self,row):
        if self.direction == 1:
            if row.mid_c >= self.TP:
                self.result = 2.0
            elif row.mid_c <= self.SL:
                self.result = -1.0
        else:
            if row.mid_c <= self.TP:
                self.result = 2.0
            elif row.mid_c >= self.SL:
                self.result = -1.0

        if self.result is not None:
            self.result = False
            self.stopped = row.time

open_trades = []
closed_trades = []
for index, row in df.iterrows():
    for ot in open_trades:
        ot.update(row)
        if ot.stopped is not None:
            closed_trades.append(ot)
    open_trades = [x for x in open_trades if x.stopped is None]

    if row.SIGNAL != 0:
        open_trades = [x for x in open_trades if x.running == True]
        open_trades.append(Trade(row))


df_trades = pd.DataFrame.from_dict([vars(x) for x in closed_trades])



    ##check open trades, update
        ##add closed, remove from open

    ##signal and open trade
