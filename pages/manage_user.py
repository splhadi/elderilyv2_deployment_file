import dash
import GCP_class
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, callback,dash_table,ctx
import requests
from datetime import datetime
from google.cloud import storage
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import gen_key
import ast
import numpy as np
import gtts
import time
dash.register_page(__name__,path='/manage_user')

# authentication details
jsonfile="cred_details.json"
bucket_name = "ee4002d_bucket"
server = GCP_class.Server(bucket_name, jsonfile)

#download account list
data = server.retrieve_file_string('accounts.txt')
res = ast.literal_eval(data)
users=pd.DataFrame(res['user'],columns=['Current Users'])


table=dash_table.DataTable(users.to_dict('records'),id='manage-table',
row_selectable="single",
style_as_list_view=True,
                           style_header={
                               'fontWeight': 'bold',
                               'color': 'white'
                           }
                           , style_data={
        'whiteSpace': 'normal',
        'height': '40px',
        'color': 'white'
    },
                           style_cell={'textAlign': 'left'},
                           )

table_unit=dash_table.DataTable(id='manage-table-unit',
row_selectable="single",
style_as_list_view=True,
                           style_header={
                               'fontWeight': 'bold',
                               'color': 'white'
                           }
                           , style_data={
        'whiteSpace': 'normal',
        'height': '40px',
        'color': 'white'
    },
                           style_cell={'textAlign': 'left'},
                           )

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

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.H6("Please enter the Gmail account that you wish to add:"),
            html.Br(),
            dbc.Input(id="input", placeholder="Enter email here...", type="email"),
            html.Br(),
            dbc.Button("Register email", color="success",id='add-user-button'),
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.H6("Select the following email address to remove:", className="card-text"),
            html.Div(table,className="dbc dbc-row-selectable"),
            #html.P(html.Br()),
            dbc.Button("Refresh Table for users",id='refresh-table-btn', color="primary",outline=True,size='sm'),
            html.P(html.Br()),
            html.P("User selected: ",id='manage-user-text'),
            dbc.Button("Remove User", color="danger",id='delete-user-button'),
        ]
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        dbc.Form([
            #address portion
            html.H5("Address form"),
            html.P("Please enter the address details below"),
dbc.Label("Postal code:"),
dbc.InputGroup(
    [

        dbc.Input(placeholder='Input postal code',id="postal-code-input",type='number'),
        dbc.Button("Generate address",id='generate-address-btn'),
    ]),
            html.Br(),
            dbc.Label("Address:"),
            dbc.Input(id='address-input', type="text"),
            html.Br(),
html.P("Address Latitude: ",id='lat-input'),
html.P("Address Longitude: ",id='long-input'),
dbc.Label("Unit no:", ),
            dbc.InputGroup(
                [dbc.InputGroupText("#"), dbc.Input(placeholder="Unit number",id='unit-no-input')],
                className="mb-3",
            ),
            html.Br(),
            #elderly portion
            html.H5("Elderly form"),
            html.P("Please enter the elderly details below"),
            dbc.Label("Elderly Name:"),
            dbc.Input(id='elderly-name-input-manage', type="text"),
html.Br(),
            dbc.Label("Elderly Age:"),
            dbc.Input(id='elderly-age-input-manage', type="number"),
            html.Br(),

            #Caretaker portion
            html.H5("Caretaker form"),
            html.P("Please enter the caretaker details below"),
            dbc.Label("Caretaker Name:"),
            dbc.Input(id='care-name-input-manage', type="text"),
html.Br(),
            dbc.Label("Caretaker contact no:"),
            dbc.Input(id='care-no-input-manage', type="text"),
html.Br(),
            dbc.Label("Caretaker Telegram handle:"),
            dbc.Input(id='care-tele-input-manage', type="text"),

html.Br(),
            dbc.Label("Caretaker Relationship:"),
            dbc.Input(id='care-rela-input-manage', type="text"),
html.Br(),
            dbc.Label("Caretaker Age:"),
            dbc.Input(id='care-age-input-manage', type="number"),
html.Br(),
html.H6("To receive notifications on this unit, please connect with the telegram bot EFD_bot after this unit has been added into the data."),
            dbc.Alert(tele_instructions,color='primary'),
            dbc.Button("Register Unit", color="success",id='add-unit-button'),
        ])
    ),
    className="mt-3",
)

tab4_content = dbc.Card(
    dbc.CardBody(
        [
            html.H6("Select the following Unit address to remove:", className="card-text"),
            html.Div(table_unit,className="dbc dbc-row-selectable"),
            #html.P(html.Br()),
            dbc.Button("Refresh Table for unit",id='refresh-table-unit-btn', color="primary",outline=True,size='sm'),
            html.P(html.Br()),
            html.P("Unit selected: ",id='manage-unit-text'),
            dbc.Button("Remove Unit", color="danger",id='delete-unit-button'),
        ]
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Add user"),
        dbc.Tab(tab2_content, label="Manage user"),
        dbc.Tab(tab3_content, label="Add New Unit"),
        dbc.Tab(tab4_content, label="Remove Unit"),

    ]
)


layout_stack=dbc.Row(dbc.Col([tabs],
#width={"size": 7}
width=7
),justify='center'
)

modal_confirm=dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Warning!")),
            dbc.ModalBody("",id='confirm-text'),

            dbc.ModalFooter([
                dbc.Button(
                    "Confirm", id="manage-save", n_clicks=0
                )
                ,
                dbc.Button(
                    "Cancel", id="manage-close", className="ms-auto", n_clicks=0
                )
            ]),
        ],
        id="modal-confirm",
        #size='lg',
        is_open=False,
    )

modal_confirm2=dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Warning!")),
            dbc.ModalBody('Are you sure you wish to delete this address?'),

            dbc.ModalFooter([
                dbc.Button(
                    "Confirm", id="manage-unit-save", n_clicks=0
                )
                ,
                dbc.Button(
                    "Cancel", id="manage-unit-close", className="ms-auto", n_clicks=0
                )
            ]),
        ],
        id="modal-confirm2",
        #size='lg',
        is_open=False,
    )

layout = html.Div([layout_stack,
                   dcc.Location(id='url-admin', refresh=True),
                  dbc.Modal(
                      [
                          dbc.ModalHeader(dbc.ModalTitle("Notification")),
                          dbc.ModalBody("This is the content of the modal",id='modal-text'),

                      ],
                      id="modal-noti",
                      is_open=False,

                  ),
                   dbc.Modal(
                       [
                           dbc.ModalHeader(dbc.ModalTitle("Notification")),
                           dbc.ModalBody("User deleted!"),

                       ],
                       id="modal-noti-2",
                       is_open=False,

                   ),
                   dbc.Modal(
                       [
                           dbc.ModalHeader(dbc.ModalTitle("Notification")),
                           dbc.ModalBody("Unit and Address deleted!"),

                       ],
                       id="modal-noti-3",
                       is_open=False,

                   ),
                   dbc.Modal(
                       [
                           dbc.ModalHeader(dbc.ModalTitle("Notification")),
                           dbc.ModalBody(dcc.Loading(html.P("New unit added!",id='loading-text1'))),
                           dbc.ModalBody("Please wait while the dashboard is adding a new unit",id='loading-text2'),

                       ],
                       id="modal-add-unit",
                       is_open=False,

                   )

                      ,modal_confirm
,modal_confirm2
                  ])



@callback(

Output('manage-user-text','children'),
Output('confirm-text','children'),
Input("manage-table","selected_rows"),
)
def show_email(index):
    print("Selected",index)
    if index is None:
        return "User not selected",""
    #print("User selected: "+res['user'][index],index)
    return "User selected: "+str(res['user'][index[0]]),"Are you sure you wish to remove "+str(res['user'][index[0]])+"?"

@callback(
    Output('modal-noti','is_open'),
Output('modal-text','children'),
Input("add-user-button","n_clicks"),
    State('input','value'),
State('input','valid')
)
def add_user(n_click,input,state):
    if n_click is None:
        return False,''
    #if not state:
     #   return True,"Invalid Email Input. Please reenter again!"
    user_email=input.lower()
    res['user'].append(user_email)
    server.upload_string('accounts.txt',str(res))
    return True,'User added!'

@callback(
Output('modal-confirm','is_open'),
Input("delete-user-button","n_clicks"),
Input("manage-close","n_clicks"),
Input("manage-save","n_clicks"),
State('modal-confirm','is_open'),
)
def confirm(n1,n2,n3,is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

@callback(
    Output('modal-noti-2','is_open'),
Input("manage-save","n_clicks"),
State("manage-table","selected_rows"),
State('manage-table','data'),
)
def delete_user(click,index,data):
    if click:
        res['user'].pop(index[0])
        server.upload_string('accounts.txt', str(res))
        users = pd.DataFrame(res['user'], columns=['Current Users'])
        return True
    return False


@callback(
Output('manage-table','data'),
Input("add-user-button","n_clicks"),
Input("manage-save","n_clicks"),
Input('refresh-table-btn','n_clicks'),
State('manage-table','data'),
)
def update_table(n1,n2,n3,data):
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if n1 or n2 or n3:
        if button_id=='refresh-table-btn':
            data = server.retrieve_file_string('accounts.txt')
            res2 = ast.literal_eval(data)
            users = pd.DataFrame(res2['user'], columns=['Current Users'])
        else:
            users = pd.DataFrame(res['user'], columns=['Current Users'])
        return users.to_dict('records')
    else:
        return data

@callback(
    Output('url-admin', 'pathname'),

    Input('url-admin', 'pathname')
)
def redirect(path):
    if not gen_key.dash_session['user_type']=='admin':
        return gen_key.DASH_URL_BASE
    else:
        return path

@callback(
    Output('address-input','value'),
    Output('lat-input','children'),
    Output('long-input','children'),
    Input('generate-address-btn','n_clicks'),
    State('postal-code-input','value')


)
def generate_address(n_clicks,postal_code):
    if n_clicks is None:
        return "","Address Latitude: ","Address Longitude: "
    else:
        print('button clicked to generate address from postal code')
        url = f"https://developers.onemap.sg/commonapi/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        response = requests.get(url).json()
        print(response)
        results = response.get('results')
        print(results)
        if results:
            address = results[0].get('ADDRESS')
            latitude=results[0].get('LATITUDE')
            longitude = results[0].get('LONGITUDE')
            return address,"Address Latitude: "+str(latitude),"Address Longitude: "+str(longitude)
        else:
            print("Error getting results")
            return None,"Address Latitude: ","Address Longitude: "

@callback(
    Output('modal-add-unit','is_open'),
Input("add-unit-button","n_clicks"),

)
def open_modal_for_add_unit(n_click):
    if n_click is None:
        return False
    return True

@callback(
    Output('loading-text1','children'),
Output('loading-text2','children'),
Input("add-unit-button","n_clicks"),
State('postal-code-input','value'),
State('address-input','value'),
State('lat-input','children'),
State('long-input','children'),
State('unit-no-input','value'),

    State(component_id="elderly-name-input-manage", component_property="value"),
    State(component_id="elderly-age-input-manage", component_property="value"),
    State(component_id="care-name-input-manage", component_property="value"),
    State(component_id="care-no-input-manage", component_property="value"),
    State(component_id="care-tele-input-manage", component_property="value"),
    State(component_id="care-rela-input-manage", component_property="value"),
    State(component_id="care-age-input-manage", component_property="value"),


)
def add_unit(n_click,postal,address,lat,long,unit_no,elderly_name,elderly_age,c_name,c_contact,c_tele,c_rela,c_age):
    if n_click is None:
        return '','Please wait while the dashboard is adding the unit'
    postal = str(postal)
    postalID = 'S' + postal + '.' + unit_no
    unit_no = '#' + unit_no
    parent_path = 'unitdata_readings/'
    pri = 'nil'
    remarks = 'nil'
    lat = lat.replace("Address Latitude: ", "")
    long = long.replace("Address Longitude: ", "")

    # retrieve unit location and insert new one

    message = server.retrieve_file_string("unit_location.txt")
    # print(message)
    data = message.split("\r\n")
    print(data)
    unit_data = [i.split(",") for i in data if len(i) > 1]
    number = str(len(unit_data) + 1)
    column_item = number + ',' + address + ',' + unit_no + ',' + postalID + ',' + lat + ',' + long + ',' + pri + ',' + remarks
    message = message + '\r\n' + column_item

    # prepare details of new unit
    new_unit = {"Sensor": {"Lidar": ""}, "bio": {"elderly": {"Name": "", "Age": "", "Weight": "",'medical':''},
                                                 "caretaker": {"name": "", "contact": "", "tele": "", "chat_ID": "",
                                                               "relationship": "", "age": ""}}}
    new_unit['bio']['elderly']['Name'] = elderly_name
    new_unit['bio']['elderly']['Age'] = str(elderly_age)
    new_unit['bio']['elderly']['medical'] = 'Nil'
    new_unit['bio']['caretaker']['name'] = c_name
    new_unit['bio']['caretaker']['contact'] = str(c_contact)
    new_unit['bio']['caretaker']['tele'] = c_tele
    new_unit['bio']['caretaker']['chat_ID'] = ''
    new_unit['bio']['caretaker']['relationship'] = c_rela
    new_unit['bio']['caretaker']['age'] = str(c_age)

    # prepare other files

    # 2d image data
    image_2d = server.retrieve_img('template/2d_lidar_image.jpg')
    image_2d.save('temp/temp_save.jpg')
    img = open('temp/temp_save.jpg', 'rb')
    lidar_image_2d = img

    result_2d = "New unit no transmission"
    result_3d = "New unit no transmission"
    unconscious_result = "New unit no transmission"
    acknowledge = 'False,08/03/2023 16:36:45'
    calibration = "{'2D': True, '3D': True}"
    details = str(new_unit)
    fall = ""

    # 3d data lidar
    numpy_3d = server.retrieve_file('template/3d_cloud.npy', 'npy')
    numpy_3d = np.load(numpy_3d)
    lidar_3d = str([list(i) for i in numpy_3d])

    lidar_mode = "Unknown mode"
    mic_cmd = 'False,08/03/2023 17:29:58'

    # mic mp3 data
    tts = gtts.gTTS("This is a new unit that has been created by the elderly dashboard. No audio has been created yet.",
                    lang="en")
    tts.save("temp/temp_save.mp3")
    mic_data = open('temp/temp_save.mp3', 'rb')


    # mic mp3 data for false audio
    string_audio="This is an audio file for Address:"+address+"unit no: "+unit_no+"elderly name"+elderly_name+". No fall detected therefore no access to microphone audio is allowed"
    tts = gtts.gTTS(string_audio,
                    lang="en")
    tts.save("temp/temp_save.mp3")
    mic_data2 = open('temp/temp_save.mp3', 'rb')



    pressure_data = '17:31:21, 10.3, 39.9, 10.0'
    pressure_data_1000 = '17:31:21, 10.3, 39.9, 10.0'
    pressure_result = 'No available data'

    # register into server for unit_location.txt
    server.upload_string('unit_location.txt',message)

    # create folder for postal id
    server.create_folder(parent_path,postalID)

    # create all necessary files
    item_list = {'2d_lidar_image.jpg': lidar_image_2d, '2d_result.txt': result_2d, '3d_result.txt': result_3d,
                 'unconscious_result.txt': unconscious_result, 'acknowledge.txt': acknowledge,
                 'calibration.txt': calibration, 'details.txt': details, 'fall.txt': fall,
                 'lidar_3d.txt': lidar_3d, 'lidar_mode.txt': lidar_mode, 'mic_cmd.txt': mic_cmd,
                 'microphone.mp3': mic_data,'microphone_false.mp3': mic_data2, 'pressure_data.txt': pressure_data,
                 'pressure_data_1000.txt': pressure_data_1000,
                 'pressure_result.txt': pressure_result
                 }
    # uploading each files
    for item in item_list:
        stuff = item.split('.')
        server.create_unit_file(parent_path, postalID, stuff[0], stuff[1], False, item_list[item])

    mic_data.close()
    mic_data2.close()
    return '',"Unit added!"

@callback(
Output('manage-table-unit','data'),
Input('refresh-table-unit-btn','n_clicks'),
Input("manage-unit-save","n_clicks"),
State('manage-table-unit','data'),
)
def refresh_table(btn,btn2,unit):
    message=server.retrieve_file_string('unit_location.txt')
    data = message.split("\r\n")
    unit_data = [i.split(",") for i in data if len(i) > 1]

    print(len(unit_data[0]))
    ud = pd.DataFrame(unit_data, columns=["No", 'Address', 'Unit', 'Postal ID', 'lat', 'lon', 'Fall Status', 'Sensors'])
    return ud.to_dict('records')

@callback(

Output('manage-unit-text','children'),
Input("manage-table-unit","selected_rows"),
State('manage-table-unit','data')
)
def show_unit(index,data):
    print("Selected",index)
    if index is None:
        return "Address not selected"

    return "Address selected: "+str(data[index[0]]['Address']+' '+data[index[0]]['Unit']    )

@callback(
Output('modal-confirm2','is_open'),
Input("delete-unit-button","n_clicks"),
Input("manage-unit-close","n_clicks"),
Input("manage-unit-save","n_clicks"),
State('modal-confirm2','is_open'),
)
def confirm(n1,n2,n3,is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

@callback(
    Output('modal-noti-3','is_open'),
Input("manage-unit-save","n_clicks"),
State("manage-table-unit","selected_rows"),
State('manage-table-unit','data'),
)
def delete_user(click,index,datatable):
    if click:
        message = server.retrieve_file_string('unit_location.txt')
        data = message.split("\r\n")
        unit_data = [i.split(",") for i in data if len(i) > 1]
        print("Selected:",data[index[0]])
        data.pop(index[0])
        for index_no,i in enumerate(data):

            data[index_no]=str(index_no+1)+i[1:]
        new_data="\r\n".join(data)
        print(datatable[index[0]]['Postal ID'],index[0])

        print(new_data)

        directory="unitdata_readings/"+datatable[index[0]]['Postal ID']+'/'
        print(directory)
        server.upload_string('unit_location.txt',new_data)
        server.delete_folder(directory)


        return True
    return False