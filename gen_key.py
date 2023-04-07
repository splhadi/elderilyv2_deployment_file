import secrets
global url_secret
global dash_session
global DASH_URL_BASE
global session_temp
DASH_INIT='/<path:parent_path>/dash/'
session_temp=''
#DASH_URL_BASE='/test/dash/'
#url_secret=secrets.token_urlsafe(4)
#url_secret="dash"
#print(url_secret)

def update_url_secret():
    global url_secret
    url_secret.pop()
    url_secret.append(secrets.token_urlsafe(4))