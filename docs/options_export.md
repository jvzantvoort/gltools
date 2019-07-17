# glt export

## Synopsis

```
  glt export [-g|--gitlab <gitlabsection>] [--http] [-e|--extended]
    [-b|--bundles] [-o|--outputdir <dirname>] [-q|--quiet]
    [-v|--verbose] [-h|--help] <gitlabgroupname>
```

## Description

**glt export** exports the latest version of the projects within the
provided **GITLABGROUPNAME**. The exports come in two versions:

* **bundles**, these are git bundles which can be used to backup
  and/or move the project.
* **regular**, these are exports of the code created with
  ``git archive``. If the project has a target called
  ``roles/requirements.yml`` the file is then used to install the
  relevant roles using the ``ansible-galaxy install`` command. This
  ensures the resulting export is portable and usable for example in
  scenario's where direct access to outside sources is not available.

## Options

- `-g, --gitlab GITLABSECTION`

  Which configuration section should be used (default: local)

- `-q, --quiet`

  Silence warnings

- `-v, --verbose`

  Enable verbose output

- `-h, --help`

  Show this message and exit.

- `--http`

  Use http urls instead of ssh in project sourcing.

- `-e, --extended`

  This overrides the ``mask`` filter and provides all visible
  projects in the listing.

- `-b, --bundles`

  Create output to bundles. These bundles can then later be accessed
  via the ``git clone`` command.

- `-o, --outputdir <directory>`

  There the export shut be put.

## See Also

* [the gltools config file](gltools_cfg.md)
