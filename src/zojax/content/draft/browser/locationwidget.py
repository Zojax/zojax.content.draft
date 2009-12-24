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
from zope.i18n import translate
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.schema.interfaces import ITitledTokenizedTerm

from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.i18n import MessageFactory as _
from z3c.form.widget import SequenceWidget, FieldWidget
from z3c.form.browser import widget
from z3c.breadcrumb.interfaces import IBreadcrumb

from zojax.content.type.interfaces import IContentType

from interfaces import ILocationContainer


class LocationWidget(widget.HTMLSelectWidget, SequenceWidget):

    klass = u'select-widget'
    items = ()
    prompt = False

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    # Internal attributes
    _adapterValueAttributes = SequenceWidget._adapterValueAttributes + \
        ('noValueMessage', 'promptMessage')

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(LocationWidget, self).update()
        widget.addFieldClass(self)

        request = self.request

        self.items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            self.items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })

        for count, term in enumerate(self.terms):
            selected = term.token in self.value

            id = '%s-%i' % (self.id, count)

            info = {'id':id,
                    'value': term.token,
                    'selected': selected,
                    'breadcrum': term.title,
                    'space': '',
                    'spaceUrl': '',
                    'icon': queryMultiAdapter(
                       (term.content, request), name='zmi_icon'),
                    'description': getattr(term.content,'description','')or None}

            container = getattr(term.content, '__parent__', None)
            while not ILocationContainer.providedBy(container) and \
                    container is not None:
                container = getattr(container, '__parent__', None)

            if container is not None:
                breadcrum = getMultiAdapter((container, request), IBreadcrumb)
                info['space'] = breadcrum.name
                info['spaceUrl'] = breadcrum.url
                info['spaceDescription'] = container.description or None

            self.items.append(info)


def LocationFieldWidget(field, request):
    return FieldWidget(field, LocationWidget(request))
