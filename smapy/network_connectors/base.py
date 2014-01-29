# -*- coding: utf-8 -*-
#!/usr/bin/env python

from settings import *
from utilities import check_dublicates_complete
import logging
import datetime

def need_token(func):
    def wrapper(self, **kargv):
        if 'token' in kargv.keys():
            self.token = kargv['token']
            if self.check_token():
                return func(self, **kargv)
        try:
            if self.token and self.check_token():
                kargv['token'] = self.token
                return func(self, **kargv)
            else:
                logging.critical(u'{}: No access token to make requests'.format(self.network.upper()))
                return None
        except AttributeError:
            logging.critical(u'{}: No access token to make requests'.format(self.network.upper()))
            return None
    return wrapper

def need_profiles(func):
    def wrapper(self, **kargv):
        try:
            self._profiles
        except AttributeError:
            self.profiles(**kargv)
            try:
                self._profiles
            except AttributeError:
                logging.critical(u'{}: Tried to collect profiles, but failed'.format(self.network.upper()))
                return None
        return func(self, **kargv)
    return wrapper

def need_statuses(func):
    def wrapper(self, **kargv):
        try:
            self._statuses
        except AttributeError:
            self.statuses(**kargv)
            try:
                self._statuses
            except AttributeError:
                logging.critical(u'{}: Tried to collect statuses, but failed'.format(self.network.upper()))
                return None
        return func(self, **kargv)
    return wrapper

def need_comments(func):
    def wrapper(self, **kargv):
        try:
            self._comments
        except AttributeError:
            self.comments(**kargv)
            try:
                self._comments
            except AttributeError:
                logging.critical(u'{}: Tried collect comments, but failed'.format(self.network.upper()))
                return None
        return func(self, **kargv)
    return wrapper

def check_dates(func):
    def wrapper(self, **kargv):
        if 'start_date' not in kargv.keys():
            try:
                kargv['start_date'] = self.start_date
            except AttributeError:
                logging.warning(u'{}: Start date not specified - collecting data from 01-01-1990.'.format(self.network.upper()))
                kargv['start_date'] = datetime.datetime.strptime('1990.01.01', '%Y.%m.%d')
        self.start_date = kargv['start_date']

        if 'fin_date' not in kargv.keys():
            try:
                kargv['fin_date'] = self.fin_date
            except AttributeError:
                logging.warning(u'{}: Finish date not specified - collecting data till now.'.format(self.network.upper()))
                kargv['fin_date'] = datetime.datetime.now()
        self.fin_date = kargv['fin_date']
        return func(self, **kargv)
    return wrapper

class BaseConnector():
    """Base connector class
Every connector, based on it required to have these functions:
    * get_profiles()
    * get_statuse()
    * get_comments()
    * _token_checker()"""

    def __init__(self, accounts = {}, **kargv):
        self.accounts = accounts
        self._token_ok = False
        self.token = None
        if 'token' in kargv.keys():
            self.token = kargv['token']
            if not self.check_token():
                self.token = None
        if 'start_date' in kargv.keys():
            self._start_date = kargv['start_date']
        if 'fin_date' in kargv.keys():
            self._fin_date = kargv['fin_date']

    def check_token(self, **kargv):
        if 'token' in kargv.keys():
            self.token = kargv['token']
        if not self.token:
            logging.critical(u'{}: There is no token to check.'.format(self.network.upper()))
            return False
        if self._token_ok:
            return True
        self._token_ok = self._token_checker()
        return self._token_ok

    def profiles(self, **kargv):
        try:
            return self._profiles
        except AttributeError:
            data = self.get_profiles(**kargv)
            if data:
                self._profiles = data
                return self._profiles
            else:
                return {k:None for k in self.accounts.keys()}

    def statuses(self, **kargv):
        try:
            return self._statuses
        except AttributeError:
            data = self.get_statuses(**kargv)
            if data:
                self._statuses = {user:check_dublicates_complete(statuses) for (user, statuses) in data.items()}
                return self._statuses
            else:
                return {k:[] for k in self.accounts.keys()}

    def comments(self, **kargv):
        try:
            return self._comments
        except AttributeError:
            data = self.get_comments(**kargv)
            if data:
                self._comments = {user:check_dublicates_complete(comments) for (user, comments) in data.items()}
                return self._comments
            else:
                return {k:[] for k in self.accounts.keys()}

    def _users_list(self):
        empty_users = {}
        try:
            ulist = [k for k in self._profiles.keys() if self._profiles[k]]
            for user in set(self._profiles.keys()).difference(set(ulist)):
                empty_users[user] = []
        except AttributeError:
            ulist = self.accounts.keys()
        return ulist, empty_users

    def _token_checker(self):
        logging.warning(u'{}: There is no network-specific token checker.'.format(self.network.upper()))
        return False

    def get_profiles(self, **kargv):
        logging.warning(u'{}: Profiles collector not specified.'.format(self.network.upper()))
        return {acc:None for acc in self.accounts.keys()}

    def get_statuses(self, **kargv):
        logging.warning(u'{}: Statuses collector not specified.'.format(self.network.upper()))
        return {acc:[] for acc in self.accounts.keys()}

    def get_comments(self, **kargv):
        logging.warning(u'{}: Comments collector not specified.'.format(self.network.upper()))
        return {acc:[] for acc in self.accounts.keys()}