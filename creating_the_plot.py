import numpy as np
import pandas as pd
import utils
import plotly.graph_objects as go


pair = "CAD_JPY"
granularity = "H1"
movingAverage_list = [8, 16]
dataFrame = pd.read_pickle(utils.get_his_data_filename(pair, granularity))
non_cols = ['time', 'volume']
mod_cols = [x for x in dataFrame.columns if x not in non_cols]
dataFrame[mod_cols] = dataFrame[mod_cols].apply(pd.to_numeric)

dataFrame_ma = dataFrame[['time', 'mid_o', 'mid_h', 'mid_l', 'mid_c']].copy()
for ma in movingAverage_list:
    dataFrame_ma[f'MA_{ma}'] = dataFrame_ma.mid_c.rolling(window=ma).mean()
dataFrame_ma.dropna(inplace=True)
dataFrame_ma.reset_index(drop=True, inplace=True)
dataFrame_ma['DIFF'] = dataFrame_ma.MA_8 - dataFrame_ma.MA_16
dataFrame_ma['DIFF_PREV'] = dataFrame_ma.DIFF.shift(1)


dataFrame_plot = dataFrame_ma.iloc[-300:]
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=dataFrame_plot.time, open=dataFrame_plot.mid_o, high=dataFrame_plot.mid_h, low=dataFrame_plot.mid_l, close=dataFrame_plot.mid_c,
    line=dict(width=1), opacity=1,
    increasing_fillcolor='#24A06B',
    decreasing_fillcolor="#CC2E3C",
    increasing_line_color='#2EC886',
    decreasing_line_color='#FF3A4C'
))
for ma in movingAverage_list:
    column = f"MA_{ma}"
    fig.add_trace(go.Scatter(x=dataFrame_plot.time, y=dataFrame_plot[column],
                             line=dict(width=2),
                             line_shape='spline',
                             name=column
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
