Connector to Twitter micro-blog platform (http://www.twitter.com).

### Time costs:
* PROFILES: ~1000 users per 1 minute;
* STATUSES: ~1 user's timeline per 2 minutes (with `count_replies=False`, 2k tweets maximum);
* COMMENTS: replies to ~1 user per 1 minute (1k replies per user maximum).

### API restrictions:
* STATUSES:
    - Twitter doesn't care about history/storaging. So there is no opportunity to get old tweets. Generally only last ~2k tweets are avaliable.
* COMMENTS:
    - There is no special endpoint for replies. So smapy uses search API to find replies to exact user, and then matches them to original tweets. Search API response for one query is limited to ~1k tweets. So, if there is more replies to one person - this data wuold be lost.

### Additional settings:
* STATUSES:
    - `with_rts = True/False` (default - False). Collect only original author tweets, or his tweets and retweets in his timeline. Note, that statistics for retweets is taken from originals.
    - `count_replies = True/False` (default - True). Count number of replies for every tweet. Original API has no 'replies' fieled, so connector uses Search to find replies. It takes much more time: actually all comments section is being collected. If you don't need number of comments - switch this parameter to False to speedup the process.

### Compatibility features:
* STATUSES:
    - `likes` field is always equal to zero. There is no likes in Twitter, and this field is used for unification purposes.

### Access token format:

Token data is stored in dictionary-like object. [[KeyChain]] identifier: `tw`.

```python
token = {
    'consumer_key'    : ...,
    'consumer_secret' : ...,
    'access_token'    : ...,
    'access_secret'   : ...
        }
```

Read how to get access token: [[Twitter token]]