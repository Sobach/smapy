# -*- coding: utf-8 -*-
#!/usr/bin/env python

from smapy.connectors.base import *
from smapy.settings import *
from smapy.utilities import strip_tags, strip_spaces
from smapy.http_utilities import get_json
import logging
from time import sleep
import datetime
import re

class VKontakteConnector(BaseConnector):
    """Connector to VKontakte social network (http://www.vk.com)"""

    network = u'vk'
    name = u'ВКонтакте'

    def _token_checker(self):
        url = 'https://api.vk.com/method/isAppUser'
        params = {'access_token':self.token}
        response = self.__api_request__(url, params)
        if isinstance(response, dict) and 'response' in response and response['response'] == '1':
            return True
        logging.critical(u'VK: Access token is not valid.')
        return False

    @need_token
    def _get_profiles(self, token, **kargv):
        retdict = {}
        for user in self.accounts.keys():
            udict = {
                'nickname':self.accounts[user],
                'link':'http://www.vk.com/{}'.format(self.accounts[user]),
                'type':'unknown',
                'followers':0
            }
            if re.search(r'^id\d+$', self.accounts[user]):
                uid = self.accounts[user][2:]
                udict['type'] = 'person'
            elif re.search(r'^public\d+$', self.accounts[user]):
                uid = self.accounts[user][6:]
                udict['type'] = 'page'
            elif re.search(r'^club\d+$', self.accounts[user]):
                uid = self.accounts[user][4:]
                udict['type'] = 'page'
            elif re.search(r'^event\d+$', self.accounts[user]):
                uid = self.accounts[user][5:]
                udict['type'] = 'page'
            else:
                uid = self.accounts[user]

            if udict['type'] == 'page':
                udict = self.__page_profile(uid, udict)
            else:
                udict = self.__person_profile(uid, udict)
            retdict[user] = udict
            if not udict:
                logging.warning(u'VK: No data for {}.'.format(user))
            else:
                logging.info(u'VK: Personal info for {} (id: {}) collected'.format(user, udict['id']))
        return retdict

    @check_dates
    @need_token
    @need_profiles
    def _get_statuses(self, start_date, fin_date, token, by_author_only = True, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        if by_author_only:
            wall_filter = 'owner'
        else:
            wall_filter = 'all'
        for user in userlist[0]:
            url = 'https://api.vk.com/method/wall.get'
            maxoffset = 100
            offset = 0
            posts = []
            if self._profiles[user]['type'] == 'page':
                uid = '-'+str(self._profiles[user]['id'])
            else:
                uid = str(self._profiles[user]['id'])
            while offset < maxoffset:
                params = {'owner_id': uid, 'access_token':token, 'count':100, 'offset':offset, 'filter':wall_filter}
                vk_data = self.__api_request__(url, params)
                if not isinstance(vk_data, dict) or 'response' not in vk_data or len(vk_data['response']) < 1:
                    logging.warning(u'VK: No posts on wall {} (id: {})'.format(user, uid))
                    break
                vk_data = vk_data['response']
                maxoffset = vk_data[0]
                offset += 100
                for post in vk_data[1:]:
                    postdate = datetime.datetime.fromtimestamp(int(post['date']))
                    if postdate >= start_date and postdate <= fin_date:
                        link = 'http://vk.com/wall{0}_{1}'.format(uid, post['id'])
                        posts.append({
                            'id':'{}_{}'.format(uid, post['id']),
                            'date':postdate,
                            'link':link,
                            'reposts': int(post['reposts']['count']),
                            'replies': int(post['comments']['count']),
                            'likes': int(post['likes']['count']),
                            'text': strip_spaces(strip_tags(post['text']))
                        })
                if postdate < start_date:
                    break
                sleep(.5)
            retdict[user] = posts
            logging.info(u'VK: Posts statistics for {} (id: {}) collected'.format(user, uid))
        return retdict

    @check_dates
    @need_token
    @need_profiles
    @need_statuses
    def _get_comments(self, start_date, fin_date, token, **kargv):
        retdict = {}
        userlist = self._users_list()
        retdict.update(userlist[1])
        for user in userlist[0]:
            if self._profiles[user]['type'] == 'page':
                uid = '-'+str(self._profiles[user]['id'])
            else:
                uid = str(self._profiles[user]['id'])
            comments = []
            for post in self._statuses[user]:
                if post['replies'] > 0:
                    url = 'https://api.vk.com/method/wall.getComments'
                    maxoffset = 100
                    offset = 0
                    while offset < maxoffset:
                        params = {'owner_id': uid, 'post_id':post['id'].split('_')[-1], 'preview_length':0, 'access_token':token, 'count':100, 'offset':offset}
                        vk_data = self.__api_request__(url, params)
                        if not isinstance(vk_data, dict) or 'response' not in vk_data or len(vk_data['response']) < 1:
                            logging.warning(u'VK: No posts on wall {} (id: {})'.format(user, uid))
                            break
                        vk_data = vk_data['response']
                        maxoffset = vk_data[0]
                        offset += 100
                        for comment in vk_data[1:]:
                            comments.append({'id':'{}_{}'.format(uid, comment['cid']),
                                             'link':'http://www.vk.com/wall{0}_{1}'.format(uid,comment['cid']),
                                             'date':datetime.datetime.fromtimestamp(int(comment['date'])),
                                             'in_reply_to':post['id'],
                                             'author_id':comment['uid'],
                                             'text':strip_spaces(strip_tags(comment['text']))
                                             })
            retdict[user] = comments
            logging.info(u'VK: Comments statistics for {} collected'.format(user))
        return retdict

    def __person_profile(self, uid, udict):
        udict['type'] = 'person'
        url = 'https://api.vk.com/method/users.get'
        params = {
            'access_token':self.token,
            'uids':uid,
            }
        response = self.__api_request__(url, params)
        if 'error' in response:
            if response['error']['error_code'] == 113:
                return self.__page_profile(uid, udict)
            elif response['error']['error_code'] == 15:
                logging.warning(u'VK: No data for {}.'.format(udict['nickname']))
                return
        udict['id'] = response['response'][0]['uid']
        udict['name'] = response['response'][0]['first_name'] + ' ' + response['response'][0]['last_name']
        sleep(.5)
        url = 'https://api.vk.com/method/friends.get'
        params = {'uid': udict['id'], 'access_token':self.token}
        try:
            friends = len(self.__api_request__(url, params)['response'])
            sleep(.5)
        except KeyError:
            friends = 0
        url = 'https://api.vk.com/method/subscriptions.getFollowers'
        params = {'uid': udict['id'], 'access_token':self.token}
        subscrib = int(self.__api_request__(url, params)['response']['count'])
        udict['followers'] = subscrib + friends
        return udict

    def __page_profile(self, uid, udict):
        udict['type'] = 'page'
        url = 'https://api.vk.com/method/groups.getById'
        params = {
            'access_token':self.token,
            'gid':uid
            }
        response = self.__api_request__(url, params)
        if 'error' in response:
            return None
        udict['id'] = response['response'][0]['gid']
        udict['name'] = response['response'][0]['name']
        sleep(.5)
        url = 'https://api.vk.com/method/groups.getMembers'
        params = {'gid': udict['id'], 'access_token':self.token}
        try:
            udict['followers'] = int(self.__api_request__(url, params)['response']['count'])
        except:
            logging.warning(u'VK: Exception while getting followers for {} (id: {})'.format(udict['name'], udict['id']))
        return udict

    def __api_request__(self, url, params):
        while True:
            answer = get_json(url, params = params)
            if isinstance(answer, dict) and 'error' in answer:
                if answer['error']['error_code'] == 6:
                    sleep(1)
                    continue
            return answer