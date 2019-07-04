
import os
import tempfile
import logging
import base64
from .localgitlab import LocalGitLab
from .config import Config
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

        self.extended = False
        self.bundles = False

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
        """Checks whether the configured groupname exists on the server.

        :returns: True if groupname is available in the server, False if not
        :rtype: bool
        """

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

    def ignore_extended(self, row):
        """A filter funtion. If ``self.extended`` is **True** no checks are
        executed and ``False`` is returned.

        If the fields provided in ``row`` match the provided patterns 

        :param row: dictionary with variables from 
        :type row: dict
        :returns: True if row is ignore-able and False if not.
        :rtype: int, float
        """
        path = row.get('path')

        if self.extended:
            self.logger.debug("is extended")
            return False

        if path.startswith('role-'):
            self.logger.debug("exclude path: %s" % path)
            return True

        self.logger.debug("include path: %s" % path)
        return False

    def getprojects(self):

        retv = list()

        if self._lgitlab is None:
            self._lgitlab = LocalGitLab(server=self.gitlab)

        for row in self._lgitlab.grouptree(self.groupname):
            if self.ignore_extended(row):
                continue

            row['type'] = "portable"
            if self.bundles:
                row['type'] = "bundle"

            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)

        return retv

    def exec_script(self, scriptfile):
        """Execute a scriptfile

        :returns: arg1/arg2 +arg3
        :rtype: int, float

        Example::

          obj.exec_script("somefile.sh")

        """
        retv = list()
        command = list()

        command.append(scriptfile)

        self.logger.debug("  execute %s" % scriptfile)

        process = subprocess.Popen(command,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)

        stdoutdata, stderrdata = process.communicate()

        if stdoutdata is not None and len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                self.logger.debug(">>  %s" % line)
                retv.append(line)

        if stderrdata is not None and len(stderrdata.strip()) > 0:
            for line in stderrdata.split('\n'):
                line = line.strip('\n')
                self.logger.error("!!  %s" % line)

        returncode = process.returncode

        if returncode != 0:
            self.logger.error("  execute %s, failed" % scriptfile)
            raise IOError(retv[0])

        self.logger.debug("  execute %s, success" % scriptfile)
        return retv


class WorkOnGroup(Main):

    def __init__(self, **kwargs):
        props = ("GITLAB", "GROUPNAME", "WORKDIR", "HTTP", "EXTENDED")

        self._config = None
        self._lgitlab = None
        self._git = None

        self.gitlab = None
        self.groupname = None
        self.workdir = None
        self.http = False
        self.extended = False
        self.bundles = False

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

        except OSError:
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


class ExportGroup(Main):

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
        self._scriptbase64 = """
IyEvYmluL2Jhc2gKZGVjbGFyZSAtciBTQ1JJUFRQQVRIPSIkKHJlYWRsaW5rIC1mICQwKSIKZGVj
bGFyZSAtciBTQ1JJUFROQU1FPSIkKGJhc2VuYW1lICRTQ1JJUFRQQVRIIC5zaCkiCmRlY2xhcmUg
LXIgU0NSSVBURElSPSIkKGRpcm5hbWUgJFNDUklQVFBBVEgpIgpkZWNsYXJlIC1yIEdST1VQX05B
TUU9IiUoZ3JvdXBfbmFtZSlzIgpkZWNsYXJlIC1yIEdST1VQX1BBVEg9IiUoZ3JvdXBfcGF0aClz
IgpkZWNsYXJlIC1yIFRZUEU9IiUodHlwZSlzIgpkZWNsYXJlIC1yIE5BTUU9IiUobmFtZSlzIgpk
ZWNsYXJlIC1yIFhQQVRIPSIlKHBhdGgpcyIKZGVjbGFyZSAtciBQQVRIX1dJVEhfTkFNRVNQQUNF
PSIlKHBhdGhfd2l0aF9uYW1lc3BhY2UpcyIKZGVjbGFyZSAtciBVUkw9IiUodXJsKXMiCmRlY2xh
cmUgLXIgT1VUUFVURElSPSIlKG91dHB1dGRpcilzLyUoZ3JvdXBfcGF0aClzIgpkZWNsYXJlIC1y
IFRFTVBESVI9IiUodGVtcGRpcilzLyUoZ3JvdXBfcGF0aClzIgpkZWNsYXJlIC1yIE9VVFBVVEZJ
TEU9IiUob3V0cHV0ZGlyKXMvJShncm91cF9wYXRoKXMvJShwYXRoKXMiCgpSRVBPRElSPSQoYmFz
ZW5hbWUgIiR7VVJMfSIgLmdpdCkKCmZ1bmN0aW9uIG1rYnVuZGxlKCkKewogIGxvY2FsIG91dHB1
dGZpbGU9JDE7IHNoaWZ0CiAgZ2l0IGJ1bmRsZSBjcmVhdGUgJHtvdXRwdXRmaWxlfSBtYXN0ZXIK
ICBSRVRWPSQ/CiAgW1sgIiR7UkVUVn0iID0gIjAiIF1dICYmIHJldHVybiAwCiAgZWNobyAiZXhp
dCBjb2RlOiAke1JFVFZ9IgogIGV4aXQgNwp9CgpmdW5jdGlvbiBhcmNoaXZlKCkKewogIGxvY2Fs
IHBhdGg9JDE7IHNoaWZ0CiAgbG9jYWwgdGVtcGRpcj0iJHtURU1QRElSfS9hcmNoaXZlIgogIG1r
ZGlyIC1wICIke3RlbXBkaXJ9IgoKICBnaXQgYXJjaGl2ZSAtLXByZWZpeD0ke3BhdGh9LyBIRUFE
IHwgdGFyIC14ZiAtIC1DICIke3RlbXBkaXJ9IgoKICBpbnN0YWxsX3JvbGVzICIke3RlbXBkaXJ9
LyR7cGF0aH0iCgogIGlmIHJzeW5jIC1hIC0tZGVsZXRlICIke3RlbXBkaXJ9LyR7cGF0aH0vIiAi
JHtPVVRQVVRGSUxFfS8iCiAgdGhlbgogICAgcmV0dXJuIDAKICBlbHNlCiAgICBleGl0IDEwCiAg
ZmkKCn0KCmZ1bmN0aW9uIGluc3RhbGxfcm9sZXMoKQp7CiAgbG9jYWwgYXJjaGRpcj0kMTsgc2hp
ZnQKICBbWyAtZSAiJHthcmNoZGlyfS9yb2xlcy9yZXF1aXJlbWVudHMueW1sIiBdXSB8fCByZXR1
cm4gMAogIGFuc2libGUtZ2FsYXh5IGluc3RhbGwgLXIgIiR7YXJjaGRpcn0vcm9sZXMvcmVxdWly
ZW1lbnRzLnltbCIgLXAgIiR7YXJjaGRpcn0vcm9sZXMiCn0KCgpta2RpciAtcCAiJHtPVVRQVVRE
SVJ9IiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgfHwgZXhpdCAxCm1rZGly
IC1wICIke1RFTVBESVJ9IiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB8
fCBleGl0IDIKCnB1c2hkICIke1RFTVBESVJ9IiAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
ICAgICAgICAgICAgICB8fCBleGl0IDMKCmVjaG8gIkNsb25pbmcgJHtOQU1FfSIgICAgICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICB8fCBleGl0IDQKZ2l0IGNsb25lICIke1VSTH0i
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHx8IGV4aXQgNQoKcHVz
aGQgIiR7UkVQT0RJUn0iICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
IHx8IGV4aXQgNgoKY2FzZSAkVFlQRSBpbiAKICBidW5kbGUpIG1rYnVuZGxlICIke09VVFBVVEZJ
TEV9LmJ1bmRsZSI7OwogIHBvcnRhYmxlKSBhcmNoaXZlICIke1hQQVRIfSI7OwogICopIGVjaG8g
ImZhaWxlZCB0byBoYW5kbGUgJFRZUEUiOyBleGl0IDggOzsKZXNhYwoKcG9wZApwb3BkCg==
"""

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))
        self._scripttemplate = None

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

    def getprojects(self):

        retv = list()

        for row in super(ExportGroup, self).getprojects():

            row['type'] = "portable"
            if self.bundles:
                row['type'] = "bundle"

            row['url'] = row.get('ssh_url_to_repo')
            if self.http:
                row['url'] = row.get('http_url_to_repo')

            retv.append(row)
        return retv

    def main(self):
        tempdir = os.path.join(self.outputdir, "tmp")
        try:
            os.makedirs(tempdir)

        except OSError as err:
            self.logger.error(err)

        tempdir = tempfile.mkdtemp(suffix='_export',
                                   prefix=self.groupname + "_",
                                   dir=tempdir)

        for row in self.getprojects():
            self.export_project(row, self.outputdir, tempdir)


class SyncGroup(Main):

    def __init__(self, **kwargs):
        props = ("GITLAB", "DESTINATION", "SWLIST", "BUNDLES", "EXTENDED",
                 "HTTP", "GROUPNAME")

        for prop in props:
            if prop in kwargs:
                propname = prop.lower()
                setattr(self, propname, kwargs[prop])

        self.logger = kwargs.get('logger', logging.getLogger('gltools'))

    def main(self):
        tempdir = os.path.join(self.outputdir, "tmp")
        try:
            os.makedirs(tempdir)

        except OSError as err:
            self.logger.error(err)

        tempdir = tempfile.mkdtemp(suffix='_sync',
                                   prefix=self.groupname + "_",
                                   dir=tempdir)

        for row in self.getprojects():
            print(row)
