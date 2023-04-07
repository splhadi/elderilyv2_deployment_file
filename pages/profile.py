import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, callback,ctx
import requests
from datetime import datetime
dash.register_page(__name__)
import plotly.graph_objects as go
import GCP_class
import ast
import plotly.express as px
import gen_key
import pytz
url_secret=gen_key.url_secret
print("profile.py url:",gen_key.url_secret[0])

#fall=False
bucket_name = "ee4002d_bucket"
# authentication details
#jsonfile = r"C:\Users\abdul\OneDrive - National University of Singapore\uni year three final year\EE4002D\Python projects\test ver 1\cred_details.json"
jsonfile="cred_details.json"
server = GCP_class.Server(bucket_name, jsonfile)

dash.register_page(__name__)

detected_fall=False
data={'lat':[], 'lon':[]}
fig2 = px.scatter_mapbox(
    data,
    lat="lat",
    lon="lon",
    color_discrete_sequence=["red"],
    zoom=4,
    height=500,
)
fig2.update_layout(mapbox_style="carto-darkmatter")
fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

elderly_form=html.Div([
    dbc.Label("Elderly Name:",html_for='elderly-name-input'),
    dbc.Input(id='elderly-name-input',type="text"),
    dbc.Label("Elderly Age:", html_for='elderly-age-input'),
    dbc.Input(id='elderly-age-input', type="number"),
    dbc.Label("Elderly Medical History:", html_for='elderly-medical-input'),
    dbc.Input(id='elderly-medical-input', type="text")

])
caretaker_form=html.Div([
    dbc.Label("Caretaker Name:",html_for='care-name-input'),
    dbc.Input(id='care-name-input',type="text"),
    dbc.Label("Caretaker contact no:", html_for='care-no-input'),
    dbc.Input(id='care-no-input', type="text"),
    dbc.Label("Caretaker Telegram handle:", html_for='care-tele-input'),
    dbc.Input(id='care-tele-input', type="text"),
    dbc.Label("Caretaker Telegram chat ID:", html_for='care-teleid-input'),
    dbc.Input(id='care-teleid-input', type="number"),
    dbc.Label("Caretaker Relationship:", html_for='care-rela-input'),
    dbc.Input(id='care-rela-input', type="text"),
    dbc.Label("Caretaker Age:", html_for='care-age-input'),
    dbc.Input(id='care-age-input', type="number"),

])

tele_instructions=html.Div([
    html.H5("Steps to connect to telegram chat"),
    html.P('1. Search EFD_bot on telegram'),
html.P('2. Type command "/UpdateChatID" in chat'),
html.P("3. Enter in the unique postal id. For example if the postal code is Singapore 123456 and unit number is #01-234, your unique ID is : S123456.01-234"),
html.P("4. Log in ELderily dashboard, select address and go to profile"),
html.P("5. Once the unique ID has been entered on telegram, click on Generate 2FA for 6 digit pin in elderily dashboard"),
    html.P("6. Enter the 6 digit pin on telegram"),
    html.P("7. Elderily Dashboard will sync with telegram, and you will now receive notifications from the Elderily system")


])
layout = html.Div(children=[
   # dcc.Store(id="pressure-storage"),
    #dcc.Download(id="download"),
dcc.Store(id="fall-storage"),
dcc.Store(id="profile-storage"),
dcc.Location(id='url'),
    dcc.Interval(
        id='fall-update',
        interval=1 * 50000000, n_intervals=0
    ),

    dbc.Row(children=[#dbc.Col("",width=1),
                      dbc.Col(children=[dbc.Button("Back to dashboard",href=gen_key.DASH_URL_BASE+'dashboard', color="primary",outline=True,size='sm'),html.H1(children='Profile Dashboard', className="display-3"),
                                                            html.P("Access the sensors on the Navigation bar for details")
                                                            ])])

,

 dbc.Row(children=[#dbc.Col("",width=1),
    dbc.Col(dbc.Card(dbc.CardBody([dbc.Col(children=
             [

                html.H5("Elderly biography details", className="card-title"),
                html.Hr(className="my-2"),
                html.Br(),
                html.P(id="row"),
                #dcc.Graph(
                #    id='map-graph',
                #    figure=fig2
                #),
                html.Br(),
                dbc.Row(children=

                [
                    dbc.Col(children=[
                    #html.P("test",id="key"),
                    #html.P("test2",id="key2"),
                    html.P("Address:"),

                    html.P("Unit no:"),
                    html.P("Postal ID:"),
                    html.P("Elderly name:"),
                    html.P("Elderly age:"),
                    html.P("Elderly Medical history:"),
                    #html.P("Fall detection status:"),


                    ]),
                    dbc.Col(children=[
                        html.P("Block unknown",id='blk_no'),
                        html.P('unit unknown',id='unit_no'),
                        html.P('Postal unknown',id='postal_no'),
                        html.P("Name unknown",id="elderly_name"),
                        html.P("Age unknown",id="elderly_age"),
                        html.P("medical unknown",id="elderly_medical"),




                    ])
                ]#sensor transmission and


                        ),#row for sensor transmission and on

                 #  html.P("Manual overide"),

#dbc.Alert("No Fall detected", color="success",id="fall notify"),
html.Hr(),
dbc.Button("Edit bio", id="edit-button", n_clicks=0,disabled=True, color="primary",outline=True),
html.P(" "),
dbc.Button("Generate 2FA for chat ID", id="gen-button", n_clicks=0, color="primary",outline=True),



             ]

    )
     ])#,style={"width": "40rem"}
    )#card component
    ,style={"width":"50%"}) ,
     dbc.Col(children=[


         html.H5("Caretaker details")

,  dbc.Row([dbc.Col([
             html.P("Name:"),

             html.P("Contact no"),
             html.P("Telegram handle:"),
             html.P("Telegram chat ID:"),
             html.P("Relationship with elder:"),
             html.P("Age:"),


         ]),#column 1 of caretaker
             dbc.Col([
                 html.P("Unknown name",id='c_name'),
                 html.P("Unknown contact no",id='c_contact'),
                 html.P("Unknown Telegram handle",id='c_tele'),
                 html.P("Unknown Telegram chat ID",id='c_teleid'),
                 html.P("Unknown Relationship with elder",id='c_rela'),
                 html.P("Unknown Age",id='c_age'),


             ]),  # column 2 of caretaker

         ],justify='center'),#row for caretaker

html.P("Notify the caretaker:"),
    dbc.InputGroup(
        [
            dbc.Button("Send message", id="msg-button", n_clicks=0),
            dbc.Input(id="msg-input", placeholder="Type something"),
        ]

    )

,html.Div(id="Msg-status"),

dbc.Alert(tele_instructions,color='primary'),





     ],width=6

     )

]),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Edit Profile")),
            dbc.ModalHeader(html.H6("Elderly Profile"),close_button=False),
            dbc.ModalBody(dbc.Form([elderly_form])),

            dbc.ModalHeader(html.H6("Caretaker Profile"),close_button=False),
            dbc.ModalBody(dbc.Form([caretaker_form])),
            dbc.ModalFooter([
                dbc.Button(
                    "Save Changes", id="save", n_clicks=0
                )
                ,
                dbc.Button(
                    "Cancel", id="close", className="ms-auto", n_clicks=0
                )
            ]),
        ],
        id="modal-edit",
        size='lg',
        is_open=False,
    ),

    dbc.Modal(
        [
            #dbc.ModalHeader(dbc.ModalTitle("Edit Profile")),
            dbc.ModalHeader(html.H6("Changes saved!"), close_button=False),

            dbc.ModalFooter([

            dcc.Link(dbc.Button("Close", id="close-save", className="ms-auto", n_clicks=0),href=gen_key.DASH_URL_BASE+"profile",refresh=False)
            ]),
        ],
        id="modal-save",
        size='sm',
        centered=True,
        is_open=False,
    ),

    dbc.Modal(
        [
            # dbc.ModalHeader(dbc.ModalTitle("Edit Profile")),
            dbc.ModalHeader(html.H6("Generate code"), close_button=False),
            dbc.ModalBody([html.P("Generating for postal code:",id='gen-text-0'),html.H5("xxxxx",id='gen-text-1'),html.P("Your 2FA code:",id='gen-text-2'),html.H5("123456",id='gen-text-3')]),
            dbc.ModalFooter([

               dbc.Button("Close", id="close-gen", className="ms-auto", n_clicks=0),
            ]),
        ],
        id="modal-gen",
        size='md',
        centered=True,
        is_open=False,
    ),
])



@callback(
    Output( component_id='Msg-status', component_property='children'),
    Output( component_id='msg-input', component_property='value'),
    #Output(component_id="main-storage",component_property="data"),
    State( component_id='msg-input', component_property='value'),
    State(component_id="profile-storage",component_property="data"),
    Input( component_id='msg-button', component_property='n_clicks'),

)
def send_message(input,res,n_click):

    print("BUtton click ",n_click)
    if n_click is not None and input is not None:
        TOKEN = "5649276466:AAEA6339HRIFo55uUizfct69_NnRX7uxIc4"
    
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={res['bio']['caretaker']['chat_ID']}&text={input}"
        print(requests.get(url).json())  # this sends the message
        now = datetime.now()

        asia_tz = pytz.timezone('Asia/Singapore')
        now = now.replace(tzinfo=pytz.utc).astimezone(asia_tz)
        dt_string = now.strftime("%H:%M:%S")

        return "Message sent at "+dt_string,""
    else:
        return "No messsage sent",""
@callback(

    Output(component_id="blk_no",component_property="children"),
    Output(component_id="unit_no",component_property="children"),
    Output(component_id="postal_no",component_property="children"),
    Output(component_id="elderly_name",component_property="children"),
    Output(component_id="elderly_age",component_property="children"),
    Output(component_id="elderly_medical",component_property="children"),
    Output(component_id="c_name", component_property="children"),
    Output(component_id="c_contact", component_property="children"),
    Output(component_id="c_tele", component_property="children"),
    Output(component_id="c_teleid", component_property="children"),
    Output(component_id="c_rela", component_property="children"),
    Output(component_id="c_age", component_property="children"),
    #Output(component_id='map-graph', component_property='figure'),
    Output(component_id='row', component_property='children'),
    Output(component_id="edit-button",component_property="disabled"),
    Output(component_id="profile-storage",component_property="data"),
    Input(component_id="main-storage",component_property="data"),
    Input(component_id="address_unit",component_property="data"),
    Input(component_id="coordinates",component_property="data"),
    #State(component_id='map-graph', component_property='figure'),

)
def retrieve(data,data2,coor,):
   # print("in home page: ",data,data2,coor)

   # graph["data"][0]["lat"].append(coor[0])
    #graph["data"][0]["lon"].append(coor[1])
    #graph["layout"]['mapbox']['center']={"lat":coor[0],"lon":coor[1]}
    #print("graphlayout:", graph["layout"]['mapbox'])
    address=""
    fig = px.scatter_mapbox(
        {"lat":[coor[0]],"lon":[coor[1]]},
        lat="lat",
        lon="lon",
        color_discrete_sequence=["red"],
        zoom=15,
        height=200,
    )
    fig.update_layout(mapbox_style="carto-darkmatter")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    test=go.Figure(fig)

    #retrieve address and unit no from prev page
  #  for item in data2:
 #       if item["value"]==data:
   #         address=item["label"]
    item=data2.split("#")
    postal=data
    #retrieve data from GCP
    direc_item="details"
    detail_direc = server.get_directory(data, direc_item)
    data = server.retrieve_file_string(detail_direc)
    res = ast.literal_eval(data)


    return item[0],item[1],postal,res['bio']['elderly']['Name'],res['bio']['elderly']['Age'],res['bio']['elderly']['medical'],\
           res['bio']['caretaker']['name'],res['bio']['caretaker']['contact'], \
           res['bio']['caretaker']['tele'],res['bio']['caretaker']['chat_ID'], \
           res['bio']['caretaker']['relationship'],res['bio']['caretaker']['age'],dcc.Graph(figure=fig), \
           False, res

#modal callback
@callback(
    Output("modal-edit", "is_open"),
    [Input("edit-button", "n_clicks"), Input("close", "n_clicks"),Input("save", "n_clicks")],
    [State("modal-edit", "is_open")],
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

#form retrival for bio
@callback(

    Output(component_id="elderly-name-input",component_property="value"),
    Output(component_id="elderly-age-input", component_property="value"),
    Output(component_id="elderly-medical-input", component_property="value"),
    Output(component_id="care-name-input", component_property="value"),
    Output(component_id="care-no-input", component_property="value"),
    Output(component_id="care-tele-input", component_property="value"),
    Output(component_id="care-teleid-input", component_property="value"),
    Output(component_id="care-rela-input", component_property="value"),
    Output(component_id="care-age-input", component_property="value"),
    Input(component_id="blk_no",component_property="children"),
    Input(component_id="unit_no",component_property="children"),
    Input(component_id="postal_no",component_property="children"),
    Input(component_id="elderly_name",component_property="children"),
    Input(component_id="elderly_age",component_property="children"),
    Input(component_id="elderly_medical",component_property="children"),
    Input(component_id="c_name", component_property="children"),
    Input(component_id="c_contact", component_property="children"),
    Input(component_id="c_tele", component_property="children"),
    Input(component_id="c_teleid", component_property="children"),
    Input(component_id="c_rela", component_property="children"),
    Input(component_id="c_age", component_property="children"),
)
def bio_form(blk_no,unit_no,postal_no,elderly_name,elderly_age,elderly_medical,c_name,c_contact,c_tele,c_teleid,c_rela,c_age):
    return elderly_name,elderly_age,elderly_medical,c_name,c_contact,c_tele,c_teleid,c_rela,c_age
    pass



#save changes for bio form
@callback(

    Output("modal-save", "is_open"),
    State(component_id="elderly-name-input",component_property="value"),
    State(component_id="elderly-age-input", component_property="value"),
    State(component_id="elderly-medical-input", component_property="value"),
    State(component_id="care-name-input", component_property="value"),
    State(component_id="care-no-input", component_property="value"),
    State(component_id="care-tele-input", component_property="value"),
    State(component_id="care-teleid-input", component_property="value"),
    State(component_id="care-rela-input", component_property="value"),
    State(component_id="care-age-input", component_property="value"),
    Input(component_id="save",component_property="n_clicks"),
    Input(component_id="close-save",component_property="n_clicks"),
    Input(component_id="profile-storage",component_property="data"),
    State("modal-save", "is_open"),
    Input(component_id="main-storage", component_property="data")

)
def save_form(elderly_name,elderly_age,elderly_medical,c_name,c_contact,c_tele,c_teleid,c_rela,c_age,save,close_save,dict,is_open,key):
    #if state for button ID detection for close save so that it doesnt toggle both save

    button_id = ctx.triggered_id if not None else 'No clicks yet'
    res=dict
    if button_id=="save":
        #perform all saving function here
        res['bio']['elderly']['Name']           =elderly_name
        res['bio']['elderly']['Age']            =elderly_age
        res['bio']['elderly']['medical']        =elderly_medical
        res['bio']['caretaker']['name']         =c_name
        res['bio']['caretaker']['contact']      =c_contact
        res['bio']['caretaker']['tele']         =c_tele
        res['bio']['caretaker']['chat_ID']      =c_teleid
        res['bio']['caretaker']['relationship'] =c_rela
        res['bio']['caretaker']['age']          =c_age



        # hardcoded key first,remember to change later on
        item = "details"
        cal_direc = server.get_directory(key, item)
        server.upload_string(cal_direc, str(res))

        pass
   # print("save form:", dict)
    if save or close_save:
        return not is_open
    return is_open

@callback(
    Output("modal-gen", "is_open"),
    Output("gen-text-0", "children"),
    Output("gen-text-1", "children"),
    Output("gen-text-2", "children"),
    Output("gen-text-3", "children"),
    [Input("close-gen", "n_clicks"),Input("gen-button", "n_clicks")],
    [State("modal-gen", "is_open")],
)
def toggle_modal_generate2FA(n1, n2, is_open):

    item=server.retrieve_file_string("telebot_2FA.txt")
    if item=="False":
        title1=""
        text="Commmand /UpdateChatID not activated!"
        title2=""
        pin="Not authorised to make changes"
    else:
        things=item.split(',')
        title1="Generating for postal code:"
        title2="Your 2FA code:"
        text=things[2]
        pin=things[1]
    if n1 or n2:
        return not is_open,title1,text,title2,pin
    return is_open,title1,text,title2,pin