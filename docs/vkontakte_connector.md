---
layout: default
title: VKontakte connector
---

# VKontakte connector

Connector to VK social network ([http://www.vk.com](http://www.vk.com)).

### Time costs:

* PROFILES: ~50 users per 1 minute;

* STATUSES: ~3000 statuses per 1 minute (with `count_replies=False` and `count_likes=False`);

* COMMENTS: ~5000 comments per 1 minute.

### Additional fields:

* PROFILES:

    - `type`: person or page instance

### Access token format:

Two types of token-data are available in [KeyChain](/smapy/docs/keychain/) object:

1. `token = 'ACCESS_TOKEN_STRING'` - real access token, that is used to make requests. It's time-limited, so you need to update it every time when using connector.

2. Raw access data. [KeyChain](/smapy/docs/keychain/) identifier: `raw_vk`. Format:

    ```python
    token = {
        'app_id'    :STRING,
        'app_secret':STRING,
        'login'     :STRING,
        'password'  :STRING
    }
    ```
    
    In this form token data could be stored for unlimited time. Before using your token call `KeyChain().autocomplete()` or use `vk_auth` function from `smapy.utilities` to generate valid common access token.

    Read how to get access token: [VKontakte token](/smapy/docs/vkontakte_token/)