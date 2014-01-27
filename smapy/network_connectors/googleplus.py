# -*- coding: utf-8 -*-
#!/usr/bin/env python

from .base import *
from ..utilities import *
from ..settings import *
import logging
from time import sleep
import datetime
from urllib import quote_plus
import re

class GooglePlusConnector(BaseConnector):
    """Connector to Google Plus social network (http://plus.google.com)."""

    def __init__(self, **kargv):
        self.network = u'gp'
        BaseConnector.__init__(self, **kargv)

    def _token_checker(self):
        url = 'https://www.googleapis.com/plus/v1/people?query=google&key={}'.format(self.token)
        info = jsonrequest(url, get = True)
        if not info or 'error' in info:
            logging.critical(u'GP: Access token is not valid.')
            self._token_ok = False
            return False
        self._token_ok = True
        return True

    @need_token
    def get_profiles(self, token, **kargv):
        retdict = {}
        logging.warning(u'GP: Number of followers only avaliable for pages (not persons) that made this info public.')
        for user in self.accounts.keys():
            if not re.search(ur'^\d+$', self.accounts[user]):
                url = 'https://www.googleapis.com/plus/v1/people?query={}&key={}'.format(quote_plus(self.accounts[user].encode('utf-8')), token)
                resp = jsonrequest(url, get = True)
                uid = 0
                if not resp or 'items' not in resp:
                    retdict[user] = None
                    logging.warning(u'GP: No data for {}.'.format(user))
                    continue
                for item in resp['items']:
                    if self.accounts[user].lower() in item['url'].lower():
                        uid = item['id']
                        break
                if uid == 0:
                    retdict[user] = None
                    logging.warning(u'GP: No data for {}.'.format(user))
                    continue
            else:
                uid = self.accounts[user].encode('utf-8')
            url = 'https://www.googleapis.com/plus/v1/people/{0}?key={1}'.format(uid, token)
            resp = jsonrequest(url, get = True)
            if not resp:
                retdict[user] = None
                logging.warning(u'GP: No data for {}.'.format(user))
                continue

            name = resp['displayName']
            try:
                followers = int(resp['plusOneCount'])
            except KeyError:
                try:
                    followers = int(resp['circledByCount'])
                except KeyError:
                    followers = 0
            retdict[user] = {
                'id':str(uid),
                'name':name,
                'nickname':self.accounts[user],
                'followers':followers,
                'link':resp['url'],
                'type':resp['objectType']
                }
            logging.info(u'GP: Personal info for {} (id: {}) collected.'.format(user, uid))
        return retdict

    @check_dates
    @need_token
    @need_profiles
    def get_statuses(self, start_date, token, fin_date, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            posts = []
            url = 'https://www.googleapis.com/plus/v1/people/{}/activities/public?key={}'.format(self._profiles[user]['id'], token)
            while True:
                resp = jsonrequest(url, get = True)
                if not resp or 'items' not in resp:
                    break
                for post in resp['items']:
                    postdate = datetime.datetime.strptime(post['published'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(seconds=TIME_OFFSET)
                    if postdate >= start_date and postdate <= fin_date:
                        text = post['title'] + '\n' + post['object']['content']
                        text = strip_spaces(strip_tags(text))
                        post_id = post['id']
                        post_link = post['url']
                        try:
                            comments = int(post['object']['replies']['totalItems'])
                        except:
                            comments = 0
                        try:
                            likes = int(post['object']['plusoners']['totalItems'])
                        except:
                            likes = 0
                        try:
                            retweets = int(post['object']['resharers']['totalItems'])
                        except:
                            retweets = 0
                        posts.append({
                            'date':postdate,
                            'id':post_id,
                            'likes': likes,
                            'replies': comments,
                            'reposts': retweets,
                            'text': text,
                            'link': post_link
                        })
                if postdate < start_date or 'nextPageToken' not in resp:
                    break
                else:
                    url = url.split('&')[0] + '&pageToken={0}'.format(resp['nextPageToken'])
            retdict[user] = posts
            logging.info(u'GP: Posts statistics for {} (id/nick: {}) collected.'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    @need_token
    @need_statuses
    def get_comments(self, token, start_date, fin_date, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            comments = []
            for post in self._statuses[user]:
                if post['replies'] > 0:
                    url = 'https://www.googleapis.com/plus/v1/activities/{0}/comments?key={1}'.format(post['id'], token)
                    while True:
                        resp = jsonrequest(url, get = True)
                        if not resp or 'items' not in resp:
                            break
                        for element in resp['items']:
                            comments.append({
                                'id':element['id'],
                                'link':post['link'],
                                'date':datetime.datetime.strptime(element['published'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(seconds=TIME_OFFSET),
                                'in_reply_to':post['id'],
                                'author_id':element['actor']['id'],
                                'text':strip_tags(element['object']['content'])
                                })
                        if 'nextPageToken' in resp:
                            url = url.split('&')[0] + '&pageToken={0}'.format(resp['nextPageToken'])
                        else:
                            break
            retdict[user] = comments
            logging.info(u'GP: Comments statistics for {} (id/nick: {}) collected.'.format(user, self.accounts[user]))
        return retdict