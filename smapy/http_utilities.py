# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy http-requests utilities"""

from smapy.settings import *
import logging

from urllib import urlencode
from urllib2 import HTTPCookieProcessor, build_opener, Request, urlopen, ProxyHandler, getproxies, URLError, HTTPErrorProcessor
from httplib import BadStatusLine
import cookielib, urlparse

from HTMLParser import HTMLParser
import xml.etree.ElementTree as ET
import bs4

import re
import json
from time import sleep

def get_url(url, params = {}, headers = {}, opener = None, read = True,
            noerrors = False, get = False, encode_params = True,
            log_activity = True, **kargv):
    errorcount = 0
    if encode_params:
        cparams = urlencode(params)
    else:
        cparams = params
    if get:
        request=Request(url, headers=headers)
    else:
        request=Request(url, headers=headers, data=cparams)
    while True:
        sleeptime = 0
        try:
            if opener:
                req = opener.open(request)
                if read:
                    return req.read(), opener
                else:
                    return req, opener
            else:
                req = urlopen(request)
                if read:
                    return req.read()
                else:
                    return req
        except URLError as e:
            if 'HTTP Error 404' in str(e):
                err_msg = u'404 - Not found - Return None.'

            elif 'HTTP Error 400' in str(e):
                err_msg = u'400 - Bad request - Return None.'

            elif 'Gateway Time-out' in str(e) or 'HTTP Error 504' in str(e):
                err_msg = u'504 - Gateway timeout - sleep (20).'
                sleeptime = 20

            elif 'EOF occurred in violation of protocol' in str(e):
                err_msg = u'EOF occurred - sleep (5).'
                sleeptime = 5

            elif 'Service Unavailable' in str(e) or 'HTTP Error 503' in str(e):
                err_msg = u'503 - Service unavailable - sleep (60).'
                sleeptime = 60

            elif 'HTTP Error 500' in str(e):
                err_msg = u'500 - Internal server error - sleep(60).'
                sleeptime = 60
            else:
                err_msg = unicode(str(e))

        except BadStatusLine:
            err_msg = u'BadStatusLine'
            sleeptime = 4

        if log_activity:
            logging.warning(u'GETTING URL: '+err_msg)

        if not sleeptime:
            if opener:
                return None, opener
            else:
                return None
        sleep(sleeptime)

def get_json(url, **kargv):
    data = get_url(url, **kargv)
    try:
        return json.loads(data.decode('utf-8', 'replace'))
    except AttributeError:
        return None
    except:
        logging.error(u'JSON DECODING ERROR: {} - {}'.format(url, data))
        return None

def get_html(url, xml = False, **kargv):
    data = get_url(url, **kargv)
    try:
        if xml:
            tree = ET.fromstring(data)
        else:
            tree = bs4.BeautifulSoup(data.decode('utf-8', 'replace'), 'html5lib')
        return tree
    except AttributeError:
        return None

def vk_auth(raw_token, scope='groups,friends'):
    """raw_token - dict with these keys:
- app_id,
- app_secret,
- login,
- password"""

    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    cj = cookielib.CookieJar()
    vk_browser=build_opener(ProxyHandler(getproxies()), HTTPCookieProcessor(cj))
    url = 'http://m.vk.com'
    p, vk_browser = get_url(url, opener = vk_browser, headers = headers, get = True)
    url = re.search('<form method=\"post\" action=\"([^\"]+)"',p).group(1)
    params = {
        'email':raw_token['login'].encode('utf-8'),
        'pass':raw_token['password'].encode('utf-8')
    }
    p, vk_browser = get_url(url, opener = vk_browser, headers = headers, params = params, read = False)
    url = 'https://oauth.vk.com/authorize?client_id={}&scope={}&redirect_uri=http://api.vk.com/blank.html&display=page&response_type=code'.format(raw_token['app_id'], scope)
    p, vk_browser = get_url(url, opener = vk_browser, headers=headers, get = True, read = False)
    url = None
    for furl in re.findall('location.href = \"([^\"]+)\"', p.read()):
        if 'login.vk.com' in furl and 'cancel' not in furl:
            url = furl
            break
    if url:
        p, vk_browser = get_url(url, opener = vk_browser, headers=headers, get = True, read = False)
    tree = urlparse.parse_qs(urlparse.urlparse(p.geturl()).fragment)
    try:
        code = tree['code'][0]
    except:
        return None
    vkapi = {
        'client_id':raw_token['app_id'],
        'client_secret':raw_token['app_secret'],
        'redirect_uri':'http://api.vk.com/blank.html',
        'scope':scope,
        'code':code
        }
    try:
        return get_json('https://oauth.vk.com/access_token', params = vkapi)['access_token']
    except:
        return None

def fb_auth(raw_token):
    """raw_token - dict with these keys:
- app_id,
- app_secret,
- app_url,
- login,
- password"""

    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    cj = cookielib.CookieJar()
    fb_browser=build_opener(ProxyHandler(getproxies()), HTTPCookieProcessor(cj), MyHTTPErrorProcessor)
    url = 'http://m.facebook.com'
    p, fb_browser = get_url(url, opener = fb_browser, get = True, headers = headers)
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
        'email': raw_token['login'],
        'pass': raw_token['password'],
        'login': re.search('value=\"([^\"]+)\" type=\"submit\" name=\"login\"',p).group(1),
    }
    p, fb_browser = get_url(url, opener = fb_browser, params = params, headers=headers, read = False)
    url = 'https://www.facebook.com/dialog/oauth?client_id={}&redirect_uri={}'.format(raw_token['app_id'], raw_token['app_url'])
    p, fb_browser = get_url(url, opener = fb_browser, headers=headers, get = True, read = False)
    if 'Location' not in p.info() or 'code=' not in p.info()['Location']:
        return None
    code = urlparse.parse_qs(urlparse.urlparse(p.info()['Location']).query)['code'][0]
    url = 'https://graph.facebook.com/oauth/access_token'
    params = {'client_id': raw_token['app_id'],
              'redirect_uri':raw_token['app_url'],
              'client_secret':raw_token['app_secret'],
              'code':code}
    p, fb_browser = get_url(url, opener = fb_browser, headers=headers, params=params)
    tree=urlparse.parse_qs(p)
    return tree['access_token'][0]

def ok_auth(raw_token):
    """raw_token - dict with these keys:
- app_id,
- app_key,
- app_secret,
- login,
- password,
- refresh_token = {'token':..., 'timestamp':...}"""

    if 'refresh_token' in raw_token and raw_token['refresh_token'] and (datetime.datetime.now() - raw_token['refresh_token']['timestamp']).days < 30:
        url = 'http://api.odnoklassniki.ru/oauth/token.do'
        params = {'refresh_token':raw_token['refresh_token']['token'],
                  'grant_type':'refresh_token',
                  'client_id':raw_token['app_id'],
                  'client_secret':raw_token['app_secret']}
        access_data = jsonrequest(url, params = params)
        raw_token['refresh_token'] = {'timestamp':datetime.datetime.now(), 'token':access_data['refresh_token']}
        return {'app_key':raw_token['app_key'], 'app_secret':raw_token['app_secret'], 'access_token':access_data['access_token']}, raw_token

    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:10.0.6) Gecko/20100101 Firefox/10.0.6',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

    cj = cookielib.CookieJar()
    ok_opener=build_opener(ProxyHandler(getproxies()), HTTPCookieProcessor(cj), MyHTTPErrorProcessor)
    url = 'http://m.odnoklassniki.ru/'
    p, ok_opener = get_url(url, headers = headers, opener = ok_opener, read = False, get = True)
    tkn = re.search(r'/dk\?bk=GuestMain&amp;st\.cmd=main&amp;_prevCmd=main&amp;tkn=([0-9]{2,4})', p.read()).group(1)
    url = 'http://m.odnoklassniki.ru/dk?bk=GuestMain&st.cmd=main&tkn={0}'.format(tkn)
    params = {'fr.posted': 'set',
              'fr.needCaptcha': '',
              'fr.login': raw_token['login'],
              'fr.password': raw_token['password'],
              'button_login': 'Войти'}
    sleep(2)
    p, ok_opener = get_url(url, headers = headers, params = params, opener = ok_opener, read = False)

    url = 'http://www.odnoklassniki.ru/dk?st.cmd=OAuth2Permissions&st.scope=VALUABLE+ACCESS&st.response_type=code&st.redirect_uri=http%3A%2F%2Flocalhost&st.client_id={}&st.show_permissions=off'.format(raw_token['app_id'])
    p, ok_opener = get_url(url, headers = headers, opener = ok_opener, read = False, get = True)
    try:
        code = urlparse.parse_qs(urlparse.urlparse(p.info()['Location']).query)['code'][0]
    except AttributeError:
        p = p.read()
        key = re.search(r'name=\"fr.submitKey\" value=\"([^\"]+)\"', p).group(1)
        url = 'http://www.odnoklassniki.ru/dk?cmd=OAuth2Permissions&st.cmd=OAuth2Permissions&st.scope=VALUABLE+ACCESS&st.response_type=code&st.redirect_uri=http%3A%2F%2Flocalhost&st.client_id={}&st.show_permissions=off'.format(raw_token['app_id'])
        params = {'fr.posted': 'set',
                  'fr.submitKey': key,
                  'button_accept_request':'clicked',
                  'hook_form_button_click':'button_accept_request'}
        p, ok_opener = get_url(url, headers = headers, params = params, opener = ok_opener, read = False)
        code = urlparse.parse_qs(urlparse.urlparse(p.info()['Location']).query)['code'][0]
    url = 'http://api.odnoklassniki.ru/oauth/token.do'
    params = {'code':code,
              'redirect_uri':'http://localhost',
              'grant_type':'authorization_code',
              'client_id':raw_token['app_id'],
              'client_secret':raw_token['app_secret']}
    access_data = get_json(url, params = params)
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