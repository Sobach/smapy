How-to: recieving access token for Google products: Google+ (http://plus.google.com) and YouTube (http://www.youtube.com).

## Registering application

1. Go to [developers page](https://cloud.google.com/console) page. Login, if needed.

2. Create new project. Required fields are already filled. But Google may ask you to verify your phone number.

 ![Create project button](https://dl.dropboxusercontent.com/u/81437006/smapy/token_go_1.PNG)

 ![Create project widget](https://dl.dropboxusercontent.com/u/81437006/smapy/token_go_2.PNG)

3. Go to "APIs" menu section and enable "Google+ API" and "YouTube Data API v3".

 ![App settings page](https://dl.dropboxusercontent.com/u/81437006/smapy/token_go_3.PNG)

4. Now go to "Registered Apps" tab and press "Register app". Next step - type app name and check "Web Application" type.

5. Now you can choose authorisation type. For our purposes "Server Key" is quite enough. Open "Server Key" section and you will get your API key (numeric and characters string).

 ![Auth types](https://dl.dropboxusercontent.com/u/81437006/smapy/token_go_4.PNG)

## Adding token to [[KeyChain]]

Only API key string is needed to make requests through [[YouTube connector]] and [[GooglePlus connector]]. So just save it to KeyChain:

```python
from smapy.network_connectors.addons import KeyChain
k = KeyChain()
k.assign('gp', token)
k.dump()
```

You can assign token either to `gp` KeyChain() slot, or `yt`. It doesn't matter: alter network slot will be updated automaticaly.

## Using token

After enetering and storing token in KeyChain it can be used to gather data through [[GooglePlus connector]] or [[YouTube connector]]:

```python
>>> from smapy.network_connectors.addons import KeyChain
>>> k = KeyChain()
>>> k.load_last()
>>> k.check('gp')
True
>>> k.check('yt')
True
>>> from smapy.network_connectors.youtube import YouTubeConnector
>>> y = YouTubeConnector(accounts = {'RIA Novosti':'rianews'}, token = k.get('yt'))
>>> y.profiles()
{'RIA Novosti': {'followers': 4123,
                 'id': u'UC5zq7RSXKKAv8c4TK_jqFgQ',
                 'link': 'http://www.youtube.com/rianews',
                 'name': u'rianews',
                 'nickname': u'rianews'}}
>>> from smapy.network_connectors.googleplus import GooglePlusConnector
>>> g = GooglePlusConnector(token = k.get('gp'))
>>> g.accounts = {'Digit.ru':'111752365837842278731'}
>>> g.profiles()
{'Digit.ru': {'followers': 255516,
              'id': '111752365837842278731',
              'link': u'https://plus.google.com/111752365837842278731',
              'name': u'Digit.ru',
              'nickname': '111752365837842278731',
              'type': u'page'}}
```