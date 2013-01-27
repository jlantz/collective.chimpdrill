import transaction
import unittest2 as unittest
from zope.component import getSiteManager
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from plone.dexterity.utils import createContentInContainer
from collective.chimpdrill.utils import IMailsnakeConnection
from collective.chimpdrill.testing import FUNCTIONAL_TESTING
from collective.chimpdrill.tests.dummy_mailsnake import DummyMailsnakeConnectionUtil
from collective.chimpdrill.tests.dummy_mailsnake import MC_TEMPLATE_HTML, MC_TEMPLATE_INLINED_HTML

class TemplateFunctionalTest(unittest.TestCase):
    # The layer's setup will run once before all of these tests run,
    # and its teardown will run once after all these tests run.
    layer = FUNCTIONAL_TESTING

    # setUp is run once before *each* of these tests.
    # This stuff can be moved to the layer's setupPloneSite if you want
    # it for all tests using the layer, not just this test class.
    def setUp(self):
        self.layer['portal'].validate_email = False
        portal = self.layer['portal']

        # replace MailsnakeConnection utility with dummy harness
        sm = getSiteManager(portal)
        sm.unregisterUtility(provided=IMailsnakeConnection)
        sm.registerUtility(DummyMailsnakeConnectionUtil(), IMailsnakeConnection)

        # Create an email repository to use for adding content
        repository = createContentInContainer(portal,
            'collective.chimpdrill.repository', checkConstraints = False,
            title=u"Test Repository")

        transaction.commit()
    
    

    # tearDown is run once after *each* of these tests.
    # We're using it to remove objects that we recorded as having been
    # added to Salesforce.
    def tearDown(self):
        pass

    def test_create_template_from_existing(self):
        portal = self.layer['portal']

        # Now as a normal user, go through the steps in the browser
        browser = Browser(portal)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open('http://nohost/plone/test-repository/++add++collective.chimpdrill.template')

        browser.getControl(name='form.widgets.mailchimp_template:list').value = [u"1",]
        browser.getControl(name='form.widgets.description').value = u"Description Test 1"
        browser.getControl(name='form.widgets.email_subject').value = u"Test Template 1 Subject"
        browser.getControl(name='form.widgets.from_email').value = u"jack@example.com"
        browser.getControl(name='form.widgets.from_name').value = u"Jack Black"
        browser.getControl(name='form.buttons.save').click()

        self.assertEqual('http://nohost/plone/test-repository/test-template-1/view', browser.url)
        self.assertTrue('Test Template 1' in browser.contents)
        self.assertTrue('Description Test 1' in browser.contents)

        template = portal.unrestrictedTraverse('test-repository/test-template-1')
        self.assertEqual(template.mandrill_template, 'mailchimp-1')
        self.assertEqual(template.mandrill_template_info['name'], 'mailchimp-1')
        self.assertEqual(template.mailchimp_template_info['name'], 'Test Template 1')
        
    def test_create_new_template(self):
        portal = self.layer['portal']
    
        browser = Browser(portal)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open('http://nohost/plone/test-repository/++add++collective.chimpdrill.template')
    
        browser.getControl(name='form.widgets.upload_title').value = "Test Template 3"
        browser.getControl(name='form.widgets.template_code').value = MC_TEMPLATE_HTML
        browser.getControl(name='form.widgets.description').value = u"Test Upload Description"
        browser.getControl(name='form.widgets.email_subject').value = u"Test Template 3 Subject"
        browser.getControl(name='form.widgets.from_email').value = u"jack@example.com"
        browser.getControl(name='form.widgets.from_name').value = u"Jack Black"
        browser.getControl(name='form.buttons.save').click()
    
        self.assertEqual("http://nohost/plone/test-repository/test-template-3/view", browser.url)
        self.assertTrue('Test Template 3' in browser.contents)
        self.assertTrue('Test Upload Description' in browser.contents)

        template = portal.unrestrictedTraverse('test-repository/test-template-3')
        self.assertEqual(template.mandrill_template, 'mailchimp-3')
        self.assertEqual(template.mandrill_template_info['name'], 'mailchimp-3')
        self.assertEqual(template.mailchimp_template_info['name'], 'Test Template 3')

        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open('http://nohost/plone/test-repository/test-template-3/preview')

        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        browser.open('http://nohost/plone/test-repository/test-template-3/send_email')
        browser.getControl(name='form.widgets.send_to')
        
        
        
    def test_select_or_upload_invariant(self):
        portal = self.layer['portal']
    
        browser = Browser(portal)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

        browser.open('http://nohost/plone/test-repository/++add++collective.chimpdrill.template')

        # No values filled in
        browser.getControl(name='form.buttons.save').click()
        self.assertEqual("http://nohost/plone/test-repository/++add++collective.chimpdrill.template", browser.url)
        self.assertTrue('You must either select a Mailchimp Template or provide a name and template code to create a new template' in browser.contents)
       
        # No template, title, no template code, should fail 
        browser.getControl(name='form.widgets.upload_title').value = "Test Template 3"
        browser.getControl(name='form.widgets.description').value = u"Test Upload Description"
        browser.getControl(name='form.buttons.save').click()
        self.assertEqual("http://nohost/plone/test-repository/++add++collective.chimpdrill.template", browser.url)
        self.assertTrue('You must either select a Mailchimp Template or provide a name and template code to create a new template' in browser.contents)

        # No template, no title, template code, should fail 
        browser.getControl(name='form.widgets.upload_title').value = ""
        browser.getControl(name='form.widgets.template_code').value = MC_TEMPLATE_HTML
        browser.getControl(name='form.widgets.description').value = u"Test Upload Description"
        browser.getControl(name='form.buttons.save').click()
        self.assertEqual("http://nohost/plone/test-repository/++add++collective.chimpdrill.template", browser.url)
        self.assertTrue('You must either select a Mailchimp Template or provide a name and template code to create a new template' in browser.contents)
