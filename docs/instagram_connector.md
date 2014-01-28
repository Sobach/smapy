---
layout: default
title: Instagram connector
---

Connector to Instagram ([http://www.instagram.com](http://www.instagram.com)).

## Time costs:

* PROFILES: ~100 users per 1 minute;

* STATUSES: ~500 statuses per 1 minute;

* COMMENTS: ~2000 comments per 1 minute.

## API restrictions:

* COMMENTS:

    - There is no tools to extract more than 150 comments for each photo.

## Compatibility features:

* STATUSES:

    - `reposts` field is always equal to zero. There is no reposts/shares instances in Instagram.

## Access token format:

Access token used in connector is a simple string variable. As for now - it doesn't expire. So you can use it as long as you need.

`token = 'ACCESS_TOKEN_STRING'`

[KeyChain](/smapy/docs/keychain/) token identifier is `ig`.

Read how to get access token: [Instagram token](/smapy/docs/instagram_token/)