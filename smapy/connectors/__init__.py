# -*- coding: utf-8 -*-
#!/usr/bin/env python

from urllib2 import build_opener, install_opener, ProxyHandler, getproxies
install_opener(build_opener(ProxyHandler(getproxies())))

from smapy.connectors.facebook import FacebookConnector as Facebook
from smapy.connectors.instagram import InstagramConnector as Instagram
from smapy.connectors.livejournal import LiveJournalConnector as LiveJournal
from smapy.connectors.twitter import TwitterConnector as Twitter
from smapy.connectors.vkontakte import VKontakteConnector as VKontakte
from smapy.connectors.youtube import YouTubeConnector as YouTube
from smapy.connectors.googleplus import GooglePlusConnector as GooglePlus
from smapy.connectors.odnoklassniki import OdnoklassnikiConnector as Odnoklassniki

__all__ = ['Facebook','Instagram','LiveJournal', 'Twitter', 'VKontakte',
           'YouTube', 'GooglePlus', 'Odnoklassniki']