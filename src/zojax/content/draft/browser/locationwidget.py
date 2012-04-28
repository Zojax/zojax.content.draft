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
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from zope.security import checkPermission
from zope.session.interfaces import ISession
from zope.schema.interfaces import IField
from zope.traversing.api import getPath

from z3c.breadcrumb.interfaces import IBreadcrumb
from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser.widget import HTMLInputWidget

from zojax.batching.session import SessionBatch
from zojax.catalog.interfaces import ICatalog
from zojax.catalog.utils import listAllowedRoles
from zojax.content.type.interfaces import IContentType, IItem

from zojax.content.draft.interfaces import ILocationField, ILocationWidget
from zojax.content.draft.browser.interfaces import ILocationContainer

SESSIONKEY = 'zojax.batching'


def searchLocations(query=None):

    results = None
    catalog = getUtility(ICatalog)

    if query:
        results = catalog.searchResults(**query)

    return results


class LocationWidget(HTMLInputWidget, Widget):
    interface.implementsOnly(ILocationWidget)

    pageSize = 20

    def update(self):
        name = self.name
        request = self.request
        context = self.form.context

        key = u'%s:%s'%(getPath(context), name)
        self.sessionKey = key
        self.selectedName = u'%s-selectedItem'%name

        super(LocationWidget, self).update()

        query = {}

        # NOTE: types
        ct = IContentType(self.context)
        types = []
        for tp in ct.destination:
            types.append(tp.name)

        if types:
            query['type'] = {'any_of': types}

        # NOTE: permissions
        perms = {}
        permissions = []
        for id in listAllowedRoles(request.principal, self.context):
            perms[ct.submit] = 1
            perms[ct.publish] = 1
            permissions.append((ct.submit, id))
            permissions.append((ct.publish, id))

        if permissions:
            query['draftSubmitTo'] = {'any_of': permissions}

        # NOTE: search text + searchLocations
        data = ISession(request)[SESSIONKEY]
        if '%s-empty-marker'%name not in request and key in data:
            del data[key]

        if u'%s.searchButton'%name in request:
            searching = True
            searchtext = request.get(u'%s.searchText'%name, u'')
            data[key] = (searchtext, True)
            if searchtext:
                query['searchableText'] = searchtext
                try:
                    results = searchLocations(query)
                except:
                    results = []
            else:
                results = []
        elif u'%s.searchClear'%name in request:
            if key in data:
                del data[key]
            searchtext = u''
            searching = False
            results = searchLocations(query)
        else:
            searchtext, searching = data.get(key, (u'', False))
            if searchtext:
                query['searchableText'] = searchtext
                try:
                    results = searchLocations(query)
                except:
                    results = []
            else:
                results = searchLocations(query)

        self.searching = searching
        self.searchtext = searchtext
        self.totalcount = len(results)

        self.locations = SessionBatch(
            results, size=self.pageSize,
            context=context, request=request, prefix=name,
            queryparams = {'%s-empty-marker'%self.name: '1'})

    def getLocationInfo(self, location):

        path = getPath(location)
        title = IItem(location).title
        id = getUtility(IIntIds).getId(location)

        breadcrum = getMultiAdapter((location, self.request), IBreadcrumb)
        icon = queryMultiAdapter((location, self.request), name='zmi_icon')

        selected = str(id) in self.value
        if selected:
            print location

        info = {'id':id,
                'value': str(id),
                'selected': selected,
                'breadcrum': breadcrum,
                'space': '',
                'spaceUrl': '',
                'icon': icon,
                'description': getattr(location,'description','')or None}

        container = getattr(location, '__parent__', None)
        while not ILocationContainer.providedBy(container) and \
                container is not None:
            container = getattr(container, '__parent__', None)

        if container is not None:
            breadcrum = getMultiAdapter((container, self.request), IBreadcrumb)
            info['space'] = breadcrum.name
            info['spaceUrl'] = breadcrum.url
            info['spaceDescription'] = container.description or None

        return info

    def getSelected(self):

        try:
            return self.value
        except:
            pass


@component.adapter(ILocationField, interfaces.IFormLayer)
@interface.implementer(interfaces.IFieldWidget)
def LocationFieldWidget(field, request):
    """IFieldWidget factory for LocationWidget."""
    return FieldWidget(field, LocationWidget(request))
