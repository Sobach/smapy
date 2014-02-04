---
layout: page
title: Connectors
---

# Connectors

Most of the popular social media services have APIs (application programming interfaces). Using them, one could collect a lot of interesting research data. But there are some difficulties. Every API has its own request endpoints, syntax, response format, rate limits, etc. If you are dealing with more than one social media source - you constantly have to switch between these API-languages. Moreover, if you want to compare multiple networks, first you have to "similarify" your data from different sources.

The main purpose of connectors - is to build a high-level meta-API wrapper, and to bring to network data required similarity. There is no need to care about how alike concepts are called in different networks (i.e. "tweet" in Twitter, "status" in Facebook, or "post" in Livejournal), and what exactly endpoints you should use. Also connectors keep track of rate limits and handle errors and exceptions.

Connectors output standardized pieces of data, that could be used "as is", or processed to more complex models, or saved in suitable form using exporters.

## Aviable connectors and time rates for base data pieces

Every connector is a class, that inherits from `smapy.connectors.BaseConnector()`. This is done for maximal similarity. The only pieces, implemented individually in every conncetor concern low-level API interactions.

| name and detailed description                               | class propierty                  | .profiles() | .statuses() | .comments() |
|-------------------------------------------------------------|----------------------------------|-------------|-------------|-------------|
| [Facebook connector](/smapy/docs/facebook_connector/)       | `smapy.connectors.Facebook()`    |  50         | 750         |  2500       |
| [Twitter connector](/smapy/docs/twitter_connector/)         | `smapy.connectors.Twitter()`     |  1000       | 1000        |  1000       |
| [GooglePlus connector](/smapy/docs/googleplus_connector/)   | `smapy.connectors.GooglePlus()`  |  100        | 1000        |  2000       |
| [YouTube connector](/smapy/docs/youtube_connector/)         | `smapy.connectors.YouTube()`     |  50         | 400         |  700        |
| [Instagram connector](/smapy/docs/instagram_connector/)     | `smapy.connectors.Instagram()`   |  100        | 500         |  2000       |
| [LiveJournal connector](/smapy/docs/livejournal_connector/) | `smapy.connectors.LiveJournal()` |  30         | 10          |  40         |
| [VKontakte connector](/smapy/docs/vkontakte_connector/)     | `smapy.connectors.VKontakte()`   |  50         | 3000        |  5000       |

\* Time costs evaluated in average number of collected instances per 1 minute.

## smapy.Connection(_net_) class

Every connector could be imported from `smapy.connectors` package. I.e.:

```python
>>> from smapy.connectors import LiveJournal
>>> lj_stat = LiveJournal()
>>> lj_stat.accounts = ['tema', 'drugoi', 'zyalt']
>>> lj_stat.profiles()
{'drugoi': {'followers': 78984,
            'id': 'drugoi',
            'link': 'http://users.livejournal.com/drugoi/',
            'name': u'Журнал Другого',
            'nickname': 'drugoi',
            'statuses': u'14519',
            'type': 'person'},
 'tema': {'followers': 77734,
          'id': 'tema',
          'link': 'http://users.livejournal.com/tema/',
          'name': u'мы приготовили для Вас приятное напоминание о теплом лете, Бабочку держатель с оживляющим эффектом.',
          'nickname': 'tema',
          'statuses': u'6137',
          'type': 'person'},
 'zyalt': {'followers': 62946,
           'id': 'zyalt',
           'link': 'http://users.livejournal.com/zyalt/',
           'name': u'Шик и великолепие!',
           'nickname': 'zyalt',
           'statuses': u'3780',
           'type': 'person'}}
```

But when you often switch between multiple connectors - it's easier to use universal `Connection(net)` class. This class returns initialised connector to social media channel, specified using _net_ parameter. `net` - is a two-letter abbreviation, unique for every registered in smapy.CONNECTORS connector. The above example with the same result, using `Connection(net)` class:

```python
>>> from smapy import Connection
>>> lj_stat = Connection('lj')
>>> lj_stat.accounts = ['tema', 'drugoi', 'zyalt']
>>> lj_stat.profiles()
{'drugoi': {'followers': 78984,
            'id': 'drugoi',
            'link': 'http://users.livejournal.com/drugoi/',
            'name': u'Журнал Другого',
            'nickname': 'drugoi',
            'statuses': u'14519',
            'type': 'person'},
 'tema': {'followers': 77734,
          'id': 'tema',
          'link': 'http://users.livejournal.com/tema/',
          'name': u'мы приготовили для Вас приятное напоминание о теплом лете, Бабочку держатель с оживляющим эффектом.',
          'nickname': 'tema',
          'statuses': u'6137',
          'type': 'person'},
 'zyalt': {'followers': 62946,
           'id': 'zyalt',
           'link': 'http://users.livejournal.com/zyalt/',
           'name': u'Шик и великолепие!',
           'nickname': 'zyalt',
           'statuses': u'3780',
           'type': 'person'}}
```

List of avaliable connectors (already registered) with two-letter abbreviation:

    - `tw` - Twitter
    
    - `fb` - Facebook
    
    - `gp` - Google+
    
    - `ig` - Instagram
    
    - `lj` - LiveJournal
    
    - `vk` - VKontakte
    
    - `yt` - YouTube

## Documentation

Every connector is to be unified with others. So there are quite a few differences between them, and that differences concern optional parameters. So here abstract connector will be described. IRL substitute `smapy.connectors.Connector()` with appropriate connector (i.e., `smapy.connectors.Twitter()`, `smapy.connectors.Facebook()`) or `smapy.Connection(net)` object.

## Properties

* .Connector().**network** and .Connector().**name**

  (1) Two-letter abbreviation, unique for every network, and (2) full name of the network, connector used for. These propiertes are avaliable before connector initialisation and unchangeable. These properties are used to register connector in smapy.CONNECTORS agregator.
  
  *Example:*
  
  ```python
  >>> from smapy.connectors import GooglePlus
  >>> GooglePlus.network
  u'gp'
  >>> GooglePlus.name
  u'Google+'
  ```

* **accounts**

  Propierty created on connector initialization. By default it is an epty dict object. `.Connector().accounts()` stores user names to work with. Dict type is used to make it possible to use user-comfortable names as keys, and specific network nicknames or ids as values.
  
  It is possible to assign to `.Connector().accounts()` not only dict, but also list, set, tuple, or string object. On assigning they will be converted to dict: in case of list-like objects every element would be both key and value, in case of string (or unicode, or int) - dict with one key-value pair would be created.
  
  Reassigning `.Connector().accounts()` on initialised connector deletes all previously collected data (profiles, statuses, comments, etc.).
  
  *Example:*
  
  ```python
  >>> from smapy.connectors import Twitter
  >>> twit_stat = Twitter()
  >>> twit_stat.accounts
  {}
  >>> twit_stat.accounts = {'RIA Novosti':'rianru', 'The Moscow News':'themoscownews'}
  >>> twit_stat.accounts
  {'RIA Novosti': 'rian', 'The Moscow News': 'themoscownews'}
  >>> twit_stat.accounts = ['rianru', 'themoscownews']
  >>> twit_stat.accounts
  {'rianru': 'rianru', 'themoscownews': 'themoscownews'}
  >>> twit_stat.accounts = 'rianru'
  >>> twit_stat.accounts
  {u'rianru': u'rianru'}
  ```

* **token**

  Access token to make requests to network's API. Not required for some networks (i.e. Livejournal). Read more about how to get tokens to different networks:
  
  * [Facebook token](/smapy/docs/facebook_token/)

  * [Twitter token](/smapy/docs/twitter_token/)

  * [Google token](/smapy/docs/google_token/)

  * [Instagram token](/smapy/docs/instagram_token/)

  * [VKontakte token](/smapy/docs/vkontakte_token/)

  * [Odnoklassniki token](/smapy/docs/odnoklassniki_token/)

* **start_date**

  This is `datetime`-variable, pointing to timestamp from which posts and comments are being collected. Default value is January, 1 1990.

* **fin_date**

  `datetime` variable, specifying point, until posts and comments are being collected. Default value is `datetime.datetime.now()` (current local date and time).

## Functions-properties

BaseConnector itself describes functions, that are more properties.
Different connectors just use their own get_{property} functions.
List of functions-properties:

* **profiles**

  Dictionary object. Keys - the same as **accounts** dict keys.
  Values - None (if error with object occured) or dict with these keys:
  
    ```python
        {
         'id'       :STRING,
         'nickname' :STRING,
         'name'     :STRING,
         'link'     :STRING,
         'followers':INT,
         'type'     :STRING
        }
    ```

    - id - Network-specific user's id. Can be used (but not necessary) to build canonical URL for profile. In smapy used for definite object identification.
    
    - nickname - Part of url, used to identify user inside the network. Can be based on id, or represent seaprate short name.
    
    - name - Full name, specified by user.
    
    - link - URL to account's profile (not necessary canonical form).
    
    - followers - number of other accounts inside network, who can view posts/publications of current account. I.e., in Twitter - number of followers; in LiveJournal - number of 'friends of' for personal account, or members for communities; for personal Facebook accounts - it's number of friends plus number of subscribers.
    
    - type - 'person' or 'page' - distinguishes personal user accounts and pages/groups/communities/events (all types of collective accounts, avaliable for specified network).

* **statuses**

  Dictionary object. Keys - the same as **accounts** dict keys.
  Values - list of statuses/posts/tweets by person (possibly empty).
  Every list element is a dict with these keys:

    ```python
        {
         'id'     :STRING,
         'link'   :STRING,
         'date'   :DATETIME,
         'reposts':INT,
         'replies':INT,
         'likes'  :INT,
         'text'   :STRING
        }
    ```

    - id -
    
    - link -
    
    - date - 
    
    - reposts - 
    
    - replies - 
    
    - likes - 
    
    - text - 

* **comments**

  Dictionary object. Keys - the same as ACCOUNTS dict keys.
  Values - list of comments/replies to person (possibly empty).
  Every list element is a dict with these keys:

    ```python
        {
         'id'         :STRING,
         'link'       :STRING,
         'date'       :DATETIME,
         'in_reply_to':STRING,
         'author_id'  :STRING,
         'text'       :STRING
        }
    ```

## Functions

Every connector, based on BaseConnector required to have these functions:

- `get_profiles()`;

- `get_statuse()`;

- `get_comments()`;

- `check_token()`.