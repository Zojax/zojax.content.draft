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
from zope.component import getUtility
from zope.security.management import queryInteraction
from zope.securitypolicy.interfaces import IRolePermissionMap

from zojax.content.type.interfaces import \
    IContent, IContentType, IDraftedContent
from zojax.permissionsmap.interfaces import IPermissionsMap

from interfaces import IDraftContentType, IDraftedContentType


@component.adapter(IContent)
@interface.implementer(IRolePermissionMap)
def getContentPermissions(context):
    if IDraftedContent.providedBy(context):
        return getUtility(IPermissionsMap, 'content.permissions.opened')

    ct = IContentType(context, None)

    if ct is not None and IDraftedContentType.providedBy(ct):
        interaction = queryInteraction()
        if interaction is not None:
            dct = getUtility(IDraftContentType, ct.name)

            if dct.retractable and not \
                    interaction.checkPermission(dct.publish,context.__parent__):
                return getUtility(IPermissionsMap, 'content.permissions.closed')

    return getUtility(IPermissionsMap, 'content.permissions.opened')
