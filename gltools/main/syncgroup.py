#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.syncgroup"""

from __future__ import print_function

import os
import logging
import pkgutil
import tempfile

from gltools.main.common import Main

log = logging.getLogger('gltools.syncgroup')

__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"
__license__ = "proprietary"
__version__ = "1.0.1"


class SyncGroup(Main):

    def __init__(self, **kwargs):
        self.tempdir = None

        super(SyncGroup, self).__init__(**kwargs)

        self.repository = "origin"
        self.refspec = "master"

        self._scripttemplate = pkgutil.get_data(__package__, 'sync.sh')
        self.outputdir = None # shutup pylint

    def main(self):
        tempdir = os.path.join(self.outputdir, "tmp")
        try:
            os.makedirs(tempdir)

        except OSError as err:
            log.error(err)

        tempdir = tempfile.mkdtemp(suffix='_sync',
                                   prefix=self.groupname + "_",
                                   dir=tempdir)

        for row in self.getprojects():
            print(row)
