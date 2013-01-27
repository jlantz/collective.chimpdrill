import doctest
import unittest

from datetime import datetime

from five import grok

from collective.chimpdrill.utils import IMailsnakeConnection


MC_TEMPLATE_HTML = """
<html>
<head>
  <style type="text/css">
    #test-container {
        background-color: red;
    }
    #test-container p {
        color: green;
    }
  </style>
</head>
<body>
  <div id="test-container">
    <p mc:edit="block1">Template Name: %s</p>
  </div>
</body>
</html>
"""

MC_TEMPLATE_INLINED_HTML = """
<html>
<head>
  <style type="text/css">
    #test-container {
        background-color: red;
    }
    #test-container p {
        color: green;
    }
  </style>
</head>
<body>
  <div id="test-container" style="background-color: red">
    <p mc:edit="block1" style="background-color: red; color: green">Template Name: %s</p>
  </div>
</body>
</html>
"""

DEFAULT_CREATED_DATE = datetime(2012, 1, 1)
DEFAULT_UPDATED_DATE = datetime(2013, 1, 15)
DEFAULT_PUB_DATE = datetime(2012, 12, 21)

class DummyMailsnakeConnectionUtil(object):
    grok.implements(IMailsnakeConnection)

    def get_mailchimp(self):
        return DummyMailchimpConnection()

    def get_mandrill(self):
        return DummyMandrillConnection()
    

class DummyMailsnake(object):

    def __init__(self, test=None, api=None):
        if api is None:
            return DummyMailchimpConnection()

        if api == 'mandrill':
            # Mimick Mailsnake exception raised by Mandrill API ping
            if test is not False:
                # FIXME - insert execption here
                pass
            return DummyMandrillConnection()

class DummyMailchimpConnection(object):
    def templates(self):
        return {'user': [
            {'id': 1, 'name': 'Test Template 1'},
            {'id': 2, 'name': 'Test Template 2'},
            {'id': 3, 'name': 'Test Template 3'},
        ]}

    def templateInfo(self, tid):
        name = 'Test Template %s' % tid
        return {
            'name': name,
            'default_content': {'block1': 'Block 1 Default Text'},
            'sections': ['block1',],
            'preview': MC_TEMPLATE_HTML % name,
            'source': MC_TEMPLATE_HTML % name,
        }

    def templateAdd(self, name, html):
        return 3

    def inlineCss(self, html):
        return MC_TEMPLATE_INLINED_HTML % 'INLINED TITLE'
    

class DummyMandrillTemplates(object):
    def list(self):
        pass

    def add(self, **kwargs):
        return {
            'slug': kwargs['name'],
            'name': kwargs['name'],
            'code': kwargs['code'],
            'publish_name': kwargs['name'],
            'publish_code': kwargs['code'],
            'published_at': DEFAULT_PUB_DATE,
            'created_at': DEFAULT_CREATED_DATE,
            'updated_at': DEFAULT_UPDATED_DATE,
        }

    def update(self, **kwargs):
        return {
            'slug': kwargs['name'],
            'name': kwargs['name'],
            'code': kwargs['code'],
            'publish_name': kwargs['name'],
            'publish_code': kwargs['code'],
            'published_at': DEFAULT_PUB_DATE,
            'created_at': DEFAULT_CREATED_DATE,
            'updated_at': DEFAULT_UPDATED_DATE,
        }

    def info(self, **kwargs):
        return {
            'slug': kwargs['name'],
            'name': kwargs['name'],
            'code': MC_TEMPLATE_HTML % kwargs['name'],
            'publish_name': kwargs['name'],
            'publish_code': MC_TEMPLATE_HTML % kwargs['name'],
            'published_at': DEFAULT_PUB_DATE,
            'created_at': DEFAULT_CREATED_DATE,
            'updated_at': DEFAULT_UPDATED_DATE,
        }

class DummyMandrillConnection(object):
    templates = DummyMandrillTemplates()

