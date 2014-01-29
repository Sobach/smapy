# -*- coding: utf-8 -*-
#!/usr/bin/env python

from base import *
from settings import *
from http_utilities import get_json
import logging
import hashlib
from urllib import urlencode

class OdnoklassnikiConnector(BaseConnector):
    """Connector to Odnoklassniki social network (http://odnoklassniki.ru)."""
    def __init__(self, **kargv):
        self.network = u'ok'
        BaseConnector.__init__(self, **kargv)

    def _token_checker(self):
        data = self.__api_request__('friends.get')
        if not data or (isinstance(data, dict) and 'error_code' in data.keys()):
            logging.critical(u'OK: Access token is not valid.')
            self._token_ok = False
            return False
        self._token_ok = True
        return True

    def __api_request__(self, method, **kargv):
        if 'params' in kargv:
            params = kargv['params']
        else:
            params = {}
        print params
        url = 'http://api.odnoklassniki.ru/fb.do'
        params['format'] = 'JSON'
        params['method'] = method
        params['application_key'] = self.token['app_key']
        secret_key = hashlib.md5('{}{}'.format(self.token['access_token'], self.token['app_secret'])).hexdigest()
        params['sig'] = hashlib.md5((''.join(['{}={}'.format(p[0], p[1]) for p in sorted(params.items(), key=lambda x:x[0])]) + secret_key).encode('utf-8')).hexdigest().lower()
        print params
        params['access_token'] = self.token['access_token']
        url = '{}?{}'.format(url, urlencode(params))
        return get_json(url, get= True)
        print params

    @need_token
    def get_profiles(self, token, **kargv):
        logging.warning(u'OK: Number of followers only avaliable for pages (and groups).')
        step = 90
        retdict = {}
        userslist = {}
        grouplist = {}
        for user in self.accounts.keys():
            print self.token
            resp = self.__api_request__('adv.getOdnoklassnikiUrlType', {'url':'http://www.odnoklassniki.ru/{}'.format(self.accounts[user])}, in_session=False)
            logging.debug(u'OK: {}'.format(resp))
            if not resp or resp['type'] == 'UNKNOWN':
                retdict[user] = None
                continue
            retdict[user] = {'id':str(resp['objectId']), 'link':'http://www.odnoklassniki.ru/{}'.format(self.accounts[user])}
            if resp['type'] == 'PROFILE':
                retdict[user]['type'] = 'person'
                userslist[user] = resp['objectId']
            else:
                retdict[user]['type'] = 'page'
                grouplist[user] = resp['objectId']
        users = {}
        for i in range(0, len(userslist), step):
            idl = ','.join([str(x) for x in userslist.values()[i:i+step]])
            resp = self.__api_request__('users.getInfo',{'uids':idl,'fields':'uid,name','emptyPictures':'true'})
            users.update({str(x['uid']):x for x in resp})
        for i in range(0, len(grouplist), step):
            idl = ','.join([str(x) for x in grouplist.values()[i:i+step]])
            resp = self.__api_request__('group.getInfo',{'uids':idl,'fields':'uid,name,shortname,members_count'})
            users.update({str(x['uid']):x for x in resp})
        for user in retdict.keys():
            if retdict[user]['id'] not in users.keys():
                retdict[user] = None
                continue
            try:
                retdict[user]['name'] = users[retdict[user]['id']]['name']
            except KeyError:
                retdict[user]['name'] = 'NA'

            try:
                retdict[user]['nickname'] = users[retdict[user]['id']]['shortname']
            except KeyError:
                retdict[user]['nickname'] = retdict[user]['id']

            if retdict[user]['type'] == 'page':
                try:
                    retdict[user]['followers'] = int(users[retdict[user]['id']]['members_count'])
                except KeyError:
                    retdict[user]['followers'] = 0
            else:
                retdict[user]['followers'] = 0
            logging.info(u'OK: Personal info for {} (id: {}) collected.'.format(user, retdict[user]['id']))
        return retdict

    @check_dates
    @need_token
    def get_statuses(self, start_date, fin_date, token, **kargv):
        logging.error(u'OK: Statuses collection not implemented yet.')
        return BaseConnector.get_statuses(self, **kargv)

    @check_dates
    @need_token
    def get_comments(self, start_date, fin_date, token, **kargv):
        logging.error(u'OK: Comments collection not implemented yet.')
        return BaseConnector.get_comments(self, **kargv)