# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy

Social media anatomist for Python is a comprehensive tool for social media
researchers: sociologists, culturologists, anthropologists, etc. It provides
unified interfaces to number of popular social networks and blog platforms
(Connectors) and several templates for models representation (Exporters).

Requires Python 2.7

Changelog:

2014-01-30, Changelog started. Structure & imports changed.
"""

__author__ = 'Alexander Tolmach (tolmach@me.com)'
__copyright__ = 'Copyright 2014, Alexander Tolmach'
__contributors__ = [] # Hope, they will be
__license__ = 'MIT'
__version__ = '0.4.0'

def register_connectors():
    from smapy import connectors
    avaliable_conn = {}
    for conn in connectors.__all__:
        c = eval('connectors.{}'.format(conn))
        avaliable_conn[c.network] = {'networkname':c.name, 'connector':c}
    return avaliable_conn

import settings
CONNECTORS = register_connectors()
from smapy.keychain import KeyChain
from smapy import connectors

class Connection(type):
    def __new__(self, net, **kwar):
        if net in CONNECTORS.keys():
            return CONNECTORS[net]['connector'](**kwar)
        else:
            return