import pandas as pd
import plotly.graph_objects as go
from rows_and_columns import *

ma_test_res = pd.read_pickle("ma_test_res.pkl")
all_trades = pd.read_pickle("all_trades.pkl")

ma_test_res = ma_test_res[['pair', 'num_trades', 'total_gain', 'mashort', 'malong']]

ma_test_res["CROSS"] = "MA_" + ma_test_res.mashort.map(str) + "_" + ma_test_res.malong.map(str)
#print(movingAverage_test_results.head())


df_all_gains = ma_test_res.groupby(by=["CROSS", "mashort", "malong"], as_index=False).sum()
df_all_gains.sort_values(by="total_gain", ascending=False, inplace=True)
#print(df_all_gains.head())

ma_8_16 = ma_test_res[ma_test_res.CROSS=='MA_8_16'].copy()
ma_8_16.sort_values(by="total_gain", ascending=False, inplace=True)
total_pairs = len(ma_8_16.pair.unique())
# print(ma_8_16[ma_8_16.total_gain>0].shape[0])
# print(ma_8_16)
# print(total_pairs)
# print(ma_8_16[ma_8_16.total_gain>0].shape[0]/total_pairs)

df_all_gains.CROSS.unique()
for cross in df_all_gains.CROSS.unique():
    df_temp = ma_test_res[ma_test_res.CROSS==cross]
    total_pairs = df_temp.shape[0]
    n_good = df_temp[df_temp.total_gain>0].shape[0]
    #print((f"{cross:12} {n_good:4} {(n_good/total_pairs)*100:4.0f}%"))

crosses = df_all_gains.CROSS.unique()[:3]
df_good = ma_test_res[(ma_test_res.CROSS.isin(crosses)) & (ma_test_res.total_gain>0)].copy()
our_pairs = list(df_good.pair.value_counts()[:5].index)

all_trades["CROSS"] = "MA_" + all_trades.MASHORT.map(str) + "_" + all_trades.MALONG.map(str)
trades_cad_jpy = all_trades[(all_trades.CROSS=="MA_8_16") & (all_trades.PAIR+"CAD_JPY")].copy()
trades_cad_jpy['CUM_GAIN'] = trades_cad_jpy.GAIN.cumsum()

def plot_line(df_plot, name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot.time,
        y=df_plot.CUM_GAIN,
        line=dict(width=2,color="#3d825f"),
        line_shape='spline',
        name=name,
        mode='lines'
        ))
    fig.update_layout(width=1400,height=800,
        margin=dict(l=15,r=15,b=10),
        font=dict(size=10,color="#e1e1e1"),
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e",
        title=name)
    fig.update_xaxes(
        linewidth=1,
        linecolor='#3a4a54',
        showgrid=False,
        zeroline=False
    )
    fig.update_yaxes(
        linewidth=1,
        linecolor='#3a4a54',
        showgrid=False,
        zeroline=False
    )
  #  fig.show()

#plot_line(trades_cad_jpy,"CAD_JPY")
c = 'MA_8_16'
for p in our_pairs:
    temp_df = all_trades[(all_trades.CROSS==c)&(all_trades.PAIR==p)].copy()
    temp_df['CUM_GAIN'] = temp_df.GAIN.cumsum()
    plot_line(temp_df, p + "_" + c)

for c in crosses:
    temp_df = all_trades[(all_trades.CROSS==c)].copy()
    temp_df = temp_df.groupby(by="time", as_index=False).sum()
    temp_df['CUM_GAIN'] = temp_df.GAIN.cumsum()
    plot_line(temp_df, c)
#plot_line(trades_cad_jpy,"CAD_JPY")
#print(trades_cad_jpy.head())


print(df_good)

