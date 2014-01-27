# -*- coding: utf-8 -*-
#!/usr/bin/env python

from ..utilities import *
from ..settings import *
from .base import *
from urllib import quote_plus
from time import sleep
import logging
import datetime

class FacebookConnector(BaseConnector):
    """Connector to Facebook social network (http://www.facebook.com)."""

    def __init__(self, **kargv):
        self.network = u'fb'
        BaseConnector.__init__(self, **kargv)

    def _token_checker(self):
        url = 'https://graph.facebook.com/me?access_token={}'.format(self.token)
        info = linkrequest(url, get = True, log_activity = False)
        if info:
            self._token_ok = True
            return True
        url = 'https://graph.facebook.com/{}?access_token={}'.format(self.token.split('|')[0], self.token)
        info = linkrequest(url, get = True, log_activity = False)
        if info:
            logging.warning(u'FB: Your token has limited functionality. You can\'t count person\'s subscribers and some other things.')
            self._token_ok = True
            return True
        logging.critical(u'FB: Access token is not valid.')
        return False

    @need_token
    def get_profiles(self, token, **kargv):
        retdict = {}
        for user in self.accounts.keys():
            udict = {
                'nickname':self.accounts[user],
                'link':'http://www.facebook.com/{0}'.format(self.accounts[user]),
                'type':'unknown',
                'followers':0
            }
            url = 'https://graph.facebook.com/{0}?access_token={1}'.\
                format(self.accounts[user], token)
            info = jsonrequest(url, get = True)
            if not info:
                retdict[user] = None
                logging.warning(u'FB: No data for {}.'.format(user))
                continue
            udict['id'] = info['id']
            udict['name'] = info['name']
            if 'likes' in info:
                udict['type'] = 'page'
                udict['followers'] = int(info['likes'])
            else:
                url = 'https://graph.facebook.com/{0}/subscribers?access_token={1}'.format(udict['id'], token)
                try:
                    subscr = int(jsonrequest(url, get = True, noerrors = True)['summary']['total_count'])
                except:
                    subscr = 0
                    logging.warning(u'FB: Exception while getting subscribers for {} (id: {}).'.format(user, udict['id']))
                req = quote_plus('SELECT friend_count FROM user WHERE uid = {0}'.format(udict['id']))
                url = 'https://graph.facebook.com/fql?q={0}&access_token={1}'.format(req, token)
                try:
                    fri = int(jsonrequest(url, get = True, noerrors = True)['data'][0]['friend_count'])
                except:
                    fri = 0
                    logging.warning(u'FB: Exception while getting friends for {} (id: {}).'.format(user, udict['id']))
                udict['type'] = 'person'
                udict['followers'] = subscr + fri
            retdict[user] = udict
            logging.info(u'FB: Personal info for {} (id: {}) collected.'.format(user, udict['id']))
            sleep(1)
        return retdict

    @check_dates
    @need_token
    def get_statuses(self, start_date, fin_date, token, count_replies = True, count_likes = True, **kargv):
        if not count_replies:
            logging.warning(u'FB: Number of comments per status is not collected.')
        if not count_likes:
            logging.warning(u'FB: Number of likes per status is not collected.')
        bad_statuses = ['tagged_in_photo', 'approved_friend']
        if count_replies:
            self._comments = {}
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        if count_replies:
            self._comments.update(userlist[1])
        for user in userlist[0]:
            self._comments[user] = []
            posts = []
            url = 'https://graph.facebook.com/{0}/posts?access_token={1}'.format(self.accounts[user], token)
            while True:
                fb_data = jsonrequest(url, get = True)
                if not fb_data or 'data' not in fb_data:
                    break
                for post in fb_data['data']:
                    postdate = datetime.datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000') + datetime.timedelta(seconds=TIME_OFFSET)
                    try:
                        status_type = post['status_type']
                    except:
                        pass
                    else:
                        if postdate >= start_date and postdate <= fin_date and status_type not in bad_statuses:
                            text = []
                            try: text.append(post['message'])
                            except KeyError: pass
                            try: text.append(post['caption'])
                            except KeyError: pass
                            try: text.append(post['name'])
                            except KeyError: pass
                            try: text.append(post['story'])
                            except KeyError: pass
                            try: text.append(post['description'])
                            except KeyError: pass
                            text = strip_spaces('\n'.join(text))
                            link = 'NA'
                            try:
                                link = post['actions'][0]['link']
                            except (KeyError, IndexError):
                                try:
                                    link = 'http://www.facebook.com/{}/posts/{}'.format(post['id'].split('_')[0],
                                                                                        post['id'].split('_')[1])
                                except (KeyError, IndexError):
                                    link = 'http://www.facebook.com/{}'.format(post['id'])
                            post_id = post['id']

                            if count_likes:
                                likes = len(self.__add_likes('https://graph.facebook.com/{0}/likes?limit=100&access_token={1}'.format(post_id, token)))
                            else:
                                likes = 0

                            try:
                                shares = int(post['shares']['count'])
                            except:
                                shares = 0

                            if count_replies:
                                com_data = self.__add_comments('https://graph.facebook.com/{0}/comments?limit=100&filter=stream&access_token={1}'.format(post_id, token))
                                comments = len(com_data)
                                for comment in com_data:
                                    comment['in_reply_to'] = post_id
                                    comment['link'] = link + comment['link']
                                    self._comments[user].append(comment)
                            else:
                                comments = 0

                            posts.append({
                                'date':postdate,
                                'id':post_id,
                                'reposts': shares,
                                'replies': comments,
                                'likes': likes,
                                'link':link,
                                'text':strip_spaces(text)
                            })

                if postdate < start_date:
                    break
                try:
                    url = fb_data['paging']['next']
                except:
                    break
                sleep(1)
            retdict[user] = posts
            logging.info(u'FB: Posts statistics for {} (id/nick: {}) collected.'.format(user, self.accounts[user]))
            if count_replies:
                logging.info(u'FB: Comments statistics for {} (id/nick: {}) collected.'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    @need_token
    def get_comments(self, start_date, fin_date, token, **kargv):
        self.get_statuses(start_date = start_date, fin_date = fin_date, token = token, count_replies = True, count_likes = False)
        return self._comments

    def __add_comments(self, url):
        comments = []
        while True:
            com_data = jsonrequest(url, get = True)
            if com_data and 'data' in com_data:
                for comment in com_data['data']:
                    comments.append({
                        'id': comment['id'],
                        'link':'/?comment_id={}'.format(comment['id'].split('_')[-1]),
                        'date':datetime.datetime.strptime(comment['created_time'], '%Y-%m-%dT%H:%M:%S+0000') + datetime.timedelta(seconds=TIME_OFFSET),
                        'author_id':comment['from']['id'],
                        'text':strip_spaces(comment['message'])
                        })

            if 'paging' in com_data and 'next' in com_data['paging']:
                sleep(1)
                url = com_data['paging']['next']
            else:
                return check_dublicates_complete(comments)

    def __add_likes(self, url):
        likes = []
        while True:
            like_data = jsonrequest(url, get = True)
            if like_data and 'data' in like_data:
                for like in like_data['data']:
                    likes.append({
                        'author_id':like['id'],
                        })

            if like_data and 'paging' in like_data and 'next' in like_data['paging']:
                sleep(1)
                url = like_data['paging']['next']
            else:
                return check_dublicates_complete(likes)