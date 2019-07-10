#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""exportgroup.py - $description


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

import os
import tempfile
import logging
import pkgutil

from gltools.main.common import Main


class ExportGroup(Main):

    def __init__(self, **kwargs):
        props = ("GITLAB", "OUTPUTDIR", "SWLIST", "BUNDLES", "EXTENDED",
                 "HTTP", "GROUPNAME")

        self._lgitlab = None

        self.swlist = False
        self.bundles = False
        self.extended = False
        self.http = False
        self.gitlab = None
        self.outputdir = None
        self.groupname = None
        self._scripttemplate = pkgutil.get_data(__package__, 'export.sh')

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

    def export_project(self, row, outputdir, tempdir):
        row['outputdir'] = outputdir
        row['tempdir'] = tempdir

        self.logger.info("export %(name)s, start" % row)
        scriptname = "%(group_path)s_%(name)s.sh" % row
        scriptname = scriptname.lower().replace(' ', '_')
        outfile = os.path.join(tempdir, scriptname)
        self.logger.debug("  wrote scriptfile: %s" % outfile)
        with open(outfile, "w") as ofh:
            ofh.write(self._scripttemplate % row)
        os.chmod(outfile, 493)
        self.exec_script(outfile)
        os.unlink(outfile)
        self.logger.info("export %(name)s, end" % row)

    def getprojects(self):

        retv = list()

        for row in super(ExportGroup, self).getprojects():

            row['type'] = "portable"
            if self.bundles:
                row['type'] = "bundle"

            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)
        return retv

    def main(self):
        tempdir = os.path.join(self.outputdir, "tmp")
        try:
            os.makedirs(tempdir)

        except OSError as err:
            self.logger.error(err)

        tempdir = tempfile.mkdtemp(suffix='_export',
                                   prefix=self.groupname + "_",
                                   dir=tempdir)

        for row in self.getprojects():
            self.export_project(row, self.outputdir, tempdir)