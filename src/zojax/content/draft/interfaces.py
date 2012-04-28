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
from zope import schema, interface
from zope.i18nmessageid import MessageFactory
from zope.component.interfaces import IObjectEvent

from z3c.form.interfaces import IWidget

from zojax.content.type.interfaces import IContentType, IDraftedContent

_ = MessageFactory('zojax.content.draft')


class DraftException(Exception):
    """Base draft exception."""


class IDraftContent(interface.Interface):
    """Draft content item."""

    content = interface.Attribute('Managed content')

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'May contain spaces and special characters.'),
        required = True,
        missing_value = u'')

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'A short summary of the content item.'),
        required = False,
        missing_value = u'')

    published = interface.Attribute('Published state')

    def getLocation():
        """Return location."""

    def submit():
        """Submit draft."""

    def publish():
        """Publish draft."""

    def retract():
        """Retract draft."""

    def reject(comment):
        """Reject draft."""

    def isSubmitable():
        """Is draft content submitable. """

    def isPublishable():
        """Is draft content publishable. """


class ISubmittedDraftContent(interface.Interface):
    """Marker interface for submitted draft."""


class IDraftLocation(interface.Interface):
    """Draft location."""

    location = schema.Int(
        title = _(u'Content location'),
        description = _('Please select location where you whould like to create content.'),
        required = True,
        default = 0)

    shortname = schema.TextLine(
        title = _(u'Short Name'),
        description = _(u'Should not contain spaces, underscores or mixed case. '
                        "Short Name is part of the item's web address."),
        required = True,
        missing_value = u'')


class IDraftContentType(IContentType):
    """Draf ContentType wrapper"""

    submit = interface.Attribute('Submit permission')
    publish = interface.Attribute('Publish permission')
    retractperm = interface.Attribute('Retract permission')
    contenttype = interface.Attribute('Original content type')
    destination = interface.Attribute('Destination content type')
    saveable = interface.Attribute('Saveable draft')
    retractable = interface.Attribute('Retractable content')

    def retract(principal=None):
        """ retract bound content """

    def isRetractable(principal=None):
        """ is bound content retractable """


class IDraftContainer(interface.Interface):
    """Draft container."""

    allowedTypes = interface.Attribute('List of allowed types')


class IDraftedContentType(interface.Interface):
    """ Marker interface for drafted content type """


class IDraftEvent(IObjectEvent):
    """ content draft event """

    draft = interface.Attribute('Draft object')


class IDraftLocationChangedEvent(IDraftEvent):
    """ content draft location changed """

    location = interface.Attribute('Location object')


class IDraftStatusEvent(IDraftEvent):
    """ draft status changed event """

    comment = interface.Attribute('Comment')


class IDraftSubmittedEvent(IDraftStatusEvent):
    """ draft submitted """


class IDraftRejectedEvent(IDraftStatusEvent):
    """ draft rejected """


class IDraftRetractedEvent(IDraftStatusEvent):
    """ draft retracted """


class IDraftPublishedEvent(IDraftStatusEvent):
    """ draft published """


class IObjectRetractedEvent(IDraftEvent):
    """ content retracted event """


class ILocationWidget(IWidget):
    """ location widget """


class ILocationField(interface.Interface):
    """ location id field """
