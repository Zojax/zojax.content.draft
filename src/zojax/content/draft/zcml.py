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
from zope import interface, component, schema
from zope.interface.interface import InterfaceClass
from zope.security.zcml import Permission
from zope.security.checker import CheckerPublic
from zope.security.interfaces import IPermission
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import Tokens, GlobalObject, GlobalInterface

from zojax.content.type.interfaces import IContentType

import zojax.content.draft
from draft import DraftContent
from contenttype import DraftContentType
from interfaces import IDraftContentType, IDraftedContentType


class IDraftContentDirective(interface.Interface):

    content = schema.TextLine(
        title = u'Original Content',
        required = True)

    destination = Tokens(
        title = u'Destination content',
        value_type = schema.TextLine(),
        required = False)

    submit = Permission(
        title = u'Submit permission',
        required = False)

    publish = Permission(
        title = u'Publish permission',
        required = False)

    retract = Permission(
        title = u'Retract permission',
        required = False)

    class_ = GlobalObject(
        title = u'Content Class',
        description = u'Custom content implementation',
        required = False)

    ctclass = GlobalObject(
        title = u'Content Type Class',
        description = u'Custom content type implementation',
        required = False)

    provides = Tokens(
        title = u'Provides',
        value_type = GlobalInterface(),
        required = False)

    saveable = schema.Bool(
        title = u'Saveable',
        description = u'Allow save draft to draft container.',
        required = False)

    retractable = schema.Bool(
        title = u'Retractable',
        description = u'Allow retract content to draft container.',
        required = False)


def draftContentHandler(_context, content,
                        class_=DraftContent, ctclass=DraftContentType,
                        destination='', submit='', publish='', retract='',
                        saveable=True, retractable=True, provides=()):

    if submit == 'zope.Public' or publish == 'zope.Public':
        raise ConfigurationError("zope.Public permission is not supported.")

    cname = str(content)
    for ch in ('.', '-'):
        cname = cname.replace(ch, '_')

    draftcontenttype = InterfaceClass(
        cname, (IDraftContentType,),
        __doc__='Draft Content Type: %s' %cname,
        __module__='zojax.content.draft.interfaces')

    # Add the content type to the `zojax.content` module.
    setattr(zojax.content.draft.interfaces, cname, draftcontenttype)

    _context.action(
        discriminator = ('zojax.content.draft:draftcontent', content),
        callable = draftContent,
        args = (_context, content, class_, ctclass,
                draftcontenttype, destination,
                submit, publish, retract, saveable, retractable, provides))


def draftContent(_context, content, class_,
                 ctclass, ctiface, destination, submit, publish, retract,
                 saveable, retractable, provides):
    sm = component.getGlobalSiteManager()

    ct = sm.getUtility(IContentType, content)
    interface.alsoProvides(ct, IDraftedContentType)

    dest = []
    for dct in destination:
        destct = sm.queryUtility(IContentType, dct)
        if destct is not None:
            dest.append(destct)

    draft = ctclass(
        ct, dest, submit, publish, retract, saveable, retractable, class_)
    sm.registerUtility(draft, IDraftContentType, name=content)

    # added custom interface to contenttype object
    for iface in (ctiface,) + tuple(provides):
        contenttypeInterface(draft, iface)

    # register utilities
    for iface in tuple(provides):
        sm.registerUtility(draft, iface, name=content)


def contenttypeInterface(ct, iface):
    provides = list(interface.directlyProvidedBy(ct))
    if iface not in provides:
        provides = [iface] + provides
        interface.directlyProvides(ct, *provides)
