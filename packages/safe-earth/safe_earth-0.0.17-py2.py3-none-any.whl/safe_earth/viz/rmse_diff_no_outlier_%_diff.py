import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import pickle
import pdb
from scipy import stats

df = pd.DataFrame()
models = ['graphcast', 'keisler', 'pangu', 'sphericalcnn', 'fuxi', 'neuralgcm']
newnames = {'graphcast':'GraphCast', 'keisler': 'Keisler (2022)', 'pangu': 'Pangu-Weather', 'sphericalcnn': 'Spherical CNN', 'fuxi': 'FuXi', 'neuralgcm': 'NeuralGCM'}
lead_times = [x for x in range(12, 241, 12)]
categories = ['territory', 'subregion', 'income']

for model in models:
    with open(f'outputs/metrics_{model}_240x121.pkl', 'rb') as f:
        metrics = pickle.load(f)
    
    for category in categories:
        data = metrics[category]
        for lead_time in lead_times:
            sliced_data = data[data['variable']=='T850'][data['lead_time']==lead_time]['rmse_weighted_l2']
            zscores = np.abs(stats.zscore(sliced_data))
            sliced_data = sliced_data[zscores<2]
            tmax = np.max(sliced_data)
            tmin = np.min(sliced_data)
            df = pd.concat([df, pd.DataFrame([{'model': model, 'lead_time': lead_time, 'variable': 'T850', 'rmse_diff': tmax-tmin, 'rmse_%_diff': tmax/tmin, 'stratum': category, 'outliers': 'no'}])], ignore_index=True)
            tmax = np.max(data[data['variable']=='T850'][data['lead_time']==lead_time]['rmse_weighted_l2'])
            tmin = np.min(data[data['variable']=='T850'][data['lead_time']==lead_time]['rmse_weighted_l2'])
            df = pd.concat([df, pd.DataFrame([{'model': model, 'lead_time': lead_time, 'variable': 'T850', 'rmse_diff': tmax-tmin, 'rmse_%_diff': tmax/tmin, 'stratum': category, 'outliers': 'yes'}])], ignore_index=True)
            
            sliced_data = data[data['variable']=='Z500'][data['lead_time']==lead_time]['rmse_weighted_l2']
            zscores = np.abs(stats.zscore(sliced_data))
            sliced_data = sliced_data[zscores<2]
            zmax = np.max(sliced_data)
            zmin = np.min(sliced_data)
            df = pd.concat([df, pd.DataFrame([{'model': model, 'lead_time': lead_time, 'variable': 'Z500', 'rmse_diff': zmax-zmin, 'rmse_%_diff': zmax/zmin, 'stratum': category, 'outliers': 'no'}])], ignore_index=True)
            zmax = np.max(data[data['variable']=='Z500'][data['lead_time']==lead_time]['rmse_weighted_l2'])
            zmin = np.min(data[data['variable']=='Z500'][data['lead_time']==lead_time]['rmse_weighted_l2'])
            df = pd.concat([df, pd.DataFrame([{'model': model, 'lead_time': lead_time, 'variable': 'Z500', 'rmse_diff': zmax-zmin, 'rmse_%_diff': zmax/zmin, 'stratum': category, 'outliers': 'yes'}])], ignore_index=True)


fig_T850 = px.line(
    df[df['variable']=='T850'],
    x='lead_time',
    y='rmse_%_diff',
    color='outliers',
    facet_col='stratum',
    facet_col_spacing=0.03,
    facet_row='model',
    labels={
        'lead_time': 'lead time (hours)',
        'rmse_%_diff': 'Highest RMSE as % of Lowest RMSE (T850)'
    }
)
# fig_T850.for_each_trace(lambda t: t.update(name = newnames[t.name],
#     legendgroup = newnames[t.name],
#     hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
#     )
# )
fig_T850.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
fig_T850.update_xaxes(tickmode = 'array', tickvals = lead_times)
fig_T850.update_yaxes(matches=None)
fig_T850.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, range=[0.9,9]))
for i in range(3, 19, 3):
    fig_T850.layout['yaxis'+str(i)].update(showticklabels=True, range=[0.9,2.5])
for i in range(1, 19, 1):
    if not i == 7:
        fig_T850.layout['yaxis'+str(i)].update(title_text='')
fig_T850.show()
fig_T850.write_image('outputs/viz/rmse_diff_t850_no_outliers_%_diff.png', width=1200, height=500, scale=8)

fig_Z500 = px.line(
    df[df['variable']=='Z500'],
    x='lead_time',
    y='rmse_%_diff',
    color='outliers',
    facet_col='stratum',
    facet_col_spacing=0.03,
    facet_row='model',
    labels={
        'lead_time': 'lead time (hours)',
        'rmse_%_diff': 'Highest RMSE as % of Lowest RMSE (Z500)'
    }
)
# fig_Z500.for_each_trace(lambda t: t.update(name = newnames[t.name],
#     legendgroup = newnames[t.name],
#     hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
#     )
# )
fig_Z500.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
fig_Z500.update_xaxes(tickmode = 'array', tickvals = lead_times)
fig_Z500.update_yaxes(matches=None)
fig_Z500.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, range=[0.9,18]))
for i in range(3, 19, 3):
    fig_Z500.layout['yaxis'+str(i)].update(showticklabels=True, range=[0.9,6])
for i in range(1, 19, 1):
    if not i == 7:
        fig_Z500.layout['yaxis'+str(i)].update(title_text='')
fig_Z500.show()
fig_Z500.write_image('outputs/viz/rmse_diff_z500_no_outliers_%_diff.png', width=1200, height=500, scale=8)

