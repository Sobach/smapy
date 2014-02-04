# -*- coding: utf-8 -*-
#!/usr/bin/env python

from smapy.connectors.base import *
from smapy.settings import *
from smapy.utilities import strip_tags, strip_spaces
from smapy.http_utilities import get_url, get_html, get_json
import logging
from time import sleep
import datetime
import re
import bs4
import json

class LiveJournalConnector(BaseConnector):
    """Connector to LiveJournal (http://www.livejournal.com)"""

    network = u'lj'
    name = u'LiveJournal'

    def __init__(self, **kargv):
        BaseConnector.__init__(self, **kargv)
        self._token_ok = True

    def check_token(self):
        return True

    def _get_profiles(self, **kargv):
        retdict = {}
        for user in self.accounts.keys():
            url = 'http://users.livejournal.com/{}/profile'.format(self.accounts[user].replace('-', '_'))
            tree = get_html(url, get = True)
            if not tree:
                logging.warning(u'LJ: No data for {}.'.format(user))
                retdict[user] = None
                continue
            type = None
            for element in tree.findAll('script'):
                try:
                    type = re.search('xtpage = \'journal::([^:]+)::', element.text).group(1)
                    if type == 'personal':
                        type = 'person'
                        break
                    elif type == 'community':
                        type = 'page'
                        break
                except AttributeError:
                    pass

            followers = 0
            try:
                for tag in tree.findAll('li', 'b-steps-step'):
                    if u'В друзьях у' in tag.get_text()\
                    or 'Friend of' in tag.get_text() \
                    or u'Читают' in tag.get_text() \
                    or 'Watched by' in tag.get_text():
                        followers = int(''.join(re.findall('\d', tag.find('span', 'b-friends-count').get_text())))
            except:
                pass

            try:
                name = tree.find('h1', 'b-details-journal-title').get_text()
            except:
                name = self.accounts[user]

            try: posts = ''.join(re.findall('\d', tree.find('div', 'b-details-links').findChildren('li')[0].get_text()))
            except:
                posts = 0
                pass
            udict = {
                'id':user,
                'nickname':user,
                'name':name,
                'link':'http://users.livejournal.com/{}/'.format(self.accounts[user].replace('-', '_')),
                'followers':followers,
                'statuses':posts,
                'type':type
            }
            retdict[user] = udict
            logging.info(u'LJ: Personal info for {} collected'.format(user))
        return retdict

    @check_dates
    def _get_statuses(self, start_date, fin_date, get_replies = True, **kargv):
        if get_replies:
            self._comments = {user:[] for user in self.accounts.keys()}
        retdict = {}
        i = 1
        for user in self.accounts.keys():
            posts = []
            posturl = None
            token = None
            rss_posts = get_html('http://users.livejournal.com/{}/data/rss'.format(self.accounts[user]), get = True)
            try:
                posturl = rss_posts.find('item').comments.get_text()
            except AttributeError:
                logging.warning(u'LJ: No posts for user {} (nick: {}).'.format(user, self.accounts[user]))
                pass
            else:
                while True:
                    html = get_html('{}?format=light'.format(posturl), get = True)
                    ljdat = datetime.datetime.strptime(html.find('span', 'b-singlepost-author-date').get_text(), '%Y-%m-%d %H:%M:%S')
                    if ljdat >= start_date and ljdat <= fin_date:
                        postid = re.search(r'/(\d+)\.html', posturl).group(1)
                        text = html.find('div', 'b-singlepost-wrapper')
                        if text.find('div', 'lj-like'):
                            text.find('div', 'lj-like').clear()
                        text = strip_spaces(strip_tags(text.get_text()))

                        for el in html.findAll('script'):
                            if '"auth_token":' in el.get_text():
                                for line in el.get_text().splitlines():
                                    if line.strip().startswith('var p ='):
                                        ttoken = json.loads(line.strip()[8:-4])
                                        token = ttoken['auth_token']
                        l = 'http://www.livejournal.com/__api/'
                        params = json.dumps([{"jsonrpc":"2.0",
                                              "method":"repost.get_status",
                                              "params":{"url":posturl,
                                              "auth_token":token},
                                              "id":i}])
                        i += 1
                        fr = get_json(l, params = params, encode_params = False)
                        if fr:
                            try:
                                num_rt = int(fr[0]['result']['count'])
                            except KeyError:
                                logging.warning(u'LJ: There is no reposts count for {} post'.format(posturl))
                        else:
                            num_rt = 0

                        try:
                            replies = int(''.join(re.findall('\d', html.find('li', 'b-xylem-cell-amount').get_text())))
                        except AttributeError:
                            replies = 0

                        if get_replies and replies > 0:
                            post_com_data = self.__html_comments_pager__(html).values()
                            replies = len(post_com_data)
                            self._comments[user] += post_com_data

                        posts.append({
                            'id':postid,
                            'link':posturl,
                            'date':ljdat,
                            'text':text,
                            'reposts':num_rt,
                            'replies':replies,
                            'likes':0})
                    if ljdat < start_date:
                        break
                    posturl = get_url(html.find('a', 'b-controls-prev').get('href'), get = True, read = False).url
                    if not posturl:
                        break
            retdict[user] = posts
            logging.info(u'LJ: Posts statistics for {} (nick: {}) collected'.format(user, self.accounts[user]))
        return retdict

    @check_dates
    def _get_comments(self, start_date, fin_date, **kargv):
        try:
            return self._comments
        except AttributeError:
            self._get_statuses(start_date = start_date, fin_date = fin_date, get_replies = True)
            return self._comments

    def __html_comments_pager__(self, tree):
        comments = {}
        try:
            js_com = json.loads(tree.find('script', {'id':'comments_json'}).get_text())
        except AttributeError:
            pass
        else:
            comments.update(self.__json_comments_parser__(js_com))
            if tree.find('div', 'b-pager-next'):
                nexturl = tree.find('div', 'b-pager-next').find('a').get('href')
                if 'http' in nexturl:
                    comments.update(self.__html_comments_pager__(get_html(nexturl, get = True)))
        return comments

    def __json_comments_parser__(self, js_data):
        good = []
        collapsed = []
        comments = {}
        still_collapsed = {}

        for element in js_data:
            if 'article' in element and element['collapsed'] == 0:
                good.append(element)
            else:
                collapsed.append(element)

        for element in good:
            if ('deleted' in element and element['deleted'] == 1) or \
            ('state' in element and element['state'] == 'deleted') or \
            ('suspended' in element and element['suspended'] == 1):
                pass
            else:
                id = str(element['dtalkid'])
                link = 'NA'
                for lnk in element['actions']:
                    if lnk['name'] == 'permalink':
                        link = lnk['href']
                        break
                author_id = element['uname']
                reply_to = re.search(r'/(\d+)\.html', link).group(1)
                text = element['article']
                if element['subject'] != None:
                    text = element['subject']+'\n'+text
                comments[id] = {
                    'id':id,
                    'link':link,
                    'text':strip_spaces(strip_tags(text)),
                    'date':datetime.datetime.fromtimestamp(int(element['ctime_ts'])),
                    'in_reply_to':reply_to,
                    'author_id':author_id
                    }

        for element in collapsed:
            if ('deleted' in element and element['deleted'] == 1) or \
            ('state' in element and element['state'] == 'deleted') or \
            ('suspended' in element and element['suspended'] == 1):
                pass
            else:
                for lnk in element['actions']:
                    if lnk['name'] == 'expand':
                        url_param = re.search(r'http://([^\.]*)[^\d]*(\d*)\.html.*thread=(\d*)', lnk['href'])
                        break
                next_js = get_json(
                    'http://{0}.livejournal.com/{0}/__rpc_get_thread?journal={0}&itemid={1}&flat=&skip=&thread={2}&expand_all=1'.format(url_param.group(1),url_param.group(2),url_param.group(3)),
                    get = True)
                if next_js:
                    comments.update(self.__json_comments_selector__(next_js))
        return comments

    def __ajax_comments_parser__(self, js_data):
        comments = {}
        for comment in js_data:
            if comment['state'] == 'collapsed':
                html_comment = bs4.BeautifulSoup(comment['html'], 'html5lib')
                for lnk in html_comment.findAll('a'):
                    if lnk.get('onclick'):
                        url_param = re.search(r'http://([^\.]*)[^\d]*(\d*)\.html.*thread=(\d*)', lnk['href'])
                        break
                next_js = get_json(
                    'http://{0}.livejournal.com/{0}/__rpc_get_thread?journal={0}&itemid={1}&flat=&skip=&thread={2}&expand_all=1'.format(url_param.group(1),url_param.group(2),url_param.group(3)),
                    get = True)
                if next_js:
                    comments.update(self.__json_comments_selector__(next_js))
            elif ('deleted' in comment and comment['deleted'] == 1) or \
            ('state' in comment and comment['state'] == 'deleted') or \
            ('suspended' in comment and comment['suspended'] == 1):
                pass
            else:
                html_comment = bs4.BeautifulSoup(comment['html'], 'html5lib')
                link = html_comment.find('a', 'comment-permalink').get('href')
                text = html_comment.find('div', 'comment-text').get_text()
                author_id = html_comment.find('span', 'ljuser  i-ljuser     ').get('lj:user')
                data = html_comment.find('a', 'comment-permalink').findChildren('span')[0].get_text()
                if 'am' in data or 'pm' in data:
                    dataformat = '%Y-%m-%d %I:%M %p (UTC)'
                else:
                    dataformat = '%Y-%m-%d %H:%M (UTC)'
                data = datetime.datetime.strptime(data, dataformat) + datetime.timedelta(seconds=TIME_OFFSET)
                reply_to = re.search(r'/(\d+)\.html', link).group(1)
                try:
                    text = html_comment.find('h3').get_text() + ' ' + text
                except:
                    pass
                id = re.search(r'\#t(\d*)', link).group(1)
                comments[id] = {
                    'id':id,
                    'link':link,
                    'text':strip_spaces(strip_tags(text)),
                    'date':data,
                    'in_reply_to':reply_to,
                    'author_id':author_id
                    }
        return comments

    def __json_comments_selector__(self, js_data):
        if isinstance(js_data, dict) and 'comments' in js_data:
            return self.__json_comments_parser__(js_data['comments'])
        else:
            return self.__ajax_comments_parser__(js_data)