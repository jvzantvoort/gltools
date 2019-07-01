
import sys
import logging

from .exceptions import GLToolsException

try:
    import gitlab

except ImportError:
    raise GLToolsException('python-gitlab module not available')


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

        self.server = "local"
        self.groupname = "default"

        props = ('server', 'groupname')
        for prop in props:
            if prop in kwargs:
                setattr(self, prop, kwargs[prop])
        self._gitlab = gitlab.Gitlab.from_config(self.server)
        self._groups = list()

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

    @property
    def groups(self):
        """return the gitlab group objects visible to the user"""
        if self._groups:
            return self._groups

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
    def _proxy_url(url):
        # Gotta love incositent fqdn's
        return url.replace('gitlab.mst.proxy.nl', 'gitlab.proxy.nl')

    def getproj(self, project):
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
        retv['http_url_to_repo'] = self._proxy_url(attributes.get('http_url_to_repo'))
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
        retv = list()
        obj = self.getgroup(groupname)
        if obj is None:
            raise GLToolsException("Could not find group %s"  % groupname)

        for project in obj.projects.list(all=True):
            retv.append(self.getproj(project))
        return retv
