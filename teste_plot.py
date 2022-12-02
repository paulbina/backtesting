import numpy as np
import pandas as pd
import utils
import plotly.graph_objects as go


pair = "EUR_USD"
granularity = "H1"
ma_list = [5,8,13,21,34]
df = pd.read_pickle(utils.get_his_data_filename(pair,granularity))
non_cols = ['time', 'volume']
mod_cols = [x for x in df.columns if x not in non_cols]
df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

df_ma = df[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c']].copy()
for ma in ma_list:
    df_ma[f'MA_{ma}'] = df_ma.mid_c.rolling(window=ma).mean()
df_ma.dropna(inplace=True)
df_ma.reset_index(drop=True, inplace=True)
df_ma['DIFF'] = df_ma.MA_5 - df_ma.MA_8
df_ma['DIFF_PREV'] = df_ma.DIFF.shift(1)
df_ma['DIFF2'] = df_ma.MA_8 - df_ma.MA_13
df_ma['DIFF_PREV2'] = df_ma.DIFF2.shift(1)
df_ma['DIFF3'] = df_ma.MA_13 - df_ma.MA_21
df_ma['DIFF_PREV3'] = df_ma.DIFF2.shift(1)
df_ma['DIFF4'] = df_ma.MA_21 - df_ma.MA_34
df_ma['DIFF_PREV4'] = df_ma.DIFF2.shift(1)


df_plot = df_ma.iloc[-1000:]
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df_plot.time, open=df_plot.mid_o, high=df_plot.mid_h, low=df_plot.mid_l, close=df_plot.mid_c,
    line=dict(width=1), opacity=1,
    increasing_fillcolor='#24A06B',
    decreasing_fillcolor="#CC2E3C",
    increasing_line_color='#2EC886',
    decreasing_line_color='#FF3A4C'
))
for ma in ma_list:
    col = f"MA_{ma}"
    fig.add_trace(go.Scatter(x=df_plot.time, y=df_plot[col],
                             line=dict(width=2),
                             line_shape='spline',
                             name=col
                             ))

#fig.update_layout(width=1000,height=400)
fig.update_layout(margin=dict(l=10,r=10,b=10,t=10),
                  font=dict(size=10,color='#e1e1e1'),
                  plot_bgcolor='black',
                  paper_bgcolor='black')
fig.update_xaxes(
    gridcolor="#1f292f",
    showgrid=False,fixedrange=True,rangeslider=dict(visible=True)
)

fig.update_yaxes(
    gridcolor="#1f292f",
    showgrid=False
)
