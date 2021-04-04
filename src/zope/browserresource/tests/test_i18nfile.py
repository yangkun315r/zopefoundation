##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""I18n File-Resource Tests

$Id$
"""
from unittest import main, makeSuite
import os

from zope.publisher.interfaces import NotFound

from zope.component import provideAdapter, provideUtility
from zope.testing import cleanup

from zope.i18n.interfaces import IUserPreferredCharsets, IUserPreferredLanguages

from zope.publisher.http import IHTTPRequest, HTTPCharsets
from zope.publisher.browser import BrowserLanguages, TestRequest

from zope.browserresource.i18nfile import I18nFileResource
from zope.browserresource.i18nfile import I18nFileResourceFactory
from zope.browserresource.file import File
import zope.browserresource.tests as p

from zope.i18n.interfaces import INegotiator
from zope.i18n.negotiator import negotiator

from zope.i18n.tests.testii18naware import TestII18nAware

test_directory = os.path.dirname(p.__file__)


class Test(cleanup.CleanUp, TestII18nAware):

    def setUp(self):
        super(Test, self).setUp()
        TestII18nAware.setUp(self)
        provideAdapter(HTTPCharsets, (IHTTPRequest,), IUserPreferredCharsets)
        provideAdapter(BrowserLanguages, (IHTTPRequest,), IUserPreferredLanguages)
        # Setup the negotiator utility
        provideUtility(negotiator, INegotiator)


    def _createObject(self):
        obj = I18nFileResource({'en':None, 'lt':None, 'fr':None},
                               TestRequest(), 'fr')
        return obj

    def test_setDefaultLanguage(self):
        ob = self._createObject()
        self.assertRaises(ValueError, ob.setDefaultLanguage, 'ru')

    def _createDict(self, filename1='test.pt', filename2='test2.pt'):
        path1 = os.path.join(test_directory, 'testfiles', filename1)
        path2 = os.path.join(test_directory, 'testfiles', filename2)
        return { 'en': File(path1, filename1),
                 'fr': File(path2, filename2) }


    def testNoTraversal(self):

        resource = I18nFileResourceFactory(self._createDict(), 'en')\
                                          (TestRequest())

        self.assertRaises(NotFound,
                          resource.publishTraverse,
                          resource.request,
                          '_testData')

    def testFileGET(self):

        # case 1: no language preference, should get en
        path = os.path.join(test_directory, 'testfiles', 'test.txt')

        resource = I18nFileResourceFactory(self._createDict('test.txt'), 'en')\
                                          (TestRequest())


        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 2: prefer lt, have only en and fr, should get en
        resource = I18nFileResourceFactory(
                        self._createDict('test.txt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='lt'))

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 3: prefer fr, have it, should get fr
        path = os.path.join(test_directory, 'testfiles', 'test2.pt')
        resource = I18nFileResourceFactory(
                        self._createDict('test.pt', 'test2.pt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='fr'))

        self.assertEqual(resource.GET(), open(path, 'rb').read())

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/html')


    def testFileHEAD(self):

        # case 1: no language preference, should get en
        resource = I18nFileResourceFactory(self._createDict('test.txt'), 'en')\
                                          (TestRequest())

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 2: prefer lt, have only en and fr, should get en
        resource = I18nFileResourceFactory(
                        self._createDict('test.txt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='lt'))

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/plain')

        # case 3: prefer fr, have it, should get fr
        resource = I18nFileResourceFactory(
                        self._createDict('test.pt', 'test2.pt'), 'en')\
                        (TestRequest(HTTP_ACCEPT_LANGUAGE='fr'))

        self.assertEqual(resource.HEAD(), '')

        response = resource.request.response
        self.assertEqual(response.getHeader('Content-Type'), 'text/html')


def test_suite():
    return makeSuite(Test)
