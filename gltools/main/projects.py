#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gltools.main.projects"""

import sys
import os
import logging
from gltools.main.common import Main

log = logging.getLogger('gltools.projects')

__author__ = "John van Zantvoort"
__copyright__ = "Proxy B.V."
__email__ = "john.van.zantvoort@proxy.nl"

class ListProjects(Main):

    def __init__(self, **kwargs):
        super(ListProjects, self).__init__(**kwargs)
        self.description_max_lenght = 40

    def tabulate(self, legend, rows):
        lengths = dict()
        fmt = str()
        srows = list()

        for row in rows:
            tmpdict = dict()
            for keyn in row.keys():
                keyv = str(row.get(keyn, ''))
                if keyv == 'None':
                    keyv = ''
                if keyn == 'description':
                    keyv = keyv.replace('\n', ' ')
                    if len(keyv) >= self.description_max_lenght:
                        n = self.description_max_lenght -4
                        keyv = keyv[:n] + " ..."

                tmpdict[keyn] = keyv

                keyl = len(str(keyv))
                lkeyl = lengths.get(keyn, 1)
                lengths[keyn] = max(lkeyl, keyl)

            srows.append(tmpdict)

        for keyn in legend:
            fmt += "%%(%s)-%ds " % (keyn, lengths.get(keyn))
        fmt.strip()
        log.debug(fmt)
        for row in srows:
            print(fmt % row)

    def main(self):
        legend = ['name']
        if not self.terse:
            legend.append('url')
            legend.append('description')

        rows = super(ListProjects, self).getprojects()
        self.tabulate(legend, rows)

