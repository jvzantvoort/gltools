import re
import os
import subprocess
import logging

from .exceptions import GLToolsException


class Git(object):

    def __init__(self, **kwargs):
        self._topdir = None
        self._path = None
        self._remote_origin_url = None
        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

    @property
    def topdir(self):
        """returns the top most directory of the git project

        :rtype: str

        .. note:: uses the current working directory
        """
        if self._topdir:
            return self._topdir

        topleveldata = self.git("rev-parse", "--show-toplevel")
        self._topdir = topleveldata[0]
        return self._topdir

    @property
    def remote_origin_url(self):
        """returns the remote url of the project

        :rtype: str

        .. note:: uses the current working directory
        """
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
        """return the content of the ``PATH`` variable as a list"""
        if self._path:
            return self._path
        path = os.environ["PATH"].split(os.pathsep)
        path = [os.path.expanduser(x) for x in path]
        path = [os.path.abspath(x) for x in path]
        path = [x for x in path if os.path.exists(x)]
        self._path = path
        return self._path

    def which(self, executeable):
        """get the full path of a command

        :param executeable: the first value
        :type executeable: int, float,...
        :returns: full path of the command or None
        :rtype: str
        """
        for path in self.path:
            executeable_path = os.path.join(path, executeable)
            if os.path.exists(executeable_path):
                if os.access(executeable_path, os.X_OK):
                    return os.path.join(path, executeable)

        return executeable

    def git(self, *args, **kwargs):
        """wrapper for the ``git`` command

        :param args: arguments for the command
        :param kwargs: extra options
        :type args: list of strings
        :type kwargs: dict
        :returns: stdout lines as a list if sucessful
        :rtype: list
        :raise: GLToolsException on fail
        """
        retv = list()
        command = list()
        command.append(self.which('git'))
        # pylint: disable=W0106
        [command.append(x) for x in args]
        # pylint: enable=W0106

        cmd_args = {'stderr': subprocess.STDOUT, 'stdout': subprocess.PIPE}
        for kname, kvalue in kwargs.items():
            cmd_args[kname] = kvalue

        process = subprocess.Popen(command, **cmd_args)
        stdoutdata, stderrdata = process.communicate()
        if len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                self.logger.debug(line)
                retv.append(line)
        returncode = process.returncode

        if returncode == 0:
            return retv

        raise GLToolsException("%s\n\n%s" % (stderrdata, stdoutdata))
