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
""" Castom Button Widget Implementation

$Id$
"""
from zope import interface, component

from z3c.form import interfaces, widget, action, button
from zojax.layoutform.interfaces import ILayoutFormLayer
from interfaces import \
    ISubmitAction, IPublishAction, IRemoveAction, ISaveDraftAction


class SubmitButtonAction(button.ButtonAction):
    interface.implements(interfaces.IButtonAction)
    component.adapts(ILayoutFormLayer, ISubmitAction)

    klass="z-draft-submitbutton"


class PublishButtonAction(button.ButtonAction):
    interface.implements(interfaces.IButtonAction)
    component.adapts(ILayoutFormLayer, IPublishAction)

    klass="z-draft-publishbutton"


class RemoveButtonAction(button.ButtonAction):
    interface.implements(interfaces.IButtonAction)
    component.adapts(ILayoutFormLayer, IRemoveAction)

    klass="z-draft-removebutton"


class SaveDraftButtonAction(button.ButtonAction):
    interface.implements(interfaces.IButtonAction)
    component.adapts(ILayoutFormLayer, ISaveDraftAction)

    klass="z-draft-savedraftbutton"
