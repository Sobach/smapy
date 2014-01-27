Connector to Google Plus social network (http://plus.google.com).

### Time costs:
* PROFILES: ~100 users per 1 minute;
* STATUSES: ~1000 posts per 1 minute;
* COMMENTS: ~2000 comments per 1 minute.

### API restrictions:
* PROFILES:
    - `followers` number avaliable only for public pages. For persons and private pages it is equal to zero. It's privacy policy issue.

### Additional fields:
* PROFILES:
    - `type`: person or page instance.

### Access token format:
Connector uses API Key without identifying a particular user. [[KeyChain]] identifier: `gp`. Token format: `token = 'ACCESS_TOKEN_STRING'`.

Read how to get access token: [[Google token]]