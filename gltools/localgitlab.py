
import sys
# import os
# import re
# import subprocess
# import logging
# import tempfile
# import base64
# import shutil
try:
    import gitlab

except ImportError:
    sys.exit('python-gitlab module not available')

from .exceptions import GLToolsException

class LocalGitLab(object):

    def __init__(self, **kwargs):

        self.section = "local"
        self.groupname = "default"
        props = ('section', 'groupname')
        for prop in props:
            if prop in kwargs:
                setattr(self, prop, kwargs[prop])
        self._gitlab = gitlab.Gitlab.from_config(self.section)
        self._groups = list()

    @property
    def groups(self):
        if self._groups:
            return self._groups

        for obj in self._gitlab.groups.list(all=True):
            self._groups.append(obj)

        return self._groups

    @property
    def groupnames(self):
        retv = list()
        for group in self.groups:
            retv.append(group.name)
        return sorted(retv)

    @staticmethod
    def _proxy_url(url):
        # Gotta love incositent fqdn's
        return url.replace('gitlab.mst.proxy.nl', 'gitlab.proxy.nl')

    def getproj(self, project):
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
