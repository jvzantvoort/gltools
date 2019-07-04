# coding: utf-8

# from __future__ import unicode_literals
import logging
import click
import sys
import os.path
from gltools.exceptions import GLToolsException
from gltools.main import ExportGroup, WorkOnGroup, SyncGroup
from gltools.version import __version__

HELP_OPT_GITLAB = "Which configuration section should be used"
HELP_OPT_LIST = "List groups"
HELP_OPT_OUTPUTDIR = "There the export shut be put"
HELP_OPT_BUNDLES = "Export to bundles"
HELP_OPT_EXTENDED = "Extended project listing (include roles)"
HELP_OPT_HTTP = "Use http urls i.s.o. ssh in project listing"
HELP_OPT_GROUPNAME = "Set groupname"
HELP_OPT_WORKDIR = "Where the group should be maintained"
HELP_OPT_DEST = "Source group"

logger = logging.getLogger('gltools')
logger.setLevel(logging.DEBUG)

consolehandler = logging.StreamHandler(sys.stdout)
consolehandler.setFormatter(logging.Formatter("%(levelname)s %(funcName)s:  %(message)s"))
consolehandler.setLevel(logging.INFO)
logger.addHandler(consolehandler)

class State(object):
    ''' Maintain logging level.'''

    def __init__(self, log_name='gltools', level=logging.INFO):
        self.logger = logging.getLogger(log_name)
        self.logger.propagate = False
        stream = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s %(funcName)s:  %(message)s")
        stream.setFormatter(formatter)
        self.logger.addHandler(stream)

        self.logger.setLevel(level)


pass_state = click.make_pass_decorator(State, ensure=True)

def gitlab_option(f):
    return click.option('--gitlab', '-g', 'sw_gitlab',
                        help=HELP_OPT_GITLAB)(f)

def bundles_option(f):
    return click.option('-b', '--bundles', 'sw_bundles',
                        is_flag=True, default=False, help=HELP_OPT_BUNDLES)(f)

def list_option(f):
    return click.option('-l', '--list', 'sw_list',
                        is_flag=True, default=False, help=HELP_OPT_LIST)(f)

def http_option(f):
    return click.option('--http', 'sw_http',
                        is_flag=True, default=False, help=HELP_OPT_HTTP)(f)

def extended_option(f):
    return click.option('--extended', '-e', 'sw_extended',
              default=False, is_flag=True, help=HELP_OPT_EXTENDED)(f)

def groupname_option(f):
    return click.option('--groupname', '-g', 'sw_groupname',
              help=HELP_OPT_GROUPNAME)(f)

def common_options(f):
    f = gitlab_option(f)
    f = bundles_option(f)
    f = list_option(f)
    f = http_option(f)
    f = extended_option(f)
    f = groupname_option(f)
    return f

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    """
    GitLab tools
    """
    pass

@cli.command(name="export")
@click.option('--outputdir', '-o', 'outputdir',
              help=HELP_OPT_OUTPUTDIR,
              default=os.path.expanduser('~/exports'))
@common_options
def export(sw_gitlab, sw_bundles, sw_list, sw_http, sw_extended, sw_groupname, outputdir):
    """Export the latest version of the projects"""

    args = dict(GITLAB=sw_gitlab,
                OUTPUTDIR=outputdir,
                SWLIST=sw_list,
                BUNDLES=sw_bundles,
                EXTENDED=sw_extended,
                HTTP=sw_http,
                GROUPNAME=sw_groupname,
                logger=logger)

    glt_obj = ExportGroup(**args)

    if not glt_obj.check_gitlab_section():
        sys.exit(1)

    if not glt_obj.check_gitlab_group():
        sys.exit(2)

    try:
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))


@cli.command(name="setup")
@click.option('--workdir', '-w', 'workdir',
              help=HELP_OPT_WORKDIR,
              default=os.path.expanduser('~/Workspace'))
@common_options
def setup_wd(sw_gitlab, sw_bundles, sw_list, sw_http, sw_extended, sw_groupname, workdir):
    """Setup or update local clones of the group"""

    args = dict(GITLAB=sw_gitlab,
                WORKDIR=workdir,
                SWLIST=sw_list,
                BUNDLES=sw_bundles,
                EXTENDED=sw_extended,
                HTTP=sw_http,
                GROUPNAME=sw_groupname,
                logger=logger)

    glt_obj = WorkOnGroup(**args)
    if not glt_obj.check_gitlab_section():
        sys.exit(1)

    if not glt_obj.check_gitlab_group():
        sys.exit(2)

    try:
        glt_obj.main()
    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))

@cli.command(name="sync")
@click.option('--destination', '-d', 'destination',
              help=HELP_OPT_DEST)
@common_options
def sync(sw_gitlab, sw_bundles, sw_list, sw_http, sw_extended, sw_groupname, destination):
    """Sync one GitLab group to another."""

    args = dict(GITLAB=sw_gitlab,
                DESTINATION=destination,
                SWLIST=sw_list,
                BUNDLES=sw_bundles,
                EXTENDED=sw_extended,
                HTTP=sw_http,
                GROUPNAME=sw_groupname,
                logger=logger)

    glt_obj = SyncGroup(**args)

    if not glt_obj.check_gitlab_section():
        sys.exit(1)

    if not glt_obj.check_gitlab_group():
        sys.exit(2)

    try:
        glt_obj.main()
    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))
