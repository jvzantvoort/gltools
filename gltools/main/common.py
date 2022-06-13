#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""common.py - $description


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
import re
import os
import tempfile
import logging
import subprocess
from gltools.exceptions import GLToolsException
from gltools.config import GitLabToolsConfig
from gltools.localgitlab import QueryGitLab

log = logging.getLogger("gltools.common")


__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"
__license__ = "proprietary"
__version__ = "1.0.1"


class Main(object):
    """brief explanation

    extended explanation

    :param gitlab_config_section: gitlab configuration section
    :param GROUPNAME: gitlab groupname

    :type gitlab_config_section: string
    :type GROUPNAME: string
    :return: return description
    :rtype: the return type description

    Example::

      obj = Main(gitlab_config_section="local", GROUPNAME="golang")

    """

    def __init__(self, **kwargs):

        # command line options
        self.gitlab_config_section = kwargs.get("gitlab_config_section")
        self.dst_gitlab_config_section = kwargs.get("dst_gitlab_config_section")
        self.srcgroupname = kwargs.get("srcgroupname")
        self.homedir = os.path.expanduser("~")

        self.terse = kwargs.get("terse", False)

        self.http = kwargs.get("http", False)
        self.extended = kwargs.get("extended", False)

        self.bundles = kwargs.get("bundles", False)
        self.dstdirectory = kwargs.get("dstdirectory", self.homedir)
        self.outputdir = kwargs.get("outputdir", "/")

        self.workdir = kwargs.get("workdir")
        self.dstgroupname = kwargs.get("dstgroupname")

        self.tempdir = None
        # container variables
        self._gitlab = None
        self._gltcfg = None
        self._scripttemplate = None

        self._maskpatterns = list()

        if self.gitlab_config_section is None:
            raise GLToolsException("gitlab config section not defined")
        log.debug("gitlab_config_section %s" % self.gitlab_config_section)

    @property
    def gltcfg(self):
        if not self._gltcfg or self._gltcfg is None:
            log.debug("start")
            self._gltcfg = GitLabToolsConfig(
                servername=self.gitlab_config_section, groupname=self.srcgroupname
            )
        return self._gltcfg

    @property
    def gitlab(self):
        if self._gitlab is None:
            log.debug("connect to %s" % self.gitlab_config_section)
            self._gitlab = QueryGitLab(configname=self.gitlab_config_section)
            log.debug("connect to %s, done" % self.gitlab_config_section)
        return self._gitlab

    @property
    def maskpatterns(self):
        if self._maskpatterns:
            return self._maskpatterns

        for pattern in self.gltcfg.mask:
            self._maskpatterns.append(re.compile(pattern))
        return self._maskpatterns

    def check_gitlab_group(self, groupname):
        """Checks whether the configured groupname exists on the server.

        :returns: True if groupname is available in the server, False if not
        :rtype: bool
        """
        return self.gitlab.check_gitlab_group(groupname)

    def ignore_extended(self, row):
        """A filter funtion. If ``self.extended`` is **True** no checks are
        executed and ``False`` is returned.

        If the fields provided in ``row`` match the provided patterns

        :param row: dictionary with variables from
        :type row: dict
        :returns: True if row is ignore-able and False if not.
        :rtype: int, float
        """
        path = row.get("path")

        if self.extended:
            log.debug("is extended")
            return False

        if not self.gltcfg.mask:
            log.debug("no patterns available")
            return False

        for pattern in self.maskpatterns:
            if pattern.match(path):
                log.debug("exclude path: %s" % path)
                return True

        log.debug("include path: %s" % path)
        return False

    def getprojects(self):
        """get a list of projects

        :returns: list of dicts
        :rtype: list

        """

        retv = list()
        log.debug("start")

        for row in self.gitlab.projects(self.srcgroupname):
            log.debug("project: %(name)s" % row)
            if self.ignore_extended(row):
                continue

            row["type"] = "portable"
            if self.bundles:
                row["type"] = "bundle"

            row["url"] = row.get("ssh_url_to_repo")
            if self.http:
                row["url"] = row.get("http_url_to_repo")

            retv.append(row)

        log.debug("end")
        return retv

    def mktemp(self, suffix="_gltools"):

        if self.tempdir is None:
            self.tempdir = self.gltcfg.tempdir

        try:
            os.makedirs(self.tempdir)

        except OSError as err:
            if os.path.isdir(self.tempdir):
                log.debug("%s already exists" % self.tempdir)
            else:
                log.error(err)

        return tempfile.mkdtemp(
            suffix=suffix, prefix=self.srcgroupname + "_", dir=self.tempdir
        )

    def exec_script(self, scriptfile):
        """Execute a scriptfile

        :returns: arg1/arg2 +arg3
        :rtype: int, float

        Example::

          obj.exec_script("somefile.sh")

        """
        retv = list()
        command = list()

        command.append(scriptfile)

        log.debug("  execute %s" % scriptfile)

        process = subprocess.Popen(
            command, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )

        stdoutdata, stderrdata = process.communicate()

        if stdoutdata is not None and len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split("\n"):
                line = line.strip("\n")
                log.debug(">>  %s" % line)
                retv.append(line)

        if stderrdata is not None and len(stderrdata.strip()) > 0:
            for line in stderrdata.split("\n"):
                line = line.strip("\n")
                log.error("!!  %s" % line)

        returncode = process.returncode

        if returncode != 0:
            log.error("  execute %s, failed" % scriptfile)
            raise GLToolsException(retv[0])

        log.debug("  execute %s, success" % scriptfile)
        return retv
