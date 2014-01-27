# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy utilities"""

from .settings import *
from urllib import urlencode
from urllib2 import HTTPCookieProcessor, build_opener, Request, urlopen, ProxyHandler, getproxies, URLError, HTTPErrorProcessor
from httplib import BadStatusLine
import cookielib, urlparse
import json, csv
from time import sleep
import datetime
import logging
from HTMLParser import HTMLParser
import xml.etree.ElementTree as ET
import bs4
import re
import codecs

def urlrequest(url, xml = False, **kargv):
    data = linkrequest(url, **kargv)
    try:
        if xml:
            tree = ET.fromstring(data)
        else:
            tree = bs4.BeautifulSoup(data.decode('utf-8', 'replace'), 'html5lib')
        return tree
    except AttributeError:
        return None

def jsonrequest(url, **kargv):
    data = linkrequest(url, **kargv)
    try:
        return json.loads(data.decode('utf-8', 'replace'))
    except AttributeError:
        return None
    except:
        logging.error(u'JSON DECODING ERROR: {} -- {}'.format(url, data))
        return None

def linkrequest(url, params = {}, noerrors = False, get = False, encode_params = True, log_activity = True, **kargv):
    errorcount = 0
    if encode_params:
        try:
            cparams = urlencode(params)
        except:
            logging.critical(u'LINKREQUEST: {}'.format(url))
    else:
        cparams = params
    sleeper = 1
    if get:
        request=Request(url)
    else:
        request=Request(url, headers={}, data=cparams)
    while True:
        try:
            req = urlopen(request)
            return req.read()
        except URLError as e:
            if log_activity:
                logging.critical(u'URLError: {}, {}'.format(e, url))
            if 'HTTP Error 404' in str(e):
                logging.critical(u'URLError: Return None')
                return None
            elif 'HTTP Error 400' in str(e):
                logging.critical(u'URLError: Return None')
                return None
            elif 'Gateway Time-out' in str(e):
                sleep(20)
                pass
            elif 'EOF occurred in violation of protocol' in str(e):
                sleep(5)
                pass
            elif 'Service Unavailable' in str(e):
                sleep(60)
                pass
            elif 'HTTP Error 500' in str(e):
                sleep(60)
                pass
            elif 'HTTP Error 504' in str(e):
                sleep(10)
                pass
            elif 'HTTP Error 503' in str(e):
                sleep(10)
                pass
            else:
                logging.critical(u'URLError: Return None')
                return None
        except BadStatusLine:
            sleep(4)
            pass

def browserrequest(opener, request):
    while True:
        try:
            p = opener.open(request)
            return p, opener
        except URLError as e:
            if 'HTTP Error 404' in str(e):
                logging.critical(u'URLError: Return None')
                return None, opener
            elif 'HTTP Error 400' in str(e):
                logging.critical(u'URLError: Return None')
                return None, opener
            elif 'Gateway Time-out' in str(e):
                sleep(20)
                pass
            elif 'EOF occurred in violation of protocol' in str(e):
                sleep(5)
                pass
            elif 'Service Unavailable' in str(e):
                sleep(60)
                pass
            elif 'HTTP Error 500' in str(e):
                sleep(60)
                pass
            elif 'HTTP Error 504' in str(e):
                sleep(10)
                pass
            elif 'HTTP Error 503' in str(e):
                sleep(10)
                pass
            else:
                logging.critical(u'URLError: Return None. {}'.format(str(e)))
                return None, opener
        except BadStatusLine:
            sleep(4)
            pass

def csvdump(destination, datum, delim = ';', new = True):
    if new:
        dest = open(destination, 'w')
        dest.write(codecs.BOM_UTF8)
    else:
        dest = open(destination, 'a')
    myWriter = csv.writer(dest, delimiter=delim, lineterminator='
')
    for row in datum:
        row1 = []
        for r in row:
            try: r = r.encode('utf-8')
            except: pass
            row1.append(r)
        myWriter.writerow(row1)
    dest.close()

def csvload(source, delim = ';'):
    sour = open(source, 'r')
    myReader = csv.reader(sour, delimiter=delim, lineterminator='
')
    worktable = []
    for row in myReader:
        row1 = []
        for element in row:
            try:
                element = element.decode('utf-8')
            except:
                pass
            try:
                element = int(element)
            except:
                try:
                    element = float(element)
                except:
                    pass
            row1.append(element)
        worktable.append(row1)
    return worktable

def jsondump(destination, data_structure):
    jtm = json.dumps(data_structure)
    dest = open(destination, 'w')
    logging.info(u'JSON-dump created: {}'.format(destination))
    dest.write(jtm)
    dest.close()

def jsonload(source):
    sour = open(source, 'r')
    ret_data = json.load(sour)
    sour.close()
    logging.info(u'JSON-dump loaded: {}'.format(source))
    return ret_data

def strip_tags(html):
    soup = bs4.BeautifulSoup('<tree>'+html+'</tree>')
    for tag in soup.findAll(True):
        tag.append(' ')
        tag.replaceWithChildren()
    result = unicode(soup)
    result = re.sub(' +', ' ', result, flags=re.UNICODE)
    result = re.sub(r' ([\.,;:?!])', r'\1', result, flags=re.UNICODE)
    return result.strip()

def strip_spaces(text):
    text = re.sub('
[ ]+', '
', text, flags=re.UNICODE)
    while True:
        newtext = text.replace('

', '  ')
        if newtext == text:
            break
        else:
            text = newtext
    text = re.sub('(^
)|(
$)', '', text, flags=re.UNICODE)
    text = re.sub('\s
', ' ', text, flags=re.UNICODE)
    return text

def check_dublicates_by_id(list_of_dicts, check_var):
    retdict = {}
    for element in list_of_dicts:
        retdict[element[check_var]] = element
    return retdict.values()

def check_dublicates_complete(list_of_dicts):
    retdict = []
    for element in list_of_dicts:
        if element not in retdict:
            retdict.append(element)
    return retdict

def vk_auth(app_id, app_secret, login, password, scope='groups,friends'):
    '''
    Create access token for VKontakte from
    app id, app secret, user's login and password.
    Without browser (could be used on server side).
    '''
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    cj = cookielib.CookieJar()
    vk_browser=build_opener(ProxyHandler(getproxies()), HTTPCookieProcessor(cj))
    url = 'http://m.vk.com'
    request = Request(url, headers=headers)
    p, vk_browser = browserrequest(vk_browser, request)
    url = re.search('<form method=\"post\" action=\"([^\"]+)"',p.read()).group(1)
    params = {
        'email':login.encode('utf-8'),
        'pass':password.encode('utf-8')
    }
    cparams = urlencode(params)
    request = Request(url, headers=headers, data=cparams)
    p, vk_browser = browserrequest(vk_browser, request)
    url = 'https://oauth.vk.com/authorize?client_id={}&scope={}&redirect_uri=http://api.vk.com/blank.html&display=page&response_type=code'.format(app_id, scope)
    request = Request(url, headers=headers)
    p, vk_browser = browserrequest(vk_browser, request)
    url = None
    for furl in re.findall('location.href = \"([^\"]+)\"', p.read()):
        if 'login.vk.com' in furl and 'cancel' not in furl:
            url = furl
            break
    if url:
        request = Request(url, headers=headers)
        p, vk_browser = browserrequest(vk_browser, request)
    tree = urlparse.parse_qs(urlparse.urlparse(p.geturl()).fragment)
    try:
        code = tree['code'][0]
    except:
        return None
    vkapi = {
        'client_id':app_id,
        'client_secret':app_secret,
        'redirect_uri':'http://api.vk.com/blank.html',
        'scope':scope,
        'code':code
        }
    try:
        return jsonrequest('https://oauth.vk.com/access_token', params = vkapi)['access_token']
    except:
        return None

def fb_auth(app_id, app_secret, app_url, login, password):
    import httplib
    httplib.HTTPConnection.debuglevel = 1

    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    cj = cookielib.CookieJar()
    fb_browser=build_opener(ProxyHandler(getproxies()), HTTPCookieProcessor(cj), MyHTTPErrorProcessor)
    url = 'http://m.facebook.com'
    request = Request(url, headers=headers)
    p, fb_browser = browserrequest(fb_browser,request)
    p = p.read()
    url = re.search('<form method=\"post\" class=\"mobile-login-form _[a-zA-Z0-9]+\" id=\"login_form\" novalidate=\"1\" action=\"([^\"]+)\">',p).group(1)
    params = {
        'lsd': re.search('name=\"lsd\" value=\"([^\"]+)\"',p).group(1),
        'charset_test': re.search('name=\"charset_test\" value=\"([^\"]+)\"',p).group(1),
        'version': re.search('name=\"version\" value=\"([^\"]+)\"',p).group(1),
        'ajax': re.search('name=\"ajax\" value=\"([^\"]+)\"',p).group(1),
        'width': re.search('name=\"width\" value=\"([^\"]+)\"',p).group(1),
        'pxr': re.search('name=\"pxr\" value=\"([^\"]+)\"',p).group(1),
        'gps': re.search('name=\"gps\" value=\"([^\"]+)\"',p).group(1),
        'm_ts': re.search('name=\"m_ts\" value=\"([^\"]+)\"',p).group(1),
        'li': re.search('name=\"li\" value=\"([^\"]+)\"',p).group(1),
        'signup_layout': re.search('name=\"signup_layout\" value=\"([^\"]+)\"',p).group(1),
        'email': login,
        'pass': password,
        'login': re.search('value=\"([^\"]+)\" type=\"submit\" name=\"login\"',p).group(1),
    }
    cparams = urlencode(params)
    request = Request(url, headers=headers, data=cparams)
    p, fb_browser = browserrequest(fb_browser, request)
    url = 'https://www.facebook.com/dialog/oauth?client_id={}&redirect_uri={}'.format(app_id, app_url)
    request = Request(url, headers=headers)
    p, fb_browser = browserrequest(fb_browser, request)
    if 'Location' not in p.info() or 'code=' not in p.info()['Location']:
        return None
    code = urlparse.parse_qs(urlparse.urlparse(p.info()['Location']).query)['code'][0]
    url = 'https://graph.facebook.com/oauth/access_token'
    params = urlencode({
        'client_id': app_id,
        'redirect_uri':app_url,
        'client_secret':app_secret,
        'code':code})
    request=Request(url, headers=headers, data=params)
    p, fb_browser = browserrequest(fb_browser, request)
    tree=urlparse.parse_qs(p.read())
    return tree['access_token'][0]

def ok_auth(raw_token):
    if 'refresh_token' in raw_token and raw_token['refresh_token'] and (datetime.datetime.now() - raw_token['refresh_token']['timestamp']).days < 30:
        url = 'http://api.odnoklassniki.ru/oauth/token.do'
        params = {'refresh_token':raw_token['refresh_token']['token'],
                  'grant_type':'refresh_token',
                  'client_id':raw_token['app_id'],
                  'client_secret':raw_token['app_secret']}
        access_data = jsonrequest(url, params = params)
        return {'app_key':raw_token['app_key'], 'app_secret':raw_token['app_secret'], 'access_token':access_data['access_token']}, raw_token

    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    cj = cookielib.CookieJar()
    ok_opener=build_opener(ProxyHandler(getproxies()), HTTPCookieProcessor(cj), MyHTTPErrorProcessor)
    url = 'http://m.odnoklassniki.ru/'
    request = Request(url, headers = headers)
    while True:
        try:
            p, ok_opener = browserrequest(ok_opener, request)
            break
        except BadStatusLine:
            sleep(2)
            pass
    tkn = re.search(r'/dk\?bk=GuestMain&amp;st\.cmd=main&amp;_prevCmd=main&amp;tkn=([0-9]{2,4})', p.read()).group(1)
    params = urlencode({'fr.posted': 'set',
                        'fr.needCaptcha': '',
                        'fr.login': raw_token['login'],
                        'fr.password': raw_token['password'],
                        'button_login': 'Войти'})
    request = Request('http://m.odnoklassniki.ru/dk?bk=GuestMain&st.cmd=main&tkn={0}'.format(tkn), headers = headers, data = params)
    sleep(2)
    p, ok_opener = browserrequest(ok_opener, request)
    url = 'http://www.odnoklassniki.ru/dk?st.cmd=OAuth2Permissions&st.scope=VALUABLE+ACCESS&st.response_type=code&st.redirect_uri=http%3A%2F%2Flocalhost&st.client_id={}&st.show_permissions=off'.format(raw_token['app_id'])
    request = Request(url, headers = headers)
    p, ok_opener = browserrequest(ok_opener, request)
    try:
        code = urlparse.parse_qs(urlparse.urlparse(p.info()['Location']).query)['code'][0]
    except AttributeError:
        p = p.read()
        key = re.search(r'name=\"fr.submitKey\" value=\"([^\"]+)\"', p).group(1)
        url = 'http://www.odnoklassniki.ru/dk?cmd=OAuth2Permissions&st.cmd=OAuth2Permissions&st.scope=VALUABLE+ACCESS&st.response_type=code&st.redirect_uri=http%3A%2F%2Flocalhost&st.client_id={}&st.show_permissions=off'.format(raw_token['app_id'])
        params = urlencode({'fr.posted': 'set',
                            'fr.submitKey': key,
                            'button_accept_request':'clicked',
                            'hook_form_button_click':'button_accept_request'})
        request = Request(url, headers = headers, data = params)
        p, ok_opener = browserrequest(ok_opener, request)
        code = urlparse.parse_qs(urlparse.urlparse(p.info()['Location']).query)['code'][0]
    url = 'http://api.odnoklassniki.ru/oauth/token.do'
    params = {'code':code,
              'redirect_uri':'http://localhost',
              'grant_type':'authorization_code',
              'client_id':raw_token['app_id'],
              'client_secret':raw_token['app_secret']}
    access_data = jsonrequest(url, params = params)
    raw_token['refresh_token'] = {'timestamp':datetime.datetime.now(), 'token':access_data['refresh_token']}
    return {'app_key':raw_token['app_key'], 'app_secret':raw_token['app_secret'], 'access_token':access_data['access_token']}, raw_token

class MyHTTPErrorProcessor(HTTPErrorProcessor):
    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        #print response.code
        #print response.info()
        #print response.msg

        # only add this line to stop 302 redirection.
        if code == 302: return response

        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response
    https_response = http_response