import dash
from dash import html, dcc
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import random
import pandas as pd
from datetime import datetime
import gen_key
import gtts
import base64
url_secret=gen_key.url_secret
print("pressure.py url:",gen_key.url_secret[0])
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import GCP_class

dash.register_page(__name__,path='/pressure')
bucket_name = "ee4002d_bucket"
jsonfile = "cred_details.json"
server = GCP_class.Server(bucket_name, jsonfile)

item = 'microphone_false'
key="S129793.02-123"
direc = server.get_directory(key, item)
data_mp3 = server.download_as_bytes(direc)

global audio_base64
audio_base64 = base64.b64encode(data_mp3).decode('ascii')


df = pd.DataFrame(
    {
        "Tile no": ["Pressure tile 1", "Pressure tile 2", "Pressure tile 3"],
        "Weight reading(kg)": [1,2,3],
        "Delta reading(kg/s)":[0,0,0,]
    }
)

def plotly_pressuregraph():


    fig = make_subplots(rows=2, cols=1,subplot_titles=("Pressure graph","Delta pressure graph"))

    fig.add_trace(go.Scatter(
        y=[0, 0],
        x=[0, 0],

        mode='lines',
        marker=dict(
            size=3,
            colorscale='Viridis',  # choose a colorscale
            opacity=0.8
        ),

        name="Tile 1"), row=1, col=1

    )

    fig.add_trace(go.Scatter(
        y=[0,0],
        x=[0,0],

        mode='lines',
        marker=dict(
            size=3,
            colorscale='Viridis',  # choose a colorscale
            opacity=0.8
        ),

    name="Tile 2"), row=1, col=1

    )

    fig.add_trace(go.Scatter(
        y=[0,0],
        x=[0,0],

        mode='lines',
        marker=dict(
            size=3,
            colorscale='Viridis',  # choose a colorscale
            opacity=0.8
        ),

    name="Tile 3"), row=1, col=1

    )


    fig.add_trace(go.Scatter(
        y=[0, 0],
        x=[0, 0],

        mode='lines',
        marker=dict(
            size=3,
            colorscale='Viridis',  # choose a colorscale
            opacity=0.8
        ),

        name="delta Tile 1"), row=2, col=1

    )

    fig.add_trace(go.Scatter(
        y=[0, 0],
        x=[0, 0],

        mode='lines',
        marker=dict(
            size=3,
            colorscale='Viridis',  # choose a colorscale
            opacity=0.8
        ),

        name="delta Tile 2"), row=2, col=1

    )

    fig.add_trace(go.Scatter(
        y=[0, 0],
        x=[0, 0],

        mode='lines',
        marker=dict(
            size=3,
            colorscale='Viridis',  # choose a colorscale
            opacity=0.8
        ),

        name="delta Tile 3"), row=2, col=1

    )
    #fig.add_vrect(x0=5.123, x1=6,
     #             annotation_text="decline", annotation_position="top left",
      #           fillcolor="green", opacity=0.25, line_width=0)


    print(fig.data[0].y,type(fig.data[0].y))

    fig.update_xaxes(nticks=20)
    fig.update_layout(height=600,template="plotly_dark",legend_tracegroupgap=40)
    fig.update_xaxes(title_text="Seconds(s)")
    fig.update_yaxes(title_text="Weight(Kg)",range=[0,120])

    return fig


layout = html.Div(children=[
dcc.Location(id='url-pressure', refresh=False),
    dcc.Store(id="pressure-storage"),
    dcc.Download(id="download"),
    dcc.Interval(
        id='pressure-interval',
        interval=1 * 50, n_intervals=0
    ),
    dcc.Interval(id='5-sec-interval',
                 interval=1 * 5000, n_intervals=0),

    dbc.Row(children=[#dbc.Col("",width=1),
                      dbc.Col(children=[dbc.Button("Back to dashboard",href=gen_key.DASH_URL_BASE+'dashboard', color="primary",outline=True,size='sm'),
                                        html.H1(children='Pressure & Mic Sensor', className="display-3")]
                              )]
            )
,

 dbc.Row(children=[#dbc.Col("",width=1),
    dbc.Col(dbc.Card(dbc.CardBody([dbc.Col(children=
             [

                html.H5("Sensor type: StrainGauge", className="card-title",id='sensor-pressure-header'),
                html.Hr(className="my-2"),
                html.Br(),
                html.Br(),
                dbc.Row(children=

                [
                    dbc.Col(children=[
                    html.P("Sensor Status:"),

                    html.P("Transmission Status:"),
                   # html.P("Average time of reading:"),
                    html.P("Pressure Tile fall result:"),

                    ]),
                    dbc.Col(children=[
                        html.P([dbc.Badge("Healthy", color="success", className="me-1")]),
                        html.P([dbc.Badge("Transmitting", color="success", className="me-1")]),
                      #  html.P("1 sec"),
                        html.P([dbc.Badge("Transmitting",id="pressure-result-text", color="success", className="me-1")]),





                    ])
                ]#sensor transmission and


                        ),#row for sensor transmission and on

                 #  html.P("Manual overide"),
                dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True,id="pressure_table"),
                 html.Span("Last updated: ", id="pressure update time", style={"verticalAlign": "right"}),
                html.P(' '),
                 html.H5("Audio recordings:", className="card-title", ),
html.Hr(className="my-2"),
                 dbc.Row(children=

                 [
                     dbc.Col(children=[
                         html.P("Microphone Status:"),


                     ]),
                     dbc.Col(children=[
                         html.P([dbc.Badge("Disabled", color="success", className="me-1",id='mic-cmd')]),

                     ])
                 ]),




                html.Audio(src='',controls=True,id='audio-pressure'),
                 html.P('',id='audio-time')


             ]

    )
     ])#,style={"width": "40rem"}
    )#,width=5
    )#card component
     ,
     dbc.Col(children=[
         html.H5("Live Pressure Data Feed")
,
         dcc.Graph(
             id='pressure-graph',
             figure=plotly_pressuregraph(),
            style={
                 #\ 'height': 100,
                #  'width': 1200,
                  "display": "block",
                  "margin-left": "auto",
                  "margin-right": "auto",
              }
         )#dcc.graph
         ,
     ]#,width=5

     )

]#end of row items
,justify='center' )
])

temp_pressure_data=[["0","0","0","0"]]
temp_pressure_time=[]
@callback(
    Output(component_id='pressure_table', component_property='children'),
    Output(component_id='pressure update time', component_property='children'),
    Output(component_id='pressure-storage', component_property='data'),
    Output(component_id='pressure-graph', component_property='figure'),
    Input(component_id='pressure-interval', component_property='n_intervals'),
    Input(component_id='pressure-storage', component_property='data'),
    State(component_id='pressure-graph', component_property='figure'),
    State(component_id='pressure-gcp', component_property='data'),


)
def update_pressure_data(n_click,prevr,graph_data,whole_data):
    #print(graph_data["data"][0]["y"],graph_data["data"][0]["x"],graph_data["data"][0]["name"])
    row_data=temp_pressure_data[0]
    n_click=n_click/20
    check_row=''.join(row_data)
    prevr = prevr or {"pr1":0,"pr2":0,"pr3":0,'fall':0,'fall_display':False}

    #print(row_data)
    #print(type(graph_data),graph_data['layout']['annotations'])
    #graph_data['layout']['shapes']
    if check_row.isalpha() or len(row_data)<4:
        r1 = prevr["pr1"]
        r2 = prevr["pr2"]
        r3 = prevr["pr3"]
    else:
        r1 = row_data[1] if 1<len(row_data) else prevr["pr1"]
        r2 = row_data[2] if 2<len(row_data) else prevr["pr2"]
        r3 = row_data[3] if 3<len(row_data) else prevr["pr3"]
    #print("row data:",r1,r2,r3,"temp left:",len(temp_pressure_data))
    if len(temp_pressure_data)>1:
        temp_pressure_data.pop(0)


    trigger_display=5

    #['22:31:35', ' Fall detected']

    #if n_click%trigger_display==0:
    if ' Fall detected' in row_data:
        print('Entring add_vrect at n_click:',n_click)
        graph_data=add_vrect(graph_data,n_click)
        #print(graph_data['layout']['shapes'])
        #print(graph_data['layout']['annotations'])
        prevr['fall']=n_click
        prevr['fall_display'] = True

    #Update graphs
    graph_data["data"][0]["y"].append(float(r1))
    graph_data["data"][0]["x"].append(n_click)
    graph_data["data"][1]["y"].append(float(r2))
    graph_data["data"][1]["x"].append(n_click)
    graph_data["data"][2]["y"].append(float(r3))
    graph_data["data"][2]["x"].append(n_click)

    graph_data["data"][3]["y"].append(float(r1)-prevr['pr1'])
    graph_data["data"][3]["x"].append(n_click)
    graph_data["data"][4]["y"].append(float(r2)-prevr['pr2'])
    graph_data["data"][4]["x"].append(n_click)
    graph_data["data"][5]["y"].append(float(r3)-prevr['pr3'])
    graph_data["data"][5]["x"].append(n_click)

    GRAPH_PERIOD=50
    if n_click-GRAPH_PERIOD>prevr['fall']-1 and prevr['fall_display']:
        prevr['fall_display']=False
        graph_data=remove_vrect(graph_data)

    if n_click>GRAPH_PERIOD:
        graph_data["data"][0]["y"].pop(0)
        graph_data["data"][0]["x"].pop(0)
        graph_data["data"][1]["y"].pop(0)
        graph_data["data"][1]["x"].pop(0)
        graph_data["data"][2]["y"].pop(0)
        graph_data["data"][2]["x"].pop(0)
        graph_data["data"][3]["y"].pop(0)
        graph_data["data"][3]["x"].pop(0)
        graph_data["data"][4]["y"].pop(0)
        graph_data["data"][4]["x"].pop(0)
        graph_data["data"][5]["y"].pop(0)
        graph_data["data"][5]["x"].pop(0)


    df = pd.DataFrame(
        {
            "Tile no": ["Pressure tile 1", "Pressure tile 2", "Pressure tile 3" ],
            "Pressure": [r1, r2, r3],
            "Delta": [str(round(float(r1)-prevr["pr1"],3)), str(round(float(r2)-prevr["pr2"],3)), str(round(float(r3)-prevr["pr3"],3))],

        })

   #@ print(df.to_dict())
    prevr["pr1"] = float(r1)
    prevr["pr2"] = float(r2)
    prevr["pr3"] = float(r3)

    #return df.to_dict('records')

    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True),"Last updated: "+"".join(temp_pressure_time)+" Event count: "+str(n_click),prevr,graph_data


#add trace vrect
def add_vrect(graph,x_value):
    #1. settle the shapes first in graph_data['layout']['shapes']

    shape_item= [{'fillcolor': 'red', 'line': {'width': 0}, 'opacity': 0.25, 'type': 'rect', 'x0': x_value-2, 'x1': x_value, 'xref': 'x', 'y0': 0, 'y1': 1, 'yref': 'y domain'},
                     {'fillcolor': 'red', 'line': {'width': 0}, 'opacity': 0.25, 'type': 'rect', 'x0': x_value-2, 'x1': x_value, 'xref': 'x2', 'y0': 0, 'y1': 1, 'yref': 'y2 domain'}]
    graph['layout']['shapes']=shape_item

    #declaring annotations for  graph['layout']['annotations']
    ann1={'showarrow': False, 'text': 'Fall detected', 'x': x_value-1, 'xanchor': 'center', 'xref': 'x', 'y': 1, 'yanchor': 'top', 'yref': 'y domain'}
    ann2={'showarrow': False, 'text': 'Fall detected', 'x': x_value-1, 'xanchor': 'center', 'xref': 'x2', 'y': 1, 'yanchor': 'top', 'yref': 'y2 domain'}


    #checking if annotations are present
    if len(graph['layout']['annotations'])<4:

        graph['layout']['annotations'].append(ann1)
        graph['layout']['annotations'].append(ann2)
    else:
        graph['layout']['annotations'][-1] = ann1
        graph['layout']['annotations'][-2] = ann2





    return graph

def remove_vrect(graph):
    graph['layout'].pop('shapes')
    graph['layout']['annotations'].pop(-1)
    graph['layout']['annotations'].pop(-1)
    return graph



@callback(
    Output(component_id='pressure-gcp', component_property='data'),
    Input(component_id='5-sec-interval', component_property='n_intervals'),
    State(component_id="main-storage",component_property="data")  ,
    State(component_id='pressure-gcp', component_property='data'),
)
def retrieve_pressure_file(n_click,key,pressure_data):
    try:
        if key is None:
            return None
        item = "pressure_data"
        direc = server.get_directory(key, item)
        data = server.retrieve_file_string(direc)


        #print("Printing data:",data)
        ver1=data.split('\n')
        p_data=[i.split(",") for i in ver1 if len(i) > 1]

        #retrieve time details
        details = server.file_details(direc)

        # update to singapore time
        time_updated = details[-1] + timedelta(hours=8)
        # convert to format d/m/y h:m:s
        time_updated = time_updated.strftime("%d/%m/%Y, %H:%M:%S")


        if not pressure_data== p_data[0]:
            now = datetime.now()
            dt_string = time_updated
            print("Receiving new input! Time: ",dt_string)
            temp_pressure_data.extend(p_data)
            temp_pressure_time.clear()
            temp_pressure_time.append(dt_string)

        return p_data[0]
    except Exception as e:
        print("Retrieve_pressure_file error:",e)
        return None

@callback(
        Output(component_id='pressure-result-text', component_property='children'),
        Output(component_id='pressure-result-text', component_property='color'),
        Input(component_id='pressure-result', component_property='data'),
       # State(component_id="main-storage", component_property="data"),

    )
def pressure_result(result):
    try:
        if result=="True":
            color='danger'
        else:
            color='success'
        return result,color
    except Exception as e:
        print(e)
        return "Error",'warning'

@callback(
    Output('sensor-pressure-header','children'),

    State('url-pressure','pathname'),
    Input('main-storage','data'),

)
def elderly_name(name,key):
    print('returinng item:',name)

    item = 'microphone_false'
    #key = "S129793.02-123"
    direc = server.get_directory(key, item)
    server.download_file(direc,'assets/'+key+'_audio2.mp3')

    item = 'microphone'
    direc = server.get_directory(key, item)
    server.download_file(direc, 'assets/'+key+'_audio1.mp3')

    #load and save the mp3 files

    return "Postal ID: "+key

#@callback(
#    Output('audio-pressure','src'),
#    Input('mic-cmd','children'),
#    State(component_id='5-sec-interval', component_property='n_intervals'),
#State('main-storage','data'),


#)
#def swap_audio(mic_cmd,interval,key):
 #   if  mic_cmd=="Enabled":
  #      src = 'assets/'+key+'_audio1.mp3'
   # else:
    #    src = 'assets/'+key+'_audio2.mp3'
   # return src

@callback(
    Output('audio-time','children'),
    Output('mic-cmd','children'),
    Output('mic-cmd','color'),
    Output('audio-pressure','src'),
    Input(component_id='5-sec-interval', component_property='n_intervals'),
    State(component_id="main-storage",component_property="data")  ,
)
def update_audio(interval,key):

    item = 'mic_cmd'
    #key = "S129793.02-123"
    direc = server.get_directory(key, item)
    mic=server.retrieve_file_string(direc)
    mic=mic.split(',')

    if mic[0]=='True':
        item = 'microphone'
        direc = server.get_directory(key, item)
        try:
            server.download_file(direc, 'assets/'+key+'_audio1.mp3')
        except:
            print("Error in update_audio. Unable to download audio")
        info=server.file_details(direc)

        # update to singapore time
        time_updated = info[-1] + timedelta(hours=8)
        # convert to format d/m/y h:m:s
        time_updated = time_updated.strftime("%d/%m/%Y, %H:%M:%S")

        text='Fall detected. Audio retrieved: '+time_updated
        mic_cmd='Enabled'
        color='warning'
    else:
        text='No fall detected. No access allowed to microphone.'
        mic_cmd = 'Disabled'
        color='success'



    if  mic_cmd=="Enabled":
        src = 'assets/'+key+'_audio1.mp3'
    else:
        src = 'assets/'+key+'_audio2.mp3'

    return text,mic_cmd,color,src