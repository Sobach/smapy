# -*- coding: utf-8 -*-
#!/usr/bin/env python

from smapy.connectors.base import *
from smapy.settings import *
from smapy.utilities import strip_spaces, strip_tags
from smapy.http_utilities import get_json
import logging
from time import sleep
import datetime

class YouTubeConnector(BaseConnector):
    """Connector to YouTube (http://www.youtube.com)"""

    network = u'yt'
    name = u'YouTube'

    def _token_checker(self):
        url = 'https://www.googleapis.com/plus/v1/people?query=google&key={}'.format(self.token)
        info = get_json(url, get = True)
        if not info or 'error' in info:
            logging.critical(u'YT: Access token is not valid.')
            self._token_ok = False
            return False
        self._token_ok = True
        return True

    @need_token
    def _get_profiles(self, token, **kargv):
        retdict = {}
        for user in self.accounts.keys():
            url =  'https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={0}&type=channel&key={1}'.format(self.accounts[user], token)
            yt_data = get_json(url, get = True)
            if not isinstance(yt_data, dict) or 'items' not in yt_data:
                retdict[user] = None
                logging.warning(u'YT: No data for {}.'.format(user))
                continue

            found = False
            for item in yt_data['items']:
                if item['id']['kind'] == 'youtube#channel' and (item['snippet']['channelTitle'].upper() == self.accounts[user].upper() or item['snippet']['title'].upper() == self.accounts[user].upper()):
                    found = True
                    uid = item['id']['channelId']
                    url = 'https://www.googleapis.com/youtube/v3/channels?part=contentDetails%2Cstatistics&id={}&key={}'.format(item['id']['channelId'], token)
                    prof_data = get_json(url, get = True)
                    if not isinstance(prof_data, dict) or 'items' not in prof_data:
                        retdict[user] = None
                        logging.warning(u'YT: No data for {}.'.format(user))
                        break
                    retdict[user] = {
                        'id':item['id']['channelId'],
                        'nickname':item['snippet']['channelTitle'],
                        'name':item['snippet']['title'],
                        'link':'http://www.youtube.com/{}'.format(item['snippet']['channelTitle']),
                        'followers':int(prof_data['items'][0]['statistics']['subscriberCount']),
                        'type':'person'
                        }
                    logging.info(u'YT: Personal info for {} collected'.format(user))
                    break
            if not found:
                retdict[user] = None
                logging.warning(u'YT: No data for {}.'.format(user))
            sleep(2)
        return retdict

    @need_token
    @need_profiles
    @check_dates
    def _get_statuses(self, token, start_date, fin_date, slowmo = 0, **kargv):
        userlist = self._users_list()
        retdict = userlist[1]
        for user in userlist[0]:
            posts = {}
            for time_pair in self._daterange(start_date, fin_date, slowmo):
                burl = 'https://www.googleapis.com/youtube/v3/search?part=id%2Csnippet&channelId={}&maxResults=50&order=date&publishedAfter={}&publishedBefore={}&type=video&key={}'.format(
                    self._profiles[user]['id'],
                    (time_pair[0] - datetime.timedelta(seconds=TIME_OFFSET)).strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ'),
                    (time_pair[1] - datetime.timedelta(seconds=TIME_OFFSET)).strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ'),
                    token,
                    )
                checkId = ''
                prevId = ''
                url = burl
                while True:
                    yt_data = get_json(url, get = True)
                    if not isinstance(yt_data, dict) or 'items' not in yt_data or len(yt_data['items']) == 0:
                        break
                    checkId = yt_data['items'][0]['id']['videoId']
                    if checkId == prevId:
                        break
                    for item in yt_data['items']:
                        postdate = datetime.datetime.strptime(item['snippet']['publishedAt'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(seconds=TIME_OFFSET)
                        if postdate >= start_date and postdate <= fin_date:
                            text = item['snippet']['title'] + '\n' + item['snippet']['description']
                            post_id = item['id']['videoId']
                            post_link = 'http://www.youtube.com/watch?v={}'.format(item['id']['videoId'])
                            posts[post_id] = {
                                'id':post_id,
                                'link':post_link,
                                'date':postdate,
                                'reposts':0,
                                'replies':0,
                                'likes':0,
                                'text':strip_spaces(strip_tags(text)),
                                }
                    if 'nextPageToken' in yt_data:
                        url = '{}&pageToken={}'.format(burl, yt_data['nextPageToken'])
                    else:
                        break
                    sleep(2)
            step = 5
            for i in range(0, len(posts.keys()), step):
                idl = '%2C'.join([str(x) for x in posts.keys()[i:i+step]])
                url = 'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={}&key={}'.format(idl,token)
                yt_stat = get_json(url, get = True)
                if not isinstance(yt_stat, dict) or 'items' not in yt_stat:
                    logging.warning(u'YT: Posts likes and comments stat may be not full')
                    continue
                for item in yt_stat['items']:
                    posts[item['id']]['replies'] = int(item['statistics']['commentCount'])
                    posts[item['id']]['likes'] = int(item['statistics']['likeCount'])
                sleep(1)
            retdict[user] = posts.values()
            logging.info(u'YT: Posts statistics for {} (nick: {}) collected'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    @need_token
    @need_statuses
    def _get_comments(self, token, start_date, fin_date, **kargv):
        userlist = self._users_list()
        retdict = userlist[1]
        for user in userlist[0]:
            comments = []
            for post in self._statuses[user]:
                if post['replies'] > 0:
                    url = 'http://gdata.youtube.com/feeds/api/videos/{}/comments?max-results=50&alt=json&key={}'.format(post['id'], token)
                    while True:
                        yt_comments = get_json(url, get = True)
                        if not isinstance(yt_comments, dict) or 'feed' not in yt_comments or 'entry' not in yt_comments['feed']:
                            break
                        for comment in yt_comments['feed']['entry']:
                            comments.append({'id':comment['id']['$t'].split('/')[-1],
                                             'link':'http://www.youtube.com/all_comments?v={}&lc={}'.format(post['id'], comment['id']['$t'].split('/')[-1]),
                                             'date':datetime.datetime.strptime(comment['published']['$t'][:19], '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(seconds=TIME_OFFSET),
                                             'in_reply_to':comment['yt$videoid']['$t'],
                                             'author_id':comment['author'][0]['uri']['$t'].split('/')[-1],
                                             'text':strip_spaces(strip_tags(comment['content']['$t']))
                                             })
                        next = False
                        for link in yt_comments['feed']['link']:
                            if link['rel'] == 'next':
                                url = link['href']
                                next = True
                        if not next:
                            break
                        sleep(2)
                    if post['replies'] >= 1000:
                        logging.warning(u'YT: Comments statistics for {} (video: {}) possible not full (over 1000 comments).'.format(user, post['link']))
            retdict[user] = comments
            logging.info(u'YT: Comments statistics for {} (nick: {}) collected'.format(user, self.accounts[user]))
        return retdict

    def _daterange(self, startdate, findate, step):
        if step == 0:
            return [(startdate, findate)]
        else:
            r_list = []
            mindate = startdate
            while mindate < findate:
                if mindate+datetime.timedelta(days = step) < findate:
                    r_list.append((mindate, mindate+datetime.timedelta(days = step)))
                else:
                    r_list.append((mindate, findate))
                mindate += datetime.timedelta(days = step)
            return r_list