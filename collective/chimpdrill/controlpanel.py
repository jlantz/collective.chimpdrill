from z3c.form import interfaces

from zope import schema
from zope.interface import Interface

from plone.app.registry.browser import controlpanel

class IChimpdrillSettings(Interface):
    """ Global settings for collective.chimpdrill stored in the registry """
    template_schemas = schema.List(
        title=u"Schemas",
        description=u"format: label|interface_path",
        value_type=schema.TextLine(),
        default=[
            u"Basic|collective.chimpdrill.schema.IBasic",
            u"Target Only|collective.chimpdrill.schema.ITargetOnly",
            u"Body Only|collective.chimpdrill.schema.IBodyOnly",
            u"Body and Target|collective.chimpdrill.schema.IBodyAndTarget",
        ]
    )

    mailchimp_api_key = schema.TextLine(
        title=u"Mailchimp API Key",
        description=u"This can be located in the account settings of your Mailchimp acccount",
    )
    
    mandrill_api_key = schema.TextLine(
        title=u"Mandrill API Key",
        description=u"This can be located in the account settings of your Mandrill acccount",
    )
    

class ChimpdrillSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IChimpdrillSettings
    label = u"Mailchimp/Mandrill settings"
    description = u"Configuration for collective.chimpdrill providing integration with Mailchimp and Mandrill"

    def updateFields(self):
        super(ChimpdrillSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(ChimpdrillSettingsEditForm, self).updateWidgets()

class ChimpdrillSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ChimpdrillSettingsEditForm
