Connector to LiveJournal blog platform (http://www.livejournal.com).

### Time costs:
* PROFILES: ~30 users per 1 minute;
* STATUSES: ~10 posts per 1 minute (with `get_replies=False`);
* COMMENTS: ~40 comments per 1 minute.

### Additional settings:
* STATUSES:
    - `get_replies = True/False` (default - True). In LiveJournal comments crawling organized through posts parsing. So - if you are collecting posts and going later to collect comments - just leave default value. Otherwise - if you don't need comments (text data, number of comments will be collected in both cases) - set get_replies to False. It will speedup crawling.

### Additional fields:
* PROFILES:
    - `type`: person or page (community) instance

### Access token format:
There is no need in access token in LiveJournal.