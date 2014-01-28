---
title: Document Center
---

Connector to Facebook social network (http://www.facebook.com).

### Time costs:
* PROFILES: ~50 users per 1 minute;
* STATUSES: ~750 statuses per 1 minute (with `count_replies=False` and `count_likes=False`);
* COMMENTS: ~2500 comments per 1 minute.

### API restrictions:
* PROFILES:
    - If using app-token (not user token) - followers count is not avaliable.


### Additional settings:
* STATUSES:
    - `count_replies = True/False` (default - True). Count number of comments per status. Original API has no 'replies_count' fieled. If `count_replies = True`, connector collects comments for every post and then counts them. It takes much more time: actually all comments section is being collected. If you don't need number of comments - switch this parameter to False to speedup the process.
    - `count_likes = True/False` (default - True). Count number of likes per status. Original API has no 'likes_count' fieled. If `count_likes = True`, connector collects likes (with authorship) for every post and then counts them. It takes much more time. If you don't  need number of likes - switch this parameter to False. Then every status `likes` parameter would be equal to zero.

### Additional fields:
* PROFILES:
    - `type`: person or page instance

### Access token format:
Two types of token-data are available in [[KeyChain]] object:

1. `token = 'ACCESS_TOKEN_STRING'` - real access token, that is used to make requests. If App access token is used - it can be stored in such form, but it has some API-restrictions. Don't store User access token in this form: due to security reasons such tokens expires. User access tokens should be stored in raw formed and renewed every time, application is being executed. [[KeyChain]] identifier: `fb`.

2. Raw access data. [[KeyChain]] identifier: `raw_fb`. Format:

    ```python
    token = {
        'app_id'    :STRING,
        'app_secret':STRING,
        'app_url'   :STRING,
        'login'     :STRING,
        'password'  :STRING
    }
    ```
    In this form token data could be stored for unlimited time. Before using your token call `KeyChain().autocomplete()` or `fb_auth` function from `smapy.utilities` to generate valid common access token.

    Read how to get access token: [[Facebook token]]