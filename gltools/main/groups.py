#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.groups """

import sys
import os
import logging
from gltools.main.common import Main
from gltools.localgitlab import QueryGitLab
from gltools.exceptions import GLToolsException

log = logging.getLogger("gltools.main.groups")

__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"


class ListGroups(Main):
    """List the groups on the gitlab server

    :param gitlab_config_section: section in the python-gitlab configuration
                                  file.
    :param logger: logging object if any
    :type arg1: str
    :type arg1: class
    """

    def __init__(self, **kwargs):
        super(ListGroups, self).__init__(**kwargs)

    def main(self):
        if self.terse:
            for groupname in self.gitlab.tersegroupnames:
                print(groupname)

        else:
            for groupname in self.gitlab.groupnames:
                print(groupname)
