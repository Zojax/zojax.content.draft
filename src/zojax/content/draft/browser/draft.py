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
from zope import interface, event
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL

from zojax.layoutform import button
from zojax.content.type.interfaces import IContentType, IContentViewView
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.draft.interfaces import _, DraftException

import interfaces
from wizard import DraftWizard


class EditDraftWizard(DraftWizard):
    interface.implements(interfaces.IEditDraftWizard)

    prefix = 'draft.edit.'
    handlers = DraftWizard.handlers.copy()
    buttons = button.Buttons(interfaces.IEditDraftWizardButtons)

    def hasViewStep(self):
        return False

    @button.handler(interfaces.IPublishAction)
    def handlePublish(self, action):
        errorSteps = []
        for step in self.steps:
            if not step.isComplete():
                errorSteps.append(step)

        if errorSteps:
            IStatusMessage(self.request).add(errorSteps, 'wizardError')
            return

        draft = self.draft
        request = self.request
        try:
            content = draft.publish()
            IStatusMessage(self.request).add(
                _(u'Your ${type_title} has been published.',
                  mapping={'type_title': IContentType(content).title}))

            view = queryMultiAdapter((content, request), IContentViewView)
            if view is not None:
                self.redirect('%s/%s'%(absoluteURL(content,request), view.name))
            else:
                self.redirect('%s/'%absoluteURL(content, request))

            del draft.__parent__[draft.__name__]
        except DraftException, err:
            IStatusMessage(request).add(str(err), 'error')
            self.wizard.setCurrentStep('content')
            self.redirect('%s/index.html'%absoluteURL(draft, request))

    @button.handler(interfaces.ISubmitAction)
    def handleSubmit(self, action):
        errorSteps = []
        for step in self.steps:
            if not step.isComplete():
                errorSteps.append(step)

        if errorSteps:
            IStatusMessage(self.request).add(errorSteps, 'wizardError')
            return

        self.draft.submit()
        IStatusMessage(self.request).add(
            _(u'Your ${type_title} draft has been submitted.',
              mapping={'type_title': IContentType(self.draft.content).title}))

        self.redirect('../')

    @button.handler(interfaces.IRemoveAction)
    def handleRemove(self, action):
        container = self.draft.__parent__

        del container[self.draft.__name__]

        IStatusMessage(self.request).add(
            _(u'${type_title} draft has been removed.',
              mapping={'type_title': IContentType(self.draft.content).title}))

        self.redirect('../../../')
