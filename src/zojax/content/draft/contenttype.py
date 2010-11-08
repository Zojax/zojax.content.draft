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
from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.component import getUtility, getAdapters, queryMultiAdapter
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.interfaces import Unauthorized
from zope.app.container.interfaces import INameChooser

from zojax.catalog.utils import getRequest
from zojax.content.type.contenttype import ContentType
from zojax.content.type.interfaces import IContentType, IBoundContentType

from zojax.security.utils import getPrincipal, checkPermissionForPrincipal

from draft import DraftContent
from events import ObjectRetractedEvent
from interfaces import DraftException
from interfaces import IDraftContent, IDraftContainer, IDraftContentType


class DraftContentType(ContentType):
    interface.implements(IDraftContentType)

    saveable = True

    def __init__(self, ct, dest,
                 submit, publish, retractperm, saveable, retractable,
                 klass=DraftContent):
        super(DraftContentType, self).__init__(
            ct.name, IDraftContent, DraftContent,
            ct.title, ct.description, 'zope.View')

        self.contenttype = ct
        self.destination = dest
        self.submit = submit
        self.publish = publish
        self.retractperm = retractperm
        self.saveable = saveable
        self.retractable = retractable
        self.klass = klass

    def listContainedTypes(self, checkAvailability=True):
        return ()

    def create(self, **data):
        content = self.contenttype.create(**data)

        draft = self.klass(content)

        for name in ('location', 'shortname'):
            if name in data:
                setattr(draft, name, data[name])

        draft.data = data

        event.notify(ObjectCreatedEvent(draft))

        del draft.data

        return draft

    def add(self, content, context):
        if not IDraftContainer.providedBy(context):
            raise Unauthorized("Can't create '%s' instance"%self.name)

        content = removeAllProxies(content)

        name = INameChooser(context).chooseName('', content)

        context[name] = content
        return context[name]

    def isAvailable(self):
        return IDraftContainer.providedBy(self.context)

    def isRetractable(self, principal=None):
        if not IBoundContentType.providedBy(self):
            return False

        if not self.retractable or not self.retractperm:
            return False

        if principal is None:
            principal = getPrincipal()

        return checkPermissionForPrincipal(
            principal, self.retractperm, self.context)

    def retract(self, principal=None):
        if principal is None:
            principal = getPrincipal()

        if not self.isRetractable(principal):
            raise DraftException('Cannot retract content.')

        container = queryMultiAdapter((principal, self), IDraftContainer)
        if container is None:
            raise DraftException('Cannot find draft container.')

        content = self.context

        origName = content.__name__
        oldContainer = content.__parent__

        newName = INameChooser(container).chooseName(u'', content)

        container[newName] = removeAllProxies(content)
        del removeAllProxies(oldContainer)[origName]

        draft = container[newName]
        event.notify(ObjectRetractedEvent(content, draft))

        return draft


@component.adapter(IDraftContent)
@interface.implementer(IContentType)
def draftContentType(draftContent):
    ct = IContentType(draftContent.content, None)
    if ct is not None:
        return getUtility(IDraftContentType, ct.name)


class DraftContainerType(ContentType):

    def listContainedTypes(self, checkAvailability=True):
        context = self.context

        if context.allowedTypes is None:
            for ct in super(DraftContainerType, self).listContainedTypes():
                yield ct
        else:
            for ct in context.allowedTypes:
                bct = getUtility(IContentType, ct).__bind__(context)
                if not checkAvailability:
                    yield bct

                elif bct.isAvailable():
                    yield bct


class DraftedContentType(ContentType):

    def isAvailable(self):
        if super(DraftedContentType, self).isAvailable():
            if self.permission is not None:
                principal = getattr(getRequest(), 'principal', None)
                df = queryMultiAdapter(
                    (principal, getUtility(IDraftContentType, self.name)),
                    IDraftContainer)
                if df is not None:
                    return True
            else:
                return True

        return False
