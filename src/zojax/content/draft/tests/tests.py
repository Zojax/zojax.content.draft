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
""" zojax.content.draft tests

$Id$
"""
import os, unittest, doctest
from zope import interface, component, event
from zope.app.testing import functional, setup, placelesssetup
from zope.app.component.hooks import setSite
from zope.app.rotterdam import Rotterdam
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.security.interfaces import IAuthentication
from zope.lifecycleevent import ObjectCreatedEvent
from zojax.catalog.interfaces import ICatalog
from zojax.catalog.catalog import Catalog
from zojax.ownership.interfaces import IOwnership
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.content.type.testing import setUpContents


zojaxContentDraftLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxContentDraftLayer', allow_teardown=True)


def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxContentDraftLayer

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        root = functional.getRootFolder()
        setSite(root)

        sm = root.getSiteManager()

        # IIntIds
        root['ids'] = IntIds()
        sm.registerUtility(root['ids'], IIntIds)
        root['ids'].register(root)

        # catalog
        root['catalog'] = Catalog()
        sm.registerUtility(root['catalog'], ICatalog)

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old|doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def setUp(test):
    placelesssetup.setUp(test)
    setUpContents()
    setup.setUpTestAsModule(test, 'zojax.content.draft.TESTS')


def tearDown(test):
    placelesssetup.tearDown(test)
    setup.tearDownTestAsModule(test)


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def test_suite():
    return unittest.TestSuite((
            doctest.DocTestSuite(
                'zojax.content.draft.indexes',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),

            doctest.DocFileSuite(
                './zcml.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),

            FunctionalDocFileSuite("draft.txt"),
            #FunctionalDocFileSuite("vocabulary.txt"),
            FunctionalDocFileSuite("testbrowser.txt"),
            ))
