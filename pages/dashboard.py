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
from PIL import Image
from datetime import datetime
from google.cloud import storage
import gen_key

url_secret=gen_key.url_secret
print("dashbaord.py url:",gen_key.url_secret[0])

#img1= Image.open("elderly_cover.jpg")
#img2= Image.open("lidar_cover_crop.jpg")
#img3= Image.open("pressure_cover_crop.jpg")




dash.register_page(__name__)

bucket_name = "ee4002d_bucket"
# authentication details

jsonfile="cred_details.json"
server=GCP_class.Server(bucket_name,jsonfile)
img1= server.retrieve_img('template/elderly_cover.jpg')
img2= server.retrieve_img('template/lidar_cover.jpg')
img3= server.retrieve_img('template/pressure_cover.jpg')

card1=dbc.Card([
    dbc.CardImg(src=img1,title='Image by Lifestylememory on Freepik', top=True),
    dbc.CardBody([html.H5("Profile bio", className="card-title"),
                  html.P("Access both profile of the Elderly currently living in the unit as well as the caretaker."),
                  dbc.Row(children=

                  [
                      dbc.Col(children=[
                          # html.P("test",id="key"),
                          # html.P("test2",id="key2"),
                          html.P("Postal Code ID:"),



                          html.P("Elderly name:"),



                      ]),
                      dbc.Col(children=[
                          html.P("Block unknown",id='dash-blk'),


                          html.P("Name unknown",id='dash-name'),


                      ])
                  ]),  # sensor transmission and

                  dbc.Button("Access Profile bio",href=gen_key.DASH_URL_BASE+'profile', color="primary"),
                  ])

    ]#,style={"width": "30rem","height":"30rem"}
            ,class_name='h-100'
             ,style={"height":"100vh"}
)#card component

card2 = dbc.Card([
dbc.CardImg(src=img2, top=True),
    dbc.CardBody([html.H5("Lidar data", className="card-title"),
                               html.P("Check status of LIDAR sensor, scanning mode, and graph to verify if there is a detected fall."),
                               dbc.Row(children=

                               [
                                   dbc.Col(children=[



                                       html.P("2D LIDAR result:"),
                                       html.P("Consciousness result:"),



                                       # html.Br(),
                                       # html.P("3D calibration:"),

                                       # html.P("Full calibration:"),

                                   ]),
                                   dbc.Col(children=[


                                       html.P([dbc.Badge("Unknown result", color="info",id="2d-result-dash", className="me-1")]),
                                       html.P([dbc.Badge("Unknown result",id="3d-result-dash", color="info",
                                                         className="me-1")]),




                                       # html.P(dbc.Button("Run",id="2d-run",size='sm')),
                                       # html.P(dbc.Button("Run",id="3d-run",size='sm')),
                                       # html.P(dbc.Button("Run",id="full-run",size='sm'))

                                   ])
                               ]  # sensor transmission and

                               ),  # row for sensor transmission and on

                               dbc.Button("Access LIDAR readings",href=gen_key.DASH_URL_BASE+'lidar', color="primary"),
                               ])]
#, style={"width": "30rem", "height": "30rem"}
,class_name='h-100'
#,style={"height":"30rem"}
)  # card component

card3 = dbc.Card([
dbc.CardImg(src=img3, top=True),
    dbc.CardBody([html.H5("Pressure tile & Mic readings", className="card-title"),
                               html.P("Check the status of the SMART pressure tiles, Graph or Microphone recordings for any anormalities or fall detection."),
                               dbc.Row(children=

                               [
                                   dbc.Col(children=[

                                       html.P("Microphone status:"),
                                       html.P("Pressure Tile fall result:"),

                                   ]),
                                   dbc.Col(children=[

                                       html.P([dbc.Badge("Unknown result", id="mic-cmd-dash", color="info",
                                                         className="me-1")]),
                                       html.P([dbc.Badge("Unknown result", id="pressure-result-dash", color="info",
                                                         className="me-1")]),

                                   ]),


                               ]  # sensor transmission and

                               ),  # row for sensor transmission and on

                               dbc.Button("Access Pressure graph & Mic recordings",href=gen_key.DASH_URL_BASE+'pressure', color="primary"),
                               ])
]#, style={"width": "30rem", "height": "30rem"}
,class_name='h-100'
#    , style={"height": "30rem"}
)  # card component

layout = dbc.Container(children=[
dcc.Store(id="elderly-name-storage",storage_type="session"),

    dbc.Row(children=[#dbc.Col("",width=1),
                      dbc.Col(children=[dbc.Button("Back to Overview",href=gen_key.DASH_URL_BASE, color="primary",outline=True,size='sm',external_link=True),html.H1(children='Welcome user',id='title-name', className="display-3")])]),
dbc.Row(children=[#dbc.Col("",width=1),
                  dbc.Col(children=[html.P("Access the sensors on the Navigation bar for details")])])

,

 dbc.Container(dbc.Row(children=[
#dbc.Col("",width=1),
    dbc.Col(card1,style={"height": "150%"}),
    dbc.Col(card2,style={"height": "150%"}),
    dbc.Col(card3,style={"height": "100%"}),
#dbc.Col("",width=1),
     ],justify="center",align='center'),fluid=True)

],style = {'flexGrow': '1'},fluid=True)#end of layout

@callback(
    Output(component_id='title-name', component_property='children'),
    Output(component_id='dash-blk', component_property='children'),
    Output(component_id='dash-name', component_property='children'),
    Output(component_id="elderly-name-storage",component_property="data"),
    Output(component_id='2d-result-dash', component_property='children'),
    Output(component_id='2d-result-dash', component_property='color'),
    Output(component_id='3d-result-dash', component_property='children'),
    Output(component_id='3d-result-dash', component_property='color'),
    Output(component_id='pressure-result-dash', component_property='children'),
    Output(component_id='pressure-result-dash', component_property='color'),
    Output(component_id='mic-cmd-dash', component_property='children'),
    Output(component_id='mic-cmd-dash', component_property='color'),
    Input(component_id="main-storage",component_property="data"),
    Input(component_id="address_unit",component_property="data"),
    Input("2d-result-storage", "data"),
    Input("unconscious-result-storage", "data"),
    Input("pressure-result", "data"),

)
def update_dashboard(main,add,f2d,f3d,fps):

    #f2d = 'fall'
    #f3d = 'lying'
    #fps = "True"

    #retriving profile bio
    direc_item = "details"
    detail_direc = server.get_directory(main, direc_item)
    data = server.retrieve_file_string(detail_direc)
    res = ast.literal_eval(data)

    #setting mic settings
    mic_cmd=False
    mic_cmd_text  = 'Disabled'
    mic_cmd_color = 'success'

    if f2d=="fall":
        f2d_color="danger"
        mic_cmd = True
    else:
        f2d_color='success'

    if f3d=="lying":
        f3d_color="warning"

    elif f3d == "unconscious" and ( f2d == "fall"):
        f3d_color = "danger"
        mic_cmd = True
    else:
        f3d_color='success'

    if fps=="True":
        fps_color="danger"
        mic_cmd = True
    else:
        fps_color='success'

    #checking mic_cmd
    if mic_cmd:
        mic_cmd_text = 'Enabled'
        mic_cmd_color = 'warning'


    return 'Welcome '+gen_key.dash_session['given_name']+'',main,res['bio']['elderly']['Name'],res['bio']['elderly']['Name'],f2d,f2d_color,f3d,f3d_color,fps,fps_color,mic_cmd_text,mic_cmd_color






