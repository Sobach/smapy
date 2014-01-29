# -*- coding: utf-8 -*-
#!/usr/bin/env python

from base import *
from settings import *
from http_utilities import get_json
import logging
from urllib import quote, quote_plus, urlencode, unquote
import datetime
import time
import random
import base64
import hmac
import hashlib
import string

class TwitterConnector(BaseConnector):
    """Connector to Twitter micro-blog platform (http://www.twitter.com)."""

    def __init__(self, **kargv):
        self.network = u'tw'
        BaseConnector.__init__(self, **kargv)

    def _token_checker(self):
        method = 'account/verify_credentials'
        answer = self.__api_request__(method, {})
        if not answer:
            logging.critical(u'TW: Access token is not valid.')
            return False
        self._token_ok = True
        return True

    @need_token
    def get_profiles(self, token, **kargv):
        step = 80
        api_dict = {}
        for i in range(0, len(self.accounts.values()), step):
            idl = ','.join([str(x) for x in self.accounts.values()[i:i+step]])
            params = {'screen_name':idl, 'include_entities':'false'}
            info = self.__api_request__('users/lookup', params)
            for element in info:
                api_dict[element['screen_name'].lower()] = {
                    'id':element['id'],
                    'nickname':element['screen_name'],
                    'name':element['name'],
                    'link':'https://www.twitter.com/{}'.format(element['screen_name']),
                    'followers':element['followers_count']
                    }
            time.sleep(5)

        retdict = {}
        for user in self.accounts.keys():
            try:
                retdict[user] = api_dict[self.accounts[user].lower()]
                logging.info(u'TW: Personal info for {} (id: {}) collected.'.format(user, retdict[user]['id']))

            except KeyError:
                retdict[user] = None
                logging.warning(u'TW: No data for {}, nick: {}.'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    @need_token
    def get_statuses(self, start_date, fin_date, token, by_author_only = True, count_replies = True, **kargv):
        method = 'statuses/user_timeline'
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            posts = []
            for i in range(20):
                params = {'screen_name':self.accounts[user],
                          'count':'200',
                          'trim_user':'1',
                          'include_rts':str(int(not(by_author_only))),
                          'exclude_replies':'0',
                          'include_entities':'1',
                          'page':str(i+1)}
                home_timeline = self.__api_request__(method, params)
                time.sleep(5)
                if not home_timeline:
                    break
                for status in home_timeline:
                    twidate = datetime.datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y') + datetime.timedelta(seconds=TIME_OFFSET)
                    if twidate >= start_date and twidate <= fin_date:
                        posts.append({
                            'date':twidate,
                            'id':status['id_str'],
                            'link':'http://www.twitter.com/{}/status/{}'.format(self.accounts[user], status['id_str']),
                            'likes':0,
                            'reposts':status['retweet_count'],
                            'replies':0,
                            'text':status['text']
                            })
                if twidate < start_date or not len(home_timeline):
                    logging.info(u'TW: Posts statistics for {} (nick: {}) collected.'.format(user, self.accounts[user]))
                    break
                if i == 19:
                    logging.info(u'TW: Posts statistics for {} (nick: {}) collected.'.format(user, self.accounts[user]))
                    logging.warning(u'TW: Posts statistics for {} (nick: {}) possible not full. Last tweet timestamp is {}.'.format(user, self.accounts[user], twidate.strftime('%d.%m.%Y %H:%M')))
            retdict[user] = posts

        if count_replies:
            self.comments(start_date = start_date, fin_date = fin_date)
            retdict = self.__count_comments__(statuses = retdict)
        return retdict

    @check_dates
    @need_token
    def get_comments(self, start_date, fin_date, token, **kargv):
        method = 'search/tweets'
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            comments = []
            params = {'q':'to:{}'.format(self.accounts[user]),
                      'count':'100',
                      'until':(fin_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')}
            while True:
                page = self.__api_request__(method, params)
                if not page or 'statuses' not in page:
                    logging.error(u'TW: Comments collection error for {}.'.format(self.accounts[user]))
                    break
                for tweet in page['statuses']:
                    twidate = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y') + datetime.timedelta(seconds=TIME_OFFSET)
                    if twidate >= start_date:
                        comments.append({
                            'id':tweet['id_str'],
                            'link':'http://www.twitter.com/{0}/status/{1}'.format(tweet['user']['screen_name'], tweet['id_str']),
                            'date':twidate,
                            'in_reply_to':tweet['in_reply_to_status_id_str'],
                            'author_id':tweet['user']['id'],
                            'text':tweet['text']
                            })
                time.sleep(5)
                try:
                    if twidate < start_date:
                        logging.info(u'TW: Comments statistics for {} (nick: {}) collected.'.format(user, self.accounts[user]))
                        break
                    else:
                        try:
                            params = {unquote(k):unquote(v) for k, v in [tuple(x.split('=')) for x in str(page['search_metadata']['next_results'])[1:].split('&')]}
                        except KeyError:
                            logging.info(u'TW: Comments statistics for {} (nick: {}) collected.'.format(user, self.accounts[user]))
                            break
                except UnboundLocalError:
                    logging.warning(u'TW: No comments data for {} (nick: {}).'.format(user, self.accounts[user]))
                    twidate = start_date
                    break

            if len(comments) > 0 and twidate > start_date:
                logging.warning(u'TW: Comments statistics for {} (nick: {}) possible not full. Last tweet timestamp is {}.'.format(user, self.accounts[user], twidate.strftime('%d.%m.%Y %H:%M')))

            retdict[user] = comments
            del twidate
        return retdict

    @need_comments
    def __count_comments__(self, statuses):
        for user in statuses.keys():
            if len(statuses[user]):
                for i in range(len(statuses[user])):
                    com_count = 0
                    for comment in self._comments[user]:
                        if comment['in_reply_to'] == statuses[user][i]['id']:
                            com_count += 1
                    statuses[user][i]['replies'] = com_count
            else:
                pass
        return statuses

    def __api_request__(self, method, params):
        url = 'https://api.twitter.com/1.1/{}.json'.format(method)
        nonce = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))
        tstamp = str(int(time.time()))

        sig_params = {
            'oauth_consumer_key':quote(self.token['consumer_key']),
            'oauth_nonce': quote(nonce),
            'oauth_signature_method':'HMAC-SHA1',
            'oauth_timestamp': tstamp,
            'oauth_token':quote(self.token['access_token']),
            'oauth_version':'1.0'
            }

        for k, v in params.items():
            sig_params[quote(k)] = quote(v)

        sign_string = 'GET&'+quote_plus(url)+'&'+quote('&'.join(['{}={}'.format(k, v) for k, v in sorted(sig_params.items(), key = lambda x:x[0])]))
        sign = base64.b64encode(hmac.new('{}&{}'.format(self.token['consumer_secret'], self.token['access_secret']), sign_string, hashlib.sha1).digest())
        head = [('oauth_consumer_key', self.token['consumer_key']),
                ('oauth_nonce', nonce),
                ('oauth_signature', sign),
                ('oauth_signature_method','HMAC-SHA1'),
                ('oauth_timestamp', tstamp),
                ('oauth_token', self.token['access_token']),
                ('oauth_version', '1.0')
                ]

        auth_header = 'OAuth '+', '.join(['{}="{}"'.format(quote(k), quote(v)) for k, v in head])
        return get_json(url = '{}?{}'.format(url, urlencode(params)), headers = {'Authorization':auth_header}, get = True)