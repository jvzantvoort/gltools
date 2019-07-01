
import os
import tempfile
import logging
import base64
import shutil
import subprocess
from .localgitlab import LocalGitLab
from .config import Config
from .exceptions import GLToolsException
from .git import Git


class Main(object):
    """brief explanation

    extended explanation

    :param GITLAB: gitlab configuration section
    :param GROUPNAME: gitlab groupname

    :type GITLAB: string
    :type GROUPNAME: string
    :return: return description
    :rtype: the return type description

    Example::

      obj = Main(GITLAB="local", GROUPNAME="golang")

    """

    def __init__(self, **kwargs):
        props = ("GITLAB", "GROUPNAME")

        self._config = None
        self._lgitlab = None

        self.gitlab = None
        self.groupname = None

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

        self._scriptbase64 = kwargs.get('scriptbase64', "")
        self._scripttemplate = None

    def check_gitlab_section(self):
        """Check if the provided ``gitlab`` parameter is valid.

        :returns: True is valid, False if not
        :rtype: boolean

        Example::

          if not obj.check_gitlab_section():
              sys.exit("Invalid config section")

        """

        if self._config is None:
            self._config = Config()

        if self.gitlab is None:
            self.gitlab = self._config.default

        if self.gitlab not in self._config.configs:
            self.logger.error("Invalid config section called. Valid options are:")
            for csect in self._config.configs:
                self.logger.error(" - %s" % csect)
            self.logger.error("     Check %s for more information" % self._config.configfile)
            return False
        return True

    def check_gitlab_group(self):

        if self._lgitlab is None:
            self._lgitlab = LocalGitLab(server=self.gitlab)

        self.group = self._lgitlab.getgroup(self.groupname)

        if not self.group:
            self.logger.error("Invalid group called. Valid options are:")
            for groupsect in self._lgitlab.groups:
                if groupsect.name != groupsect.path:
                    print(" - %s (%s)" % (groupsect.name, groupsect.path))
                else:
                    print(" - %s" % groupsect.name)
            return False
        return True

    def getprojects(self):
        if self._lgitlab is None:
            self._lgitlab = LocalGitLab(server=self.gitlab)

        return self._lgitlab.grouptree(self.groupname)

    def exec_script(self, scriptfile):
        """Execute a scriptfile

        :returns: arg1/arg2 +arg3
        :rtype: int, float

        Example::

          obj.exec_script("somefile.sh")

        .. note:: can be useful to emphasize
            important feature
        .. seealso:: :class:
        .. warning:: arg2 must be non-zero.
        .. todo:: check that arg2 is non zero.
        """
        retv = list()
        command = list()

        command.append(scriptfile)

        self.logger.info("  execute %s" % scriptfile)

        process = subprocess.Popen(command,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)

        stdoutdata, stderrdata = process.communicate()

        if len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                self.logger.debug(">>  %s" % line)
                retv.append(line)

        if len(stderrdata.strip()) > 0:
            for line in stderrdata.split('\n'):
                line = line.strip('\n')
                self.logger.error("!!  %s" % line)

        returncode = process.returncode

        if returncode != 0:
            self.logger.info("  execute %s, failed" % scriptfile)
            raise IOError(retv[0])

        self.logger.info("  execute %s, success" % scriptfile)
        return retv


class WorkOnGroup(Main):

    def __init__(self, **kwargs):
        props = ("GITLAB", "GROUPNAME", "WORKDIR", "HTTP")

        self._config = None
        self._lgitlab = None
        self._git = None

        self.gitlab = None
        self.groupname = None
        self.workdir = None
        self.http = False

        self.repository = "origin"
        self.refspec = "master"

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))
        self._git = Git(logger=self.logger)
        # self._scriptbase64 = kwargs.get('scriptbase64', "")
        # self._scripttemplate = None

    @property
    def grouppath(self):
        return os.path.join(self.workdir, self.groupname)

    def setup_group(self):
        try:
            os.makedirs(self.grouppath)

        except OSError as err:
            pass


    def getprojects(self):

        retv = list()

        for row in super(WorkOnGroup, self).getprojects():
            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)
        return retv

    def setup_project(self, row):
        self.setup_group()
        projectpath = os.path.join(self.grouppath, row.get('path'))
        gitconfig = os.path.join(projectpath, '.git', 'config')

        if os.path.exists(gitconfig):
            return self.update_project(row)

        else:
            return self.clone_project(row)

    def update_project(self, row):
        projectpath = os.path.join(self.grouppath, row.get('path'))
        self.logger.info("update path %s, START" % projectpath)

        self.logger.debug("  pull last version, START")
        self._git.git("pull", self.repository, self.refspec, "--tags", cwd=projectpath)

        self._git.git("fetch", "--prune", cwd=projectpath)
        self.logger.debug("update path %s, END" % projectpath)

    def clone_project(self, row):
        projectpath = os.path.join(self.grouppath, row.get('path'))
        self.logger.debug("clone path %s" % projectpath)
        self._git.git("clone", row.get('url'), cwd=self.grouppath)

    def main(self):

        for row in self.getprojects():
            self.setup_project(row)


class ExportGroup(object):


    def __init__(self, **kwargs):
        props = ("GITLAB", "OUTPUTDIR", "SWLIST", "BUNDLES", "EXTENDED",
                "HTTP", "GROUPNAME")

        self._config = None
        self._lgitlab = None

        self.swlist = False
        self.bundles = False
        self.extended = False
        self.http = False
        self.gitlab = None
        self.outputdir = None
        self.groupname = None

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))
        self._scriptbase64 = kwargs.get('scriptbase64', "")
        self._scripttemplate = None

    def check_gitlab_section(self):
        self._config = Config()

        if self.gitlab is None:
            self.gitlab = self._config.default

        if self.gitlab not in self._config.configs:
            self.logger.error("Invalid config section called. Valid options are:")
            for csect in self._config.configs:
                self.logger.error(" - %s" % csect)
            self.logger.error("     Check %s for more information" % self._config.configfile)
            return False
        return True

    def check_gitlab_group(self):

        self._lgitlab = LocalGitLab(server=self.gitlab)

        self.group = self._lgitlab.getgroup(self.groupname)

        if not self.group:
            self.logger.error("Invalid group called. Valid options are:")
            for groupsect in self._lgitlab.groups:
                if groupsect.name != groupsect.path:
                    print(" - %s (%s)" % (groupsect.name, groupsect.path))
                else:
                    print(" - %s" % groupsect.name)
            return False
        return True

    def getprojects(self):
        retv = list()

        for row in self._lgitlab.grouptree(self.groupname):
            row['type'] = "portable"
            if self.bundles:
                row['type'] = "bundle"

            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)
        return retv

    def exec_script(self, scriptfile):
        retv = list()
        command = [scriptfile]
        self.logger.info("  execute %s" % scriptfile)
        process = subprocess.Popen(command,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)
        stdoutdata = process.communicate()[0]
        if len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                self.logger.debug(line)
                retv.append(line)
        returncode = process.returncode

        if returncode != 0:
            self.logger.info("  execute %s, failed" % scriptfile)
            raise IOError(retv[0])

        self.logger.info("  execute %s, success" % scriptfile)
        return retv

    def export_project(self, row, outputdir, tempdir):
        row['outputdir'] = outputdir
        row['tempdir'] = tempdir
        if not self._scripttemplate:
            self._scripttemplate = base64.b64decode(self._scriptbase64)

        self.logger.info("export %(name)s, start" % row)
        scriptname = "%(group_path)s_%(name)s.sh" % row
        scriptname = scriptname.lower().replace(' ', '_')
        outfile = os.path.join(tempdir, scriptname)
        self.logger.debug("  wrote scriptfile: %s" % outfile)
        with open(outfile, "w") as ofh:
            ofh.write(self._scripttemplate % row)
        os.chmod(outfile, 493)
        self.exec_script(outfile)
        os.unlink(outfile)
        self.logger.info("export %(name)s, end" % row)

    def main(self):
        print(self.outputdir)
        print(self.groupname)
        tempdir = os.path.join(self.outputdir, "tmp")
        try:
            os.makedirs(tempdir)

        except OSError as err:
            print(err)
            pass

        tempdir = tempfile.mkdtemp(suffix='_export',
                                   prefix=self.groupname + "_",
                                   dir=tempdir)

        for row in self.getprojects():
            self.export_project(row, self.outputdir, tempdir)
