"""This module handles the gitlab interactions."""


from __future__ import print_function
import re
import os
import logging
import pprint

from gltools.exceptions import GLToolsException, GLToolsConfigException

log = logging.getLogger('gltools.localgitlab')

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

CONFIGFILE = os.path.expanduser('~/.python-gitlab.cfg')

class GitLabInitConfig(object):
    """brief explanation

    extended explanation

    :param arg1: description
    :param arg2: description
    :type arg1: type description
    :type arg1: type description
    :return: return description
    :rtype: the return type description

    Example::

      initconfig = GitLabInitConfig()
      initconfig()

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

        self.configfile = kwargs.get('configfile', CONFIGFILE)


        self.config = configparser.RawConfigParser()

        for varname, varval in kwargs.items():
            self._args[varname] = varval

    @property
    def default(self):
        """return the default section

        :returns: default section
        :rtype: str
        """
        return self.config.get('global', 'default')

    def set(self, *args):
        """set a variable in the config

        :param section: Configuration section (defaults to the default section)
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
        """initialize an empty conifguration"""

        if not self.config.has_section('global'):
            log.debug("adding required section 'global'")
            self.config.add_section('global')

        for varname, varval in self.globalopts.items():
            if varname in self._args:
                log.debug(
                    "adding %s (value: %s) to global from arguments" %
                    (varname, self._args[varname]))
                self.config.set('global', varname, self._args[varname])
            else:
                log.debug(
                    "adding %s (value: %s) to global from defaults" %
                    (varname, varval))
                self.config.set('global', varname, varval)

        if not self.config.has_section(self.default):
            log.debug("adding section '%s'" % self.default)
            self.config.add_section(self.default)

        for varname, varval in self.sectionopts.items():
            if varname in self._args:
                log.debug(
                    "adding %s (value: %s) to %s from arguments" %
                    (varname, self._args[varname], self.default))
                self.config.set(self.default, varname, self._args[varname])
            else:
                log.debug(
                    "adding %s (value: %s) to %s from section opts" %
                    (varname, varval, self.default))
                self.config.set(self.default, varname, varval)

    def __call__(self):
        self.initconfig()
        with open(self.configfile, 'w') as cfgh:
            self.config.write(cfgh)

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

        self.configfile = CONFIGFILE

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

    def loadconfig(self):
        """load the content from the configfile. If none exists a dummy will be
        created.

        :raises: GLToolsException if either the existsing configfile cannot be
                 read or the configfile contains dummy data.
        """

        if not os.path.exists(self.configfile):
            raise GLToolsConfigException("required configfile %s does not exist" % self.configfile)

        if not self.config.read(self.configfile):
            raise GLToolsConfigException("failed to read configfile %s\n" % self.configfile)

        private_token = self.config.get(self.default, 'private_token')

        if private_token == 'FIXME':
            raise GLToolsConfigException(
                "provided configfile %s is not valid, perhaps new?\n" % self.configfile)

    @property
    def configs(self):
        """return available configs
        :returns: list of configurations
        :rtype: list of str
        """
        return [x for x in self.config.sections() if x != 'global']

    def has_section(self, section):
        return self.config.has_section(section)

class QueryGitLab(object):
    """Wrapper for the ``gitlab`` library

    :param configname:
    :param groupname: description

    :type configname: str
    :type groupname: str


    Example::

      from gltools.localgitlab import QueryGitLab
      obj = QueryGitLab()
    """

    def __init__(self, **kwargs):

        self._configname = "local"
        self._groupname = None
        self._groupid = None
        self._groups = list()
        self._gitlab = None
        self.config = GitLabConfig()

        props = ('configname', 'groupname')
        for prop in props:
            pname = "_" + prop
            if prop in kwargs:
                setattr(self, pname, kwargs[prop])


    def connect(self, configname):
        """(re)connect to server and refresh the groups list"""
        log.debug('connect to %s, start' % configname)
        self._gitlab = gitlab.Gitlab.from_config(self.configname)
        self._groups = [grp for grp in self.gitlab.groups.list(all=True)]
        log.debug('connect to %s, end' % configname)

    # used
    @property
    def gitlab(self):
        if self._gitlab is None:
            self.connect(self.configname)
        return self._gitlab

    # used
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

    # exposed
    def check_gitlab_group(self, groupname):
        """Checks whether the configured groupname exists on the server.

        :returns: True if groupname is available in the server, False if not
        :rtype: bool
        """
        groups = self.gitlab.getgroup(groupname)
        if not groups:
            return False
        else:
            return True

    @property
    def groupname(self):
        """The name of the gitlab group used."""
        return self._groupname

    @groupname.setter
    def groupname(self, varval):
        if not self.check_gitlab_group(varval):
            raise GLToolsException("%s is an invalid groupname" % varval)
        self._groupname = varval
        return self._groupname

    @property
    def configname(self):
        """The name of the gitlab server definition used."""
        if self._configname is None:
            self.configname = self.config.default
        return self._configname

    @configname.setter
    def configname(self, varval):
        if not self.check_servername(varval):
            raise GLToolsException("%s is an invalid configname" % varval)
        self._configname = varval

        # reset the connection if the variable changes
        self._gitlab = gitlab.Gitlab.from_config(self._configname)

    @property
    def groups(self):
        """return the gitlab group objects visible to the user"""

        # this should already have been loaded by connect
        if self._groups:
            return self._groups

        self._groups = self.gitlab.groups.list(all=True)

        return self._groups

    @property
    def groupnames(self):
        """return the gitlab group names visible to the user"""
        retv = list()
        for groupsect in self.groups:
            if groupsect.name != groupsect.path:
                retv.append("%s (%s)" % (groupsect.name, groupsect.path))
            else:
                retv.append("%s" % groupsect.name)
        return sorted(retv)

    @staticmethod
    def getprojectmeta(project):
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
        retv['description'] = attributes.get('description')
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

    def projects(self, groupname):
        """List the projects in ``groupname``.

        :param groupname: name of the group
        :type groupname: str
        """
        retv = list()
        log.debug('lookup projects for %s' % groupname)
        obj = self.getgroup(groupname)
        if obj is None:
            raise GLToolsException("Could not find group %s" % groupname)

        for project in obj.projects.list(all=True):
            retv.append(self.getprojectmeta(project))
        return retv

class MirrorGitLab(object):
    """Wrapper for the ``gitlab`` library

    Example::

      from gltools.localgitlab import MirrorGitLab
      lgl = MirrorGitLab()
      lgl.source = 'configname'
      lgl.destination = 'configname'


    """

    def __init__(self, *args, **kwargs):

        self.config = GitLabConfig()
        self.defaultserver = self.config.default
        self.gitlab = dict()
        self._source = self.defaultserver
        self._destination = self.defaultserver

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, servername):
        if not self.config.has_section(servername):
            raise GLToolsConfigException("config %s not found" % servername)
        self._source = servername
        return self._source

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, servername):
        if not self.config.has_section(servername):
            raise GLToolsConfigException("config %s not found" % servername)
        self._destination = servername
        return self._destination

    def connect(self, servername):
        if servername in self.gitlab:
            return self.gitlab[servername]

        if servername not in self.config.configs:
            raise GLToolsConfigException("config %s not found" % servername)

        log.debug("connect to %s" % servername)

        self.gitlab[servername] = gitlab.Gitlab.from_config(servername)
        return self.gitlab[servername]

    def get_group_obj(self, servername, groupname):
        connection = self.connect(servername)
        objects = connection.groups.list(search=groupname)

        if len(objects) == 0:
            return None

        if len(objects) == 1:
            return objects[0]

        raise GLToolsException("search for %s in %s yields multiple results" %
                               (groupname, servername))

    def mirror_to_local(self, src_group, basedir):
        srcgrpobj = self.get_group_obj(self.source, src_group)
        retv = list()

        for srcproj in srcgrpobj.projects.list(all=True):
            tmpproj = {'namespace_id': srcgrpobj.id, 'basedir': basedir}

            for keyn in ['description', 'group_id', 'http_url_to_repo', 'id',
                         'name', 'name_with_namespace', 'path',
                         'path_with_namespace', 'ssh_url_to_repo']:
                tmpproj[keyn] = srcproj.attributes.get(keyn)

            retv.append(tmpproj)

        return retv


    def mirror_groups(self, src_group, dst_group):
        srcgrpobj = self.get_group_obj(self.source, src_group)
        dstgrpobj = self.get_group_obj(self.destination, dst_group)
        dstconn = gitlab.Gitlab.from_config(self.destination)
        srcprojs = srcgrpobj.projects.list(all=True)
        projects = list()
        srcurls = dict()
        retv = list()

        for srcproj in srcprojs:
            project = dict()
            path = srcproj.attributes.get('path')
            name = srcproj.attributes.get('name')
            url = srcproj.attributes.get('ssh_url_to_repo')
            project['name'] = name
            project['path'] = path
            project['description'] = srcproj.attributes.get('description')
            project['namespace_id'] = dstgrpobj.id
            projects.append(project)
            srcurls[path] = url

        log.info("create remote projects, start")

        for projectdef in projects:
            try:
                project = dstconn.projects.create(projectdef)

            except gitlab.exceptions.GitlabCreateError as err:
                try:
                    message = " ".join(err.error_message['name'])

                except IndexError:
                    message = err

                except KeyError:
                    message = err

                projectdef['error'] = message
                log.warn("failed to create %(name)s: %(error)s" % projectdef)

        log.info("create remote projects, end")

        log.info("reload remote project configuration, start")
        dstgrpobj = self.get_group_obj(self.destination, dst_group)

        for dstproj in dstgrpobj.projects.list(all=True):
            tmpdict = dict()
            for keyn in ['description', 'group_id', 'http_url_to_repo', 'id',
                         'name', 'name_with_namespace', 'path',
                         'path_with_namespace', 'ssh_url_to_repo']:
                tmpdict[keyn] = dstproj.attributes.get(keyn)

            path = tmpdict.get('path')
            tmpdict['src_ssh_url_to_repo'] = srcurls.get(path)

            retv.append(tmpdict)
        log.info("reload remote project configuration, end")

        return retv
