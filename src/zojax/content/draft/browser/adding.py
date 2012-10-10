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
from zope.security import checkPermission
from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL
from zope.security.interfaces import Unauthorized
from zope.copypastemove.interfaces import IObjectMover
from zope.app.container.interfaces import INameChooser
from zope.security.management import endInteraction, newInteraction

from zojax.layoutform import button
from zojax.content.browser.adding import Adding
from zojax.content.type.interfaces import IContentType, IContentViewView
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.draft.interfaces import _, IDraftContainer, IDraftContentType
from zojax.content.draft.interfaces import DraftException

import interfaces
from wizard import DraftWizard
from interfaces import IContentLocationStep


class BaseAddDraftWizard(DraftWizard):

    label = _('Adding content:')
    handlers = DraftWizard.handlers.copy()
    buttons = button.Buttons(interfaces.IAddDraftWizardButtons)
    formCancelMessage = _(u'Content creation has been canceled.')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def isSaveable(self):
        draft = self.draft
        ct = IContentType(draft)

        if not ct.saveable:
            return False
        return True

    def isPublishable(self):
        return self.draft.isPublishable() and \
            not IContentLocationStep.providedBy(self.step)

    def isSubmitable(self):
        draft = self.draft
        ct = IContentType(draft)

        if not ct.saveable:
            return False

        if not draft.isPublishable() and checkPermission(ct.submit, self):
            return not IContentLocationStep.providedBy(self.step)

        return False

    def isLocationStep(self):
        return IContentLocationStep.providedBy(self.step)

    @button.handler(interfaces.ISaveDraftAction)
    def handleSaveContinueDraft(self, action):
        draft = self.draft
        ct = IContentType(draft)

        if not ct.saveable:
            raise DraftException("Saving draft is not allowed.")

        errorSteps = []
        for step in self.steps:
            if not step.isComplete():
                errorSteps.append(step)

        if errorSteps:
            IStatusMessage(self.request).add(errorSteps, 'wizardError')
            return

        draft = removeAllProxies(self.draft)
        draftContainer = self.getDraftContainer()

        name = INameChooser(draftContainer).chooseName(u'', draft)
        name = IObjectMover(draft).moveTo(draftContainer, name)

        draft = draftContainer[name]

        self.clear()
        self.redirect('%s/'%absoluteURL(draft, self.request))
        IStatusMessage(self.request).add(
            _(u'Your ${type_title} draft has been added.',
              mapping={'type_title': IContentType(draft.content).title}))

    @button.handler(interfaces.ISubmitAction)
    def handleSubmit(self, action):
        errorSteps = []
        for step in self.steps:
            if not step.isComplete():
                errorSteps.append(step)

        if errorSteps:
            IStatusMessage(self.request).add(errorSteps, 'wizardError')
            return

        draft = removeAllProxies(self.draft)
        draftContainer = self.getDraftContainer()

        name = INameChooser(draftContainer).chooseName(u'', draft)
        name = IObjectMover(draft).moveTo(draftContainer, name)

        draft = draftContainer[name]
        try:
            draft.submit()
        except DraftException, err:
            IStatusMessage(self.request).add(str(err), 'error')
            self.redirect('%s/index.html'%absoluteURL(draft, self.request))
            return

        self.clear()
        self.redirect('%s/'%absoluteURL(draft, self.request))
        IStatusMessage(self.request).add(
            _(u'Your ${type_title} draft has been submitted.',
              mapping={'type_title': IContentType(draft.content).title}))

    @button.handler(interfaces.IPublishAction)
    def handlePublish(self, action):
        errorSteps = []
        for step in self.steps:
            if not step.isComplete():
                errorSteps.append(step)

        if errorSteps:
            IStatusMessage(self.request).add(errorSteps, 'wizardError')
            return

        endInteraction()
        self.request.interaction = None
        newInteraction(self.request)

        draft = self.draft
        try:
            content = draft.publish()
        except DraftException, err:
            IStatusMessage(self.request).add(str(err), 'error')
            self.redirect('%s/index.html'%absoluteURL(draft, self.request))
            return

        self.clear()

        view = queryMultiAdapter((content, self.request), IContentViewView)
        if self.request.response.getStatus() in (302, 303):
            self.redirect(self.request.response.getHeader('location'))
        else:
            if view is not None:
                self.redirect('%s/%s'%(absoluteURL(content,self.request),view.name))
            else:
                self.redirect('%s/'%absoluteURL(content, self.request))

        IStatusMessage(self.request).add(
            _(u'Your ${type_title} has been published.',
              mapping={'type_title': IContentType(content).title}))

    def clear(self):
        container = self.getDraftContainer()
        if 'draft' in container:
            del container['draft']

    def getDraftContainer(self):
        return self.context.__parent__.__parent__

    def nextURL(self):
        return '%s/'%absoluteURL(
            self.context.__parent__.__parent__, self.request)

    def cancelURL(self):
        return '%s/'%absoluteURL(
            self.context.__parent__.__parent__, self.request)


class AddDraftWizard(BaseAddDraftWizard):
    interface.implements(interfaces.IAddDraftWizard)

    @property
    def draft(self):
        container = self.getDraftContainer()

        draft = None
        if 'draft' in container:
            draft = container['draft']
            if IContentType(draft, None) is None:
                draft = None
                del container['draft']

            if draft is not None:
                if IContentType(draft).name != self.context.__name__:
                    draft = None
                    del container['draft']

        if draft is None:
            dct = getUtility(IDraftContentType, self.context.__name__)
            draft = dct.create()
            container['draft'] = removeAllProxies(draft)
        return container['draft']


class AddContentWizard(BaseAddDraftWizard):
    interface.implements(interfaces.IAddContentWizard)

    def getDraftContainer(self):
        dct = getUtility(IDraftContentType, self.context.__name__)
        return queryMultiAdapter(
            (self.request.principal, dct), IDraftContainer)

    @property
    def draft(self):
        container = self.getDraftContainer()
        if container is None:
            return None

        draft = None
        if 'draft' in container:
            draft = container['draft']
            if IContentType(draft, None) is None:
                draft = None
                del container['draft']

            if draft is not None:
                if IContentType(draft).name != self.context.__name__:
                    draft = None
                    del container['draft']

        if draft is None:
            dct = getUtility(IDraftContentType, self.context.__name__)
            draft = dct.create()
            draft.location = getUtility(IIntIds).getId(
                removeAllProxies(self.context.context))
            container['draft'] = removeAllProxies(draft)
        return container['draft']

    def update(self):
        container = self.getDraftContainer()

        draft = None
        if 'draft' in container:
            draft = container['draft']
            if IContentType(draft, None) is None:
                draft = None
                del container['draft']

        if draft is not None:
            draft.location = getUtility(IIntIds).getId(
                removeAllProxies(self.context.context))

        super(AddContentWizard, self).update()


class Adding(Adding):

    def getContentType(self, name):
        ctype = queryUtility(IDraftContentType, name)
        if ctype is not None:
            context = self.context
            ctype = ctype.__bind__(context)

            ctype.__name__ = name
            ctype.__parent__ = self
            return ctype
