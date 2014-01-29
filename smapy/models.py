# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy - social media abstract models module"""

from settings import *
import datetime
import re

network_types = {k:v['networkname'] for k, v in CONNECTORS.items()}

class AccountWall(object):
    """model for 'wall'/'account' in particular network; tree-like object:
base profile info -> posts -> every posts has bruch of comments"""

    def __init__(self, name, network, profile, statuses, comments = None):
        self.global_name = name
        if network in network_types.keys():
            self.network = network
        else:
            return None
        self.followers = profile['followers']
        self.nickname = profile['nickname']
        self.network_title = network_types[network]
        self.link = profile['link']
        if comments:
            self.with_comments = True
            self.statuses, self.unassigned_comments = self.__make_posts(statuses, comments)
        else:
            self.with_comments = False
            self.statuses = []
            for status in statuses:
                status['comment_tree'] = []
                self.statuses.append(status)
            self.unassigned_comments = []
        self.statuses = sorted(self.statuses, key=lambda x:x['date'], reverse=True)

    def all_comments(self):
        if not with_comments:
            return
        else:
            return [x['comment_tree'] for x in self.statuses] + self.unassigned_comments

    def commenting_stat(self, by_date=True, min_date = None, max_date = None):
        if not self.statuses and not min_date and not max_date:
            by_date = False

        if by_date and not min_date:
            min_date = min([x['date'] for x in self.statuses])

        if by_date and not max_date:
            max_date = max([x['date'] for x in self.statuses])

        rettab = {'network_title':self.network_title,
                  'network':self.network,
                  'name':self.global_name,
                  'audience':self.followers,
                  'stats':{'summary':{'posts':0,'comments':0, 'shares':0, 'likes':0}}}
        if by_date:
            rettab['date_from'] = min_date.strftime('%d.%m.%Y')
            rettab['date_to'] = max_date.strftime('%d.%m.%Y')
            daterange = datelist(min_date, max_date)
            rettab['stats'].update({k:{'posts':0,'comments':0, 'shares':0, 'likes':0} for k in daterange})

        for post in self.statuses:
            if by_date:
                rettab['stats'][post['date'].strftime('%d.%m.%Y')]['posts'] += 1
                if self.with_comments:
                    rettab['stats'][post['date'].strftime('%d.%m.%Y')]['comments'] += len(post['comment_tree'])
                else:
                    rettab['stats'][post['date'].strftime('%d.%m.%Y')]['comments'] += post['replies']
                rettab['stats'][post['date'].strftime('%d.%m.%Y')]['shares'] += post['reposts']
                rettab['stats'][post['date'].strftime('%d.%m.%Y')]['likes'] += post['likes']
            rettab['stats']['summary']['posts'] += 1
            if self.with_comments:
                rettab['stats']['summary']['comments'] += len(post['comment_tree'])
            else:
                rettab['stats']['summary']['comments'] += post['replies']
            rettab['stats']['summary']['shares'] += post['reposts']
            rettab['stats']['summary']['likes'] += post['likes']
        return rettab

    def filter_posts_by_content(self, keywords = None, patterns = None, only_in_post = False):
        if not keywords and not patterns:
            return
        clean_statuses = []
        keywords = tuple([x.lower() for x in keywords])
        for post in self.statuses:
            if only_in_post:
                checktext = post['text'].lower()
            else:
                checktext = (post['text'] + ' '.join([x['text'] for x in post['comment_tree']])).lower()
            if self.__text_checker(checktext, keywords, patterns):
                clean_statuses.append(post)
        self.statuses = clean_statuses
        unassigned = []
        for comment in self.unassigned_comments:
            checktext = comment['text'].lower()
            if self.__text_checker(checktext, keywords, patterns):
                unassigned.append(comment)
        self.unassigned_comments = unassigned

    def filter_posts_by_comments_count(self, min_comments_count = 1):
        clean_statuses = []
        for post in self.statuses:
            if len(post['comment_tree']) >= min_comments_count:
                clean_statuses.append(post)
        self.statuses = clean_statuses

    def __make_posts(self, statuses, comments):
        postdict = {}
        unassigned = []
        for post in statuses:
            post['comment_tree'] = []
            postdict[post['id']] = post
        for comment in comments:
            if comment['in_reply_to'] in postdict.keys():
                postdict[comment['in_reply_to']]['comment_tree'].append(comment)
            else:
                comment['in_reply_to'] == 'unassigned'
                unassigned.append(comment)
        return postdict.values(), unassigned

    def __text_checker(self, text, keywords, patterns):
        if keywords:
            for item in keywords:
                if item.lower() in text:
                    return True
        if patterns:
            for item in patterns:
                if re.search(item, text):
                    return True
        return False

class PersonWalls(object):
    """model for multi-network person/organization - collection of multiple
AccountWall objects"""

    def __init__(self, name, profiles_dict, statuses_dict, comments_dict = None):
        self.networks = [x for x in profiles_dict.keys() if x in network_types.keys()]
        self.name = name
        self._accounts = {}
        for net in self.networks:
            if comments_dict:
                self._accounts[net] = AccountWall(name, net, profiles_dict[net], statuses_dict[net], comments_dict[net])
            else:
                self._accounts[net] = AccountWall(name, net, profiles_dict[net], statuses_dict[net])

    def wall_from_network(self, network):
        return self._accounts[network]

class NetworkWalls(object):
    """model for multiple accounts inside one network - collection of multiple
AccountWall objects"""
    def __init__(self, network, profiles_dict, statuses_dict, comments_dict = None):
        if network in network_types.keys():
            self.network = network
        else:
            return None
        self.users = profiles_dict.keys()
        self._accounts = {}
        for profile in profiles_dict.keys():
            if profiles_dict[profile]:
                if comments_dict:
                    self._accounts[profile] = AccountWall(profile, network, profiles_dict[profile], statuses_dict[profile], comments_dict[profile])
                else:
                    self._accounts[profile] = AccountWall(profile, network, profiles_dict[profile], statuses_dict[profile])

    def wall_by_user(self, user):
        return self._accounts[user]

def datelist(startdate=datetime.datetime.now()-datetime.timedelta(days = 30), findate=datetime.datetime.now()):
    retlist = []
    while startdate <= findate:
        retlist.append(startdate.strftime('%d.%m.%Y'))
        startdate += datetime.timedelta(days=1)
    return retlist