
gl-export-group
===============

-------------------------------------------------
Export all relevant projects from a GitLab group.
-------------------------------------------------


Synopsis
--------

::

  usage: gl-export-group [-h] [--version] [-g GITLAB] [-o OUTPUTDIR] [-l] [-b]
                         [-e] [--http] [--groupname GROUPNAME]
  
  optional arguments:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    -g GITLAB, --gitlab GITLAB
                          Which configuration section should be used
    -o OUTPUTDIR, --outputdir OUTPUTDIR
                          There the export shut be put
    -l, --list            List groups
    -b, --bundles         Export to bundles
    -e, --extended        Extended project listing (include roles)
    --http                Use http urls i.s.o. ssh in project listing
    --groupname GROUPNAME
                        Set groupname


Description
-----------

``gl-export-group`` 


Author
------

John van Zantvoort

