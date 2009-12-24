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
from persistent.interfaces import IPersistent

from zope import interface, component
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.keyreference.interfaces import NotYet, IKeyReference
from zope.keyreference.persistent import KeyReferenceToPersistent
from zope.app.intid.interfaces import \
    IIntIds, IIntIdAddedEvent, IIntIdRemovedEvent
from zope.app.intid import addIntIdSubscriber, removeIntIdSubscriber

from zojax.content.type.interfaces import IContent
from zojax.content.draft.interfaces import IDraftContent


@component.adapter(IContent)
@interface.implementer(IKeyReference)
def getKeyReference(object):
    if not IPersistent.providedBy(object):
        return

    try:
        return KeyReferenceToPersistent(object)
    except NotYet:
        while not IDraftContent.providedBy(object):
            object = getattr(object, '__parent__', None)
            if object is None:
                raise


@component.adapter(IDraftContent, IIntIdAddedEvent)
def draftAdded(object, event):
    if getUtility(IIntIds).queryId(removeAllProxies(object.content)) is None:
        addIntIdSubscriber(object.content, event)


@component.adapter(IDraftContent, IIntIdRemovedEvent)
def draftRemoved(object, event):
    if not object.published:
        removeIntIdSubscriber(object.content, event)
