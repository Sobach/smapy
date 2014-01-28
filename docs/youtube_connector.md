---
title: Document Center
---

Connector to YouTube video sharing system (http://www.youtube.com).

### Time costs:
* PROFILES: ~50 users per 1 minute;
* STATUSES: ~400 statuses per 1 minute (without "slowmotion" mode: `slowmo=0`);
* COMMENTS: ~700 comments per 1 minute.

### Additional settings:
* STATUSES:
    - `slowmo = time_interval` (default - 0). 

### Access token format:
Connector uses API Key without identifying a particular user. [[KeyChain]] identifier: `yt`. Token format: `token = 'ACCESS_TOKEN_STRING'`.

Read how to get access token: [[Google token]]