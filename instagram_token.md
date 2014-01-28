---
title: Document Center
---

How-to: recieving access token for Instagram (www.instagram.com).

## Registering application

1. Go to [developers page](http://instagram.com/developer/) page. Login, if needed.

2. Create new app ("Register Your Application" button). Then create a new app.

3. Fill all the fields (Application Name, Description, Website, and OAuth redirect_uri). Type whatever you want, just remember about urls format.

4. After application creation go to ["managers page"](http://instagram.com/developer/clients/manage/) and copy Client ID and Redirect URI.

5. Substitute them into this URL: https://instagram.com/oauth/authorize/?client_id=Client_ID&redirect_uri=Redirect_URI&response_type=token and open it in your browser.

6. You will be asked to authorize your app and after this you will be redirected to the page, specified earlier. In browser address bar - in the end of your redirect address "access_token" parameter would be written. As for now, this token doesn't expire, so you need to do this task only once. 

## Adding token to [[KeyChain]]

Only access_token string is needed to make requests through [[Instagram connector]]. So just save it to KeyChain:

```python
from smapy.network_connectors.addons import KeyChain
k = KeyChain()
k.assign('ig', access_token)
k.dump()
```

## Using token

After enetering and storing token in KeyChain it can be used to gather data through [[Facebook connector]]:

```python
>>> from smapy.network_connectors.addons import KeyChain
>>> k = KeyChain()
>>> k.load_last()
>>> k.check('ig')
True
>>> from smapy.network_connectors.vkontakte import InstagramConnector
>>> i = InstagramConnector(token = k.get('ig'))
>>> i.accounts = {'RIA Novosti':'ria_novosti'}
>>> i.profiles()
{'RIA Novosti': {'followers': 75645,
                 'id': u'40148843',
                 'link': 'http://instagram.com/ria_novosti',
                 'name': u'РИА Новости',
                 'nickname': 'ria_novosti'}}
```