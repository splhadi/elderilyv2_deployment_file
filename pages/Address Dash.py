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
import pytz
url_secret=gen_key.url_secret
print("address dasb.py url:",gen_key.url_secret[0])



dash.register_page(__name__, path='/')



bucket_name = "ee4002d_bucket"
# authentication details
#jsonfile = r"C:\Users\abdul\OneDrive - National University of Singapore\uni year three final year\EE4002D\Python projects\test ver 1\cred_details.json"
jsonfile="cred_details.json"
storage_client = storage.Client.from_service_account_json(
    jsonfile)
bucket = storage_client.get_bucket(bucket_name)
server = GCP_class.Server(bucket_name, jsonfile)


legend_header=[['Priority 4','This is where all system are normal and functioning as intended.'],['Priority 3','This indicates that at least 1 sensor has been triggered.'],
               ['Priority 2','This indicates that 2 sensors have been triggered.'],['Priority 1','This is an urgent priority as all sensors have been activated.']
               ]
legend_header=pd.DataFrame(legend_header,columns=['Priority No','Definition'])
#print(panda)
legend_table=dash_table.DataTable(legend_header.to_dict('records'),
style_as_list_view=True,
style_header={
        'fontWeight': 'bold',
    'color':'white'
    },
style_data={
  'whiteSpace': 'normal',
  'height': '40px',
  'color': 'white'
},
style_cell={'textAlign': 'left'},
style_data_conditional=[{
    'if':{
            'filter_query':'{Priority No} ="Priority 4"',
            'column_id': 'Priority No'
        }
,
'backgroundColor': 'green',
}
,
{
    'if':{
            'filter_query':'{Priority No}= "Priority 3"',
            'column_id': 'Priority No'
        }
,
'backgroundColor': 'orange',
},
{
    'if':{
            'filter_query':'{Priority No}="Priority 2"',
            'column_id': 'Priority No'
        }
,
'backgroundColor': 'orange',
},
{
    'if':{
            'filter_query':'{Priority No}="Priority 1"',
            'column_id': 'Priority No'
        }
,
'backgroundColor': 'red',
}]

                                  )

def load_fig_table():
    blob = bucket.blob("unit_location.txt")
    msg_xdecode = blob.download_as_string()
    message = msg_xdecode.decode('utf-8')
    data = message.split("\r\n")
    unit_data = [i.split(",") for i in data if len(i) > 1]

    print(len(unit_data[0]))
    ud = pd.DataFrame(unit_data,
                      columns=["No", 'Address', 'Unit', 'Postal ID', 'lat', 'lon', 'Fall Status', 'Sensors'])

    # mapbox testing
    ud['lat'] = pd.to_numeric(ud['lat'])
    ud['lon'] = pd.to_numeric(ud['lon'])

    fig2 = px.scatter_mapbox(
        ud.to_dict('list'),
        lat="lat",
        lon="lon",

        color="No",
        # color=['priority 4','priority 4','priority 2','priority 1'],
        color_discrete_map={'Priority 4': 'green', 'Priority 3': 'orange', 'Priority 2': 'orange',
                            'Priority 1': 'red'},

        zoom=11,
        #height=500,
       # width=1000
    )

    fig2.update_layout(mapbox_style="carto-darkmatter", showlegend=False)
    fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig2.update_traces(marker=dict(color='red'))
    return fig2,ud

fig_main,ud_main=load_fig_table()

table=dash_table.DataTable(ud_main.to_dict('records'),
row_selectable="single",
style_as_list_view=True,
style_header={
        'fontWeight': 'bold',
    'color':'white'
    }
,    style_data={
        'whiteSpace': 'normal',
        'height': '40px',
        'color':'white'
    },
style_cell={'textAlign': 'left'},
style_data_conditional=[{
    'if':{
            'filter_query':'{Fall Status} ="Priority 4"',
            'column_id': 'Fall Status'
        }
,
'backgroundColor': 'green',
}
,
{
    'if':{
            'filter_query':'{Fall Status}= "Priority 3"',
            'column_id': 'Fall Status'
        }
,
'backgroundColor': 'orange',
},
{
    'if':{
            'filter_query':'{Fall Status}="Priority 2"',
            'column_id': 'Fall Status'
        }
,
'backgroundColor': 'orange',
},
{
    'if':{
            'filter_query':'{Fall Status}="Priority 1"',
            'column_id': 'Fall Status'
        }
,
'backgroundColor': 'red',
}
,{
      'if':{
        'column_id':'lat'


    },'display':'none'




    },

{
      'if':{
        'column_id':'lon'


    },'display':'none'




    }
],#end of conditional style
style_header_conditional=[

{
      'if':{
        'column_id':'lat'


    },'display':'none'




    }
,
{
      'if':{
        'column_id':'lon'


    },'display':'none'




    }
],
id='table'
                           )#table settings


layout_stack=dbc.Row(dbc.Col([

    html.H1("Deployed Systems:", style={'textAlign': 'auto', }),

    dcc.Graph(figure=fig_main,
              style={
                 # 'height': 100,
                #  'width': 1200,
                  "display": "block",
                  "margin-left": "auto",
                  "margin-right": "auto",
              },id='map-graph'
              ),
    html.Br(),
dbc.Button("Open Legend", id="open-offcanvas", n_clicks=0,color="primary",outline=True,size='sm'),
    html.Hr(),
    dbc.InputGroup([
dbc.InputGroupText("Access Address: "),
dbc.Input(id="table-selection", placeholder="Add an address to begin...", type="text",disabled=True),
dbc.Button("Access", id="access button", href=gen_key.DASH_URL_BASE+"dashboard")
    ]),
#dbc.Input(id="input", placeholder="Type something...", type="text",disabled=True),
    html.Br(),

    html.Div(table,className="dbc dbc-row-selectable"),
 #   html.P("No selection",id="table-selection")
html.Br(),
#dbc.Spinner(html.P("",id='refresh-text'),fullscreen=True,spinner_style={"width": "7rem", "height": "7rem"}),
dcc.Loading(html.P("",id='refresh-text'),fullscreen=False,loading_state={'content':'test123'}),
dbc.Button("Refresh all fall status",id='refresh-fall', color="primary",outline=True,size='sm'),

],
#width={"size": 7}
width=7
),justify='center'
)


#main layout of webpage
layout = html.Div(children=[
dcc.Location(id='url-address', refresh=False),
    dcc.Interval(id='startup',interval=1*1000,n_intervals=0,max_intervals=5),
layout_stack,

    dbc.Offcanvas([
        html.P(
            "The list of priority names and definitions are shown below. Press ESC or the 'close' button to exit this popover."
        )
            ,
        html.Div(legend_table,className="dbc dbc-row-selectable")
                ],
        id="offcanvas",
        title="Legend information",
        is_open=False,
        backdrop=False,
        scrollable=True,
        keyboard=True
    ),
    dbc.Popover(
        [
            dbc.PopoverHeader("Warning"),
            dbc.PopoverBody("Please select an address before proceeding!"),
        ],
        id="popover",
        is_open=False,
        target="access button",
       # trigger = "hover",
        placement='top'
    ),
])



@callback(

          Output(component_id="main-storage",component_property="data"),
          Output(component_id="address_unit",component_property="data"),
          Output(component_id="coordinates",component_property="data"),
          #Output(component_id="access link", component_property="href"),
          Output("popover", "is_open"),
          #State(component_id="dropdown",component_property="value"),
          State(component_id="table-selection", component_property="value"),
          State(component_id="table",component_property="selected_rows"),
          State(component_id="table",component_property="data"),
          Input(component_id="access button", component_property="n_clicks"),

          #State("popover", "is_open"),
          )
def gotoProfile(option,index,data,n_click):

    item=None
    coor=[]

    if n_click is not None:


        print(item, "selected", option,'index:',index,type(index))
        if index is None:
            is_open=True
        else:
            index_no = index[0]
            item = data[index_no]['Postal ID']
            coor = [data[index_no]['lat'],data[index_no]['lon']]
            #item = ud['Postal ID'][index_no]
            #coor = [ud['lat'][index_no], ud['lon'][index_no]]
            is_open=False
        return item,option,coor,is_open
    else:
        return item,option,coor,False


@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@callback(
          Output(component_id="access button", component_property="href"),
          #Output("popover", "is_open"),
          Input(component_id="table",component_property="selected_rows"),
          State(component_id="access button", component_property="n_clicks"),

          )
def allow_access(value,click):
    if value is None:
        ref = gen_key.DASH_URL_BASE
    else:
        ref = gen_key.DASH_URL_BASE+"dashboard"

    return ref

@callback(
          Output(component_id="table-selection", component_property="value"),
          Input(component_id="table",component_property="selected_rows"),
          State('table','data')
          )
def select_tabledata(item,data):
    if item is None:
        return "No address Selected. Select any addresses from the list to begin."
    index=item[0]

    print(data[index])
    return data[index]['Address']+' '+data[index]['Unit']
    #return ud['Address'][index]+" "+ud['Unit'][index]

@callback(
          Output(component_id="refresh-text", component_property="children"),
          Output(component_id="table",component_property="data"),
          Output(component_id='map-graph', component_property='figure'),
          Input(component_id="refresh-fall",component_property="n_clicks"),
          Input('startup', 'n_intervals'),
          State(component_id="table",component_property="data"),
          State(component_id='map-graph', component_property='figure'),
prevent_initial_call=True
          )
def refresh_table(click,interval,table_data,fig):
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    print("loading table with triggered id:",button_id,'interval:',interval)
    #load table for interval =0 first load:
    if interval<5:
        print("Interval equal 0")
        fig2,ud=load_fig_table()
        print("Returning data")

        return "Loaded maps and data",ud.to_dict('Records'),fig2


   # print('printing fig:',fig['layout'])
   # fig['data'][0]['lat'] = [fig['data'][0]['lat'][0]]
    #fig['data'][0]['legendgroup']="Priority 1"
    #fig['data'][0]['lon'] = [fig['data'][0]['lon'][0]]
    #fig['data'][0]['marker']['color'] = 'red'
    #fig['data'][0]['name']='Priority 1'
    #print('printing fig:', fig['data'][0])

    data={'Fall Status':[],"Sensors":[]}
    if click:
        now = datetime.now()

        asia_tz = pytz.timezone('Asia/Singapore')
        now = now.replace(tzinfo=pytz.utc).astimezone(asia_tz)
        dt_string = now.strftime("%H:%M:%S")

        output=" Last Updated: "+ dt_string
    else:
        output="No update"
    #print([table_data[i]['Postal ID'] for i in range(len(table_data))])
    #print(len(table_data))
    #print([table_data[i]['Postal ID'] for i in range(len(table_data))])
    if output:#=='clicked':
        #for index,key in enumerate(ud["Postal ID"]):
        for index, key in enumerate([table_data[i]['Postal ID'] for i in range(len(table_data))]):
            #print(table_data[index])
            try:
                directory = server.get_directory(key, "2d_result")
                fall_2d = server.retrieve_file_string(directory)
            except:
                print("Download error encounted in refresh_table() at address page for fall_2d")
                fall_2d = "Error"

            try:
                directory = server.get_directory(key, "3d_result")
                fall_3d = server.retrieve_file_string(directory)
            except:
                print("Download error encounted in refresh_table() at address page for fall_3d")
                fall_3d = "Error"
            try:
                directory = server.get_directory(key, "unconscious_result")
                fall_uncon = server.retrieve_file_string(directory)
            except:
                print("Download error encounted in refresh_table() at address page for fall_uncon")
                fall_uncon = "Error"
            try:

                directory = server.get_directory(key, "pressure_result")
                fall_ps = server.retrieve_file_string(directory)
            except:
                print("Download error encounted in refresh_table() at address page for fall_ps")
                fall_ps = "Error"


            pri_check, detected_fall_sensors = fall_priority(fall_2d, fall_uncon, fall_ps)
            #print(key, fall_2d,fall_3d,fall_ps)
            print(key,pri_check,detected_fall_sensors)

            if pri_check==1:
                pri="Priority 1"
                sensor=",".join(detected_fall_sensors)
            elif pri_check==2:
                pri="Priority 2"
                sensor=",".join(detected_fall_sensors)
            elif pri_check==3:
                pri="Priority 3"
                sensor=" ".join(detected_fall_sensors)
            else:
                pri = "Priority 4"
                sensor = "NIL"

            table_data[index]['Fall Status']=pri

            table_data[index]['Sensors'] = sensor
           # data['Fall Status'].append(pri)
            #data['Sensors'].append(sensor)
            print("entering fig_modify with index ",index,pri)
            fig=fig_modify(fig,index,pri,table_data)


        #print("final data:",data)
        #print(table_data)

       # fig['layout']['showlegend']=True
        fig['layout']['legend']['title']['text']='Priority status of Unit'

    return output,table_data,fig


def fig_modify(fig,index,priority_grp,table_data):
    color_discrete_map = {'Priority 4': 'green', 'Priority 3': 'orange', 'Priority 2': 'orange', 'Priority 1': 'red'}
    remarks= {'Priority 4': 'No sensors have been tripped. No fall detected, all systems normal.', 'Priority 3': 'At least one sensor has been tripped. Check the unit dashboard for details', 'Priority 2': 'Two sensors have been detected. Please investigate.', 'Priority 1': 'All sensors have detected a fall. Please attend immediately or inform relevant authorities!'}
    print(f"currently at index: {index}, data currently:{fig['data'][index]['lat']}")
    #fig['data'][index]['lat'] = [fig['data'][index]['lat'][index]]
    hover_template=f"No: {table_data[index]['No']}<br>Address: {table_data[index]['Address']}<br>Unit No: {table_data[index]['Unit']}<br><br>Status: {priority_grp}<br>Sensors activated: {table_data[index]['Sensors']}<br><br>Remarks: {remarks[priority_grp]}<extra></extra>"
    fig['data'][index]['hovertemplate'] =hover_template
    #fig['data'][index]['hovertemplate']= 'No:%{No}<br><br>Address:%{Address}<br>lat=%{lat}<br>lon=%{lon}<extra></extra>'
    fig['data'][index]['legendgroup']=priority_grp
    #fig['data'][index]['lon'] = [fig['data'][index]['lon'][index]]
    fig['data'][index]['marker']['color'] = color_discrete_map[priority_grp]
    fig['data'][index]['name']=priority_grp
    fig['data'][index]['showlegend'] = True
    return fig
def fall_priority(f2d,f3d,fps):

    #simulation variables for testing
    #f2d = 'fall'
    #f3d = 'lying'
    #fps = "True"

    count=4
    item=[]
    if f2d=="fall":
        count-=1
        item.append("2D Lidar")
    if fps=="True":
        count-=1
        item.append("Pressure Sensor")

    if f3d=="unconscious" and ( f2d=="fall"):
        count-=1
        item.append("3D Lidar")

    return count,item

#testing stuff
#{'data': [{'hovertemplate': 'No=1<br>lat=%{lat}<br>lon=%{lon}<extra></extra>', 'lat': [1.30895], 'legendgroup': '1', 'lon': [103.77163], 'marker': {'color': '#FFA15A'}, 'mode': 'markers', 'name': '1', 'showlegend': True, 'subplot': 'mapbox', 'type': 'scattermapbox'},
 #         {'hovertemplate': 'No=2<br>lat=%{lat}<br>lon=%{lon}<extra></extra>', 'lat': [1.34905], 'legendgroup': '2', 'lon': [103.74458], 'marker': {'color': '#19d3f3'}, 'mode': 'markers', 'name': '2', 'showlegend': True, 'subplot': 'mapbox', 'type': 'scattermapbox'},
  #        {'hovertemplate': 'No=3<br>lat=%{lat}<br>lon=%{lon}<extra></extra>', 'lat': [1.31435], 'legendgroup': '3', 'lon': [103.76524], 'marker': {'color': '#FF6692'}, 'mode': 'markers', 'name': '3', 'showlegend': True, 'subplot': 'mapbox', 'type': 'scattermapbox'},
   #       {'hovertemplate': 'No=4<br>lat=%{lat}<br>lon=%{lon}<extra></extra>', 'lat': [1.30901], 'legendgroup': '4', 'lon': [103.76902], 'marker': {'color': '#B6E880'}, 'mode': 'markers', 'name': '4', 'showlegend': True, 'subplot': 'mapbox', 'type': 'scattermapbox'}],
 #'layout': {'template': {'data': {'histogram2dcontour': [{'type': 'histogram2dcontour', 'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'colorscale': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']]}], 'choropleth': [{'type': 'choropleth', 'colorbar': {'outlinewidth': 0, 'ticks': ''}}], 'histogram2d': [{'type': 'histogram2d', 'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'colorscale': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']]}], 'heatmap': [{'type': 'heatmap', 'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'colorscale': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']]}], 'heatmapgl': [{'type': 'heatmapgl', 'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'colorscale': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']]}], 'contourcarpet': [{'type': 'contourcarpet', 'colorbar': {'outlinewidth': 0, 'ticks': ''}}], 'contour': [{'type': 'contour', 'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'colorscale': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']]}], 'surface': [{'type': 'surface', 'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'colorscale': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']]}], 'mesh3d': [{'type': 'mesh3d', 'colorbar': {'outlinewidth': 0, 'ticks': ''}}], 'scatter': [{'fillpattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}, 'type': 'scatter'}], 'parcoords': [{'type': 'parcoords', 'line': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'scatterpolargl': [{'type': 'scatterpolargl', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'bar': [{'error_x': {'color': '#2a3f5f'}, 'error_y': {'color': '#2a3f5f'}, 'marker': {'line': {'color': '#E5ECF6', 'width': 0.5}, 'pattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}}, 'type': 'bar'}], 'scattergeo': [{'type': 'scattergeo', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'scatterpolar': [{'type': 'scatterpolar', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'histogram': [{'marker': {'pattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}}, 'type': 'histogram'}], 'scattergl': [{'type': 'scattergl', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'scatter3d': [{'type': 'scatter3d', 'line': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'scattermapbox': [{'type': 'scattermapbox', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'scatterternary': [{'type': 'scatterternary', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'scattercarpet': [{'type': 'scattercarpet', 'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}}], 'carpet': [{'aaxis': {'endlinecolor': '#2a3f5f', 'gridcolor': 'white', 'linecolor': 'white', 'minorgridcolor': 'white', 'startlinecolor': '#2a3f5f'}, 'baxis': {'endlinecolor': '#2a3f5f', 'gridcolor': 'white', 'linecolor': 'white', 'minorgridcolor': 'white', 'startlinecolor': '#2a3f5f'}, 'type': 'carpet'}], 'table': [{'cells': {'fill': {'color': '#EBF0F8'}, 'line': {'color': 'white'}}, 'header': {'fill': {'color': '#C8D4E3'}, 'line': {'color': 'white'}}, 'type': 'table'}], 'barpolar': [{'marker': {'line': {'color': '#E5ECF6', 'width': 0.5}, 'pattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}}, 'type': 'barpolar'}], 'pie': [{'automargin': True, 'type': 'pie'}]}, 'layout': {'autotypenumbers': 'strict', 'colorway': ['#636efa', '#EF553B', '#00cc96', '#ab63fa', '#FFA15A', '#19d3f3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'], 'font': {'color': '#2a3f5f'}, 'hovermode': 'closest', 'hoverlabel': {'align': 'left'}, 'paper_bgcolor': 'white', 'plot_bgcolor': '#E5ECF6', 'polar': {'bgcolor': '#E5ECF6', 'angularaxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': ''}, 'radialaxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': ''}}, 'ternary': {'bgcolor': '#E5ECF6', 'aaxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': ''}, 'baxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': ''}, 'caxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': ''}}, 'coloraxis': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'colorscale': {'sequential': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']], 'sequentialminus': [[0, '#0d0887'], [0.1111111111111111, '#46039f'], [0.2222222222222222, '#7201a8'], [0.3333333333333333, '#9c179e'], [0.4444444444444444, '#bd3786'], [0.5555555555555556, '#d8576b'], [0.6666666666666666, '#ed7953'], [0.7777777777777778, '#fb9f3a'], [0.8888888888888888, '#fdca26'], [1, '#f0f921']], 'diverging': [[0, '#8e0152'], [0.1, '#c51b7d'], [0.2, '#de77ae'], [0.3, '#f1b6da'], [0.4, '#fde0ef'], [0.5, '#f7f7f7'], [0.6, '#e6f5d0'], [0.7, '#b8e186'], [0.8, '#7fbc41'], [0.9, '#4d9221'], [1, '#276419']]}, 'xaxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': '', 'title': {'standoff': 15}, 'zerolinecolor': 'white', 'automargin': True, 'zerolinewidth': 2}, 'yaxis': {'gridcolor': 'white', 'linecolor': 'white', 'ticks': '', 'title': {'standoff': 15}, 'zerolinecolor': 'white', 'automargin': True, 'zerolinewidth': 2}, 'scene': {'xaxis': {'backgroundcolor': '#E5ECF6', 'gridcolor': 'white', 'linecolor': 'white', 'showbackground': True, 'ticks': '', 'zerolinecolor': 'white', 'gridwidth': 2}, 'yaxis': {'backgroundcolor': '#E5ECF6', 'gridcolor': 'white', 'linecolor': 'white', 'showbackground': True, 'ticks': '', 'zerolinecolor': 'white', 'gridwidth': 2}, 'zaxis': {'backgroundcolor': '#E5ECF6', 'gridcolor': 'white', 'linecolor': 'white', 'showbackground': True, 'ticks': '', 'zerolinecolor': 'white', 'gridwidth': 2}}, 'shapedefaults': {'line': {'color': '#2a3f5f'}}, 'annotationdefaults': {'arrowcolor': '#2a3f5f', 'arrowhead': 0, 'arrowwidth': 1}, 'geo': {'bgcolor': 'white', 'landcolor': '#E5ECF6', 'subunitcolor': 'white', 'showland': True, 'showlakes': True, 'lakecolor': 'white'}, 'title': {'x': 0.05}, 'mapbox': {'style': 'light'}}}, 'mapbox': {'domain': {'x': [0, 1], 'y': [0, 1]}, 'center': {'lat': 1.32034, 'lon': 103.7626175}, 'zoom': 11, 'style': 'carto-darkmatter'}, 'legend': {'title': {'text': 'No'}, 'tracegroupgap': 0}, 'margin': {'t': 0, 'r': 0, 'l': 0, 'b': 0}, 'height': 500, 'width': 1000, 'showlegend': False}
 #}

'''
 
 
blob = bucket.blob("unit_location.txt")
msg_xdecode = blob.download_as_string()
message = msg_xdecode.decode('utf-8')
data=message.split("\r\n")
unit_data=[i.split(",") for i in data if len(i)>1]

print(len(unit_data[0]))
ud=pd.DataFrame(unit_data,columns=["No",'Address','Unit','Postal ID','lat','lon','Fall Status','Sensors'])
#display_ud=ud.drop(ud.columns[[4,7]],axis = 1)
    #display_ud=display_ud.rename(columns={'lon':'Fall Status'})
display_ud=ud

#print(ud)
print("Address page")
print(ud.to_dict('records'))


#mapbox testing
ud['lat']=pd.to_numeric(ud['lat'])
ud['lon']=pd.to_numeric(ud['lon'])


fig2 = px.scatter_mapbox(
    ud.to_dict('list'),
    lat="lat",
    lon="lon",

    color="No",
    #color=['priority 4','priority 4','priority 2','priority 1'],
    color_discrete_map={'Priority 4':'green','Priority 3':'orange','Priority 2':'orange','Priority 1':'red'},

    zoom=11,
    height=500,
    width=1000
)
fig2.update_layout(mapbox_style="carto-darkmatter",showlegend=False)
fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig2.update_traces(marker=dict(color='red'))
#fig2.update_layout(mapbox_bounds={"west": -180, "east": -50, "south": 20, "north": 90})
 '''