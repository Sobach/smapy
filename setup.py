# -*- coding: utf-8 -*-
#!/usr/bin/env python

from setuptools import setup

setup(name='smapy',
      version='0.3.3',
      description='Single wrapper for main social media API\'s',
      long_description='''Social media anatomist for Python is a comprehensive tool for social media researchers: sociologists, culturologists, anthropologists, etc. It provides unified interfaces to number of popular social networks and blog platforms (Connectors) and several templates for models representation (Exporters).''',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: Russian',
        'Topic :: Sociology',
      ],
      keywords='social media networks facebook twitter vkontakte instagram googleplus livejournal youtube',
      url='http://www.facebook/atolmach',
      author='Alexander Tolmach',
      author_email='tolmach@me.com',
      license='MIT License',
      packages=['smapy', 'smapy.network_connectors'],
      install_requires=[
          'beautifulsoup4',
          'jinja2',
      ],
      zip_safe=False)