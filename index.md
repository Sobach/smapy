---
layout: default
title: Home
---

Social media anatomist for Python (smapy) is a comprehensive tool for social media researchers: sociologists, culturologists, anthropologists, etc. It provides unified interfaces to number of popular social networks and blog platforms (Connectors); collection of structured data instances (Models); and several templates for models representation (Exporters). These three blocks correspond to appropriate data-collecting stages:

* Creating standardized bricks of raw social media data;

* Building from these bricks comparable models;

* Saving models in suitable form:

    - formatted text reports
    
    - statistic tables;
    
    - graph/network structures.

# Connectors

Most of the popular social media services have APIs (application programming interfaces). Using them, one could collect a lot of interesting research data. But there are some difficulties. Every API has its own request endpoints, syntax, response format, rate limits, etc. If you are dealing with more than one social media source - you constantly have to switch between these API-languages. Moreover, if you want to compare multiple networks, first you have to "similarify" your data from different sources.

The main purpose of connectors - is to build a high-level meta-API wrapper, and to bring to network data required similarity. There is no need to care about how alike concepts are called in different networks (i.e. "tweet" in Twitter, "status" in Facebook, or "post" in Livejournal), and what exactly endpoints you should use. Also connectors keep track of rate limits and handle errors and exceptions.

Connectors output standardized pieces of data, that could be used "as is", or processed to more complex models.

Available connectors:

- `tw` - [Twitter](/smapy/docs/twitter_connector/)
    
- `fb` - Facebook
    
- `gp` - Google+
    
- `ig` - Instagram
    
- `lj` - LiveJournal
    
- `vk` - VKontakte
    
- `yt` - YouTube

# Models

Connectors return unified but separate pieces of data. Models - are next abstraction level objects. They combine these pieces into high-level model. E.g. profile, statuses and comments pieces from connector could be used to build AccountWall object. Using different AccountWall functions one can compute stats or build comments tree, etc. Multiple AccountWall objects could be processed to PersonWalls (if all these accounts belong to one subject) or NetworkWalls (if all accounts are from the same network).

# Exporters

It's not necessary to process collected data in Python itself. Sometimes it's easier to analyse it in a more familiar form in other software. E.g., posting and commenting statistics - in spreadsheet editor (Excel or whatever), friendship network - in Gephi, it's easier to make content analysis in properly formatted text document. 'Exporters' - is a set of appropriate functions. They take models as input and produce .gexf (graph), .csv (tables) or .md (text) files.