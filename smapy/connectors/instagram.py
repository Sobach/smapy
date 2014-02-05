# -*- coding: utf-8 -*-
#!/usr/bin/env python

from smapy.connectors.base import *
from smapy.settings import *
from smapy.http_utilities import get_json
import logging
from time import sleep
import datetime

class InstagramConnector(BaseConnector):
    """Connector to Instagram photo-sharing network service (http://www.instagram.com)."""

    network = u'ig'
    name = u'Instagram'

    def _token_checker(self):
        if not isinstance(self.token, (str, unicode)):
            logging.critical(u'IG: Access token is not valid.')
            self._token_ok = False
            return False
        url = 'https://api.instagram.com/v1/users/self?access_token={}'.format(self.token)
        info = get_json(url, log_activity = False, get = True)
        if not info:
            logging.critical(u'IG: Access token is not valid.')
            self._token_ok = False
            return False
        elif 'meta' in info and 'error_type' in info['meta'] and info['meta']['error_type'] == 'OAuthAccessTokenException':
            logging.critical(u'IG: Access token is not valid.')
            self._token_ok = False
            return False
        self._token_ok = True
        return True

    @need_token
    def _get_profiles(self, token, **kargv):
        retdict = {}
        for user in self.accounts.keys():
            url = 'https://api.instagram.com/v1/users/search?q={}&access_token={}'.format(self.accounts[user], token)
            search_res = get_json(url, get = True)
            if not search_res or 'data' not in search_res:
                logging.warning(u'IG: No data for {}.'.format(user))
                retdict[user] = None
                continue
            uid = 0
            for profile in search_res['data']:
                if profile['username'] == self.accounts[user]:
                    uid = profile['id']
                    break
            if uid == 0:
                logging.warning(u'IG: No data for {}.'.format(user))
                retdict[user] = None
                continue
            url = 'https://api.instagram.com/v1/users/{0}/?access_token={1}'.format(uid, token)
            userinfo = get_json(url, get = True)
            if not userinfo or 'data' not in userinfo:
                logging.warning(u'IG: No data for {}.'.format(user))
                retdict[user] = None
                continue
            retdict[user] = {
                'id':uid,
                'nickname':self.accounts[user],
                'name':userinfo['data']['full_name'],
                'link':'http://instagram.com/{}'.format(self.accounts[user]),
                'followers':int(userinfo['data']['counts']['followed_by']),
                'type':'person'
                }
            logging.info(u'IG: Personal info for {} (id: {}) collected'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    @need_token
    @need_profiles
    def _get_statuses(self, start_date, fin_date, token, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            posts = []
            url = 'https://api.instagram.com/v1/users/{0}/media/recent/?access_token={1}'.format(self._profiles[user]['id'], token)
            while True:
                ig_data = get_json(url, get = True)
                if not ig_data or 'data' not in ig_data:
                    break

                for element in ig_data['data']:
                    postdate = datetime.datetime.fromtimestamp(float(element['created_time'])) + datetime.timedelta(seconds=TIME_OFFSET)
                    if postdate >= start_date and postdate <= fin_date:
                        try:
                            text = element['caption']['text']
                        except TypeError:
                            text = ''
                        posts.append({'date':postdate,
                                      'id':element['id'],
                                      'link':element['link'],
                                      'reposts':0,
                                      'replies':int(element['comments']['count']),
                                      'likes':int(element['likes']['count']),
                                      'text':text})
                if postdate > start_date and 'pagination' in ig_data and 'next_url' in ig_data['pagination']:
                    url = ig_data['pagination']['next_url']
                else:
                    break
                sleep(1)
            retdict[user] = posts
            logging.info(u'IG: Posts statistics for {} (id/nick: {}) collected'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    @need_token
    @need_statuses
    def _get_comments(self, start_date, fin_date, token, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            comments = []
            for post in self._statuses[user]:
                if post['replies'] > 0:
                    url = 'https://api.instagram.com/v1/media/{0}/comments?access_token={1}'.format(post['id'], token)
                    answer = get_json(url, get = True)
                    if not answer or 'data' not in answer:
                        continue
                    if post['replies'] > 150:
                        logging.warning(u'IG: There are more 150 comments to post ({}). But only last 150 could be retreived.'.format(post['link']))
                    for element in answer['data']:
                        comments.append({
                            'id':element['id'],
                            'text':element['text'],
                            'link':post['link'],
                            'date':datetime.datetime.fromtimestamp(float(element['created_time'])) + datetime.timedelta(seconds=TIME_OFFSET),
                            'parent':post['id'],
                            'author_id':element['from']['id']})
            retdict[user] = comments
            logging.info(u'IG: Comments statistics for {} (id/nick: {}) collected'.format(user, self.accounts[user]))
        return retdict