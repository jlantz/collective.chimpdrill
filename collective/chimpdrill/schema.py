from zope import schema
from zope.interface import Interface
from zope.interface import alsoProvides
from z3c.relationfield import RelationChoice
from plone.directives import form
from plone.app.textfield import RichText

class ITemplate(Interface):
    """ Base interface for chimpdrill template schemas """ 
    send_to = schema.TextLine(
        title=u"Send to Email Address",
        description=u"Enter the email address you wish to send this template to."
    )

class IBody(Interface):
    """ Schema mixin for content title and body blocks """
    block_title = schema.TextLine(
        title=u"Title",
        description=u"The email's subject and the title merge variable",
    )
    block_body = RichText(
        title=u"Body Content",
        description=u"This content will be merged into the body"
    )

class ITarget(Interface):
    """ Schema mixin for linking to content """
    target_title = schema.TextLine(
        title=u"Target Title",
        description=u"The title of the target content exposed as target_title merge variable in the template",
    ) 
    target_description = schema.Text(
        title=u"Target Description",
        description=u"A brief summary of the target content exposed as the target_description merge variable in the template",
        required=False,
    )
    target_url = schema.TextLine(
        title=u"Target URL",
        description=u"The URL to the target content",
    )
    block_target = RichText(
        title=u"Target Block Content",
        description=u"This content populates the 'target' mc:edit block if it exists in the template",
        required=False,
    )

class IBasic(form.Schema, ITemplate):
    """ Schema for basic input only """ 

class IBodyAndTarget(form.Schema, ITemplate, IBody, ITarget):
    """ Schema for body and target """
    
class IBodyOnly(form.Schema, ITemplate, IBody):
    """ Schema for body and target """
    
class ITargetOnly(form.Schema, ITemplate, ITarget):
    """ Schema for target only """
    
