# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = u'Erdem \xd6zkol'
SITENAME = u'Erdem \xd6zkol | Blog'
SITEURL = ''

PATH = 'content'


TIMEZONE = 'Europe/Istanbul'

DEFAULT_LANG = 'tr'

# LOCALE = u'tr_TR'

DEFAULT_DATE_FORMAT = u"%d %B %Y"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 5

GITHUB = "https://github.com/erdemozkol/"
TWITTER = "https://twitter.com/erdemozkol/"
EMAIL = "erdemozkol@gmail.com"
COMPANY = "http://hipolabs.com/"


THEME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes', 'pastel')

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

