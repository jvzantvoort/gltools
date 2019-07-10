#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.exportgroup"""

import os
import tempfile
import logging
import pkgutil
from gltools.main.common import Main

log = logging.getLogger('gltools.main.exportgroup')

class ExportGroup(Main):

    def __init__(self, **kwargs):
        self.tempdir = None

        super(ExportGroup, self).__init__(**kwargs)

        if self.outputdir is None:
            self.outputdir = self.gltcfg.exportdir

        if self.tempdir is None:
            self.tempdir = self.gltcfg.tempdir

        self._scripttemplate = pkgutil.get_data(__package__, 'export.sh')


    def export_project(self, row, outputdir, tempdir):
        row['outputdir'] = outputdir
        row['tempdir'] = tempdir

        log.info("%(name)s" % row)
        log.debug("export %(name)s, start" % row)
        scriptname = "%(group_path)s_%(name)s.sh" % row
        scriptname = scriptname.lower().replace(' ', '_')
        outfile = os.path.join(tempdir, scriptname)
        log.debug("  wrote scriptfile: %s" % outfile)
        with open(outfile, "w") as ofh:
            ofh.write(self._scripttemplate % row)
        os.chmod(outfile, 493)
        self.exec_script(outfile)
        os.unlink(outfile)
        log.debug("export %(name)s, end" % row)

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
        log.info("outputdir: %s" % self.outputdir)
        try:
            os.makedirs(self.tempdir)

        except OSError as err:
            pass

        tempdir = tempfile.mkdtemp(suffix='_export',
                                   prefix=self.srcgroupname + "_",
                                   dir=self.tempdir)

        for row in self.getprojects():
            self.export_project(row, self.outputdir, tempdir)
