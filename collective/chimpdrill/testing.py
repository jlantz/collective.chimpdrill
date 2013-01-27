from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import ploneSite
from plone.app.testing import quickInstallProduct
import transaction


class CollectiveChimpdrillLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.chimpdrill
        self.loadZCML(package=collective.chimpdrill)

#        z2.installProduct(app, 'collective.chimpdrill')

    def setUpPloneSite(self, portal):
        quickInstallProduct(portal, 'collective.chimpdrill')
        #self.applyProfile(portal, 'collective.chimpdrill:default')
        transaction.commit()

#    def tearDownZope(self, app):
#        z2.uninstallProduct(app, 'collective.chimpdrill')


FIXTURE = CollectiveChimpdrillLayer()
INTEGRATION_TESTING = IntegrationTesting(bases=(FIXTURE,), name='collective.chimpdrill:Integration')
FUNCTIONAL_TESTING = FunctionalTesting(bases=(FIXTURE,), name='collective.chimpdrill:Functional')
