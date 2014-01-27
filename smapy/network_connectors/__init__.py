# -*- coding: utf-8 -*-
#!/usr/bin/env python

from urllib2 import build_opener, install_opener, ProxyHandler, getproxies
install_opener(build_opener(ProxyHandler(getproxies())))