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
from rwproperty import getproperty, setproperty

from zope import interface, component, event
from zope.component import getUtility
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized
from zope.schema.fieldproperty import FieldProperty
from zope.app.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IDCPublishing
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zojax.content.type.item import PersistentItem
from zojax.content.type.interfaces import IContentType, IDraftedContent
from zojax.content.type.constraints import checkContentType
from zojax.ownership.interfaces import IOwnership
from zojax.permissionsmap.interfaces import IObjectPermissionsMapsManager

import events
from interfaces import IDraftContent, IDraftLocation
from interfaces import IDraftContentType, ISubmittedDraftContent, DraftException


class BaseDraftContent(PersistentItem):
    interface.implements(IDraftContent)

    shortname = u''
    published = False

    def __init__(self, content):
        self.content = content
        self.content.__name__ = u'content'
        self.content.__parent__ = self
        interface.alsoProvides(content, IDraftedContent)

    @getproperty
    def title(self):
        return self.content.title

    @setproperty
    def title(self, value):
        self.content.title = value

    @getproperty
    def description(self):
        return self.content.description

    @setproperty
    def description(self, value):
        self.content.description = value

    def getLocation(self):
        raise NotImplemented

    def isPublishable(self, location=None):
        if location is None:
            location = self.getLocation()

        if location is None:
            return False

        ct = IContentType(self)

        try:
            checkContentType(location, ct.contenttype)
        except:
            return False

        return checkPermission(ct.publish, location)

    def isSubmitable(self, location=None):
        if location is None:
            location = self.getLocation()

        if location is None:
            return False

        ct = IContentType(self)

        try:
            checkContentType(location, ct.contenttype)
        except:
            return False

        return checkPermission(ct.submit, location)

    def publish(self, comment=u''):
        location = self.getLocation()

        if not self.isPublishable(location):
            raise DraftException("You can't publish content to this location.")

        self.published = True

        contentType = IContentType(self.content).__bind__(location)

        content = self.content
        interface.noLongerProvides(content, IDraftedContent)

        content = contentType.add(content, self.shortname)

        event.notify(ObjectModifiedEvent(content))
        event.notify(events.DraftPublishedEvent(content, self, comment))

        return content

    def submit(self, comment=u''):
        if not self.isSubmitable():
            raise DraftException("You can't submit content to this location.")

        manager = IObjectPermissionsMapsManager(self)
        manager.set(('draft.submitted',))

        interface.alsoProvides(self, ISubmittedDraftContent)
        event.notify(ObjectModifiedEvent(self))
        event.notify(events.DraftSubmittedEvent(self.content, self, comment))

    def reject(self, comment=u''):
        if not ISubmittedDraftContent.providedBy(self):
            raise Unauthorized('reject')

        manager = IObjectPermissionsMapsManager(self)
        manager.set(())
        interface.noLongerProvides(self, ISubmittedDraftContent)
        event.notify(ObjectModifiedEvent(self))
        event.notify(events.DraftRejectedEvent(self.content, self, comment))

    def retract(self, comment=u''):
        if not ISubmittedDraftContent.providedBy(self):
            raise Unauthorized('retract')

        manager = IObjectPermissionsMapsManager(self)
        manager.set(())
        interface.noLongerProvides(self, ISubmittedDraftContent)
        event.notify(ObjectModifiedEvent(self))
        event.notify(events.DraftRetractedEvent(self.content, self, comment))


class DraftContent(BaseDraftContent):
    interface.implements(IDraftLocation)

    location = 0

    def getLocation(self):
        try:
            return getUtility(IIntIds).queryObject(self.location)
        except:
            return None


@component.adapter(IDraftContent)
@interface.implementer(IOwnership)
def draftOwnership(draft):
    return IOwnership(draft.content, None)


@component.adapter(IDraftContent, IObjectModifiedEvent)
def daftModifiedHandler(draft, obevent):
    if not IDraftLocation.providedBy(draft):
        return

    for attr in obevent.descriptions:
        if attr.interface.isOrExtends(IDraftLocation):
            if 'location' in attr.attributes:
                event.notify(events.DraftLocationChangedEvent(
                        draft.content, draft, draft.getLocation()))


@component.adapter(IDraftContent, IObjectRemovedEvent)
def draftRemovedHandler(draft, obevent):
    if IDraftedContent.providedBy(draft.content):
        event.notify(ObjectRemovedEvent(draft.content))
