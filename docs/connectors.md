---
layout: page
title: Connectors
---

# Connectors

Most of the popular social media services have APIs (application programming interfaces). Using them, one could collect a lot of interesting research data. But there are some difficulties. Every API has its own request endpoints, syntax, response format, rate limits, etc. If you are dealing with more than one social media source - you constantly have to switch between these API-languages. Moreover, if you want to compare multiple networks, first you have to "similarify" your data from different sources.

The main purpose of connectors - is to build a high-level meta-API wrapper, and to bring to network data required similarity. There is no need to care about how alike concepts are called in different networks (i.e. "tweet" in Twitter, "status" in Facebook, or "post" in Livejournal), and what exactly endpoints you should use. Also connectors keep track of rate limits and handle errors and exceptions.

Connectors output standardized pieces of data, that could be used "as is", or processed to more complex models.

## Aviable connectors

<table>
  <tr>
    <th>Time rates*</th><th>persons</th><th>statuses</th><th>comments</th>
  </tr>
  <tr>
    <td>[Facebook connector](/smapy/docs/facebook_connector/)</td><td>50</td><td>750</td><td>2500</td>
  </tr>
  <tr>
    <td>[Twitter connector](/smapy/docs/twitter_connector/)</td><td>1000</td><td>1000</td><td>1000</td>
  </tr>
  <tr>
    <td>[GooglePlus connector](/smapy/docs/googleplus_connector/)</td><td>100</td><td>1000</td><td>2000</td>
  </tr>
  <tr>
    <td>[YouTube connector](/smapy/docs/youtube_connector/)</td><td>50</td><td>400</td><td>700</td>
  </tr>
  <tr>
    <td>[Instagram connector](/smapy/docs/instagram_connector/)</td><td>100</td><td>500</td><td>2000</td>
  </tr>
  <tr>
    <td>[LiveJournal connector](/smapy/docs/livejournal_connector/)</td><td>30</td><td>10</td><td>40</td>
  </tr>
  <tr>
    <td>[VKontakte connector](/smapy/docs/vkontakte_connector/)</td><td>50</td><td>3000</td><td>5000</td>
  </tr>
</table>

\* Time costs evaluated in average number of collected instances per 1 minute.

| Time rates | profiles | statuses | comments |
|------------|----------|----------|----------|
|      [safsad](/smapy/)|  adfsad  |      asdf|  dfsdfad |
|      safsad|  adfsad  |      asdf|  dfsdfad |

## Properties

* **accounts**
  
  Dictionary object. Keys - 'real' users' names, values - their nicknames or ids in specified network.

* **network**

  Two-letter abbreviation, unique for every network:
  
    - `tw` - Twitter
    
    - `fb` - Facebook
    
    - `gp` - Google+
    
    - `ig` - Instagram
    
    - `lj` - LiveJournal
    
    - `vk` - VKontakte
    
    - `yt` - YouTube

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