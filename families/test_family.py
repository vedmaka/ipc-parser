# -*- coding: utf-8  -*-

__version__ = '$Id: test_family.py 11553 2013-05-19 11:15:48Z xqt $'

import family

# The test wikipedia family
class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'test'
        self.langs = {
            'test': 'test.wikipedia.org',
        }
        if family.config.SSL_connection:
            self.langs['test'] = None


        self.namespaces[4] = {
            '_default': [u'Wikipedia', self.namespaces[4]['_default']],
            'test': [u'Wikipedia', u'WP'],
        }
        self.namespaces[5] = {
            '_default': [u'Wikipedia talk', self.namespaces[5]['_default']],
            'test': [u'Wikipedia talk', u'WT'],
        }
        self.namespaces[90] = {
            '_default': u'Thread',
        }
        self.namespaces[91] = {
            '_default': u'Thread talk',
        }
        self.namespaces[92] = {
            '_default': u'Summary',
        }
        self.namespaces[93] = {
            '_default': u'Summary talk',
        }
        self.namespaces[710] = {
            '_default': u'TimedText',
        }
        self.namespaces[711] = {
            '_default': u'TimedText talk',
        }
        self.namespaces[866] = {
            '_default': u'CNBanner',
        }
        self.namespaces[867] = {
            '_default': u'CNBanner talk',
        }
        self.namespaces[1198] = {
            '_default': u'Translations',
        }
        self.namespaces[1199] = {
            '_default': u'Translations talk',
        }
        self.namespaces[2500] = {
            '_default': u'VisualEditor',
        }
        self.namespaces[2501] = {
            '_default': u'VisualEditor talk',
        }
        self.interwiki_forward = 'wikipedia'
