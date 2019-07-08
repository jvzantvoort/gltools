"""This module handles the gitlab interactions."""


from __future__ import print_function
import os
import logging

from gltools.exceptions import GLToolsException

try:
    import gitlab

except ImportError:
    raise GLToolsException('python-gitlab module not available')

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

__author__ = "John van Zantvoort"
__email__ = "john.van.zantvoort@proxy.nl"
__copyright__ = "John van Zantvoort"
__license__ = "proprietary"
__version__ = "1.0.1"


class GitLabConfig(object):
    """Handle the gitlab config file

    If it doesn't exist a dummy will be created.

    :param arg1: description
    :param arg2: description

    :type arg1: type description
    :type arg1: type description
    :return: return description
    :rtype: the return type description

    Example::

      from gltools.config import GitLabConfig

      config = GitLabConfig()

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

class LocalGitLab(object):
    """Wrapper for the ``gitlab`` library

    :param server:
    :param groupname: description

    :type server: str
    :type groupname: str


    Example::

      from gltools.localgitlab import LocalGitLab
      obj = LocalGitLab()
    """

    def __init__(self, **kwargs):

        self._server = "local"
        self._groupname = "default"
        self._groups = list()
        self._gitlab = None
        self.config = None

        props = ('server', 'groupname')
        for prop in props:
            pname = "_" + prop
            if prop in kwargs:
                setattr(self, pname, kwargs[prop])

        self.loadconfig()

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))


    def check_servername(self, sectionname):
        """Check if the section name is valid

        :param sectionname: name of the section in the ``~/.python-gitlab.cfg`` file
        :type arg1: str
        :returns: True if valid
        :rtype: bool
        """
        if sectionname in self.config.configs:
            return True
        return False


    def loadconfig(self):
        """(re)load the configfile"""
        self.config = GitLabConfig(servername=self.server,
                                   groupname=self.groupname)

    @property
    def groupname(self):
        """The name of the gitlab group used."""
        return self._groupname

    @groupname.setter
    def groupname(self, varval):
        self._groupname = varval
        self.loadconfig()
        return self._groupname

    @property
    def server(self):
        """The name of the gitlab server definition used."""
        return self._server

    @server.setter
    def server(self, varval):
        if not self.check_servername(varval):
            raise GLToolsException("%s is an invalid configname" % varval)
        self._server = varval
        self._gitlab = gitlab.Gitlab.from_config(self._server)
        self.loadconfig()

    @property
    def groups(self):
        """return the gitlab group objects visible to the user"""
        if self._groups:
            return self._groups

        if self._gitlab is None:
            self._gitlab = gitlab.Gitlab.from_config(self.server)

        for obj in self._gitlab.groups.list(all=True):
            self._groups.append(obj)

        return self._groups

    @property
    def groupnames(self):
        """return the gitlab group names visible to the user"""
        retv = list()
        for group in self.groups:
            retv.append(group.name)
        return sorted(retv)

    @staticmethod
    def getproj(project):
        """Translate the provided object in a more useable dictionary.

        Return value descriptions:

        +---------------------+------------------------------------------+
        | Name                | value source                             |
        +=====================+==========================================+
        | group_id            | ``attributes['namespace']['id']``        |
        +---------------------+------------------------------------------+
        | group_name          | ``attributes['namespace']['name']``      |
        +---------------------+------------------------------------------+
        | group_path          | ``attributes['namespace']['full_path']`` |
        +---------------------+------------------------------------------+
        | name                | ``attributes['name']``                   |
        +---------------------+------------------------------------------+
        | id                  | ``attributes['id']``                     |
        +---------------------+------------------------------------------+
        | path                | ``attributes['path']``                   |
        +---------------------+------------------------------------------+
        | path_with_namespace | ``attributes['path_with_namespace']``    |
        +---------------------+------------------------------------------+
        | ssh_url_to_repo     | ``attributes['ssh_url_to_repo']``        |
        +---------------------+------------------------------------------+
        | http_url_to_repo    | ``attributes['http_url_to_repo']``       |
        +---------------------+------------------------------------------+

        :param project: project object
        :type project:
        :rtype: dict

        """
        retv = dict()

        attributes = project.attributes
        namespace = attributes.get('namespace')

        retv['group_id'] = namespace.get('id')
        retv['group_name'] = namespace.get('name')
        retv['group_path'] = namespace.get('full_path')

        retv['name'] = attributes.get('name')
        retv['http_url_to_repo'] = attributes.get('http_url_to_repo')
        retv['id'] = attributes.get('id')
        retv['path'] = attributes.get('path')
        retv['path_with_namespace'] = attributes.get('path_with_namespace')
        retv['ssh_url_to_repo'] = attributes.get('ssh_url_to_repo')
        return retv

    def getgroup(self, groupname):
        """Get a single group object from a list of object based on match
        parameters provided.

        if either the ``full_name``, ``name``, ``full_path`` or ``path`` match
        the provide ``groupname`` string the relevant object is returned.

        :param groupname: name of the relevant group
        :returns: relevant group
        """
        for group in self.groups:
            matches = [group.full_name, group.name, group.full_path, group.path]
            for refstr in matches:
                if groupname == refstr:
                    return group

    def grouptree(self, groupname):
        """

        :param groupname: name of the group
        :type groupname: str
        """
        retv = list()
        obj = self.getgroup(groupname)
        if obj is None:
            raise GLToolsException("Could not find group %s" % groupname)

        for project in obj.projects.list(all=True):
            retv.append(self.getproj(project))
        return retv

if __name__ == '__main__':
    GL = LocalGitLab()
    print(GL.grouptree('homenet'))
