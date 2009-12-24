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
from zope.security import checkPermission
from zope.component import getUtility, queryMultiAdapter
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import ICMFDublinCore

from zojax.content.type.interfaces import IContentType
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.draft.interfaces import _, ISubmittedDraftContent


class DraftContainerView(object):

    def listDrafts(self):
        ids = getUtility(IIntIds)
        request = self.request
        context = self.context

        drafts = []
        for name in context:
            draft = context[name]
            if not checkPermission('zope.View', draft):
                continue

            try:
                loc = ids.queryObject(draft.location)
                locTitle = loc.title
                locUrl = '%s/'%absoluteURL(loc, request)
            except:
                locTitle = _('Unknown')
                locUrl = u''

            dc = ICMFDublinCore(draft.content)

            info = {'name': name,
                    'title': draft.title or _('[No title]'),
                    'description': draft.description,
                    'url': '%s/'%absoluteURL(draft, request),
                    'location': locTitle,
                    'locationURL': locUrl,
                    'icon': queryMultiAdapter((draft, request), name='zmi_icon'),
                    'draft': draft,
                    'modified': dc.modified,
                    'status': ISubmittedDraftContent.providedBy(draft),
                    'contentType': IContentType(draft.content)}
            drafts.append(info)

        return drafts

    def update(self):
        request = self.request
        context = self.context

        if 'form.button.remove' in request:
            ids = request.get('draftId', ())
            if not ids:
                IStatusMessage(request).add(_('Please select draft items.'))
            else:
                for id in request.get('draftId', ()):
                    if id in context:
                        del context[id]

                IStatusMessage(request).add(
                    _('Selected draft items have been removed.'))
