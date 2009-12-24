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
from zope.exceptions.interfaces import UserError
from zope.app.container.interfaces import \
    IWriteContainer, IContainerNamesContainer, INameChooser

from z3c.form import validator
from z3c.form.error import ErrorViewSnippet

from zojax.layoutform import button, Fields, PageletEditSubForm
from zojax.content.forms.content import ContentStep
from zojax.content.forms.interfaces import IContentRenameForm
from zojax.content.type.interfaces import \
    IContentNamesContainer, IEmptyNamesNotAllowed

from interfaces import _


class ContentStep(ContentStep):

    def isComplete(self):
        if super(ContentStep, self).isComplete():
            draft = self.wizard.draft
            location = draft.getLocation()

            if location is not None:
                if IContentNamesContainer.providedBy(draft.content):
                    return True

                if not draft.shortname and \
                        not IEmptyNamesNotAllowed.providedBy(location):
                    return True

                chooser = INameChooser(location)
                try:
                    chooser.checkName(draft.shortname, None)
                    return True
                except UserError, err:
                    pass

        return False


class ContentShortnameForm(PageletEditSubForm):

    fields = Fields(IContentRenameForm)

    def getContent(self):
        draft = self.parentForm.wizard.draft
        return {'shortname': draft.shortname}

    def applyChanges(self, data):
        draft = self.parentForm.wizard.draft
        if draft.shortname != data['shortname']:
            draft.shortname = data['shortname']

    def isAvailable(self):
        draft = self.parentForm.wizard.draft
        content = draft.content
        location = draft.getLocation()

        if not IContentNamesContainer.providedBy(content) and \
                IWriteContainer.providedBy(location) and \
                not IContainerNamesContainer.providedBy(location):
            return True

        return False


class NameError(schema.ValidationError):
    __doc__ = _(u'Content name already in use.')

    def __init__(self, msg):
        self.message = msg


class NameErrorViewSnippet(ErrorViewSnippet):

    def update(self):
        self.message = self.error.message


class ContentNameValidator(validator.InvariantsValidator):
    component.adapts(
        interface.Interface,
        interface.Interface,
        ContentShortnameForm,
        interface.Interface,
        interface.Interface)

    def validate(self, data):
        form = self.view
        if 'shortname' not in form.widgets:
            return super(ContentNameValidator, self).validate(data)

        widget = form.widgets['shortname']

        if widget.error:
            return (widget.error.error, ) + super(ContentNameValidator, self).validate(data)

        shortname = data.get('shortname')
        draft = self.view.parentForm.wizard.draft
        location = draft.getLocation()

        if location is None or \
                not shortname and not IEmptyNamesNotAllowed.providedBy(location):
            return super(ContentNameValidator, self).validate(data)

        errors = []
        chooser =  INameChooser(location)
        try:
            chooser.checkName(shortname, draft.content)
        except (UserError, ValueError), err:
            exc = NameError(unicode(err))

            widget.error = NameErrorViewSnippet(
                exc, self.request, widget, widget.field, form, self.context)
            widget.error.update()
            errors.append(exc)
        return tuple(errors) + super(ContentNameValidator, self).validate(data)
