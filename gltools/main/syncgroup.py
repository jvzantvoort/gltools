#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""syncgroup.py - $description


Copyright (C) 2019 John van Zantvoort

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import print_function

import os
import logging
import pkgutil
import tempfile

from gltools.main.common import Main

__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"
__license__ = "proprietary"
__version__ = "1.0.1"


class SyncGroup(Main):

    def __init__(self, **kwargs):
        props = ("GITLAB", "DESTINATION", "SWLIST", "BUNDLES", "EXTENDED",
                 "HTTP", "GROUPNAME")

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))
        self._scripttemplate = pkgutil.get_data(__package__, 'sync.sh')
        self.outputdir = None # shutup pylint

    def main(self):
        tempdir = os.path.join(self.outputdir, "tmp")
        try:
            os.makedirs(tempdir)

        except OSError as err:
            self.logger.error(err)

        tempdir = tempfile.mkdtemp(suffix='_sync',
                                   prefix=self.groupname + "_",
                                   dir=tempdir)

        for row in self.getprojects():
            print(row)
