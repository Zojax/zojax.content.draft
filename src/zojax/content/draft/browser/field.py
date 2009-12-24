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
from zope import interface, schema
from zope.schema import TextLine
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.exceptions.interfaces import UserError
from zope.app.container.interfaces import INameChooser
from zojax.content.type.interfaces import IContentType


class IAddName(interface.Interface):
    """ Content short name for add content form """


class IEditName(interface.Interface):
    """ Content short name for edit content form """


class NameError(schema.ValidationError):
    __doc__ = u'Content name already in use.'

    def __init__(self, msg):
        self.__doc__ = msg


class AddName(TextLine):
    interface.implements(IAddName)

    def validate(self, value):
        super(AddName, self).validate(value)

        if self.context is None:
            return

        return True
        container = getUtility(IIntIds).queryObject(self.context.get('location'))
        if container is not None:
            # check content name
            chooser = INameChooser(container)

            try:
                chooser.checkName(value, None)
            except UserError, err:
                raise NameError(unicode(err))
