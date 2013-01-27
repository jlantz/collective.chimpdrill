from five import grok
from zope import schema
from zope.interface import alsoProvides
from plone import namedfile
from zope.app.content.interfaces import IContentType
from plone.directives import dexterity, form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

class IRepository(form.Schema):
    """
    A container for templates
    """

alsoProvides(IRepository, IContentType)

class Repository(dexterity.Container):
    grok.implements(IRepository)

class RepositoryView(grok.View):
    grok.context(IRepository)
    grok.require('zope2.View')

    grok.name('view')
    grok.template('view')
