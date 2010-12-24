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
from zope.component import getUtility, getMultiAdapter
from zope.traversing.api import getPath
from zope.security import checkPermission
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from z3c.breadcrumb.interfaces import IBreadcrumb
from zojax.catalog.interfaces import ICatalog
from zojax.catalog.utils import getRequest, listAllowedRoles
from zojax.content.type.interfaces import IContentType, IItem
from zojax.content.type.constraints import checkContentType
from zojax.content.draft.interfaces import _, IDraftContent


class Vocabulary(SimpleVocabulary):

    def getTerm(self, value):
        try:
            return self.by_value[value]
        except KeyError:
            try:
                return self.by_value[self.by_value.keys()[0]]
            except IndexError:
                raise LookupError(value)


class LocationsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        if not IDraftContent.providedBy(context):
            return Vocabulary(())

        ct = IContentType(context)
        types = []
        for tp in ct.destination:
            types.append(tp.name)

        kwargs = {}
        if types:
            kwargs['type'] = {'any_of': types}

        request = getRequest()
        catalog = getUtility(ICatalog)

        perms = {}
        permissions = []
        for id in listAllowedRoles(request.principal, context):
            perms[ct.submit] = 1
            perms[ct.publish] = 1
            permissions.append((ct.submit, id))
            permissions.append((ct.publish, id))

        results = catalog.searchResults(
            draftSubmitTo={'any_of': permissions}, **kwargs)

        if not results:
            return Vocabulary(())

        perms = perms.keys()
        ids = getUtility(IIntIds)

        contents = []
        for content in results:
            allow = False
            for perm in perms:
                if checkPermission(perm, content):
                    allow = True
                    break

            if allow:
                contents.append(
                    (getPath(content),
                     IItem(content).title, ids.getId(content), content))

        contents.sort()

        terms = []
        for path, title, id, content in contents:
            term = SimpleTerm(
                id, str(id), getMultiAdapter((content, request), IBreadcrumb))
            term.content = content
            terms.append(term)

        return Vocabulary(terms)
