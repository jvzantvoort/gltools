"""

.. todo:: finish documenting

"""
import sys
import os
import logging
import copy

log = logging.getLogger('gltools.config')

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .exceptions import GLToolsException
from .localgitlab import GitLabConfig

GLTCONFIGFILE = os.path.expanduser('~/.gltools.cfg')

class GitLabToolsConfig(object):
    """Provides configuration defaults and overrides for projects.

    :param servername: name or description of the server in question
    :param groupname: name of the group in question
    :param configfile: overrule the ``~/.gltools.cfg`` config file
    :type servername: str
    :type groupname: str
    :type configfile: str

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
          projectdir: /scratch/jvzantvoort
          exportdir: /scratch/jvzantvoort/exports
          tempdir: /scratch/jvzantvoort/temp
        common:
          protected: true

        homenet:
          projectdir: /projects
          exportdir: /staging
          mask:
            - "^role-.*$"
      
      proxy:
        default:
          projectdir: /encrypted/proxy
    """

    def __init__(self, **kwargs):
        self.configdata = dict()
        self._cache = dict()
        self._defaults = {'projectdir': os.path.expanduser('~/Workspace'),
                          'exportdir': os.path.expanduser('~/exports'),
                          'tempdir': os.path.expanduser('~/tmp'),
                          'protected': False}


        self.servername = kwargs.get('servername', self.glconfig_default())
        self.groupname = kwargs.get('groupname')
        self.configfile = kwargs.get('configfile', GLTCONFIGFILE)

        self.loadconfig()

    @staticmethod
    def glconfig_default():
        retv = 'local'
        try:
            glc = GitLabConfig()
            retv = glc.default
        except GLToolsConfigException:
            pass
        return retv

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
        combination."""
        if self._cache:
            return self._cache

        tmpdict = self.configdata.get(self.servername, {})

        # setup the defaults
        self._cache = copy.deepcopy(self._defaults)

        if 'default' in tmpdict:
            for k, v in tmpdict['default'].items():
                self._cache[k] = v
        if self.groupname is not None:
            if self.groupname in tmpdict:
                for k, v in tmpdict[self.groupname].items():
                    self._cache[k] = v
        return self._cache

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

    @property
    def protected(self):
        return self.config.get('protected')

