---
layout: default
title: VKontakte token
---

# VKontakte access token

How-to: recieving access token for VK social network ([http://www.vk.com](http://www.vk.com)).

## Registering application

1. Go to [developers page](http://vk.com/dev) page. Login, if needed.

2. Press "Creeate an Application" button. Name it and check "Standalone application" type.

![Create app button](/smapy/img/token_vk_1.png)

3. Now you need to verify your regictration through SMS.

4. After verification go to application "Settings" tab and look for Application ID and Secure key.

![App tab selector](/smapy/img/token_vk_2.png)

## Adding token to [KeyChain](/smapy/docs/keychain/)

If you got valuable access token by yourself - you can just add it to `vk` slot of KeyChain().

```python
from smapy.network_connectors.addons import KeyChain
k = KeyChain()
k.assign('vk', 'your_valid_token')
k.dump()
```

But note, that this token is time limited, and next time you need to refresh it manually. If you want to automate the process - there is a function `vk_auth` in `smapy.utilities`. It takes data in "raw" format: app ID, secret key, login, and password and produces valid access token. In terms of security it's quite ugly. But it's rather easy. So use it at your own risk (one good way - is to create a separate virtual VK account, and not to use your real account). KeyChain() object integrates `vk_auth`, and this method called with `KeyChain().autocomplete()` if there is `raw_vk` data.

Raw token data is a dictionary-like object:

```python
token = {
    'app_id'    :STRING,
    'app_secret':STRING,
    'login'     :STRING,
    'password'  :STRING
}
```

## Using token

After enetering and storing token in KeyChain it can be used to gather data through [VKontakte connector](/smapy/docs/vkontakte_connector/):

```python
>>> from smapy.network_connectors.addons import KeyChain
>>> k = KeyChain()
>>> k.load_last()
>>> k.autocomplete()
>>> k.check('vk')
True
>>> from smapy.network_connectors.vkontakte import VKontakteConnector
>>> v = VKontakteConnector(accounts = {'RIA Novosti':'ria'}, token = k.get('vk'))
>>> v.profiles()
{'RIA Novosti': {'followers': 579277,
                 'id': 15755094,
                 'link': 'http://www.vk.com/ria',
                 'name': u'РИА Новости',
                 'nickname': 'ria',
                 'type': 'page'}}
```