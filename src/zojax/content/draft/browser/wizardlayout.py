##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.security.interfaces import Unauthorized
from z3c.breadcrumb.interfaces import IBreadcrumb
from zojax.wizard.browser.wizardlayout import WizardWithTabsLayout

from interfaces import ILocationContainer


class WizardLayout(WizardWithTabsLayout):

    locationUrl = None
    locationTitle = None
    containerUrl = None
    containerTitle = None

    def update(self):
        draft = self.context.draft
        if draft is None:
            raise Unauthorized(self)

        location = self.context.draft.getLocation()
        if location is not None:
            self.locationUrl = '%s/'%absoluteURL(location, self.request)
            self.locationTitle = getMultiAdapter(
                (location, self.request), IBreadcrumb).name

            container = location.__parent__
            while not ILocationContainer.providedBy(container):
                container = getattr(container, '__parent__', None)
                if container is None:
                    break

            if container is not None:
                self.containerUrl = '%s/'%absoluteURL(container, self.request)
                self.containerTitle = getMultiAdapter(
                    (container, self.request), IBreadcrumb).name

        super(WizardLayout, self).update()
