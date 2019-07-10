# coding: utf-8
"""Command line handling."""

# from __future__ import unicode_literals
import sys
import os.path
import logging
import click
from gltools.exceptions import GLToolsException, GLToolsConfigException
from gltools.main import ExportGroup, WorkOnGroup, SyncGroup, ListProjects, ListGroups, InitConfig
from gltools.version import __version__
from gltools.localgitlab import GitLabConfig

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

def verbose_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.logger.setLevel(logging.DEBUG)
    return click.option('-v', '--verbose',
                        is_flag=True,
                        expose_value=False,
                        help='Enable verbose output',
                        callback=callback)(f)

def quiet_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.logger.setLevel(logging.ERROR)
    return click.option('-q', '--quiet',
                        is_flag=True,
                        expose_value=False,
                        help='Silence warnings',
                        callback=callback)(f)

def verbosity_options(f):
    f = verbose_option(f)
    f = quiet_option(f)
    return f

# attempt to get a default from the config
DEFAULT_GITLAB_SECTION = 'local'
GITLAB_CONFIGS = list()

try:
    glc = GitLabConfig()
    DEFAULT_GITLAB_SECTION = glc.default
    GITLAB_CONFIGS = glc.configs
except GLToolsConfigException:
    pass


gitlab_opt = click.option('--gitlab', '-g', 'gitlab_config_section',
                          help="which configuration section should be used" +
                          " (default: %s)" % DEFAULT_GITLAB_SECTION,
                          metavar="GITLABSECTION",
                          default=DEFAULT_GITLAB_SECTION)

# base options for all
base_options = [
    gitlab_opt,
    click.argument('srcgroupname', nargs=1, required=True, type=str, metavar='GITLABGROUPNAME')
]

# options that effect output
output_options = [
    click.option('--http', 'http', is_flag=True, default=False, help="Use http urls i.s.o. ssh in project sourcing"),
    click.option('--extended', '-e', 'extended', default=False, is_flag=True, help="Extended project listing (include roles)")
]

# export specific options
export_options = base_options + output_options + [
    click.option('-b', '--bundles', 'bundles', is_flag=True, default=False, help="Export to bundles"),
    click.option('--outputdir', '-o', 'outputdir', help="There the export shut be put")
]

# setup specific options
setup_options = base_options + output_options + [
    click.option('--workdir', '-w', 'workdir', help="Where the group should be maintained")
]

# sync options
sync_options = base_options + [
    click.argument('dstgroupname', nargs=1, required=True, type=str, metavar='DESTGROUPNAME')
]

# groups options
groups_options = [gitlab_opt]

# projects options
projects_options = base_options + output_options + [
    click.option('--terse', '-t', 'terse', is_flag=True, default=False, help="Terse output in command"),
]

def add_options(options):
    """ Given a list of click options this creates a decorator that
    will return a function used to add the options to a click command.
    :param options: a list of click.options decorator.
    """
    def _add_options(func):
        """ Given a click command and a list of click options this will
        return the click command decorated with all the options in the list.
        :param func: a click command function.
        """
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    """
    GitLab tools
    """
    pass


@cli.command(name="export")
@add_options(export_options)
@verbosity_options
def export(**kwargs):
    """Export the latest version of the projects"""
    try:
        glt_obj = ExportGroup(**kwargs)
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))


@cli.command(name="setup")
@add_options(setup_options)
@verbosity_options
def setup_wd(**kwargs):
    """Setup or update local clones of the group"""
    try:
        glt_obj = WorkOnGroup(**kwargs)
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))


@cli.command(name="sync")
@add_options(sync_options)
@verbosity_options
def sync(**kwargs):
    """Sync one GitLab group to another."""
    try:
        glt_obj = SyncGroup(**kwargs)
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))

@cli.command(name="groups")
@add_options(groups_options)
@verbosity_options
def groups(**kwargs):
    """list groups on the server"""
    try:
        glt_obj = ListGroups(**kwargs)
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))

@cli.command(name="projects")
@add_options(projects_options)
@verbosity_options
def projects(**kwargs):
    """list projects in the selected group"""
    try:
        glt_obj = ListProjects(**kwargs)
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))

@cli.command(name="init")
@add_options([gitlab_opt])
@verbosity_options
def init_gitlab_config(**kwargs):
    """initialize the local gitlab config"""

    try:
        glt_obj = InitConfig(**kwargs)
        glt_obj.main()

    except GLToolsException as exp:
        raise SystemExit("\n" + str(exp))

