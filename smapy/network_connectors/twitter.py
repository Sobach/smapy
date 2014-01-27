# -*- coding: utf-8 -*-
#!/usr/bin/env python

from .base import *
from ..utilities import *
from ..settings import *
import logging
from time import sleep
import datetime
import oauth2
import json
import socks
import httplib2
from urllib2 import getproxies

class TwitterConnector(BaseConnector):
    """Connector to Twitter micro-blog platform (http://www.twitter.com)."""

    def __init__(self, **kargv):
        self.network = u'tw'
        self.proxy_info = proxy_info()
        BaseConnector.__init__(self, **kargv)

    def _token_checker(self):
        url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        answer = self.__oauth_request__(url)
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
            url = 'https://api.twitter.com/1.1/users/lookup.json?screen_name={}&include_entities=false'.format(idl)
            info = self.__oauth_request__(url = url)
            for element in info:
                api_dict[element['screen_name'].lower()] = {
                    'id':element['id'],
                    'nickname':element['screen_name'],
                    'name':element['name'],
                    'link':'https://www.twitter.com/{}'.format(element['screen_name']),
                    'followers':element['followers_count']
                    }
            sleep(6)
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
    def get_statuses(self, start_date, fin_date, token, with_rts = False, count_replies = True, **kargv):
        if with_rts:
            with_rts = 1
        else:
            with_rts = 0
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            posts = []
            for i in range(20):
                home_timeline = self.__oauth_request__('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={}&count=200&trim_user=1&include_rts=0&exclude_replies=0&include_entities=1&page={}'.format(self.accounts[user], i+1))
                sleep(5)
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
                    logging.warning(u'TW: Posts statistics for {} (nick: {}) possible not full. Last tweet date is {}.'.format(user, self.accounts[user], twidate.strftime('%d.%m.%Y')))
            retdict[user] = posts

        if count_replies:
            self.comments(start_date = start_date, fin_date = fin_date)
            retdict = self.__count_comments__(statuses = retdict)
        return retdict

    @check_dates
    @need_token
    def get_comments(self, start_date, fin_date, token, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            comments = []
            url = 'https://api.twitter.com/1.1/search/tweets.json?q=to%3A{}&count=100&until={}'.format(self.accounts[user],
                                                                                              (fin_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
            logging.debug(u'TW: Comments for {}'.format(url))
            while True:
                page = self.__oauth_request__(url)
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
                sleep(5)
                try:
                    if twidate < start_date:
                        logging.info(u'TW: Comments statistics for {} (nick: {}) collected.'.format(user, self.accounts[user]))
                        break
                    else:
                        try:
                            nurl = 'https://api.twitter.com/1.1/search/tweets.json' + str(page['search_metadata']['next_results'])
                            logging.debug(u'TW: urls: {}, {}'.format(url, nurl))
                            url = nurl
                        except KeyError:
                            logging.info(u'TW: Comments statistics for {} (nick: {}) collected.'.format(user, self.accounts[user]))
                            break
                except UnboundLocalError:
                    logging.warning(u'TW: No comments data for {} (nick: {}).'.format(user, self.accounts[user]))
                    twidate = start_date
                    break

            if twidate > start_date:
                logging.warning(u'TW: Comments statistics for {} (nick: {}) possible not full. Last tweet date is {}.'.format(user, self.accounts[user], twidate.strftime('%d.%m.%Y')))

            retdict[user] = comments
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

    def __oauth_request__(self, url):
        try:
            self.client
        except AttributeError:
            consumer = oauth2.Consumer(key=self.token['consumer_key'], secret=self.token['consumer_secret'])
            token = oauth2.Token(key=self.token['access_token'], secret=self.token['access_secret'])
            self.client = oauth2.Client(consumer, token, proxy_info = self.proxy_info)

        while True:
            logging.debug(u'TW: OAUTH: {}'.format(url))
            resp, content = self.client.request(
                url,
                method='GET',
                body=None,
                headers=None,
                force_auth_header=True
            )
            if resp['status'] == '200':
                logging.debug(u'TW: OAUTH: Returnet smth'.format(url))
                return json.loads(content.decode('utf-8'))
            elif resp['status'] == '429': # Rate limit exceed
                s_time = (datetime.datetime.fromtimestamp(int(resp['x-rate-limit-reset'])) - datetime.datetime.now()).seconds + 1
                logging.warning(u'TW: Rate limit exceeded, will sleep {} seconds.'.format(s_time))
                sleep(s_time)
            elif resp['status'] == '404': # No such page (user, tweet, etc.)
                logging.warning(u'TW: No such page: {}.'.format(url))
                return None
            elif resp['status'] == '401': # Token is not valid
                logging.warning(u'TW: Token is not valid.')
                return None
            else:
                logging.error(u'TW: SMTH WRONG: {}'.format(str(resp)))
                return None

def proxy_info():
    try:
        p_inf = getproxies()['http'].split(':')
        return httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, p_inf[1][2:], int(p_inf[-1]))
    except KeyError:
        return None