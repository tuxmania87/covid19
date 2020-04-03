import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import numpy as np


def create_multi_df(ddf,country_val,measure,dayfilter=True):
    dftotal = None
    
    
    for country in country_val:
        dfc = ddf[country]
        if dayfilter:
            dfc = dfc[last28days:]
        
        dfc = dfc[[measure]]
        dfc.columns = [measure+"_"+country]
        
        if dftotal is None:
            dftotal = dfc
        else:
            dftotal = dftotal.join(dfc,how="outer",rsuffix="_"+country)

    return dftotal

def generate_data(df,countries,measure,kind="bar"):
    return [ dict(x = df.index, y= [xx for xx in df[measure+"_"+c].values.tolist()], type=kind,name=c) for c in countries]


todaydate = datetime.today().strftime('%Y-%m-%d')
last14days = pd.to_datetime(todaydate, format="%Y-%m-%d") - pd.DateOffset(days=14)
last28days = pd.to_datetime(todaydate, format="%Y-%m-%d") - pd.DateOffset(days=28)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

df1 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")

dfus = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")


d = df1.drop(["Province/State","Lat","Long"],axis=1)

dworld = d.copy()
dworld = dworld.drop(["Country/Region"],axis=1).sum()
dworld = pd.DataFrame(dworld)
dworld.columns = [ "World" ]
dworld.index = pd.to_datetime(dworld.index)


d = d.groupby(["Country/Region"]).sum().T.reset_index()
d = d.set_index(pd.to_datetime(d["index"]))
d = d.drop(["index"],axis=1)

dfus = dfus.drop(["UID","iso2","iso3","code3","FIPS","Admin2","Lat","Long_","Combined_Key"],axis=1)
dfus = dfus.groupby(["Country_Region"]).sum().T.reset_index()
dfus = dfus.set_index(pd.to_datetime(dfus["index"]))
dfus = dfus.drop(["index"],axis=1)

#d = d.join(dfus,how="outer")


dd = {}

for country in d.columns:
    c2 = "United States" if country == "US" else country 
    dd[c2] = pd.DataFrame(d[country])
    dd[c2].columns = ["Infections"]

dd["World"] = dworld 
dd["World"].columns = ["Infections"]

df1 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

dfus = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv")

d = df1.drop(["Province/State","Lat","Long"],axis=1)

dworld = d.copy()
dworld = dworld.drop(["Country/Region"],axis=1).sum()
dworld = pd.DataFrame(dworld)
dworld.columns = [ "World" ]
dworld.index = pd.to_datetime(dworld.index)

d = d.groupby(["Country/Region"]).sum().T.reset_index()
d = d.set_index(pd.to_datetime(d["index"]))
d = d.drop(["index"],axis=1)



#dfus = dfus.drop(["UID","iso2","iso3","code3","FIPS","Admin2","Lat","Long_","Combined_Key","Population","Province/State"],axis=1)
#dfus = dfus.groupby(["Country/Region"]).sum().T.reset_index()
#dfus = dfus.set_index(pd.to_datetime(dfus["index"]))
#dfus = dfus.drop(["index"],axis=1)

#d = d.join(dfus,how="outer")

for c in d.columns:
    #current data frame = dataframe[country]
    cdf = pd.DataFrame(d[c])
    cdf.columns = ["Deaths"]
    c2 = "United States" if c == "US" else c 
    dd[c2] = dd[c2].join(cdf,how="outer")
    
dworld.columns = ["Deaths"]
dd["World"] = dd["World"].join(dworld,how="outer")
    
df1 =  pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

d = df1.drop(["Province/State","Lat","Long"],axis=1)

dworld = d.copy()
dworld = dworld.drop(["Country/Region"],axis=1).sum()
dworld = pd.DataFrame(dworld)
dworld.columns = [ "World" ]
dworld.index = pd.to_datetime(dworld.index)

d = d.groupby(["Country/Region"]).sum().T.reset_index()
d = d.set_index(pd.to_datetime(d["index"]))
d = d.drop(["index"],axis=1)

for c in d.columns:
    #current data frame = dataframe[country]
    cdf = pd.DataFrame(d[c])
    cdf.columns = ["Recovery"]
    c2 = "United States" if c == "US" else c 
    dd[c2] = dd[c2].join(cdf,how="outer")

dworld.columns = ["Recovery"]
dd["World"] = dd["World"].join(dworld,how="outer")

for key in dd:
    cdf = dd[key]
    cdf["Infections diff abs"] = cdf["Infections"].diff()
    cdf["Infections diff %"] = cdf["Infections"].pct_change()*100
    cdf["Infections diff %"] = cdf["Infections diff %"].round(2)
    
    cdf["Deaths diff abs"] = cdf["Deaths"].diff()
    cdf["Deaths diff %"] = cdf["Deaths"].pct_change()*100
    cdf["Deaths diff %"] = cdf["Deaths diff %"].round(2)    
    
    cdf["Current Infections"] = cdf["Infections"] - cdf["Recovery"]
    
    cdf["Current Infections diff abs"] = cdf["Current Infections"].diff()
    cdf["Current Infections diff %"] = cdf["Current Infections"].pct_change()*100
    cdf["Current Infections diff %"] = cdf["Current Infections diff %"].round(2)  

    cdf = cdf[["Infections","Infections diff abs","Infections diff %","Deaths","Deaths diff abs","Deaths diff %","Recovery","Current Infections","Current Infections diff abs","Current Infections diff %"]]
    
    dd[key] = cdf

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets=[dbc.themes.BOOTSTRAP]

def style_callback(colname):
    if colname == "index":
        return { 'border-right':'2px solid black','width':'9%' }
    elif "Recovery" in colname or "%" in colname:
        return { 'border-right':'2px solid black' }

def generate_table(dataframe, max_rows=10000):
    dataframe = dataframe.sort_index(ascending=False)
    dataframe = dataframe.reset_index()
    dataframe["index"] = dataframe["index"].astype(str).str[:10]
    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col,style= style_callback(col) ) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col], style= {'border-right':'2px solid black'} if "%" in col or "Recovery" in col or "index" in col else {}) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ],className='table')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(className='container',children=[
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
            multi=True,
        ),
    ],style={'width': '20%', 'margin': 'auto','margin-bottom':'20px'}),
    
    html.Div([
        html.Span('Measures',style={'font-weight':'bold'}),
        dcc.Dropdown(
            id='val-slider',
            options=[{'label':i, 'value': i} for i in ['Infections','Deaths', 'Recovery', 'Current Infections']],
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
    #],style={'width': '60%','margin':'auto'}),
    ],className="container"),
    
    html.Div([
        html.Span('Scale',style={'font-weight':'bold'}),
        dcc.RadioItems(
            id='diffscale',
            options=[{'label': i, 'value': i} for i in ['absolute', 'percentage']],
            value='absolute',
            labelStyle={'display': 'inline-block'}
        )
    #],style={'width': '48%', 'display': 'inline-block'}),
    ],className="container"),
    
    
    html.Div([
        dcc.Graph(id='diffdata'),
    ],className="container"),
    
    html.Span('Detailed data of last 14 days of first selected country',
        style={'font-weight':'bold'}),
    html.Div([
    ],id='tabelle',className='table-responsive'),
        
    html.Div([
        html.A("Data Source: https://github.com/CSSEGISandData/COVID-19",href="https://github.com/CSSEGISandData/COVID-19")
    ],className="container",style={ 'margin-bottom':'20px'})
    
],style={'margin': 'auto','text-align':'center'})


@app.callback(
    Output('timeseries','figure'),
    [Input('val-slider','value'),
     Input('yaxis-type','value'),
     Input('drop-countries','value')])
def update_figure(selected_value, yaxis_type, country_val):

    if not isinstance(country_val, list):
        country_val = [ country_val ]
    
    df_ger = create_multi_df(dd,country_val,selected_value,False)
    return {
        'data': generate_data(df_ger,country_val,selected_value,"scatter"),
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
                'text': 'Timeline '+selected_value+' of '+ (",".join(country_val)),
            },
        }
    }

@app.callback(
    Output('diffdata','figure'),
    [Input('diffscale','value'),
     Input('drop-countries','value'),
     Input('val-slider','value')])
def update_diffs(vala,country_val,selected_value):

    measure = selected_value+" diff " + ("abs" if vala == "absolute" else "%")
    if selected_value == "Recovery":
        measure = "Infections diff " + ("abs" if vala == "absolute" else "%")
    
    if not isinstance(country_val, list):
        country_val = [ country_val ]
    
    dftotal = create_multi_df(dd,country_val,measure)

    df_ger = dftotal
    df2 = df_ger
    df2 = df2[last28days:]
    
    
    return {
        'data': generate_data(df2, country_val, measure),
        #'data': [
        #    { 'x': df2.index, 'y': [x[0] for x in df2.values.tolist()], 'type':'bar','name':'pad'},
        #],
        'layout': {
            'title': {
                'text': selected_value+' difference to prior day in '+ (",".join(country_val)),
            },
        }
    }
 
@app.callback(
    Output('tabelle','children'),
    [Input('drop-countries','value')])
def update_table(country_val):

    if not isinstance(country_val,list):
        country_val = [ country_val ]


    df_ger = dd[country_val[0]]
    return generate_table(df_ger[last14days:]),

if __name__ == '__main__':
    app.run_server(debug=True)
