import plotly.express as px
import pandas as pd
import pickle
import pdb
from safe_earth.utils.geometry_funcs import df2gdf
from typing import Union, List, Optional

# TODO: have custom yaxis ranges be pass-in-able as an argument

def subregions(metrics: Union[dict, List[dict]], show: bool = False, save_path: Optional[str] = None):

    if type(metrics) == dict:
        metrics = [metrics]
    if not type(metrics) == list:
        raise ValueError('Passed in argument must be a dictionary of metrics or a list of them')

    df = pd.DataFrame()
    for data in metrics:
        new_df = pd.DataFrame(data['subregion'])
        baseline = pd.DataFrame(data['baseline'])
        baseline['subregion'] = 'Baseline (all gridpoints)'
        df = pd.concat([df, new_df, baseline], ignore_index=True)

    fig = px.line(
        df,
        x='lead_time',
        y='rmse_weighted_l2',
        color='subregion',
        line_dash='subregion',
        symbol='subregion',
        facet_col='model',
        facet_row='variable',
        labels={
            'lead_time': 'lead time (hours)'
        },
    )

    # annotation_new_names = {
    #     'model=graphcast': 'GraphCast',
    #     'model=keisler': 'Keisler',
    #     'model=pangu': 'Pangu-Weather',
    #     'model=sphericalcnn': 'Spherical CNN',
    #     'model=fuxi': 'FuXi',
    #     'model=neuralgcm': 'NeuralGCM'
    # }
    # fig.for_each_annotation(lambda x: x.update(text = 
    #     annotation_new_names[x.text] if x.text in annotation_new_names else ''
    # ))
    # fig.update_yaxes(matches=None) # enables unique ranges
    # fig.layout.yaxis1.update(title_text='Per-strata RMSE (Z500)')
    # fig.layout.yaxis7.update(title_text='Per-strata RMSE (T850)')
    # for i in range(1, 13):
    #     if i < 7:
    #         fig.layout['yaxis'+str(i)].update(range=[-25, 1225])
    #     else:
    #         fig.layout['yaxis'+str(i)].update(range=[-0.25, 5.5])
    
    # fig.update_traces(line={'width': 0.5})

    # if show:
    #     fig.show()
    #     fig.write_image('../outputs/viz/viz_income.png', width=1200, height=500, scale=8)
    # else:
    #     return fig

    if show:
        fig.show()
    if save_path:
        fig.write_image(save_path)
    return fig

def incomes(metrics: Union[dict, List[dict]], show: bool = False, save_path: Optional[str] = None, lead_time_max = None):

    if type(metrics) == dict:
        metrics = [metrics]
    if not type(metrics) == list:
        raise ValueError('Passed in argument must be a dictionary of metrics or a list of them')

    df = pd.DataFrame()
    for data in metrics:
        new_df = pd.DataFrame(data['income'])
        baseline = pd.DataFrame(data['baseline'])
        baseline['income'] = 'Baseline (all gridpoints)'
        df = pd.concat([df, new_df, baseline], ignore_index=True)

    if lead_time_max:
        df = df[df['lead_time'] <= lead_time_max]

    fig = px.line(
        df,
        x='lead_time',
        y='rmse_weighted_l2',
        color='income',
        symbol='income',
        facet_col='model',
        facet_row='variable',
        labels={
            'lead_time': 'lead time (hours)'
        },
        category_orders={
            'income': ['High-income Countries', 'Upper-middle-income Countries', 'Lower-middle-income Countries', 'Low-income Countries', 'Baseline (all gridpoints)']
        }
    )
    
    # annotation_new_names = {
    #     'model=graphcast': 'GraphCast',
    #     'model=keisler': 'Keisler',
    #     'model=pangu': 'Pangu-Weather',
    #     'model=sphericalcnn': 'Spherical CNN',
    #     'model=fuxi': 'FuXi',
    #     'model=neuralgcm': 'NeuralGCM'
    # }
    # fig.for_each_annotation(lambda x: x.update(text = 
    #     annotation_new_names[x.text] if x.text in annotation_new_names else ''
    # ))
    # fig.update_yaxes(matches=None) # enables unique ranges
    # fig.layout.yaxis1.update(title_text='Per-strata RMSE (Z500)')
    # fig.layout.yaxis7.update(title_text='Per-strata RMSE (T850)')
    # if not lead_time_max:
    #     for i in range(1, 13):
    #         if i < 7:
    #             fig.layout['yaxis'+str(i)].update(range=[-25, 925])
    #         else:
    #             fig.layout['yaxis'+str(i)].update(range=[-0.25, 5.25])
    # else:
    #     fig.for_each_yaxis(lambda x: x.update(showticklabels=True))
    #     # fig.layout.facet_col_spacing=0.3

    # if show:
    #     fig.show()
    #     fig.write_image('../outputs/viz/viz_income.pdf', width=1200, height=500, scale=8)
    # else:
    #     return fig

    if show:
        fig.show()
    if save_path:
        fig.write_image(save_path)
    return fig
    
def territories(metrics: Union[dict, List[dict]], show: bool = False, save_path: Optional[str] = None):
    ''' If `save_path` is None, then it won't be saved, otherwise saved to specified filepath
    '''

    if type(metrics) == dict:
        metrics = [metrics]
    if not type(metrics) == list:
        raise ValueError('Passed in argument must be a dictionary of metrics or a list of them')

    df = pd.DataFrame()
    for data in metrics:
        new_df = pd.DataFrame(data['territory'])
        baseline = pd.DataFrame(data['baseline'])
        baseline['territory'] = 'Baseline (all gridpoints)'
        df = pd.concat([df, new_df, baseline], ignore_index=True)

    fig = px.line(
        df,
        x='lead_time',
        y='rmse_weighted_l2',
        color='territory',
        symbol='territory',
    )

    if show:
        fig.show()
    if save_path:
        fig.write_image(save_path)
    return fig

if __name__ == '__main__':
    # run with `python -m safe_earth.viz.viz_metrics` while inside src/
    data = []
    models = ['graphcast', 'keisler', 'pangu', 'sphericalcnn', 'fuxi', 'neuralgcm']
    resolution = '240x121'
    for model in models:
        with open(f'../outputs/metrics_{model}_{resolution}.pkl', 'rb') as f:
            metrics = pickle.load(f)
        data.append(metrics)
    incomes(data, show=True)
    # # incomes(data, show=True, lead_time_max=48)
    # subregions(data, show=True)
