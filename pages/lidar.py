import ast
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import numpy as np
import plotly.express as px  # interactive charts
import GCP_class
import requests
import dash
from dash import Dash, html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc

import gen_key

url_secret=gen_key.url_secret
print("lidar.py url:",gen_key.url_secret[0])

from datetime import datetime,timedelta

from google.cloud import storage
import time

dash.register_page(__name__,)
def plotly_graph():

    bucket_name = "ee4002d_bucket"
    # authentication details
    #jsonfile = r"C:\Users\abdul\OneDrive - National University of Singapore\uni year three final year\EE4002D\Python projects\test ver 1\cred_details.json"
    jsonfile="cred_details.json"
    server=GCP_class.Server(bucket_name,jsonfile)
    key="S129793.02-123"
    item="lidar"
    graph_direc=server.get_directory(key,item)
    data=server.retrieve_file_string(graph_direc)
    res = ast.literal_eval(data)


    x = [x[0] for x in res]
    y = [x[1] for x in res]
    z = [x[2] for x in res]

    #random.sample(range(10, 100), 10)
    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=3,
            color=x,  # set color to an array/list of desired values
            colorscale='bugn',  # choose a colorscale
            opacity=0.8
        )
    )]

    )


    fig.update_layout(uirevision=True,template="plotly_dark")

    return fig




card_2d = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        id="2d-lidar-img",
                        className="img-fluid rounded-start",
                    ),
                    className="col-md-4",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            html.H4("2D LIDAR live feed", className="card-title"),
                            html.P(
                                "" ,
                                className="card-text",
                                id='2d-lidar-text'
                            ),
                            html.Small(
                                "Note: The 2D image displayed is a developer reference for fall detection via JPG.",
                                className="card-text text-muted",

                            ),
                        ]
                    ),
                    className="col-md-8",
                ),
            ],
            className="g-0 d-flex align-items-center",
        )
    ],
    className="mb-3",
    style={"maxWidth": "540px"},
)



layout = html.Div(children=[
    dcc.Download(id="download"),
dcc.Location(id='url-lidar', refresh=True),
    dbc.Row(children=[dbc.Col(children=[dbc.Button("Back to dashboard",href=gen_key.DASH_URL_BASE+'dashboard', color="primary",outline=True,size='sm'),html.H1(children='Lidar Sensor', className="display-3")])])
,

 dbc.Row(children=[#dbc.Col("",width=1),
    dbc.Col(dbc.Card(dbc.CardBody([dbc.Col(children=
             [

                html.H5("Sensor type: RPLidar A1", className="card-title",id='sensor-lidar-header'),
                html.Hr(className="my-2"),
                html.Br(),
                html.Br(),
                dbc.Row(children=

                [
                    dbc.Col(children=[
                    html.P("Developer mode:"),
                    html.P("Show 2D lidar image: "),
                    #html.Br(),
                    html.P("Sensor Status:"),

                    html.P("Transmission Status:"),
                    html.P("Sensor Mode:"),
                    html.P("2D result:"),
                    html.P("3D result:"),
                    html.P("Conscious Status:"),
                    #html.P("Average time of reading:"),

                        html.P("Calibration command:"),
                       # html.Br(),
                        #html.P("3D calibration:"),

                        #html.P("Full calibration:"),


                    ]),
                    dbc.Col(children=[
                        html.P(dbc.Switch(
                            id="manual-switch",

                            value=False,
                        )),
                        html.P(dbc.Switch(
                            id="2d-switch",

                            value=False,
                        )),
                        html.P([dbc.Badge("Healthy", color="success", className="me-1")]),
                        html.P([dbc.Badge("Transmitting",id="transmit", color="success", className="me-1")]),
                        html.P([dbc.Badge("Unknown mode", id="lidar-mode", color="info", className="me-1")]),
                        html.P([dbc.Badge("Unknown result", id="2d-result", color="success", className="me-1")]),
                        html.P([dbc.Badge("Unknown result", id="3d-result", color="success", className="me-1")]),
                        html.P([dbc.Badge("Unknown result", id="unconscious-result", color="success", className="me-1")]),

                       # html.P("Unknown result",id="2d-result"),
                        #html.P("Unknown result",id='3d-result'),
                        #html.P("Unknown result",id='unconscious-result'),
                        #html.P("15 sec"),


                        html.P(dbc.ButtonGroup([
                        dbc.Button("2D",id="2d-run",),
                        dbc.Button("3D",id="3d-run",),
                        dbc.Button("Full",id="full-run",),
                        dbc.Button("Cancel",id="cnl",)
                        ],size='sm')),

                        #html.P(dbc.Button("Run",id="2d-run",size='sm')),
                        #html.P(dbc.Button("Run",id="3d-run",size='sm')),
                        #html.P(dbc.Button("Run",id="full-run",size='sm'))

                    ])
                ]#sensor transmission and


                        ),#row for sensor transmission and on

                 #  html.P("Manual overide"),







             ]

    )
     ])#,style={"width": "40rem"}
    )#card component
    ,style={"height": "100%"}),
     dbc.Col(children=[
         html.H5("Live Data Feed")
,
         dbc.Collapse(
             #dbc.Card(dbc.CardBody([html.H6("2D live image feed",style={"text-align":'center'}),dbc.CardImg(id="2d-lidar-img",class_name ='align-self-center',style={'height':'30%', 'width':'30%'})]),)
             card_2d
             #[,style={"text-align:center"}),html.Img()]
                      ,id="2d-collapse",is_open=False),
         dcc.Graph(
             id='example-graph',
             figure=plotly_graph(),
             style={
                 # \ 'height': 100,
                 #  'width': 1200,
                 "display": "block",
                 "margin-left": "auto",
                 "margin-right": "auto",
             }

         )
         ,
         dcc.Interval(
            id='graph-update',
            interval=1*8000,n_intervals=0
        ),
         dcc.Interval(
             id='5s-update',
             interval=1 * 5000, n_intervals=0
         ),

        html.Div(
        [dbc.Button("Download graph as HTML",id="download graph html", color="info", className="me-1"),
        html.Span("Last updated: ",id="update time",style={"verticalAlign": "right"}),])

     ]#,width=6

     )

],justify='center'),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Information")),
            dbc.ModalBody("Command sent to LIDAR"),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="close", className="ms-auto", n_clicks=0
                )
            ),
        ],
        id="modal-calibration",
        is_open=False,
    ),
])



@callback(
    Output(component_id='example-graph', component_property='figure'),
    Output(component_id='update time', component_property='children'),
    Input(component_id='graph-update', component_property='n_intervals'),
    State(component_id="main-storage",component_property="data"),
)
def update_plotly(test,key ):
   # print("testing a main storage:",data_main)
    print("event occur:",test)
    start=time.time()
  #  x = random.sample(range(10, 1000), 100)
    #y = random.sample(range(10, 1000), 100)
  #  z = random.sample(range(10, 1000), 100)

    bucket_name = "ee4002d_bucket"
    # authentication details
    #jsonfile = r"C:\Users\abdul\OneDrive - National University of Singapore\uni year three final year\EE4002D\Python projects\test ver 1\cred_details.json"
    jsonfile="cred_details.json"
    server = GCP_class.Server(bucket_name, jsonfile)
    #key = "S129793.02-123"
    item = "lidar"
    graph_direc = server.get_directory(key, item)
    data = server.retrieve_file_string(graph_direc)
    details=server.file_details(graph_direc)
    res = ast.literal_eval(data)


    # update to singapore time
    time_updated = details[-1] + timedelta(hours=8)
    # convert to format d/m/y h:m:s
    time_updated = time_updated.strftime("%d/%m/%Y, %H:%M:%S")

    x = [x[0] for x in res]
    y = [x[1] for x in res]
    z = [x[2] for x in res]
    #x = random.sample(range(10, 1000), 100)
    #y = random.sample(range(10, 1000), 100)
    #z = random.sample(range(10, 1000), 100)

    update=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=2,
            color=x,  # set color to an array/list of desired values
            colorscale='bugn',  # choose a colorscale
            opacity=0.8
        ),

    )]

    print("end of  event")
    print("time taken:",time.time()-start)


    return {"data":update,"layout":{'title':'3D Lidar Cloud Point','uirevision':True,\

                                    'paper_bgcolor':'rgba(0,0,0,0)',
                                    'height':500,
                                    'gridcolor':'aqua',
                                    'bordercolor':'aqua',
                                    'font':{'color':'white','size':15}
                                    }
            },"Last updated: "+time_updated+" hrs. Interval count: "+str(test)

@callback(
    Output(component_id="download", component_property="data"),
    State(component_id='example-graph', component_property='figure'),
    Input( component_id='download graph html', component_property='n_clicks'),

)
def download_graph(fig, n):
    if n is not None:
        print("//button click :", n)
        #print(fig)
        figure=go.Figure(fig["data"])
        #figure.write_html("test_file1.html")
        return dict(content=figure.to_html(), filename="Lidar_data.html")

@callback(
    Output(component_id="2d-run",component_property="disabled"),
    Output(component_id="3d-run",component_property="disabled"),
    Output(component_id="full-run",component_property="disabled"),
    Output(component_id="cnl",component_property="disabled"),
    Input(component_id='manual-switch', component_property="value")
)
def disable_manualinput(value):
    if value:
        return False,False, False, False
    else:
        return True, True, True, True

@callback(
    Output(component_id='modal-calibration', component_property="is_open"),
    Input(component_id="2d-run",component_property="n_clicks"),
    Input(component_id="3d-run",component_property="n_clicks"),
    Input(component_id="full-run",component_property="n_clicks"),
    Input(component_id="close",component_property="n_clicks"),
    Input(component_id="cnl",component_property="n_clicks"),
    State(component_id='modal-calibration', component_property="is_open")
)
def calibration(d2,d3,full,close,cnl,is_open):

    bucket_name = "ee4002d_bucket"
    # authentication details
    jsonfile="cred_details.json"
    server = GCP_class.Server(bucket_name, jsonfile)
    key = "S129793.02-123"
    #hardcoded key first,remember to change later on
    item = "calibration"
    cal_direc = server.get_directory(key, item)


    button_id = ctx.triggered_id if not None else 'No clicks yet'
    print(button_id)
    c2,c3=True,True
    if button_id=="2d-run":
        c2= False
    elif button_id=="3d-run":
        c3 = False
    elif button_id=="full-run":
        c2 = False
        c3 = False
    else:
        c2,c3=True,True

    print(button_id,type(button_id))
    if button_id is not None:
        print("detected not none")

    if button_id is not None and button_id != "close":
        cal_dict={"2D":c2,"3D":c3}
        server.upload_string(cal_direc,str(cal_dict))
        print("Command sent: ",button_id," set False, 2d,3d:",c2, c3)
    else:
        print("Command sent: ", button_id, " no changes set:", c2, c3)
    if d2 or d3 or full or close or cnl:
        return not is_open
    return is_open

@callback(
    Output(component_id='transmit', component_property='children'),
    Output(component_id='transmit', component_property='color'),
    Output(component_id='lidar-mode', component_property='children'),
    Output(component_id='lidar-mode', component_property='color'),
    Input(component_id='5s-update', component_property='n_intervals'),
    State(component_id='transmit', component_property='children'),
    State(component_id='transmit', component_property='color'),
    State(component_id='lidar-mode', component_property='children'),

    #Input(component_id="main-storage",component_property="data"),
)
def update_items(time,val,col,mode):
    bucket_name = "ee4002d_bucket"
    # authentication details
    jsonfile="cred_details.json"
    server = GCP_class.Server(bucket_name, jsonfile)
    key = "S129793.02-123"
    #hardcoded key first,remember to change later on
    item = "calibration"
    cal_direc = server.get_directory(key, item)
    data = server.retrieve_file_string(cal_direc)
    res = ast.literal_eval(data)

    #get item for lidar mode
    item = "lidar_mode"
    cal_direc = server.get_directory(key, item)
    scan_type = server.retrieve_file_string(cal_direc)
    if scan_type=='2D Scan':
        scan_color='success'
    else:
        scan_color='info'
    #res_mode = ast.literal_eval(data)
    print('\nEntering LIDAR check')
    #print("printing resmode:",res_mode,res_mode["mode"])


    if res['2D']==False and res['3D']==False:
        return "Calibrating " + '2D & 3D' + " Lidar", "warning", scan_type,scan_color
    else:
        for key,value in res.items():
            if value is False:
                print('found calibrating:',key)
                return "Calibrating "+key+" Lidar","warning",scan_type,scan_color
    print("No calibration",val,col)
    return "Transmiting","success",scan_type,scan_color

@callback(
    Output(component_id='2d-result', component_property='children'),
    Output(component_id='2d-result', component_property='color'),
    Output(component_id='3d-result', component_property='children'),
    Output(component_id='3d-result', component_property='color'),
    Output(component_id='unconscious-result', component_property='children'),
    Output(component_id='unconscious-result', component_property='color'),
    Input('2d-result-storage', 'data'),
    Input('3d-result-storage', 'data'),
    Input('unconscious-result-storage', 'data'),

)
def update_result(result_2d,result_3d,result_conscious):
    if result_2d=="fall":
        result_2d_color='danger'
    else:
        result_2d_color='success'

    if result_3d=="lying":
        result_3d_color='warning'
    else:
        result_3d_color='success'
    if result_conscious=="unconscious":
        result_3d_color='danger'
        result_conscious_color='danger'
    else:
        result_conscious_color='success'


    return result_2d,result_2d_color,result_3d,result_3d_color,result_conscious,result_conscious_color


@callback(
    Output(component_id="2d-lidar-img",component_property="src"),
    Output(component_id="2d-collapse",component_property="is_open"),
Output(component_id="2d-lidar-text",component_property="children"),
    Input (component_id='2d-switch', component_property="value"),
    Input(component_id='5s-update', component_property='n_intervals'),
)
def show_2dlidarimage(value,interval):
    bucket_name = "ee4002d_bucket"
    jsonfile="cred_details.json"
    server = GCP_class.Server(bucket_name, jsonfile)
    key = "S129793.02-123"
    #hardcoded key first,remember to change later on
    item = "2d lidar"
    img_direc = server.get_directory(key, item)
    data = server.retrieve_img(img_direc)
    details=server.file_details(img_direc)

    #update to singapore time
    time_updated=details[-1]+timedelta(hours=8)
    #convert to format d/m/y h:m:s
    time_updated =time_updated.strftime("%d/%m/%Y, %H:%M:%S")
    print(details,type(details[-1]))

    if value:
        return data,True,"Last updated: "+time_updated+ ' Hrs'
    else:
        return data,False,details

@callback(
    Output('sensor-lidar-header','children'),

    Input('url-lidar','pathname'),
    State('main-storage','data'),

)
def elderly_name(name,path):
    print('returinng item:',name)
    return "Postal ID: "+path
