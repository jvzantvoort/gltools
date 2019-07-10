#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""workongroup.py - $description


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
import logging
from gltools.config import GitLabToolsConfig
from gltools.main.common import Main
from gltools.git import Git


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
        props = ("GITLAB", "GROUPNAME", "WORKDIR", "HTTP", "EXTENDED")

        self._lgitlab = None
        self._git = None

        self.gitlab = None
        self.groupname = None
        self.workdir = None
        self.http = False
        self.extended = False
        self.bundles = False

        self.repository = "origin"
        self.refspec = "master"

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self._gltcfg = GitLabToolsConfig(servername=self.gitlab,
                                         groupname=self.groupname)
        self.maskpatterns = list()

        if self.workdir is None:
            self.workdir = self._gltcfg.projectdir
        self.tempdir = self._gltcfg.tempdir

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))
        self._git = Git(logger=self.logger)

    @property
    def grouppath(self):
        return os.path.join(self.workdir, self.groupname)

    def setup_group(self):
        try:
            os.makedirs(self.grouppath)

        except OSError:
            pass

    def getprojects(self):

        retv = list()

        for row in super(WorkOnGroup, self).getprojects():
            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)
        return retv

    def setup_project(self, row):
        self.setup_group()
        projectpath = os.path.join(self.grouppath, row.get('path'))
        gitconfig = os.path.join(projectpath, '.git', 'config')

        if os.path.exists(gitconfig):
            return self.update_project(row)

        else:
            return self.clone_project(row)

    def update_project(self, row):
        projectpath = os.path.join(self.grouppath, row.get('path'))
        self.logger.info("update path %s, START" % projectpath)

        self.logger.debug("  pull last version, START")
        self._git.git("pull", self.repository, self.refspec, "--tags",
                      cwd=projectpath)

        self._git.git("fetch", "--prune", cwd=projectpath)
        self.logger.debug("update path %s, END" % projectpath)

    def clone_project(self, row):
        projectpath = os.path.join(self.grouppath, row.get('path'))
        self.logger.debug("clone path %s" % projectpath)
        self._git.git("clone", row.get('url'), cwd=self.grouppath)

    def main(self):

        for row in self.getprojects():
            self.setup_project(row)
