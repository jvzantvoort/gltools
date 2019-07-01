"""

.. todo:: finish documenting

"""
import re
import os
import subprocess
import logging

class Git(object):

    def __init__(self):
        self._topdir = None
        self._path = None
        self._remote_origin_url = None

    @property
    def topdir(self):
        if self._topdir:
            return self._topdir

        topleveldata = self.git("rev-parse", "--show-toplevel")
        self._topdir = topleveldata[0]
        return self._topdir

    @property
    def remote_origin_url(self):
        if self._remote_origin_url:
            return self._remote_origin_url

        topleveldata = self.git("config", "--get", "remote.origin.url")
        self._remote_origin_url = topleveldata[0]
        return self._remote_origin_url

    @property
    def exploded_url(self):
        """

        .. todo:: patterns are not done yet
        """
        pattern_ssh = re.compile(r"^(?P<user>.*?)@(?P<hostname>.*):(?P<path>.*)$")
        pattern_http = re.compile(r"^(https|http)://(?P<hostname>.*?)/(?P<path>.*)$")
        match_ssh = pattern_ssh.match(self.remote_origin_url)
        match_http = pattern_http.match(self.remote_origin_url)
        if match_ssh is not None:
            data = match_ssh.groupdict()
        elif match_http is not None:
            data = match_http.groupdict()
        return data

    @property
    def path(self):
        if self._path:
            return self._path
        path = os.environ["PATH"].split(os.pathsep)
        path = [os.path.expanduser(x) for x in path]
        path = [os.path.abspath(x) for x in path]
        path = [x for x in path if os.path.exists(x)]
        self._path = path
        return self._path

    def which(self, executeable):
        for path in self.path:
            executeable_path = os.path.join(path, executeable)
            if os.path.exists(executeable_path):
                if os.access(executeable_path, os.X_OK):
                    return os.path.join(path, executeable)

        return executeable

    def git(self, *args):
        retv = list()
        command = list()
        command.append(self.which('git'))
        [command.append(x) for x in args]

        process = subprocess.Popen(command,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE
                                  )
        stdoutdata = process.communicate()[0]
        if len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                logging.debug(line)
                retv.append(line)
        returncode = process.returncode

        if returncode != 0:
            raise IOError(retv[0])
        return retv
