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
from zope.component.interfaces import ObjectEvent

import interfaces


class DraftLocationChangedEvent(ObjectEvent):
    interface.implements(interfaces.IDraftLocationChangedEvent)

    def __init__(self, object, draft, location):
        self.object = object
        self.draft = draft
        self.location = location


class DraftStatusEvent(ObjectEvent):

    def __init__(self, object, draft, comment):
        self.object = object
        self.draft = draft
        self.comment = comment


class DraftSubmittedEvent(DraftStatusEvent):
    interface.implements(interfaces.IDraftSubmittedEvent)


class DraftRejectedEvent(DraftStatusEvent):
    interface.implements(interfaces.IDraftRejectedEvent)


class DraftRetractedEvent(DraftStatusEvent):
    interface.implements(interfaces.IDraftRetractedEvent)


class DraftPublishedEvent(DraftStatusEvent):
    interface.implements(interfaces.IDraftPublishedEvent)


class ObjectRetractedEvent(ObjectEvent):
    interface.implements(interfaces.IObjectRetractedEvent)

    def __init__(self, object, draft):
        self.object = object
        self.draft = draft
