from datetime import datetime
from five import grok
from zope import schema
from zope.interface import alsoProvides
from zope.interface import invariant, Invalid
from zope.component import getUtility
from zope.dottedname.resolve import resolve
from plone import namedfile
from z3c.form import button
from zope.app.content.interfaces import IContentType
from zope.app.container.interfaces import IObjectAddedEvent
from plone.directives import dexterity, form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from collective.chimpdrill.utils import IMailsnakeConnection
from collective.chimpdrill.utils import get_settings

class MailchimpTemplatesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        mc = getUtility(IMailsnakeConnection).get_mailchimp()
        if not mc:
            return SimpleVocabulary()
    
        templates = mc.templates()
        if templates:
            templates = templates.get('user')
    
            for template in templates:
                terms.append(SimpleTerm(
                    value=template.get('id'),
                    token=str(template.get('id')),
                    title=template.get('name'),
                ))
    
        return SimpleVocabulary(terms)
grok.global_utility(MailchimpTemplatesVocabulary, name=u"collective.chimpdrill.MailchimpTemplates")

class TemplateSchemasVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        for line in get_settings().template_schemas:
            label, path = line.split('|')
            terms.append(SimpleTerm(
                value=path,
                token=str(path),
                title=label,
            ))
        return SimpleVocabulary(terms)
grok.global_utility(TemplateSchemasVocabulary, name=u"collective.chimpdrill.TemplateSchemas")


class ITemplate(form.Schema, namedfile.interfaces.IImageScaleTraversable):
    """
    A representation of a Mailchimp Template loaded into Mandrill
    """

    mailchimp_template = schema.Choice(
        title=u"Mailchimp Template",
        description=u"",
        source=u"collective.chimpdrill.MailchimpTemplates",
        required=False,
    )

    upload_title = schema.TextLine(
        title=u"Uploaded Template Name",
        description=u"If you are uploading a template rather than linking to an existing one, you must provide a name for the new template",
        required=False,
    )

    template_code = schema.Text(
        title=u"Manual Upload - Template HTML",
        description=u"Cut and paste custom template html here to have the template created in Mailchimp and sync'ed with Mandrill for use",
        required=False,
    )

    template_schema = schema.Choice(
        title=u"Template Data Schema",
        description=u"Select the schema of data which should be used to collect values to merge into the template.  The schemas in this list are configured in the Template Schemas section of the Mailchimp/Mandrill Settings control panel",
        default=u"collective.chimpdrill.schema.IBasic",
        source=u"collective.chimpdrill.TemplateSchemas",
        required=True
    )

    description = schema.Text(
        title=u"Description",
        description=u"A Description of the Template",
        required=False,
    )

    email_subject = schema.TextLine(
        title=u"Email Subject",
        description=u"The subject line for emails sent through this template",
    )
    from_email = schema.TextLine(
        title=u"Sender Email",
        description=u"The email of the sender of the email",
    )
    from_name = schema.TextLine(
        title=u"Sender Name",
        description=u"The name of the sender of the email",
    )

    form.omitted('mandrill_template')
    mandrill_template = schema.TextLine(
        title=u"Mandrill Template",
        description=u"The Mandrill Template being synced",
        required=False,
    )

    form.omitted('last_sync')
    last_sync = schema.Datetime(
        title=u"Last Sync Date",
        description=u"The date the Mailchimp template was last synced with the Mandrill template.",
        required=False,
    )

    form.omitted('title')
    title = schema.TextLine(
        title=u"Title",
        description=u"The template title.  Note that if you are selecting a Mailchimp Template, the Title will be set automatically.",
        required=False,
    )

    @invariant
    def selectOrUploadInvariant(data):
        has_upload_values = data.upload_title is not None and data.template_code is not None
        if data.mailchimp_template is None and not has_upload_values:
            raise Invalid(u"You must either select a Mailchimp Template or provide a name and template code to create a new template")

alsoProvides(ITemplate, IContentType)

class Template(dexterity.Item):
    grok.implements(ITemplate)

    def get_title(self):
        title = None
        if self.mailchimp_template:
            title = self.mailchimp_template_name
            if title:
                return title

        if self.upload_title:
            title = self.upload_title
            
            # If there is no Mailchimp template yet, this is a new upload
            # so we need to upload the template to Mailchimp
            self.create_mailchimp_template(title, self.template_code)

        return title

    title = property(get_title, lambda *args, **kwargs: None)

    @property
    def c_mailchimp(self):
        #if not hasattr(self, '_c_mailchimp'):
        #    self._c_mailchimp = getUtility(IMailsnakeConnection).get_mailchimp()
        #return self._c_mailchimp
        return getUtility(IMailsnakeConnection).get_mailchimp()

    @property
    def c_mandrill(self):
        #if not hasattr(self, '_c_mailchimp'):
        #    self.c_mandrill = getUtility(IMailsnakeConnection).get_mandrill()
        #return self.c_mandrill
        return getUtility(IMailsnakeConnection).get_mandrill()

    @property
    def mailchimp_template_name(self):
        if not self.mailchimp_template:
            return

        if not hasattr(self, '_mailchimp_template_name'):
            templates = self.c_mailchimp.templates()
            template_name = None
            for template in templates:
                if template.get('tid') == self.mailchimp_template:
                    template_name = template.get('name')
                    break
            self._mailchimp_template_name = template_name
        return self._mailchimp_template_name

    @property
    def mailchimp_template_info(self):
        if not self.mailchimp_template:
            return

        if not hasattr(self, '_mailchimp_template_info'):
            self._mailchimp_template_info = self.c_mailchimp.templateInfo(tid = self.mailchimp_template)
        return self._mailchimp_template_info

    @property
    def mandrill_template_info(self):
        if not self.mandrill_template:
            return
        
        if not hasattr(self, '_mandrill_template_info'):
            self._mandrill_template_info = self.c_mandrill.templates.info(name=self.mandrill_template)
        return self._mandrill_template_info

    @property
    def updated_since_sync(self):
        pass

    def sync_to_mandrill(self):
        mc_info = self.mailchimp_template_info

        md_name = 'chimpdrill-%s' % self.mailchimp_template
        md_code = '%s' % self.process_mailchimp_source(mc_info['source'])

        info = {
            'name': md_name,
            'code': md_code,
            'publish': True,
        }

        if self.mandrill_template:
            resp = self.c_mandrill.templates.update(**info)
        else:
            resp = self.c_mandrill.templates.add(**info)

        if not resp.has_key('status'):
            self.mandrill_template = resp['name']
            self.last_sync = datetime.now()
            return True

        if hasattr(self, '_mandrill_template_info'):
            del(self._mandrill_template_info)

        return False

    def process_mailchimp_source(self, html):
        return self.c_mailchimp.inlineCss(html=html)

    def create_mailchimp_template(self, name, html):
        template_id = self.c_mailchimp.templateAdd(name=name, html=html)
        self.mailchimp_template = template_id

    def send(self, email, merge_vars, blocks):
        return self.c_mandrill.messages.send_template(**{
            'template_name': self.mandrill_template,
            'template_content': blocks,
            'message': {
                'subject': self.email_subject,
                'from_email': self.from_email,
                'from_name': self.from_name,
                'to': [
                    {'email': email},
                ],
                'global_merge_vars': merge_vars,
            },
        })

@grok.subscribe(ITemplate, IObjectAddedEvent)
def createMandrillTemplate(template, event):
    template.sync_to_mandrill()

class TemplateView(grok.View):
    grok.context(ITemplate)
    grok.require('zope2.View')

    grok.name('view')
    grok.template('view')

class TemplatePreviewView(grok.View):
    grok.context(ITemplate)
    grok.require('zope2.View')
    grok.name('preview')
    
    def render(self):
        mc_info = self.context.mailchimp_template_info
        if mc_info:
            return mc_info.get('preview')

class TemplateSendView(form.SchemaForm):
    grok.context(ITemplate)
    grok.require('zope2.View')
    grok.name('send_email')
    
    ignoreContext = True
    
    @property
    def schema(self):
        path = self.context.template_schema
        return resolve(path)

    @button.buttonAndHandler(u"Send")
    def handleOk(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        merge_vars = []
        blocks = []

        for key in data.keys():
            value = data[key]
            if hasattr(value, 'output'):
                value = value.output

            if key.startswith('block_'):
                block = key.replace('block_','')
                blocks.append({'name': block, 'content': value})
                continue

            value = data[key]
            merge_vars.append({'name': key, 'content': data[key]})

        self.context.send(data['send_to'], merge_vars, blocks)

        return self.request.response.redirect(self.context.absolute_url())
