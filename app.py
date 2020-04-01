import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import numpy as np

todaydate = datetime.today().strftime('%Y-%m-%d')
last14days = pd.to_datetime(todaydate, format="%Y-%m-%d") - pd.DateOffset(days=14)
last28days = pd.to_datetime(todaydate, format="%Y-%m-%d") - pd.DateOffset(days=28)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

df1 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")

d = df1.drop(["Province/State","Lat","Long"],axis=1)
d = d.groupby(["Country/Region"]).sum().T.reset_index()
d = d.set_index(pd.to_datetime(d["index"]))
d = d.drop(["index"],axis=1)

dd = {}

for country in d.columns:
    dd[country] = pd.DataFrame(d[country])
    dd[country].columns = ["Infections"]


df1 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

d = df1.drop(["Province/State","Lat","Long"],axis=1)
d = d.groupby(["Country/Region"]).sum().T.reset_index()
d = d.set_index(pd.to_datetime(d["index"]))
d = d.drop(["index"],axis=1)



for c in d.columns:
    #current data frame = dataframe[country]
    cdf = pd.DataFrame(d[c])
    cdf.columns = ["Deaths"]
    dd[c] = dd[c].join(cdf,how="outer")
    

for key in dd:
    cdf = dd[key]
    cdf["Infections diff abs"] = cdf["Infections"].diff()
    cdf["Infections diff %"] = cdf["Infections"].pct_change()*100
    cdf["Infections diff %"] = cdf["Infections diff %"].round(2)
    
    cdf["Deaths diff abs"] = cdf["Deaths"].diff()
    cdf["Deaths diff %"] = cdf["Deaths"].pct_change()*100
    cdf["Deaths diff %"] = cdf["Deaths diff %"].round(2)    

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def generate_table(dataframe, max_rows=10000):
    dataframe = dataframe.sort_index(ascending=False)
    dataframe = dataframe.reset_index()
    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.Div([
        html.H2(children='COVID19 - Custom Dashboard'),
    
        #html.Div(children='''
        #    Dash: A web application framework for Python!
        #'''),
        
        html.Div([
            html.Span('Choose Country',style={'font-weight':'bold'}),
            dcc.Dropdown(
                id='drop-countries',
                options=[{'label':i, 'value': i} for i in dd.keys()],
                value="Germany",
            ),
        ],style={'width': '20%', 'margin': 'auto','margin-bottom':'20px'}),
        
        html.Div([
            html.Span('Measures',style={'font-weight':'bold'}),
            dcc.Dropdown(
                id='val-slider',
                options=[{'label':i, 'value': i} for i in ['Infections','Deaths']],
                value="Infections",
            ),
            html.Span('Y-Axis Scale',style={'font-weight':'bold'}),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='timeseries'),
        ],style={'width': '60%','margin':'auto'}),
        
        html.Div([
            html.Span('Scale',style={'font-weight':'bold'}),
            dcc.RadioItems(
                id='diffscale',
                options=[{'label': i, 'value': i} for i in ['absolute', 'percentage']],
                value='absolute',
                labelStyle={'display': 'inline-block'}
            )
        ],style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='diffdata'),
        ],style={'width': '60%','margin':'auto'}),
        
        html.Div([
        ],style={'margin':'auto', 'text-align':'center','width':'48%'},id='tabelle'),
            
        
    ],style={'margin': 'auto','text-align':'center'})
])

@app.callback(
    Output('timeseries','figure'),
    [Input('val-slider','value'),
     Input('yaxis-type','value'),
     Input('drop-countries','value')])
def update_figure(selected_value, yaxis_type, country_val):
    df_ger = dd[country_val]
    return {
        'data': [
            { 'x': df_ger.index, 'y': [x[0] for x in df_ger[[selected_value]].values.tolist()], 'type':'scatter','name':'pad'},
        ],
        'layout': {
            #'plot_bgcolor': colors['background'],
            #'paper_bgcolor': colors['background'],
            #'font': {
            #    'color': colors['text']
            #},
            'yaxis': {
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            'title': {
                'text': 'Timeline '+selected_value+' of '+country_val,
            },
        }
    }

@app.callback(
    Output('diffdata','figure'),
    [Input('diffscale','value'),
     Input('drop-countries','value')])
def update_diffs(vala,country_val):
    df_ger = dd[country_val]
    df2 = df_ger
    df2 = df2[last28days:]
    
    if vala == "absolute":
        df2 = df2[["Infections diff abs"]]
    else:
        df2 = df2[["Infections diff %"]]
    
    return {
        'data': [
            { 'x': df2.index, 'y': [x[0] for x in df2.values.tolist()], 'type':'bar','name':'pad'},
        ],
        'layout': {
            'title': {
                'text': 'Infections difference to prior day in '+country_val,
            },
        }
    }
 
@app.callback(
    Output('tabelle','children'),
    [Input('drop-countries','value')])
def update_table(country_val):
    df_ger = dd[country_val]
    return generate_table(df_ger[last14days:]),

if __name__ == '__main__':
    app.run_server(debug=True)