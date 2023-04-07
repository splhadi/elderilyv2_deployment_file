from dash import Dash, html, dcc, callback, Input,Output,State
import dash
import dash_bootstrap_components as dbc
import ast
from flask import Flask, session, abort,redirect,request, render_template, flash, make_response
from pages import GCP_class
import time
from functools import wraps
#import dash_auth
import gen_key
import urllib.parse
import os
import pathlib
from google_auth_oauthlib.flow import Flow
import secrets
from google.oauth2 import id_token
import google.auth.transport.requests
import requests
from datetime import datetime
from pip._vendor import cachecontrol
import pytz

#setting CSS sylesheets
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

external_stylesheets = [dbc.themes.CYBORG,dbc_css]

#server and dashboard initialization

gen_key.url_secret=[secrets.token_urlsafe(4)]
url_secret=gen_key.url_secret
print("app.py url:",gen_key.url_secret[0])

#initialise flask
server_flask = Flask(__name__)
server_flask.secret_key = secrets.token_urlsafe(128)



gen_key.DASH_URL_BASE='/'+secrets.token_urlsafe(32)+'/dash/'

#for debugging only at dash side
#gen_key.DASH_URL_BASE='/dash/'
#app = Dash(__name__, use_pages=True,external_stylesheets=external_stylesheets,url_base_pathname=gen_key.DASH_URL_BASE)

app = Dash(__name__,server=server_flask, use_pages=True,
           external_stylesheets=external_stylesheets,
           url_base_pathname=gen_key.DASH_URL_BASE,
           meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
           )

#Google client oauth ID
GOOGLE_CLIENT_ID='8823199232-4rranl775jq8n0g60viqp2gg7aq8oq26.apps.googleusercontent.com'
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    #redirect_uri="http://127.0.0.1:5000/callback"
    redirect_uri='https://elderilyv2-3f5k5qq63a-as.a.run.app/callback'
)


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


#establishing final link
final_link = urllib.parse.quote(gen_key.DASH_URL_BASE+'/')
print('http://127.0.0.1:8050/'+final_link)

# authentication details
jsonfile="cred_details.json"
bucket_name = "ee4002d_bucket"
server = GCP_class.Server(bucket_name, jsonfile)

#retrieve logos for dash dashboard
img=server.retrieve_img('page_icon.png')
img_footer=server.retrieve_img('NUS-logo.png')
img_id=''



nav=dbc.Nav([
    dbc.NavItem(dcc.Link("Home", href="/", refresh=True)),
    dbc.NavItem(dcc.Link("Dashboard", href="/dashboard", refresh=True)),
  dbc.NavItem(dbc.NavLink("Home", href="/",external_link=True,active=True)),
  dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard",external_link=True)),
dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Profile page",href="/profile",id="profile-ddm",disabled=True,external_link=True),
                dbc.DropdownMenuItem("Lidar readings", href="/lidar",id='lidar-ddm',disabled=True,external_link=True),
                dbc.DropdownMenuItem("Pressure tile", href="/pressure",id='pressure-ddm',disabled=True,external_link=True),
            ],
    nav=True,
    in_navbar=True,
    label="More",
)


])

menu_list = dbc.Row(
    children=[
        dbc.Col(dbc.NavItem(dbc.NavLink("Manage User", href=gen_key.DASH_URL_BASE+"manage_user",id="text1-ddm",disabled=False,external_link=True))),
        dbc.Col(dbc.NavItem(dbc.NavLink("Dashboard", href=gen_key.DASH_URL_BASE+"dashboard",id="text2-ddm",disabled=False,external_link=True))),
        dbc.Col(dbc.NavItem(dbc.NavLink("Home", href=gen_key.DASH_URL_BASE,external_link=True))),
        dbc.Col(dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Profile page", href=gen_key.DASH_URL_BASE+"profile",id="profile-ddm",disabled=True,external_link=True),
                dbc.DropdownMenuItem("Lidar readings", href=gen_key.DASH_URL_BASE+"lidar",id='lidar-ddm',disabled=True,external_link=True),
                dbc.DropdownMenuItem("Pressure tile", href=gen_key.DASH_URL_BASE+"pressure",id='pressure-ddm',disabled=True,external_link=True),
                #dbc.DropdownMenuItem("Logout", href="/logout",external_link=True),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        )),
        dbc.Col(dbc.Button(html.Img(src='', height="30px",id='profile-pic'),color='secondary',id='profile-popover'))
    ],
    className="g-2 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=img, height="60px")),
                        dbc.Col(dbc.NavbarBrand("Fall Detection System", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href=gen_key.DASH_URL_BASE,
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            #nav,
            dbc.Collapse(
                children=[menu_list],
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]#end of dbc container
    ),
    color="secondary",
    dark=True,
)
footer=html.Div([
html.Br(),
html.Hr(className="my-2"),

dbc.Row([dbc.Col([html.Img(src=img_footer,height="90px")],width=3),
         dbc.Col([html.P("\u00A9 Copyright 2023: All rights reserved to NUS.")]),
         dbc.Col([html.P("",id='session-text')]),
         ],align="center"),


],style={'color':'white'})


profile_card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        src="",
                        #style={'height':"50px"},
                        className="img-fluid rounded-start",
                        id='profile-pic-2'
                    ),
                    className="col-md-4",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            html.H5("Card title",className="card-title", id="profile-name"),
                            html.P(
                                "Some text.",
                                id="profile-email",
                                className="card-text",
                            ),
                            html.Small(
                                "Last updated 3 mins ago",
                                className="card-text text-muted",
                                id='profile-login-text'
                            ),
                        ]
                    ),
                    className="col-md-8",
                ),
            ],
            className="g-0 d-flex align-items-center",
        ),
   # dbc.CardFooter(
        dbc.Row([dbc.Col(dbc.Button('Google account',outline=True,size='sm',color='info',href='https://myaccount.google.com/')),
                            dbc.Col(dbc.Button('Log Out',outline=True,size='sm',color='info',href='/logout',external_link=True))
                            ],justify='end')
             #      ),
    ],
    className="mb-3",
    style={"max-width": "600px"},
)

fall_text=html.P(dbc.Collapse(
    dbc.Alert([html.P("", id='fall-text'), html.P("", id='fall-sensor'), html.P("", id='fall-postal')], color="info",
              id="fall-popup"), is_open=False, id='fall-collapse'))

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    navbar,
    fall_text,
    dcc.Store(id="pressure-gcp"),
    dcc.Store(id="pressure-result"),
    dcc.Store(id="2d-result-storage"),
    dcc.Store(id="3d-result-storage"),
    dcc.Store(id="unconscious-result-storage"),
    dcc.Store(id="main-storage",storage_type="session"),
    dcc.Store(id="address_unit",storage_type="session"),
    dcc.Store(id="coordinates",storage_type="session"),
    dcc.Interval(       id='main-update',
        interval=1 * 5000, n_intervals=0),
    dbc.Row([
        #dbc.Col("",width=1),
        dbc.Col(dash.page_container,width=11),
        #dbc.Col("",width=1),
    ],justify='center'
    ),
	#dash.page_container,
    html.Footer(footer),

    dbc.Popover(
        [profile_card

        ],
        id="popover",
        trigger="legacy",
        placement='bottom',
        body=True,
        target="profile-popover",
        style={"max-width": "700px  ",'width':'400px'}
    ),

])

@app.callback(
    Output('url', 'pathname'),
    Output('profile-pic','src'),
    Output('profile-pic-2','src'),
    Output('profile-name','children'),
    Output('profile-email','children'),
    Output('profile-login-text','children'),
    Output('text1-ddm','children'),
    Output('text1-ddm','href'),
    Output('text2-ddm','children'),
    Output('text2-ddm','href'),
    Input('url', 'pathname')
)
def check_session_id(path):
    print("Checking sessionID")

    #remove this for flask implementation
    #session={'state':'True','picture':"",'name':'','email':'','time':'','user_type':'admin'}
    gen_key.dash_session=session
    #enable_admin=True
    #check for admin
    text1 = ''
    text_link1 = gen_key.DASH_URL_BASE
    text2='Dashboard'
    text_link2=gen_key.DASH_URL_BASE+"dashboard"


    if 'state' not in session:
        print("Session id not found. returning 403")

        return '/error','','','','','' ,text1,text_link1,text2,text_link2
    else:
        print('print:',gen_key.session_temp)
        print("Session ID found")
        if session['user_type'] == 'admin':
            #enable_admin = False
            text1 = 'Dashboard'
            text_link1 = gen_key.DASH_URL_BASE + "dashboard"
            text2 = 'Manage'
            text_link2 = gen_key.DASH_URL_BASE + "manage_user"
        return path,session['picture'],session['picture'],session['name'],session['email'],"Logged in at: "+session['time'],text1,text_link1,text2,text_link2


@callback(
    Output("fall-text",'children'),
    Output("fall-sensor",'children'),
    Output("fall-postal",'children'),
    Output("fall-popup",'color'),
    Output("fall-collapse",'is_open'),
    Output("2d-result-storage","data"),
    Output("3d-result-storage","data"),
    Output("pressure-result","data"),
    Output("unconscious-result-storage","data"),
    Input("main-update","n_intervals"),
    State(component_id="main-storage",component_property="data"),
)
def fall_check(interval,key):
    print("Beginning fall check... interval:",interval)
    #this will be the main fall check for all the detected falls
    alert=False
    if key is None:
        print("Key=None, no check done, returning")
        return "","","","",alert,"No data","No data","No data",'No data'


#chat id used for reference

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

    #print("Status:",fall_2d,fall_3d,fall_ps)
    print("\nChecking: ",key)

    pri_check,detected_fall_sensors=fall_priority(fall_2d,fall_uncon,fall_ps)
    color='info'
    if pri_check==1:   #priority 1
        message="URGENT! Priority 1 detected! All sensors have detected a fall. Please attend immediately!\n\n"
        sensors="Sensors detected: All sensors"
        address="Postal code: "+key+"\n\n"
        color='danger'
       # message=message+address
        alert=True
    elif pri_check==2: #priority 2
        message = "Warning! Priority 2 detected! Two sensors have detected a fall. Please attend immediately!\n"
        sensors="Sensors detected: "+",".join(detected_fall_sensors)+"\n"
        address="Postal code: "+key+"\n"

       # message = message + sensors + address
        color='warning'
        #print(message,sensors)
        alert=True
        pass
    elif pri_check==3: #priority 3
        message = "Caution! Priority 3 detected! One sensor have detected a fall.\n\n"
        sensors="Sensors detected: "+" ".join(detected_fall_sensors)+'\n\n'
        address="Postal code: "+key+"\n\n"

        alert=True
        color = 'warning'
        #message = message + sensors + address
        #print(message,sensors)
        pass
    else: #priority 4
        #print("Priority 4: all systems normal")
        message="Priority 4: all systems normal"
        sensors=""
        address=""
        alert=False
        pass

    print("Message issued:",message,"|Alert state:",alert)
    return message,sensors,address,color,alert,fall_2d,fall_3d,fall_ps,fall_uncon
    #alert the GUI




def fall_priority(f2d,f3d,fps):

    #simulation variables for testing
    #f2d = 'fall'
    #f3d = 'lying'
    #fps = "True"

    #new sensor to read conscious or unconscious

    count=4
    item=[]
    if f2d=="fall":
        count-=1
        item.append("2D Lidar")
    if fps=="True":
        count-=1
        item.append("Pressure Sensor")

    #if f3d=="lying" and (fps=="True" or f2d=="fall"):
    if f3d == "unconscious" and (f2d == "fall"):
        count-=1
        item.append("3D Lidar")

    return count,item

# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output(component_id="profile-ddm", component_property="disabled"),
    Output(component_id="lidar-ddm", component_property="disabled"),
    Output(component_id="pressure-ddm", component_property="disabled"),
    Output(component_id="text1-ddm", component_property="disabled"),
    Output(component_id="text2-ddm", component_property="disabled"),
    #Output(component_id="dashboard-ddm", component_property="disabled"),
    Input(component_id="main-storage",component_property="data"),


)
def check_selected_id(key):



    #simulation for dash version debug
    session=gen_key.dash_session
    print("ID STARTINGG",session['user_type'])

    if key is not None:#selected postal address
        if session['user_type']=='admin':
            return False, False, False, False, False
        else:
            return False,False,False,True,False
    else:# not selected address
        if session['user_type'] == 'admin':
            return True,True,True, True, False
        else:
            return True,True,True, True, True

#####################################################################################################################################
#flask portion
#####################################################################################################################################

#login wrapper
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

#no cache wrapper
@server_flask.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


#flask portion

@server_flask.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@server_flask.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    #set timezone
    now = datetime.now()
    asia_tz = pytz.timezone('Asia/Singapore')
    now = now.replace(tzinfo=pytz.utc).astimezone(asia_tz)
    dt_string = now.strftime("%H:%M:%S")

    #retrieve session details
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session['picture']=id_info.get('picture')
    session['given_name'] = id_info.get('given_name')
    session['time']=dt_string
    print(id_info)

    session['email']=session['email'].lower()
    gen_key.dash_session=session
    return redirect("/success")


@server_flask.route("/success")
@login_is_required
def success():
    data = server.retrieve_file_string('accounts.txt')
    res = ast.literal_eval(data)
    res['user']=[i.lower() for i in res['user']]
    flash('Login successful')
    if session['email']==res['admin']:
        session['user_type']='admin'
        return redirect('/access_dashboard')

        pass
    elif session['email'].lower() in res['user']:
        session['user_type'] = 'user'
        return redirect('/access_dashboard')

        pass
    else:
        return f"Not allowed to proceed !{session['name']} {session['google_id']} {session['email']}! " \
               f"<br/> <a href='/logout'><button>Logout</button></a>"
        pass



@server_flask.route("/access_dashboard")
def access_dashboard():
    if "google_id" not in session:
        return abort(401)  # Authorization required
    else:
        return redirect(gen_key.DASH_URL_BASE)



@server_flask.route('/logout')
#@no_cache
def logout():

    session.clear()

    #response = make_response('Logged out successfully!')
    #response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    #response.headers['Pragma'] = 'no-cache'
    #response.headers['Expires'] = '0'
    #return response

    time.sleep(1)


    return redirect("/")

def change_base_pathname(new_pathname):
    app.config.update({
        'routes_pathname_prefix': new_pathname,
        'requests_pathname_prefix': new_pathname
    })


@server_flask.route('/')
def login_page_load():
    test=""
    return render_template("Login.html")



@server_flask.route('/error')
def error_main():
    return redirect('/error403')

@server_flask.route('/error403')
def error():
    abort(403)
#@server_flask.route('/<path:parent_path>/dash')
#def dash():
 #   return redirect("/")

if __name__ == '__main__':
    #app.run_server(debug=True, dev_tools_hot_reload=False)
    #app.run_server(debug=False, host='0.0.0.0', port=8080)
    #server_flask.run(debug=True)
    server_flask.run(debug=False, host='0.0.0.0', port=8080)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8080)
