---
layout: default
title: Twitter access token
---

# Twitter access token

How-to: recieving access token for Twitter(_www.twitter.com_).

## Registering application

1. Go to [developers page](https://dev.twitter.com) page. Login, if needed and agree with terms and conditions.

2. Then navigate to [My apps](https://dev.twitter.com/apps) page. Press "Create a new application" button.

3. Fill name, description and website fileds (website field required, but wouldn't be used, so enter whatever you want). Check "Agree with developers rules", enter captcha, and submit the form.

 ![Creating app form-1](https://dl.dropboxusercontent.com/u/81437006/smapy/token_tw_1.PNG)
 
 ![Creating app form-2](https://dl.dropboxusercontent.com/u/81437006/smapy/token_tw_2.PNG)

4. You will be redirected to the "detailes" app page. In the bottom there is "You access token" section and "Create my access token" button. 

 ![You access token section](https://dl.dropboxusercontent.com/u/81437006/smapy/token_tw_3.PNG)

5. It may take up to 1 minute. So refresh page after some time. If everything was fine, new fields will occur in "You access token" section: access token, access token secret and access level ("read-only").

## Adding token to [[KeyChain]]

To make requests through [[Twitter connector]] you need "Consumer key", "Consumer secret", "Access token", and "Access token secret". All displayed on app detailes page. In KeyChain object these credentials are stored in a dictionary-like form. 

Adding Twitter token to KeyChain:

```python
from smapy.network_connectors.addons import KeyChain
token = {
    'consumer_key'    : 'Consumer key',
    'consumer_secret' : 'Consumer secret',
    'access_token'    : 'Access token',
    'access_secret'   : 'Access token secret'
        }
k = KeyChain()
k.assign('tw', token)
k.dump()
```

## Using token

After enetering and storing token in KeyChain it can be used to gather data through [[Twitter connector]]:

```python
>>> from smapy.network_connectors.addons import KeyChain
>>> k = KeyChain()
>>> k.load_last()
>>> k.check('tw')
True
>>> from smapy.network_connectors.twitter import TwitterConnector
>>> t = TwitterConnector(accounts = {'RIA Novosti':'ria_novosti'}, token = k.get('tw'))
>>> t.profiles()
{'RIA Novosti': {'followers': 27772,
                 'id': 34262462,
                 'link': 'https://www.twitter.com/ria_novosti',
                 'name': u'RIA Novosti',
                 'nickname': u'ria_novosti'}}
```