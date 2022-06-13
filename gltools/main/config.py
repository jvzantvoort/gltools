#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.projects"""

import sys
import os
import logging
from gltools.main.common import Main
from gltools.localgitlab import QueryGitLab, GitLabInitConfig

log = logging.getLogger("gltools.projects")

__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"


class InitConfig(Main):
    def __init__(self, **kwargs):
        super(InitConfig, self).__init__(**kwargs)

    def main(self):
        self._gltinitconfig = GitLabInitConfig()

        configfile = self._gltinitconfig.configfile

        if os.path.exists(configfile):
            raise SystemExit("file exists %s" % configfile)

        self._gltinitconfig()
