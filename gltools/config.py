"""

.. todo:: finish documenting

"""
import sys
import os
import logging
import copy


from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .exceptions import GLToolsException
from .localgitlab import GitLabConfig



class GitLabToolsConfig(object):
    """Provides configuration defaults and overrides for projects.

    :param arg1: description
    :param arg2: description
    :type arg1: type description
    :type arg1: type description
    :return: return description
    :rtype: the return type description

    Example::

      obj = GitLabToolsConfig(servername="local",
                              groupname="homepage")
      print(obj.projectdir)
      >>> /projects/jvzantvoort

      obj = GitLabToolsConfig(servername="local",
                              groupname="derp")
      print(obj.projectdir)
      >>> /home/jvzantvoort/Workspace

    Config example::

      # cat ~/.gltools.cfg
      ---
      local:
        default:
          projectdir: /projects/jvzantvoort
        homepage:
          groupname: homepage
          projectdir: /projects
          exportdir: /staging
      
      proxy:
        default:
          projectdir: /encrypted/proxy


    """

    def __init__(self, **kwargs):
        self.configdata = dict()
        self.cache = dict()
        self._defaults = {'projectdir': os.path.expanduser('~/Workspace'),
                          'exportdir': os.path.expanduser('~/exports'),
                          'tempdir': os.path.expanduser('~/tmp')}

        glconfig = GitLabConfig()

        self.servername = kwargs.get('servername', glconfig.default)
        self.groupname = kwargs.get('groupname')
        self.configfile = kwargs.get('configfile',
                                     os.path.expanduser('~/.gltools.cfg'))
        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

        self.loadconfig()

    def loadconfig(self):
        """load the content from the configfile. If none exists a dummy will be
        created.

        :raises: GLToolsException if either the existsing configfile cannot be
                 read or the configfile contains dummy data.
        """
        if os.path.exists(self.configfile):
            with open(self.configfile) as stream:
                self.configdata = load(stream, Loader=Loader)
        else:
            return

    @property
    def config(self):
        """returns the configuration provided for the servername/groupname
        combination

        """


        if self.cache:
            return self.cache

        tmpdict = self.configdata.get(self.servername, {})

        # setup the defaults
        self.cache = copy.deepcopy(self._defaults)

        if 'default' in tmpdict:
            for k, v in tmpdict['default'].items():
                self.cache[k] = v
        if self.groupname is not None:
            if self.groupname in tmpdict:
                for k, v in tmpdict[self.groupname].items():
                    self.cache[k] = v
        return self.cache

    @property
    def projectdir(self):
        return self.config.get('projectdir')

    @property
    def exportdir(self):
        return self.config.get('exportdir')

    @property
    def tempdir(self):
        return self.config.get('tempdir')

    @property
    def mask(self):
        return self.config.get('mask')


