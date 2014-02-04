---
layout: page
title: Connectors
---

# Connectors

Most of the popular social media services have APIs (application programming interfaces). Using them, one could collect a lot of interesting research data. But there are some difficulties. Every API has its own request endpoints, syntax, response format, rate limits, etc. If you are dealing with more than one social media source - you constantly have to switch between these API-languages. Moreover, if you want to compare multiple networks, first you have to "similarify" your data from different sources.

The main purpose of connectors - is to build a high-level meta-API wrapper, and to bring to network data required similarity. There is no need to care about how alike concepts are called in different networks (i.e. "tweet" in Twitter, "status" in Facebook, or "post" in Livejournal), and what exactly endpoints you should use. Also connectors keep track of rate limits and handle errors and exceptions.

Connectors output standardized pieces of data, that could be used "as is", or processed to more complex models, or saved in suitable form using exporters.

## Aviable connectors and time rates for base data pieces

Every connector is a class, that inherits from `smapy.connectors.base.BaseConnector()`. This is done for maximal similarity. The only pieces, implemented individually in every conncetor concern low-level API interactions.

| class propierty                                                            | .profiles() | .statuses() | .comments() |
|----------------------------------------------------------------------------|-------------|-------------|-------------|
| [`smapy.connectors.Facebook()`](/smapy/docs/facebook_connector/)           |  50         | 750         |  2500       |
| [`smapy.connectors.Twitter()`](/smapy/docs/twitter_connector/)             |  1000       | 1000        |  1000       |
| [`smapy.connectors.GooglePlus()`](/smapy/docs/googleplus_connector/)       |  100        | 1000        |  2000       |
| [`smapy.connectors.YouTube()`](/smapy/docs/youtube_connector/)             |  50         | 400         |  700        |
| [`smapy.connectors.Instagram()`](/smapy/docs/instagram_connector/)         |  100        | 500         |  2000       |
| [`smapy.connectors.LiveJournal()`](/smapy/docs/livejournal_connector/)     |  30         | 10          |  40         |
| [`smapy.connectors.VKontakte()`](/smapy/docs/vkontakte_connector/)         |  50         | 3000        |  5000       |
| [`smapy.connectors.Odnoklassniki()`](/smapy/docs/odnoklassniki_connector/) |  -          | -           |  -          |

\* Time costs evaluated in average number of collected instances per 1 minute.

## smapy.Connection(_net_) class

Every connector could be imported from `smapy.connectors` package. I.e.:

```python
>>> from smapy.connectors import LiveJournal
>>> lj_stat = LiveJournal()
>>> lj_stat.accounts = 'drugoi'
>>> lj_stat.profiles()
{'drugoi': {'followers': 78984,
            'id': 'drugoi',
            'link': 'http://users.livejournal.com/drugoi/',
            'name': u'Журнал Другого',
            'nickname': 'drugoi',
            'statuses': u'14519',
            'type': 'person'}}
```

But when you often switch between multiple connectors - it's easier to use universal `Connection(net)` class. This class returns initialised connector to social media channel, specified using _net_ parameter. `net` - is a two-letter abbreviation, unique for every registered in smapy.CONNECTORS connector. The above example with the same result, using `Connection(net)` class:

```python
>>> from smapy import Connection
>>> lj_stat = Connection('lj')
>>> lj_stat.accounts = 'drugoi'
>>> lj_stat.profiles()
{'drugoi': {'followers': 78984,
            'id': 'drugoi',
            'link': 'http://users.livejournal.com/drugoi/',
            'name': u'Журнал Другого',
            'nickname': 'drugoi',
            'statuses': u'14519',
            'type': 'person'}}
```

List of avaliable connectors (already registered) with two-letter abbreviation (`.Connector().network` property):

| Network       | .Connector().network | .Connector().name |
|---------------|----------------------|-------------------|
| Twitter       | `tw`                 | `Twitter`         |
| Facebook      | `fb`                 | `Facebook`        |
| GooglePlus    | `gp`                 | `Google+`         |
| Instagram     | `ig`                 | `Instagram`       |
| LiveJournal   | `lj`                 | `LiveJournal`     |
| VKontakte     | `vk`                 | `ВКонтакте`       |
| YouTube       | `yt`                 | `YouTube`         |
| Odnoklassniki | `ok`                 | `Одноклассники`   |

## Documentation

Every connector is to be unified with others. So there are quite a few differences between them, and that differences concern optional parameters. So here abstract connector will be described. IRL substitute `smapy.connectors.Connector()` with appropriate connector (i.e., `smapy.connectors.Twitter()`, `smapy.connectors.Facebook()`) or `smapy.Connection(net)` object.

### Properties

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

* .Connector().**accounts**

  Propierty created on connector initialization. By default it is an epty dict object. `.Connector().accounts` stores user names to work with. Dict type is used to make it possible to use user-comfortable names as keys, and specific network nicknames or ids as values.
  
  It is possible to assign to `.Connector().accounts` not only dict, but also list, set, tuple, or string object. On assigning they will be converted to dict: in case of list-like objects every element would be both key and value, in case of string (or unicode, or int) - dict with one key-value pair would be created.
  
  Reassigning `.Connector().accounts` on initialised connector deletes all previously collected data (profiles, statuses, comments, etc.).
  
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

* .Connector().**token**

  Access token to make requests to network's API. Not required for some networks (i.e. Livejournal). When working with smapy or any other program - you need to register it on media developers page, authenticate and authorise, and finnaly get access token. Without token most part of the data would be closed. To make the process easier we wrote how-to's for several networks: 
  * [Facebook token](/smapy/docs/facebook_token/)

  * [Twitter token](/smapy/docs/twitter_token/)

  * [Google token](/smapy/docs/google_token/)

  * [Instagram token](/smapy/docs/instagram_token/)

  * [VKontakte token](/smapy/docs/vkontakte_token/)

  * [Odnoklassniki token](/smapy/docs/odnoklassniki_token/)

  Follow them once to get your own access token for network(s), you are interested in. Then you can store your keys, using [`smapy.KeyChain()`](/smapy/docs/keychain/) class object.

* .Connector().**start_date** and .Connector().**fin_date**

  This is `datetime`-properties, pointing to timestamp from (start&#95;date) and to (fin&#95;date) which posts and comments are being collected. These dates are used to bound statuses and comments collecting period. If not specified, default values used:
  
  - January, 1 1990 for start_date

  - `datetime.datetime.now()` (current local date and time) for fin_date

  Reassigning `.Connector().start_date` or `.Connector().fin_date` on initialised connector deletes previously collected statuses and comments.


### Functions

* .Connector().**check_token()**

  Tries to make test request to appropriate social media to check validity of `self.token` property. Return `True` if access token is valid, otherwise -- `False`. Function, implemented in `smapy.connectors.base.BaseConnector()`, looks for `self.token` property, and then uses `self._token_checker()` function (specific for every connector class).

* .Connector().**profiles()**

  Checks, whether profiles data already collected, or not. If not - tries to collect it, using `self._get_statuses(**kargv)` function - it is specific for every connector. Collects data for every user, defined in `self.accounts`.
  
  Finnaly, returns dictionary object. Keys -- the same as `.Connector().accounts` dict keys.
  Values - `None` (if error with object occured) or dict with these keys:
  
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
    
    - nickname - Part of url, used to identify user inside the network. Can be based on id, or represent seaprate short name. Mostly - repeats `.Connector().accounts` values.
    
    - name - Full name, specified by user in network profile.
    
    - link - URL to account's profile (not necessary canonical form).
    
    - followers - number of other accounts inside network, who can view posts/publications of current account. I.e., in Twitter - number of followers; in LiveJournal - number of 'friends of' for personal account, or members for communities; for personal Facebook accounts - it's number of friends plus number of subscribers.
    
    - type - 'person' or 'page' - distinguishes personal user accounts and pages/groups/communities/events (all types of collective accounts, avaliable for specified network). In Twitter, YouTube, and Instagram `type` always equal to `person`. There is no different account types.

* .Connector().**statuses()**

  Checks, whether posts (or statuses) data already collected, or not. If not - tries to collect it, using `self._get_profiles(**kargv)` function - it is specific for every connector. Collects data for every user, defined in `self.accounts`. Time period bounded using `self.start_date` and `self.fin_date` properties. If not specified - default values are used.
  
  Finnaly, returns dictionary object. Keys - the same as `.Connector().accounts` dict keys. Values -- list of messages (statuses/posts/tweets) on person's/page's wall (in timeline) -- possibly empty.
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

    - id - Network-specific message id. Used to identify message itself and comments to this message.
    
    - link - URL of the message.
    
    - date - `datetime` object - time, when the message was written. By default current machine time zone used (not UTC).
    
    - reposts - number of actions, sharing the message's content to other audiences (share, retweet, repost, recommend, etc.).
    
    - replies - number of comments to the message (by other users or author himself).
    
    - likes - number of actions, marking the message as interesting (likes, +1's, favorites, etc.)
    
    - text - text of the message, cleaned from html tags and any media data.

* .Connector().**comments()**

  Checks, whether comments to author messages already collected, or not. If not - tries to collect it, using `self._get_comments(**kargv)` function - it is specific for every connector. Collects data for every user, defined in `self.accounts`. Time period bounded using `self.start_date` and `self.fin_date` properties. Limitation applied to original message publication timestamp. I.e., if post was published before `self.fin_date`, but got comment after this time, this comment will be collected. If bounds not specified - default values are used.
  
  Finnaly, returns dictionary object. Keys - the same as `.Connector().accounts` dict keys. Values -- list of comments to messages on person's/page's wall (in timeline) -- possibly empty.
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
    
    - id - Network-specific unique comment id. Used to identify comment.
    
    - link - URL of 'original' message with current comment highlighted.
    
    - date - `datetime` object - time, when the comment was written. By default current machine time zone used (not UTC).
    
    - in&#95;reply&#95;to - `id` of message (`status`) the comment was written to. Used to connect comments and messages.
    
    - author_id - `id` of the user, who wrote the comment. Could be used to collect additional data about him.
    
    - text - text of the comment, cleaned from html tags and any media data.

* .Connector().**statuses&#95;with&#95;comments()**

  Checks, whether author messages and comments to them already collected, or not. If not - tries to collect the data, using `self._get_statuses(**kargv)` and `self._get_comments(**kargv)` functions. Collects data for every user, defined in `self.accounts`. Time period bounded using `self.start_date` and `self.fin_date` properties. Limitation applied to original message publication timestamp.
  
  Finnaly, breaks comments by `in_reply_to` field and adds list of comments to every particular post. Returns dict object. Keys - the same as `.Connector().accounts` dict keys. Values -- list of messages (statuses/posts/tweets) on person's/page's wall (in timeline). Every message has list of related comments -- as one additional field. Every message is a dict with same as `self.statuses()` element keys with one additioanl field - 'comments' - that is a flat list of all realted to the post comments.
  
     ```python
        {
         'id'      :STRING,
         'link'    :STRING,
         'date'    :DATETIME,
         'reposts' :INT,
         'replies' :INT,
         'likes'   :INT,
         'text'    :STRING,
         'comments':LIST(comments_to_the_message)
        }
    ``` 

## Other

Some of described functions has specific optional parameters. Most of them concern concrete media platforms. Find out more about connectors you are interested in:

* [Facebook connector](/smapy/docs/facebook_connector/)

* [Twitter connector](/smapy/docs/twitter_connector/)

* [GooglePlus connector](/smapy/docs/googleplus_connector/)

* [YouTube connector](/smapy/docs/youtube_connector/)

* [Instagram connector](/smapy/docs/instagram_connector/)

* [LiveJournal connector](/smapy/docs/livejournal_connector/)

* [VKontakte connector](/smapy/docs/vkontakte_connector/)

* [Odnoklassniki connector](/smapy/docs/odnoklassniki_connector/)

Besides this, every connector has a bunch of "hidden" properties and functions. Find out more about them on [writing your own connector](/smapy/docs/new_connector/) page.