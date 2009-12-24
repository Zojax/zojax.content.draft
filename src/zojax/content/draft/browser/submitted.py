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
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent

from zojax.layoutform import button
from zojax.content.forms.content import ContentStep
from zojax.content.type.interfaces import IContentType
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.content.draft.interfaces import _, DraftException

import interfaces
from wizard import DraftWizard
from location import ContentLocationStep


class SubmittedDraftWizard(DraftWizard):
    interface.implements(interfaces.ISubmittedDraftWizard)

    prefix = 'draft.submitted.'
    handlers = DraftWizard.handlers.copy()
    buttons = button.Buttons(interfaces.ISubmittedDraftWizardButtons)

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
        except DraftException, err:
            IStatusMessage(request).add(str(err), 'error')
            return

        draft = removeAllProxies(draft)
        del draft.__parent__[draft.__name__]

        IStatusMessage(self.request).add(
            _(u'${type_title} has been published.',
              mapping={'type_title': IContentType(content).title}))

        self.redirect('../../')

    @button.handler(interfaces.IRejectAction)
    def handleReject(self, action):
        comment = self.request.get('form.action.comment', u'')
        self.draft.reject(comment)

        event.notify(ObjectModifiedEvent(self.draft))

        IStatusMessage(self.request).add(
            _(u'${type_title} has been rejected.',
              mapping={'type_title': IContentType(self.draft.content).title}))

        self.redirect('../../')

    @button.handler(interfaces.IRetractAction)
    def handleRetract(self, action):
        self.draft.retract()
        self.redirect('../')
        event.notify(ObjectModifiedEvent(self.draft))
        IStatusMessage(self.request).add(
            _(u'Your ${type_title} has been retracted.',
              mapping={'type_title': IContentType(self.draft.content).title}))

    @button.handler(interfaces.IRemoveAction)
    def handleRemove(self, action):
        draft = removeAllProxies(self.draft)
        container = draft.__parent__

        del container[draft.__name__]

        IStatusMessage(self.request).add(
            _(u'${type_title} draft has been removed.',
              mapping={'type_title': IContentType(draft.content).title}))

        self.redirect('../../../')


class ContentStep(ContentStep):

    def isAvailable(self):
        if self.wizard.draft.isPublishable():
            return super(ContentStep, self).isAvailable()

        return False


class ContentLocationStep(ContentLocationStep):

    def isAvailable(self):
        return self.wizard.draft.isPublishable()
