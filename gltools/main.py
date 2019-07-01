
import os
import tempfile
import logging
import base64
import shutil
import subprocess
from .localgitlab import LocalGitLab
from .config import Config
from .exceptions import GLToolsException


class Main(object):


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
        self._scriptbase64 = kwargs.get('scriptbase64', "")
        self._scripttemplate = None

    def check_gitlab_section(self):
        self._config = Config()

        if self.gitlab is None:
            self.gitlab = self._config.default

        if self.gitlab not in self._config.configs:
            logging.error("Invalid config section called. Valid options are:")
            for csect in self._config.configs:
                logging.error(" - %s" % csect)
            logging.error("     Check %s for more information" % self._config.configfile)
            return False
        return True

    def check_gitlab_group(self):

        self._lgitlab = LocalGitLab(section=self.gitlab)

        self.group = self._lgitlab.getgroup(self.groupname)

        if not self.group:
            logging.error("Invalid group called. Valid options are:")
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
        logging.info("  execute %s" % scriptfile)
        process = subprocess.Popen(command,
                                   stderr=subprocess.STDOUT,
                                   stdout=subprocess.PIPE)
        stdoutdata = process.communicate()[0]
        if len(stdoutdata.strip()) > 0:
            for line in stdoutdata.split('\n'):
                line = line.strip('\n')
                logging.debug(line)
                retv.append(line)
        returncode = process.returncode

        if returncode != 0:
            logging.info("  execute %s, failed" % scriptfile)
            raise IOError(retv[0])

        logging.info("  execute %s, success" % scriptfile)
        return retv

    def export_project(self, row, outputdir, tempdir):
        row['outputdir'] = outputdir
        row['tempdir'] = tempdir
        if not self._scripttemplate:
            self._scripttemplate = base64.b64decode(self._scriptbase64)

        logging.info("export %(name)s, start" % row)
        scriptname = "%(group_path)s_%(name)s.sh" % row
        scriptname = scriptname.lower().replace(' ', '_')
        outfile = os.path.join(tempdir, scriptname)
        logging.debug("  wrote scriptfile: %s" % outfile)
        with open(outfile, "w") as ofh:
            ofh.write(self._scripttemplate % row)
        os.chmod(outfile, 493)
        self.exec_script(outfile)
        os.unlink(outfile)
        logging.info("export %(name)s, end" % row)

    def export(self):
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
