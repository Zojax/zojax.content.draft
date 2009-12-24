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
from zope import component, interface
from zojax.content.type.interfaces import IContentType
from zojax.content.browser.breadcrumb import ContentBreadcrumb

from zojax.content.draft.interfaces import \
    _, IDraftContent, IDraftedContent, IDraftContainer, IDraftContentType


class DraftContainerBreadcrumb(ContentBreadcrumb):
    component.adapts(IDraftContainer, interface.Interface)

    name = _(u'Your draft items')


class DraftContentBreadcrumb(ContentBreadcrumb):
    component.adapts(IDraftContent, interface.Interface)

    @property
    def name(self):
        return u'Draft: %s'%IContentType(self.context.content).title


class DraftedContentBreadcrumb(ContentBreadcrumb):
    component.adapts(IDraftedContent, interface.Interface)

    @property
    def name(self):
        return u'Draft: %s'%IContentType(self.context).title
