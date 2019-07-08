"""

.. todo:: finish documenting

"""
import sys
import os
import logging
import copy

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .exceptions import GLToolsException


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

        self.glconfig = PyGitLabConfig()

        self.servername = kwargs.get('servername', self.glconfig.default)
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


class PyGitLabConfig(object):
    """brief explanation

    extended explanation

    :param arg1: description
    :param arg2: description
    :type arg1: type description
    :type arg1: type description
    :return: return description
    :rtype: the return type description

    Example::

      from gltools.config import PyGitLabConfig

      config = PyGitLabConfig()

    """
    def __init__(self, **kwargs):

        self.vars = dict()
        self._args = dict()

        self.globalopts = {'default': 'local',
                           'ssl_verify': 'false',
                           'timeout': 15}
        self.sectionopts = {'url': 'http://localhost',
                            'private_token': 'FIXME',
                            'api_version': 4}

        self.configfile = kwargs.get('configfile',
                                     os.path.expanduser('~/.python-gitlab.cfg'))
        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

        self.config = configparser.RawConfigParser()

        for varname, varval in kwargs.items():
            self._args[varname] = varval
        self.loadconfig()

    @property
    def default(self):
        """return the default section

        :returns: default section
        :rtype: str
        """
        return self.config.get('global', 'default')

    def initconfig(self):
        """initialize an empty conifguration

        """

        if not self.config.has_section('global'):
            self.logger.debug("adding required section 'global'")
            self.config.add_section('global')

        for varname, varval in self.globalopts.items():
            if varname in self._args:
                self.logger.debug(
                    "adding %s (value: %s) to global from arguments" %
                    (varname, self._args[varname]))
                self.config.set('global', varname, self._args[varname])
            else:
                self.logger.debug(
                    "adding %s (value: %s) to global from defaults" %
                    (varname, varval))
                self.config.set('global', varname, varval)

        if not self.config.has_section(self.default):
            self.logger.debug("adding section '%s'" % self.default)
            self.config.add_section(self.default)

        for varname, varval in self.sectionopts.items():
            if varname in self._args:
                self.logger.debug(
                    "adding %s (value: %s) to %s from arguments" %
                    (varname, self._args[varname], self.default))
                self.config.set(self.default, varname, self._args[varname])
            else:
                self.logger.debug(
                    "adding %s (value: %s) to %s from section opts" %
                    (varname, varval, self.default))
                self.config.set(self.default, varname, varval)

    def dump(self):
        """Write the ini file content."""
        self.config.write(sys.stdout)

    def sect_global(self, name, varval):
        """Set a global variable

        :param name: the first value
        :param varval: the first value
        :type name: int, float,...
        :type varval: int, float,...

        Example::

          config.sect_global("ssl_verify", "false")
        """
        self.set('global', name, varval)

    def set(self, *args):
        """short description

        extended description

        :param section: Configuration section
        :param name: Configuration parameter name
        :param value: Configuration parameter value
        :type arg1: str
        :type arg2: str
        :type arg3: str
        """

        if len(args) == 3:
            section = args[0]
            name = args[1]
            varval = args[2]

        elif len(args) == 2:
            section = self.default
            name = args[0]
            varval = args[1]

        tmpdict = self.vars[section, {}]
        tmpdict[name] = varval
        self.vars[section] = tmpdict

    def loadconfig(self):
        """load the content from the configfile. If none exists a dummy will be
        created.

        :raises: GLToolsException if either the existsing configfile cannot be
                 read or the configfile contains dummy data.
        """
        cfgfile = self.configfile

        if not os.path.exists(cfgfile):
            self.initconfig()
            with open(cfgfile, 'w') as cfgh:
                self.config.write(cfgh)
        else:
            if not self.config.read(cfgfile):
                raise GLToolsException("failed to read configfile %s\n" % cfgfile)

        private_token = self.config.get(self.default, 'private_token')
        if private_token == 'FIXME':
            raise GLToolsException(
                "provided configfile %s is not valid, perhaps new?\n" % cfgfile)

    @property
    def configs(self):
        """return available configs
        :returns: list of configurations
        :rtype: list of str
        """
        return [x for x in self.config.sections() if x != 'global']
