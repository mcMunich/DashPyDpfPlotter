# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 13:24:07 2023

@author: mcapella
"""
import subprocess

moduleNames = ['ansys-dpf-core', 'easygui', 'dash', 'webbrowser'] 
for module in moduleNames:
    try: 
        __import__(module)
    except:
        subprocess.run('pip install '+ module)

from dash import Dash, dcc, html, Input, Output, callback
from ansys.dpf import core as dpf
import webbrowser, easygui


path1 = easygui.fileopenbox(msg="Choose a file", default=r"D:\PYANSYS\dpf\dpfComp\*.rst",filetypes='*.rst')

dashurl = 'http://127.0.0.1:8050/'
webbrowser.open(dashurl)
#path1 = r'D:\PYANSYS\dpf\dpfComp\file.rst'

def extPlotter(category,plottype, model, nset):
    """ Here we take the dash input and generate plot"""
    ntime = int(nset) + 1
    time_sets_scoping = dpf.time_freq_scoping_factory.scoping_by_sets([ntime])
    resOp = getattr(dpf.operators.result, plottype)(data_sources = model, time_scoping = time_sets_scoping)
    resOpFieldContainer = resOp.outputs.fields_container()[0]
    try: 
        openplot = model1.metadata.meshed_region.plot(resOpFieldContainer,text = category + ': ' + plottype + ' - Time Step : '  + str(ntime))
    except:
        print('That result is not available.')
        openplot = ''
    return openplot


model1 = dpf.Model(path1)
print(model1)
metadata1 = model1.metadata

resultsSets1 = model1.metadata.time_freq_support.n_sets

resultSetList = [str(i) for i in range(resultsSets1)]

results1 = [i.name for i in  metadata1.result_info.available_results]
fullList = dir(dpf.operators.result)
resultDict = {}
for resultkey in results1:
    resultDict[resultkey] = [i for i in fullList if resultkey in i and 'compute' not in i]

plot = ['N','Y']    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

all_options = resultDict

app.layout = html.Div([
    dcc.Markdown('''
    ### Choose a result type:
    '''),
    dcc.RadioItems(
        list(all_options.keys()),
        list(all_options.keys())[0],
        id = 'result_category',
    ),
    html.Hr(),
    dcc.Markdown('''
    ### Choose a plot type:
    '''),
    dcc.RadioItems(id='plot_type'),
    html.Hr(),
    dcc.Markdown('''
    ### Choose a time step:
    '''),
    dcc.RadioItems(
        resultSetList,
        resultSetList[0],
        inline = True,
        id='time_set',
        ),
    html.Hr(),
    dcc.Markdown('''
    ### Plot result?:
    '''),
    dcc.RadioItems(
        plot,
        plot[0],
        inline = True,
        id='plot_command',
        ),
    html.Hr(),
    html.Div(id='display-selected-values'),
])


@callback(
    Output('plot_type', 'options'),
    Input('result_category', 'value'))
def set_result_options(result_type):
    return [{'label': i, 'value': i} for i in all_options[result_type]]

@callback(
    Output('plot_type', 'value'),
    Input('plot_type', 'options'))
def set_plot_value(available_options):
    #print(available_options[0]['value'])
    return available_options[0]['value']

@callback(
    Output('time_set', 'value'),
    Input('time_set', 'options'))
def set_nset_value(resultSetList):
    return resultSetList[0]

@callback(
    Output('plot_command', 'value'),
    Input('plot_command', 'options'))
def get_plot_command(plot):
    return plot[0]

@callback(
    Output('display-selected-values', 'children'),
    Input('result_category', 'value'),
    Input('plot_type', 'value'),
    Input('time_set', 'value'),
    Input('plot_command', 'value'),
    )
def set_display_children(category, plottype,nset,to_plot):
    #
    if to_plot == 'Y':
         openplot = extPlotter(category,plottype,model1,nset)
         if openplot == ():
            return f'Will try to plot {plottype} load step {nset} from  {category}'

if __name__ == '__main__':
    app.run(debug=False)