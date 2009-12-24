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
from zope import interface
from zope.location import LocationProxy
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from zojax.wizard.step import WizardStep
from zojax.layout.interfaces import IPagelet
from zojax.content.type.interfaces import IContentPreview
from zojax.content.forms.interfaces import IContentViewStep


class ContentPreviewStep(WizardStep):
    interface.implements(IContentViewStep)

    def update(self):
        super(ContentPreviewStep, self).update()

        draft = self.wizard.context
        content = LocationProxy(draft.content, draft, name='content')

        view = queryMultiAdapter((content, self.request), IContentPreview)
        view.update()
        self.view = view

        self.activity = queryMultiAdapter(
            (draft.content, self.request, self), IContentProvider,
            name='content.activity')

        if self.activity is not None:
            self.activity.update()
            if not self.activity:
                self.activity = None
