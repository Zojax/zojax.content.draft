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
from zojax.activity.interfaces import IActivityAware
from zojax.content.type.interfaces import IItem
from zojax.content.type.item import PersistentItem
from zojax.content.type.container import ContentContainer


class IContent1(IItem):
    """ content 1 """


class Content1(PersistentItem):
    interface.implements(IContent1, IActivityAware)


class IContent2(IItem):
    """ content 2 """


class Content2(PersistentItem):
    interface.implements(IContent2, IActivityAware)



class IContainer1(IItem):
    """ container 1 """


class Container1(ContentContainer):
    interface.implements(IContainer1, IActivityAware)


class IContainer2(IItem):
    """ container 2 """


class Container2(ContentContainer):
    interface.implements(IContainer2, IActivityAware)
