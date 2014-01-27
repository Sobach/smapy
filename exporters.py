# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy - exporters module
Exporters for models (text-files, tables, graphs, etc.)
* report_users_networks - creates .txt file with full wall texts for multiple
  persons. Some kind of markup is used:
    - [h1] - first level header (user name)
    - [h2] - second level header (network name)
    - [h3] - third level header (post number)
    - [b] - bold text - date
    - [comment] - this text is a comment
"""

from settings import *

def datetimeformat(value, format='%d.%m.%Y'):
    """date-time jinja filter"""
    return value.strftime(format)

def linebrakes(text, tag = '[comment]'):
    """line-breaks tag adder jinja filter"""
    return text.replace('\n', '\n{}'.format(tag))

def report_users_networks(users, fname):
    """accounts exporter to txt-document with tags"""
    template = u'''{% for user in users %}[h1]{{ user.name }}
{% for network, posts in user.walls.iteritems() %}[h2]{{ network }}
{% for post in posts %}[h3]post {{ loop.index }}
[b]{{ post.date|datetimeformat }}
{{ post.text }}
{{ post.link }}{% if post.comment_tree|length > 0 %}\n\n{% endif %}{% for comment in post.comment_tree %}[comment]{{ comment.text|linebrakes }}
[comment]{{ comment.link }}{% if not loop.last %}\n\n{% endif %}{% endfor %}{% if not loop.last %}\n\n{% endif %}{% endfor %}{% if not loop.last %}\n\n{% endif %}{% endfor %}{% if not loop.last %}\n\n{% endif %}{% endfor %}'''
    import codecs
    from jinja2 import Template, Environment
    env = Environment()
    env.filters['datetimeformat'] = datetimeformat
    env.filters['linebrakes'] = linebrakes
    template = env.from_string(template)
    file = codecs.open(fname, 'w', 'utf-8')
    users = [{'name':user.name, 'walls':{user.wall_from_network(x).network_title: user.wall_from_network(x).statuses for x in user.networks}} for user in users]
    file.write(template.render(users = users))
    file.close()