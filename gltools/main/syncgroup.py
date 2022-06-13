#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.syncgroup"""

from __future__ import print_function

import os
import logging
import pkgutil
import tempfile

from gltools.main.common import Main
from gltools.localgitlab import MirrorGitLab
from gltools.config import GitLabToolsConfig
from gltools.exceptions import GLToolsException

log = logging.getLogger("gltools.syncgroup")

__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"
__license__ = "proprietary"
__version__ = "1.0.1"


class SyncGroup(Main):
    """this class syncs data from one group to another.

    extended explanation

    :param arg1: description
    :param arg2: description
    :type arg1: type description
    :type arg1: type description

    .. note:: we only use origin/main and ssh for the moment. Life is hard
              enough already.
    """

    def __init__(self, **kwargs):
        super(SyncGroup, self).__init__(**kwargs)

        self.srcconfig = GitLabToolsConfig(
            servername=self.gitlab_config_section, groupname=self.srcgroupname
        )

        self.dstconfig = GitLabToolsConfig(
            servername=self.dst_gitlab_config_section, groupname=self.dstgroupname
        )

        self.repository = "source"
        self.refspec = "master"

        self._scripttemplate = pkgutil.get_data(__package__, "sync.sh")

    def sync_project(self, row, tempdir):
        row["tempdir"] = tempdir
        row["branch"] = self.refspec
        row["source"] = self.repository
        log.info("%(name)s" % row)
        log.debug("sync %(name)s, start" % row)
        scriptname = "%(path)s.sh" % row
        outfile = os.path.join(tempdir, scriptname)
        log.debug("  wrote scriptfile: %s" % outfile)
        with open(outfile, "w") as ofh:
            ofh.write(self._scripttemplate % row)

        os.chmod(outfile, 493)
        self.exec_script(outfile)
        os.unlink(outfile)
        log.debug("export %(name)s, end" % row)

    def main(self):
        tempdir = self.mktemp("_sync")

        if not self.srcconfig.protected:
            log.warn("%s should be protected in gltools config" % self.srcgroupname)

        if self.dstconfig.protected:
            raise GLToolsException("cowardly refusing to sync to a protected group")

        mirror = MirrorGitLab()
        mirror.source = self.gitlab_config_section
        mirror.destination = self.dst_gitlab_config_section
        mirrordata = mirror.mirror_groups(self.srcgroupname, self.dstgroupname)
        for row in mirrordata:
            self.sync_project(row, tempdir)


class SyncGroupLocal(Main):
    def __init__(self, **kwargs):
        super(SyncGroupLocal, self).__init__(**kwargs)

        self.srcconfig = GitLabToolsConfig(
            servername=self.gitlab_config_section, groupname=self.srcgroupname
        )

        self.repository = "source"
        self.refspec = "master"
        # self.dstdirectory

        self._scripttemplate = pkgutil.get_data(__package__, "synclocal.sh")

    def sync_project(self, row, tempdir):

        scriptname = "%(path)s.sh" % row
        outfile = os.path.join(tempdir, scriptname)

        row["tempdir"] = tempdir
        row["branch"] = self.refspec
        row["source"] = self.repository

        log.info("%(name)s" % row)
        log.debug("sync %(name)s, start" % row)
        log.debug("  wrote scriptfile: %s" % outfile)
        with open(outfile, "w") as ofh:
            ofh.write(self._scripttemplate % row)

        os.chmod(outfile, 493)
        self.exec_script(outfile)
        os.unlink(outfile)
        log.debug("export %(name)s, end" % row)

    def main(self):
        tempdir = self.mktemp("_synclocal")

        if not self.srcconfig.protected:
            log.warn("%s should be protected in gltools config" % self.srcgroupname)

        mirror = MirrorGitLab()
        mirror.source = self.gitlab_config_section
        mirrordata = mirror.mirror_to_local(self.srcgroupname, self.dstdirectory)
        for row in mirrordata:
            self.sync_project(row, tempdir)
