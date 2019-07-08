# coding: utf-8
"""Command line handling."""

# from __future__ import unicode_literals
import sys
import os.path
import logging
import click
from gltools.exceptions import GLToolsException
from gltools.main import ExportGroup, WorkOnGroup, SyncGroup
from gltools.version import __version__

HELP_OPT_OUTPUTDIR = "There the export shut be put"
HELP_OPT_WORKDIR = "Where the group should be maintained"
HELP_OPT_DEST = "Source group"

LOG = logging.getLogger('gltools')
LOG.setLevel(logging.DEBUG)

CONSOLE = logging.StreamHandler(sys.stdout)
CONSOLE.setFormatter(logging.Formatter("%(levelname)s %(funcName)s:  %(message)s"))
CONSOLE.setLevel(logging.DEBUG)
LOG.addHandler(CONSOLE)


class State(object):
    """Maintain logging level."""

    def __init__(self, log_name='gltools', level=logging.INFO):
        self.logger = logging.getLogger(log_name)
        self.logger.propagate = False
        stream = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s %(funcName)s:  %(message)s")
        stream.setFormatter(formatter)
        self.logger.addHandler(stream)

        self.logger.setLevel(level)


# pylint: disable=C0103
pass_state = click.make_pass_decorator(State, ensure=True)


def gitlab_option(flag_obj):
    """which configuration section should be used"""
    return click.option('--gitlab', '-g', 'sw_gitlab',
                        help=gitlab_option.__doc__)(flag_obj)


def bundles_option(flag_obj):
    """Export to bundles"""
    return click.option('-b', '--bundles', 'sw_bundles',
                        is_flag=True, default=False, help=bundles_option.__doc__)(flag_obj)


def list_option(flag_obj):
    """List groups"""
    return click.option('-l', '--list', 'sw_list',
                        is_flag=True, default=False, help=list_option.__doc__)(flag_obj)


def http_option(flag_obj):
    """Use http urls i.s.o. ssh in project listing"""
    return click.option('--http', 'sw_http',
                        is_flag=True, default=False, help=http_option.__doc__)(flag_obj)


def extended_option(flag_obj):
    """Extended project listing (include roles)"""
    return click.option('--extended', '-e', 'sw_extended',
                        default=False, is_flag=True, help=extended_option.__doc__)(flag_obj)


def groupname_option(flag_obj):
    """Set groupname"""
    return click.option('--groupname', '-g', 'sw_groupname',
                        help=groupname_option.__doc__)(flag_obj)


def common_options(flag_obj):
    """Collection of common options"""
    flag_obj = gitlab_option(flag_obj)
    flag_obj = bundles_option(flag_obj)
    flag_obj = list_option(flag_obj)
    flag_obj = http_option(flag_obj)
    flag_obj = extended_option(flag_obj)
    flag_obj = groupname_option(flag_obj)
    return flag_obj


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    """
    GitLab tools
    """
    pass


@cli.command(name="export")
@click.option('--outputdir', '-o', 'outputdir',
              help=HELP_OPT_OUTPUTDIR)
@common_options
# pylint: disable=R0913
def export(sw_gitlab, sw_bundles, sw_list, sw_http, sw_extended, sw_groupname, outputdir):
    """Export the latest version of the projects"""

    args = dict(GITLAB=sw_gitlab,
                OUTPUTDIR=outputdir,
                SWLIST=sw_list,
                BUNDLES=sw_bundles,
                EXTENDED=sw_extended,
                HTTP=sw_http,
                GROUPNAME=sw_groupname,
                logger=LOG)

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
              help=HELP_OPT_WORKDIR)
@common_options
# pylint: disable=R0913
def setup_wd(sw_gitlab, sw_bundles, sw_list, sw_http, sw_extended, sw_groupname, workdir):
    """Setup or update local clones of the group"""

    args = dict(GITLAB=sw_gitlab,
                WORKDIR=workdir,
                SWLIST=sw_list,
                BUNDLES=sw_bundles,
                EXTENDED=sw_extended,
                HTTP=sw_http,
                GROUPNAME=sw_groupname,
                logger=LOG)

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
# pylint: disable=R0913
def sync(sw_gitlab, sw_bundles, sw_list, sw_http, sw_extended, sw_groupname, destination):
    """Sync one GitLab group to another."""

    args = dict(GITLAB=sw_gitlab,
                DESTINATION=destination,
                SWLIST=sw_list,
                BUNDLES=sw_bundles,
                EXTENDED=sw_extended,
                HTTP=sw_http,
                GROUPNAME=sw_groupname,
                logger=LOG)

    glt_obj = SyncGroup(**args)

    if not glt_obj.check_gitlab_section():
        sys.exit(1)

    if not glt_obj.check_gitlab_group():
        sys.exit(2)

    try:
        glt_obj.main()
    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))
