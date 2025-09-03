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
            df = pd.concat([df, pd.DataFrame([{'model': model, 'lead_time': lead_time, 'variable': 'T850', 'rmse_diff': tmax-tmin, 'stratum': category}])], ignore_index=True)
            
            sliced_data = data[data['variable']=='Z500'][data['lead_time']==lead_time]['rmse_weighted_l2']
            zscores = np.abs(stats.zscore(sliced_data))
            sliced_data = sliced_data[zscores<2]
            zmax = np.max(sliced_data)
            zmin = np.min(sliced_data)
            df = pd.concat([df, pd.DataFrame([{'model': model, 'lead_time': lead_time, 'variable': 'Z500', 'rmse_diff': zmax-zmin, 'stratum': category}])], ignore_index=True)

fig_T850 = px.line(
    df[df['variable']=='T850'],
    x='lead_time',
    y='rmse_diff',
    color='model',
    symbol='model',
    facet_col='stratum',
    facet_col_spacing=0.08,
    labels={
        'lead_time': 'lead time (hours)',
        'rmse_diff': 'Greatest Absolute Difference in RMSE (T850)'
    }
)
fig_T850.for_each_trace(lambda t: t.update(name = newnames[t.name],
    legendgroup = newnames[t.name],
    hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
    )
)
fig_T850.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
fig_T850.update_xaxes(tickmode = 'array', tickvals = lead_times)
fig_T850.update_yaxes(matches=None)
fig_T850.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, range=[-0.05,5.15]))
fig_T850.show()
fig_T850.write_image('outputs/viz/rmse_diff_t850_no_outliers.png', width=1200, height=500, scale=8)

fig_Z500 = px.line(
    df[df['variable']=='Z500'],
    x='lead_time',
    y='rmse_diff',
    color='model',
    symbol='model',
    facet_col='stratum',
    facet_col_spacing=0.08,
    labels={
        'lead_time': 'lead time (hours)',
        'rmse_diff': 'Greatest Absolute Difference in RMSE (Z500)'
    }
)
fig_Z500.for_each_trace(lambda t: t.update(name = newnames[t.name],
    legendgroup = newnames[t.name],
    hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
    )
)
fig_Z500.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
fig_Z500.update_xaxes(tickmode = 'array', tickvals = lead_times)
fig_Z500.update_yaxes(matches=None)
fig_Z500.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, range=[-10,1410]))
fig_Z500.show()
fig_Z500.write_image('outputs/viz/rmse_diff_z500_no_outliers.png', width=1200, height=500, scale=8)

