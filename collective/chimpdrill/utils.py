#from zope.site.hooks import getSite
from five import grok
from zope.interface import Interface
from zope import schema
from mailsnake import MailSnake
from mailsnake.exceptions import MailSnakeException
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.chimpdrill.controlpanel import IChimpdrillSettings

def get_settings():
    registry = getUtility(IRegistry)
    return registry.forInterface(IChimpdrillSettings, False)

class IMailsnakeConnection(Interface):
    def get_mailchimp():
        """ Returns a Mailsnake connection instance to the Mailchimp API """
    def get_mandrill():
        """ Returns a Mailsnake connection instance to the Mailchimp API """

class MailsnakeConnection(object):
    grok.implements(IMailsnakeConnection)
    
    def lookup_key(self, api):
        settings = get_settings()
        if api is None or api == 'api':
            return settings.mailchimp_api_key
        if api == 'mandrill':
            return settings.mandrill_api_key

    def get_connection(self, api):
        key = self.lookup_key(api)
        return MailSnake(key, api=api)

    def get_mailchimp(self):
        return self.get_connection('api')

    def get_mandrill(self):
        return self.get_connection('mandrill')

grok.global_utility(MailsnakeConnection, provides=IMailsnakeConnection)
