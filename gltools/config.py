"""

.. todo:: finish documenting

"""
import sys
import os
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from .exceptions import GLToolsException

class Config(object):
    """brief explanation

    extended explanation

    :param arg1: description
    :param arg2: description
    :type arg1: type description
    :type arg1: type description
    :return: return description
    :rtype: the return type description

    Example::

      from gltools.config import Config

      config = Config()

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

        self.config = configparser.RawConfigParser()

        for k, v in kwargs.items():
            self._args[k] = v
        self.loadconfig()

    @property
    def default(self):
        """short description

        extended description

        :param arg1: the first value
        :param arg2: the first value
        :param arg3: the first value
        :type arg1: int, float,...
        :type arg2: int, float,...
        :type arg3: int, float,...
        :returns: arg1/arg2 +arg3
        :rtype: int, float

        Example::

          lala

        .. note:: can be useful to emphasize
            important feature
        .. seealso:: :class:
        .. warning:: arg2 must be non-zero.
        .. todo:: check that arg2 is non zero.
        """
        return self.config.get('global', 'default')

    def initconfig(self):
        """short description

        extended description

        :param arg1: the first value
        :param arg2: the first value
        :param arg3: the first value
        :type arg1: int, float,...
        :type arg2: int, float,...
        :type arg3: int, float,...
        :returns: arg1/arg2 +arg3
        :rtype: int, float

        Example::

          lala

        .. note:: can be useful to emphasize
            important feature
        .. seealso:: :class:
        .. warning:: arg2 must be non-zero.
        .. todo:: check that arg2 is non zero.
        """

        if not self.config.has_section('global'):
            self.config.add_section('global')

        for k, v in self.globalopts.items():
            if k in self._args:
                self.config.set('global', k, kwargs[k])
            else:
                self.config.set('global', k, v)

        if not self.config.has_section(self.default):
            self.config.add_section(self.default)

        for k, v in self.sectionopts.items():
            if k in self._args:
                self.config.set(self.default, k, kwargs[k])
            else:
                self.config.set(self.default, k, v)

    def dump(self):
        """short description

        extended description

        :param arg1: the first value
        :param arg2: the first value
        :param arg3: the first value
        :type arg1: int, float,...
        :type arg2: int, float,...
        :type arg3: int, float,...
        :returns: arg1/arg2 +arg3
        :rtype: int, float

        Example::

          lala

        .. note:: can be useful to emphasize
            important feature
        .. seealso:: :class:
        .. warning:: arg2 must be non-zero.
        .. todo:: check that arg2 is non zero.
        """
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
            raise GLToolsException("provided configfile %s is not valid, perhaps new?\n" % cfgfile)

    @property
    def configs(self):
        """return available configs
        :returns: list of configurations
        :rtype: list of str
        """
        return [x for x in self.config.sections() if x != 'global']
