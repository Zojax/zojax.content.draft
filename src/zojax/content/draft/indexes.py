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
from zope.component import getAdapters, queryUtility
from zope.app.component.interfaces import ISite
from zope.security.proxy import removeSecurityProxy
from zc.catalog.catalogindex import ValueIndex, SetIndex
from zojax.catalog.utils import Indexable, getAccessList
from zojax.catalog.interfaces import ICatalogIndexFactory
from zojax.content.type.interfaces import IContent, IContentType
from zojax.content.draft.interfaces import \
    IDraftContent, IDraftedContent
from zojax.content.draft.interfaces import \
    IDraftContentType, IDraftedContentType, ISubmittedDraftContent


def isDraft():
    return ValueIndex(
        'isDraft', Indexable('zojax.content.draft.indexes.IsDraftChecker'))

def draftContent():
    return ValueIndex(
        'draft', Indexable('zojax.content.draft.indexes.DraftContentChecker'))

def draftStatus():
    return ValueIndex(
        'status', Indexable('zojax.content.draft.indexes.DraftStatusChecker'))

def draftSubmitTo():
    return SetIndex(
        'value', Indexable('zojax.content.draft.indexes.DraftSubmitTo'))

def draftPublishTo():
    return SetIndex(
        'value', Indexable('zojax.content.draft.indexes.DraftPublishTo'))

def draftPublishable():
    return SetIndex(
        'value',
        Indexable('zojax.content.draft.indexes.DraftPublishableChecker'))


class DraftContentChecker(object):
    """
    >>> from zojax.content.type.item import Item
    >>> class Content(Item):
    ...     interface.implements(IContent)

    >>> content = Content()
    >>> DraftContentChecker(content).draft
    False

    >>> from zojax.content.draft.draft import DraftContent

    >>> draft = DraftContent(content)
    >>> DraftContentChecker(content).draft
    True
    """

    def __init__(self, content, default=None):
        self.draft = False

        if IContent.providedBy(content):
            while content is not None:
                if IDraftContent.providedBy(content):
                    self.draft = True

                content = getattr(content, '__parent__', None)


class IsDraftChecker(object):
    """
    >>> from zojax.content.type.item import Item
    >>> class Content(Item):
    ...     interface.implements(IContent)

    >>> content = Content()
    >>> IsDraftChecker(content).isDraft
    False

    >>> from zojax.content.draft.draft import DraftContent

    >>> draft = DraftContent(content)

    >>> IsDraftChecker(content).isDraft
    True
    >>> IsDraftChecker(draft).isDraft
    True
    """

    def __init__(self, content, default=None):
        while not IDraftContent.providedBy(content):
            content = content.__parent__

            if ISite.providedBy(content) or content is None:
                self.isDraft = False
                return

        self.isDraft = True


class DraftStatusChecker(object):
    """
    >>> from zojax.content.type.item import Item
    >>> class Content(Item):
    ...     interface.implements(IContent)

    >>> content = Content()
    >>> print DraftStatusChecker(content).status
    None

    >>> from zojax.content.draft.draft import DraftContent

    >>> draft = DraftContent(content)

    >>> print DraftStatusChecker(draft).status
    None
    >>> interface.alsoProvides(draft, ISubmittedDraftContent)
    >>> DraftStatusChecker(draft).status
    u'submitted'
    """

    def __init__(self, content, default=None):
        self.status = default

        if IDraftContent.providedBy(content) and \
                ISubmittedDraftContent.providedBy(content):
            self.status = u'submitted'


class DraftPublishableChecker(object):

    def __init__(self, context, default=None):
        self.value = default
        self.allowed = default

        if not IDraftContent.providedBy(context):
            return

        ct = IContentType(context, None)
        if ct is None:
            return

        location = context.getLocation()
        if location is None:
            return

        users = getAccessList(removeSecurityProxy(location), ct.publish)

        self.value = users
        self.allowed = users


class DraftSubmitTo(object):

    def __init__(self, context, default=None):
        self.value = default
        if IDraftedContent.providedBy(context):
            return

        _context = removeSecurityProxy(context)

        ct = IContentType(_context, None)
        if ct is None:
            return

        perms = {}
        for ct in ct.listContainedTypes(False):
            dct = queryUtility(IDraftContentType, ct.name)
            if dct is not None:
                # do not check permission
                if IDraftedContentType.providedBy(ct):
                    interface.noLongerProvides(ct, IDraftedContentType)

                ct.permission = None
                if not ct.isAvailable():
                    continue

                if dct.submit:
                    perms[dct.submit] = 1
                if dct.publish:
                    perms[dct.publish] = 1

        permissions = []
        for permission in perms.keys():
            permissions.extend(
                [(permission, user) for user in
                 getAccessList(_context, permission)])

        if permissions:
            self.value = permissions


class DraftPublishTo(object):
    """ list of principals """

    def __init__(self, context, default=None):
        self.value = default
        if IDraftedContent.providedBy(context):
            return

        _context = removeSecurityProxy(context)

        ct = IContentType(_context, None)
        if ct is None:
            return

        perms = {}
        for ct in ct.listContainedTypes(False):
            dct = queryUtility(IDraftContentType, ct.name)
            if dct is not None:
                # do not check permission
                if IDraftedContentType.providedBy(ct):
                    interface.noLongerProvides(ct, IDraftedContentType)
                ct.permission = None
                if not ct.isAvailable():
                    continue

                if dct.publish:
                    perms[dct.publish] = 1

        principals = {}
        for permission in perms.keys():
            principals.update(
                [(user, 1) for user in getAccessList(_context, permission)])

        if principals:
            self.value = principals.keys()
