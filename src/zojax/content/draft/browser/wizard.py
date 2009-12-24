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
from zope.proxy import removeAllProxies
from zope.location import LocationProxy
from zope.component import getAdapters
from zope.security.interfaces import Unauthorized

from zojax.wizard import Wizard, WizardWithTabs
from zojax.wizard.interfaces import IWizardStep
from zojax.layoutform.interfaces import IPageletSubform
from zojax.content.type.interfaces import IContentType

from interfaces import _


class ContentLocationProxy(LocationProxy):

    def __hash__(self):
        return id(self)


class BaseDraftWizard(Wizard):

    label = _(u'Draft:')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.draft = context

    @property
    def title(self):
        return self.ct.title

    @property
    def description(self):
        return self.ct.description

    def isPublishable(self):
        return self.draft.isPublishable()

    def isSubmitable(self):
        draft = self.draft
        return not draft.isPublishable() and draft.isSubmitable()

    def update(self):
        content = self.getContent()
        if content is not None:
            self.ct = IContentType(content)
            super(BaseDraftWizard, self).update()
        else:
            raise Unauthorized(self)

    def _loadSteps(self):
        content = removeAllProxies(self.getContent())
        content = ContentLocationProxy(
            content, self.__parent__.__parent__, self.__parent__.__name__)

        return [form for name, form in getAdapters(
                (content, self, self.request), IWizardStep)]

    def getContent(self):
        draft = self.draft
        if draft is not None:
            return self.draft.content
        return None


class DraftWizard(BaseDraftWizard, WizardWithTabs):
    pass
