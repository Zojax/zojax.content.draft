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
from zope.component import getUtility, getUtilitiesFor
from zope.app.intid.interfaces import IIntIds
from zope.exceptions.interfaces import DuplicationError
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.app.container.contained import ObjectAddedEvent, ObjectMovedEvent
from zope.app.container.contained import notifyContainerModified
from zope.app.container.constraints import IItemTypePrecondition

from zojax.content.type.contenttype import ContentType
from zojax.content.type.container import ContentContainer
from zojax.content.type.interfaces import IContentType, IBoundContentType

from interfaces import IDraftContent, IDraftContainer, IDraftContentType


class DraftContainer(ContentContainer):
    interface.implements(IDraftContainer)

    allowedTypes = None

    def __setitem__(self, key, object):
        if IDraftContent.providedBy(object):
            super(DraftContainer, self).__setitem__(key, object)
        else:
            setitem(self, self._SampleContainer__data.__setitem__, key, object)


def setitem(container, setitemmf, name, object):
    # Do basic name check:
    if isinstance(name, str):
        try:
            name = unicode(name)
        except UnicodeError:
            raise TypeError("name not unicode or ascii string")
    elif not isinstance(name, unicode):
        raise TypeError("name not unicode or ascii string")

    if not name:
        raise ValueError("empty names are not allowed")

    old = container.get(name)
    if old is object:
        return
    if old is not None:
        raise DuplicationError(name)

    oldparent = object.__parent__
    oldname = object.__name__

    # create and store draft
    dct = getUtility(IDraftContentType, IContentType(object).name)

    draft = dct.klass(removeAllProxies(object))

    draft.__name__ = name
    draft.__parent__ = container

    if oldparent is not None:
        draft.shortname = oldname
        draft.location = getUtility(IIntIds).getId(oldparent)

    event.notify(ObjectCreatedEvent(draft))

    # added draft to container
    setitemmf(name, draft)
    event.notify(ObjectAddedEvent(draft, container, name))

    # notify content and container objects
    if oldparent is not None:
        event.notify(
            ObjectMovedEvent(object,oldparent,oldname,draft,object.__name__))

    event.notify(ObjectModifiedEvent(object))
    notifyContainerModified(container)


class DraftContainerContentType(ContentType):

    def listContainedTypes(self, checkAvailability=True):
        if IBoundContentType.providedBy(self):
            context = self.context

            precondition = IItemTypePrecondition(self, None)

            if precondition is not None:
                contenttypes = []
                for tp in precondition.types:
                    ct = queryUtility(IDraftContentType, tp)
                    if ct is not None and ct not in contenttypes:
                        contenttypes.append(ct)

                for tp in precondition.ifaces:
                    for name, ct in getUtilitiesFor(tp):
                        if ct not in contenttypes:
                            contenttypes.append(ct)

                for contenttype in contenttypes:
                    yield contenttype.__bind__(context)
