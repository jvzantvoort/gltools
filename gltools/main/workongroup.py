#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.workongroup"""

import os
import logging
from gltools.git import Git
from gltools.config import GitLabToolsConfig
from gltools.main.common import Main

log = logging.getLogger("gltools.main.workongroup")


class WorkOnGroup(Main):
    """Setup a project directory so the user can work on it.

    :param arg1: description
    :param arg2: description
    :type arg1: type description
    :type arg1: type description
    :return: return description
    :rtype: the return type description

    """

    def __init__(self, **kwargs):
        self.tempdir = None

        super(WorkOnGroup, self).__init__(**kwargs)

        self.repository = "origin"
        self.refspec = "master"

        self._git = None

        if self.workdir is None:
            self.workdir = self.gltcfg.projectdir

        if self.tempdir is None:
            self.tempdir = self.gltcfg.tempdir

        self._git = Git(logger=log)

    @property
    def grouppath(self):
        return os.path.join(self.workdir, self.srcgroupname)

    def setup_group(self):
        try:
            os.makedirs(self.grouppath)

        except OSError:
            pass

    def getprojects(self):

        retv = list()

        for row in super(WorkOnGroup, self).getprojects():
            row["url"] = row.get("ssh_url_to_repo")
            if self.http:
                row["url"] = row.get("http_url_to_repo")

            retv.append(row)
        return retv

    def setup_project(self, row):
        self.setup_group()
        projectpath = os.path.join(self.grouppath, row.get("path"))
        gitconfig = os.path.join(projectpath, ".git", "config")

        if os.path.exists(gitconfig):
            return self.update_project(row)

        else:
            return self.clone_project(row)

    def update_project(self, row):
        projectpath = os.path.join(self.grouppath, row.get("path"))
        log.info("update path %s, START" % projectpath)

        log.debug("  pull last version, START")
        self._git.git("pull", self.repository, self.refspec, "--tags", cwd=projectpath)

        self._git.git("fetch", "--prune", cwd=projectpath)
        log.debug("update path %s, END" % projectpath)

    def clone_project(self, row):
        projectpath = os.path.join(self.grouppath, row.get("path"))
        log.debug("clone path %s" % projectpath)
        self._git.git("clone", row.get("url"), cwd=self.grouppath)

    def main(self):

        for row in self.getprojects():
            self.setup_project(row)
