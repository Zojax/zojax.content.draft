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
from zope.component import queryMultiAdapter
from zojax.content.draft.interfaces import IDraftContent, IDraftContentType


@interface.implementer(interface.Interface)
@component.adapter(IDraftContent, interface.Interface)
def draftContentIcon(draft, request):
    return queryMultiAdapter((draft.content, request), name='zmi_icon')


@interface.implementer(interface.Interface)
@component.adapter(IDraftContentType, interface.Interface)
def draftContentTypeIcon(draft, request):
    return queryMultiAdapter((draft.contenttype, request), name='zmi_icon')
