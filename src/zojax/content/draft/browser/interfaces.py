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
from zojax.layoutform import button
from zojax.layoutform.interfaces import ISaveAction, ICancelAction
from zojax.wizard.interfaces import IWizard, IWizardStep
from zojax.wizard.interfaces import ISaveable, IPreviousAction, IForwardAction
from zojax.content.forms.interfaces import \
    IContentWizard, IAddContentWizard, IEditContentWizard

from zojax.content.draft.interfaces import _


class ILocationContainer(interface.Interface):
    """ marker interface for location container """


# Draft wizards actions
class IPublishAction(ISaveAction):
    """Publish content action."""


class ISubmitAction(ISaveAction):
    """Submit content action."""


class IRetractAction(interface.Interface):
    """Retract draft action."""


class IRejectAction(interface.Interface):
    """Reject draft action."""


class IRemoveAction(interface.Interface):
    """Remove draft action."""


class IApproveAction(ISaveAction):
    """Approve submitted content action."""


class ISaveDraftAction(ISaveAction):
    """Save draft action."""


# draft content step
class IDraftContentStep(interface.Interface):
    """ Content step for drafted content. """


# content location steps
class IContentLocationStep(IWizardStep):
    """Location step."""


# Add Draft wizard

class IAddDraftWizard(IAddContentWizard):
    """ Add Draft wizard """

    draft = interface.Attribute('Draft')

    def isSaveable():
        """ Allow save draft """

    def isSubmitable():
        """Is submitable"""

    def isPublishable():
        """Is publishable"""

    def isLocationStep():
        """Is location step"""


class IAddContentWizard(IAddContentWizard):
    """ Add content wizard """

    draft = interface.Attribute('Draft')

    def isSaveable():
        """ Allow save draft """

    def isSubmitable():
        """Is submitable"""

    def isPublishable():
        """Is publishable"""

    def isLocationStep():
        """Is location step"""


class IAddDraftWizardButtons(interface.Interface):
    """Add wizard buttons """

    previous = button.Button(
        title = _(u'Previous'),
        condition = lambda form: not form.isFirstStep())
    interface.alsoProvides(previous, IPreviousAction)

    savenext = button.Button(
        title = _(u'Next'),
        condition = lambda form: not form.isLastStep())
    interface.alsoProvides(savenext, IForwardAction, ISaveAction)

    saveDraft = button.Button(
        title = _(u'Save as Draft'),
        condition = lambda form: not form.isLocationStep() and form.isSaveable())
    interface.alsoProvides(saveDraft, ISaveDraftAction)

    publish = button.Button(
        title = _(u'Publish'),
        condition = lambda form: form.isPublishable())
    interface.alsoProvides(publish, IPublishAction)

    submit = button.Button(
        title = _(u'Submit'),
        condition = lambda form: form.isSubmitable())
    interface.alsoProvides(submit, ISubmitAction)

    cancel = button.Button(title=u'Cancel')
    interface.alsoProvides(cancel, ICancelAction)


# Edit draft wizard

class IEditDraftWizard(IEditContentWizard):
    """ Edit draft wizard """

    draft = interface.Attribute('Draft')


class IEditDraftWizardButtons(interface.Interface):
    """ Edit draft wizard buttons """

    previous = button.Button(
        title = _(u'Previous'),
        condition = lambda form: not form.isFirstStep())
    interface.alsoProvides(previous, IPreviousAction)

    savenext = button.Button(
        title = _(u'Save & Next'),
        condition = lambda form: not form.isLastStep() \
            and form.step.isSaveable())
    interface.alsoProvides(savenext, IForwardAction, ISaveAction)

    save = button.Button(
        title = _(u'Save'),
        condition = lambda form: form.isLastStep() \
            and form.step.isSaveable())
    interface.alsoProvides(save, ISaveAction)

    next = button.Button(
        title = _(u'Next'),
        condition = lambda form: not form.isLastStep() \
            and not form.step.isSaveable())
    interface.alsoProvides(next, IForwardAction)

    publish = button.Button(
        title = _(u'Publish'),
        condition = lambda form: form.isPublishable() and \
            not IContentLocationStep.providedBy(form.step))
    interface.alsoProvides(publish, IPublishAction)

    submit = button.Button(
        title = _(u'Submit'),
        condition = lambda form: form.isSubmitable() and \
            not IContentLocationStep.providedBy(form.step))
    interface.alsoProvides(submit, ISubmitAction)

    remove = button.Button(
        title = _(u'Remove'))
    interface.alsoProvides(remove, IRemoveAction)


# submitted draft view

class ISubmittedDraftWizard(IWizard):
    """Submitted draft wizard."""

    draft = interface.Attribute('Draft')

    title = interface.Attribute('Title')

    description = interface.Attribute('Description')


class ISubmittedDraftWizardButtons(interface.Interface):

    retract = button.Button(
        title = _(u'Retract'),
        condition = lambda form: not form.context.isPublishable())
    interface.alsoProvides(retract, IRetractAction)

    reject = button.Button(
        title = _(u'Reject'),
        condition = lambda form: form.context.isPublishable())
    interface.alsoProvides(reject, IRejectAction)

    publish = button.Button(
        title = _(u'Publish'),
        condition = lambda form: form.context.isPublishable())
    interface.alsoProvides(publish, IPublishAction)

    remove = button.Button(
        title = _(u'Remove'))
    interface.alsoProvides(remove, IRemoveAction)
