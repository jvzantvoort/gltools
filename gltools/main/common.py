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
import logging
import subprocess
from gltools.exceptions import GLToolsException
from gltools.localgitlab import QueryGitLab


__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"
__license__ = "proprietary"
__version__ = "1.0.1"


class Main(object):
    """brief explanation

    extended explanation

    :param GITLAB: gitlab configuration section
    :param GROUPNAME: gitlab groupname

    :type GITLAB: string
    :type GROUPNAME: string
    :return: return description
    :rtype: the return type description

    Example::

      obj = Main(GITLAB="local", GROUPNAME="golang")

    """

    def __init__(self, **kwargs):
        props = ("GITLAB", "GROUPNAME")

        self._lgitlab = None
        self._gltcfg = None

        self.gitlab = None
        self.groupname = None

        self.extended = False
        self.bundles = False

        self.maskpatterns = list()
        self.http = False

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

        self._scripttemplate = None

    def check_gitlab_group(self, groupname):
        """Checks whether the configured groupname exists on the server.

        :returns: True if groupname is available in the server, False if not
        :rtype: bool
        """

        if self._lgitlab is None:
            self._lgitlab = QueryGitLab(server=self.gitlab)
        return self._lgitlab.check_gitlab_group(groupname)

    def ignore_extended(self, row):
        """A filter funtion. If ``self.extended`` is **True** no checks are
        executed and ``False`` is returned.

        If the fields provided in ``row`` match the provided patterns

        :param row: dictionary with variables from
        :type row: dict
        :returns: True if row is ignore-able and False if not.
        :rtype: int, float
        """
        path = row.get('path')

        if self.extended:
            self.logger.debug("is extended")
            return False

        if not self._gltcfg or self._gltcfg is None:
            raise GLToolsException("GitLabToolsConfig not loaded")

        if not self._gltcfg.mask:
            self.logger.debug("no patterns available")
            return False

        if not self.maskpatterns:
            for pattern in self._gltcfg.mask:
                self.maskpatterns.append(re.compile(pattern))

        for pattern in self.maskpatterns:
            if pattern.match(path):
                self.logger.debug("exclude path: %s" % path)
                return True

        self.logger.debug("include path: %s" % path)
        return False

    def getprojects(self):
        """get a list of projects

        :returns: list of dicts
        :rtype: list

        """

        retv = list()

        if self._lgitlab is None:
            self._lgitlab = QueryGitLab(server=self.gitlab)

        for row in self._lgitlab.projects(self.groupname):
            if self.ignore_extended(row):
                continue

            row['type'] = "portable"
            if self.bundles:
                row['type'] = "bundle"

            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)

        return retv

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

        self.logger.debug("  execute %s" % scriptfile)

        process = subprocess.Popen(command,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)

        stdoutdata, stderrdata = process.communicate()

        if stdoutdata is not None and len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                self.logger.debug(">>  %s" % line)
                retv.append(line)

        if stderrdata is not None and len(stderrdata.strip()) > 0:
            for line in stderrdata.split('\n'):
                line = line.strip('\n')
                self.logger.error("!!  %s" % line)

        returncode = process.returncode

        if returncode != 0:
            self.logger.error("  execute %s, failed" % scriptfile)
            raise GLToolsException(retv[0])

        self.logger.debug("  execute %s, success" % scriptfile)
        return retv
