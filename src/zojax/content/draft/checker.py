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
from zope import interface, component
from zope.component import getUtility, queryMultiAdapter
from zope.security.management import queryInteraction
from zojax.content.type.interfaces import IContentTypeChecker
from zojax.content.type.interfaces import IContentType, IContentContainer

from interfaces import IDraftContentType, IDraftedContentType, IDraftContainer


class PermissionChecker(object):
    interface.implements(IContentTypeChecker)
    component.adapts(IDraftedContentType, IContentContainer)

    def __init__(self, contenttype, context):
        self.contenttype = contenttype
        self.context = context
        self.draftct = getUtility(IDraftContentType, contenttype.name)

    def check(self):
        interaction = queryInteraction()
        if interaction is None:
            return False

        request = None
        for participation in interaction.participations:
            request = participation
            if request is not None:
                break

        if request is None:
            return False

        contenttype = self.draftct

        container = queryMultiAdapter(
            (request.principal, contenttype), IDraftContainer)
        if container is None:
            return False

        if contenttype.submit:
            if interaction.checkPermission(contenttype.submit, self.context):
                return True

        if contenttype.publish:
            if interaction.checkPermission(contenttype.publish, self.context):
                return True

        return False
