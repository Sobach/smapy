---
layout: default
title: Facebook token
---

# Facebook access token

How-to: recieving access token for Facebook ([http://www.facebook.com](http://www.facebook.com)).

## Registering application

1. Go to [developers page](https://developers.facebook.com/apps/) page. Login, if needed.

2. Create new app. Here you only need to specify your app name.

 ![Create app button](/smapy/img/token_fb_1.png)

 ![Create app widget](/smapy/img/token_fb_2.png)

3. Enter captcha, and on settings page select type of Facebook integration "App on Facebook". Fill Canvas URL and Secure Canvas URL fields (type whatever you want, just remember about protocol prefixes (http and https respectively).

 ![App settings page](/smapy/img/token_fb_3.png)

## Adding token to [KeyChain](/smapy/docs/keychain/)

There are several possibilities to use your app credintials on Facebook. The simpliest one is just to use App ID and App secret (so-called *App token*): Just concatenate these two strings using "|" symbol: `app_id|app_secret` and add this string to your [KeyChain](/smapy/docs/keychain/) with 'fb' identifier.

```python
from smapy.network_connectors.addons import KeyChain
k = KeyChain()
k.assign('fb', 'abb_id|app_secret')
k.dump()
```

But this type of token has limited functionality. For example, with this token you can't get number of subscribers, there could be problems with posts links, etc.

Better way is to use *User Access Token*. In order to generate it your have to grant access for your app to your account. [Here](https://developers.facebook.com/docs/facebook-login/access-tokens/) you can find more information about it and learn, how to do it manually. If you want to automate the process - there is a function `fb_auth` in `smapy.utilities`. But it needs your login and password. In terms of security it's quite ugly. But it's rather easy. So use it at your own risk (one good way - is to create a separate virtual Facebook account, and not to use your real account).

User Access token is time limited. So from time to time it needs to be refreshed (manually or using `fb_auth` function. The most usable way - is to store required credentials in `raw_fb` slot of [KeyChain](/smapy/docs/keychain/). It's a dictionary-like object:

```python
token = {
    'app_id'    :STRING,
    'app_secret':STRING,
    'app_url'   :STRING,
    'login'     :STRING,
    'password'  :STRING
}
```

These parameters are fixed. And using them, it's easy to generate time-limited user access token: just call `KeyChain().autocomplete()` method. It will authorise and authenticate app for user's account and store valid access token in `KeyChain().get('fb')`.

## Using token

After enetering and storing token in KeyChain it can be used to gather data through [Facebook connector](/smapy/docs/facebook_connector/):

```python
>>> from smapy.network_connectors.addons import KeyChain
>>> k = KeyChain()
>>> k.load_last()
>>> k.autocomplete()
>>> k.check('fb')
True
>>> from smapy.network_connectors.facebook import FacebookConnector
>>> f = FacebookConnector(accounts = {'RIA Novosti':'RiaNovosti'}, token = k.get('fb'))
>>> f.profiles()
{'RIA Novosti': {'followers': 148030,
                 'id': u'357990416180',
                 'link': 'http://www.facebook.com/RiaNovosti',
                 'name': u'RIA Novosti',
                 'nickname': 'RiaNovosti',
                 'type': 'page'}}
```
