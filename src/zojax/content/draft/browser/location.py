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

from zojax.layoutform import Fields
from zojax.wizard import WizardStepForm
from zojax.content.draft.interfaces import IDraftLocation
from zojax.content.draft.events import DraftLocationChangedEvent

from locationwidget import LocationFieldWidget
from interfaces import _, ISaveable, IContentLocationStep


class ContentLocationStep(WizardStepForm):
    interface.implements(ISaveable, IContentLocationStep)

    name = u'location'
    title = _(u'Location')

    @property
    def fields(self):
        if not IDraftLocation.providedBy(self.wizard.draft):
            return Fields()

        fields = Fields(IDraftLocation).omit('shortname')
        fields['location'].widgetFactory = LocationFieldWidget

        return fields

    def isComplete(self):
        if super(ContentLocationStep, self).isComplete():
            location = self.getContent().getLocation()
            if location is not None:
                return True

        return False

    def update(self):
        super(ContentLocationStep, self).update()

        widget = self.widgets['location']
        if len(widget.terms) == 1:
            draft = self.wizard.draft
            term = iter(widget.terms).next()

            if draft.location != term.value:
                draft.location = term.value
                event.notify(DraftLocationChangedEvent(
                        draft.content, draft, draft.getLocation()))


    def isAvailable(self):
        if not IDraftLocation.providedBy(self.wizard.draft):
            return False

        widget = self.widgets['location']
        if len(widget.terms) == 1:
            return False

        return super(ContentLocationStep, self).isAvailable()

    def getContent(self):
        return self.wizard.draft

    def applyChanges(self, data):
        changes = super(ContentLocationStep, self).applyChanges(data)
        if changes:
            self.redirect('.')
        return changes
