# -*- coding: utf-8 -*-
#!/usr/bin/env python

from ..utilities import vk_auth, fb_auth, ok_auth
from ..settings import *
import pprint
import datetime
import pickle
import hashlib
import os

class KeyChain(object):
    """KeyChain - is an object to save all your tokens for connectors"""
    def __init__(self):
        self._networks = CONNECTORS.keys()
        self._keys = {}

    def assign(self, net, token):
        if net in self._networks:
            self._keys[net] = token
            if net == 'yt':
                self._keys['gp'] = token
            elif net == 'gp':
                self._keys['yt'] = token
            self.autocomplete()
        elif net == 'raw_vk' or net == 'raw_fb' or net == 'raw_ok':
            self._keys[net] = token
            self.autocomplete()
        else:
            return

    def get(self, net = None):
        if not net:
            return self._keys
        try:
            return self._keys[net]
        except:
            return

    def delete(self, net):
        self._keys.pop(net, None)

    def autocomplete(self):
        if 'raw_vk' in self._keys.keys():
            self._keys['vk'] = vk_auth(self._keys['raw_vk']['app_id'],
                               self._keys['raw_vk']['app_secret'],
                               self._keys['raw_vk']['login'],
                               self._keys['raw_vk']['password'])

        if 'raw_fb' in self._keys.keys():
            self._keys['fb'] = fb_auth(self._keys['raw_fb']['app_id'],
                               self._keys['raw_fb']['app_secret'],
                               self._keys['raw_fb']['app_url'],
                               self._keys['raw_fb']['login'],
                               self._keys['raw_fb']['password'])
        if 'raw_ok' in self._keys.keys():
            self._keys['ok'], self._keys['raw_ok'] = ok_auth(self._keys['raw_ok'])

        if 'lj' not in self._keys.keys():
            self._keys['lj'] = ''
        if 'yt' in self._keys.keys() and 'gp' not in self._keys.keys():
            self._keys['gp'] = self._keys['yt']
        if 'gp' in self._keys.keys() and 'yt' not in self._keys.keys():
            self._keys['yt'] = self._keys['gp']

    def show(self):
        for net in self._keys.keys():
            print net.upper()
            print '--'
            pprint.pprint(self._keys[net])
            print '\n'

    def dump(self, key_dir = os.path.dirname(__file__)):
        data = {
            'keys':self._keys,
            'date':datetime.datetime.now()
            }
        fname = os.path.normpath(os.path.join(key_dir, hashlib.md5(str(data)).hexdigest() + '.key_pickle'))
        keyfile = open(fname, 'wb')
        pickle.dump(data, keyfile)
        keyfile.close()

    def available_dumps(self, key_dir = os.path.dirname(__file__)):
        rettab = []
        dirlist = os.listdir(key_dir)
        for fname in dirlist:
            if fname.endswith('.key_pickle'):
                datafile = open(os.path.normpath(os.path.join(key_dir,fname)), 'rb')
                info = pickle.load(datafile)
                rettab.append({
                    'hash':fname.replace('.key_pickle', ''),
                    'date':info['date'],
                    'networks':info['keys'].keys()
                    })
                datafile.close()
        return rettab

    def load(self, hashstr, key_dir = os.path.dirname(__file__)):
        datafile = open(os.path.normpath(os.path.join(key_dir, hashstr+'.key_pickle')), 'rb')
        info = pickle.load(datafile)
        self._keys = info['keys']
        datafile.close()

    def load_last(self, key_dir = os.path.dirname(__file__)):
        try:
            return self.load(sorted(self.available_dumps(key_dir), key=lambda x:x['date'], reverse = True)[0]['hash'], key_dir)
        except IndexError:
            logging.error(u'KEYCHAIN: No dumps to load.')

    def check(self, net = None, token = None):
        ret_dict = {}
        if not net and token:
            logging.error(u'KEYCHAIN: Specify network, your key belongs to.')
            return False
        elif not net and not token:
            self.autocomplete()
            for network in list(set(CONNECTORS.keys()).intersection(set(self._keys.keys()))):
                ret_dict[network] = self._checker(network, self._keys[network])
            return retdict

        elif net and not token:
            if net not in self._keys or net not in self._networks:
                logging.error(u'KEYCHAIN: There is no key for \'{}\' in this KeyChain object.'.format(net))
                return False
            if net == 'fb' and 'raw_fb' in self._keys:
                self._keys['fb'] = fb_auth(self._keys['raw_fb']['app_id'],
                               self._keys['raw_fb']['app_secret'],
                               self._keys['raw_fb']['app_url'],
                               self._keys['raw_fb']['login'],
                               self._keys['raw_fb']['password'])
            elif net == 'vk' and 'raw_vk' in self._keys:
                self._keys['vk'] = vk_auth(self._keys['raw_vk']['app_id'],
                               self._keys['raw_vk']['app_secret'],
                               self._keys['raw_vk']['login'],
                               self._keys['raw_vk']['password'])
            return self._checker(net, self._keys[net])
        else:
            if net not in self._networks:
                logging.error(u'KEYCHAIN: There is no connector for \'{}\'.'.format(net))
                return False
            return self._checker(net, token)

    def _checker(self, network, key):
        conn = CONNECTORS[network]['connector']
        result = conn(token = key).check_token()
        if result:
            logging.info(u'KEYCHAIN: Token for {} is valid.'.format(CONNECTORS[network]['networkname']))
        else:
            logging.info(u'KEYCHAIN: Token for {} is not valid.'.format(CONNECTORS[network]['networkname']))
        return result